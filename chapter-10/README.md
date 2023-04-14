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

### 10.4.1 运行bcc工具

### 10.4.2 运行bpftrace工具

### 10.4.3 如何编译基于libbpf的eBPF程序


## 10.5 eBPF实现安卓系统进程跟踪



## 10.6 小结
