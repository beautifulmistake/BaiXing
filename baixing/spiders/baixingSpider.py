from scrapy_redis.spiders import RedisSpider
import scrapy
import time
from baixing.items import BaixingItem

"""
北京百姓网爬虫：
抓取百姓网上跟工商，商标，专利相关的公司以及服务内容，联系人相关线索
"""
# 定义全局的变量
default_value = "暂无相应信息"


class BaiXingSpider(RedisSpider):
    # 爬虫名称
    name = "baiXing"
    # start_urls = ['http://beijing.baixing.com/daibanzhuce/']
    redis_key = 'BaiXingSpider:start_urls'

    def __init__(self):
        # 初始url
        # self.base_url = 'http://hubei.baixing.com/daibanzhuce/?page={}'   # 单独爬取某个城市时使用
        # 请求切换城市的页面
        self.base_url = 'http://www.baixing.com/?changeLocation=yes&return=%2Fdaibanzhuce%2F'
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                          '(KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        }

    def start_requests(self):
        """
        构造初始请求
        :return:
        """
        # for num in range(1, 101):
        #     # 总共可以抓取一百页，采用循环遍历的方式
        #     yield scrapy.Request(url=self.base_url.format(num), callback=self.list_page, headers=self.headers)
        yield scrapy.Request(url=self.base_url, callback=self.get_all_city, headers=self.headers,
                             meta={"current_url": self.base_url})

    def get_all_city(self, response):
        """
        获取所有城市工商代理的链接
        :param response:
        :return:
        """
        if response.status == 200:
            # 匹配出所有城市的链接
            all_city_url_list = response.xpath('//ul/li[2]/ul/li/a/@href|//ul/li/div/ul/li/a/@href').extract()
            # 遍历所有城市工商注册的页面链接
            for signal_city_url in all_city_url_list:
                print(signal_city_url)
                yield scrapy.Request(url="http:" + signal_city_url, callback=self.list_page, headers=self.headers
                                     , meta={"current_url": "http:" + signal_city_url})

    def list_page(self, response):
        """
        根据初始url获取响应页面,获取详情页的链接
        :param response:
        :return:
        """
        if response.status == 200:
            # print("查看响应的页面：", response.text)
            # 获取详情页的链接,为列表
            detail_page_list = response.xpath('//div[@class="main"]/ul/li/div/div'
                                              '[@class="media-body-title"]/a[1]/@href').extract()
            print(detail_page_list)
            # 获取页码列表最后一个li标签
            last_li = response.xpath('//ul[@class="list-pagination"]/li[last()]/a/text()').extract_first()
            # 以下是测试代码
            # yield scrapy.Request(url=detail_page_list[15], headers=self.headers, callback=self.get_detail_page)
            # 将详情页的请求加入到请求队列
            for detail_page_url in detail_page_list:
                yield scrapy.Request(url=detail_page_url, headers=self.headers, callback=self.get_detail_page,
                                     meta={"current_url": detail_page_url})
            # 判端是否有下一页
            if last_li == "下一页":
                # 获取当前的URL
                current_url = response.url
                print("查看当前的URL：===============", current_url)
                # 有下一页，获取下一页的链接
                next_page_url = response.xpath('//ul[@class="list-pagination"]/li[last()]/a/@href').extract_first()
                # 拼接获取完整的下一页链接
                whole_url = current_url.split("/daibanzhuce")[0] + next_page_url
                print("查看获取的URL：===========================", whole_url)
                # 将下一页的请求加入请求队列,调用自身进行解析响应
                yield scrapy.Request(url=whole_url, callback=self.list_page, headers=self.headers,
                                     meta={"current_url": whole_url})

    def get_detail_page(self, response):
        """
        解析详情页信息,
        找出最全的网页信息，主要是判断服务内容部分的有哪几项：
        服务内容--服务范围--报价--所在地--联系人    （完整的网页结构，有些可能缺失报价或者所在地，后者两者都缺失）
        :param response:
        :return:
        """
        if response.status == 200:
            time.sleep(3)
            # 调试代码
            # print(response.text)
            # 搜索标题
            viewed_title = response.xpath('//div[@class="viewad-title"]/h1/text()').extract_first()
            # 公司名称(注意与上面的区别，有时候网页上没有公司的名称）
            company_name = response.xpath('//div[@class="viewad-meta2-item"]/div/span/text()').extract_first()
            # 获取服务内容的总div标签数目
            total_div = response.xpath('//div[@class="viewad-meta2"]/div'
                                       '[@class="viewad-meta2-item fuwu-content"]').extract()   # 判断数目
            # 服务内容,有时候会有多个服务内容，此时获取的为一个服务内容的列表，需要对数据做拼接
            service = response.xpath('//div[@class="viewad-meta2-item fuwu-content"][1]/div/a/text()').extract()
            # 服务范围，有时候会有多个服务地区，此时获取的为一个服务地区的列表，需要对数据做拼接
            service_area = response.xpath('//div[@class="viewad-meta2-item fuwu-content"]'
                                          '[2]/div/a/text()').extract()
            # 获取第三个标签的标题，用于判断
            third_div_title = response.xpath('//div[@class="viewad-meta2-item fuwu-content"][3]'
                                             '/label/text()').extract_first()   # 报价：
            # 服务报价
            price = response.xpath('//div[@class="viewad-meta2-item fuwu-content"][3]/div/span/text()').extract_first()
            # 公司地址
            company_address = response.xpath('//div[@class="viewad-meta2-item fuwu-content"]'
                                             '[4]/div/span/text()').extract_first()
            # 联系人,这个肯定是服务项的最后一个
            contact = response.xpath('//div[@class="viewad-meta2-item fuwu-content"]'
                                     '[last()]/div/span/text()').extract_first()
            # 联系方式,需要将最后四位*号替换成真实号码
            contact_way_first = response.xpath('//section[@class="viewad-contact"]/ul/li[1]/a[1]/text()').extract_first()
            contact_way_last = response.xpath('//section[@class="viewad-contact"]/ul/li[1]/'
                                              'a[2]/@data-contact').extract_first()
            # 服务简介,需要将空白以及换行符替换,使用re去匹配文字
            service_introduction = response.xpath('//div[@class="viewad-detail"]/section/'
                                                  'div[@class="viewad-text-hide"]/text()').extract_first()
            # 创建item对象
            items = BaixingItem()
            # 判断数量
            if len(total_div) == 3:
                items['price'] = default_value
                items['company_address'] = default_value
            elif len(total_div) == 5:
                items['price'] = price if price else default_value
                items['company_address'] = company_address if company_address else default_value
            elif len(total_div) == 4:
                if third_div_title == "报价：":
                    items['price'] = price if price else default_value
                    items['company_address'] = default_value
                else:
                    items['price'] = default_value
                    items['company_address'] = price if price else default_value
            items['viewed_title'] = viewed_title if viewed_title else default_value  # 搜索标题
            items['company_name'] = company_name if company_name else default_value  # 公司名称
            items['service'] = "\t".join(service) if service else default_value     # 服务内容
            items['service_area'] = "\t".join(service_area) if service_area else default_value  # 服务范围
            # items['price'] = price if price else default_value  # 服务报价
            # items['company_address'] = company_address if company_address else default_value    # 公司地址
            items['contact'] = contact if contact else default_value    # 联系人
            items['contact_way'] = contact_way_first[:-4] + contact_way_last[:] \
                if contact_way_first and contact_way_last else default_value    # 联系方式
            items['service_introduction'] = " ".join(service_introduction.split()) if \
                service_introduction else default_value     # 服务简介
            yield items
