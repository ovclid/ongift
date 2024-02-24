#version = 1.0.0
import sys
import requests

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
            download = requests.get(url)
            file_content = download.text
        except:
            file_content= ""
                
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

def update_files(file_names, pc_location, github_location):
    for i in range(len(file_names)):
        print(f"{file_names[0]} 를 확인중...")

        pc_file_content = get_file_content(file_names[i], pc_location, "pc")
        pc_file_version = get_version(pc_file_content)
        print(pc_file_version)
        
        github_file_content =get_file_content(file_names[i], github_location, "github")
        github_file_version = get_version(github_file_content)
        print(get_version(github_file_content))

        if github_file_content == "":
            print("github로 부터 파일을 제대로 다운로드 하지 못했습니다.")
            continue

        if pc_file_version == github_file_version:
            print("버전이 일치합니다")
        else:
            print("버전이 일치하지 않아 업데이트 합니다.")
            try:
                f = open(file_names[i], "w", encoding = "utf-8")
                f.write(github_file_content.replace("\r\n", "\n"))
                f.close()
            except:
                print(f"{file_names[i]} 쓰기에 실패하였습니다. ")
                sys.exit()
            
