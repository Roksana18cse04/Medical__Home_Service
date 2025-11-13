from sentence_transformers import SentenceTransformer, util
from typing import List, Tuple
print("================ Loading Semantic Matcher ==================")
# Load the model globally so it’s not reloaded every call
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')  
print("================ after Loading ==================")

def get_semantic_specialist(specialist_list: List[str], ai_recommended: str, threshold: float = 0.35) -> str:
    print("========",specialist_list)

    # Encode once per call
    specialist_embeddings = model.encode(specialist_list, convert_to_tensor=True)
    ai_embedding = model.encode(ai_recommended, convert_to_tensor=True)

    # Compute cosine similarities
    cosine_scores = util.cos_sim(ai_embedding, specialist_embeddings)[0]

    # Find the highest similarity
    max_score_idx = cosine_scores.argmax()
    max_score = cosine_scores[max_score_idx].item()

    if max_score >= threshold:
        return specialist_list[max_score_idx]
    else:
        return "unknown"

# Example usage:
canonical_specialists = ["cardiology","Allergy-Doctor", "neurology", "dermatology", "pulmonology", "urology"]
ai_output = "immune specialist"
matched = get_semantic_specialist(canonical_specialists, ai_output)
print(matched)  # -> "cardiology"
