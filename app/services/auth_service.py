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
    import jwt
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

# ---------------- Get User Info ----------------
def get_doctor_info_by_id(doctor_id: str):
    """Get doctor info by ID"""
    try:
        doctor = doctors_col.find_one({"_id": ObjectId(doctor_id)}, {"name": 1, "email": 1, "phone": 1, "specialist_info": 1})
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
    """Get patient info by ID"""
    try:
        patient = patients_col.find_one({"_id": ObjectId(patient_id)}, {"name": 1, "email": 1, "phone": 1})
        if not patient:
            return {"error": "Patient not found"}
        
        return {
            "name": patient["name"],
            "email": patient["email"],
            "phone": patient["phone"]
        }
    except Exception as e:
        return {"error": f"Invalid patient ID: {str(e)}"}

def get_user_info_by_token(token: str):
    """Get user name and email by access token for notifications"""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        role = payload.get("role")
        
        if not user_id or not role:
            return {"error": "Invalid token payload"}
        
        if role == "doctor":
            return get_doctor_info_by_id(user_id)
        elif role == "patient":
            return get_patient_info_by_id(user_id)
        else:
            return {"error": "Invalid role"}
    except Exception as e:
        return {"error": f"Invalid token: {str(e)}"}

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


l=get_doctor_info_by_id("691600e59191af1768e87246")
print(l)