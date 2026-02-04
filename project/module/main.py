import subprocess
import threading
import os
from schedule.night_talk import night_talk
from schedule.notifier import schedule_notifier
from db.user import select_or_create_user
from schedule.medication_schedule import initialize_medication_schedule
from utils.exit_handler import listen_for_exit, set_emotion_proc, set_flask_proc, set_react_proc
from audio.remote_wakeword import run_assistant

emotion_proc = None
flask_proc = None
react_proc = None

def initialize():
    global flask_proc, react_proc

    selected_user = select_or_create_user()
    user_id, username, birth_year, phone_number = selected_user

    print(f"\n'{username}'님의 복약 및 식사 알림을 시작합니다...\n")

    user_schedule = initialize_medication_schedule(user_id, username)

    # 감정 분석 subprocess 실행
    emotion_proc = subprocess.Popen(["python", "face/run_emotion_detection.py", str(user_id)])
    set_emotion_proc(emotion_proc)

    # Flask 서버 실행
    flask_proc = subprocess.Popen(["python", "report_api.py"])
    set_flask_proc(flask_proc)

    # React 앱 실행 (start_app.bat 파일 경로가 mental-report 디렉토리 안에 있는 경우)
    react_bat_path = os.path.abspath("mental-report/start_app.bat")
    react_proc = subprocess.Popen([react_bat_path], shell=True)
    set_react_proc(react_proc)

    # 종료 감지 스레드 시작
    threading.Thread(target=listen_for_exit, daemon=True).start()

    threading.Thread(target=schedule_notifier, args=(user_id, username, user_schedule), daemon=True).start()
    threading.Thread(target=night_talk, args=(user_id,), daemon=True).start()

    print("\n웨이크 워드 감지 시작합니다.")
    run_assistant(user_id)

if __name__ == "__main__":
    initialize()
