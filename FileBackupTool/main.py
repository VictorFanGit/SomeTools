# -*- coding: UTF-8 -*-
import os
import json
import shutil

src_dir = ""
des_dir = ""
ignore_type = []
override = False

current_dir = os.path.dirname(__file__)
conf_path = os.path.join(current_dir, 'config.json')


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
    global ignore_type
    file_type = os.path.splitext(s_path)[-1][1:]
    if file_type in ignore_type:
        if os.path.exists(d_path):
            if not override:
                pass
        else:
            with open(d_path, 'a'):
                pass
    else:
        try:
            shutil.copy(s_path, d_path)
        except IOError as e:
            print("拷贝文件失败. %s" % e)
        except:
            print("拷贝文件发生未知错误:", sys.exc_info())


if __name__ == "__main__":
    load_config()
    if not os.path.isdir(src_dir):
        print('源目录不存在！')
        exit(1)
    if not os.path.isdir(des_dir):
        os.makedirs(des_dir)
    copy_all_files(src_dir, des_dir)
