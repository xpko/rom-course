# 第三章 认识系统组件 #

## 3.1 源码结构介绍

​	在上一章的学习中，我们成功编译了Android12以及对应的内核，并且通过多种方式刷入手机。接下来我们需要先对Android源码的根结构有一定的了解，对结构有一定了解能帮助我们更快的定位和分析源码，同时能让开发人员更好的理解Android系统。

​	Android源码结构分为四个主要的模块：frameworks、packages、hardware、system。frameworks模块是Android系统的核心，包含了Android系统的核心类库、Java框架和服务，它是Android开发的基础。packages模块包括了Android系统的应用程序，主要是用户使用的应用程序，例如通讯录、日历和相机。hardware模块提供了对硬件设备的支持，例如触摸屏、摄像头等。最后，system模块包含了Linux内核和Android底层服务，它负责管理资源和处理系统事件。除了这些主要模块，Android源码中还有一些其他的文件夹，例如build、external、prebuilts和tools等，他们提供了编译系统所需的资源和工具。接下来我们对根目录进行一个简单的介绍。

​	1、art：该目录是Android 5.0中新增加的，主要是实现Android RunTime（ART）的目录，它作为Android 4.4中的Dalvik虚拟机的替代，主要处理Java字节码。

​	2、bionic：这是Android的C库，包含了很多标准的C库函数和头文件，还有一些Android特有的函数和头文件。 

​	3、bootable：该目录包含了引导程序，这些引导程序用于从系统启动，并初始化硬件， 例如Bootloader和Recovery程序。

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

​	下载两个驱动文件后，我们将文件放到源码根目录中解压，并且执行相应的sh脚本进行导出，到了这里我们了解到vendor中是硬件厂商提供的摄像头蓝牙之类的驱动程序。那么我们就可以观察到，脚本执行后，实际就是将驱动文件放到了对应目录中。
