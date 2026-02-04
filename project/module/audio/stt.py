import whisper
import os
import warnings
from utils.colab_api import send_text_to_colab
from audio.tts import play_tts
import time

AUDIO_FILE_PATH = os.path.join(os.path.dirname(__file__), "audio_file", "processed_audio.wav")

#FP16 관련 경고 숨기기
warnings.simplefilter("ignore")

audio_file = AUDIO_FILE_PATH

#Whisper 모델 로드
whisper_model = whisper.load_model("small")

def transcribe_audio(user_id):
    """음성을 Whisper STT로 변환 후 Colab과 통신"""
    try:
        #파일이 존재하지 않거나 비어 있으면 변환 중단
        if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
            print("[경고] 오류: 변환할 오디오 파일이 존재하지 않거나 비어 있습니다.")
            return ""

        print("음성을 인식 중...")
        start_time = time.time()
        result = whisper_model.transcribe(audio_file, fp16=False, language="ko", task="transcribe", no_speech_threshold=0.4)
        end_time = time.time()
        print(f"[Whisper] 변환 속도: {end_time - start_time:.3f}초")
        transcribed_text = result.get("text", "").strip()
        
        if transcribed_text:
            if is_stop_intent(transcribed_text):
                play_tts("필요하시면 또 불러주세요.")
                return "stop"
        
            response = send_text_to_colab(user_id, transcribed_text)
            return transcribed_text
        
        else:
            print("[경고] 변환된 텍스트 없음")
            return ""
    except Exception as e:
        print(f"[경고] Whisper 변환 오류: {e}")
        return ""

stop_words = {"그만하자", "이제 됐어", "그만 하자"}
def is_stop_intent(text: str) -> bool:
    """종료 의도가 담긴 텍스트인지 판별"""
    return any(stop_word in text for stop_word in stop_words)



