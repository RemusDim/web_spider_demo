from selenium import webdriver
from bs4 import BeautifulSoup
from urllib import request
import os
import time
import threading
from queue import Queue


"""
使用selenium + BeautifulSoup + 多线程抓取百度图片并保存

记录：
    1.threading.current_thread().name获取当前线程的名字
"""


# 保存图片函数
def save_img(url_q):
    while True:
        # 不写超时时间，貌似图片一直有
        img_url = url_q.get()
        print('%s 下载中：%s' % (threading.current_thread().name, img_url))
        # 获取图片名称
        i_name = img_url.split('/')[-1]
        # 保存，记录错误信息到log文件
        try:
            request.urlretrieve(img_url, os.path.join('./baidu_pic', i_name))
        except Exception as err:
            print(err)
            with open('./baidu_pic/log', 'a+', encoding='utf-8') as f:
                f.write(time.ctime() + '\n' + img_url + '\n' + str(err) + '\n\n')


# 获取页面数据函数
def get_data(driver, url_q):
    # 循环
    while True:
        # 获取页面信息
        html = driver.page_source
        html = BeautifulSoup(html, 'lxml')
        last_div = html.select('div#imgid > div')[-1]
        # 获取图片地址
        img_url_list = last_div.select('li.imgitem')
        # 把图片地址存入队列
        for img in img_url_list:
            url_q.put(img.get('data-objurl'))
        # 滚动到页面底部
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        # 等待图片加载
        time.sleep(5)


def main():
    # 发出请求
    driver = webdriver.Chrome(executable_path=r'/Users/remus/PycharmProjects/tools/chromedriver')
    driver.get('http://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&'
               'cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1529664645415_R&pv=&ic=0&nc=1&z=&se=1&'
               'showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=%E9%A3%8E%E6%99%AF%E5%9B%BE%E7%89%87')

    # 创建保存图片的文件夹
    if not os.path.exists('./baidu_pic'):
        os.makedirs('./baidu_pic')

    # 创建队列存储图片
    url_q = Queue()

    # 创建一个线程去循环抓取数据
    t1 = threading.Thread(target=get_data, args=(driver, url_q), name='抓取数据线程')
    t1.start()

    # 创建几个线程去下载图片
    download_list = []
    for i in range(4):
        t = threading.Thread(target=save_img, args=(url_q,), name='下载图片线程%d' % (i+1))
        t.start()
        download_list.append(t)

    # 设置等待
    t1.join()
    for i in download_list:
        i.join()


if __name__ == '__main__':
    main()
