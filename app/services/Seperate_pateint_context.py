import pickle
import numpy as np
import warnings
from sentence_transformers import SentenceTransformer
from app.utils.gemini_utils import call_gemini_api
import re
import json
import faiss
warnings.filterwarnings("ignore", category=FutureWarning)

# Load Patient Knowledge Base
with open("patient_kb.pkl", "rb") as f:
    kb_data = pickle.load(f)

faiss_index = kb_data["index"]
kb_texts = kb_data["texts"]
embedding_model_name = kb_data["model_name"]

embed_model = SentenceTransformer(embedding_model_name, device="cpu")

def search_kb(query, top_k=3):
    """Return top-k patient KB examples for a given query."""
    query_embedding = embed_model.encode([query], convert_to_numpy=True).astype("float32")
    D, I = faiss_index.search(query_embedding, top_k)
    return [kb_texts[i] for i in I[0]]

def _clean_json_response(raw):
    """Normalize Gemini output → always return a dict."""
    
    if raw is None:
        return {"patient_context": ""}

    # If raw is already a dict, convert to string safely
    if isinstance(raw, dict):
        raw = json.dumps(raw)

    # Step 1: Remove markdown fencing
    raw = re.sub(r"```(json|JSON)?", "", raw).replace("```", "").strip()

    # Step 2: Extract JSON substring
    match = re.search(r"\{[\s\S]+\}", raw)
    if match:
        raw = match.group(0)

    # Step 3: Try to parse JSON safely
    try:
        data = json.loads(raw)
    except Exception:
        # fallback: return text as patient_context
        return {"patient_context": raw}

    # Step 4: Ensure key exists
    context = data.get("patient_context", "")

    # Always return clean string
    if not isinstance(context, str):
        context = str(context)

    return {"patient_context": context.strip()}


def extract_patient_context_from_transcript(transcribed_text: str, model_preference="gemma-3n-e2b-it"):
    """
    Input:
        transcribed_text: str - raw transcript including doctor and patient conversation
        model_preference: str - Gemini AI model
    Output:
        dict: {"patient_context": "..."} strictly
    """
    # Retrieve KB Examples
    kb_examples = search_kb(transcribed_text)
    kb_str = "\n".join([f"- {ex}" for ex in kb_examples])

    # System Prompt
    system_prompt = """
You are a medical conversation analyzer. 
Extract ONLY the patient's statements from a doctor-patient conversation. 
Patient statements include:
- Descriptions of symptoms, feelings, or conditions.
- Questions the patient asks about their health.
- Statements about past medical history or medications.

Do NOT include:
- Any statements or advice from the doctor.
- Any meta-text or unrelated content.

Use the provided patient knowledge base examples to guide your extraction. 
Return STRICTLY in JSON format:

{
  "patient_context": "..."
}

Ensure the order of patient statements is preserved and do not add any interpretation.

"""

    user_prompt = f"""
Transcript:
{transcribed_text}

Relevant Knowledge Base Examples:
{kb_str}

Extract ONLY the patient context.
"""

    prompt = f"System Prompt:\n{system_prompt}\n\nUser Prompt:\n{user_prompt}"

    # Call Gemini
    response=call_gemini_api(prompt, model_preference)
    # Normalize response for API pipeline
    normalized = _clean_json_response(response)

    
    return normalized

# Usage Example
if __name__ == "__main__":
    transcript = """
I'm so sorry. Well you are only twenty five, so let's hope this is the last of the worst. Let's see how we can best help you. When did it start? 
Patient: Around eleven in the morning. 
Doctor: Today? 
Patient: Um no yesterday. July thirty first. 
Doctor: July thirty first O eight. Got it. Did it come on suddenly? 
Patient: Yeah. 
Doctor: Are you having any symptoms with it, such as blurry vision, light sensitivity, dizziness, lightheadedness, or nausea? 
Patient: I'm having blurry vision and lightheadedness.  I also can't seem to write well. It looks so messy. I am naturally right handed but my writing looks like I am trying with my left. 
Doctor: How would you describe the lightheadedness? 
Patient: Like there are blind spots. 
Doctor: Okay. How about any vomiting? 
Patient: Um no. I feel like my face is pretty swollen though. I don't know if it's related to the headache but it started around the same time. 
"""
    output = extract_patient_context_from_transcript(transcript)
    print(output)