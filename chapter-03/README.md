# 第三章 认识系统组件 #

## 3.1 源码结构介绍

​	在上一章的学习中，我们成功编译了Android12以及对应的内核，并且通过多种方式刷入手机。接下来我们需要先对Android源码的根结构有一定的了解，对结构有一定了解能帮助我们更快的定位和分析源码，同时能让开发人员更好的理解Android系统。

​	Android源码结构分为四个主要的模块：frameworks、packages、hardware、system。frameworks模块是Android系统的核心，包含了Android系统的核心类库、Java框架和服务，它是Android开发的基础。packages模块包括了Android系统的应用程序，主要是用户使用的应用程序，例如通讯录、日历和相机。hardware模块提供了对硬件设备的支持，例如触摸屏、摄像头等。最后，system模块包含了Linux内核和Android底层服务，它负责管理资源和处理系统事件。除了这些主要模块，Android源码中还有一些其他的文件夹，例如build、external、prebuilts和tools等，他们提供了编译系统所需的资源和工具。接下来我们对根目录进行一个简单的介绍。

​	1、art：该目录是Android 5.0中新增加的，主要是实现Android RunTime（ART）的目录，它作为Android 4.4中的Dalvik虚拟机的替代，主要处理Java字节码。

​	2、bionic：这是Android的C库，包含了很多标准的C库函数和头文件，还有一些Android特有的函数和头文件。 

​	3、bootable：包含了一些用于生成引导程序相关代码的工具和脚本，以及引导程序相关的一些源代码，但并不包含完整的引导程序代码。

​	4、build：该目录包含了编译Android源代码所需要的脚本，包括makefile文件和一些构建工具。 

​	5、compatibility：该目录收集了Android设备的兼容性测试套件（CTS）和兼容性实现（Compatibility Implementation）。 

​	6、cts：该目录包含了Android设备兼容性测试套件（CTS），主要用来测试设备是否符合Android标准。 

​	7、dalvik：该目录包含了Dalvik虚拟机，它是Android 2.3版本之前的主要虚拟机，它主要处理Java字节码。 

​	8、developers：该目录包含了Android开发者文档和样例代码。 

​	9、development：该目录包含了一些调试工具，如systrace、monkey、ddms等。 

​	10、device：该目录包含了特定的Android设备的驱动程序。 

​	11、external：该目录包含了一些第三方库，如WebKit、OpenGL等。

​	12、frameworks：该目录提供了Android应用程序调用底层服务的API，它也是Android应用程序开发的重要组成部分。 

​	13、hardware：该目录包含了Android设备硬件相关的驱动代码，如摄像头驱动、蓝牙驱动等。 

​	14、kernel：该目录包含了Android系统内核的源代码，它是Android系统的核心部分。 

​	15、libcore：该目录包含了Android底层库，它提供了一些基本的API，如文件系统操作、网络操作等。 

​	16、libnativehelper：该目录提供了一些C++库，它们可以帮助我们调用本地代码。

​	17、packages：该目录包含了Android框架、应用程序和其他模块的源代码。 包含了 Android 系统中的所有应用程序，例如短信、电话、浏览器、相机等

​	18、pdk：该目录是一个Android平台开发套件，它包含了一些工具和API，以便开发者快速开发Android应用程序。 

​	19、platform_testing：该目录包含了一些测试工具，用于测试Android平台的稳定性和性能。 

​	20、prebuilts：该目录包含了一些预先编译的文件，如编译工具、驱动程序等。 

​	21、sdk：该目录是Android SDK的源代码，它包含了Android SDK的API文档、代码示例、工具等。 

​	22、system：该目录包含了Android系统的核心部分，如系统服务、应用程序、内存管理机制、文件系统、网络协议等。 

​	23、test：该目录包含了一些测试代码，用于测试Android系统的各个组件。 

​	24、toolchain：该目录包含了一些编译器和工具链，如GCC、Clang等，用于编译Android源代码。 

​	25、tools：该目录包含了一些开发工具，如Android SDK工具、Android Studio、Eclipse等。 

​	26、vendor：该目录包含了一些硬件厂商提供的驱动程序，如摄像头驱动、蓝牙驱动等。

​	我们并不需要全部记下，只要大致的有个印象，当你常常为了实现某个功能，查阅翻读源码时，就会不断加深你对这些目录划分的了解，这里我们回顾一下第二章中，在我们编译源码的过程中下载了两个驱动相关的文件。回顾下图。

![image-20230219161123065](.\images\image-20230219161123065.png)

​	下载两个驱动文件后，我们将文件放到源码根目录中解压，并且执行相应的sh脚本进行导出，到了这里我们了解到vendor中是硬件厂商提供的摄像头蓝牙之类的驱动程序。那么我们就可以观察到，脚本执行后，实际就是将驱动文件放到了对应目录中。对根目录结构有一个简单的了解之后，我们就可以开始翻阅源码，翻阅源码我们可以通过前面搭建好的开发环境，或者是使用在线的源码查看网站http://aospxref.com/。

## 3.2 Android启动流程

​	Android启动流程主要分为四个阶段：Bootloader阶段、Kernel阶段、Init进程阶段和System Server启动阶段，首先我们先简单介绍下这几个阶段的启动流程。

1. Bootloader阶段： 当手机或平板电脑开机时，首先会执行引导加载程序（Bootloader），它会在手机的ROM中寻找启动内核（Kernel）的镜像文件，并将其加载进RAM中。在这个阶段中，Android系统并没有完全启动，只是建立了基本的硬件和内核环境。
2. Kernel阶段： Kernel阶段是Android启动流程的第二阶段，它主要负责初始化硬件设备、加载驱动程序、设置内存管理等。此外，Kernel还会加载initramfs，它是一个临时文件系统，包含了init程序和一些设备文件。
3. Init进程阶段： Kernel会启动init进程，它是Android系统中的第一个用户空间进程。Init进程的主要任务是读取init.rc文件，并根据该文件中的配置信息启动和配置Android系统的各个组件。在这个阶段中，系统会依次启动各个服务和进程，包括启动Zygote进程和创建System Server进程。
4. System Server启动阶段： System Server是Android系统的核心服务进程，它会启动所有的系统服务。其中包括Activity Manager、Package Manager、Window Manager、Location Manager、Telephony Manager、Wi-Fi Service、Bluetooth Service等。System Server启动后，Android系统就完全启动了，用户可以进入桌面，开始使用各种应用程序。

​	在开始启动流程代码追踪前，最重要的一点是不要试图了解所有细节过程，分析代码时要抓住需求重点，然后围绕着需求点来进行深入分析。尽管Android源码是一个非常庞大的体系但是我们仅仅抓住一个方向来熟悉代码，这样就能快速的达成目标，且不会深陷进去。

## 3.3 内核启动

​	Bootloader其实就是一段程序，这个程序的主要功能就是用来引导系统启动所以我们也称之为引导程序，而这个引导程序是存放在一个只读的寄存器中，从物理地址0开始的一段空间分配给了这个只读存储器来存放引导程序。

​	Bootloader会初始化硬件设备并准备内存空间映射，为启动内核准备环境。然后寻找内核的镜像文件，验证boot分区和recovery分区的完整性，然后将其加载到内存中，最后开始执行内核。我们可以通过命令`adb reboot bootloader`直接重启进入引导程序。

​	Bootloader 将件初始化完成后，会在特定的物理地址处查找 EFI 引导头（efi_head）。如果查找到 EFI 引导头，bootloader 就会加载 EFI 引导头指定的 EFI 引导程序，然后开始执行 EFI 引导程序，以进行后续的 EFI 引导流程。而这个efi_head就是linux内核最早的入口了。

​	这里注意，我们现在并需要完全看懂内核中的汇编部分代码，主要是为了解执行的流程，所以并不需要你有汇编的功底，只需要能看懂简单的几个指令即可，接下来打开我们编译内核源码时的目录，找到文件`~/android_src/android-kernel/private/msm-google/arch/arm64/kernel/head.S`查看汇编代码如下。

~~~assembly
	__HEAD
_head:
	/*
	 * DO NOT MODIFY. Image header expected by Linux boot-loaders.
	 */
#ifdef CONFIG_EFI
	/*
	 * This add instruction has no meaningful effect except that
	 * its opcode forms the magic "MZ" signature required by UEFI.
	 */
	add	x13, x18, #0x16
	b	stext
#else
	b	stext				// branch to kernel start, magic
~~~

​	在arm指令集中，指令b表示跳转，所以我们继续找到stext的定义部分。

~~~assembly
	/*
	 * The following callee saved general purpose registers are used on the
	 * primary lowlevel boot path:
	 *
	 *  Register   Scope                      Purpose
	 *  x21        stext() .. start_kernel()  FDT pointer passed at boot in x0
	 *  x23        stext() .. start_kernel()  physical misalignment/KASLR offset
	 *  x28        __create_page_tables()     callee preserved temp register
	 *  x19/x20    __primary_switch()         callee preserved temp registers
	 */
ENTRY(stext)
	bl	preserve_boot_args		//把引导程序传的4个参数保存在全局数组boot_args
	bl	el2_setup			// Drop to EL1, w0=cpu_boot_mode
	adrp	x23, __PHYS_OFFSET
	and	x23, x23, MIN_KIMG_ALIGN - 1	// KASLR offset, defaults to 0
	bl	set_cpu_boot_mode_flag
	bl	__create_page_tables		// 创建页表映射 x25=TTBR0, x26=TTBR1
	/*
	 * The following calls CPU setup code, see arch/arm64/mm/proc.S for
	 * details.
	 * On return, the CPU will be ready for the MMU to be turned on and
	 * the TCR will have been set.
	 */
	bl	__cpu_setup			// // 初始化处理器 initialise processor
	b	__primary_switch
ENDPROC(stext)
~~~

​	能看到最后一行是跳转到__primary_switch，接下来继续看它的实现代码

~~~assembly
__primary_switch:
#ifdef CONFIG_RANDOMIZE_BASE
	mov	x19, x0				// preserve new SCTLR_EL1 value
	mrs	x20, sctlr_el1			// preserve old SCTLR_EL1 value
#endif

	bl	__enable_mmu
#ifdef CONFIG_RELOCATABLE
	bl	__relocate_kernel
#ifdef CONFIG_RANDOMIZE_BASE
	ldr	x8, =__primary_switched		//将x8设置成__primary_switched的地址
	adrp	x0, __PHYS_OFFSET
	blr	x8							//调用__primary_switched

	/*
	 * If we return here, we have a KASLR displacement in x23 which we need
	 * to take into account by discarding the current kernel mapping and
	 * creating a new one.
	 */
	msr	sctlr_el1, x20			// disable the MMU
	isb
	bl	__create_page_tables		// recreate kernel mapping

	tlbi	vmalle1				// Remove any stale TLB entries
	dsb	nsh
	isb

	msr	sctlr_el1, x19			// re-enable the MMU
	isb
	ic	iallu				// flush instructions fetched
	dsb	nsh				// via old mapping
	isb

	bl	__relocate_kernel
#endif
#endif
	ldr	x8, =__primary_switched
	adrp	x0, __PHYS_OFFSET
	br	x8
ENDPROC(__primary_switch)
~~~

接着我们继续跟踪__primary_switched函数，然后我们就能看到一个重点函数start_kernel了。

~~~assembly
__primary_switched:
	adrp	x4, init_thread_union
	add	sp, x4, #THREAD_SIZE
	adr_l	x5, init_task
	msr	sp_el0, x5			// Save thread_info

	adr_l	x8, vectors			// load VBAR_EL1 with virtual
	msr	vbar_el1, x8			// vector table address
	isb

	stp	xzr, x30, [sp, #-16]!
	mov	x29, sp

#ifdef CONFIG_SHADOW_CALL_STACK
	adr_l	x18, init_shadow_call_stack	// Set shadow call stack
#endif

	str_l	x21, __fdt_pointer, x5		// Save FDT pointer

	ldr_l	x4, kimage_vaddr		// Save the offset between
	sub	x4, x4, x0			// the kernel virtual and
	str_l	x4, kimage_voffset, x5		// physical mappings

	// Clear BSS
	adr_l	x0, __bss_start
	mov	x1, xzr
	adr_l	x2, __bss_stop
	sub	x2, x2, x0
	bl	__pi_memset
	dsb	ishst				// Make zero page visible to PTW
#ifdef CONFIG_KASAN
	bl	kasan_early_init
#endif
#ifdef CONFIG_RANDOMIZE_BASE
	tst	x23, ~(MIN_KIMG_ALIGN - 1)	// already running randomized?
	b.ne	0f
	mov	x0, x21				// pass FDT address in x0
	mov	x1, x23				// pass modulo offset in x1
	bl	kaslr_early_init		// parse FDT for KASLR options
	cbz	x0, 0f				// KASLR disabled? just proceed
	orr	x23, x23, x0			// record KASLR offset
	ldp	x29, x30, [sp], #16		// we must enable KASLR, return
	ret					// to __primary_switch()
0:
#endif
	b	start_kernel		// 内核的入口函数
ENDPROC(__primary_switched)
~~~

​		上面能看到最后一个指令就是start_kernel了，这个函数是内核的入口函数，同时也是c语言部分的入口函数。接下来我们查看文件`~/android_src/android-kernel/private/msm-google/init/main.c`，可以看到其中大量的init初始化各种子系统的函数调用。

~~~c
asmlinkage __visible void __init start_kernel(void)
{
    // 加载各种子系统
	...

	/* Do the rest non-__init'ed, we're now alive */
	rest_init();

	prevent_tail_call_optimization();
}
~~~

​	这里我们继续追踪关键的函数rest_init，就是在这里开启的内核初始化线程以及创建内核线程。

~~~c
static noinline void __ref rest_init(void)
{
	...
	kernel_thread(kernel_init, NULL, CLONE_FS);
	numa_default_policy();
	pid = kernel_thread(kthreadd, NULL, CLONE_FS | CLONE_FILES);
	...
}
~~~

接着看看kernel_init线程执行的内容。

~~~c
static int __ref kernel_init(void *unused)
{
	int ret;

	kernel_init_freeable();
	/* need to finish all async __init code before freeing the memory */
	async_synchronize_full();
	free_initmem();
	mark_readonly();
	system_state = SYSTEM_RUNNING;
	numa_default_policy();

	rcu_end_inkernel_boot();

	if (ramdisk_execute_command) {
		ret = run_init_process(ramdisk_execute_command);
		if (!ret)
			return 0;
		pr_err("Failed to execute %s (error %d)\n",
		       ramdisk_execute_command, ret);
	}

	/*
	 * We try each of these until one succeeds.
	 *
	 * The Bourne shell can be used instead of init if we are
	 * trying to recover a really broken machine.
	 */
	if (execute_command) {
		ret = run_init_process(execute_command);
		if (!ret)
			return 0;
		panic("Requested init %s failed (error %d).",
		      execute_command, ret);
	}
	if (!try_to_run_init_process("/sbin/init") ||
	    !try_to_run_init_process("/etc/init") ||
	    !try_to_run_init_process("/bin/init") ||
	    !try_to_run_init_process("/bin/sh"))
		return 0;

	panic("No working init found.  Try passing init= option to kernel. "
	      "See Linux Documentation/init.txt for guidance.");
}
~~~

​	在这里我们看到了原来init进程是用try_to_run_init_process启动的，运行失败的情况下会依次执行上面的4个进程。我们继续看看这个函数是如何启动进程的。

~~~c
static int try_to_run_init_process(const char *init_filename)
{
	int ret;

	ret = run_init_process(init_filename);

	if (ret && ret != -ENOENT) {
		pr_err("Starting init: %s exists but couldn't execute it (error %d)\n",
		       init_filename, ret);
	}

	return ret;
}
~~~

这里简单包装调用的run_init_process，继续看下面的代码

~~~c
static int run_init_process(const char *init_filename)
{
	argv_init[0] = init_filename;
	return do_execve(getname_kernel(init_filename),
		(const char __user *const __user *)argv_init,
		(const char __user *const __user *)envp_init);
}
~~~

​	这里能看到最后是通过execve拉起来的init进程。到这里内核就成功拉起了在最后，我们总结内核启动的简单流程图如下。

![startkernel](.\images\startkernel.png)

## 3.4 Init进程启动

​	init进程是Android系统的第一个进程，它在系统启动之后就被启动，并且一直运行到系统关闭，它是Android系统的核心进程，隶属于系统进程，具有最高的权限，所有的其他进程都是它的子进程，它的主要功能有以下几点：

​	 1、启动Android系统的基础服务：init进程负责启动Android系统的基础服务，如zygote、surfaceflinger、bootanim、power manager等；

​	 2、管理系统进程：init进程管理系统进程，比如启动和关闭系统进程；

​	 3、加载设备驱动：init进程会加载设备的驱动，使设备可以正常使用；

​	 4、加载系统环境变量：init进程会加载系统所需要的环境变量，如PATH、LD_LIBRARY_PATH等； 

​	 5、加载系统配置文件：init进程会加载系统所需要的配置文件，以便系统正常运行； 

​	 6、启动用户进程：init进程会启动用户进程，如桌面程序、默认浏览器等。

​	init进程的入口是在Android源码的`system/core/init/main.cpp`。下面我们看看入口函数main

~~~cpp
int main(int argc, char** argv) {
#if __has_feature(address_sanitizer)
    __asan_set_error_report_callback(AsanReportCallback);
#endif
    // Boost prio which will be restored later
    setpriority(PRIO_PROCESS, 0, -20);
    if (!strcmp(basename(argv[0]), "ueventd")) {
        return ueventd_main(argc, argv);
    }
	
    if (argc > 1) {
        if (!strcmp(argv[1], "subcontext")) {
            android::base::InitLogging(argv, &android::base::KernelLogger);
            const BuiltinFunctionMap& function_map = GetBuiltinFunctionMap();

            return SubcontextMain(argc, argv, &function_map);
        }
		// 第二步 装载selinux策略
        if (!strcmp(argv[1], "selinux_setup")) {
            return SetupSelinux(argv);
        }
		// 第三步
        if (!strcmp(argv[1], "second_stage")) {
            return SecondStageMain(argc, argv);
        }
    }
	// 第一步 挂载设备节点
    return FirstStageMain(argc, argv);
}
~~~

​	根据上一章的启动init的参数，可以判断第一次启动时，执行的是FirstStageMain函数，我们继续看看这个函数的实现，可以看到初始化了一些基础系统支持的目录，以及使用mount进行挂载。

~~~cpp

int FirstStageMain(int argc, char** argv) {
    ...
    CHECKCALL(clearenv());
    CHECKCALL(setenv("PATH", _PATH_DEFPATH, 1));
    // Get the basic filesystem setup we need put together in the initramdisk
    // on / and then we'll let the rc file figure out the rest.
    CHECKCALL(mount("tmpfs", "/dev", "tmpfs", MS_NOSUID, "mode=0755"));
    CHECKCALL(mkdir("/dev/pts", 0755));
    CHECKCALL(mkdir("/dev/socket", 0755));
    CHECKCALL(mkdir("/dev/dm-user", 0755));
    CHECKCALL(mount("devpts", "/dev/pts", "devpts", 0, NULL));
#define MAKE_STR(x) __STRING(x)
    CHECKCALL(mount("proc", "/proc", "proc", 0, "hidepid=2,gid=" MAKE_STR(AID_READPROC)));
#undef MAKE_STR
    // Don't expose the raw commandline to unprivileged processes.
    CHECKCALL(chmod("/proc/cmdline", 0440));
    std::string cmdline;
    android::base::ReadFileToString("/proc/cmdline", &cmdline);
    // Don't expose the raw bootconfig to unprivileged processes.
    chmod("/proc/bootconfig", 0440);
    std::string bootconfig;
    android::base::ReadFileToString("/proc/bootconfig", &bootconfig);
    gid_t groups[] = {AID_READPROC};
    CHECKCALL(setgroups(arraysize(groups), groups));
    CHECKCALL(mount("sysfs", "/sys", "sysfs", 0, NULL));
    CHECKCALL(mount("selinuxfs", "/sys/fs/selinux", "selinuxfs", 0, NULL));
    CHECKCALL(mknod("/dev/kmsg", S_IFCHR | 0600, makedev(1, 11)));
	...
    // 这里可以看到重新访问了init进程，并且参数设置为selinux_setup
    const char* path = "/system/bin/init";
    const char* args[] = {path, "selinux_setup", nullptr};
    auto fd = open("/dev/kmsg", O_WRONLY | O_CLOEXEC);
    dup2(fd, STDOUT_FILENO);
    dup2(fd, STDERR_FILENO);
    close(fd);
    // 使用execv再次调用起init进程
    execv(path, const_cast<char**>(args));
	
    // execv() only returns if an error happened, in which case we
    // panic and never fall through this conditional.
    PLOG(FATAL) << "execv(\"" << path << "\") failed";

    return 1;
}
~~~

​	在目录初始化完成后，又拉起了一个init进程，并且传了参数selinux_setup，所以接下来我们直接看前面main入口函数中判断出现该参数时调用的SetupSelinux函数。

~~~cpp
int SetupSelinux(char** argv) {
    SetStdioToDevNull(argv);
    InitKernelLogging(argv);
	...

    LOG(INFO) << "Opening SELinux policy";

    // Read the policy before potentially killing snapuserd.
    std::string policy;
    ReadPolicy(&policy);

    auto snapuserd_helper = SnapuserdSelinuxHelper::CreateIfNeeded();
    if (snapuserd_helper) {
        // Kill the old snapused to avoid audit messages. After this we cannot
        // read from /system (or other dynamic partitions) until we call
        // FinishTransition().
        snapuserd_helper->StartTransition();
    }

    LoadSelinuxPolicy(policy);

    if (snapuserd_helper) {
        // Before enforcing, finish the pending snapuserd transition.
        snapuserd_helper->FinishTransition();
        snapuserd_helper = nullptr;
    }

    SelinuxSetEnforcement();

    // We're in the kernel domain and want to transition to the init domain.  File systems that
    // store SELabels in their xattrs, such as ext4 do not need an explicit restorecon here,
    // but other file systems do.  In particular, this is needed for ramdisks such as the
    // recovery image for A/B devices.
    if (selinux_android_restorecon("/system/bin/init", 0) == -1) {
        PLOG(FATAL) << "restorecon failed of /system/bin/init failed";
    }

    setenv(kEnvSelinuxStartedAt, std::to_string(start_time.time_since_epoch().count()).c_str(), 1);
	// 继续再拉起一个init进程,参数设置second_stage
    const char* path = "/system/bin/init";
    const char* args[] = {path, "second_stage", nullptr};
    execv(path, const_cast<char**>(args));

    // execv() only returns if an error happened, in which case we
    // panic and never return from this function.
    PLOG(FATAL) << "execv(\"" << path << "\") failed";

    return 1;
}
~~~

​	上面的代码可以看到，在完成selinux的加载处理后，又拉起了一个init进程，并且传参数second_stage。接下来我们看第三步SecondStageMain函数

~~~cpp

int SecondStageMain(int argc, char** argv) {
    ...
	// 初始化属性系统
    PropertyInit();

    // 开启属性服务
    StartPropertyService(&property_fd);
	
    // 解析init.rc 以及启动其他相关进程
    LoadBootScripts(am, sm);

    ...
    return 0;
}
~~~

​	接下来我们看看LoadBootScripts这个函数的处理

~~~cpp

static void LoadBootScripts(ActionManager& action_manager, ServiceList& service_list) {
    Parser parser = CreateParser(action_manager, service_list);

    std::string bootscript = GetProperty("ro.boot.init_rc", "");
    if (bootscript.empty()) {
        // 解析各目录中的init.rc
        parser.ParseConfig("/system/etc/init/hw/init.rc");
        if (!parser.ParseConfig("/system/etc/init")) {
            late_import_paths.emplace_back("/system/etc/init");
        }
        // late_import is available only in Q and earlier release. As we don't
        // have system_ext in those versions, skip late_import for system_ext.
        parser.ParseConfig("/system_ext/etc/init");
        if (!parser.ParseConfig("/vendor/etc/init")) {
            late_import_paths.emplace_back("/vendor/etc/init");
        }
        if (!parser.ParseConfig("/odm/etc/init")) {
            late_import_paths.emplace_back("/odm/etc/init");
        }
        if (!parser.ParseConfig("/product/etc/init")) {
            late_import_paths.emplace_back("/product/etc/init");
        }
    } else {
        parser.ParseConfig(bootscript);
    }
}

~~~

​	继续看看解析的逻辑，可以看到参数可以是目录或者文件

~~~cpp
bool Parser::ParseConfig(const std::string& path) {
    if (is_dir(path.c_str())) {
        return ParseConfigDir(path);
    }
    return ParseConfigFile(path);
}
~~~

​	如果是目录，则遍历所有文件再调用解析文件，所以我们下面直接看ParseConfigFile就好了

~~~cpp
bool Parser::ParseConfigFile(const std::string& path) {
    ...
    ParseData(path, &config_contents.value());
	...
}
~~~

​	最后看看ParseData是如何解析数据的

~~~cpp

void Parser::ParseData(const std::string& filename, std::string* data) {
    ...
    
    for (;;) {
        switch (next_token(&state)) {
            case T_EOF:
                ...
                return;
            case T_NEWLINE: {
                ...
                else if (section_parsers_.count(args[0])) {
                    end_section();
                    // 从section_parsers_中获取出来的
                    section_parser = section_parsers_[args[0]].get();
                    section_start_line = state.line;
                    // 使用了ParseSection进行解析
                    if (auto result =
                                section_parser->ParseSection(std::move(args), filename, state.line);
                        !result.ok()) {
                        parse_error_count_++;
                        LOG(ERROR) << filename << ": " << state.line << ": " << result.error();
                        section_parser = nullptr;
                        bad_section_found = true;
                    }
                } else if (section_parser) {
                    // 使用了ParseLineSection进行解析
                    if (auto result = section_parser->ParseLineSection(std::move(args), state.line);
                        !result.ok()) {
                        parse_error_count_++;
                        LOG(ERROR) << filename << ": " << state.line << ": " << result.error();
                    }
                } 
                ...
            }
            case T_TEXT:
                args.emplace_back(state.text);
                break;
        }
    }
}
~~~

​	这里我们简单解读一下这里的代码，首先这里看到从section_parsers_中找到指定的节点解析对象来执行ParseSection或者ParseLineSection进行解析.rc文件中的数据，我们看下parse创建的函数CreateParser

~~~cpp
void Parser::AddSectionParser(const std::string& name, std::unique_ptr<SectionParser> parser) {
    section_parsers_[name] = std::move(parser);
}


Parser CreateParser(ActionManager& action_manager, ServiceList& service_list) {
    Parser parser;

    parser.AddSectionParser("service", std::make_unique<ServiceParser>(
                                               &service_list, GetSubcontext(), std::nullopt));
    parser.AddSectionParser("on", std::make_unique<ActionParser>(&action_manager, GetSubcontext()));
    parser.AddSectionParser("import", std::make_unique<ImportParser>(&parser));

    return parser;
}
~~~

​	如果了解过init.rc文件格式的，看到这里就很眼熟了，这就是.rc文件中配置时使用的节点名称了。他们的功能简单的描述如下。

​	1、service		定义一个服务

​	2、on				触发某个action时，执行对应的指令

​	3、import	   表示导入另外一个rc文件

​	那么我们再解读上面的代码就是，根据rc文件的配置不同，来使用ServiceParser、ActionParser、ImportParser这三种节点解析对象的ParseSection或者ParseLineSection函数来处理。接下来我们看看这三个对象的处理函数把。

~~~cpp
// service节点的解析处理
Result<void> ServiceParser::ParseSection(std::vector<std::string>&& args,
                                         const std::string& filename, int line) {
    if (args.size() < 3) {
        return Error() << "services must have a name and a program";
    }

    const std::string& name = args[1];
    if (!IsValidName(name)) {
        return Error() << "invalid service name '" << name << "'";
    }

    filename_ = filename;

    Subcontext* restart_action_subcontext = nullptr;
    if (subcontext_ && subcontext_->PathMatchesSubcontext(filename)) {
        restart_action_subcontext = subcontext_;
    }

    std::vector<std::string> str_args(args.begin() + 2, args.end());

    if (SelinuxGetVendorAndroidVersion() <= __ANDROID_API_P__) {
        if (str_args[0] == "/sbin/watchdogd") {
            str_args[0] = "/system/bin/watchdogd";
        }
    }
    if (SelinuxGetVendorAndroidVersion() <= __ANDROID_API_Q__) {
        if (str_args[0] == "/charger") {
            str_args[0] = "/system/bin/charger";
        }
    }

    service_ = std::make_unique<Service>(name, restart_action_subcontext, str_args, from_apex_);
    return {};
}


// on 节点的解析处理
Result<void> ActionParser::ParseSection(std::vector<std::string>&& args,
                                        const std::string& filename, int line) {
    std::vector<std::string> triggers(args.begin() + 1, args.end());
    if (triggers.size() < 1) {
        return Error() << "Actions must have a trigger";
    }

    Subcontext* action_subcontext = nullptr;
    if (subcontext_ && subcontext_->PathMatchesSubcontext(filename)) {
        action_subcontext = subcontext_;
    }

    std::string event_trigger;
    std::map<std::string, std::string> property_triggers;

    if (auto result =
                ParseTriggers(triggers, action_subcontext, &event_trigger, &property_triggers);
        !result.ok()) {
        return Error() << "ParseTriggers() failed: " << result.error();
    }

    auto action = std::make_unique<Action>(false, action_subcontext, filename, line, event_trigger,
                                           property_triggers);

    action_ = std::move(action);
    return {};
}

// import节点的解析处理
Result<void> ImportParser::ParseSection(std::vector<std::string>&& args,
                                        const std::string& filename, int line) {
    if (args.size() != 2) {
        return Error() << "single argument needed for import\n";
    }

    auto conf_file = ExpandProps(args[1]);
    if (!conf_file.ok()) {
        return Error() << "Could not expand import: " << conf_file.error();
    }

    LOG(INFO) << "Added '" << *conf_file << "' to import list";
    if (filename_.empty()) filename_ = filename;
    imports_.emplace_back(std::move(*conf_file), line);
    return {};
}

~~~

​	到这里大致的init进程的启动流程相信大家已经有了一定了解。明白init的原理后，对于init.rc相信大家已经有了简单的印象，接下来将详细展开讲解init.rc文件。

## 3.5 init.rc

​	init.rc是Android系统中的一个脚本文件并非配置文件，是一种名为`Android Init Language`的脚本语言写成的文件，当然也可以简单当作是配置文件理解，主要用于启动和管理Android上的其他进程对系统进行初始化工作。

​	我们可以将init.rc看作是init进程功能的动态延申，一些经常可能需要改动的初始化系统任务就放在配置文件中，然后读取配置解析后再进行初始化执行，如此可以提高一定的灵活性，相信很多开发人员在工作中都有做过类似的封装。而init.rc就是配置文件的入口，在init.rc中再通过上一章所说的import节点来导入其他的配置文件，所以这些文件都可以算是init.rc的一部分。在上一章我们通过了解Init进程的工作流程，看到了解析init.rc文件的过程，这将帮助我们更容易理解init.rc文件。

​	init.rc是由多个section节点组成的，而节点的类型分别主要是service、on、import三种。而这三种在上一节的原理介绍中，有简单的介绍，它们的作用分别是定义服务、事件触发、导入其他rc文件。下面我们来看init.rc文件中的几个例子，查看文件`system/core/rootdir/init.rc`。

~~~
// 导入另一个rc文件
import /init.environ.rc
import /system/etc/init/hw/init.usb.rc
import /init.${ro.hardware}.rc
import /vendor/etc/init/hw/init.${ro.hardware}.rc
import /system/etc/init/hw/init.usb.configfs.rc
import /system/etc/init/hw/init.${ro.zygote}.rc
...
// 当初始化触发时,执行section下的命令
on init
    sysclktz 0

    # Mix device-specific information into the entropy pool
    copy /proc/cmdline /dev/urandom
    copy /system/etc/prop.default /dev/urandom

    symlink /proc/self/fd/0 /dev/stdin
    symlink /proc/self/fd/1 /dev/stdout
    symlink /proc/self/fd/2 /dev/stderr

    # Create energy-aware scheduler tuning nodes
    mkdir /dev/stune/foreground
...

// 当属性ro.debuggable变更为1时触发section内的命令
on property:ro.debuggable=1
    # Give writes to anyone for the trace folder on debug builds.
    # The folder is used to store method traces.
    chmod 0773 /data/misc/trace
    # Give reads to anyone for the window trace folder on debug builds.
    chmod 0775 /data/misc/wmtrace
    # Give reads to anyone for the accessibility trace folder on debug builds.
    chmod 0775 /data/misc/a11ytrace
...

// 定义系统服务 服务名称ueventd  服务路径/system/bin/ueventd
// 服务类型core，关机行为critical，安全标签u:r:ueventd:s0
service ueventd /system/bin/ueventd
    class core
    critical
    seclabel u:r:ueventd:s0
    shutdown critical

// 定义系统服务 服务名称console 服务路径/system/bin/sh
// 服务类型core 服务状态disabled 服务所属用户shell 服务所属组shell log readproc
// 安全标签u:r:shell:s0 设置环境变量HOSTNAME console
service console /system/bin/sh
    class core
    console
    disabled
    user shell
    group shell log readproc
    seclabel u:r:shell:s0
    setenv HOSTNAME console
~~~

​	看完各种节点的样例后，我们大概了解init.rc中应该如何添加一个section了。import非常简单，只需要指定一个rc文件的路径即可。on节点在源码中我们看到对应的处理是ActionParser，这个节点就是当触发了一个Action的事件后就自上而下，依次执行节点下的所有命令，所以我们就得了解一下一共有哪些Action事件提供使用。详细介绍参考自`http://www.gaohaiyan.com/4047.html`

~~~
on boot                     #系统启动触发
on early-init               #在初始化之前触发
on init                     #在初始化时触发（在启动配置文件/init.conf被装载之后）
on late-init                #在初始化晚期阶段触发
on charger                  #当充电时触发
on property:<key>=<value>   #当属性值满足条件时触发
on post-fs                  #挂载文件系统
on post-fs-data             #挂载data
on device-added-<path>      #在指定设备被添加时触发
on device-removed-<path>    #在指定设备被移除时触发
on service-exited-<name>    #在指定service退出时触发
on <name>=<value>           #当属性<name>等于<value>时触发
~~~

​	在触发Action事件后执行的命令一共有如下这些

~~~
chdir <dirc>                                  更改工作目录为<dirc>
chmod <octal-mode> <path>                     更改文件访问权限
chown <owner> <group> <path>                  更改文件所有者和组群
chroot <direc>                                更改根目录位置
class_start <serviceclass>                    如果它们不在运行状态的话，启动由<serviceclass>类名指定的所有相关服务
class_stop <serviceclass>                     如果它们在运行状态的话，停止
domainname <name>                             设置域名
exec <path> [ <argument> ]*                   fork并执行一个程序，其路径为<path>，这条命令将阻塞直到该程序启动完成，因此它有可能造成init程序在某个节点不停地等待
export <name> <value>                         设置某个环境变量<name>的值为<value>，这是对全局有效的，即其后所有进程都将继承这个变量
hostname <name>                               设置主机名
ifup <interface>                              使网络接口<interface>成功连接
import <filename>                             引入一个名为<filename>的文件
insmod <path>                                 在<path>路径上安装一个模块
mkdir <path> [mode] [owner] [group]           在<path>路径上新建一个目录
mount <type> <device> <dir> [<mountoption>]*  尝试在指定路径上挂载一个设备 
setprop <name> <value>                        设置系统属性<name>的值为<value>
setrlinit <resource> <cur> <max>              设置一种资源的使用限制。这个概念亦存在于Linux系统中，<cur>表示软限制，<max>表示硬限制
start <service>                               启动一个服务
stop <service>                                停止一个服务
symlink <target> <path>                       创建一个<path>路径的软链接，目标为<target>
sysclk <mins_west_of_gmt>                     设置基准时间，如果当前时间时GMT，这个值是0
trigger <event>                               触发一个事件
write <path> <string> [<string>]*             打开一个文件，并写入字符串
~~~

​	而service节点主要是将可执行程序作为服务启动，上面的例子我们看到节点下面有一系列的参数，下面是这些参数的详细描述。

~~~
class <name>                                       为该服务指定一个class名，同一个class的所有服务必须同时启动或者停止。
                                                   默认情况下服务的class名是“default”。另外还有core(其它服务依赖的基础性核心服务)、main(java须要的基本服务)、late_start(厂商定制的服务)
critical                                           表示这是一个对设备至关重要的一个服务，如果它在四分钟内退出超过四次，则设备将重启进入恢复模式
disabled                                           此服务不会自动启动，而是需要通过显式调用服务名来启动
group <groupname> [<groupname>]*                   在启动服务前将用户组切换为<groupname>
oneshot                                            只启动一次，当此服务退出时，不要主动去重启它
onrestart                                          当此服务重启时，执行某些命令
setenv <name> <value>                              设置环境变量<name>为某个值<value>
socket <name> <type> <perm> [ <user> [<group>]]    创建一个名为/dev/socket/<name>的unix domain socket，然后将它的fd值传给启动它的进程，有效的<type>值包括dgram，stream和seqacket，而user和group的默认值是0
user <username>                                    在启动服务前将用户组切换为<username>，默认情况下用户都是root
~~~

​	到这里，相信大家应该能够看懂init.rc中的大多数section的意义了。下面的例子我们将组合使用，定义一个自己的服务，并且启动它。

~~~
service kservice /system/bin/app_process -Djava.class.path=/system/framework/ksvr.jar /system/bin cn.mik.ksvr.kSystemSvr svr
    class main
    user root
    group root
    oneshot
    seclabel u:r:su:s0

on property:sys.boot_completed=1
    bootchart stop
    start kservice
~~~

​	上面的案例中，我定义了一个kservice的服务，使用`/system/bin/app_process`作为进程启动，并设置目标jar作为应用的classpath，最后设置jar文件的入口类`cn.mik.ksvr.kSystemSvr`，最后的svr是做为参数传递给kSystemSvr中的main函数。接下来是当属性sys.boot_completed变更为1时表示手机完成引导，执行节点下的命令启动刚刚定义的服务。

## 3.6 Zygote启动

​	在前面init进程的最后，我们知道了是解析处理init.rc文件，在上一节学习了init.rc中的各节点的详细介绍，这时我们已经可以继续阅读init.rc追踪后续的启动流程了。

~~~
# 导入含有zygote服务定义的rc文件，这个会根据系统所支持的对应架构导入
import /system/etc/init/hw/init.${ro.zygote}.rc

# init完成后触发zygote-start事件
on late-init
    ...
    # Now we can start zygote for devices with file based encryption
    trigger zygote-start
    ...

# 最后启动了zygote和zygote_secondary
on zygote-start && property:ro.crypto.state=unencrypted
    wait_for_prop odsign.verification.done 1
    # A/B update verifier that marks a successful boot.
    exec_start update_verifier_nonencrypted
    start statsd
    start netd
    start zygote
    start zygote_secondary
    
~~~

​	zygote服务定义的rc文件在路径`system/core/rootdir/`中。分别是init.zygote32.rc、init.zygote64.rc、init.zygote32_64.rc、init.zygote64_32.rc，其中32_64表示32位是主模式而64_32的则表示64位是主模式。下面我们查看zygote64的是如何定义的。

~~~
// --zygote 传递给app_process程序的参数,表示这是启动一个孵化器。
// --start-system-server 传递给app_process程序的参数，表示进程启动后需要启动system_server进程
service zygote /system/bin/app_process64 -Xzygote /system/bin --zygote --start-system-server
    class main
    priority -20
    user root
    group root readproc reserved_disk
    socket zygote stream 660 root system
    socket usap_pool_primary stream 660 root system
    onrestart exec_background - system system -- /system/bin/vdc volume abort_fuse
    onrestart write /sys/power/state on
    onrestart restart audioserver
    onrestart restart cameraserver
    onrestart restart media
    onrestart restart netd
    onrestart restart wificond
    writepid /dev/cpuset/foreground/tasks
    critical window=${zygote.critical_window.minute:-off} target=zygote-fatal
~~~

​	前面我们定义和启动一个自己定义的java服务时也看到是通过app_process启动的。app_process是Android系统的主要进程，它是其他所有应用程序的容器，它负责创建新的进程，并启动它们。此外，它还管理应用程序的生命周期，防止任何一个应用程序占用资源过多，或者做出不良影响。app_process还负责在应用运行时为它们提供上下文，以及管理应用进程之间的通信。

​	接下来我们跟踪app_process的实现，它的入口是在目录`frameworks/base/cmds/app_process/app_main.cpp`中。

~~~c++
#if defined(__LP64__)
static const char ABI_LIST_PROPERTY[] = "ro.product.cpu.abilist64";
static const char ZYGOTE_NICE_NAME[] = "zygote64";
#else
static const char ABI_LIST_PROPERTY[] = "ro.product.cpu.abilist32";
static const char ZYGOTE_NICE_NAME[] = "zygote";
#endif

int main(int argc, char* const argv[])
{
  	...
    // Parse runtime arguments.  Stop at first unrecognized option.
    bool zygote = false;
    bool startSystemServer = false;
    bool application = false;
    String8 niceName;
    String8 className;

    ++i;  // Skip unused "parent dir" argument.
    // 参数的处理
    while (i < argc) {
        const char* arg = argv[i++];
        if (strcmp(arg, "--zygote") == 0) {
            zygote = true;
            niceName = ZYGOTE_NICE_NAME;
        } else if (strcmp(arg, "--start-system-server") == 0) {
            startSystemServer = true;
        } else if (strcmp(arg, "--application") == 0) {
            application = true;
        } else if (strncmp(arg, "--nice-name=", 12) == 0) {
            niceName.setTo(arg + 12);
        } else if (strncmp(arg, "--", 2) != 0) {
            className.setTo(arg);
            break;
        } else {
            --i;
            break;
        }
    }
   	...
    if (!niceName.isEmpty()) {
        runtime.setArgv0(niceName.string(), true /* setProcName */);
    }
    // 如果启动时设置--zygote，则启动ZygoteInit，否则启动RuntimeInit
    if (zygote) {
        const char* zygoteName="com.android.internal.os.ZygoteInit";
        runtime.start(zygoteName, args, zygote);
    } else if (className) {
        const char* zygoteName="com.android.internal.os.RuntimeInit";
        runtime.start(zygoteName, args, zygote);
    } else {
        fprintf(stderr, "Error: no class name or --zygote supplied.\n");
        app_usage();
        LOG_ALWAYS_FATAL("app_process: no class name or --zygote supplied.");
    }
}
~~~

​	从代码中可以看到主要是对参数进行处理包装后，然后根据是否携带--zygote选择启动ZygoteInit或者是RuntimeInit。

​	ZygoteInit是Android应用程序运行期间的主要接口。ZygoteInit负责加载和初始化Android运行时环境，例如应用程序运行器，垃圾收集器等，并且它启动Android系统中的所有核心服务。

​	 RuntimeInit负责将应用程序的执行环境与系统的运行环境进行联系，然后将应用程序的主类加载到运行时，最后将应用程序的控制权交给应用程序的主类。

​	下面继续看看runtime.start的实现，查看对应文件`frameworks/base/core/jni/AndroidRuntime.cpp`

~~~cpp
void AndroidRuntime::start(const char* className, const Vector<String8>& options, bool zygote)
{
    ...
    //const char* kernelHack = getenv("LD_ASSUME_KERNEL");
    //ALOGD("Found LD_ASSUME_KERNEL='%s'\n", kernelHack);

    /* 启动vm虚拟机 */
    JniInvocation jni_invocation;
    jni_invocation.Init(NULL);
    JNIEnv* env;
    if (startVm(&mJavaVM, &env, zygote, primary_zygote) != 0) {
        return;
    }
    onVmCreated(env);

    /*
     * 注册框架使用的JNI调用
     */
    if (startReg(env) < 0) {
        ALOGE("Unable to register all android natives\n");
        return;
    }
  	...
    char* slashClassName = toSlashClassName(className != NULL ? className : "");
    jclass startClass = env->FindClass(slashClassName);
    if (startClass == NULL) {
        ALOGE("JavaVM unable to locate class '%s'\n", slashClassName);
        /* keep going */
    } else {
        // 这里调用ZygoteInit或者是RuntimeInit的main函数
        jmethodID startMeth = env->GetStaticMethodID(startClass, "main",
            "([Ljava/lang/String;)V");
        if (startMeth == NULL) {
            ALOGE("JavaVM unable to find main() in '%s'\n", className);
            /* keep going */
        } else {
            env->CallStaticVoidMethod(startClass, startMeth, strArray);

#if 0
            if (env->ExceptionCheck())
                threadExitUncaughtException(env);
#endif
        }
    }
    free(slashClassName);

    ALOGD("Shutting down VM\n");
    if (mJavaVM->DetachCurrentThread() != JNI_OK)
        ALOGW("Warning: unable to detach main thread\n");
    if (mJavaVM->DestroyJavaVM() != 0)
        ALOGW("Warning: VM did not shut down cleanly\n");
}
~~~

​	看到这里通过JNI函数CallStaticVoidMethod调用了ZygoteInit的main入口函数，现在我们就来到了java层中，查看文件代码`frameworks/base/core/java/com/android/internal/os/ZygoteInit.java`

~~~java
public static void main(String[] argv) {
        ZygoteServer zygoteServer = null;
		...
        try {
            ...
            if (!enableLazyPreload) {
                bootTimingsTraceLog.traceBegin("ZygotePreload");
                EventLog.writeEvent(LOG_BOOT_PROGRESS_PRELOAD_START,
                        SystemClock.uptimeMillis());
                // 预加载资源，比如类、主题资源、字体资源等等
                preload(bootTimingsTraceLog);
                EventLog.writeEvent(LOG_BOOT_PROGRESS_PRELOAD_END,
                        SystemClock.uptimeMillis());
                bootTimingsTraceLog.traceEnd(); // ZygotePreload
            }
            ...

            Zygote.initNativeState(isPrimaryZygote);

            ZygoteHooks.stopZygoteNoThreadCreation();
			// 创建socket服务端
            zygoteServer = new ZygoteServer(isPrimaryZygote);
			// 前面在init.rc中有配置--start-system-server的进程则会进入fork启动SystemServer
            if (startSystemServer) {
                Runnable r = forkSystemServer(abiList, zygoteSocketName, zygoteServer);

                // {@code r == null} in the parent (zygote) process, and {@code r != null} in the
                // child (system_server) process.
                if (r != null) {
                    r.run();
                    return;
                }
            }

            Log.i(TAG, "Accepting command socket connections");

            // socket服务端等待AMS的请求，收到请求后就会由Zygote服务端来通过fork创建应用程序的进程
            caller = zygoteServer.runSelectLoop(abiList);
        } catch (Throwable ex) {
            Log.e(TAG, "System zygote died with fatal exception", ex);
            throw ex;
        } finally {
            if (zygoteServer != null) {
                zygoteServer.closeServerSocket();
            }
        }

        // We're in the child process and have exited the select loop. Proceed to execute the
        // command.
        if (caller != null) {
            caller.run();
        }
    }
~~~

​	这里的重点是创建了一个zygoteServer，然后根据参数决定是否forkSystemServer，最后runSelectLoop等待AMS发送消息创建应用程序的进程。我们依次从代码观察他们的本质。首先是ZygoteServer的构造函数，可以看到，主要是创建Socket套接字。

~~~java
ZygoteServer(boolean isPrimaryZygote) {
        mUsapPoolEventFD = Zygote.getUsapPoolEventFD();

        if (isPrimaryZygote) {
            mZygoteSocket = Zygote.createManagedSocketFromInitSocket(Zygote.PRIMARY_SOCKET_NAME);
            mUsapPoolSocket =
                    Zygote.createManagedSocketFromInitSocket(
                            Zygote.USAP_POOL_PRIMARY_SOCKET_NAME);
        } else {
            mZygoteSocket = Zygote.createManagedSocketFromInitSocket(Zygote.SECONDARY_SOCKET_NAME);
            mUsapPoolSocket =
                    Zygote.createManagedSocketFromInitSocket(
                            Zygote.USAP_POOL_SECONDARY_SOCKET_NAME);
        }

        mUsapPoolSupported = true;
        fetchUsapPoolPolicyProps();
    }
~~~

​	然后就是forkSystemServer的返回值到底是什么，最后的run会调用到哪里呢

~~~java
private static Runnable forkSystemServer(String abiList, String socketName,
            ZygoteServer zygoteServer) {
		// 服务启动的相关参数，这里注意到类名是com.android.server.SystemServer
        String[] args = {
                "--setuid=1000",
                "--setgid=1000",
                "--setgroups=1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1018,1021,1023,"
                        + "1024,1032,1065,3001,3002,3003,3006,3007,3009,3010,3011",
                "--capabilities=" + capabilities + "," + capabilities,
                "--nice-name=system_server",
                "--runtime-args",
                "--target-sdk-version=" + VMRuntime.SDK_VERSION_CUR_DEVELOPMENT,
                "com.android.server.SystemServer",
        };
        ZygoteArguments parsedArgs;

        int pid;

        try {
            ...
            // 使用fork创建一个SystemServer进程
            /* Request to fork the system server process */
            pid = Zygote.forkSystemServer(
                    parsedArgs.mUid, parsedArgs.mGid,
                    parsedArgs.mGids,
                    parsedArgs.mRuntimeFlags,
                    null,
                    parsedArgs.mPermittedCapabilities,
                    parsedArgs.mEffectiveCapabilities);
        } catch (IllegalArgumentException ex) {
            throw new RuntimeException(ex);
        }
		
        /* For child process */
        if (pid == 0) {
            if (hasSecondZygote(abiList)) {
                waitForSecondaryZygote(socketName);
            }
			
            zygoteServer.closeServerSocket();
            // pid为0的部分，就是由这里fork出来的SystemServer执行的了。
            return handleSystemServerProcess(parsedArgs);
        }

        return null;
    }


private static Runnable handleSystemServerProcess(ZygoteArguments parsedArgs) {
    ...
    ClassLoader cl = getOrCreateSystemServerClassLoader();
    if (cl != null) {
        Thread.currentThread().setContextClassLoader(cl);
    }
	// 初始化SystemServer
    return ZygoteInit.zygoteInit(parsedArgs.mTargetSdkVersion,
                                 parsedArgs.mDisabledCompatChanges,
                                 parsedArgs.mRemainingArgs, cl);
    ...
}

public static Runnable zygoteInit(int targetSdkVersion, long[] disabledCompatChanges,
            String[] argv, ClassLoader classLoader) {
        ...
    	// 继续跟进去
        return RuntimeInit.applicationInit(targetSdkVersion, disabledCompatChanges, argv,
                classLoader);
    }


protected static Runnable applicationInit(int targetSdkVersion, long[] disabledCompatChanges,
                                          String[] argv, ClassLoader classLoader) {
    ...
    // 反射获取com.android.server.SystemServer的入口函数并返回
    return findStaticMain(args.startClass, args.startArgs, classLoader);
}

// 可以看到就是通过反射，获取到对应类的main函数，最后封装到MethodAndArgsCaller返回
protected static Runnable findStaticMain(String className, String[] argv,
                                         ClassLoader classLoader) {
    Class<?> cl;

    try {
        cl = Class.forName(className, true, classLoader);
    } catch (ClassNotFoundException ex) {
        throw new RuntimeException(
            "Missing class when invoking static main " + className,
            ex);
    }

    Method m;
    try {
        m = cl.getMethod("main", new Class[] { String[].class });
    } catch (NoSuchMethodException ex) {
        throw new RuntimeException(
            "Missing static main on " + className, ex);
    } catch (SecurityException ex) {
        throw new RuntimeException(
            "Problem getting static main on " + className, ex);
    }

    int modifiers = m.getModifiers();
    if (! (Modifier.isStatic(modifiers) && Modifier.isPublic(modifiers))) {
        throw new RuntimeException(
            "Main method is not public and static on " + className);
    }

    /*
         * This throw gets caught in ZygoteInit.main(), which responds
         * by invoking the exception's run() method. This arrangement
         * clears up all the stack frames that were required in setting
         * up the process.
         */
    return new MethodAndArgsCaller(m, argv);
}

// forkSystemServer最终返回的就是这个类
static class MethodAndArgsCaller implements Runnable {
    /** method to call */
    private final Method mMethod;

    /** argument array */
    private final String[] mArgs;

    public MethodAndArgsCaller(Method method, String[] args) {
        mMethod = method;
        mArgs = args;
    }

    public void run() {
        try {
            mMethod.invoke(null, new Object[] { mArgs });
        } catch (IllegalAccessException ex) {
            throw new RuntimeException(ex);
        } catch (InvocationTargetException ex) {
            Throwable cause = ex.getCause();
            if (cause instanceof RuntimeException) {
                throw (RuntimeException) cause;
            } else if (cause instanceof Error) {
                throw (Error) cause;
            }
            throw new RuntimeException(ex);
        }
    }
}


~~~

​	forkSystemServer函数走到最后是通过反射获取com.android.server.SystemServer的入口函数main，并封装到MethodAndArgsCaller对象中返回。最后的返回结果调用run时，就会执行到SystemServer中的main函数。继续看看main函数的实现，查看文件`frameworks/base/services/java/com/android/server/SystemServer.java`

~~~java
public static void main(String[] args) {
	new SystemServer().run();
}

private void run() {
    	...
        // 创建主线程Looper
        Looper.prepareMainLooper();
        
        // 初始化系统Context上下文
        createSystemContext();
    	
        // 创建SystemServiceManager，由它管理系统的所有服务
        mSystemServiceManager = new SystemServiceManager(mSystemContext);
        mSystemServiceManager.setStartInfo(mRuntimeRestart,
                                           mRuntimeStartElapsedTime, mRuntimeStartUptime);
        mDumper.addDumpable(mSystemServiceManager);
        LocalServices.addService(SystemServiceManager.class, mSystemServiceManager);
        ...
        
    // 启动各种服务
    try {
        t.traceBegin("StartServices");
        // 启动引导服务
        startBootstrapServices(t);
        // 启动核心服务
        startCoreServices(t);
        // 启动其他服务
        startOtherServices(t);
    } catch (Throwable ex) {
        Slog.e("System", "******************************************");
        Slog.e("System", "************ Failure starting system services", ex);
        throw ex;
    } finally {
        t.traceEnd(); // StartServices
    }
	...
    // Loop forever.
    Looper.loop();
}

// 启动负责引导的服务
private void startBootstrapServices(@NonNull TimingsTraceAndSlog t) {
    t.traceBegin("startBootstrapServices");

    ...
    // 启动ActivityManagerService
    t.traceBegin("StartActivityManager");
    // TODO: Might need to move after migration to WM.
    ActivityTaskManagerService atm = mSystemServiceManager.startService(
        ActivityTaskManagerService.Lifecycle.class).getService();
    mActivityManagerService = ActivityManagerService.Lifecycle.startService(
        mSystemServiceManager, atm);
    mActivityManagerService.setSystemServiceManager(mSystemServiceManager);
    mActivityManagerService.setInstaller(installer);
    mWindowManagerGlobalLock = atm.getGlobalLock();
    t.traceEnd();
	...
}

private void startOtherServices(@NonNull TimingsTraceAndSlog t) {
    t.traceBegin("startOtherServices");
	...
    // 从systemReady开始可以启动第三方应用
    mActivityManagerService.systemReady(() -> {
        ...
    }, t);
	...
}

// 最后看看systemReady的处理
// frameworks/base/services/java/com/android/server/am/ActivitymanagerService.java
public void systemReady(final Runnable goingCallback, @NonNull TimingsTraceAndSlog t) {
		...
        Slog.i(TAG, "System now ready");
		...
		// 启动多用户下的Home Activity，最终会开启系统应用Luncher桌面显示
        if (bootingSystemUser) {
            t.traceBegin("startHomeOnAllDisplays");
            mAtmInternal.startHomeOnAllDisplays(currentUserId, "systemReady");
            t.traceEnd();
        }
		...	
}

~~~

​	到这里大致的服务启动流程我们就清楚了，最后成功抵达了Luncher的启动，后面的章节会介绍到应该如何添加一个自定义的系统服务。现在我们重新回到流程中，继续看看runSelectLoop函数是如何实现的

~~~java
Runnable runSelectLoop(String abiList) {
        ...
        socketFDs.add(mZygoteSocket.getFileDescriptor());
        peers.add(null);

        mUsapPoolRefillTriggerTimestamp = INVALID_TIMESTAMP;

        while (true) {
            fetchUsapPoolPolicyPropsWithMinInterval();
            mUsapPoolRefillAction = UsapPoolRefillAction.NONE;

            int[] usapPipeFDs = null;
            StructPollfd[] pollFDs;
			
            int pollReturnValue;
            try {
                pollReturnValue = Os.poll(pollFDs, pollTimeoutMs);
            } catch (ErrnoException ex) {
                throw new RuntimeException("poll failed", ex);
            }
			...
            if (mUsapPoolRefillAction != UsapPoolRefillAction.NONE) {
                int[] sessionSocketRawFDs =
                        socketFDs.subList(1, socketFDs.size())
                                .stream()
                                .mapToInt(FileDescriptor::getInt$)
                                .toArray();

                final boolean isPriorityRefill =
                        mUsapPoolRefillAction == UsapPoolRefillAction.IMMEDIATE;

                final Runnable command =
                        fillUsapPool(sessionSocketRawFDs, isPriorityRefill);

                if (command != null) {
                    return command;
                } else if (isPriorityRefill) {
                    // Schedule a delayed refill to finish refilling the pool.
                    mUsapPoolRefillTriggerTimestamp = System.currentTimeMillis();
                }
            }
        }
    }
~~~

​	重点主要放在返回值的跟踪上，所以我们直接看fillUsapPool函数做了些什么

~~~java
Runnable fillUsapPool(int[] sessionSocketRawFDs, boolean isPriorityRefill) {
        ...
        while (--numUsapsToSpawn >= 0) {
            Runnable caller =
                    Zygote.forkUsap(mUsapPoolSocket, sessionSocketRawFDs, isPriorityRefill);

            if (caller != null) {
                return caller;
            }
        }
		...
        return null;
    }
    
// 继续追踪关键返回值的函数forkUsap
// 对应文件frameworks/base/core/java/com/android/internal/os/Zygote.java
static @Nullable Runnable forkUsap(LocalServerSocket usapPoolSocket,
                                       int[] sessionSocketRawFDs,
                                       boolean isPriorityFork) {
        FileDescriptor readFD;
        FileDescriptor writeFD;

        try {
            FileDescriptor[] pipeFDs = Os.pipe2(O_CLOEXEC);
            readFD = pipeFDs[0];
            writeFD = pipeFDs[1];
        } catch (ErrnoException errnoEx) {
            throw new IllegalStateException("Unable to create USAP pipe.", errnoEx);
        }
		// 这里fork出一个子进程并初始化信息，最后返回pid
        int pid = nativeForkApp(readFD.getInt$(), writeFD.getInt$(),
                                sessionSocketRawFDs, /*argsKnown=*/ false, isPriorityFork);
        if (pid == 0) {
            IoUtils.closeQuietly(readFD);
            // 如果是子进程就调用childMain获取返回值
            return childMain(null, usapPoolSocket, writeFD);
        } else if (pid == -1) {
            // Fork failed.
            return null;
        } else {
            // readFD will be closed by the native code. See removeUsapTableEntry();
            IoUtils.closeQuietly(writeFD);
            nativeAddUsapTableEntry(pid, readFD.getInt$());
            return null;
        }
    }

// 继续看childMain的实现
private static Runnable childMain(@Nullable ZygoteCommandBuffer argBuffer,
                                      @Nullable LocalServerSocket usapPoolSocket,
                                      FileDescriptor writePipe) {
		...
		// 初始化应用程序环境，设置应用程序上下文，初始化应用程序线程等等
        specializeAppProcess(args.mUid, args.mGid, args.mGids,
                             args.mRuntimeFlags, rlimits, args.mMountExternal,
                             args.mSeInfo, args.mNiceName, args.mStartChildZygote,
                             args.mInstructionSet, args.mAppDataDir, args.mIsTopApp,
                             args.mPkgDataInfoList, args.mAllowlistedDataInfoList,
                             args.mBindMountAppDataDirs, args.mBindMountAppStorageDirs);

        Trace.traceEnd(Trace.TRACE_TAG_ACTIVITY_MANAGER);
		// 又看到这个了，在SystemServer的启动中，我们追踪过
    	// 这里最后是反射获取某个java类的main函数封装后返回
        return ZygoteInit.zygoteInit(args.mTargetSdkVersion,
                                     args.mDisabledCompatChanges,
                                     args.mRemainingArgs,
                                     null /* classLoader */);
        
    }
~~~

​	由于我们前面分析过了zygoteInit，所以这里就不需要再继续进去看了，我们直接看看孵化器进程是如何初始化应用程序环境的，追踪specializeAppProcess函数。

~~~java
private static void specializeAppProcess(int uid, int gid, int[] gids, int runtimeFlags,
            int[][] rlimits, int mountExternal, String seInfo, String niceName,
            boolean startChildZygote, String instructionSet, String appDataDir, boolean isTopApp,
            String[] pkgDataInfoList, String[] allowlistedDataInfoList,
            boolean bindMountAppDataDirs, boolean bindMountAppStorageDirs) {
    	
    	// 可以看到准备的一大堆参数，继续传递到了native层进行初始化处理了。
        nativeSpecializeAppProcess(uid, gid, gids, runtimeFlags, rlimits, mountExternal, seInfo,
                niceName, startChildZygote, instructionSet, appDataDir, isTopApp,
                pkgDataInfoList, allowlistedDataInfoList,
                bindMountAppDataDirs, bindMountAppStorageDirs);
    	...
    }

// 继续查看nativeSpecializeAppProcess
// 文件所在frameworks/base/core/jni/com_android_internal_os_Zygote.cpp
static void com_android_internal_os_Zygote_nativeSpecializeAppProcess(
        JNIEnv* env, jclass, jint uid, jint gid, jintArray gids, jint runtime_flags,
        jobjectArray rlimits, jint mount_external, jstring se_info, jstring nice_name,
        jboolean is_child_zygote, jstring instruction_set, jstring app_data_dir,
        jboolean is_top_app, jobjectArray pkg_data_info_list,
        jobjectArray allowlisted_data_info_list, jboolean mount_data_dirs,
        jboolean mount_storage_dirs) {
    jlong capabilities = CalculateCapabilities(env, uid, gid, gids, is_child_zygote);
	
    SpecializeCommon(env, uid, gid, gids, runtime_flags, rlimits, capabilities, capabilities,
                     mount_external, se_info, nice_name, false, is_child_zygote == JNI_TRUE,
                     instruction_set, app_data_dir, is_top_app == JNI_TRUE, pkg_data_info_list,
                     allowlisted_data_info_list, mount_data_dirs == JNI_TRUE,
                     mount_storage_dirs == JNI_TRUE);
}

// 继续查看SpecializeCommon实现
static void SpecializeCommon(JNIEnv* env, uid_t uid, gid_t gid, jintArray gids, jint runtime_flags,
                             jobjectArray rlimits, jlong permitted_capabilities,
                             jlong effective_capabilities, jint mount_external,
                             jstring managed_se_info, jstring managed_nice_name,
                             bool is_system_server, bool is_child_zygote,
                             jstring managed_instruction_set, jstring managed_app_data_dir,
                             bool is_top_app, jobjectArray pkg_data_info_list,
                             jobjectArray allowlisted_data_info_list, bool mount_data_dirs,
                             bool mount_storage_dirs) {
    const char* process_name = is_system_server ? "system_server" : "zygote";
    auto fail_fn = std::bind(ZygoteFailure, env, process_name, managed_nice_name, _1);
    auto extract_fn = std::bind(ExtractJString, env, process_name, managed_nice_name, _1);
	
    auto se_info = extract_fn(managed_se_info);
    auto nice_name = extract_fn(managed_nice_name);
    auto instruction_set = extract_fn(managed_instruction_set);
    auto app_data_dir = extract_fn(managed_app_data_dir);
    // 在这里的nick_name就是应用的包名了
    const char* nice_name_ptr = nice_name.has_value() ? nice_name.value().c_str() : nullptr;
	// 如果是系统服务，就初始化系统服务的classloader
    if (is_system_server) {
        // Prefetch the classloader for the system server. This is done early to
        // allow a tie-down of the proper system server selinux domain.
        env->CallStaticObjectMethod(gZygoteInitClass, gGetOrCreateSystemServerClassLoader);
        if (env->ExceptionCheck()) {
            // Be robust here. The Java code will attempt to create the classloader
            // at a later point (but may not have rights to use AoT artifacts).
            env->ExceptionClear();
        }
    }
	...
    if (selinux_android_setcontext(uid, is_system_server, se_info_ptr, nice_name_ptr) == -1) {
        fail_fn(CREATE_ERROR("selinux_android_setcontext(%d, %d, \"%s\", \"%s\") failed", uid,
                             is_system_server, se_info_ptr, nice_name_ptr));
    }

    // Make it easier to debug audit logs by setting the main thread's name to the
    // nice name rather than "app_process".
    if (nice_name.has_value()) {
        SetThreadName(nice_name.value());
    } else if (is_system_server) {
        SetThreadName("system_server");
    }

    // 调用java层的callPostForkChildHooks函数
    // 这个函数主要用来在新创建的子进程中调用回调函数进行初始化。
    env->CallStaticVoidMethod(gZygoteClass, gCallPostForkChildHooks, runtime_flags,
                              is_system_server, is_child_zygote, managed_instruction_set);
    ...
}
~~~

​	我们可以在这里插入一个日志，看看在android启动完成时，为我们孵化出了哪些进程。

~~~cpp
env->CallStaticVoidMethod(gZygoteClass, gCallPostForkChildHooks, runtime_flags,
                              is_system_server, is_child_zygote, managed_instruction_set);
ALOGW("start CallStaticVoidMethod current process:%s", nice_name_ptr);
~~~

​	然后编译aosp后刷入手机中。

~~~
// 执行脚本初始化编译环境
source ./build/envsetup.sh
// 选择要编译的版本
lunch aosp_blueline-userdebug
// 多线程编译
make -j$(nproc --all)
// 设置刷机目录
export ANDROID_PRODUCT_OUT=/home/king/android_src/mikrom_out/target/product/blueline
// 手机重启进入bootloader
adb reboot bootloader
// 查看手机是否已经进入bootloader了
fastboot devices
// 将刚刚编译的系统刷入手机
fastboot flashall -w
~~~

​	然后我们使用android studio的logcat查看日志，或者直接使用命令`adb logcat > tmp.log`将日志输出到文件中，再进行观察。

~~~
system_process                       W  start CallStaticVoidMethod current process:(null)
com.android.bluetooth                W  start CallStaticVoidMethod current process:com.android.bluetooth
com.android.systemui                 W  start CallStaticVoidMethod current process:com.android.systemui
pid-2292                             W  start CallStaticVoidMethod current process:WebViewLoader-armeabi-v7a
pid-2293                             W  start CallStaticVoidMethod current process:WebViewLoader-arm64-v8a
com.android.networkstack             W  start CallStaticVoidMethod current process:com.android.networkstack.process
com.qualcomm.qti.telephonyservice    W  start CallStaticVoidMethod current process:com.qualcomm.qti.telephonyservice
pid-2401                             W  start CallStaticVoidMethod current process:webview_zygote
com.android.se                       W  start CallStaticVoidMethod current process:com.android.se
com.android.phone                    W  start CallStaticVoidMethod current process:com.android.phone
com.android.settings                 W  start CallStaticVoidMethod current process:com.android.settings
android.ext.services                 W  start CallStaticVoidMethod current process:android.ext.services
com.android.launcher3                W  start CallStaticVoidMethod current process:com.android.launcher3
com....cellbroadcastreceiver.module  W  start CallStaticVoidMethod current process:com.android.cellbroadcastreceiver.module
com.android.carrierconfig            W  start CallStaticVoidMethod current process:com.android.carrierconfig
com.android.providers.blockednumber  W  start CallStaticVoidMethod current process:android.process.acore
pid-2859                             W  start CallStaticVoidMethod current process:com.android.deskclock
pid-2899                             W  start CallStaticVoidMethod current process:com.android.nfc
pid-2927                             W  start CallStaticVoidMethod current process:com.android.keychain
pid-2944                             W  start CallStaticVoidMethod current process:com.android.providers.media.module
pid-3028                             W  start CallStaticVoidMethod current process:com.android.quicksearchbox
pid-3059                             W  start CallStaticVoidMethod current process:com.android.printspooler
pid-3077                             W  start CallStaticVoidMethod current process:com.android.music
pid-3112                             W  start CallStaticVoidMethod current process:com.android.traceur
pid-3145                             W  start CallStaticVoidMethod current process:com.android.dialer
pid-3151                             W  start CallStaticVoidMethod current process:android.process.media
pid-3213                             W  start CallStaticVoidMethod current process:com.android.calendar
pid-3230                             W  start CallStaticVoidMethod current process:com.android.imsserviceentitlement
pid-3256                             W  start CallStaticVoidMethod current process:com.android.camera2
pid-3277                             W  start CallStaticVoidMethod current process:com.android.contacts
pid-3302                             W  start CallStaticVoidMethod current process:com.android.dynsystem
pid-3322                             W  start CallStaticVoidMethod current process:com.android.dynsystem:dynsystem
pid-3337                             W  start CallStaticVoidMethod current process:com.android.inputmethod.latin
pid-3359                             W  start CallStaticVoidMethod current process:com.android.managedprovisioning
pid-3380                             W  start CallStaticVoidMethod current process:com.android.messaging
pid-3413                             W  start CallStaticVoidMethod current process:com.android.onetimeinitializer
pid-3436                             W  start CallStaticVoidMethod current process:com.android.packageinstaller
pid-3455                             W  start CallStaticVoidMethod current process:com.android.permissioncontroller
pid-3480                             W  start CallStaticVoidMethod current process:com.android.providers.calendar
pid-3503                             W  start CallStaticVoidMethod current process:com.android.settings
pid-3504                             W  start CallStaticVoidMethod current process:com.android.localtransport
pid-3545                             W  start CallStaticVoidMethod current process:com.android.shell
pid-3568                             W  start CallStaticVoidMethod current process:com.android.statementservice
pid-3595                             W  start CallStaticVoidMethod current process:com.android.quicksearchbox
pid-3615                             W  start CallStaticVoidMethod current process:com.android.cellbroadcastreceiver.module
pid-3638                             W  start CallStaticVoidMethod current process:com.android.externalstorage

~~~

​	从日志中可以看到system_process进程是孵化出来的一个进程，然后还孵化了一堆系统相关的进程，包括launcher桌面应用管理的系统应用。

​	根据我们前文看到的一系列的代码，我们能够在代码中看到以下几个结论

​	1、所有进程均来自于zygote进程的fork而来，所以zygote是进程的始祖

​	2、zygote是在ZygoteServer这个服务中收到消息后，再去fork出新进程的

​	3、在第一个zygote进程中创建的ZygoteServer，并开始监听消息。

​	4、zygote进程启动是通过app_process执行程序启动的

​	5、由init进程解析init.rc时启动的第一个zygote

​	最后结合我们观测到的代码流程，再看下面的一个汇总图。不需要完全理解启动过程中的所有的处理，重点是在这里留下一个大致的印象以及简单的整理。

![image](.\images\android-boot.jpg)

## 3.7 Android app应用启动

​	经过一系列的代码跟踪，我们学习到了android是如何启动的，系统服务是如何启动的，进程是如何启动。接下来相信大家也好奇，当我们点开一个应用后，在android为我们做了一系列的什么事，最后打开了这个app，调用到MainActivity的onCreate的呢。

​	当我们的Android成功进入系统后，在主界面中显示的桌面是一个叫做Launcher的系统应用，它是用来显示系统中已经安装的应用程序，并将这些信息的图标作为快捷方式显示在屏幕上，当用户点击图标时，Launcher就会帮助我们启动对应的应用。在前文中，我们从forkSystemServer的流程中，最后能看到系统启动准备就绪后拉起了Launcher的应用。

​	那么Launcher是如何打开一个应用的呢？其实Launcher本身就是作为第一个应用在系统启动后首先打开的，那么既然Launcher就是应用。那么我们在手机上看到各种应用的图标，就是它读取到需要展示的数据，然后布局展示出来的，点击后打开应用，就是给每个item设置的点击事件进行处理的。接着我们来看看这个Launcher应用的源码。

​	查看代码`frameworks/base/core/java/android/app/LauncherActivity.java`。

~~~java
public abstract class LauncherActivity extends ListActivity {
	...
	@Override
    protected void onListItemClick(ListView l, View v, int position, long id) {
        Intent intent = intentForPosition(position);
        startActivity(intent);
    }
	...
}
~~~

​	如果你是一名android开发人员，相信你对startActivity这个函数非常熟悉了，但是startActivity是如何打开一个应用的呢，很多人不会深入了解，但是我们有了前文中的一系列基础铺垫，这时你已经能尝试追踪调用链了。现在我们继续深入挖掘startActivity的原理。

​	查看代码`frameworks/base/core/java/android/app/Activity.java`

~~~java
public void startActivity(Intent intent, @Nullable Bundle options) {
        ...
        if (options != null) {
            startActivityForResult(intent, -1, options);
        } else {
            // Note we want to go through this call for compatibility with
            // applications that may have overridden the method.
            startActivityForResult(intent, -1);
        }
    }

~~~

​	继续追踪startActivityForResult

~~~java

// 继续追踪startActivityForResult
public void startActivityForResult(
            String who, Intent intent, int requestCode, @Nullable Bundle options) {
        Uri referrer = onProvideReferrer();
        if (referrer != null) {
            intent.putExtra(Intent.EXTRA_REFERRER, referrer);
        }
        options = transferSpringboardActivityOptions(options);
        Instrumentation.ActivityResult ar =
            mInstrumentation.execStartActivity(
                this, mMainThread.getApplicationThread(), mToken, who,
                intent, requestCode, options);
        if (ar != null) {
            mMainThread.sendActivityResult(
                mToken, who, requestCode,
                ar.getResultCode(), ar.getResultData());
        }
        cancelInputsAndStartExitTransition(options);
    }
~~~

​	接下来的关键函数是execStartActivity，我们继续深入

~~~java
// 继续追踪execStartActivity
public ActivityResult execStartActivity(
            Context who, IBinder contextThread, IBinder token, Activity target,
            Intent intent, int requestCode, Bundle options) {
        ...
        try {
            intent.migrateExtraStreamToClipData(who);
            intent.prepareToLeaveProcess(who);
            int result = ActivityTaskManager.getService().startActivity(whoThread,
                    who.getOpPackageName(), who.getAttributionTag(), intent,
                    intent.resolveTypeIfNeeded(who.getContentResolver()), token,
                    target != null ? target.mEmbeddedID : null, requestCode, 0, null, options);
            checkStartActivityResult(result, intent);
        } catch (RemoteException e) {
            throw new RuntimeException("Failure from system", e);
        }
        return null;
    }


~~~

​	接下来发现是ActivityTaskManager对应的service调用的startActivity。

​	查看代码`frameworks/base/services/core/java/com/android/server/wm/ActivityTaskManagerService.java`

~~~java

public final int startActivity(IApplicationThread caller, String callingPackage,
                               String callingFeatureId, Intent intent, String resolvedType, IBinder resultTo,
                               String resultWho, int requestCode, int startFlags, ProfilerInfo profilerInfo,
                               Bundle bOptions) {
    return startActivityAsUser(caller, callingPackage, callingFeatureId, intent, resolvedType,
                               resultTo, resultWho, requestCode, startFlags, profilerInfo, bOptions,
                               UserHandle.getCallingUserId());
}

private int startActivityAsUser(IApplicationThread caller, String callingPackage,
            @Nullable String callingFeatureId, Intent intent, String resolvedType,
            IBinder resultTo, String resultWho, int requestCode, int startFlags,
            ProfilerInfo profilerInfo, Bundle bOptions, int userId, boolean validateIncomingUser) {
        ...
        // TODO: Switch to user app stacks here.
        return getActivityStartController().obtainStarter(intent, "startActivityAsUser")
                .setCaller(caller)
                .setCallingPackage(callingPackage)
                .setCallingFeatureId(callingFeatureId)
                .setResolvedType(resolvedType)
                .setResultTo(resultTo)
                .setResultWho(resultWho)
                .setRequestCode(requestCode)
                .setStartFlags(startFlags)
                .setProfilerInfo(profilerInfo)
                .setActivityOptions(bOptions)
                .setUserId(userId)
                .execute();

    }

~~~

​	最后是调用的execute，我们先看看obtainStarter返回的对象类型

~~~java
ActivityStarter obtainStarter(Intent intent, String reason) {
        return mFactory.obtain().setIntent(intent).setReason(reason);
    }
~~~

​	看到返回的是ActivityStarter类型，我们到找到对应的excute的实现

​	TODO 下面的代码帮我补充下细节描述

~~~java
// 处理 Activity 启动请求的接口 
int execute() {
        ...
        res = executeRequest(mRequest);
		...
    }

// 各种权限检查，合法的请求则继续
private int executeRequest(Request request) {
        ...
        mLastStartActivityResult = startActivityUnchecked(r, sourceRecord, voiceSession,
                request.voiceInteractor, startFlags, true /* doResume */, checkedOptions, inTask,
                restrictedBgActivity, intentGrants);

        ...
    }


private int startActivityUnchecked(final ActivityRecord r, ActivityRecord sourceRecord,
                IVoiceInteractionSession voiceSession, IVoiceInteractor voiceInteractor,
                int startFlags, boolean doResume, ActivityOptions options, Task inTask,
                boolean restrictedBgActivity, NeededUriGrants intentGrants) {
       ...
       Trace.traceBegin(Trace.TRACE_TAG_WINDOW_MANAGER, "startActivityInner");
       result = startActivityInner(r, sourceRecord, voiceSession, voiceInteractor,
       startFlags, doResume, options, inTask, restrictedBgActivity, intentGrants);
       ...
    }



int startActivityInner(final ActivityRecord r, ActivityRecord sourceRecord,
            IVoiceInteractionSession voiceSession, IVoiceInteractor voiceInteractor,
            int startFlags, boolean doResume, ActivityOptions options, Task inTask,
            boolean restrictedBgActivity, NeededUriGrants intentGrants) {
        setInitialState(r, options, inTask, doResume, startFlags, sourceRecord, voiceSession,
                voiceInteractor, restrictedBgActivity);

        ...
        // 主要作用是判断当前 activity 是否可见以及是否需要为其新建 Task
        mTargetRootTask.startActivityLocked(mStartActivity,
                topRootTask != null ? topRootTask.getTopNonFinishingActivity() : null, newTask,
                mKeepCurTransition, mOptions, sourceRecord);
        if (mDoResume) {
            final ActivityRecord topTaskActivity =
                    mStartActivity.getTask().topRunningActivityLocked();
            if (!mTargetRootTask.isTopActivityFocusable()
                    || (topTaskActivity != null && topTaskActivity.isTaskOverlay()
                    && mStartActivity != topTaskActivity)) {
               	...
            } else {
                if (mTargetRootTask.isTopActivityFocusable()
                        && !mRootWindowContainer.isTopDisplayFocusedRootTask(mTargetRootTask)) {
                    mTargetRootTask.moveToFront("startActivityInner");
                }
                
                mRootWindowContainer.resumeFocusedTasksTopActivities(
                        mTargetRootTask, mStartActivity, mOptions, mTransientLaunch);
            }
        }
        ...
    }


// 将所有聚焦的 Task 的所有 Activity 恢复运行，因为有些刚加入的 Activity 是处于暂停状态的
boolean resumeFocusedTasksTopActivities(
            Task targetRootTask, ActivityRecord target, ActivityOptions targetOptions,
            boolean deferPause) {
        ...
        for (int displayNdx = getChildCount() - 1; displayNdx >= 0; --displayNdx) {
            final DisplayContent display = getChildAt(displayNdx);
            ...
            final Task focusedRoot = display.getFocusedRootTask();
            if (focusedRoot != null) {
                result |= focusedRoot.resumeTopActivityUncheckedLocked(target, targetOptions);
            } else if (targetRootTask == null) {
                result |= resumeHomeActivity(null /* prev */, "no-focusable-task",
                                             display.getDefaultTaskDisplayArea());
            }
            
        }

        return result;
    }


boolean resumeTopActivityUncheckedLocked(ActivityRecord prev, ActivityOptions options,
            boolean deferPause) {
        ...
        someActivityResumed = resumeTopActivityInnerLocked(prev, options, deferPause);
        ...
    }


private boolean resumeTopActivityInnerLocked(ActivityRecord prev, ActivityOptions options,
            boolean deferPause) {
        ...
        
        mTaskSupervisor.startSpecificActivity(next, true, true);
        ...

        return true;
    }

~~~

​	接下来startProcessAsync判断目标Activity的应用是否在运行，在运行的则直接启动，否则启动新进程。

~~~java
void startSpecificActivity(ActivityRecord r, boolean andResume, boolean checkConfig) {
        // Is this activity's application already running?
        final WindowProcessController wpc =
                mService.getProcessController(r.processName, r.info.applicationInfo.uid);

        boolean knownToBeDead = false;
    	// 在运行中的直接启动
        if (wpc != null && wpc.hasThread()) {
            try {
                realStartActivityLocked(r, wpc, andResume, checkConfig);
                return;
            } catch (RemoteException e) {
                Slog.w(TAG, "Exception when starting activity "
                        + r.intent.getComponent().flattenToShortString(), e);
            }

            // If a dead object exception was thrown -- fall through to
            // restart the application.
            knownToBeDead = true;
        }

        r.notifyUnknownVisibilityLaunchedForKeyguardTransition();
		// 不在运行中则启动新进程
        final boolean isTop = andResume && r.isTopRunningActivity();
        mService.startProcessAsync(r, knownToBeDead, isTop, isTop ? "top-activity" : "activity");
    }
~~~

​	我们主要关注开启一个新应用的流程，所以这里只追踪startProcessAsync调用即可。

~~~java
void startProcessAsync(ActivityRecord activity, boolean knownToBeDead, boolean isTop,
            String hostingType) {
        try {
            if (Trace.isTagEnabled(TRACE_TAG_WINDOW_MANAGER)) {
                Trace.traceBegin(TRACE_TAG_WINDOW_MANAGER, "dispatchingStartProcess:"
                        + activity.processName);
            }
            // Post message to start process to avoid possible deadlock of calling into AMS with the
            // ATMS lock held.
            final Message m = PooledLambda.obtainMessage(ActivityManagerInternal::startProcess,
                    mAmInternal, activity.processName, activity.info.applicationInfo, knownToBeDead,
                    isTop, hostingType, activity.intent.getComponent());
            mH.sendMessage(m);
        } finally {
            Trace.traceEnd(TRACE_TAG_WINDOW_MANAGER);
        }
    }
~~~

​	上面开启新进程的代码是异步发送消息给了ActivityManagerService。找到AMS中对应的startProcess

~~~java
@Override
        public void startProcess(String processName, ApplicationInfo info, boolean knownToBeDead,
                boolean isTop, String hostingType, ComponentName hostingName) {
            try {
                if (Trace.isTagEnabled(Trace.TRACE_TAG_ACTIVITY_MANAGER)) {
                    Trace.traceBegin(Trace.TRACE_TAG_ACTIVITY_MANAGER, "startProcess:"
                            + processName);
                }
                synchronized (ActivityManagerService.this) {
                    // If the process is known as top app, set a hint so when the process is
                    // started, the top priority can be applied immediately to avoid cpu being
                    // preempted by other processes before attaching the process of top app.
                    startProcessLocked(processName, info, knownToBeDead, 0 /* intentFlags */,
                            new HostingRecord(hostingType, hostingName, isTop),
                            ZYGOTE_POLICY_FLAG_LATENCY_SENSITIVE, false /* allowWhileBooting */,
                            false /* isolated */);
                }
            } finally {
                Trace.traceEnd(Trace.TRACE_TAG_ACTIVITY_MANAGER);
            }
        }

// 继续追踪startProcessLocked
final ProcessRecord startProcessLocked(String processName,
            ApplicationInfo info, boolean knownToBeDead, int intentFlags,
            HostingRecord hostingRecord, int zygotePolicyFlags, boolean allowWhileBooting,
            boolean isolated) {
        return mProcessList.startProcessLocked(processName, info, knownToBeDead, intentFlags,
                hostingRecord, zygotePolicyFlags, allowWhileBooting, isolated, 0 /* isolatedUid */,
                null /* ABI override */, null /* entryPoint */,
                null /* entryPointArgs */, null /* crashHandler */);
    }

// 在这里初始化了一堆进程信息，然后调用了另一个重载
// 并且注意entryPoint赋值android.app.ActivityThread
boolean startProcessLocked(ProcessRecord app, HostingRecord hostingRecord,
            int zygotePolicyFlags, boolean disableHiddenApiChecks, boolean disableTestApiChecks,
            String abiOverride) {
        	...
            // the PID of the new process, or else throw a RuntimeException.
            final String entryPoint = "android.app.ActivityThread";
			
            return startProcessLocked(hostingRecord, entryPoint, app, uid, gids,
                    runtimeFlags, zygotePolicyFlags, mountExternal, seInfo, requiredAbi,
                    instructionSet, invokeWith, startTime);
    }

// 
boolean startProcessLocked(HostingRecord hostingRecord, String entryPoint, ProcessRecord app,
            int uid, int[] gids, int runtimeFlags, int zygotePolicyFlags, int mountExternal,
            String seInfo, String requiredAbi, String instructionSet, String invokeWith,
            long startTime) {
        	...
            final Process.ProcessStartResult startResult = startProcess(hostingRecord,
                                                                            entryPoint, app,
                                                                            uid, gids, runtimeFlags, zygotePolicyFlags, mountExternal, seInfo,
                                                                            requiredAbi, instructionSet, invokeWith, startTime);
                handleProcessStartedLocked(app, startResult.pid, startResult.usingWrapper,
                                           startSeq, false);
            ...
    		return app.getPid() > 0;
        
    }

// 继续查看startProcess
private Process.ProcessStartResult startProcess(HostingRecord hostingRecord, String entryPoint,
            ProcessRecord app, int uid, int[] gids, int runtimeFlags, int zygotePolicyFlags,
            int mountExternal, String seInfo, String requiredAbi, String instructionSet,
            String invokeWith, long startTime) {
        	...
            final Process.ProcessStartResult startResult;
            boolean regularZygote = false;
    		// 这里根据应用情况使用不同类型的zygote来启动进程
            if (hostingRecord.usesWebviewZygote()) {
                startResult = startWebView(entryPoint,
                        app.processName, uid, uid, gids, runtimeFlags, mountExternal,
                        app.info.targetSdkVersion, seInfo, requiredAbi, instructionSet,
                        app.info.dataDir, null, app.info.packageName,
                        app.getDisabledCompatChanges(),
                        new String[]{PROC_START_SEQ_IDENT + app.getStartSeq()});
            } else if (hostingRecord.usesAppZygote()) {
                final AppZygote appZygote = createAppZygoteForProcessIfNeeded(app);

                // We can't isolate app data and storage data as parent zygote already did that.
                startResult = appZygote.getProcess().start(entryPoint,
                        app.processName, uid, uid, gids, runtimeFlags, mountExternal,
                        app.info.targetSdkVersion, seInfo, requiredAbi, instructionSet,
                        app.info.dataDir, null, app.info.packageName,
                        /*zygotePolicyFlags=*/ ZYGOTE_POLICY_FLAG_EMPTY, isTopApp,
                        app.getDisabledCompatChanges(), pkgDataInfoMap, allowlistedAppDataInfoMap,
                        false, false,
                        new String[]{PROC_START_SEQ_IDENT + app.getStartSeq()});
            } else {
                regularZygote = true;
                startResult = Process.start(entryPoint,
                        app.processName, uid, uid, gids, runtimeFlags, mountExternal,
                        app.info.targetSdkVersion, seInfo, requiredAbi, instructionSet,
                        app.info.dataDir, invokeWith, app.info.packageName, zygotePolicyFlags,
                        isTopApp, app.getDisabledCompatChanges(), pkgDataInfoMap,
                        allowlistedAppDataInfoMap, bindMountAppsData, bindMountAppStorageDirs,
                        new String[]{PROC_START_SEQ_IDENT + app.getStartSeq()});
            }

            if (!regularZygote) {
                // webview and app zygote don't have the permission to create the nodes
                if (Process.createProcessGroup(uid, startResult.pid) < 0) {
                    Slog.e(ActivityManagerService.TAG, "Unable to create process group for "
                            + app.processName + " (" + startResult.pid + ")");
                }
            }
			...
            return startResult;
    }

~~~

​	这里我们看到了zygote有三种类型，根据启动的应用信息使用不同类型的zygote来启动。

1、regularZygote 常规进程，zygote32/zygote64 进程，是所有 Android Java 应用的父进程

2、appZygote 应用进程，比常规进程多一些限制。

3、webviewZygote 辅助zygote进程，渲染不可信的web内容，最严格的安全限制

​	三种zygote类型的启动流程差不多的，所以我们看常规进程启动即可。首先看getProcess返回的是什么类型

~~~java
public ChildZygoteProcess getProcess() {
        synchronized (mLock) {
            if (mZygote != null) return mZygote;

            connectToZygoteIfNeededLocked();
            return mZygote;
        }
    }
~~~

​	所以我们应该找ChildZygoteProcess的start函数，然后找到类定义后，发现没有start，那么应该就是父类中的实现。

~~~java
public class ChildZygoteProcess extends ZygoteProcess {
    private final int mPid;
    
    ChildZygoteProcess(LocalSocketAddress socketAddress, int pid) {
        super(socketAddress, null);
        mPid = pid;
    }
    
    public int getPid() {
        return mPid;
    }
}

~~~

​	继续找到父类ZygoteProcess的start函数，参数太长，这里省略掉参数的描述

~~~java
public final Process.ProcessStartResult start(...) {
        ...
        return startViaZygote(processClass, niceName, uid, gid, gids,
                    runtimeFlags, mountExternal, targetSdkVersion, seInfo,
                    abi, instructionSet, appDataDir, invokeWith, /*startChildZygote=*/ false,
                    packageName, zygotePolicyFlags, isTopApp, disabledCompatChanges,
                    pkgDataInfoMap, allowlistedDataInfoList, bindMountAppsData,
                    bindMountAppStorageDirs, zygoteArgs);
        ...
    }


private Process.ProcessStartResult startViaZygote(...)
                                                      throws ZygoteStartFailedEx {
        ArrayList<String> argsForZygote = new ArrayList<>();
		// 前面是将前面准备的参数填充好
        // --runtime-args, --setuid=, --setgid=,
        // and --setgroups= must go first
        argsForZygote.add("--runtime-args");
        argsForZygote.add("--setuid=" + uid);
        argsForZygote.add("--setgid=" + gid);
        argsForZygote.add("--runtime-flags=" + runtimeFlags);
        if (mountExternal == Zygote.MOUNT_EXTERNAL_DEFAULT) {
            argsForZygote.add("--mount-external-default");
        } else if (mountExternal == Zygote.MOUNT_EXTERNAL_INSTALLER) {
            argsForZygote.add("--mount-external-installer");
        } else if (mountExternal == Zygote.MOUNT_EXTERNAL_PASS_THROUGH) {
            argsForZygote.add("--mount-external-pass-through");
        } else if (mountExternal == Zygote.MOUNT_EXTERNAL_ANDROID_WRITABLE) {
            argsForZygote.add("--mount-external-android-writable");
        }
		...
        synchronized(mLock) {
            // The USAP pool can not be used if the application will not use the systems graphics
            // driver.  If that driver is requested use the Zygote application start path.
            return zygoteSendArgsAndGetResult(openZygoteSocketIfNeeded(abi),
                                              zygotePolicyFlags,
                                              argsForZygote);
        }
    }

private Process.ProcessStartResult zygoteSendArgsAndGetResult(
            ZygoteState zygoteState, int zygotePolicyFlags, @NonNull ArrayList<String> args)
            throws ZygoteStartFailedEx {
        ...
        //是否用非特定的应用程序进程池进行处理，默认不使用
        if (shouldAttemptUsapLaunch(zygotePolicyFlags, args)) {
            try {
                return attemptUsapSendArgsAndGetResult(zygoteState, msgStr);
            } catch (IOException ex) {
                // If there was an IOException using the USAP pool we will log the error and
                // attempt to start the process through the Zygote.
                Log.e(LOG_TAG, "IO Exception while communicating with USAP pool - "
                        + ex.getMessage());
            }
        }

        return attemptZygoteSendArgsAndGetResult(zygoteState, msgStr);
    }


private Process.ProcessStartResult attemptZygoteSendArgsAndGetResult(
            ZygoteState zygoteState, String msgStr) throws ZygoteStartFailedEx {
        try {
            final BufferedWriter zygoteWriter = zygoteState.mZygoteOutputWriter;
            final DataInputStream zygoteInputStream = zygoteState.mZygoteInputStream;
			// 这里实际就是连接SocketServer了，发送一个消息给zygote孵化出来的第一个进程
            zygoteWriter.write(msgStr);
            zygoteWriter.flush();

            Process.ProcessStartResult result = new Process.ProcessStartResult();
            result.pid = zygoteInputStream.readInt();
            result.usingWrapper = zygoteInputStream.readBoolean();
			// ZygoteServer创建好进程后，返回pid
            if (result.pid < 0) {
                throw new ZygoteStartFailedEx("fork() failed");
            }

            return result;
        } catch (IOException ex) {
            zygoteState.close();
            Log.e(LOG_TAG, "IO Exception while communicating with Zygote - "
                    + ex.toString());
            throw new ZygoteStartFailedEx(ex);
        }
    }
~~~

​	那么到这里，我们回首看看前文中介绍ZygoteServer启动进程的流程，我们当时看到执行到最后是findStaticMain函数，是获取一个类名下的main函数，并返回后进行调用。然后现在我们启动进程时，在startProcessLocked函数中能看到类名赋值是android.app.ActivityThread，所以这里和ZygoteServer进行通信创建线程，最后调用的函数就是android.app.ActivityThread中的main函数。这样一来，启动流程就衔接上了，ActivityThread是Android应用程序运行的主线程，负责处理应用程序的所有生命周期事件，接收系统消息并处理它们，我们继续看看这个main函数

~~~java
public static void main(String[] args) {
    	...
    	ActivityThread thread = new ActivityThread();
        thread.attach(false, startSeq);
        ...
        Looper.loop();
    }

//接着看attach做了什么
private void attach(boolean system, long startSeq) {
        ...
        mgr.attachApplication(mAppThread, startSeq);
        ...
    }
~~~

​	mgr就是AMS，所以继续回到ActivityManagerService查看attachApplication

~~~java
public final void attachApplication(IApplicationThread thread, long startSeq) {
        if (thread == null) {
            throw new SecurityException("Invalid application interface");
        }
        synchronized (this) {
            int callingPid = Binder.getCallingPid();
            final int callingUid = Binder.getCallingUid();
            final long origId = Binder.clearCallingIdentity();
            attachApplicationLocked(thread, callingPid, callingUid, startSeq);
            Binder.restoreCallingIdentity(origId);
        }
    }

// 继续追踪attachApplicationLocked
private boolean attachApplicationLocked(@NonNull IApplicationThread thread,
            int pid, int callingUid, long startSeq) {

        	...
            if (app.getIsolatedEntryPoint() != null) {
                // This is an isolated process which should just call an entry point instead of
                // being bound to an application.
                thread.runIsolatedEntryPoint(
                        app.getIsolatedEntryPoint(), app.getIsolatedEntryPointArgs());
            } else if (instr2 != null) {
                thread.bindApplication(processName, appInfo, providerList,
                        instr2.mClass,
                        profilerInfo, instr2.mArguments,
                        instr2.mWatcher,
                        instr2.mUiAutomationConnection, testMode,
                        mBinderTransactionTrackingEnabled, enableTrackAllocation,
                        isRestrictedBackupMode || !normalMode, app.isPersistent(),
                        new Configuration(app.getWindowProcessController().getConfiguration()),
                        app.getCompat(), getCommonServicesLocked(app.isolated),
                        mCoreSettingsObserver.getCoreSettingsLocked(),
                        buildSerial, autofillOptions, contentCaptureOptions,
                        app.getDisabledCompatChanges(), serializedSystemFontMap);
            } else {
                thread.bindApplication(processName, appInfo, providerList, null, profilerInfo,
                        null, null, null, testMode,
                        mBinderTransactionTrackingEnabled, enableTrackAllocation,
                        isRestrictedBackupMode || !normalMode, app.isPersistent(),
                        new Configuration(app.getWindowProcessController().getConfiguration()),
                        app.getCompat(), getCommonServicesLocked(app.isolated),
                        mCoreSettingsObserver.getCoreSettingsLocked(),
                        buildSerial, autofillOptions, contentCaptureOptions,
                        app.getDisabledCompatChanges(), serializedSystemFontMap);
            }
			...
    }
~~~

​	最后重新调用回ActivityThread的bindApplication，继续跟进去查看

~~~java
public final void bindApplication(...) {
            ...
            AppBindData data = new AppBindData();
            data.processName = processName;
            data.appInfo = appInfo;
            data.providers = providerList.getList();
            data.instrumentationName = instrumentationName;
            data.instrumentationArgs = instrumentationArgs;
            data.instrumentationWatcher = instrumentationWatcher;
            data.instrumentationUiAutomationConnection = instrumentationUiConnection;
            data.debugMode = debugMode;
            data.enableBinderTracking = enableBinderTracking;
            data.trackAllocation = trackAllocation;
            data.restrictedBackupMode = isRestrictedBackupMode;
            data.persistent = persistent;
            data.config = config;
            data.compatInfo = compatInfo;
            data.initProfilerInfo = profilerInfo;
            data.buildSerial = buildSerial;
            data.autofillOptions = autofillOptions;
            data.contentCaptureOptions = contentCaptureOptions;
            data.disabledCompatChanges = disabledCompatChanges;
            data.mSerializedSystemFontMap = serializedSystemFontMap;
            sendMessage(H.BIND_APPLICATION, data);
        }
~~~

​	这时AppBindData数据初始化完成了，最后发送消息BIND_APPLICATION通知准备就绪，并将准备好的数据发送过去，接着我们查看消息循环的处理部分handleMessage函数，看这个数据传给哪个函数处理了。

~~~java
public void handleMessage(Message msg) {
            if (DEBUG_MESSAGES) Slog.v(TAG, ">>> handling: " + codeToString(msg.what));
            switch (msg.what) {
                case BIND_APPLICATION:
                    Trace.traceBegin(Trace.TRACE_TAG_ACTIVITY_MANAGER, "bindApplication");
                    AppBindData data = (AppBindData)msg.obj;
                    handleBindApplication(data);
                    Trace.traceEnd(Trace.TRACE_TAG_ACTIVITY_MANAGER);
                    break;
             ...
}
~~~

​	发现调用到了handleBindApplication，继续追踪这个函数

~~~java
private void handleBindApplication(AppBindData data) {
        ...
        //前面准备好的data数据赋值给了mBoundApplication
        mBoundApplication = data;
        ...
        // 创建出了Context
        final ContextImpl appContext = ContextImpl.createAppContext(this, data.info);
        ...
        Application app;
        final StrictMode.ThreadPolicy savedPolicy = StrictMode.allowThreadDiskWrites();
        final StrictMode.ThreadPolicy writesAllowedPolicy = StrictMode.getThreadPolicy();
        try {
            // 创建出了Application
            app = data.info.makeApplication(data.restrictedBackupMode, null);
            ...
            // Application赋值给了mInitialApplication
            mInitialApplication = app;
            ...
            try {
                mInstrumentation.callApplicationOnCreate(app);
            } catch (Exception e) {
                ...
            }
        } finally {
            ...
        }
		...
    }

// 看看是如何创建出Application的
public Application makeApplication(boolean forceDefaultAppClass,
            Instrumentation instrumentation) {
        if (mApplication != null) {
            return mApplication;
        }
		...
        app = mActivityThread.mInstrumentation.newApplication(
                    cl, appClass, appContext);
        ...
        return app;
    }

// 继续看newApplication的实现
static public Application newApplication(Class<?> clazz, Context context)
            throws InstantiationException, IllegalAccessException, 
            ClassNotFoundException {
        Application app = (Application)clazz.newInstance();
        // 最后发现调用了attach
        app.attach(context);
        return app;
    }

~~~

​	在上面我们看到了Context的创建和Application的创建，最后我们继续看看怎么调用到自己开发的app中的onCreate的，继续追踪callApplicationOnCreate的实现

~~~java
public void callApplicationOnCreate(Application app) {
    	...
        app.onCreate();
    }
~~~

​	到这里我们成功跟踪到最后调用app应用的onCreate函数，并且发现为什么很多人喜欢hook attach函数，因为在Application创建出来最早先调用了这个函数，所以这里是一个较早hook时机。下面是结合我们跟踪的代码总结的简单的启动流程图。

TODO 流程图

​	在这一小节我们不断加深对Android源码的了解，由分析Android的启动流程和App应用的启动流程两个分析点入手将过程划为一条线，接着我们将围绕着追踪流程中，碰到的一些较为重要的模块进行介绍。

## 3.8 了解Service

​	Service是一种运行在后台的组件也可以称之为服务，它不像Activity那样有前台显示用户界面的能力，而是一种更加抽象的组件，它可以提供后台服务，如播放音乐、下载文件等操作，或者在后台定时执行某些任务。Service可以被应用程序绑定，也可以独立运行，它可以接收外部的命令，执行耗时的任务，并提供不依赖于用户界面的后台运行。这些

​	在Android启动流程中，我们就已经看到了很多Service的启动，前文代码看到当系统启动后通过forkSystemServer执行到SystemServer来启动一系列的Service。这些Service有着各自负责的功能，其中最关键的是ActivityManagerService，常常被我们简称为AMS。而启动了AMS的SystemServer也是一个服务，这个服务负责在Android完成启动后，加载和启动所有的系统服务，管理系统级别的资源。

​	AMS是Android系统中的一个核心服务，它是一个系统级服务，负责Android系统中的所有活动管理，包括应用程序的启动，暂停，恢复，终止，以及对系统资源的管理和分配。负责Android系统中所有活动的管理。它负责管理任务栈，并允许任务栈中的任务来回切换，以便在任务之间改变焦点。它还负责管理进程，并将进程启动，暂停，恢复，终止，以及分配系统资源。在启动流程中我们能看到，所有Service都是由它来启动的，下面是启动的相关代码。

~~~java
ActivityTaskManagerService atm = mSystemServiceManager.startService(
        ActivityTaskManagerService.Lifecycle.class).getService();
~~~

​	除了AMS外，也有其他重要的Service为Android应用提供基础的功能，下面简单介绍这些常用的Service。

​	 WindowManagerService是Android系统中一个非常重要的服务，它主要功能是负责管理系统上所有窗口的显示和操作，包括管理全屏窗口、小窗口、弹窗、菜单和其他应用程序的窗口，使窗口在手机屏幕上正确的显示。 它包括以下几个部分： 

​	1、布局管理器：负责管理系统中所有窗口的位置和大小，实现窗口的移动、调整大小、切换窗口等功能。 

​	2、窗口管理器：负责管理系统中所有窗口的显示和操作，比如添加、移除、隐藏、显示窗口，以及设置窗口的属性如背景、边框、大小等。 

​	3、动画管理器：负责实现窗口的过渡动画，比如淡入淡出、缩放、旋转等。 

​	4、事件处理器：负责处理窗口上的触摸、按键等事件，实现窗口的响应功能。

​	PackageManagerService是Android系统中提供给应用程序访问Android软件包的主要服务。下面是这个服务提供的相关功能。

​	1、负责管理Android软件包的安装、删除和更新，以及软件包的查询和配置。

​	2、它有一个名为Packages.xml的XML文档，该文档是Android系统中所有软件包的列表，其中包含了每个软件包的基本信息，如应用程序的版本，安装时间，文件大小等。

​	3、同时还负责检查安装的软件包是否与Android系统兼容，并确保软件包的安全性。它还可以检查某一软件包是否已安装，并获取软件包的版本号。

​	4、提供了应用程序组件的管理功能，可以查看应用程序的组件，如活动，服务，广播接收器，内容提供器等，并提供对它们的控制。

​	5、提供了对Android系统的配置的访问，可以检查与Android系统相关的系统属性，用户设置，系统设置等。

​	PowerManagerService是Android系统中用来管理设备电源状态的服务可以有效地管理设备的电源，从而大大提升设备的电池续航能力，也可以降低设备运行时的功耗。它负责处理设备上的所有电源相关操作。下面是提供的相关功能。

​	1、设置设备的电源模式，如在电池和充电时的运行模式。

​	2、管理屏幕状态，如屏幕亮度、屏幕超时时间。

​	3、管理CPU频率，确保CPU在低频下运行，以节省电量。

​	4、根据需要自动检测电池电量，以及提供充电提醒。

​	5、管理设备上的设备锁以及设备唤醒功能，确保在特定情况下设备可以正常工作

​	InputMethodManagerService是Android系统中输入法服务的核心，它负责处理用户输入，管理输入法状态，以及向应用程序提供输入服务。

​	1、输入法管理：负责管理当前输入法，它可以安装、卸载和更新输入法，还可以管理系统的输入法开关，以及支持多种输入法语言切换。 

​	2、 输入法状态管理：管理输入法的状态，包括输入法最近使用的语言，以及输入法当前输入的内容和应用程序上下文。 

​	3、输入服务：可以通过服务接口为应用程序提供输入服务，例如，应用程序可以通过它来访问输入法的当前状态和内容，以及实时输入的文本内容。

​	4、 输入事件处理：可以接收并处理用户的输入事件，包括按键、触摸屏、语音输入等，并将这些输入事件发送给当前输入法，从而实现用户输入的实时响应。

​	NotificationManagerService是Android框架的一部分，它负责处理和管理应用程序发出的通知。它主要是用来管理系统的通知，包括消息、提醒、更新等，相关功能如下。

​	1、它实现了通知的管理，收集、组织、过滤通知，并将它们发送给用户。它能够管理所有应用程序发出的通知，包括系统通知、应用程序发出的通知，并可以根据用户的偏好，显示哪些通知。

​	2、包含一系列用于处理不同类型通知的回调方法，例如，当应用程序发出新消息时，它将调用NotificationManagerService的onNotificationPosted()回调方法，并将新消息传递给该方法。此外，NotificationManagerService还可以拦截用户设备上的所有通知，并在必要时修改它们，例如更改通知栏的显示格式等。

​	LocationManagerService是Android操作系统中的一个位置管理服务，相关功能如下。

​	1、可以根据应用程序的要求调用GPS、网络和其他位置技术来获取当前设备的定位信息。

​	2、可以根据设备的位置信息，控制应用程序的定位功能，以及设备的位置报警功能。

​	3、还可以收集设备的位置数据，并将其存储在系统中，以便应用程序可以获取设备的历史位置数据。

​	InputManagerService是Android系统中一个重要的核心服务，它负责输入设备的管理和控制，以及系统中所有输入事件的处理。相关功能如下。

​	1、负责管理Android系统的输入设备，如触摸屏、虚拟按键、键盘、轨迹球等。

​	2、会将输入事件传递给应用程序，以便处理和响应。 

​	3、负责输入设备的管理和控制，能够根据应用程序的需求，对输入设备进行调整和控制。 

​	4、负责处理Android系统中所有输入事件，并将处理结果传递给相应的应用程序。

​	AlarmManagerService负责处理所有系统定时任务，如闹钟，定时器等。它可以安排可执行的任务，使它们在指定的时刻开始执行。 

​	1、监控系统中的各种时间事件，以执行指定的任务。 

​	2、可以安排可执行的任务，使它们在指定的时刻开始执行。

​	3、可以发送唤醒广播，以启动指定的服务或应用程序。 

​	4、可以安排周期性的任务，可以在指定的时间间隔内重复执行指定的任务。 

​	5、可以用于处理设备睡眠、唤醒等系统状态切换。 

​	6、可以按照特定的时间间隔定期更新设备的时间。

​	NetworkManagementService是Android操作系统中的一种网络管理服务。它是Android操作系统的一部分，用于控制和管理Android系统中的网络连接，并且能够在不同的网络之间进行切换。 

​	1、能够检查和管理手机的网络状态，能够监控网络设备的连接状态，如WiFi、蓝牙、移动数据等，能够有效地检测当前手机所连接的网络信息和状态，并进行相应的网络状态管理。  	

​	2、能够为Android系统中的应用提供网络接入服务，提供网络连接状态的反馈，以及网络设备连接状态的反馈，以便应用能够更好的控制网络连接。  

​	3、能够实现网络连接的切换，并且能够在不同的网络之间进行切换，从而实现最优路由，有效地提升网络性能和体验。 

​	4、能够实现网络安全管理，可以针对不同的网络设备进行安全管理，以防止网络攻击，保护系统的安全性。  

​	5、能够实现网络信息的统计和分析，可以统计网络设备的使用情况，并对其进行分析，以便对网络的管理更加有效。

​	BluetoothService是Android操作系统中的一种服务，它可以实现蓝牙设备之间的无线通信。它提供了一种方便的方式来建立和管理蓝牙连接，使蓝牙设备之间能够进行文件传输、远程打印、蓝牙键盘连接等活动。

​	还有更多的系统服务为Android的运行提供着各模块的基础功能，这里就不展开详细叙述了，当我们对某一个服务的功能实现感兴趣时，我们可以顺着启动服务的地方开始跟踪代码，分析实现的逻辑。也可以直接参考系统服务的定义模式来自定义系统服务来提供特殊需求的功能。下面我们先分析一个系统服务的启动到它的代码实现。

​	

