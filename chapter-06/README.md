# 第六章 功能定制

​	上一章中系统内置的过程和`Android`系统的编译流程息息相关，而本章功能的定制就是和安卓源码的执行紧密相连，通过对源码运行的理解，可以在执行过程的源码中添加需求功能，插入自己的业务逻辑，例如对其插桩输出，可以帮助我们更好的理解源码的执行过程。在本章中，将头开始分析功能，应该如何分析其原理，然后逐步进行实现。

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

​	下面开始了解两种注册方式的实现原理，最终在系统执行过程中找到一个共同调用处进行插桩，将所有App的静态注册和动态注册进行输出，打印出进行注册的目标函数名，以及注册对应的C++函数的偏移地址。

### 6.3.1 静态注册

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

​	静态注册函数必须使用`JNIEXPORT`和`JNICALL`来修饰，这两个修饰符是 JNI 中的预处理器宏。其中`JNIEXPORT`会将函数名称保存到动态符号表，当Linker在注册时就能通过dlsym找到该函数。

​	`JNICALL` 宏主要用于消除不同编译器和操作系统之间的调用规则的差异。在不同的平台上，本地方法的参数传递、调用约定和名称修饰等方面可能存在一些差异。这些差异可能会导致在一个平台上编译的共享库无法在另一个平台上运行。为了解决这个问题，JNI 规范定义了一种标准的本地方法命名方式，即 `Java_包名_类名_方法名` 的格式。使用 `JNICALL` 宏，我们可以让编译器自动根据规范来生成符合要求的本地方法名，从而保证在不同平台上都能正确调用本地方法。

​	需要注意的是，虽然 `JNICALL` 可以帮助我们消除平台差异，但在某些情况下，我们仍然需要手动指定本地方法的名称，例如当我们需要使用 JNI 的反射机制来动态调用本地方法时。此时，我们需要在注册本地方法时显式地指定方法名，并将其与 Java 代码中的方法名相对应。

​	对于静态注册而言，尽管没有看到使用RegisterNative进行注册，但是在内部有进行隐式注册的，当java类被加载时会调用LoadMethod将方法加载到虚拟机中，随后调用LinkCode将Native函数与Java函数进行链接。下面看LoadClass的相关代码。

```c++
void ClassLinker::LoadClass(Thread* self,
                            const DexFile& dex_file,
                            const dex::ClassDef& dex_class_def,
                            Handle<mirror::Class> klass) {
  	...
    // 遍历一个 Java 类的所有字段和方法，并对它们进行操作
    accessor.VisitFieldsAndMethods([&](
        const ClassAccessor::Field& field) REQUIRES_SHARED(Locks::mutator_lock_) {
          ...
          // 所有字段
          LoadMethod(dex_file, method, klass, art_method);
          LinkCode(this, art_method, oat_class_ptr, class_def_method_index);
          ...
        }, [&](const ClassAccessor::Method& method) REQUIRES_SHARED(Locks::mutator_lock_) {
          // 所有方法
          ArtMethod* art_method = klass->GetVirtualMethodUnchecked(
              class_def_method_index - accessor.NumDirectMethods(),
              image_pointer_size_);
          LoadMethod(dex_file, method, klass, art_method);
          LinkCode(this, art_method, oat_class_ptr, class_def_method_index);
          ++class_def_method_index;
        });
    ...
}
```

​	下面继续看看LinkCode的实现，如果已经被编译就会有Oat文件，就可以获取到`quick_code`，直接从二进制中调用来快速执行，否则走解释执行。

```c++
static void LinkCode(ClassLinker* class_linker,
                     ArtMethod* method,
                     const OatFile::OatClass* oat_class,
                     uint32_t class_def_method_index) REQUIRES_SHARED(Locks::mutator_lock_) {
  ...
  const void* quick_code = nullptr;
  if (oat_class != nullptr) {
    const OatFile::OatMethod oat_method = oat_class->GetOatMethod(class_def_method_index);
    quick_code = oat_method.GetQuickCode();
  }
  // 是否使用解释执行
  bool enter_interpreter = class_linker->ShouldUseInterpreterEntrypoint(method, quick_code);
  // 为指定的java函数设置二进制的快速执行入口
  if (quick_code == nullptr) {
    method->SetEntryPointFromQuickCompiledCode(
        method->IsNative() ? GetQuickGenericJniStub() : GetQuickToInterpreterBridge());
  } else if (enter_interpreter) {
    method->SetEntryPointFromQuickCompiledCode(GetQuickToInterpreterBridge());
  } else if (NeedsClinitCheckBeforeCall(method)) {
    method->SetEntryPointFromQuickCompiledCode(GetQuickResolutionStub());
  } else {
    method->SetEntryPointFromQuickCompiledCode(quick_code);
  }

  if (method->IsNative()) {
    // 为指定的java函数设置JNI入口点，IsCriticalNative表示java中带有@CriticalNative标记的native函数。一般的普通函数会调用后面的GetJniDlsymLookupStub
    method->SetEntryPointFromJni(
        method->IsCriticalNative() ? GetJniDlsymLookupCriticalStub() : GetJniDlsymLookupStub());

    if (enter_interpreter || quick_code == nullptr) {
      DCHECK(class_linker->IsQuickGenericJniStub(method->GetEntryPointFromQuickCompiledCode()));
    }
  }
}
```

​	上面可以看到JNI设置入口点有两种情况，Critical Native 方法通常用于需要高性能、低延迟和可预测行为的场景，例如音频处理、图像处理、网络协议栈等。一般情况开发者使用的都是普通Native函数，所以会调用后者`GetJniDlsymLookupStub`，接着继续看看实现代码。

```c++
static inline const void* GetJniDlsymLookupStub() {
  return reinterpret_cast<const void*>(art_jni_dlsym_lookup_stub);
}
```

​	这里看到就是将一个函数指针转换后返回，这个函数指针对应的是一段汇编代码，下面看看汇编代码实现。

```assembly
ENTRY art_jni_dlsym_lookup_stub
    // spill regs.
    ...
    bl    artFindNativeMethod
    b     .Llookup_stub_continue
    .Llookup_stub_fast_or_critical_native:
    bl    artFindNativeMethodRunnable
	...

1:
    ret             // restore regs and return to caller to handle exception.
END art_jni_dlsym_lookup_stub
```

​	能看到里面调用了`artFindNativeMethod`和`artFindNativeMethodRunnable`继续查看相关函数。

```c++
extern "C" const void* artFindNativeMethod(Thread* self) {
  DCHECK_EQ(self, Thread::Current());
  Locks::mutator_lock_->AssertNotHeld(self);  // We come here as Native.
  ScopedObjectAccess soa(self);
  return artFindNativeMethodRunnable(self);
}

extern "C" const void* artFindNativeMethodRunnable(Thread* self)
    REQUIRES_SHARED(Locks::mutator_lock_) {
  Locks::mutator_lock_->AssertSharedHeld(self);  // We come here as Runnable.
  uint32_t dex_pc;
  ArtMethod* method = self->GetCurrentMethod(&dex_pc);
  DCHECK(method != nullptr);
  ClassLinker* class_linker = Runtime::Current()->GetClassLinker();
  // 非静态函数的处理
  if (!method->IsNative()) {
    ...
  }
  // 如果注册过了，这里就会直接获取到，返回对应的地址
  const void* native_code = class_linker->GetRegisteredNative(self, method);
  if (native_code != nullptr) {
    return native_code;
  }
  // 查找对应的函数地址
  JavaVMExt* vm = down_cast<JNIEnvExt*>(self->GetJniEnv())->GetVm();
  native_code = vm->FindCodeForNativeMethod(method);
  if (native_code == nullptr) {
    self->AssertPendingException();
    return nullptr;
  }
  // 最后通过Linker进行注册
  return class_linker->RegisterNative(self, method, native_code);
}
```

​	`FindCodeForNativeMethod`执行到内部最后是通过`dlsym`查找符号，并且成功在这里看到了前文所说的隐式调用的`RegisterNative`。

### 6.3.2 动态注册

​	动态注册一般是写代码手动注册，将指定的符号名与对应的函数地址进行关联，在AOSP源码中Native函数大部分都是使用动态注册方式的，动态注册例子如下。

```java
// java文件
public class MainActivity extends AppCompatActivity {
    static {
        System.loadLibrary("native-lib");
    }

    public native String stringFromJNI2();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        TextView tv = findViewById(R.id.sample_text);
        tv.setText(stringFromJNI());
    }
}

//c++文件
jstring stringFromJNI2(JNIEnv* env, jobject /* this */) {
    return env->NewStringUTF("Hello from C++");
}

// 在 JNI_OnLoad 中进行动态注册
JNIEXPORT jint JNICALL
JNI_OnLoad(JavaVM* vm, void* reserved) {
    JNIEnv* env;
    if (vm->GetEnv(reinterpret_cast<void**>(&env), JNI_VERSION_1_6) != JNI_OK) {
        return -1;
    }

    // 手动注册 stringFromJNI 方法
    jclass clazz = env->FindClass("com/example/myapplication/MainActivity");
    JNINativeMethod methods[] = {
            {"stringFromJNI2", "()Ljava/lang/String;", reinterpret_cast<void *>(stringFromJNI2)}
    };
    env->RegisterNatives(clazz, methods, sizeof(methods)/sizeof(methods[0]));

    return JNI_VERSION_1_6;
}
```

​	动态注册中是直接调用JniEnv的`RegisterNatives`进行注册的，找到对应的实现代码如下。

```c++
  static jint RegisterNatives(JNIEnv* env,
                              jclass java_class,
                              const JNINativeMethod* methods,
                              jint method_count) {
    ...
    // 遍历所有需要注册的函数
    for (jint i = 0; i < method_count; ++i) {
      // 取出函数名，函数签名，函数地址
      const char* name = methods[i].name;
      const char* sig = methods[i].signature;
      const void* fnPtr = methods[i].fnPtr;
      ...
      // 遍历Java对象的继承层次结构，也就是所有父类，来获取函数
      for (ObjPtr<mirror::Class> current_class = c.Get();
           current_class != nullptr;
           current_class = current_class->GetSuperClass()) {
        m = FindMethod<true>(current_class, name, sig);
        if (m != nullptr) {
          break;
        }
        m = FindMethod<false>(current_class, name, sig);
        if (m != nullptr) {
          break;
        }
        ...
      }

      if (m == nullptr) {
        ...
        return JNI_ERR;
      } else if (!m->IsNative()) {
        ...
        return JNI_ERR;
      }
      ...
      const void* final_function_ptr = class_linker->RegisterNative(soa.Self(), m, fnPtr);
      UNUSED(final_function_ptr);
    }
    return JNI_OK;
  }
```

​	在动态注册中，同样看到内部是调用了Linker的`RegisterNative`进行注册的，最后我们看看Linker中的实现。

```c++
const void* ClassLinker::RegisterNative(
    Thread* self, ArtMethod* method, const void* native_method) {
  CHECK(method->IsNative()) << method->PrettyMethod();
  CHECK(native_method != nullptr) << method->PrettyMethod();
  void* new_native_method = nullptr;
  Runtime* runtime = Runtime::Current();
  runtime->GetRuntimeCallbacks()->RegisterNativeMethod(method,
                                                       native_method,
                                                       /*out*/&new_native_method);
  if (method->IsCriticalNative()) {
    ...
  } else {
    // 给指定的java函数设置对应的Native函数的入口地址。
    method->SetEntryPointFromJni(new_native_method);
  }
  return new_native_method;
}
```

​	分析到这里，就已经看到了两个目标需求：` ClassLinker::RegisterNative`是静态注册和动态注册执行流程中的共同点、该函数的返回值就是Native函数的入口地址。接下来可以开始进行插桩输出了。

### 6.3.3 RegisterNative实现插桩

​	前文简单介绍ROM插桩其实就是输出日志，找到了合适的时机，以及要输出的内容，最后就是输出日志即可。在函数`ClassLinker::RegisterNative`调用结束时插入日志输出如下

```c++
#inclue
const void* ClassLinker::RegisterNative(
    Thread* self, ArtMethod* method, const void* native_method) {
  ...
  LOG(INFO) << "mikrom ClassLinker::RegisterNative "<<method->PrettyMethod().c_str()<<" native_ptr:"<<new_native_method<<" method_idx:"<<method->GetMethodIndex()<<" baseAddr:"<<base_addr;
  return new_native_method;
}
```

​	刷机编译后，安装测试demo，输出结果如下，成功打印出静态注册和动态注册的对应函数以及其函数地址。

```
mik.nativedem: mikrom ClassLinker::RegisterNative java.lang.String cn.mik.nativedemo.MainActivity.stringFromJNI2() native_ptr:0x7983a918c8 method_idx:632
mik.nativedem: mikrom ClassLinker::RegisterNative java.lang.String cn.mik.nativedemo.MainActivity.stringFromJNI() native_ptr:0x7983a916e8 method_idx:631
```

​	这里尽管已经输出了函数地址，但是可以再进行细节的优化，比如将函数地址去掉动态库的基址，获取到文件中的真实函数偏移。在这个时机已知了函数地址，只需要遍历已加载的所有动态库，计算出动态库结束地址，如果函数地址在某个动态库范围中，则返回动态库基址，最后打桩时，使用函数地址减掉基址即可拿到真实偏移了。实现代码如下。

```c++
#include "link.h"
#include "utils/Log.h"

// 遍历输出所有已经加载的动态库
int dl_iterate_callback(struct dl_phdr_info* info, size_t , void* data) {
    uintptr_t addr = reinterpret_cast<uintptr_t>(*(void**)data);
    // 计算出结束地址
    void* endptr=  (void*)(info->dlpi_addr + info->dlpi_phdr[info->dlpi_phnum - 1].p_vaddr + info->dlpi_phdr[info->dlpi_phnum - 1].p_memsz);
    uintptr_t end=reinterpret_cast<uintptr_t>(endptr);
    ALOGD("mikrom native: %p\n", (void*)addr);
    ALOGD("mikrom Library name: %s\n", info->dlpi_name);
    ALOGD("mikrom Library base address: %p\n", (void*) info->dlpi_addr);
    ALOGD("mikrom Library end address: %p\n\n",endptr);
    // 函数地址在动态库范围则返回该动态库的基址
    if(addr >= info->dlpi_addr && addr<=end){
        ALOGD("mikrom Library found address: %p\n\n",(void*)info->dlpi_addr);
        reinterpret_cast<void**>(data)[0] = reinterpret_cast<void*>(info->dlpi_addr);
    }
    return 0;
}

// 根据函数地址获取对应动态库的基址
void* FindLibraryBaseAddress(void* entry_addr) {
    void* lib_base_addr = entry_addr;
    // 遍历所有加载的动态库，设置回调函数
    dl_iterate_phdr(dl_iterate_callback, &lib_base_addr);
    return lib_base_addr;
}


const void* ClassLinker::RegisterNative(
    Thread* self, ArtMethod* method, const void* native_method) {
    ...
    void * native_ptr=new_native_method;
    void* base_addr=FindLibraryBaseAddress(native_ptr);
    // 指针尽量转换后再进行操作，避免出现问题。
    uintptr_t native_data = reinterpret_cast<uintptr_t>(native_ptr);
    uintptr_t base_data = reinterpret_cast<uintptr_t>(base_addr);
    uintptr_t offset=native_data-base_data;
    ALOGD("mikrom ClassLinker::RegisterNative %s native_ptr:%p method_idx:%p offset:0x%lx",method->PrettyMethod().c_str(),new_native_method,method->GetMethodIndex(),(void*)offset);
    return new_native_method;
}

```

​	优化后的输出日志如下

```
mik.nativedem: mikrom native: 0x7a621108c8
mik.nativedem: mikrom Library name: /data/app/~~sm_GZ36XVwW9zZJGRl1ABg==/cn.mik.nativedemo-VJiQEEQ3s9XXRMp6pkOKqA==/base.apk!/lib/arm64-v8a/libnativedemo.so
mik.nativedem: mikrom Library base address: 0x7a62102000
mik.nativedem: mikrom Library end address: 0x7a62136000
mik.nativedem: mikrom Library found address: 0x7a62102000
mik.nativedem: mikrom ClassLinker::RegisterNative java.lang.String cn.mik.nativedemo.MainActivity.stringFromJNI2() native_ptr:0x7a621108c8 method_idx:0x278 offset:0xe8c8

mik.nativedem: mikrom native: 0x7a621106e8
mik.nativedem: mikrom Library name: /data/app/~~sm_GZ36XVwW9zZJGRl1ABg==/cn.mik.nativedemo-VJiQEEQ3s9XXRMp6pkOKqA==/base.apk!/lib/arm64-v8a/libnativedemo.so
mik.nativedem: mikrom Library base address: 0x7a62102000
mik.nativedem: mikrom Library end address: 0x7a62136000
mik.nativedem: mikrom Library found address: 0x7a62102000
mik.nativedem: mikrom ClassLinker::RegisterNative java.lang.String cn.mik.nativedemo.MainActivity.stringFromJNI() native_ptr:0x7a621106e8 method_idx:0x277 offset:0xe6e8
```

## 6.4 自定义系统服务

​	自定义系统服务是指在操作系统中创建自己的服务，以便在需要时可以使用它。系统服务可以在启动时自动运行且没有UI界面，并在后台执行某些特定任务或提供某些功能。由于系统服务有着system身份的权限，所以自定义系统服务可以用于各种用途。例如如下：

1. 系统监控与管理：通过定期收集和分析系统数据，自动化报警和管理，保证系统稳定性和安全性；
2. 自动化部署和升级：通过编写脚本和程序实现自动化部署和升级软件，简化人工干预过程；
3. 数据备份与恢复：通过编写脚本和程序实现数据备份和恢复，保证数据安全性和连续性；
4. 后台任务处理：例如定时清理缓存、定时更新索引等任务，减轻人工干预压力，提高系统效率。

​	在第三章简单介绍过系统服务的启动，添加一个自定义的系统服务可以参考AOSP源码中的添加方式来逐步完成。接下来参考源码来添加一个最简单的系统服务`MIK_SERVICE`。

​	首先在文件`frameworks/base/core/java/android/content/Context.java`看到了定义了各种系统服务的名称，在这里参考`POWER_SERVICE`服务的添加，在这个服务的下面添加自定义的服务，同时找到该文件中，其他对`POWER_SERVICE`进行处理的地方，将自定义的服务做同样的处理，相关代码如下

```java
public abstract class Context {
    @StringDef(suffix = { "_SERVICE" }, value = {
            POWER_SERVICE,
            ...
            MIKROM_SERVICE,
    })
    ...
    public static final String POWER_SERVICE = "power";
    public static final String MIKROM_SERVICE = "mikrom";
}
```

​	接着搜索`POWER_SERVICE`找到该服务注册的地方，找到了文件`frameworks/base/core/java/android/app/SystemServiceRegistry.java`中进行了注册，所以在注册该服务的下方，模仿源码添加对自定义服务的注册。

```java
public final class SystemServiceRegistry {
	...
	static {
		...
		registerService(Context.POWER_SERVICE, PowerManager.class,
                new CachedServiceFetcher<PowerManager>() {
            @Override
            public PowerManager createService(ContextImpl ctx) throws ServiceNotFoundException {
                IBinder powerBinder = ServiceManager.getServiceOrThrow(Context.POWER_SERVICE);
                IPowerManager powerService = IPowerManager.Stub.asInterface(powerBinder);
                IBinder thermalBinder = ServiceManager.getServiceOrThrow(Context.THERMAL_SERVICE);
                IThermalService thermalService = IThermalService.Stub.asInterface(thermalBinder);
                return new PowerManager(ctx.getOuterContext(), powerService, thermalService,
                        ctx.mMainThread.getHandler());
            }});

        registerService(Context.MIKROM_SERVICE, MikRomManager.class,
                        new CachedServiceFetcher<MikRomManager>() {
                    @Override
                    public MikRomManager createService(ContextImpl ctx) throws ServiceNotFoundException {
                        IBinder mikromBinder = ServiceManager.getServiceOrThrow(Context.MIKROM_SERVICE);
                        IMikRomManager mikromService = IMikRomManager.Stub.asInterface(mikromBinder);
                        return new MikRomManager(ctx.getOuterContext(), mikromService, ctx.mMainThread.getHandler());
                    }});
        ...
	}
	...
}
```

​	`PowerManager`的功能中用到了`THERMAL_SERVICE`系统服务，所以这里不必完全照搬，省略掉这个参数即可。接下来发现注册时用到的`IMikRomManager`、`MikRomManager`并不存在，所以继续参考`PowerManager`的实现，先寻找`IPowerManager`在哪里定义的，通过搜索，发现该接口在文件`frameworks/base/core/java/android/os/IPowerManager.aidl`中。在同目录下新建文件`IMikRomManager.aidl`并添加简单的接口内容如下。

```java
package android.os;

interface IMikRomManager
{
    String hello();
}
```

​	AIDL（Android 接口定义语言）是一种 Android 平台上的 IPC 机制，用于不同应用程序组件之间进行进程通信。要使用 AIDL 实现进程间通信，需要定义一个接口文件并实现它，在服务端和客户端之间传递 Parcelable 类型的数据。

​	在 Android 中使用 AIDL 首先需要创建一个 .aidl 文件来定义接口。接下来，将 .aidl 文件编译成 Java 接口，并在服务端和客户端中分别实现该接口。最后，在服务端通过 bindService() 方法绑定服务并向客户端返回 IBinder 对象。使用 AIDL 可以轻松地实现跨进程通信，但需要考虑线程安全性和数据完整性等问题。

​	添加完毕后还需要找到在哪里将这个文件添加到编译中的，搜索`IPowerManager.aidl`后，找到文件`frameworks/base/core/java/Android.bp`中进行处理的。所以跟着添加上刚刚定义的aidl文件。修改如下。

```
filegroup {
    name: "libpowermanager_aidl",
    srcs: [
        ...
        "android/os/IPowerManager.aidl",
        "android/os/IMikRomManager.aidl",
    ],
}
```

​	然后继续寻找`IPowerManager.aidl`在哪里进行实现的，搜索`IPowerManager.Stub`，找到文件`frameworks/base/services/core/java/com/android/server/power/PowerManagerService.java`实现的具体的逻辑。该服务的路径是在power目录下，并不适合存放自定义的服务，所以选择在更上级目录创建一个对应的新文件`frameworks/base/services/core/java/com/android/server/MikRomManagerService.java`，代码如下。

```java
public class MikRomManagerService extends IMikRomManager.Stub {
    private Context mContext;
    private String TAG="MikRomManagerService";
    public MikRomManagerService(Context context){
        mContext=context;
    }

    @Override
    public String hello(){
        return "hello mikrom service";
    }
}
```

​	接着找到`PowerManager`在文件` frameworks/base/core/java/android/os/PowerManager.java`中实现，所以在这个目录中创建文件`MikRomManager.java`，代码实现如下。

```java
package android.os;

@SystemService(Context.MIKROM_SERVICE)
public final class MikRomManager {
    private static final String TAG = "MikRomManager";
    final Context mContext;
    @UnsupportedAppUsage
    final IMikRomManager mService;
    @UnsupportedAppUsage(maxTargetSdk = Build.VERSION_CODES.P)
    final Handler mHandler;
    public MikRomManager(Context context, IMikRomManager service,Handler handler) {
            mContext = context;
            mService = service;
            mHandler = handler;
    }

    public String hello(){
        return mService.hello();
    }
}
```

​	到这里注册一个自定义的系统服务基本完成了，最后是启动这个自定义的服务，而启动的流程在第三章中有详细的介绍，在文件`frameworks/base/services/java/com/android/server/SystemServer.java`中启动，这里选择系统准备就绪后的时机再拉起这个服务，参考其他任意服务启动的方式即可。

```java
private void startOtherServices(@NonNull TimingsTraceAndSlog t) {

    ...
    t.traceBegin("StartNetworkStatsService");
    try {
        networkStats = NetworkStatsService.create(context, networkManagement);
        ServiceManager.addService(Context.NETWORK_STATS_SERVICE, networkStats);
    } catch (Throwable e) {
        reportWtf("starting NetworkStats Service", e);
    }
    t.traceEnd();


    t.traceBegin("StartMikRomManagerService");
    try {
        MikRomManagerService mikromService = new MikRomManagerService(context);
        ServiceManager.addService(Context.MIKROM_SERVICE,mikromService);
    } catch (Throwable e) {
        reportWtf("starting MikRom Service", e);
    }
    t.traceEnd();
    ...
}

```

​	到这里基本准备就绪了，可以开始尝试编译，由于添加了aidl文件，所以需要先调用`make update-api`进行编译，编译过程如下，最后出现编译报错。

```
source ./build/envsetup.sh

lunch aosp_blueline-userdebug

make update-api -j8

// 出现下面的错误
frameworks/base/core/java/android/os/MikRomManager.java:10: error: Method parameter type `android.content.Context` violates package layering: nothin
g in `package android.os` should depend on `package android.content` [PackageLayering]
frameworks/base/core/java/android/os/MikRomManager.java:16: error: Managers must always be obtained from Context; no direct constructors [ManagerCon
structor]
frameworks/base/core/java/android/os/MikRomManager.java:16: error: Missing nullability on parameter `context` in method `MikRomManager` [MissingNull
ability]
frameworks/base/core/java/android/os/MikRomManager.java:16: error: Missing nullability on parameter `service` in method `MikRomManager` [MissingNull
ability]
```

​	这是由于Android 11 以后谷歌强制开启lint检查来提高应用程序的质量和稳定性。Lint检查是Android Studio中的一个静态分析工具，用于检测代码中可能存在的潜在问题和错误。它可以帮助开发人员找到并修复代码中的bug、性能问题、安全漏洞等。可以设置让其忽略掉对这个`android.os`目录的检查，修改文件`framewoks/base/Android.bp`文件如下。

```
metalava_framework_docs_args = "--manifest $(location core/res/AndroidManifest.xml) " +
    ...
    "--api-lint-ignore-prefix android.os."
```

​	提示需要将Managers必须是单例模式，并且String是允许为null值的，参数或返回值需要携带`@Nullable`注解，调用service函数时，需要捕获异常。针对以上的提示对`MikRomManager`进行调整如下。

```java
package android.os;

import android.annotation.NonNull;
import android.annotation.Nullable;
import android.compat.annotation.UnsupportedAppUsage;
import android.content.Context;
import android.annotation.SystemService;
import android.os.IMikRomManager;

@SystemService(Context.MIKROM_SERVICE)
public final class MikRomManager {
    private static final String TAG = "MikRomManager";
    IMikRomManager mService;
    public MikRomManager(IMikRomManager service) {
            mService = service;
    }
    private static MikRomManager sInstance;
    /**
     *@hide
     */
    @NonNull
    @UnsupportedAppUsage
    public static MikRomManager getInstance() {
        synchronized (MikRomManager.class) {
            if (sInstance == null) {
                try {
                    IBinder mikromBinder = ServiceManager.getServiceOrThrow(Context.MIKROM_SERVICE);
                    IMikRomManager mikromService = IMikRomManager.Stub.asInterface(mikromBinder);
                    sInstance= new MikRomManager(mikromService);
                } catch (ServiceManager.ServiceNotFoundException e) {
                    throw new IllegalStateException(e);
                }
            }
            return sInstance;
        }
    }
    @Nullable
    public String hello(){
        try{
            return mService.hello();
        }catch (RemoteException ex){
            throw ex.rethrowFromSystemServer();
        }
    }
}
```

​	除此之外，在注册该服务的地方也要对应的调整初始化的方式。调整如下

```java
public final class SystemServiceRegistry {
	...
	static {
		...
        registerService(Context.MIKROM_SERVICE, MikRomManager.class,
                        new CachedServiceFetcher<MikRomManager>() {
                    @Override
                    public MikRomManager createService(ContextImpl ctx) throws ServiceNotFoundException {
                        return MikRomManager.getInstance();
                    }});
        ...
	}
	...
}
```

​	经过修改后，再重新编译就能正常编译完成了，最后还需要对selinux进行修改，对新增的服务开放权限。找到文件`system/sepolicy/public/service.te`，参考其他的服务定义，在最后添加一条类型定义如下。

```
type mikrom_service, system_api_service, system_server_service, service_manager_type;
```

​	然后找到文件`system/sepolicy/private/service_contexts`，在最后给我们`Context`中定义的`mikrom`服务设置使用刚刚定义的`mikrom_service`类型的权限，修改如下。

```
mikrom                                    u:object_r:mikrom_service:s0
```

​	为自定义的系统服务添加了selinux权限后，还需要给应用开启权限访问这个系统服务，找到`system/sepolicy/public/untrusted_app.te`文件，添加如下策略开放让其能查找该系统服务。

```
allow untrusted_app mikrom_service:service_manager find;
allow untrusted_app_27 mikrom_service:service_manager find;
allow untrusted_app_25 mikrom_service:service_manager find;
```

​	这时如果直接编译会出现下面的错误。

```
FAILED: ~/android_src/mikrom_out/target/product/blueline/obj/FAKE/sepolicy_freeze_test_intermediates/sepolicy_freeze_test
/bin/bash -c "(diff -rq -x bug_map system/sepolicy/prebuilts/api/31.0/public system/sepolicy/public ) && (diff -rq -x bug_map system/sepolicy/prebui
lts/api/31.0/private system/sepolicy/private ) && (touch ~/android_src/mikrom_out/target/product/blueline/obj/FAKE/sepolicy_freeze_test_int
ermediates/sepolicy_freeze_test )"
```

​	在前文介绍selinux时有说到系统会使用 prebuilts 中的策略进行对比，这是因为 prebuilts 中包含了在 Android 设备上预置的 sepolicy 策略和规则。所以当改动策略时，要将prebuilts 下对应的文件做出相同的修改。因为对应要调整`system/sepolicy/prebuilts/api/31.0/public/service.te`和`system/sepolicy/prebuilts/api/31.0/private/service_contexts`进行和上面相同的调整。这里需要注意的是`untrusted_app.te`文件只需要修改`prebuilts/api/31.0`的即可，而`service.te`和`service_contexts`，需要将`prebuilts/api/`目录下所有版本都添加定义，否则会出现如下错误。

```
SELinux: The following public types were found added to the policy without an entry into the compatibility mapping file(s) found in private/compat/V
.v/V.v[.ignore].cil, where V.v is the latest API level.
```

​	到这里selinux策略就基本修改完毕，成功编译后，刷入手机，检查服务是否成功开启。

```
adb shell

service list|grep mikrom

// 成功查询到自定义的系统服务
120	mikrom: [android.os.IMikRomManager]
```

​	最后开发一个测试的app对这个系统服务调用hello函数。创建一个Android项目，在java目录下创建一个package路径`android.os`，然后再这个package下创建一个文件`IMikRomManager.aidl`，内容和前文添加系统服务时一至，内容如下。

```java
package android.os;

interface IMikRomManager
{
    String hello();
}

```

​	可以通过反射获取`ServiceManager`类，调用该类的`getService`函数得到mikrom的系统服务，将返回的结果转换为刚刚定义的接口对象，最后调用目标函数拿到结果。实现代码如下。

```java

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

​	最后成功输出结果如下。

```
cn.mik.myservicedemo I/MainActivity: msg: hello mikrom service
```

## 6.5 APP权限

​	Android中的权限是指应用程序访问设备功能和用户数据所需的授权。在Android系统中，所有的应用程序都必须声明其需要的权限，以便在安装时就向用户展示，并且在运行时需要获取相应的授权才能使用。

​	这一节将介绍APP的权限，以及在源码中是如何加载`AndroidManifest.xml`文件获取到权限，并进行控制的，最后尝试在加载流程中进行修改，让APP默认具有一些权限，无需APP进行申请。

### 6.5.1 APP权限介绍

​		Android系统将权限分为普通权限和危险权限两类，其中危险权限需要用户明确授权才能使用，而普通权限则不需要。普通权限通常不涉及到用户隐私和设备安全问题，例如访问网络、读取手机状态等。而危险权限则可能会涉及到用户隐私和设备安全问题，例如读取联系人信息、访问摄像头等。
​	在AndroidManifest.xml文件中声明权限，可以使用`<uses-permission>`标签来声明需要的权限，例如：

```
<manifest package="com.example.app">
    <uses-permission android:name="android.permission.READ_CONTACTS" />
    <uses-permission android:name="android.permission.CAMERA" />
    ...
</manifest>
```

​	Android中的常见权限列表如下。

1. 日历权限：`android.permission.READ_CALENDAR、android.permission.WRITE_CALENDAR`
2. 相机权限：`android.permission.CAMERA`
3. 联系人权限：`android.permission.READ_CONTACTS、android.permission.WRITE_CONTACTS、android.permission.GET_ACCOUNTS`
4. 定位权限：`android.permission.ACCESS_FINE_LOCATION、android.permission.ACCESS_COARSE_LOCATION`
5. 麦克风权限：`android.permission.RECORD_AUDIO`
6. 手机状态和电话权限：`android.permission.READ_PHONE_STATE、android.permission.CALL_PHONE、android.permission.READ_CALL_LOG、android.permission.WRITE_CALL_LOG、android.permission.ADD_VOICEMAIL、android.permission.USE_SIP、android.permission.PROCESS_OUTGOING_CALLS`
7. 传感器权限：`android.permission.BODY_SENSORS`
8. 短信权限：`android.permission.READ_SMS、android.permission.RECEIVE_SMS、android.permission.SEND_SMS、android.permission.RECEIVE_WAP_PUSH、android.permission.RECEIVE_MMS`
9. 存储权限：`android.permission.READ_EXTERNAL_STORAGE、android.permission.WRITE_EXTERNAL_STORAGE`
10. 联网权限：`android.permission.INTERNET`

​	androidManifest.xml文件是Android应用程序的清单文件，它在应用程序安装和运行过程中都会被解析。Android系统启动时也会解析每个已安装应用程序的清单文件（即androidManifest.xml），以了解应用程序所需的权限、组件等信息，并将这些信息记录在系统中。而这项解析工作是由`PackageManagerService`系统服务来完成的。因此开始分析的入手点可以从该系统服务的启动开始。

### 6.5.2 权限解析源码跟踪

​	`PackageManagerService`系统服务的启动是再`SystemServer`进程中，在`SystemServer.java`中搜索就能该进程启动的入口，相关代码如下。

```java
private void startBootstrapServices() {
	...
    t.traceBegin("StartPackageManagerService");
    try {
        Watchdog.getInstance().pauseWatchingCurrentThread("packagemanagermain");
        mPackageManagerService = PackageManagerService.main(mSystemContext, installer,
                                                            domainVerificationService, mFactoryTestMode != FactoryTest.FACTORY_TEST_OFF,
                                                            mOnlyCore);
    } finally {
        Watchdog.getInstance().resumeWatchingCurrentThread("packagemanagermain");
    }
    ...
}
```

​	继续跟进看该服务的main函数

```java
public static PackageManagerService main(Context context, Installer installer,
            @NonNull DomainVerificationService domainVerificationService, boolean factoryTest,
            boolean onlyCore) {
        ...
        PackageManagerService m = new PackageManagerService(injector, onlyCore, factoryTest,
                Build.FINGERPRINT, Build.IS_ENG, Build.IS_USERDEBUG, Build.VERSION.SDK_INT,
                Build.VERSION.INCREMENTAL);
		...
        ServiceManager.addService("package", m);
        final PackageManagerNative pmn = m.new PackageManagerNative();
        ServiceManager.addService("package_native", pmn);
        return m;
    }
```

​	然后这里调用了`PackageManagerService`的构造函数，继续查看构造函数代码。

```java
public PackageManagerService(Injector injector, boolean onlyCore, boolean factoryTest,
            final String buildFingerprint, final boolean isEngBuild,
            final boolean isUserDebugBuild, final int sdkVersion, final String incrementalVersion) {
        ...
        synchronized (mInstallLock) {
        // writer
        synchronized (mLock) {
            ...
            // 遍历系统应用程序目录列表
            for (int i = mDirsToScanAsSystem.size() - 1; i >= 0; i--) {
                final ScanPartition partition = mDirsToScanAsSystem.get(i);
                if (partition.getOverlayFolder() == null) {
                    continue;
                }
                scanDirTracedLI(partition.getOverlayFolder(), systemParseFlags,
                        systemScanFlags | partition.scanFlag, 0,
                        packageParser, executorService);
            }

            scanDirTracedLI(frameworkDir, systemParseFlags,
                    systemScanFlags | SCAN_NO_DEX | SCAN_AS_PRIVILEGED, 0,
                    packageParser, executorService);
            ...

        } // synchronized (mLock)
        } // synchronized (mInstallLock)
        // CHECKSTYLE:ON IndentationCheck
		...
    }
```

​	`mDirsToScanAsSystem`是`PackageManagerService`类中的一个成员变量，用于存储系统应用程序目录列表。

​	系统应用程序存储在多个目录中，例如`/system/app、/system/priv-app`等。当系统启动时，`PackageManagerService`类会扫描这些目录以查找系统应用程序，并将其添加到应用程序列表中。这个列表中的每个元素都是一个File对象，表示一个系统应用程序目录。

​	当系统启动时，`PackageManagerService`会遍历`mDirsToScanAsSystem`列表并扫描其中的所有目录以查找系统应用程序。如果发现新的应用程序，则将其添加到应用程序列表中；如果发现已删除或升级的应用程序，则将其添加到`possiblyDeletedUpdatedSystemApps`列表中进行后续处理。下面看看`scanDirTracedLI`方法的实现。

```java
private void scanDirTracedLI(File scanDir, final int parseFlags, int scanFlags,
            long currentTime, PackageParser2 packageParser, ExecutorService executorService) {
        Trace.traceBegin(TRACE_TAG_PACKAGE_MANAGER, "scanDir [" + scanDir.getAbsolutePath() + "]");
        try {
            scanDirLI(scanDir, parseFlags, scanFlags, currentTime, packageParser, executorService);
        } finally {
            Trace.traceEnd(TRACE_TAG_PACKAGE_MANAGER);
        }
    }

private void scanDirLI(File scanDir, int parseFlags, int scanFlags, long currentTime,
            PackageParser2 packageParser, ExecutorService executorService) {
        final File[] files = scanDir.listFiles();
        if (ArrayUtils.isEmpty(files)) {
            Log.d(TAG, "No files in app dir " + scanDir);
            return;
        }

        if (DEBUG_PACKAGE_SCANNING) {
            Log.d(TAG, "Scanning app dir " + scanDir + " scanFlags=" + scanFlags
                    + " flags=0x" + Integer.toHexString(parseFlags));
        }

        ParallelPackageParser parallelPackageParser =
                new ParallelPackageParser(packageParser, executorService);

        // Submit files for parsing in parallel
        int fileCount = 0;
    	// 遍历所有文件
        for (File file : files) {
            final boolean isPackage = (isApkFile(file) || file.isDirectory())
                    && !PackageInstallerService.isStageName(file.getName());
            if (!isPackage) {
                // Ignore entries which are not packages
                continue;
            }
            // 使用parallelPackageParser.submit()方法异步地将其提交给PackageParser类来解析
            parallelPackageParser.submit(file, parseFlags);
            fileCount++;
        }
		...
    }
```

​	以上代码可以看到`scanDirLI`方法主要是遍历所有文件筛选是Apk文件，或者是一个目录，`isStageName`方法是判断当前文件是否为分阶段安装的数据，`parallelPackageParser.submit()`方法异步地将其提交给`PackageParser`类来解析。跟踪查看`submit`。

```java
public void submit(File scanFile, int parseFlags) {
        mExecutorService.submit(() -> {
            ParseResult pr = new ParseResult();
            Trace.traceBegin(TRACE_TAG_PACKAGE_MANAGER, "parallel parsePackage [" + scanFile + "]");
            try {
                pr.scanFile = scanFile;
                // 解析应用程序包
                pr.parsedPackage = parsePackage(scanFile, parseFlags);
            } catch (Throwable e) {
                pr.throwable = e;
            } finally {
                Trace.traceEnd(TRACE_TAG_PACKAGE_MANAGER);
            }
            try {
                // 返回数据
                mQueue.put(pr);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                // Propagate result to callers of take().
                // This is helpful to prevent main thread from getting stuck waiting on
                // ParallelPackageParser to finish in case of interruption
                mInterruptedInThread = Thread.currentThread().getName();
            }
        });
    }
```

​	继续跟踪`parsePackage`是如何解析的

```java
protected ParsedPackage parsePackage(File scanFile, int parseFlags)
            throws PackageParser.PackageParserException {
        return mPackageParser.parsePackage(scanFile, parseFlags, true);
    }
```

​	这里需要留意`mPackageParser`的类型是`PackageParser2`，而在AOSP10中，它的类型是`PackageParser`。继续查看`parsePackage`方法的实现。

```java
public ParsedPackage parsePackage(File packageFile, int flags, boolean useCaches)
            throws PackageParserException {
    	// 尝试从缓存中找解析结果
        if (useCaches && mCacher != null) {
            ParsedPackage parsed = mCacher.getCachedResult(packageFile, flags);
            if (parsed != null) {
                return parsed;
            }
        }

        long parseTime = LOG_PARSE_TIMINGS ? SystemClock.uptimeMillis() : 0;
        ParseInput input = mSharedResult.get().reset();
    	// 解析
        ParseResult<ParsingPackage> result = parsingUtils.parsePackage(input, packageFile, flags);
        if (result.isError()) {
            throw new PackageParserException(result.getErrorCode(), result.getErrorMessage(),
                    result.getException());
        }
		...
        return parsed;
    }
```

​	继续跟踪`parsingUtils.parsePackage`的实现。

```java
public ParseResult<ParsingPackage> parsePackage(ParseInput input, File packageFile,
            int flags)
            throws PackageParserException {
        if (packageFile.isDirectory()) {
            return parseClusterPackage(input, packageFile, flags);
        } else {
            return parseMonolithicPackage(input, packageFile, flags);
        }
    }
```

​	如果是一个目录，则说明这是一个集群版本`（cluster package）`的应用程序包，可能由多个应用程序组成。在这种情况下，它调用`parseClusterPackage`方法对应用程序包进行解析，并返回解析结果。

​	`parseClusterPackage`方法会遍历该目录下的所有文件，解析其中的每个应用程序，并将它们打包成一个`PackageParser.Package`集合返回。每个`PackageParser.Package`对象表示单独的一个应用程序。

​	如果`packageFile`不是一个目录，则说明这是一个单体版本`（monolithic package）`的应用程序包，只包含一个应用程序。在这种情况下，它调用`parseMonolithicPackage`方法对应用程序包进行解析，并返回解析结果。

​	`parseMonolithicPackage`方法会读取应用程序包的内容，并解析其中的`AndroidManifest.xml`文件和资源文件等信息，然后创建一个`PackageParser.Package`对象来表示整个应用程序，并返回该对象作为解析结果。

​	所以我们跟踪一条路线即可，接下来查看`parseMonolithicPackage`的实现代码。

```java
private ParseResult<ParsingPackage> parseMonolithicPackage(ParseInput input, File apkFile,
            int flags) throws PackageParserException {
        ...
        try {
            // 解析应用程序
            final ParseResult<ParsingPackage> result = parseBaseApk(input,
                    apkFile,
                    apkFile.getCanonicalPath(),
                    assetLoader, flags);
            if (result.isError()) {
                return input.error(result);
            }

            return input.success(result.getResult()
                    .setUse32BitAbi(lite.isUse32bitAbi()));
        } catch (IOException e) {
            return input.error(INSTALL_PARSE_FAILED_UNEXPECTED_EXCEPTION,
                    "Failed to get path: " + apkFile, e);
        } finally {
            IoUtils.closeQuietly(assetLoader);
        }
    }
```

​	继续查看`parseBaseApk`的实现代码。

```java
private ParseResult<ParsingPackage> parseBaseApk(ParseInput input, File apkFile,
            String codePath, SplitAssetLoader assetLoader, int flags)
            throws PackageParserException {
        final String apkPath = apkFile.getAbsolutePath();
		...
		// 读取AndroidMannifest.xml文件
        try (XmlResourceParser parser = assets.openXmlResourceParser(cookie,
                ANDROID_MANIFEST_FILENAME)) {
            final Resources res = new Resources(assets, mDisplayMetrics, null);
			// 调用另一个重载进行解析
            ParseResult<ParsingPackage> result = parseBaseApk(input, apkPath, codePath, res,
                    parser, flags);
            ...
            return input.success(pkg);
        } catch (Exception e) {
            return input.error(INSTALL_PARSE_FAILED_UNEXPECTED_EXCEPTION,
                    "Failed to read manifest from " + apkPath, e);
        }
    }
```

​	在这里看到读取`AndroidMannifest.xml`配置文件了，随后调用另一个重载进行解析。代码如下。

```java
private ParseResult<ParsingPackage> parseBaseApk(ParseInput input, String apkPath,
            String codePath, Resources res, XmlResourceParser parser, int flags)
            throws XmlPullParserException, IOException {
		...
        final TypedArray manifestArray = res.obtainAttributes(parser, R.styleable.AndroidManifest);
        try {
            final boolean isCoreApp =
                    parser.getAttributeBooleanValue(null, "coreApp", false);
            final ParsingPackage pkg = mCallback.startParsingPackage(
                    pkgName, apkPath, codePath, manifestArray, isCoreApp);
            // 解析Apk文件中xml的各种标记
            final ParseResult<ParsingPackage> result =
                    parseBaseApkTags(input, pkg, manifestArray, res, parser, flags);
            if (result.isError()) {
                return result;
            }

            return input.success(pkg);
        } finally {
            manifestArray.recycle();
        }
    }
```

​	继续查看`parseBaseApkTags`的实现代码。

```java
private ParseResult<ParsingPackage> parseBaseApkTags(ParseInput input, ParsingPackage pkg,
            TypedArray sa, Resources res, XmlResourceParser parser, int flags)
            throws XmlPullParserException, IOException {
        ...
        while ((type = parser.next()) != XmlPullParser.END_DOCUMENT
                && (type != XmlPullParser.END_TAG
                || parser.getDepth() > depth)) {
            ...
            // <application> has special logic, so it's handled outside the general method
            if (TAG_APPLICATION.equals(tagName)) {
                if (foundApp) {
                    ...
                } else {
                    foundApp = true;
                    result = parseBaseApplication(input, pkg, res, parser, flags);
                }
            } else {
                result = parseBaseApkTag(tagName, input, pkg, res, parser, flags);
            }

            if (result.isError()) {
                return input.error(result);
            }
        }
		...
        return input.success(pkg);
    }
```

​	检查`tagName`是否为`<application>`标记。如果是`<application>`标记，则表示当前正在解析应用程序包的主要组件，在该标记中会定义应用程序的所有组件、权限等信息。如果没有发现`<application>`标记，则继续递归调用处理其他标记。所以接下来查看`parseBaseApplication`方法的实现。

```java
private ParseResult<ParsingPackage> parseBaseApplication(ParseInput input,
            ParsingPackage pkg, Resources res, XmlResourceParser parser, int flags)
            throws XmlPullParserException, IOException {
        final String pkgName = pkg.getPackageName();
        int targetSdk = pkg.getTargetSdkVersion();

        TypedArray sa = res.obtainAttributes(parser, R.styleable.AndroidManifestApplication);
        try {
            ...
			// 解析应用程序包中基本APK文件的标志
            parseBaseAppBasicFlags(pkg, sa);
			...
            // 根据xml配置，对pkg的值做相应的修改
            if (sa.getBoolean(R.styleable.AndroidManifestApplication_persistent, false)) {
                // Check if persistence is based on a feature being present
                final String requiredFeature = sa.getNonResourceString(R.styleable
                        .AndroidManifestApplication_persistentWhenFeatureAvailable);
                pkg.setPersistent(requiredFeature == null || mCallback.hasFeature(requiredFeature));
            }

            if (sa.hasValueOrEmpty(R.styleable.AndroidManifestApplication_resizeableActivity)) {
                pkg.setResizeableActivity(sa.getBoolean(
                        R.styleable.AndroidManifestApplication_resizeableActivity, true));
            } else {
                pkg.setResizeableActivityViaSdkVersion(
                        targetSdk >= Build.VERSION_CODES.N);
            }
			...

        } finally {
            sa.recycle();
        }
		...
    	// 根据xml中的tag进行对应的处理
        while ((type = parser.next()) != XmlPullParser.END_DOCUMENT
                && (type != XmlPullParser.END_TAG
                || parser.getDepth() > depth)) {
            if (type != XmlPullParser.START_TAG) {
                continue;
            }
            final ParseResult result;
            String tagName = parser.getName();
            boolean isActivity = false;
            switch (tagName) {
                case "activity":
                    isActivity = true;
                    // fall-through
                case "receiver":
                    ParseResult<ParsedActivity> activityResult =
                            ParsedActivityUtils.parseActivityOrReceiver(mSeparateProcesses, pkg,
                                    res, parser, flags, sUseRoundIcon, input);

                    if (activityResult.isSuccess()) {
                        ParsedActivity activity = activityResult.getResult();
                        if (isActivity) {
                            hasActivityOrder |= (activity.getOrder() != 0);
                            pkg.addActivity(activity);
                        } else {
                            hasReceiverOrder |= (activity.getOrder() != 0);
                            pkg.addReceiver(activity);
                        }
                    }

                    result = activityResult;
                    break;
                case "service":
                    ParseResult<ParsedService> serviceResult =
                            ParsedServiceUtils.parseService(mSeparateProcesses, pkg, res, parser,
                                    flags, sUseRoundIcon, input);
                    if (serviceResult.isSuccess()) {
                        ParsedService service = serviceResult.getResult();
                        hasServiceOrder |= (service.getOrder() != 0);
                        pkg.addService(service);
                    }

                    result = serviceResult;
                    break;
                case "provider":
                    ParseResult<ParsedProvider> providerResult =
                            ParsedProviderUtils.parseProvider(mSeparateProcesses, pkg, res, parser,
                                    flags, sUseRoundIcon, input);
                    if (providerResult.isSuccess()) {
                        pkg.addProvider(providerResult.getResult());
                    }

                    result = providerResult;
                    break;
                case "activity-alias":
                    activityResult = ParsedActivityUtils.parseActivityAlias(pkg, res,
                            parser, sUseRoundIcon, input);
                    if (activityResult.isSuccess()) {
                        ParsedActivity activity = activityResult.getResult();
                        hasActivityOrder |= (activity.getOrder() != 0);
                        pkg.addActivity(activity);
                    }

                    result = activityResult;
                    break;
                default:
                    result = parseBaseAppChildTag(input, tagName, pkg, res, parser, flags);
                    break;
            }

            if (result.isError()) {
                return input.error(result);
            }
        }
		...
        return input.success(pkg);
    }
```

​	基本大多数的解析都在这里实现了，最后看看基本APK标志是如何解析处理的。`parseBaseAppBasicFlags`的实现如下。

```java
private void parseBaseAppBasicFlags(ParsingPackage pkg, TypedArray sa) {
        int targetSdk = pkg.getTargetSdkVersion();
        //@formatter:off
        // CHECKSTYLE:off
        pkg
                // Default true
                .setAllowBackup(bool(true, R.styleable.AndroidManifestApplication_allowBackup, sa))
                .setAllowClearUserData(bool(true, R.styleable.AndroidManifestApplication_allowClearUserData, sa))
                .setAllowClearUserDataOnFailedRestore(bool(true, R.styleable.AndroidManifestApplication_allowClearUserDataOnFailedRestore, sa))
                .setAllowNativeHeapPointerTagging(bool(true, R.styleable.AndroidManifestApplication_allowNativeHeapPointerTagging, sa))
                .setEnabled(bool(true, R.styleable.AndroidManifestApplication_enabled, sa))
                .setExtractNativeLibs(bool(true, R.styleable.AndroidManifestApplication_extractNativeLibs, sa))
                .setHasCode(bool(true, R.styleable.AndroidManifestApplication_hasCode, sa))
                // Default false
                .setAllowTaskReparenting(bool(false, R.styleable.AndroidManifestApplication_allowTaskReparenting, sa))
                .setCantSaveState(bool(false, R.styleable.AndroidManifestApplication_cantSaveState, sa))
                .setCrossProfile(bool(false, R.styleable.AndroidManifestApplication_crossProfile, sa))
                .setDebuggable(bool(false, R.styleable.AndroidManifestApplication_debuggable, sa))
                .setDefaultToDeviceProtectedStorage(bool(false, R.styleable.AndroidManifestApplication_defaultToDeviceProtectedStorage, sa))
                .setDirectBootAware(bool(false, R.styleable.AndroidManifestApplication_directBootAware, sa))
                .setForceQueryable(bool(false, R.styleable.AndroidManifestApplication_forceQueryable, sa))
                .setGame(bool(false, R.styleable.AndroidManifestApplication_isGame, sa))
                .setHasFragileUserData(bool(false, R.styleable.AndroidManifestApplication_hasFragileUserData, sa))
                .setLargeHeap(bool(false, R.styleable.AndroidManifestApplication_largeHeap, sa))
                .setMultiArch(bool(false, R.styleable.AndroidManifestApplication_multiArch, sa))
                .setPreserveLegacyExternalStorage(bool(false, R.styleable.AndroidManifestApplication_preserveLegacyExternalStorage, sa))
                .setRequiredForAllUsers(bool(false, R.styleable.AndroidManifestApplication_requiredForAllUsers, sa))
                .setSupportsRtl(bool(false, R.styleable.AndroidManifestApplication_supportsRtl, sa))
                .setTestOnly(bool(false, R.styleable.AndroidManifestApplication_testOnly, sa))
                .setUseEmbeddedDex(bool(false, R.styleable.AndroidManifestApplication_useEmbeddedDex, sa))
                .setUsesNonSdkApi(bool(false, R.styleable.AndroidManifestApplication_usesNonSdkApi, sa))
                .setVmSafeMode(bool(false, R.styleable.AndroidManifestApplication_vmSafeMode, sa))
                .setAutoRevokePermissions(anInt(R.styleable.AndroidManifestApplication_autoRevokePermissions, sa))
                .setAttributionsAreUserVisible(bool(false, R.styleable.AndroidManifestApplication_attributionsAreUserVisible, sa))
                // targetSdkVersion gated
                .setAllowAudioPlaybackCapture(bool(targetSdk >= Build.VERSION_CODES.Q, R.styleable.AndroidManifestApplication_allowAudioPlaybackCapture, sa))
                .setBaseHardwareAccelerated(bool(targetSdk >= Build.VERSION_CODES.ICE_CREAM_SANDWICH, R.styleable.AndroidManifestApplication_hardwareAccelerated, sa))
                .setRequestLegacyExternalStorage(bool(targetSdk < Build.VERSION_CODES.Q, R.styleable.AndroidManifestApplication_requestLegacyExternalStorage, sa))
                .setUsesCleartextTraffic(bool(targetSdk < Build.VERSION_CODES.P, R.styleable.AndroidManifestApplication_usesCleartextTraffic, sa))
                // Ints Default 0
                .setUiOptions(anInt(R.styleable.AndroidManifestApplication_uiOptions, sa))
                // Ints
                .setCategory(anInt(ApplicationInfo.CATEGORY_UNDEFINED, R.styleable.AndroidManifestApplication_appCategory, sa))
                // Floats Default 0f
                .setMaxAspectRatio(aFloat(R.styleable.AndroidManifestApplication_maxAspectRatio, sa))
                .setMinAspectRatio(aFloat(R.styleable.AndroidManifestApplication_minAspectRatio, sa))
                // Resource ID
                .setBanner(resId(R.styleable.AndroidManifestApplication_banner, sa))
                .setDescriptionRes(resId(R.styleable.AndroidManifestApplication_description, sa))
                .setIconRes(resId(R.styleable.AndroidManifestApplication_icon, sa))
                .setLogo(resId(R.styleable.AndroidManifestApplication_logo, sa))
                .setNetworkSecurityConfigRes(resId(R.styleable.AndroidManifestApplication_networkSecurityConfig, sa))
                .setRoundIconRes(resId(R.styleable.AndroidManifestApplication_roundIcon, sa))
                .setTheme(resId(R.styleable.AndroidManifestApplication_theme, sa))
                .setDataExtractionRules(
                        resId(R.styleable.AndroidManifestApplication_dataExtractionRules, sa))
                // Strings
                .setClassLoaderName(string(R.styleable.AndroidManifestApplication_classLoader, sa))
                .setRequiredAccountType(string(R.styleable.AndroidManifestApplication_requiredAccountType, sa))
                .setRestrictedAccountType(string(R.styleable.AndroidManifestApplication_restrictedAccountType, sa))
                .setZygotePreloadName(string(R.styleable.AndroidManifestApplication_zygotePreloadName, sa))
                // Non-Config String
                .setPermission(nonConfigString(0, R.styleable.AndroidManifestApplication_permission, sa));
        // CHECKSTYLE:on
        //@formatter:on
    }
```

​	相信你坚持跟踪到这里后，对于权限处理已经豁然开朗了，实际上总结就是，读取并解析xml文件，然后根据xml中配置的节点进行相应的处理，最终这些处理都是将值对应的设置给了`ParsingPackage`类型的对象`pkg`中。最终外层就通过拿到pkg对象，知道应该如何控制它的权限了。

### 6.5.3 修改APP默认权限

​	经过对源码的阅读，熟悉了APK对xml文件的解析流程后，想要为APP添加一个默认的权限就非常简单了。下面将为ROM添加一个联网权限：android.permission.INTERNET作为例子。只需要在`parseBaseApplication`函数中为`pkg`对象添加权限即可。

```java
private ParseResult<ParsingPackage> parseBaseApplication(ParseInput input,
            ParsingPackage pkg, Resources res, XmlResourceParser parser, int flags)
            throws XmlPullParserException, IOException {
        ...
		// add 添加联网权限
        List<String> requestedPermissions = pkg.getRequestedPermissions();
        String addPermissionName = "android.permission.INTERNET";
        if (!requestedPermissions.contains(addPermissionName)){

            pkg.addUsesPermission(new ParsedUsesPermission(addPermissionName, 0));

            Slog.w("mikrom","parseBaseApplication add android.permission.INTERNET " );
        }
		// add end
        boolean hasActivityOrder = false;
        boolean hasReceiverOrder = false;
        boolean hasServiceOrder = false;
        final int depth = parser.getDepth();
        int type;
        while ((type = parser.next()) != XmlPullParser.END_DOCUMENT
                && (type != XmlPullParser.END_TAG
                || parser.getDepth() > depth)) {
            ...
        }
        ...
        return input.success(pkg);
    }
```

​	理解源码中的实现原理后，有各种方式都能完成修改APP权限，由此可见，阅读跟踪源码观察实现原理是非常重要的手段。

## 6.6 进程注入

​	在上一小节中，通过对加载解析xml文件的流程进行分析，最终找到了合适的时机对默认权限进行修改，而在第三章的学习中，详细介绍了一个APP运行起来的流程，当对源码的运行流程有了足够的了解后，同样可以在其中找到合适的时机对普通用户的APP进行一些定制化的处理，例如对该进程进行注入，这一小节将介绍如何为用户进程注入jar包。

### 6.6.1 注入时机的选择

​	`ActivityThread`负责管理应用程序的主线程以及所有活动`Activity`的生命周期。通过`MessageQueue`和`Handler`机制与其他线程进行通信，处理来自系统和应用程序的各种消息。

​	在应用程序启动时，`ActivityThread`会被创建并开始运行，它会负责创建应用程序的主线程，并调用`Application`对象的`onCreate`方法初始化应用程序。同时，`ActivityThread`还会负责加载和启动应用程序中的第一个`Activity`，即启动界面`Splash Screen`或者主界面`Main Activity`，并处理`Activity`的生命周期事件，如`onCreate()、onResume()、onPause()`等。

​	所以可以在`ActivityThread`的调用中寻找合适的时机，那么什么叫合适的时机呢，可以将注入的需求进行整理，然后所有符合条件的调用时机都可以算作合适的时机。

​	注入时机尽量在一个仅调用一次的函数中，避免多次注入出现不可预料的异常情况。

​	注入时机分为早期和晚期，早期表示在一个调用链尽量靠前时机，这时进程的业务代码还没开始执行，就完成注入代码了，但是过早的时机会导致有些需要用到的数据还未准备就绪，例如`Application`未完成创建。如果你注入的代码无需涉及这些数据，那么可以选择尽量早的时机。例如在Zygote进程孵化的时机也是可以的。

​	第三章中介绍到的`handleBindApplication`就是比较合适的注入时机，主线程中通过调用这个方法来绑定应用程序，在该方法中创建了`Application`对象，并且调用了`attachBaseContext`方法和`onCreate`方法进行初始化。可以选择在创建`Application`对象后，就注入自己的jar包和so动态库。

### 6.6.2 注入jar包

​	在`handleBindApplication`方法中加一段注入jar包的方式和正常开发的APP中注入jar包并没有什么区别。在这个时机中是调用的onCreate方法，所以完成可以想象成是在onCreate中写一段注入代码。而onCreate中注入jar包在第五章，内置jar包中有详细介绍过。下面贴上当时的注入代码。

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
    }
```

​	唯一的区别仅仅在于，需要将注入的代码封装成一个方法，然后在`handleBindApplication`方法中，`Application`函数执行后进行调用。下面简单调整测试使用的jar包添加一个测试方法`injectJar`，代码如下。

```java
public class MyCommon {
    public static String getMyJarVer(){
        return "v1.0";
    }
    public static int add(int a,int b){
        return a+b;
    }
    public static void injectJar(){
        Log.i("MyCommon","injectJar enter");
    }
}

```

​	重新将测试的jar包编译后，解压并使用dx将classes.dex文件转换为jar包后内置到系统中。

```
unzip app-debug.apk -d app-debug

dx --dex --min-sdk-version=26 --output=./kjar.jar ./app-debug/classes.dex

cp ./kjar.jar ~/android_src/aosp12/framewoorks/native/myjar/

```

​	最后添加注入代码如下。

```java
private void InjectJar(){
    String jarPath = "/system/framework/kjar.jar";
    ClassLoader systemClassLoader=ClassLoader.getSystemClassLoader();
    String javaPath= System.getProperty("java.library.path");
    PathClassLoader pathClassLoader=new PathClassLoader(jarPath,javaPath,systemClassLoader);
    Class<?> clazz1 = null;
    try {
        // 通过反射调用函数
        clazz1 = pathClassLoader.loadClass("cn.mik.myjar.MyCommon");
        Method method = clazz1.getDeclaredMethod("injectJar");
        Object result = method.invoke(null);

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
    	InjectJar()
    }

}
```

​	准备就绪，编译并刷入手机中，安装任意app后，都会注入该jar包并打印日志。

​	注入so动态库同样和内置jar的步骤没有任何区别，直接通过在jar包中加载动态库即可，无需另外添加代码。
