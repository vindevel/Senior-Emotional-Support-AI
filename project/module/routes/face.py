from flask import Blueprint, request, jsonify
from db.database_connect import get_db_connection
from datetime import date, datetime

face_bp = Blueprint('face', __name__)

@face_bp.route("/api/avg/face")
def get_face_avg():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT date, is_joy, is_neutral, is_negative
        FROM daily_face_avg
        WHERE user_id = %s
        ORDER BY date ASC
    """, (user_id,))
    data = cursor.fetchall()

    # 날짜 포맷을 'YYYY-MM-DD' 로 변환
    for row in data:
        if isinstance(row['date'], (datetime, date)):
            row['date'] = row['date'].strftime('%Y-%m-%d')

    cursor.close()
    conn.close()
    return jsonify(data)

@face_bp.route("/api/weekly/face_avg")
def get_weekly_face_avg():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            YEAR(date) AS year,
            MONTH(date) AS month,
            FLOOR((DAY(date) - 1) / 7) + 1 AS week,
            ROUND(AVG(is_joy), 4) AS avg_joy,
            ROUND(AVG(is_neutral), 4) AS avg_neutral,
            ROUND(AVG(is_negative), 4) AS avg_negative
        FROM daily_face_avg
        WHERE user_id = %s
        GROUP BY year, month, week
        ORDER BY year, month, week
    """
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    conn.close()

    return jsonify(results)
