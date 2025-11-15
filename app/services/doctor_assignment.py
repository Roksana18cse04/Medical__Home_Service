from app.DataBase import doctor_specialists_col, doctor_assignment_col

def assign_doctor_equally(specialist_type: str):
    """
    Assigns doctor based on equal distribution (round-robin)
    """
    # Get all doctors with this specialty
    doctors = list(doctor_specialists_col.find({"specialist": specialist_type}))
    
    if not doctors:
        return None
    
    # Get assignment counts for these doctors
    assignments = {}
    for doctor in doctors:
        doc_id = doctor["doctor_id"]
        assignment_record = doctor_assignment_col.find_one({"doctor_id": doc_id})
        assignments[doc_id] = assignment_record["count"] if assignment_record else 0
    
    # Find doctor with minimum assignments
    min_assigned_doctor = min(assignments, key=assignments.get)
    
    # Update assignment count
    doctor_assignment_col.update_one(
        {"doctor_id": min_assigned_doctor},
        {"$inc": {"count": 1}},
        upsert=True
    )
    
    # Return doctor info
    assigned_doctor = next(d for d in doctors if d["doctor_id"] == min_assigned_doctor)
    return assigned_doctor