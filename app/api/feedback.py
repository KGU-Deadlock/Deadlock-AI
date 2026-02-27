from fastapi import APIRouter, Depends, HTTPException
from app.services.ai_service import AIService
from app.models.schemas import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

ai_service_instance = AIService()

@router.post("/evaluate", response_model=FeedbackResponse)
async def evaluate_answer(request: FeedbackRequest):
    try:
        result = await ai_service_instance.get_feedback(
            request.question, 
            request.user_answer, 
            request.model_answer
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="AI 피드백 생성 중 오류가 발생했습니다.")
