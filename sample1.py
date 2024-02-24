import ss_source_file_update as sfu

pc_location = "./"
github_location = "ovclid/ongift"

file_names = ["ss_auto_chromedriver.py"]
sfu.update_files(file_names, pc_location, github_location)

import ss_auto_chromedriver
driver = ss_auto_chromedriver.start()

input("아무키나 누르세요... 프로그램 종료")
