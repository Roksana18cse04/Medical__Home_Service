from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", module="tensorflow")
warnings.filterwarnings("ignore", category=FutureWarning)
from app.routes.doctor_dashboard import router as doctor_dashboard_router
from app.routes.doctor_dashboard import router as doctor_dashboard_router
from app.routes.patient_dashboard import router as patient_dashboard_router
from app.routes.admin_dashboard import router as admin_dashboard_router

app = FastAPI(title="HomeCare Hospital API")

# ------------------- CORS Setup -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- Routers -------------------
app.include_router(doctor_dashboard_router)
app.include_router(patient_dashboard_router)
app.include_router(admin_dashboard_router)

# ✅ Root GET route
@app.get("/")
def root():
    return {
        "message": "Welcome to HomeCare Hospital API",
        "status": "Running",
    }