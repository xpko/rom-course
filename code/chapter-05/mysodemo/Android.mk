LOCAL_PATH := $(call my-dir)

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
