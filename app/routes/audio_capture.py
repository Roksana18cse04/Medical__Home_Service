from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from app.core.security import verify_token
from app.utils.record_audio import process_audio
from app.utils.audio_transcribe import transcribe_audio
from app.services.text_profilling import Risk_Analysis
from app.DataBase import audit_review_col, patients_col, doctor_specialists_col
from app.utils.voice_upload import upload_file
from app.services.email_service import send_Alert_message_doctor
from app.schemas.AuditReview import AlertInfo, AuditReview
import uuid
import os
from datetime import datetime

audio_router = APIRouter(prefix="/patient_dashboard", tags=["Audio Stream"])

@audio_router.post("/audio_stream")
async def audio_stream(
    token: str = Query(..., description="JWT token for authentication"),
    voice_file: UploadFile = File(...)
):
    # ------------------- Verify Token & Fetch Patient Info -------------------
    try:
        patient_id = verify_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    patient_doc = patients_col.find_one({"patient_id": patient_id})
    if not patient_doc:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient_age = patient_doc.get("age")
    patient_gender = patient_doc.get("gender")
    previous_symptoms = patient_doc.get("previous_symptoms", [])
    medical_history = patient_doc.get("medical_history", {})

    # ------------------- Save Audio Temporarily -------------------
    audio_filename = f"{uuid.uuid4()}.wav"
    os.makedirs("temp_audio", exist_ok=True)
    audio_filepath = os.path.join("temp_audio", audio_filename)

    with open(audio_filepath, "wb") as f:
        f.write(await voice_file.read())

    # ------------------- Process & Transcribe -------------------
    process_audio(audio_filepath)  # resample, mono, noise suppression
    voice_url = upload_file(audio_filepath)  # upload to cloud
    transcription = transcribe_audio(audio_filepath)  # Whisper ASR
    os.remove(audio_filepath)  # cleanup

    # ------------------- Prepare Data for Risk Analysis -------------------
    patient_data = {
        "age": patient_age,
        "gender": patient_gender,
        "symptoms": previous_symptoms,
        "current_situation": transcription
    }

    # ------------------- Risk Analysis -------------------
    analysis_result = Risk_Analysis(patient_data)

    # ------------------- Attach Doctor Based on Specialist -------------------
    doctor_id = None
    urgency = "low"
    if analysis_result and "recommended_specialist" in analysis_result[0]:
        specialist = analysis_result[0]["recommended_specialist"]
        doctor_doc = doctor_specialists_col.find_one({"specialist": specialist})
        if doctor_doc:
            doctor_id = doctor_doc["doctor_id"]
        urgency = analysis_result[0].get("urgency", "low").lower()

    # ------------------- Prepare Alert -------------------
    alert_sent = False
    alert_methods = []
    if urgency in ["high", "medium"] and doctor_id:
        # send alert to doctor
        send_Alert_message_doctor(
            doctor_id=doctor_id,
            patient_id=patient_id,
            disease=analysis_result[0].get("disease", ""),
            urgency=urgency,
            transcript=transcription
        )
        alert_sent = True
        alert_methods = ["email"]  # adjust if using SMS/push

    # ------------------- Store in Audit Review -------------------
    audit_doc = {
        "patient_id": patient_id,
        "voice_url": voice_url,
        "transcript": transcription,
        "keywords": previous_symptoms,
        "detected_disease": analysis_result[0].get("disease", "") if analysis_result else "",
        "alert": {
            "doctor_id": doctor_id,
            "specialist": analysis_result[0].get("recommended_specialist", "") if analysis_result else "",
            "sent": alert_sent,
            "method": alert_methods,
            "timestamp": datetime.utcnow()
        },
        "created_at": datetime.utcnow()
    }

    audit_review_col.insert_one(audit_doc)

    return {
        "patient_id": patient_id,
        "age": patient_age,
        "gender": patient_gender,
        "previous_symptoms": previous_symptoms,
        "transcript": transcription,
        "analysis": analysis_result,
        "doctor_id": doctor_id,
        "alert_sent": alert_sent
    }
