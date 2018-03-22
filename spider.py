from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import re
import time
import pandas as pd
import json


def login(driver):
    '''
    实现登录功能
    '''
    # 显式等待，确保页面加载完成
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[@title="点击登录"]'))
    )

    # 输入账号
    driver.find_element_by_xpath(
        '//input[@name="account"]').send_keys(ACCOUNT)

    # 输入密码
    driver.find_element_by_xpath(
        '//input[@name="password"]').send_keys(PASSWORD)

    # 点击登陆
    driver.find_element_by_xpath('//a[@title="点击登录"]').click()

    # 显示等待，确保二维码扫描完毕
    WebDriverWait(driver, 999).until(
        EC.text_to_be_present_in_element((By.XPATH, '//h3'), '帐号整体情况')
    )

    # 获取token
    return re.search(r'token=(\d+)', driver.current_url).group(1)


def go_to(driver, i):
    '''
    跳转页面
    '''
    driver.get(REQUSET_TMPL.format(i*7))
    time.sleep(1)


def parse_json(driver):
    '''
    解析reponse
    '''
    # 提取json部分
    data = re.search(r'<pre.*?>(.*)</pre>', driver.page_source).group(1)

    # 校正格式
    data = re.sub('true', 'True', data)
    data = re.sub('false', 'False', data)
    return eval(data)


def parse_data(data, ret):
    '''
    提取数据
    '''
    global PUBLISH_COUNT
    for items in data['sent_list']:
        date = time.localtime(items['sent_info']['time'])

        if items['appmsg_info']:
            PUBLISH_COUNT += 1
        else:
            continue

        for item in items['appmsg_info']:
            ret.append({
                'time': time.strftime("%Y-%m-%d %H:%M:%S", date),
                'like_num': item['like_num'],
                'read_num': item['read_num'],
                'comment_num': item.get('comment_num',0),
                'title': item['title']
            })
            print(ret[-1])


def save_ret(ret):
    '''
    保存结果
    '''
    data = pd.read_json(json.dumps(ret))
    data.to_csv('d:ret.csv', encoding='utf-8-sig')


REQUSET_TMPL = None  # url 模板
PUBLISH_COUNT = 0  # 发布次数
END_PAGE = 63  # 总计页数
ACCOUNT = '你的张号'
PASSWORD = '你的密码'


def main():
    global REQUSET_TMPL

    driver = webdriver.Chrome()
    driver.get('https://mp.weixin.qq.com/')

    token = login(driver)
    REQUSET_TMPL = token.join(('https://mp.weixin.qq.com/cgi-bin/newmasssendpage?count=7&begin={}&token=',
                               '&lang=zh_CN&token=', '&lang=zh_CN&f=json&ajax=1'))
    ret = []
    for i in range(END_PAGE+1):
        go_to(driver, i)
        data = parse_json(driver)
        parse_data(data, ret)

    save_ret(ret)
    print('共推送图文', PUBLISH_COUNT)  # 打印发布次数


if __name__ == '__main__':
    main()
