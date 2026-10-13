from typing import Tuple, Optional
from db.models import InterviewSessionDB
from schemas.websocket_schema import ClientEventType
from services.follow_up_service import generate_dynamic_follow_up
from services.interview_service import update_session


def initialize_session_question(session: InterviewSessionDB) -> str:
    """Sets the initial base question when the interview begins."""
    session.current_base_idx = 0
    session.follow_up_count = 0
    session.is_current_follow_up = False
    session.status = "IN_PROGRESS"

    first_q = session.questions[0] if session.questions else "Could you introduce yourself and your background?"
    session.current_question_text = first_q
    update_session(session)
    return first_q


async def advance_interview_state(
    session: InterviewSessionDB,
    action: ClientEventType,
    answer_text: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Executes a single state transition in the interview.
    Records the answer for the current question in the database, then determines whether to:
    1. Generate Follow-up 1 or Follow-up 2 (if answered or follow-up 1 skipped)
    2. Advance to the next Base Question
    3. Complete the interview (if all base questions finished or END_INTERVIEW requested)

    Returns:
        (is_completed: bool, next_question_text: Optional[str])
    """
    # 1. Record current answer
    is_skip = (action == ClientEventType.SKIP)
    recorded_answer = None if is_skip else (answer_text.strip() if answer_text else None)

    current_answers = session.answers
    current_answers.append({
        "question": session.current_question_text,
        "answer": recorded_answer,
        "skip": is_skip,
        "is_follow_up": session.is_current_follow_up,
        "follow_up_num": session.follow_up_count
    })
    session.answers = current_answers

    # 2. Check early exit
    if action == ClientEventType.END_INTERVIEW:
        session.status = "COMPLETED"
        update_session(session)
        return True, None

    # 3. Decision Matrix
    base_question = session.questions[session.current_base_idx] if session.current_base_idx < len(session.questions) else ""
    prev_question = session.current_question_text

    need_follow_up = False
    next_follow_up_num = 0

    if is_skip:
        if session.follow_up_count == 0:
            # Skipped Base Question -> skip entire follow-up thread, advance to next Base Question
            session.current_base_idx += 1
            session.follow_up_count = 0
            session.is_current_follow_up = False
        elif session.follow_up_count == 1:
            # Skipped Follow-up 1 -> as aligned, still ask Follow-up 2
            session.follow_up_count = 2
            session.is_current_follow_up = True
            need_follow_up = True
            next_follow_up_num = 2
        else:
            # Skipped Follow-up 2 -> thread finished, advance to next Base Question
            session.current_base_idx += 1
            session.follow_up_count = 0
            session.is_current_follow_up = False
    else:
        # Candidate answered
        if session.follow_up_count < session.max_follow_ups:
            # Under follow-up budget -> generate next follow-up
            session.follow_up_count += 1
            session.is_current_follow_up = True
            need_follow_up = True
            next_follow_up_num = session.follow_up_count
        else:
            # Reached max follow-ups (2) -> thread finished, advance to next Base Question
            session.current_base_idx += 1
            session.follow_up_count = 0
            session.is_current_follow_up = False

    # 4. Check if all base questions are exhausted
    if not need_follow_up and session.current_base_idx >= len(session.questions):
        session.status = "COMPLETED"
        update_session(session)
        return True, None

    # 5. Generate either Follow-up OR Next Base Question
    if need_follow_up:
        follow_up_q = await generate_dynamic_follow_up(
            base_question=base_question,
            previous_question=prev_question,
            candidate_answer=recorded_answer,
            follow_up_num=next_follow_up_num
        )
        session.current_question_text = follow_up_q
        update_session(session)
        return False, follow_up_q
    else:
        next_base_q = session.questions[session.current_base_idx]
        session.current_question_text = next_base_q
        session.is_current_follow_up = False
        session.follow_up_count = 0
        update_session(session)
        return False, next_base_q
