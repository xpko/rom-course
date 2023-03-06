# 第二章 系统开发环境与工具 #

## 2.1 重新看待系统定制

​	经过第一章的学习，对AOSP定制进行简略的介绍后，相信此时，系统定制开发这个领域，在读者的心中会有大致的了解。简单来说，所谓的系统定制，相当于在一款成熟的产品上进行二次开发。和常见的软件项目的二次开发的学习步骤类似，不会有太大的出入，细节的区别就在于，Android源码相比其他软件项目要更加庞大复杂，修改编译以及测试系统所花费的时间周期更长。

​	尽管Android源码结构非常庞大，但对于初学者，并不需要完整的吃透所有代码。重点的是，掌握系统代码分析的思路，阅读理解工程的整体结构，了解Android系统框架的运行原理，结合思考与实践，达到自定义定制的目标。

​	学习的流程需要循序渐进，有的放矢，以免迷失在纷繁复杂的代码海洋中。通常，第一步需要了解如何将整个系统项目成功编译并刷机。这一章将详细讲解在各种不同的环境下，我们应该如何编译Android源码，并将其刷入手机中。

## 2.2 环境准备

安卓系统在版本10之前，是支持macOS系统上编译AOSP代码的。在新版本系统的演进过程中，安卓官方已经放弃在macOS系统平台上做AOSP开发的支持，官方开发指导环境采用了Linux上比较流行的Ubuntu发行版本。

在实际的开发过程中，可以使用Windows系统下的WSL2或Docker来构建一个Ubuntu系统运行环境，同样可以完成AOSP编译与开发工作。

这一节将会介绍在Windows系统与Linux系统上，如何完成环境准备工作。

### 2.2.1 Windows

​	由于在Windows中缺少了各种底层编译器与开发库的支持，一般情况下，开发人员不会直接在Windows环境中编译，而是选择在Windows中创建一个Linux的虚拟环境，然后在虚拟环境中安装编译所需要用到的底层依赖。在Windows系统上部署Ubuntu虚拟环境有多种可选方案，例如Docker、WSL（Windows Subsystem for Linux）、Vmware虚拟机，QEMU、HyperV虚拟机平台等等。

​	几种方案经过编译对比测试，发现Docker在Windows系统上的体验并不怎么好，主要体现在编译这类大型项目时，需要较大的磁盘存储空间，选择外挂磁盘映射时，编译时IO性能较弱，而选择创建虚拟磁盘时，对宿主机的开机耗时明显变高。这里不太建议在Windows下采用Docker来编译源码。

​	WSL是Windows下内置的Linux子系统，最新的版本号为2，通常将其称为WSL2。它是一个非常轻量化的Linux系统，让那些想在Windows中编译与运行Linux程序的开发人员爱不释手。安装好WSL2后，只要在终端中输入一个`wsl`命令就可以启动环境。使用起来的感觉就好似直接使用命令行一样。并且编译性能相比`Vmware`这类虚拟机要更加高效。在我的笔记本环境中，WSL2完整编译的耗时为130分钟，而`Vmware`虚拟机的耗时是170分钟，这是因为WSL2采用直通计算机硬件，IO性能有着较为显著的提升。

​	如果你的系统上Windows10，那么你需要先查询当前系统版本，必须是18917或更高的版本才支持WSL2。在cmd命令行中输入`winver`命令查看当前系统版本号。

![image-20230102183339463](.\images\image-20230102183339463.png)

​	由于是系统自带的，所以安装起来非常方便，可以直接在控制面版->程序->启动或关闭Window功能中开启支持即可，如下图

![img](.\images\69ba546fd55c4fea8ef9b5d55a9bd354.png)

​	或者是采用命令的方式开启虚拟机平台和Linux子系统，使用管理员权限启动` `。

![image-20230102183708998](.\images\image-20230102183708998.png)

​	执行下面的命令开启功能

```
//启用虚拟机平台
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
//启用Linux子系统
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
```

​	启动完成这些特性后，重新启动计算机，然后我们就可以开始安装一个`Ubuntu`系统了。打开Microsoft Store应用商店搜索`Ubuntu`系统，然后选择自己需要的版本即可，例如我安装的是22.04版本，如下图。

![image-20230102184626538](.\images\image-20230102184626538.png)

​	成功获取`Ubuntu`系统后，从应用中启动系统即开始正式安装。安装过程只需要设置好用户名与密码即可。完成后会进行一个shell环境供用户输入。
​	需要注意的是，应用商店默认会将WSL安装在C盘中，而我们编译系统会占用相当大的空间，如果你的系统盘空间不够，需要做一个迁移操作，将子系统迁移到其他硬盘中。操作方法是：桌面任意位置右键选择终端，在打开的终端环境中自毁长城下面的命令，查询当前的子系统名称。

```
wsl -l -v

  NAME        STATE           VERSION
* ubuntu22    Running         2
```

然后，执行`wsl --export`命令，将子系统导出到其它较大空间的分区中；接着，执行`wsl --unregister`将其注销，最后，执行`wsl --import `再重新导入放在其他分区或磁盘上的子系统。如下所示。

```
//导出子系统
wsl --export ubuntu22 E:\wsl2\ubuntu22.tar
//注销之前的虚拟机
wsl --unregister ubuntu22
//重新导入虚拟机,并且指定新的虚拟机存放位置
wsl --import ubuntu22 E:\wsl2\ubuntu22_wsl E:\wsl2\ubuntu22.tar
```

​	现在，再次执行`wsl`命令，即可进入子系统的shell环境。

​	使用WSL2主要是在于轻量级和更优的高性能，一般都是命令模式的Linux，图形界面的程序可以通过安装一些依赖来解决，但这不是WSL2的强项。使用WSL2搭建开发环境时，使用远程开发模式不失为一种优雅的技术方案，典型的有使用`vscode`配合wsl插件，可以快速的远程访问WSL2环境上的代码与程序，另外，WSL2安装ssh服务后，`vscode`配合使用remote ssh插件也可以进行开发环境的搭建。

​	如果需要完整的Linux系统环境，使用`VMware`虚拟机会更加的合适。步骤也非常简单，流程如下。

​	1、下载并安装`VMware`虚拟机，然后下载Ubuntu22.04系统ISO镜像文件。

​	2、VWware创建虚拟机，选择指定镜像

![image-20230102194041709](.\images\image-20230102194041709.png)

3、设置初始账号密码

![image-20230102194243774](.\images\image-20230102194243774.png)

4、选择虚拟机保存位置，这里不要保存在C盘，记得磁盘要有至少300G的空间

![image-20230102194331141](.\images\image-20230102194331141.png)

5、虚拟硬件CPU核心根据你的电脑配置进行调整，尽量多分点给虚拟机。

![image-20230102194543812](.\images\image-20230102194543812.png)

6、虚拟内存分配，至少保证16G以上的内存，否则可能会碰到内存不足编译失败的情况。

![image-20230102194722427](.\images\image-20230102194722427.png)

7、虚拟硬盘分配，这里至少分配500G的空间，考虑到性能，我选择的是单文件吗，这里如果选择立即分配所有磁盘空间，能提高一定的性能。如果你的电脑配置不是很高，建议你选择立即分配。

![image-20230102194952517](.\images\image-20230102194952517.png)

​	虚拟机开机后，将默认进入Ubuntu安装界面，按照提示进行选择语言，区域等待安装完成即可。

### 2.2.2 Linux

​	Linux系统的选择非常多，本书中选择最新的Ubuntu 22.04 LTS稳定版。这里假定读者已经在自己的硬件上安装好了系统环境（安装方法与Vmware安装系统的操作流程类似）。

首先，安装必备的开发工具。

1、Android Studio下载并安装，下载地址：`https://developer.android.google.cn/studio/`

2、Clion下载并安装，下载地址：`https://www.jetbrains.com/zh-cn/clion/`

3、vscode下载并安装，下载地址：`https://code.visualstudio.com/`

​	然后，执行下面的命令配置好`python`与`pip`。

```
// 更新软件列表
sudo apt update -y && sudo apt upgrade -y

// 安装python和apt-utils
sudo apt-get install -y apt-utils python3 python3-pip python2

// 安装pip
pip install -U pip

// 设置pip使用国内源
python -m pip install --upgrade pip
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install pytest

```

到这里，Ubuntu系统上的AOSP编译开发环境就补步准备好了。


### 2.3 如何选择源码版本

​	在开始拉取代码前，首选需要了解自己需要编译的AOSP分支版本，可以参考官网对版本的说明链接。https://source.android.com/docs/setup/about/build-numbers?hl=zh-cn

​	然后根据需求，比如想要在Android10的基础上进行二次开发，那么就找到对应的版本描述，根据下图，可以看到各个版本号关联的代码分支，Android版本，支持哪些设备。

![image-20230103220519836](.\images\image-20230103220519836.png)

​	这么多版本，需要选一个最适合的版本，选择策略如下:

1、优先选择与你的测试机兼容的版本。

2、除了支持你的这个设备外，还支持更多设备的版本。

3、满足上面两个条件的最高分支版本，即优先最新的代码分支。

如果选择使用虚拟机，那么选择支持版本最多的分支即可。这里我的测试设备是pixel 3，所以选择了版本`SP1A.210812.016.A1`,对应的分支代码是`android-12.0.0_r3`，如下图。

![image-20230103220838404](.\images\image-20230103220838404.png)

### 2.3.1 编译

​	上面知道了需要的目标分支，接下来的步骤是拉取代码。

​	AOSP官方使用`repo`管理项目。`repo`是一个以`git`为基础包装的代码版本管理工具，内部是由`python`脚本构成的，对`git`命令进行包装，方便管理大型的项目。下面开始拉取代码。

```
// 安装git
sudo apt-get install git

//设置git身份
git config --global user.email "xxxx@qq.com"
git config --global user.name "xxxx"

// 安装curl
sudo apt-get install curl

// 创建bin目录，并加入PATH
mkdir ~/bin
PATH=~/bin:$PATH

// 下载repo，并设置权限
curl https://mirrors.tuna.tsinghua.edu.cn/git/git-repo > ~/bin/repo
chmod a+x ~/bin/repo

// 设置使用国内源拉取代码
export REPO_URL='https://mirrors.tuna.tsinghua.edu.cn/git/git-repo/'

// 创建源码存放的目录
mkdir aosp_12 && cd aosp_12

// 初始化仓库
repo init -u https://aosp.tuna.tsinghua.edu.cn/platform/manifest

// 指定分支版本
repo init -u https://aosp.tuna.tsinghua.edu.cn/platform/manifest -b android-12.0.0_r3

// 同步代码
repo sync -c -j8
```

​	同步代码使用`repo sync -c -j8`的命令，其中，`-c`表示只同步当前分支代码，可以提高同步速度，而`-j`是设置同步使用的线程数，这里我使用了8个线程，并不是线程越多速度越快，而是根据cpu的核心数，使用最合理的线程数才能达到最佳的并发效果。

```
// 查看可用cpu数量，我的环境显示为16
nproc --all

// 直接使用最佳线程数
repo sync -c -j16

//也可以直接省略成一句
repo sync -c -j$(nproc --all)
```

​	代码同步完成后，会提示`Success`，如果失败了，就重新拉取即可，多拉取几次后，基本都能同步成功。接下来，开始安装编译的底层依赖。

```
// AOSP编译的相关依赖安装
sudo apt-get install -y git-core gnupg flex bison build-essential \
	zip curl zlib1g-dev gcc-multilib g++-multilib libc6-dev-i386 lib32ncurses5-dev \
	x11proto-core-dev libx11-dev lib32z1-dev libgl1-mesa-dev libxml2-utils xsltproc unzip \
	fontconfig libncurses5 procps rsync libsqlite3-0
```

​	注意：编译AOSP需要大量的磁盘空间，通常300G的空间足够存放代码与编译输出的结果。如果你希望将输出的结果存放在其它目录。这一点通过设置`OUT_DIR`环境变量来调整编译结果的输出目录。如下所示，

```
vim ./build/envsetup.sh
// 在底部加上环境变量设置为和源码同一级的目录，我当前源码路径为~/android_src/aosp12
export OUT_DIR=~/android_src/aosp12_out
```

​	在开始编译前，还需要准备对应设备的驱动，根据前面选择的版本号`SP1A.210812.016.A1`,在官网地址：`https://developers.google.com/android/drivers`中找到对应的版本号，并且可以看到`Pixel 3`的手机对应的代号是`blueline`。

![image-20230103232052738](.\images\image-20230103232052738.png)

​	第一个文件`Vendor`是用来存储厂商特定的文件，比如设备驱动程序。Android驱动会根据提供的这些设备驱动来正确的加载硬件。这个文件通常由设备厂商提供。如果你成功编译Android后，输出目录缺少vendor.img文件，那么你就需要检查下是否忘记导入对应型号的设备驱动了。

​	第二个文件是高通提供的相关设备驱动程序，比如GPS，摄像头，传感器等设备的闭源二进制文件。

​	点击`Link`下载，然后将下载的文件拷贝到Android源码根目录下。然后解压，并导出相关驱动文件。

```
// 解压驱动文件
tar -xvf qcom-blueline-sp1a.210812.016.a1-33e668b9.tgz
tar -xvf google_devices-blueline-sp1a.210812.016.a1-d10754e0.tgz

// 解压会得到两个文件extract-google_devices-blueline.sh和extract-qcom-blueline.sh
// 依次运行两个文件，运行后会提示许可说明，按回车键，然后按q跳过，最后手动输入I ACCEPT后回车即可
./extract-google_devices-blueline.sh
./extract-qcom-blueline.sh
```

​	导入设备驱动完成后，准备工作基本完成，可以开始编译源码了。

```
// 初始化构建环境参数
source ./build/envsetup.sh

// 选择编译的版本
lunch

//下面是我这边显示的结果
Lunch menu... pick a combo:
     1. aosp_arm-eng
     2. aosp_arm64-eng
     3. aosp_barbet-userdebug
     4. aosp_blueline-userdebug
     5. aosp_blueline_car-userdebug
     6. aosp_bonito-userdebug
     7. aosp_bonito_car-userdebug
     8. aosp_bramble-userdebug
     9. aosp_bramble_car-userdebug
Which would you like? [aosp_arm-eng]

// 选择版本可以填写直接填写aosp_blueline-userdebug或者是填写编号4
// 同样我们可以省略成一句，直接lunch 4或者是lunch aosp_blueline-userdebug
4

// 和上面一样。直接使用当前cpu的核心数作为编译的并发线程
make -j$(nproc --all)
```

​	在上面选择版本中，可以看到`aosp_arm-eng`和`aosp_arm64-eng`的选项，这两个是模拟器使用的版本。而模拟器使用的版本是可以不需要导入设备驱动文件的。如果在`lunch`的菜单中没有看到你要编译的版本，并且直接`lunch aosp_blueline-userdebug `也提示错误，可能是没有成功导入驱动文件，或者下载的驱动文件错误。

​	同一个代号的编译有三种编译版本选择。分别如下：

1、`aosp_blueline-user` 为用户版本，一般是默认的编译版本。主要用于发布版本，这种版本编译的环境会默认开启大多数的安全机制，比如`ro.secure`值为1，`ro.debuggable`值为0，，需要自行用第三方工具获取root权限。厂商设备出厂时，设备通常会编译为user版本。

2、`aosp_blueline-userdebug` 为用户调试版本，通常用于测试和调试Android系统，会启动一些调试工具，例如默认开启`adb`调试，`ro.debuggable`值为1，系统自带root权限等。

3、`aosp_blueline-eng` 为工程版本，同样也是用于测试和调试的环境，但是系统限制比`userdebug`要更加少，会禁用一些安全机制，比如签名验证，关闭一些编译优化等。

​	第一次完整编译非常的漫长，笔者的电脑耗时约2个小时成功编译。编译成功后，检查一下输出的文件。

```
// 查看输出目录的所有镜像文件
ls /root/android_src/aosp12_out/target/product/blueline | grep img

// 输出结果如下
boot-debug.img
boot.img
bootloader.img
boot-test-harness.img
dtb.img
dtbo.img
persist.img
radio.img
ramdisk-debug.img
ramdisk.img
ramdisk-recovery.img
ramdisk-test-harness.img
super_empty.img
system_ext.img
system.img
system_other.img
userdata.img
vbmeta.img
vendor.img
```

​	确定有编译出`vendor.img、system.img、boot.img`等镜像文件，就说明编译成功了。

### 2.4 模块编译

​	前文在编译的过程中介绍到，使用`source ./build/envsetup.sh`初始化环境的时候，导入了多个命令来辅助编译。接下来，先看看有哪些常用的命令。

通过命令`hmm`查看提供的命令帮助。

```
hmm

Run "m help" for help with the build system itself.

Invoke ". build/envsetup.sh" from your shell to add the following functions to your environment:
- lunch:      lunch <product_name>-<build_variant>
              Selects <product_name> as the product to build, and <build_variant> as the variant to
              build, and stores those selections in the environment to be read by subsequent
              invocations of 'm' etc.
- tapas:      tapas [<App1> <App2> ...] [arm|x86|arm64|x86_64] [eng|userdebug|user]
              Sets up the build environment for building unbundled apps (APKs).
- banchan:    banchan <module1> [<module2> ...] [arm|x86|arm64|x86_64] [eng|userdebug|user]
              Sets up the build environment for building unbundled modules (APEXes).
- croot:      Changes directory to the top of the tree, or a subdirectory thereof.
- m:          Makes from the top of the tree.
- mm:         Builds and installs all of the modules in the current directory, and their
              dependencies.
- mmm:        Builds and installs all of the modules in the supplied directories, and their
              dependencies.
              To limit the modules being built use the syntax: mmm
// 省略
......
```

​	`croot` 命令可以跳转根目录，或者是根目录下的任意子目录

​	`m` 命令会直接在根目录运行编译，即使当前目录是在子目录也是相当于在根目录编译。也可以指定名称来编译单独的目标，例如`m droid`。

​	`mm ` 编译当前目录中的所有模块及依赖项

​	`mmm` 编译指定目录中的所有模块及依赖项

​	`clean` 清除编译的结果，相当于删掉out目录中的内容

​	可以通过`m help`查看可以单独编译哪些选项

```
m help

Common goals are:

    clean                   (aka clobber) equivalent to rm -rf out/
    checkbuild              Build every module defined in the source tree
    droid                   Default target
    nothing                 Do not build anything, just parse and validate the build structure

    java                    Build all the java code in the source tree
    native                  Build all the native code in the source tree

    host                    Build all the host code (not to be run on a device) in the source tree
    target                  Build all the target code (to be run on the device) in the source tree

    (java|native)-(host|target)
    (host|target)-(java|native)
                            Build the intersection of the two given arguments

    snod                    Quickly rebuild the system image from built packages
                            Stands for "System, NO Dependencies"
    vnod                    Quickly rebuild the vendor image from built packages
                            Stands for "Vendor, NO Dependencies"
    pnod                    Quickly rebuild the product image from built packages
                            Stands for "Product, NO Dependencies"
    senod                   Quickly rebuild the system_ext image from built packages
                            Stands for "SystemExt, NO Dependencies"
    onod                    Quickly rebuild the odm image from built packages
                            Stands for "Odm, NO Dependencies"
    vdnod                   Quickly rebuild the vendor_dlkm image from built packages
                            Stands for "VendorDlkm, NO Dependencies"
    odnod                   Quickly rebuild the odm_dlkm image from built packages
                            Stands for "OdmDlkm, NO Dependencies"
```

​	通过帮助命令的提示，可以看到`m snod`就是单独编译`system`模块,命令`m vnod`就是单独编译`Vendor`。大多数时候，修改的内容都是在`system`模块中。可以根据自己对系统的修改情况，执行不同的模块编译。

### 2.5 内核编译

​	在前面我们编译完成后，可以在编译的镜像结果中看到文件`boot.img`，这个文件就是内核镜像文件。但是这个内核是Android源码树中已经编译好的内核文件，并不是我们编译出来的，如果我们想要修改内核，就需要拉取内核的对应分支，编译内核，将编译结果放入Android源码中的指定路径，然后再重新编译Android。刷入手机后，使用的内核就是我们自己编译的了。

​	首先第一步是找到对应我们当前手机的内核分支，官网提供了详细的说明https://source.android.com/docs/setup/build/building-kernels。根据下图可以看到，对应`Pixel 3`测试机分支是`android-msm-crosshatch-4.9-android12`。

![image-20230105221730348](.\images\image-20230105221730348.png)

​	接下来我们按照官网的说明拉取代码并编译。

```
// 内核编译的相关依赖安装
sudo apt install p7zip-full wget curl git tree -y
sudo apt-get install dialog file python3 python3-pip python2 libelf-dev gpg gpg-agent tree flex bison libssl-dev zip unzip curl wget tree build-essential bc software-properties-common libstdc++6 libpulse0 libglu1-mesa locales lcov --no-install-recommends -y
sudo apt-get install pahole libreadline-dev -y

// 创建内核的源码目录，不用放再Android源码目录下
mkdir android-kernel && cd android-kernel

// 初始化指定分支
repo init -u https://android.googlesource.com/kernel/manifest -b android-msm-crosshatch-4.9-android12

// 同步分支代码
repo sync -j$(nproc --all)

// 编译内核
build/build.sh

// 编译完成后，查看编译结果，最后输出显示Image.lz4文件就表示内核编译是成功的。
ls /root/android_src/android-kernel/out/android-msm-pixel-4.9/dist |grep Image
```

​	编译成功后，我们还需要指定Android源码编译时使用这个内核文件。只需要设置环境变量指定路径即可。方式如下。

```
// 为了以后方便，环境路径相关的，我们都写在这个初始化导入环境命令的地方
vim ./build/envsetup.sh

// 在最底部添加
export TARGET_PREBUILT_KERNEL=/root/android_src/android-kernel/out/android-msm-pixel-4.9/dist/Image.lz4

// 保存配置后，重新加载一下
source ./build/envsetup.sh

// 选择编译版本
lunch aosp_blueline-userdebug

// 单独编译内核镜像
make bootimage
```

### 2.6 刷机

​	大多数情况下，非技术的Android爱好者通常会使用傻瓜式一键刷机工具，例如刷机大师、刷机精灵、奇兔等等。这种刷机方式就是属于软刷（软件刷机），除此之外还有我们第一章中简单介绍到的线刷和卡刷。不论刷机的方式是什么，他们最终的原理都是相同的，都是对刷机包进行处理，然后将ROM文件写入对应的分区，替换掉原始文件。下面我们将简单介绍如何进行线刷和卡刷。

### 2.6.1 线刷

​	通过上面编译中的步骤，在目录`aosp12_out/target/product/blueline/`中能看到若干个后缀为`img`的镜像文件。我的输出路径`aosp12_out`是由于我手动指定了输出目录，如果你没有设置，那么默认是在`aosp12/out/target/product/blueline/`目录下。最后的目录`blueline`是对应编译的版本，如果你是其他版本，就在对应的目录下查看。

​	首先我们要进入刷机模式，然后环境变量设置编译结果的路径，然后使用命令完整刷机即可。详细流程如下

```
// 进入刷机模式
adb reboot bootloader

// 设置刷机包的路径到环境变量
export ANDROID_PRODUCT_OUT=/home/king/android_src/mikrom_out/target/product/blueline

// 查询fastboot是否能成功看到设备
fastboot devices

// 上面的查看命令显示的结果
8ARX0Y7EP	fastboot

// 完整刷机
fastboot flashall -w
```

​	等待刷机结束即可，刷机结束后会自动进入Android系统。如果我们只想刷单个分区镜像，也是可以的。流程如下

```
// 进入刷机模式
adb reboot bootloader

// 进入编译结果的目录
cd /home/king/android_src/mikrom_out/target/product/blueline

// 单独刷入内核
fastboot flash boot ./boot.img

// 单独刷入系统
fastboot flash system ./system.img

// 部分机型可能会出现如下错误提示
fastboot: error: The partition you are trying to flash is dynamic, and should be flashed via fastbootd. Please run:

    fastboot reboot fastboot

And try again. If you are intentionally trying to overwrite a fixed partition, use --force.

// 这种情况我们按照他的提示操作即可，执行下面的命令后，发现进入了fastbootd模式
fastboot reboot fastboot

// 重新刷入系统
fastboot flash system ./system.img

// 刷入共享系统
fastboot flash system_ext ./system_ext.img

// 刷入硬件驱动
fastboot flash vendor ./vendor.img

// 重启
fastboot reboot
```

### 2.6.2 卡刷

​	我们前面编译出来的是线刷包，如果我们需要卡刷包，就需要使用下面的方式进行编译

```
// 下面是简单的编译卡刷包
cd aosp12
source ./build/envsetup.sh
lunch aosp_blueline-userdebug
make otapackage
```

​	编译完成后，我们可以在前面线刷包的路径下看到卡刷包文件，我这里的文件名是`aosp_blueline-ota-eng.king.zip`。除了上面的方式，我们还可以完整编译卡刷包，编译方式如下

```
//下面是完整编译卡刷包
cd aosp12
source ./build/envsetup.sh
lunch aosp_blueline-userdebug
mkdir dist_output
make dist DIST_DIR=dist_output
```

​	编译完成后，可以在目录`dist_output`中看到完整卡刷包结果。

​	接下来是如何刷入卡刷包，有两种刷入方式，一种是使用`adb sideload`命令刷入，另一种方式是使用twrp刷入。下面演示两种不同方式的刷机流程。

​	1、adb sideload（TODO这里没写完，你补充一下，我这边环境没跑通）

​		首先进入fastbootd

```
adb reboot bootloader
fastboot reboot fastboot
```

​		这时的界面如下图，使用音量键减，切换到`Enter recovery`，然后按电源键进入`recovery`模式

![image-20230108190236615](.\images\image-20230108190236615.png)

​		接下来进入下面的界面，选择`Apply update from ADB`

![image-20230108190631803](.\images\image-20230108190631803.png)



​	2、twrp（TODO这里没写完，你补充一下，我这边环境没跑通）

### 2.8 源码的开发环境搭建

​	Android系统是一个非常庞大的项目，所以我们需要采用合适的编辑器或者是`ide`来修改代码，如果你的改动不多，那么我们简单的使用`VsCode`导入工作区即可开始修改代码。但是`VsCode`的智能提示和跳转较为简陋，所以如果想要更加友好的开发体验，我们可以选择将源码导入`Android Studio`中编辑java部分代码，导入`Clion`中编辑`native`部分代码。下面简单介绍如何将源码导入Android Studio。

```
cd ~/aosp12
source build/envsetup.sh
lunch aosp_blueline-userdebug

// 编译生成idegen.jar
make idegen

// 在源码根目录生成android.ipr和android.iml
development/tools/idegen/idegen.sh

// 编辑iml文件，找到excludeFolder的属性位置，新增排除掉一些基本不怎么修改或者是native代码相关的部分
vim ./android.iml

// 例如新增下面这些部分
<excludeFolder url="file://$MODULE_DIR$/abi"/>
<excludeFolder url="file://$MODULE_DIR$/art"/>
<excludeFolder url="file://$MODULE_DIR$/bionic"/>
<excludeFolder url="file://$MODULE_DIR$/bootable"/>
<excludeFolder url="file://$MODULE_DIR$/build"/>
<excludeFolder url="file://$MODULE_DIR$/cts"/>
<excludeFolder url="file://$MODULE_DIR$/dalvik"/>
<excludeFolder url="file://$MODULE_DIR$/developers"/>
<excludeFolder url="file://$MODULE_DIR$/development"/>
<excludeFolder url="file://$MODULE_DIR$/device"/>
<excludeFolder url="file://$MODULE_DIR$/docs"/>
<excludeFolder url="file://$MODULE_DIR$/external"/>
<excludeFolder url="file://$MODULE_DIR$/hardware"/>
<excludeFolder url="file://$MODULE_DIR$/libcore"/>
<excludeFolder url="file://$MODULE_DIR$/libnativehelper"/>
<excludeFolder url="file://$MODULE_DIR$/ndk"/>
<excludeFolder url="file://$MODULE_DIR$/out"/>
<excludeFolder url="file://$MODULE_DIR$/pdk"/>
<excludeFolder url="file://$MODULE_DIR$/prebuilts"/>
<excludeFolder url="file://$MODULE_DIR$/sdk"/>
<excludeFolder url="file://$MODULE_DIR$/system"/>
<excludeFolder url="file://$MODULE_DIR$/tools"/>
<excludeFolder url="file://$MODULE_DIR$/kernel"/>
```

​	修改好配置后，最后使用Android studio打开`android.ipr`文件即可。接下来简单介绍将代码导入Clion。

```
// 设置环境变量,在编译时生成CMakeLists.txt文件
export SOONG_GEN_CMAKEFILES=1
export SOONG_GEN_CMAKEFILES_DEBUG=1

// 正常编译一次
cd ~/aosp12
source build/envsetup.sh
lunch aosp_blueline-userdebug
make -j$(nproc --all)

// 查看clion目录下面生成了大量的CMakeLists.txt
tree out/development/ide/clion/

// 在clion目录下创建一个CMakeLists.txt来合并导入我们需要使用的各个模块
touch out/development/ide/clion/CMakeLists.txt

// 配置CMakeLists.txt导入模块
vim out/development/ide/clion/CMakeLists.txt

// CMakeLists.txt文件添加下面的内容，单独导入一个先
cmake_minimum_required(VERSION 3.6)
project(AOSP-Native)
// 添加子模块，导入了部分工程
add_subdirectory(frameworks/native)
add_subdirectory(art/dalvikvm/dalvikvm-arm64-android)
add_subdirectory(art/libdexfile/libdexfile-arm64-android)
add_subdirectory(art/runtime/libart-arm64-android)
add_subdirectory(bionic/libc/libc_bionic-arm64-android)
add_subdirectory(bionic/libc/libc_bionic_ndk-arm64-android)
add_subdirectory(bionic/libc/system_properties/libsystemproperties-arm64-android)
add_subdirectory(external/compiler-rt/lib/sanitizer_common/libsan-arm64-android)
add_subdirectory(frameworks/av/media/libaaudio/src/libaaudio-arm64-android)
add_subdirectory(frameworks/av/soundtrigger/libsoundtrigger-arm64-android)
add_subdirectory(frameworks/base/core/jni/libandroid_runtime-arm64-android)
add_subdirectory(frameworks/native/cmds/installd/installd-arm64-android)
add_subdirectory(frameworks/native/cmds/servicemanager/servicemanager-arm64-android)
add_subdirectory(frameworks/native/libs/binder/libbinder-arm64-android)
add_subdirectory(libcore/libjavacore-arm64-android)
add_subdirectory(libcore/libopenjdk-arm64-android)
add_subdirectory(libnativehelper/libnativehelper-arm64-android)
add_subdirectory(libnativehelper/libnativehelper_compat_libc++-arm64-android)
add_subdirectory(system/core/base/libbase-arm64-android)
add_subdirectory(system/core/init/libinit-arm64-android)
add_subdirectory(system/core/libziparchive/libziparchive-arm64-android)
add_subdirectory(system/core/liblog/liblog-arm64-android)
add_subdirectory(system/core/libcutils/libcutils-arm64-android)
add_subdirectory(system/core/libutils/libutils-arm64-android)
add_subdirectory(system/core/libprocessgroup/libprocessgroup-arm64-android)
add_subdirectory(system/core/logcat/logcatd-arm64-android)
add_subdirectory(system/core/logcat/liblogcat-arm64-android)
add_subdirectory(system/core/logd/logd-arm64-android)
add_subdirectory(system/core/logd/liblogd-arm64-android)
add_subdirectory(system/core/lmkd/liblmkd_utils-arm64-android)
add_subdirectory(system/core/lmkd/lmkd-arm64-android)
```

​	配置好cmake文件后，使用clion打开项目，选择刚刚配置好的`CMakeLists.txt`文件的目录`out/development/ide/clion/`。导入成功后，我们需要修改工程的根目录，`Tools->Cmake->Change Project Root`，然后选择源码根目录即可。

## 2.9 gitlab+repo管理源码

​	虽然我们将源码导入idea中后，已经可以正常的开始修改源码了。但是由于这是一个庞大的项目，所以我们需要考虑到源码的管理，便于我们随时能够查看自己的修改和切换不同的分支进行开发。否则这样一个巨大的项目，一个月后，再想要找齐当时修改的逻辑，就非常困难了。如果你是个人开发，并且修改的逻辑不是特别复杂，或者是刚开始学习，那么可以选择跳过这个部分，直接修改源码即可。

​	首先我们需要对repo进行一定的了解，在前文中，有简单的介绍到，repo是python脚本实现的，是对git命令的封装，用来管理大型项目关联多个子项目的。现在我们重新回顾一下下载android代码的过程。前文中，我们使用repo进行初始化指定分支，在完成初始化后，会在当前目录生成一个.repo的目录，首先我们查看目录中的manifest.xml文件，内容如下。

```
<?xml version="1.0" encoding="UTF-8"?>
<!--
DO NOT EDIT THIS FILE!  It is generated by repo and changes will be discarded.
If you want to use a different manifest, use `repo init -m <file>` instead.

If you want to customize your checkout by overriding manifest settings, use
the local_manifests/ directory instead.

For more information on repo manifests, check out:
https://gerrit.googlesource.com/git-repo/+/HEAD/docs/manifest-format.md
-->
<manifest>
  <include name="default.xml" />
</manifest>
```

可以看到只是导入了default.xml文件。接着我们查看这个配置文件。

```
<manifest>
  <remote  name="aosp"
           fetch=".."
           review="https://android-review.googlesource.com/" />
  <default revision="refs/tags/android-12.0.0_r3"
           remote="aosp"
           sync-j="4" />

  <superproject name="platform/superproject" remote="aosp" revision="android-12.0.0_r3" />
  <contactinfo bugurl="go/repo-bug" />

  <project path="build/make" name="platform/build" groups="pdk" >
    <copyfile src="core/root.mk" dest="Makefile" />
    <linkfile src="CleanSpec.mk" dest="build/CleanSpec.mk" />
    <linkfile src="buildspec.mk.default" dest="build/buildspec.mk.default" />
    <linkfile src="core" dest="build/core" />
    <linkfile src="envsetup.sh" dest="build/envsetup.sh" />
    <linkfile src="target" dest="build/target" />
    <linkfile src="tools" dest="build/tools" />
  </project>
  <project path="build/bazel" name="platform/build/bazel" groups="pdk" >
    <linkfile src="bazel.WORKSPACE" dest="WORKSPACE" />
    <linkfile src="bazel.sh" dest="tools/bazel" />
    <linkfile src="bazel.BUILD" dest="BUILD" />
  </project>
  <project path="build/blueprint" name="platform/build/blueprint" groups="pdk,tradefed" />
  <project path="build/pesto" name="platform/build/pesto" groups="pdk" />
  <project path="build/soong" name="platform/build/soong" groups="pdk,tradefed" >
    <linkfile src="root.bp" dest="Android.bp" />
    <linkfile src="bootstrap.bash" dest="bootstrap.bash" />
  </project>
  <project path="art" name="platform/art" groups="pdk" />
  <project path="bionic" name="platform/bionic" groups="pdk" />
  .....
</manifest>
```

​	可以看到，这个文件实际上是一份git仓库清单，`repo init`初始化的过程就是下载git仓库清单文件，以及下载repo工具的仓库也就是git-repo项目，使用国内网络进行初始化时的速度非常慢的主要原因就在于git-repo项目较大且必须通过外网访问，所以很多人使用国内源进行`repo init`前还需要通过设置环境变量`REPO_URL`修改git-repo的拉取地址。而`repo sync`步骤就是就是将清单文件中对应的子模块全部拉取下来。而default.xml中的元素主要为以下几种。

​	1、manifest：根元素，所有元素都要定义再根元素中

​	2、remote：git仓库的地址以及名称

​	3、default：仓库默认的属性，比如路径、分支、远程仓库名称

​	4、project：子模块仓库的名称、路径、默认分支等信息

​	5、remove-project：需要从清单中删除的仓库

​	6、copyfile：同步代码时，要复制的文件和目录

​	7、include：导入另外一个清单文件，比如我们觉得一个清单看起来太复杂，可以根据目录分类存放

​	8、linkfile：定义对应的文件或目录的软连接

​	在配置文件中我们可以看到有大量的project元素，在这里我们先记下一个信息，在project元素中的path指的是项目拉取到本地之后存放的路径，而name才是指在git仓库中存放的路径。

​	清楚了使用repo同步代码的原理，以及git清单中元素的作用后我们就可以开始搭建自己的Android源码远程仓库了。由于项目较大，所以我们可以在本地搭建一个gitlab服务，然后将项目上传至gitlab中进行管理，如下是搭建gitlab服务的步骤。

```
// 安装gitlab服务的依赖
sudo apt-get update
sudo apt-get install -y curl openssh-server ca-certificates
sudo apt-get install -y postfix

// 信任gitlab的GPG公钥
curl https://packages.gitlab.com/gpg.key 2> /dev/null | sudo apt-key add - &>/dev/null

// 添加gitlab的源
vim /etc/apt/sources.list.d/gitlab-ce.list
// 加入下面的代码后保存
deb https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/ubuntu xenial main

// 安装gitlab-ce
sudo apt-get update
sudo apt-get install gitlab-ce

// 执行配置
sudo gitlab-ctl reconfigure

// 启动gitlab
sudo gitlab-ctl start

```

​	接下来直接在浏览器中输入局域网ip来访问gitlab页面，比如我的是`http://192.168.2.189/`。然后注册一个账号。在登录的时候出现了下面这个错误

```
Your account has been blocked. Please contact your GitLab administrator if you think this is an error.
```

​	这是因为注册的账号需要审批激活后才能使用。我们回到终端上通过下面的命令激活账号

```
// 进入gitlab的控制台
gitlab-rails console

// 查找刚刚注册的账号
user = User.find_by_email("myuser@example.com")

// 将状态设为激活
user.state = "active"

// 保存修改并退出
user.save
exit
```

​	到这里，gitlab服务准备就绪，登录账号后就可以创建aosp的子模块仓库了。

​	根据前面repo的介绍，我们知道了源码一共是三个部分：git-repo.git的工具仓库、manifests.git的子模块清单仓库、aosp源码子模块仓库。接下来我们将代码同步的流程分割为下面几个步骤。

​	1、参考.repo/manifests/default.xml配置修改为我们自己的gitlab地址并创建一个manifests.git仓库。

​	2、使用脚本批量创建子模块仓库

​	3、使用脚本批量同步子模块代码

​	4、使用自己的gitlab地址同步代码测试

​	由于我们一会需要创建大量的子模块仓库，所以我们不可能在web页面上手动一个个的创建，所以下面我们使用命令来创建一个manifests.git仓库。而命令创建仓库，我们需要gitlab账号的Access Token。我们可以通过在web中登录账号，点击右上角的用户图标，选择Preferences来到用户设置页面，然后进入Access Tokens栏目，填写token名称以及勾选权限，最后点击生成，我生成的token为`27zctxyWZP9Txksenkxb`。流程见下图。

![image-20230216211544482](.\images\image-20230216211544482.png)

​	首选我们需要在gitlab中手动创建一个根目录的group，我这里创建了一个android12_r3的组，所有的子模块仓库都将在这个分组下。在gitlab页面中点击左上角Groups->your Groups。然后点击New group创建分组。成功创建后，记录下这个分组的id，比如我的根目录组id是6.

然后就可以使用curl命令通过token访问gitlab的api创建一个空白的仓库

```
// 创建一个名称为manifests的空白仓库，namespace_id是根目录的分组id
curl --header "PRIVATE-TOKEN: 27zctxyWZP9Txksenkxb" \
     --data "name=manifest&namespace_id=6" \
     --request POST "http://192.168.2.189/api/v4/projects"
```

​	接下来修改配置，并且将清单项目上传到gitlab中

```
// 创建项目目录
mkdir manifest && cd manifest

// 拷贝安卓源码中的git子模块清单文件
cp ~/android_src/aosp12/.repo/manifests/default.xml ./

//编辑清单
vim default.xml

//修改内容如下
<manifest>

  // 修改name为orgin，修改review为我们自己的服务器地址
  <remote  name="origin"
           fetch=".."
           review="http://192.168.2.189/" />
  // 修改remote为上面定义的name
  <default revision="master"
           remote="origin"
           sync-j="4" />
  // 修改remote为上面定义的name
  <superproject name="platform/superproject" remote="origin" revision="master" />
  <contactinfo bugurl="go/repo-bug" />
  .....
</manifest>

//保存上面的修改,然后提交到仓库
git init
git remote add origin git@192.168.2.189:android12_r3/manifest.git
git add . && git commit -m "init"
git push
```

​	准备好清单文件后，接下来就需要准备所有子模块仓库了。首先我们得知道一共有哪些子模块需要上传，而这个通过default.xml中的project元素，很容易得到。我们可以编写一个python脚本来匹配出所有project中的path属性，然后创建group和仓库。下面贴上一份网上找到读取default.xml自动创建所有仓库。

```python
#!/usr/bin/python3

import gitlab
import os
import re
import time
// 读取的配置文件
MANIFEST_XML = "default.xml"
ROOT = os.getcwd()
# gitlab中自己手动创建这个group
ROOT_GROUP = "android12_r3"
MANIFEST_XML_PATH_NAME_RE = re.compile(r"<project\s+path=\"(?P<path>[^\"]+)\"\s+name=\"(?P<name>[^\"]+)\"",
                                       re.DOTALL)
# 修改成自己的gitlab服务地址，以及账号的token
gl = gitlab.Gitlab('http://192.168.2.189/', private_token='27zctxyWZP9Txksenkxb')

manifest_xml_project_paths = []

# 加载default.xml。取出所有需要创建的子仓库，需要验证一下这里的数量和你的project是否一致。
def parse_repo_manifest():
    with open(os.path.join(ROOT, MANIFEST_XML), "rb") as strReader:
        for line in strReader:
            if line is not None and len(line) != 0:
                this_temp_line = line.decode()
                if line.find("path".encode(encoding="utf-8")):

                    s = MANIFEST_XML_PATH_NAME_RE.search(this_temp_line)

                    if s is not None:
                        manifest_xml_project_paths.append(s.group("name"))

    print("manifest_xml_project_paths=" + str(manifest_xml_project_paths))
    print("manifest_xml_project_paths len=" + str(len(manifest_xml_project_paths)))

# 创建组以及对应的子模块仓库
def create_group_and_project():
    all_groups = gl.groups.list(all=True)
    print("all_groups=" + str(all_groups))
    group_parent = None
	# 遍历所有组，查找根组android12_r3是否存在
    for g in all_groups:
        if g.name == ROOT_GROUP:
            group_parent = g
            break
    print("group parent=" + str(group_parent))
	# 遍历所有子仓库路径
    for path in manifest_xml_project_paths:
        print("path=" + path)
        paths = path.split("/")
        print("paths=" + str(paths))

        last_path_index = len(paths) - 1

        group = group_parent
        for index in range(0, last_path_index):
            p = paths[index]
            print("p=" + p)
            # is the group exist
            print("parent group=" + group.name)
            try:
                all_groups = group.subgroups.list(all=True)
            except AttributeError:
                all_groups = []
                print("AttributeError: clear all subgroups")
			# 遍历所有组，找当前子模块的组是否存在
            is_group_exist = False
            for g in all_groups:
                if g.name == p:
                    is_group_exist = True
                    group = g
                    print("group exist=" + g.name)
                    break
            if is_group_exist:
                continue
            # create subgroup
            data = {
                "name": p,
                "path": p,
                "parent_id": group.id
            }
			# 不存在则创建子模块所属的组
            try:
                group = gl.groups.create(data)
                print("group create success name=" + p)
                time.sleep(1)
            except gitlab.exceptions.GitlabCreateError as e:
                if e.response_code == 400:
                    print("group:" + p + " has already been created")

                    query_groups = gl.groups.list(all=True)
                    print("query_groups:" + str(query_groups))
                    for query_group in query_groups:
                        if query_group.name == p and query_group.parent_id == group.id:
                            group = query_group
                            print("update exit group:" + group.name)
                            break
		# 创建子模块仓库，创建前先遍历是否仓库已存在
        project = paths[last_path_index]
        print("group project list group=" + group.name)
        real_group = gl.groups.get(group.id, lazy=True)
        all_projects = real_group.projects.list(all=True)
        print("group all projects=" + str(all_projects))
        is_project_exist = False
        for p in all_projects:
            if p.name == project:
                is_project_exist = True
                print("project exist=" + p.name)
                break
        if not is_project_exist:
            print("create project=" + project)
            gl.projects.create({'name': project, 'path': project, 'namespace_id': group.id})
            print("project create success name=" + project)
            time.sleep(1)

# 测试是否能成功创建
def test_create_project_with_dot_name():
    # need use path field, if don't use path, GitLab url will replace "." to "_"
    res=gl.projects.create({'name': "xxx.yy.xy", 'path': "xxx.yy.xy"})
    print(res)

if __name__ == '__main__':
    parse_repo_manifest()
    create_group_and_project()
    # test_create_project_with_dot_name()

```

​	子模块仓库建立完成，最后我们还需要将代码上传到对应的仓库中。同样参考网上找的上传代码，修改一部分细节，这里一定要注意default.xml中，project元素的属性path的是本地路径，而name才是指的git仓库的路径，代码如下

```python
#!/usr/bin/python3

import os
import re,time
# 代码放在我们之前准备好的清单仓库中，然后指定default.xml路径
MANIFEST_XML = "./manifests/default.xml"
ROOT = os.getcwd()
LOG_FILE_PATH = os.path.join(ROOT, "push.log")
# 匹配path
MANIFEST_XML_PATH_NAME_RE = re.compile(r"<project\s+path=\"(?P<path>[^\"]+)\"\s+name=\"(?P<name>[^\"]+)\"\s+",
                                       re.DOTALL)
# 设置源码路径
SOURCE_CODE_ROOT = "/home/king/android_src/android12_r3/"
# 设置gitlab仓库的根目录分组
REMOTE = "git@192.168.2.189:android12_r3/"
manifest_xml_project_paths = []

# 读取配置文件中的所有子模块路径
def parse_repo_manifest():
    with open(os.path.join(ROOT, MANIFEST_XML), "rb") as strReader:
        for line in strReader:
            if line is not None and len(line) != 0:
                this_temp_line = line.decode()
                if line.find("path".encode(encoding="utf-8")):

                    s = MANIFEST_XML_PATH_NAME_RE.search(this_temp_line)

                    if s is not None:
                        manifest_xml_project_paths.append({"path":s.group("path"),"name":s.group("name")})

    print("manifest_xml_project_paths=" + str(manifest_xml_project_paths))
    print("manifest_xml_project_paths len=" + str(len(manifest_xml_project_paths)))

# 上传源码
def push_source_code_by_folder(str_writer):
    # 遍历所有路径
    for path in manifest_xml_project_paths:
        print("path=" + path["path"])
        abs_path = SOURCE_CODE_ROOT + path["path"]
        # 路径存在则进行上传
        if os.path.exists(abs_path):
            # change current work dir
            os.chdir(abs_path + "/")
            # 1\. delete .git & .gitignore folder
            rm_git_cmd = "rm -rf .git"
            rm_gitignore_cmd = "rm -rf .gitignore"
            os.system(rm_git_cmd)
            os.system(rm_gitignore_cmd)

            # 2\. list dir
            dir_data = os.listdir(os.getcwd())

            cmd_list = []

            print("changed cwd=" + os.getcwd())

            if len(dir_data) == 0:
                echo_cmd = "echo \"This is a empty repository.\" > ReadMe.md"
                str_writer.write(f"empty repository:{abs_path}".encode() )
                str_writer.write("\r\n".encode())
                cmd_list.append(echo_cmd)
			# 将所有上传命令组装好
            git_init_cmd = "git init"
            cmd_list.append(git_init_cmd)

            git_remote_cmd = "git remote add origin " + REMOTE + path["name"] + ".git"
            cmd_list.append(git_remote_cmd)

            git_add_dot_cmd = "git add ."
            cmd_list.append(git_add_dot_cmd)

            git_commit_cmd = "git commit -m \"Initial commit\""
            cmd_list.append(git_commit_cmd)

            git_push_cmd = "git push -u origin master"
            cmd_list.append(git_push_cmd)
			# 执行上传命令
            for cmd in cmd_list:
                print("begin exec cmd=" + cmd)
                os.system(cmd)
                print("end exec cmd=" + cmd)
        else:
            print("abs_path=" + abs_path + " is not exist.")
            str_writer.write(f"folder not exist:{abs_path}".encode() )
            str_writer.write("\r\n".encode())

def wrapper_push_source_code_write_log():
    with open(LOG_FILE_PATH, 'wb+') as strWriter:
        push_source_code_by_folder(strWriter)
        strWriter.close()

# def test_only_dot_git_folder():
#     subdir_and_file = os.listdir(os.getcwd())
#     print("subdir_and_file=" + str(subdir_and_file))
#     with open(LOG_FILE_PATH, 'wb+') as strWriter:
#         strWriter.write(str(subdir_and_file).encode())
#         strWriter.write("\r\n".encode())
#         strWriter.write(str(subdir_and_file).encode())
#         strWriter.close()

if __name__ == '__main__':
    parse_repo_manifest()
    wrapper_push_source_code_write_log()

```

​	上传过程较慢，等待所有仓库上传完成，最后将git-repo工具子模块上传到我们的仓库。首先在gitlab中创建一个分组android-tools。然后在分组中手动创建一个仓库git-repo。然后从github下载一份git-repo的工具源码传到我们的gitlab。过程如下。

```
// 从github下载git-repo源码并上传到gitlab仓库
git clone https://github.com/GerritCodeReview/git-repo.git && cd git-repo
rm .git -rf
git init
git remote add origin git@192.2.189:android-tools/git-repo.git
git add .
git commit -m "init"
git push -u origin master

// 将这里的repo拿来使用
cp ./repo ~/bin/
PATH=~/bin:$PATH
```

​	终于一切准备就绪，那么开始拉取我们自己的代码吧。

```
// 创建存放源码的目录
mkdir myandroid12 && cd myandroid12

// 指定使用我们自己的仓库，使用我们自己的git-repo
repo init -u git@192.168.2.189:android12_r3/manifest.git --repo-url=git@192.168.2.189:android-tools/git-repo.git --no-repo-verify

// 出现了下面的错误
repo: error: unable to resolve "stable"
fatal: double check your --repo-rev setting.
fatal: cloning the git-repo repository failed, will remove '.repo/repo'

// 然后我们修改使用master分支，再重新执行上面的repo init命令
export REPO_REV=refs/heads/master

repo init -u git@192.168.2.189:android12_r3/manifest.git --repo-url=git@192.168.2.189:android-tools/git-repo.git --no-repo-verify

//同步代码
repo sync -j8
```

​	在同步的过程中，出现了两个问题。首先第一个是出现如下错误

```
remote:
remote: ========================================================================
remote:
remote: The project you were looking for could not be found or you don't have permission to view it.
remote:
remote: ========================================================================
remote:
fatal: 无法读取远程仓库。

请确认您有正确的访问权限并且仓库存在。

platform/build/bazel:
```

​	检测代码后发现bazel仓库在路径build中不存在，这个仓库被建立在了platform下。导致这个问题的原因是由于前面的创建git的脚本中，发现build被指定为project，所以创建为仓库，而bazel必须是在一个group下，路径才会成立。而build的仓库已经存在，创建这个group失败后，就默认使用了更上一层的group。而解决办法也非常简单，直接将default中的几个build路径下的几个project重新命名，不要放在build的group下即可。下面是解决后的default.xml配置。

```
<project path="build/make" name="platform/build" groups="pdk" >
    <copyfile src="core/root.mk" dest="Makefile" />
    <linkfile src="CleanSpec.mk" dest="build/CleanSpec.mk" />
    <linkfile src="buildspec.mk.default" dest="build/buildspec.mk.default" />
    <linkfile src="core" dest="build/core" />
    <linkfile src="envsetup.sh" dest="build/envsetup.sh" />
    <linkfile src="target" dest="build/target" />
    <linkfile src="tools" dest="build/tools" />
</project>
<project path="build/bazel" name="platform/build_bazel" groups="pdk" >
	<linkfile src="bazel.WORKSPACE" dest="WORKSPACE" />
	<linkfile src="bazel.sh" dest="tools/bazel" />
	<linkfile src="bazel.BUILD" dest="BUILD" />
</project>
<project path="build/blueprint" name="platform/build_blueprint" groups="pdk,tradefed" />
<project path="build/pesto" name="platform/build_pesto" groups="pdk" />
<project path="build/soong" name="platform/build_soong" groups="pdk,tradefed" >
    <linkfile src="root.bp" dest="Android.bp" />
    <linkfile src="bootstrap.bash" dest="bootstrap.bash" />
</project>
```

​	另外一个问题也非常类似。错误如下。

```
请确认您有正确的访问权限并且仓库存在。
device/mediatek/wembley-sepolicy: sleeping 4.0 seconds before retrying
```

​	经过检查后发现，这是由于这个仓库在default.xml中的配置如下

```
<project name="device/mediatek/wembley-sepolicy" path="device/mediatek/wembley-sepolicy" groups="device"/>
```

​	然后看了创建仓库和批量提交代码的逻辑就明白了，是的，name和path的顺序反了，导致正则表达式未能成功匹配到这个仓库，所以我们调整一下name和path的顺序即可。

​	成功拉取完成后，如果在编译时碰到找不到文件的问题，这是由于有些子模块仓库下的子目录中有`.gitignore`文件，将一些应该提交的文件给过滤掉了。就回到我们同步代码的目录中，找到指定的git仓库，使用下面的方式重新提交一下。然后回到我们同步下来的代码处重新拉取更新的代码。

```
// 进入缺少文件的子模块仓库目录
cd ~/external/angle/
git add . -f
git commit -m "init"
git push -u origin master
cd ~/android_src/myandroid12/
repo sync -j8
```

​	到这里就完成了gitlab源码管理android源码开发了。最后如何使用git提交和查看历史记录我就不在这里叙述了。

## 2.10 小结

​	在这一章里，主要讲述了如何从零开始搭建一个编译Android源码的环境，以及如何选择编译的版本和完整的编译Android源码并使用自己编译的内核，然后将这个我们编译好的镜像尝试多种方式刷入测试手机中。为了后续开发和阅览代码的便利，又讲述了如何使用Android Studio和Clion导入源码。最后为了便于长期维护和持续性的开发，我们又搭建了gitlab+repo管理Android源码。终于将一切准备就绪了。

​	TODO 你看看这里是不是小结写的有点简单。看着应该怎么丰富一下。

