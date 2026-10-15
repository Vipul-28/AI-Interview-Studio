from sqlalchemy import text
from db.session import engine, Base
from db.models import InterviewSessionDB, RecruiterUserDB


def init_db():
    """Initializes tables in SQLite/PostgreSQL and performs non-destructive schema migrations."""
    Base.metadata.create_all(bind=engine)

    # Auto-migrate SQLite schema if new columns are missing
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(interview_sessions);"))
            columns = [row[1] for row in result.fetchall()]
            if "github_url" not in columns:
                conn.execute(text("ALTER TABLE interview_sessions ADD COLUMN github_url VARCHAR(500);"))
            if "github_context" not in columns:
                conn.execute(text("ALTER TABLE interview_sessions ADD COLUMN github_context TEXT;"))
            if "recruiter_id" not in columns:
                conn.execute(text("ALTER TABLE interview_sessions ADD COLUMN recruiter_id VARCHAR(64);"))
            conn.commit()
    except Exception as e:
        print(f"[init_db] Migration check notice: {e}")
