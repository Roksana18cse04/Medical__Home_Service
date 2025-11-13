import smtplib
from email.mime.text import MIMEText
from app.core.config import EMAIL_USER, EMAIL_PASS
from email.mime.multipart import MIMEMultipart



def send_verification_email_Doctor(to_email, otp):
    subject = "HomeCare App: Doctor Email Verification"
    
    # HTML content
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <p>Dear Doctor,</p>

        <p>We hope this message finds you well.</p>

        <p>Your verification code for accessing the <strong>HomeCare App</strong> is:</p>

        <h2 style="background-color: #f2f2f2; padding: 10px; display: inline-block;">{otp}</h2>

        <p>Please enter this code in the app to verify your email address. This code will expire in <strong>10 minutes</strong> for security reasons.</p>

        <p>If you did not request this code, please ignore this email.</p>

        <p>Best regards,<br>
        <strong>HomeCare App Team</strong></p>
      </body>
    </html>
    """

    # -------- Email Setup --------
    msg = MIMEMultipart("alternative")
    msg["From"] = f"HomeCare App <{EMAIL_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, to_email, msg.as_string())
        print("✅ Alert email sent successfully.")
    except Exception as e:
        print("❌ Failed to send email:", e)



def send_verification_email_Patient(to_email, otp):
    msg = MIMEText(f"Your verification code is: {otp}")
    msg["Subject"] = "Home Care App Patient Email Verification"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

def send_Alert_message_doctor(
    doctor_email: str,
    doctor_name: str,
    patient_id: str,
    disease: str,
    urgency: str,
    transcript: str,
    patient_name: str = "Patient",
    symptoms: list = []
):
    # -------- Email Subject --------
    subject = f"🚨 [HomeCare Alert] {patient_name} ({patient_id}) - Urgency: {urgency.upper()} | Suspected: {disease}"

    # -------- Email Body (HTML) --------
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #222; background-color:#f9f9f9; padding:20px;">
            <div style="max-width:600px; background:white; padding:25px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1);">
                
                <h2 style="color:#1a73e8; text-align:center;">🏥 HomeCare Hospital - AI Alert System</h2>
                <hr style="border:0; border-top:2px solid #eee; margin:10px 0 20px 0;">
                
                <p>Dear <strong>{doctor_name}</strong>,</p>

                <p>
                    Our AI monitoring system has detected a <strong>{urgency.upper()}</strong> risk event 
                    for the following patient under your supervision. Kindly review the case details below:
                </p>

                <table style="border-collapse: collapse; width: 100%; margin-top: 10px; border:1px solid #ddd;">
                    <tr style="background:#f2f2f2;">
                        <td style="padding:8px; border:1px solid #ddd;"><strong>Patient Name</strong></td>
                        <td style="padding:8px; border:1px solid #ddd;">{patient_name}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px; border:1px solid #ddd;"><strong>Patient ID</strong></td>
                        <td style="padding:8px; border:1px solid #ddd;">{patient_id}</td>
                    </tr>
                    <tr style="background:#f9f9f9;">
                        <td style="padding:8px; border:1px solid #ddd;"><strong>Detected Condition</strong></td>
                        <td style="padding:8px; border:1px solid #ddd;">{disease}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px; border:1px solid #ddd;"><strong>Urgency Level</strong></td>
                        <td style="padding:8px; border:1px solid #ddd; color:{'red' if urgency.lower()=='high' else '#e68a00'};">
                            {urgency.capitalize()}
                        </td>
                    </tr>
                    <tr style="background:#f9f9f9;">
                        <td style="padding:8px; border:1px solid #ddd;"><strong>Symptoms</strong></td>
                        <td style="padding:8px; border:1px solid #ddd;">{', '.join(symptoms)}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px; border:1px solid #ddd;"><strong>Patient Description</strong></td>
                        <td style="padding:8px; border:1px solid #ddd;">{transcript}</td>
                    </tr>
                </table>

                <p style="margin-top:20px;">
                    🕑 Please review this patient's case immediately in your 
                    <strong>HomeCare Hospital Dashboard</strong> and take necessary action.
                </p>

                <p style="margin-top:25px; color:#555;">
                    Regards,<br>
                    <strong>HomeCare AI – Automated Alert System</strong><br>
                    <small>HomeCare Hospital, Digital Health Monitoring Division</small>
                </p>

                <hr style="border:0; border-top:1px solid #eee; margin-top:30px;">
                <p style="text-align:center; font-size:12px; color:#999;">
                    © 2025 HomeCare Hospital. This is an automated notification, please do not reply directly.
                </p>
            </div>
        </body>
    </html>
    """

    # -------- Email Setup --------
    msg = MIMEMultipart("alternative")
    msg["From"] = f"HomeCare Hospital AI Alert <{EMAIL_USER}>"
    msg["To"] = doctor_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, doctor_email, msg.as_string())
        print("✅ Alert email sent successfully.")
    except Exception as e:
        print("❌ Failed to send alert email:", e)


# ----------- Example Call -----------
if __name__ == "__main__":
    send_Alert_message_doctor(
        doctor_Name="Dr. Shakil Ahmed",
        to_email="shakilahammed055@gmail.com",
        patient_name="Roksana Akter",
        patient_id="P-1023",
        disease="Cardiac Stress Indicator",
        urgency="high",
        symptoms=["Chest pain", "Shortness of breath", "Irregular heartbeat"],
        transcript="Doctor, I felt a sharp pain in my chest while walking and felt dizzy for a few seconds."
    )
