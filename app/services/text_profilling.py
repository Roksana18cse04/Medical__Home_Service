from datetime import datetime
import json
import google.generativeai as genai
from app.core.config import GEMINI_API_KEY
from app.DataBase import doctor_specialists_col
from app.services.matcher import get_doctor_by_semantic_specialist

# ------------------- Gemini Model Config -------------------
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

# ------------------- Helpers -------------------
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
        return [{"error": "Invalid JSON format", "raw_output": text}]

# ------------------- MAIN FUNCTION -------------------
def Risk_Analysis(data, model_preference="gemma-3n-e2b-it"):
    global total_requests

    # ------------------- Limit Checks -------------------
    if total_requests >= total_daily_limit:
        return [{"error": "Reached total daily limit."}]

    if requests_done.get(model_preference, 0) >= models_rpd.get(model_preference, 0):
        return [{"error": f"Model {model_preference} reached its daily limit."}]

    # ------------------- Patient Data -------------------
    patient_age = getattr(data, "age", "Unknown")
    patient_gender = getattr(data, "gender", "Unknown")
    patient_previous_situation = getattr(data, "previous_situation", "None provided")
    patient_current_situation = getattr(data, "current_situation", "None provided")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    patient_text = (
        f"Previous condition: {patient_previous_situation}\n"
        f"Current condition: {patient_current_situation}"
    )

    # ------------------- AI Prompt -------------------
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

    # ------------------- Gemini API Call -------------------
    try:
        response = genai.GenerativeModel(model_preference).generate_content(prompt)
    except Exception as e:
        print("Error calling Gemini API:", e)
        return [{"error": str(e)}]

    requests_done[model_preference] += 1
    total_requests += 1

    # ------------------- Parse AI Response -------------------
    raw_output = response.text.strip()
    cleaned_output = clean_model_json(raw_output)
    parsed_data = parse_safe_json(cleaned_output)

    # ------------------- Match Doctor from DB -------------------
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
