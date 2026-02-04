# Senior-Emotional-Support-AI (안녕, 보리야!)

> **AI-based Conversational Emotional Support System for Seniors Living Alone** > 독거노인의 정서적 고립 해소를 위한 멀티모달(음성+표정) 감정 케어 및 생활 지원 시스템

[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18.0-61DAFB?logo=react)](https://reactjs.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql)](https://www.mysql.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-1.13-EE4C2C?logo=pytorch)](https://pytorch.org/)

## Introduction
한국의 독거노인 수는 급격히 증가하고 있으며, 이에 따른 정서적 고립과 우울감은 심각한 사회 문제입니다.
**'안녕, 보리야!'** 는 단순한 알림 기능을 넘어, **사용자의 표정과 음성을 실시간으로 분석**하여 정서 상태를 파악하고, 이에 맞는 **공감형 대화와 맞춤형 콘텐츠**를 제공하는 반려 AI 파트너입니다.

## Key Features
* **🗣️ 멀티모달 감정 분석 (Multimodal Emotion Analysis):**
    * [cite_start]**음성:** KoBERT 기반 2단계(3중/5중) 감정 분류[cite: 68].
    * [cite_start]**표정:** Mediapipe & HSEmotion(EfficientNet-B0) 기반 실시간 표정 인식[cite: 87].
* **💬 공감형 대화 생성 (Empathetic Chatbot):**
    * [cite_start]사용자의 감정에 맞춰 위로와 공감을 건네는 KoGPT2 기반 생성형 챗봇[cite: 72].
* **📊 심리 분석 리포트 (Psychological Report):**
    * 일간/주간 감정 변화 추이를 시각화(Chart.js)하여 제공.
    * [cite_start]2주 이상 부정 감정 지속 시 보호자에게 알림 발송[cite: 31, 102].
* **💊 생활 밀착형 케어 (Life Care):**
    * 복약 알림, 일정 관리, 식사 알림 기능.
    * [cite_start]우울/불안 감지 시 클래식 음악 및 시(Poem) 낭독 서비스 자동 제공[cite: 124].

## System Architecture
![System Architecture](./docs/images/architecture.png)

### Tech Stack
* [cite_start]**Frontend:** React, TailwindCSS, Chart.js [cite: 44]
* [cite_start]**Backend:** Flask (RESTful API), Python [cite: 42]
* [cite_start]**Database:** MySQL [cite: 43]
* **AI & ML:**
    * [cite_start]**STT:** OpenAI Whisper (Medium) [cite: 53]
    * [cite_start]**NLP:** KoBERT (Emotion Classification), KoGPT2 (Chat Generation) [cite: 39]
    * [cite_start]**Vision:** Mediapipe, HSEmotion (Face Analysis) [cite: 85]

## My Contribution
**Role: Backend & AI Logic Developer**

* **시스템 아키텍처 설계 및 DB 구축:**
    * 시스템 전반의 MySQL 데이터베이스 설계 및 구축 (User, Emotion Logs, Schedules 등).
    * 자연어 처리(NLP)와 컴퓨터 비전(CV) 로직을 분리하여 **모듈화(Modularization)** 진행, 유지보수성 향상.
* **AI 파이프라인 구현:**
    * **표정 분석:** HSEmotion 모델을 로컬 CPU 환경에 최적화하여 적용 및 데이터 전처리 파이프라인 구축.
    * **음성 인식:** Whisper 모델을 활용한 STT 구현 및 Wake-word/종료 명령어("그만", "멈춰") 인식 로직 개발.
* **백엔드 기능 개발:**
    * 심리 분석 리포트 생성을 위한 REST API 설계 및 구현.
    * 사용자 발화 데이터를 기반으로 한 **WordCloud 시각화** 로직 개발.
    * Python Scheduler를 이용한 복약 및 일정 알림 시스템 구현.

## AI Model Performance
* [cite_start]**Emotion Classification (KoBERT):** Accuracy **84.17%** (3-class)[cite: 170].
* [cite_start]**Chat Generation (KoGPT2):** Perplexity **2.75**, Accuracy 81.91% (Fine-tuned on Wellness data)[cite: 276, 282].
* [cite_start]**Face Analysis (HSEmotion):** F1-score **99%** (Negative Emotion) - CPU 실시간 처리 최적화[cite: 235].

## Troubleshooting & Retrospective
### 1. Monolithic to Modular Architecture
초기에는 하나의 코드 파일에 모든 기능이 섞여 있어 관리가 어려웠으나, **기능별(Vision, Voice, NLP)로 모듈화**하여 가독성과 협업 효율을 높였습니다.

### 2. Whisper Model Optimization
[cite_start]로컬 PC(CPU)에서 Whisper 모델 구동 시 지연(Latency)이 발생하여, **Google Colab GPU 서버와 Flask 연동**을 통해 실시간성을 확보했습니다[cite: 294].

## Directory Structure
Senior-Emotional-Support-AI/ ├── project/ │ └── module/ │ ├── face/ # HSEmotion Face Analysis Module │ ├── mental-report/ # React Frontend Source │ ├── routes/ # Flask API Routes │ ├── schedule/ # Scheduler Logic │ ├── utils/ # Helper Functions │ ├── db/ # Database Connection │ ├── main.py # Application Entry Point │ ├── report_api.py # Report Generation API │ └── NLP_module_flask.ipynb # AI Model Training Code ├── docs/ # Project Report & Images └── requirements.txt

## Resources
* **Project Report:** [시스템 설계 및 구현 보고서 (PDF)](./docs/System_Design_Report.pdf)
* **Model Weights:** 용량 제한으로 인해 학습된 모델 가중치 파일은 포함되어 있지 않습니다. 상세한 학습 과정은 `NLP_module_flask.ipynb`와 보고서를 참고해 주세요.

---
© 2025. Team Annyeong-Bori. All rights reserved.
