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
      // We have a native method here without code. Then it should have the generic JNI
      // trampoline as entrypoint.
      // TODO: this doesn't handle all the cases where trampolines may be installed.
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



## 6.6 进程注入器



## 6.7 修改APP默认权限

### 6.7.1 APP权限介绍



### 6.7.2 APP权限的源码跟踪



### 6.7.3 AOSP10下的默认权限修改

