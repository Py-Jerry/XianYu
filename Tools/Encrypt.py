#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/3/31 下午4:11
# @Author  : Soin
# @File    : Encrypt.py
# @Software: PyCharm
"""
    这是一个md5加密工具
"""
import hashlib
import base64

def to_md5(plaintext:str)->str:
   """
    对字符串进行md5加密
   :param plaintext: 明文字符串
   :return: 加密后的字符串
   """
   return hashlib.md5(plaintext.encode()).hexdigest()

def to_base64(plaintext:str)->str:
   """
    对字符串进行base64加密
   :param plaintext: 明文字符串
   :return: 加密后的字符串
   """
   return base64.b64encode(plaintext.encode()).decode()
def from_base64(plaintext:str, decode_to_str:bool=True)->bytes:
    """
        对base64加密后的字符串进行解密
       :param plaintext: 加密后的字符串
       :param decode_to_str: 是否解码为字符串（默认True）
       :return: 解密后的字节或字符串
       """
    # 解码base64
    decoded_bytes = base64.b64decode(plaintext.encode())

    # 根据参数决定返回类型
    if decode_to_str:
        return decoded_bytes.decode('utf-8')
    else:
        return decoded_bytes

def from_base64_to_str(plaintext:str)->str:
    """
        对base64加密后的字符串进行解密并返回字符串
       :param plaintext: 加密后的字符串
       :return: 解密后的字符串
       """
    return from_base64(plaintext, decode_to_str=True)

def from_base64_to_bytes(plaintext:str)->bytes:
    """
        对base64加密后的字符串进行解密并返回字节
       :param plaintext: 加密后的字符串
       :return: 解密后的字节
       """
    return from_base64(plaintext, decode_to_str=False)

if __name__ == '__main__':
    md5_result = to_md5('6784ec914d80fc4d4544f6270c11bd26&1775184669255&34839810&{"sessionTypes":"1,19,15,32,3,44,51,52,24","fetch":50}') # ->>> e10adc3949ba59abbe56e057f20f883e
    print(md5_result)
