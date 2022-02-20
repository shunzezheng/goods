#                                 _                                      _               _
#                                | |                                    | |             | |
#      ___  _ __  __ _ __      __| |  ___  _ __   _ __   _ __  ___    __| | _   _   ___ | |_
#     / __|| '__|/ _` |\ \ /\ / /| | / _ \| '__| | '_ \ | '__|/ _ \  / _` || | | | / __|| __|
#    | (__ | |  | (_| | \ V  V / | ||  __/| |    | |_) || |  | (_) || (_| || |_| || (__ | |_
#     \___||_|   \__,_|  \_/\_/  |_| \___||_|    | .__/ |_|   \___/  \__,_| \__,_| \___| \__|
#                                                | |
#                                                |_|
#
#
# 目前版本 v1.7.0
# 撰寫成員:余若榛、鄭舜澤


# 若無安裝套件則選是否要自動安裝
try:
    import os
    import io
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
        os.system('python ' + basename)  # automatic run script on root
        quit()
    elif Promote=="n":
        exit()

# local connection info
db = MySQLdb.connect(host="localhost", user="root", passwd="password", db="carrefour")


# connection to database and execute query
def connection():
    # noinspection PyBroadException
    try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM carrefour.goods')
        global results
        results = cursor.fetchall()
    except:
        print("error:Disable connections!")


# connection to database
def disconnection():
    db.close()


msg = '''
您好，歡迎使用本系統!
請輸入'1': 查詢商品資訊
請輸入'2': 查詢商家資訊
請輸入'3': 查看本月DM
'''

business_info = '''
家樂福 中原店
服務選項: 店內購物 · 路邊取貨 · 外送
地址： 320桃園市中壢區中華路二段501號
營業時間： 24 小時營業
健康與安全: 必須戴口罩 · 需要測量體溫 · 員工有配戴口罩 · 員工會接受體溫測量
電話： 080 020 0359
'''


def show_menu():
    with open('ascii_art.txt', 'r', encoding='UTF-8') as f:
        for line in f:
            print(line.rstrip())
    # try:
    print(msg, end='')
    opts = input(':')
    if opts=='1':
        while 1==1:
            connection()
            goods_info()
            find_db()
    elif opts=='2':
        print(business_info)
        show_menu()
    elif opts=='3':
        catalogs(url_api)
        show_menu()
    else:
        print('輸入錯誤!')
        show_menu()


# except Exception as e:
#     disconnection()
#     print(e)


# recognize speech using Google Speech Recognition
def ASR():
    global words
    # obtain audio from the microphone
    r = sr.Recognizer()
    # read the audio
    with sr.Microphone() as source:
        # create the ambient noise energy level
        r.adjust_for_ambient_noise(source, duration=0)  # duration=0 not restrain ambient noise
        audio = r.listen(source)  # recognize finished stop
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
        blank = input("請按下Enter鍵後進行搜尋!")
        if blank=="":
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
        print('聆聽中......')
        return ASR()
    except sr.RequestError as err:
        print("No response from Google Speech Recognition service: {0}".format(err))


def loading(durtion):
    for num in range(100 + 1):
        time.sleep(durtion / 100)
        sys.stdout.write(("\r查詢中... [ %d" % num + "% ] "))
        sys.stdout.flush()


# crawler the product info (name、link、price、pop)
def goods_info():
    global content, text, listx, pop_result, t1, path
    content = ""
    listx = []
    print("請輸入欲查詢商品的關鍵字(語音輸入):", end='')
    url = 'https://online.carrefour.com.tw/zh/search?q=' + str(ASR() if not None else print("error!"))
    user_agent = UserAgent()
    asession = req.AsyncHTMLSession()
    response = requests.get(url, headers={'user-agent': user_agent.random})
    soup = BeautifulSoup(response.text, "lxml")  # Parser選用lxml，較為快速
    # extract the html tag <a> sections
    extract = soup.find_all('a', class_='gtm-product-alink', limit=3)
    ele = [s.get('href') for s in extract]

    if len(ele) > 0:
        listx.append(ele)
        path = './recode/{}.txt'
        if os.path.isfile(path.format(words)):
            with io.open(path.format(words), encoding='utf8') as recode:
                good_info = recode.read()
                print(good_info)
        else:
            t = threading.Thread(target=loading, args=(5,))
            t.start()
            t1 = time.time()
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
                listx.append(link)
                pop = '與此商品之相關熱銷商品:\n' + str(pop_result[items])
                content += f"\n{category}\n{name}\t{price}\n{link}\n{pop}"
            last = time.time() - t1
            print('\n搜尋時間', last, '秒')
            print("以下是商品熱門結果:\n" + content)
            save_data_to_local()
    else:
        print("商品不存在!")


def save_data_to_local():
    file = open('recode/{}.txt'.format(words), 'w+', encoding='utf8')
    file.write('關鍵字:{}\n'.format(words) + content)


async def pop_goods(url):
    global i, j, k
    asession = req.AsyncHTMLSession()
    pre = 'https://online.carrefour.com.tw'
    r = await asession.get(pre + url)
    try:
        await r.html.arender()
    except:
        await r.html.arender(timeout=20)
    e3 = r.html.find("#cq_recomm_slot-89984c043f9f6c5dfe5899d4eb > div > div > div > div:nth-child(9) > div.photo > a")
    e2 = r.html.find("#cq_recomm_slot-89984c043f9f6c5dfe5899d4eb > div > div > div > div:nth-child(6) > div.photo > a")
    e1 = r.html.find("#cq_recomm_slot-89984c043f9f6c5dfe5899d4eb > div > div > div > div:nth-child(3) > div.photo > a")
    for r1, r2, r3 in zip(e1, e2, e3):
        i = '第 ' + r1.attrs['data-position'] + ' 名 ' + r1.attrs['data-name'] + ' ' + r1.attrs['data-price'] + ' 元 '
        await asyncio.sleep(1)
        j = '第 ' + r2.attrs['data-position'] + ' 名 ' + r2.attrs['data-name'] + ' ' + r2.attrs['data-price'] + ' 元 '
        await asyncio.sleep(1)
        k = '第 ' + r3.attrs['data-position'] + ' 名 ' + r3.attrs['data-name'] + ' ' + r3.attrs['data-price'] + ' 元 '
    return i, j, k


url_api = 'https://www.carrefour.com.tw/console/api/v1/catalogues/%E8%BC%95%E5%A5%A2%E7%BE%8E%E5%A6%9D'


def catalogs(url_api):
    global urls
    session = HTMLSession()
    r = session.get(url_api, headers={'accept': 'application/json'})
    r.html.render()
    responseData = r.json()
    urls = responseData['data']['images']
    print(urls)


# 爬取線上購物網的商品與db產生相關聯
def crawler(n_area):
    category = [record[0] for record in results]
    area = [record[3] for record in results]
    l_area = []
    for category, area in dict.fromkeys(zip(category, area)):
        if re.match(words, category):
            l_area.append(area)
        key = dict.fromkeys(l_area).keys()
        n_area = re.sub(r"\[|\]|\'", "", str(list(key)).replace(',', '、'))
    return n_area


# 查找線上購物商品的字詞
def find_db():
    if len(listx) > 0:
        if len(crawler(print())) > 0:
            print(words + '可能在: ' + crawler(print()) + ' 走道區域')
        else:
            print('錯誤:資料庫未建立種類資訊，無法得知商品位在哪些走道區域!')


# 縮網址
def shorten(long_url, alias):
    URL = "http://tinyurl.com/create.php?source=indexpage&url=" + long_url + "&submit=Make+TinyURL%21&alias=" + alias
    response = urlopen(URL)
    soup = BeautifulSoup(response, 'lxml')
    return soup.find_all('div', {'class': 'indent'})[1].b.string


if __name__=="__main__":
    show_menu()
