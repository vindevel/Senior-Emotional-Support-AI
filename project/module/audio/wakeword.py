from pvporcupine import create
from pvrecorder import PvRecorder
import time
from audio.recorder import record_audio
from audio.tts import play_tts
from audio.stt import transcribe_audio

access_key = "access key" #본인 access_key
keyword_path = r"C:\project\module\보리야_ko_windows_v3_0_0\보리야_ko_windows_v3_0_0.ppn" #웨이크 워드 설정
model_path = r"C:\project\module\porcupine_params_ko.pv"

porcupine = create(access_key=access_key, keyword_paths=[keyword_path], model_path=model_path)
recorder = PvRecorder(frame_length=512, device_index=0)
recorder.start()

# --------- 보리야 감지 후 녹음 및 STT 실행 ----------
def wake_word_detected(user_id):
    """'보리야' 감지 후 녹음 및 STT 실행"""
    try:
        while True:
            if porcupine.process(recorder.read()) == 0:
                play_tts("네, 말씀하세요.")
                time.sleep(0.8)

                while True:
                    record_audio()  #녹음 실행
                    transcribed_text = transcribe_audio(user_id)  #변환 실행

                    if transcribed_text:
                        print(f"인식된 명령어: {transcribed_text}")

                        if transcribed_text == "stop":
                            break

                        record_audio()
                        additional_input = transcribe_audio(user_id)
                        print(f"인식된 명령어: {additional_input}\n")

                        if transcribed_text == "stop":
                            break

                        if not additional_input:
                            play_tts("잘 못 들었어요. 다시 말씀해주세요.")
                            record_audio()
                            additional_input = transcribe_audio(user_id)
                            print(f"인식된 명령어: {additional_input}\n")

                            if transcribed_text == "stop":
                                break

                            if not additional_input:
                                play_tts("필요하면 또 불러주세요.")
                                break

                    else:
                        play_tts("잘 못 들었어요. 다시 말씀해주세요.")
                        record_audio()
                        additional_input = transcribe_audio(user_id)
                        print(f"인식된 명령어: {additional_input}\n")

                        if transcribed_text == "stop":
                            break
                        
                        if not additional_input:
                            play_tts("필요하면 또 불러주세요.")
                            break
            
    except KeyboardInterrupt:
        recorder.stop()
        porcupine.delete()
        exit()