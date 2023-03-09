# 第五章 系统内置功能

## 5.1 什么是系统内置

​	系统内置简单的说，就是将镜像刷入手机后默认就在手机中能够使用的功能，例如Android内置的Launcher、Phone、Email、Setting等系统App都是属于内置的。同样开发者也可以制作一个App，将其内置在系统中并且作为系统应用，又或者在工作中，每次手机刷机后需要安装的一些环境，也可以内置在系统中，这样每次刷机后都不必重新配置环境。

​	在前几章的学习中，介绍了Android是如何实现启动系统，以及打开应用程序的执行流程，并且小牛试刀修改替换了系统的资源文件。将AOSP看做是一个大型的项目，本章需要学习的是，如何对这个项目二次开发，在它的基础上扩展一些，将一些更加便利的功能内置在系统中，由于Android系统非常庞大，每次修改后都需要进行编译再刷入手机。而这些功能的业务相关的代码，尽量不要直接写在AOSP源码中，避免浪费大量的时间在等待中。

## 5.2 系统内置App

​	首先，找到Android系统自身内置app的所在目录`packages/apps`，在系统中内置的大多数App源码都是在这里，打开任意一个系统内App的目录进去后，能看到这里的结构和正常开发的Android App没有什么区别。需要内置的App代码并不是一定要放在这个目录下，可以选择将编译后的apk内置进去，这样就能使用`Android Studio`单独开发这个App。

```
cd ./packages/apps
ls

BasicSmsReceiver       DevCamera              ManagedProvisioning    QuickSearchBox             Test
Bluetooth              Dialer                 Messaging              RemoteProvisioner          ThemePicker
Browser2               DocumentsUI            Music                  SafetyRegulatoryInfo       TimeZoneData
Calendar               EmergencyInfo          MusicFX                SampleLocationAttribution  TimeZoneUpdater
Camera2                Gallery                Nfc                    SecureElement              Traceur
Car                    Gallery2               OnDeviceAppPrediction  Settings                   TV
CarrierConfig          HTMLViewer             OneTimeInitializer     SettingsIntelligence       TvSettings
CellBroadcastReceiver  ImsServiceEntitlement  PhoneCommon            SpareParts                 UniversalMediaPlayer
CertInstaller          KeyChain               Protips                Stk                        WallpaperPicker
Contacts               Launcher3              Provision              StorageManager             WallpaperPicker2
DeskClock              LegacyCamera           QuickAccessWallet      Tag

cd WallpaperPicker
ls

Android.bp  AndroidManifest.xml  build.gradle  CleanSpec.mk  LibraryManifest.xml  OWNERS  res  src
```

​	接下来，开发一个简单的案例。然后将这个App应用内置到系统中，编译后刷入手机，案例的实现代码直接直接默认的即可。

```java

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }
}
```

​	`android:shareUserId` 是`AndroidManifest.xml`文件中的一个属性，用于应用程序之间的共享用户ID。共用用户ID可以让应用程序之间更好的进行相互访问和操作。当一个应用程序定义了`android:shareUserId`属性时，另一个相互信任的应用程序，可以设置相同的 `android:shareUserId` 属性，从而实现应用程序的数据共享和交互。

​	在安装和运行应用程序之前，设备会将具有相同共享用户ID的应用程序，视为同一用户。因此，可以访问对方的数据，比如，`SharedPreferences`和文件等。如果应用程序没有设置`android:shareUserId`属性，则其默认值是该应用程序的包名。以下是`AndroidManifest.xml`中的配置。

```
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:sharedUserId="android.uid.system"
    package="cn.mik.systemappdemo">
    ...
</manifest>
```

​	如果直接设置了这个属性，再使用常规的方式安装就提示下面的错误。

```
Installation did not succeed.
The application could not be installed: INSTALL_FAILED_SHARED_USER_INCOMPATIBLE

List of apks:
[0] 'C:\Users\king\AndroidStudioProjects\SystemAppDemo\app\build\intermediates\apk\debug\app-debug.apk'
Installation failed due to: 'INSTALL_FAILED_SHARED_USER_INCOMPATIBLE: Package cn.mik.systemappdemo tried to change user null'
```

​	测试用例准备就绪后就可以来到源码的目录`packages/apps`，创建一个新的目录`SystemAppDemo`，将刚刚编译的样例App也改名为SystemAppDemo放入这个目录，在这个新目录中，添加一个编译的配置文件Android.mk。

```
cd ./packages/apps/
mkdir SystemAppDemo && cd SystemAppDemo
touch Android.mk
gedit Android.mk

//添加下面的内容
LOCAL_PATH := $(call my-dir)
#清除环境变量
include $(CLEAR_VARS)
#模块文件名
LOCAL_SRC_FILES := SystemAppDemo.apk
#模块名称
LOCAL_MODULE := SystemAppDemo
#定义模块的类型
LOCAL_MODULE_CLASS := APPS
#哪个版本进行编译，optional表示可选模块。可选字段： user 、 eng 、 tests
LOCAL_MODULE_TAGS := optional
#签名，platform表示系统签名，PRESIGNED表示保持原签名
LOCAL_CERTIFICATE := platform
#不进行odex优化
LOCAL_DEX_PREOPT := false
include $(BUILD_PREBUILT)


```

​	在Android系统编译过程中，`PRODUCT_PACKAGES` 是一个重要的变量，它定义了系统所需构建的软件包列表。`PRODUCT_PACKAGES` 变量定义的是本次构建需要编译打包的软件包，包括一些基础系统组件和应用程序模块，例如音频服务模块、媒体播放库、输入法、设置应用程序等。

​	在构建规则文件`./build/make/target/product/mainline_system.mk`中添加配置。

```
PRODUCT_PACKAGES += SystemAppDemo \
```

​	到这里就修改完毕了，重新编译系统，将其刷入手机中。手机成功进入系统后，打开应用查看进程身份即可。

```
source ./build/envsetup.sh

lunch aosp_blueline-userdebug

make -j$(nproc --all)

adb reboot bootloader

flashflash all -w

// 等待系统刷机完成后打开桌面上的SystemAppDemo
adb shell
ps -e|grep systemappdemo
// 发现进程身份已经变成system的了。
system        5033  1058 14718076 89256 0                   0 S cn.mik.systemappdemo

```

## 5.3 构建系统

​	Android提供了两种构建系统方式，在Android7.0之前都是使用基于make的构建系统，在源码中由`Android.mk`文件描述构建规则，这是Android开发历史中遗留的一种构建方式，由于make在Android中构建缓慢、容易出错、无法扩展难以测试。所以在7.0后引入了soong构建系统，在源码中由Android.bp文件描述soong的构建规则，在soong中采用了`kati GNU Make`克隆工具和`ninja`来加速对系统的构建。

​	Soong构建系统是一个由Google开发的、用于构建Android的构建系统。它是一个用go语言编写的构建系统，旨在解决早期版本的Android构建系统中存在的问题，所以，它现在是Android构建系统的首选。

​	Soong的主要特点和优势包括：

1. 速度快：Soong采用Makefile-style的语法并支持增量构建，使其比较快速。
2. 简洁易用：Soong的语法清晰，易于理解和使用。
3. 自动化代码生成：Soong可以自动化生成代码，减少手动输入的工作量。
4. 插件式：Soong采用插件式的结构，使其易于扩展以满足不同的构建要求。

​	尽管Android.mk使用的make构建系统已经被soong逐渐取代了，但是依然可以在开发中使用它，下面将对Android.mk和Android.bp的规则进行介绍。

​	Android.mk文件采用makefile格式，由一系列的Target配置和Macro定义组成，在Android.mk中可以定义整个应用或组件的编译过程，包括Java代码、C/C++代码、资源文件。以下是Android.mk的常见写。

```
// 定义模块
module_name := mymodule
// 通常作为一个Android.mk文件中的第一行
// 就是把之前的所有的LOCAL_变量都清空，从而确保每个模块的变量之间互不干扰，避免变量混淆。
include $(CLEAR_VARS)

// 通常情况下，定义为“optional”的模块会在构建环境变量中被忽略，需要添加编译选项来编译它们。
// 通过向PRODUCT_PACKAGES中添加模块名称，我们可以确保这些模块能够被构建系统所识别，从而完成编译。
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE := $(module_name)

// 定义模块依赖项，例如依赖其他模块库
LOCAL_STATIC_LIBRARIES := lib1 lib2
LOCAL_SHARED_LIBRARIES := lib3 lib4

// 定义源文件
LOCAL_SRC_FILES := test.cpp

// 定义源文件的头文件
LOCAL_C_INCLUDES := $(LOCAL_PATH)/include

// 定义编译选项
LOCAL_CFLAGS := -Wall
LOCAL_CPPFLAGS := -Wall

// 定义静态库
include $(CLEAR_VARS)
LOCAL_MODULE := my_static_lib
LOCAL_SRC_FILES := test1.c test2.c
LOCAL_CFLAGS := -Wall
include $(BUILD_STATIC_LIBRARY)

// 定义动态库
include $(CLEAR_VARS)
LOCAL_MODULE := my_shared_lib
LOCAL_SRC_FILES := test.c
LOCAL_CFLAGS := -Wall
include $(BUILD_SHARED_LIBRARY)

// 定义可执行文件
include $(CLEAR_VARS)
LOCAL_MODULE := my_binary
LOCAL_SRC_FILES := main.c
LOCAL_CFLAGS := -Wall
include $(BUILD_EXECUTABLE)

// 定义资源文件
include $(CLEAR_VARS)
LOCAL_MODULE := my_resources
LOCAL_SRC_FILES := test.xml

// 表示将该预先构建的文件添加到系统构建目标列表中。
include $(BUILD_PREBUILT)
```

​	接下来看看一个Android.mk的示例文件

```
// 使用当前目录
LOCAL_PATH := $(call my-dir)
// 清除之前设置的变量和规则
include $(CLEAR_VARS)
// 模块名
LOCAL_MODULE := libxmlrpc++
// 该变量定义模块所依赖的操作系统
LOCAL_MODULE_HOST_OS := linux
// 允许使用 RTTI 特性
LOCAL_RTTI_FLAG := -frtti
// 指定 C++ 标志选项
LOCAL_CPPFLAGS := -Wall -Werror -fexceptions
// 指定该库的头文件搜索路径
LOCAL_EXPORT_C_INCLUDES := $(LOCAL_PATH)/src
// 指定要编译的源文件的列表
LOCAL_SRC_FILES := $(call \
     all-cpp-files-under,src)
// 该指令指示编译器生成动态链接库文件。如果要生成静态库文件，则可以使用 $(BUILD_STATIC_LIBRARY) 指令。
include $(BUILD_SHARED_LIBRARY)
```

​	`Android.bp`文件使用的是一种名为`Blueprint`的语言来表示模块和它们的依赖关系。`Blueprint` 是一种声明式语言，它描述了一个系统的构建规则和依赖关系，而无需描述如何构建代码本身。在`Android.bp`文件中，每个模块都表示为一个独立的蓝图，并且该蓝图包含有关模块的信息，例如名称、类型、源文件等。此外，蓝图还可以包含有关与该模块相关的依赖关系的信息，例如库、标头文件等。使用 `Android.bp`文件可以使Android模块的构建过程更加简单明了，并且易于实现自定义构建规则和自动化构建操作。同时，它还能提高编译效率，特别是在多核CPU系统上。下面是`Android.bp`文件的基本格式：

```
// Android.bp文件中的模块以模块类型开头，后跟一组 name: "value", 格式的属性
// 每个模块都必须具有 name 属性，并且相应值在所有 name 文件中必须是唯一的

//cc_binary指示需要构建的 C/C++ 二进制程序
cc_binary {
    name: "gzip",	// 二进制的名称
    srcs: ["src/test/minigzip.c"],		// 需要编译的源码
    shared_libs: ["libz"],		// 指定所需链接的共享库
    // 指定C++标准库的使用方式，"none" 表示不使用 C++ 标准库，因为模拟 C++ 标准库的所有垫子库可能在某些平台上都不可用。
    stl: "none",
}

// cc_binary指示需要构建的 C/C++ 静态库或者动态库
cc_library {
    ...
    srcs: ["generic.cpp"],
    // 可以指定不同平台使用的支持文件
    arch: {
        arm: {
            srcs: ["arm.cpp"],
        },
        x86: {
            srcs: ["x86.cpp"],
        },
    },
}

// cc_defaults是默认模块可用于在多个模块中重复使用相同的属性
cc_defaults {
    name: "gzip_defaults",
    shared_libs: ["libz"],
    stl: "none",
}
cc_binary {
    name: "gzip",
    defaults: ["gzip_defaults"],		// 使用上面的默认模块
    srcs: ["src/test/minigzip.c"],
}

// 定义一个Java库模块
java_library {
    name: "myjava",
    srcs: ["MyJava.java"],  // Java源代码文件列表
    libs: ["mylib"],  // 依赖的本地库列表
    static_libs: ["libz"], // 依赖的静态本地库列表
}

// 定义一个android模块
android_library {
    name: "myandroid",
    srcs: ["MyAndroid.java"],  // Java源代码文件列表
    libs: ["mylib"],  // 依赖的本地库列表
    static_libs: ["libz"],  // 依赖的静态本地库列表
    shared_libs: ["liblog"],  // 依赖的共享库列表
    manifest: "AndroidManifest.xml",  // AndroidManifest.xml路径
    resource_dirs: ["res"],  // 资源文件目录列表
}

//声明命名空间，可以让不同目录中的模块指定相同的名称，只要每个模块都在单独的命名空间中声明即可
soong_namespace {
    imports: ["path/to/otherNamespace1", "path/to/otherNamespace2"],
}

```

​	除了以上的几种模块定义外，可通过查看androidmk的源码查看还有哪些模块类型，找到文件`./build/soong/androidmk/androidmk/android.go`

```go
var moduleTypes = map[string]string{
	"BUILD_SHARED_LIBRARY":        "cc_library_shared",
	"BUILD_STATIC_LIBRARY":        "cc_library_static",
	"BUILD_HOST_SHARED_LIBRARY":   "cc_library_host_shared",
	"BUILD_HOST_STATIC_LIBRARY":   "cc_library_host_static",
	"BUILD_HEADER_LIBRARY":        "cc_library_headers",
	"BUILD_EXECUTABLE":            "cc_binary",
	"BUILD_HOST_EXECUTABLE":       "cc_binary_host",
	"BUILD_NATIVE_TEST":           "cc_test",
	"BUILD_HOST_NATIVE_TEST":      "cc_test_host",
	"BUILD_NATIVE_BENCHMARK":      "cc_benchmark",
	"BUILD_HOST_NATIVE_BENCHMARK": "cc_benchmark_host",

	"BUILD_JAVA_LIBRARY":             "java_library_installable", // will be rewritten to java_library by bpfix
	"BUILD_STATIC_JAVA_LIBRARY":      "java_library",
	"BUILD_HOST_JAVA_LIBRARY":        "java_library_host",
	"BUILD_HOST_DALVIK_JAVA_LIBRARY": "java_library_host_dalvik",
	"BUILD_PACKAGE":                  "android_app",
	"BUILD_RRO_PACKAGE":              "runtime_resource_overlay",

	"BUILD_CTS_EXECUTABLE":          "cc_binary",               // will be further massaged by bpfix depending on the output path
	"BUILD_CTS_SUPPORT_PACKAGE":     "cts_support_package",     // will be rewritten to android_test by bpfix
	"BUILD_CTS_PACKAGE":             "cts_package",             // will be rewritten to android_test by bpfix
	"BUILD_CTS_TARGET_JAVA_LIBRARY": "cts_target_java_library", // will be rewritten to java_library by bpfix
	"BUILD_CTS_HOST_JAVA_LIBRARY":   "cts_host_java_library",   // will be rewritten to java_library_host by bpfix
}
var prebuiltTypes = map[string]string{
	"SHARED_LIBRARIES": "cc_prebuilt_library_shared",
	"STATIC_LIBRARIES": "cc_prebuilt_library_static",
	"EXECUTABLES":      "cc_prebuilt_binary",
	"JAVA_LIBRARIES":   "java_import",
	"APPS":             "android_app_import",
	"ETC":              "prebuilt_etc",
}
```

​	androidmk是`soong`中提供的一个工具，因为基于`make`的构建系统已经逐渐被`soong`替代了，但是依然有很多人习惯使用`Android.mk`的规则来配置构建条件，在这种情况下可以选择写完Android.mk后，再使用androidmk工具将其转换为Android.bp文件。所有文件的相关代码中，可以看到很多是由一个map进行存放数据的，左边是Android.mk的规则，右边则是对应Android.bp中的新名字，在编写的过程中，如果对Android.bp不是很熟悉，可以借鉴转换工具的源码进行参考，或者直接使用工具进行转换。

​	下面讲述如何编译androidmk工具，并使用其进行转换。

```
source ./build/envsetup.sh

lunch aosp_blueline-userdebug

make androidmk

cd ../out/soong/host/linux-x86/bin

./androidmk ./Android.mk > ./Android.bp
```

​	最后使用工具将上一节中的Android.mk转换为Android.bp后的结果如下，能够看到对比起mk中的内容，看起来要更加简单清晰。

```
android_app_import {
    name: "SystemAppDemo",

    certificate: "platform",
    dex_preopt: {
        enabled: false,
    },
    apk: "SystemAppDemo.apk",

}
```

## 5.4 系统内置jar包

​	Android系统默认携带了许多jar包（Java Archive文件），这些jar包包含了许多与Android系统本身相关的类和库，以及用于开发应用程序的API。以下是Android系统默认携带的一些重要的jar包：

​	`android.jar` - 这是Android操作系统最重要且默认包含的jar包。它包含了Android开发中所有常规的API。

​	`junit.jar` - 这是执行测试的jar包，用于单元测试和UI测试。

​	`okhttp.jar` - 这是一个HTTP客户端和服务器，用于在Android应用程序中进行网络通信，支持HTTP/2、WebSocket和HTTP缓存等特性。

​	`picasso.jar` - 这是一个图片加载和显示库，可以用于自动处理异步加载、缓存和裁剪。

​	`retrofit.jar` - 这是一个RESTful API客户端库，支持类型安全的HTTP请求、多种HTTP操作和异步通信。

​	`annotations.jar` - 这是一个元注解库，用于在Android应用程序中生成或应用注解。

​	`commons-codec-1.4.jar` - 这是一个编解码器库，支持16种编码格式及Base64编码和解码。

​	`android-support-annotations.jar` - 这是一个支持library库的注释jar包，可以在Android应用程序中使用注释。

​	除此之外，Android系统中还包含了许多其他的jar包，如guava.jar、jackson-core.jar、okio.jar、conscrypt.jar等。这些都是 Android 库和框架的核心部分，它们提供了多种不同的扩展功能和支持，帮助开发者更快地构建高质量的 Android 应用程序。

​	通过修改Android源码的方式，同样可以让开发人员将自己经常使用的jar包也内置到系统中，又或者将定制的业务功能包装在jar包中，在调整时就仅需要修改jar包的代码，最后更新到系统中即可。如此可以节省臃肿的编译时间，还能更加便捷的管理业务代码。

​	内置jar包的方式是有多种的，下面将使用两种方式将一个自己编写的jar包集成到系统中。首先创建一个no Activity的Android项目，项目命名为MyJar，如下图所示。

![image-20230308211039320](.\images\create_no_activity.png)

​	接着简单的写两个测试函数。在最后内置成功后，将对这个函数进行调用测试是否内置成功。

```java
public class MyCommon {
    public String getMyJarVer(){
        return "v1.0";
    }
    public int add(int a,int b){
        return a+b;
    }
}
```

​	然后就可以编译这个项目。编译结束后得到`./build/output/debug/app-debug.apk`文件，需要内置的是一个JAR文件，所以接下来解压apk文件，java代码在解压结果的classes.dex文件中，应用程序编译过程中，如果生成的DEX 文件大小超过 65536 字节，则编译工具链将尝试在同一 APK 包中生成多个 classes.dex 文件以存储所有的字节码。为了方便内置，可以编译前在build.gradle中添加配置，声明不要生成多个DEX文件，相关配置如下。

```
plugins {
    id 'com.android.application'
}

android {
    compileSdk 33
    defaultConfig {
        applicationId "cn.mik.kframework"
        minSdk 29
        targetSdk 32
        versionCode 1
        versionName "1.0"
        multiDexEnabled false		// 禁止生成多个dex文件
        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }
    ...
}
```

​	经过前面的流程拿到的DEX 文件虽然都是存储着java指令，但是和JAR 文件是有一定区别的。他们的区别如下所示。

1. 目标平台不同：JAR 文件是为 Java 虚拟机（JVM）设计的，而 DEX 文件是为 Dalvik 虚拟机（DVM）和 ART（Android Run Time）设计的。
2. 字节码格式不同：JAR 文件包含 Java 编译器生成的字节码，而 DEX 文件包含经过转换和优化的字节码，以适应 Android 平台的内存限制和设备特性。
3. 加载速度不同：由于 Dalvik 虚拟机使用预先处理的 DEX 文件，因此加载速度更快，而 JVM 在运行 JAR 文件时需要实时编译字节码，因此加载速度较慢。
4. 版本兼容性不同：JAR 文件可以在不同版本的 JVM 上运行，但 DEX 文件只能在支持 DVM 或 ART 的 Android 设备上运行。

​	综上所述，所以DEX文件需要先转换为JAR，然后再将这个JAR文件拷贝到AOSP源码中进行内置。以下是具体的实现步骤。

```
// 进入编译输出结果目录
cd ./app/build/outputs/apk/debug/

// APK的本质就是一个压缩文件，直接解压apk文件即可
unzip app-debug.apk -d ./app-debug

// 将解压目录的DEX文件拷贝到当前目录
cp ./app-debug/classes.dex ./

// 通过dx工具将DEX转换为JAR
dx --dex --min-sdk-version=26 --output=./kjar.jar ./classes.dex

// 创建一个目录来存放需要内置的JAR文件
mkdir /root/android_src/aosp12/frameworks/native/myjar

// 将转换后的JAR文件放入AOSP源码目录中
cp ./myjar.jar /root/android_src/aosp12/frameworks/native/myjar/kjar.jar

```

​	最后就可以修改编译时的规则，将这个JAR文件拷贝到指定分区中。找到文件`build/target/product/base_system.mk`，在构建规则中添加如下配置，表示将源码路径下的文件拷贝到目标目录。

```
PRODUCT_COPY_FILES += \
      frameworks/native/myjar/kjar.jar:system/framework/kjar.jar \
```

​	`base_system.mk `定义了构建 Android 系统镜像时需要包含哪些模块和库，并指定了这些模块和库在系统镜像中的位置和顺序，以及它们之间的依赖关系。在build目录下的多个mk文件都能添加这个配置进行拷贝文件，并不是只能加在这个`base_system.mk`文件中，在不同的 mk 文件中定义的 PRODUCT_COPY_FILES 规则可能会相互覆盖，因此需要确保它们之间没有冲突，并且按照预期的顺序执行。通常情况下，建议将自己添加的所有的 PRODUCT_COPY_FILES 规则放在同一个文件中，以避免混乱和错误。

​	重新编译系统并刷入手机中，先来到刚刚指定的目录中查看kjar文件是否存在。

```
adb shell
cd /system/framework
ls -all |grep kjar

-rw-r--r--  1 root root  3705442 2023-03-08 21:55:46.000000000 +0800 kjar.jar
```

​	最后写一个普通的App来对kjar中的函数进行调用，有两种方式加载这个jar文件。DexClassLoader 和 PathClassLoader 是 Android 应用程序中常用的两种类加载器，它们之间的主要区别如下。

1. 加载路径不同：DexClassLoader 可以从任意路径中加载 .dex 文件，包括应用程序中的私有目录和外部存储器等位置；而 PathClassLoader 只能从预定义的系统路径中加载 .dex 文件，如 /system/framework、/system/app 等。
2. 加载方式不同：DexClassLoader 是通过指定 .dex 文件的路径和输出目录，将该文件加载到内存中的；而 PathClassLoader 则是通过指定 Classpath 路径来加载 .dex 文件，包括系统类库和应用程序类库等。
3. 安全性和隐私性不同：由于 DexClassLoader 可以加载任意路径中的 .dex 文件，因此可能存在潜在的安全风险和隐私问题，特别是对于多个应用程序之间共享代码的场景；而 PathClassLoader 则更加安全可靠，因为只能加载预定义的路径中的文件，并且具有较高的权限限制。

​	下面是两种加载方式对函数进行调用的实现例子。

```java
protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    	// 使用PathClassLoader加载jar文件
        String jarPath = "/system/framework/kjar.jar";
        ClassLoader systemClassLoader=ClassLoader.getSystemClassLoader();
        String javaPath= System.getProperty("java.library.path");
        PathClassLoader pathClassLoader=new PathClassLoader(jarPath,javaPath,systemClassLoader);
        Class<?> clazz1 = null;
        try {
            // 通过反射调用函数
            clazz1 = pathClassLoader.loadClass("cn.mik.myjar.MyCommon");
            Method method = clazz1.getDeclaredMethod("getMyJarVer");
            Object result = method.invoke(null);
            Log.i("MainActivity","getMyJarVer:"+result);

        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        } catch (InvocationTargetException e) {
            e.printStackTrace();
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        }
		// 使用DexClassLoader加载jar文件
        String dexPath = "/system/framework/kjar.jar";
        String dexOutputDir = getApplicationInfo().dataDir;
        ClassLoader classLoader = new DexClassLoader(dexPath, dexOutputDir, null,
                getClass().getClassLoader());

        Class<?> clazz2 = null;
        try {
            // 通过反射调用函数
            clazz2 = classLoader.loadClass("cn.mik.myjar.MyCommon");
            Method addMethod = clazz2.getDeclaredMethod("add", int.class,int.class);
            Object result = addMethod.invoke(null, 12,25);
            Log.i("MainActivity","getMyJarVer:"+result);
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        } catch (InvocationTargetException e) {
            e.printStackTrace();
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        }
    }
```

## 5.5 系统内置so动态库

​	上一小节介绍的内置方式非常简单，只需通过配置PRODUCT_COPY_FILES即可将指定文件从源码中复制到目标目录中。除了JAR文件外，其他文件也可以使用这种方式进行内置。为了内置so文件，将采用另一种方式。并且，第二种内置方式同样适用于JAR文件。

​	第二种方式是前文使用内置apk的方式，对构建规则进行细节的描述，在内置apk的同时，将指定的so动态库内置到`/system/lib`和`/system/lib64`目录中。并且同时将调用so动态库的JAR文件也内置在`/system/framework`目录中，在内置完成后，将调用JAR文件来访问so动态库，以及直接调用动态库进行测试。

​	首先准备一个测试项目，创建Native C++的项目。见下图。

![image-20230308232615347](.\images\create_so_project.png)

​	这个项目并不需要启动，所以直接删除MainActivity文件，重新创建一个类来加载动态库。并且修改cpp中对应的函数名称，相关修改如下。

```java
// 在这个类中进行加载动态库
public class NativeCommon {
    static {
        System.loadLibrary("mysodemo");
    }
    public native String stringFromJNI();
}

// native-lib.cpp文件中调整名称来对应新的类
extern "C" JNIEXPORT jstring JNICALL
Java_cn_mik_mysodemo_NativeCommon_stringFromJNI(
        JNIEnv* env,
        jobject /* this */) {
    std::string hello = "Hello from C++";
    return env->NewStringUTF(hello.c_str());
}

```

​	成功编译测试项目后的步骤和前文基本一致，唯一的区别就是在这里多拷贝了apk文件和so动态库文件，下面是具体流程。

```
// 进入编译输出结果目录
cd ./app/build/outputs/apk/debug/

// 解压apk文件
unzip app-debug.apk -d ./app-debug

// dex转换为jar
dx --dex --min-sdk-version=26 --output=./mysodemo.jar ./app-debug/classes.dex

// 创建目录存放要内置的文件
mkdir /root/android_src/aosp12_mikrom/frameworks/base/packages/apps/mysodemo

// 拷贝apk到需要内置的目录
cp ./app-debug.apk /root/android_src/aosp12/frameworks/base/packages/apps/mysodemo/mysodemo.apk

// 拷贝jar到需要内置的目录
cp ./mysodemo.jar /root/android_src/aosp12/frameworks/base/packages/apps/mysodemo/mysodemo.jar

// 拷贝64位动态库到需要内置的目录
cp ./app-debug/lib/arm64-v8a/libmysodemo.so /root/android_src/aosp12/frameworks/base/packages/apps/mysodemo/libmysodemo_arm64.so

// 拷贝32位动态库到需要内置的目录
cp ./app-debug/lib/armeabi-v7a/libmysodemo.so /root/android_src/aosp12/frameworks/base/packages/apps/mysodemo/libmysodemo_arm.so
```

​	需要内置的文件准备就绪后，创建一个构建规则Android.mk文件，将相关依赖文件都内置进去。

```
cd ./frameworks/base/packages/apps/mysodemo

touch Android.mk

gedit Android.mk

// 添加下面的内容到文件

LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)


LOCAL_SRC_FILES := mysodemo.apk
LOCAL_MODULE := mysodemo
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_TAGS := optional
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_MODULE_PATH := $(TARGET_OUT)/framework
// mysodemo.apk编译后将放在/system/framework/mysodemo/mysodemo.jar
LOCAL_INSTALLED_MODULE_STEM := mysodemo.jar
LOCAL_DEX_PREOPT := false
LOCAL_SHARED_LIBRARIES := liblog

include $(BUILD_PREBUILT)

#--------------------------------
include $(CLEAR_VARS)

LOCAL_MODULE := libmysodemo
LOCAL_SRC_FILES_arm := libmysodemo.so
LOCAL_SRC_FILES_arm64 := libmysodemo_arm64.so
LOCAL_MODULE_TARGET_ARCHS:= arm arm64
LOCAL_MULTILIB := both
LOCAL_MODULE_SUFFIX := .so
LOCAL_MODULE_CLASS := SHARED_LIBRARIES
LOCAL_MODULE_TAGS := optional
LOCAL_SHARED_LIBRARIES := liblog

include $(BUILD_PREBUILT)
```

​	规则文件可以看到和前文中的apk内置基本是一致的，前文是在`mainline_system.mk`中添加的配置将新增的模块加入构建，这次在`base_system.mk`文件中将模块加入，最后可以看到同样能内置成功。

```
PRODUCT_PACKAGES_DEBUG := \
    adb_keys \
    arping \
    dmuserd \
    gdbserver \
   	...
	mysodemo \
	libmysodemo \
```

​	编译并刷机后，检查`/system/lib/libmysodemo.so`是否存在，检查`/system/framework/mysodemo/mysodemo.jar`是否存在。

```
source ./build/envsetup.sh

lunch aosp_blueline-userdebug

make -j$(nproc --all)

adb reboot bootloader

flashflash all -w

// 等待刷机完成，开始检查内置结果
adb shell 
 
ls -all /system/lib |grep libmy

-rw-r--r--  1 root root  153056 2023-03-09 21:25:52.000000000 +0800 libmysodemo.so

cd /system/framework/mysodemo/
 
ls -all

-rw-r--r-- 1 root root 7937264 2023-03-09 20:58:40.000000000 +0800 mysodemo.jar

// 查看文件的描述，发现其实就是zip，是将刚刚的apk文件重新命名为jar的。
file mysodemo.jar

mysodemo.jar: Zip archive data
```

​	到这里内置流程就完成了，最后写一个测试程序来进行调用新方式内置的jar包。
```java
protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
		
		// 加载jar文件
        String jarPath = "/system/framework/mysodemo/mysodemo.jar";
        ClassLoader systemClassLoader=ClassLoader.getSystemClassLoader();
        String javaPath= System.getProperty("java.library.path");
        PathClassLoader pathClassLoader=new PathClassLoader(jarPath,javaPath,systemClassLoader);
        Class<?> clazz1 = null;
        try {
        	// 这里案例中没有使用静态函数，所以先反射初始化一个对象，再进行调用测试
            clazz1 = pathClassLoader.loadClass("com.example.mysodemo.NativeCommon");
            Constructor<?> clazzInitMethod= clazz1.getConstructor();
            Object obj=clazzInitMethod.newInstance();
            Method method = clazz1.getDeclaredMethod("stringFromJNI");
            Object result = method.invoke(obj);
            Log.i("MainActivity","stringFromJNI:"+result);
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        } catch (InvocationTargetException e) {
            e.printStackTrace();
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        } catch (InstantiationException e) {
            e.printStackTrace();
        }
    }
```

​	加载系统中的动态库进行调用我就不再详细写案例测试了，这个流程和正常加载系统中的动态库基本一致。只需要留意案例中的native函数的符号，加载动态库后，查找对应符号，最后调用即可。

## 5.6 修改su

​	

## 5.7 修改testkey



## 5.8 修改usb默认连接



