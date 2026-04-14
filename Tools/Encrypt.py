#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/3/31 下午4:11
# @Author  : Soin
# @File    : Encrypt.py
# @Software: PyCharm
"""
加密工具模块

提供 MD5 哈希和 Base64 编解码能力，是闲鱼 API 签名计算的基础依赖。

核心用途：
    - to_md5: 用于闲鱼 MTOP 接口的 sign 签名计算
             签名公式: md5(token + "&" + timestamp + "&" + appKey + "&" + data)
    - to_base64 / from_base64: 用于 WebSocket 消息的编解码

扩展点 [EXT-P1]:
    - 若闲鱼后续升级签名算法（如 HMAC-SHA256），可在此模块新增对应函数，
      并在 ItemPublish._compute_sign 中切换调用
    - 可考虑增加签名防重放机制（nonce + timestamp 校验）
"""

import hashlib
import base64


def to_md5(plaintext: str) -> str:
    """
    对字符串进行 MD5 哈希，返回 32 位小写十六进制摘要

    注意：MD5 是哈希而非加密，不可逆。闲鱼 MTOP 接口的 sign 即使用此函数计算。

    :param plaintext: 明文字符串，如 "token&timestamp&appKey&data"
    :return: 32位小写十六进制 MD5 摘要，如 "e10adc3949ba59abbe56e057f20f883e"
    """
    return hashlib.md5(plaintext.encode()).hexdigest()


def to_base64(plaintext: str) -> str:
    """
    对字符串进行 Base64 编码

    :param plaintext: 原始字符串
    :return: Base64 编码后的字符串
    """
    return base64.b64encode(plaintext.encode()).decode()


def from_base64(plaintext: str, decode_to_str: bool = True) -> bytes | str:
    """
    对 Base64 编码的字符串进行解码

    :param plaintext: Base64 编码后的字符串
    :param decode_to_str: 是否解码为字符串（默认 True）；False 时返回原始字节
    :return: 解码后的字符串或字节
    """
    decoded_bytes = base64.b64decode(plaintext.encode())
    if decode_to_str:
        return decoded_bytes.decode('utf-8')
    return decoded_bytes


def from_base64_to_str(plaintext: str) -> str:
    """
    对 Base64 编码的字符串进行解码并返回字符串

    :param plaintext: Base64 编码后的字符串
    :return: 解码后的字符串
    """
    return from_base64(plaintext, decode_to_str=True)


def from_base64_to_bytes(plaintext: str) -> bytes:
    """
    对 Base64 编码的字符串进行解码并返回字节

    :param plaintext: Base64 编码后的字符串
    :return: 解码后的原始字节
    """
    return from_base64(plaintext, decode_to_str=False)


if __name__ == '__main__':
    md5_result = to_md5('6784ec914d80fc4d4544f6270c11bd26&1775184669255&34839810&{"sessionTypes":"1,19,15,32,3,44,51,52,24","fetch":50}')
    print(md5_result)
