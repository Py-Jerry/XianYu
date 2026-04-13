#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/3/31 下午4:17
# @Author  : Soin
# @File    : MaterialPush.py
# @Software: PyCharm
"""
咸鱼推送素材，挂商品肯定是得有点素材对吧
支持图片上传，返回图片URL及尺寸信息
"""
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from Tools.config import logger


UPLOAD_URL = "https://stream-upload.goofish.com/api/upload.api"

UPLOAD_HEADERS = {
    "origin": "https://www.goofish.com",
    "referer": "https://www.goofish.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
}

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def _get_image_dimensions(image_path: str) -> Tuple[int, int]:
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            return img.size
    except ImportError:
        logger.warning("Pillow 未安装，无法获取图片尺寸，将使用默认值")
        return (0, 0)
    except Exception as e:
        logger.warning(f"获取图片尺寸失败: {e}，将使用默认值")
        return (0, 0)


def upload_image(
    image_path: str,
    cookies: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    上传图片到闲鱼

    :param image_path: 本地图片文件路径
    :param cookies: 登录态 cookies（必须包含 cookie2）
    :return: 上传接口返回的 JSON 结果
    :raises ValueError: 文件格式不支持
    :raises RuntimeError: 上传失败
    """
    if cookies is None:
        raise ValueError("cookies 参数不能为空，需要登录态")

    suffix = Path(image_path).suffix.lower()
    if suffix not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError(f"不支持的图片格式: {suffix}，仅支持 {SUPPORTED_IMAGE_EXTENSIONS}")

    if not Path(image_path).exists():
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    params = {"floderId": "0", "appkey": "fleamarket", "_input_charset": "utf-8"}

    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/png"

    filename = Path(image_path).name

    from Tools.config import request_post

    with open(image_path, "rb") as f:
        files = {"file": (filename, f, mime_type)}
        response = request_post(
            UPLOAD_URL,
            headers=UPLOAD_HEADERS,
            cookies=cookies,
            params=params,
            files=files,
        )

    result = response.json()
    logger.info(f"图片上传完成: {filename}")
    return result


def upload_image_and_get_info(
    image_path: str,
    cookies: Optional[Dict[str, str]] = None,
    major: bool = False,
) -> Dict[str, Any]:
    """
    上传图片并返回可直接用于发布商品的图片信息字典

    :param image_path: 本地图片文件路径
    :param cookies: 登录态 cookies
    :param major: 是否为主图
    :return: 符合 imageInfoDOList 格式的字典
    """
    upload_result = upload_image(image_path, cookies)

    url = upload_result.get("url")
    if not url:
        raise RuntimeError(f"上传图片后未获取到URL: {upload_result}")

    width, height = _get_image_dimensions(image_path)

    return {
        "extraInfo": {"isH": "false", "isT": "false", "raw": "false"},
        "isQrCode": False,
        "url": url,
        "heightSize": height,
        "widthSize": width,
        "major": major,
        "type": 0,
        "status": "done",
    }


if __name__ == "__main__":
    image_path = "/Users/soin/SoinJobs/XianYu/test/extracted_image.png"
    try:
        cookies_ = {"cookie2": "your_cookie2_here"}
        response = upload_image(image_path, cookies=cookies_)
        print(response)
    except ValueError as e:
        print(f"参数错误: {e}")
    except FileNotFoundError as e:
        print(f"文件不存在: {e}")
