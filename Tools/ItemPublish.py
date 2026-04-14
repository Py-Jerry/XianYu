#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/04/13
# @Author  : Soin
# @File    : ItemPublish.py
# @Software: PyCharm
"""
闲鱼商品发布模块

封装商品发布的完整流程：数据构建 → 签名计算 → 数据编码 → HTTP 请求

核心流程：
    1. 使用 dataclass 构建结构化的商品数据（PublishItem 及其子模型）
    2. 调用 validate_publish_item 进行前置数据校验
    3. 从 cookies 中提取 token，结合时间戳和商品数据计算 MTOP 签名
    4. 将数据 URL 编码为 application/x-www-form-urlencoded 格式
    5. POST 到闲鱼 MTOP 网关完成发布

MTOP 签名算法（关键）：
    sign = md5(token + "&" + timestamp + "&" + appKey + "&" + data_json_str)
    其中：
        - token: 从 cookies._m_h5_tk 中提取（下划线前的部分）
        - timestamp: 毫秒级时间戳
        - appKey: 固定值 "34839810"
        - data_json_str: 商品数据的紧凑 JSON 字符串（separators=(",", ":"), ensure_ascii=False）

数据编码：
    请求体格式为 data=<url_encoded_json>，模拟浏览器 encodeURIComponent 行为，
    safe 字符集为 ~!*()'

扩展点 [EXT-I1]:
    - 商品编辑/下架接口（需逆向 mtop.idle.pc.idleitem.update / delete）
    - 商品列表查询接口
    - 分类属性动态获取（当前为硬编码预设，可对接闲鱼分类 API）
    - 地址定位接口（当前硬编码，可对接高德/百度 POI 搜索）
    - Token 自动刷新机制（参考 cv-cat/XianYuApis 的实现）
"""

import json
import time
import urllib.parse
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

from Tools.Encrypt import to_md5
from Tools.config import request_post, logger


# ============================================================
# 常量定义
# ============================================================

API_BASE_URL = "https://h5api.m.goofish.com/h5/mtop.idle.pc.idleitem.publish/1.0/"
APP_KEY = "34839810"
JSV = "2.7.2"

DEFAULT_HEADERS = {
    "accept": "application/json",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6,ja;q=0.5",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.goofish.com",
    "priority": "u=1, i",
    "referer": "https://www.goofish.com/",
    "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
}


# ============================================================
# 数据模型（dataclass）
# ============================================================
# 每个模型对应闲鱼发布接口的一个嵌套 JSON 对象，
# 提供 to_dict() 方法将 Python 风格字段名转换为闲鱼接口的驼峰命名。

@dataclass
class ImageInfo:
    """
    商品图片信息，对应接口的 imageInfoDOList 数组元素

    :param url: 图片 CDN 地址（由 MaterialPush.upload_image_and_get_info 返回）
    :param height_size: 图片高度（像素）
    :param width_size: 图片宽度（像素）
    :param major: 是否为主图（封面图），每张商品有且仅有一张主图
    :param is_qr_code: 是否为二维码图片
    :param type: 图片类型，0=普通图片
    :param status: 上传状态，"done"=已完成
    """
    url: str
    height_size: int
    width_size: int
    major: bool = False
    is_qr_code: bool = False
    type: int = 0
    status: str = "done"

    def to_dict(self) -> Dict[str, Any]:
        """转换为闲鱼接口所需的驼峰命名字典"""
        return {
            "extraInfo": {"isH": "false", "isT": "false", "raw": "false"},
            "isQrCode": self.is_qr_code,
            "url": self.url,
            "heightSize": self.height_size,
            "widthSize": self.width_size,
            "major": self.major,
            "type": self.type,
            "status": self.status,
        }


@dataclass
class ItemText:
    """
    商品文本信息，对应接口的 itemTextDTO

    :param title: 商品标题（最长60字符）
    :param desc: 商品描述
    :param title_desc_separate: 标题和描述是否分离显示
    """
    title: str
    desc: str
    title_desc_separate: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为闲鱼接口所需的驼峰命名字典"""
        return {
            "desc": self.desc,
            "title": self.title,
            "titleDescSeparate": self.title_desc_separate,
        }


@dataclass
class ItemLabel:
    """
    商品标签/属性，对应接口的 itemLabelExtList 数组元素

    标签分为两类：
        - 分类标签（propertyId="-10000"）：如 "其他技能服务"
        - 属性标签（propertyId 为具体 ID）：如 "计价方式: 元/起"

    properties 字段格式: "{propertyId}##{propertyName}:{valueId}##{valueName}"
    示例: "-10000##分类:201454913##其他技能服务"

    :param property_name: 属性名称，如 "分类"、"计价方式"
    :param text: 显示文本，如 "其他技能服务"、"元/起"
    :param properties: 属性拼接字符串（格式见上方说明）
    :param channel_cate_id: 渠道分类 ID
    :param tb_cat_id: 淘宝分类 ID
    :param property_id: 属性 ID，"-10000" 表示分类属性
    :param channel_cate_name: 渠道分类名称
    :param value_id: 属性值 ID
    :param value_name: 属性值名称
    :param sub_property_id: 子属性 ID
    :param sub_value_id: 子属性值 ID
    :param label_id: 标签 ID
    :param label_type: 标签类型，默认 "common"
    :param is_user_click: 是否用户点击选择，"1"=是
    :param is_user_cancel: 是否用户取消
    :param from_field: 来源，默认 "newPublishChoice"
    :param label_from: 标签来源，默认 "newPublish"

    扩展点 [EXT-I2]:
        - 当前标签数据需手动构造，可对接闲鱼分类属性查询 API 自动获取
    """
    property_name: str
    text: str
    properties: str
    channel_cate_id: str
    tb_cat_id: str
    property_id: str
    channel_cate_name: Optional[str] = None
    value_id: Optional[str] = None
    value_name: Optional[str] = None
    sub_property_id: Optional[str] = None
    sub_value_id: Optional[str] = None
    label_id: Optional[str] = None
    label_type: str = "common"
    is_user_click: str = "1"
    is_user_cancel: Optional[str] = None
    from_field: str = "newPublishChoice"
    label_from: str = "newPublish"

    def to_dict(self) -> Dict[str, Any]:
        """转换为闲鱼接口所需的驼峰命名字典"""
        return {
            "channelCateName": self.channel_cate_name,
            "valueId": self.value_id,
            "channelCateId": self.channel_cate_id,
            "valueName": self.value_name,
            "tbCatId": self.tb_cat_id,
            "subPropertyId": self.sub_property_id,
            "labelType": self.label_type,
            "subValueId": self.sub_value_id,
            "labelId": self.label_id,
            "propertyName": self.property_name,
            "isUserClick": self.is_user_click,
            "isUserCancel": self.is_user_cancel,
            "from": self.from_field,
            "propertyId": self.property_id,
            "labelFrom": self.label_from,
            "text": self.text,
            "properties": self.properties,
        }


@dataclass
class ItemPrice:
    """
    商品价格信息，对应接口的 itemPriceDTO

    价格单位为"分"（1元 = 100分），前端展示时需除以100。

    :param price_in_cent: 售价（分），如 "12000" 表示 120 元
    :param orig_price_in_cent: 原价（分），可选，如 "15000" 表示 150 元
    """
    price_in_cent: str
    orig_price_in_cent: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为闲鱼接口所需的驼峰命名字典

        注意：orig_price_in_cent 为 None 时不输出该字段，
        闲鱼接口会自动隐藏原价展示。
        """
        d: Dict[str, Any] = {"priceInCent": self.price_in_cent}
        if self.orig_price_in_cent is not None:
            d["origPriceInCent"] = self.orig_price_in_cent
        return d


@dataclass
class UserRightsProtocol:
    """
    用户权益协议，对应接口的 userRightsProtocols 数组元素

    可选的服务码：
        - FAST_DELIVERY_48_HOUR: 48小时发货
        - FAST_DELIVERY_24_HOUR: 24小时发货
        - VIRTUAL_NONCONFORMITY_FREE_REFUND_SERVICE: 虚拟商品不符免费退款
        - SKILL_PLAY_NO_MIND: 技能无忧
        - AI_SALE: AI 促销（部分分类可用）

    :param service_code: 服务码
    :param enable: 是否启用，默认 False
    """
    service_code: str
    enable: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为闲鱼接口所需的驼峰命名字典"""
        return {"enable": self.enable, "serviceCode": self.service_code}


@dataclass
class ItemPostFee:
    """
    商品运费信息，对应接口的 itemPostFeeDTO

    :param can_free_shipping: 是否包邮
    :param support_freight: 是否支持快递
    :param only_take_self: 是否仅自提
    :param template_id: 运费模板 ID，"0" 表示无模板
    """
    can_free_shipping: bool = False
    support_freight: bool = False
    only_take_self: bool = False
    template_id: str = "0"

    def to_dict(self) -> Dict[str, Any]:
        """转换为闲鱼接口所需的驼峰命名字典"""
        return {
            "canFreeShipping": self.can_free_shipping,
            "supportFreight": self.support_freight,
            "onlyTakeSelf": self.only_take_self,
            "templateId": self.template_id,
        }


@dataclass
class ItemAddr:
    """
    商品发货地址，对应接口的 itemAddrDTO

    :param area: 区/县，如 "翔安区"
    :param city: 城市，如 "厦门"
    :param division_id: 行政区划编码，如 350213
    :param gps: GPS 坐标，格式 "纬度,经度"，如 "24.565742,118.223729"
    :param poi_id: POI 兴趣点 ID（高德地图），如 "B0FFLEDOTH"
    :param poi_name: POI 名称，如 "厦门双十中学翔安附属学校(振南中学)"
    :param prov: 省份，如 "福建"

    扩展点 [EXT-I3]:
        - 可对接高德/百度地图 API 实现地址搜索和 POI 选择
        - 可通过 IP 定位自动填充默认地址
    """
    area: str
    city: str
    division_id: int
    gps: str
    poi_id: str
    poi_name: str
    prov: str

    def to_dict(self) -> Dict[str, Any]:
        """转换为闲鱼接口所需的驼峰命名字典"""
        return {
            "area": self.area,
            "city": self.city,
            "divisionId": self.division_id,
            "gps": self.gps,
            "poiId": self.poi_id,
            "poiName": self.poi_name,
            "prov": self.prov,
        }


@dataclass
class ItemCat:
    """
    商品分类信息，对应接口的 itemCatDTO

    闲鱼商品分类涉及三层 ID：
        - catId: 闲鱼自身分类 ID
        - channelCatId: 渠道分类 ID
        - tbCatId: 淘宝标准分类 ID

    :param cat_id: 闲鱼分类 ID，如 "50023914"
    :param cat_name: 分类名称，如 "其他技能服务"
    :param channel_cat_id: 渠道分类 ID，如 "201454913"
    :param tb_cat_id: 淘宝分类 ID，如 "201159705"
    """
    cat_id: str
    cat_name: str
    channel_cat_id: str
    tb_cat_id: str

    def to_dict(self) -> Dict[str, Any]:
        """转换为闲鱼接口所需的驼峰命名字典"""
        return {
            "catId": self.cat_id,
            "catName": self.cat_name,
            "channelCatId": self.channel_cat_id,
            "tbCatId": self.tb_cat_id,
        }


@dataclass
class PublishItem:
    """
    商品发布数据聚合模型，对应完整的发布接口请求体

    该 dataclass 将所有子模型聚合为一个完整商品对象，
    通过 to_dict() 生成可直接用于签名和编码的字典。

    :param title: 商品标题（必填，最长60字符）
    :param desc: 商品描述（必填）
    :param price_in_cent: 售价，单位分（必填，如 "12000"=120元）
    :param images: 图片列表（必填，至少1张），第一个元素默认为主图
    :param item_cat: 商品分类（必填）
    :param item_addr: 发货地址（必填）
    :param item_labels: 商品标签/属性列表
    :param orig_price_in_cent: 原价，单位分（选填）
    :param quantity: 数量，默认 "1"
    :param freebies: 是否赠品，默认 False
    :param item_type_str: 商品类型，"b"=普通商品
    :param simple_item: 是否简单商品，默认 True
    :param default_price: 是否使用默认价格，默认 False
    :param user_rights_protocols: 用户权益协议列表
    :param item_post_fee: 运费信息，默认包邮
    :param item_properties: 额外属性列表
    :param unique_code: 唯一码，默认自动生成（毫秒时间戳+3位随机）
    :param source_id: 来源标识，默认 "pcMainPublish"
    :param bizcode: 业务码，默认 "pcMainPublish"
    :param publish_scene: 发布场景，默认 "pcMainPublish"

    扩展点 [EXT-I4]:
        - 可增加商品编辑场景（复用模型，增加 item_id 字段）
        - 可增加定时发布功能（增加 publish_time 字段）
        - 可增加多规格 SKU 支持
    """
    title: str
    desc: str
    price_in_cent: str
    images: List[ImageInfo]
    item_cat: ItemCat
    item_addr: ItemAddr
    item_labels: List[ItemLabel] = field(default_factory=list)
    orig_price_in_cent: Optional[str] = None
    quantity: str = "1"
    freebies: bool = False
    item_type_str: str = "b"
    simple_item: bool = True
    default_price: bool = False
    user_rights_protocols: List[UserRightsProtocol] = field(default_factory=lambda: [
        UserRightsProtocol(service_code="FAST_DELIVERY_48_HOUR"),
        UserRightsProtocol(service_code="FAST_DELIVERY_24_HOUR"),
        UserRightsProtocol(service_code="VIRTUAL_NONCONFORMITY_FREE_REFUND_SERVICE"),
        UserRightsProtocol(service_code="SKILL_PLAY_NO_MIND"),
    ])
    item_post_fee: Optional[ItemPostFee] = None
    item_properties: List[Dict[str, Any]] = field(default_factory=list)
    unique_code: Optional[str] = None
    source_id: str = "pcMainPublish"
    bizcode: str = "pcMainPublish"
    publish_scene: str = "pcMainPublish"

    def __post_init__(self):
        """初始化后处理：填充默认值"""
        if self.item_post_fee is None:
            self.item_post_fee = ItemPostFee()
        if self.unique_code is None:
            self.unique_code = str(int(time.time() * 1000)) + str(int(time.time() * 1000) % 1000).zfill(3)

    def to_dict(self) -> Dict[str, Any]:
        """
        将聚合模型转换为闲鱼发布接口所需的完整字典

        转换逻辑：
            - simple_item 布尔值转为字符串 "true"/"false"（接口要求字符串）
            - 图片列表保证第一张为主图
            - 价格、标签、地址等子模型各自调用 to_dict() 转换
        """
        return {
            "freebies": self.freebies,
            "itemTypeStr": self.item_type_str,
            "quantity": self.quantity,
            "simpleItem": "true" if self.simple_item else "false",
            "imageInfoDOList": [img.to_dict() for img in self.images],
            "itemTextDTO": ItemText(title=self.title, desc=self.desc).to_dict(),
            "itemLabelExtList": [label.to_dict() for label in self.item_labels],
            "itemProperties": self.item_properties,
            "itemPriceDTO": ItemPrice(
                price_in_cent=self.price_in_cent,
                orig_price_in_cent=self.orig_price_in_cent,
            ).to_dict(),
            "userRightsProtocols": [p.to_dict() for p in self.user_rights_protocols],
            "itemPostFeeDTO": self.item_post_fee.to_dict(),
            "itemAddrDTO": self.item_addr.to_dict(),
            "defaultPrice": self.default_price,
            "itemCatDTO": self.item_cat.to_dict(),
            "uniqueCode": self.unique_code,
            "sourceId": self.source_id,
            "bizcode": self.bizcode,
            "publishScene": self.publish_scene,
        }


# ============================================================
# 签名与编码工具函数
# ============================================================

def _data_to_json_str(data: Dict[str, Any]) -> str:
    """
    将字典序列化为紧凑 JSON 字符串（无空格、无转义中文）

    这是签名计算的关键步骤：sign 的输入必须是确定性的 JSON 字符串，
    因此使用 separators=(",", ":") 去除所有空白，ensure_ascii=False 保留中文。

    :param data: 待序列化的字典
    :return: 紧凑 JSON 字符串，如 '{"freebies":false,"title":"测试"}'
    """
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def _encode_data(data_dict: Dict[str, Any]) -> str:
    """
    将商品数据编码为 application/x-www-form-urlencoded 格式

    编码规则：
        1. 先序列化为紧凑 JSON
        2. 对 JSON 字符串进行 URL 编码（模拟浏览器 encodeURIComponent）
        3. safe 字符集 "~!*()'" 不编码（与闲鱼前端 JS 行为一致）
        4. 添加 "data=" 前缀

    :param data_dict: 商品数据字典
    :return: 编码后的请求体字符串，如 "data=%7B%22freebies%22%3Afalse%7D"
    """
    json_str = _data_to_json_str(data_dict)
    encoded_json = urllib.parse.quote(json_str, safe="~!*()'")
    return "data=" + encoded_json


def _compute_sign(token: str, timestamp: str, data_dict: Dict[str, Any]) -> str:
    """
    计算 MTOP 接口签名

    签名算法：
        sign = md5(token + "&" + timestamp + "&" + appKey + "&" + data_json_str)

    各参数说明：
        - token: 从 cookies._m_h5_tk 提取（下划线前的32位十六进制字符串）
        - timestamp: 13位毫秒级时间戳
        - appKey: 固定值 "34839810"
        - data_json_str: 商品数据的紧凑 JSON 字符串（由 _data_to_json_str 生成）

    注意：data_json_str 必须与请求体中的 JSON 完全一致，否则签名校验失败。

    :param token: 登录 token（从 _m_h5_tk cookie 提取）
    :param timestamp: 毫秒级时间戳字符串
    :param data_dict: 商品数据字典
    :return: 32位小写十六进制 MD5 签名
    """
    data_str = _data_to_json_str(data_dict)
    raw = f"{token}&{timestamp}&{APP_KEY}&{data_str}"
    return to_md5(raw)


def _build_params(timestamp: str, sign: str) -> Dict[str, str]:
    """
    构建 MTOP 接口的 URL query 参数

    :param timestamp: 毫秒级时间戳
    :param sign: 计算得到的签名
    :return: URL 参数字典
    """
    return {
        "jsv": JSV,
        "appKey": APP_KEY,
        "t": timestamp,
        "sign": sign,
        "v": "1.0",
        "type": "originaljson",
        "accountSite": "xianyu",
        "dataType": "json",
        "timeout": "20000",
        "api": "mtop.idle.pc.idleitem.publish",
        "sessionOption": "AutoLoginOnly",
        "spm_cnt": "a21ybx.publish.0.0",
        "spm_pre": "a21ybx.personal.sidebar.1.32336ac2lwic8T",
        "log_id": "32336ac2lwic8T",
    }


def _extract_token(cookies: Dict[str, str]) -> str:
    """
    从 cookies 中提取 MTOP 签名所需的 token

    _m_h5_tk cookie 格式为 "{token}_{timestamp}"，如 "d7ceb821446686b2468651a251e0212c_1776078548849"
    提取下划线前的部分即为 token。

    :param cookies: 登录态 cookies 字典
    :return: token 字符串
    :raises ValueError: cookies 中缺少 _m_h5_tk 或格式无效

    扩展点 [EXT-I5]:
        - 可增加 token 过期检测（比较时间戳与当前时间）
        - 可增加 token 自动刷新逻辑（参考 cv-cat/XianYuApis）
    """
    tk = cookies.get("_m_h5_tk", "")
    if "_" in tk:
        return tk.split("_")[0]
    raise ValueError("cookies 中缺少有效的 _m_h5_tk，无法提取 token")


# ============================================================
# 数据校验
# ============================================================

def validate_publish_item(item: PublishItem) -> List[str]:
    """
    校验商品发布数据的完整性和合法性

    校验规则：
        - 标题：非空，不超过60字符
        - 描述：非空
        - 售价：必须为正整数（单位：分）
        - 原价（如有）：必须为数字且不低于售价
        - 图片：至少1张，URL 非空
        - 分类ID：非空
        - 地区编码：非零

    :param item: 待校验的 PublishItem 对象
    :return: 错误信息列表，空列表表示校验通过

    扩展点 [EXT-I6]:
        - 可增加图片 URL 有效性检查（HEAD 请求验证）
        - 可增加分类与标签一致性校验
        - 可增加违禁词检测
    """
    errors: List[str] = []
    if not item.title or not item.title.strip():
        errors.append("商品标题不能为空")
    if len(item.title) > 60:
        errors.append("商品标题不能超过60个字符")
    if not item.desc or not item.desc.strip():
        errors.append("商品描述不能为空")
    if not item.price_in_cent or not item.price_in_cent.isdigit():
        errors.append("价格必须为有效的数字（分）")
    elif int(item.price_in_cent) <= 0:
        errors.append("价格必须大于0")
    if item.orig_price_in_cent is not None:
        if not item.orig_price_in_cent.isdigit():
            errors.append("原价必须为有效的数字（分）")
        elif int(item.orig_price_in_cent) < int(item.price_in_cent):
            errors.append("原价不能低于售价")
    if not item.images:
        errors.append("至少需要一张商品图片")
    else:
        for i, img in enumerate(item.images):
            if not img.url:
                errors.append(f"第{i + 1}张图片URL不能为空")
    if not item.item_cat.cat_id:
        errors.append("商品分类ID不能为空")
    if not item.item_addr.division_id:
        errors.append("地区编码不能为空")
    return errors


# ============================================================
# 发布主流程
# ============================================================

def publish_item(item: PublishItem, cookies: Dict[str, str]) -> Dict[str, Any]:
    """
    发布商品到闲鱼平台

    完整流程：
        1. 数据校验（validate_publish_item）
        2. 提取 token（_extract_token）
        3. 生成时间戳
        4. 计算签名（_compute_sign）
        5. 编码请求体（_encode_data）
        6. 发送 POST 请求到 MTOP 网关
        7. 检查返回结果

    :param item: 完整的商品数据对象
    :param cookies: 登录态 cookies（必须包含 _m_h5_tk 和 cookie2）
    :return: 闲鱼接口返回的完整 JSON 数据
    :raises ValueError: 数据校验失败
    :raises RuntimeError: 闲鱼接口返回业务错误（如 token 过期、参数错误）
    :raises Exception: 网络请求异常（由 config.request_post 自动重试5次后抛出）

    扩展点 [EXT-I7]:
        - 可增加发布结果解析（提取商品 ID、商品链接等）
        - 可增加发布后自动上架逻辑
        - 可增加发布频率限制（避免被风控）
    """
    errors = validate_publish_item(item)
    if errors:
        raise ValueError(f"商品数据验证失败: {'; '.join(errors)}")

    token = _extract_token(cookies)
    timestamp = str(int(time.time() * 1000))
    data_dict = item.to_dict()

    sign = _compute_sign(token, timestamp, data_dict)
    params = _build_params(timestamp, sign)
    encoded_body = _encode_data(data_dict)

    logger.info(f"发布商品: title={item.title}, price={item.price_in_cent}分, sign={sign}")

    try:
        response = request_post(
            API_BASE_URL,
            headers=DEFAULT_HEADERS,
            cookies=cookies,
            params=params,
            data=encoded_body,
        )
        result = response.json()
    except Exception as e:
        logger.error(f"发布商品请求异常: {e}")
        raise

    # 检查业务返回码：ret[0] 应为 "SUCCESS::调用成功"
    ret_list = result.get("ret", [])
    if ret_list and ret_list[0] != "SUCCESS::调用成功":
        error_msg = ret_list[0] if ret_list else "未知错误"
        logger.error(f"发布商品失败: {error_msg}")
        raise RuntimeError(f"发布商品失败: {error_msg}")

    logger.info(f"发布商品成功: {result}")
    return result
