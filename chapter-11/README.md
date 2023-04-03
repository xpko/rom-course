# 第十一章 反调试

## 11.1 反调试常见手段

​	在`Android`逆向分析中，最常见的情况就是攻防的对抗，攻击者通过对样本进行静态分析，以及动态调试等手段，获取想要的信息。而保护方则通过对混淆，以及多种加固方式，来对自己的重要信息进行保护。例如使用加固的手段来干扰攻击者的静态分析，通过检测环境来对抗攻击者注入`hook`函数，添加各种检测调试来阻止攻击者动态分析。

​	`ptrace`是`Linux`操作系统提供的一个系统调用，它允许一个进程监控另一个进程的执行，并能够在运行时修改它的寄存器和内存等资源。`ptrace`通常被用于调试应用程序、分析破解软件以及实现进程间沙盒隔离等场景。

​	使用`ptrace`来监控目标进程时，需要以`tracer`(追踪者)的身份启动一个新的进程，然后通过`ptrace`函数来请求操作系统将目标进程挂起并转交给`tracer`进程。一旦目标进程被挂起，`tracer`进程就可以读写其虚拟地址空间中的数据、修改寄存器值、单步执行指令等操作。当`tracer`完成了对目标进程的调试操作后，可以通过`ptrace`函数将控制权还原到目标进程上，使其继续执行。

​	由于`ptrace`功能的强大，它也被广泛应用于破解软件、恶意攻击等场景。因此，在一些安全敏感的场合，为了防止恶意攻击者使用`ptrace`来监控和修改进程的行为，需要采取一些反调试的手段来加强保护。

### 11.1.1 根据文件检测

​	通过在被保护程序中定期检测其父进程是否为指定的`tracer`进程，可以避免恶意攻击者使用`ptrace`跟踪程序的执行流程。

​	接下来写一个简单的实例来进行测试。`Android Studio`创建`native c++`的项目。修改函数如下。

```c++
#include <jni.h>
#include <string>
#include <unistd.h>
#include <android/log.h>

#define LOG_TAG "native-lib"
#define ALOGD(...) __android_log_print(ANDROID_LOG_DEBUG  , LOG_TAG, __VA_ARGS__)

extern "C" JNIEXPORT jstring JNICALL
Java_cn_mik_nativedemo_MainActivity_stringFromJNI(
        JNIEnv* env,
        jobject /* this */) {
    std::string hello = "Hello from C++";
    int ppid= getppid();
    ALOGD("my ppid=%d",ppid);
    return env->NewStringUTF(hello.c_str());
}
```

​	然后添加一个按钮，每次点击时则调用该函数，便于随时观测到`ppid`的变化。

```java
Button btn1;
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    binding = ActivityMainBinding.inflate(getLayoutInflater());
    setContentView(binding.getRoot());

    TextView tv = binding.sampleText;
    tv.setText(stringFromJNI());
    btn1=findViewById(R.id.button);
    btn1.setOnClickListener(v->{
        tv.setText(stringFromJNI());
    });
}
```

​	在调用该函数时，就会打印其`ppid`（父进程`id`）。运行该函数后输出如下。

```
cn.mik.nativedemo D/native-lib: my ppid=1053
```

​	然后查看该进程`id`对应哪个进程。

```
adb shell 
ps -e|grep 1053

// 输出如下
root          1053     1 14644500 115568 0                  0 S zygote64
```

​	发现该进程是`zygote`进程，说明没有被调试。接下来使用`ida`调试该进程。找到`ida`下的`dbgsrv`目录，将其中的`android_server64`拷贝到`Android`系统中，将调试的端口`23946`转发到本地。并且将该服务启动起来，操作如下。

```
adb push "D:\tools\IDA Pro 7.6\dbgsrv\android_server64" /data/local/tmp/

adb forward tcp:23946 tcp:23946

adb shell

cd /data/local/tmp/

chmod +x ./android_server64

su

./android_server64

```

​	接下来打开`ida`，选择`Debugger->Attach->Remote Arm linux/android debugger`，在`hostname`选项中填本地回环地址`127.0.0.1`，如下图。

![image-20230403223624911](.\images\ida_debug_attach.png)

​		点击`ok`后，则会展示所有`Android`中的进程，在其中进行过滤，找到目标进程。如下图

![image-20230403223830842](.\images\ida_debug_process.png)

​	成功挂起调试后，检查日志中的 `ppid`，发现并没有任何变化，依然是`zygote`作为父进程。

​	当使用 `IDA` 进行调试时，`IDA` 会创建一个调试器进程，并将其作为目标进程的父进程。但是，由于目标进程最初是由 `zygote `进程` fork `出来的，因此在查询其父进程` id` 时，仍然会返回` zygote `进程的 `id`。这并不意味着调试器进程没有被正确设置为目标进程的父进程。实际上，在`IDA`调试过程中，目标进程的执行状态确实是由调试器进程所控制的。因此，即使查询到的父进程`id`不正确，也不会影响`IDA`对目标进程的控制和调试操作。

​	尽管查询`ppid`无法判断出进程被调试了，但是依然有其他地方会出现被调试的信息，例如`/proc/<pid>/status`文件中的字段`TracerPid`，就能看到调试进程的`id`。下面查看该文件。

```
// 没有调试时的文件内容
Name:   .mik.nativedemo
Umask:  0077
State:  S (sleeping)
Tgid:   7759
Ngid:   0
Pid:    7759
PPid:   1053
TracerPid:      0

// ida附加调试后的文件内容

Name:   .mik.nativedemo
Umask:  0077
State:  t (tracing stop)
Tgid:   7759
Ngid:   0
Pid:    7759
PPid:   1053
TracerPid:      7525
```

​	查看该`id`对应哪一个进程。

```
ps -e|grep 7525

// 显示结果
root          7525  7523 10803524 33392 0                   0 S android_server64
```

​	除了`status`文件外，`wchan`文件同样可以用来检测。下面是调试附加前，和附加后的对比。

```
// 附加前
SyS_epoll_wait

// 附加后，中断时
ptrace_stop
```

### 11.1.2 根据ptrace的特性检测

​	

## 11.2 常见反调试绕过方案



## 11.3 系统层面如何解决反调试



## 11.4 集成反调试功能



## 11.5 Android下的硬件调试

### 11.5.1 什么是硬件调试

### 11.5.2 开启Android的硬件调试

### 11.5.3 硬件调试测试



