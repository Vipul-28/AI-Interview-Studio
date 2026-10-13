import os
import re
import json
from typing import Optional, List
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "qwen/qwen3.8-27b")

client = OpenAI(base_url=OPENAI_BASE_URL) if OPENAI_BASE_URL else OpenAI()


class FollowUpQuestionSchema(BaseModel):
    follow_up_question: str
    focus_topic: Optional[str] = ""


def _extract_json_fallback(content: str) -> dict:
    if not content:
        return {}
    content = content.strip()
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    try:
        return json.loads(content)
    except Exception:
        pass
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except Exception:
            pass
    match_braces = re.search(r"(\{[\s\S]*\})", content)
    if match_braces:
        try:
            return json.loads(match_braces.group(1))
        except Exception:
            pass
    return {"follow_up_question": content}


async def generate_dynamic_follow_up(
    base_question: str,
    previous_question: str,
    candidate_answer: Optional[str],
    follow_up_num: int,
) -> str:
    """
    Generates a targeted, conversational technical follow-up question based on the candidate's actual answer.
    """
    answer_text = candidate_answer.strip() if candidate_answer else "Candidate skipped or gave no answer."

    SYSTEM_PROMPT = f"""
        You are an expert, encouraging technical interviewer conducting a mock interview.
        You are asking Follow-up #{follow_up_num} of 2 for the current topic.

        Context:
        - Primary Topic / Base Question: "{base_question}"
        - Just Asked Question: "{previous_question}"
        - Candidate's Answer: "{answer_text}"

        Rules for the Follow-up Question:
        1. Generate EXACTLY 1 follow-up question directly probing or expanding on what the candidate just said.
        2. If the candidate gave a solid answer: Probe a technical trade-off, edge case, or practical scenario.
        3. If the candidate gave a short or partial answer: Ask for a specific clarification or simple concrete example.
        4. If the candidate skipped: Ask a simpler alternative question related to the same primary topic.
        5. Keep the question SHORT, clear, and direct (1-2 sentences maximum).
        6. It must be comfortable to understand via voice text-to-speech.
    """

    user_prompt = f"Generate Follow-up #{follow_up_num} in JSON format with field 'follow_up_question'."

    try:
        response = client.beta.chat.completions.parse(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format=FollowUpQuestionSchema,
        )
        if response.choices[0].message.parsed:
            return response.choices[0].message.parsed.follow_up_question
        fallback = _extract_json_fallback(response.choices[0].message.content)
        return fallback.get("follow_up_question", "Could you elaborate on that concept?")
    except Exception as e:
        print(f"Error in generate_dynamic_follow_up: {e}")
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            fallback = _extract_json_fallback(response.choices[0].message.content)
            return fallback.get("follow_up_question", "Can you provide a practical example of how you would use that?")
        except Exception as e2:
            print(f"Fallback error in generate_dynamic_follow_up: {e2}")
            return "Can you tell me more about how you would implement this in a real project?"
