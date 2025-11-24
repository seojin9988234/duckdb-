import streamlit as st 
import pymysql
import pandas as pd
import time
import duckdb

conn = duckdb.connect("madang.duckdb")

# CSV 파일에서 테이블 생성 (처음 한 번만 실행)
conn.execute("CREATE TABLE IF NOT EXISTS Customer AS SELECT * FROM read_csv_auto('Customer_madang.csv')")
conn.execute("CREATE TABLE IF NOT EXISTS Book AS SELECT * FROM read_csv_auto('Book_madang.csv')")
conn.execute("CREATE TABLE IF NOT EXISTS Orders AS SELECT * FROM read_csv_auto('Orders_madang.csv')")

def fetch(sql):
    return conn.execute(sql).df()

dbConn = pymysql.connect(user='root', passwd='1234', host='192.168.133.130',port = 3306,  db='madang', charset='utf8')
cursor = dbConn.cursor(pymysql.cursors.DictCursor)



def query(sql):
       cursor.execute(sql)
       return cursor.fetchall()

books = [None]
result = query("select concat(bookid, ',', bookname) from Book")
for res in result:
       books.append(list(res.values())[0])

tab1, tab2 = st.tabs(["고객조회", "거래 입력"])
name = ""
custid = 999
result =pd.DataFrame()
name = tab1.text_input("고객명")
select_book = ""

if len(name) > 0:
       sql = "select c.custid, c.name, b.bookname, o.orderdate, o.saleprice from Customer c, Book b, Orders o \
              where c.custid = o.custid and o.bookid = b.bookid and name = '" + name + "';"
       cursor.execute(sql)
       result = cursor.fetchall()
       result = pd.DataFrame(result)
       tab1.write(result)
       custid = result['custid'][0]
       tab2.write("고객번호: " + str(custid))
       tab2.write("고객명: " + name)
       select_book = tab2.selectbox("구매 서적:",books)

       if select_book is not None:
              bookid = select_book.split(",")[0]
              dt = time.localtime()
              dt = time.strftime('%Y-%m-%d', dt)
              orderid = query("select max(orderid) from orders;")[0]['max(orderid)'] + 1
              price = tab2.text_input("금액")
              sql = "insert into orders (orderid, custid, bookid, saleprice, orderdate) values (" + str(orderid) + "," + str(custid) + "," + str(bookid) + "," + str(price) + ",'" + dt + "');"
              if tab2.button('거래 입력'):
                     dbConn.commit()
                     tab2.write('거래가 입력되었습니다.')


