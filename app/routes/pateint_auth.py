from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from app.DataBase import patients_col, doctors_col, doctor_specialists_col
from app.services.auth_service import hash_password, verify_password, create_access_token, decode_access_token,create_patient_account
from app.services.email_service import send_verification_email_Patient
from app.services.patient_context_recognize import diseases_Recognize
from app.schemas.user import PatientCreate ,LoginRequest
import random

router = APIRouter(prefix="/patient", tags=["PatientAuth"])


# ---------------- Signup ----------------
@router.post("/signup")
def patient_signup(data: PatientCreate):
    Patient = create_patient_account(data)
    if "error" in Patient:
        raise HTTPException(status_code=400, detail=Patient["error"])

    otp = str(random.randint(100000, 999999))
    patients_col.update_one({"email": data.email}, {"$set": {"otp": otp}})
    send_verification_email_Patient(data.email, otp)
    return {"message": "Signup successful. Check your email for OTP verification."}
#----------------------Patient/verify--------------------------

@router.post("/verify")
def verify_patient(email: EmailStr, otp: str):
    print("email---",email)
    patient = patients_col.find_one({"email": email})
    print("==========",patient)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if str(patient.get("otp")) != str(otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Mark verified and clear OTP
    patients_col.update_one({"email": email}, {"$set": {"is_verified": True, "otp": None}})

    # Trigger doctor recommendation only if symptoms exist
    if not patient.get("symptoms"):
        return {"message": "Patient verified but no symptoms submitted yet."}

    from app.schemas.diseases import User_SymptomsRequest
    symptoms_request = User_SymptomsRequest(
        age=patient["age"],
        gender=patient["gender"],
        symptoms=patient["symptoms"]
    )
    diagnosis = diseases_Recognize(symptoms_request)
    print(diagnosis)

    # `diagnosis` is already a list of dicts
    recommended_doctors = diagnosis  # contains AI diagnosis + matched DB doctor

    # Mark patient as recommended
    patients_col.update_one({"email": email}, {"$set": {"is_recommended": True}})

    return {
        "message": "Patient verified successfully. Doctor recommendations generated.",
        "recommendations": recommended_doctors
    }

# ---------------- Login ----------------
@router.post("/login")
def patient_login(data:LoginRequest ):
    patient = patients_col.find_one({"email": data.email})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if not patient["is_verified"]:
        raise HTTPException(status_code=401, detail="Patient not verified")
    if not verify_password(data.password, patient["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_access_token({"user_id": str(patient["_id"]), "role": "patient"})
    return {"access_token": token, "token_type": "bearer"}