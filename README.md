# Deadlock-AI

듀오링고 CS 버전을 위한 AI 엔진 서비스

## 프로젝트 개요

Deadlock-AI는 컴퓨터 과학(CS) 학습을 위한 듀오링고 스타일 플랫폼의 AI 파트입니다. 
현재 STT(Speech-to-Text) 기능을 제공하며, 향후 퀴즈 해결 및 AI 피드백 기능이 추가될 예정입니다.

## 주요 기능

### ✅ STT (Speech-to-Text)
- OpenAI Whisper API를 활용한 음성 인식
- 클라우드 기반으로 로컬 모델 설치 불필요
- 다국어 지원 (한국어, 영어 등)
- 다양한 오디오 포맷 지원 (WAV, MP3, M4A, OGG, FLAC)
- RESTful API 제공

### 🚧 개발 예정
- 퀴즈 해결 데이터 처리
- AI 피드백 생성

## 기술 스택

- **Framework**: FastAPI
- **STT Model**: OpenAI Whisper API
- **Python**: 3.8+
- **Server**: Uvicorn

## 프로젝트 구조

```
Deadlock-AI/
├── app/
│   ├── api/              # API 엔드포인트
│   │   └── stt.py        # STT API
│   ├── services/         # 비즈니스 로직
│   │   └── stt_service.py
│   ├── models/           # 데이터 모델
│   │   └── schemas.py
│   ├── config.py         # 설정 파일
│   └── main.py           # 애플리케이션 진입점
├── tests/                # 테스트 코드
├── uploads/              # 임시 파일 업로드 디렉토리
├── requirements.txt      # 의존성 패키지
├── .env.example          # 환경 변수 예시
└── README.md
```

## 설치 방법

### 1. 저장소 클론

```bash
git clone <repository-url>
cd Deadlock-AI
git checkout develop  # develop 브랜치로 전환
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 OpenAI API 키를 설정하세요
```

**중요**: `.env` 파일에서 다음을 반드시 설정해야 합니다:
```bash
OPENAI_API_KEY=your-actual-openai-api-key
```

OpenAI API 키는 [OpenAI Platform](https://platform.openai.com/api-keys)에서 발급받을 수 있습니다.

## 실행 방법

### 개발 모드로 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 프로덕션 모드로 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

서버가 실행되면 다음 주소에서 접근할 수 있습니다:
- API 서버: http://localhost:8000
- API 문서 (Swagger): http://localhost:8000/docs
- API 문서 (ReDoc): http://localhost:8000/redoc

## API 사용 방법

### STT API

**엔드포인트**: `POST /api/stt/transcribe`

**요청 예시 (cURL)**:

```bash
curl -X POST "http://localhost:8000/api/stt/transcribe" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.wav" \
  -F "language=ko" \
  -F "task=transcribe"
```

**요청 파라미터**:
- `file`: 음성 파일 (필수)
- `language`: 언어 코드 (기본값: ko) - ko, en, auto 등
- `task`: transcribe(음성인식) 또는 translate(영어로 번역)

**응답 예시**:

```json
{
  "text": "안녕하세요, 컴퓨터 과학을 공부하고 있습니다.",
  "language": "ko",
  "duration": 3.5,
  "segments": [...]
}
```

### 헬스 체크

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/stt/health
```

## 테스트

```bash
pytest tests/ -v
```

## Whisper 모델

OpenAI Whisper API는 `whisper-1` 모델을 사용합니다. 이는 OpenAI가 관리하는 최신 버전으로 자동 업데이트되며, 로컬 설치나 GPU 설정이 필요하지 않습니다.

**장점**:
- 로컬 모델 다운로드 불필요 (수 GB 절약)
- GPU 없이도 빠른 처리 속도
- 자동으로 최신 버전 사용
- 서버 메모리 부담 감소

**비용**: OpenAI API 사용량에 따라 과금 (Whisper는 $0.006/분)

## 브랜치 전략

- `main`: 프로덕션 배포용 브랜치
- `develop`: 개발용 메인 브랜치 (현재 STT 기능)
- `feature/*`: 개별 기능 개발 브랜치

## 팀 협업

- **프론트엔드**: 웹 UI 개발
- **백엔드**: API 및 비즈니스 로직
- **클라우드**: 인프라 및 배포
- **AI**: STT, 퀴즈 처리, 피드백 생성 (현재 저장소)

## 라이선스

MIT License

## 기여 방법

1. 이 저장소를 Fork합니다
2. 새 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.
