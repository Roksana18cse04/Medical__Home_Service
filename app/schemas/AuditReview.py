from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class AlertInfo(BaseModel):
    doctor_id: Optional[str] = None
    specialist: Optional[str] = None
    sent: bool = False
    method: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AuditReview(BaseModel):
    patient_id: str
    voice_url: Optional[HttpUrl] = None  # Cloud URL for audio
    transcript: str
    keywords: List[str] = []
    detected_disease: Optional[str] = ""
    alert: AlertInfo
    created_at: datetime = Field(default_factory=datetime.utcnow)
