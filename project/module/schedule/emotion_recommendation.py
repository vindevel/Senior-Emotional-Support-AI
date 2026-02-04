import datetime
import time
from audio.tts import play_tts
from db.get_audio_blob import get_random_content
from db.avg_daily import fetch_yesterday_conversation_avg
from audio.play_audio_blob import play_audio_blob

# 감정 이름 매핑
emotion_name_map = {
    'is_joy':'기쁨',
    'is_sadness': '슬픔',
    'is_anxiety': '불안',
    'is_wound': '상처',
    'is_anger': '분노',
    'is_surprise': '놀람',
    'is_neutral':'중립'
}

def get_dominant_emotion(user_id):
    data = fetch_yesterday_conversation_avg(user_id)
    if not data:
        print("감정 데이터가 없습니다.")
        return None

    # 1단계 점수 수집
    neutral = data.get('is_neutral', 0)
    joy = data.get('is_joy', 0)
    anxiety = data.get('is_anxiety', 0)
    wound = data.get('is_wound', 0)
    anger = data.get('is_anger', 0)
    sadness = data.get('is_sadness', 0)
    surprise = data.get('is_surprise', 0)

    negative_total = anxiety + wound + anger + sadness + surprise

    # 1차 그룹 비교
    group_scores = {
        'neutral': neutral,
        'joy': joy,
        'negative': negative_total
    }

    dominant_group = max(group_scores, key=group_scores.get)

    if dominant_group == 'negative':
        # 2차 판단: 부정 감정 중 가장 높은 것 선택
        negative_emotions = {
            'anxiety': anxiety,
            'wound': wound,
            'anger': anger,
            'sadness': sadness,
            'surprise': surprise
        }
        dominant_emotion = max(negative_emotions, key=negative_emotions.get)
    else:
        dominant_emotion = dominant_group

    print(f"우세한 감정: {dominant_emotion} ({emotion_name_map.get(dominant_emotion, dominant_emotion)})")
    return dominant_emotion

def present_content(dominant_emotion):
    """감정에 따른 콘텐츠 안내 및 재생"""
    emotion_kr = emotion_name_map.get(dominant_emotion, "")

    if dominant_emotion in ['anger', 'surprise']:
        if dominant_emotion == 'surprise':
            dominant_emotion = 'confusion'
        result = get_random_content("classic", dominant_emotion)
        if result and result.get("audio_data"):
            play_tts(f"오늘은 차분한 클래식 음악을 추천드립니다.")
            play_tts(f"'{result['title']}'입니다.")
            play_audio_blob(result["audio_data"])
        else:
            print("클래식 콘텐츠를 찾을 수 없습니다.")

    elif dominant_emotion in ['sadness', 'anxiety', 'wound']:
        result = get_random_content("poems", dominant_emotion)
        if result and result.get("content"):
            play_tts(f"오늘은 위로가 되는 시 한 편을 소개하겠습니다.")
            play_tts(f"{result['author']}의 시, '{result['title']}'입니다.")
            play_tts(result["content"])
        else:
            print("시 콘텐츠를 찾을 수 없습니다.")

def is_morning():
    current_hour = datetime.datetime.now().hour
    return 8 <= current_hour < 10

def is_evening():
    current_hour = datetime.datetime.now().hour
    return 18 <= current_hour < 20

def emotion_based_content_routine(user_id):
    dominant_emotion = get_dominant_emotion(user_id)
    if not dominant_emotion:
        return

    if dominant_emotion in ['anger', 'surprise'] and is_morning():
        present_content(dominant_emotion)
    elif dominant_emotion in ['sadness', 'anxiety', 'wound'] and is_evening():
        present_content(dominant_emotion)
    else:
        print("현재 시간대에는 실행 조건이 맞지 않습니다.")

def run_daily_emotion_support(user_id):
    """매일 아침 또는 저녁에 감정 기반 콘텐츠 실행"""
    while True:
        now = datetime.datetime.now()
        if is_morning() or is_evening():
            print(f"{now.strftime('%Y-%m-%d %H:%M')} - 감정 기반 콘텐츠 실행 시도 중...")
            emotion_based_content_routine(user_id)
            print("오늘 콘텐츠 실행 완료. 내일을 기다립니다.")
            time.sleep(24 * 3600)  # 하루 대기
        else:
            print(f"{now.strftime('%Y-%m-%d %H:%M')} - 현재는 실행 시간이 아닙니다. 1시간 후 재확인합니다.")
            time.sleep(3600)
