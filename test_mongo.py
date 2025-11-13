from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# Get MongoDB URI and DB Name
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print(f"✅ Successfully connected to database: {DB_NAME}")
    client.admin.command('ping')
    print(client.admin.command('ping'))
    # Optional: list collections
    print("Collections in DB:", db.list_collection_names())
except Exception as e:
    print("❌ Connection failed:", e)


# # Delete the test user by email
# result = db["users"].delete_one({"email": "john@example.com"})

# if result.deleted_count:
#     print("✅ Test user deleted successfully.")
# else:
#     print("⚠️ No test user found to delete.")


# # Insert dummy patient
# test_user = {
#     "name": "John Doe",
#     "email": "john@example.com",
#     "role": "patient",
#     "phone": "+8801700000000"
# }

# result = db["users"].insert_one(test_user)
# print("Inserted user ID:", result.inserted_id)

# # Fetch all users
# users = list(db["users"].find({}))
# for u in users:
#     print(u)

# # #Drop the entire users collection
# if "users" in db.list_collection_names():
#     db.drop_collection("users")
#     print("✅ 'users' collection deleted successfully.")
# else:
#     print("⚠️ 'users' collection does not exist.")