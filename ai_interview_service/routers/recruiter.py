from typing import Optional, List
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends, status
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import InterviewSessionDB
from services.ai_service import generate_questions_intro
from services.interview_service import create_session, get_session, list_sessions
from util.file_util import extract_text, validate_file

from services.github_service import fetch_github_context
from services.email_service import send_invitation_email, send_report_email

router = APIRouter(
    prefix="/recruiter",
    tags=["Recruiter"]
)


@router.post("/create-interview")
async def create_candidate_interview(
    job_title: str = Form(...),
    job_description: str = Form(...),
    candidate_name: Optional[str] = Form("Candidate"),
    candidate_email: Optional[str] = Form(None),
    github_url: Optional[str] = Form(None),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Recruiter endpoint to upload Job Description + Candidate Resume + Optional GitHub URL.
    Pre-generates role-tailored interview questions and creates a persistent interview link.
    """
    # 1. Validate and extract text from resume PDF
    await validate_file(resume)
    resume_text = await extract_text(resume)

    # 2. Fetch GitHub repository context if provided
    github_context = None
    if github_url and github_url.strip():
        github_context = fetch_github_context(
            github_url=github_url.strip(),
            job_description=job_description,
            job_title=job_title
        )

    # 3. AI generates base questions and personalized intro text
    ai_gen = await generate_questions_intro(
        job_title=job_title,
        job_description=job_description,
        resume_text=resume_text,
        github_url=github_url,
        github_context=github_context
    )

    detected_name = ai_gen.get("candidate_name")
    final_name = candidate_name if candidate_name and candidate_name != "Candidate" else (detected_name or "Candidate")

    # 4. Persist session to SQLite database
    new_session = create_session(
        job_title=job_title,
        job_description=job_description,
        resume_text=resume_text,
        candidate_name=final_name,
        candidate_email=candidate_email,
        github_url=github_url,
        github_context=github_context,
        questions=ai_gen.get("questions", []),
        intro_text=ai_gen.get("introText", ""),
        db=db
    )

    candidate_url = f"/candidate/{new_session.session_id}"

    # 5. Automatically send invitation email if candidate email was provided
    email_sent = False
    if candidate_email and "@" in candidate_email:
        email_sent = send_invitation_email(
            to_email=candidate_email,
            candidate_name=final_name,
            job_title=job_title,
            session_id=new_session.session_id
        )

    return {
        "session_id": new_session.session_id,
        "candidate_name": new_session.candidate_name,
        "candidate_email": new_session.candidate_email,
        "job_title": new_session.job_title,
        "github_url": new_session.github_url,
        "candidate_url": candidate_url,
        "questions": new_session.questions,
        "status": new_session.status,
        "email_sent": email_sent
    }


@router.get("/interviews")
def list_all_interviews(db: Session = Depends(get_db)):
    """Fetches all interview sessions for the recruiter dashboard."""
    sessions = list_sessions(db)
    return [
        {
            "session_id": s.session_id,
            "candidate_name": s.candidate_name,
            "candidate_email": s.candidate_email,
            "job_title": s.job_title,
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "total_questions": len(s.questions),
            "score": s.report.get("score") if s.report else None,
            "has_report": s.report is not None
        }
        for s in sessions
    ]


@router.get("/interview/{session_id}")
def get_interview_detail(session_id: str, db: Session = Depends(get_db)):
    """Fetches full details and graded report of a specific candidate interview."""
    session_obj = get_session(session_id, db)
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found."
        )

    return {
        "session_id": session_obj.session_id,
        "candidate_name": session_obj.candidate_name,
        "candidate_email": session_obj.candidate_email,
        "job_title": session_obj.job_title,
        "job_description": session_obj.job_description,
        "github_url": session_obj.github_url,
        "status": session_obj.status,
        "created_at": session_obj.created_at.isoformat() if session_obj.created_at else None,
        "questions": session_obj.questions,
        "answers": session_obj.answers,
        "report": session_obj.report
    }


@router.post("/send-invite/{session_id}")
def resend_candidate_invite(session_id: str, db: Session = Depends(get_db)):
    """Manually resends or sends the candidate interview invitation email."""
    session_obj = get_session(session_id, db)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    if not session_obj.candidate_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Candidate has no email address configured.")

    sent = send_invitation_email(
        to_email=session_obj.candidate_email,
        candidate_name=session_obj.candidate_name,
        job_title=session_obj.job_title,
        session_id=session_obj.session_id
    )
    return {"success": sent, "message": "Invitation email sent successfully!" if sent else "Failed to send email. Check SMTP credentials."}


@router.post("/send-report/{session_id}")
def email_candidate_report(session_id: str, db: Session = Depends(get_db)):
    """Emails the final evaluation report to the candidate."""
    session_obj = get_session(session_id, db)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    if not session_obj.candidate_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Candidate has no email address configured.")
    if not session_obj.report:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Interview does not have a completed report yet.")

    sent = send_report_email(
        to_email=session_obj.candidate_email,
        candidate_name=session_obj.candidate_name,
        job_title=session_obj.job_title,
        report=session_obj.report
    )
    return {"success": sent, "message": "Assessment report emailed successfully!" if sent else "Failed to send email. Check SMTP credentials."}

