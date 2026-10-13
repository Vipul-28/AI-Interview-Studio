from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from models.interview import InteriewStatusEnum
from request_model.AnswerRequest import AnswerRequest
from response_model.AnswerResponse import AnswerResponse
from services.ai_service import generate_questions_intro, generate_report
from services.interview_service import create_session, get_session, save_answer
from util.file_util import extract_text, validate_file

from typing import Optional
from services.github_service import fetch_github_context

router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)

@router.post("/generate-question")
async def generate_questions(
    job_title: str = Form(...),
    job_description: str = Form(...),
    resume: UploadFile = File(...),
    github_url: Optional[str] = Form(None)
):
    # Validate resume file
    await validate_file(resume)

    # Extract text from resume
    resume_text = await extract_text(resume)

    # Fetch GitHub context if provided
    github_context = None
    if github_url and github_url.strip():
        github_context = fetch_github_context(
            github_url=github_url.strip(),
            job_description=job_description,
            job_title=job_title
        )

    # Generate questions and intro text using title, description, resume, and GitHub context
    resp = await generate_questions_intro(
        job_title=job_title,
        job_description=job_description,
        resume_text=resume_text,
        github_url=github_url,
        github_context=github_context
    )

    session = create_session(
        job_title=job_title,
        job_description=job_description,
        resume_text=resume_text,
        github_url=github_url,
        github_context=github_context,
        questions=resp.get("questions", []),
        intro_text=resp.get("introText", "")
    )

    return { "session_id": session.session_id }



@router.get("/start/{session_id}")
async def start_interview(session_id: str):
    # Check valid session_id
    session = get_session(session_id)
    if not session or session.status == InteriewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")

    return {
        "introText": session.introText,
        "firstQuestion": session.questions[0]
    }


@router.post("/submit", response_model=AnswerResponse)
async def submit_answer(answerReq: AnswerRequest):
    # Check valid session_id
    session = get_session(answerReq.session_id)
    if not session or session.status == InteriewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")


    # save answer in interview session
    save_answer(answerReq.answer, answerReq.skip, session)

    # return
    if session.status == InteriewStatusEnum.COMPLETED:
        return {
            "interviewEnded": True
        }
    
    return {
        "interviewEnded": False,
        "nextQuestion": session.questions[session.current_index]
    }

@router.put("/end/{session_id}")
async def end_interview(session_id: str):
    # Check valid session_id
    session = get_session(session_id)
    if not session or session.status == InteriewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")
    
    session.status = InteriewStatusEnum.COMPLETED

    return {
            "interviewEnded": True
    }

@router.get("/report/{session_id}")
async def report(session_id: str):
    # Check valid session_id
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")
    
    resp = await generate_report(session.answers)

    return { "result":  resp }
