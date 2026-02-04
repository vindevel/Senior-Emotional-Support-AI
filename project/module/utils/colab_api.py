import requests
from audio.tts import play_tts
from db.emotion_logger import save_emotion_conversation
import time
# import json

# Colab 서버 주소 (ngrok 실행 후 업데이트 필요)
COLAB_URL = "https://6c26-34-142-240-28.ngrok-free.app"
SERVER_URL = "https://807c-34-16-164-48.ngrok-free.app/"
def send_text_to_colab(user_id, text):
	"""user_id와 함께 텍스트를 Colab 서버로 보내서 감정 분석 및 응답 받기"""

	colab_url_kobert = f"{COLAB_URL}/predict/conversation"
	colab_url_kogpt2 = f"{COLAB_URL}/generate/response"

	try:
		# KoBERT 감정 분석 요청
		start_time = time.time()
		response_kobert = requests.post(colab_url_kobert, json={"text": text})
		emotion = response_kobert.json().get("emotion", "알 수 없음")
		end_time = time.time()
		print(f"[KoBERT] 서버 전송 및 응답 속도: {end_time - start_time:.3f}초")

		# KoGPT2 응답 생성 요청
		start_time = time.time()
		response_kogpt2 = requests.post(colab_url_kogpt2, json={"text": text})
		chatbot_response = response_kogpt2.json().get("response", "응답 생성 실패")
		end_time = time.time()
		print(f"[KoGPT2] 응답 생성 속도: {end_time - start_time:.3f}초")

		# 결과 출력
		print(f"\n감정 분석 결과: {emotion}")
		print(f"챗봇 응답: {chatbot_response}")

		# 챗봇 응답을 TTS로 출력
		play_tts(chatbot_response)

		# 감정 분석 결과 DB 저장
		save_emotion_conversation(user_id, emotion)

		return chatbot_response

	except Exception as e:
		print(f"[오류] Colab 요청 중 오류 발생: {e}")

def send_audio_to_colab(user_id, audio_path, history=None):
    try:
        with open(audio_path, "rb") as f:
            files = {"audio": f}
            data = {"user_id": str(user_id)}

            if history:
                # history를 문자열로 변환하여 전송
                data["history"] = "\n".join(history)

            start_time = time.time()
            response = requests.post(
                f"{SERVER_URL}/process/audio",
                data=data,
                files=files
            )
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"[DEBUG] 전체 응답 시간: {elapsed:.3f}초")

            if response.ok:
                data = response.json()
                transcribed_text = data.get("transcribed_text", "")
                emotion = data.get("emotion", "알 수 없음")
                chatbot_response = data.get("response", "응답 생성 실패")
                stop_intent = data.get("stop_intent", False)

                print(f"인식된 텍스트: {transcribed_text}")
                print(f"감정 분석 결과: {emotion}")
                print(f"챗봇 응답: {chatbot_response}")
                print(f"[DEBUG] stop_intent: {stop_intent}")

                if emotion and emotion.strip() and emotion != "알 수 없음":
                    save_emotion_conversation(user_id, emotion, user_text=transcribed_text)
                else:
                    print("[DB] 감정 없음 또는 저장 불가한 감정 결과 → 저장 생략")

                return {
                    "transcribed_text": transcribed_text,
                    "emotion": emotion,
                    "response": chatbot_response,
                    "stop_intent": stop_intent
                }
            else:
                print(f"[오류] 서버 응답 실패: {response.status_code} - {response.text}")
                play_tts("서버 응답에 실패했어요.")
                return None

    except Exception as e:
        print(f"[예외] 서버 요청 중 오류 발생: {e}")
        play_tts("오류가 발생했어요.")
        return None

