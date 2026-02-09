from fastapi import APIRouter, Depends
from app.services.ai_service import AIService
from app.models.schemas import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

@router.post("/evaluate", response_model=FeedbackResponse)
async def evaluate_answer(request: FeedbackRequest, ai_service: AIService = Depends()):
    # AI 엔진 실행
    result = await ai_service.get_feedback(
        request.question, 
        request.user_answer, 
        request.model_answer
    )
    return result
