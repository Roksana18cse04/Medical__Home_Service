from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.security import OAuth2PasswordBearer
from app.DataBase import doctors_col, doctor_specialists_col, patients_col, patient_visits_col, audit_review_col
from pydantic import EmailStr
from app.services.auth_service import hash_password, verify_password, create_access_token, get_user_info_by_token, decode_access_token, delete_account
from app.services.email_service import send_verification_email_Doctor
from app.schemas.user_schemas import DoctorCreate
from app.schemas.auth_schemas import LoginRequest
from bson import ObjectId
import random

router = APIRouter(prefix="/doctor", tags=["DoctorDashboard"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/doctor/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/signup")
def doctor_signup(data: DoctorCreate):
    if doctors_col.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(data.password)
    doctor_data = {
        "name": data.name,
        "email": data.email,
        "phone": data.phone,
        "role": data.role,
        "type": data.type,
        "specialist": data.specialist,
        "sub_specialist": data.sub_specialist,
        "designation": data.designation,
        "password": hashed_password,
        "is_verified": False
    }
    
    result = doctors_col.insert_one(doctor_data)
    otp = str(random.randint(100000, 999999))
    doctors_col.update_one({"email": data.email}, {"$set": {"otp": otp}})
    send_verification_email_Doctor(data.email, otp)
    return {"message": "Signup successful. Check email for OTP."}

@router.post("/verify")
def verify_doctor(email: EmailStr, otp: str):
    doctor = doctors_col.find_one({"email": email})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if str(doctor.get("otp")) != str(otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    doctors_col.update_one({"email": email}, {"$set": {"is_verified": True, "otp": None}})
    
    doctor_specialists_col.insert_one({
        "doctor_id": str(doctor["_id"]),
        "type": doctor["type"],
        "email": email,
        "name": doctor["name"],
        "phone": doctor["phone"],
        "specialist": doctor["specialist"],
        "sub_specialist": doctor["sub_specialist"]
    })
    
    return {"message": "Doctor verified successfully"}

@router.post("/login")
def doctor_login(data: LoginRequest):
    doctor = doctors_col.find_one({"email": data.email})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if not doctor["is_verified"]:
        raise HTTPException(status_code=401, detail="Doctor not verified")
    if not verify_password(data.password, doctor["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    token = create_access_token({"user_id": str(doctor["_id"]), "role": "doctor"})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/patients")
async def get_doctor_patients(token: str = Query(...)):
    try:
        doctor_id = get_user_info_by_token(token)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get patients from visits and audit logs
    visits = list(patient_visits_col.find({"doctor_assigned": doctor_id}, {"_id": 0}))
    audits = list(audit_review_col.find({"alert.doctor_id": doctor_id}, {"_id": 0}))
    
    # Combine visit and audit data
    all_patients = visits + audits
    return {"doctor_id": doctor_id, "total_patients": len(all_patients), "patients": all_patients}

@router.get("/patient/{patient_id}/history")
async def get_patient_history_by_doctor(patient_id: str, token: str = Query(...)):
    try:
        doctor_id = get_user_info_by_token(token)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    visits = list(patient_visits_col.find({"patient_id": patient_id}, {"_id": 0}))
    return {"patient_id": patient_id, "total_visits": len(visits), "visits": visits}

@router.delete("/delete-account")
def delete_my_account(authorization: str):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    
    token = authorization.split(" ")[1]
    try:
        payload = decode_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")

    user_id = payload.get("user_id")
    role = payload.get("role")

    if not user_id or not role:
        raise HTTPException(status_code=400, detail="Invalid token payload")

    result = delete_account(user_id, role)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {"message": f"{role.capitalize()} account deleted successfully"}

# @router.get("/profile")
# def get_user_profile(current_user: dict = Depends(get_current_user)):
#     user_id = current_user["user_id"]
#     role = current_user["role"]
    
#     if role == "doctor":
#         user = doctors_col.find_one({"_id": ObjectId(user_id)}, {"name": 1, "email": 1, "phone": 1})
#     else:
#         raise HTTPException(status_code=400, detail="Invalid role")
    
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     return {
#         "user_id": user_id,
#         "name": user["name"],
#         "email": user["email"],
#         "phone": user["phone"],
#         "role": role
#     }

@router.get("/specialists")
def get_all_specialists():
    specialists = list(doctor_specialists_col.find({}, {"_id": 0, "doctor_id": 0}))
    return {"count": len(specialists), "specialists": specialists}

@router.get("/audit-patients")
async def get_doctor_audit_patients(token: str = Query(...)):
    try:
        doctor_id = get_user_info_by_token(token)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get patients from audit logs where doctor was alerted
    audits = audit_review_col.find({"alert.doctor_id": doctor_id})
    results = []
    
    for audit in audits:
        results.append({
            "patient_id": audit.get("patient_id"),
            "patient_name": audit.get("patient_name"),
            "patient_email": audit.get("patient_email"),
            "voice_url": audit.get("voice_url"),
            "transcript": audit.get("transcript"),
            "alert_sent": audit.get("alert", {}).get("sent", False),
            "alert_method": audit.get("alert", {}).get("method", [])
        })
    
    return {"doctor_id": doctor_id, "total_audit_patients": len(results), "patients": results}