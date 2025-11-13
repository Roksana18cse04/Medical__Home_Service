from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
import random
import jwt
from fastapi import APIRouter, HTTPException, Depends, Header


from app.schemas.user import DoctorCreate, LoginRequest
from app.services.auth_service import (
    create_doctor_account,
    verify_password,
    create_access_token,
    delete_account,
    decode_access_token,
    get_doctor_info_by_id,
    get_patient_info_by_id,
    get_user_info_by_token
)
from app.services.email_service import send_verification_email_Doctor
from app.DataBase import doctors_col, doctor_specialists_col, patients_col
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["DoctorAuth"])

# OAuth2 dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

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

# ----------------- Doctor Signup -----------------
@router.post("/doctor/signup")
def doctor_signup(data: DoctorCreate):
    doctor = create_doctor_account(data)
    if "error" in doctor:
        raise HTTPException(status_code=400, detail=doctor["error"])

    otp = str(random.randint(100000, 999999))
    doctors_col.update_one({"email": data.email}, {"$set": {"otp": otp}})
    send_verification_email_Doctor(data.email, otp)

    return {"message": "Signup successful. Check your email for OTP verification."}

# ----------------- Doctor Email Verification -----------------
@router.post("/doctor/verify")
def verify_doctor(email: EmailStr, otp: str):
    doctor = doctors_col.find_one({"email": email})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if doctor["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    doctors_col.update_one({"email": email}, {"$set": {"is_verified": True, "otp": None}})

    info = doctor["specialist_info"]
    doctor_specialists_col.insert_one({
        "type": doctor["type"],
        "email": email,
        "name": doctor["name"],
        "specialist": info["specialist"],
        "sub_specialist": info["sub_specialist"],
        "doctor_id": str(doctor["_id"])
    })

    return {"message": "Doctor verified successfully. You can now log in."}

# ----------------- Login -----------------
@router.post("/login")
def login_user(data: LoginRequest):
    user = doctors_col.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    token = create_access_token({"user_id": str(user["_id"]), "role": user["role"]})
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}

@router.delete("/delete-account")
def delete_my_account(
    authorization: str  # alias is important
):
    """
    Delete your account using JWT token from Authorization header.
    """
    print("Auth",authorization)
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

    return {"message": f"{role.capitalize()} account and related data deleted successfully"}
# ----------------- Get User Info by Token -----------------
@router.get("/user/profile")
def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's name and email using access token"""
    user_id = current_user["user_id"]
    role = current_user["role"]
    
    if role == "doctor":
        user = doctors_col.find_one({"_id": ObjectId(user_id)}, {"name": 1, "email": 1, "phone": 1})
    elif role == "patient":
        user = patients_col.find_one({"_id": ObjectId(user_id)}, {"name": 1, "email": 1, "phone": 1})
    else:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "name": user["name"],
        "email": user["email"],
        "phone": user["phone"],
        "role": role
    }

@router.get("/doctor/info/{doctor_id}")
def get_doctor_info(doctor_id: str):
    """Get doctor's name and email by doctor ID"""
    try:
        doctor = doctors_col.find_one({"_id": ObjectId(doctor_id)}, {"name": 1, "email": 1, "phone": 1, "specialist_info": 1})
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        return {
            "doctor_id": doctor_id,
            "name": doctor["name"],
            "email": doctor["email"],
            "phone": doctor["phone"],
            "specialist": doctor["specialist_info"]["specialist"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid doctor ID: {str(e)}")

@router.get("/patient/info/{patient_id}")
def get_patient_info(patient_id: str):
    """Get patient's name and email by patient ID"""
    try:
        patient = patients_col.find_one({"_id": ObjectId(patient_id)}, {"name": 1, "email": 1, "phone": 1})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return {
            "patient_id": patient_id,
            "name": patient["name"],
            "email": patient["email"],
            "phone": patient["phone"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid patient ID: {str(e)}")

# ----------------- Get All Specialists -----------------
@router.get("/doctor/specialists")
def get_all_specialists():
    specialists = list(doctor_specialists_col.find({}, {"_id": 0}))
    return {"count": len(specialists), "specialists": specialists}
