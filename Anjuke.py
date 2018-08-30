#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import math
import time

url = "https://wuhan.anjuke.com/community/view/213231?from=Filter_1&hfilter=filterlist"
url1 = "https://wuhan.anjuke.com/community/?from=navigation"
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/66.0.3359.139 Safari/537.36'
}
proxies = {
    'http:': 'http://121.232.146.184',
    'https:': 'https://144.255.48.197'
}
total = []


def get_navigation(first_url):
    """
    得到导航页面
    :param first_url:导航页的网址
    :return: 网页html
    """
    try:
        resp = requests.get(url=first_url, headers=header, timeout=500)
        soup_html = BeautifulSoup(resp.text, 'html.parser')  # 得到网页html
    except requests.ConnectionError as err:
        print("连接超时" + str(err))
    except requests.HTTPError as her:
        print("HTTP请求失败" + str(her))
    except requests.TooManyRedirects as trer:
        print("请求超过了设定的最大重定向次数" + str(trer))
    except TimeoutError:
        print("连接尝试失败")
    return soup_html


def get_all_num(strw):
    """
    从导航页获取页数
    :param url: 导航网址
    :return: 总页数
    """
    community_temp = strw.find_all('span', {"class": "tit"})  # 从网页得到全部小区
    all_community = int(re.findall(r'\d+', str(community_temp))[-1])  # 全部小区数
    print("一共找到" + str(all_community) + "个小区信息")
    all_pages = math.ceil(all_community / 30)
    print("一共找到" + str(all_pages) + "页")
    return all_pages


def get_all_url(num_page):
    """
    得到当前页面的所有url
    :param ever_url:
    :return:
    """
    for i in range(1, 25):  # 从第1页到第x页
        second_url = "https://wuhan.anjuke.com/community/p" + str(i)
        html_text = get_navigation(second_url)
        all_link = html_text.find_all("a", {"hidefocus": "true"})
        print("开始抓取第"+str(i)+"页")
        for link in all_link:
            href = link['href']
            total_info = get_community_info(href)
            total.append(total_info)
    return total


def get_community_info(list_all):
    soup = get_navigation(list_all)
    house_name = soup.title.text.split(',')[0]
    dict_info = {"小区名称": house_name}
    html_info = get_navigation(list_all)
    first_info = html_info.find_all("dl", {"class": "basic-parms-mod"})
    second = BeautifulSoup(str(first_info), "html.parser")
    tree_info = second.find_all("dd")
    sess = [
        '物业类型',
        '物业费',
        '总建面积',
        '总户数',
        '建造年代',
        '停车位',
        '容积率',
        '绿化率',
        '开发商',
        '物业公司']
    for i, j in zip(sess, tree_info):
        di_inf = {
            i: j.string
        }
        dict_info.update(di_inf)
    print(dict_info)
    return dict_info


def save_info(data):
    """
    写入excel
    :param data: dataframe
    :return:
    """
    writer = pd.ExcelWriter(u"安居客.xlsx")
    df = pd.DataFrame(data)
    df.to_excel(writer, sheet_name='AnJuKe', encoding='UTF-8')
    writer.save()
    print("写入成功")


if __name__ == '__main__':
    start_time = time.time()
    html = get_navigation(url1)
    pages = get_all_num(html)
    data = get_all_url(pages)
    save_info(data)
    stop_time = time.time()
    print("程序运行时间为: " + str(stop_time - start_time) + "秒")
