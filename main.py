#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/04/13
# @Author  : Soin
# @File    : main.py
# @Software: PyCharm
"""
闲鱼商品发布 - 主入口
"""

from Tools.ItemPublish import (
    PublishItem,
    ImageInfo,
    ItemCat,
    ItemAddr,
    ItemLabel,
    publish_item,
    validate_publish_item,
)
from Tools.MaterialPush import upload_image_and_get_info
from Tools.config import logger


COOKIES = {
    'cookie2': '10f5a6b2fa49ad1f5af5cfa3e0e7f6ec',
    'mtop_partitioned_detect': '1',
    '_m_h5_tk': 'd7ceb821446686b2468651a251e0212c_1776078548849',
    '_m_h5_tk_enc': 'eabf8e8f6fdc941bc049923933eec099',
    'xlly_s': '1',
    '_samesite_flag_': 'true',
    't': 'fc14e51b8c39739b7e9425478e444a83',
    '_tb_token_': 'fe5613ee59e6b',
    'sgcookie': 'E100ZZExh%2FyJe%2BXBjBkGqV7DI30Gu1%2B4%2FdiIejqSmiNOzbZmiascTpw%2BGtY2qhhMVco0kWBtIFXcWzI4YrL11We%2BGAgw0COtkLoFUKBJT7FoK14%3D',
    'tracknick': 'tb764198236',
    'csg': '60f9d6dd',
    'unb': '4109648144',
    'havana_lgc2_77': 'eyJoaWQiOjQxMDk2NDgxNDQsInNnIjoiZGJlMzZmODE3ZmM4YjQ4NTUzZjEwM2JjYjI4NzM3NzYiLCJzaXRlIjo3NywidG9rZW4iOiIxVFFuZmQzeWc2YkJldVgzTHA2a2VndyJ9',
    '_hvn_lgc_': '77',
    'havana_lgc_exp': '1778660136131',
    'sdkSilent': '1776154538386',
    'tfstk': 'gMQth3aCUWhtFYUQeVqhomRj4pV3rkfNIO5SoKvic9BdN_kMcNYGHmBGgtxbQFbAps58gEjMIjhNJT3mSRrNGqLDl82urzfabE8bE1PXQ0kw_QHbodOsdFR0mlDipzfN_XTbE84urrFusgpXhtt6ADOMdIg61tiIdpR2GAOj5WCBLpGsChOsdBOJ1cTXlt1Q9IJBhEt1h6Npgp9XrJ2J34vokMgwS20a_33jlwd9vkf6dP1PRCIve11nlqZW6hp51peOIALWDOKO-PHy6M1RLCB4zV86DGsW5Ze8We1PxOOdh8nvdgQNk3bTe0J17KWJ5MeIWETBwsKlxSiJKi1FJHQTqjRFSs_wqUarCKjhwZdAu-zde16OV3_sBg5FraEQ0YvJicNL9mo2fB7-xMEZdhHf6BputEmq0HUv9LVKymo2fBRpEWci0m-Lk',
}



def build_item_with_local_images(image_paths: list[str]) -> PublishItem:
    images = []
    for i, path in enumerate(image_paths):
        img_info = upload_image_and_get_info(path, cookies=COOKIES, major=(i == 0))
        images.append(ImageInfo(
            url=img_info["url"],
            height_size=img_info["heightSize"],
            width_size=img_info["widthSize"],
            major=img_info["major"],
        ))

    return PublishItem(
        title="Python 数据爬虫、分析、数据处理，在线接单",
        desc="Python 数据爬虫、分析、数据处理，在线接单",
        price_in_cent="12000",
        orig_price_in_cent="15000",
        images=images,
        item_cat=ItemCat(
            cat_id="50023914",
            cat_name="其他技能服务",
            channel_cat_id="201454913",
            tb_cat_id="201159705",
        ),
        item_addr=ItemAddr(
            area="翔安区",
            city="厦门",
            division_id=350213,
            gps="24.565742,118.223729",
            poi_id="B0FFLEDOTH",
            poi_name="厦门双十中学翔安附属学校(振南中学)",
            prov="福建",
        ),
        item_labels=[
            ItemLabel(
                property_name="分类",
                text="其他技能服务",
                properties="-10000##分类:201454913##其他技能服务",
                channel_cate_id="201454913",
                tb_cat_id="201159705",
                property_id="-10000",
                channel_cate_name="其他技能服务",
            ),
            ItemLabel(
                property_name="计价方式",
                text="元/起",
                properties="150360447##计价方式:432128703##元/起",
                channel_cate_id="201454913",
                tb_cat_id="201159705",
                property_id="150360447",
                value_id="432128703",
                value_name="元/起",
            ),
        ],
    )


def build_item_with_urls() -> PublishItem:
    return PublishItem(
        title="Python 数据爬虫、分析、数据处理，在线接单",
        desc="Python 数据爬虫、分析、数据处理，在线接单",
        price_in_cent="12000",
        orig_price_in_cent="15000",
        images=[
            ImageInfo(
                url="https://img.alicdn.com/imgextra/i1/O1CN01uAZQzl2A20gvvsJ7z_!!4109648144-2-fleamarket.png",
                height_size=470, width_size=849, major=True,
            ),
            ImageInfo(
                url="https://img.alicdn.com/imgextra/i1/O1CN01S36nja2A20gvivMsf_!!4109648144-2-fleamarket.png",
                height_size=686, width_size=1144,
            ),
            ImageInfo(
                url="https://img.alicdn.com/imgextra/i3/O1CN01DP1xFV2A20gvtlgSu_!!4109648144-2-fleamarket.png",
                height_size=1000, width_size=2000,
            ),
        ],
        item_cat=ItemCat(
            cat_id="50023914",
            cat_name="其他技能服务",
            channel_cat_id="201454913",
            tb_cat_id="201159705",
        ),
        item_addr=ItemAddr(
            area="翔安区",
            city="厦门",
            division_id=350213,
            gps="24.565742,118.223729",
            poi_id="B0FFLEDOTH",
            poi_name="厦门双十中学翔安附属学校(振南中学)",
            prov="福建",
        ),
        item_labels=[
            ItemLabel(
                property_name="分类",
                text="其他技能服务",
                properties="-10000##分类:201454913##其他技能服务",
                channel_cate_id="201454913",
                tb_cat_id="201159705",
                property_id="-10000",
                channel_cate_name="其他技能服务",
            ),
            ItemLabel(
                property_name="计价方式",
                text="元/起",
                properties="150360447##计价方式:432128703##元/起",
                channel_cate_id="201454913",
                tb_cat_id="201159705",
                property_id="150360447",
                value_id="432128703",
                value_name="元/起",
            ),
        ],
    )


def main():
    item = build_item_with_urls()

    errors = validate_publish_item(item)
    if errors:
        for e in errors:
            logger.error(f"校验失败: {e}")
        return

    try:
        result = publish_item(item, COOKIES)
        logger.info(f"发布成功: {result}")
    except ValueError as e:
        logger.error(f"数据校验错误: {e}")
    except RuntimeError as e:
        logger.error(f"发布失败: {e}")
    except Exception as e:
        logger.error(f"未知异常: {e}")


if __name__ == "__main__":
    main()
