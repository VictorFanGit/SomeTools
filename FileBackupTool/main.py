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
    sum = 0
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
            sum += copy_all_files(s_path, d_path)
        if os.path.isfile(s_path):
            sum += copy_file(s_path, d_path)
    return sum    

def dir_size(d):
    '''
    定义计算指定目录大小的函数
    '''
    sum = 0
    #判断指定目录是否为文件
    if os.path.isfile(d):
        sum+=os.path.getsize(d)
    #判断指定目录是否为文件夹
    if os.path.isdir(d):
        dir_list = os.listdir(d)    
        for f in dir_list:
            file = os.path.join(d,f)
            if os.path.isfile(file):
                sum+=os.path.getsize(file)
            if os.path.isdir(file):
                sum+=dir_size(file)#递归统计
    return sum

def convert_unit(byte_size):
    if byte_size > 1024:
        k_size = int(byte_size / 1024)
        if k_size > 1024:
            m_size = int(k_size / 1024)
            if m_size > 1024:
                g_size = m_size / 1024
                g_size = round(g_size, 1)
                return str(g_size) + 'G'
            else:
                return str(m_size) + 'M'    

        else:
            return str(int(k_size)) + 'K'
    else:
        return str(int(byte_size)) + 'B'


def copy_file(s_path, d_path):
    global ignore_type, file_count
    copy_size = 0
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
                copy_size = os.path.getsize(s_path)
            except IOError as e:
                print('拷贝文件失败. %s' % e)
                logger.warning('拷贝文件失败: %s' % e)
    return copy_size


if __name__ == "__main__":
    load_config()
    logger.info('start...')
    if not os.path.isdir(src_dir):
        print('源目录不存在！')
        logger.error('源目录不存在！')
        exit(1)
    if not os.path.isdir(des_dir):
        os.makedirs(des_dir)
    copy_size = copy_all_files(src_dir, des_dir)
    copy_size_str = convert_unit(copy_size)
    print("复制文件总大小：" + copy_size_str)
    logger.info("复制文件总大小：" + copy_size_str)
    print("复制文件数量：" + str(file_count))
    logger.info("复制文件数量：" + str(file_count))
    d_size = convert_unit(dir_size(des_dir))
    print("目标目录大小：" + d_size)
    logger.info("目标目录大小：" + d_size)
