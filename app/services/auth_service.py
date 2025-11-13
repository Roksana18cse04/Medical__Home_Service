import bcrypt
import jwt
from datetime import datetime, timedelta
from bson import ObjectId
from app.DataBase import doctors_col, doctor_specialists_col, patients_col
from app.core.config import SECRET_KEY, ALGORITHM


# ---------------- Password ----------------
def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed_password: str):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())




# ---------------- JWT ----------------
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.core.config import SECRET_KEY, ALGORITHM

# ---------------- JWT ----------------
def create_access_token(data: dict, expires_delta: int = 60):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    # Using python-jose
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": payload.get("user_id"), "role": payload.get("role")}
    except JWTError as e:
        raise Exception(f"Invalid token: {str(e)}")


# ---------------- Signup ----------------
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
        "is_verified": False,  # OTP verification required
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
        "otp":None,  # save OTP for verification
        "is_verified": False,
        "created_at": datetime.utcnow()
    }

    result = patients_col.insert_one(patient)
    return {**patient, "_id": str(result.inserted_id)}

# ---------------- Delete Account ----------------
def delete_account(user_id: str, role: str):
    if role == "doctor":
        # Remove from specialists first
        doctor_specialists_col.delete_many({"doctor_id": user_id})
        result = doctors_col.delete_one({"_id": ObjectId(user_id)})
    elif role == "patient":
        result = patients_col.delete_one({"_id": ObjectId(user_id)})
    else:
        return {"error": "Invalid role"}

    if result.deleted_count == 0:
        return {"error": "Account not found"}

    return {"message": f"{role.capitalize()} account deleted successfully"}

# ---------------- Login ----------------
def login_user(email: str, password: str):
    # Check both collections
    user = doctors_col.find_one({"email": email})
    role = "doctor"
    if not user:
        user = patients_col.find_one({"email": email})
        role = "patient"
    if not user:
        return {"error": "User not found"}

    if not verify_password(password, user["password"]):
        return {"error": "Incorrect password"}

    # JWT token
    token = create_access_token({"user_id": str(user["_id"]), "role": role})
    return {"access_token": token, "token_type": "bearer", "role": role}
