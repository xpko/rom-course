# 第四章 系统美化 #

## 4.1 系统美化简介

​	AOSP的UI界面是非常简陋的，其原因是由于AOSP是一个开源的项目，主要面向开发人员和技术爱好者。AOSP并不是为了提供最终用户的优美外观而设计的，而是用于供开发人员进行二次开发。此外，AOSP还旨在提供一个实验平台，以便测试新的Android功能和特性。因此，AOSP界面相对简陋，主要是为了加快开发和测试过程，而不是提供给最终用户一个完整的Android体验。当然，用户也可以使用第三方界面，如各大手机厂商自家的界面或其他主题桌面等，来定制自己的Android体验，而这个打造UI展示的过程，就是对系统进行美化了。通常情况下，常见的对UI进行美化大致分为如下几项：

​	更换主题：可以在Google Play Store中下载各种主题软件，使Android的用户界面变得更加个性化。

​	自定义图标：使用图标包来替换默认的应用图标，为应用程序打造更加独特的外观。

​	安装桌面主题：可以下载和安装各种桌面主题应用程序，如Nova Launcher、Apex Launcher等，来定制主屏幕和菜单。

​	动态壁纸：将Android设备的背景设置为动态图片或视频，并可以使其与其他美化应用程序相互配合。

​	安装定制字体：可以下载和安装自己喜欢的字体，使Android系统上的应用程序和菜单更加丰富多彩。

​	使用第三方启动屏幕：像MIUI、华为EMUI等ROM都提供了自己的启动屏幕，使用第三方启动屏幕会更有个性化并提升用户体验。

​	自定义状态栏和导航栏：root后，可以使用Xposed框架来替换状态栏和导航栏。

​	Android UI美化需求的目的是提高用户体验、突出品牌形象、展示产品价值和增加营销价值。设计美观、符合使用习惯、便于操作的用户界面对于Android设备的吸引力和实用性非常重要。下面简单介绍一下常见对美化系统的需求。

​	个性化：许多用户希望能够个性化自己的手机界面，让它看起来更加独特和有趣。这可以通过更改主题、图标、壁纸、字体等实现。

​	提高用户体验：美化UI还有一个目的是为了提高用户体验。优秀的用户界面可以提高用户的舒适度、使用效率和满意度，从而吸引更多的用户。

​	提高产品价值：一个好看的UI更容易吸引用户，从而提高产品的价值。这对于Android应用开发商或者手机厂商来说尤为重要。

​	突出品牌形象：对于企业，使其品牌形象在Android界面中得到突出展示也是有一定需要的，通过UI美化营造品牌形象。

​	凸显功能 : 突出重要功能，提高用户感知度和使用体验，可以通过UI设计实现。

​	改善可用性: 使用条件恶劣的环境下设计UI，如夜间、低光、震动等，来提高系统的可用性。

​	用户群体区分：美化UI还可以通过设计不同款式的主题来适应不同群体的需求，例如儿童、青少年、年轻人、老年人等。

​	下图展示的是Google官方的Android Rom桌面图以及自己编译AOSP的桌面图。

![未标题-1](.\images\未标题-1.jpg)

​	从上图中可以看处明显差异，Google官方的ROM相较于AOSP ROM多了一些功能和应用，例如：

​	谷歌应用套件：Google Mobile Services（GMS）包含了各种谷歌应用，如Gmail、Google Maps、Play商店等等。这些应用在AOSP ROM中是没有的。

​	谷歌助手：Google Assistant是谷歌推出的语音助手，旨在为用户提供更好的服务体验。该功能只会在谷歌官方ROM中内置。

​	谷歌照片：该应用提供了许多强大的相册管理和编辑功能，支持实时照片备份和共享。在谷歌官方ROM中预置了该应用。

​	谷歌相机：该相机应用在图片处理方面表现出色，包括HDR+、夜间拍摄等多种特效。同样只会在谷歌官方ROM中内置。

​	谷歌智能锁屏：谷歌智能锁屏可以学习用户的用习惯，预测用户可能要进行的操作，并以最快的速度为用户提供相关选项，比如预测下一个目的地并提供路线规划等等。

​	为了能够使第三方ROM能方便的搭载Google套装，Google 官方提供了一个应用与服务集合GApps，包括谷歌商店、谷歌地图、谷歌浏览器、谷歌日历、Gmail等等，如果我们想要的是一个界面类似官方ROM的，直接从官网：`https://opengapps.org/`下载GApps刷入即可。

​	接下来我们将围绕如何自己修改美化ROM进行展开。

## 4.2 常见的系统美化方式

​	UI界面美化并不是一件非常难的事情，随着用户的需求，有着各类产品可以满足我们方便快捷的美化Android的界面展示。这里我们从简易到复杂的几种方式进行逐一介绍。

​	最简单的美化方式，就是直接使用一些管理主题壁纸图标的App来管理UI界面资源，这种方式我们无需对美化过程进行了解，只需要挑选喜欢的资源进行替换就能完成对部分UI界面进行变动。缺点就是较为被动，App提供的功能并不能完全满足一些人的定制需求。这种方式通常适用于普通Android用户。

​	其次是使用ROM编辑类的工具，将编译好的镜像导入，然后由工具进行解析后，再修改主题，图标等。最后替换资源生成新的镜像，这种方式同样不需要我们深入了解具体美化的原理，但是和上一种相同的问题，提供的功能有限，并且类似的工具非常少见。并且还需要有一定的刷机经验。这种方式适用于一些Android发烧友。

​	最后就是从原理层面了解资源所在位置，如何修改Android源码替换资源。实现对系统UI的定制化，从根本上解决美化系统的问题，编译出来的镜像直接刷机后就能获得美化后的界面。这种定制方式的难度最高，同时也是最根源的办法。当我们掌握原理后，那么以上两种方式是如何做到美化的同样也会了如指掌。接下来，我们将先对原理性的知识进行了解。

## 4.3 UI界面资源

​	我们可以直接通过修改Android源码中对资源的配置，达到修改系统UI的目的，大多数的系统UI相关的资源和配置都存放在目录`frameworks/base/core/res/res/`。我们可以找到与主题相关的资源文件，通过修改这些资源文件中的属性来实现改变 整个系统UI的外观样式，而图标相关的素材一般在这个目录下的`drrawable-*`的子目录中。我们可以直接替换图标素材来实现修改图标。

​	在源码编译刷入手机后，在手机中会有默认自带文件`./system/framework/framework-res.apk`，这是存放Android系统UI界面的资源文件，图片、布局、颜色、字符串等。它包含了 Android Framework 中的所有公共资源。当Android应用程序需要使用系统级的UI资源时，就可以访问并使用这些资源。

​	由此可以看的出，其实前面介绍的几种方式都是相同的原理。软件进行修改系统UI实际是对`framework-res.apk`进行处理，而从源码层面处理，也是对`frameworks/base/core/res/`进行修改和替换处理。

​	`framework-res.apk` 和 `SystemUI.apk` 都是 Android 操作系统的应用程序包，`SystemUI.apk`同样也是系统UI相关的，但是他们的主要功能不同。

​	1、`framework-res.apk `包含了 Android 操作系统的核心 UI 组件（资源文件），例如系统主题、UI 图标、颜色的定义、字体、过渡动画等等。这些资源文件是 Android 操作系统的一部分，可用于在 Android 应用程序中构建 UI 或定制 Android 操作系统的 UI。

​	2、`SystemUI.apk` 是 Android 操作系统的一个关键 UI 组件，它负责设备状态栏和通知管理，锁定屏幕上的日期和时间, 系统UI 中的图标、通知中心等等。当用户接收到来自应用程序或系统的通知时，负责将通知以可视化的方式展示给用户，并允许用户控制通知和设备状态栏的设置。

​	虽然两个应用程序包目的不同，但在 Android 操作系统中，它们都是极为重要的组成部分。由于 `framework-res.apk` 包含了 Android 操作系统的核心资源文件，因此它也被包括在 `SystemUI.apk` 中使用的资源文件中。这类系统应用程序包，通常不能被用户直接安装或卸载。不过，该应用程序包可以被理解为 Android 系统的一部分，针对其进行开发将有助于开发人员了解并扩展 Android 系统界面。

## 4.4  修改壁纸

​	在前文中的图文和Google官方ROM对比的界面，就是Android的UI界面中的壁纸了，壁纸是在手机主页面也就是Launcher中背景图，壁纸可以在手机中进行切换修改，同样我们也可以直接修改掉默认的壁纸，默认壁纸的路径是`frameworks/base/core/res/res/drawable-nodpi/default_wallpaper.png`。下图是AOSP中的默认壁纸。

![image-20230305152441883](.\images\image-20230305152441883.png)

​	知道壁纸素材的路径后，可以通过对这个素材进行替换来达到目的，同样也可以通过查找设置的地方，修改默认设置选项，将壁纸切换为另一张图片来达到修改壁纸的目的，前者的好处在于简单快捷，替换素材即可。而后者在于稳妥，随时可以调整切换回原素材。替换的方式较为简单就不再细说，这里我们看看通过修改设置的实现。

​	首先我们找到一个新的壁纸素材命令为`new_wallpaper.png`，然后放到目录`frameworks/base/core/res/res/drawable-nodpi/`下，并且在res目录下的`values/symbols.xml`中添加相应的配置。

```
...
<!-- 在default_wallpaper下面添加一条新数据 -->
<java-symbol type="drawable" name="default_wallpaper" />
<java-symbol type="drawable" name="new_wallpaper" />
...
```

接下来我们先看看源码了解一下壁纸设置的关键逻辑。

```java
public class WallpaperManager {
    ...
    private static final String PROP_WALLPAPER = "ro.config.wallpaper";
    private static final String PROP_LOCK_WALLPAPER = "ro.config.lock_wallpaper";
    private static final String WALLPAPER_CMF_PATH = "/wallpaper/image/";
	...
    public static InputStream openDefaultWallpaper(Context context, @SetWallpaperFlags int which) {
        final String whichProp;
        final int defaultResId;
        if (which == FLAG_LOCK) {
            return null;
        } else {
            whichProp = PROP_WALLPAPER;
            // 原本默认使用default_wallpaper，修改成我们最新的new_wallpaper
//             defaultResId = com.android.internal.R.drawable.default_wallpaper;
            defaultResId = com.android.internal.R.drawable.new_wallpaper;
        }
        // 优先从属性ro.config.wallpaper中获取一个默认的壁纸路径
        final String path = SystemProperties.get(whichProp);
        final InputStream wallpaperInputStream = getWallpaperInputStream(path);
        if (wallpaperInputStream != null) {
            return wallpaperInputStream;
        }
        // 属性路径获取失败后，尝试从cmf路径中获取默认壁纸
        final String cmfPath = getCmfWallpaperPath();
        final InputStream cmfWallpaperInputStream = getWallpaperInputStream(cmfPath);
        if (cmfWallpaperInputStream != null) {
            return cmfWallpaperInputStream;
        }
        // 前两个失败的情况，从默认资源文件中获取默认壁纸
        try {
            return context.getResources().openRawResource(defaultResId);
        } catch (NotFoundException e) {
            // no default defined for this device; this is not a failure
        }
        return null;
    }

    private static InputStream getWallpaperInputStream(String path) {
        if (!TextUtils.isEmpty(path)) {
            final File file = new File(path);
            if (file.exists()) {
                try {
                    return new FileInputStream(file);
                } catch (IOException e) {
                    // Ignored, fall back to platform default
                }
            }
        }
        return null;
    }

    private static String getCmfWallpaperPath() {
        return Environment.getProductDirectory() + WALLPAPER_CMF_PATH + "default_wallpaper_"
                + VALUE_CMF_COLOR;
    }
    ...
}

```

​	从源码中看到可以从三个地方获取默认壁纸，同样想要修改也能从这三个方式着手，比如添加一个属性设置默认壁纸路径，或者修改cmfpath的路径设置默认壁纸，最后就是修改资源文件名来设置默认壁纸。这里我们采用的是最后一种。

