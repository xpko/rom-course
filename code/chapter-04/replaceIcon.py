import os
import shutil
import subprocess

# 执行cmd命令
def exec(cmd):
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE  # 重定向输入值
    )
    proc.stdin.close()  # 既然没有命令行窗口，那就关闭输入
    result = proc.stdout.read()  # 读取cmd执行的输出结果（是byte类型，需要decode）
    proc.stdout.close()
    return result.decode(encoding="utf-8")

# 替换图标
def replacePng(target,appName):
    # 搜索该路径下的图标
    cmdRes = exec(f"find /home/king/android_src/mikrom12_gitlab/packages/ -name {target}")
    filePathList = cmdRes.split("\n")
    curpath=os.getcwd()
	# 遍历所有搜到的结果
    for filepath in filePathList:
        if filepath=="":
            continue
        # 为了避免其他应用的同名素材图标，所以使用appName过滤一下
        if appName not in filepath:
            continue
        print('Found file: ' + filepath)
        # 先将文件进行备份
        shutil.copy(filepath,filepath+".bak")
        # 然后将当前目录准备好的替换文件复制进去
        replacePath=curpath+"/images/"+target
        # 如果新文件不存在，则结束该文件的替换
        if os.path.exists(replacePath)==False:
            print("not found replace file:",replacePath)
            break
        shutil.copy(replacePath, filepath)

# 使用备份的文件还原该图标
def unReplacePng(target):
    # 查找目标文件
    cmdRes = exec(f"find /home/king/android_src/mikrom12_gitlab/frameworks/base/packages/ -name {target}")
    filePathList = cmdRes.split("\n")
    # 遍历所有结果
    for filepath in filePathList:
        if filepath=="":
            continue
        print('Found file: ' + filepath)
        # 备份文件如果存在，则将其还原
        bakfile=filepath + ".bak"
        if os.path.exists(bakfile):
            shutil.copy(bakfile, filepath)
            print("unReplace file:",bakfile)

def main():
    # 替换为新素材
    replacePng('ic_launcher_settings.png',"Setting")
    replacePng('ic_contacts_launcher.png',"Contacts")
    replacePng('ic_launcher_calendar.png',"Calendar")
	
    # 还原素材
    # unReplacePng('ic_launcher_settings.png')
    # unReplacePng('ic_contacts_launcher.png')
    # unReplacePng('ic_launcher_calendar.png')

if __name__ == '__main__':
    main()
