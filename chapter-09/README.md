# 第九章 xposed

## 9.1 什么是Xposed

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
					// 对该类进行初始化
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

## 9.3 支持Xposed的hook框架



## 9.4 集成Xposed



## 9.5 集成pine



## 9.6 集成dobby





