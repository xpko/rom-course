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
	char *command_line;
	char *after_dashes;

	set_task_stack_end_magic(&init_task);
	scs_set_init_magic(&init_task);

	smp_setup_processor_id();
	debug_objects_early_init();

	cgroup_init_early();

	local_irq_disable();
	early_boot_irqs_disabled = true;

/*
 * Interrupts are still disabled. Do necessary setups, then
 * enable them
 */
	boot_cpu_init();
	page_address_init();
	pr_notice("%s", linux_banner);
	setup_arch(&command_line);
	/*
	 * Set up the the initial canary ASAP:
	 */
	boot_init_stack_canary();
	mm_init_cpumask(&init_mm);
	setup_command_line(command_line);
	setup_nr_cpu_ids();
	setup_per_cpu_areas();
	smp_prepare_boot_cpu();	/* arch-specific boot-cpu hooks */
	boot_cpu_hotplug_init();

	build_all_zonelists(NULL, NULL, false);
	page_alloc_init();

	pr_notice("Kernel command line: %s\n", boot_command_line);
	/* parameters may set static keys */
	jump_label_init();
	parse_early_param();
	after_dashes = parse_args("Booting kernel",
				  static_command_line, __start___param,
				  __stop___param - __start___param,
				  -1, -1, NULL, &unknown_bootoption);
	if (!IS_ERR_OR_NULL(after_dashes))
		parse_args("Setting init args", after_dashes, NULL, 0, -1, -1,
			   NULL, set_init_arg);

	/*
	 * These use large bootmem allocations and must precede
	 * kmem_cache_init()
	 */
	setup_log_buf(0);
	pidhash_init();
	vfs_caches_init_early();
	sort_main_extable();
	trap_init();
	mm_init();

	/*
	 * Set up the scheduler prior starting any interrupts (such as the
	 * timer interrupt). Full topology setup happens at smp_init()
	 * time - but meanwhile we still have a functioning scheduler.
	 */
	sched_init();
	/*
	 * Disable preemption - early bootup scheduling is extremely
	 * fragile until we cpu_idle() for the first time.
	 */
	preempt_disable();
	if (WARN(!irqs_disabled(),
		 "Interrupts were enabled *very* early, fixing it\n"))
		local_irq_disable();
	idr_init_cache();

	/*
	 * Allow workqueue creation and work item queueing/cancelling
	 * early.  Work item execution depends on kthreads and starts after
	 * workqueue_init().
	 */
	workqueue_init_early();

	rcu_init();

	/* trace_printk() and trace points may be used after this */
	trace_init();

	context_tracking_init();
	radix_tree_init();
	/* init some links before init_ISA_irqs() */
	early_irq_init();
	init_IRQ();
	tick_init();
	rcu_init_nohz();
	init_timers();
	hrtimers_init();
	softirq_init();
	timekeeping_init();
	time_init();
	sched_clock_postinit();
	printk_nmi_init();
	perf_event_init();
	profile_init();
	call_function_init();
	WARN(!irqs_disabled(), "Interrupts were enabled early\n");
	early_boot_irqs_disabled = false;
	local_irq_enable();

	kmem_cache_init_late();

	/*
	 * HACK ALERT! This is early. We're enabling the console before
	 * we've done PCI setups etc, and console_init() must be aware of
	 * this. But we do want output early, in case something goes wrong.
	 */
	console_init();
	if (panic_later)
		panic("Too many boot %s vars at `%s'", panic_later,
		      panic_param);

	lockdep_info();

	/*
	 * Need to run this when irqs are enabled, because it wants
	 * to self-test [hard/soft]-irqs on/off lock inversion bugs
	 * too:
	 */
	locking_selftest();

#ifdef CONFIG_BLK_DEV_INITRD
	if (initrd_start && !initrd_below_start_ok &&
	    page_to_pfn(virt_to_page((void *)initrd_start)) < min_low_pfn) {
		pr_crit("initrd overwritten (0x%08lx < 0x%08lx) - disabling it.\n",
		    page_to_pfn(virt_to_page((void *)initrd_start)),
		    min_low_pfn);
		initrd_start = 0;
	}
#endif
	page_ext_init();
	debug_objects_mem_init();
	kmemleak_init();
	setup_per_cpu_pageset();
	numa_policy_init();
	if (late_time_init)
		late_time_init();
	sched_clock_init();
	calibrate_delay();
	pidmap_init();
	anon_vma_init();
	acpi_early_init();
#ifdef CONFIG_X86
	if (efi_enabled(EFI_RUNTIME_SERVICES))
		efi_enter_virtual_mode();
#endif
#ifdef CONFIG_X86_ESPFIX64
	/* Should be run before the first non-init thread is created */
	init_espfix_bsp();
#endif
	thread_stack_cache_init();
	cred_init();
	fork_init();
	proc_caches_init();
	buffer_init();
	key_init();
	security_init();
	dbg_late_init();
	vfs_caches_init();
	pagecache_init();
	signals_init();
	proc_root_init();
	nsfs_init();
	cpuset_init();
	cgroup_init();
	taskstats_init_early();
	delayacct_init();

	check_bugs();

	acpi_subsystem_init();
	sfi_init_late();

	if (efi_enabled(EFI_RUNTIME_SERVICES)) {
		efi_late_init();
		efi_free_boot_services();
	}

	ftrace_init();

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

​	init进程是第一个用户空间的进程，init进程的入口是在Android源码的`system/core/init/main.cpp`。下面我们看看入口函数main

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

​	根据上一章的启动init的参数，可以判断第一次启动时，执行的是FirstStageMain函数，我们继续看看这个函数的实现

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

​	这里看到又拉起了一个init进程，并且传了参数selinux_setup，所以接下来我们直接看前面main入口函数中判断出现该参数时调用的SetupSelinux函数。

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

​	1、service		开启一个服务

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

​	到这里大致的init进程的启动流程相信大家已经有了一定了解。明白init的原理后，对于init.rc相信大家已经有了简单的印象，下一章我们将详细展开讲解init.rc文件。
