# '''
# 目前版本 v1
# 撰寫者:zeze
# '''
from urllib.request import urlopen

import MySQLdb
import find_mysql
import requests
from bs4 import BeautifulSoup

list = []


def rgood():
    content = ""
    text = input("請輸入欲查詢商品的關鍵字: ")
    url = 'https://online.carrefour.com.tw/zh/search?q=' + str(text)
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    v = soup.find_all('a', class_='gtm-product-alink')

    for s in v:
        serach = s.get('href')
        get_page = "https://online.carrefour.com.tw" + serach
        short_link = shorten(get_page, '')
        goods_name = s.get('data-name')
        goods_price = s.get('data-baseprice')
        price = '價格:　' + str(goods_price) + '元'
        list.append(short_link)
        content += f"{goods_name}\t{price}\n{short_link}\n\n"
        print(content.strip())


def next_page():
    print("Ok")


def shorten(long_url, alias):
    URL = "http://tinyurl.com/create.php?source=indexpage&url=" + long_url + "&submit=Make+TinyURL%21&alias=" + alias
    response = urlopen(URL)
    soup = BeautifulSoup(response, 'html.parser')
    return soup.find_all('div', {'class': 'indent'})[1].b.string


if __name__ == "__main__":
    while 1 == 1:
        rgood()

        if len(list) == 0:
            print("商品不存在!")

        else:
            Next = input("是否要查看熱銷商品? (y/n) : ")
            if Next == 'y':
                next_page()
            elif Next == 'n':
                quit()
