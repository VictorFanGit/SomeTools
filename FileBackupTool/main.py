# -*- coding: UTF-8 -*-
import os
import json
import shutil
import logging

src_dir = ""
des_dir = ""
ignore_type = []
override = False
file_count = 0

current_dir = os.path.dirname(__file__)
conf_path = os.path.join(current_dir, 'config.json')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("running.log", mode='a',encoding='utf-8')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)

def load_config():
    global src_dir, des_dir, ignore_type, override
    with open(conf_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        print(json_data)
        src_dir = json_data['srcDir']
        des_dir = json_data['desDir']
        ignore_type = json_data['ignoreType'].split(',')
        print(ignore_type)
        if json_data['override'] != 0:
            override = True
            print('override:true')
        else:
            print('override:false')


def copy_all_files(s_dir, d_dir):
    # 列出文件夹下所有的目录与文件
    list_file = os.listdir(s_dir)

    for i in range(0, len(list_file)):

        # 构造路径
        s_path = os.path.join(s_dir, list_file[i])
        d_path = os.path.join(d_dir, list_file[i])

        # 判断路径是否是一个文件目录或者文件
        # 如果是文件目录，继续递归
        if os.path.isdir(s_path):
            if not os.path.exists(d_path):
                os.makedirs(d_path)
            copy_all_files(s_path, d_path)
        if os.path.isfile(s_path):
            copy_file(s_path, d_path)


def copy_file(s_path, d_path):
    global ignore_type, file_count
    file_type = os.path.splitext(s_path)[-1][1:]
    if file_type in ignore_type:
        if not os.path.exists(d_path):
            with open(d_path, 'a'):
                file_count = file_count + 1
    else:
        if not os.path.exists(d_path) or override:
            try:
                shutil.copy(s_path, d_path)
                file_count = file_count + 1
            except IOError as e:
                print('拷贝文件失败. %s' % e)
                logger.warning('拷贝文件失败: %s' % e.msg)


if __name__ == "__main__":
    load_config()
    logger.info('start...')
    if not os.path.isdir(src_dir):
        print('源目录不存在！')
        logger.error('源目录不存在！')
        exit(1)
    if not os.path.isdir(des_dir):
        os.makedirs(des_dir)
    copy_all_files(src_dir, des_dir)
    print("复制文件数量：" + str(file_count))
    logger.info("复制文件数量：" + str(file_count))
