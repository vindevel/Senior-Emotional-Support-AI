from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
from wordcloud import WordCloud
from konlpy.tag import Okt
from collections import Counter
from db.database_connect import get_db_connection
from datetime import date, datetime
from PIL import Image
import numpy as np

conversation_bp = Blueprint("conversation", __name__)

@conversation_bp.route("/api/avg/conversation")
def get_conversation_avg():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT date,
            is_joy,
            is_sadness,
            is_anxiety,
            is_wound,
            is_anger,
            is_surprise,
            is_neutral
        FROM daily_conversation_avg
        WHERE user_id = %s
        ORDER BY date ASC
    """, (user_id,))

    data = cursor.fetchall()
    for row in data:
        if isinstance(row['date'], (datetime, date)):
            row['date'] = row['date'].strftime('%Y-%m-%d')

    cursor.close()
    conn.close()
    return jsonify(data)


@conversation_bp.route("/api/weekly/conversation_avg")
def get_weekly_conversation_avg():
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
            ROUND(AVG(is_anxiety), 4) AS avg_anxiety,
            ROUND(AVG(is_wound), 4) AS avg_wound,
            ROUND(AVG(is_anger), 4) AS avg_anger,
            ROUND(AVG(is_sadness), 4) AS avg_sadness,
            ROUND(AVG(is_surprise), 4) AS avg_surprise
        FROM daily_conversation_avg
        WHERE user_id = %s
        GROUP BY year, month, week
        ORDER BY year, month, week
    """
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    conn.close()

    return jsonify(results)

@conversation_bp.route("/api/wordcloud/conversation_weeks")
def get_wordcloud_conversation_weeks():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            YEAR(timestamp) AS year,
            MONTH(timestamp) AS month,
            FLOOR((DAY(timestamp) - 1) / 7) + 1 AS week
        FROM emotion_conversation
        WHERE user_id = %s AND user_text IS NOT NULL
        GROUP BY year, month, week
        ORDER BY year, month, week
    """, (user_id,))
    weeks = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(weeks)

def load_stopwords_from_file(filepath: str) -> set:
    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip().lower() for line in f if line.strip())
    
@conversation_bp.route("/api/wordcloud/conversation")
def get_conversation_wordcloud():
    user_id = request.args.get("user_id")
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    week = request.args.get("week", type=int)

    if not (user_id and year and month and week):
        return jsonify({"error": "user_id, year, month, week are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_text FROM emotion_conversation
        WHERE user_id = %s 
            AND user_text IS NOT NULL
            AND YEAR(timestamp) = %s 
            AND MONTH(timestamp) = %s 
            AND FLOOR((DAY(timestamp) - 1) / 7) + 1 = %s
    """, (user_id, year, month, week))
    sentences = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    # 2. 단어 분석
    okt = Okt()
    stopwords = load_stopwords_from_file(r"stopwords-ko.txt")
    drop_words = {"그렇다", "되다", "하다", "같다", "있다", "싶다", "돼다"}
    keep_words = {"나", "너", "우리", "혼자", "딸", "죽고", "좋아", "놀라다"}
    stopwords = (stopwords | drop_words) - keep_words

    tokens = []
    for sentence in sentences:
        for word, pos in okt.pos(sentence, stem=True):
            if pos in ['Noun', 'Adjective', 'Verb']:
                word = word.lower()
                if word not in stopwords and len(word) > 1:
                    tokens.append(word)

    word_freq = Counter(tokens)

    if not word_freq:
        return jsonify({
            "status": "no_data",
            "message": "해당 주차에 사용자 대화가 없어 단어 빈도를 표시할 수 없습니다."
        }), 200
    
    # 3. 워드클라우드 생성
    wc = WordCloud(
        font_path=r"PRETENDARD-REGULAR.TTF",  # 한글 폰트 경로
        width=700,
        height=400,
        background_color="white",
        colormap="ocean",
        random_state=80
    ).generate_from_frequencies(word_freq)

    image_stream = BytesIO()
    wc.to_image().save(image_stream, format="PNG")
    image_stream.seek(0)
    return send_file(image_stream, mimetype="image/png")
