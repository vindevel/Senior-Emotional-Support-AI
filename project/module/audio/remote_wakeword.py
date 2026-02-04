import time
import os
from pvporcupine import create
from pvrecorder import PvRecorder
from audio.recorder import record_audio
from audio.tts import play_tts
from audio.recorder import AUDIO_DIR
from utils.colab_api import send_audio_to_colab

# Porcupine 웨이크워드 설정
access_key = "access_key"
keyword_path = r"C:\project\module\보리야_ko_windows_v3_0_0\보리야_ko_windows_v3_0_0.ppn"
model_path = r"C:\project\module\porcupine_params_ko.pv"
audio_path = os.path.join(AUDIO_DIR, "processed_audio.wav")

# Porcupine 및 Recorder 초기화
porcupine = create(access_key=access_key, keyword_paths=[keyword_path], model_path=model_path)
recorder = PvRecorder(frame_length=512, device_index=0)
recorder.start()

history = []

def run_assistant(user_id):
    try:
        while True:
            if porcupine.process(recorder.read()) == 0:
                play_tts("네, 말씀하세요.")
                time.sleep(0.8)

                while True:
                    record_audio()
                    data = send_audio_to_colab(user_id, audio_path, history=history)

                    if not data or not data.get("transcribed_text", "").strip():
                        play_tts("잘 못 들었어요. 다시 말씀해주세요.")
                        record_audio()
                        data = send_audio_to_colab(user_id, audio_path, history=history)

                        if not data or not data.get("transcribed_text", "").strip():
                            play_tts("필요하시면 또 불러주세요.")
                            break

                    user_text = data["transcribed_text"].strip()
                    stop_flag = data.get("stop_intent", False)

                    if stop_flag:
                        play_tts("필요하시면 또 불러주세요.")
                        break

                    chatbot_response = data.get("response", "")
                    history.append(f"사용자: {user_text}")
                    history.append(f"챗봇: {chatbot_response}")
                    play_tts(chatbot_response)

    except KeyboardInterrupt:
        recorder.stop()
        porcupine.delete()
        exit()
