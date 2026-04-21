from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class Level(str, Enum):
    NEW = "신입"
    JUNIOR = "주니어"
    SENIOR = "시니어"


class Domain(str, Enum):
    AI = "AI"
    BACKEND = "Back"
    FRONTEND = "Front"


# ── 요청 모델 ──────────────────────────────────────────────────────────────────

class InterviewInitRequest(BaseModel):
    """[기능 01] 면접 세션 초기화 요청"""
    name: str
    level: Level
    domain: Domain
    total_rounds: int


class SubmitAnswerRequest(BaseModel):
    """[기능 02] 답변 제출 요청"""
    session_id: str
    answer: str


# ── 응답 모델 ──────────────────────────────────────────────────────────────────

class InterviewInitResponse(BaseModel):
    """[기능 01] 면접 세션 초기화 응답"""
    session_id: str
    message: str
    first_question: str
    current_round: int
    total_rounds: int


class SubmitAnswerResponse(BaseModel):
    """[기능 02] 답변 제출 응답"""
    round_completed: int
    next_question: Optional[str] = None
    current_round: Optional[int] = None
    is_complete: bool
    message: str
    quality_score: Optional[int] = None          # 1~5, 이번 라운드 답변 품질
    adjusted_total_rounds: Optional[int] = None  # 라운드 조정 발생 시 새 총 라운드 수


class QARecord(BaseModel):
    """[기능 03] 단일 문답 기록"""
    round: int
    topic: str
    question: str
    answer: str
    quality_score: Optional[int] = None  # AI 평가 점수 1~5


# ── 피드백 세부 모델 ───────────────────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    """5개 평가 항목별 세부 점수"""
    logical_structure: int   # 논리적 답변 구조  (만점 20)
    technical_accuracy: int  # 기술적 정확성     (만점 25)
    concreteness: int        # 구체성·사례 제시  (만점 20)
    communication: int       # 전달력·명확성     (만점 15)
    depth: int               # 지식의 깊이       (만점 20)


class RoundFeedback(BaseModel):
    """라운드별 한 줄 코멘트"""
    round: int
    comment: str


class FeedbackResponse(BaseModel):
    """[기능 04] 종합 피드백"""
    session_id: str
    user_name: str
    total_score: int                         # 0 ~ 100
    score_breakdown: ScoreBreakdown          # 항목별 세부 점수
    per_round_feedback: List[RoundFeedback]  # 라운드별 코멘트
    strengths: str
    weaknesses: str
    recommended_keywords: List[str]


class SessionExportResponse(BaseModel):
    """[기능 05] 전체 세션 데이터 (파일 출력용)"""
    session_id: str
    user_name: str
    level: str
    domain: str
    total_rounds: int
    interview_history: List[QARecord]
    feedback: Optional[FeedbackResponse] = None


# ── OpenAI 응답 파싱용 내부 모델 ───────────────────────────────────────────────

class AIQuestion(BaseModel):
    """AI가 반환하는 질문 JSON 구조"""
    topic: str
    question: str


class AIAnswerScore(BaseModel):
    """AI가 반환하는 답변 품질 평가 JSON 구조"""
    score: int    # 1~5
    reason: str   # 간단한 평가 근거


class AIFeedback(BaseModel):
    """AI가 반환하는 피드백 JSON 구조"""
    total_score: int
    score_breakdown: ScoreBreakdown
    per_round_feedback: List[RoundFeedback]
    strengths: str
    weaknesses: str
    recommended_keywords: List[str]
