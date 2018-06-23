import requests
from lxml import etree
from urllib import request
import os


"""
成人网站视频抓取
requests + xpath

网站视频使用videojs加载，传输.ts格式文件，带key.key加密
最终方法：抓取视频接口，使用ffmpeg解析下载
"""


base_url = 'http://www.yemalu.net/videos?page=%d'
v_base_url = 'http://www.yemalu.net/video'

# 拿到总页数
response = requests.get('http://www.yemalu.net/videos')
response.encoding = response.apparent_encoding
html = response.text
html = etree.HTML(html)
page_num = html.xpath('//ul[@class="pagination"]/li')[-2]
page_num = page_num.xpath('./a/text()')[0]

# 循环请求
for i in range(int(page_num) + 1):
    # 拿到每一页的url
    full_url = base_url % (i + 1)
    response = requests.get(full_url)
    response.encoding = response.apparent_encoding
    html = response.text
    html = etree.HTML(html)
    v_url_list = html.xpath('//div[@class="well well-sm"]/a/@href')
    # 拿到每一页中所有视频的详情页url
    for url in v_url_list:
        detail_url = v_base_url + url
        f_name = detail_url.split('/')[-1]
        # 再去发请求
        response = requests.get(detail_url)
        response.encoding = response.apparent_encoding
        html = response.text
        # xpath处理
        html = etree.HTML(html)
        v_src = html.xpath('//source/@src')[0]
        # 获取第一次response
        response = requests.get(v_src)
        response.encoding = response.apparent_encoding
        print('第一次响应：%s' % response.status_code)
        res = response.content.decode('utf-8')
        res = res.split('\n')[-1]
        # 获取url
        f_res = request.urljoin(v_src, res)
        # 下载
        os.system('ffmpeg -i "' + f_res + '" -c copy ' + f_name + '.ts')
