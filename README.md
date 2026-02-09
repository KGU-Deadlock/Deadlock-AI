# Deadlock-AI: Feedback Engine (HelloCS)

**컴퓨터 과학(CS) 학습을 위한 AI 면접관 및 피드백 엔진** `Deadlock-AI` 프로젝트의 핵심 지능형 서비스로, 사용자의 음성 답변을 분석하여 전문적인 기술 피드백을 제공합니다.

---

## 🎯 주요 기능 (Key Features)

* **시니어 개발자 페르소나**: IT 대기업 시니어 개발자 컨셉의 전문적이고 친근한 피드백 제공 (반드시 존댓말 사용).
* **정밀 채점 시스템**: 사용자의 답변과 기술적 핵심 개념을 비교하여 0~100점 사이의 점수 산출.
* **키워드 분석**: 답변에서 누락된 핵심 CS 용어를 자동으로 추출하여 리스트화.
* **답변 교정 (Highlighting)**: `<highlight>` 태그를 활용하여 프론트엔드에서 즉시 시각화 가능한 교정 답변 생성.

---

## 🛠 기술 스택 (Tech Stack)

* **AI Model**: Google Gemini 2.0 Flash (또는 3 Flash Preview)
* **Environment**: Google AI Studio (GUI Tuning 완료)
* **Output Format**: Strict JSON Mode

---

## 🚀 API Specification (연동 가이드)

### 1. AI Feedback Evaluate
사용자의 답변을 분석하고 기술적 정확도에 따른 점수와 피드백을 반환합니다.

**Endpoint:** `POST /api/feedback/evaluate`

#### **Request Body (JSON)**
| Field | Type | Description |
| :--- | :--- | :--- |
| `question` | String | 면접 질문 내용 |
| `user_answer` | String | 사용자가 음성으로 답한 내용 (STT 결과물) |
| `model_answer` | String | (Optional) 채점 기준이 되는 모범 답안 가이드 |

#### **Response Body (JSON)**
```json
{
  "score": 85,
  "missing_keywords": ["프로세스 독립 메모리 공간", "스레드 자원 공유"],
  "improved_answer": "-> 프로세스는 <highlight>독립된 메모리 공간</highlight>을 할당받는 실행 단위이며...",
  "message": "핵심을 잘 짚으셨어요! 조금만 더 보완해 볼까요? 💪"
}
```

---

## 🎨 프론트엔드 연동 가이드 (Integration Guide)

* **동적 텍스트 렌더링**: `improved_answer` 필드 내에 포함된 `<highlight>...</highlight>` 태그를 파싱하여 특정 색상(예: Red 또는 Orange)으로 강조 표시하는 로직이 필요합니다.
* **피드백 시각화**: 응답받은 `score`와 `missing_keywords` 데이터를 활용하여 사용자의 학습 성취도를 시각적인 프로그레스 바나 리스트 형태로 표현합니다.
* **데이터 매핑**: AI 응답 객체의 각 필드를 해당 UI 컴포넌트(점수판, 피드백 박스, 응원 메시지 칸)에 자동으로 매핑하여 화면을 갱신합니다.

---

## 🔐 환경 변수 설정 (Environment Variables)

보안을 위해 API 키는 소스 코드에 직접 노출하지 않으며, `.env` 파일에 저장하여 관리합니다. 프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 아래 내용을 추가하세요.

```bash
# Google Gemini API Key
GEMINI_API_KEY=your-actual-gemini-api-key
```
