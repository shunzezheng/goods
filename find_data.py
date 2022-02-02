import MySQLdb

db = MySQLdb.connect(host="localhost",
                     user="root",
                     passwd="password",
                     db="carrefour")


def connetion():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM carrefour.goods')
    global results
    results = cursor.fetchall()
    return results


def show():
    for record in results:
        col0 = record[0]  # 類別
        col1 = record[1]  # 最低價格
        col2 = record[2]  # 最高價格
        col3 = record[3]  # 區域
        col4 = record[4]  # 左1右2
        col5 = record[5]  # 櫃子數
        col6 = record[6]  # 上1下2全3
        col7 = record[7]  # 備註
        print("%s, %s, %s,%s,%s,%s,%s" % (col1, col2, col3, col4
                                          , col5, col6, col7))
    db.close()


if __name__ == "__main__":
    connetion()
    show()
