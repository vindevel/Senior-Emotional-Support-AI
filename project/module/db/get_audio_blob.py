#db\get_audio_blob.py

from db.database_connect import get_db_connection
import random

def get_random_content(table, emotion_type):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if table == "classic":
        cursor.execute("""
            SELECT audio_data, title
            FROM classic 
            WHERE emotion_type = %s
        """, (emotion_type,))
    elif table == "poems":
        cursor.execute("""
            SELECT content, title, author 
            FROM poems 
            WHERE emotion_type = %s
        """, (emotion_type,))
    else:
        return None

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    if not results:
        return None

    return random.choice(results)
