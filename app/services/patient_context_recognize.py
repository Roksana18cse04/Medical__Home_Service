from datetime import datetime
import json
import google.generativeai as genai
from app.core.config import GEMINI_API_KEY
from app.schemas.diseases import User_SymptomsRequest
from app.services.matcher import get_doctor_by_semantic_specialist
from app.DataBase import doctor_specialists_col

# ------------------- Rate-limiting setup -------------------
models_rpd = {
    "gemini-2.5-pro": 50,
    "gemini-2.5-flash": 250,
    "gemini-2.5-flash-lite": 1000,
    "gemini-2.0-flash": 200,
    "gemini-2.0-flash-lite": 200,
    "gemma-3n-e2b-it": 14400,
}

UTILIZATION_RATIO = 0.8
total_daily_limit = int(sum(models_rpd.values()) * UTILIZATION_RATIO)
requests_done = {model: 0 for model in models_rpd}
total_requests = 0

genai.configure(api_key=GEMINI_API_KEY)

# ------------------- Helper Functions -------------------
def clean_model_json(raw_text: str) -> str:
    """Clean AI response by removing Markdown or code formatting."""
    cleaned = raw_text.strip()
    if "```" in cleaned:
        cleaned = cleaned.split("```json")[-1].split("```")[0].strip()
    return cleaned.replace("\n", "").replace("\r", "")

def parse_safe_json(text: str):
    """Safely parse JSON, return dict with error if parsing fails."""
    try:
        return json.loads(text)
    except Exception as e:
        print("JSON Parse Error:", e)
        return {"error": "Invalid JSON format", "raw_output": text}

# ------------------- Main Function -------------------
def diseases_Recognize(data: User_SymptomsRequest, model_preference="gemma-3n-e2b-it"):
    """
    Recognize the best matching disease from given symptoms using Gemini API
    and attach matched doctor info from the database.
    """
    global total_requests

    if total_requests >= total_daily_limit:
        return {"error": "Reached total daily limit."}

    if requests_done.get(model_preference, 0) >= models_rpd.get(model_preference, 0):
        return {"error": f"Model {model_preference} reached its daily limit."}

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

    # ------------------- Call Gemini API -------------------
    try:
        response = genai.GenerativeModel(model_preference).generate_content(prompt)
        raw_output = response.text.strip()
    except Exception as e:
        print("Error calling Gemini API:", e)
        return {"error": str(e)}

    requests_done[model_preference] += 1
    total_requests += 1

    # ------------------- Parse and Clean AI Output -------------------
    cleaned_output = clean_model_json(raw_output)
    parsed_data = parse_safe_json(cleaned_output)

    # ------------------- Match Doctor -------------------
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
