#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/04/13
# @Author  : Soin
# @File    : app.py
# @Software: PyCharm
"""
闲鱼商品发布 Web 应用

基于 Flask 的 Web 服务，为前端页面提供 RESTful API，
将前端表单数据转换为 ItemPublish 模块所需的数据结构并调用发布流程。

架构：
    前端 (static/index.html)
        ↓ HTTP REST API
    Flask 路由层 (本文件)
        ↓ 调用业务模块
    ItemPublish + MaterialPush
        ↓ HTTP 请求
    闲鱼 MTOP 网关

API 接口列表：
    GET  /                → 前端页面
    GET  /api/categories  → 获取商品分类预设列表
    POST /api/upload      → 上传图片到闲鱼 CDN
    POST /api/publish     → 发布商品
    POST /api/validate    → 前端表单校验

扩展点 [EXT-A1]:
    - 可增加 Cookie 管理接口（登录/刷新 Token）
    - 可增加商品管理接口（列表/编辑/下架）
    - 可增加 WebSocket 实时推送发布状态
    - 可增加用户系统（多账号管理）
    - 可将 COOKIES 和 CATEGORY_PRESETS 迁移到数据库/配置文件
"""

import os
import uuid
import json
from pathlib import Path
from typing import Any, Dict

from flask import Flask, request, jsonify, send_from_directory
from Tools.ItemPublish import (
    PublishItem,
    ImageInfo,
    ItemCat,
    ItemAddr,
    ItemLabel,
    validate_publish_item,
    publish_item,
)
from Tools.MaterialPush import upload_image_and_get_info
from Tools.config import logger

app = Flask(__name__, static_folder="static", static_url_path="/static")

# ============================================================
# 配置常量
# ============================================================

# 临时文件目录：前端上传的图片先保存到此处，上传到闲鱼后删除
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 图片大小上限：20MB
MAX_IMAGE_SIZE = 20 * 1024 * 1024

# 登录态 cookies（从浏览器开发者工具获取）
# 扩展点 [EXT-A2]: 应迁移到环境变量或配置文件，避免硬编码敏感信息
COOKIES = {
}

# 商品分类预设数据
# 扩展点 [EXT-A3]: 可对接闲鱼分类查询 API 动态获取，支持全部分类
CATEGORY_PRESETS = [
    {
        "cat_id": "50023914",
        "cat_name": "其他技能服务",
        "channel_cat_id": "201454913",
        "tb_cat_id": "201159705",
        "labels": [
            {
                "property_name": "分类",
                "text": "其他技能服务",
                "properties": "-10000##分类:201454913##其他技能服务",
                "channel_cate_id": "201454913",
                "tb_cat_id": "201159705",
                "property_id": "-10000",
                "channel_cate_name": "其他技能服务",
            },
            {
                "property_name": "计价方式",
                "text": "元/起",
                "properties": "150360447##计价方式:432128703##元/起",
                "channel_cate_id": "201454913",
                "tb_cat_id": "201159705",
                "property_id": "150360447",
                "value_id": "432128703",
                "value_name": "元/起",
            },
        ],
    },
    {
        "cat_id": "50025461",
        "cat_name": "软件安装包/序列号/激活码",
        "channel_cat_id": "201449620",
        "tb_cat_id": "50003316",
        "labels": [
            {
                "property_name": "分类",
                "text": "软件安装包/序列号/激活码",
                "properties": "-10000##分类:201449620##软件安装包/序列号/激活码",
                "channel_cate_id": "201449620",
                "tb_cat_id": "50003316",
                "property_id": "-10000",
                "channel_cate_name": "软件安装包/序列号/激活码",
            },
        ],
    },
]


# ============================================================
# 页面路由
# ============================================================

@app.route("/")
def index():
    """返回前端单页应用页面"""
    return send_from_directory("static", "index.html")


@app.route("/favicon.ico")
def favicon():
    """返回空响应，避免浏览器 404 报错"""
    return "", 204


# ============================================================
# API 路由
# ============================================================

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """
    获取商品分类预设列表

    返回前端分类选择器所需的数据，包含分类 ID、名称及关联的标签属性。

    :return: JSON {"categories": [...]}
    """
    return jsonify({"categories": CATEGORY_PRESETS})


@app.route("/api/upload", methods=["POST"])
def upload_image():
    """
    上传图片到闲鱼 CDN

    流程：
        1. 从请求中获取文件对象
        2. 校验文件格式（PNG/JPG/JPEG）和大小（≤20MB）
        3. 保存到临时目录
        4. 调用 MaterialPush.upload_image_and_get_info 上传到闲鱼
        5. 删除临时文件
        6. 返回图片 URL 和尺寸信息

    请求格式: multipart/form-data，字段名 "file"
    成功响应: {"success": true, "data": {"url": "...", "heightSize": N, "widthSize": N}}
    失败响应: {"success": false, "message": "错误描述"}

    :return: JSON 响应
    """
    if "file" not in request.files:
        return jsonify({"success": False, "message": "未找到上传文件"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"success": False, "message": "文件名为空"}), 400

    # 校验文件格式
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg"}:
        return jsonify({"success": False, "message": f"不支持的图片格式: {suffix}"}), 400

    # 校验文件大小
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_IMAGE_SIZE:
        return jsonify({"success": False, "message": f"图片大小超过限制({MAX_IMAGE_SIZE // 1024 // 1024}MB)"}), 400

    # 保存到临时文件 → 上传 → 删除临时文件
    temp_filename = f"{uuid.uuid4().hex}{suffix}"
    temp_path = os.path.join(UPLOAD_DIR, temp_filename)
    try:
        file.save(temp_path)

        img_info = upload_image_and_get_info(temp_path, cookies=COOKIES, major=False)

        return jsonify({
            "success": True,
            "data": {
                "url": img_info["url"],
                "heightSize": img_info["heightSize"],
                "widthSize": img_info["widthSize"],
            },
        })
    except Exception as e:
        logger.error(f"图片上传失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # 确保临时文件被清理
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route("/api/publish", methods=["POST"])
def publish():
    """
    发布商品到闲鱼

    流程：
        1. 解析前端 JSON 请求体
        2. 构建图片列表（ImageInfo），自动将第一张设为主图
        3. 构建分类（ItemCat）、地址（ItemAddr）、标签（ItemLabel）
        4. 价格从"元"转换为"分"（前端传元，接口要分）
        5. 组装 PublishItem 并校验
        6. 调用 ItemPublish.publish_item 发布
        7. 返回发布结果

    请求格式: application/json
    请求体字段:
        - title: 商品标题
        - desc: 商品描述
        - price: 售价（元）
        - origPrice: 原价（元，可选）
        - freebies: 是否包邮
        - images: [{url, heightSize, widthSize, major}, ...]
        - itemCat: {catId, catName, channelCatId, tbCatId}
        - itemAddr: {area, city, divisionId, gps, poiId, poiName, prov}
        - itemLabels: [{propertyName, text, properties, ...}, ...]

    成功响应: {"success": true, "data": {闲鱼返回数据}}
    失败响应: {"success": false, "message": "错误描述"}

    :return: JSON 响应
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求体为空"}), 400

        # 构建图片列表
        images = []
        for img_data in data.get("images", []):
            images.append(ImageInfo(
                url=img_data["url"],
                height_size=img_data.get("heightSize", 0),
                width_size=img_data.get("widthSize", 0),
                major=img_data.get("major", False),
            ))
        # 保证第一张为主图
        if images:
            images[0].major = True

        # 构建分类
        cat_data = data.get("itemCat", {})
        item_cat = ItemCat(
            cat_id=cat_data.get("catId", ""),
            cat_name=cat_data.get("catName", ""),
            channel_cat_id=cat_data.get("channelCatId", ""),
            tb_cat_id=cat_data.get("tbCatId", ""),
        )

        # 构建地址
        addr_data = data.get("itemAddr", {})
        item_addr = ItemAddr(
            area=addr_data.get("area", ""),
            city=addr_data.get("city", ""),
            division_id=addr_data.get("divisionId", 0),
            gps=addr_data.get("gps", ""),
            poi_id=addr_data.get("poiId", ""),
            poi_name=addr_data.get("poiName", ""),
            prov=addr_data.get("prov", ""),
        )

        # 构建标签列表
        labels = []
        for lbl in data.get("itemLabels", []):
            labels.append(ItemLabel(
                property_name=lbl.get("propertyName", ""),
                text=lbl.get("text", ""),
                properties=lbl.get("properties", ""),
                channel_cate_id=lbl.get("channelCateId", ""),
                tb_cat_id=lbl.get("tbCatId", ""),
                property_id=lbl.get("propertyId", ""),
                channel_cate_name=lbl.get("channelCateName"),
                value_id=lbl.get("valueId"),
                value_name=lbl.get("valueName"),
            ))

        # 价格转换：元 → 分（前端传元，接口要分）
        price_in_cent = str(int(float(data.get("price", 0)) * 100))
        orig_price_in_cent = None
        if data.get("origPrice"):
            orig_price_in_cent = str(int(float(data["origPrice"]) * 100))

        # 组装商品数据
        item = PublishItem(
            title=data.get("title", ""),
            desc=data.get("desc", ""),
            price_in_cent=price_in_cent,
            orig_price_in_cent=orig_price_in_cent,
            images=images,
            item_cat=item_cat,
            item_addr=item_addr,
            item_labels=labels,
            freebies=data.get("freebies", False),
        )

        # 前置校验
        errors = validate_publish_item(item)
        if errors:
            return jsonify({"success": False, "message": "; ".join(errors)}), 400

        # 执行发布
        result = publish_item(item, COOKIES)
        return jsonify({"success": True, "data": result})

    except ValueError as e:
        logger.error(f"发布校验错误: {e}")
        return jsonify({"success": False, "message": str(e)}), 400
    except RuntimeError as e:
        logger.error(f"发布失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        logger.error(f"发布异常: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/validate", methods=["POST"])
def validate():
    """
    前端表单校验接口

    在用户点击发布前，先调用此接口校验数据完整性，
    避免无效请求发送到闲鱼。

    请求格式: application/json（与 /api/publish 相同）
    响应: {"valid": true/false, "errors": ["错误1", ...]}

    :return: JSON 响应
    """
    data = request.get_json()
    if not data:
        return jsonify({"valid": False, "errors": ["请求体为空"]}), 400

    images = [ImageInfo(url=img.get("url", ""), height_size=0, width_size=0) for img in data.get("images", [])]
    item = PublishItem(
        title=data.get("title", ""),
        desc=data.get("desc", ""),
        price_in_cent=str(int(float(data.get("price", 0)) * 100)) if data.get("price") else "0",
        images=images,
        item_cat=ItemCat(cat_id="1", cat_name="", channel_cat_id="", tb_cat_id=""),
        item_addr=ItemAddr(area="", city="", division_id=1, gps="", poi_id="", poi_name="", prov=""),
    )
    errors = validate_publish_item(item)
    return jsonify({"valid": len(errors) == 0, "errors": errors})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
