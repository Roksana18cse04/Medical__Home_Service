from datetime import datetime
import json
import google.generativeai as genai
from app.core.config import GEMINI_API_KEY
from app.schemas.diseases import User_SymptomsRequest
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

print(f"Dynamic total daily limit set to: {total_daily_limit} requests/day (at {UTILIZATION_RATIO*100}% utilization)\n")

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

def match_specialist_db(ai_specialist: str):
    """
    Match AI recommended specialist to DB entry.
    Returns the specialist document from DB if found.
    """
    ai_lower = ai_specialist.lower()
    db_specs = list(doctor_specialists_col.find({}, {"_id": 0}))
    
    for spec in db_specs:
        spec_name_lower = spec["specialist"].lower()
        sub_spec_lower = spec.get("sub_specialist", "").lower()
        
        if "cardio" in ai_lower and "heart" in spec_name_lower:
            return spec
        elif "pulmon" in ai_lower and "medicine" in spec["type"].lower():
            return spec
        elif "general" in ai_lower and "medicine" in spec["type"].lower():
            return spec
    return None

def attach_db_specialist(ai_diagnosis: list):
    """
    Attach matched DB specialist info to each AI diagnosis entry.
    """
    for entry in ai_diagnosis:
        matched_doc = match_specialist_db(entry.get("recommended_specialist", ""))
        entry["matched_doctor"] = matched_doc
    return ai_diagnosis

# ------------------- Main Function -------------------
def diseases_Recognize(data: User_SymptomsRequest, model_preference="gemma-3n-e2b-it"):
    """
    Recognize diseases based on patient symptoms using Gemini API
    and attach matched doctor from the database.
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
You are an experienced AI medical assistant trained on reliable medical sources (WHO, Mayo Clinic, PubMed).

### Objective:
Analyze patient data and symptoms to identify possible diseases with probability and recommend the right doctor.

### Patient Info:
- Age: {patient_age}
- Gender: {patient_gender}
- Symptoms: {patient_symptoms}

### Instructions:
1. Identify 2–3 most probable diseases.
2. For each, return:
   - disease: name of disease
   - probability: chance percentage (integer)
   - possible_causes: short cause summary (max 2 lines)
   - recommended_specialist: which doctor to see (e.g. Cardiologist, Dermatologist)
   - advice: short, actionable step (1–2 lines)
3. Output must be pure JSON, nothing else. Use this exact schema:

[
  {{
    "disease": "string",
    "probability": 0,
    "possible_causes": "string",
    "recommended_specialist": "string",
    "advice": "string"
  }}
]
"""

    # ------------------- Call Gemini API -------------------
    try:
        response = genai.GenerativeModel(model_preference).generate_content(prompt)
    except Exception as e:
        print("Error calling Gemini API:", e)
        return {"error": str(e)}

    requests_done[model_preference] += 1
    total_requests += 1

    raw_output = response.text.strip()
    cleaned_output = clean_model_json(raw_output)
    parsed_data = parse_safe_json(cleaned_output)

    # ------------------- Attach DB specialist -------------------
    final_result = attach_db_specialist(parsed_data)
    

    return final_result

# ------------------- Example Usage -------------------
if __name__ == "__main__":
    class Dummy:
        age = 32
        gender = "Female"
        symptoms = ["chest pain", "shortness of breath"]

    result = diseases_Recognize(Dummy())
    print("\n AI Diagnosis Result with Matched Doctors:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
