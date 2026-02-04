import mysql.connector

#----------------MySQL 연결 정보 설정----------------
DB_CONFIG = {
    "host": "host ip address",
    "user": "유저 이름",
    "password": "비밀번호",
    "database": "데이터베이스 이름",
    "port": 3306
}

def get_db_connection():
    """MySQL 데이터베이스 연결"""
    try:
        return mysql.connector.connect(**DB_CONFIG)

    except mysql.connector.Error as err:
        print(f"[경고] MySQL 연결 오류: {err}")
        return None  # 연결 실패 시 None 반환