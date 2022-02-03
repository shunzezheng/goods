# '''
# 目前版本 v1.1.0
# 撰寫者:zeze
# '''

import re
from urllib.request import urlopen
import MySQLdb

import requests
from bs4 import BeautifulSoup

list = []


def connetion():
    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="password",
                         db="carrefour")
    cursor = db.cursor()
    cursor.execute('SELECT * FROM carrefour.goods')
    global results
    results = cursor.fetchall()


def rgood():
    text = input("請輸入欲查詢商品的關鍵字: ")
    global content
    content = ""
    url = 'https://online.carrefour.com.tw/zh/search?q=' + str(text)
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    num = int(input("您想要查看前幾名熱銷商品: "))
    v = soup.find_all('a', class_='gtm-product-alink', limit=num)

    for s in v:
        serach = s.get('href')
        link = shorten("https://online.carrefour.com.tw" + serach, '')
        name = s.get('data-name')
        price = s.get('data-baseprice')
        category = s.get('data-category')
        list.append(link)
        print(category, name, price, link)
        # content += f"{good_category}\n{goods_name}\t{goods_price}\n{short_link}\n"
        # print(content)


def match_sql():
    for record in results:
        col0 = record[0]  # 類別
        col1 = record[1]  # 最低價格
        col2 = record[2]  # 最高價格
        col3 = record[3]  # 區域
        col4 = record[4]  # 左1右2
        col5 = record[5]  # 櫃子數
        col6 = record[6]  # 上1下2全3
        col7 = record[7]  # 備註


def parseInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def next_page():
    print("Ok")


def shorten(long_url, alias):
    URL = "http://tinyurl.com/create.php?source=indexpage&url=" + long_url + "&submit=Make+TinyURL%21&alias=" + alias
    response = urlopen(URL)
    soup = BeautifulSoup(response, 'html.parser')
    return soup.find_all('div', {'class': 'indent'})[1].b.string


if __name__ == "__main__":
    while 1 == 1:
        connetion()
        rgood()
        # match_sql()

        if len(list) == 0:
            print("商品不存在!")

        else:
            Next = input("是否要繼續搜尋? (y/n) : ")
            if Next == 'y':
                rgood()
            elif Next == 'n':
                quit()
