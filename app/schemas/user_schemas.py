from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Literal, List

# ---------------- Doctor Schemas ----------------
class DoctorCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    role: Literal["doctor"] = "doctor"
    type: Literal["Medicine", "Surgery"]
    specialist: str
    sub_specialist: str
    designation: str
    password: str
    confirm_password: str

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

class DoctorSpecialist(BaseModel):
    doctor_id: str
    type: str
    email: EmailStr
    name: str
    phone: str
    specialist: str
    sub_specialist: str

# ---------------- Patient Schemas ----------------
class PatientCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    role: Literal["patient"] = "patient"
    age: int
    gender: Literal["male", "female", "other"]
    symptoms: List[str]
    password: str
    confirm_password: str

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v
    
    @validator("age")
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError("Age must be between 0 and 150")
        return v

class PatientInfo(BaseModel):
    name: str
    email: EmailStr
    phone: str
    age: int
    gender: str
    symptoms: List[str]
    is_verified: bool
    is_recommended: bool

class PatientHistory(BaseModel):
    patient_id: str
    patient_email: EmailStr
    voice_submissions: int
    last_visit: Optional[str]
    total_consultations: int
    created_at: Optional[str]

class PatientVisit(BaseModel):
    patient_id: str
    patient_email: EmailStr
    visit_date: str
    visit_reason: str
    consultation_type: str
    symptoms_reported: List[str]
    diagnosis_given: Optional[str]
    doctor_assigned: Optional[str]
    status: str