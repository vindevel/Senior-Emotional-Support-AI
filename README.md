# Senior-Emotional-Support-AI (안녕, 보리야!)

> **AI-based Conversational Emotional Support System for Seniors Living Alone**
> 독거노인의 정서적 고립 해소를 위한 멀티모달(음성+표정) 감정 케어 및 생활 지원 시스템

**🏆 2025 참빛설계학기 성과발표회 최우수상 수상작**

[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18.0-61DAFB?logo=react)](https://reactjs.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql)](https://www.mysql.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-1.13-EE4C2C?logo=pytorch)](https://pytorch.org/)

<br>

## Introduction
한국의 독거노인 수는 급격히 증가하고 있으며, 이에 따른 정서적 고립과 우울감은 심각한 사회 문제입니다.
**'안녕, 보리야!'** 는 단순한 알림 기능을 넘어, **사용자의 표정과 음성을 실시간으로 분석**하여 정서 상태를 파악하고, 이에 맞는 **공감형 대화와 맞춤형 콘텐츠**를 제공하는 반려 AI 파트너입니다.

<br>

## Key Features
* **🗣️ 멀티모달 감정 분석 (Multimodal Emotion Analysis):**
    * **음성:** KoBERT 기반 2단계(3중/5중) 감정 분류
    * **표정:** Mediapipe & HSEmotion(EfficientNet-B0) 기반 실시간 표정 인식
* **💬 공감형 대화 생성 (Empathetic Chatbot):**
    * 사용자의 감정에 맞춰 위로와 공감을 건네는 KoGPT2 기반 생성형 챗봇
* **📊 심리 분석 리포트 (Psychological Report):**
    * 일간/주간 감정 변화 추이를 시각화(Chart.js)하여 제공.
    * 2주 이상 부정 감정 지속 시 보호자에게 알림
* **💊 생활 밀착형 케어 (Life Care):**
    * 복약 알림, 일정 관리, 식사 알림 기능.
    * 우울/불안 감지 시 클래식 음악 및 시 낭독 서비스 자동 제공

<br>

## System Architecture
<img width="850" height="307" alt="image" src="https://github.com/user-attachments/assets/f2e4315b-9dd5-4995-93ab-e720a6bd7c47" />

### Tech Stack
* **Frontend:** React, TailwindCSS, Chart.js
* **Backend:** Flask (RESTful API), Python
* **Database:** MySQL 
* **AI & ML:**
    * **STT:** OpenAI Whisper (Medium)
    * **NLP:** KoBERT (Emotion Classification), KoGPT2 (Chat Generation)
    * **Vision:** Mediapipe, HSEmotion (Face Analysis)

<br>

## My Contribution
**Role: Backend & AI Logic Developer**
팀장으로서 프로젝트의 전체적인 방향성을 설정하고 일정을 관리하였으며 AI 모델 파이프라인 구축 및 백엔드 아키텍처 설계 역할을 맡았습니다.

### AI Pipeline & Model Selection
* **표정 분석 모델:** HSEmotion 기반 표정 분석 모델 평가를 위한 데이터셋 구성 및 전처리, 성능 테스트를 통한 최종 모델 선정
* **음성 인식 및 대화 제어:** Whisper 모델 기반 STT(Speech-to-Text) 기능 구현 및 대화 지속 구조 설계, "그만", "멈춰" 등 대화 종료 명령어 인식 로직 개발.

### Backend Architecture & Database
* **Database Schema Design:** 사용자, 감정 로그, 스케줄 관리를 위한 효율적인 **MySQL 데이터베이스 스키마 설계 및 구축**
* **Real-time Data Pipeline:** 표정 기반 감정 분석 결과를 실시간으로 DB에 적재하는 **데이터 로깅 로직 구현**
* **Scheduled Data Aggregation:** 매일 자정 감정 데이터를 집계하여 일간 평균을 저장하는 **스케줄링 및 배치 처리 로직 개발**
* **System Modularization:** 초기 통합되어 있던 자연어 처리(NLP)와 컴퓨터 비전(CV) 로직을 기능별로 **모듈화**하여 코드 유지보수성과 확장성 확보.
* **RESTful API Development:** Flask를 사용하여 심리 분석 리포트 데이터 및 AI 추론 결과를 제공하는 **RESTful API** 설계 및 구현.

### Key Feature Implementation
* **Life Care System:** 복약 알림 및 일정 관리 기능의 설계 및 스케줄러 연동.
* **Emotion-based Content:** 사용자 감정 상태와 시간대를 분석하여 맞춤형 콘텐츠(시, 클래식 음악)를 자동으로 제공하는 알고리즘 구현.
* **Data Visualization:** 사용자 발화 데이터를 분석하여 단어 빈도수 기반의 **Word Cloud 시각화** 기능 개발.

<br>

## AI Model Performance
* **Emotion Classification (KoBERT):** Accuracy **0.84** (3-class), ** Accuracy **0.78** (5-class)
* **Chat Generation (KoGPT2):** Perplexity **2.75**, Accuracy 0.77 (Fine-tuned on Wellness data)
* **Face Analysis (HSEmotion):** F1-score **0.89** - CPU 실시간 처리 최적화

<br>

## Troubleshooting & 회고

### Technical Troubleshooting

#### 1. 심리 분석 리포트 데이터 불일치 해결
* **Issue:** 심리 분석 리포트 생성 시, 감정 데이터 집계가 완료되기 전에 API가 호출되어 결과가 `NULL` 또는 `0%`로 출력되는 **Race Condition**이 발생했습니다. 또한, DB 조회 시 타임존 차이로 인해 사용자 요청 날짜와 데이터 적재 날짜가 불일치하는 문제가 있었습니다.
* **Solution:**
    * 데이터 집계가 완벽히 끝난 후 리포트 생성 로직이 실행되도록 **비동기 처리 순서를 동기적으로 제어**했습니다.
    * 사용자 ID와 날짜가 정확히 매핑되도록 SQL 쿼리 구조를 수정하고, 데이터가 없을 경우에 대한 **예외 처리**를 추가하여 시스템 안정성을 확보했습니다.

#### 2. 한글 출력 공백 문제
* **Issue:** 'users' 테이블 조회 시 '사용자'가 '사 용자'처럼 공백이 포함되어 출력되는 현상이 발생했습니다.
* **Solution:**
    * MySQL 내 `HEX()`, `LENGTH()` 함수를 사용하여 데이터 무결성을 검증했으나 이상이 없음을 확인했습니다.
    * Python의 `print(dict)` 출력 시 한글(가변폭 문자) 정렬 과정에서 시각적 공백이 발생함을 파악했습니다.
    * 디버깅 시 단순 출력이 아닌 **f-string 포맷팅**을 적용하여 데이터를 명시적으로 직렬화함으로써 문제를 해결하고 데이터 가독성을 높였습니다.

---

### 회고

#### 1. 모듈 구조
기능 구현에 집중하다 보니 초기에 최종 결과물의 범위와 구성을 명확히 정의하지 못해 개발 과정에서 감정 기반 콘텐츠 제공, WordCloud 등 기능이 추가될수록 코드가 비대해지는 **코드 구조의 한계**를 경험했습니다. 이를 해결하기 위해 **자연어 처리(NLP), 컴퓨터 비전(Vision), 백엔드 로직을 기능별로 모듈화**하여 유지보수성과 협업 효율을 개선했습니다.

#### 2. 개발자로서의 성장
백엔드뿐만 아니라 **프론트엔드 연동 및 자연어 처리 로직**까지 직접 다루며 시스템의 End-to-End 흐름을 깊이 있게 이해할 수 있었습니다. 익숙하지 않은 영역에 도전하여 기술적 시야를 넓히고 문제를 주도적으로 해결하는 과정에서 개발자로서 한 단계 성장했습니다.

#### 3. 향후 개선 계획
이번 프로젝트를 통해 **초기 요구사항 정의**와 **협업 환경 구축**의 중요성을 느꼈습니다. 다음 프로젝트에서는 기획 단계에서 기능 명세를 명확히 하고, GitHub Issue/Project 기능을 적극 활용하고자 합니다.

<br>

## Directory Structure
```text
Senior-Emotional-Support-AI/
├── docs/                        # 시스템 설계 및 구현 보고서 (시연 사진 포함)
├── project/
│   └── module/
│       ├── audio/               # 음성 인식(STT) 및 합성(TTS) 모듈
│       │   ├── stt.py           # Whisper 모델 기반 STT 로직
│       │   ├── tts.py           # 텍스트-음성 변환
│       │   ├── wakeword.py      # 호출어("보리야") 감지 (Porcupine)
│       │   ├── recorder.py      # 마이크 입력 및 녹음 처리
│       │   └── remote_wakeword.py # 원격 호출 처리 로직
│       ├── db/                  # 데이터베이스 연결 및 관리
│       │   ├── database_connect.py # MySQL Connection
│       │   ├── emotion_logger.py   # 실시간 감정 데이터 로깅
│       │   ├── avg_daily.py        # 일간 감정 통계 집계
│       │   └── user.py             # 사용자 정보
│       ├── face/                # 표정 인식 모듈
│       │   ├── HSEmotion.py     
│       │   └── run_emotion_detection.py 
│       ├── mental-report/       # React Frontend Application
│       │   ├── public/
│       │   ├── src/             # 리포트 UI 소스 코드
│       │   ├── package.json     
│       │   └── start_app.bat    # 리포트 실행 스크립트
│       ├── routes/              # Flask RESTful API 라우팅
│       │   ├── conversation.py  
│       │   ├── face.py          
│       │   └── user.py          
│       ├── schedule/            # 생활 관리 및 스케줄러
│       │   ├── general_schedule_data/  # 일반 일정 데이터 (JSON)
│       │   ├── medication_schedules_json/ # 복약 일정 데이터 (JSON)
│       │   ├── emotion_recommendation.py # 감정 기반 콘텐츠(시/음악) 추천
│       │   ├── medication_schedule.py    # 복약 알림 로직
│       │   ├── notifier.py               # 알림 모듈
│       │   └── night_talk.py             # 심야 시간 대화 제어
│       ├── utils/               # 유틸리티 및 설정
│       │   ├── colab_api.py     # Colab GPU 서버 연동 유틸
│       │   └── exit_handler.py  # 프로그램 종료 처리
│       ├── main.py              # 메인 실행 파일 (Application Entry Point)
│       ├── report_api.py        # 리포트 API 서버 실행
│       ├── NLP_module_flask.ipynb # AI 모델 실행 환경 노트북
│       ├── porcupine_params_ko.pv # Wake-word 모델 파라미터
│       ├── stopwords-ko.txt       # 불용어 사전
│       └── PRETENDARD-REGULAR.TTF # 폰트 파일
├── .gitignore                   # Git 제외 파일 목록
└── README.md                    # 프로젝트 문서
```

<br>

## Resources
* **Project Report:** [시스템 설계 및 구현 보고서 (PDF)] -> docs 디렉토리 안에 첨부되어 있습니다.
* **Model Weights:** 용량 제한으로 인해 학습된 모델 가중치 파일은 포함되어 있지 않습니다. 상세한 학습 과정은 보고서를 참고해 주세요.
* 각종 출처는 시스템 설계 및 구현 보고서 마지막 페이지에 기재되어 있습니다.
---
© 2025. Team Annyeong-Bori. All rights reserved.
