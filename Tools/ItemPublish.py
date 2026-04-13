#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/04/13
# @Author  : Soin
# @File    : ItemPublish.py
# @Software: PyCharm
"""
闲鱼商品发布模块
封装商品发布的完整流程：数据构建 → 签名 → 编码 → 请求发布
"""

import json
import time
import urllib.parse
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

from Tools.Encrypt import to_md5
from Tools.config import request_post, logger


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


@dataclass
class ImageInfo:
    url: str
    height_size: int
    width_size: int
    major: bool = False
    is_qr_code: bool = False
    type: int = 0
    status: str = "done"

    def to_dict(self) -> Dict[str, Any]:
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
    title: str
    desc: str
    title_desc_separate: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "desc": self.desc,
            "title": self.title,
            "titleDescSeparate": self.title_desc_separate,
        }


@dataclass
class ItemLabel:
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
    price_in_cent: str
    orig_price_in_cent: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"priceInCent": self.price_in_cent}
        if self.orig_price_in_cent is not None:
            d["origPriceInCent"] = self.orig_price_in_cent
        return d


@dataclass
class UserRightsProtocol:
    service_code: str
    enable: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {"enable": self.enable, "serviceCode": self.service_code}


@dataclass
class ItemPostFee:
    can_free_shipping: bool = False
    support_freight: bool = False
    only_take_self: bool = False
    template_id: str = "0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "canFreeShipping": self.can_free_shipping,
            "supportFreight": self.support_freight,
            "onlyTakeSelf": self.only_take_self,
            "templateId": self.template_id,
        }


@dataclass
class ItemAddr:
    area: str
    city: str
    division_id: int
    gps: str
    poi_id: str
    poi_name: str
    prov: str

    def to_dict(self) -> Dict[str, Any]:
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
    cat_id: str
    cat_name: str
    channel_cat_id: str
    tb_cat_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "catId": self.cat_id,
            "catName": self.cat_name,
            "channelCatId": self.channel_cat_id,
            "tbCatId": self.tb_cat_id,
        }


@dataclass
class PublishItem:
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
        if self.item_post_fee is None:
            self.item_post_fee = ItemPostFee()
        if self.unique_code is None:
            self.unique_code = str(int(time.time() * 1000)) + str(int(time.time() * 1000) % 1000).zfill(3)

    def to_dict(self) -> Dict[str, Any]:
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


def _data_to_json_str(data: Dict[str, Any]) -> str:
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def _encode_data(data_dict: Dict[str, Any]) -> str:
    json_str = _data_to_json_str(data_dict)
    encoded_json = urllib.parse.quote(json_str, safe="~!*()'")
    return "data=" + encoded_json


def _compute_sign(token: str, timestamp: str, data_dict: Dict[str, Any]) -> str:
    data_str = _data_to_json_str(data_dict)
    raw = f"{token}&{timestamp}&{APP_KEY}&{data_str}"
    return to_md5(raw)


def _build_params(timestamp: str, sign: str) -> Dict[str, str]:
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
    tk = cookies.get("_m_h5_tk", "")
    if "_" in tk:
        return tk.split("_")[0]
    raise ValueError("cookies 中缺少有效的 _m_h5_tk，无法提取 token")


def validate_publish_item(item: PublishItem) -> List[str]:
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


def publish_item(item: PublishItem, cookies: Dict[str, str]) -> Dict[str, Any]:
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

    ret_list = result.get("ret", [])
    if ret_list and ret_list[0] != "SUCCESS::调用成功":
        error_msg = ret_list[0] if ret_list else "未知错误"
        logger.error(f"发布商品失败: {error_msg}")
        raise RuntimeError(f"发布商品失败: {error_msg}")

    logger.info(f"发布商品成功: {result}")
    return result
