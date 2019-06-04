# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import requests
import time

from fake_useragent import UserAgent
from scrapy import signals
from baixing.util.db import REDISCLIENT


class BaixingSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class BaixingDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProxyMiddleware(object):
    def __init__(self):
        # self.logger = logging.getLogger(__name__)
        self.db = REDISCLIENT()

    # def get_random_proxy(self):
    #     """
    #     连接数据库获取随机的proxy
    #     :return: proxy
    #     """
    #     try:
    #         # 获取随机的代理
    #         proxy = self.db.random()
    #         # 顺便检查一下代理数量是否达到阈值
    #         self.db.check()
    #         # 将获取的代理返回
    #         return proxy
    #     except requests.ConnectionError:
    #         # 出现连接错误
    #         return False

    def process_request(self, request, spider):
        """
        每个请求都会经过这里，在此添加代理IP
        :param request:
        :param spider:
        :return:
        """
        proxy = self.db.random()
        self.db.check()
        if proxy:
            try:
                ip = proxy.split(":")[0]
                port = proxy.split(":")[1]
                if self.db.check_proxy(ip, port):
                    uri = 'http://{proxy}'.format(proxy=proxy)
                    print(uri)
                    # 将使用代理信息打印在控制台中
                    spider.logger.info("使用代理[%s]访问[%s]" % (proxy, request.url))
                    request.meta['proxy'] = uri
                else:
                    self.db.delet_proxy(proxy)
            except:
                spider.logger.info("代理出错**********")

    def process_response(self, request, response, spider):
        """
        如果响应中出现重定向则需要重新更换proxy
        :param request:
        :param response:
        :param spider:
        :return:
        """
        if response.status == 302:
            spider.logger.info("被重定向**********")
            # 获取被重定向的url
            current_url = request.meta['current_url']
            print("查看被重定向的原始url:", current_url)
            # 重定向到登陆界面，代理失效
            spider.logger.info("代理失效")
            # 先删除这个失效的代理IP
            proxy = request.meta['proxy'][7:]
            print("查看获取已经失效的代理：", proxy)
            self.db.delet_proxy(proxy)
            # 设置代理IP=None
            request.meta['proxy'] = None
            return request.replace(url=current_url, dont_filter=True)
        # 如果出现重定向，获取重定向的地址
        elif 'redirect' in response.url:
            spider.logger.info("被重定向**********")
            # 获取被重定向的url
            current_url = request.meta['current_url']
            print("查看被重定向的原始url:", current_url)
            # 重定向到登陆界面，代理失效
            spider.logger.info("代理失效")
            # 先删除这个失效的代理IP
            proxy = request.meta['proxy'][7:]
            print("查看获取已经失效的代理：", proxy)
            self.db.delet_proxy(proxy)
            # 设置代理IP=None
            request.meta['proxy'] = None
            return request.replace(url=current_url, dont_filter=True)
        return response


# 编写随即切换user_agent的中间件
class RandomUserAgentMiddleware(object):
    # 初始化方法
    def __init__(self,crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()
        # 从settings.py中读取RANDOM_UA_TYPE配置，如果没有则采用默认的random，达到可配置的目的
        # 默认是random随机选择。但是可以在配置指定ie或者Firefox等浏览器的不同版本
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE","random")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            """
            闭包函数
            读取上面的ua_type设置，让process_request直接调用本get_ua
            :return:
            """
            print("已经获得用户代理，开始爬取")
            return getattr(self.ua, self.ua_type)
        request.headers.setdefault('User-Agent', get_ua())