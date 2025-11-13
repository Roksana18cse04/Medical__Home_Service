from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Literal, List

# ---------------- Doctor Schema ----------------
class DoctorCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    role: Literal["doctor"] = "doctor"     # fixed role
    type: Literal["Medicine", "Surgery"]   # main type
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

# ---------------- Patient Schema ----------------
class PatientCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    role: Literal["patient"] = "patient"    # fixed role
    age: int
    gender: str
    symptoms: list[str]
    password: str
    confirm_password: str

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

# ---------------- Login Schema ----------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
