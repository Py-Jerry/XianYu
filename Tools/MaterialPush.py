#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/3/31 下午4:17
# @Author  : Soin
# @File    : MaterialPush.py
# @Software: PyCharm
"""
素材推送模块 —— 闲鱼图片上传

负责将本地图片文件上传到闲鱼 CDN，返回图片 URL 及尺寸信息，
供 ItemPublish 模块在发布商品时引用。

闲鱼图片上传接口：
    POST https://stream-upload.goofish.com/api/upload.api
    参数: floderId=0, appkey=fleamarket, _input_charset=utf-8
    认证: cookies 中的 cookie2 字段

返回数据结构（关键字段）：
    {
        "object": {
            "fileId": "...",
            "url": "https://img.alicdn.com/imgextra/...",   ← 图片 CDN 地址
            "pix": "2554x1554",                               ← 宽x高（像素）
            "size": "198089",                                 ← 文件大小（字节）
            "quality": 100
        },
        "success": true,
        "status": 0
    }

扩展点 [EXT-M1]:
    - 当前仅支持图片上传，闲鱼网页版暂不支持视频上传
    - 可扩展批量上传接口（并发上传多张图片）
    - 可增加图片压缩/水印功能（上传前预处理）
    - 可接入图片 CDN 缓存，避免同一图片重复上传
"""

import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from Tools.config import logger


# ============================================================
# 常量定义
# ============================================================

UPLOAD_URL = "https://stream-upload.goofish.com/api/upload.api"

UPLOAD_HEADERS = {
    "origin": "https://www.goofish.com",
    "referer": "https://www.goofish.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
}

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


# ============================================================
# 内部工具函数
# ============================================================

def _get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """
    获取图片的宽高尺寸（像素）

    优先使用 Pillow 读取真实尺寸；若 Pillow 不可用则返回 (0, 0)，
    由调用方决定是否使用接口返回的 pix 字段作为降级方案。

    :param image_path: 本地图片文件路径
    :return: (width, height) 元组，获取失败时返回 (0, 0)
    """
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


# ============================================================
# 公开 API
# ============================================================

def upload_image(
    image_path: str,
    cookies: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    上传单张图片到闲鱼 CDN

    流程：
        1. 校验文件格式（仅 PNG/JPG/JPEG）和文件存在性
        2. 自动识别 MIME 类型
        3. 以 multipart/form-data 方式 POST 到闲鱼上传接口
        4. 返回接口原始 JSON 响应

    :param image_path: 本地图片文件的绝对路径
    :param cookies: 登录态 cookies，必须包含 cookie2 字段
    :return: 闲鱼上传接口的原始 JSON 响应（结构见模块文档）
    :raises ValueError: cookies 为空或文件格式不支持
    :raises FileNotFoundError: 图片文件不存在
    :raises requests.exceptions.RequestException: 网络请求失败（由 config.request_post 自动重试）
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
    上传图片并返回可直接用于商品发布的图片信息字典

    该函数是 upload_image 的高层封装，在上传成功后：
        1. 从响应中提取图片 URL（兼容顶层 url 和嵌套 object.url 两种格式）
        2. 获取图片尺寸（优先使用接口返回的 pix 字段，降级使用 Pillow 读取）
        3. 组装为 imageInfoDOList 所需的字典格式

    :param image_path: 本地图片文件的绝对路径
    :param cookies: 登录态 cookies
    :param major: 是否为主图（商品列表展示的封面图），默认 False
    :return: 符合 imageInfoDOList 格式的字典，示例：
        {
            "extraInfo": {"isH": "false", "isT": "false", "raw": "false"},
            "isQrCode": false,
            "url": "https://img.alicdn.com/...",
            "heightSize": 1554,
            "widthSize": 2554,
            "major": true,
            "type": 0,
            "status": "done"
        }
    :raises RuntimeError: 上传成功但未获取到图片 URL

    扩展点 [EXT-M2]:
        - 可增加图片压缩逻辑（超过指定大小时自动压缩）
        - 可增加二维码检测逻辑（isQrCode 字段）
    """
    upload_result = upload_image(image_path, cookies)

    # 提取 URL：兼容两种响应格式
    # 格式1: {"url": "..."}           —— 直接在顶层
    # 格式2: {"object": {"url": "..."}} —— 嵌套在 object 中（当前闲鱼实际返回格式）
    url = upload_result.get("url")
    if not url:
        obj = upload_result.get("object", {})
        url = obj.get("url")
    if not url:
        raise RuntimeError(f"上传图片后未获取到URL: {upload_result}")

    # 提取尺寸：优先使用接口返回的 pix 字段（格式 "宽x高"，如 "2554x1554"）
    # 降级使用 Pillow 读取本地文件尺寸
    obj = upload_result.get("object", {})
    if not obj:
        obj = upload_result
    pix = obj.get("pix", "")

    width, height = _get_image_dimensions(image_path)
    if pix and "x" in pix:
        try:
            parts = pix.split("x")
            width = int(parts[0])
            height = int(parts[1])
        except (ValueError, IndexError):
            pass

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
