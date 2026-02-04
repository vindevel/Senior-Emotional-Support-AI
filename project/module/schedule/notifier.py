import time
import datetime
import random
import queue
import threading
from audio.tts import play_tts
from schedule.medication_schedule import load_medication_schedule
from schedule.general_schedule import load_schedule, save_schedule

alarm_queue = queue.Queue()

def alarm_worker():
    """대기열에 있는 알람을 하나씩 실행"""
    while True:
        task = alarm_queue.get()  # 대기열에서 작업 가져오기
        if task is None:
            break  # 종료 신호 받으면 루프 탈출
        task()  # 실행할 작업 실행
        alarm_queue.task_done()

#백그라운드 스레드에서 `alarm_worker()` 실행 (알람 대기열 처리)
worker_thread = threading.Thread(target=alarm_worker, daemon=True)
worker_thread.start()

#------------ 삭사 알림을 음성으로 출력 ------------
def check_meal_schedule():
    """노인의 생활 패턴에 맞춘 식사 알림 (음성 출력)"""
    now = time.strftime("%H:%M")

    meal_schedule = {
        "09:00": "아침 식사 챙기셨나요?",
        "13:00": "점심 식사 챙기셨나요?",
        "19:00": "저녁 식사 챙기셨나요?"
    }

    if now in meal_schedule:
        alert_text = meal_schedule[now]
        print(f"\n[알림] {now} - {alert_text}")
        play_tts(alert_text)  #음성 출력

def is_time_in_range(target_time, margin=1):
    now = datetime.datetime.now()
    target = datetime.datetime.strptime(target_time, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
    delta = abs((now - target).total_seconds() / 60)
    return delta <= margin  # 1분 이내면 True 반환

#------------- 복약 알림을 음성으로 출력 -------------
executed_medicine_alerts = set()
last_checked_date_medicine = datetime.date.today()

def check_medicine_schedule(user_id, username, schedule):
    global last_checked_date_medicine

    if not schedule:
        return

    current_date = datetime.date.today()
    now = datetime.datetime.now().strftime("%H:%M")

    if current_date != last_checked_date_medicine:
        executed_medicine_alerts.clear()
        last_checked_date_medicine = current_date

    for med, times in schedule.items():
        for time in times:
            if is_time_in_range(time, margin=1):  # 1분 이내로 허용
                if (time, med) not in executed_medicine_alerts:
                    alert_text = f"{username}님, {med}을 복용하셨나요?"
                    print(f"\n[알림] {now} - {alert_text}")
                    play_tts(alert_text)
                    executed_medicine_alerts.add((time, med))

# -------------- 알람 관리 함수 --------------
def schedule_notifier(user_id, username, user_schedule):
    user_schedule = load_medication_schedule(user_id)
    if not user_schedule:
        print(f"[오류] 사용자 {user_id}의 스케줄 정보가 비어 있습니다.")
        return

    executed_alerts = set()
    last_checked_date = datetime.date.today()

    while True:
        now = time.strftime("%H:%M")
        current_date = datetime.date.today()

        if current_date != last_checked_date:
            executed_alerts.clear()
            last_checked_date = current_date

        if now not in executed_alerts:
            def execute_tasks():
                check_meal_schedule()
                check_medicine_schedule(user_id, username, user_schedule)
                morning_reminder()

            alarm_queue.put(execute_tasks)
            executed_alerts.add(now)

        time.sleep(1)

#-------------- 일정 관리 JSON 관리 ---------------
def morning_reminder():
    """아침 일정 리마인드 및 해제"""
    now = time.strftime("%H:%M")
    morning_time = "08:00"  # 아침 일정 알림 시간

    if now == morning_time:
        data = load_schedule()
        
        today = str(datetime.date.today())
        if today in data and data[today] == "있어요":
            alert_text = "오늘 일정이 있습니다. 확인해 주세요."
            print(f"[알림] {now} - {alert_text}")
            play_tts(alert_text)  #음성 출력

            del data[today]  #일정 확인 후 삭제
            save_schedule(data)