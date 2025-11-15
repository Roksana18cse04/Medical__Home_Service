from pydantic import BaseModel
from typing import List, Optional

# ---------------- Medical & Disease Schemas ----------------
class UserSymptomsRequest(BaseModel):
    age: int
    gender: str
    symptoms: List[str]

class RiskAnalysisInput(BaseModel):
    age: int
    gender: str
    symptoms: List[str]
    current_situation: str

class RiskAnalysisOutput(BaseModel):
    symptoms: List[str]
    disease: str
    probability: float
    urgency: str
    possible_causes: str
    recommended_specialist: str
    advice: str

class DiagnosisResult(BaseModel):
    disease: str
    probability: float
    recommended_specialist: str
    doctor_id: Optional[str]
    urgency: str