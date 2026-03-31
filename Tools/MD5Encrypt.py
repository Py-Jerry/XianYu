#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/3/31 下午4:11
# @Author  : Soin
# @File    : MD5Encrypt.py
# @Software: PyCharm
"""
    这是一个md5加密工具
"""
import hashlib

def to_md5(plaintext:str)->str:
   """
    对字符串进行md5加密
   :param plaintext: 明文字符串
   :return: 加密后的字符串
   """
   return hashlib.md5(plaintext.encode()).hexdigest()

if __name__ == '__main__':
    md5_result = to_md5("123456") # ->>> e10adc3949ba59abbe56e057f20f883e
    print(md5_result)
