from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import os
import uuid
from pathlib import Path

from app.models.schemas import STTResponse, ErrorResponse
from app.services.stt_service import stt_service
from app.config import settings

router = APIRouter(prefix="/api/stt", tags=["STT"])

# 음성 파일을 텍스트로 변환하는 엔드포인트
@router.post("/transcribe", response_model=STTResponse)
async def transcribe_audio(
    file: UploadFile = File(..., description="음성 파일 (wav, mp3, m4a, ogg, flac)"),
    language: Optional[str] = Form("ko", description="언어 코드 (ko, en, auto 등)"),
    task: Optional[str] = Form("transcribe", description="transcribe 또는 translate")
):
    """
    음성 파일을 텍스트로 변환하는 STT API
    
    - **file**: 음성 파일 (최대 25MB)
    - **language**: 언어 코드 (기본값: ko)
    - **task**: transcribe(음성인식) 또는 translate(영어로 번역)
    """
    
    # 파일 검증
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # 임시 파일 저장
    file_id = str(uuid.uuid4())
    temp_file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_ext}")
    
    try:
        # 파일 저장
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        with open(temp_file_path, "wb") as f:
            f.write(content)
        
        # STT 처리
        result = await stt_service.transcribe_audio(
            file_path=temp_file_path,
            language=language,
            task=task
        )
        
        return STTResponse(
            text=result["text"],
            language=result["language"],
            duration=result.get("duration"),
            segments=result.get("segments")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT processing failed: {str(e)}")
    
    finally:
        # 임시 파일 삭제
        stt_service.cleanup_file(temp_file_path)


@router.get("/health")
async def health_check():
    """STT 서비스 헬스 체크"""
    return {
        "status": "healthy",
        "service": "STT",
        "model": settings.WHISPER_MODEL,
        "device": settings.WHISPER_DEVICE
    }
