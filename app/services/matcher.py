from sentence_transformers import SentenceTransformer, util
from typing import List, Optional
from app.DataBase import doctor_specialists_col  # MongoDB collection

# ------------------- Load Model Globally -------------------
print("================ Loading Semantic Matcher ==================")
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
print("================ Model Loaded ==================")

# ------------------- Semantic Specialist + Doctor Fetch -------------------
def get_doctor_by_semantic_specialist(
    ai_recommended: str,
    threshold: float = 0.35
) -> Optional[dict]:
    """
    Match AI recommended specialist to DB specialist using semantic search,
    then return doctor info: doctor_id, name, email, specialist.
    """
    # Fetch all specialists from DB
    doctors = list(doctor_specialists_col.find({}, {"_id":0, "doctor_id":1, "name":1, "email":1, "specialist":1}))
    print("=================",doctors)
    
    if not doctors:
        return None

    # Prepare list of canonical specialist names
    specialist_list = [doc["specialist"] for doc in doctors]

    # Encode embeddings
    specialist_embeddings = model.encode(specialist_list, convert_to_tensor=True)
    ai_embedding = model.encode(ai_recommended, convert_to_tensor=True)

    # Compute cosine similarities
    cosine_scores = util.cos_sim(ai_embedding, specialist_embeddings)[0]
    max_idx = cosine_scores.argmax()
    max_score = cosine_scores[max_idx].item()

    if max_score >= threshold:
        # Return matched doctor info
        matched_doctor = doctors[max_idx]
        matched_doctor["similarity"] = max_score
        return matched_doctor
    else:
        return None

# ------------------- Example Usage -------------------
if __name__ == "__main__":
    ai_specialist = "immune specialist"
    doctor_info = get_doctor_by_semantic_specialist(ai_specialist)
    print(doctor_info)
    # Example Output:
    # {
    #   "doctor_id": "D123",
    #   "name": "Dr. John Doe",
    #   "email": "john@example.com",
    #   "specialist": "immunology",
    #   "similarity": 0.68
    # }
