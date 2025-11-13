
import os
import cloudinary
import cloudinary.uploader
from app.core.config import CLOUDINARY_API_KEY,CLOUDINARY_API_SECRET,CLOUDINARY_CLOUD_NAME,MAX_FILE_SIZE,ALLOWED_AUDIO_EXTENSIONS
from typing import Union

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

def upload_file(file_path: str, folder: str = None) -> dict:

        
    try:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            return {"error": f"File too large: {file_size} bytes"}

        # Check file extension for audio files
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ALLOWED_AUDIO_EXTENSIONS:
            return {"error": f"Unsupported file type: {ext}"}

        result = cloudinary.uploader.upload(
            file_path,
            folder=folder,
            resource_type="auto"
        )

        # return {
        #     "message": "File uploaded successfully",
        #     "file_url": result.get("secure_url"),
        #     "public_id": result.get("public_id"),
        #     "resource_type": result.get("resource_type"),
        #     "bytes": result.get("bytes"),
        # }
        return result.get("secure_url")
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}


if __name__ == "__main__":
    file_path = "recordings\patient_final.wav"  # any file: .wav, .mp3, .png, .pdf, etc.
    print(os.path.exists(file_path))  # just to verify the file exists
    response = upload_file(file_path)
    print(response)
