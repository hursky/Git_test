import shutil
import os
from datetime import datetime
import json

def is_valid_path(path):
    try:
        return os.path.isdir(path)  
    except:
        return False

def delete_all_files_in_folder(folder_path):
    try:
        # 폴더 내부의 모든 파일 리스트를 가져옴
        file_list = os.listdir(folder_path)

        # 각 파일을 순회하며 삭제
        for file_name in file_list:
            file_path = os.path.join(folder_path, file_name)

            # 파일인 경우 삭제
            if os.path.isfile(file_path):
                os.remove(file_path)

            # 폴더인 경우 재귀적으로 삭제
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    except Exception as e:
        print(f"An error occurred: {e}")


def load_conf():
    with open("./data/config.json", "r", encoding="utf-8") as f:
        conf = json.load(f)
    # motor_set = {
    #     "name": "",
    #     "data": ["path",]
    # }
    return conf


def save_conf(conf):
    with open("./data/config.json", "w", encoding="utf-8") as f:
        json.dump(conf, f, indent=4, ensure_ascii=False)


def initialize():
    conf = load_conf()
    os.makedirs("./temp", exist_ok=True)
    delete_all_files_in_folder("./temp")
    return conf
