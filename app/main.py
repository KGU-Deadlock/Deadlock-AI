from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import interview, feedback

app = FastAPI(
    title="Deadlock-AI Interviewer",
    description="CS 기술 면접 진행 서비스",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview.router)
app.include_router(feedback.router)


@app.get("/")
async def root():
    return {"status": "online", "message": "Deadlock-AI Interviewer 정상 작동 중"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
