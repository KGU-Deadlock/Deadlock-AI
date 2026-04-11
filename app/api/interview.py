import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.interview_schemas import (
    FeedbackResponse,
    InterviewInitRequest,
    InterviewInitResponse,
    SessionExportResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services.interview_service import SESSION_DIR, interview_service

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/init", response_model=InterviewInitResponse, summary="[기능 01] 면접 세션 초기화")
async def init_interview(request: InterviewInitRequest):
    """
    사용자 정보를 입력받아 면접 세션을 초기화하고 첫 번째 질문을 반환합니다.

    - **name**: 사용자 이름(ID)
    - **level**: 숙련도 (신입 / 주니어 / 시니어)
    - **domain**: 도메인 (AI / Back / Front)
    - **total_rounds**: 총 진행 라운드 수
    """
    try:
        result = interview_service.init_session(
            name=request.name,
            level=request.level,
            domain=request.domain,
            total_rounds=request.total_rounds,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return InterviewInitResponse(
        session_id=result["session_id"],
        message=f"안녕하세요, {request.name}님! {request.domain} 도메인 {request.level} 면접을 시작합니다. 총 {request.total_rounds}라운드 진행됩니다.",
        first_question=result["first_question"],
        current_round=1,
        total_rounds=request.total_rounds,
    )


@router.post("/answer", response_model=SubmitAnswerResponse, summary="[기능 02/03] 답변 제출 및 다음 질문 수신")
async def submit_answer(request: SubmitAnswerRequest):
    """
    현재 라운드의 답변을 제출합니다.
    모든 라운드가 완료되면 `is_complete: true`를 반환합니다.

    - **session_id**: 초기화 시 발급된 세션 ID
    - **answer**: 사용자 답변 텍스트
    """
    try:
        result = interview_service.submit_answer(
            session_id=request.session_id,
            answer=request.answer,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if result["is_complete"]:
        message = f"모든 라운드가 완료되었습니다! /interview/feedback/{request.session_id} 에서 종합 피드백을 확인하세요."
    else:
        message = f"Round {result['round_completed']} 완료! 다음 질문입니다. (Round {result['current_round']})"

    return SubmitAnswerResponse(
        round_completed=result["round_completed"],
        next_question=result["next_question"],
        current_round=result["current_round"],
        is_complete=result["is_complete"],
        message=message,
    )


@router.get("/feedback/{session_id}", response_model=FeedbackResponse, summary="[기능 04] 종합 피드백 조회")
async def get_feedback(session_id: str):
    """
    모든 라운드가 완료된 세션의 종합 피드백을 반환합니다.

    - **total_score**: 종합 점수 (0~100)
    - **strengths**: 강점 분석
    - **weaknesses**: 약점 분석
    - **recommended_keywords**: 추천 학습 키워드
    """
    try:
        return interview_service.get_feedback(session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{session_id}", response_model=SessionExportResponse, summary="[기능 05] 세션 JSON 데이터 조회")
async def export_session(session_id: str):
    """
    전체 면접 세션 데이터를 JSON 형식으로 반환합니다.
    서버의 `interview_sessions/` 디렉토리에도 파일로 저장됩니다.
    """
    try:
        return interview_service.export_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{session_id}/file", summary="[기능 05] 세션 JSON 파일 다운로드")
async def download_session_file(session_id: str):
    """
    저장된 면접 세션 JSON 파일을 직접 다운로드합니다.
    """
    # export_session을 먼저 호출해서 파일을 최신 상태로 갱신
    try:
        interview_service.export_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    file_path = os.path.join(SESSION_DIR, f"{session_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

    return FileResponse(
        path=file_path,
        media_type="application/json",
        filename=f"interview_{session_id}.json",
    )
