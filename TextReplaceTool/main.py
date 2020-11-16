# -*- coding: UTF-8 -*-
import os
import json
import shutil
import log_util
import sys
import re


src_dir = "."
file_types = ['md']
local_img_folder = "img"
net_img_base_url = "https://yulaodou.oss-cn-shenzhen.aliyuncs.com"

current_dir = os.path.dirname(__file__)
conf_path = os.path.join(current_dir, 'config.json')


def load_config():
    global src_dir, file_types, local_img_folder, net_img_base_url
    with open(conf_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        print('===config info===')
        print(json_data)
        if json_data['srcDir'] == None or len(json_data['srcDir']) == 0:
            src_dir = os.path.dirname(__file__)
        else:
            src_dir = json_data['srcDir']


def copy_img_folder(src_dir, des_dir):
    if not os.path.isdir(des_dir):
        os.makedirs(des_dir)
    list_file = os.listdir(src_dir)

    for f_name in list_file:
        s_path = os.path.join(src_dir, f_name)
        d_path = os.path.join(des_dir, f_name)
        try:
            shutil.copy(s_path, d_path)
        except IOError as e:
            logger.warning('拷贝文件失败: %s' % e)


def process_all_files():
    process_count = 0
    global src_dir, file_types, local_img_folder, net_img_base_url
    oss_dir = os.path.join(src_dir, 'oss')
    local_dir = os.path.join(src_dir, 'local')
    orig_img_dir = os.path.join(src_dir, local_img_folder)
    if not os.path.isdir(oss_dir):
        os.makedirs(oss_dir)
    if not os.path.isdir(local_dir):
        os.makedirs(local_dir)
    if not os.path.isdir(orig_img_dir):
        os.makedirs(orig_img_dir)

    local_img_dir = os.path.join(local_dir, local_img_folder)
    copy_img_folder(orig_img_dir, local_img_dir)
    
    list_file = os.listdir(src_dir)
    for f_name in list_file:
        f_type = os.path.splitext(f_name)[-1][1:]
        if f_type not in file_types:
            continue
        original_file_path = os.path.join(src_dir, f_name)
        oss_file_path = os.path.join(oss_dir, f_name)
        local_file_path = os.path.join(local_dir, f_name)
        file_content = None
        with open(original_file_path, 'r', encoding='utf-8') as o_f:
            file_content = o_f.readlines()
        if file_content:
            convert_pic_url_to_oss(oss_file_path, file_content)
            convert_pic_url_to_local(local_file_path, file_content)
            process_count += 1
    return process_count


def convert_local_url_to_oss(local_pic_url):
    global net_img_base_url
    head, tail = os.path.split(local_pic_url)
    return '(' + net_img_base_url + '/' + tail


def convert_oss_url_to_local(oss_pic_url):
    global local_img_folder
    head, tail = os.path.split(oss_pic_url)
    return '(' + local_img_folder + '/' + tail

def convert_pic_url_to_oss(oss_file_path, file_content):
    global local_img_folder
    local_pattern = re.compile(r'\('+ local_img_folder + r'[\S|\s]+\)')
    with open(oss_file_path, 'w', encoding='utf-8') as c_f:
        for fc in file_content:
            local_pic_urls = re.findall(local_pattern, fc)
            if len(local_pic_urls) > 0:
                for local_pic_url in local_pic_urls:
                    des_content = convert_local_url_to_oss(local_pic_url)
                    new_fc = re.sub(local_pic_url, des_content, fc)
                    c_f.write(new_fc)
            else:
                c_f.write(fc)

def convert_pic_url_to_local(local_file_path, file_content):
    global net_img_base_url
    oss_pattern = re.compile(r'\(' + net_img_base_url + r'[\S|\s]+\)')
    with open(local_file_path, 'w', encoding='utf-8') as c_f:
        for fc in file_content:
            oss_pic_urls = re.findall(oss_pattern, fc)
            if len(oss_pic_urls) > 0:
                for oss_pic_url in oss_pic_urls:
                    
                    des_content = convert_oss_url_to_local(oss_pic_url)
                    new_fc = re.sub(oss_pic_url, des_content, fc)
                    c_f.write(new_fc)
            else:
                c_f.write(fc)


if __name__ == "__main__":
    load_config()
    logger.info('start...')
    if not os.path.isdir(src_dir):
        print('源目录不存在！')
        logger.error('源目录不存在！')
        exit(1)
    processed_file_count = process_all_files()
    print("处理文件总数：" + str(processed_file_count))
    logger.info("处理文件总数：" + str(processed_file_count))
