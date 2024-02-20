## import 모듈
import os
import glob
import io
import time
import datetime
import shutil
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

## 온누리가맹점 사이트 로그인
def login_ongift(driver):
    ele = driver.find_element("id", "userId")
    ele.send_keys("sweet7")
    time.sleep(1)

    ele = driver.find_element("id", "userPw")
    ele.send_keys("smba1357**")
    time.sleep(1)

    ele = driver.find_element("class name", "btn.btn-primary.btn-block.btn-large")
    ele.click()
    time.sleep(5)
    
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
    time.sleep(1)
    new_store_info_class = "x-panel.x-container.x-component.x-bordered.x-widthed.\
x-header-position-top.x-managed-borders.x-paint-monitored.\
x-size-monitored.x-dock-item.x-docked-right.x-noborder-trb"

    store_info_element = driver.find_element("class name", new_store_info_class)
    store_info_element.click()    # (좌측) 신규 가맹점 클릭 -> (우측) 정보영역에 표시하기
    body = driver.find_element("css selector", 'body')

    images = []
    images.append(store_info_element.screenshot_as_png)

    for i in range(2):
        body.send_keys(Keys.PAGE_DOWN)   # 스크롤 영역 한번 클릭하기
        time.sleep(1)
        images.append(store_info_element.screenshot_as_png)

    for i in range(len(images)):  # 이미지를 BytesIO형태로 변환하기
        images[i] = Image.open(io.BytesIO(images[i]))
    
    time.sleep(2)
    return images

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

## 리스트의 모든 이미지를 세로로 합쳐서 PDF 파일로 만들기
def images_to_file (i, images, store_name, current_folder):
    # 화면캡쳐한 이미지들 처리
    global download_folder
    global current
    
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
            new_im.paste(im, (0, im.size[1] - co_area))
            images_result.append(new_im)

    # 사업자등록증 처리
    downfile = download_attachedfile()
    if downfile.split(".")[-1] == "pdf" :   # 확장자가 PDF인 경우
        downfile_image = convert_from_path(download_folder + downfile)  # 리턴값이 리스트임
        downfile_image= downfile_image[0]  
    elif downfile.split(".")[-1] == "png" :   # 확장자가 PDF인 경우
        downfile_image = Image.open(download_folder + downfile).convert("RGB")
    else:
        downfile_image = Image.open(download_folder + downfile)

    if downfile_image.size[0] > downfile_image.size[1] :
        downfile_image = downfile_image.resize((842,595))   # A4 가로 크기로 재조정
        downfile_image = downfile_image.rotate(270)         # 세로로 전환
    else:
        downfile_image = downfile_image.resize((595,842))   # A4 세로 크기로 재조정            
    images_result.append(downfile_image)

    #os.remove(download_folder + downfile) # 다운로드한 파일 삭제하기
    shutil.move(download_folder + downfile, current_folder+"/사업자등록증")
    os.rename(current_folder+"/사업자등록증"+f"/{downfile}",
                  current_folder+"/사업자등록증"+f"/{i+1}_{store_name}_{downfile}")
    
    images_result[0].save(f"./{current_folder}/{i+1}_{store_name}.pdf", save_all = True, append_images=images_result[1:])
    print(f"파일생성 완료 : {i+1}_{store_name}.pdf")

## 중복 검색 오류(시스템 기준)  가맹점에 대한 대화창 닫기
def close_error_dialog():
    time.sleep(2)      # 가맹관리 시스템에서 정보 조회하는 동안 기다리기
    close_class = "x-dialog.x-panel.x-container.x-component.x-bordered.\
x-header-position-top.x-floated.x-widthed.x-heighted.x-shadow.\
x-root.x-managed-borders.x-paint-monitored.x-size-monitored"

    ele_close = driver.find_element("class name", close_class)
    ele_close_btn = ele_close.find_element("class name", "x-icon-el.x-font-icon.x-tool-type-close")
    ele_close_btn.click()

## 다음 신청 가맹점에 대한 정보를 담고있는 div element을 찾아서 리턴
def get_next_store_element(driver, i):   
    temp_ele = driver.find_elements("class name", "ag-root.ag-unselectable.ag-layout-normal")
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
                  "대표명", "사업자", "상인회", "지자체", "확인여부", "확인기관", "확인일자"]
    
    divs = div_e.find_elements("tag name", "div")
    try:
        for k, div in enumerate(divs):
            print(f"{info_list[k]} : {div.text}")
    except:
        print("신청 가맹정 정보 확인중 에러가 발생하였습니다.")
        
    #승인된 것만 진행하기
    confirm = div_e.find_element("xpath", f".//div[11]").text

    return confirm

#############################################################
####################### 프로그램 시작 ##########################
#############################################################

def start(driver, site, login_id, login_pw):
    driver.maximize_window()    
    driver.get("https://www.ongift.or.kr/")
    time.sleep(2)
    
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
        div_e = get_next_store_element(driver, i)
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
            
        try:     # "중복 조회" 등 예외 상황 발생 체크  
            store_ele.click()
            time.sleep(3)

            images = screen_capture( )
            images_to_file(i, images, store_name, current_folder)
        except:
            print("!!!! 중복 조회 등 예외 발생!!!!")
            close_error_dialog()
            time.sleep(5)

            images = screen_capture( )
            images_to_file(i, images, store_name + "_중복 조회 등(확인필요)", current_folder)
#############################################################
