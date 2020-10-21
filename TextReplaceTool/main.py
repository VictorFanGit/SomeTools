# -*- coding: UTF-8 -*-
import os
import json
import shutil
import logging
import sys
import re


src_dir = ""
file_types = []
src_content = ""
des_content = ""

current_dir = os.path.dirname(__file__)
conf_path = os.path.join(current_dir, 'config.json')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("running.log", mode='a', encoding='utf-8')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)


def load_config():
    global src_dir, file_types, src_content, des_content
    with open(conf_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        print('===config info===')
        print(json_data)
        src_dir = json_data['srcDir']
        file_types = json_data['fileType'].split(',')
        src_content = json_data['srcContent']
        des_content = json_data['desContent']


def process_all_files(src_dir, src_content, des_content):
    process_count = 0
    global file_types
    des_dir = os.path.join(src_dir, 'convert')
    if not os.path.isdir(des_dir):
        os.makedirs(des_dir)
    # 列出文件夹下所有的目录与文件
    list_file = os.listdir(src_dir)
    
    for f_name in list_file:
        f_type = os.path.splitext(f_name)[-1][1:]
        if f_type not in file_types:
            continue
        original_file_path = os.path.join(src_dir, f_name)
        convert_file_path = os.path.join(des_dir, f_name)
        content = None

        with open(original_file_path, 'r', encoding='utf-8') as o_f:
            content = o_f.readlines()
        with open(convert_file_path, 'w', encoding='utf-8') as c_f:
            if content:
                for line_c in content:
                    new_c = re.sub(src_content, des_content, line_c)
                    c_f.write(new_c)
        if content:
            process_count += 1
    return process_count


if __name__ == "__main__":
    load_config()
    logger.info('start...')
    if not os.path.isdir(src_dir):
        print('源目录不存在！')
        logger.error('源目录不存在！')
        exit(1)
    processed_file_count = process_all_files(src_dir, src_content, des_content)
    print("处理文件总数：" + str(processed_file_count))
    logger.info("处理文件总数：" + str(processed_file_count))
