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

backup_dir = None

current_dir = os.path.dirname(__file__)
conf_path = os.path.join(current_dir, 'config.json')

local_pattern = None
oss_pattern = None

def load_config():
    global src_dir, local_img_folder,backup_dir
    with open(conf_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        print('===配置信息===')
        print(json_data)
        if json_data['srcDir'] == None or json_data['srcDir'] == ".":
            src_dir = os.path.dirname(__file__)
        else:
            src_dir = json_data['srcDir']
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
            log_util.logger.warning('拷贝文件出错: %s' % e)

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
    global src_dir, file_types, local_img_folder,local_pattern,oss_pattern

    local_pattern = re.compile(r'\!\[[\S|\s]*\]\('+ local_img_folder + r'[\S|\s]+\)')
    oss_pattern = re.compile(r'\!\[[\S|\s]*\]\(http[\s]*[\S|\s]+\)')

    net_dir = os.path.join(src_dir, 'net')
    local_dir = os.path.join(src_dir, 'local')
    orig_img_dir = os.path.join(src_dir, local_img_folder)
    if not os.path.isdir(net_dir):
        os.makedirs(net_dir)
    if not os.path.isdir(local_dir):
        os.makedirs(local_dir)
    if not os.path.isdir(orig_img_dir):
        os.makedirs(orig_img_dir)

    local_img_dir = os.path.join(local_dir, local_img_folder)
    net_img_dir = os.path.join(net_dir, local_img_folder)
    copy_img_folder(orig_img_dir, local_img_dir)
    copy_img_folder(orig_img_dir, net_img_dir)
    
    list_file = os.listdir(src_dir)
    for f_name in list_file:
        f_type = os.path.splitext(f_name)[-1][1:]
        if f_type not in file_types:
            continue
        original_file_path = os.path.join(src_dir, f_name)
        oss_file_path = os.path.join(net_dir, f_name)
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

    shutil.rmtree(net_img_dir) 
    return process_count, failed_count


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
        log_util.logger.error('上传图片文件出错:' + pic_path)
        return None


def rename_pic_file(file_path, rename):
    head, tail = os.path.split(file_path)
    split_arr = tail.split('.')
    if len(split_arr) < 2:
        log_util.logger.error("文件名格式错误：" + file_path)
        return file_path
    name = split_arr[0]
    suffix = split_arr[1]
    if tail == name:
        return file_path
    rename_path = os.path.join(head, rename + '.' + suffix)
    os.rename(file_path, rename_path)
    return rename_path


def rename_and_upload_pic(c_f, fc, local_pic_urls):
    global src_dir
    isSuccess = True
    for local_pic_url in local_pic_urls:
        split_arr = local_pic_url.split(']')
        if len(split_arr) == 2:
            pic_name = split_arr[0][2:]
            local_pic_url = split_arr[1][1:-1].strip()
            pic_path = os.path.join(src_dir, 'net', local_pic_url)
            new_path = pic_path
            if len(pic_name) > 0:
                new_path = rename_pic_file(pic_path, pic_name)
            pic_url = upload_pic_to_oss(new_path)
            if pic_url == None:
                isSuccess = False
                c_f.write(fc)
            else:
                new_fc = re.sub(local_pic_url, pic_url, fc)
                c_f.write(new_fc)
        else:
            log_util.logger.error('图片地址格式错误！')
            c_f.write(fc)
    return isSuccess


def convert_pic_url_to_oss(oss_file_path, file_content):
    global local_img_folder, local_pattern, src_dir
    isSuccess = True
    with open(oss_file_path, 'w', encoding='utf-8') as c_f:
        for fc in file_content:
            local_pic_urls = re.findall(local_pattern, fc)
            if len(local_pic_urls) > 0:
                if not rename_and_upload_pic(c_f, fc, local_pic_urls):
                    isSuccess = False
            else:
                c_f.write(fc)
    return isSuccess


def convert_oss_url_to_local(full_path):
    global local_img_folder
    head, tail = os.path.split(full_path)
    return local_img_folder + '/' + tail


def download_pic_and_rename(c_f, fc, oss_pic_urls):
    global src_dir, local_img_folder
    isSuccess = True
    img_full_dir = os.path.join(src_dir, "local", local_img_folder)
    if not os.path.exists(img_full_dir):
        os.makedirs(img_full_dir)
    for url in oss_pic_urls:
        split_arr = url.split(']')
        if len(split_arr) == 2:
            pic_pre_name = split_arr[0][2:]
            url = split_arr[1][1:-1].strip()
            head, tail = os.path.split(url)
            filename = tail
            if len(pic_pre_name) > 0:
                filename = pic_pre_name + '.' + url.split('.')[-1]
            filepath = os.path.join(img_full_dir, filename)
            if os.path.exists(filepath):
                log_util.logger.info("图片文件已经存在，跳过！")
            else:
                try:
                    #下载图片，并保存到文件夹中
                    urllib.request.urlretrieve(url,filename=filepath)
                    des_content = convert_oss_url_to_local(filepath)
                    new_fc = re.sub(url, des_content, fc)
                    c_f.write(new_fc)
                except Exception as e:
                    log_util.logger.error("下载图片出错:%s" %e)
                    isSuccess = False
                    c_f.write(fc)
        else:
            isSuccess = False
            log_util.logger.error("下载图片出错:%s" %e)
            c_f.write(fc)

    return isSuccess 


def convert_pic_url_to_local(local_file_path, file_content):
    global oss_pattern
    isSuccess = True
    with open(local_file_path, 'w', encoding='utf-8') as c_f:
        for fc in file_content:
            oss_pic_urls = re.findall(oss_pattern, fc)
            if len(oss_pic_urls) > 0:
                if not download_pic_and_rename(c_f, fc, oss_pic_urls):
                    isSuccess = False
            else:
                c_f.write(fc)
    return isSuccess


if __name__ == "__main__":
    load_config()
    log_util.logger.info('开始...')
    if not os.path.isdir(src_dir):
        print('源目录不存在！')
        log_util.logger.error('源目录不存在！')
        exit(1)
    process_count, failed_count = process_all_files()
    # move_orignal_files_to_backup()
    print("处理文件总数：" + str(process_count))
    print("处理失败文件数：" + str(failed_count))
    log_util.logger.info("处理文件总数：" + str(process_count))
    log_util.logger.info("处理失败文件数：" + str(failed_count))

