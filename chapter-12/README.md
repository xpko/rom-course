# 第十二章 逆向实战

## 12.1 案例实战

​	经过对`AOSP`源码的不断探索，对`Android`中应用深入了解，在最后一章中，将结合前文中学习的知识，来进行一个案例的实战，在实战的过程中，首先要对需求进行分析，然后将需要实现的目标进行拆分，最后对其逐一实现，最后组合并测试效果。

​	`JniTrace`是一个逆向分析中常用的基于`frida`实现的工具，在`native`函数调用时，`c++`代码可以通过`JNI`来访问`Java`中的类，类成员以及函数，而`JniTrace`工具主要负责对所有`JNI`的函数调用进行监控，输出所有调用的`JNI`函数，传递的参数，以及其返回值。

​	但是由于`frida`过于知名，导致大多数情况下，开发者们都会对其进行检测，所以在使用时常常会面临各种反制手段导致无法进行下一步的分析。为了能够躲避检测并继续使用`JniTrace`，逆向人员将其迁移到了更隐蔽的类`Xposed`框架中（例如`LSPosed`）。

​	而对比`Hook`的方案来说，从`AOSP`中修改，则完全不存在有`Hook`的痕迹，但是相对而言，开发也更沉重一些，因为需要对系统有一定的理解，并且需要重复的编译系统来进行测试。

​	在这一章的实战中，将讲解如何从`AOSP`的角度完成`JniTrace`这样的功能，并且使用配置进行管理，让其仅对目标进程生效，仅对目标`native`函数生效。

​	在前文讲解`RegisterNative`的输出时，注意到当时的处理将会对所有的进程生效，导致输出过于庞大，在，优化的处理也是从一个配置中，获取到当前进程是否为目标进程，才进行对应的打桩输出。在这个例子中的配置管理同样适用该优化。

## 12.2 需求

​	本案例的需求是参考`JniTrace`，修改`AOSP`源码实现对`JNI`函数调用的监控。所以第一步，是了解`JniTrace`，安装该工具，并开发简单的`demo`来测试其对`JNI`函数监控的效果。

### 12.2.1 功能分析

首先是安装`JniTrace`，该工具是使用`python`开发的，该工具是开源的，想要分析其实现的原理也非常方便，地址：`https://github.com/chame1eon/jnitrace`。安装起来非常方便，使用`pip`安装即可。

```
pip install jnitrace
```

​	由于该工具是基于`frida`实现的，需要在手机中运行`frida-server`，在地址`https://github.com/frida/frida/releases`中下载`frida-server`，开发环境是`AOSP12`的情况直接下载`16`任意版本即可。然后将其推送到手机的`/data/local/tmp`目录中，并运行。具体命令如下。

```
adb push ./frida-server-16.0.11-android-arm64 /data/local/tmp

adb forward tcp:27042 tcp:27042

adb shell 

su

cd /data/local/tmp

chmod +x ./frida-server-16.0.11-android-arm64

// 为防止出现错误，先将selinux关闭
setenforce 0

./frida-server-16.0.10-android-arm64
```

​	`JniTrace`的启动环境准备就绪后，接下来准备测试的案例，案例实现如下。

```java
public class MainActivity extends AppCompatActivity {
    static {
        System.loadLibrary("nativedemo");
    }
    private ActivityMainBinding binding;
    Button btn1;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        TextView tv = binding.sampleText;
        btn1=findViewById(R.id.button);
        btn1.setOnClickListener(v->{
            tv.setText(stringFromJNI());
        });
    }
    public String demo(){
        return "hello";
    }
    public native String stringFromJNI();
}
```

​	修改`stringFromJNI`的实现，让其通过`JNI`调用`MainActivity`中的`demo`函数。

```c++
extern "C" JNIEXPORT jstring JNICALL
Java_cn_mik_nativedemo_MainActivity_stringFromJNI(
        JNIEnv* env,
        jobject obj /* this */) {
    jclass cls= env->FindClass("cn/mik/nativedemo/MainActivity");
    jmethodID mid=env->GetMethodID(cls,"demo","()Ljava/lang/String;");
    jstring data= (jstring)env->CallObjectMethod(obj,mid);
    std::string datatmp= env->GetStringUTFChars(data,nullptr);
    return env->NewStringUTF(datatmp.c_str());
}
```

​	案例准备就绪后，接着通过命令，让`JniTrace`启动应用并监控`JNI`的调用，操作如下。

```
jnitrace -l libnativedemo.so cn.mik.nativedemo
```

​	默认会以`spawn`的方式进行附加，所以应用会自动拉起，点击按钮触发`JNI`调用，`JniTrace`则会输出日志如下。

```
        /* TID 6996 */
        
    309 ms [+] JNIEnv->FindClass							// 调用的JNI函数
    309 ms |- JNIEnv*          : 0x7d3892f610				// 参数1的类型和值
    309 ms |- char*            : 0x7c011aaf00				// 参数2的类型和值
    309 ms |:     cn/mik/nativedemo/MainActivity
    309 ms |= jclass           : 0x71    { cn/mik/nativedemo/MainActivity }// 参数3的类型和值
	// 下面是调用的堆栈
    309 ms ---------------------------------------Backtrace---------------------------------------
    309 ms |->       0x7c011919c4: _ZN7_JNIEnv9FindClassEPKc+0x2c (libnativedemo.so:0x7c01183000)
    309 ms |->       0x7c011919c4: _ZN7_JNIEnv9FindClassEPKc+0x2c (libnativedemo.so:0x7c01183000)

           /* TID 6996 */
    310 ms [+] JNIEnv->GetMethodID
    310 ms |- JNIEnv*          : 0x7d3892f610
    310 ms |- jclass           : 0x71    { cn/mik/nativedemo/MainActivity }
    310 ms |- char*            : 0x7c011aaf1f
    310 ms |:     demo
    310 ms |- char*            : 0x7c011aaf24
    310 ms |:     ()Ljava/lang/String;
    310 ms |= jmethodID        : 0x39    { demo()Ljava/lang/String; }

    310 ms ----------------------------------------------Backtrace----------------------------------------------
    310 ms |->       0x7c01191a0c: _ZN7_JNIEnv11GetMethodIDEP7_jclassPKcS3_+0x3c (libnativedemo.so:0x7c01183000)
    310 ms |->       0x7c01191a0c: _ZN7_JNIEnv11GetMethodIDEP7_jclassPKcS3_+0x3c (libnativedemo.so:0x7c01183000)

           /* TID 6996 */
    311 ms [+] JNIEnv->CallObjectMethodV
    311 ms |- JNIEnv*          : 0x7d3892f610
    311 ms |- jobject          : 0x7ff8e863e8
    311 ms |- jmethodID        : 0x39    { demo()Ljava/lang/String; }
    311 ms |- va_list          : 0x7ff8e861f0
    311 ms |= jobject          : 0x85

    311 ms ------------------------------------------------------Backtrace------------------------------------------------------
    311 ms |->       0x7c01191adc: _ZN7_JNIEnv16CallObjectMethodEP8_jobjectP10_jmethodIDz+0xc4 (libnativedemo.so:0x7c01183000)
    311 ms |->       0x7c01191adc: _ZN7_JNIEnv16CallObjectMethodEP8_jobjectP10_jmethodIDz+0xc4 (libnativedemo.so:0x7c01183000)

           /* TID 6996 */
    313 ms [+] JNIEnv->GetStringUTFChars
    313 ms |- JNIEnv*          : 0x7d3892f610
    313 ms |- jstring          : 0x85
    313 ms |- jboolean*        : 0x0
    313 ms |= char*            : 0x7c8893f330

    313 ms ------------------------------------------------Backtrace------------------------------------------------
    313 ms |->       0x7c01191b4c: _ZN7_JNIEnv17GetStringUTFCharsEP8_jstringPh+0x34 (libnativedemo.so:0x7c01183000)
    313 ms |->       0x7c01191b4c: _ZN7_JNIEnv17GetStringUTFCharsEP8_jstringPh+0x34 (libnativedemo.so:0x7c01183000)

           /* TID 6996 */
    314 ms [+] JNIEnv->NewStringUTF
    314 ms |- JNIEnv*          : 0x7d3892f610
    314 ms |- char*            : 0x7ff8e862c1
    314 ms |:     hello
    314 ms |= jstring          : 0x99    { hello }

    314 ms -----------------------------------------Backtrace-----------------------------------------
    314 ms |->       0x7c01191bdc: _ZN7_JNIEnv12NewStringUTFEPKc+0x2c (libnativedemo.so:0x7c01183000)
    314 ms |->       0x7c01191bdc: _ZN7_JNIEnv12NewStringUTFEPKc+0x2c (libnativedemo.so:0x7c01183000)
```

​	从日志中能非常清晰的看到`JNI`调用函数的具体参数和参数类型，被调用的`Java`函数，以及调用的堆栈等信息。在该工具分析时，能帮助逆向分析人员快速定位到`JNI`函数的调用位置。

### 12.2.2 模块划分

​	有了一个输出的样例作为参考后，就可以开始对该功能进行模块划分了，将一个完整的需求拆分为若干个小块，再针对每个小块逐步实现，下面是对功能进行细化的分割。

* 配置管理，在进程启动后，在`Java`层中，读取配置文件，该配置信息中存储着需要被监控`JNI`调用的进程名称，需要被监控的动态库名称，以及需要监控的`native`函数（监控该函数调用中触发的所有`JNI`），将这些信息传递到`AOSP`的`native`中，并存储在一个全局都能很方便访问到的位置。
* `JNI`调用分析，并进行打桩，从存储在某个全局的配置来判断当前调用是否应该输出，符合条件则打桩输出基本信息。
* 打桩函数分类，由于`JNI`调用的各类函数需要输出的信息不一致，但大致的输出格式一致，所以要准备几种函数来分别处理。

* 调用堆栈信息展示，为了便于追踪调用位置，所以需要输出其调用栈信息。
* 解析参数的类型和值，进行细化输出信息，参考`JniTrace`的输出进行优化展示。

## 12.3 配置管理

### 12.3.1 配置文件的访问权限

​	既然是配置管理，那么肯定是从一个文件中读取数据，而该配置文件必须符合条件是所有`APP`应用都有权限读取，而在`Android`中，每个应用都有各自的用户身份，而不同用户之间的访问权限是受限的。在`Android8`以前，`sdcard`中还没有用户访问具体目录时，只要打开`sdcard`权限，即可访问同一个文件。但是在当前编译的`AOSP12`中已经无法访问`sdcard`下的任意文件了。

​	要解决这种各类应用访问同一个配置文件，有多种解决方式。例如通过自定义系统服务来访问具体文件，这样所有进程只要调用系统服务获取配置数据即可。例如通过共享内存，也可以达到相同的效果。

​	在这个案例中，将采用另一种简单的方式来解决该问题。在`Android`中有一个特殊的目录是`/data/local/tmp`，下面开始简单测试，在该目录创建一个文件。

```
echo "test" > /data/local/tmp/config.json
```

​	接着写一个简单的案例，来尝试在该目录读取测试文件。

```java
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    binding = ActivityMainBinding.inflate(getLayoutInflater());
    setContentView(binding.getRoot());

    String res= FileHelper.readTextFile("/data/local/tmp/mydemo");
    Log.i("MainActivity",res);
}
```

​	测试发现，能成功的读取到文件，这里的重点在于，该文件是`shell`身份创建的，不带有身份标识，所以只要有访问权限就能正常读取，`selinux`不会拦截该操作。而`App`应用创建的文件则无法进行读取。下面看看`shell`创建的文件和应用创建的文件之间的区别。

```
-rw-r--r-- 1 root    root    u:object_r:shell_data_file:s0                             5 2023-04-13 23:19 config.json
-rw-rw-rw- 1 u0_a240 u0_a240 u:object_r:shell_data_file:s0:c240,c256,c512,c768         4 2023-04-13 23:16 mydemo
```

​	可以看到`mydemo`的`setlinux`安全策略限制了哪些用户才能访问该文件。因此对于配置文件的处理，只需要用`shell`创建即可满足条件。

### 12.3.2 配置文件的结构

​	为了访问方便，配置文件以`json`的格式进行存储，在执行进入应用主进程后，则读取该配置文件，然后再根据配置的值进行相应的处理。下面是该配置文件的内容。

```
[{"packageName":"cn.mik.nativedemo","isJNIMethodPrint":true,"isRegisterNativePrint":true,"jniModuleName":"libnativedemo.so","jniFuncName":"stringFromJNI"}]
```

​	为了便于访问，使用一个对应的类对象来解析该配置文件，类结构定义如下。

```java
public class PackageItem {
    //应用包名
    public String packageName;
    //是否打印native函数注册
    public boolean isRegisterNativePrint;
    //是否打印JNI的函数调用
    public boolean isJNIMethodPrint;
    //监控触发JNI调用的模块名
    public String jniModuleName;
    //监控触发JNI调用的函数名
    public String jniFuncName;

    public PackageItem(){
        packageName="";
        jniModuleName="";
        jniFuncName="";
    }
}
```

### 12.3.3 解析配置文件

​	当任意应用程序启动到`ActivityThread`中的主进程入口时，就可以执行解析配置文件逻辑，然后进行相应的处理了，而在`ActivityThread`中`Application`创建后调用的时机，和应用中的`onCreate`调用时机其实相差不大的，但是在测试的时候，在`ActivityThread`中写代码会导致每次修改后，要等待重新编译和刷机，所以完全可以选择先在正常的应用`onCreate`中写入要解析的代码，在最后流程完全跑通后，再将测试无误的代码放入`ActivityThread`中。

​	这里使用`fastjson`将配置文件内容解析成类对象，下面是解析的代码。

```java
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    binding = ActivityMainBinding.inflate(getLayoutInflater());
    setContentView(binding.getRoot());

    String packageName= this.getPackageName();
    String configJson= FileHelper.readTextFile("/data/local/tmp/config.json");
    if(configJson.isEmpty()){
        Log.i(TAG,"not found config json "+packageName);
        return;
    }
    if(!configJson.contains("{")){
        Log.i(TAG,"config data is error "+packageName);
        return;
    }

    List<PackageItem> packageItems= JSON.parseObject(configJson,new TypeReference<List<PackageItem>>(){});
    if(packageItems.size()<=0){
        Log.i(TAG,"not found config json parse "+packageName);
        return;
    }
}
```

### 12.3.4 配置参数的传递

​	由于`JNI`的调用部分是在`native`中进行，所以获取到的配置内容，需要将其传递到`native`层，并将其保存在一个可以全局访问的位置。便于后续打桩时获取配置的参数。

​	传递数据到`native`层，必然是需要新定义一个`native`函数，在这个案例实现中，在文件`libcore/dalvik/src/main/java/dalvik/system/DexFile.java`中添加了`native`函数实现配置数据的传递。修改如下。

```java
public final class DexFile {
    ...
    @UnsupportedAppUsage
    private static native void initConfig(Object item);
}
```

​	接着找到其对应的实现文件`art/runtime/native/dalvik_system_DexFile.cc`，添加对应的实现。

```c++
static void
DexFile_initConfig(JNIEnv* env, jobject ,jobject item) {
    ...
}

static JNINativeMethod gMethods[] = {
  ...
  NATIVE_METHOD(DexFile, getDexFileOptimizationStatus,
                "(Ljava/lang/String;Ljava/lang/String;)[Ljava/lang/String;"),
  NATIVE_METHOD(DexFile, setTrusted, "(Ljava/lang/Object;)V"),
  NATIVE_METHOD(DexFile, initConfig,"(Ljava/lang/Object;)V"),
};

```

​	参数传递到`native`层后，需要将其保存到一个全局能够访问的位置，便于后续`JNI`触发时进行判断。在案例中，我选择将其存放在`Runtime`中。修改`art/runtime/runtime.h`文件如下。

```c++
typedef struct{
    char packageName[128];
    char jniModuleName[128];
    char jniFuncName[128];
    bool isRegisterNativePrint;
    bool isJNIMethodPrint;
    bool jniEnable;
}PackageItem;

class Runtime {
    ...
    public
    ...
        void SetConfigItem(PackageItem item){
            configItem=item;
        }

        PackageItem GetConfigItem(){
            return configItem;
        }
    ...
    private:
    	...
    	PackageItem configItem;
    	...
}
```

​	这样在能访问到`Runtime`的任意地方都能获取到该配置了。现在就可以实现前面的`initConfig`函数了，将`java`传递过来的对象，转换为`c++`对象存储到`Runtime`中。具体实现如下。

```c++

static void
DexFile_initConfig(JNIEnv* env, jobject ,jobject item) {

    Runtime* runtime=Runtime::Current();
    // 将各字段取出
    jclass jcInfo = env->FindClass("cn/krom/PackageItem");
    jfieldID jPackageName = env->GetFieldID(jcInfo, "packageName", "Ljava/lang/String;");
    jfieldID jJniModuleName = env->GetFieldID(jcInfo, "jniModuleName", "Ljava/lang/String;");
    jfieldID jJniFuncName = env->GetFieldID(jcInfo, "jniFuncName", "Ljava/lang/String;");
    jfieldID jIsRegisterNativePrint = env->GetFieldID(jcInfo, "isRegisterNativePrint", "Z");
    jfieldID jIsJNIMethodPrint = env->GetFieldID(jcInfo, "isJNIMethodPrint", "Z");

    PackageItem citem;
	// 将java的值转换为c++的值
    jstring jstrPackageName = (jstring)env->GetObjectField(item, jPackageName);
    const char* pPackageName = (char*)env->GetStringUTFChars(jstrPackageName, 0);
    strcpy(citem.packageName, pPackageName);

    jstring jstrJniModuleName = (jstring)env->GetObjectField(item, jJniModuleName);
    const char* pJniModuleName = (char*)env->GetStringUTFChars(jstrJniModuleName, 0);
    strcpy(citem.jniModuleName, pJniModuleName);

    jstring jstrJniFuncName = (jstring)env->GetObjectField(item, jJniFuncName);
    const char* pJniFuncName = (char*)env->GetStringUTFChars(jstrJniFuncName, 0);
    strcpy(citem.jniFuncName, pJniFuncName);

    citem.isRegisterNativePrint = env->GetBooleanField(item, jIsRegisterNativePrint);
    citem.isJNIMethodPrint = env->GetBooleanField(item, jIsJNIMethodPrint);
	
    // 配置存储到全局
    runtime->SetConfigItem(citem);
}

```

​	到这里就成功从配置文件中读取数据，并解析后通过`native`函数将其存储到全局能访问的位置了。最后在成功读取配置后，通过反射调用`initConfig`函数，即可完成配置的初始化工作。

```java
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    binding = ActivityMainBinding.inflate(getLayoutInflater());
    setContentView(binding.getRoot());

    String packageName= this.getPackageName();
    // 读取配置文件
    String configJson= FileHelper.readTextFile("/data/local/tmp/config.json");
    if(configJson.isEmpty()){
        Log.i(TAG,"not found config json "+packageName);
        return;
    }
    // 判断是否是json格式
    if(!configJson.contains("{")){
        Log.i(TAG,"config data is error "+packageName);
        return;
    }
	// 将json转换为对象
    List<PackageItem> packageItems= JSON.parseObject(configJson,new TypeReference<List<PackageItem>>(){});
    if(packageItems.size()<=0){
        Log.i(TAG,"not found config json parse "+packageName);
        return;
    }
    // 判断当前app是否为目标应用
    PackageItem currentItem=null;
    for(PackageItem item : packageItems){
        if(item.packageName.contains(this.getPackageName())){
            currentItem=item;
            break;
        }
    }
    if(currentItem==null){
        return;
    }
    // 是目标应用则反射调用初始化函数，将配置内容传递到native层。
    try {
        Class dexFileClazz=ClassLoader.getSystemClassLoader().loadClass("dalvik.system.DexFile");
        Method method=dexFileClazz.getMethod("initConfig",Object.class);
        method.invoke(null,currentItem);
    } catch (ClassNotFoundException e) {
        throw new RuntimeException(e);
    } catch (NoSuchMethodException e) {
        throw new RuntimeException(e);
    } catch (InvocationTargetException e) {
        throw new RuntimeException(e);
    } catch (IllegalAccessException e) {
        throw new RuntimeException(e);
    }
}
```

## 12.4 JNI调用分析

​	`JNI`的调用流程并不是非常复杂，`env`中对应的相关函数定义是在文件`libnativehelper/include_jni/jni.h`中，`JNIEnv`的定义描述如下。

```c++
#if defined(__cplusplus)
// 判断当前是否在C++环境下
typedef _JNIEnv JNIEnv;
typedef _JavaVM JavaVM;
#else
// 如果在C环境下
typedef const struct JNINativeInterface* JNIEnv;
typedef const struct JNIInvokeInterface* JavaVM;
#endif
```

​	接着看看`_JNIEnv`的定义描述。

```c++
struct _JNIEnv {
    /* do not rename this; it does not seem to be entirely opaque */
    const struct JNINativeInterface* functions;

#if defined(__cplusplus)

    ...
    void CallStaticVoidMethod(jclass clazz, jmethodID methodID, ...)
    {
        va_list args;
        va_start(args, methodID);
        functions->CallStaticVoidMethodV(this, clazz, methodID, args);
        va_end(args);
    }
    void CallStaticVoidMethodV(jclass clazz, jmethodID methodID, va_list args)
    { functions->CallStaticVoidMethodV(this, clazz, methodID, args); }
    void CallStaticVoidMethodA(jclass clazz, jmethodID methodID, const jvalue* args)
    { functions->CallStaticVoidMethodA(this, clazz, methodID, args); }
	...
#endif /*__cplusplus*/
};
```

​	可以看到虽然`c++`的情况下是使用结构体进行一层包装，但是最终实际也调用的`JNINativeInterface`下的函数实现。继续看看该结构体的定义。

```c++
struct JNINativeInterface {
    void*       reserved0;
    void*       reserved1;
    void*       reserved2;
    void*       reserved3;
	...
    jmethodID   (*GetMethodID)(JNIEnv*, jclass, const char*, const char*);
    jobject     (*CallObjectMethod)(JNIEnv*, jobject, jmethodID, ...);
    jobject     (*CallObjectMethodV)(JNIEnv*, jobject, jmethodID, va_list);
    jobject     (*CallObjectMethodA)(JNIEnv*, jobject, jmethodID, const jvalue*);
    ...
};
```

​	根据上面源码分析，能够看到`JNIEnv`实际就是`JNINativeInterface`的指针，而该指针对应的结构体中存储着函数表，接下来看是如何给`functions`进行赋值的。

```c++
JNIEnvExt::JNIEnvExt(Thread* self_in, JavaVMExt* vm_in, std::string* error_msg)
    : self_(self_in),
      vm_(vm_in),
      local_ref_cookie_(kIRTFirstSegment),
      locals_(kLocalsInitial, kLocal, IndirectReferenceTable::ResizableCapacity::kYes, error_msg),
      monitors_("monitors", kMonitorsInitial, kMonitorsMax),
      critical_(0),
      check_jni_(false),
      runtime_deleted_(false) {
  MutexLock mu(Thread::Current(), *Locks::jni_function_table_lock_);
  check_jni_ = vm_in->IsCheckJniEnabled();
  // 函数指针赋值
  functions = GetFunctionTable(check_jni_);
  unchecked_functions_ = GetJniNativeInterface();
}
```

​	继续分析`GetFunctionTable`实现。

```c++
const JNINativeInterface* JNIEnvExt::GetFunctionTable(bool check_jni) {
  const JNINativeInterface* override = JNIEnvExt::table_override_;
  if (override != nullptr) {
    return override;
  }
  return check_jni ? GetCheckJniNativeInterface() : GetJniNativeInterface();
}
```

​	继续进入查看`GetJniNativeInterface`实现逻辑

```c++
const JNINativeInterface* GetJniNativeInterface() {
  return Runtime::Current()->GetJniIdType() == JniIdType::kPointer
             ? &JniNativeInterfaceFunctions<false>::gJniNativeInterface
             : &JniNativeInterfaceFunctions<true>::gJniNativeInterface;
}
```

​	到这里就对`JNI`对应函数进行赋值了。

```c++
template<bool kEnableIndexIds>
struct JniNativeInterfaceFunctions {
  using JNIImpl = JNI<kEnableIndexIds>;
  static constexpr JNINativeInterface gJniNativeInterface = {
    nullptr,  // reserved0.
    nullptr,  // reserved1.
    nullptr,  // reserved2.
    nullptr,  // reserved3.
    ...
    JNIImpl::GetMethodID,
    JNIImpl::CallObjectMethod,
    JNIImpl::CallObjectMethodV,
    JNIImpl::CallObjectMethodA,
    ...
  };
};
```

​	根据上面的源码分析，知道了`JNI`中函数对应的实现就在文件`art/runtime/jni/jni_internal.cc`中实现。明白了这个原理后，接下来添加一个打桩函数简单的输出信息，来确定流程是否正确。

```c++
static jobject CallObjectMethodV(JNIEnv* env, jobject obj, jmethodID mid, va_list args) {
    CHECK_NON_NULL_ARGUMENT(obj);
    CHECK_NON_NULL_ARGUMENT(mid);
    ALOGD("mikrom %s",__FUNCTION__);
    ScopedObjectAccess soa(env);
    JValue result(InvokeVirtualOrInterfaceWithVarArgs(soa, obj, mid, args));
    return soa.AddLocalReference<jobject>(result.GetL());
  }
```

​	编译后成功看到了大量该函数调用的日志，接下来需要封装一个函数，在这个函数中根据前文传递的配置进行判断是否需要输出`JNI`调用的相关信息。符合条件才进行打桩。具体实现如下。

```c++
void ShowVarArgs(const ScopedObjectAccessAlreadyRunnable& ,
                 const char* funcname,
                 jmethodID ,
                 va_list ){
	// 从Runtime获取配置信息，配置了需要打印JNI，并且当前符合输出条件才进行打桩
    Runtime* runtime=Runtime::Current();
    if(!runtime->GetConfigItem().isJNIMethodPrint ||!runtime->GetConfigItem().jniEnable){
        return;
    }
    // 打桩信息
    ALOGD("mikrom ShowVarArgs %s %s %s %s %p",runtime->GetProcessPackageName().c_str(),runtime->GetConfigItem().jniModuleName,
          runtime->GetConfigItem().jniFuncName,funcname,Thread::Current());

}
```

​	这里使用了两个条件来控制打桩，`isJNIMethodPrint`表示是否要对`JNI`监控打桩，而`jniEnable`则表示，当前是否应该打桩，例如在指定的`native`函数调用期间，才打桩输出，或者指定动态库加载后，才进行打桩，这个过滤条件大大的降低了对无效日志的输出，提高分析的效率。

​	`jniEnable`默认是`false`的，值不应由配置文件决定，而是在调用过程中进行赋值，所有`native`函数开始执行和执行结束时都会经过`JniMethodStart`和`JniMethodEnd`函数，所以只需要在进入该函数时，将该字段修改为`true`，在结束时，再将其关闭即可。下面是实现代码。

```c++
extern uint32_t JniMethodStart(Thread* self) {
  JNIEnvExt* env = self->GetJniEnv();
  DCHECK(env != nullptr);
  uint32_t saved_local_ref_cookie = bit_cast<uint32_t>(env->GetLocalRefCookie());
  env->SetLocalRefCookie(env->GetLocalsSegmentState());
  //add
  Runtime* runtime=Runtime::Current();
  if(runtime->GetConfigItem().isJNIMethodPrint){
      ArtMethod* native_method = *self->GetManagedStack()->GetTopQuickFrame();
      std::string methodname=native_method->PrettyMethod();
      // 当前开始函数为要监控的目标函数时，则开启输出JNI
      if(strstr(methodname.c_str(),runtime->GetConfigItem().jniFuncName)){
          runtime->GetConfigItem().jniEnable=true;
          ALOGD("mikrom enter jni %s",methodname.c_str());
      }
  }
  //endadd
  if (kIsDebugBuild) {
    ArtMethod* native_method = *self->GetManagedStack()->GetTopQuickFrame();
    CHECK(!native_method->IsFastNative()) << native_method->PrettyMethod();
  }
  // Transition out of runnable.
  self->TransitionFromRunnableToSuspended(kNative);
  return saved_local_ref_cookie;
}


extern void JniMethodEnd(uint32_t saved_local_ref_cookie, Thread* self) {
    //add
    Runtime* runtime=Runtime::Current();
    if(runtime->GetConfigItem().isJNIMethodPrint){
        ArtMethod* native_method = *self->GetManagedStack()->GetTopQuickFrame();
        std::string methodname=native_method->PrettyMethod();
        // 当前结束函数为要监控的目标函数时，则关闭输出JNI
        if(strstr(methodname.c_str(),runtime->GetConfigItem().jniFuncName)){
            runtime->GetConfigItem().jniEnable=false;
            ALOGD("mikrom leave jni %s",methodname.c_str());
        }
    }
    //endadd

  GoToRunnable(self);
  PopLocalReferences(saved_local_ref_cookie, self);
}


static mirror::Object* JniMethodEndWithReferenceHandleResult(jobject result,
                                                             uint32_t saved_local_ref_cookie,
                                                             Thread* self)
    NO_THREAD_SAFETY_ANALYSIS {
    //add
    Runtime* runtime=Runtime::Current();
    if(runtime->GetConfigItem().isJNIMethodPrint){
        ArtMethod* native_method = *self->GetManagedStack()->GetTopQuickFrame();
        std::string methodname=native_method->PrettyMethod();
        if(strstr(methodname.c_str(),runtime->GetConfigItem().jniFuncName)){
            runtime->GetConfigItem().jniEnable=false;
            ALOGD("mikrom leave jni %s",methodname.c_str());
        }
    }
    //endadd
	...
}
```

## 12.5 打桩函数分类

​	前文中仅仅对其中类似`CallObjectMethodV`函数，进行简单的输出，而实际场景中，大量的`JNI`函数调用，并非有着这些参数，所以需要将`ShowVarArgs`进行封装，并有多种重载实现。具体重载参数需要根据实际`JNI`函数中有哪些参数来决定。在这里篇幅有限，所以不会将所有的`JNI`函数情况进行处理，主要将前文中测试中调用到的`JNI`函数进行对应处理。

​	根据`JniTrace`中的日志，需要对四个`JNI`函数进行打桩处理，分别是`GetMethodID、GetStringUTFChars、NewStringUTF、CallObjectMethodV`。根据这些函数对应的参数，对打桩的函数进行重载处理。

### 12.5.1 GetMethodID打桩

​	在开始修改代码前，先看看该函数的定义。

```c++
// 根据函数名，以及对应的函数签名来获取对应函数
static jmethodID GetMethodID(JNIEnv* env, jclass java_class, const char* name, const char* sig);
```

​	再看看`JniTrace`对于该函数的输出。

```
           /* TID 6996 */
    310 ms [+] JNIEnv->GetMethodID
    310 ms |- JNIEnv*          : 0x7d3892f610
    310 ms |- jclass           : 0x71    { cn/mik/nativedemo/MainActivity }
    310 ms |- char*            : 0x7c011aaf1f
    310 ms |:     demo
    310 ms |- char*            : 0x7c011aaf24
    310 ms |:     ()Ljava/lang/String;
    310 ms |= jmethodID        : 0x39    { demo()Ljava/lang/String; }

    310 ms ----------------------------------------------Backtrace----------------------------------------------
    310 ms |->       0x7c01191a0c: _ZN7_JNIEnv11GetMethodIDEP7_jclassPKcS3_+0x3c (libnativedemo.so:0x7c01183000)
    310 ms |->       0x7c01191a0c: _ZN7_JNIEnv11GetMethodIDEP7_jclassPKcS3_+0x3c (libnativedemo.so:0x7c01183000)
```

​	该输出中，关键展示了函数所在类的类名称、函数名称、函数签名，以及所找到的对应函数id，调用堆栈。参考该类型的`JNI`调用，下面重构一个相应的打桩函数。

```c++
// 是否需要打印
bool HasShow(){
    Runtime* runtime=Runtime::Current();
    if(!runtime->GetConfigItem().isJNIMethodPrint ||!runtime->GetConfigItem().jniEnable){
        return false;
    }
    return true;
}

// JNI打桩函数重载,针对GetMethodID进行输出
void ShowVarArgs(const ScopedObjectAccessAlreadyRunnable& soa,const char* funcname,jclass java_class, const char* name, const char* sig,jmethodID methodID){
    if(!HasShow()){
        return;
    }
    ObjPtr<mirror::Class> c = soa.Decode<mirror::Class>(java_class);
    std::string temp;
    const char* className= c->GetDescriptor(&temp);
    ArtMethod* method = jni::DecodeArtMethod(methodID);
    pid_t pid = getpid();
    // 前面加上标志是为了方便搜索日志
    ALOGD("%s           /* TID %d */","mikrom",pid);
    ALOGD("%s           [+] JNIEnv->%s","mikrom",funcname);
    ALOGD("%s           |- jclass           :%s","mikrom",className);
    ALOGD("%s           |- char*            :%p","mikrom",name);
    ALOGD("%s           |:     %s","mikrom",name);
    ALOGD("%s           |- char*            :%p","mikrom",sig);
    ALOGD("%s           |:     %s","mikrom",sig);
    ALOGD("%s           |= jmethodID        :0x%x   {%s}","mikrom",method->GetMethodIndex(),method->PrettyMethod().c_str());
}
```

​	最后在`JNI`函数调用处，使用该打桩函数。

```c++
static jmethodID GetMethodID(JNIEnv* env, jclass java_class, const char* name, const char* sig) {
    CHECK_NON_NULL_ARGUMENT(java_class);
    CHECK_NON_NULL_ARGUMENT(name);
    CHECK_NON_NULL_ARGUMENT(sig);
    ScopedObjectAccess soa(env);
    jmethodID result = FindMethodID<kEnableIndexIds>(soa, java_class, name, sig, false);
    ShowVarArgs(soa,__FUNCTION__,java_class,name,sig,result);
    return result;
  }
```

### 12.5.2 GetStringUTFChars打桩

​	参考上面的流程，首先了解该函数的定义结构。

```c++
static const char* GetStringUTFChars(JNIEnv* env, jstring java_string, jboolean* is_copy);
```

​	接着查看`JniTrace`的输出显示。

 ```
            /* TID 6996 */
     313 ms [+] JNIEnv->GetStringUTFChars
     313 ms |- JNIEnv*          : 0x7d3892f610
     313 ms |- jstring          : 0x85
     313 ms |- jboolean*        : 0x0
     313 ms |= char*            : 0x7c8893f330
 
     313 ms ------------------------------------------------Backtrace------------------------------------------------
     313 ms |->       0x7c01191b4c: _ZN7_JNIEnv17GetStringUTFCharsEP8_jstringPh+0x34 (libnativedemo.so:0x7c01183000)
     313 ms |->       0x7c01191b4c: _ZN7_JNIEnv17GetStringUTFCharsEP8_jstringPh+0x34 (libnativedemo.so:0x7c01183000)
 ```

​	看的出来这个函数非常的简单，主要是对返回值进行输出即可。添加打桩函数如下。

```c++
void ShowVarArgs(const ScopedObjectAccessAlreadyRunnable& ,
                 const char* funcname,
                 jboolean* is_copy ,
                 const char* data ){
    if(!HasShow()){
        return;
    }
    pid_t pid = getpid();
    ALOGD("%s           /* TID %d */","mikrom",pid);
    ALOGD("%s           [+] JNIEnv->%s","mikrom",funcname);
    if(is_copy== nullptr){
        ALOGD("%s           |- jboolean*        : %d","mikrom",false);
    }else{
        ALOGD("%s           |- jboolean*        : %d","mikrom",*is_copy);
    }
    ALOGD("%s           |= char*            : %s","mikrom",data);
}
```

​	修改原调用函数如下。

```c++

  static const char* GetStringUTFChars(JNIEnv* env, jstring java_string, jboolean* is_copy) {
    ...
    bytes[byte_count] = '\0';
    ShowVarArgs(soa,__FUNCTION__,is_copy,bytes);
    return bytes;
  }
```

### 12.5.3 NewStringUTF打桩

​	该函数同样非常简单，和上一个函数相反，只需要将参数打印即可，无需处理返回值，函数定义如下。

```c++
static jstring NewStringUTF(JNIEnv* env, const char* utf);
```

​	接着看`JniTrace`的输出，同样非常简单。

```
           /* TID 6996 */
    314 ms [+] JNIEnv->NewStringUTF
    314 ms |- JNIEnv*          : 0x7d3892f610
    314 ms |- char*            : 0x7ff8e862c1
    314 ms |:     hello
    314 ms |= jstring          : 0x99    { hello }
```

​	添加对应打桩函数如下。

```c++
void ShowVarArgs(const ScopedObjectAccessAlreadyRunnable& ,
                 const char* funcname,
                 const char* data ){
    if(!HasShow()){
        return;
    }
    pid_t pid = getpid();
    ALOGD("%s           /* TID %d */","mikrom",pid);
    ALOGD("%s           [+] JNIEnv->%s","mikrom",funcname);
    ALOGD("%s           |- char*        : %d","mikrom",data);
}
```

​	调整原函数调用该打桩如下。

```c++

static jstring NewStringUTF(JNIEnv* env, const char* utf) {
    ...
    ScopedObjectAccess soa(env);
    ShowVarArgs(soa,__FUNCTION__,utf);
    ObjPtr<mirror::String> result =
        mirror::String::AllocFromModifiedUtf8(soa.Self(), utf16_length, utf, utf8_length);
    return soa.AddLocalReference<jstring>(result);
}
```

### 12.5.4 CallObjectMethodV打桩

​	这个`JNI`函数不同于前面几种函数，在前几个函数中，参数是明确固定的，而`CallObjectMethodV`是通过`JNI`，调用一个`java`函数，而为此`java`函数提供的所有参数的类型，以及参数个数。都是未知的。而这些参数的信息同样是需要打桩展示出来的。

​	将测试样例中，被调用的`java`函数进行调整，将测试函数新增参数，并且使用`JniTrace`观察`CallObjectMethodV`的输出结果。样例函数修改如下。

```java
public String demo(int a,float b,long c,String d){
    return a+b+c+d;
}
```

​	同时修改`native`函数中使用`JNI`调用的逻辑。

```c++
extern "C" JNIEXPORT jstring JNICALL
Java_cn_mik_nativedemo_MainActivity_stringFromJNI(
        JNIEnv* env,
        jobject obj /* this */) {
    jclass cls= env->FindClass("cn/mik/nativedemo/MainActivity");
    jmethodID mid=env->GetMethodID(cls,"demo", "(IFLjava/lang/String;)Ljava/lang/String;");
    jstring c=env->NewStringUTF("newdemo");
    jstring data= (jstring)env->CallObjectMethod(obj,mid,1,2.0f,c);
    std::string datatmp= env->GetStringUTFChars(data,nullptr);
    return env->NewStringUTF(datatmp.c_str());
}
```

​	再次使用`JniTrace`观察到的`CallObjectMethodV`输出如下。

```
           /* TID 18863 */
   2169 ms [+] JNIEnv->CallObjectMethodV
   2169 ms |- JNIEnv*          : 0x704e856090
   2169 ms |- jobject          : 0x7fe4d55d38
   2169 ms |- jmethodID        : 0x3d    { demo(IFLjava/lang/String;)Ljava/lang/String; }
   2169 ms |- va_list          : 0x7fe4d55b30
   2169 ms |:     jint         : 1
   2169 ms |:     jfloat       : 2
   2169 ms |:     jstring      : 0x81    { newdemo }
   2169 ms |= jobject          : 0x95    { java/lang/String }

   2169 ms ------------------------------------------------------Backtrace------------------------------------------------------
   2169 ms |->       0x6f5d458ae4: _ZN7_JNIEnv16CallObjectMethodEP8_jobjectP10_jmethodIDz+0xc4 (libnativedemo.so:0x6f5d44a000)
   2169 ms |->       0x6f5d458ae4: _ZN7_JNIEnv16CallObjectMethodEP8_jobjectP10_jmethodIDz+0xc4 (libnativedemo.so:0x6f5d44a000)
```

​	从日志中能看到，参数列表被解析后将具体的值进行输出，而返回值的部分，如果是`jobject`，则将其类型进行输出。明白具体需求后，接着就可以开始根据`CallObjectMethodV`类型参数定义来准备打桩函数了。定义描述如下。

```c++
static jobject CallObjectMethodV(JNIEnv* env, jobject obj, jmethodID mid, va_list args);
```

​	根据参考，需要输出调用的目标函数，参数，以及其返回值。而其他的类似调用函数的情况，和该函数差不多的处理，只是返回值的输出不同。优化后的打桩函数如下。

```c++
// 输出JNI的参数部分
void ShowVarArgs(const ScopedObjectAccessAlreadyRunnable& soa,
                 const char* funcname,
                 jmethodID mid,
                 va_list vaList){
    if(!HasShow()){
        return;
    }

    ArtMethod* method = jni::DecodeArtMethod(mid);
    pid_t pid = getpid();
    ALOGD("%s           /* TID %d */","mikrom",pid);
    ALOGD("%s           [+] JNIEnv->%s","mikrom",funcname);
    ALOGD("%s           |- jmethodID        :0x%x   {%s}","mikrom",method->GetMethodIndex(),method->PrettyMethod().c_str());
    ALOGD("%s           |- va_list          :%p","mikrom",&vaList);

    uint32_t shorty_len = 0;
    const char* shorty =
            method->GetInterfaceMethodIfProxy(kRuntimePointerSize)->GetShorty(&shorty_len);
    ArgArray arg_array(shorty, shorty_len);
    arg_array.VarArgsShowArg(soa, vaList);
}


void ShowVarArgs(const ScopedObjectAccessAlreadyRunnable& soa,
                 const char* funcname,
                 jmethodID mid,
                 va_list valist,
                 jobject ret){
    if(!HasShow()){
        return;
    }
    // 输出JNI的参数部分
    ShowVarArgs(soa,funcname,mid,valist);
	// 输出JNI的返回值
    ObjPtr<mirror::Object> receiver =soa.Decode<mirror::Object>(ret);
    if(receiver==nullptr){
        return;
    }
    ObjPtr<mirror::Class> cls=receiver->GetClass();
    if (cls->DescriptorEquals("Ljava/lang/String;")){
        ObjPtr<mirror::String> retStr =soa.Decode<mirror::String>(ret);
        ALOGD("%s           |= jstring          :%s","mikrom",(const char*)retStr->GetValue());
    }else{
        std::string temp;
        const char* className= cls->GetDescriptor(&temp);
        ALOGD("%s           |= jobject          :%p   {%s}","mikrom",&ret,className);
    }
}
```

​	很多`JNI`的调用函数除了返回值的处理不同，其他调用部分都是相同的，所以将打印参数部分和打印返回值部分拆分开来，而参数`va_list`的解析，可以直接参考`AOSP`源码中，函数`BuildArgArrayFromVarArgs`对其的处理。实现如下。

```c++
void VarArgsShowArg(const ScopedObjectAccessAlreadyRunnable& soa,
                        va_list ap)
    REQUIRES_SHARED(Locks::mutator_lock_) {
            std::stringstream ss;
            for (size_t i = 1; i < shorty_len_; ++i) {
                switch (shorty_[i]) {
                    case 'Z':
                    case 'B':
                    case 'C':
                    case 'S':
                    case 'I':
                        ss<<"mikrom"<<"           |:     jint         : "<<va_arg(ap, jint)<<"\n";
                        break;
                    case 'F':
                        ss<<"mikrom"<<"           |:     jfloat       : "<<va_arg(ap, jdouble)<<"\n";
                        break;
                    case 'L':{
                        jobject obj=va_arg(ap, jobject);
                        ObjPtr<mirror::Object> receiver =soa.Decode<mirror::Object>(obj);
                        if(receiver==nullptr){
                            ss<<"mikrom"<<"           |:     jobject      : null\n";
                            break;
                        }
                        ObjPtr<mirror::Class> cls=receiver->GetClass();
                        if (cls->DescriptorEquals("Ljava/lang/String;")){
                            ObjPtr<mirror::String> argStr =soa.Decode<mirror::String>(obj);
                            ss<<"mikrom"<<"           |:     jstring      : "<<(const char*)argStr->GetValue()<<"\n";
                        }else{
                            ss<<"mikrom"<<"           |:     jobject      : "<<&obj<<"\n";
                        }
                        break;
                    }
                    case 'D':
                        ss<<"mikrom"<<"           |:     jdouble       : "<<va_arg(ap, jdouble)<<"\n";
                        break;
                    case 'J':
                        ss<<"mikrom"<<"           |:     jlong         : "<<va_arg(ap, jlong)<<"\n";
                        break;
                }
            }
            ALOGD("%s",ss.str().c_str());
    }
```

​	到这里案例中使用的相关`JNI`函数处理就添加完成了，编译后刷入测试机。当点击样例中的按钮时，最后输出效果如下所示。

```
mikrom enter jni java.lang.String cn.mik.nativedemo.MainActivity.stringFromJNI() 0x74656a77b0
mikrom           /* TID 5465 */
mikrom           [+] JNIEnv->GetMethodID
mikrom           |- jclass           :Lcn/mik/nativedemo/MainActivity;
mikrom           |- char*            :0x7275d69f1b
mikrom           |:     demo
mikrom           |- char*            :0x7275d69eef
mikrom           |:     (IFLjava/lang/String;)Ljava/lang/String;
mikrom           |= jmethodID        :0x277   {java.lang.String cn.mik.nativedemo.MainActivity.demo(int, float, java.lang.String)}
mikrom           /* TID 5465 */
mikrom           [+] JNIEnv->NewStringUTF
mikrom           |- char*        : newdemo
mikrom           /* TID 5465 */
mikrom           [+] JNIEnv->CallObjectMethodV
mikrom           |- jmethodID        :0x277   {java.lang.String cn.mik.nativedemo.MainActivity.demo(int, float, java.lang.String)}
mikrom           |- va_list          :0x7fe0461bb0
mikrom           |:     jint         : 1
mikrom           |:     jfloat       : 2
mikrom           |:     jstring      : newdemo
mikrom           |= jstring          :3.0newdemo
mikrom           /* TID 5465 */
mikrom           [+] JNIEnv->GetStringUTFChars
mikrom           |- jboolean*        : 0
mikrom           |= char*            : 3.0newdemo
mikrom           /* TID 5465 */
mikrom           [+] JNIEnv->NewStringUTF
mikrom           |- char*        : 3.0newdemo
mikrom leave jni java.lang.String cn.mik.nativedemo.MainActivity.stringFromJNI()
```

## 12.6 调用栈展示

​	经过调整后，打桩函数已经非常接近`JniTrace`的输出效果了，但是还有最后的一点区别是在于`JNI`函数的调用堆栈，不仅仅需要看到函数的参数和返回值，还需要知道是在哪里触发了该函数。而获取调用堆栈地址，在`AOSP`源码是有相关支持的，当应用崩溃时，在`logcat`中能看到详细的堆栈信息。

### 12.6.1 xUnwind获取调用栈

​	`xUnwind`是一个开源工具，该工具将堆栈获取进行了封装，并且有简单的`demo`演示如何获取堆栈。下载地址：`https://github.com/hexhacking/xUnwind.git`。接下来将分析该工具是如何实现的获取堆栈，然后再将其内置到`AOSP`中，在`JNI`函数调用结束时获取堆栈进行输出。

​	`xUnwind`提供了三种调用堆栈回溯方案。

- `CFI (Call Frame Info)`：由安卓系统库提供。
- `EH (Exception handling GCC extension)`：由编译器提供。
- `FP (Frame Pointer)`：只支持 `ARM64`。

​	其中`CFI`主要针对`java`层调用回溯，`FP`仅支持`ARM64`。根据功能需要，选择`EH`方案进行调用栈回溯。下面看看该工具是如何实现的，首先查看`JNI_OnLoad`的实现。

```c++
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM *vm, void *reserved) {
  JNIEnv *env;
  jclass cls;

  (void)reserved;

  if (NULL == vm) return JNI_ERR;
  if (JNI_OK != (*vm)->GetEnv(vm, (void **)&env, SAMPLE_JNI_VERSION)) return JNI_ERR;
  if (NULL == env || NULL == *env) return JNI_ERR;
  if (NULL == (cls = (*env)->FindClass(env, SAMPLE_JNI_CLASS_NAME))) return JNI_ERR;
  // 注册对应的函数
  if (0 != (*env)->RegisterNatives(env, cls, sample_jni_methods,
                                   sizeof(sample_jni_methods) / sizeof(sample_jni_methods[0])))
    return JNI_ERR;
  // 注册信号处理
  sample_signal_register();

  return SAMPLE_JNI_VERSION;
}
```

​	然后看看`sample_signal_register`对信号进行了什么处理

```c++
static void sample_signal_register(void) {
  struct sigaction act;
  // 清空act
  memset(&act, 0, sizeof(act));
    
  // 填充所有信号
  sigfillset(&act.sa_mask);
  // 删除SIGSEGV信号
  sigdelset(&act.sa_mask, SIGSEGV);
  // 设置信号动作的对应函数
  act.sa_sigaction = sample_sigabrt_handler;
  act.sa_flags = SA_RESTART | SA_SIGINFO | SA_ONSTACK;
  // 设置指定信号的动作
  sigaction(SIGABRT, &act, NULL);
  // 清空act
  memset(&act, 0, sizeof(act));
  // 填充所有信号
  sigfillset(&act.sa_mask);
  // 设置信号动作的对应函数
  act.sa_sigaction = sample_sigsegv_handler;
  act.sa_flags = SA_RESTART | SA_SIGINFO | SA_ONSTACK;
  // 设置指定信号的动作
  sigaction(SIGSEGV, &act, &g_sigsegv_oldact);
}
```

​	在这个函数中主要是对信号指定了处理函数，`SIGSEGV` 是一种表示段错误的信号，通常意味着进程访问了无法访问的内存地址。

​	`SIGABRT` 是一种表示异常终止的信号，通常由调用 `abort()` 函数或 C++ 异常处理程序显式引发。 `abort()` 函数会向进程发送 `SIGABRT` 信号，并导致进程异常终止。

​	如果进程接收到 `SIGABRT` 信号，操作系统将其发送给进程，并中断进程的正常执行流程。此时，进程通常会尝试处理该信号并进行恢复或退出。如果进程没有为 `SIGABRT` 信号设置信号处理程序，则默认行为是终止进程。

​	接着开始跟踪`EH`的调用栈获取函数`sample_test_eh`的实现。

```c++
static void sample_test_eh(JNIEnv *env, jobject thiz, jboolean with_context, jboolean signal_interrupted) {
  (void)env, (void)thiz;

  sample_test(SAMPLE_SOLUTION_EH, JNI_FALSE, with_context, signal_interrupted);
}
```

​	继续查看`sample_test`的实现。

```c++

static void sample_test(int solution, jboolean remote_unwind, jboolean with_context,
                        jboolean signal_interrupted) {
  // 将参数存储到全局变量
  g_solution = solution;
  g_remote_unwind = (JNI_TRUE == remote_unwind ? true : false);
  g_with_context = (JNI_TRUE == with_context ? true : false);
  g_signal_interrupted = (JNI_TRUE == signal_interrupted ? true : false);
  
  // 原子请求，为了保证获取到的g_frames_sz没问题
  __atomic_store_n(&g_frames_sz, 0, __ATOMIC_SEQ_CST);
  // 触发SIGABRT信号
  tgkill(getpid(), gettid(), SIGABRT);

  if ((solution == SAMPLE_SOLUTION_FP || solution == SAMPLE_SOLUTION_EH) &&
      __atomic_load_n(&g_frames_sz, __ATOMIC_SEQ_CST) > 0)
    // 根据堆栈的地址信息，打印堆栈日志
    xunwind_frames_log(g_frames, g_frames_sz, SAMPLE_LOG_TAG, SAMPLE_LOG_PRIORITY, NULL);
}
```

​	由于堆栈信息需要通过触发信号后，在信号处理函数中获取，所以这里的参数没办法传过去，这里就将参数放到了全局变量中。然后信号函数执行完毕后，将会填充`g_frames`调用栈的地址信息，最后使用`xunwind_frames_log`函数解析调用栈，最后输出详细的调用栈。

​	接下来查看`SIGABRT`信号的处理函数`sample_sigabrt_handler`的实现。

```java

static void sample_sigabrt_handler(int signum, siginfo_t *siginfo, void *context) {
  (void)signum, (void)siginfo;

  if (g_solution == SAMPLE_SOLUTION_FP || g_solution == SAMPLE_SOLUTION_EH) {
    if (!g_signal_interrupted) {
      if (g_solution == SAMPLE_SOLUTION_FP) {
        // FP local unwind
		...
      } else if (g_solution == SAMPLE_SOLUTION_EH) {
        // EH local unwind
        size_t frames_sz = xunwind_eh_unwind(g_frames, sizeof(g_frames) / sizeof(g_frames[0]),
                                             g_with_context ? context : NULL);
        __atomic_store_n(&g_frames_sz, frames_sz, __ATOMIC_SEQ_CST);
      }
    } else {
      // trigger a segfault, we will do "FP local unwind" in the sigsegv's signal handler
      ...
    }
  } else if (!g_remote_unwind) {
    // CFI local unwind
    ...
  } else {
    // CFI remote unwind
    ...
  }
}
```

​	`EH`方案是通过`xunwind_eh_unwind`函数获取的调用栈信息，继续查看其具体实现。

```c++
size_t xunwind_eh_unwind(uintptr_t *frames, size_t frames_cap, void *context) {
  return xu_eh_unwind(frames, frames_cap, context);
}

size_t xu_eh_unwind(uintptr_t *frames, size_t frames_cap, void *context) {
  if (NULL == frames || 0 == frames_cap) return 0;

  xu_eh_info_t info;
  info.frames = frames;
  info.frames_cap = frames_cap;
  info.frames_sz = 0;
  info.prev_sp = 0;
  info.uc = (ucontext_t *)context;

  _Unwind_Backtrace(xu_eh_unwind_cb, &info);

  return info.frames_sz;
}
```

​	`_Unwind_Backtrace`函数用于获取当前线程的调用堆栈信息。它使用`C++`异常处理机制中的`unwind`操作来实现，因此只能在支持`C++`异常处理的系统上使用。到这里就知道堆栈获取的来源了。但是这里的信息和真实看的还是有一定差距，继续看看`xunwind_frames_log`是如何对其进行转换展示的。

```c++
void xunwind_frames_log(uintptr_t *frames, size_t frames_sz, const char *logtag, android_LogPriority priority,
                        const char *prefix) {
  if (priority < ANDROID_LOG_VERBOSE || ANDROID_LOG_FATAL < priority) return;

  xu_printer_t printer;
  xu_printer_init_log(&printer, logtag, priority);

  xu_formatter_print(frames, frames_sz, prefix, &printer);
}
```

​	继续跟踪`xu_formatter_print`的实现。

```c++

void xu_formatter_print(uintptr_t *frames, size_t frames_sz, const char *prefix, xu_printer_t *printer) {
  if (NULL == frames || 0 == frames_sz) return;

  if (NULL == prefix) prefix = "";

  void *cache = NULL;
  xdl_info_t info;
  for (size_t i = 0; i < frames_sz; i++) {
    memset(&info, 0, sizeof(xdl_info_t));
    int r = 0;

    if (0 != frames[i]) {
      // 根据调用栈地址获取动态库的信息
      r = xdl_addr((void *)(frames[i]), &info, &cache);

      // 如果查找到的动态库的起始地址大于这条调用栈信息的地址，则从maps中重新找动态库信息
      char buf[512];
      if (0 == r || (uintptr_t)info.dli_fbase > frames[i])
        r = xu_formatter_maps_addr(frames[i], &info, buf, sizeof(buf));
    }

    // 输出打印
    if (0 == r || (uintptr_t)info.dli_fbase > frames[i])
      xu_printer_append_format(printer, XU_FORMATTER_PREFIX "<unknown>\n", prefix, i, frames[i]);
    else if (NULL == info.dli_fname || '\0' == info.dli_fname[0])
      xu_printer_append_format(printer, XU_FORMATTER_PREFIX "<anonymous:" XU_FORMATTER_ADDR ">\n", prefix, i,
                               frames[i] - (uintptr_t)info.dli_fbase, (uintptr_t)info.dli_fbase);
    else if (NULL == info.dli_sname || '\0' == info.dli_sname[0])
      xu_printer_append_format(printer, XU_FORMATTER_PREFIX "%s\n", prefix, i,
                               frames[i] - (uintptr_t)info.dli_fbase, info.dli_fname);
    else if (0 == (uintptr_t)info.dli_saddr || (uintptr_t)info.dli_saddr > frames[i])
      xu_printer_append_format(printer, XU_FORMATTER_PREFIX "%s (%s)\n", prefix, i,
                               frames[i] - (uintptr_t)info.dli_fbase, info.dli_fname, info.dli_sname);
    else
      xu_printer_append_format(printer, XU_FORMATTER_PREFIX "%s (%s+%" PRIuPTR ")\n", prefix, i,
                               frames[i] - (uintptr_t)info.dli_fbase, info.dli_fname, info.dli_sname,
                               frames[i] - (uintptr_t)info.dli_saddr);
  }
  xdl_addr_clean(&cache);
}

```

​	继续查看是如何输出的。

```c++
void xu_printer_append_format(xu_printer_t *self, const char *format, ...) {
  va_list ap;
  va_start(ap, format);

  char tmpbuf[1024];
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wformat-nonliteral"
  vsnprintf(tmpbuf, sizeof(tmpbuf), format, ap);
#pragma clang diagnostic pop

  va_end(ap);

  xu_printer_append_string(self, tmpbuf);
}


void xu_printer_append_string(xu_printer_t *self, const char *str) {
  if (XU_PRINTER_TYPE_LOG == self->type) {
    __android_log_print(self->data.log.priority, self->data.log.logtag, "%s", str);
  } else if (XU_PRINTER_TYPE_DUMP == self->type) {
    size_t len = strlen(str);
    if (len > 0) {
      xu_util_write(self->data.dump.fd, str, len);
      if ('\n' != str[len - 1]) xu_util_write(self->data.dump.fd, "\n", 1);
    }
  } else if (XU_PRINTER_TYPE_GET == self->type) {
    size_t len = strlen(str);
    if (len > 0) {
      xu_printer_string_append_to_buf(self, str);
      if ('\n' != str[len - 1]) xu_printer_string_append_to_buf(self, "\n");
    }
  }
}
```

​	到了最后输出的部分可以看到，支持三种方式输出，在调用时，根据不同的需求来选择合适的输出方式。

* `XU_PRINTER_TYPE_LOG` 直接`logcat`输出信息
* `XU_PRINTER_TYPE_DUMP `将堆栈信息写入到指定描述符
* `XU_PRINTER_TYPE_GET` 返回堆栈信息的字符串。

​	了解完整个实现原理后，最后看看其输出效果。`EH`方案的调用栈输出如下。

```
I/xunwind_tag: >>> EH: Local Process (pid: 6713), Current Thread (tid: 6713) <<<
I/xunwind_tag: #00 pc 00000000000093a4  /data/app/~~H824r8gCTUibCXd65QZfPw==/io.github.hexhacking.xunwind.sample-1gWu3tav0VA7-qGsCc7nZQ==/lib/arm64/libxunwind.so (xunwind_eh_unwind+72)
I/xunwind_tag: #01 pc 00000000000014a8  /data/app/~~H824r8gCTUibCXd65QZfPw==/io.github.hexhacking.xunwind.sample-1gWu3tav0VA7-qGsCc7nZQ==/lib/arm64/libsample.so
I/xunwind_tag: #02 pc 00000000000008b0  [vdso] (__kernel_rt_sigreturn+0)
I/xunwind_tag: #03 pc 000000000009e598  /apex/com.android.runtime/lib64/bionic/libc.so (tgkill+8)
I/xunwind_tag: #04 pc 0000000000001320  /data/app/~~H824r8gCTUibCXd65QZfPw==/io.github.hexhacking.xunwind.sample-1gWu3tav0VA7-qGsCc7nZQ==/lib/arm64/libsample.so
I/xunwind_tag: #05 pc 0000000000001254  /data/app/~~H824r8gCTUibCXd65QZfPw==/io.github.hexhacking.xunwind.sample-1gWu3tav0VA7-qGsCc7nZQ==/lib/arm64/libsample.so
I/xunwind_tag: #06 pc 0000000000222248  /apex/com.android.art/lib64/libart.so (art_quick_generic_jni_trampoline+152)
I/xunwind_tag: #07 pc 0000000000218bec  /apex/com.android.art/lib64/libart.so (art_quick_invoke_static_stub+572)
I/xunwind_tag: #08 pc 0000000000290300  /apex/com.android.art/lib64/libart.so (_ZN3art9ArtMethod6InvokeEPNS_6ThreadEPjjPNS_6JValueEPKc+536)
I/xunwind_tag: #09 pc 00000000003f09e4  /apex/com.android.art/lib64/libart.so (_ZN3art11interpreter34ArtInterpreterToCompiledCodeBridgeEPNS_6ThreadEPNS_9ArtMethodEPNS_11ShadowFrameEtPNS_6JValueE+404)
I/xunwind_tag: #10 pc 00000000003eb858  /apex/com.android.art/lib64/libart.so (_ZN3art11interpreter6DoCallILb0ELb0EEEbPNS_9ArtMethodEPNS_6ThreadERNS_11ShadowFrameEPKNS_11InstructionEtPNS_6JValueE+808)
I/xunwind_tag: #11 pc 00000000007658d0  /apex/com.android.art/lib64/libart.so (MterpInvokeStatic+984)
I/xunwind_tag: #12 pc 0000000000203998  /apex/com.android.art/lib64/libart.so (mterp_op_invoke_static+24)
I/xunwind_tag: #13 pc 00000000003e3688  /apex/com.android.art/lib64/libart.so (_ZN3art11interpreterL7ExecuteEPNS_6ThreadERKNS_20CodeItemDataAccessorERNS_11ShadowFrameENS_6JValueEbb+348)
I/xunwind_tag: #14 pc 000000000074920c  /apex/com.android.art/lib64/libart.so (artQuickToInterpreterBridge+780)
I/xunwind_tag: #15 pc 000000000022237c  /apex/com.android.art/lib64/libart.so (art_quick_to_interpreter_bridge+92)
I/xunwind_tag: #16 pc 000000000021160c  /apex/com.android.art/lib64/libart.so (nterp_helper+156)
I/xunwind_tag: #17 pc 0000000000218968  /apex/com.android.art/lib64/libart.so (art_quick_invoke_stub+552)
I/xunwind_tag: #18 pc 00000000002902d4  /apex/com.android.art/lib64/libart.so (_ZN3art9ArtMethod6InvokeEPNS_6ThreadEPjjPNS_6JValueEPKc+492)
I/xunwind_tag: #19 pc 000000000062ba5c  /apex/com.android.art/lib64/libart.so (_ZN3art12InvokeMethodILNS_11PointerSizeE8EEEP8_jobjectRKNS_33ScopedObjectAccessAlreadyRunnableES3_S3_S3_m+1388)
I/xunwind_tag: #20 pc 000000000059d2f8  /apex/com.android.art/lib64/libart.so (_ZN3artL13Method_invokeEP7_JNIEnvP8_jobjectS3_P13_jobjectArray+56)
I/xunwind_tag: #21 pc 0000000000222248  /apex/com.android.art/lib64/libart.so (art_quick_generic_jni_trampoline+152)
I/xunwind_tag: #22 pc 0000000000212524  /apex/com.android.art/lib64/libart.so (nterp_helper+4020)
I/xunwind_tag: #23 pc 00000000002132e8  /apex/com.android.art/lib64/libart.so (nterp_helper+7544)
I/xunwind_tag: #24 pc 00000000002124c8  /apex/com.android.art/lib64/libart.so (nterp_helper+3928)
I/xunwind_tag: #25 pc 00000000002124c8  /apex/com.android.art/lib64/libart.so (nterp_helper+3928)
I/xunwind_tag: #26 pc 00000000002115a8  /apex/com.android.art/lib64/libart.so (nterp_helper+56)
I/xunwind_tag: #27 pc 00000000002132e8  /apex/com.android.art/lib64/libart.so (nterp_helper+7544)
I/xunwind_tag: #28 pc 00000000002115a8  /apex/com.android.art/lib64/libart.so (nterp_helper+56)
I/xunwind_tag: #29 pc 00000000002124c8  /apex/com.android.art/lib64/libart.so (nterp_helper+3928)
I/xunwind_tag: #30 pc 00000000002115a8  /apex/com.android.art/lib64/libart.so (nterp_helper+56)
I/xunwind_tag: #31 pc 00000000002115a8  /apex/com.android.art/lib64/libart.so (nterp_helper+56)
I/xunwind_tag: #32 pc 0000000000218bec  /apex/com.android.art/lib64/libart.so (art_quick_invoke_static_stub+572)
I/xunwind_tag: #33 pc 0000000000290300  /apex/com.android.art/lib64/libart.so (_ZN3art9ArtMethod6InvokeEPNS_6ThreadEPjjPNS_6JValueEPKc+536)
I/xunwind_tag: #34 pc 000000000062ba5c  /apex/com.android.art/lib64/libart.so (_ZN3art12InvokeMethodILNS_11PointerSizeE8EEEP8_jobjectRKNS_33ScopedObjectAccessAlreadyRunnableES3_S3_S3_m+1388)
I/xunwind_tag: #35 pc 000000000059d2f8  /apex/com.android.art/lib64/libart.so (_ZN3artL13Method_invokeEP7_JNIEnvP8_jobjectS3_P13_jobjectArray+56)
I/xunwind_tag: #36 pc 0000000000222248  /apex/com.android.art/lib64/libart.so (art_quick_generic_jni_trampoline+152)
I/xunwind_tag: #37 pc 0000000000212524  /apex/com.android.art/lib64/libart.so (nterp_helper+4020)
I/xunwind_tag: #38 pc 00000000002132e8  /apex/com.android.art/lib64/libart.so (nterp_helper+7544)
I/xunwind_tag: #39 pc 0000000000218bec  /apex/com.android.art/lib64/libart.so (art_quick_invoke_static_stub+572)
I/xunwind_tag: #40 pc 0000000000290300  /apex/com.android.art/lib64/libart.so (_ZN3art9ArtMethod6InvokeEPNS_6ThreadEPjjPNS_6JValueEPKc+536)
I/xunwind_tag: #41 pc 000000000062c1b4  /apex/com.android.art/lib64/libart.so (_ZN3art17InvokeWithVarArgsIPNS_9ArtMethodEEENS_6JValueERKNS_33ScopedObjectAccessAlreadyRunnableEP8_jobjectT_St9__va_list+452)
I/xunwind_tag: #42 pc 000000000062c678  /apex/com.android.art/lib64/libart.so (_ZN3art17InvokeWithVarArgsIP10_jmethodIDEENS_6JValueERKNS_33ScopedObjectAccessAlreadyRunnableEP8_jobjectT_St9__va_list+96)
I/xunwind_tag: #43 pc 0000000000507c68  /apex/com.android.art/lib64/libart.so (_ZN3art3JNIILb1EE21CallStaticVoidMethodVEP7_JNIEnvP7_jclassP10_jmethodIDSt9__va_list+620)
I/xunwind_tag: #44 pc 00000000000aeac8  /system/lib64/libandroid_runtime.so (_ZN7_JNIEnv20CallStaticVoidMethodEP7_jclassP10_jmethodIDz+124)
I/xunwind_tag: #45 pc 00000000000ba060  /system/lib64/libandroid_runtime.so (_ZN7android14AndroidRuntime5startEPKcRKNS_6VectorINS_7String8EEEb+840)
I/xunwind_tag: #46 pc 00000000000025a8  /system/bin/app_process64 (main+1364)
I/xunwind_tag: #47 pc 00000000000498cc  /apex/com.android.runtime/lib64/bionic/libc.so (__libc_init+100)
I/xunwind_tag: >>> finished <<<
```

### 12.6.2 优化调用栈样例

​	尽管在该工具中的样例可以直接使用，但是想要将其内置到`AOSP`中还需要将其进行优化处理，简单写一个模拟注入流程的样例，对样例做出以下调整。

* 去掉非`EH`获取方案的代码部分
* 优化获取调用栈信息的代码，让其结果仅输出想要关注的目标动态库的调用栈。
* 直接输出日志调整为返回调用栈字符串。

​	新建`native`的项目，将`xUnwind`的样例`apk`解压后，取出其`lib`目录中的依赖动态库，将其复制到新项目的`libs`目录中，如下图。

​	

### 12.6.3 内置获取调用栈
