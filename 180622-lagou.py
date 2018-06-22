from selenium import webdriver
from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

"""
使用selenium + xpath抓取拉勾网发布的Python职位信息
"""


# 访问页面
driver = webdriver.Chrome(executable_path=r'/Users/remus/PycharmProjects/tools/chromedriver')
driver.get('https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=')

# 自动等待，获取总页数
wait = WebDriverWait(driver, 20)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.pager_not_current')))
page_num = driver.find_element_by_css_selector('div.pager_container span:nth-last-of-type(2)').text


while True:
    # 获取网页源码
    html = driver.page_source
    # 使用xpath解析
    html = etree.HTML(html)
    # 获取当前页码
    page_current = html.xpath('//span[@class="pager_is_current"]/text()')[0].split()[0]
    print('------第%s页------' % page_current)

    pos_list = html.xpath('//ul[@class="item_con_list"]/li')
    for pos in pos_list:
        # 职位标题
        title = pos.xpath('.//h3/text()')[0]
        # 工作地点
        loc = pos.xpath('.//span[@class="add"]//em/text()')[0]
        # 钱数
        money = pos.xpath('.//span[@class="money"]/text()')[0]
        if 'k' in money or 'K' in money:
            money = money.replace('k', '*1000').replace('K', '*1000')
        if '以上' in money:
            money = money.replace('以上', '') + '-None'
        money_list = money.split('-')
        for i in range(2):
            money_list[i] = eval(money_list[i])
        # 公司名称
        company = pos.xpath('.//div[@class="company_name"]/a/text()')[0]
        # 描述
        description = pos.xpath('.//div[@class="list_item_bot"]/div[@class="li_b_l"]/span/text()')
        description = ', '.join(description)
        # 组织数据
        f_data = {
            'title': title,
            'loc': loc,
            'min_money': money_list[0],
            'max_money': money_list[1],
            'company': company,
            'description': description
        }
        print(f_data)

    # 翻页
    if 'pager_next_disabled' not in driver.page_source:
        driver.find_element_by_css_selector('.pager_next').click()
        print('------翻页中------')
        time.sleep(10)
    else:
        break
