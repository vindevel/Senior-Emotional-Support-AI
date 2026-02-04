from db.database_connect import get_db_connection

#---------------- 사용자 조회 ---------------
def get_all_users():
    """role이 '사용자'인 사용자만 조회 (id, 이름, 전화번호 포함)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, birth_year, phone_number FROM users WHERE role = '사용자'")
    users = cursor.fetchall()
    
    conn.close()
    return users 
    #[(1, '홍길동', '2002', '010-0000-0000'), (2, '김영희', '2002', None)]