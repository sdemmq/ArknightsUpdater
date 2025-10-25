import requests
from bs4 import BeautifulSoup
import subprocess
import os



#path='F:\Project\ArknightsUpdater'
#os.chdir(path)
#print('已切换工作目录')

arknightsurl = "https://ak.hypergryph.com/downloads/android_lastest"#yj方舟安装包下载链接

apkpath=r'.\apk\明日方舟.apk'

def CreateDirectory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"目录 '{directory_path}' 已创建！")
    else:
        print(f"目录 '{directory_path}' 已存在。")


CreateDirectory(os.path.dirname(apkpath))
def GetRecentArknightsVersion()->str:
    headers_={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'}

    response=requests.get(r"https://www.taptap.cn/app/70253/all-info?platform=android",headers=headers_)


    if response.ok :#爬取taptap，获取版本号

        soup=BeautifulSoup(response.content.decode('utf-8'),'html.parser')
        allprice=soup.find_all(attrs={"class":"tap-text tap-text__one-line paragraph-m14-w14 gray-08 info-form__item-text"})
        for i in allprice:
            
            startlocation = str(i).find('>')+9
            version=str(i)[startlocation:startlocation+6]
            if version.count('.') == 2:#看哪一项有两个点,那就是版本号
                return (version)
def GetYourArknightsVersion():#通过命令获取模拟器中明日方舟版本号
               

    cmd='adb shell pm dump com.hypergryph.arknights | grep "version"'
    #print(cmd)
    result = subprocess.run(cmd,capture_output=True)
                
    result_str=result.stdout.decode('utf-8')
    startlocation=result_str.find('versionName=')+12
    endlocation=startlocation+6
    version=result_str[startlocation:endlocation]
    if version != "" and version.find('.') !=-1:#防止返回空值造成后续出现问题
        return version
    else:
        print("请先启动模拟器")
        quit()#直接退出(doge

def IsNeedupdate()->bool:#判断是否需要更新
    print('最新版本',GetRecentArknightsVersion())
    print('您的版本',GetYourArknightsVersion())
    return GetRecentArknightsVersion() != GetYourArknightsVersion()
"""
def countdown(t):#用来倒计时的，不过好像用不上了


    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(f"倒计时:{timeformat}", end='\r')
        time.sleep(1)
        t -= 1


    print('倒计时结束')
"""
def DownloadFile(url,save_file,chunk_size=8192):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(save_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    if total_size == 0:
                        done = 0
                    else:
                        done = int(50 * downloaded_size / total_size)
                    
                    print(f"\r[{'█' * done}{' ' * (50 - done)}] {round(downloaded_size/(1024*1024))}/{total_size/(1024*1024)} MB", end='')
        
        print("\n下载完成!")
        return(True)
    except requests.exceptions.RequestException as e:
        print(f"请求错误：{e}")

def InstallApk(apk_path, overwrite=True, grant_permissions=True, install_path=None):#这是AI写的
    """
    使用 ADB 安装 APK 文件
    
    参数:
        apk_path (str): APK 文件的绝对路径或相对路径
        overwrite (bool): 是否覆盖安装已存在的应用（-r 参数）
        grant_permissions (bool): 是否自动授予所有权限（-g 参数）
        install_path (str): 安装位置，可选值：'auto'(-a)、'internal'(-f)、'external'(-s)
    
    返回:
        tuple: (安装是否成功, 执行结果信息)
    """
    # 检查 APK 文件是否存在
    if not os.path.exists(apk_path):
        return False, f"错误：APK 文件不存在 - {apk_path}"
    
    # 构建 ADB 命令
    adb_command = ["adb", "install"]
    
    # 添加安装参数
    if overwrite:
        adb_command.append("-r")  # 覆盖安装
    if grant_permissions:
        adb_command.append("-g")  # 授予所有权限
    if install_path == "auto":
        adb_command.append("-a")
    elif install_path == "internal":
        adb_command.append("-f")
    elif install_path == "external":
        adb_command.append("-s")
    
    # 添加 APK 文件路径（转换为绝对路径，避免相对路径问题）
    adb_command.append(os.path.abspath(apk_path))
    
    try:
        # 执行命令并捕获输出（中文支持）
        result = subprocess.run(
            adb_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8"
        )
        output = result.stdout
        
        # 判断安装结果
        if "Success" in output:
            print(f"安装成功：{apk_path}\n{output.strip()}")
            return True
        else:
            print(f"安装失败：{apk_path}\n{output.strip()}")
            return False
    
    except Exception as e:
        return False, f"执行命令出错：{str(e)}"


def UpdateArknights():
    

    

    if IsNeedupdate() :
        print('您的明日方舟需要更新')


        if DownloadFile(arknightsurl,apkpath) :#先下载
            
            if InstallApk(apkpath):#通过命令行安装
                if not IsNeedupdate():#检查是否更新成功
                    
                    print('更新成功')
                    os.remove(apkpath)#删掉安装包
                    print("清理安装包成功")
                    quit()#退出
                else:
                    print("因未知原因更新失败")

    else:
        print("已是最新版本")

print('初始化完成')

UpdateArknights()



