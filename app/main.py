from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.doctor_auth import router as auth_router
from app.routes.pateint_auth import router as auth_patient_router
from app.routes.audio_capture import audio_router

app = FastAPI(title="HomeCare Hospital API")

# ------------------- CORS Setup -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # for development, later replace with frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- Routers -------------------
app.include_router(auth_router)
app.include_router(auth_patient_router)

app.include_router(audio_router)  # attach MY audio_stream endpoint

# ✅ Root GET route
@app.get("/")
def root():
    return {
        "message": "Welcome to HomeCare Hospital API",
        "status": "Running",
    }