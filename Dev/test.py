import time

# import requests
# from requests.exceptions import MissingSchema, InvalidURL
from requests_html import HTMLSession


def find():
    global r
    session = HTMLSession()
    url = input('請輸入網址: ')
    start = time.time()
    try:
        r = session.get(url)
    except:
        print("error!")
        find()

    r.html.render(timeout=20)

    # ele = r.html.find('#cq_recomm_slot-89984c043f9f6c5dfe5899d4eb > div > div > div > div:nth-child(3) > div.photo > a')

    e3 = r.html.find("#cq_recomm_slot-89984c043f9f6c5dfe5899d4eb > div > div > div > div:nth-child(9) > div.photo > a")
    e2 = r.html.find("#cq_recomm_slot-89984c043f9f6c5dfe5899d4eb > div > div > div > div:nth-child(6) > div.photo > a")
    e1 = r.html.find("#cq_recomm_slot-89984c043f9f6c5dfe5899d4eb > div > div > div > div:nth-child(3) > div.photo > a")
    for r1, r2, r3 in zip(e1, e2, e3):
        i = '第 ' + r1.attrs['data-position'] + ' 名 ' + r1.attrs['data-name'] + ' ' + r1.attrs['data-price'] + ' 元 '
        j = '第 ' + r2.attrs['data-position'] + ' 名 ' + r2.attrs['data-name'] + ' ' + r2.attrs['data-price'] + ' 元 '
        k = '第 ' + r3.attrs['data-position'] + ' 名 ' + r3.attrs['data-name'] + ' ' + r3.attrs['data-price'] + ' 元 '
        print(i + '\n' + j + '\n' + k)

    # print(e1.attrs['data-name'], '人氣熱銷', '第 ' + e1.attrs['data-position'] + ' 名')
    # print(e2.attrs['data-name'], '人氣熱銷', '第 ' + e2.attrs['data-position'] + ' 名')
    # print(e3.attrs['data-name'], '人氣熱銷', '第 ' + e3.attrs['data-position'] + ' 名')
    end = time.time()
    print('搜尋時間', end - start, '秒')


if __name__ == "__main__":
    try:
        while 1 == 1:
            find()
    except:
        find()
