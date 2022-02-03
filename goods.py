# '''
# 目前版本 v1.1.0
# 撰寫者:zeze
# '''


try:
    import os
    from urllib.request import urlopen
    # import MySQLdb
    import requests
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    Promote = input("錯誤: 尚未安所需的套件! 是否自動安裝所需套件(Y/n)? : ")
    if Promote == "Y":
        command_1 = 'pip install BeautifulSoup4'
        command_2 = 'pip install requests'
        command_3 = 'pip install urllib3'
        os.system(command_1)
        os.system(command_2)
        os.system(command_3)
        basename = os.path.basename(__file__)
        os.system('python ' + basename)
        quit()
    elif Promote == 'n':
        os.exit()

list = []


#
# def connetion():
#     db = MySQLdb.connect(host="localhost",
#                          user="root",
#                          passwd="password",
#                          db="carrefour")
#     cursor = db.cursor()
#     cursor.execute('SELECT * FROM carrefour.goods')


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
        global category
        serach = s.get('href')
        link = shorten("https://online.carrefour.com.tw" + serach, '')
        name = s.get('data-name')
        price = s.get('data-baseprice')
        category = s.get('data-category')
        list.append(link)
        content += f"{category}\n{name}\t{price}\n{link}\n"
    print(content)


def shorten(long_url, alias):
    URL = "http://tinyurl.com/create.php?source=indexpage&url=" + long_url + "&submit=Make+TinyURL%21&alias=" + alias
    response = urlopen(URL)
    soup = BeautifulSoup(response, 'html.parser')
    return soup.find_all('div', {'class': 'indent'})[1].b.string


if __name__ == "__main__":
    while 1 == 1:
        # connetion()
        rgood()
        if len(list) == 0:
            print("商品不存在!")
        else:
            Next = input("是否要繼續搜尋? (y/n) : ")
            if Next == 'y':
                rgood()
            elif Next == 'n':
                quit()
