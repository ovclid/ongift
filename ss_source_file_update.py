#version = 1.0.1
import sys
import os
import requests
from packaging import version

def get_file_content(file_name, file_location, location_type):
    global github
    
    if location_type == "pc":
        try:
            f = open(file_location + file_name, "r", encoding = "utf-8")
            file_content = f.read()
            f.close()
        except:
            file_content= ""
            
    elif location_type == "github":
        try:
            url = f"https://raw.githubusercontent.com/{file_location}/main/{file_name}"
                     #https://raw.githubusercontent.com/ovclid/ongift/main/ss_source_file_update.py
            
            print(url)
            download = requests.get(url)
            file_content = download.text
        except:
            file_content= ""
            print("github로 부터 다운로드 실패")
                
    return file_content

def get_version(file_content):
    file_version = ""
    file_lines = file_content.split("\n")
    for i in range(len(file_lines)):
        if "version" in file_lines[i]:
            print(file_lines[i])
            file_version = file_lines[i].split("=")[1]
            file_version = file_version.replace("\r", "").replace(" ", "")
            break

    return file_version

def update_files(file_names = ["ss_auto_chromedriver.py"],
                     #pc_location = "./", #os.getcwd(),
                   pc_location = os.path.dirname(sys.executable),
                  github_location = "ovclid/ongift"):

    print(file_names, pc_location, github_location)
    
    if os.path.exists(pc_location) == False:
        print(f"해당 PC의 {pc_location} 디렉토리가 존재하지 않습니다.")
        return False
    
    for i in range(len(file_names)):
        print(f"{file_names[0]} 를 확인중...")

        pc_file_content = get_file_content(file_names[i], pc_location, "pc")
        if pc_file_content == "":
            pc_file_version = "0.0.0"
        else:
            pc_file_version = get_version(pc_file_content)
        print(pc_file_version)
        
        github_file_content =get_file_content(file_names[i], github_location, "github")
        print(github_file_content)
        github_file_version = get_version(github_file_content)
        print(get_version(github_file_content))

        if github_file_content == "":
            print("github로 부터 파일을 제대로 다운로드 하지 못했습니다.")
            continue

        if pc_file_version == github_file_version:
            print("버전이 일치합니다")
        else:
            if version.parse(pc_file_version) > version.parse(github_file_version):
                print("현재 설치된 버전이 더 최신입니다.")
            else:
                print("버전이 일치하지 않아 업데이트 합니다.")
                try:
                    f = open(file_names[i], "w", encoding = "utf-8")
                    f.write(github_file_content.replace("\r\n", "\n"))
                    f.close()
                except:
                    print(f"{file_names[i]} 쓰기에 실패하였습니다. ")
                    sys.exit()
            

update_files()

#import ss_auto_chromedriver as ss_driver
#driver = ss_driver.start()
