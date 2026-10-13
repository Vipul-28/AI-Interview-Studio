from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.interview_service import get_session, update_session
from services.ai_service import generate_report
from services.interview_state_manager import (
    initialize_session_question,
    advance_interview_state
)
from schemas.websocket_schema import (
    ClientEventType,
    ServerEventType,
    ClientMessage
)
from models.interview import InteriewStatusEnum

router = APIRouter(
    prefix="/interview",
    tags=["Interview WebSocket"]
)


@router.websocket("/ws/{session_id}")
async def interview_websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    session = get_session(session_id)
    if not session:
        await websocket.send_json({
            "type": ServerEventType.ERROR.value,
            "message": "Interview session not found. Please start from the upload page."
        })
        await websocket.close(code=1008)
        return

    if session.status == InteriewStatusEnum.COMPLETED:
        await websocket.send_json({
            "type": ServerEventType.ERROR.value,
            "message": "This interview session has already ended."
        })
        await websocket.close(code=1000)
        return

    # Initialize first base question if starting fresh
    first_q = initialize_session_question(session)

    # Send initial event with introText and first base question
    await websocket.send_json({
        "type": ServerEventType.INIT.value,
        "data": {
            "introText": session.intro_text,
            "question": first_q,
            "base_num": session.current_base_idx + 1,
            "total_base": len(session.questions),
            "is_follow_up": False,
            "follow_up_num": 0
        }
    })

    try:
        while True:
            raw_data = await websocket.receive_json()
            client_msg = ClientMessage.model_validate(raw_data)

            # Inform client that AI is evaluating and preparing the next turn
            await websocket.send_json({
                "type": ServerEventType.AI_THINKING.value,
                "message": "AI is analyzing your response..."
            })

            is_completed, next_q = await advance_interview_state(
                session=session,
                action=client_msg.type,
                answer_text=client_msg.answer
            )

            if is_completed:
                # Interview completed! Generate final graded report
                report = await generate_report(session.answers)
                session.report = report
                session.status = "COMPLETED"
                update_session(session)

                # Automatically email report to candidate if email configured
                if session.candidate_email and "@" in session.candidate_email:
                    try:
                        from services.email_service import send_report_email
                        send_report_email(
                            to_email=session.candidate_email,
                            candidate_name=session.candidate_name,
                            job_title=session.job_title,
                            report=report
                        )
                    except Exception as email_err:
                        print(f"Error emailing report: {email_err}")

                await websocket.send_json({
                    "type": ServerEventType.REPORT.value,
                    "data": {
                        "report": report
                    }
                })
                break
            else:
                # Push the next question (either follow-up or next base question)
                await websocket.send_json({
                    "type": ServerEventType.QUESTION.value,
                    "data": {
                        "question": next_q,
                        "base_num": session.current_base_idx + 1,
                        "total_base": len(session.questions),
                        "is_follow_up": session.is_current_follow_up,
                        "follow_up_num": session.follow_up_count
                    }
                })

    except WebSocketDisconnect:
        print(f"WebSocket client disconnected for session: {session_id}")
    except Exception as e:
        print(f"Unexpected error in interview WebSocket: {e}")
        try:
            await websocket.send_json({
                "type": ServerEventType.ERROR.value,
                "message": f"Server processing error: {str(e)}"
            })
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
