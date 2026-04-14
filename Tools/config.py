# -*- coding: utf-8 -*-
"""
@File    :   config.py
@Time    :   2026/03/26 14:58
@Author  :   Soin
@Desc    :   全局配置模块

提供项目级别的公共基础设施，被所有业务模块引用：
    1. 日志系统（loguru）—— 统一格式、自动轮转、文件归档
    2. HTTP 请求层（StableSession + tenacity 重试）—— 所有外部 API 调用的底层
    3. 工具函数（taskid）

架构设计：
    StableSession 是全局单例的 requests.Session，配合 HTTPAdapter 连接池复用 TCP 连接。
    tenacity 装饰器在应用层实现指数退避重试，与 urllib3 底层重试互不干扰。

扩展点 [EXT-C1]:
    - 日志 sink 可扩展为远程日志服务（如 ELK / Loki）
    - request_retry 的重试策略可按 API 差异化配置（如发布接口重试次数更少）
    - 可引入 httpx 替代 requests 以支持 HTTP/2 和 async
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

# ============================================================
# 日志配置
# ============================================================
# 双通道输出：控制台（彩色） + 文件（按天轮转，保留7天，zip压缩）
# 扩展点 [EXT-C2]: 打包部署时切换为下方注释配置，日志写入相对路径
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

logger.configure(**config)


# ============================================================
# HTTP 请求层
# ============================================================

class StableSession:
    """
    全局 HTTP Session 单例

    设计思路：
        - 使用连接池（pool_connections=100, pool_maxsize=100）复用 TCP 连接，
          避免每次请求都建立新连接的开销
        - max_retries=0 禁用 urllib3 底层重试，将重试逻辑统一交给 tenacity 处理，
          避免两层重试叠加导致等待时间不可控

    扩展点 [EXT-C3]:
        - 可添加全局请求钩子（如自动注入 Cookie、请求耗时统计）
        - 可接入代理池（session.proxies）
    """
    session = requests.Session()
    adapter = HTTPAdapter(
        pool_connections=100,
        pool_maxsize=100,
        max_retries=0,
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)


def _network_request(method, url, **kwargs):
    """
    底层请求执行函数，不包含重试逻辑

    :param method: HTTP 方法（GET/POST/PUT 等）
    :param url: 请求 URL
    :param kwargs: 传递给 session.request 的额外参数（headers, cookies, data 等）
    :return: requests.Response 对象
    :raises requests.exceptions.HTTPError: 响应状态码非 2xx 时抛出
    """
    resp = StableSession.session.request(method, url, **kwargs)
    resp.raise_for_status()
    return resp


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((
        requests.exceptions.SSLError,
        requests.exceptions.ConnectionError,
        requests.exceptions.ReadTimeout,
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ChunkedEncodingError,
        urllib3.exceptions.IncompleteRead,
        urllib3.exceptions.ProtocolError,
        requests.exceptions.Timeout,
        OSError,
    )),
    reraise=True,
)
def request_retry(method, url, **kwargs):
    """
    带自动重试的请求函数

    重试策略：
        - 最多重试 5 次
        - 指数退避：2s → 4s → 8s → 10s（上限）
        - 仅对网络层异常重试，业务层异常（如 HTTP 4xx）不重试

    :param method: HTTP 方法
    :param url: 请求 URL
    :param kwargs: 传递给 _network_request 的额外参数
    :return: requests.Response 对象
    """
    return _network_request(method, url, **kwargs)


def request_get(url, **kwargs):
    """
    GET 请求，超时 (连接5s, 读取30s)

    :param url: 请求 URL
    :param kwargs: 额外参数
    :return: requests.Response
    """
    return request_retry("GET", url, timeout=(5, 30), **kwargs)


def request_head(url, **kwargs):
    """
    HEAD 请求，超时 (连接3s, 读取10s)

    :param url: 请求 URL
    :param kwargs: 额外参数
    :return: requests.Response
    """
    return request_retry("HEAD", url, timeout=(3, 10), **kwargs)


def request_post(url, **kwargs):
    """
    POST 请求，超时 (连接5s, 读取30s)

    :param url: 请求 URL
    :param kwargs: 额外参数（headers, cookies, data, files 等）
    :return: requests.Response
    """
    return request_retry("POST", url, timeout=(5, 30), **kwargs)


def request_put(url, **kwargs):
    """
    PUT 请求，超时 (连接10s, 读取120s)，适用于大文件上传等耗时操作

    :param url: 请求 URL
    :param kwargs: 额外参数
    :return: requests.Response
    """
    return request_retry("PUT", url, timeout=(10, 120), **kwargs)


def taskid(user_id):
    """
    生成任务唯一 ID

    格式: {user_id}{yyMMddHHmmss}
    示例: tb764198236260326143758

    :param user_id: 用户标识
    :return: 唯一 ID 字符串

    扩展点 [EXT-C4]:
        - 当前仅精确到秒级，高并发场景可能冲突，可追加随机后缀
        - 可引入 UUID 替代自定义拼接
    """
    date_part = datetime.datetime.now().strftime("%y%m%d%H%M%S")
    base_prefix = f"{user_id}{date_part}"
    return base_prefix
