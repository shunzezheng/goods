#                                 _                                      _               _
#                                | |                                    | |             | |
#      ___  _ __  __ _ __      __| |  ___  _ __   _ __   _ __  ___    __| | _   _   ___ | |_
#     / __|| '__|/ _` |\ \ /\ / /| | / _ \| '__| | '_ \ | '__|/ _ \  / _` || | | | / __|| __|
#    | (__ | |  | (_| | \ V  V / | ||  __/| |    | |_) || |  | (_) || (_| || |_| || (__ | |_
#     \___||_|   \__,_|  \_/\_/  |_| \___||_|    | .__/ |_|   \___/  \__,_| \__,_| \___| \__|
#                                                | |
#                                                |_|

# '''
# 目前版本 v1.5.0
# 撰寫成員:余若榛、鄭舜澤
# '''
# 若無安裝套件則選是否要自動安裝
try:
    import os
    import re
    import MySQLdb
    import asyncio
    import sys
    import threading
    import time
    import requests_html as req
    import speech_recognition as sr
    from multiprocessing import Process
    from fake_useragent import UserAgent
    from urllib.request import urlopen
    from requests.exceptions import MissingSchema, InvalidURL
    from requests_html import HTMLSession
    import requests
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    Promote = input("錯誤: 尚未安所需的套件! 是否自動安裝所需套件(Y/n)? : ")
    if Promote=="Y":
        command = 'pip3 install -r requirements.txt'
        os.system(command)
        basename = os.path.basename(__file__)
        os.system('python ' + basename)  # 執行此命令
        quit()
    elif Promote=="n":
        exit()

# 建立db連線到本地端資訊
db = MySQLdb.connect(host="localhost",
    user="root",
    passwd="password",
    db="carrefour")


# db連線
def connection():
    # noinspection PyBroadException
    try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM carrefour.goods')
        global results
        results = cursor.fetchall()
    except:
        print("錯誤:無法連上db!")


def disconnection():
    db.close()


def ASR():
    # obtain audio from the microphone
    r = sr.Recognizer()
    # 語音讀取
    with sr.Microphone() as source:
        # create the ambient noise energy level

        r.adjust_for_ambient_noise(source, duration=0)
        audio = r.listen(source)  # 檢測到靜音停止

    # recognize speech using Google Speech Recognition
    dancing = '''
            ⊂_ヽ
            　 ＼＼ 
            　   ＼(°ʖ°)
            　　　 >　⌒ヽ
            　　　 / 　 へ ＼
            　　  /　　/　＼ \❤️
            　　  ﾚ　ノ　　 ヽ_つ
            　　  /　/
            　   /　/|
            　   (　(ヽ
            　   |　|、＼
            　   | 丿 ＼ ⌒)
            　   | |　　) /
                ノ )　　Lﾉ
                (_／
            '''
    try:
        words = r.recognize_google(audio, language="zh-TW")
        print(words, dancing)
        text = input("請按下Enter鍵後進行搜尋!")
        if text=="":
            return words
        else:
            return ASR()
    except sr.UnknownValueError:
        cat = '''
        ＿＿
　　　　　／＞　　フ ♡
　　　　　| 　_　_ l ♡
　 　　　／` ミ ωノ ♡
　　 　 /　　　 　 |
　　　 /　 ヽ　　 ﾉ
　 　 │　　|　|　|
　／￣|　　 |　|　|
　| (￣ヽ＿_ヽ_)__)
　＼二つ
        '''
        print('無法辨識喔，請重新再說一次!', cat)
        return ASR()
    except sr.RequestError as e:
        print("No response from Google Speech Recognition service: {0}".format(e))


def loading(t):
    for i in range(100 + 1):
        time.sleep(t / 100)
        sys.stdout.write(("\r查詢中... [ %d" % i + "% ] "))
        sys.stdout.flush()


t = threading.Thread(target=loading, args=(7,))


# 爬蟲獲取商品名稱、價格、熱銷、縮網址
def goods_info():
    global content, text, list, pop_result, t1
    content = ""
    list = []

    print("請輸入欲查詢商品的關鍵字(語音輸入):", end='')
    url = 'https://online.carrefour.com.tw/zh/search?q=' + str(ASR() if not None else print("error!"))
    # print("搜尋中••••請稍後!")
    # text = ASR()
    # str(stext=ASR()) if None else str(wtext)
    # headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    #                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"}
    # response = requests.get(url, headers=headers)
    user_agent = UserAgent()
    asession = req.AsyncHTMLSession()

    t = threading.Thread(target=loading, args=(7,))
    t.start()
    t1 = time.time()
    response = requests.get(url, headers={'user-agent': user_agent.random})
    soup = BeautifulSoup(response.text, "lxml")  # Parser選用lxml，較為快速
    # 撈資料
    extract = soup.find_all('a', class_='gtm-product-alink', limit=3)
    ele = [s.get('href') for s in extract]
    try:
        pop_result = asession.run(pop_goods, urls=ele)
    except:
        pass

    for (s, items) in zip(extract, [0, 1, 2]):
        search = s.get('href')
        link = shorten("https://online.carrefour.com.tw" + search, '')
        name = s.get('data-name')
        price = s.get('data-baseprice') + '元'
        category = s.get('data-category')
        list.append(link)
        pop = '與此商品之相關熱銷商品:\n' + str(pop_result[items])
        content += f"\n{category}\n{name}\t{price}\n{link}\n{pop}\n"
    last = time.time() - t1
    print('\n搜尋時間', last, '秒')
    t.join()


async def pop_goods(url):
    global i, j, k
    asession = req.AsyncHTMLSession()
    pre = 'https://online.carrefour.com.tw'
    r = await asession.get(pre + url)
    await r.html.arender()
    e1 = r.html.find("#cq_recomm_slot-89984c043f9f6c5dfe5899d4eb > div > div > div > div:nth-child(3) > div.photo > a")

    e2 = r.html.find("#cq_recomm_slot-89984c043f9f6c5dfe5899d4eb > div > div > div > div:nth-child(6) > "
                     "div.photo > a")
    e3 = r.html.find("#cq_recomm_slot-89984c043f9f6c5dfe5899d4eb > div > div > div > div:nth-child(9) > "
                     "div.photo > a")
    for r1, r2, r3 in zip(e1, e2, e3):
        i = '第 ' + r1.attrs['data-position'] + ' 名 ' + r1.attrs['data-name'] + ' ' + r1.attrs['data-price'] + ' 元 '
        j = '第 ' + r2.attrs['data-position'] + ' 名 ' + r2.attrs['data-name'] + ' ' + r2.attrs['data-price'] + ' 元 '
        k = '第 ' + r3.attrs['data-position'] + ' 名 ' + r3.attrs['data-name'] + ' ' + r3.attrs['data-price'] + ' 元 '

    return i, j, k


# 爬取線上購物網的商品與db產生相關聯
def crawler(n_area):
    category = [record[0] for record in results]
    area = [record[3] for record in results]
    # lowprice = [record[1] for record in results]
    # higtprice = [record[2] for record in results]
    remarks = [record[7] for record in results]
    l_area = []
    for category, area in dict.fromkeys(zip(category, area)):
        if re.match(text, category):
            l_area.append(area)
            n_area = re.sub(r"\[|\]|\'", "", str(l_area)).replace(',', '、')
    return n_area


# 查找線上購物商品的字詞
def find_db():
    if len(list) > 0:
        # noinspection PyBroadException
        try:
            print(text + '可能在: ' + crawler(print()) + ' 走道區域')
            print("以下是商品熱門結果:\n" + content)
        except:
            print('錯誤:資料庫未建立種類資訊!', "\n以下是商品有關連性的結果(若無結果，請檢查關鍵字詞是否輸入有誤!):\n" + content)
    elif len(list)==0:
        print("商品不存在!")
    else:
        pass

    # def pop_goods():
    #     next = input("是否查看前五名人氣熱銷商品(Y/n)? : ")
    rcontent = ''
    if next=="Y":
        # response_hot = requests.get(list[0])
        # soup_hot = BeautifulSoup(response_hot.text, "lxml")
        # k = soup_hot.find_all('a', class_='gtm-product-alink-hotsale')
        # for t in k:
        #     rank = t.get('data-position')
        #     rname = t.get('data-name')
        #     rcontent += f"\n{rank}\n{rname}\n"
        # print(rcontent)
        print('OK')
        # pop = [list[2] for test.find in a]
        # print(pop)
        # test.find(list[0])
        # test.find(list[1])
        # test.find(list[2])


    # print("以下是 {} 前五名人氣熱銷商品: ".format(text))


    # 縮網址


def shorten(long_url, alias):
    URL = "http://tinyurl.com/create.php?source=indexpage&url=" + long_url + "&submit=Make+TinyURL%21&alias=" + alias
    response = urlopen(URL)
    soup = BeautifulSoup(response, 'lxml')
    return soup.find_all('div', {'class': 'indent'})[1].b.string


if __name__=="__main__":
    with open('ascii_art.txt', 'r') as f:
        for line in f:
            print(line.rstrip())
    # noinspection PyBroadException
    try:
        while 1==1:
            connection()
            goods_info()
            find_db()
    except Exception as e:
        disconnection()
        print(e)
