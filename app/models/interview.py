from pydantic import BaseModel
from typing import List, Optional

class InterviewRequest(BaseModel):
    current_stage: str  # START, SELF_INTRO, TECH, SURPRISE, END
    user_answer: Optional[str] = None
    history: List[dict] = []  # [{"role": "assistant", "content": "..."}, {"role": "user", "content": "..."}]

class InterviewResponse(BaseModel):
    thought: str
    question: str
    stage: str
    is_surprise_question: bool
    message: Optional[str] = None
