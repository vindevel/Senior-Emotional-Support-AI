import time
import random
import datetime
from schedule.general_schedule import load_schedule, save_schedule
from audio.recorder import record_audio
from audio.tts import play_tts
from audio.stt import transcribe_audio

def wait_until(target_hour):
    """현재 시간이 target_hour(예: 20)보다 작으면 대기"""
    while True:
        now = datetime.datetime.now()
        if now.hour >= target_hour:
            break  #20:00 이후면 바로 실행
        remaining_seconds = (target_hour - now.hour) * 3600 - now.minute * 60 - now.second
        print(f"현재 시간 {now.strftime('%H:%M:%S')}, {target_hour}:00까지 {remaining_seconds}초 대기...")
        time.sleep(min(remaining_seconds, 3600))  #최대 1시간 단위로 대기


#-------------- 하루 마무리 대화 기능 --------------
def night_talk(user_id):
    """하루 마무리 대화 (20:00~22:00 랜덤 실행)"""

    #20:00 전이면 자동 대기
    wait_until(20)

    #20:00~22:00 사이에 랜덤 대기 (0~119분)
    random_minutes = random.randint(0, 119)
    print(f"{random_minutes}분 후 night_talk 실행")
    time.sleep(random_minutes * 60)

    #내일 일정 확인
    play_tts("내일 일정이 있으신가요? 네, 아니요로 대답해주세요.")
    time.sleep(1)

    record_audio()

    answer = transcribe_audio(user_id)
    print(answer)
    if "네" in answer:
        data = load_schedule()
        tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))
        data[tomorrow] = "있어요"
        save_schedule(data)
        play_tts("내일 일정을 저장했습니다.")
    elif "아니요" in answer:
        play_tts("알겠습니다. 내일도 좋은 하루 보내세요.")
    else:
        play_tts("일정을 저장하지 못 했습니다. 다시 한 번 말씀해주세요.")
        record_audio()
        answer = transcribe_audio(user_id)
        print(answer)
        if "네" in answer:
            data = load_schedule()
            tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))
            data[tomorrow] = "있어요"
            save_schedule(data)
            play_tts("내일 일정을 저장했습니다.")
        
        elif "아니요" in answer:
            play_tts("알겠습니다. 내일도 좋은 하루 보내세요.")

        else:
            play_tts("일정을 저장하지 못 했습니다.")

    #하루 마무리 대화
    play_tts("오늘 하루는 어떠셨나요?")
    time.sleep(1)
    record_audio()

    transcribe_audio(user_id)