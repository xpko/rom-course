# 第九章 Android Hook框架

​	在第五章的系统内置中，简单介绍了如何将开发的模块内置到系统中，并注入到应用执行。而内置并注入一个第三方开发的工具，和前文中简单的内置注入过程并没有太大区别。其关键过程就是加载其依赖的动态库，然后再加载器核心业务组件。在这一章中，将以几个典型的`Hook`框架作为例子，将其内置在系统中。

## 9.1 Xposed

​	`Xposed`是一个`Android Hook`框架，它可以实现在不修改`APK`文件的情况下更改系统行为和应用程序的行为，通过开发模块，就能对目标进程的`Java`函数调用进行`Hook`拦截，但是需要安装在`Root`的`Android`设备上，才能使用该框架中的模块生效。根据该框架的原理衍生出了很多类似的框架，例如`Edxposed`、`Lsposed`、`VirtualXposed`等等。

​	在`Xposed`的架构中，主要包含了三个部分：`Xposed Installer`、`Xposed Bridge`和`Xposed Module`。其中，`Xposed Installer`是用户安装和管理`Xposed`模块的应用程序；`Xposed Bridge`是实现系统和模块之间相互通信的核心组件；`Xposed Module`则是开发者使用`Xposed API`编写的模块，用于实现对目标进程的函数调用的拦截和修改。

​	在运行时，`Xposed Installer`会通过`Android`的`PackageManager`查询已安装的应用程序，并将相关信息传递给`Xposed Bridge`。`Xposed Bridge`会在运行过程中监听应用程序的启动事件，当目标应用程序启动时，`Xposed Bridge`会将`Xposed Module`加载到目标进程中，并且与`Xposed Module`建立通信管道，以便进行后续的函数调用拦截和修改操作。

​	`	Xposed Module`通过实现`IXposedHookLoadPackage`接口，来完成对应用程序的启动事件的监听和模块的加载。一旦模块加载成功，在`IXposedHookLoadPackage`回调函数中，我们就可以使用`Xposed API`提供的函数来实现对目标进程的函数调用的拦截和修改。这些函数包括`XposedHelpers.findAndHookMethod()`和`XposedHelpers.callMethod()`等，它们能够帮助我们定位到目标进程中的函数，并对其进行拦截和修改。

​	需要注意的是，`Xposed`框架只能在`Root`的`Android`设备上使用，因为它需要对系统进行修改才能实现函数调用的拦截和修改。在使用`Xposed`框架时，需要特别小心，不要随意地修改系统行为和应用程序行为，以免引起意外的后果。

​	这一章将详细解析`Xposed`的原理，学习`Xposed`是如何利用`Android`的运行机制来实现对函数的`Hook`机制。

## 9.2 Xposed实现原理

​	在开始分析`Xposed`源码前，首先回顾一下第三章中，讲解`Android`启动流程时，最后根据`AOSP`的源码得到的以下结论。

 	1. `zygote`进程启动是通过`app_process`执行程序启动的
 	2. 由`init`进程解析`init.rc`时启动的第一个`zygote`
 	3. 在第一个`zygote`进程中创建的`ZygoteServer`，并开始监听消息。
 	4. `zygote`是在`ZygoteServer`这个服务中收到消息后，再去`fork`出新进程的
 	5. 所有进程均来自于`zygote`进程的`fork`而来，所以`zygote`是进程的始祖

​	从上面的结论中可以看到，`app_process`执行程序在其中占据着非常重要的位置，而`Xposed`的核心原理，就是将`app_process`替换为`Xposed`修改过的`app_process`，这样就会让所有进程都会通过它的业务逻辑处理。首先找到项目`https://github.com/rovo89/Xposed`。查看文件`Android.mk`。

```
ifeq (1,$(strip $(shell expr $(PLATFORM_SDK_VERSION) \>= 21)))
  LOCAL_SRC_FILES := app_main2.cpp
  LOCAL_MULTILIB := both
  LOCAL_MODULE_STEM_32 := app_process32_xposed
  LOCAL_MODULE_STEM_64 := app_process64_xposed
else
  LOCAL_SRC_FILES := app_main.cpp
  LOCAL_MODULE_STEM := app_process_xposed
endif
```

​	可以看到这里是用来编译一个`Xposed`专用的`app_process`。当`Android`版本大于21（Android 5）时，使用`app_main2.cpp`来编译。接下来查看入口函数的实现。

```cpp
#define XPOSED_CLASS_DOTS_TOOLS  "de.robv.android.xposed.XposedBridge$ToolEntryPoint"

int main(int argc, char* const argv[])
{
    ...
    // 检测Xposed的参数
    if (xposed::handleOptions(argc, argv)) {
        return 0;
    }
	...
    if (zygote) {
        // Xposed 框架的初始化，为后续的 Hook 操作和代码注入操作提供支持。
        isXposedLoaded = xposed::initialize(true, startSystemServer, NULL, argc, argv);
        runtimeStart(runtime, isXposedLoaded ? XPOSED_CLASS_DOTS_ZYGOTE : "com.android.internal.os.ZygoteInit", args, zygote);
    } else if (className) {
        isXposedLoaded = xposed::initialize(false, false, className, argc, argv);
        runtimeStart(runtime, isXposedLoaded ? XPOSED_CLASS_DOTS_TOOLS : "com.android.internal.os.RuntimeInit", args, zygote);
    } else {
        fprintf(stderr, "Error: no class name or --zygote supplied.\n");
        app_usage();
        LOG_ALWAYS_FATAL("app_process: no class name or --zygote supplied.");
        return 10;
    }
}
```

​	在这个特殊的`app_process`中，首先是对启动进程的参数进行检查，然后初始化`Xposed`框架，如果初始化成功了，则使用`Xposed`的入口`de.robv.android.xposed.XposedBridge$ToolEntryPoint`来替换系统原本的`com.android.internal.os.ZygoteInit`入口。

​	`xposed::initialize`是一个非常关键的函数，它完成了 `Xposed `框架的初始化工作。查看实现代码如下。

```c++
bool initialize(bool zygote, bool startSystemServer, const char* className, int argc, char* const argv[]) {
#if !defined(XPOSED_ENABLE_FOR_TOOLS)
    ...
	// 将参数保存
    xposed->zygote = zygote;
    xposed->startSystemServer = startSystemServer;
    xposed->startClassName = className;
    xposed->xposedVersionInt = xposedVersionInt;

#if XPOSED_WITH_SELINUX
    xposed->isSELinuxEnabled   = is_selinux_enabled() == 1;
    xposed->isSELinuxEnforcing = xposed->isSELinuxEnabled && security_getenforce() == 1;
#else
    xposed->isSELinuxEnabled   = false;
    xposed->isSELinuxEnforcing = false;
#endif  // XPOSED_WITH_SELINUX

    ...

    if (startSystemServer) {
        if (!determineXposedInstallerUidGid() || !xposed::service::startAll()) {
            return false;
        }
        // 启动Xposed框架的日志记录，将xposed框架日志写入logcat中。
        xposed::logcat::start();
// SELinux启用的情况
#if XPOSED_WITH_SELINUX
    } else if (xposed->isSELinuxEnabled) {
        // 用于启动Xposed框架的 membased 服务，该服务实现hooking功能
        if (!xposed::service::startMembased()) {
            return false;
        }
#endif  // XPOSED_WITH_SELINUX
    }
// SELinux启用的情况
#if XPOSED_WITH_SELINUX
    // 限制内存继承，以确保Xposed服务只能被当前进程和其子进程使用，而不能被其他进程使用
    if (xposed->isSELinuxEnabled) {
        xposed::service::membased::restrictMemoryInheritance();
    }
#endif  // XPOSED_WITH_SELINUX

	// 是否禁用xposed
    if (zygote && !isSafemodeDisabled() && detectSafemodeTrigger(shouldSkipSafemodeDelay()))
        disableXposed();

    if (isDisabled() || (!zygote && shouldIgnoreCommand(argc, argv)))
        return false;
	// 将Xposed JAR文件添加到应用程序或服务的类路径中
    return addJarToClasspath();
}

```

​	在启用`SELinux`的情况下，`Xposed`需要使用 `membased` 服务来实现`hooking`功能。但是，为了确保安全性，`Xposed`需要限制将`Xposed`服务复制到其他进程中的能力。通过调用 `restrictMemoryInheritance` 函数，`Xposed`会防止任何进程继承`Zygote`进程的内存，这将确保`Xposed`服务只能被当前进程和其子进程使用。

​	初始化完成时，将一个`JAR`文件添加到了`CLASSPATH`环境变量中，查看`addJarToClasspath`的实现。

```java
#define XPOSED_JAR               "/system/framework/XposedBridge.jar"

bool addJarToClasspath() {
    ALOGI("-----------------");
    if (access(XPOSED_JAR, R_OK) == 0) {
        if (!addPathToEnv("CLASSPATH", XPOSED_JAR))
            return false;

        ALOGI("Added Xposed (%s) to CLASSPATH", XPOSED_JAR);
        return true;
    } else {
        ALOGE("ERROR: Could not access Xposed jar '%s'", XPOSED_JAR);
        return false;
    }
}
```

​	初始化成功后，接着继续追踪替换后的入口点`de.robv.android.xposed.XposedBridge$ToolEntryPoint`，该入口点的实现是在`XposedBridge.jar`中。查看项目`https://github.com/rovo89/XposedBridge`，文件`XposedBridge.java`的实现代码如下。

```java
package de.robv.android.xposed;

public final class XposedBridge {
	protected static final class ToolEntryPoint {
		protected static void main(String[] args) {
			isZygote = false;
			XposedBridge.main(args);
		}
	}

    protected static void main(String[] args) {
		// 初始化Xposed框架和模块
		try {
			if (!hadInitErrors()) {
				initXResources();
				SELinuxHelper.initOnce();
				SELinuxHelper.initForProcess(null);

				runtime = getRuntime();
				XPOSED_BRIDGE_VERSION = getXposedVersion();

				if (isZygote) {
                    // hook Android 资源系统
					XposedInit.hookResources();
                    // 初始化 Xposed 框架的 zygote 进程，创建用于跨进程通信的 Binder 对象，并注册相关的 Service。这样就能够实现跨进程的 Hook 功能
					XposedInit.initForZygote();
				}
				// 加载Xposed模块
				XposedInit.loadModules();
			} else {
				Log.e(TAG, "Not initializing Xposed because of previous errors");
			}
		} catch (Throwable t) {
			Log.e(TAG, "Errors during Xposed initialization", t);
			disableHooks = true;
		}

		// 调用原始应用的入口
		if (isZygote) {
			ZygoteInit.main(args);
		} else {
			RuntimeInit.main(args);
		}
	}
}
```

​	到这里，`Xposed`的启动流程基本完成了，`Xposed`首先替换原始的`app_process`，让每个进程启动时使用自己的`app_process_xposed`，在执行`zygote`入口函数前，先初始化了自身的环境，然后每个进程后是先进入的`XposedBridge`，在完成自身的逻辑后，才调用`zygote`的入口函数，进入应用正常启动流程。这也意味着，对于系统定制者来说，所谓的`Root`权限才能使用`Xposed`并不是必须的。最后看看`loadModules`的实现，是如何加载`Xposed`模块的。

```java
private static final String INSTANT_RUN_CLASS = "com.android.tools.fd.runtime.BootstrapApplication";

// 加载模块列表
static void loadModules() throws IOException {

		final String filename = BASE_DIR + "conf/modules.list";
		BaseService service = SELinuxHelper.getAppDataFileService();
		if (!service.checkFileExists(filename)) {
			Log.e(TAG, "Cannot load any modules because " + filename + " was not found");
			return;
		}
		// 拿到顶端的ClassLoader
		ClassLoader topClassLoader = XposedBridge.BOOTCLASSLOADER;
		ClassLoader parent;
		while ((parent = topClassLoader.getParent()) != null) {
			topClassLoader = parent;
		}
		// 读取模块列表
		InputStream stream = service.getFileInputStream(filename);
		BufferedReader apks = new BufferedReader(new InputStreamReader(stream));
		String apk;
    	// 使用顶端ClassLoader加载每个模块
		while ((apk = apks.readLine()) != null) {
			loadModule(apk, topClassLoader);
		}
		apks.close();
	}


private static void loadModule(String apk, ClassLoader topClassLoader) {
		Log.i(TAG, "Loading modules from " + apk);

		if (!new File(apk).exists()) {
			Log.e(TAG, "  File does not exist");
			return;
		}

		DexFile dexFile;
		try {
			dexFile = new DexFile(apk);
		} catch (IOException e) {
			Log.e(TAG, "  Cannot load module", e);
			return;
		}
		// 如果加载成功，说明该应用启用了 Instant Run
		if (dexFile.loadClass(INSTANT_RUN_CLASS, topClassLoader) != null) {
			Log.e(TAG, "  Cannot load module, please disable \"Instant Run\" in Android Studio.");
			closeSilently(dexFile);
			return;
		}
		// 尝试在目标模块中加载XposedBridge类，可以获取到说明已经成功注入XposedBridge
		if (dexFile.loadClass(XposedBridge.class.getName(), topClassLoader) != null) {
			Log.e(TAG, "  Cannot load module:");
			Log.e(TAG, "  The Xposed API classes are compiled into the module's APK.");
			Log.e(TAG, "  This may cause strange issues and must be fixed by the module developer.");
			Log.e(TAG, "  For details, see: http://api.xposed.info/using.html");
			closeSilently(dexFile);
			return;
		}

		closeSilently(dexFile);
		// 由于模块实际都是apk，而apk本质是压缩包，所以使用Zip来处理文件
		ZipFile zipFile = null;
		InputStream is;
		try {
			zipFile = new ZipFile(apk);
            // 解压出xposed_init文件，这里存放着模块启动的入口
			ZipEntry zipEntry = zipFile.getEntry("assets/xposed_init");
			if (zipEntry == null) {
				Log.e(TAG, "  assets/xposed_init not found in the APK");
				closeSilently(zipFile);
				return;
			}
			is = zipFile.getInputStream(zipEntry);
		} catch (IOException e) {
			Log.e(TAG, "  Cannot read assets/xposed_init in the APK", e);
			closeSilently(zipFile);
			return;
		}
		// 动态加载模块
		ClassLoader mcl = new PathClassLoader(apk, XposedBridge.BOOTCLASSLOADER);
		BufferedReader moduleClassesReader = new BufferedReader(new InputStreamReader(is));
		try {
			String moduleClassName;
			while ((moduleClassName = moduleClassesReader.readLine()) != null) {
				moduleClassName = moduleClassName.trim();
				if (moduleClassName.isEmpty() || moduleClassName.startsWith("#"))
					continue;

				try {
                    // 加载模块的入口类
					Log.i(TAG, "  Loading class " + moduleClassName);
					Class<?> moduleClass = mcl.loadClass(moduleClassName);
					// 检查该类是否有实现接口
					if (!IXposedMod.class.isAssignableFrom(moduleClass)) {
						Log.e(TAG, "    This class doesn't implement any sub-interface of IXposedMod, skipping it");
						continue;
					} else if (disableResources && IXposedHookInitPackageResources.class.isAssignableFrom(moduleClass)) {
						Log.e(TAG, "    This class requires resource-related hooks (which are disabled), skipping it.");
						continue;
					}
					// 使用该类初始化一个对象
					final Object moduleInstance = moduleClass.newInstance();
					if (XposedBridge.isZygote) {
                        // 不同的实现接口有各自对应的处理，这里是Zygote模块初始化时使用的模块
						if (moduleInstance instanceof IXposedHookZygoteInit) {
							IXposedHookZygoteInit.StartupParam param = new IXposedHookZygoteInit.StartupParam();
							param.modulePath = apk;
							param.startsSystemServer = startsSystemServer;
							((IXposedHookZygoteInit) moduleInstance).initZygote(param);
						}
						// 普通应用的模块接口
						if (moduleInstance instanceof IXposedHookLoadPackage)
                            // 调用了模块中的实现。
							XposedBridge.hookLoadPackage(new IXposedHookLoadPackage.Wrapper((IXposedHookLoadPackage) moduleInstance));

						if (moduleInstance instanceof IXposedHookInitPackageResources)
							XposedBridge.hookInitPackageResources(new IXposedHookInitPackageResources.Wrapper((IXposedHookInitPackageResources) moduleInstance));
					} else {
						if (moduleInstance instanceof IXposedHookCmdInit) {
							IXposedHookCmdInit.StartupParam param = new IXposedHookCmdInit.StartupParam();
							param.modulePath = apk;
							param.startClassName = startClassName;
							((IXposedHookCmdInit) moduleInstance).initCmdApp(param);
						}
					}
				} catch (Throwable t) {
					Log.e(TAG, "    Failed to load class " + moduleClassName, t);
				}
			}
		} catch (IOException e) {
			Log.e(TAG, "  Failed to load module from " + apk, e);
		} finally {
			closeSilently(is);
			closeSilently(zipFile);
		}
	}
```

​	分析完加载模块的实现后，这时就明白模块开发时定义的入口是如何被调用的，以及被调用的时机在哪里。理解其中的原理后，同样可以自己进行修改，在其他的时机来选择注入。用自己的方式来定义模块。

## 9.3 常见的hook框架

​	根据`Xposed`的源码分析不难看出其关键在于`XposedBridge.jar`的注入，然后由`XposedBridge.jar`实现对函数`Hook`的关键逻辑，因为`Xposed`框架提供了非常方便和灵活的`API`，使得开发者可以快速地编写自己的`Hook`模块并且可以兼容大多数`Android`系统版本和设备。所以很多`Hook`框架都会兼容支持`Xposed`框架。

​	`SandHook `是作用在`Android ART`虚拟机上的` Java `层 `Hook `框架，作用于进程内是不需要` Root `的，支持`Android 4.4 - Android 10`，该框架兼容`Xposed Api`调用。

​	除了支持常规的`Java`层`Hook`外，`Sandhook`还支持对`Native`层的函数进行`Hook`。它通过使用系统提供的符号表来获取函数地址，并将函数地址转换为可执行代码，从而实现`Native Hook`。

​	`Sandhook`本身是没有注入功能的，开发完模块功能后，需要自行重打包，或者使用其他工具将模块注入。从开发`AOSP`的角度，可以参考前文内置`JAR`包的做法，直接将`Sandhook`内置到`AOSP`系统中，并实现对任意进程自动注入。

​	`pine`是一个在虚拟机层面、以`Java`方法为粒度的运行时动态`Hook`框架，它可以拦截本进程内几乎所有的`java`方法调用。支持`Android 4.4 - Android 12`。同样该框架也兼容`Xposed Api`调用。

​	`Pine`支持两种方案，一种是替换入口，即修改`ArtMethod`的`entrypoint`；另一种类似于`native`的`inline hook`，即覆盖掉目标方法的代码开始处的一段代码，用于弥补`Android 8.0`以下版本入口替换很有可能不生效的问题。

​	`Dobby`是一个基于`Android NDK`开发的`Native Hook`框架。它可以在`Android`应用程序中注入自定义代码段，从而实现函数替换、跳转、插桩等操作。`Dobby`主要使用了动态链接库和指令重写技术，通过Hook目标进程中的函数来达到修改目的。

​	相比`Java`层的`Hook`框架，`Native Hook`有一些优势。首先，`Native Hook`可以直接操作目标进程的内存空间，更加灵活；其次，`Native Hook`可以通过指令重写技术来控制执行流程，效果更加精准；最后，`Native Hook`避免了`Java`层`Hook`可能引起的兼容性问题，适用范围更广。

## 9.4 集成pine

​	其实集成各种`Hook`框架的方式基本大同小异，主要就是将核心`JAR`文件或者依赖的`so`动态库内置到系统中，在进程启动阶段将其注入，注入时机越早，能支持`Hook`的范围自然是越广，在注入后，再对模块进行动态加载即可。在前几章中，有详细的讲解如何内置`JAR`文件和`so`动态库，以及如何动态加载调用，在这一小节中，将会结合前文中学习到的，完整把`pine hook`框架内置到`AOSP12`中。

​	首先需要知道`pine`的模块需要依赖哪些动态库，按照`pine`模块的开发规则，`Android Studio`新建项目，在`build.gradle`下添加`pine`的引用如下。

```
dependencies {
    ...
    implementation 'top.canyie.pine:core:0.2.6'
    ...
}
```

 	然后添加一个测试`hook` 的目标类和函数。

```java
public class Demo {
    public static String ceshi(){
        Log.i("Demo","ceshi");
        return "1123";
    }
}
```

​	接着在`onCreate`中添加`hook`代码如下。

```java
	@Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        PineConfig.debug = true; // 是否debug，true会输出较详细log
        PineConfig.debuggable = BuildConfig.DEBUG; // 该应用是否可调试

        try {
            Pine.hook(Demo.class.getDeclaredMethod("ceshi"), new MethodHook() {
                @Override public void beforeCall(Pine.CallFrame callFrame) {
                    Log.i(TAG, "Before " + callFrame.thisObject + " ceshi()");
                }

                @Override public void afterCall(Pine.CallFrame callFrame) {
                    Log.i(TAG, "After " + callFrame.thisObject + " ceshi()");
                    callFrame.setResult("aasd");
                }
            });
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        }
        Log.i(TAG,Demo.ceshi());
    }
```

​	可以看到`hook`代码执行后，再触发函数的调用，运行该应用后，能看到在本进程内成功`hook`。说明该模块正常运行，将这个测试模块编译出来的`apk`文件解压，查看`lib`目录，发现`hook`框架添加后，新增了动态库`libpine.so`。接下来需要将该动态库内置到系统中。

​	在目录`frameworks/base/packages/apps`下新建一个目录`mypine`，然后在该目录中新建文件`Android.mk`，将`pine`的依赖动态库`libpine.so`的，`armv7`以及`arm64`两个版本拷贝到该目录，并加入配置，配置具体内容如下。

```
//内容如下
LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE := libpine
LOCAL_SRC_FILES_arm := libpine.so
LOCAL_SRC_FILES_arm64 := libpine_arm64.so
LOCAL_MODULE_TARGET_ARCHS:= arm arm64
LOCAL_MULTILIB := both
LOCAL_MODULE_SUFFIX := .so
LOCAL_MODULE_CLASS := SHARED_LIBRARIES
LOCAL_MODULE_TAGS := optional
LOCAL_SHARED_LIBRARIES := liblog

include $(BUILD_PREBUILT)
```

​	然后在`build/make/target/product/mainline_system.mk`文件中，将配置好的模块加入`PRODUCT_PACKAGES`中，具体实现如下。

```
PRODUCT_PACKAGES += \
			libpine \
```

​	依赖的动态库成功内置到了系统中，只需要在应用启动的过程中，将开发的模块动态加载进去即可，模块的开发可以直接参考`Xposed`实现的思路，在`Xposed`中定义了接口`IXposedHookLoadPackage`，然后开发模块时，实现该接口中的入口函数`handleLoadPackage`，在进程启动中，动态加载模块后，就调用实现了该接口的函数即可触发模块的入口函数。

​	参考上面的流程，开发一个要注入的模块，首先创建一个接口文件如下，包名随意，但是要注意的是，模块中的接口包名，必须和`AOSP`系统中添加的接口包名一致。

```java
package java.krom;

public interface IHook {
    void onStart(Object app);
}
```

​	然后创建一个类，实现该接口，并在入口函数中实现需要`hook`内容。

```java
package cn.mik.mymodule

public class Module implements IHook {
    public static Method GetClsMethod(Class cls,String methodName){
        Method methlist[] = cls.getDeclaredMethods();
        Method mGoal=null;
        for (int i = 0; i < methlist.length; i++) {
            Method m = methlist[i];
            if(m.getName().equals(methodName)){
                mGoal=m;
                break;
            }
        }
        return mGoal;
    }

    @Override
    public void onStart(Object app) {
        Log.i("dengrui", "Module  is running...");
        Application application=(Application)app;
        ClassLoader classLoader=application.getClassLoader();
        try {
            Class cls=Class.forName("cn.mik.pinedemo.Demo",false,classLoader);
            if(cls==null){
                Log.i(TAG, "not found Demo");
                return;
            }
            Method method=GetClsMethod(cls,"ceshi");
            if(method!=null){
                Log.i(TAG, "success get method");
                Pine.hook(method, new MethodHook() {
                    @Override public void beforeCall(Pine.CallFrame callFrame) {
                        Toast.makeText(application, "成功注入模块",Toast.LENGTH_LONG).show();
                    }
                    @Override public void afterCall(Pine.CallFrame callFrame) {
                    }
                });
            }

        } catch (ClassNotFoundException e) {
            e.printStackTrace();
            Log.i(TAG, "err:"+e.getMessage());
        }
    }
}
```

​	在该模块中依然是对前面的例子进行`Hook`，而前文是直接在本进程中进行`Hook`操作，现在则是将前面例子中，`onCreate`的`hook`代码删除，并且去掉`pine`框架的相关引用。在该进程启动时，在`AOSP`源码中将其注入。这里的注入时机选择`handleBindApplication`中，创建`Application`后进行处理。下面是`AOSP`的相关修改。

```java
private void loadModule(Application app){
    String apkPath="/data/data/cn.mik.pinedemo/mymodule.apk";
    String apkClass="cn.mik.mymodule.Module"
    File f=new File(apkPath);
    if(!f.exists()){
        return;
    }
    ClassLoader mcl = new PathClassLoader(apkPath, app.getClassLoader());
    IHook moduleInstance = null;
    try {
        Log.i(TAG, "Loading class " + apkClass);
        Class<?> moduleClass = mcl.loadClass(apkClass);
        moduleInstance = (IHook) moduleClass.newInstance();
    } catch (IllegalAccessException | InstantiationException | ClassNotFoundException e) {
        Log.e(TAG, "", e);
    } finally {
    }
    if (moduleInstance != null) {
        moduleInstance.onStart(app);
    }
}

private void handleBindApplication(AppBindData data) {
	...
    app = data.info.makeApplication(data.restrictedBackupMode, null);
    // Propagate autofill compat state
    app.setAutofillOptions(data.autofillOptions);
    // Propagate Content Capture options
    app.setContentCaptureOptions(data.contentCaptureOptions);
    sendMessage(H.SET_CONTENT_CAPTURE_OPTIONS_CALLBACK, data.appInfo.packageName);
    mInitialApplication = app;
    // 非系统进程则注入jar包
    int flags = mBoundApplication == null ? 0 : mBoundApplication.appInfo.flags;
    if(flags>0&&((flags&ApplicationInfo.FLAG_SYSTEM)!=1)){
    	loadModule(app)
    }
}
```

​	注入代码添加完成后，需要在`AOSP`中相同包名目录下也添加`IHook.java`的接口文件。该例子中接口文件存放在`openjdk`，也可以选择直接放`android.app`包名或任意包名下，只需要和模块中的一致即可。

​	在该例子中，为了简化过程，模块路径以及模块实现接口的类名固定写在代码中，所以在刷入手机测试时，需要手动将该模块上传到指定路径，并且保证在该目录有权限，才能进行动态加载。

​	在实际运用常见，可以选择参考`Xposed`的做法，写在某个资源文件中，然后解压出单个文件读取内容获取到。而`apk` 的路径，可以选择从配置文件获取，如果配置路径下的没有权限，可以由代码实现将模块拷贝到当前进程的私有目录下进行动态加载。也可以选择调整`selinux`规则，为指定目录添加普通进程的访问权限。

## 9.5 集成dobby

​	集成方式与`pine`相同，首先开发一个使用`dobby`的样例，然后将其中的依赖动态库集成到系统中，最后在进程启动的过程中，将其加载即可。由于`dobby`是对`native`函数进行`hook`的，所以`Android Studio`创建一个`native c++`的项目，然后使用`git`将`dobby`项目拉取下来。项目地址：`https://github.com/jmpews/Dobby`。然后修改项目中`cpp`目录下的`CMakeLists.txt`文件，将`dobby`加入其中。修改如下。

```cmake
cmake_minimum_required(VERSION 3.18.1)
// 设置dobby源码的目录
set(DobbyHome ~/git_src/Dobby)
enable_language(C ASM)

include_directories(
        dlfc
        utils
)

project("mydobby")

add_library(
        mydobby
        SHARED
        native-lib.cpp
        utils/parse.cpp)

find_library(
        log-lib
        log)

target_link_libraries(
        mydobby
        dobby
        ${log-lib})

# 使用设置的路径,引入Dobby
include_directories(
        ${DobbyHome}/include
        ${DobbyHome}/source
        ${DobbyHome}/builtin-plugin
        ${DobbyHome}/builtin-plugin/AndroidRestriction
        ${DobbyHome}/builtin-plugin/SymbolResolver
        ${DobbyHome}/external/logging
)

macro(SET_OPTION option value)
    set(${option} ${value} CACHE INTERNAL "" FORCE)
endmacro()

SET_OPTION(DOBBY_DEBUG ON)
SET_OPTION(DOBBY_GENERATE_SHARED ON)
SET_OPTION(Plugin.LinkerLoadCallback OFF)

add_subdirectory(~/git_src/Dobby dobby.build)

if(${CMAKE_ANDROID_ARCH_ABI} STREQUAL "arm64-v8a")
    add_definitions(-DCORE_SO_NAME="${LIBRARY_NAME}")
elseif(${CMAKE_ANDROID_ARCH_ABI} STREQUAL "armeabi-v7a")
    add_definitions(-DCORE_SO_NAME="${LIBRARY_NAME}")
endif()
```

​	将`dobby`的源码引入后，就可以在项目中使用`dobby`进行`hook`处理了。修改`native-lib.cpp`

文件，添加测试的`hook`代码，内容如下。

```c++
#include <jni.h>
#include <string>
#include <android/log.h>
#include "dobby.h"

#define LOG_TAG "native-lib"

#define ALOGD(...) __android_log_print(ANDROID_LOG_DEBUG  , LOG_TAG, __VA_ARGS__)

int (*source_openat)(int fd, const char *path, int oflag, int mode) = nullptr;

// 替换后的新函数
int MyOpenAt(int fd, const char *pathname, int flags, int mode) {
    ALOGD("mik MyOpenAt  pathname :%s",pathname);
    if (strcmp(pathname, "/sbin/su") == 0 || strcmp(pathname, "/system/bin/su") == 0) {
        pathname = "/system/xbin/Mysu";
    }
    // 执行原来的openat函数
    return source_openat(fd, pathname, flags, mode);
}

void HookOpenAt() {
    // 找到函数对应的地址
    void *__openat =
            DobbySymbolResolver("libc.so", "__openat");

    if (__openat == nullptr) {
        ALOGD("__openat null ");
        return;
    }
    ALOGD("拿到 __openat 地址 ");
    //dobby hook 函数
    if (DobbyHook((void *) __openat,
                  (dobby_dummy_func_t) MyOpenAt,
                  (dobby_dummy_func_t*) &source_openat) == RT_SUCCESS) {
        ALOGD("DobbyHook __openat sucess");
    }
}

jint JNICALL JNI_OnLoad(JavaVM *vm, void *reserved) {

    ALOGD("Hello JNI_OnLoad 开始加载");
    JNIEnv *env = nullptr;
    //改变openat 指定函数 函数地址 替换成自己的
    HookOpenAt();

    if (vm->GetEnv((void **) &env, JNI_VERSION_1_6) == JNI_OK) {
        return JNI_VERSION_1_6;
    }
    return 0;
}
```

​	样例应用准备完毕，将该样例编译并运行后，就能成功看到对`openat`进行`hook`的输出如下。

```
...
D  mik MyOpenAt  pathname :/data/vendor/gpu/esx_config_cn.mik.devchangemodule.txt
D  mik MyOpenAt  pathname :/data/vendor/gpu/esx_config.txt
D  mik MyOpenAt  pathname :/data/misc/gpu/esx_config_cn.mik.devchangemodule.txt
D  mik MyOpenAt  pathname :/data/misc/gpu/esx_config.txt
D  mik MyOpenAt  pathname :/data/vendor/gpu/esx_config_cn.mik.devchangemodule.txt
D  mik MyOpenAt  pathname :/data/vendor/gpu/esx_config.txt
D  mik MyOpenAt  pathname :/data/misc/gpu/esx_config_cn.mik.devchangemodule.txt
D  mik MyOpenAt  pathname :/data/misc/gpu/esx_config.txt
...
```

​	接下来将该样例应用编译的`apk`文件进行解压，在`lib`目录中找到依赖的动态库，分别是`libdobby.so`和`libmydobby.so`，其中前者是`hook`框架的核心库，后者是刚刚对`openat`进行`hook`的业务代码。只需要在任何进程启动前，按顺序将依赖的核心动态库，和业务代码加载，即可完成集成的工作，`libdobby.so`可以选择集成到系统中，也可以选择跟业务代码动态库一起放同一个目录进行加载。下面看实现加载的代码。

```java

private static void loadSoModule(String soName){
    String soPath="";
    if(System.getProperty("os.arch").indexOf("64") >= 0) {
        soPath = String.format("/data/data/cn.mik.dobbydemo/%s", soName);
    }else{
        soPath = String.format("/data/data/cn.mik.dobbydemo/%s", soName);
    }
    File file = new File(soPath);
    if (file.exists()){
        Log.e("mikrom", "load so "+soPath);
        System.load(tmpPath);
        Log.e("mikrom", "load over so "+soPath);
    }else{
        Log.e("mikrom", "load so "+soPath+" not exist");
    }
}

private void handleBindApplication(AppBindData data) {
	...
    app = data.info.makeApplication(data.restrictedBackupMode, null);
    // Propagate autofill compat state
    app.setAutofillOptions(data.autofillOptions);
    // Propagate Content Capture options
    app.setContentCaptureOptions(data.contentCaptureOptions);
    sendMessage(H.SET_CONTENT_CAPTURE_OPTIONS_CALLBACK, data.appInfo.packageName);
    mInitialApplication = app;
    // 非系统进程则注入jar包
    int flags = mBoundApplication == null ? 0 : mBoundApplication.appInfo.flags;
    if(flags>0&&((flags&ApplicationInfo.FLAG_SYSTEM)!=1)){
    	loadSoModule("libdobby.so");
        loadSoModule("libmydobby.so");
    }
}
```

​	这只是简单的演示加载样例，安装目标应用后，还需要把两个动态库拷贝到对应目录中，在实际运用场景，尽量不要将动态库的路径，以及要加载的库名称固定写在源码中，最好通过配置的方式，来管理这些需要加载的参数，加载动态库需要目录有执行权限，所以要将文件放在当前应用的私有目录中。完成修改后，随意安装任何应用，打开后，都会被`hook openat`函数。
