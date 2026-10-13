from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class InteriewStatusEnum(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Answer(BaseModel):
    question: str
    answer: Optional[str] = None
    skip: bool = False
    is_follow_up: bool = False
    follow_up_num: int = 0


class InterviewSession(BaseModel):
    session_id: str
    questions: List[str] = []  # List of N base questions
    status: InteriewStatusEnum = InteriewStatusEnum.IN_PROGRESS
    answers: List[Answer] = []
    current_base_idx: int = 0  # Index into questions list
    follow_up_count: int = 0  # 0 = base question, 1 = follow-up 1, 2 = follow-up 2
    max_follow_ups: int = 2   # Configurable ceiling per base question
    current_question_text: str = ""
    is_current_follow_up: bool = False
    introText: str = ""