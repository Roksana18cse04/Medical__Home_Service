import json
import google.generativeai as genai
from app.core.config import GEMINI_API_KEY

# ------------------- Rate Limiting Config -------------------
MODELS_RPD = {
    "gemini-2.5-pro": 50,
    "gemini-2.5-flash": 250,
    "gemini-2.5-flash-lite": 1000,
    "gemini-2.0-flash": 200,
    "gemini-2.0-flash-lite": 200,
    "gemma-3n-e2b-it": 14400,
}

UTILIZATION_RATIO = 0.8
TOTAL_DAILY_LIMIT = int(sum(MODELS_RPD.values()) * UTILIZATION_RATIO)

# Global counters
requests_done = {model: 0 for model in MODELS_RPD}
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

def check_rate_limits(model_preference: str) -> dict:
    """Check if rate limits are exceeded."""
    global total_requests
    
    if total_requests >= TOTAL_DAILY_LIMIT:
        return {"error": "Reached total daily limit."}
    
    if requests_done.get(model_preference, 0) >= MODELS_RPD.get(model_preference, 0):
        return {"error": f"Model {model_preference} reached its daily limit."}
    
    return {"status": "ok"}

def call_gemini_api(prompt: str, model_preference: str = "gemma-3n-e2b-it"):
    """Make API call to Gemini and handle rate limiting."""
    global total_requests
    
    # Check rate limits
    limit_check = check_rate_limits(model_preference)
    if "error" in limit_check:
        return limit_check
    
    try:
        response = genai.GenerativeModel(model_preference).generate_content(prompt)
        requests_done[model_preference] += 1
        total_requests += 1
        
        cleaned_output = clean_model_json(response.text.strip())
        return parse_safe_json(cleaned_output)
        
    except Exception as e:
        print("Error calling Gemini API:", e)
        return {"error": str(e)}