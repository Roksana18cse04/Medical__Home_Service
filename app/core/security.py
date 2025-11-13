from jose import jwt, JWTError
from fastapi import WebSocket
from app.core.config import SECRET_KEY

def verify_token(token: str):
    """
    Validate JWT token and extract payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        patient_id = payload.get("patient_id")

        if not patient_id:
            raise ValueError("Missing patient_id in token")
        return patient_id

    except JWTError:
        raise ValueError("Invalid or expired JWT")
