import pygame
import os
import time
from gtts import gTTS

#---------------TTS 및 효과음 설정 ---------------
pygame.mixer.init()

# 효과음 및 음성 파일 저장 폴더 설정
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio_file")
os.makedirs(AUDIO_DIR, exist_ok=True)  # 폴더가 없으면 생성

beep_sound_path = os.path.join(AUDIO_DIR, "MP_Pling.mp3")

def play_tts(text, filename="alert.mp3"):
    """gTTS를 사용하여 음성을 생성하고 재생"""
    filename = os.path.join(AUDIO_DIR, filename)  # audio_file 폴더에 저장
    
    tts = gTTS(text=text, lang="ko")

    #기존 파일이 존재하면 unload() 후 삭제
    if os.path.exists(filename):
        try:
            pygame.mixer.init()
            pygame.mixer.music.unload()  #파일을 사용 중인 프로세스 해제
            os.remove(filename)  #파일 삭제
        except Exception as e:
            print(f"파일 삭제 실패: {e}")

    tts.save(filename)  #새로운 TTS 파일 저장

    #파일 저장 후 대기 (안정성 확보)
    time.sleep(0.5)

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)  # 0.1초 대기