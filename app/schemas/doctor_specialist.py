from pydantic import BaseModel

class DoctorSpecialist(BaseModel):
    doctor_id: str
    type: str
    specialist: str
    sub_specialist: str
