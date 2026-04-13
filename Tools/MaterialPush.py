#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/3/31 下午4:17
# @Author  : Soin
# @File    : MaterialPush.py
# @Software: PyCharm
"""
    咸鱼推送素材，挂商品肯定是得有点素材对吧
"""
import requests
import mimetypes
from pathlib import Path


def upload_image(image_path: str):
    """
        咸鱼网页版目前只支持上传图片，不支持上传视频
    :param image_path:
    :return:
    """
    # 查看后缀是否是图片格式
    print(Path(image_path).suffix)
    print(Path(image_path).suffix not in [".png", ".jpg", ".jpeg"])
    if Path(image_path).suffix not in [".png", ".jpg", ".jpeg"]:
        raise ValueError("Only image files are supported.")
    url = "https://stream-upload.goofish.com/api/upload.api"

    params = {'floderId': '0', 'appkey': 'fleamarket', '_input_charset': 'utf-8', }

    # 只保留必要 header
    headers = {'origin': 'https://www.goofish.com', 'referer': 'https://www.goofish.com/',
               'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36', }


    cookies = {'cookie2': '180109ea3efa8e358c1e050bd4288c44', }

    # 自动识别 MIME
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/png"

    filename = Path(image_path).name

    # 用 files
    with open(image_path, "rb") as f:
        files = {'file': (filename, f, mime_type)}

        response = requests.post(url, params=params, headers=headers, cookies=cookies, files=files, timeout=20)
        print(response.text)
    return response.json()  # 返回json


if __name__ == "__main__":
    image_path = "/Users/soin/SoinJobs/XianYu/test/extracted_image.png"
    try:
        response = upload_image(image_path)
    except ValueError as e:
        print("请上传图片文件")
