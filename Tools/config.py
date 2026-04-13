# -*- coding: utf-8 -*-
"""
@File    :   config.py
@Time    :   2026/03/26 14:58
@Author  :   Soin
@Desc    :   全局的一个配置文档，封装了一些类在这里面
"""

import requests
from loguru import logger
from pathlib import Path
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import datetime
import sys
from requests.adapters import HTTPAdapter
import urllib3
import json
import os

# 定义日志配置
config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": (
                "<green>{time:YYYYMMDD HH:mm:ss}</green> | "
                "{process.name} | {thread.name} | "
                "<level>{module}</level>.<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{level.icon}{level}</level>: <level>{message}</level>"
            ),
        },
        {
            "sink": f"./temp_logs/{time.strftime('%Y-%m-%d')}咸鱼.log",
            "level": "DEBUG",
            "rotation": "1 week",
            "retention": "7 days",
            "enqueue": True,
            "compression": "zip",
            "encoding": "utf-8",
        },
    ],
    "extra": {"user": "Soin"},
}
# 打包版日志配置
# config = {
#     "handlers": [
#         {
#             "sink": f"./temp_logs/咸鱼/{time.strftime('%Y-%m-%d')}.log",
#             "level": "DEBUG",
#             "rotation": "1 week",
#             "retention": "7 days",
#             "enqueue": True,
#             "compression": "zip",
#             "encoding": "utf-8",
#         },
#     ],
#     "extra": {"user": "Soin"},
# }


# 应用配置
logger.configure(**config)


class StableSession:
    session = requests.Session()
    adapter = HTTPAdapter(
        pool_connections=100,
        pool_maxsize=100,
        max_retries=0  # ❗ 禁用 urllib3 retry，全部交给 tenacity
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)


def _network_request(method, url, **kwargs):
    resp = StableSession.session.request(
        method,
        url,
        **kwargs
    )
    resp.raise_for_status()
    return resp


@retry(
    stop=stop_after_attempt(5),  # 建议重试次数设为 5
    wait=wait_exponential(multiplier=1, min=2, max=10),  # 失败后等待时间稍微拉长，给服务器喘息
    retry=retry_if_exception_type((
            requests.exceptions.SSLError,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ChunkedEncodingError,  # 对应 IncompleteRead
            urllib3.exceptions.IncompleteRead,  # 底层 urllib3 异常
            urllib3.exceptions.ProtocolError,
            requests.exceptions.Timeout,  # 覆盖所有 Timeout 子类
            OSError,  # SSLWantWriteError 的父类
    )),
    reraise=True
)
def request_retry(method, url, **kwargs):
    return _network_request(method, url, **kwargs)


def request_get(url, **kwargs):
    return request_retry("GET", url, timeout=(5, 30), **kwargs)


def request_head(url, **kwargs):
    return request_retry("HEAD", url, timeout=(3, 10), **kwargs)


def request_post(url, **kwargs):
    return request_retry("POST", url, timeout=(5, 30), **kwargs)


def request_put(url, **kwargs):
    return request_retry("PUT", url, timeout=(10, 120), **kwargs)


def taskid(user_id):
    # 算出唯一 ID
    date_part = datetime.datetime.now().strftime("%y%m%d%H%M%S")
    base_prefix = f"{user_id}{date_part}"
    return base_prefix
