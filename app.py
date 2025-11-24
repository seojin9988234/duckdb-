import streamlit as st
import duckdb
import pandas as pd

# DuckDB 연결 (GitHub에 올린 madang.duckdb 파일 사용)
con = duckdb.connect(database='madang.duckdb', read_only=True)

tab1, tab2 = st.tabs(["고객조회", "거래 입력"])

# 고객조회 탭
with tab1:
    name = st.text_input("고객명")
    if name:
        query = f"""
        SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice
        FROM customer_madang c
        JOIN orders_madang o ON c.custid = o.custid
        JOIN book_madang b ON b.bookid = o.bookid
        WHERE c.name = '{name}';
        """
        result = con.execute(query).df()
        st.write(result)

# 거래 입력 탭 (Cloud에서는 비활성화)
with tab2:
    st.info("Cloud 버전에서는 보안/DB 문제로 입력 기능이 비활성화되었습니다.")
