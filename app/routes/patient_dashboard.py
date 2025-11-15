from fastapi import APIRouter, HTTPException, Query
from app.DataBase import patients_col, patient_visits_col, doctor_specialists_col
from pydantic import EmailStr
from app.services.auth_service import verify_password, create_access_token, create_patient_account, get_user_info_by_token
from app.services.email_service import send_verification_email_Patient
from app.schemas.user_schemas import PatientCreate
from app.schemas.auth_schemas import LoginRequest
import random

router = APIRouter(prefix="/patient", tags=["PatientDashboard"])

@router.post("/signup")
def patient_signup(data: PatientCreate):
    Patient = create_patient_account(data)
    if "error" in Patient:
        raise HTTPException(status_code=400, detail=Patient["error"])

    otp = str(random.randint(100000, 999999))
    patients_col.update_one({"email": data.email}, {"$set": {"otp": otp}})
    send_verification_email_Patient(data.email, otp)
    return {"message": "Signup successful. Check your email for OTP verification."}

@router.post("/verify")
def verify_patient(email: EmailStr, otp: str):
    patient = patients_col.find_one({"email": email})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if str(patient.get("otp")) != str(otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    patients_col.update_one({"email": email}, {"$set": {"is_verified": True, "otp": None}})
    return {"message": "Patient verified successfully"}

@router.post("/login")
def patient_login(data: LoginRequest):
    patient = patients_col.find_one({"email": data.email})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if not patient["is_verified"]:
        raise HTTPException(status_code=401, detail="Patient not verified")
    if not verify_password(data.password, patient["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_access_token({"user_id": str(patient["_id"]), "role": "patient"})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/my-visits")
async def get_my_visits(token: str = Query(...)):
    try:
        patient_id = get_user_info_by_token(token)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    visits = list(patient_visits_col.find({"patient_id": patient_id}, {"_id": 0}))
    return {"patient_id": patient_id, "total_visits": len(visits), "visits": visits}

@router.get("/specialists")
async def get_specialists():
    specialists = list(doctor_specialists_col.find({}, {"_id": 0, "doctor_id": 0}))
    return {"total_specialists": len(specialists), "specialists": specialists}

# Audio capture route for patients
from app.routes.audio_capture import audio_router
router.include_router(audio_router, prefix="", tags=["PatientAudio"])