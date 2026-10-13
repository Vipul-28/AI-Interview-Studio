from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from db.session import get_db
from services.interview_service import get_session

router = APIRouter(
    prefix="/candidate",
    tags=["Candidate"]
)


@router.get("/session/{session_id}")
def get_candidate_session_info(session_id: str, db: Session = Depends(get_db)):
    """
    Public candidate endpoint that returns only invitation information
    without exposing recruiter-sensitive internal prompts.
    """
    session_obj = get_session(session_id, db)
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview invitation not found. Please check your invitation link."
        )

    return {
        "session_id": session_obj.session_id,
        "candidate_name": session_obj.candidate_name,
        "job_title": session_obj.job_title,
        "github_url": session_obj.github_url,
        "status": session_obj.status,
        "intro_text": session_obj.intro_text,
        "has_completed": session_obj.status == "COMPLETED"
    }
