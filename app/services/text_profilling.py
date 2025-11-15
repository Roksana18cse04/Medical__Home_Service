from datetime import datetime
import json
from app.utils.gemini_utils import call_gemini_api
from app.DataBase import doctor_specialists_col
from app.services.matcher import get_doctor_by_semantic_specialist

def Risk_Analysis(data, model_preference="gemma-3n-e2b-it"):
    # Patient Data
    patient_age = data.get("age")
    patient_gender = data.get("gender",)
    patient_current_situation = data.get("current_situation")
    patient_previous_situation = data.get("previous_situation")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    patient_text = (
        f"Previous condition: {patient_previous_situation}\n"
        f"Current condition: {patient_current_situation}"
    )

    # AI Prompt
    prompt = f"""
You are an AI-powered medical triage assistant (trained on WHO, Mayo Clinic, and PubMed data).

### Objective:
Analyze the patient's description and extract:
1. Key symptoms
2. Urgency level (high, medium, low)
3. Probable disease name
4. Which specialist doctor to contact
5. Brief medical advice

### Patient Data:
- Age: {patient_age}
- Gender: {patient_gender}
- Description: {patient_text}
- Time: {timestamp}

### Output Schema (must be valid JSON):
[
  {{
    "symptoms": ["string"],
    "disease": "string",
    "probability": 0,
    "urgency": "string",
    "possible_causes": "string",
    "recommended_specialist": "string",
    "advice": "string"
  }}
]
Only return the JSON, nothing else.
"""

    # Call Gemini API
    parsed_data = call_gemini_api(prompt, model_preference)
    
    if "error" in parsed_data:
        return [parsed_data]
    
    if not isinstance(parsed_data, list):
        parsed_data = [parsed_data]

    # Match Doctor from DB
    if parsed_data and "recommended_specialist" in parsed_data[0]:
        specialist_name = parsed_data[0]["recommended_specialist"]
        doctor_id = get_doctor_by_semantic_specialist(specialist_name)
        parsed_data[0]["doctor_id"] = doctor_id

    return parsed_data

# ------------------- Example Test -------------------
if __name__ == "__main__":
    class DummyPatient:
        age = 29
        gender = "Female"
        previous_situation = "আগে একটু মাথা ব্যথা থাকতো কিন্তু এখন ভালো।"
        current_situation = (
            "গতকাল থেকে বুক ধড়ফড় করছে, মাথা ঘোরে, শ্বাস নিতে কষ্ট হয়। মাঝে মাঝে বুকে ব্যথা হয়।"
        )

    result = Risk_Analysis(DummyPatient(), model_preference="gemma-3n-e2b-it")
    print("\n🩺 AI Diagnosis Result:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
