import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime
from db.session import Base


class InterviewSessionDB(Base):
    __tablename__ = "interview_sessions"

    session_id = Column(String(64), primary_key=True, index=True)
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=False)
    candidate_name = Column(String(255), default="Candidate")
    candidate_email = Column(String(255), nullable=True)
    resume_text = Column(Text, nullable=True)
    github_url = Column(String(500), nullable=True)
    github_context = Column(Text, nullable=True)

    # JSON-serialized fields
    questions_json = Column(Text, default="[]")  # List of base questions
    answers_json = Column(Text, default="[]")    # List of Answer dicts
    report_json = Column(Text, nullable=True)     # Final evaluation report dict

    intro_text = Column(Text, default="")
    status = Column(String(50), default="CREATED")  # CREATED, IN_PROGRESS, COMPLETED

    # Dynamic state machine progress
    current_base_idx = Column(Integer, default=0)
    follow_up_count = Column(Integer, default=0)
    max_follow_ups = Column(Integer, default=2)
    current_question_text = Column(Text, default="")
    is_current_follow_up = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Helper properties for JSON serialization
    @property
    def questions(self) -> List[str]:
        try:
            return json.loads(self.questions_json or "[]")
        except Exception:
            return []

    @questions.setter
    def questions(self, value: List[str]):
        self.questions_json = json.dumps(value or [])

    @property
    def answers(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.answers_json or "[]")
        except Exception:
            return []

    @answers.setter
    def answers(self, value: List[Dict[str, Any]]):
        self.answers_json = json.dumps(value or [])

    @property
    def report(self) -> Optional[Dict[str, Any]]:
        if not self.report_json:
            return None
        try:
            return json.loads(self.report_json)
        except Exception:
            return None

    @report.setter
    def report(self, value: Optional[Dict[str, Any]]):
        self.report_json = json.dumps(value) if value else None

    @property
    def introText(self) -> str:
        return self.intro_text or ""

    @introText.setter
    def introText(self, value: str):
        self.intro_text = value or ""

