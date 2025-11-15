# import bcrypt
from datetime import datetime, timedelta
from bson import ObjectId
from jose import jwt, JWTError
import bcrypt
from fastapi import HTTPException, status

from app.DataBase import doctors_col, doctor_specialists_col, patients_col
from app.core.config import SECRET_KEY, ALGORITHM


# ---------------- Password Hashing ----------------
def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed_password: str):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


# ---------------- JWT Handling ----------------
def create_access_token(data: dict):
    """
    Create a JWT access token containing user_id and role.
    """
    to_encode = data.copy()
    # expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    # to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    """
    Decode JWT and return payload (user_id, role).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": payload.get("user_id"), "role": payload.get("role")}
    except JWTError as e:
        raise Exception(f"Invalid token: {str(e)}")


# ---------------- Account Creation ----------------
def create_doctor_account(data):
    existing = doctors_col.find_one({"email": data.email})
    if existing:
        return {"error": "Doctor already exists"}

    hashed_pw = hash_password(data.password)
    doctor = {
        "name": data.name,
        "email": data.email,
        "phone": data.phone,
        "type": data.type,
        "designation": data.designation,
        "specialist_info": {
            "specialist": data.specialist,
            "sub_specialist": data.sub_specialist
        },
        "password": hashed_pw,
        "role": "doctor",
        "is_verified": False,
        "otp": None,
        "created_at": datetime.utcnow()
    }

    result = doctors_col.insert_one(doctor)
    return {**doctor, "_id": str(result.inserted_id)}


def create_patient_account(data):
    existing = patients_col.find_one({"email": data.email})
    if existing:
        return {"error": "Patient already exists"}

    hashed_pw = hash_password(data.password)
    patient = {
        "name": data.name,
        "email": data.email,
        "phone": data.phone,
        "role": "patient",
        "age": data.age,
        "gender": data.gender,
        "symptoms": data.symptoms,
        "password": hashed_pw,
        "otp": None,
        "is_verified": False,
        "created_at": datetime.utcnow()
    }

    result = patients_col.insert_one(patient)
    return {**patient, "_id": str(result.inserted_id)}


# ---------------- Account Deletion ----------------
def delete_account(user_id: str, role: str):
    if role == "doctor":
        doctor_specialists_col.delete_many({"doctor_id": user_id})
        result = doctors_col.delete_one({"_id": ObjectId(user_id)})
    elif role == "patient":
        result = patients_col.delete_one({"_id": ObjectId(user_id)})
    else:
        return {"error": "Invalid role"}

    if result.deleted_count == 0:
        return {"error": "Account not found"}

    return {"message": f"{role.capitalize()} account deleted successfully"}


# ---------------- Get User Info by ID ----------------
def get_doctor_info_by_id(doctor_id: str):
    """Get doctor info by ID"""
    try:
        doctor = doctors_col.find_one(
            {"_id": ObjectId(doctor_id)},
            {"name": 1, "email": 1, "phone": 1, "specialist_info": 1}
        )
        if not doctor:
            return {"error": "Doctor not found"}

        return {
            "name": doctor["name"],
            "email": doctor["email"],
            "phone": doctor["phone"],
            "specialist": doctor["specialist_info"]["specialist"]
        }
    except Exception as e:
        return {"error": f"Invalid doctor ID: {str(e)}"}

def get_patient_info_by_id(patient_id: str):
    """Get selected patient info by ID"""
    try:
        patient = patients_col.find_one(
            {"_id": ObjectId(patient_id)},
            {
                "_id": 1,
                "name": 1,
                "email": 1,
                "phone": 1,
                "role": 1,
                "age": 1,
                "gender": 1,
                "symptoms": 1
            }
        )

        if not patient:
            return {"error": "Patient not found"}

        # Convert ObjectId → string
        patient["_id"] = str(patient["_id"])

        return patient

    except Exception as e:
        return {"error": f"Invalid patient ID: {str(e)}"}


# ---------------- Get User Info from Token ----------------
def get_user_info_by_token(authorization: str):
    """
    Get user (doctor or patient) info using an access token.
    Accepts both 'Bearer <token>' and raw '<token>'.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    # Handle both "Bearer <token>" and raw "<token>"
    if authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    else:
        token = authorization

    try:
        payload = decode_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")

    user_id = payload.get("user_id")
    role = payload.get("role")

    if not user_id or not role:
        raise HTTPException(status_code=400, detail="Invalid token payload")


    return user_id

# ---------------- Login ----------------
def login_user(email: str, password: str):
    """
    Authenticate user (doctor or patient) and return access token.
    """
    # Try doctor first
    user = doctors_col.find_one({"email": email})
    role = "doctor"

    if not user:
        # Then try patient
        user = patients_col.find_one({"email": email})
        role = "patient"

    if not user:
        return {"error": "User not found"}

    if not verify_password(password, user["password"]):
        return {"error": "Incorrect password"}

    token = create_access_token({"user_id": str(user["_id"]), "role": role})
    return {"access_token": token, "token_type": "bearer", "role": role}


# ---------------- Manual Test ----------------
if __name__ == "__main__":
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjkxNjFjMWQwNWQ5ZjhhOWVmMDI1NmQwIiwicm9sZSI6InBhdGllbnQiLCJleHAiOjE3NjMwNjY1MjN9._ylWihhRFnlCjHcnOrJx6fH1HeMktFt-2dXZNUN714M"
    info = get_user_info_by_token(test_token)
    print(info)
