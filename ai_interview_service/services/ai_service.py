from openai import OpenAI
from dotenv import load_dotenv
import json
import os
import re
from typing import List, Optional
from pydantic import BaseModel

load_dotenv()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "qwen/qwen3.8-27b")

client = OpenAI(base_url=OPENAI_BASE_URL) if OPENAI_BASE_URL else OpenAI()

class InterviewQuestionsSchema(BaseModel):
    questions: List[str]
    introText: str
    candidate_name: Optional[str] = "Candidate"

class ReportSchema(BaseModel):
    score: int  # 0 to 100 percentage integer
    correct_answer: int
    improvment_area: List[str]

def parse_json_response(content: str) -> dict:
    """Robust parser that handles markdown code fences, reasoning tags, and raw JSON."""
    if not content:
        return {}
    content = content.strip()
    # Strip <think>...</think> if present
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
    
    # Try direct parse
    try:
        return json.loads(content)
    except Exception:
        pass
        
    # Remove markdown code blocks if any
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except Exception:
            pass

    # Find first '{' to last '}'
    match_braces = re.search(r'(\{[\s\S]*\})', content)
    if match_braces:
        try:
            return json.loads(match_braces.group(1))
        except Exception:
            pass

    raise ValueError(f"Could not parse valid JSON from model response: {content[:200]}")


async def generate_questions_intro(job_title, job_description, resume_text, github_url=None, github_context=None):
    github_section = ""
    if github_context:
        github_section = f"""
        Candidate GitHub Repository / Profile Context:
        {github_context}
        """

    SYSTEM_PROMPT = f"""
        You are an AI interview expert who generates targeted, professional interview questions based on the candidate's target job_title, job_description, resume_text, and GitHub portfolio (if available).
        You need to identify the candidate's name, generate an encouraging introduction text, and generate interview questions tailored specifically to the role ({job_title}).

        Input:
            job_title: {job_title}
            job_description: {job_description}
            resume_text: {resume_text}
            {github_section}

        Output:
            questions: array of 2 strings
            introText: string
            candidate_name: string

        Rules:
            - For Questions:
                a) Generate EXACTLY 2 questions (no more, no less).
                b) Questions must directly assess the core competencies of the job_title and the specific requirements in the job_description.
                c) Questions must be short, clear, and direct (1-2 sentences each), suitable for spoken oral answers.
                d) IMPORTANT: If Candidate GitHub Context is provided above:
                   - Cross-reference the Job Requirements against the candidate's GitHub projects and codebase.
                   - Identify the specific technology, architecture, or feature in their repository that relates to the skills required in the job_description.
                   - EXACTLY ONE question MUST be generated asking specifically about that related project in their repository (e.g., "In your GitHub repository [Repository Name], we saw you implemented [Relevant Technology/Feature from Job Requirements]; could you explain your architectural approach and how you designed that?").
                   - If no direct technology match is found, ask a question examining their largest project architecture in their repo and how it translates to the demands of this role.
            - For Introduction Text:
                a) Welcoming text played on the browser before starting the interview.
                b) Include candidate name and target job title.
                c) Keep it welcoming, short, and encouraging.
            - For Candidate Name:
                a) Extract candidate name from resume, if candidate not found then consider candidate name as "Candidate".

            - Output:
                Output needs to be in json format and it should have questions, introText, candidate_name
    """

    try:
        response = client.beta.chat.completions.parse(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Generate exactly 2 focused, clear questions, introText and candidate_name as instructed."}
            ],
            response_format=InterviewQuestionsSchema
        )
        if response.choices[0].message.parsed:
            return response.choices[0].message.parsed.model_dump()
        return parse_json_response(response.choices[0].message.content)
    except Exception:
        # Fallback to standard chat completions
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Generate the questions, introText and candidate_name as instructed. Return valid JSON only."}
            ]
        )
        return parse_json_response(response.choices[0].message.content)


async def generate_report(answers = []):
    formatted_answers = [
        a.model_dump() if hasattr(a, "model_dump") else (a.dict() if hasattr(a, "dict") else a)
        for a in answers
    ]
    answers_json = json.dumps(formatted_answers, indent=2)

    # ---- DEBUG ----
    print("\n===== ANSWERS RECEIVED FOR REPORT =====")
    print(answers_json)
    print("========================================\n")
    # ---------------

    SYSTEM_PROMPT = f"""
        You are an expert AI technical interviewer assessing candidate performance.
        Evaluate the candidate's answers to the technical interview questions.

        Candidate Answers Data:
        {answers_json}

        Evaluation Guidelines:
        1. Review each question and the candidate's answer.
        2. If an answer was skipped (skip=true) or is blank/empty, consider it incorrect.
        3. If the candidate demonstrated reasonable technical understanding and answered relevant points, count it as correct.
        4. Be lenient — if the answer shows even partial understanding, count it as correct.
        5. score is an integer from 0 to 100 representing percentage of correct answers.
        6. correct_answer is the integer count of correct answers.
        7. improvment_area is an array of actionable feedback points (maximum 5 items).
    """

    try:
        response = client.beta.chat.completions.parse(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Analyse the answers and return the score (0-100 integer), correct_answer count, and improvment_area list."}
            ],
            response_format=ReportSchema
        )
        if response.choices[0].message.parsed:
            res_dict = response.choices[0].message.parsed.model_dump()

            # ---- DEBUG ----
            print("\n===== AI REPORT RESULT =====")
            print(res_dict)
            print("============================\n")
            # ---------------

            res_dict["score"] = f"{res_dict['score']}%"
            return res_dict
        fallback = parse_json_response(response.choices[0].message.content)
        if "score" in fallback and not str(fallback["score"]).endswith("%"):
            fallback["score"] = f"{fallback['score']}%"
        return fallback
    except Exception as e:
        print(f"\n===== generate_report EXCEPTION: {e} =====\n")
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Analyse the answers and return the score, correct_answer, and improvment_area as instructed. Return valid JSON only."}
            ]
        )
        return parse_json_response(response.choices[0].message.content)

