from fastapi import APIRouter
from app.DataBase import patients_col, patient_visits_col, audit_review_col

router = APIRouter(prefix="/admin", tags=["AdminDashboard"])

@router.get("/audit-reviews")
async def get_all_audit_reviews():
    """
    Returns all audit review logs for admin.
    """
    audits = list(audit_review_col.find({}, {"_id": 0}))
    return {"total_audits": len(audits), "audits": audits}

@router.get("/patients")
async def get_all_patients():
    """
    Returns all patients without sensitive data.
    """
    patients = list(patients_col.find({}, {"_id": 0, "password": 0, "confirm_password": 0, "otp": 0}))
    return {"total_patients": len(patients), "patients": patients}

@router.get("/patient-visits")
async def get_all_patient_visits():
    """
    Returns all patient visits for admin monitoring.
    """
    visits = list(patient_visits_col.find({}, {"_id": 0}))
    return {"total_visits": len(visits), "visits": visits}