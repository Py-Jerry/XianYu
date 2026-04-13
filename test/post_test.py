# -*- coding: utf-8 -*-
"""
@File    :   post_test.py
@Time    :   2026/03/26 10:39
@Author  :   Soin
@Desc    :   用来做测试的文件
"""

import requests
import json
import urllib.parse
from typing import Dict, Any
import hashlib

import time

def to_md5(plaintext:str)->str:
   """
    对字符串进行md5加密
   :param plaintext: 明文字符串
   :return: 加密后的字符串
   """
   return hashlib.md5(plaintext.encode()).hexdigest()

def encode(data_dict: Dict[str, Any]) -> str:
    json_str = json.dumps(
        data_dict,
        separators=(',', ':'),
        ensure_ascii=False
    )

    # 👇 模拟 encodeURIComponent
    encoded_json = urllib.parse.quote(
        json_str,
        safe="~!*()'"
    )

    # 添加 'data=' 前缀
    return "data=" + encoded_json.replace("False", "false").replace("True", "true").replace('None', 'null')


headers = {
    "accept": "application/json",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6,ja;q=0.5",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.goofish.com",
    "priority": "u=1, i",
    "referer": "https://www.goofish.com/",
    "sec-ch-ua": "\"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Google Chrome\";v=\"146\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
}
timestamp = str(int(time.time() * 1000))

cookies = {
    # "t": "a629bf23cebb50370d1ab0099dc06b0c",
    # "tracknick": "tb764198236",
    # "unb": "4109648144",
    # "havana_lgc2_77": "eyJoaWQiOjQxMDk2NDgxNDQsInNnIjoiM2NkZjJiNjAyNDA0ZDNhNmJlM2EwZDliZDQxYjExNjMiLCJzaXRlIjo3NywidG9rZW4iOiIxdnJTX2JQTm5iekdxNVpaSzRqOTBBZyJ9",
    # "_hvn_lgc_": "77",
    # "havana_lgc_exp": "1777456621946",
    # "cna": "w7dSIiyCeDACAdrPvgVPppxW",
    "cookie2": "180109ea3efa8e358c1e050bd4288c44",
    # "_samesite_flag_": "true",
    # "_tb_token_": "76e953eae550e",
    # "sgcookie": "E1009O0MUMdQna4VubBUljZnXpdiDu93sBvYkhQv%2BaLMgJLYdeJvsmkCT3P9GFKi1U3BB4UwY43tUCL9Yt6jPv18l7R9Tl8xLOMqitwHazi8i44%3D",
    # "csg": "1e3a329a",
    # "sdkSilent": "1775199406788",
    # "xlly_s": "1",
    # "mtop_partitioned_detect": "1",
    '_m_h5_tk': f'19ae7538f03b06f940195722df1ed877_1775817304879',
    '_m_h5_tk_enc': '123e7a0bcf74d12c004edb0fecf61819',
    # "tfstk": "gJfjHxZJtGCzlG4YXmzrPKblggd1fzPUGVTO-NhqWIdxXcQp4i-2gPV6XixPgn72MNhOfgQqg151Ef_hSszD_rAcoCATYkPFCZbDsTId571X2QLhyEnxH8RJQa73NkPUTZevoC78YtRlFZLwWCLvBFF8PFTiHCL9WztJ5eDtDGdTPzTwJFH9Hn38wFtJXCdOXUhJqFO9kGdTPaKkWUyq5UrHqZaTCA6OLWHCO3Gt6_T8jHQfDUY5NZpDvKAt6p5WlKtdk6dgxNL1p69cvuk2D96NAeS4wjsCki6ppsn8VCbPdGTCMyHBfibRgLCY7vYkstBpM1ZIDZpCwsRcFkGevTbO1LQ0AvYPBw5VCiro6nWCyg9Fa0lewssfMLOd4qleAnzsC49n1UtUPzMiIGhnFcUe6xqXHUYz3zaSLd9vrU6zPzMiIKLkzGz7PvJ1."
}
# timestamp = str(1775200773560)
url = "https://h5api.m.goofish.com/h5/mtop.idle.pc.idleitem.publish/1.0/"
params = {
    "jsv": "2.7.2",
    "appKey": "34839810",
    "t": timestamp,  # 时间戳 毫秒时间戳
    "v": "1.0",
    "type": "originaljson",
    "accountSite": "xianyu",
    "dataType": "json",
    "timeout": "20000",  # 超时时间 毫秒
    "api": "mtop.idle.pc.idleitem.publish",
    "sessionOption": "AutoLoginOnly",
    "spm_cnt": "a21ybx.publish.0.0",
    "spm_pre": "a21ybx.personal.sidebar.1.32336ac2lwic8T",
    "log_id": "32336ac2lwic8T"
}
data = {
    "freebies": False,
    "itemTypeStr": "b",
    "quantity": "1",
    "simpleItem": "true",
    "imageInfoDOList": [
        {
            "extraInfo": {
                "isH": "false",
                "isT": "false",
                "raw": "false"
            },
            "isQrCode": False,
            "url": "https://img.alicdn.com/imgextra/i1/O1CN01uAZQzl2A20gvvsJ7z_!!4109648144-2-fleamarket.png",
            "heightSize": 470,
            "widthSize": 849,
            "major": True,
            "type": 0,
            "status": "done"
        },
        {
            "extraInfo": {
                "isH": "false",
                "isT": "false",
                "raw": "false"
            },
            "isQrCode": False,
            "url": "https://img.alicdn.com/imgextra/i1/O1CN01S36nja2A20gvivMsf_!!4109648144-2-fleamarket.png",
            "heightSize": 686,
            "widthSize": 1144,
            "major": False,
            "type": 0,
            "status": "done"
        },
        {
            "extraInfo": {
                "isH": "false",
                "isT": "false",
                "raw": "false"
            },
            "isQrCode": False,
            "url": "https://img.alicdn.com/imgextra/i3/O1CN01DP1xFV2A20gvtlgSu_!!4109648144-2-fleamarket.png",
            "heightSize": 1000,
            "widthSize": 2000,
            "major": False,
            "type": 0,
            "status": "done"
        }
    ],
    "itemTextDTO": {
        "desc": "python 数据爬虫、分析、数据处理，在线接单",  # 商品描述
        "title": "python 数据爬虫、分析、数据处理，在线接单",  # 标题
        "titleDescSeparate": False
    },
    "itemLabelExtList": [
      # 这里是后续要解析的位置，后面肯定是要灵活变动的
        {
            "channelCateName": "其他技能服务",
            "valueId": None,
            "channelCateId": "201454913",
            "valueName": None,
            "tbCatId": "201159705",
            "subPropertyId": None,
            "labelType": "common",
            "subValueId": None,
            "labelId": None,
            "propertyName": "分类",
            "isUserClick": "1",
            "isUserCancel": None,
            "from": "newPublishChoice",
            "propertyId": "-10000",
            "labelFrom": "newPublish",
            "text": "其他技能服务",
            "properties": "-10000##分类:201454913##其他技能服务"
        },
        {
            "channelCateName": None,
            "valueId": "432128703",
            "channelCateId": "201454913",
            "valueName": "元/起",
            "tbCatId": "201159705",
            "subPropertyId": None,
            "labelType": "common",
            "subValueId": None,
            "labelId": None,
            "propertyName": "计价方式",
            "isUserClick": "1",
            "isUserCancel": None,
            "from": "newPublishChoice",
            "propertyId": "150360447",
            "labelFrom": "newPublish",
            "properties": "150360447##计价方式:432128703##元/起",
            "text": "元/起"
        }
    ],
    "itemProperties": [],
    "itemPriceDTO": {
        "origPriceInCent": "15000",  # 原价
        "priceInCent": "12000"  # 价格
    },
    "userRightsProtocols": [
      # 这里是用户权益协议，后面会根据实际情况添加
        {
            "enable": False,
            "serviceCode": "FAST_DELIVERY_48_HOUR"
        },
        {
            "enable": False,
            "serviceCode": "FAST_DELIVERY_24_HOUR"
        },
        {
            "enable": False,
            "serviceCode": "VIRTUAL_NONCONFORMITY_FREE_REFUND_SERVICE"
        },
        {
            "enable": False,
            "serviceCode": "SKILL_PLAY_NO_MIND"
        }
    ],
    "itemPostFeeDTO": {
        "canFreeShipping": False,
        "supportFreight": False,
        "onlyTakeSelf": False,
        "templateId": "0"
    },
    "itemAddrDTO": {
        # 位置信息这里后面会有接口提供
        "area": "翔安区",
        "city": "厦门",
        "divisionId": 350213,
        "gps": "24.565742,118.223729",
        "poiId": "B0FFLEDOTH",
        "poiName": "厦门双十中学翔安附属学校(振南中学)",
        "prov": "福建"
    },
    "defaultPrice": False,
    "itemCatDTO": {
        # 商品类型
        "catId": "50023914",
        "catName": "其他技能服务",
        "channelCatId": "201454913",
        "tbCatId": "201159705"
    },
    "uniqueCode": "1775114888500830",
    "sourceId": "pcMainPublish",
    "bizcode": "pcMainPublish",
    "publishScene": "pcMainPublish"
}
# data = {"freebies":False,"itemTypeStr":"b","quantity":"1","simpleItem":"true","imageInfoDOList":[{"extraInfo":{"isH":"false","isT":"false","raw":"false"},"isQrCode":False,"url":"https://img.alicdn.com/imgextra/i3/O1CN01eo8vPi2A20gwWFpgK_!!4109648144-2-fleamarket.png","heightSize":1000,"widthSize":2000,"major":True,"type":0,"status":"done"}],"itemTextDTO":{"desc":"test","title":"test","titleDescSeparate":False},"itemLabelExtList":[{"channelCateName":"软件安装包/序列号/激活码","valueId":None,"channelCateId":"201449620","valueName":None,"tbCatId":"50003316","subPropertyId":None,"labelType":"common","subValueId":None,"labelId":None,"propertyName":"分类","isUserClick":"1","isUserCancel":None,"from":"newPublishChoice","propertyId":"-10000","labelFrom":"newPublish","text":"软件安装包/序列号/激活码","properties":"-10000##分类:201449620##软件安装包/序列号/激活码"}],"itemPriceDTO":{"origPriceInCent":"322100","priceInCent":"12300"},"userRightsProtocols":[{"enable":False,"serviceCode":"FAST_DELIVERY_48_HOUR"},{"enable":False,"serviceCode":"FAST_DELIVERY_24_HOUR"},{"enable":False,"serviceCode":"VIRTUAL_NONCONFORMITY_FREE_REFUND_SERVICE"},{"enable":False,"serviceCode":"SKILL_PLAY_NO_MIND"}],"itemPostFeeDTO":{"canFreeShipping":True,"supportFreight":True,"onlyTakeSelf":False},"itemAddrDTO":{"area":"翔安区","city":"厦门","divisionId":350213,"gps":"24.565742,118.223729","poiId":"B0FFLEDOTH","poiName":"厦门双十中学翔安附属学校(振南中学)","prov":"福建"},"defaultPrice":False,"itemCatDTO":{"catId":"50025461","catName":"软件安装包/序列号/激活码","channelCatId":"201449620","tbCatId":"50003316"},"uniqueCode":"177520077355891","sourceId":"pcMainPublish","bizcode":"pcMainPublish","publishScene":"pcMainPublish"}
processed_data = str(data).replace("\n", "").replace("False", "false").replace("True", "true").replace('None', 'null').replace(' ','').replace("'",'"')
sign = to_md5('19ae7538f03b06f940195722df1ed877' + "&" + timestamp + "&" + '34839810' + "&" + processed_data)
print(sign)
params["sign"] = sign
print(encode(data))
response = requests.post(url, headers=headers, cookies=cookies, params=params, data=encode(data))

print(response.text)
print(response.status_code)
print(response.headers)
print(response)
