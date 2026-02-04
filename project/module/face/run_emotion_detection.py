# face/run_emotion_detection.py
# 감정 분석 실행 진입점
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 상위 폴더 추가

from face.HSEmotion import run_emotion_detection

if __name__ == "__main__":
    user_id = int(sys.argv[1])
    run_emotion_detection(user_id)
