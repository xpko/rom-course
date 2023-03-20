# 第七章 脱壳

## 7.1 壳，加壳，脱壳

​	`Android`的`APK`文件实际上是一种压缩文件格式，它包含了应用程序的二进制代码、资源文件、清单文件等。在安装应用程序之前，系统会将`APK`文件解压缩并安装到设备上。在`APK`文件中，应用程序的二进制代码通常是以`DEX（Dalvik Executable）`格式存储的。`DEX`格式是一种针对移动设备优化的字节码格式，与`Java`虚拟机`（JVM）`的字节码格式有所不同。由于`DEX`格式采用了特殊的指令集和数据结构，使得反编译工具可以轻松地将其转换为可读性较高的`Java`代码。此外，许多反编译工具还可以通过反汇编和反混淆等技术来还原出源代码，因此为了防止应用程序的关键代码轻易被暴露，开发人员会采取一系列的手段来保护代码。

​	Android常规对代码保护的方案主要包括以下几种：

1. 混淆（Obfuscation）：通过重命名类、方法、变量等标识符来隐藏程序逻辑，使得反编译后的代码难以被理解和分析。
2. 压缩（Compression）：将应用程序的二进制代码压缩成较小的体积，防止恶意用户逆向工程和复制源代码。
3. 签名（Signing）：在应用程序发布前，使用数字证书对应用程序进行签名，确保其完整性和来源可信。
4. 加固（Hardening）：在应用程序内部添加额外的安全保护机制，如代码加密、反调试、反注入等，增强应用程序的抵御能力。
5. 动态加载（Dynamic Loading）：将敏感的代码和资源文件放置在远程服务器上，在运行时动态加载到本地设备，以防止被攻击者轻易访问和修改。

### 7.1.1 什么是加壳

​	加壳`（Packing）`就是一种应用程序加固手段之一。它将原始应用程序二进制代码嵌入到一个特殊的外壳中，通过修改程序入口和解密算法等方式，增加反调试、反逆向、防篡改等安全机制，提高应用程序的安全性。

​	加壳的目的是使应用程序难以被攻击者分析和修改，从而提高应用程序的抵御能力。但是，加壳也会带来一些负面影响，如增加应用程序的体积、降低应用程序运行效率、可能引入新的安全漏洞等。

​	常见的加壳壳包括：

1. `DexProtector`：一款商业化的加壳工具，支持`Android`和`iOS`平台，可以对`Java`代码和`NDK`库进行加固。其特点是支持多种代码混淆技术，同时还提供了反调试、防止`Hook`攻击、反模拟器等多种安全机制。
2. `Qihoo360`加固保：一款免费的加壳工具，支持`Android`和`iOS`平台，采用自己研发的加固壳技术，可以对`Java`代码和`C/C++`库进行加固，同时还提供了反调试、反逆向、防篡改等多种安全机制。
3. `Bangcle`：一款国内著名的加壳工具，支持`Android`和`iOS`平台，提供了多种加固壳方案，如`DexShell、SOShell、`加密资源等，同时还支持反调试、反注入等多种安全机制。
4. `APKProtect`：一款功能强大的加壳工具，支持`Android`平台，可以对`Java`代码和`Native`库进行加固，支持多种加固方式，如代码混淆、`Resource Encryption、Anti-debugging`等，同时还提供了反反编译、反调试等多种安全机制。

​	这些加壳工具都有不同的特点和适用场景，开发者可以根据实际需求选择合适的加壳壳进行加固。需要注意的是，加壳只是一种安全加固手段，不能取代其他常规的安全措施，并且可能带来一些负面影响，如体积增大、运行效率下降等。

### 7.1.3 如何脱壳

​	加壳的本质就是对DEX格式的java字节码进行保护避免被攻击者分析和修改，而脱壳就是通过分析壳的特征和原理，将被壳保护的java字节码还原出来，通常用于逆向分析、恶意代码分析等领域。

​	脱壳常用的几个步骤如下。

1. 静态分析：通过对样本进行静态分析，获取样本中的壳的特征，加密算法、解密函数等信息，为后续的动态分析做好准备。
2. 动态分析：在调试器或hook工具的帮助下，运行加密的程序，跟踪程序的执行流程，并尝试找到解密或解压的位置，获取加密或压缩前的原始数据。
3. 重构代码：通过分析反汇编代码，重新构建可读性高且易于理解的代码，以便更好地理解样本的行为。

​	在脱壳的过程中，会面临开发者为保护代码而添加的各类的防护措施，例如代码混淆、反调试、ROM检测、root检测、hook注入检测等加固手段，而这个博弈的过程就是一种攻防对抗。而ROM脱壳将从另外一个层面解决一部分对抗的问题。

## 7.2 壳的特征

​	早期的Android应用程序很容易被反编译和修改，因此一些开发者会使用简单的壳来保护自己的应用程序。这些壳主要是基于Java层的代码混淆和加密，以及Native层的简单加密。

​	但是单纯的混淆和加密很难保障代码的安全性，第一代壳，动态加载壳就诞生了，这时的思想主要还是将整个DEX进行加密保护，在运行期间才会解密还原DEX文件，再动态加载运行原文件。但是这样依赖Java的动态加载机制，非常容易被攻击，直接通过加载流程就能拿到被保护的数据，这种壳的特征非常明显，当反编译解析时，只能看到壳的代码，找不到任何Activity相关的处理，这种情况就是动态加载壳了。

​	随后第二代壳，指令抽取壳就出现了，对Java层的代码进行函数粒度的保护，第一代的思想是将整个DEX保护起来，而第二代的思想就是只需要保护关键的函数即可。将原始DEX中需要保护的函数内部的codeitem进行清空，将真正的函数内容加密保护存放在其他地方，只有当这个函数真正执行时，才通过解密函数将其还原填充回去，达到让其能正常执行的目的，有些指令抽取壳甚至会在函数执行完成后，重新将codeitem清空。否则执行过一次的函数指令将很容易被还原出来。这种壳的特征可以通过函数内容的特征来分辨，例如一些空的函数，查看smali指令发现内部有大量的nop空指令，这种情况就时指令抽取壳

​	随着攻防的对抗不断的升级，第二代壳也无法带来安全保障，第三代壳，指令转换壳诞生了。指令转换壳的思想和指令抽取是相同的，对具体的函数进行保护，但是在第二代壳的缺陷上进行了优化，由于指令抽取壳最终依然还是一个Java函数的调用，最终还是要将指令回填后进行执行的。不管是如何保护，只要在获取到执行过程中的`codeitem`，就能轻易的修复为真实的`DEX`文件。而指令转换壳则是将被保护的函数转换为native，将函数的指令集解析成中间码，中间码会被映射到自定义的虚拟机进行解析执行。这样就不会走Android提供的指令解析执行流程了。但是这样也会导致函数执行过慢，以及一些兼容问题，这类壳的特征也非常明显，就是native化一些函数，并且可能会包含大量密集的虚拟指令。

### 7.2.1 动态加载壳

​	动态加载壳是一种常见的代码保护技术，它通过在程序运行时动态加载壳来保护应用程序。下面是一般情况下动态加载壳的流程：

1. 壳程序和被保护的应用程序分开编译，壳程序中包含有解密、加载、映射被保护程序等功能代码，并将被保护程序加密。
2. 当启动被保护的程序时，先运行壳程序。
3. 壳程序首先会进行自身的初始化，例如获取壳程序自身路径、解密被加密的被保护程序等操作。
4. 然后，壳程序会将被保护程序从加密状态中解密出来。
5. 接着，壳程序会在内存中为被保护程序申请一块连续的内存区域，将被保护程序的代码和数据映射到该内存区域中。
6. 壳程序会根据被保护程序的程序入口点开始执行被保护程序的代码。
7. 被保护程序运行时的系统调用和DLL库的调用等操作，都会由壳程序处理并返回结果给被保护程序。同时，壳程序可能会进行一些额外的安全检查，例如防止调试、防止反汇编、防止破解等操作。

​	接下来我们看一个简单的动态加载壳的实现。首先准备一个需要被保护的apk，这里直接使用前文中测试动态加载系统内置jar包的APP作为样例，代码如下。

```java
package cn.mik.myservicedemo;

import androidx.appcompat.app.AppCompatActivity;

import android.app.Application;
import android.os.Bundle;
import android.os.IBinder;
import android.os.IMikRomManager;
import android.os.RemoteException;
import android.util.Log;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

import dalvik.system.PathClassLoader;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Class localClass = null;
        try {
            localClass = Class.forName("android.os.ServiceManager");
            Method getServiceMethod = localClass.getMethod("getService", new Class[] {String.class});
            if(getServiceMethod != null) {
                Object objResult = getServiceMethod.invoke(localClass, new Object[]{"mikrom"});
                if (objResult != null) {
                    IBinder binder = (IBinder) objResult;
                    IMikRomManager iMikRom = IMikRomManager.Stub.asInterface(binder);
                    String msg= iMikRom.hello();
                    Log.i("MainActivity", "msg: " + msg);
                }
            }
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        } catch (InvocationTargetException e) {
            e.printStackTrace();
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        } catch (RemoteException e) {
            e.printStackTrace();
        }
    }
}
```

​	TODO 动态加载壳的流程



​	最后使用压缩包打开apk文件，将加壳处理好的`classes.dex`替换apk中的原文件。然后开始重新签名这个apk，首先生成一个签名证书，命令如下。

```
keytool -genkeypair -alias myalias -keyalg RSA -keysize 2048 -validity 9125 -keystore mykeystore.keystore
```

​	输入口令以及各项信息后，得到一个证书文件`mykeystore.keystore`，然后使用该证书对刚刚处理好的apk文件进行签名。

```
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore mykeystore.keystore  app-debug.apk myalias
```

​	签名后尝试安装该apk，结果发现报错如下。

```
adb install app-debug.apk

// 安装失败
adb: failed to install app-debug.apk: Failure [-124: Failed parse during installPackageLI: Targeting R+ (version 30 and above) requires the resources.arsc of installed APKs to be stored uncompressed and aligned on a 4-byte boundary]
```

​	这个错误提示表示 APK 文件未正确压缩对齐。在 Android 11（API 级别 30）及以上版本中，要求 APK 文件必须按照一定的规则进行压缩和对齐，以确保应用程序的安全性和稳定性。可以使用 zipalign 工具对 APK 文件进行对齐操作。

```
zipalign -v 4 app-debug.apk app-debug-over.apk
```

​	再次尝试安装apk后，发现变成了另外一个错误。

```
adb install ./app-debug-over.apk

adb: failed to install ./app-debug-over.apk: Failure [INSTALL_PARSE_FAILED_NO_CERTIFICATES: Scanning Failed.: No signature found in package of version 2 or newer for package cn.mik.myservicedemo]
```

​	这是因为当`targetSdkVersion`版本号，只要大于30时，需要使用v2进行签名，签名方式如下。

```
apksigner sign --ks mykeystore.keystore  app-debug-over.apk
```

​	重新再安装apk，又换成了一个新错误。

```
adb install ./app-debug-over.apk

Exception occurred while executing 'install-incremental':
java.lang.IllegalArgumentException: Incremental installation not allowed.
        at com.android.server.pm.PackageInstallerSession.<init>(PackageInstallerSession.java:1082)
        at com.android.server.pm.PackageInstallerService.createSessionInternal(PackageInstallerService.java:787)
        at com.android.server.pm.PackageInstallerService.createSession(PackageInstallerService.java:519)
        at com.android.server.pm.PackageManagerShellCommand.doCreateSession(PackageManagerShellCommand.java:3143)
        at com.android.server.pm.PackageManagerShellCommand.doRunInstall(PackageManagerShellCommand.java:1341)
        at com.android.server.pm.PackageManagerShellCommand.runIncrementalInstall(PackageManagerShellCommand.java:1299)
        at com.android.server.pm.PackageManagerShellCommand.onCommand(PackageManagerShellCommand.java:197)
        at com.android.modules.utils.BasicShellCommandHandler.exec(BasicShellCommandHandler.java:97)
        at android.os.ShellCommand.exec(ShellCommand.java:38)
        at com.android.server.pm.PackageManagerService.onShellCommand(PackageManagerService.java:24612)
        at android.os.Binder.shellCommand(Binder.java:950)
        at android.os.Binder.onTransact(Binder.java:834)
        at android.content.pm.IPackageManager$Stub.onTransact(IPackageManager.java:4818)
        at com.android.server.pm.PackageManagerService.onTransact(PackageManagerService.java:8506)
        at android.os.Binder.execTransactInternal(Binder.java:1184)
        at android.os.Binder.execTransact(Binder.java:1143)
```

​	这是因为旧版本不支持流式安装，所以需要禁用增量安装，增量安装是一种优化技术，它只安装已更改的文件和资源，而不是重新安装整个应用程序。使用 `--no-incremental` 选项可以确保在安装应用程序时，所有文件都被完全重新安装，使用下面的命令安装apk。

```
adb install -r  --no-incremental app-debug-over.apk
```

​	

### 7.2.2 指令抽取壳

​	指令抽取壳通过将原始程序中的指令提取出来，并放置到一个独立的内存区域中，来保护原始程序。

### 7.2.3 指令转换壳



## 7.3 脱壳的原理

### 7.3.1 双亲委派机制

### 7.3.2 类的加载流程

### 7.3.3 函数调用流程

### 7.3.4 初代壳实现

### 7.3.5 如何脱壳



## 7.4 简单脱壳实现



## 7.5 自动化脱壳



