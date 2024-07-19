# API로 데이터 가져오기(이미 가져온 것으로 가정)
import json
import sqlite3
import numpy as np

with open("/root/LLM_Bootcamp/stay_recommendation_service/info_list.json", 'r', encoding='utf-8') as file: # api로 불러온 JSON 파일을 열고 내용 읽기
    data = json.load(file)  # JSON 파일을 파이썬 딕셔너리로 변환
with open("/root/LLM_Bootcamp/stay_recommendation_service/info_result_list.json", 'r', encoding='utf-8') as file: # api로 불러온 JSON 파일을 열고 내용 읽기
    data2 = json.load(file)  # JSON 파일을 파이썬 딕셔너리로 변환

# 데이터베이스에 데이터를 저장하는 함수
def save_data_to_db(data):
    conn = sqlite3.connect('accommodations.db')
    cur = conn.cursor()

    # 기존 테이블 삭제
    cur.execute("DROP TABLE IF EXISTS accommodations")

    # 테이블 생성
    cur.execute("""
        CREATE TABLE IF NOT EXISTS accommodations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            address TEXT,
            tel TEXT,
            type TEXT,
            checkintime TEXT,
            checkouttime TEXT,
            sauna TEXT,
            seminar TEXT,
            fitness TEXT,
            karaoke TEXT,
            beauty TEXT,
            barbecue TEXT
        )
    """)

    # 데이터 삽입
    for row_num in range(len(data2)):
        cur.execute(
            "INSERT INTO accommodations (title, address, tel, type, checkintime, checkouttime, sauna, seminar, fitness, karaoke, beauty, barbecue) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (data[row_num]['title'], data[row_num]['address'], data[row_num]['tel'], 
             data[row_num]['type'], data2[row_num]['checkintime'], data2[row_num]['checkouttime'],
             data2[row_num]['sauna'], data2[row_num]['seminar'], data2[row_num]['fitness'],
             data2[row_num]['karaoke'], data2[row_num]['beauty'], data2[row_num]['barbecue']
            )
        )

    conn.commit()
    cur.close()
    conn.close()

# 벡터 생성 및 저장
save_data_to_db(data)

def fetch_rows():
    conn = sqlite3.connect('accommodations.db')
    cur = conn.cursor()

    # 첫 행을 조회하는 SQL 쿼리
    cur.execute("SELECT * FROM accommodations LIMIT 400")
    rows = cur.fetchall()

    # 조회된 결과 출력
    # for row in rows:
    #     print(row)

    conn.close()

    return rows

# fetch_rows()
