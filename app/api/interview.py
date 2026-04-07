from fastapi import APIRouter, Depends
from app.services.interview_service import InterviewService
from app.models.interview import InterviewRequest, InterviewResponse

router = APIRouter(prefix="/api/interview", tags=["interview"])

@router.post("/next", response_model=InterviewResponse)
async def get_next_step(request: InterviewRequest, interview_service: InterviewService = Depends()):
    # 면접관 AI에게 다음 질문 요청
    result = await interview_service.generate_question(
        current_stage=request.current_stage,
        user_answer=request.user_answer,
        history=request.history
    )
    return result
