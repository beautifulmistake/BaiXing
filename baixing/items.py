# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaixingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 搜索标题（网页上看到的标题）
    viewed_title = scrapy.Field()
    # 公司名称
    company_name = scrapy.Field()
    # 服务内容
    service = scrapy.Field()
    # 服务范围
    service_area = scrapy.Field()
    # 服务报价
    price = scrapy.Field()
    # 公司地址
    company_address = scrapy.Field()
    # 联系人
    contact = scrapy.Field()
    # 联系方式
    contact_way = scrapy.Field()
    # 服务简介
    service_introduction = scrapy.Field()
