# 第二章 系统开发环境与工具 #

## 2.1 重新看待系统定制

​  经过第一章的学习，对AOSP定制进行简略的了解后，相信这时，在读者的心中已经对系统定制开发有了大致的理解。简单来说，所谓的系统定制，相当于在一款成熟的产品上进行二次开发。和我们二次开发其他软件项目的学习步骤不会有太大的出入，细节的区别就在于Android源码相比其他软件项目要更加庞大。

​	尽管Android源码非常庞大，但对于初学者，并不需要完整的吃透所有代码。重要的是学会分析的思路，学会看代码，了解Android的部分运行原理，然后思考如何达到自己的目的，最后自已去尝试实现。

​	学习的流程和我们二次开发其他应用一样，第一步是要了解如何将项目成功编译并运行。这一章将详细讲解在各种不同的环境下，我们应该如何编译Android源码，并将其刷入手机中。

## 2.2 环境准备

安卓系统在低于版本10之前，是支持macOS系统上编译AOSP代码的。在新版本系统的演进过程中，安卓官方已经放弃在macOS系统平台上做AOSP开发的支持，官方开发指导环境采用了Linux上比较有名的Ubuntu发行版本。

在实际的开发过程中，可以使用Windows系统下的WSL2或Docker来构建一个Ubuntu系统运行环境，同样可以完成AOSP编译与开发工作。

这一节将会介绍在Windows系统与Linux系统上，如何完成环境准备工作。
### 2.2.1 Windows

​	由于在Windows中缺少了各种底层支持，所以一般情况我们不会直接在Windows环境中编译，而是选择在Windows中创建一个Linux的虚拟环境，然后在虚拟环境中安装编译所需要用到的底层依赖。而Windows的虚拟机环境我们有多种选择，例如Docker、WSL2、Vmware。

​	三种虚拟环境我都尝试过编译，其中Docker在Windows的体验并不怎么好，特别是在我们编译需要较大体积硬盘的情况下，完整编译后，下次开机耗时明显变高。如果不擅长折腾的话，不太建议在Windows下采用Docker来编译源码。

​	WSL2是Windows下内置的Linux子系统，是一个非常轻量化的Linux系统，如果你是属于那种又想在Windows中编译，但是又不想打开虚拟机，那选择WSL2就没错了。使用起来的感觉就好似直接使用命令行一样。并且编译性能相比Vmware要更加高效。在我的笔记本环境中，WSL2完整编译的耗时为130分钟，而Vmware的耗时是170分钟，这是因为它是完全直连计算机硬件，无需虚拟化硬件的。所以性能是有较为显著的提升。

​	如果你是Windows10的环境，那么你需要先查询当前系统版本，必须是18917或更高的版本才支持WSL2。在cmd命令行中输入`winver`查看当前版本

![image-20230102183339463](.\images\image-20230102183339463.png)

​	由于是系统自带的，所以安装起来非常方便，可以直接在控制面版->程序->启动或关闭Window功能中开启支持即可，如下图

![img](.\images\69ba546fd55c4fea8ef9b5d55a9bd354.png)

​	或者是采用命令的方式开启虚拟机平台和Linux子系统，使用管理员权限启动PowerShell。

![image-20230102183708998](.\images\image-20230102183708998.png)

​	执行下面的命令开启功能

~~~
//启用虚拟机平台
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
//启用Linux子系统
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
~~~

​	启动完成后重启计算机，然后我们就可以开始安装一个ubuntu了。直接打开Microsoft Store应用商店搜索ubuntu，然后选择自己需要的版本即可，例如我安装的是22.04版本，如下图。

![image-20230102184626538](.\images\image-20230102184626538.png)

​	成功获取ubuntu后，从应用中启动ubuntu即开始正式安装。安装完成后，我们点细节需要处理，子系统需要迁移，由于应用商店默认会给我们安装在C盘中，而我们编译系统会占用相当大的空间，所以必须将子系统迁移到其他硬盘中。首先打开命令行工具查询当前的子系统名称。

~~~
wsl -l -v

  NAME        STATE           VERSION
* ubuntu22    Running         2
~~~

然后我们将这个子系统导出，并且注销掉，然后再重新导入放在其他磁盘的子系统。

~~~
//导出子系统
wsl --export ubuntu22 E:\wsl2\ubuntu22.tar
//注销之前的虚拟机
wsl --unregister ubuntu22
//重新导入虚拟机,并且指定新的虚拟机存放位置
wsl --import ubuntu22 E:\wsl2\ubuntu22_wsl E:\wsl2\ubuntu22.tar
~~~

​	这时我们在直接在命令行执行`wsl`即可进入子系统。

​	使用WSL2主要是在于轻量级和更优的高性能，一般都是命令模式的linux，即使我们在WSL2中安装了图形界面，也会存在一些依赖缺陷，所以使用WSL2开发时，一般是在Windows使用插件来远程代码管理进行开发。例如使用vscode就直接用wsl插件可以快速的远程访问代码，或者是安装ssh服务后，使用remote ssh插件进行代码修改。

​	如果我们需要完整的Linux虚拟机，使用VMware会更加的省事。步骤也非常简单流程如下。

​	1、下载并安装VMware虚拟机，然后下载ubuntu22.04镜像。

​	2、VWware创建虚拟机，选择指定镜像

![image-20230102194041709](.\images\image-20230102194041709.png)

3、设置初始账号密码

![image-20230102194243774](.\images\image-20230102194243774.png)

4、选择虚拟机保存位置，这里不要保存在c盘，记得磁盘要有至少300G的空间

![image-20230102194331141](.\images\image-20230102194331141.png)

5、虚拟硬件CPU核心根据你的电脑配置进行调整，尽量多分点给虚拟机。

![image-20230102194543812](.\images\image-20230102194543812.png)

6、虚拟内存分配，至少保证16G以上的内存，否则可能会碰到内存不足编译失败的情况。

![image-20230102194722427](.\images\image-20230102194722427.png)

7、虚拟硬盘分配，这里至少分配300G的空间，考虑到性能，我选择的是单文件吗，这里如果选择立即分配所有磁盘空间，能提高一定的性能。如果你的电脑配置不是很高，建议你选择立即分配。

![image-20230102194952517](.\images\image-20230102194952517.png)

​	虚拟机开机后将默认进入Ubuntu安装界面，按照提示进行选择语言，区域等待安装完成即可。

### 2.2.2 Linux

​	Linux系统的选择非常多，一般情况首选最新的Ubuntu LTS稳定版即可。首先是安装我们必备的开发工具。

1、Android Studio下载并安装，下载地址：`https://developer.android.google.cn/studio/`

2、Clion下载并安装，下载地址：`https://www.jetbrains.com/zh-cn/clion/`

3、vscode下载并安装，下载地址：`https://code.visualstudio.com/`

​	然后用命令更新一下软件，并安装一下基本的工具

~~~
// 更新软件列表
sudo apt update -y && sudo apt upgrade -y

// 安装python和apt-utils
sudo apt-get install -y apt-utils python3 python3-pip python2

// 安装pip
pip install -U pip

// 设置pip使用国内源
mkdir ~/.pip
touch ~/.pip/pip.conf
echo -e '\n[install]\ntrusted-host=pypi.douban.com\n[global]\nindex-url=http://pypi.douban.com/simple' > ~/.pip/pip.conf
cat ~/.pip/pip.conf
pip install pytest

~~~



### 2.3 如何选择源码版本

​	在开始拉取代码前，我们首选需要了解自己需要的是哪个分支版本，所以我们先看官网对版本的说明https://source.android.com/docs/setup/about/build-numbers?hl=zh-cn

​	然后根据我们的需求，比如我想要在Android10的基础上进行二次开发，那么我就找到对应的版本描述，根据下图，可以看到各个版本号关联的代码分支，Android版本，支持哪些设备。

![image-20230103220519836](.\images\image-20230103220519836.png)

​	这么多版本，我们需要选一个最适合我们的版本，我的选择规律如下:

1、优先找对你的测试机支持的对应版本。

2、然后再找除了支持你的这个设备外，还支持了更多设备的版本。

3、满足上面两个条件的最高分支版本，也就是尽量找最新的代码。

如果你是直接选择使用虚拟机的，那么直接选择支持版本最多的分支即可。这里我的测试设备是pixel 3，所以我选择了版本`SP1A.210812.016.A1`,对应的分支代码是`android-12.0.0_r3`，如下图。

![image-20230103220838404](.\images\image-20230103220838404.png)

### 2.3.1 编译

​	上面知道了我们需要的目标分支，接下来要拉取代码。repo是一个以git为基础包装的代码版本管理工具，内部是由python脚本构成的，对git命令进行包装，主要为了方便管理大型的项目，使用repo可以非常方便的拉取对应的分支节点。下面我们开始拉取代码。

~~~
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
~~~

​	同步代码`repo sync -c -j8`的命令其中`-c`表示只同步当前分支代码，可以提高同步速度，而`-j`是设置同步使用的线程数，这里我使用了8条线程，但并不是线程越多速度越快，而是根据cpu的核心使用最合理的线程数才能达到最佳的并发效果。

~~~
// 查看可用cpu数量，我的环境显示为16
nproc --all

// 直接使用最佳线程数
repo sync -c -j16

//也可以直接省略成一句
repo sync -c -j$(nproc --all)
~~~

​	代码同步完成后,会提示`Success`，如果失败了，就重新拉取即可，多拉取几次后，基本都能同步成功。接下来我们开始安装编译的底层依赖。

~~~
// AOSP编译的相关依赖安装
sudo apt-get install -y git-core gnupg flex bison build-essential \
	zip curl zlib1g-dev gcc-multilib g++-multilib libc6-dev-i386 lib32ncurses5-dev \
	x11proto-core-dev libx11-dev lib32z1-dev libgl1-mesa-dev libxml2-utils xsltproc unzip \
	fontconfig libncurses5 procps rsync libsqlite3-0
~~~

​	依赖安装完成后，我们再进行一个细节调整，由于我们经常需要备份代码，将整个源码进行打包备份，但是编译出来的输出目录`out`的体积非常庞大，所以我备份时会选择移走`out`目录，或者干脆删除掉，这样非常的麻烦，所以我会选择直接修改编译输出的目录。通过设置环境变量`OUT_DIR`就可以调整编译结果的输出目录了。

~~~
vim ./build/envsetup.sh
// 在底部加上环境变量设置为和源码同一级的目录，我当前源码路径为~/android_src/aosp12
export OUT_DIR=~/android_src/aosp12_out
~~~

​	在开始编译前，我们还需要准备对应设备的驱动，根据我们前面选择的版本号`SP1A.210812.016.A1`,在官网地址：`https://developers.google.com/android/drivers`中找到对应的版本号，并且可以看到`Pixel 3`的手机对应的代号是`blueline`。

![image-20230103232052738](.\images\image-20230103232052738.png)

​	第一个文件`Vendor`是用来存储厂商特定的文件，比如设备驱动程序。Android穷的那个时会根据提供的这些设备驱动来正确的加载硬件。这个文件通常由设备厂商提供。如果你成功编译Android后，输出目录缺少vendor.img文件，那么你就需要检查下是否忘记导入对应型号的设备驱动了。

​	第二个文件是高通提供的相关设备驱动程序，比如GPS，摄像头，传感器等等。

​	点击`Link`下载，然后将下载的文件拷贝到Android源码根目录下。然后解压，并导出相关驱动文件。

~~~
// 解压驱动文件
tar -xvf qcom-blueline-sp1a.210812.016.a1-33e668b9.tgz
tar -xvf google_devices-blueline-sp1a.210812.016.a1-d10754e0.tgz

// 解压会得到两个文件extract-google_devices-blueline.sh和extract-qcom-blueline.sh
// 依次运行两个文件，运行后会提示许可说明，按回车键，然后按q跳过，最后手动输入I ACCEPT后回车即可
./extract-google_devices-blueline.sh
./extract-qcom-blueline.sh
~~~

​	导入设备驱动完成后，准备工作基本完成，可以开始编译源码了。

~~~
// 初始化环境，执行后会导入多个命令，辅助我们进行编译。
// 这里也可以使用. build/envsetup.sh 是同样的效果
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
~~~

​	在上面选择版本中可以看到`aosp_arm-eng`和`aosp_arm64-eng`的选项，这两个是模拟器使用的版本。而模拟器使用的版本是可以不需要导入设备驱动文件的。如果在`lunch`的菜单中没有看到你要编译的版本，并且直接`lunch aosp_blueline-userdebug `也提示错误，可能是没有成功导入驱动文件，或者下载的驱动文件不对。

​	同一个代号的编译有三种编译版本选择。分别如下：

1、`aosp_blueline-user` 一般是默认的编译环境，主要是作为发布版本，这种版本编译的环境会默认开启大多数的安全机制，比如`ro.secure`值为1，`ro.debuggable`值为0，，需要我们自行用第三方工具获取root权限。我们日常使用的机子就是属于user环境的。

2、`aosp_blueline-userdebug` 通常用于测试和调试Android系统，会启动一些调试工具，例如默认开启`adb`调试，`ro.debuggable`值为1，系统自带root权限等等。

3、`aosp_blueline-eng` 同样也是用于测试和调试的环境，但是比`userdebug`要更加极端，会禁用一些安全机制，比如签名验证，关闭一些编译优化等等。

​	第一次完整编译非常的漫长，我的电脑耗时2个小时成功编译。编译成功后我们检查一下输出的文件。

~~~
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
~~~

​	确定有编译出`vendor.img、system.img、boot.img`等等镜像文件，就说明编译成功了。

### 2.4 模块编译

​	前文在编译的过程中介绍到，我们使用`source ./build/envsetup.sh`初始化环境的时候，导入了多个命令来帮助我们进行编译。我们可以通过命令`hmm`查看提供的命令帮助。

~~~
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
~~~

​	`croot` 命令可以跳转根目录，或者是根目录下的任意子目录

​	`m` 命令会直接在根目录运行编译，即使我们当前目录是在子目录也是相当于在根目录编译。也可以指定名称来编译单独的目标，例如`m droid`。

​	`mm ` 编译当前目录中的所有模块及依赖项

​	`mmm` 编译指定目录中的所有模块及依赖项

​	`clean` 清除编译的结果，相当于删掉out目录中的内容

​	我们可以通过`m help`查看可以单独编译哪些选项

~~~
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
~~~

​	通过帮助命令的提示，我们可以看到`m snod`就是单独编译`System`,命令`m vnod`就是单独编译`Vendor`。大多数时候我们修改的内容都是在`System`中。我们可以根据自己的变动情况，模块编译即可。

### 2.5 内核编译

​	在前面我们编译完成后，可以在编译的镜像结果中看到文件`boot.img`，这个文件就是内核镜像文件。但是这个内核是Android源码树中已经编译好的内核文件，并不是我们编译出来的，如果我们想要修改内核，就需要拉取内核的对应分支，编译内核，将编译结果放入Android源码中的指定路径，然后再重新编译Android。刷入手机后，使用的内核就是我们自己编译的了。

​	首先第一步是找到对应我们当前手机的内核分支，官网提供了详细的说明https://source.android.com/docs/setup/build/building-kernels。根据下图可以看到，对应`Pixel 3`测试机分支是`android-msm-crosshatch-4.9-android12`。

![image-20230105221730348](.\images\image-20230105221730348.png)

​	接下来我们按照官网的说明拉取代码并编译。

~~~
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
~~~

​	编译成功后，我们还需要指定Android源码编译时使用这个内核文件。只需要设置环境变量指定路径即可。方式如下。

~~~
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
~~~

### 2.6 刷机

​	大多数情况下，非技术的Android爱好者通常会使用傻瓜式一键刷机工具，例如刷机大师、刷机精灵、奇兔等等。这种刷机方式就是属于软刷（软件刷机），除此之外还有我们第一章中简单介绍到的线刷和卡刷。不论刷机的方式是什么，他们最终的原理都是相同的，都是对刷机包进行处理，然后将ROM文件写入对应的分区，替换掉原始文件。下面我们将简单介绍如何进行线刷和卡刷。

### 2.6.1 线刷

​	通过上面编译中的步骤，在目录`aosp12_out/target/product/blueline/`中能看到若干个后缀为`img`的镜像文件。我的输出路径`aosp12_out`是由于我手动指定了输出目录，如果你没有设置，那么默认是在`aosp12/out/target/product/blueline/`目录下。最后的目录`blueline`是对应编译的版本，如果你是其他版本，就在对应的目录下查看。

​	首先我们要进入刷机模式，然后环境变量设置编译结果的路径，然后使用命令完整刷机即可。详细流程如下

~~~
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
~~~

​	等待刷机结束即可，刷机结束后会自动进入Android系统。如果我们只想刷单个分区镜像，也是可以的。流程如下

~~~
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
~~~

### 2.6.2 卡刷

​	我们前面编译出来的是线刷包，如果我们需要卡刷包，就需要使用下面的方式进行编译

~~~
// 下面是简单的编译卡刷包
cd aosp12
source ./build/envsetup.sh
lunch aosp_blueline-userdebug
make otapackage
~~~

​	编译完成后，我们可以在前面线刷包的路径下看到卡刷包文件，我这里的文件名是`aosp_blueline-ota-eng.king.zip`。除了上面的方式，我们还可以完整编译卡刷包，编译方式如下

~~~
//下面是完整编译卡刷包
cd aosp12
source ./build/envsetup.sh
lunch aosp_blueline-userdebug
mkdir dist_output
make dist DIST_DIR=dist_output
~~~

​	编译完成后，可以在目录`dist_output`中看到完整卡刷包结果。

​	接下来是如何刷入卡刷包，有两种刷入方式，一种是使用`adb sideload`命令刷入，另一种方式是使用twrp刷入。下面演示两种不同方式的刷机流程。

​	1、adb sideload（这里没写完，你补充一下，我这边环境没跑通）

​		首先进入fastbootd

~~~
adb reboot bootloader
fastboot reboot fastboot
~~~

​		这时的界面如下图，使用音量键减，切换到`Enter recovery`，然后按电源键进入`recovery`模式

![image-20230108190236615](.\images\image-20230108190236615.png)

​		接下来进入下面的界面，选择`Apply update from ADB`

![image-20230108190631803](.\images\image-20230108190631803.png)

​

​	2、twrp（这里没写完，你补充一下，我这边环境没跑通）
