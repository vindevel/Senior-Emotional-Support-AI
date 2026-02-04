import cv2
from utils.exit_handler import exit_event
import numpy as np
import torch
import mediapipe as mp
import time
from hsemotion.facial_emotions import HSEmotionRecognizer
from db.emotion_logger import save_emotion_to_db

# PyTorch 2.6의 `weights_only=True` 기본값을 `False`로 강제 변경
torch_load_original = torch.load  # 기존 `torch.load()` 저장
def torch_load_override(*args, **kwargs):
    if "weights_only" not in kwargs:
        kwargs["weights_only"] = False  # 기본값을 False로 변경하여 모델 로딩 문제 방지
    return torch_load_original(*args, **kwargs)
torch.load = torch_load_override  # `torch.load()`를 새로운 함수로 교체

BRIGHTNESS_THRESHOLD = 15  # 감정 분석이 원활하게 이루어지는 최소 밝기 값

# Mediapipe 얼굴 감지 초기화
mp_face_detection = mp.solutions.face_detection
face_detector = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

# HSEmotion 모델 로드
model = HSEmotionRecognizer(model_name='enet_b0_8_va_mtl')

# 감정 라벨을 정수로 맵핑 (0 = 중립, 1 = 부정, 2 = 긍정)
EMOTION_MAPPING = {
    'Neutral': 0, 'Happiness': 2, 'Surprise': 1, 'Sadness': 1, 
    'Anger': 1, 'Disgust': 1, 'Fear': 1, 'Contempt':1
}

def get_brightness(frame):
    """ 현재 프레임의 평균 밝기를 계산하는 함수 """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 흑백 변환
    return np.mean(gray)  # 밝기의 평균값 계산

def is_face_detected(frame):
    """ 얼굴이 감지되었는지 확인하는 함수 """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR -> RGB 변환
    results = face_detector.process(rgb_frame)      # Mediapipe 얼굴 감지 수행
    return results.detections is not None, results  # 감지된 얼굴이 있으면 True 반환

def select_external_camera():
    for i in range(10):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if not cap.isOpened():
            continue
        
        # 해상도 강제 설정
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        ret, frame = cap.read()
        if ret:
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"카메라 {i}: {int(width)}x{int(height)}")
            if width > 1280:  # 외장 캠으로 간주
                cap.release()
                return i
        cap.release()
    return None


def open_camera_fast(index, timeout=3.0):
    """
    가능한 빠르게 카메라를 열되, 프레임 유효성 확인 후 반환
    timeout 초 내에 유효 프레임을 못 받으면 실패
    """
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # Windows에서 안정적인 DirectShow 백엔드 사용
    # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

    """
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
    print(f"[DEBUG] 실제 FOURCC: {codec}")
    """

    start_time = time.time()
    
    while time.time() - start_time < timeout:
        ret, frame = cap.read()
        if ret and frame is not None and frame.shape[0] > 0:
            print(f"[INFO] 카메라 index {index} 열기 성공 (경과: {time.time() - start_time:.2f}s)")
            return cap
        
    print(f"[ERROR] 카메라 index {index} 열기 실패 (timeout {timeout}s)")
    return None


def measure_camera_startup(cap, warmup=10):
    print(f"[DEBUG] 카메라 워밍업 시작")
    t_start = time.time()

    if not cap.isOpened():
        print("[ERROR] 카메라 열기 실패")
        return

    for i in range(warmup):
        ret, frame = cap.read()
        if not ret or frame is None:
            print(f"[WARNING] 프레임 {i+1} 실패")
        else:
            if i == 0:
                t_first = time.time()
                print(f"[DEBUG] 첫 유효 프레임 도착: {(t_first - t_start):.3f}초")

    t_end = time.time()
    print(f"[DEBUG] 워밍업 전체 소요 시간: {(t_end - t_start):.3f}초")

def run_emotion_detection(user_id):
    # t0 = time.time()  # 전체 감정 분석 시작 시점

    cap = None

    # 웹캠 초기화
    # 외장 카메라 자동 선택
    cam_index = select_external_camera()
    if cam_index is None:
        print("[ERROR] 외장 카메라를 찾을 수 없습니다.")
        return

    # 자동 선택된 인덱스로 카메라 열기
    cap = open_camera_fast(index=cam_index)
    if cap is None or not cap.isOpened():
        print("[ERROR] 웹캠을 열 수 없습니다.")
        return

    print(f"[DEBUG] 웹캠 index {cam_index} 열기 성공!")
    measure_camera_startup(cap)  # 워밍업 측정

    # 분석 간격 설정
    last_analysis_time = 0
    analysis_interval = 1  # 초 단위

    # 감정 분석 결과 저장용 딕셔너리
    latest_emotion_results = {}  # key: 얼굴 인덱스 또는 id, value: (emotion_label, prob, timestamp)


    try:
        while cap.isOpened() and not exit_event.is_set():
            ret, frame = cap.read()
            if not ret or frame is None:
                print("[ERROR] 웹캠 프레임을 읽을 수 없습니다.")
                break

            frame = cv2.flip(frame, 1)
            current_time = time.time()

            brightness = get_brightness(frame)
            face_detected, results = is_face_detected(frame)

            # 얼굴이 감지되었고 밝기가 기준 이상일 경우 → 매 프레임마다 실행
            if face_detected:
                for i, detection in enumerate(results.detections):

                                        # 바운딩 박스를 그릴 위치 계산
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x, y, w, h = (
                        int(bboxC.xmin * iw),
                        int(bboxC.ymin * ih),
                        int(bboxC.width * iw),
                        int(bboxC.height * ih),
                    )

                    if i in latest_emotion_results:
                        emotion_text, prob, _ = latest_emotion_results[i]
                        cv2.putText(
                            frame,
                            f'{emotion_text} ({prob:.2f})',
                            (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0, 255, 0),
                            2
                        )

                    # 바운딩 박스는 항상 표시 (감정 분석 여부와 관계없이)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    
                    if brightness < BRIGHTNESS_THRESHOLD:
                        print(f"[ERROR] 밝기 부족: {brightness:.2f}")

                    else:
                        # 감정 분석 1초마다 한 번만 수행
                        if current_time - last_analysis_time > analysis_interval:
                            try:
                                face = frame[y:y+h, x:x+w]
                                face = cv2.resize(face, (224, 224))
                                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                                face = face.astype(np.uint8)

                                prediction_result = model.predict_emotions(face, logits=False)

                                if isinstance(prediction_result, tuple) and len(prediction_result) == 2:
                                    top_emotion, probs = prediction_result
                                    prob = float(np.max(probs))
                                    label_mapped = EMOTION_MAPPING.get(top_emotion, 0)

                                    if prob > 0.4:
                                        save_emotion_to_db(user_id, label_mapped, prob)

                                        # 표정 라벨
                                        emotion_text = {
                                            0: 'Neutral',
                                            1: 'Negative',
                                            2: 'Positive'
                                        }.get(label_mapped, 'Neutral')

                                        # 해당 얼굴 인덱스에 대한 감정 분석 결과 저장
                                        latest_emotion_results[i] = (emotion_text, prob, current_time)

                            except Exception as e:
                                pass

            else:
                if current_time - last_analysis_time > analysis_interval:
                    # print("[WARNING] 얼굴이 감지되지 않음")
                    pass

            # 감정 분석 시간 갱신
            if current_time - last_analysis_time > analysis_interval:
                last_analysis_time = current_time

            cv2.imshow('Facial Emotion Analysis', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('c'):
                break

    except KeyboardInterrupt:
        print("\n[INFO] 프로그램 수동 중지됨.")

    finally:
        cap.release()
        cv2.destroyAllWindows()