# 第五章 系统内置功能 #

## 5.1 什么是系统内置

​	系统内置简单的说就是将镜像刷入手机后默认就在手机中能够使用的功能，例如Android内置的Launcher、Phone、Email、Setting等系统App都是属于内置的。同样开发者也可以制作一个App将其内置在系统中并且作为系统应用，又或者在工作中，每次手机刷机后需要安装的一些环境，也可以内置在系统中，这样每次刷机后都不必重新配置环境。

​	在前几章的学习中，介绍了Android是如何实现启动系统以及打开应用程序的执行流程，并且小牛试刀修改替换了系统的资源文件。将AOSP看做是一个大型的项目，本章需要学习的是如何对这个项目二次开发，在它的基础上扩展一些让我们使用起来更加便利的功能内置在系统中，由于Android系统非常庞大，每次修改后都需要进行编译再刷入手机。而这些功能的业务相关的代码尽量不要直接写在AOSP源码中，避免浪费大量的时间在等待中。

## 5.2 系统内置App

​	首先找到Android系统自身内置app的所在目录`packages/apps`，在系统中内置的大多数App源码都是在这里，打开任意一个系统内App的目录进去后，能看到这里的结构和我们正常开发的Android App没有什么区别。需要内置的App代码并不是一定要放在这个目录下，可以选择将编译后的apk内置进去，这样就能使用Android Studio单独开发这个App。

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

​	接下来开发一个简单的案例，功能是在`/data/system`目录中创建一个文件并且写入内容。这个目录是只有system身份权限的进程才能访问。最后将这个App应用内置到系统中，编译后刷入手机，验证是否成功写入数据。以下是案例的实现代码。

```java

public class MainActivity extends AppCompatActivity {

    public String writeTxtToFile(String strContent, String filePath, String fileName) {
        String strFilePath = filePath+fileName;
        try {
            File file = new File(strFilePath);
            if (!file.exists()) {
                file.getParentFile().mkdirs();
                file.createNewFile();
            }
            RandomAccessFile raf = new RandomAccessFile(file, "rwd");
            raf.setLength(0);
            long writePosition = raf.getFilePointer();
            raf.seek(writePosition);
            raf.write(strContent.getBytes());
            raf.close();
            //
        } catch (Exception e) {
            Log.e("MainActivity", "Error on write File:" + e);
            return e.getMessage();
        }
        return "";
    }
    TextView txtContext;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        txtContext=findViewById(R.id.txtContext);
        String errMsg= writeTxtToFile("测试内置系统App","/data/system/","demo.txt");
        if(errMsg.isEmpty()){
            txtContext.setText("写入成功");
        }else{
            txtContext.setText("写入失败,"+errMsg);
        }
    }
}
```

​	内置到手机前，先直接将app安装测试，写入文件时提示错误`Error on write File:java.io.IOException: Permission denied`。

​	`android:shareUserId` 是 AndroidManifest.xml 文件中的一个属性，用于应用程序之间的共享用户 ID。共用用户 ID 可以让应用程序之间更好的进行相互访问和操作。当一个应用程序定义了`android:shareUserId`属性时，另一个相互信任的应用程序可以设置相同的 `android:shareUserId` 属性，从而实现应用程序的数据共享和交互。

​	在安装和运行应用程序之前，设备会将具有相同共享用户 ID 的应用程序视为同一用户，因此可以访问对方的数据，比如 SharedPreferences 和文件等。如果应用程序没有设置 `android:shareUserId` 属性，则其默认值是该应用程序的包名。以下是AndroidManifest.xml中的配置。

```
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:sharedUserId="android.uid.system"
    package="cn.mik.systemappdemo">
    ...
</manifest>
```

​	需要注意的是，如果两个应用程序带有相同的 `android:shareUserId` 属性，则它们必须由同一个签名密钥签名，这是为了保证安全性。如果你直接设置了这个属性后，再使用常规的方式安装就提示下面的错误

```
Installation did not succeed.
The application could not be installed: INSTALL_FAILED_SHARED_USER_INCOMPATIBLE

List of apks:
[0] 'C:\Users\king\AndroidStudioProjects\SystemAppDemo\app\build\intermediates\apk\debug\app-debug.apk'
Installation failed due to: 'INSTALL_FAILED_SHARED_USER_INCOMPATIBLE: Package cn.mik.systemappdemo tried to change user null'
```

​	测试用例准备就绪后就可以来到源码的目录`packages/apps`，创建一个新的目录`SystemAppDemo`，将刚刚编译的样例App也改名为SystemAppDemo放入这个目录，在这个新目录中添加一个编译的配置文件Android.mk。

~~~
cd ./packages/apps/
mkdir SystemAppDemo && cd SystemAppDemo
touch Android.mk
gedit Android.mk

//添加下面的内容
#当前路径
LOCAL_PATH := $(call my-dir)
#清除环境变量
include $(CLEAR_VARS)

#模块名称
LOCAL_MODULE := SystemAppDemo
#编译的模块文件
LOCAL_SRC_FILES := $(LOCAL_MODULE).apk
#定义编译完成之后的类型
LOCAL_MODULE_CLASS := APPS
#定义编译完成之后模块的后缀
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
#哪个版本进行编译，optional表示全版本编译。可选字段： user 、 eng 、 tests
LOCAL_MODULE_TAGS := optional
#不进行odex优化
LOCAL_DEX_PREOPT := false
#签名，platform表示系统签名，PRESIGNED表示保持原签名
LOCAL_CERTIFICATE := platform
include $(BUILD_PREBUILT)
~~~

​	在 Android 系统编译过程中，`PRODUCT_PACKAGES` 是一个重要的变量，它定义了系统所需构建的软件包列表。`PRODUCT_PACKAGES` 变量定义的是本次构建需要编译打包的软件包，包括一些基础系统组件和应用程序模块，例如音频服务模块、媒体播放库、输入法、设置应用程序等。	

​	在构建规则文件`./build/make/target/product/handheld_system.mk`的末尾添加配置。

~~~
PRODUCT_PACKAGES += SystemAppDemo \
~~~

​	到这里就修改完毕了，最后重新编译系统，将其刷入手机中。

```
source ./build/envsetup.sh

lunch aosp_blueline-userdebug

make -j$(nproc --all)

adb reboot bootloader

flashflash all -w

```

​	刷机完成后，在桌面就能看到刚刚内置的App了，这时再打开App时。不会提示没有权限了。来到`/data/system`目录验证创建的这个文件已经存在并且写入内容。



​	

​	
