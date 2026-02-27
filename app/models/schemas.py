from pydantic import BaseModel
from typing import List, Optional

class FeedbackRequest(BaseModel):
    question: str
    user_answer: str
    model_answer: Optional[str] = None

class FeedbackResponse(BaseModel):
    score: int
    missing_keywords: List[str]
    improved_answer: str
    message: str
