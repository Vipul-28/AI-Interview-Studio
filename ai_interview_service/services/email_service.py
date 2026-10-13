import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

def get_mail_config():
    load_dotenv(override=True)
    return {
        "host": os.getenv("MAIL_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("MAIL_PORT", "587")),
        "user": os.getenv("MAIL_USER", ""),
        "pass": os.getenv("MAIL_PASS", "").replace(" ", ""),
        "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:3000"),
    }


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Sends an HTML email via SMTP.
    Returns True if successful, False otherwise.
    """
    cfg = get_mail_config()
    mail_user = cfg["user"]
    mail_pass = cfg["pass"]
    mail_host = cfg["host"]
    mail_port = cfg["port"]

    if not mail_user or not mail_pass:
        print(f"[Email Service] SMTP credentials not configured. Simulating email to: {to_email}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"AI Interview Studio <{mail_user}>"
        msg["To"] = to_email

        html_part = MIMEText(html_body, "html")
        msg.attach(html_part)

        with smtplib.SMTP(mail_host, mail_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(mail_user, mail_pass)
            server.sendmail(mail_user, to_email, msg.as_string())

        print(f"[Email Service] Successfully sent email to: {to_email} | Subject: {subject}")
        return True
    except Exception as e:
        print(f"[Email Service] Failed to send email to {to_email}: {e}")
        return False



def send_invitation_email(
    to_email: str,
    candidate_name: str,
    job_title: str,
    session_id: str
) -> bool:
    """Sends the official candidate interview invitation email."""
    cfg = get_mail_config()
    frontend_url = cfg["frontend_url"]
    candidate_url = f"{frontend_url}/candidate/{session_id}"
    subject = f"Interview Invitation: {job_title} | AI Interview Studio"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f1f5f9; margin: 0; padding: 20px; }}
        .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        .header {{ background: linear-gradient(135deg, #0284c7, #2563eb); padding: 32px 24px; text-align: center; color: white; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .header p {{ margin: 8px 0 0; opacity: 0.9; font-size: 14px; }}
        .body {{ padding: 32px 28px; color: #334155; line-height: 1.6; }}
        .role-box {{ background: #f8fafc; border-left: 4px solid #0284c7; padding: 14px 18px; margin: 20px 0; border-radius: 4px; }}
        .guidelines {{ background: #f0fdf4; border: 1px solid #bbf7d0; padding: 16px; border-radius: 8px; margin: 20px 0; }}
        .btn {{ display: block; width: 220px; margin: 28px auto; background: #0284c7; color: #ffffff !important; text-decoration: none; padding: 14px 24px; text-align: center; border-radius: 8px; font-weight: bold; font-size: 16px; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h1>AI Technical Interview Invitation</h1>
          <p>Official Candidate Assessment</p>
        </div>
        <div class="body">
          <p>Dear <strong>{candidate_name}</strong>,</p>
          <p>You have been invited by the recruiting team to complete an AI-powered technical interview.</p>
          
          <div class="role-box">
            <strong>Target Position:</strong> {job_title}<br>
            <strong>Format:</strong> Voice-driven dynamic technical conversation (~10–15 mins)
          </div>

          <div class="guidelines">
            <strong>📋 Important Instructions:</strong>
            <ul style="margin: 8px 0 0 18px; padding: 0;">
              <li>Please use a desktop browser (Google Chrome or Microsoft Edge recommended).</li>
              <li>A working microphone and quiet environment are required.</li>
              <li>You can speak naturally — our AI interviewer will ask follow-up questions in real-time.</li>
            </ul>
          </div>

          <a href="{candidate_url}" class="btn" target="_blank">Start Interview</a>

          <p style="font-size: 13px; color: #64748b; text-align: center;">
            Or copy and paste this link into your browser:<br>
            <a href="{candidate_url}" style="color: #0284c7; word-break: break-all;">{candidate_url}</a>
          </p>
        </div>
        <div class="footer">
          &copy; AI Interview Studio. This is an automated notification.
        </div>
      </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_content)


def send_report_email(
    to_email: str,
    candidate_name: str,
    job_title: str,
    report: Dict[str, Any]
) -> bool:
    """Sends the candidate evaluation report email."""
    subject = f"Interview Assessment Report: {candidate_name} - {job_title}"

    score = report.get("score", "N/A")
    correct_count = report.get("correct_answer", 0)
    improvements = report.get("improvment_area", [])

    improvement_list_items = "".join([f"<li style='margin-bottom: 8px;'>{item}</li>" for item in improvements])

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f1f5f9; margin: 0; padding: 20px; }}
        .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        .header {{ background: linear-gradient(135deg, #10b981, #059669); padding: 32px 24px; text-align: center; color: white; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .body {{ padding: 32px 28px; color: #334155; line-height: 1.6; }}
        .score-banner {{ display: flex; justify-content: space-around; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px; margin: 20px 0; text-align: center; }}
        .score-val {{ font-size: 28px; font-weight: bold; color: #0284c7; }}
        .feedback-box {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 18px; margin-top: 20px; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h1>Technical Assessment Completed</h1>
          <p style="margin: 6px 0 0; opacity: 0.9;">Evaluation Summary for {candidate_name}</p>
        </div>
        <div class="body">
          <p>Hello <strong>{candidate_name}</strong>,</p>
          <p>Your technical interview for the position of <strong>{job_title}</strong> has been evaluated.</p>
          
          <div class="score-banner">
            <div>
              <div style="font-size: 12px; color: #64748b; text-transform: uppercase;">Overall Score</div>
              <div class="score-val">{score}</div>
            </div>
            <div>
              <div style="font-size: 12px; color: #64748b; text-transform: uppercase;">Correct Answers</div>
              <div class="score-val" style="color: #10b981;">{correct_count}</div>
            </div>
          </div>

          <div class="feedback-box">
            <strong style="color: #166534; font-size: 15px;">Key Improvement Areas & Technical Feedback:</strong>
            <ul style="margin: 10px 0 0 20px; padding: 0; color: #334155;">
              {improvement_list_items or "<li>No specific areas flagged.</li>"}
            </ul>
          </div>
        </div>
        <div class="footer">
          &copy; AI Interview Studio. This report was generated automatically.
        </div>
      </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_content)
