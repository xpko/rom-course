# 第十一章 反调试

​	反调试是指在软件运行时，防止恶意用户或者黑客使用调试器来分析和修改程序的行为。在安卓系统中，反调试技术是应用程序开发中非常重要的一部分，因为它可以提高应用程序的安全性，防止黑客攻击和数据泄露。另一方面，恶意软件也通过反调试技术，防止安全系统与软件对其进行分析，因此，安全从业有必要了解常见的反调试对抗技术。

​	在本章中，我们将介绍反调试的概念、原理和常见的反调试方案，以及如何对这些方案进行相应的安全对抗。

## 11.1 反调试常见手段

​	在`Android`逆向分析中，最常见的情况就是攻防的对抗，攻击者通过对样本进行静态分析，以及动态调试等手段，获取想要的信息。而保护方则通过对混淆，以及多种加固方式，来对自己的重要信息进行保护。例如使用加固的手段来干扰攻击者的静态分析，通过检测环境来对抗攻击者注入`hook`函数，添加各种检测调试来阻止攻击者动态分析。

### 11.1.1 检测调试标志

​	调试软件离不开调试器，而调试器又高度依赖`ptrace`。`ptrace`是`Linux`操作系统提供的一个系统调用，它允许一个进程监控另一个进程的执行，并能够在运行时修改它的寄存器和内存等资源。`ptrace`通常被用于调试应用程序、分析破解软件以及实现进程间沙盒隔离等场景。

​	使用`ptrace`来监控目标进程时，需要以`tracer`(追踪者)的身份启动一个新的进程，然后通过`ptrace`函数来请求操作系统将目标进程挂起并转交给`tracer`进程。一旦目标进程被挂起，`tracer`进程就可以读写其虚拟地址空间中的数据、修改寄存器值、单步执行指令等操作。当`tracer`完成了对目标进程的调试操作后，可以通过`ptrace`函数将控制权还原到目标进程上，使其继续执行。

​	由于`ptrace`功能的强大，它也被广泛应用于破解软件、恶意攻击等场景。因此，在一些安全敏感的场合，为了防止恶意攻击者使用`ptrace`来监控和修改进程的行为，需要采取一些反调试的手段来加强保护。

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
adb push android_server64 /data/local/tmp/
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

​	当使用 `IDA` 进行调试时，`IDA` 会创建一个调试器进程，并将其作为目标进程的父进程。但是，由于目标进程最初是由 `zygote`进程`fork`出来的，因此在查询其父进程`id`时，仍然会返回`zygote`进程的`id`。这并不意味着调试器进程没有被正确设置为目标进程的父进程。实际上，在`IDA`调试过程中，目标进程的执行状态确实是由调试器进程所控制的。因此，即使查询到的父进程`id`不正确，也不会影响`IDA`对目标进程的控制和调试操作。

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

​	除了`status`文件外，`/proc/<pid>/wchan`文件同样可以用来检测。下面是调试附加前，和附加后的对比。

```
// 附加前
SyS_epoll_wait

// 附加后，中断时
ptrace_stop
```

​	文件`/proc/<pid>/stat`也可以用来检测，当进程被中断等待时，内容将会由`S`变成`t`。对比如下。

```
// 附加前
 S 1027 1027 0 0 -1 1077952832 29093 4835 0 0 81 9 0 0 20 0 19 0 424763 15088168960 24716 18446744073709551615 1 1 0 0 0 0 4612 1 1073775864 0 0 0 17 0 0 0 0 0 0 0 0 0 0 0 0 0 0

// 附加后
t 1027 1027 0 0 -1 1077952832 29405 4835 0 0 81 9 0 0 20 0 19 0 424763 15088168960 24987 18446744073709551615 1 1 0 0 0 0 4612 1 1073775864 0 0 0 17 1 0 0 0 0 0 0 0 0 0 0 0 0 0
```

### 11.1.2 禁止调试器附加

​	由于动态调试基本都是依赖`ptrace`对进程追踪，那么可以通过了解`ptrace`的使用特性，来针对性的检查自身是否被调试了。由于`ptrace`附加进程时，目标进程同时只能被一个进程附加，第二次附加就会失败，那么通过对自身进行`ptrace`处理，如果发现对自己进行附加失败，说明已经被调试了。同时对自身附加后，也能阻止其他进程再对其进行附加调试。下面看实现代码。

```c++
extern "C" JNIEXPORT jstring JNICALL
Java_cn_mik_nativedemo_MainActivity_stringFromJNI(
        JNIEnv* env,
        jobject /* this */) {
    std::string hello = "Hello from C++";
    prctl(PR_SET_PTRACER, PR_SET_PTRACER_ANY, 0, 0, 0);
    pid_t pid = getpid();
    int ret=ptrace(PTRACE_TRACEME,pid, 0, 0);
    // 检测是否正在被调试
    if (ret < 0) {
        ALOGD("I'm being debugged! %d\n",ret);
    } else {
        ALOGD("Not being debugged %d\n",ret);
    }
    return env->NewStringUTF(hello.c_str());
}
```

​	在`AOSP12`中，为了增强`Android`系统的安全性，`Google`限制了应用程序使用`ptrace`对自身进行调试。在当前进程中调用`ptrace(PTRACE_TRACEME)`函数将始终返回-1。但是我们可以创建一个子进程，来进行测试。下面是调整后的代码。

```c++
extern "C" JNIEXPORT jstring JNICALL
Java_cn_mik_nativedemo_MainActivity_stringFromJNI(
        JNIEnv* env,
        jobject /* this */) {
    std::string hello = "Hello from C++";
    pid_t mypid = getpid();
    pid_t pid = fork();
    if (pid == -1) {
        perror("fork");
        exit(1);
    } else if (pid == 0 ) {
        // 这里是子进程的代码
        ALOGD("I'm child process, my PID is %d\n", getpid());
        int ret=ptrace(PTRACE_TRACEME,0, 0, 0);
        // 检测是否正在被调试
        if (ret < 0) {
            ALOGD("I'm being debugged! %d\n",ret);
        } else {
            ALOGD("Not being debugged %d\n",ret);
            sleep(30);
        }
    } else {
        // 这里是父进程的代码
        ALOGD("I'm parent process, my PID is %d and my child's PID is %d\n", mypid, pid);
    }
    return env->NewStringUTF(hello.c_str());
}
```

​	然后使用`ida`尝试对子进程进行调试，发现无法正常附加该进程了，错误如下。

![image-20230405162058014](.\images\ida_attach_err.png)

### 11.1.4 检测跟踪工具

除了常规调试器，一些安全分析工具都具备调试跟踪功能。比如Frida，可以向目标程序中注入Javascript脚本，来Hook跟踪与修改程序的执行状态。在执行反调试检测时，这类工具也是需要重点关注的对象。

使用Frida时，需要在设备上执行`frida-server`命令。检测Frida的思路来源于该工具运行时的文件与进行特征信息。例如，执行Frida注入代码到一个程序后，它的`/proc/pid/maps`中有留有注入的动态库的痕迹：

```
$ adb shell pidof com.android.settings
$ frida -U -p 27507
     ____
    / _  |   Frida 16.0.12 - A world-class dynamic instrumentation toolkit
   | (_| |
    > _  |   Commands:
   /_/ |_|       help      -> Displays the help system
   . . . .       object?   -> Display information about 'object'
   . . . .       exit/quit -> Exit
   . . . .
   . . . .   More info at https://frida.re/docs/home/
   . . . .
   . . . .   Connected to Android Emulator 5554 (id=emulator-5554)

[Android Emulator 5554::PID::27507 ]->
[Android Emulator 5554::PID::27507 ]-> Process.enumerateModules().filter(m => {
            // console.log(m.path)
            var ret = false
            if (m.path) {
                if (m.path.includes("frida")) {
                    console.log(m.path)
                }
            }
})
/data/local/tmp/re.frida.server/frida-agent-64.so
[]
```

`Process.enumerateModules()`执行后返回的是`/proc/self/maps`的内容，这里过滤显示留住`frida`字符串的路径。可以看到，输出中有`/data/local/tmp/re.frida.server/frida-agent-64.so`。这是`frida-server`注入代码时释放的动态库。检测它就能检测到程序注入了Frida。


### 11.1.4 系统调试检测接口

​	除了以上这两种比较常见的检测方式外，还有很多种方式进行检测，这些检测大多都是围绕着调试过程会产生的特征来进行检测，在真实的保护场景下，开发者会结合多种方案检测来防止被攻击者动态调试。以下是其他检测方案的介绍。

* `Android`本身提供的`api`判断是否被调试中，`android.os.Debug.isDebuggerConnected()`，这样的检测方法非常容易被`Hook`修改替换。
* 调试器默认端口检测，例如`ida`默认使用的`23946`，以及调试进程名检测，例如前文中看到的`android_server`进程名称，这种检测方式同样很容易被处理，攻击者会修改默认端口，以及进程名称。
* 运行效率检测，在函数执行过程计算执行消耗的时间，正常情况下执行效率是非常快的，如果时间较长，说明很有可能被人单步调试中。这种方式属于后知后觉，并不能根本性的阻止对方调试。
* 断点指令检测，调试器在调试时，会在`so`的代码部分插入`breakpoint`指令，可以通过获取目标`so`的可执行部分，搜索其中是否存在断点的指令。
* `ro.debuggable`是一个系统级属性，当在调试模式时，该值为1，否则是0，所以有时也会被拿来检测是否被调试中。

​	除了一些常规的检测反调试，还有一些措施是针对反反调试的，例如通常情况下，检测`/proc/<pid>/status`中的`TracerPid`来判断是否被调试了，而开发者同时也知道，攻击者会选择将`status`文件重定向，或者采取其他方式，让`TracerPid`固定返回0，而这种情况，可以先检测，是否有攻击者将`status`文件进行的特殊出合理，例如先对自己的进程使用`ptrace`，然后检测`status`中的`TracerPid`是否有变更，如果结果为0，说明是被攻击者使用某种手段篡改了该值。

​	由于大多数情况下，反调试手段会被攻击者使用各种`Hook`的方式进行替换处理，所以有些开发者会采用非常规的手段来获取，用来判断是否为调试状态的信息。例如内联汇编通过`svc`来执行对应的系统调用。


## 11.2 常见反调试绕过方案

围绕常见的反调试技术，都有相应的反反调试，也就是反调试绕过技术方案。

1. Hook技术
Hook技术是一种常见的反调试绕过方案。它可以修改目标进程的内存数据与代码，绕过应用程序的反调试技术。Hook技术在程序运行时替换函数的实现，从而绕过应用程序的反调试技术。例如，使用Frida注入程序，然后修改进程的调试标志读取接口，修改返回的内容，即可完成自身的调试标志检测。

2. 内存修改技术
内存修改技术是一种常见的反调试绕过方案，它可以让黑客修改应用程序的内存，从而绕过应用程序的反调试技术。例如，可以使用内存修改工具来修改应用程序的内存，从而绕过应用程序的反调试技术。

3. 反编译技术
反编译技术是一种常见的反调试绕过方案，通过分析App程序的代码，反编译修改掉代码中的反调试检测逻辑部分，从而绕过应用程序的反调试技术。这种技术需要对目标程序进行大量的分析工作，结合多个工具执行反编译与重打包，在安卓安全技术相对不成熟的时期，这种方案被大量使用。目前，使用Hook方案与系统级别反反调试技术的场景会更加普遍。

4. 系统级别反反调试技术
系统级别反反调试技术是一种底层的反调试绕过方案，它通过修改系统反调试相关的代码逻辑，让系统输出程序为非调试状态。这种绕过应用程序的反调试技术比较稳定，且不易被检测，是一种常用的反反调试技术。


## 11.3 系统层面解决反调试

​	了解常见的反调试检测后，就可以对其进行修改，这些修改并不会完美解决反调试的所有问题，主要是处理掉一些常规的检测办法。来尽量减少分析成本。下面开始简单的对几种检测方式进行修改处理。


### 11.3.1 过系统调试检测接口检测

​	然后修改属性`ro.debuggable`的值，让其固定显示为0，修改文件`build/make/core/main.mk`，修改代码如下。

```
# ADDITIONAL_SYSTEM_PROPERTIES += ro.debuggable=1
ADDITIONAL_SYSTEM_PROPERTIES += ro.debuggable=0
```

​	函数`__android_log_is_debuggable`是`AOSP`中用来快速获取`ro.debuggable`属性的，将该函数默认返回值修改为1。修改如下。

```c++
int __android_log_is_debuggable() {
    return 1;
//  static int is_debuggable = [] {
//    char value[PROP_VALUE_MAX] = {};
//    return __system_property_get("ro.debuggable", value) > 0 && !strcmp(value, "1");
//  }();
//
//  return is_debuggable;
}
```

这样修改后的系统代码，检测"ro.debuggable"将永远返回0，但不影响我们使用调试相关的能力。


### 11.3.2 过调试标志检测


​	除此之外，还有多个针对调试标志检测的处理，修改内核文件`fs/proc/array.c`，修改如下。

```c++
static inline void task_state(struct seq_file *m, struct pid_namespace *ns,
				struct pid *pid, struct task_struct *p)
{
	struct user_namespace *user_ns = seq_user_ns(m);
	struct group_info *group_info;
	int g, umask;
	struct task_struct *tracer;
	const struct cred *cred;
	pid_t ppid, tpid = 0, tgid, ngid;
	unsigned int max_fds = 0;

	rcu_read_lock();
	ppid = pid_alive(p) ?
		task_tgid_nr_ns(rcu_dereference(p->real_parent), ns) : 0;

	tracer = ptrace_parent(p);
	if (tracer)
		tpid = task_pid_nr_ns(tracer, ns);
	// 固定tpid为0
	tpid=0;
	...
}
```

​	在这里的`tpid`就是前文中`status`中的`TracerPid`。被调试时，该值将是调试进程`id`，但是考虑到刚刚说的反反调试检测的情况，不能直接固定将文件中的调试特征去掉，而是添加控制，当我们需要调试时，才让其调试的特征不要被检测。这里可以通过应用层和内核层交互，传递参数过来，当该参数的值为1时，就修改其过滤掉调试特征。这里就不详细展开了，继续看下一个特征的修改。

​	同样是在这个文件中，修改函数`get_task_state`，这里同样可以优化成，由值来控制是否使用新的数组，修改内容如下。

```c++
static const char * const task_state_array[] = {
	"R (running)",		/*   0 */
	"S (sleeping)",		/*   1 */
	"D (disk sleep)",	/*   2 */
	"T (stopped)",		/*   4 */
	"t (tracing stop)",	/*   8 */
	"X (dead)",		/*  16 */
	"Z (zombie)",		/*  32 */
};
// 将上面的数组拷贝一个，将T (stopped) 和t (tracing stop)都修改为S (sleeping)
static const char * const task_state_array_no_debug[] = {
	"R (running)",		/*   0 */
	"S (sleeping)",		/*   1 */
	"D (disk sleep)",	/*   2 */
	"S (sleeping)",		/*   4 */
	"S (sleeping)"	,	/*   8 */
	"X (dead)",		/*  16 */
	"Z (zombie)",		/*  32 */
};

static inline const char *get_task_state(struct task_struct *tsk)
{
	unsigned int state = (tsk->state | tsk->exit_state) & TASK_REPORT;

	/*
	 * Parked tasks do not run; they sit in __kthread_parkme().
	 * Without this check, we would report them as running, which is
	 * clearly wrong, so we report them as sleeping instead.
	 */
	if (tsk->state == TASK_PARKED)
		state = TASK_INTERRUPTIBLE;
	// 修改使用新定义的数组
	BUILD_BUG_ON(1 + ilog2(TASK_REPORT) != ARRAY_SIZE(task_state_array_no_debug)-1);
	// 使用新定义的数组
	return task_state_array_no_debug[fls(state)];
}
```

​	最后处理`wchan`的对应代码，修改内核文件`fs/proc/base.c`，相关修改如下。

```c++
static int proc_pid_wchan(struct seq_file *m, struct pid_namespace *ns,
			  struct pid *pid, struct task_struct *task)
{
	unsigned long wchan;
	char symname[KSYM_NAME_LEN];

	wchan = get_wchan(task);

	if (wchan && ptrace_may_access(task, PTRACE_MODE_READ_FSCREDS)
			&& !lookup_symbol_name(wchan, symname))
		seq_printf(m, "%s", symname);
	else{
        // add
		if (strstr(symname,"trace")){
			seq_printf(m, "%s", "SyS_epoll_wait");
		}
        // addend
		seq_putc(m, '0');
	}
	return 0;
}
```

## 11.4 集成反反调试功能

所有这些对系统的修改，都是针对不同场景反调试而产生的对应解决方案，需要重新编译系统代码。涉及内核代码的部分，需要重新编译内核，涉及framework的部分编译生成ROM。整个过程可以编写自动化操作脚本，将重复性的工作做简化处理。

在实践过程中，调试与反调试技术都是随时攻防的不断升级实时变化的，例如，有一些软件壳会对系统状态与接口作检测，这个时候，这里介绍的一些公开的方法可能就失效了。这种情况下，需要结合实际，使用安全分析技术，对目标程序做进一步的分析，确定其使用的反调试技术，重新调整系统文件修改点，然后编译打包测试效果。

