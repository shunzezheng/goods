# '''
# 目前版本 v1.2.0
# 撰寫者:zeze
# '''

# 若無安裝套件則選是否要自動安裝


try:
    import os
    import re
    import MySQLdb
    from urllib.request import urlopen
    # import MySQLdb
    import requests
    from bs4 import BeautifulSoup
    from logging import exception
except ModuleNotFoundError:
    Promote = input("錯誤: 尚未安所需的套件! 是否自動安裝所需套件(Y/n)? : ")
    if Promote == "Y":
        command = 'pip install BeautifulSoup4 requests urllib3 lxml mysqlclient'
        os.system(command)
        basename = os.path.basename(__file__)
        os.system('python ' + basename)  # 執行此命令
        quit()
    elif Promote == 'n':
        exit()

# 建立db連線到本地端資訊
db = MySQLdb.connect(host="localhost",
                     user="root",
                     passwd="password",
                     db="carrefour")


# db連線
def connection():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM carrefour.goods')
    global results
    results = cursor.fetchall()


def disconnection():
    db.close()


# 爬蟲獲取商品名稱、價格、熱銷、縮網址
def goods_info():
    global content, text, list
    text = input("請輸入欲查詢商品的關鍵字: ")
    content = ""
    list = []
    url = 'https://online.carrefour.com.tw/zh/search?q=' + str(text)
    headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")  # Parser選用lxml，較為快速(?!)
    # num = int(input("您想要查看前幾名熱銷商品: "))
    v = soup.find_all('a', class_='gtm-product-alink', limit=5)  # 前五名
    # 撈資料
    for s in v:
        global category
        serach = s.get('href')
        link = shorten("https://online.carrefour.com.tw" + serach, '')
        name = s.get('data-name')
        price = s.get('data-baseprice')
        category = s.get('data-category')
        list.append(link)
        content += f"\n{category}\n{name}\t{price}\n{link}\n"


# 爬取線上購物網的商品與db產生相關聯
def crawler():
    global n_area
    # try:
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


# 查找線上購物商品的字詞
def find_db():
    if len(list) > 0:
        try:
            crawler()
            print(text + '可能在: ' + n_area + ' 走道區域')
            print("以下是商品前五名熱銷結果:\n" + content)
        except NameError:
            print('錯誤:資料庫未建立種類資訊!', "\n以下是商品有關連性的結果(若無結果，請檢查是否輸入有誤!):" + content)
    elif len(list) == 0:
        print("商品不存在!")


# 縮網址
def shorten(long_url, alias):
    URL = "http://tinyurl.com/create.php?source=indexpage&url=" + long_url + "&submit=Make+TinyURL%21&alias=" + alias
    response = urlopen(URL)
    soup = BeautifulSoup(response, 'html.parser')
    return soup.find_all('div', {'class': 'indent'})[1].b.string


if __name__ == "__main__":

    while 1 == 1:
        connection()
        goods_info()
        find_db()
