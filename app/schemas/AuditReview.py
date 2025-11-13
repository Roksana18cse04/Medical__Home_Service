from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AlertInfo(BaseModel):
    doctor_id: Optional[str]
    specialist: Optional[str]
    sent: bool
    method: List[str]
    timestamp: Optional[datetime]

class AuditReview(BaseModel):
    patient_id: str
    voice_url: str
    transcript: str
    keywords: List[str]
    detected_disease: str
    alert: AlertInfo
    created_at: datetime

class RiskAnalysisOutput(BaseModel):
    symptoms: List[str]
    disease: str
    probability: float
    urgency: str
    possible_causes: str
    recommended_specialist: str
    advice: str
