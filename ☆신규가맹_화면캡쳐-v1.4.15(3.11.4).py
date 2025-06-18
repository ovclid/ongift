## import 모듈
import os
import glob
import io
import sys
import time
import datetime
import shutil
import base64, uuid, json
from PIL import Image
from pdf2image import convert_from_path
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#import ss_auto_chromedriver as ss_driver

# https://googlechromelabs.github.io/chrome-for-testing/

## 크롬 웹드라이버 구동
def start_webdriver():
    
    #serv = Service(r"C:\chromedriver\chromedriver.exe")
    #serv.creation_flags = CREATE_NO_WINDOW   

    
        
    #driver = ss_driver.start()
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    driver.get("https://www.ongift.or.kr/")
    time.sleep(2)
    
    return driver

def popup_close(driver):
    close_ele_class = 'x-icon-el.x-font-icon.x-tool-type-close'
    close_eles = driver.find_elements(By.CLASS_NAME, close_ele_class)

    for i in range(len(close_eles)):
        try:
            close_eles[i].click()
        except:
            continue
        
## 온누리가맹점 사이트 로그인
def login_ongift(driver):
    ele = driver.find_element("id", "userId")
    userid = os.environ.get("PY_ONNURI_ID") + ""
    
    ele.send_keys(userid)
    
    time.sleep(1)

    ele = driver.find_element("id", "userPw")
    userPw = os.environ.get("PY_ONNURI_PW") + ""
    ele.send_keys(userPw)
    time.sleep(1)

    ele = driver.find_element("class name", "btn.btn-primary.btn-block.btn-large")
    ele.click()

    """
    time.sleep(5)

    input("OTP 입력 대기중입니다. 입력 확인 후 아무키나 눌러 주세요...")
    """
    print("OTP 입력을 10분동안 대기중입니다. 10분후에는 프로그램을 다시 시작해 주세요...")
    WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.CLASS_NAME, "x-treelist-item-text")))
    
    time.sleep(2)
    #popup_close(driver)
    
    try:
        popup_class = 'x-dialog.x-panel.x-container.x-component.x-bordered.x-header-position-top.x-heighted.x-widthed.x-floated.x-shadow.x-root.x-managed-borders.x-paint-monitored.x-size-monitored'
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, popup_class)))
        print("팝업 창을 종료합니다.")

        popup_close(driver)
        #close_ele_class = 'x-icon-el.x-font-icon.x-tool-type-close'
        #close_eles = driver.find_elements(By.CLASS_NAME, close_ele_class)
        #close_eles[-1].click()
    except TimeoutException as e:
        print("별도의 팝업 창이 없어 그대로 진행합니다.")
    
    eles = driver.find_elements("class name", "x-treelist-item-text")
    eles[7].click()   # 가맹업무관리
    time.sleep(1)

    eles[8].click()   # 신규가맹관리
    time.sleep(3)

def read_file(file_name):
    try:
        file = open(file_name, encoding = "utf-8")
        result = []
        exception = []
        file_contents = file.readlines()

        for content in file_contents:
            content = content.replace("\n", "")
            if content[0] == '#' :
                exception.append(content)
            else:
                result.append(content)
        
        #contents_list = [sub.replace("\n", "") for sub in file.readlines()]
        #print("------------------------------------------------")
        print("검색 대상 : ", result)
        print("검색 제외 : ", exception)
        file.close()
    except:
        print(f"{file_name} 분석 오류")
        return []
    
    return result

## 새로운 폴더 생성하기
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('에러 : 폴더 만들기 실패하였습니다. ' +  directory)
        sys.exit()

## 신규 신청 가맹점의 정보 화면 캡쳐하기(3번에 나눠서)
def screen_capture( ):
    print("화면 캡쳐 진행중....")
    #time.sleep(2)
    new_store_info_class = "x-panel.x-container.x-component.x-bordered.x-widthed.\
x-header-position-top.x-managed-borders.x-paint-monitored.\
x-size-monitored.x-dock-item.x-docked-right.x-noborder-trb"
 
    #WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, new_store_info_class)))
    store_info_element = driver.find_element("class name", new_store_info_class)
    store_info_element.click()    # (좌측) 신규 가맹점 클릭 -> (우측) 정보영역에 표시하기
    popup_close(driver) #close_error_dialog()      ###### 중북 조회 팝업 확인(늦게 뜨는 경우 대비) #####
    time.sleep(2)
    #WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
    body = driver.find_element("css selector", 'body')

    images = []
    images.append(store_info_element.screenshot_as_png)

    for i in range(2):
        body.send_keys(Keys.PAGE_DOWN)   # 스크롤 영역 한번 클릭하기
        time.sleep(1)
        popup_close(driver)      ###### 중북 조회 팝업 확인(늦게 뜨는 경우 대비) #####
        images.append(store_info_element.screenshot_as_png)

    for i in range(len(images)):  # 이미지를 BytesIO형태로 변환하기
        images[i] = Image.open(io.BytesIO(images[i]))
        

    """
    for i in range(len(images)):  # 이미지를 BytesIO형태로 변환하기
        if i == len(images) - 1:
            image = Image.open(io.BytesIO(images[i]))
            original_size = image.size  # (width, height) -> (400, 672)
            crop_box = (0, original_size[1] - 72, original_size[0], original_size[1])
            cropped_image = image.crop(crop_box)

            cropped_image.save(f"cropped_screenshot_{i}.png")

            output_io = io.BytesIO()
            cropped_image.save(output_io, format="PNG")
            images[i] = output_io.getvalue()  # 바이트 데이터로 저장
        
            images[i] = cropped_image
        else:
            images[i] = Image.open(io.BytesIO(images[i]))
    """ 
    
    time.sleep(1)
    return images

"""
## 첨부파일(사업자등록증) 다운로드 하기
def download_attachedfile():
    ele = driver.find_element("tag name", "h")
    ele.click()
    time.sleep(4)
    
    fileinfo_eles = driver.find_elements("class name", "ag-center-cols-clipper")
    download_filename = fileinfo_eles[5].text.split("\n")[1]

    files = glob.glob(f"{download_folder}*")
    lastes_file = max(files, key = os.path.getctime)
    lastes_file = lastes_file.split("\\")[-1]
    if (lastes_file != download_filename) :
        print(f"{lastes_file} 다운로드에 문제 발생 가능(중복 또는 다운로드중..)!!!")
        time.sleep(4)
        lastes_file = max(files, key = os.path.getctime)
        lastes_file = lastes_file.split("\\")[-1]

    body = driver.find_element("css selector", 'body')
    for i in range(3):                # 스크롤을 처음으로 되돌리기
        body.send_keys(Keys.PAGE_UP)
        time.sleep(0.2)

    time.sleep(2)
    return lastes_file
"""

## 다운로드 완료까지 기다리는 함수
def download_wait(directory, timeout, nfiles=None):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        popup_close(driver)    ###### 중북 조회 팝업 확인(늦게 뜨는 경우 대비) #####
        
        time.sleep(1)
        dl_wait = False
        files = os.listdir(directory)
        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in files:
            if fname.endswith('.crdownload') or fname.endswith('.tmp'):
                dl_wait = True

        seconds += 1
    return seconds

## 첨부파일들(사업자등록증 등) 다운로드 하기
def download_attachedfiles():
    global download_folder
    eles = driver.find_elements("tag name", "h")

    lastes_files = []

    for i, ele in enumerate(eles):
        if i >= 2:       # 첨부파일 2개까지만 처리
            break
        
        ele.click()
        time.sleep(2) # 파일 다운로드 시작 후 잠시 대기
        download_wait(download_folder, 10, nfiles=None)
        
        fileinfo_eles = driver.find_elements("class name", "ag-center-cols-clipper")
        download_filename = fileinfo_eles[5].text.split("\n")[i*3 + 1]

        files = glob.glob(f"{download_folder}*")
        lastes_file = max(files, key = os.path.getctime)
        lastes_file = lastes_file.split("\\")[-1]
        if (lastes_file != download_filename) :
            print(f"{lastes_file} 다운로드에 문제 발생 가능(중복 또는 다운로드중..)!!!")
            #time.sleep(4)
            
            lastes_file = max(files, key = os.path.getctime)
            lastes_file = lastes_file.split("\\")[-1]

        lastes_files.append(lastes_file)

    body = driver.find_element("css selector", 'body')
    for i in range(4):                # 스크롤을 처음으로 되돌리기
        body.send_keys(Keys.PAGE_UP)
        time.sleep(0.2)

    #time.sleep(2)
    return lastes_files

def process_captured_images(images):
    co_area = 65    # 화면캡쳐한 이미지가 겹치는 영역
    widths, heights = zip(*(i.size for i in images))
    max_width = max(widths)
    total_height = int(sum(heights) / len(images)) * 2

    images_result = []
    for ix, im in enumerate(images):
        
        if ix % 2 == 0 :
            if ix == len(images) - 1:  # 마지막일 경우, 한페이에 1개 이미지만
                #new_im = Image.new('RGB', (max_width - 15, heights[-1]))
                new_im = Image.new('RGB', (max_width - 15, total_height - co_area * 2), color = "white")
                new_im.paste(im, (0, 0))
                images_result.append(new_im)
            else:
                new_im = Image.new('RGB', (max_width - 15, total_height - co_area * 2))
                new_im.paste(im, (0, 0))
        else:
            cropped_image = images[ix].crop((0, 20, images[ix].size[0], images[ix].size[1])) # 월 평균 매출액 중복 부분 제거
            new_im.paste(cropped_image, (0, im.size[1] - co_area))
            images_result.append(new_im)

    return images_result

def process_downloaded_files(i, downfiles, store_name, current_folder):
    images_result = []
    
    for downfile in downfiles:
        if downfile.split(".")[-1] == "pdf" :   # 확장자가 PDF인 경우
            downfile_image = convert_from_path(download_folder + downfile, poppler_path=r"C:\poppler-24.08.0\Library\bin")  # 리턴값이 리스트임
            #downfile_image = convert_from_path(download_folder + downfile)  # 리턴값이 리스트임
            downfile_image= downfile_image[0]
        else:
            downfile_image = Image.open(download_folder + downfile)

        try:
            if downfile_image.size[0] > downfile_image.size[1] :
                downfile_image = downfile_image.resize((842,595))   # A4 가로 크기로 재조정
                downfile_image = downfile_image.rotate(270)         # 세로로 전환
            else:
                downfile_image = downfile_image.resize((595,842))   # A4 세로 크기로 재조정

        except:
            print("다운로드 파일 크기 조정시 에러 발생 -> 그냥 무시하고 지나감")
            continue   #다음 다운로드 파일 처리
        
        downfile_image = downfile_image.convert("RGB")
        images_result.append(downfile_image)

        #os.remove(download_folder + downfile) # 다운로드한 파일 옮기기
        shutil.move(download_folder + downfile, current_folder+"/사업자등록증")
        os.rename(current_folder+"/사업자등록증"+f"/{downfile}",
                      current_folder+"/사업자등록증"+f"/{i+1}_{store_name}_{downfile}")
        
    return images_result
        
## 리스트의 모든 이미지를 세로로 합쳐서 PDF 파일로 만들기
def images_to_file (i, processed_capture_images, processed_download_images, store_name, current_folder):
    #global download_folder
    #global current

    processed_capture_images.extend(processed_download_images)
    images_result = processed_capture_images
    images_result[0].save(f"./{current_folder}/{i+1}_{store_name}.pdf", save_all = True, append_images=images_result[1:])
    print(f"파일생성 완료(정상) : {i+1}_{store_name}.pdf")

    
## 중복 검색 오류(시스템 기준)  가맹점에 대한 대화창 닫기
def close_error_dialog():
    #time.sleep(3)      # 가맹관리 시스템에서 정보 조회하는 동안 기다리기
    close_class = "x-dialog.x-panel.x-container.x-component.x-bordered.\
x-header-position-top.x-floated.x-widthed.x-heighted.x-shadow.\
x-root.x-managed-borders.x-paint-monitored.x-size-monitored"
    close_btn_class = "x-icon-el.x-font-icon.x-tool-type-close"

    """
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, close_class)))
        time.sleep(2)
    except TimeoutException as e:
        return
    """
    
    #print("!!!! 중복 조회 등 예외 발생!!!!")
    try:
        #WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, close_btn_class)))
        time.sleep(1)
        ele_close = driver.find_element("class name", close_class)
        ele_close_btn = ele_close.find_element("class name", "x-icon-el.x-font-icon.x-tool-type-close")
        ele_close_btn.click()
        #time.sleep(1)
    except:
        return

## 다음 신청 가맹점에 대한 정보를 담고있는 div element을 찾아서 리턴
def get_next_store_element(driver):
    temp_ele_class = "ag-root.ag-unselectable.ag-layout-normal"
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, temp_ele_class)))
    temp_ele = driver.find_elements("class name", temp_ele_class)

    ele_cols_container_class = "ag-center-cols-container"
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, ele_cols_container_class)))
    ele_cols_container = temp_ele[4].find_element("class name", "ag-center-cols-container")

    # 신규 신청건수가 일정 갯수 이상(17건 정도)으로 넘어가면
    # 가맹시스템이 번호를 동적으로 부여해서 강제로 찾아야 함
    found = False
    div_eles = ele_cols_container.find_elements("tag name", "div")
    for div_e in div_eles:
        row = div_e.get_attribute("row-index")
        #print(row)
        if row == None:   continue
        if i == int(row):
            found = True
            break  
    return div_e

## 신청 가맹점에 대한 정보를 프린트하고 승인여부 정보를 리턴
def check_store_element_info(driver, div_e, store_name):
    print(f"\n######## 신청 가맹점({store_name}) 정보 확인 ###########")
    info_list = ["순   번", "신청일", "시   도", "시군구", "대표시장", "가맹점명", \
                  "대표명", "사업자", "백년소상공인", "상인회", "지자체", "확인여부", "확인기관", "확인일자"]
    
    divs = div_e.find_elements("tag name", "div")
    try:
        for k, div in enumerate(divs):
            print(f"{info_list[k]} : {div.text}")
    except:
        print("신청 가맹정 정보 확인중 에러가 발생하였습니다.")
        
    #승인된 것만 진행하기
    confirm = div_e.find_element("xpath", f".//div[12]").text  #12 : 상인여부확인 -> 확인여

    return confirm


def request_Naver_REG_API(image):
    biz_lic_api_url = 'https://7wg55rbtgo.apigw.ntruss.com/custom/v1/16116/748d8735530048af931c59b9a6566dfc6d39276fa049c6050f1e75d324aad8da/document/biz-license'
    print("네이버 OCR를 활용하여 사업자등록증 여부를 확인중..")
    biz_lic_secret_key = os.environ.get("PY_NAVER_OCR_BIZ_LIC_API")
    #biz_lic_secret_key = 'VFlSenlQSGlpWmpjdE1OQVpUYW11ZFJ3aGtzYmhOUWI='

    headers = {
        'X-OCR-SECRET': biz_lic_secret_key,
        'Content-Type': 'application/json'
        }
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='jpeg')
    img_bytes = img_byte_arr.getvalue()

    request_json = {
            'images': [
                {
                    'format': 'jpg',
                    'name': 'demo',
                    'data': base64.b64encode(img_bytes).decode()
                    #'url': image_url
                }
            ],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000))
        }
    payload = json.dumps(request_json).encode('UTF-8')

    response = requests.request("POST", biz_lic_api_url, headers=headers, data = payload, verify=False)
    text = json.loads(response.text)

    try:
        print(text["images"][0]["message"])
        print(text["images"][0]["bizLicense"]['result']['companyName'][0]['text'], "사업자등록증")
        return text
    except:
        return False
    
#############################################################
####################### 프로그램 시작 ##########################
#############################################################
driver = start_webdriver()
login_ongift(driver)
    
selected_stores = read_file("점포선택.txt")
download_folder = str(Path.home() / "Downloads") + "/"  # 첨부파일 다운로드 기본 폴더

# 실행 시점에 기반(연도-월-일-시)하여 폴더 생성 
current_folder = str(datetime.datetime.today())[0:16].replace("-", "").replace(" ", "_").replace(":", "")
createFolder(current_folder)
createFolder(current_folder+"/사업자등록증")

temp_ele = driver.find_elements("class name", "ag-root.ag-unselectable.ag-layout-normal")
new_store_cnt = int(temp_ele[4].get_attribute("aria-rowcount")) - 2  # 신규 가맹 신청점 갯수
print("신규가맹 신청점 갯수 : ", new_store_cnt)

####################### 메인 프로세스 ##########################
for i in range(new_store_cnt):
    div_e = get_next_store_element(driver)
    time.sleep(1)
    store_ele = div_e.find_element("xpath", f".//div[6]")   # 신청 가맹점 이름
    store_name = store_ele.text
    
    
    confirm = check_store_element_info(driver, div_e, store_name)
    if confirm == '':
        print(store_name, ": 미승인 상점")
        continue
    
    #사전에 txt파일에 등록된 상점이 있으면 그 상점만 진행 
    if selected_stores != [] and store_name not in selected_stores:
        print(f"{store_name}는 선택 대상에 없습니다.")
        continue
        
    print(f"상점 : {store_name} 선택...")
    store_ele.click()

    print(f"중복 조회 팝업창 닫기...")    
    popup_close(driver) #close_error_dialog()

    print(f"화면 캡쳐 실행...")    
    captured_images = screen_capture()

    print(f"첨부파일 다운로드...")
    try:
        downfiles = download_attachedfiles()
    except:
        print("파일 다운로드 중 에러가 발생하여 중복조회 창을 닫고 다시 시도..")
        close_error_dialog()
        captured_images = screen_capture()
        downfiles = download_attachedfiles()

    processed_capture_images = process_captured_images(captured_images)
    processed_download_images = process_downloaded_files(i, downfiles, store_name, current_folder)

    #첫번째 첨부파일이 사업자등록증이 아니면 두번째 파일과 순서 교체
    try:
        reg_check = request_Naver_REG_API(processed_download_images[0])
        if reg_check == False:
            if len(processed_download_images) == 2:
                processed_download_images[0], processed_download_images[1] = processed_download_images[1], processed_download_images[0]
    except:
        print("네이버 OCR을 통한 사업자등록 검증이 안되어 그대로 진행합니다.")
    
    images_to_file(i, processed_capture_images, processed_download_images, store_name, current_folder)        
#############################################################

