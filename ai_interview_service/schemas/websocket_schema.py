from enum import Enum
from typing import Optional, Any, Dict, List
from pydantic import BaseModel


class ClientEventType(str, Enum):
    ANSWER = "ANSWER"
    SKIP = "SKIP"
    END_INTERVIEW = "END_INTERVIEW"


class ServerEventType(str, Enum):
    INIT = "INIT"
    AI_THINKING = "AI_THINKING"
    QUESTION = "QUESTION"
    REPORT = "REPORT"
    ERROR = "ERROR"


class ClientMessage(BaseModel):
    type: ClientEventType
    answer: Optional[str] = None


class QuestionPayload(BaseModel):
    question: str
    is_follow_up: bool
    follow_up_num: int
    base_num: int
    total_base: int


class ServerMessage(BaseModel):
    type: ServerEventType
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
