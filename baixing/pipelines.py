# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import os
import MySQLdb


class BaixingPipeline(object):

    def __init__(self):
        self.fw = codecs.open('baixing_data.json', 'a', encoding='utf-8')
        # 存为标准的json格式需要使用 []
        self.fw.write('[')

    def process_item(self, item, spider):
        # # 搜索标题（网页上看到的标题）
        # viewed_title = item['viewed_title']
        # print("查看搜索标题========================：", viewed_title)
        # # 公司名称
        # company_name = item['company_name']
        # print("查看公司名称========================：", company_name)
        # # 服务内容
        # service = item['service']
        # print("查看服务内容========================：", service)
        # # 服务范围
        # service_area = item['service_area']
        # print("查看服务区域========================：", service_area)
        # # 服务报价
        # price = item['price']
        # print("查看服务报价========================：", price)
        # # 公司地址
        # company_address = item['company_address']
        # print("查看公司地址========================：", company_address)
        # # 联系人
        # contact = item['contact']
        # print("查看联系人==========================：", contact)
        # # 联系方式
        # contact_way = item['contact_way']
        # print("查看联系方式========================：", contact_way)
        # # 服务简介
        # service_introduction = item['service_introduction']
        # print("查看服务简介========================：", service_introduction)

        # 将item转换为字典格式
        dict_ = dict(item)
        # 将字典转换为json格式
        data = json.dumps(dict_, ensure_ascii=False) + ",\n"    # 默认使用ascii编码，确保中文能正常显示
        # 将数据写入文件，每一行数据之后加入逗号和换行
        self.fw.write(data)
        return item

    def close_spider(self, spider):
        # 定位到倒数第二个字符，即最后一个逗号
        self.fw.seek(-2, os.SEEK_END)
        # 删除最后一个逗号
        self.fw.truncate()
        # 文件末尾加上另一半 ]
        self.fw.write(']')
        # 关闭文件
        self.fw.close()

    # 以下为将数据存储到MySQL的代码
    # def __init__(self):
    #     # 获取MySQL数据库的链接
    #     self.conn = MySQLdb.connect(
    #         host='40.73.38.109',    # 40.73.38.109
    #         port=3306,
    #         user='root',
    #         password='123456',
    #         db='xiansuo',
    #         charset='utf8'
    #     )
    #     self.cursor = self.conn.cursor()
    #     self.sql = "insert into xiansuo_all(viewed_title, company_name, service, service_area, " \
    #                "price, company_address, contact, contact_way, service_introduction)" \
    #                "VALUES (%s, %s, %s, %s, %s ,%s, %s, %s, %s)"
    #
    # def process_item(self, item, spider):
    #
    #     # 搜索标题（网页上看到的标题）
    #     viewed_title = item['viewed_title']
    #     print("查看搜索标题========================：", viewed_title)
    #     # 公司名称
    #     company_name = item['company_name']
    #     print("查看公司名称========================：", company_name)
    #     # 服务内容
    #     service = item['service']
    #     print("查看服务内容========================：", service)
    #     # 服务范围
    #     service_area = item['service_area']
    #     print("查看服务区域========================：", service_area)
    #     # 服务报价
    #     price = item['price']
    #     print("查看服务报价========================：", price)
    #     # 公司地址
    #     company_address = item['company_address']
    #     print("查看公司地址========================：", company_address)
    #     # 联系人
    #     contact = item['contact']
    #     print("查看联系人==========================：", contact)
    #     # 联系方式
    #     contact_way = item['contact_way']
    #     print("查看联系方式========================：", contact_way)
    #     # 服务简介
    #     service_introduction = item['service_introduction']
    #     print("查看服务简介========================：", service_introduction)
    #     print("开始将数据入库*********************")
    #     self.cursor.execute(self.sql, [viewed_title, company_name, service, service_area,
    #                                    price, company_address, contact, contact_way, service_introduction])
    #     self.conn.commit()
    #     return item
