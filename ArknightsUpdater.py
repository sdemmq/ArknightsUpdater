import requests
from bs4 import BeautifulSoup
import subprocess
import time
import os
import os.path as op
import threading


#path='F:\Project\ArknightsUpdater'
#os.chdir(path)
#print('已切换工作目录')

arknightsurl = "https://ak.hypergryph.com/downloads/android_lastest"

apklocation=r'.\apk\明日方舟.apk'




def GetRecentArknightsVersion()->str:
    headers_={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'}

    response=requests.get(r"https://www.taptap.cn/app/70253/all-info?platform=android",headers=headers_)


    if response.ok :

        soup=BeautifulSoup(response.content.decode('utf-8'),'html.parser')
        allprice=soup.find_all(attrs={"class":"tap-text tap-text__one-line paragraph-m14-w14 gray-08 info-form__item-text"})
        for i in allprice:
            
            startlocation = str(i).find('>')+9
            version=str(i)[startlocation:startlocation+6]
            if version.count('.') == 2:
                return (version)
def GetYourArknightsVersion():
               

    cmd='adb shell pm dump com.hypergryph.arknights | grep "version"'
    #print(cmd)
    result = subprocess.run(cmd,capture_output=True)
                
    result_str=result.stdout.decode('utf-8')
    startlocation=result_str.find('versionName=')+12
    endlocation=startlocation+6
    version=result_str[startlocation:endlocation]
    if version != "" and version.find('.') !=-1:
        return version
    else:
        print("请先启动模拟器")
        quit()

def IsNeedupdate():
    print('最新版本',GetRecentArknightsVersion())
    print('您的版本',GetYourArknightsVersion())
    return GetRecentArknightsVersion() != GetYourArknightsVersion()
def countdown(t):


    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(f"倒计时:{timeformat}", end='\r')
        time.sleep(1)
        t -= 1


    print('倒计时结束')

def download_file(url,save_file,chunk_size=8192):
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

def install_apk(apk_path, overwrite=True, grant_permissions=True, install_location=None):
    """
    使用 ADB 安装 APK 文件
    
    参数:
        apk_path (str): APK 文件的绝对路径或相对路径
        overwrite (bool): 是否覆盖安装已存在的应用（-r 参数）
        grant_permissions (bool): 是否自动授予所有权限（-g 参数）
        install_location (str): 安装位置，可选值：'auto'(-a)、'internal'(-f)、'external'(-s)
    
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
    if install_location == "auto":
        adb_command.append("-a")
    elif install_location == "internal":
        adb_command.append("-f")
    elif install_location == "external":
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

        
         


        if download_file(arknightsurl,apklocation):
            
            if install_apk(apklocation):
                if not IsNeedupdate():
                    
                    print('更新成功')
                    os.remove(apklocation)
                    print("清理安装包成功")
                    quit()
                else:
                    print("因未知原因更新失败")

    else:
        print("已是最新版本")

print('初始化完成')

UpdateArknights()



