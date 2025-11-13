import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_test(to_email):
    msg = MIMEText("Test mail from FastAPI app — OTP/email test.")
    msg["Subject"] = "Test Email"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
    print("Sent!")

if __name__ == "__main__":
    send_test("roksana.tech.2000@gmail.com")
