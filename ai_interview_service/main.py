from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.init_db import init_db
from routers.interview import router as interview_router
from routers.interview_ws import router as interview_ws_router
from routers.recruiter import router as recruiter_router
from routers.candidate import router as candidate_router
from routers.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database on startup
    init_db()
    yield


app = FastAPI(
    version="1.0.0",
    title="AI Interview Studio Service",
    description="Enterprise AI Interview Studio with Recruiter & Candidate Portals",
    lifespan=lifespan
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register modular routers
app.include_router(auth_router)
app.include_router(recruiter_router)
app.include_router(candidate_router)
app.include_router(interview_ws_router)
app.include_router(interview_router)
