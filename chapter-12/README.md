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

​	到这里就成功从配置文件中读取数据，并解析后通过`native`函数将其存储到全局能访问的位置了。

## 12.4 JNI调用分析



## 12.5 打桩函数分类



## 12.6 调用栈展示



## 12.7 解析参数和返回值



