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

### 7.1.2 如何脱壳

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

## 7.3 脱壳的原理

​	了解Android中类的加载机制和函数执行的调用流程是理解如何脱壳的基础。在Android系统中，应用程序是在`Dalvik`或者`ART`虚拟机上运行的。当应用启动时，Android系统会根据应用程序包中的`AndroidManifest.xml`文件来确定应用程序中哪些组件需要被启动，并且在启动过程中加载应用程序所需的类。

​	Android中的类加载器遵循双亲委派模型，即每个类加载器在尝试加载一个类之前，都会先委托其父类加载器去加载该类。如果父类加载器无法完成加载任务，则子类加载器才会尝试自行加载。这个模型保证了不同的类只会被加载一次，同时也保护了核心`Java API`不被恶意代码篡改。

​	在Android应用程序中，每个类都会被分配到一个特定的`DEX`文件（即`Dalvik Executable`）中。`DEX`文件中包含了所有该类的方法和属性的字节码。当一个应用程序启动时，它的DEX文件会被加载到内存中，并由虚拟机负责解释执行其中的代码。

​	在函数执行的调用流程中，当一个函数被调用时，虚拟机会将当前线程的状态保存下来，并跳转到被调用函数的入口地址开始执行该函数。在函数执行期间，虚拟机会对函数中的指令进行解释执行，并维护函数执行过程中所需的各种数据结构，例如栈帧等。在函数执行完毕后，虚拟机会将结果返回给调用方，并恢复之前保存的线程状态。

​	深入学习Android的类加载机制和函数执行的调用流程，可以更好地理解应用程序的运行机制和寻找脱壳点。

### 7.3.1 双亲委派机制

​	`Android`中的类通常是在`DEX`文件中保存的，而`ClassLoader`则是用来加载这些`DEX`文件的。在Android中，每个应用程序包`（APK）`都包含一个或多个`DEX`文件，这些`DEX`文件中包含了应用程序的所有类信息。当一个类需要被使用时，`ClassLoader`就会从相应的`DEX`文件中加载该类，并将其转换成可执行的`Java`类。因此，`ClassLoader`和`DEX`密切相关，`ClassLoader`是`DEX`文件的载体和管理者。下面是在`AOSP12`中各类的`ClassLoader`。

1. `BootClassLoader`：位于 `ClassLoader `层次结构中的最顶层。负责加载系统级别的类，如` Java` 核心库和一些基础库。
2. `PathClassLoader`：从应用程序的` APK` 文件中加载类和资源。`PathClassLoader `继承自` BaseDexClassLoader `类，它能够加载已经被优化的 `Dex` 文件和未经过优化的 `Dex` 文件。`PathClassLoader` 主要用于加载已经打包在 `APK `文件中的代码和资源。
3. `DexClassLoader`：从` .dex` 或` .odex` 文件中加载类。`DexClassLoader `继承自` BaseDexClassLoader `类，它支持动态加载 `Dex `文件，并且可以在运行时进行优化操作。`DexClassLoader `主要用于加载未安装的 `APK` 文件中的代码。
4. `InMemoryDexClassLoader`：用于从内存中加载已经存在于内存中的` dex `文件。它继承自 `BaseDexClassLoader`，并且可以处理多个` dex `文件。`InMemoryDexClassLoader `可以在运行时动态加载 `dex` 文件，并且不需要将文件保存到磁盘上，从而提高应用程序的性能。`InMemoryDexClassLoader` 主要可以用于自定义类加载器场景下。
5. `BaseDexClassLoader`：`DexClassLoader`、`InMemoryDexClassLoader` 和 `PathClassLoader` 的基类，封装了加载 `dex` 文件的基本逻辑，包括创建` DexPathList` 对象、打开 `dex `文件、查找类等操作。`BaseDexClassLoader `实现了双亲委派模型，即在自身无法加载类时，会委派给父类加载器进行查找。`BaseDexClassLoader` 还支持多个 `dex `文件的加载，并且可以在运行时进行优化操作。

​	类加载器采用了双亲委派机制`（Parent Delegation Model）`，这是一种经典的`Java`类加载机制。

​	双亲委派机制是指当一个类加载器收到请求去加载一个类时，它并不会自己去加载，而是把这个任务委托给父类加载器去完成。如果父类加载器还存在父类加载器，这个请求就会向上递归，直到达到最顶层的`BootClassLoader`为止。也就是说，最先调用加载的`ClassLoader`是最顶层的，最后尝试加载的是当前的`ClassLoader`。

​	采用双亲委派机制可以有效地避免类的重复加载，并保证核心`API`的安全性。具体表现为：

- 在类加载时，首先从当前加载器的缓存中查找是否已经加载了该类，如果已经加载，则直接返回；
- 如果没有在缓存中找到该类，则将加载任务委派给父类加载器去完成；
- 父类加载器如果也没有找到该类，则将会递归向上委派，直到`BootClassLoader`；
- `BootClassLoader`无法代理加载的类，则会让子类加载器自行加载。

​	明白了双亲委派机制后，了解到继承关系对于ClassLoader是非常重要的，下图是它们之间的继承关系。

​	TODO 帮我补一个继承关系的图



### 7.3.2 类的加载流程

​	在`Android`中，`ClassLoader`类是双亲委派机制的主要实现者。该类提供了`findClass`和`loadClass`方法，其中`findClass`是`ClassLoader`的抽象方法，需要由子类实现。接下来将跟踪源码实现，详细了解`ClassLoader`是如何进行类加载流程的。

​	在前文中曾经介绍过如何使用`DexClassLoader`加载一个类，并调用其中的函数，下面是当时的加载样例代码。

```java
protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    
        String dexPath = "/system/framework/kjar.jar";
        String dexOutputDir = getApplicationInfo().dataDir;
        ClassLoader classLoader = new DexClassLoader(dexPath, dexOutputDir, null,
                getClass().getClassLoader());

        Class<?> clazz2 = null;
        try {
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

​	`ClassLoader `加载类时，`loadClass` 和` findClass`都可以完成对类的加载工作，它们在加载类时有着不同的作用和执行流程。

​	首先看看`loadClass`的特征，它的方法签名如下。

````java
protected Class<?> loadClass( final String class_name, final boolean resolve ) throws ClassNotFoundException;
````

​	其中`name` 参数表示要加载的类的全名；`resolve` 参数表示是否需要在加载完成后进行链接操作。如果 `resolve` 参数为` true`，则会尝试在加载完成后对该类进行链接操作，包括验证、准备和解析等步骤。如果 `resolve` 参数为` false`，则不会进行链接操作。

​	在执行` loadClass `方法时，`ClassLoader `会先检查自身是否已经加载过该类，如果已经加载过，则直接返回该类的` Class` 对象。如果没有加载过，则将任务委托给父类加载器进行处理，如果父类加载器无法加载该类，则再次调用自身的` findClass` 方法进行加载。如果` findClass` 方法仍然无法找到该类，则抛出 `ClassNotFoundException` 异常。

​	接下来再了解下`findClass` 方法，它 是 `BaseClassLoader `类中定义的一个抽象方法，用于在特定的数据源（如文件、内存等）中查找指定名称的类，并返回对应的` Class` 对象。下面是方法签名。

```java
protected abstract Class<?> findClass(String name) throws ClassNotFoundException;
```

​	与` loadClass` 不同，`findClass` 方法并不会先委派给父类加载器进行处理，而是直接在当前 `ClassLoader `中进行查找。如果能够找到指定的类，则通过 `defineClass `方法将其转换成 Class 对象，并返回该对象；否则，抛出 `ClassNotFoundException `异常。

​	明白了两者的区别后，接下来开始跟踪源码，了解在AOSP具体是如何加载类的。首先找到`DexClassLoader`中`loadClass`的实现代码。

```java
public class DexClassLoader extends BaseDexClassLoader {
    public DexClassLoader(String dexPath, String optimizedDirectory,
            String librarySearchPath, ClassLoader parent) {
        super(dexPath, null, librarySearchPath, parent);
    }
}
```

​	发现内部并没有任何代码，说明该实现来自于父类中，接着来查看父类`BaseDexClassLoader`

```java
public class BaseDexClassLoader extends ClassLoader {
    public BaseDexClassLoader(String dexPath, File optimizedDirectory, String librarySearchPath, ClassLoader parent) {
        ...
    }
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        ...
    }

    protected URL findResource(String name) {
        ...
    }

    protected Enumeration<URL> findResources(String name) {
        ...
    }

    public String findLibrary(String name) {
        ...
    }

    protected synchronized Package getPackage(String name) {
        ...
    }

    public String toString() {
        ...
    }
}

```

​	同样没有找到`loadClass`的实现，继续看它的父类`ClassLoader`的实现。

```java
public abstract class ClassLoader {
    ...
    
    // 调用了另外一个重载，resolve参数不传的情况默认为false
	public Class<?> loadClass(String name) throws ClassNotFoundException {
        return loadClass(name, false);
    }
    
    protected Class<?> loadClass(String name, boolean resolve)
        throws ClassNotFoundException
    {
            // 尝试在已经加载过的里面查找
            Class<?> c = findLoadedClass(name);
            if (c == null) {
                try {
                    // 有父类的情况，就让父类来加载
                    if (parent != null) {
                        c = parent.loadClass(name, false);
                    } else {
                        // 到达父类顶端后，则使用这个函数查找，通常来查找引导类和扩展类
                        c = findBootstrapClassOrNull(name);
                    }
                } catch (ClassNotFoundException e) {
                    // ClassNotFoundException thrown if class not found
                    // from the non-null parent class loader
                }

                if (c == null) {
                    // 父类没有找到的情况，再通过findClass查找
                    c = findClass(name);
                }
            }
            return c;
    }
    ...
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        throw new ClassNotFoundException(name);
    }
}
```

​	通过这里的代码，能够很清晰的看到前文中`ClassLoader`的双亲委派机制，接着继续跟踪`findClass`分析当前`ClassLoader`是如何加载类的，由于`ClassLoader`是一个抽象类，而`findClass`在该类中并未实现具体代码，所以该方法是在子类中实现，上面在`BaseDexClassLoader`的类中，就已经看到的`findClass`的函数，下面是具体实现。

```java
public class BaseDexClassLoader extends ClassLoader {
    ...
    private final DexPathList pathList;    
    ...
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        // 首先检查当前ClassLoader是否有共享库，如果有则遍历每个共享库的ClassLoader去尝试加载该类
        if (sharedLibraryLoaders != null) {
            for (ClassLoader loader : sharedLibraryLoaders) {
                try {
                    return loader.loadClass(name);
                } catch (ClassNotFoundException ignored) {
                }
            }
        }
        List<Throwable> suppressedExceptions = new ArrayList<Throwable>();
        // 当前ClassLoader操作的dex文件中查找该类
        Class c = pathList.findClass(name, suppressedExceptions);
        if (c == null) {
            ClassNotFoundException cnfe = new ClassNotFoundException(
                    "Didn't find class \"" + name + "\" on path: " + pathList);
            for (Throwable t : suppressedExceptions) {
                cnfe.addSuppressed(t);
            }
            throw cnfe;
        }
        return c;
    }
	...
}

```

​	`pathList`是一个`DexPathList`对象，表示当前`ClassLoader`所操作的一组`dex`文件的路径列表。`findClass()`方法通过调用`DexPathList.findClass()`方法来查找指定名称的类。继续跟进查看。

```java
public final class DexPathList {
    ...
    private Element[] dexElements;
	...
    public Class<?> findClass(String name, List<Throwable> suppressed) {
        for (Element element : dexElements) {
            Class<?> clazz = element.findClass(name, definingContext, suppressed);
            if (clazz != null) {
                return clazz;
            }
        }

        if (dexElementsSuppressedExceptions != null) {
            suppressed.addAll(Arrays.asList(dexElementsSuppressedExceptions));
        }
        return null;
    }    
    ...
}
```

​	`dexElements`的数组存放着所有已经加载的`dex`文件中的类信息。具体来说，每个`dex`文件都被解析为一个`DexFile`对象，而`dexElements`数组中的每个元素实际上就是一个`Element`对象，代表了一个`dex`文件和其中包含的类信息。这些`Element`对象按照优先级顺序排列，以便`ClassLoader`可以根据它们的顺序来查找类定义。继续查看`Element`的`findClass`方法实现。

```java
static class Element {
		...
        // 管理着一个dex文件
        private final DexFile dexFile;
    
        ...
        private String getDexPath() {
            if (path != null) {
                return path.isDirectory() ? null : path.getAbsolutePath();
            } else if (dexFile != null) {
                // DexFile.getName() returns the path of the dex file.
                return dexFile.getName();
            }
            return null;
        }

        @Override
        public String toString() {
            if (dexFile == null) {
              return (pathIsDirectory ? "directory \"" : "zip file \"") + path + "\"";
            } else if (path == null) {
              return "dex file \"" + dexFile + "\"";
            } else {
              return "zip file \"" + path + "\"";
            }
        }
    	
        public Class<?> findClass(String name, ClassLoader definingContext,
                List<Throwable> suppressed) {
            return dexFile != null ? dexFile.loadClassBinaryName(name, definingContext, suppressed)
                    : null;
        }

        ...
    }
```

​	可以看到这里实际就是管理一个对应的`DexFile`对象，该对象关联着一个对应的`dex`文件，到这里通过调用`DexFile`对象的`loadClassBinaryName`去加载这个类，继续跟踪它的实现。

```java
public final class DexFile {
	...
    public Class loadClassBinaryName(String name, ClassLoader loader, List<Throwable> suppressed) {
        return defineClass(name, loader, mCookie, this, suppressed);
    }    
    ...
        
    private static Class defineClass(String name, ClassLoader loader, Object cookie,
                                     DexFile dexFile, List<Throwable> suppressed) {
        Class result = null;
        try {
            result = defineClassNative(name, loader, cookie, dexFile);
        } catch (NoClassDefFoundError e) {
            if (suppressed != null) {
                suppressed.add(e);
            }
        } catch (ClassNotFoundException e) {
            if (suppressed != null) {
                suppressed.add(e);
            }
        }
        return result;
    }
    ...
    private static native Class defineClassNative(String name, ClassLoader loader, Object cookie,
                                                  DexFile dexFile)
            throws ClassNotFoundException, NoClassDefFoundError;
}
```

​	这里看到经过几层调用后，进入了`native`实现了，根据AOSP中`native`注册的原理，直接搜索`DexFile_defineClassNative`找到对应的实现代码如下。

```java
static jclass DexFile_defineClassNative(JNIEnv* env,
                                        jclass,
                                        jstring javaName,
                                        jobject javaLoader,
                                        jobject cookie,
                                        jobject dexFile) {
  std::vector<const DexFile*> dex_files;
  const OatFile* oat_file;
  // cookie转换成一组c++中的DexFile对象以及OatFile
  if (!ConvertJavaArrayToDexFiles(env, cookie, /*out*/ dex_files, /*out*/ oat_file)) {
    VLOG(class_linker) << "Failed to find dex_file";
    DCHECK(env->ExceptionCheck());
    return nullptr;
  }
  ...
  // 将类名转换为c++的string存放在了descriptor中
  // 这里会将java中的类描述符转换为c++使用的类描述符，例如类中的.转换为\
  const std::string descriptor(DotToDescriptor(class_name.c_str()));
  const size_t hash(ComputeModifiedUtf8Hash(descriptor.c_str()));
  for (auto& dex_file : dex_files) {
    // 根据类描述符找到对应的类
    const dex::ClassDef* dex_class_def =
        OatDexFile::FindClassDef(*dex_file, descriptor.c_str(), hash);
    if (dex_class_def != nullptr) {
      ScopedObjectAccess soa(env);
      ClassLinker* class_linker = Runtime::Current()->GetClassLinker();
      ...
      // 使用类加载器和 DEX 文件定义一个新的 Java 类，并返回一个描述该类的 Class 对象指针
      ObjPtr<mirror::Class> result = class_linker->DefineClass(soa.Self(),
                                                               descriptor.c_str(),
                                                               hash,
                                                               class_loader,
                                                               *dex_file,
                                                               *dex_class_def);
      // 将DexFile插入到ClassLoader中。
      class_linker->InsertDexFileInToClassLoader(soa.Decode<mirror::Object>(dexFile),
                                                 class_loader.Get());
      if (result != nullptr) {
        VLOG(class_linker) << "DexFile_defineClassNative returning " << result
                           << " for " << class_name.c_str();
        return soa.AddLocalReference<jclass>(result);
      }
    }
  }
  VLOG(class_linker) << "Failed to find dex_class_def " << class_name.c_str();
  return nullptr;
}
```

​	代码中看到`cookie`中能拿到所有`DexFile`，最终的`Class`对象是有`DefineClass`方法定义后返回的。继续看其实现过程。

```java

ObjPtr<mirror::Class> ClassLinker::DefineClass(Thread* self,
                                               const char* descriptor,
                                               size_t hash,
                                               Handle<mirror::ClassLoader> class_loader,
                                               const DexFile& dex_file,
                                               const dex::ClassDef& dex_class_def) {
  ...
  DexFile const* new_dex_file = nullptr;
  dex::ClassDef const* new_class_def = nullptr;
  // 类被加载前的预处理
  Runtime::Current()->GetRuntimeCallbacks()->ClassPreDefine(descriptor,
                                                            klass,
                                                            class_loader,
                                                            dex_file,
                                                            dex_class_def,
                                                            &new_dex_file,
                                                            &new_class_def);
  // 将dex文件加载到内存中
  ObjPtr<mirror::DexCache> dex_cache = RegisterDexFile(*new_dex_file, class_loader.Get());
  if (dex_cache == nullptr) {
    self->AssertPendingException();
    return sdc.Finish(nullptr);
  }
  klass->SetDexCache(dex_cache);
    
  // 初始化类
  SetupClass(*new_dex_file, *new_class_def, klass, class_loader.Get());
  ...

  // 向类表中插入类对象
  ObjPtr<mirror::Class> existing = InsertClass(descriptor, klass.Get(), hash);
  ...
      
  // 加载并初始化类，在必要时创建新的类对象
  LoadClass(self, *new_dex_file, *new_class_def, klass);
  ...
      
  MutableHandle<mirror::Class> h_new_class = hs.NewHandle<mirror::Class>(nullptr);
    
  // 链接类及其相关信息
  if (!LinkClass(self, descriptor, klass, interfaces, &h_new_class)) {
    // Linking failed.
    if (!klass->IsErroneous()) {
      mirror::Class::SetStatus(klass, ClassStatus::kErrorUnresolved, self);
    }
    return sdc.Finish(nullptr);
  }
  return sdc.Finish(h_new_class);
}
```

​	`ClassPreDefine`是一个回调函数，它在类被加载之前被调用，用于进行一些预处理工作。具体来说，`ClassPreDefin`会被调用以执行以下任务：

- 对新定义的类进行验证和解析，以确保类结构的正确性。

- 为新定义的类分配内存空间，并构造新对象的实例。

- 设置类的访问控制权限并更新关联的缓存信息。

​	`RegisterDexFile`用于注册 `DEX` 文件。该函数负责将 `DEX `文件加载到内存中，并将其中包含的类和相关信息注册到运行时环境中，以供后续的程序使用。该函数的主要负责：

- 将 `DEX `文件加载到内存中，并为其分配一段连续的内存空间。

- 在运行时环境中创建` mirror::DexFile `对象，该对象包含了` DEX`文件的元数据信息，例如文件名、`MD5 `哈希值等。

- 为` DEX `文件中包含的每个类创建相应的` mirror::Class` 对象，并将其添加到类表中进行管理。

- 为新创建的` mirror::Class` 对象设置其访问权限和其他属性，例如类标志、字段、方法等。

- 创建并返回一个 `mirror::DexCache `对象，该对象表示已注册的` DEX `文件的缓存信息。

​	`SetupClass` 函数用于初始化类。该函数的主要作用：

- 解析类定义，并为其分配内存空间。

- 为新创建的类对象设置相关信息，例如类名、超类、接口信息等。

- 设置类对象的访问修饰符和标志。

- 将类对象添加到运行时环境中进行管理。

- 在必要的情况下，执行与类加载生命周期有关的回调函数。

​	`InsertClass`函数用于向类表中插入新的类对象，并确保在插入之前对其进行必要的验证和初始化工作。该函数的主要作用：

- 根据类描述符和哈希值查找类表中是否已经存在相同的类对象。

- 如果已经存在相同的类对象，则返回其指针，否则将新的类对象插入到类表中，并返回其指针。

- 在插入新的类对象之前，会先进行一些验证工作，例如检查类的访问权限，以及确保类的结构和超类的继承关系正确等。

- 在需要时，执行与类加载生命周期有关的回调函数。

​	`LoadClass` 函数用于加载并初始化类。并将其插入到类表中进行管理。主要作用：

1. 根据类描述符查找类表中是否已经存在相同的类对象，如存在则直接返回其指针。
2. 如果类表中不存在相同的类对象，则先使用 `SetupClass()` 函数创建新的类对象，并将其插入到类表中。此处调用了 `InsertClass()` 函数。
3. 加载并初始化类的超类及接口信息，以确保类的继承关系正确。
4. 执行与类加载生命周期有关的回调函数。

​	`	LinkClass` 函数是在用于链接类，该函数会返回一个新的类对象指针，以供调用者使用。主要作用：

1. 链接类的超类，并执行与超类有关的初始化工作。
2. 链接类实现的接口，并执行与接口有关的初始化工作。
3. 链接类的字段，并执行与字段有关的初始化工作。
4. 链接类的方法，并执行与方法有关的初始化工作。
5. 在必要时创建新的类对象，并将其返回给调用者。



### 7.3.3 函数调用流程

### 7.3.4 动态加载壳的实现

动态加载壳是一种常见的代码保护技术，它通过在程序运行时动态加载壳来保护应用程序。下面是一般情况下动态加载壳的流程：

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

### 7.3.5 如何脱壳



## 7.4 简单脱壳实现



## 7.5 自动化脱壳



