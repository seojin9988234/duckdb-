import streamlit as st
import duckdb
import pandas as pd
import time

# DuckDB 연결 (파일 없으면 생성됨)
conn = duckdb.connect("madang.duckdb")

# CSV를 읽어오고 DuckDB에 테이블 생성
conn.execute("CREATE TABLE IF NOT EXISTS Customer AS SELECT * FROM read_csv_auto('Customer_madang.csv')")
conn.execute("CREATE TABLE IF NOT EXISTS Book AS SELECT * FROM read_csv_auto('Book_madang.csv')")
conn.execute("CREATE TABLE IF NOT EXISTS Orders AS SELECT * FROM read_csv_auto('Orders_madang.csv')")

def fetch(sql):
    return conn.execute(sql).df()

# selectbox에 넣을 책 목록 로드
books_df = fetch("SELECT bookid, bookname FROM Book")
books = ["{} , {}".format(r.bookid, r.bookname) for i, r in books_df.iterrows()]

# UI
tab1, tab2 = st.tabs(["고객조회", "거래 입력"])

# --- 고객조회 ---
name = tab1.text_input("고객명 검색")

if name:
    sql = f"""
        SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice
        FROM Customer c
        JOIN Orders o ON c.custid = o.custid
        JOIN Book b ON o.bookid = b.bookid
        WHERE c.name = '{name}'
    """
    result = fetch(sql)
    tab1.write(result)

# --- 거래 입력 ---
cust_name = tab2.text_input("고객명 입력")
selected_book = tab2.selectbox("구매 책 선택", books)
price = tab2.text_input("금액 입력")

if tab2.button("거래 입력"):
    if cust_name and selected_book and price:
        # custid 찾기 (없으면 자동 등록)
        df_cust = fetch(f"SELECT custid FROM Customer WHERE name='{cust_name}'")
        
        if df_cust.empty:
            next_id = fetch("SELECT COALESCE(MAX(custid),0)+1 AS id FROM Customer")['id'][0]
            conn.execute(f"INSERT INTO Customer VALUES ({next_id}, '{cust_name}', '서울')")  # 주소 임의
            custid = next_id
        else:
            custid = df_cust['custid'][0]

        # bookid
        bookid = int(selected_book.split(",")[0])

        # orderid
        orderid = fetch("SELECT COALESCE(MAX(orderid),0)+1 AS id FROM Orders")['id'][0]

        dt = time.strftime('%Y-%m-%d')

        conn.execute(f"""
            INSERT INTO Orders VALUES ({orderid}, {custid}, {bookid}, {price}, '{dt}')
        """)

        tab2.success("거래가 입력되었습니다!")
    else:
        tab2.error("모든 항목을 입력해주세요.")
