import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import RecruiterUserDB
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_recruiter,
)

router = APIRouter(
    prefix="/auth",
    tags=["Recruiter Authentication"]
)


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    company_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
def recruiter_signup(data: SignupRequest, db: Session = Depends(get_db)):
    """Registers a new recruiter account and returns an access token."""
    email = data.email.strip().lower()
    name = data.name.strip()
    password = data.password

    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required.")
    if not email or "@" not in email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Valid email address is required.")
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )

    # Check for existing email
    existing = db.query(RecruiterUserDB).filter(RecruiterUserDB.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists. Please log in."
        )

    recruiter_id = str(uuid.uuid4())
    hashed_pwd = hash_password(password)

    new_recruiter = RecruiterUserDB(
        recruiter_id=recruiter_id,
        name=name,
        email=email,
        password_hash=hashed_pwd,
        company_name=data.company_name.strip() if data.company_name else None,
    )
    db.add(new_recruiter)
    db.commit()
    db.refresh(new_recruiter)

    # Generate JWT
    token_payload = {
        "sub": recruiter_id,
        "email": email,
        "name": name,
    }
    access_token = create_access_token(token_payload)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "recruiter": {
            "recruiter_id": new_recruiter.recruiter_id,
            "name": new_recruiter.name,
            "email": new_recruiter.email,
            "company_name": new_recruiter.company_name,
            "created_at": new_recruiter.created_at.isoformat() if new_recruiter.created_at else None,
        }
    }


@router.post("/login")
def recruiter_login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates a recruiter with email and password and returns an access token."""
    email = data.email.strip().lower()
    password = data.password

    recruiter = db.query(RecruiterUserDB).filter(RecruiterUserDB.email == email).first()
    if not recruiter or not verify_password(password, recruiter.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please try again."
        )

    # Generate JWT
    token_payload = {
        "sub": recruiter.recruiter_id,
        "email": recruiter.email,
        "name": recruiter.name,
    }
    access_token = create_access_token(token_payload)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "recruiter": {
            "recruiter_id": recruiter.recruiter_id,
            "name": recruiter.name,
            "email": recruiter.email,
            "company_name": recruiter.company_name,
            "created_at": recruiter.created_at.isoformat() if recruiter.created_at else None,
        }
    }


@router.get("/me")
def get_current_recruiter_profile(recruiter: RecruiterUserDB = Depends(get_current_recruiter)):
    """Returns the profile information of the currently authenticated recruiter."""
    return {
        "recruiter_id": recruiter.recruiter_id,
        "name": recruiter.name,
        "email": recruiter.email,
        "company_name": recruiter.company_name,
        "created_at": recruiter.created_at.isoformat() if recruiter.created_at else None,
    }
