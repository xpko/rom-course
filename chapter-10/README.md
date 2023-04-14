# 第十章 系统集成开发eBPF

安卓系统的安全攻防技术日新月异，现如今进入了一个全新的高度。随着eBPF技术的崛起，国内外安全人员人业也在积极发掘eBPF技术在安全领域的应用场景。

本章将为安卓系统开发与定制人员，提供一种代码修改与eBPF可观测性相结合的系统定制细路，旨在为安全行业的发展发挥一点抛砖引玉的作用。

## 10.1 eBPF概述

eBPF(extended Berkeley Packet Filter) 是一种现代化的Linux内核技术，它允许开发人员对网络数据包进行更细粒度的过滤和修改。与传统的Berkeley Packet Filter(BPF)相比，eBPF具有更灵活、可扩展性和安全性的优势，因此得到了广泛的应用和认可。在实际应用中，eBPF可以实现网络流量监控、日志记录、流量优化和安全审计等功能，因此具有广泛的应用前景。

### 10.1.1 eBPF发展背景

在2008年，Linux内核开发者提出了BPF(Berkeley Packet Filter)的概念，它是一种用于过滤和修改网络数据包的内核模块。BPF是一种非常强大的工具，它允许开发人员对网络数据包进行细粒度的过滤和修改，从而实现网络流量监控、日志记录、性能优化等功能。

然而，BPF也有一些限制。首先，BPF模块需要由内核开发人员手动编写和编译，因此对于非专业开发人员来说，编写BPF模块是一项具有挑战性的任务。其次，BPF模块的编写需要一定的技术知识和经验，否则可能会导致内核崩溃或其他问题。最后，BPF模块的访问权限非常高，意味着它们可以访问系统的所有内存和网络资源，因此需要严格的安全控制。

为了解决这些问题，Linux内核开发者在2014年引入了eBPF(extended Berkeley Packet Filter) 技术。eBPF是一种扩展的BPF，它提供了更多的功能和权限控制，同时降低了内核开发人员的编写难度和风险。与传统的BPF相比，eBPF具有更灵活、可扩展性和安全性的优势，因此得到了广泛的应用和认可。

eBPF发展之初是为了用于高效的网络数据包的过滤。在发展过程中，除了对传统的数据包过滤字节码格式进行扩展外，还支持更多类型的eBPF程序，它们可以在整个操作系统的不同模块中运行。最初提倡的可观测性领域也扩展为支持数据的观测与修改（包括用户态数据与内核函数返回值）。这样的发展路径，让eBPF技术看起来更像是一个现代化的Hook技术框架。这也是安全从业人员其对爱不释手的原因。

相信，随着内核版本的更新，其内置的eBPF功能支持也会越来越丰富。而作为eBPF的能力核心-eBPF内核方法接口也会越来越多，基于这些接口实现的安全功能势必会影响到整个行业的发展。

### 10.1.2 eBPF的工作原理

eBPF的工作原理可以概括为三个步骤：解析、执行和卸载。

1. 解析
在系统启动时，内核会将eBPF符号表(eBPF symbol table) 加载到内存中。eBPF符号表是一个二进制文件，它包含了eBPF模块的所有符号和参数。内核还会将eBPF模块的二进制代码转换为机器码，并将其加载到内存中。

2. 执行
当网络数据包到达时，内核会首先检查数据包是否被匹配到eBPF模块。如果数据包被匹配到，内核会执行eBPF模块中的代码，对网络数据包进行过滤或修改。在执行期间，内核会使用eBPF的运行时数据结构体(runtime data structure)来存储和传递参数和上下文信息。

3. 卸载
当eBPF模块执行完毕后，内核会将其卸载并从内存中清除。卸载时，内核会将所有符号和参数还原成二进制码，并将其从内存中清除。


### 10.1.3 eBPF的应用场景

eBPF是一种非常强大的技术，它可以实现许多网络流量监控、日志记录、性能优化等功能。下面列举了一些常见的eBPF应用场景:

1. 日志记录
eBPF可以用于记录网络流量、系统调用、错误事件等信息，从而实现全面的系统监控和日志记录。目前，这方面技术应用于云原生安全较多。如`sysdig`与`falco`这类安全监控工具，新版本就使用了eBPF来实现系统调用的监控。

2. 流量控制
eBPF 可以用于实现网络流量控制，例如限制同一主机的网络流量、限制同一端口的网络流量等。这个应用最多的就是防火墙，比如大名鼎鼎的`iptables`就有了基于eBPF的扩展版本。

3. 流量优化
eBPF可以用于优化网络流量，例如过滤重复数据包、压缩数据包、优化TCP/IP协议栈等。在网络应用上，典型的是可以使用eBPF开发透明代理工具、网络数据镜像转发工具、流量优化工具等。

4. 安全审计
eBPF可以用于实现安全审计功能，例如记录系统用户的操作、检查系统资源使用情况等。在这个应用领域，如主机安全类防护产品`HIDS`就有了发展的空间。安全工具`Tracee`就是属于这类应用。



## 10.2 eBPF相关的开发工具

eBPF是一种现代化的Linux内核技术，它允许开发者在内核中安全地运行外部程序，用于处理网络数据包、系统调用等场景。eBPF相比传统的内核模块有更高的安全性和可移植性，因此得到了越来越广泛的应用。eBPF虽然运行在内核，但是控制它的程序却是运行在用户态，下面将介绍一下它的开发方法。

在开发eBPF相关工具时，常用的有bcc、bpftrace和libbpf。下面将对这三个工具/库进行介绍。

### 10.2.1 bcc

`bcc`是一款开源的eBPF快速开发工具。最初使用python作为eBPF程序的开发语言，随着社区的发展，该工具支持了C语言开发eBPF程序。该项目是一个开源工具，它的仓库地址是：https://github.com/iovisor/bcc。该仓库提供了一组python语言编写的eBPF工具集，位于tools目录下，涉及的功能包含了文件、进程、网络、延时、性能观测等多个应用场景的工具;同时，也提供了一组C语言编写的eBPF工具集，位于libbpf-tools工具下，这下面的工具很多是tools的C语言实现版本，是非常好的eBPF入门学习资料。

该工具的项目README中有列出eBPF可以运行的不同系统位置的分布图。也提供了tools目录下工具用途的介绍。比如监控文件的打开操作，可以执行如下命令：

```
$ sudo python3 tools/opensnoop
```

### 10.2.2 bpftrace

`bpftrace`的主要用途是用于记录和追踪系统方法调用。eBPF程序可以用于处理网络数据包、系统调用、文件访问等场景。使用`bpftrace`，开发者可以可以快速验证要观测的函数是否支持eBPF来实现。

`bpftrace`是开源的工具，它的仓库地址是：https://github.com/iovisor/bpftrace。按照官方的说明，安装好该工具后，会提供一个`bpftrace`工具。这个主程序接受单选的命令与一个bt格式的脚本程序作为输入。脚本中可以设置观测程序的入口和出口、参数传递等信息，非常方便。需要注意的是，目前`bpftrace`只提供了观测功能，没有提供数据的修改功能。这点上不如`bcc`与`libbpf`。

执行下面的命令，可以观测所有的文件打开操作：

```
$ sudo bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm, str(args->filename)); }'
```


### 10.2.3 libbpf

libbpf是一个用于编写和运行eBPF程序的开源库。它的仓库地址是：https://github.com/libbpf/libbpf。 它提供了一组C接口的函数，允许开发者使用C/Rust语言编写和运行eBPF程序。libbpf官方还单独提供了一些使用libbpf开发eBPF程序的样例。仓库地址是：https://github.com/libbpf/libbpf-bootstrap。该仓库下的examples/c目录下的演示代码，整体的风格与bcc的libbpf-tools目录下类似，前者代码简洁，后者功能更丰富。

总的来说，`bcc`、`bpftrace`和`libbpf`都是用于开发eBPF相关工具的重要工具，它们提供了丰富的功能和工具，方便开发者进行eBPF程序的开发、调试和追踪。

## 10.3 安卓系统集成eBPF功能

eBPF的功能实现与完善，是优先对x86_64架构提供支持。arm64与其它的系统架构，则会在后面补充跟上。对于大部分的安卓手机设备来说，系统主流采用的是arm64架构的处理器，因此，它的各方面功能支持会延后支持，其支持的程度与arm64版本的Linux其他发行版本对齐，比如arm64架构同版本内核的Ubuntu系统，与安卓的eBPF功能支持基本是一致的。

### 10.3.1 不同版本内核对eBPF的影响

安卓系统的版本更新，通常也伴随着系统内核版本的升级。目前最新的安卓14采用6.1版本的内核。它的默认的内核配置支持与在同版本内核的arm64 Ubuntu系统eBPF功能一致。支持常用的`kprobes`、`uprobes`、`tracepoint`、`raw_tracepoint`。但一些arm64到高版本内核仍然不支持的特性，比如：`fentry`、`fmod_ret`、`kfuncs`、`LSM`、`SYSCALL`、`tp_btf`等，还需要等待主线内核提供更新支持。列出的不支持的部分，从内核如下地址：https://github.com/torvalds/linux/commit/efc9909fdce00a827a37609628223cd45bf95d0b，可以看到已经有了更新的支持，但Ubuntu arm64架构的6.1内核上，仍然测试失败，相信不久，这些功能都可以在arm64上运行良好。

安卓12内核采用5.10，安卓13采用5.10与5.15。这两个版本的Linux内核，支持上面说的`uprobes`、`tracepoint`、`raw_tracepoint`。但它们对`kprobes`的支持有一些欠缺，只能说部分支持。造成这个的原因是安卓GKI2.0的一些变化，让`CONFIG_DYNAMIC_FTRACE`这样的选项无法成功开启，具体会在下面一些需要注意的内核配置的小节进行说明。

### 10.3.2 一些需要注意的内核配置

与安卓eBPF相关的内核配置有如下：

1. `CONFIG_DYNAMIC_FTRACE`。如果内核配置了`CONFIG_DYNAMIC_FTRACE`, Ftrace框架内部的`mcount`会被实现成一个空函数（只有一条`ret`指令）。在系统启动时，`mcount`会被替换成`nop`指令。打开tracer后，所有函数的对应位置会被动态替换成跳转到`ftrace_caller()`的指令。这个选项是`fentry`的内核配置`CONFIG_FPROBE`的依赖，会导致fentry无法生效。

2. `CONFIG_FUNCTION_TRACER`。内核中打开`CONFIG_FUNCTION_TRACER`后，会增加`pg`编译选项，这样在每个函数入口处都会插入`bl mcount`跳转指令，函数运行时会进入`mcount`函数。`mcount`会判断函数指针`ftrace_trace_function`是否被注册，默认注册的是空函数`ftrace_stub`，这是ftrace静态方法跟踪的内核配置选项。这个选项也是`fentry`的内核配置`CONFIG_FPROBE`的依赖，会导致`fentry`无法生效。这个选项也会有一个`available_filter_functions`文件，供用户配置Ftrace，如果没有开启，会因为缺少了它，`bpftrace`在kprobes功能函数列表时，就会失败。

3. `CONFIG_FTRACE_SYSCALLS`。这是一个在几乎所有Ubuntu发行版本中都开启的内核配置，但是在安卓中却中默认关闭的。并且安卓官方的Pixel6以上设备开启后，配置Kprobe相关的选项开启，会让设备并得很卡。这个内核配置会在tracefs的events目录下，加入一个syscalls目录，支持对所有的系统调用进行单独的跟踪观测，是一个很有用的内核配置。

关于其它内核配置对eBPF的影响，可以查看bcc提供的一个内核配置说明文档。地址是：https://github.com/iovisor/bcc/blob/master/docs/kernel_config.md。


### 10.3.3 为低版本系统打上eBPF补丁

eBPF的强大功能很大一部分来源于其内核辅助方法。在这里不得不提两个功能强大的方法：`bpf_probe_read_user`与`bpf_probe_write_user`，这两个接口允许eBPF读取与写入内存地址指定的数据，它们拥有内核一样的能力，却有着比内核高得多的稳定性，功能不可谓不强大。

大多数eBPF程序都有观测函数方法的参数的需求，对于整形的参数，数据来源于其上下文的寄存器。直接读取其值便可以。涉及到字符串或结构体类型的数据，则需要使用`bpf_probe_read_user`方法来读取。如果该方法在内核中功能欠缺，则会让eBPF程序的整体功能无法实现。而这种事情却发生在了arm64架构5.5版本之前的内核中。由于arm64的功能更新滞后。`bpf_probe_read_user`接口在Linux主线内核5.5中才正式引入arm64的支持。具体的链接是：https://github.com/torvalds/linux/commit/358fdb456288d48874d44a064a82bfb0d9963fa0。这个补丁内容非常的多，修改的文件数量多达17个，包含bpf.h头文件导出接口申明，bpf/core.c添加接口实现逻辑，以及内存相关的接口的更新等，共计597处修改与197处删除。

在安卓11内核5.4上想要使用`bpf_probe_read_user`接口，需要对内核代码做一个向前移植操作（backport），其难度在可控的范围，只需要对照补丁中的代码，在5.4内核相应的地方做相应的添加与修改。更低版本如4.19与4.14的backport操作更麻烦一些，主要体现在主线内核大版本不同，接口的变化较大，版本5的内核在内存读写的多线程同步上，做了大量精细的工作，这些在内核4中是没有的，整个backport会变得更加困难。笔者本人尝试过了安卓10模拟器4.14与安卓11模拟器5.4内核的补丁，并且让它们可以正常的工作。

5.4内核补丁的网络上已经有多处的讨论，也有给出具体的解决方案。有发布针对安卓5.4内核的补丁代码的，也有提供完成补丁后内核代码分支的。当然，绝大多数的人员不关心补丁的内容详情，更在乎如何使用补丁后的产物。于是，后者更受人青睐。这里给出一个网络上修改好的方案链接：https://github.com/HorseLuke/aosp_android_common_kernels/tree/android-11-5.4-bpf_probe_read_user。

编译内核采用官方的build.sh脚本。执行下面的命令，下载内核代码。

```
mkdir -p android-kernel && pushd android-kernel
repo init -u https://android.googlesource.com/kernel/manifest -b common-android11-5.4
echo Syncing code.
repo sync -cj8
```

下载完成后，做一个内核代码替换，执行下面的命令：

```
rm -rf common
git clone https://github.com/feicong/aosp_android_common_kernels common
cd common
git checkout android-11-5.4-bpf_probe_read_user
```

最后，执行下面的命令编译生成内核。

```
BUILD_CONFIG=common-modules/virtual-device/build.config.goldfish.aarch64 SKIP_MRPROPER=1 CC=clang build/build.sh -j12
```

如果读者不关心内核与编译，可以到这里下载编译好的内核文件。https://github.com/feicong/ebpf-course/releases/tag/latest。比如，安卓模拟器5.4内核，其名字为android-arm64-common-5.4-kernelgz开头的zip文件，解压密码：qq121212。下载后，将其放到模拟器镜像目录下，替换kernel文件即可。


## 10.4 测试eBPF功能

安卓设备环境准备好后，需要`bcc`与`bpftrace`等工具来测试eBPF功能。

目前，这两个工具官方都没有提供安卓系统的编译与发布支持。使用第三方提供的工具替代。

## 10.4.1 为安卓编译bcc与bpftrace

这里使用的工具名叫ExtendedAndroidTools。它的下载仓库地址是：https://github.com/facebookexperimental/ExtendedAndroidTools。从名字上就可以看出，该仓库的目标是为安卓设备提供eBPF相关工具支持。

接官方的指导执行下面的命令编译生成二进制。

```
# Build the image
./scripts/build-docker-image.sh

# Run the environment
./scripts/run-docker-build-env.sh

# Build a target of your choice from within the container
make bpftools
```

编译好后，会生成`bcc`与`bpftrace`工具，还有一些`libbpf`相关的开发库。二进制工具可以执行python与bpftrace的脚本程序，而开发库则可以使用`libbpf`开发C语言的eBPF程序。

### 10.4.2 运行bcc工具

将生成好的bpftools推送到设备上。执行如下命令。

```
$ adb push bpftools /data/local/tmp/
```

执行`bcc`工具集需要管理员权限，执行如下命令获取root shell权限。

```
$ adb root
```

`bcc`工具集支持主流x86_64处理器的Linux系统。而对安卓系统的支持是有限的。主要的原因是常用的工具集使用的系统调用hook点，有可能在安卓系统上不存在。在执行命令过程中，如果出现错误，需要具体的问题具体分析，找出相应的解决方法。

打开一个adb shell，然后执行如下命令，开启文件打开监控。注意，所有的工具位于share/bcc/tools/目录下。

```
$ adb shell
# cd /data/local/tmp/bpftools
# ./python3 share/bcc/tools/opensnoop
```

如果不出意外，会有打开的文件列表输出。有一些工具会用到debugfs路径，在执行命令前需要执行如下命令，加载debugfs。

```
mount -t debugfs debugfs /sys/kernel/debug
```

有一些工具内容输出采用的Ftrace提供的tracing接口-bpf_trace_printk。这个时候，需要先打开Ftrace的日志输出开关。执行如下命令即可。

```
# echo 1 > /sys/kernel/tracing/tracing_on
```

后面，想要监控输出的内容，可以执行下面的命令。

```
# cat /sys/kernel/tracing/trace_pipe
```

### 10.4.3 运行bpftrace工具

`bpftrace`工具位于share/bpftrace/tools/目录下。执行方法与`bcc`一样。如尝试执行如下命令，监控命令执行操作。

```
$ adb shell
# cd /data/local/tmp/bpftools
# ./bpftrace share/bpftrace/tools/execsnoop.bt
share/bpftrace/tools/execsnoop.bt:21-23: ERROR: tracepoints not found: syscalls:sys_enter_exec*
```

从上面的输出可以看到，在内核没有开启`CONFIG_FTRACE_SYSCALLS`的情况下，是没有“tracepoint/syscalls”这个类别的，而execsnoop.bt使用这个跟踪点就会报错。解决这个问题有两种方法：

1. 将tracepoint更改为kprobe，然后调整参数名字与输出。

2. 为内核开启`CONFIG_FTRACE_SYSCALLS`，如果设备不支持开启，可以考虑更新开发板或模拟器环境。

执行如下命令可以监控设备的TCP网络连接。

```
# ./bpftrace share/bpftrace/tools/tcpconnect.bt
Attaching 2 probes...
Tracing tcp connections. Hit Ctrl-C to end.
TIME PID COMM SADDR SPORT DADDR DPORT
```

更多工具的使用与用法见`bpftrace`官方的说明文档。仓库地址是：https://github.com/iovisor/bpftrace/blob/master/docs/reference_guide.md。


## 10.5 eBPF实现安卓App动态库调用跟踪

本小节讲解如何使用eBPF开发一个完整的功能的跟踪工具。该工具名为`ndksnoop`。是笔者使用`bpftrace`实现的安卓NDK中常见的so动态库接口的跟踪工具。

整个工具分为三部分组成。头文件申明、BEGIN初始化块、Hook函数体。下面，分别进行讲解。

### 10.5.1 头文件的引用

新版本的`bpftrace`使用BTF来确定要处理的方法的参数类型、返回值与结构体类型。在没有开启支持BTF的环境中运行的话，或者Hook的第三方库没有BTF文件，只有头文件。这时，需要将使用到的类型信息通过头文件的方式引入到.bt脚本的开头。如下所示。

```
#!/usr/bin/env bpftrace
/*
 * ndksnoop	trace APK .so calls.
 *		For Android, uses bpftrace and eBPF.
 *
 * Also a basic example of bpftrace.
 *
 * USAGE: ndksnoop.bt
 *
 *
 * Copyright 2023 fei_cong@hotmail.com
 * Licensed under the Apache License, Version 2.0 (the "License")
 *
 * 09-Apr-2023	fei_cong created first version for libc.so tracing.
 */

#ifndef BPFTRACE_HAVE_BTF
#include <linux/socket.h>
#include <net/sock.h>
#else
#include <sys/socket.h>
#endif
```

最开始的部分，是.bt文件的用途与版本说明信息。说明脚本开发的目的、时间、作者、功能等。
然后，根据`BPFTRACE_HAVE_BTF`宏判断是否支持BTF来引入不同的头文件。这里引入的是与网络相头的socket结构体相头的申明，里面涉及到的Hook点，将在下在小节进行讲解。

在这里，除了使用`#include`引入头文件，还可以像C语言那样直接申明类型。如`typedef`、`#define`、`struct xxx{}`等。

### 10.5.2 传入参数的处理

有时候脚本需要使用传入参数来指定变化的参数信息。例如、`ndksnoop`需要支持对不同的安卓App进行过滤，这里使用到的过滤参数是App相关的`uid`。

安卓App在安装时，会被赋予一个不变的`uid`数值。可以对这个值进行过滤，来Hook指定的App。比如`com.android.settings`也就是设置应用，它的`uid`为1000，`shell`用户的`uid`为2000。想要查看一个App的`uid`。可以在adb shell下执行如下命令。

```
# ls -an /data/data/com.android.systemui
total 36
drwx------   4 10095 10095 4096 2023-02-03 17:47 .
drwxrwx--x 139 1000  1000  8192 2023-03-16 09:32 ..
drwxrws--x   2 10095 20095 4096 2023-02-03 17:47 cache
drwxrws--x   2 10095 20095 4096 2023-02-03 17:47 code_cache
```

`ls`命令的`-n`参数，会列出目录的`uid`信息。上面的命令列出的是systemui包的`uid`信息。对于的`cache`与`code_cache`目前行可以看出，第2列的`uid`值为10095。

`bpftrace`支持解析传入参数，以`$1`、`$2`、`$N`来命名。只传入一个`uid`，则执行如下命令传入的参数在脚本中`$1`的值为10095。

```
# ./bpftrace ndksnoop.bt 10095
```

`BEGIN`块是.bt脚本的初始化部分，可以用于对传入参数进行处理。如下所示。

```
BEGIN
{
    // # ls -an /data/data/io.github.vvb2060.mahoshojo
    if ($1 != 0) {
        @target_uid = (uint64)$1;
    } else {
        @target_uid = (uint64)10095;
    }

	printf("Tracing android ndk so functions for uid %d. Hit Ctrl-C to end.\n", @target_uid);
}
```

脚本的`$1`传给了@target_uid变量，前面的`@`表示这是一个全局变量，临时变量使用`$`。
当脚本没有传入参数时，`$1`的值为0，这个时候，可以给它一个默认的值10095，或者其它感兴趣的App的`uid`。

最后，使用`printf`方法打印输出一行调试信息。


### 10.5.3 Hook方法的实现

Hook用户态的程序与动态库，使用`uprobe`与`uretprobe`来实现。
`uprobe`负责处理方法执行前的上下文信息，`uretprobe`用于处理方法执行完返回时的返回值信息，通常一些输出的字符串与缓冲区信息也在这里进行处理。

以`libc.so`动态库的`mkdir`方法为例。它的Hook逻辑实现如下：

```
// int mkdir(const char *pathname, mode_t mode);
uprobe:/apex/com.android.runtime/lib64/bionic/libc.so:mkdir /uid == @target_uid/ {
    printf("mkdir [%s, mode:%d]\n", str(arg0), arg1);
}
```

`//`是注释，语法与C语言一样。主要是方便理解与阅读。

`uprobe`关键字指定进行`uprobe`类型的Hook。后面跟上库名或完整的库路径。在安卓系统上，`bpftrace`无法找到安卓apex目录下的动态库，因此，需要手动输入完整的路径。

`//`是过滤器，中间的内容`uid == @target_uid`为过滤表达式，表明，只有当表达满足时，才执行方法体内容。这里的表达式含义是：只Hook当前执行时`uid`为`@target_uid`的方法调用。`uid`关键字是`bpftrace` 的保留字，由`bpftrace`程序替换表示当前执行时的程序的`uid`。而`@target_uid`则上上面初始化部分设置好的目标`uid`，这样就完成了过滤操作。

`uprobe`的参数为`arg0`-`arg5`。取参数很简单，整形直接赋值就可以了！字符串类型使用`str()`来读取。字节数组使用`buf()`来读取。更多的方法参考`bpftrace`文档。

代码部分只有两行！就完成了一个方法的跟踪与参数值输出，实在是太方便了。

### 10.5.4 特殊参数与字段的处理

有一些参数，它们传入时没有传，只有在方法执行返回时才设置内容。对于这些方法，可以使用`uprobe`传入时保存指针，`uretprobe`执行时解析。如下所示，是`__system_property_get()`方法的Hook代码。

```
uprobe:/apex/com.android.runtime/lib64/bionic/libc.so:__system_property_get /uid == @target_uid/ {
    @name[tid] = str(arg0);
    @val[tid] = arg1;
}

uretprobe:/apex/com.android.runtime/lib64/bionic/libc.so:__system_property_get /uid == @target_uid/ {
    if (sizeof(@name[tid]) > 0) {
        printf("getprop [%s:0x%x:%s], ret:%d\n", @name[tid], (int32)(@val[tid]), str(@val[tid]), retval);
    }

    delete(@name[tid]);
    delete(@val[tid]);
}
```

`__system_property_get()`用于读取属性系统的值。传入的第一个参数为字符串类型的key，第二个参数为返回的内容。在`uprobe`中，使用`str()`读取了key的内容。而`arg1`存放的值，只保存了它的指针。在`uretprobe`中会对其进行`str()`内容读取。注意，最后需要调用`delete()`来删除这两个变量，因为它们是与`tid`相关的线程变量，执行后不删除，会让内存消耗越来越多，直到程序崩溃。

还有一类是比较复杂的结构体。比如`connect()`方法的第二个参数`struct sockaddr`，想要从这个参数中取得IP地址。可以使用如下方法。

```

// int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen);
uprobe:/apex/com.android.runtime/lib64/bionic/libc.so:connect /uid == @target_uid/ {
    $address = (struct sockaddr *)arg1;
    if ($address->sa_family == AF_INET) {
        $sa = (struct sockaddr_in *)$address;
        $port = $sa->sin_port;
        $addr = ntop($address->sa_family, $sa->sin_addr.s_addr);
        printf("connect [%s %d %d]\n", $addr, bswap($port), $address->sa_family);
    } else {
        $sa6 = (struct sockaddr_in6 *)$address;
        $port = $sa6->sin6_port;
        $addr6 = ntop($address->sa_family, $sa6->sin6_addr.s6_addr);
        printf("connect [%s %d %d]\n", $addr6, bswap($port), $address->sa_family);
    }
}
```

这是一种类C语言的语法，通过结构体指针强转的方式，来处理结构体中的字段信息。将字节数组的内容转换成IP地址，使用`ntop()`方法，而网络字节序的转换，使用`bswap()`方法。


### 10.5.5 效果展示

执行对`uid`为1000的`libc.so`方法调用跟踪。效果如下所示。

```
emulator64_arm64:/data/local/tmp/bpftools # ./bpftrace ./ndksnoop.bt 1000
WARNING: Cannot parse DWARF: libdw not available
Attaching 64 probes...
Tracing android ndk so functions for uid 1000. Hit Ctrl-C to end.
__system_property_find [net.qtaguid_enabled]
getenv [ANDROID_NO_USE_FWMARK_CLIENT]
getenv [ANDROID_NO_USE_FWMARK_CLIENT]
__system_property_find [persist.log.tag.android.hardware.vibrator-service.example]
__system_property_find [log.tag.android.hardware.vibrator-service.example]
__system_property_find [persist.log.tag]
__system_property_find [log.tag]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [persist.log.tag.AutofillManagerService]
__system_property_find [log.tag.AutofillManagerService]
__system_property_find [persist.log.tag.ActivityTaskManager]
__system_property_find [log.tag.ActivityTaskManager]
__system_property_find [debug.force_rtl]
__system_property_find [debug.force_rtl]
open [/proc/uid_procstat/set]
opendir [/proc/1041/task]
open [/proc/1041/timerslack_ns]
open [/proc/1048/timerslack_ns]
open [/proc/1050/timerslack_ns]
open [/proc/1054/timerslack_ns]
open [/proc/1056/timerslack_ns]
open [/proc/1057/timerslack_ns]
open [/proc/1058/timerslack_ns]
open [/proc/1059/timerslack_ns]
open [/proc/1060/timerslack_ns]
open [/proc/1061/timerslack_ns]
open [/proc/1063/timerslack_ns]
open [/proc/1064/timerslack_ns]
open [/proc/1066/timerslack_ns]
open [/proc/1078/timerslack_ns]
open [/proc/1079/timerslack_ns]
open [/proc/1107/timerslack_ns]
open [/proc/1225/timerslack_ns]
open [/proc/1241/timerslack_ns]
open [/proc/1282/timerslack_ns]
open [/proc/1341/timerslack_ns]
open [/proc/1361/timerslack_ns]
open [/proc/1372/timerslack_ns]
open [/proc/1374/timerslack_ns]
__system_property_find [debug.renderengine.capture_skia_ms]
open [/proc/1375/timerslack_ns]
open [/proc/1378/timerslack_ns]
open [/proc/1490/timerslack_ns]
open [/proc/1817/timerslack_ns]
open [/proc/2226/timerslack_ns]
open [/proc/2227/timerslack_ns]
open [/proc/2250/timerslack_ns]
open [/proc/2521/timerslack_ns]
open [/proc/6029/timerslack_ns]
opendir [/proc/889/task]
open [/proc/889/timerslack_ns]
open [/proc/902/timerslack_ns]
open [/proc/911/timerslack_ns]
open [/proc/913/timerslack_ns]
open [/proc/914/timerslack_ns]
open [/proc/915/timerslack_ns]
open [/proc/916/timerslack_ns]
open [/proc/917/timerslack_ns]
open [/proc/918/timerslack_ns]
open [/proc/932/timerslack_ns]
open [/proc/939/timerslack_ns]
open [/proc/940/timerslack_ns]
open [/proc/943/timerslack_ns]
open [/proc/972/timerslack_ns]
open [/proc/979/timerslack_ns]
open [/proc/981/timerslack_ns]
open [/proc/987/timerslack_ns]
open [/proc/989/timerslack_ns]
open [/proc/1012/timerslack_ns]
open [/proc/1013/timerslack_ns]
open [/proc/1014/timerslack_ns]
open [/proc/1015/timerslack_ns]
open [/proc/1016/timerslack_ns]
open [/proc/1017/timerslack_ns]
open [/proc/1018/timerslack_ns]
open [/proc/1019/timerslack_ns]
open [/proc/1027/timerslack_ns]
open [/proc/1029/timerslack_ns]
open [/proc/1030/timerslack_ns]
open [/proc/1069/timerslack_ns]
open [/proc/1076/timerslack_ns]
open [/proc/1080/timerslack_ns]
open [/proc/1088/timerslack_ns]
open [/proc/1089/timerslack_ns]
open [/proc/1100/timerslack_ns]
open [/proc/1165/timerslack_ns]
open [/proc/1166/timerslack_ns]
open [/proc/1249/timerslack_ns]
open [/proc/1291/timerslack_ns]
open [/proc/1403/timerslack_ns]
open [/proc/1404/timerslack_ns]
open [/proc/1406/timerslack_ns]
open [/proc/1478/timerslack_ns]
open [/proc/1671/timerslack_ns]
open [/proc/1675/timerslack_ns]
open [/proc/1764/timerslack_ns]
open [/proc/6238/timerslack_ns]
open [/proc/6256/timerslack_ns]
open [/proc/6258/timerslack_ns]
open [/proc/6260/timerslack_ns]
__system_property_find [persist.log.tag.AutofillManagerService]
__system_property_find [log.tag.AutofillManagerService]
__system_property_find [persist.log.tag.BpBinder]
__system_property_find [log.tag.BpBinder]
__system_property_find [persist.log.tag]
__system_property_find [log.tag]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [persist.log.tag.goldfish-address-space]
__system_property_find [log.tag.goldfish-address-space]
__system_property_find [persist.log.tag]
__system_property_find [log.tag]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
getenv [ART_APEX_DATA]
getenv [ANDROID_DATA]
getenv [ANDROID_DATA]
faccessat [/system_ext/priv-app/Launcher3QuickStep]
getenv [ART_APEX_DATA]
getenv [ART_APEX_DATA]
open [/system_ext/priv-app/Launcher3QuickStep/oat/arm64/Launcher3Quic]
open [/system_ext/priv-app/Launcher3QuickStep/oat/arm64/Launcher3Quic]
open [/system_ext/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk]
readlink [/proc/self/fd/426 /system_ext/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk 0]
readlink [/proc/self/fd/380 /system_ext/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk 0]
open [/system_ext/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk]
faccessat [/data/misc/iorapd/com.android.launcher3/31/com.android.launcher]
faccessat [/proc/1041/stat]
open [/proc/1041/stat]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
faccessat [/data/system_ce/0/snapshots]
faccessat [/data/system_ce/0/snapshots/135.proto.bak]
open [/data/system_ce/0/snapshots/135.proto.new]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
open [/data/system_ce/0/snapshots/135.jpg]
__system_property_find [debug.renderengine.capture_skia_ms]
open [/data/system_ce/0/snapshots/135_reduced.jpg]
__system_property_find [debug.renderengine.capture_skia_ms]
__system_property_find [debug.renderengine.capture_skia_ms]
^C

@target_uid: 1000

emulator64_arm64:/data/local/tmp/bpftools #
```

目前，Hook监控了`libc.so`共计64个接口方法。后面，可以扩展`ndksnoop`，实现对其它方法与其它库的方法跟踪。这种方式Hook最大的好处是输出内容中，没有多余的信息，所有的输出都是目标进程的行为捕获。缺点也是有的，那就是无法捕获直接使用系统调用方式执行的方法。

## 10.6 小结

本节主要介绍了eBPF相关的一些信息，以及如何在安卓系统上配置好eBPF开发与运行环境。最后，通过`ndksnoop`工具的代码，讲解了如何对安卓系统动态库调用进行跟踪分析。

任何工具与技术方案都有它的优势与短板，在学习系统定制与软件安全的过程中，应该根据实现情况，结合不同的方案，扬长避短，达到最终的目标。
