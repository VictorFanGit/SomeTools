# -*- coding: UTF-8 -*-
import os
import json
import shutil
import log_util
import sys
import re
import stat
import urllib.request
import urllib.parse
import requests
import time


src_dir = None
file_types = ['md']
local_img_folder = None
net_img_base_url = None

backup_dir = None

current_dir = os.path.dirname(__file__)
conf_path = os.path.join(current_dir, 'config.json')

local_pattern = None
oss_pattern = None

def load_config():
    global src_dir, net_img_base_url, local_img_folder,backup_dir
    with open(conf_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        print('===config info===')
        print(json_data)
        if json_data['srcDir'] == None or json_data['srcDir'] == ".":
            src_dir = os.path.dirname(__file__)
        else:
            src_dir = json_data['srcDir']
        net_img_base_url = json_data['picBaseUrl']
        local_img_folder = json_data['imgDir']
        backup_dir = os.path.join(src_dir,"backup")



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
            log_util.logger.warning('Failed to copy file: %s' % e)

def move_orignal_files_to_backup():
    global backup_dir, src_dir, local_img_folder
    orig_img_dir = os.path.join(src_dir, local_img_folder)
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    des_dir = os.path.join(backup_dir, local_img_folder)
    shutil.move(orig_img_dir, des_dir)

    list_file = os.listdir(src_dir)
    for f_name in list_file:
        f_type = os.path.splitext(f_name)[-1][1:]
        if f_type not in file_types:
            continue
        src = os.path.join(src_dir, f_name)
        des = os.path.join(backup_dir,f_name)
        shutil.move(src, des)

def process_all_files():
    process_count = 0
    failed_count = 0
    global src_dir, file_types, local_img_folder, net_img_base_url,local_pattern,oss_pattern

    local_pattern = re.compile(r'\('+ local_img_folder + r'[\S|\s]+\)')
    oss_pattern = re.compile(r'\(' + net_img_base_url + r'[\S|\s]+\)')

    oss_dir = os.path.join(src_dir, 'net')
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
            process_count += 1
            if not convert_pic_url_to_oss(oss_file_path, file_content):
                failed_count += 1
            if not convert_pic_url_to_local(local_file_path, file_content):
                failed_count += 1
            
    return process_count, failed_count


# def convert_local_url_to_oss(local_pic_url):
#     global net_img_base_url
#     head, tail = os.path.split(local_pic_url)
#     return '(' + net_img_base_url + '/' + tail


def convert_oss_url_to_local(oss_pic_url):
    global local_img_folder
    head, tail = os.path.split(oss_pic_url)
    return '(' + local_img_folder + '/' + tail


def upload_pic_to_oss(pic_path):
    headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
            "Content-Type": "application/json"
    }
    data = {"list":[pic_path]}
    resp = requests.post("http://127.0.0.1:36677/upload",json.dumps(data), headers)

    if resp.status_code == 200:
        d = json.loads(resp.content)
        if d["success"]:
            return d["result"][0]
        else:
            return None
    else:
        log_util.logger.error('failed to upload pic:' + pic_path)
        return None

def get_pic_by_url(lists):
    global src_dir, local_img_folder
    img_full_dir = os.path.join(src_dir, "local", local_img_folder)
    if not os.path.exists(img_full_dir):
        os.makedirs(img_full_dir)
    for url in lists:
        url = url[1:-1].strip()
        filename = url.split('/')[-1]
        filepath = os.path.join(img_full_dir, filename)
        if os.path.exists(filepath):
            log_util.logger.info("File have already exist. skip")
        else:
            try:
                #下载图片，并保存到文件夹中
                urllib.request.urlretrieve(url,filename=filepath)
                return True
            except Exception as e:
                log_util.logger.error("Error occurred when downloading file, error message:%s" %e)
                return False


def convert_pic_url_to_oss(oss_file_path, file_content):
    global local_img_folder, local_pattern, src_dir
    isSuccess = True
    with open(oss_file_path, 'w', encoding='utf-8') as c_f:
        for fc in file_content:
            local_pic_urls = re.findall(local_pattern, fc)
            if len(local_pic_urls) > 0:
                for local_pic_url in local_pic_urls:
                    local_pic_url = local_pic_url[1:-1].strip()
                    pic_path = os.path.join(src_dir, local_pic_url)
                    pic_url = upload_pic_to_oss(pic_path)
                    if pic_url == None:
                        isSuccess = False
                        c_f.write(fc)
                    else:
                        new_fc = re.sub(local_pic_url, pic_url, fc)
                        c_f.write(new_fc)
                        # PicGo上传文件名按时间秒为单位，避免同名文件
                        time.sleep(1)
            else:
                c_f.write(fc)
    return isSuccess

def convert_pic_url_to_local(local_file_path, file_content):
    global oss_pattern
    isSuccess = True
    with open(local_file_path, 'w', encoding='utf-8') as c_f:
        for fc in file_content:
            oss_pic_urls = re.findall(oss_pattern, fc)
            if len(oss_pic_urls) > 0:
                if not get_pic_by_url(oss_pic_urls):
                    isSuccess = False
                for oss_pic_url in oss_pic_urls:
                    des_content = convert_oss_url_to_local(oss_pic_url)
                    new_fc = re.sub(oss_pic_url, des_content, fc)
                    c_f.write(new_fc)
            else:
                c_f.write(fc)
    return isSuccess


if __name__ == "__main__":
    load_config()
    log_util.logger.info('start...')
    if not os.path.isdir(src_dir):
        print('源目录不存在！')
        log_util.logger.error('源目录不存在！')
        exit(1)
    process_count, failed_count = process_all_files()
    move_orignal_files_to_backup()
    print("处理文件总数：" + str(process_count))
    print("处理失败文件数：" + str(failed_count))
    log_util.logger.info("处理文件总数：" + str(process_count))
    log_util.logger.info("处理失败文件数：" + str(failed_count))

