from pydantic import BaseModel, EmailStr

# ---------------- Authentication Schemas ----------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserProfile(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    phone: str
    role: str

class OTPVerification(BaseModel):
    email: EmailStr
    otp: str