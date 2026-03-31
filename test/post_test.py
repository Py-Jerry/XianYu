# -*- coding: utf-8 -*-
"""
@File    :   post_test.py
@Time    :   2026/03/26 10:39
@Author  :   Soin
@Desc    :   用来做测试的文件
"""

import requests


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
cookies = {
    "cookie2": "1261cb7a55d0702fa6eb7f6799b8bad8",
    "xlly_s": "1",
    "_samesite_flag_": "true",
    "t": "a629bf23cebb50370d1ab0099dc06b0c",
    "_tb_token_": "fb50333e17a38",
    "sdkSilent": "1774515668202",
    "mtop_partitioned_detect": "1",
    "_m_h5_tk": "05e42922c61601673049ce5b3a1a30c5_1774498822607",
    "_m_h5_tk_enc": "e81fedf488b9db608259e4718eed7572",
    "sgcookie": "E100rpYhz4bOCwrZQzlT2MqxRMmjyAgx1%2BhpVrY1vf7h5sJL1lLVQddvIevwu8yG6R9oiWI1N8J6CNOleZBeSMC9VkqVTLVTtDogpy5i%2F9YDBak%3D",
    "tracknick": "xy348830521296",
    "csg": "d32d12e7",
    "unb": "2218194775430",
    "tfstk": "g4QsnQ2prtQE8qNTHAPEONE9hBLj5Wzz5jOAZs3ZMFLtHxCJLOJw7S4XHOvF7d5wWs3Ah9CZ7Z7fxq1liNPMu5YGsEYYU8zPc1fMoixLyM769pdA9fpv6k8p065uR8zzz1E9sE5LUGy80ZOXMEd9DIULOIdXHEn9DW9pGQmxBtLYOWOvNfpvHKdpvIdXkKBvkWtpipd9khBA9WODpKh_DbObfdf_MYxeLUkQS6vIkqQBORAd1cuy1ZR6IL1OsR2gmCt6e1pQCOk6yn66fwzsECsdN9A1nz0MWnsO2FQbFPTdZMW9OteScpI5SZtP58ikBNvcFFIQpVTvJQ1X4MPxVpSAtwtC5ulDtN5AS388rApVY__XGZ20RT1OCgKRWAsyi4JWQSijO30XOLPQOmmcH4mIH78xjRt9tCtUOWMOmY0xuDVQO0-XXBAEFWNIBif.."
}
url = "https://h5api.m.goofish.com/h5/mtop.idle.pc.idleitem.publish/1.0/"
params = {
    "jsv": "2.7.2",
    "appKey": "34839810",
    "t": "1774492269358",
    "sign": "3e4d1f0ffc5162533b3f8422c3ce5509",
    "v": "1.0",
    "type": "originaljson",
    "accountSite": "xianyu",
    "dataType": "json",
    "timeout": "20000",
    "api": "mtop.idle.pc.idleitem.publish",
    "sessionOption": "AutoLoginOnly",
    "spm_cnt": "a21ybx.publish.0.0",
    "spm_pre": "a21ybx.personal.sidebar.1.32336ac2lwic8T",
    "log_id": "32336ac2lwic8T"
}
data = {
    "freebies":False,
    "itemTypeStr":"b",
    "quantity":"1",
    "simpleItem":"true",
    "imageInfoDOList":
    [
        # 这里是上传后的图片列表
        {

            "extraInfo":{"isH":"false",
        "isT":"false",
        "raw":"false"},
        "isQrCode":False,
        "url":"https://img.alicdn.com/imgextra/i4/O1CN01sKhtj81pyzldG2aOE_!!2218194775430-0-fleamarket.jpg",    # 上传后的图片，返回的url
        "heightSize":470,   # 图片高度
        "widthSize":556,  # 图片宽度
        "major":True,
        "type":0,
        "status":"done"}],
        "itemTextDTO":{"desc":"爬虫 服务，专业爬虫服务",    # 文案
        "title":"爬虫 服务，专业爬虫服务",  # 标题
        "titleDescSeparate":False},
        "itemLabelExtList":[
            {"channelCateName":"其他技能服务",    # 服务类型
            "valueId":None,
            "channelCateId":"201454913",    # 类型id
            "valueName":None,
            "tbCatId":"201159705",
            "subPropertyId":None,
            "labelType":"common",
            "subValueId":None,
            "labelId":None,
            "propertyName":"分类",
            "isUserClick":"0",
            "isUserCancel":None,
            "from":"newPublishChoice",
            "propertyId":"-10000",
            "labelFrom":"newPublish",
            "text":"其他技能服务",
            "properties":"-10000##分类:201454913##其他技能服务"}],
            "itemPriceDTO":{"priceInCent":"30000"},
            "userRightsProtocols":[{"enable":False,
            "serviceCode":"AI_SALE"},
            {"enable":False,"serviceCode":"SKILL_PLAY_NO_MIND"}],
            "itemPostFeeDTO":{"canFreeShipping":True,
            "supportFreight":True,"onlyTakeSelf":False},
            # 这里是地址信息
            "itemAddrDTO":
                {
                "area":"渝北区",   # 区县
                "city":"重庆",    # 城市
                "divisionId":500112,    # 邮编
                "gps":"29.668463,106.565359",   # 经纬度
                "poiId":"B0FFH5BVDE",   # 地点id
                "poiName":"西部建材城办公楼",   # 地点名称
                "prov":"重庆" # 省份
                 },
            "defaultPrice":False,   # 是否默认价格
            "itemCatDTO":
                {
                "catId":"50023914",
                "catName":"其他技能服务",
                "channelCatId":"201454913",
                "tbCatId":"201159705"
                },
                "uniqueCode":"1774493112471956",
                "sourceId":"pcMainPublish",
                "bizcode":"pcMainPublish",
                "publishScene":"pcMainPublish"}


response = requests.post(url, headers=headers, cookies=cookies, params=params, data=data)

print(response.text)
print(response.status_code)
print(response.headers)
print(response)