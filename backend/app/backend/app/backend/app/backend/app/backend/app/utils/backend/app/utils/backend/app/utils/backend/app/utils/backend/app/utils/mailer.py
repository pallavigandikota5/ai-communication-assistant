import os, smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

SMTP_HOST = os.getenv("SENDER_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SENDER_SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SENDER_SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SENDER_SMTP_PASSWORD")
SENDER_NAME = os.getenv("SENDER_NAME", "Support Assistant")

def send_email(to_addr: str, subject: str, body: str):
    if not all([SMTP_EMAIL, SMTP_PASSWORD]):
        # For demo environments without SMTP configured, just no-op.
        return
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = formataddr((SENDER_NAME, SMTP_EMAIL))
    msg["To"] = to_addr
    msg["Subject"] = subject
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
