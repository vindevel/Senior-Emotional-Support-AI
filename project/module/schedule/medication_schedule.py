import os
import json

#--------------저장된 복약 일정 (JSON)--------------
SCHEDULE_DIR = os.path.join(os.path.dirname(__file__), "medication_schedules_json")

# 폴더가 없으면 생성
os.makedirs(SCHEDULE_DIR, exist_ok=True)

def get_medication_schedule_file(user_id):
    """사용자별 복약 일정 JSON 파일명 반환"""
    return os.path.join(SCHEDULE_DIR, f"medication_schedule_{user_id}.json")

def load_medication_schedule(user_id):
    """사용자별 복약 일정 불러오기"""
    schedule_file = get_medication_schedule_file(user_id)
    
    if not os.path.exists(schedule_file):
        print(f"'{schedule_file}' 파일이 존재하지 않습니다. 새로 생성해야 합니다.")
        return {}

    try:
        with open(schedule_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except json.JSONDecodeError:
        print(f"[경고] '{schedule_file}' 파일이 손상되었습니다. 새로 생성합니다.")
        return {}


def save_medication_schedule(user_id, schedule):
    """사용자별 복약 일정 저장"""
    schedule_file = get_medication_schedule_file(user_id)
    with open(schedule_file, "w", encoding="utf-8") as file:
        json.dump(schedule, file, indent=4, ensure_ascii=False)

#----------------복약 일정 추가----------------
def initialize_medication_schedule(user_id, username):
    """사용자별 복약 일정 입력 (파일이 없을 때만 설정 진행, `{}`이면 일정 없음으로 처리)"""
    print(f"'{username}'님의 복약 일정을 설정 중...")

    schedule_file = get_medication_schedule_file(user_id)

    #JSON 파일이 없으면 복약 설정 진행
    if not os.path.exists(schedule_file):
        print(f"\n '{schedule_file}' 파일이 존재하지 않습니다. 복약 설정을 진행합니다.")
        return setup_medication_schedule(user_id, username)  #복약 설정 실행

    #JSON 파일이 있지만 `{}`(빈 객체)이면 복약 일정 없음으로 처리
    schedule = load_medication_schedule(user_id)

    if schedule == {}:
        print(f"▶ '{username}'님은 현재 복용할 약이 없습니다. 복약 알림 없이 진행합니다.")
        return  #JSON 파일이 있지만 `{}`이면 설정 진행하지 않음

    print(f"\n'{username}'님의 기존 복약 일정이 존재합니다. 변경 없이 진행합니다.")
    return schedule

def setup_medication_schedule(user_id, username):
    """사용자별 복약 일정 설정"""
    print("\n※ 복용하는 약을 입력하세요.")
    medicine_input = input("약 이름을 쉼표로 구분하여 입력하세요 (없으면 Enter): ").strip()

    #사용자가 아무 약도 입력하지 않으면 빈 JSON 저장 후 종료
    if not medicine_input:
        print(f"\n'{username}'님은 현재 복용할 약이 없습니다. 복약 알림 없이 진행합니다.")
        save_medication_schedule(user_id, {})  #빈 JSON 저장
        return  #함수 종료

    #정상적인 복약 일정 입력
    medicines = [med.strip() for med in medicine_input.split(",")]

    schedule = {}

    for medicine in medicines:
        while True:
            time_input = input(f"{medicine}의 복약 시간을 쉼표로 구분하여 입력하세요 (예: 08:00, 20:00): ").strip()
            times = [t.strip() for t in time_input.split(",")]
            if all(t.count(":") == 1 and t.split(":")[0].isdigit() and t.split(":")[1].isdigit() for t in times):
                schedule[medicine] = times
                break
            else:
                print("[경고] 올바른 시간 형식이 아닙니다. HH:MM 형식으로 입력하세요.")

    save_medication_schedule(user_id, schedule)
    print(f"\n▶ '{username}'님의 복약 일정이 저장되었습니다. ({schedule})")
