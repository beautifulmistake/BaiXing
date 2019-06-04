import json

import requests
def get_proxies():
    """
    连接API获取付费的代理IP
    :return: 代理IP
    """
    # API 请求,修改account可修改请求的数量
    # url = 'http://api.xdaili.cn/xdaili-api//privateProxy/applyStaticProxy?spiderId=5b817f58bea74822a6c369e567e278bc&returnType=2&count=1'
    url = 'http://39.107.59.59/get'
    # 发送请求获取响应
    results = json.loads(requests.get(url).text)['RESULT']
    print("查看获取的响应：", results)
    return results
    # 获取的json,从中解析出IP，port
    # for result in results:
    #     ip = result['ip']
    #     port = result['port']
    #
    # return ip + ':' + port


if __name__ == "__main__":
    get_proxies()
