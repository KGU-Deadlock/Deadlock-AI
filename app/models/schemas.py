from pydantic import BaseModel
from typing import Optional


class STTRequest(BaseModel):
    """STT 요청 모델"""
    language: Optional[str] = "ko"  # 언어 설정 (기본값: 한국어)
    task: Optional[str] = "transcribe"  # transcribe 또는 translate


class STTResponse(BaseModel):
    """STT 응답 모델"""
    text: str
    language: str
    duration: Optional[float] = None
    segments: Optional[list] = None


class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str
    detail: Optional[str] = None
