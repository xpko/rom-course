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

### 11.1.2 根据ptrace的特性检测

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

### 11.1.3 其他检测方式

​	除了以上这两种比较常见的检测方式外，还有很多种方式进行检测，这些检测大多都是围绕着调试过程会产生的特征来进行检测，在真实的保护场景下，开发者会结合多种方案检测来防止被攻击者动态调试。以下是其他检测方案的介绍。

* `Android`本身提供的`api`判断是否被调试中，`android.os.Debug.isDebuggerConnected()`，这样的检测方法非常容易被`Hook`修改替换。
* 调试器默认端口检测，例如`ida`默认使用的`23946`，以及调试进程名检测，例如前文中看到的`android_server`进程名称，这种检测方式同样很容易被处理，攻击者会修改默认端口，以及进程名称。
* 运行效率检测，在函数执行过程计算执行消耗的时间，正常情况下执行效率是非常快的，如果时间较长，说明很有可能被人单步调试中。这种方式属于后知后觉，并不能根本性的阻止对方调试。
* 断点指令检测，调试器在调试时，会在`so`的代码部分插入`breakpoint`指令，可以通过获取目标`so`的可执行部分，搜索其中是否存在断点的指令。
* `ro.debuggable`是一个系统级属性，当在调试模式时，该值为1，否则是0，所以有时也会被拿来检测是否被调试中。

​	除了一些常规的检测反调试，还有一些措施是针对反反调试的，例如通常情况下，检测`/proc/<pid>/status`中的`TracerPid`来判断是否被调试了，而开发者同时也知道，攻击者会选择将`status`文件重定向，或者采取其他方式，让`TracerPid`固定返回0，而这种情况，可以先检测，是否有攻击者将`status`文件进行的特殊出合理，例如先对自己的进程使用`ptrace`，然后检测`status`中的`TracerPid`是否有变更，如果结果为0，说明是被攻击者使用某种手段篡改了该值。

​	由于大多数情况下，反调试手段会被攻击者使用各种`Hook`的方式进行替换处理，所以有些开发者会采用非常规的手段来获取，用来判断是否为调试状态的信息。例如内联汇编通过`svc`来执行对应的系统调用。

## 11.2 系统层面的反调试

​	了解常见的反调试检测后，就可以对症进行修改，这些修改并不会完美解决反调试的所有问题，主要是处理掉一些常规的检测办法。来尽量减少分析成本。下面开始简单的对几种检测方式进行修改处理。

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

​	除此之外，还有多个针对文件检测的处理，修改文件`android-kernel/private/msm-google/fs/proc/array.c`，修改如下。

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

​	最后处理`wchan`的对应代码，修改文件`android-kernel/private/msm-google/fs/proc/base.c`，相关修改如下。

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

## 11.3 Android下的硬件断点

​	在调试中，可以通过对程序下不同类型的断点，来辅助分析代码，其中最常见的就是软件断点，软件断点是通过将原有的指令进行替换，在`ARM64`架构中，软件断点通常是通过将原有的指令替换为`BRK`指令`（opcode为0xD4200000）`来实现的。当程序执行到该指令时，处理器会触发一个异常`（trap exception）`，从而停止程序的运行。

​	在软件断点的基础上添加条件判断，就是一个条件断点了，只有满足指定条件才会触发该软件断点。

​	内存断点，是通过修改指定内存的访问属性，让其触发异常，来实现中断的效果。在程序运行时，将要监视的内存地址标记为不可访问，当程序尝试访问该地址时，会触发一个异常，并且操作系统会中断该进程的执行。然后，调试器会根据异常信息来确定是哪个内存地址引起了中断，并且可以进行相应的处理和调试工作。内存断点的实现与硬件断点或软件断点不同，它需要操作系统提供的支持才能实现。由于内存断点的实现需要修改系统的内存映射表等底层数据结构，因此可能会影响程序的性能和稳定性。应该谨慎地选择要监视的内存地址，并避免过多地使用内存断点。

### 11.3.1 什么是硬件断点

​	硬件断点是通过CPU内置的调试功能实现的。当程序执行到设置了硬件断点的地址时，CPU会发出一个异常信号，从而让操作系统停止当前进程的执行。然后，操作系统将控制权转移给调试器，并通知调试器哪个线程触发了异常，以便调试器可以进行相应的调试工作。

​	在ARM架构下，硬件断点主要有两种类型：执行断点和数据断点。执行断点可以用于监视代码执行，当程序尝试执行指定的指令时触发中断；数据断点则可以用于监视内存读写操作，当程序尝试访问指定的内存地址时触发中断。执行断点和数据断点都由CPU硬件实现，因此响应速度很快，但数量有限。

### 11.3.2 开启Android的硬件调试

​	在开始硬件断点的使用前，首先要进行环境的准备，下面的测试案例将使用`22.0`版本`ndk`中的`gdb`来调试。然后检查当前内核编译选项中是否开启了硬件断点支持。下面是查询过程。

```bash
adb shell

zcat /proc/config.gz |grep -i BREAKPOINT

// 显示内容如下
CONFIG_HAVE_HW_BREAKPOINT=y
```

​	如果你的结果显示为`n`，则说明需要在内核中修改配置，不要直接去修改`defconfig`配置，而是使用命令生成`.config`文件，然后修改`.config`文件，再由该文件生成对应的`defconfig`，再将其覆盖原文件，最后重新编译。具体的操作过程如下。

```
cd /root/android_src/android-kernel/private/msm-google

// b1c1_defconfig是当前设备使用的对应配置，b1c1表示的是pixel3和pixel3 XL的代号
// 第一步会在当前目录生成.config文件
make ARCH=arm64 b1c1_defconfig

// 使用图形界面来开启配置，修改完成后记得保存
make ARCH=arm64 menuconfig

// 如果不想在图形界面编辑，可以直接修改.config文件
vim .config

// 添加选项
CONFIG_HAVE_HW_BREAKPOINT=y
CONFIG_HAVE_ARCH_TRACEHOOK=y

// 选项添加完成后，保存配置，将会生成新的b1c1_defconfig文件
make ARCH=arm64 savedefconfig

// 替换原文件
cp defconfig arch/arm64/configs/b1c1_defconfig

cd /root/android_src/android-kernel

// 重新编译
./build/build.sh
```

​	编译完成，重新刷入手机后，再次查询配置就能看到该选项被开启了。

​	`GEF（GDB Enhanced Features）`是一个用于`GDB`调试器的`Python`扩展框架，提供了一些额外的功能，使得在调试过程中更加便捷和高效。`GEF`具有丰富的命令行界面和可扩展性，可以通过编写`Python`脚本来自定义其功能。以下是`GEF`的特点：

1. 命令行界面友好：`GEF`提供了易于使用的命令行界面，支持自动补全、历史记录和语法高亮等功能，使得调试过程更加简单和快速。
2. 调试功能强大：`GEF`提供了一系列额外的调试功能，如内存断点、硬件断点、`ASM`混淆解析等，可以显著提高调试效率。
3. 可扩展性好：`GEF`基于`Python`开发，支持编写自定义脚本来扩展其功能，用户可以根据自己的需求进行定制化。
4. 平台支持广泛：`GEF`支持多种操作系统和处理器架构，如`Linux、macOS、Windows`，以及`ARM、x86`等常见的处理器架构。
5. 社区活跃：`GEF`是一个开源项目，拥有庞大的用户群体和贡献者团队，开发进程活跃，问题能够及时得到解决。

​	安装`GEF`非常简单，一句命令即可完成安装。

```
bash -c "$(curl -fsSL https://gef.blah.cat/sh)"
```

### 11.3.3 硬件断点测试

​	环境准备就绪后，开发一个简单的应用作为被硬件断点的目标，声明两个全局变量，分别为`int`类型和`char`数组，然后分别对两个变量进行访问和写入。下面是样例代码。

```c++
int test1=1024;
char test2[100];

extern "C" JNIEXPORT jstring JNICALL
Java_cn_mik_nativedemo_MainActivity_stringFromJNI(
        JNIEnv* env,
        jobject /* this */) {
    std::string hello = "Hello from C++";
    memset(test2,0,100);
    strcpy(test2,"demo");
    ALOGD("test1",test1);
    ALOGD("test2",test2);
    return env->NewStringUTF(hello.c_str());
}
```

​	安装该测试样例后，接着将`ndk`中的`gdbserver`传入手机中。命令如下。

```
adb push '/home/king/Android/Sdk/ndk/23.1.7779620/prebuilt/android-arm64/gdbserver/gdbserver'  /data/local/tmp/

adb shell

su

cd /datalocal/tmp

chmod +x ./gdbserver

// 在手机上打开测试应用后，查看该应用的pid
ps -e|grep nativedemo

// 设置
./gdbserver :1234 --attach 5991
```

​	接下来使用`gdb`连接上手机中的`gdbserver`，这里需要注意，使用的`gdb`和`gdbserver`的版本需要对应，否则就会导致连接错误的问题。下面是连接的相关操作。

```
// 将gdbserver监听的端口转发到本地
adb forward tcp:1234 tcp:1234

gdb

// 连接监听的端口
target remote :1234

```



