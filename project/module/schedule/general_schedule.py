import json
import os

SCHEDULE_DIR = os.path.join(os.path.dirname(__file__), "general_schedule_data")
os.makedirs(SCHEDULE_DIR, exist_ok=True)

def get_schedule_file():
    return os.path.join(SCHEDULE_DIR, "general_schedule.json")

def load_schedule():
    """JSON 파일에서 일정 불러오기"""
    try:
        with open(get_schedule_file(), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_schedule(data):
    """JSON 파일에 일정 저장하기"""
    with open(get_schedule_file(), "w") as file:
        json.dump(data, file, indent=4)