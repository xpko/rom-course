# 第六章 功能定制

## 6.1 如何进行功能定制

​	在开始动手前，必须要明确目标需求，规划要实现功能的具体表现。根据预定好的目标方向，将能抽取的业务部分隔离开来，通过开发一个普通的App先对业务实现流程，避免直接在AOSP中修改源码，发现问题后，反复编译排查这些逻辑的细节，导致耗费大量的时间成本在简单问题上。

​	除此之外，尽量使用源码版本管理工具来维护代码，避免长期迭代后，无法找到自己修改的相关代码，导致维护非常困难，以及迁移代码的不便利，如果不想搭建源码版本管理AOSP，则尽量保持代码开发时的风格，将自己修改处的代码统一打上标识，并且到一定阶段进行备份，避免因为自己的修改导致系统异常，却又无法回退代码解决问题。

​	在进行功能定制时，需要先对目标的执行流程和实现过程有一定的了解，然后找到合适的切入点，在实现过程中分析源码时，需要多多关注AOSP中提供的各种功能函数，有些常见的功能函数不要自己重新写一套实现，如果要定制的功能在AOSP源码中有类似的实现，则直接参考官方的实现。

​	功能开发的过程实际就是不断熟悉源码的过程，可以通过插桩输出日志来加深对执行流程的认知，以及对源码的理解。所以接下来这一章中将围绕着通过插桩来加深印象，通过模仿AOSP自身的系统服务，来添加一个自己的系统服务，接着是通过做一个全局的注入器，来了解如何在AOSP中添加自己的源码文件。最后通过修改默认权限，来熟悉AOSP中APP执行过程的解析环节。

## 6.2 插桩

​	在Android逆向中，插桩是一项非常常见的手段，它可以帮助开发人员检测和诊断代码问题。插桩是指在程序运行时向代码中插入额外的指令或代码段来收集有关程序执行的信息。这些信息可以用于分析程序执行流程、性能瓶颈等问题。常见的插桩方式分为静态插桩和动态插桩。

### 6.2.1 静态插桩

​	静态插桩是指将插入的代码直接嵌入到源代码中，并在编译期间将其转换为二进制形式。静态插桩通常用于收集静态信息，例如函数调用图、代码覆盖率等。比如将一个APP反编译后，找到要分析的目标函数，在smali指令中插入日志输出的指令，并且将函数的参数或返回值，或全局变量、局部变量等需要观测的相关信息进行输出，最后将代码回编成apk后，重新签名。

### 6.2.2 动态插桩

​	动态插桩是指在程序运行时动态地将插入的代码加载到内存中并执行。动态插桩通常用于收集动态信息，例如内存使用情况、线程状态等。对函数进行Hook就是一种动态插桩技术，在Hook中，通过修改函数入口地址，将自己的代码"钩"入到目标函数中，在函数调用前或调用后执行一些额外的操作，例如记录日志、篡改数据、窃听函数调用等。Hook通常用于调试、性能分析和安全审计等方面。它可以帮助开发人员诊断代码问题，提高程序的稳定性和性能，并增强程序的安全性。同时，Hook还可以被黑客用于攻击应用程序，因此需要谨慎使用。

### 6.2.3 ROM插桩

​	ROM插桩是指在预置的ROM固件中进行插桩，和前面的两种方式不同，直接通过修改系统代码，对想要关注的信息进行输出即可，过程等于是在开发的APP中添加LOG日志一般，虽然插桩非常方便，但是这并不是一个小型的APP项目，其中的调用流程相当复杂，需要具有更高的技术要求和谨慎性，所以前提是我们必须熟悉AOSP的源码，才能更加优雅的输出日志。

## 6.3 RegisterNative插桩

​	Native函数是指在Android开发中，Java代码调用的由C、C++编写的函数。Native函数通常用来访问底层系统资源，或进行高性能的计算操作。和普通Java函数不一样，Native函数需要通过JNI（Java Native Interface）进行调用。而Native函数能被调用到的前提是需要先进行注册，有两种方式进行注册，分别是静态注册和动态注册。

​	静态注册是指在编译时就将Native函数与Java方法进行绑定。这种方式需要手动编写C/C++代码，并在编译时生成一个共享库文件，然后在Java程序中加载该库文件并通过JNI接口调用其中的函数。

​	动态注册是指在程序运行时将Native函数与Java方法进行绑定。这种方式可以在Java程序中动态地加载Native函数，避免了在编译时生成共享库文件的过程。通过JNI接口提供的相关函数，可以在Java程序中实现动态注册的功能。

​	接着开始逐步的通过对RegisterNative的分析，最终在系统中插桩，将所有App的静态注册和动态注册进行输出，打印出进行注册的目标函数名，以及注册对应的C++函数的偏移地址。

### 6.3.1 Native函数注册

​	通过前文的介绍，了解到Native函数必须要进行注册才能被找到并调用，接下来看两个例子，展示了如何对Native函数进行静态注册和动态注册的。

​	当使用Android Studio创建一个Native C++的项目，其中默认使用的就是静态注册，在这个例子中，Java 函数与 C++ 函数的绑定是通过 Java 和 C++ 函数名的约定来实现的。具体地说，在 Java 代码中声明的 native 方法的命名规则为：Java_ + 全限定类名 + _ + 方法名，并且将所有的点分隔符替换为下划线。例如，在这个例子中，Java 类的全限定名为 com.mik.nativecppdemo.MainActivity，方法名为 stringFromJNI，因此对应的 C++ 函数名为 Java_com_mik_nativecppdemo_MainActivity_stringFromJNI，静态注册例子如下。

```java
// java文件
public class MainActivity extends AppCompatActivity {
    static {
        System.loadLibrary("nativecppdemo");
    }
  	...
    public native String stringFromJNI();
}
// c++文件
extern "C" JNIEXPORT jstring JNICALL
Java_com_mik_nativecppdemo_MainActivity_stringFromJNI(
        JNIEnv* env,
        jobject /* this */) {
    std::string hello = "Hello from C++";
    return env->NewStringUTF(hello.c_str());
}
```

​	动态注册一般是写代码手动注册，将指定的符号名与对应的函数地址进行关联，在AOSP源码中Native函数大部分都是使用动态注册方式的，动态注册例子如下。

```java
// java文件
public class NativeClass {
    private native int dynamicFunction(int arg);
    static {
        System.loadLibrary("native-lib");
        registerDynamicFunction();
    }
    private static native void registerDynamicFunction();
}

//c++文件
static JNINativeMethod gMethods[] = {
    {"dynamicFunction", "(I)I", (void*) dynamicFunction},
};

JNIEXPORT jint JNICALL
Java_com_example_NativeClass_dynamicFunction(JNIEnv *env, jobject instance, jint arg) {
    // 实现Native函数逻辑
    return arg + 1;
}

JNIEXPORT void JNICALL
Java_com_example_NativeClass_registerDynamicFunction(JNIEnv *env, jclass clazz) {
    // 动态注册Native函数
    jclass jclazz = env->FindClass("com/example/NativeClass");
    env->RegisterNatives(jclazz, gMethods, sizeof(gMethods) / sizeof(JNINativeMethod));
    env->DeleteLocalRef(jclazz);
}
```

### 6.3.2 RegisterNative执行流程



### 6.3.3 RegisterNative实现插桩

## 6.4 自定义系统服务



## 6.6 进程注入器



## 6.7 修改APP默认权限

### 6.7.1 APP权限介绍



### 6.7.2 APP权限的源码跟踪



### 6.7.3 AOSP10下的默认权限修改

