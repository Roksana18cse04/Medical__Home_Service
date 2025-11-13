from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
import random
from fastapi import APIRouter, HTTPException, Depends, Header


from app.schemas.user import DoctorCreate, LoginRequest
from app.services.auth_service import (
    create_doctor_account,
    verify_password,
    create_access_token,
    delete_account,
    decode_access_token
)
from app.services.email_service import send_verification_email_Doctor
from app.DataBase import doctors_col, doctor_specialists_col

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
# ----------------- Get All Specialists -----------------
@router.get("/doctor/specialists")
def get_all_specialists():
    specialists = list(doctor_specialists_col.find({}, {"_id": 0}))
    return {"count": len(specialists), "specialists": specialists}
