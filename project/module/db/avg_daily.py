from db.database_connect import get_db_connection
import datetime

def fetch_yesterday_conversation_avg(user_id):
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT date, is_joy, is_sadness, is_anxiety, is_wound, is_anger, is_surprise, is_neutral
        FROM daily_conversation_avg
        WHERE user_id = %s AND date = %s
        LIMIT 1
    """, (user_id, yesterday))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data
