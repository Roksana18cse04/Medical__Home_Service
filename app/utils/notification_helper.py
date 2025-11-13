from app.services.auth_service import get_doctor_info_by_id, get_patient_info_by_id, get_user_info_by_token
from app.services.email_service import send_verification_email_Doctor  # Reuse existing email function

def send_risk_report_notification(patient_id: str = None, doctor_id: str = None, token: str = None, risk_level: str = "High", report_details: str = ""):
    """
    Send risk report notification to patient or doctor
    Can use patient_id, doctor_id, or token
    """
    
    # Get user info
    if token:
        user_info = get_user_info_by_token(token)
    elif patient_id:
        user_info = get_patient_info_by_id(patient_id)
    elif doctor_id:
        user_info = get_doctor_info_by_id(doctor_id)
    else:
        return {"error": "Either token, patient_id, or doctor_id required"}
    
    if "error" in user_info:
        return user_info
    
    # Send notification email
    try:
        email_subject = f"Risk Report Alert - {risk_level} Risk Level"
        email_body = f"""
        Dear {user_info['name']},
        
        Your recent health assessment indicates a {risk_level} risk level.
        
        Report Details: {report_details}
        
        Please consult with your healthcare provider for further guidance.
        
        Best regards,
        MediUrgency Team
        """
        
        # Reuse existing email function (you may need to create a generic one)
        send_verification_email_Doctor(user_info['email'], email_body)
        
        return {
            "message": "Risk report notification sent successfully",
            "sent_to": user_info['email'],
            "recipient": user_info['name']
        }
    except Exception as e:
        return {"error": f"Failed to send notification: {str(e)}"}

def get_user_contact_info(patient_id: str = None, doctor_id: str = None, token: str = None):
    """
    Quick function to get user contact info for notifications
    """
    if token:
        return get_user_info_by_token(token)
    elif patient_id:
        return get_patient_info_by_id(patient_id)
    elif doctor_id:
        return get_doctor_info_by_id(doctor_id)
    else:
        return {"error": "Either token, patient_id, or doctor_id required"}