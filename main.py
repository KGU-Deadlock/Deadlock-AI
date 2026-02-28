from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.feedback import router as feedback_router

app = FastAPI(
    title="Deadlock-AI Feedback Engine",
    description="CS 학습을 위한 AI 면접관 및 피드백 서비스",
    version="1.0.0"
)

# CORS 설정 (프론트엔드 연동)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 피드백 라우터 등록
app.include_router(feedback_router)

@app.get("/")
async def root():
    return {"status": "online", "message": "Deadlock-AI 엔진 정상 작동 중"}
