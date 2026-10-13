# 🎙️ AI Interview Studio

An enterprise-grade, autonomous AI interviewing platform engineered to evaluate technical candidates through voice-driven real-time conversations, dynamic adaptive follow-up questioning, automated scoring, and email dispatch workflows.

---

## 🌟 Key Architecture & Capabilities

- **🏢 Recruiter Portal (`/recruiter`):**
  - Intuitive workspace for hiring managers and recruiters to configure job descriptions and upload candidate resumes (PDF format).
  - Automatically parses credentials, identifies candidate details, and pre-generates tailored technical questions.
  - Generates secure candidate interview invitation links with built-in one-click Gmail SMTP email delivery.
  - Centralized dashboard displaying candidate submissions, real-time status badges (`Invitation Sent`, `In Progress`, `Completed`), overall numerical scores, and full performance breakdowns.
  - Ability to re-send interview invitations or email evaluation summaries directly to candidates or internal hiring committees.

- **🎙️ Candidate Voice Studio (`/candidate/:sessionId`):**
  - Dedicated candidate experience with real-time Speech-to-Text (Web Speech API) and Speech Synthesis (Text-to-Speech audio prompts).
  - Pre-flight microphone permission checks and guidance.
  - WebSocket-powered duplex connection (`/ws/interview/{sessionId}`) for conversational interactions.
  - **Dynamic Follow-Up Engine**: Generates real-time contextual follow-ups evaluating the depth, precision, or ambiguity of candidate responses before progressing to the next topic.

- **🤖 Intelligent Evaluation & Grading Engine:**
  - Evaluates candidate responses against industry standards, depth of technical knowledge, and relevance to the target job position.
  - Computes objective numerical scores (0–100 scale), tallies correct responses, flags gaps, and outlines actionable improvement areas.

- **💾 Persistent Database Layer:**
  - SQLAlchemy SQLite database (`interview.db`) managing interview session states, questions, answers, and evaluation reports across server restarts.

- **📬 Automated Email Service:**
  - Full SMTP integration supporting automated interview invitations and comprehensive candidate evaluation report emails.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, React Router v7, Modern CSS Design System, Web Speech API, WebSockets |
| **Backend** | FastAPI (Python 3.10+), Uvicorn, WebSockets, SQLAlchemy, SQLite, Pydantic |
| **AI / LLM** | OpenAI API (Structured Outputs & Function Calling) |
| **Document Processing** | PyPDF2 (Resume text extraction) |
| **Email Delivery** | Python SMTP (`smtplib`, `email.mime`) |

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- OpenAI API Key

---

### 2. Backend Setup

```bash
cd ai_interview_service

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (.env)
cp .env.example .env
```

Ensure your `ai_interview_service/.env` contains:
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./interview.db
FRONTEND_URL=http://localhost:3000

# Email Delivery (Optional / Gmail SMTP)
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USER=your_email@gmail.com
MAIL_PASS=your_gmail_app_password
```

Start the FastAPI backend service:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The API and interactive docs will be available at:
- **Interactive API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 3. Frontend Setup

```bash
cd ai_interview_frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The application will be live at:
- **Recruiter Portal:** [http://localhost:3000/recruiter](http://localhost:3000/recruiter)
- **Practice Studio:** [http://localhost:3000/](http://localhost:3000/)

---

## 🔒 Security & Best Practices

- App passwords should be used for Gmail SMTP configuration rather than personal passwords.
- SQLite database initializes automatically with robust indexes on session identifiers.
- CORS policy is configured to secure cross-origin requests between the UI and API endpoints.

---

## 📄 License

Proprietary — AI Interview Studio. All rights reserved.
