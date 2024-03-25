#version = 1.0.0

import bs4
import webbrowser
import zipfile
import urllib3
import os
import requests
from win32com.client import Dispatch
from subprocess import CREATE_NO_WINDOW

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

###################### 경고 메시지 무시 #####################
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

###################### global 변수 선언 #####################
PYTHON_PATH = os.path.dirname(sys.executable)
CHROME_DRIVER_FOLER = "/chromedriver-win64/"
CHROME_EXE_FILE_NAME = "chromedriver.exe"
CHROME_ZIP_FILE_NAME = "chromedriver.zip"

PC_INSTALLED_CHROME_FILE = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
PC_DOWNLOADED_CHROMEDRIVER_FILE = PYTHON_PATH +  CHROME_DRIVER_FOLER + CHROME_EXE_FILE_NAME  #f"{PYTHON_PATH}/chromedriver-win64/chromedriver.exe"
URL_LASTEST_CHROMEDRIVER_LIST = 'https://googlechromelabs.github.io/chrome-for-testing/'

################## PC에 설치된 크롬 버전 얻기  ################
def get_pc_installed_chrome_version():
    global PC_INSTALLED_CHROME_FILE
    parser = Dispatch("Scripting.FileSystemObject")
    try:
        version = parser.GetFileVersion(PC_INSTALLED_CHROME_FILE)
    except Exception:
        return None
    return version

###### PC에 설치된 크롬과 연동 가능한 크롬드라이버 설치 사이트 얻기  #####
def get_compatible_chromedriver_url(chrome_version):
    global URL_LASTEST_CHROMEDRIVER_LIST
    
    response = requests.get(URL_LASTEST_CHROMEDRIVER_LIST, verify=False)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    compatible_ver_found = False
    for i in range(4):
        web_chromedriver_version = soup.find_all("tr", class_="status-ok")[i].find("code").text
        print(i, web_chromedriver_version)
        if chrome_version[:10] == web_chromedriver_version[:10]:
            print("일치되는 크롬 버전을 찾았습니다.")
            compatible_ver_found = True
            break
        
    down_url = ""
    if compatible_ver_found == True:
        down_url = f"https://storage.googleapis.com/chrome-for-testing-public/{web_chromedriver_version}/win64/chromedriver-win64.zip"
    
    return down_url

###########  최신 크롬드라이버 다운로드 가능한 사이트 보여주기 ###########
def show_chromedrivers():
    global PC_INSTALLED_CHROME_FILE
    global URL_LASTEST_CHROMEDRIVER_LIST
    #chrome_url = "https://googlechromelabs.github.io/chrome-for-testing/"
    #chrome_path = r'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
    webbrowser.get(f"{PC_INSTALLED_CHROME_FILE} %s").open(URL_LASTEST_CHROMEDRIVER_LIST)


##################### 크롬드라이버 다운로드(ZIP 파일 형태) ###################
def download_chromedriver():
    chrome_version = get_pc_installed_chrome_version()
    down_url = get_compatible_chromedriver_url(chrome_version)
    if down_url == "":
        show_chromedrivers()
        print("새창에 크롬 드라이버들을 직접 찾아서 다운로드 해야 합니다. ")
        return False

    with open(PYTHON_PATH +  CHROME_DRIVER_FOLER + CHROME_ZIP_FILE_NAME, "wb") as file:   
        response = requests.get(down_url, verify=False)               
        file.write(response.content)
        
    return True

##################### 다운로드한 ZIP파일 풀기 ##########################
def unzip_chromedriver():
    with zipfile.ZipFile(PYTHON_PATH +  CHROME_DRIVER_FOLER + CHROME_ZIP_FILE_NAME,"r") as zip_ref:
        zip_ref.extractall("./")

    os.remove(PYTHON_PATH +  CHROME_DRIVER_FOLER + CHROME_ZIP_FILE_NAME)


##################### 크롬 드라이버 구동하기   #########################
def start_chromedriver():
    global PC_DOWNLOADED_CHROMEDRIVER_FILE
    serv = Service(PC_DOWNLOADED_CHROMEDRIVER_FILE)
    #serv = Service(ChromeDriverManager().install())    
    serv.creation_flags = CREATE_NO_WINDOW
    driver = webdriver.Chrome(service = serv)

    return driver

###################################################################
def start():
    print("auto chromedriver version : 1.0.0")
    if os.path.exists(PC_DOWNLOADED_CHROMEDRIVER_FILE) == False:

        if os.path.exists(PYTHON_PATH +  CHROME_DRIVER_FOLER) == False:
            print("크롬 드라이버 폴더를 새로 생성합니다")
            os.mkdir(PYTHON_PATH +  CHROME_DRIVER_FOLER)
            
        print("크롬드라이버가 없어 다운로드를 시도힙니다...")
        if download_chromedriver() == True:
            unzip_chromedriver()
            print("크롬드라이버 구동을 시작합니다.")
            driver = start_chromedriver()
            return driver
        else:
            print("PC에 설치된 크롬과 버전이 맞는 크롬드라이버를 찾지 못했습니다...")    
    else:
        print("크롬드라이버가 이미 설치 되어있습니다.")
        print("크롬드라이버 구동을 시작해 봅니다.")
        try:
            driver = start_chromedriver()
            return driver
        except:
            print("최신 크롬드라이버 다운로드를 시도힙니다...")
            if download_chromedriver() == True:
                unzip_chromedriver()
                print("최신 크롬드이버를 설치하였습니다")
                print("크롬드라이버 구동을 다시 시작해 봅니다.")
                driver = start_chromedriver()
                return driver
            else:
                print("PC에 설치된 크롬과 버전이 맞는 크롬드라이버를 찾지 못했습니다...")
                print("크롬드라이버를 직접 설치해야 합니다.")
                show_chromedrivers()

                print("크롬 실행 -> 우측 상단 ...(세로) 클릭 -> 설정 -> chrome 정보 -> 자동 업데이트")
                sys.exit()
##############################################################################
