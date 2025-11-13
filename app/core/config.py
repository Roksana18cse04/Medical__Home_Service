import os
from dotenv import load_dotenv


# Step 2: Load the file
load_dotenv(override=True)

MONGO_URL = os.getenv("MONGO_URL")
print(MONGO_URL)
DB_NAME = os.getenv("DB_NAME")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Cloudinary
CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

# Upload settings
UPLOAD_FOLDER: str = "voice_uploads"
MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
ALLOWED_AUDIO_EXTENSIONS: set = {".mp3", ".wav", ".m4a", ".webm", ".ogg"}