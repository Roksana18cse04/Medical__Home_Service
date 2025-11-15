import json
from app.schemas.medical_schemas import UserSymptomsRequest
from app.utils.gemini_utils import call_gemini_api
from app.services.matcher import get_doctor_by_semantic_specialist
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
def diseases_Recognize(data: User_SymptomsRequest, model_preference="gemma-3n-e2b-it"):
    """
    Recognize the best matching disease from given symptoms using Gemini API
    and attach matched doctor info from the database.
    """
    patient_age = data.age
    patient_gender = data.gender
    patient_symptoms = ", ".join(data.symptoms)

    prompt = f"""
You are a medical AI assistant trained on WHO, Mayo Clinic, and PubMed data.

### Objective:
Analyze the patient's symptoms and recommend **the single best matching disease** with probability and suggested specialist doctor.

### Patient Info:
- Age: {patient_age}
- Gender: {patient_gender}
- Symptoms: {patient_symptoms}

### Instructions:
Return a single disease that best matches all symptoms. Include:
- disease: name of disease
- probability: integer chance percentage
- possible_causes: short summary
- recommended_specialist: doctor specialist to contact
- advice: short, actionable step

Output must be pure JSON with the following schema:

{{
    "disease": "string",
    "probability": 0,
    "possible_causes": "string",
    "recommended_specialist": "string",
    "advice": "string"
}}
"""

    # Call Gemini API
    parsed_data = call_gemini_api(prompt, model_preference)
    
    if "error" in parsed_data:
        return parsed_data

    # Match Doctor
    if parsed_data and isinstance(parsed_data, dict) and "recommended_specialist" in parsed_data:
        specialist_name = parsed_data["recommended_specialist"]
        doctor_info = get_doctor_by_semantic_specialist(specialist_name)

        if doctor_info:
            parsed_data["doctor_id"] = doctor_info.get("doctor_id")
            parsed_data["matched_specialist"] = doctor_info.get("specialist")
            parsed_data["similarity"] = doctor_info.get("similarity", 0)
        else:
            parsed_data["doctor_id"] = None

    return parsed_data

# ------------------- Example Usage -------------------
if __name__ == "__main__":
    class Dummy:
        age = 32
        gender = "Female"
        symptoms = ["chest pain", "shortness of breath"]

    result = diseases_Recognize(Dummy())
    print("\nAI Diagnosis Result with Matched Doctor:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
