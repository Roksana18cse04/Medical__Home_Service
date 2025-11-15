from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from datetime import datetime
from bson import ObjectId
import uuid, os

from app.DataBase import patients_col, audit_review_col
from app.services.auth_service import get_doctor_info_by_id, get_user_info_by_token, get_patient_info_by_id
from app.utils.voice_upload import upload_file
from app.services.text_profilling import Risk_Analysis
from app.services.email_service import send_Alert_message_doctor
from app.services.pateint_context_from_audio import get_patient_context_from_audio
from app.schemas.audit_schemas import AuditReview, AlertInfo
from app.core.config import UPLOAD_FOLDER

audio_router = APIRouter()

@audio_router.post("/audio_stream")
async def audio_stream(token: str = Query(...), voice_file: UploadFile = File(...)):
    """
    Upload and analyze audio, generate transcript,
    perform risk analysis, and send doctor alerts.
    """

    # -----------------------------------------------------------
    # 🔹 Step 1: Validate token & Get Patient Data
    # -----------------------------------------------------------
    try:
        patient_id = get_user_info_by_token(token)
        print("Patient ID:", patient_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    if not patient_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    patient_data_db = get_patient_info_by_id(patient_id)

    if "error" in patient_data_db:
        raise HTTPException(status_code=404, detail=patient_data_db["error"])

    patient_name = patient_data_db.get("name")
    patient_email = patient_data_db.get("email")

    # -----------------------------------------------------------
    # 🔹 Step 2: Save Audio File
    # -----------------------------------------------------------
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    audio_filename = f"{uuid.uuid4()}.wav"
    audio_filepath = os.path.join(UPLOAD_FOLDER, audio_filename)

    with open(audio_filepath, "wb") as f:
        f.write(await voice_file.read())

    # -----------------------------------------------------------
    # 🔹 Step 3: Upload File & Transcribe
    # -----------------------------------------------------------
    voice_url = upload_file(audio_filepath)

    transcription = await get_patient_context_from_audio(audio_filepath)
    transcript_text = transcription.get("patient_context") if isinstance(transcription, dict) else transcription

    print("Transcript:\n", transcription)

    # -----------------------------------------------------------
    # 🔹 Step 4: Prepare Risk Analysis Input
    # -----------------------------------------------------------
    risk_input = {
        "age": patient_data_db.get("age"),
        "gender": patient_data_db.get("gender"),
        "symptoms": patient_data_db.get("symptoms", []),
        "current_situation": transcript_text
    }

    analysis_result = Risk_Analysis(risk_input)
    print("Risk Analysis Output:\n", analysis_result)
    

    # -----------------------------------------------------------
    # 🔹 Step 5: Doctor Alert Logic
    # -----------------------------------------------------------
    alert_sent = False
    doctor_id = None
    urgency = "low"

    if analysis_result:
        result = analysis_result[0]

        # doctor_id may return dict or string → normalize
        raw_doc = result.get("doctor_id")
        if isinstance(raw_doc, dict):
            doctor_id = raw_doc.get("doctor_id")
        else:
            doctor_id = raw_doc

        urgency = result.get("urgency", "low").lower()

    # If urgent → Send Email Alert
    if urgency in ["high", "medium"] and doctor_id:
        doctor_info = get_doctor_info_by_id(doctor_id)
        if doctor_info and "error" not in doctor_info:
            send_Alert_message_doctor(
                doctor_email=doctor_info["email"],
                doctor_name=doctor_info["name"],
                patient_id=str(patient_id),
                disease=result.get("disease", ""),
                urgency=urgency,
                transcript=transcript_text
            )
            alert_sent = True

    # -----------------------------------------------------------
    # 🔹 Step 6: Build AlertInfo object
    # -----------------------------------------------------------
    alert_info = AlertInfo(
        doctor_id=doctor_id,
        specialist=result.get("recommended_specialist", ""),
        sent=alert_sent,
        method=["email"] if alert_sent else [],
        timestamp=datetime.utcnow()
    )

    # -----------------------------------------------------------
    # 🔹 Step 7: Save Audit Review Log
    # -----------------------------------------------------------
    audit_doc = AuditReview(
        patient_id=str(patient_id),
        patient_name=patient_name,
        patient_email=patient_email,
        voice_url=voice_url,
        transcript=transcript_text,
        keywords=patient_data_db.get("symptoms", []),
        detected_disease=result.get("disease", "") if analysis_result else "",
        alert=alert_info,
        created_at=datetime.utcnow()
    )

    audit_review_col.insert_one(audit_doc.dict())
    
    # -----------------------------------------------------------
    # 🔹 Step 6: Clean up temp audio folder
    # -----------------------------------------------------------
    try:
        import shutil
        shutil.rmtree(UPLOAD_FOLDER)  # Deletes all files and folder
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Recreate empty folder
    except Exception as e:
        print("Cleanup error:", e)

    # -----------------------------------------------------------
    # 🔹 Step 8: Final Response
    # -----------------------------------------------------------
    return {
        "patient_id": str(patient_id),
        "patient_name": patient_name,
        "patient_email": patient_email,
        "transcript": transcript_text,
        "analysis": analysis_result,
        "doctor_id": doctor_id,
        "doctor_email":doctor_info["email"],
        "doctor_name":doctor_info["name"],
        "alert_sent": alert_sent,
        "urgency": urgency
    }

