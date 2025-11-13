from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from app.core.security import verify_token
from app.services.text_profilling import Risk_Analysis
from app.DataBase import patients_col, audit_review_col
from app.utils.voice_upload import upload_file
from app.services.email_service import send_Alert_message_doctor
from app.services.auth_service import get_doctor_info_by_id
from app.schemas.AuditReview import AuditReview, AlertInfo
import uuid
import os
from datetime import datetime

audio_router = APIRouter(prefix="/patient_dashboard", tags=["Audio Stream"])

@audio_router.post("/audio_stream")
async def audio_stream(token: str = Query(...), voice_file: UploadFile = File(...)):
    # Verify token
    try:
        patient_id = verify_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    patient_doc = patients_col.find_one({"patient_id": patient_id})
    if not patient_doc:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Save audio
    audio_filename = f"{uuid.uuid4()}.wav"
    os.makedirs("temp_audio", exist_ok=True)
    audio_filepath = os.path.join("temp_audio", audio_filename)
    with open(audio_filepath, "wb") as f:
        f.write(await voice_file.read())
    
    # Upload and transcribe
    voice_url = upload_file(audio_filepath)
    transcription = "..."  # process_audio + transcribe_audio
    
    # Prepare patient data
    patient_data = {
        "age": patient_doc.get("age"),
        "gender": patient_doc.get("gender"),
        "symptoms": patient_doc.get("previous_symptoms", []),
        "current_situation": transcription
    }
    
    analysis_result = Risk_Analysis(patient_data)
    
    # Prepare alert info
    alert_sent = False
    doctor_id = analysis_result[0].get("doctor_id") if analysis_result else None
    urgency = analysis_result[0].get("urgency", "low").lower() if analysis_result else "low"
    
    if urgency in ["high", "medium"] and doctor_id:
        # Get doctor info for email
        doctor_info = get_doctor_info_by_id(doctor_id)
        if "error" not in doctor_info:
            send_Alert_message_doctor(
                doctor_email=doctor_info["email"],
                doctor_name=doctor_info["name"],
                patient_id=patient_id,
                disease=analysis_result[0].get("disease", ""),
                urgency=urgency,
                transcript=transcription
            )
            alert_sent = True
    
    alert_info = AlertInfo(
        doctor_id=doctor_id,
        specialist=analysis_result[0].get("recommended_specialist", "") if analysis_result else "",
        sent=alert_sent,
        method=["email"] if alert_sent else [],
        timestamp=datetime.utcnow()
    )
    
    # Store audit
    audit_doc = AuditReview(
        patient_id=patient_id,
        voice_url=voice_url,
        transcript=transcription,
        keywords=patient_data.get("symptoms", []),
        detected_disease=analysis_result[0].get("disease", "") if analysis_result else "",
        alert=alert_info,
        created_at=datetime.utcnow()
    )
    
    audit_review_col.insert_one(audit_doc.dict())
    
    return {
        "patient_id": patient_id,
        "transcript": transcription,
        "analysis": analysis_result,
        "doctor_id": doctor_id,
        "alert_sent": alert_sent
    }
