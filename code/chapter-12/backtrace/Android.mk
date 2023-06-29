
#--------------------------------
include $(CLEAR_VARS)

LOCAL_MODULE := libxdl
LOCAL_SRC_FILES_arm := libxdl.so
LOCAL_SRC_FILES_arm64 := libxdl_arm64.so
LOCAL_MODULE_TARGET_ARCHS:= arm arm64
LOCAL_MULTILIB := both
LOCAL_MODULE_SUFFIX := .so
LOCAL_MODULE_CLASS := SHARED_LIBRARIES
LOCAL_MODULE_TAGS := optional
LOCAL_SHARED_LIBRARIES := liblog

include $(BUILD_PREBUILT)

#--------------------------------
include $(CLEAR_VARS)

LOCAL_MODULE := libxunwind
LOCAL_SRC_FILES_arm := libxunwind.so
LOCAL_SRC_FILES_arm64 := libxunwind_arm64.so
LOCAL_MODULE_TARGET_ARCHS:= arm arm64
LOCAL_MULTILIB := both
LOCAL_MODULE_SUFFIX := .so
LOCAL_MODULE_CLASS := SHARED_LIBRARIES
LOCAL_MODULE_TAGS := optional
LOCAL_SHARED_LIBRARIES := liblog libxdl

include $(BUILD_PREBUILT)

#--------------------------------
include $(CLEAR_VARS)

LOCAL_MODULE := libkbacktrace
LOCAL_SRC_FILES_arm := libkbacktrace_32.so
LOCAL_SRC_FILES_arm64 := libkbacktrace_64.so
LOCAL_MODULE_TARGET_ARCHS:= arm arm64
LOCAL_MULTILIB := both
LOCAL_MODULE_SUFFIX := .so
LOCAL_MODULE_CLASS := SHARED_LIBRARIES
LOCAL_MODULE_TAGS := optional
LOCAL_SHARED_LIBRARIES := liblog libxunwind

include $(BUILD_PREBUILT)