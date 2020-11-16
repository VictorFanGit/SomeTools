import os

if __name__ == "__main__":
    url = 'https://yulaodou/oss-cn-shenzhen/aliyuncs.com/Cloud Sync利用OneDrive备份文件.png'
    head, tail = os.path.split(url)
    print(tail)