import soundfile as sf
import numpy as np
import time
from pvrecorder import PvRecorder
import os

#오디오 저장 폴더 설정
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio_file")
os.makedirs(AUDIO_DIR, exist_ok=True)  #폴더가 없으면 생성

_recorder_instance = None
def get_recorder():
    """PvRecorder 인스턴스를 한 번만 생성"""
    global _recorder_instance
    if _recorder_instance is None:
        try:
            devices = PvRecorder.get_available_devices()
            if not devices:
                raise RuntimeError("[경고] 사용 가능한 오디오 장치가 없습니다. 마이크를 확인하세요.")

            # 기본 장치 선택 (사용자가 변경 가능)
            device_index = 0

            _recorder_instance = PvRecorder(frame_length=512, device_index=device_index)
            _recorder_instance.start()
        except Exception as e:
            print(f"[경고] 마이크 초기화 실패: {e}")
            exit(1)

    return _recorder_instance

def record_audio(filename="processed_audio.wav", duration=6, gain=6.0):
    """음성 녹음 (볼륨 증폭 + 노이즈 필터링)"""
    output_file = os.path.join(AUDIO_DIR, filename)  # audio_file 폴더에 저장
    
    print("녹음 시작...")
    time.sleep(0.7)
    audio_data = []
    recorder = get_recorder()  #기존 인스턴스를 가져옴

    #기존 녹음 파일 삭제 (손상된 파일 방지)
    if os.path.exists(output_file):
        os.remove(output_file)

    for _ in range((16000 * duration) // recorder.frame_length):
        frame = np.array(recorder.read(), dtype=np.float32)
        frame = frame * gain
        frame = np.clip(frame, -32768, 32767).astype(np.int16)
        audio_data.extend(frame)

    sf.write(output_file, np.array(audio_data, dtype=np.int16), samplerate=16000, format="WAV", subtype="PCM_16")

    #파일 생성 후 확인
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        print("녹음 완료")
    else:
        print("오류: 녹음된 파일이 비어 있음")