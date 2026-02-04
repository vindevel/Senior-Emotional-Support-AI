from db.database_connect import get_db_connection

def save_emotion_to_db(user_id, emotion, confidence):
    """감정 분석 결과를 MySQL 데이터베이스에 저장"""
    conn = get_db_connection()
    if conn is None:
        return

    # 감정 라벨을 Boolean 값으로 변환
    is_neutral = 1 if emotion == 0 else 0
    is_negative = 1 if emotion == 1 else 0
    is_joy = 1 if emotion == 2 else 0

    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO emotion_face (user_id, timestamp, is_neutral, is_negative, is_joy)
                VALUES (%s, NOW(), %s, %s, %s)
            """
            cursor.execute(sql, (user_id, is_neutral, is_negative, is_joy))
        conn.commit()

    except Exception as e:
        print(f"[ERROR] 감정 데이터 저장 실패: {e}")
    finally:
        conn.close()

def save_emotion_conversation(user_id, emotion, user_text):
    """
    감정 분석 결과를 emotion_conversation 테이블에 저장
    :param user_id: 사용자 고유 ID
    :param emotion: KoBERT에서 받은 감정 분석 결과 ('중립', '부정', '기쁨')
    """

    if user_id is None:
        print("[DB 오류] 감정 분석 결과 저장 실패: user_id 없음")
        return

    # 감정 분석 결과를 Boolean 형태로 변환
    is_neutral = 1 if emotion == "중립" else 0
    is_joy = 1 if emotion == "기쁨" else 0
    is_anxiety = 1 if emotion == "불안" else 0
    is_anger = 1 if emotion == "분노" else 0
    is_wound = 1 if emotion == "상처" else 0
    is_sadness = 1 if emotion == "슬픔" else 0
    is_surprise = 1 if emotion == "놀람" else 0


    query = """
        INSERT INTO emotion_conversation (user_id, timestamp, is_neutral, is_joy, is_anxiety, is_anger, is_wound, is_sadness, is_surprise, user_text)
        VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s)
    """

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id, is_neutral, is_joy, is_anxiety, is_anger, is_wound, is_sadness, is_surprise, user_text))
                conn.commit()  # 변경 사항 저장
            print(f"[DB] 감정 분석 결과 저장 완료! (User ID: {user_id}, 감정: {emotion})")
        except Exception as e:
            print(f"[DB 오류] 감정 분석 결과 저장 실패: {e}")
        finally:
            conn.close()