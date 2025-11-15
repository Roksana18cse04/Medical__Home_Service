from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
# Import RiskAnalysisOutput from medical_schemas to avoid circular import
from app.schemas.medical_schemas import RiskAnalysisOutput
# ---------------- Audit & Review Schemas ----------------
class AlertInfo(BaseModel):
    doctor_id: Optional[str]
    specialist: Optional[str]
    sent: bool
    method: List[str]
    timestamp: Optional[datetime]

class AuditReview(BaseModel):
    patient_id: str
    patient_name: str
    patient_email: EmailStr
    voice_url: str
    transcript: str
    keywords: List[str]
    detected_disease: str
    visit_reason: str
    consultation_type: str
    alert: AlertInfo
    created_at: datetime

class AudioAnalysisRequest(BaseModel):
    patient_id: str
    audio_file_path: str

class AudioAnalysisResponse(BaseModel):
    patient_id: str
    transcript: str
    analysis: List[RiskAnalysisOutput]
    alert_sent: bool
    doctor_assigned: Optional[str]

