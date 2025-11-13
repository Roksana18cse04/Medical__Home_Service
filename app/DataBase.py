from pymongo import MongoClient
from app.core.config import MONGO_URL,DB_NAME
import certifi
client = MongoClient(MONGO_URL,tlsCAFile=certifi.where())
db = client[DB_NAME]


doctors_col = db["doctor"]
doctor_specialists_col = db["doctor_specialists"]
patients_col = db["patient"]
audit_review_col =db["audit_patient"]
test_user = {
    "name": "John Doe",
    "email": "john@example.com",
    "role": "patient",
    "phone": "+8801700000000"
}

result = db["users"].insert_one(test_user)
print("Inserted user ID:", result.inserted_id)


# -----------------------------
# Utility: Reset/Clean DB (development only)
# -----------------------------
# def clean_db():
#     """Delete all documents from core collections (use carefully)"""
#     # doctors_col.delete_many({})
#     # doctor_specialists_col.delete_many({})
#     # patients_col.delete_many({})
#     print("All core collections cleaned successfully.")
    
# patient = patients_col.find_one({"email": "roksana.tech.2000@gmail.com"})
# print(patient)
#clean_db()
