import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.models import InterviewSessionDB


def get_db_session() -> Session:
    """Helper to acquire a standalone DB session when not inside a FastAPI route dependency."""
    return SessionLocal()


def create_session(
    job_title: str = "General",
    job_description: str = "",
    resume_text: str = "",
    candidate_name: str = "Candidate",
    candidate_email: Optional[str] = None,
    github_url: Optional[str] = None,
    github_context: Optional[str] = None,
    questions: Optional[List[str]] = None,
    intro_text: str = "",
    recruiter_id: Optional[str] = None,
    db: Optional[Session] = None,
) -> InterviewSessionDB:
    """Creates and persists an interview session in the database."""
    session_id = str(uuid.uuid4())
    close_db = False
    if db is None:
        db = get_db_session()
        close_db = True

    try:
        new_session = InterviewSessionDB(
            session_id=session_id,
            job_title=job_title,
            job_description=job_description,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            resume_text=resume_text,
            github_url=github_url,
            github_context=github_context,
            recruiter_id=recruiter_id,
            intro_text=intro_text,
            status="CREATED",
        )
        new_session.questions = questions or []
        new_session.answers = []

        if new_session.questions:
            new_session.current_question_text = new_session.questions[0]

        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session
    finally:
        if close_db:
            db.close()


def get_session(session_id: str, db: Optional[Session] = None) -> Optional[InterviewSessionDB]:
    """Fetches an interview session by session_id from the database."""
    close_db = False
    if db is None:
        db = get_db_session()
        close_db = True

    try:
        return db.query(InterviewSessionDB).filter(InterviewSessionDB.session_id == session_id).first()
    finally:
        if close_db:
            db.close()


def list_sessions(recruiter_id: Optional[str] = None, db: Optional[Session] = None) -> List[InterviewSessionDB]:
    """Fetches all interview sessions for the recruiter dashboard."""
    close_db = False
    if db is None:
        db = get_db_session()
        close_db = True

    try:
        query = db.query(InterviewSessionDB)
        if recruiter_id:
            query = query.filter(
                (InterviewSessionDB.recruiter_id == recruiter_id) |
                (InterviewSessionDB.recruiter_id.is_(None))
            )
        return query.order_by(InterviewSessionDB.created_at.desc()).all()
    finally:
        if close_db:
            db.close()


def update_session(session_obj: InterviewSessionDB, db: Optional[Session] = None):
    """Commits updates to an existing session in the database."""
    close_db = False
    if db is None:
        db = get_db_session()
        close_db = True

    try:
        db.merge(session_obj)
        db.commit()
    finally:
        if close_db:
            db.close()


def save_answer(answer: Optional[str], skip: bool, session: InterviewSessionDB, db: Optional[Session] = None):
    """Saves answer for legacy HTTP /submit endpoint and commits to database."""
    answers = session.answers
    answers.append({
        "question": session.current_question_text or (session.questions[session.current_base_idx] if session.questions else ""),
        "answer": None if skip else answer,
        "skip": skip,
        "is_follow_up": False,
        "follow_up_num": 0
    })
    session.answers = answers
    session.current_base_idx += 1
    if session.current_base_idx >= len(session.questions):
        session.status = "COMPLETED"
    else:
        session.current_question_text = session.questions[session.current_base_idx]
    update_session(session, db)