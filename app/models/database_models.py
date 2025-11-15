from typing import Dict, Any, Optional, List
from datetime import datetime

# ---------------- Database Document Models ----------------
# These represent the actual MongoDB document structure

class DoctorDocument:
    """MongoDB Doctor Document Structure"""
    def __init__(self):
        self.structure = {
            "_id": "ObjectId",
            "name": "str",
            "email": "str", 
            "phone": "str",
            "role": "str",  # "doctor"
            "type": "str",  # "Medicine" or "Surgery"
            "specialist": "str",
            "sub_specialist": "str", 
            "designation": "str",
            "password": "str",  # hashed
            "is_verified": "bool",
            "otp": "Optional[str]",
            "created_at": "datetime",
            "updated_at": "datetime"
        }

class PatientDocument:
    """MongoDB Patient Document Structure"""
    def __init__(self):
        self.structure = {
            "_id": "ObjectId",
            "name": "str",
            "email": "str",
            "phone": "str", 
            "role": "str",  # "patient"
            "age": "int",
            "gender": "str",
            "symptoms": "List[str]",
            "password": "str",  # hashed
            "is_verified": "bool",
            "is_recommended": "bool",
            "otp": "Optional[str]",
            "created_at": "datetime",
            "updated_at": "datetime"
        }

class DoctorSpecialistDocument:
    """MongoDB Doctor Specialist Document Structure"""
    def __init__(self):
        self.structure = {
            "_id": "ObjectId",
            "doctor_id": "str",
            "type": "str",
            "email": "str",
            "name": "str",
            "phone": "str",
            "specialist": "str",
            "sub_specialist": "str",
            "created_at": "datetime"
        }

class PatientVisitDocument:
    """MongoDB Patient Visit Document Structure"""
    def __init__(self):
        self.structure = {
            "_id": "ObjectId",
            "patient_id": "str",
            "patient_email": "str",
            "visit_date": "str",
            "visit_reason": "str",
            "consultation_type": "str",
            "symptoms_reported": "List[str]",
            "diagnosis_given": "Optional[str]",
            "doctor_assigned": "Optional[str]",
            "assigned_doctor_name": "Optional[str]",
            "status": "str",
            "created_at": "datetime"
        }

class AuditReviewDocument:
    """MongoDB Audit Review Document Structure"""
    def __init__(self):
        self.structure = {
            "_id": "ObjectId",
            "patient_id": "str",
            "patient_name": "str",
            "patient_email": "str",
            "voice_url": "str",
            "transcript": "str",
            "keywords": "List[str]",
            "detected_disease": "str",
            "visit_reason": "str",
            "consultation_type": "str",
            "alert": {
                "doctor_id": "Optional[str]",
                "specialist": "Optional[str]",
                "sent": "bool",
                "method": "List[str]",
                "timestamp": "Optional[datetime]"
            },
            "created_at": "datetime"
        }

class PatientHistoryDocument:
    """MongoDB Patient History Document Structure"""
    def __init__(self):
        self.structure = {
            "_id": "ObjectId",
            "patient_id": "str",
            "patient_email": "str",
            "voice_submissions": "int",
            "last_visit": "Optional[str]",
            "total_consultations": "int",
            "created_at": "Optional[str]",
            "updated_at": "datetime"
        }

class DoctorAssignmentDocument:
    """MongoDB Doctor Assignment Document Structure"""
    def __init__(self):
        self.structure = {
            "_id": "ObjectId",
            "doctor_id": "str",
            "count": "int",
            "last_assigned": "datetime",
            "updated_at": "datetime"
        }

# Collection Names
COLLECTIONS = {
    "doctors": "doctor",
    "patients": "patient", 
    "doctor_specialists": "doctor_specialists",
    "patient_visits": "patient_visits",
    "audit_reviews": "audit_patient",
    "patient_history": "patient_history",
    "doctor_assignments": "doctor_assignments"
}