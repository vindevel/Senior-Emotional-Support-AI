import os
import keyboard
import threading

exit_event = threading.Event()
_emotion_proc = None 
_flask_proc = None
_react_proc = None 

def set_flask_proc(proc):
    global _flask_proc
    _flask_proc = proc

def set_emotion_proc(proc):
    global _emotion_proc
    _emotion_proc = proc

def set_react_proc(proc):
    global _react_proc
    _react_proc = proc

def listen_for_exit():
    """'C' 키를 누르면 프로그램 종료"""
    keyboard.wait("c")  # 사용자가 'c'를 누를 때까지 대기
    print("\n[WARNING] 프로그램 종료 키가 눌렸습니다. 종료합니다.")
    exit_event.set()  # 종료 플래그 설정

    if _emotion_proc and _emotion_proc.poll() is None:
        _emotion_proc.terminate()

    if _flask_proc and _flask_proc.poll() is None:
        _flask_proc.terminate()

    if _react_proc and _react_proc.poll() is None:
        print("[INFO] React 앱 종료 중...")
        _react_proc.terminate()
        _react_proc.wait(timeout=5)

    os._exit(0)  #모든 프로세스 강제 종료


