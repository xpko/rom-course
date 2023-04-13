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

​	

## 12.4 JNI调用分析



## 12.5 打桩函数分类



## 12.6 调用栈展示



## 12.7 解析参数和返回值

