

# MediUrgency — Medical Home Service

**Project Summary:**

I developed MediUrgency, a backend-first medical-home-service project that ingests patient audio, extracts context and initial symptoms, profiles urgency, matches patients to doctors, and sends alerts when necessary. I implemented the FastAPI server, services for audio processing and ML profiling, and the alerting/data layers connected to MongoDB and email.

---

## My Work / Contributions

Below is a concise summary of what I implemented in this repository, mapped to the files and folders in the workspace:

* **API & App Entry Points:** I set up the FastAPI app entry at `app/main.py` and configured unified server running via `run_app.py` that launches both backend and frontend simultaneously.
* **Routes / Dashboards:** I implemented route modules under `app/routes/` for admin, doctor, and patient dashboards, as well as audio capture: `admin_dashboard.py`, `doctor_dashboard.py`, `patient_dashboard.py`, `audio_capture.py`.
* **Core Configuration & Security:** I implemented configuration and security helpers in `app/core/config.py` and `app/core/security.py`.
* **Services (Domain Logic):** In `app/services/`, I implemented:

  * `auth_service.py` — Doctor/patient signup, OTP verification, and login flows.
  * `email_service.py` — Email alerting to notify doctors.
  * `doctor_assignment.py` — Logic for assigning doctors to patients.
  * `matcher.py` — Matching logic for patient context and intent.
  * Audio/ML profiling helpers: `pateint_context_from_audio.py`, `pateint_initail_symtoms.py`, `Seperate_pateint_context.py`, `text_profilling.py`.
* **Audio Utilities & Preprocessing:** In `app/utils/`, I implemented:

  * `audio_transcribe.py`, `ProcessAudio.py`, `voice_upload.py` — Resampling, mono/16k conversion, optional VAD, and preparation for ASR.
  * `gemini_utils.py` — Wrapper utilities for Gemini API profiling calls.
* **Models & Schemas:** I created MongoDB models in `app/models/database_models.py` and Pydantic schemas in `app/schemas/` for audit, auth, medical, and user data.
* **Vector Database & Embeddings:** I implemented `app/vector_database/Embedding.py` and CSV assets for building patient/context embeddings, with a small KB stored in `patient_kb.pkl`.
* **Streamlit Demo / UI:** I added `streamlit_app.py` and `streamlit_app_updated.py` for local visualization of uploads, transcriptions, and alerts.
* **Training Loop:** I included a PyTorch/Hugging Face-style training loop for fine-tuning models, referenced in the README.
* **Tests & Sanity Checks:** I created `test_mail.py`, `test_mongo.py`, and `test_ws.py` to smoke-test email, DB, and WebSocket functionality.
* **Helpers & Scripts:** I added utilities like `gen_secret_key.py` for configuration support.

Notes:

* I kept a modular architecture, separating AI logic (transcription, profiling) from alerting and data layers, so ASR or LLM models can be swapped without changing the alert system.

---

## Backend Implementation — Completed Features

I implemented the backend system with the following concrete features:

* **Authentication & Onboarding:** Doctor and patient signup, OTP verification, and login flows (`auth_service.py` + routes).
* **Audio Ingestion & Preprocessing:** Patient audio upload endpoints with resampling, mono 16 kHz conversion, noise suppression (`ProcessAudio.py`, `voice_upload.py`).
* **Speech-to-Text:** Integration with OpenAI Whisper via `audio_transcribe.py`.
* **ML Profiling & Context Extraction:**

  * Trained ML model persisted via pickle (`patient_kb.pkl`) to extract patient-specific context (diseases, symptoms).
  * Text profiling to extract urgency levels (Low / Medium / High) using `text_profilling.py` and supporting utilities.
* **Alerts & Notifications:** Email alerts to doctors for Medium/High urgency via `email_service.py`.
* **Logging & Storage:** MongoDB persistence for transcripts, profiling results, alerts, and patient visit history (`DataBase.py` + models). Audit logs are maintained for review.
* **Access Control:** Doctors can only access their assigned patients and patient histories (enforced in routes and services).

---

## Implemented API Endpoints

**Doctor Dashboard**

| Method | Endpoint                               | Description                   |
| ------ | -------------------------------------- | ----------------------------- |
| POST   | `/doctor/signup`                       | Doctor Signup                 |
| POST   | `/doctor/verify`                       | Verify Doctor (OTP)           |
| POST   | `/doctor/login`                        | Doctor Login                  |
| GET    | `/doctor/patients`                     | Get Doctor Patients           |
| GET    | `/doctor/patient/{patient_id}/history` | Get Patient History by Doctor |
| DELETE | `/doctor/delete-account`               | Delete My Account             |
| GET    | `/doctor/profile`                      | Get User Profile              |
| GET    | `/doctor/specialists`                  | Get All Specialists           |
| GET    | `/doctor/audit-patients`               | Get Doctor Audit Patients     |

**Patient Dashboard**

| Method | Endpoint                | Description           |
| ------ | ----------------------- | --------------------- |
| POST   | `/patient/signup`       | Patient Signup        |
| POST   | `/patient/verify`       | Verify Patient (OTP)  |
| POST   | `/patient/login`        | Patient Login         |
| GET    | `/patient/my-visits`    | Get My Visits         |
| GET    | `/patient/specialists`  | Get Specialists       |
| POST   | `/patient/audio_stream` | Audio Stream / Upload |

**Admin Dashboard**

| Method | Endpoint                | Description            |
| ------ | ----------------------- | ---------------------- |
| GET    | `/admin/audit-reviews`  | Get All Audit Reviews  |
| GET    | `/admin/patients`       | Get All Patients       |
| GET    | `/admin/patient-visits` | Get All Patient Visits |

---

## Folder Structure

```
app/
├── DataBase.py           # MongoDB connection and helper functions
├── main.py               # FastAPI app entry point
├── routes/
│   ├── admin_dashboard.py
│   ├── doctor_dashboard.py
│   ├── patient_dashboard.py
│   └── audio_capture.py
├── services/
│   ├── auth_service.py
│   ├── email_service.py
│   ├── doctor_assignment.py
│   ├── matcher.py
│   ├── pateint_context_from_audio.py
│   ├── pateint_initail_symtoms.py
│   ├── Seperate_pateint_context.py
│   └── text_profilling.py
├── utils/
│   ├── audio_transcribe.py
│   ├── ProcessAudio.py
│   ├── voice_upload.py
│   └── gemini_utils.py
├── models/
│   └── database_models.py
├── schemas/
│   ├── auth_schemas.py
│   ├── medical_schemas.py
│   ├── user_schemas.py
│   └── audit_schemas.py
├── vector_database/
│   ├── Embedding.py
│   └── training_csvs...
|   main.py
|   DataBase.py
```

---

## Tech Stack

* Backend: Python + FastAPI
* Database: MongoDB (`DataBase.py`)
* Audio Processing: `pydub`, `librosa`
* ASR: OpenAI Whisper (`audio_transcribe.py`)
* ML Model: Pickled patient context KB (`patient_kb.pkl`)
* Alerts: Email via `smtplib` (`email_service.py`)
* NLP / Profiling: Gemini API (`gemini_utils.py`) and local `text_profilling.py`

---

## Quick Setup

### Prerequisites
- Python 3.12.1

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/Roksana18cse04/Medical__Home_Service.git
cd Medical__Home_Service
```

2. **Create Virtual Environment**
```bash
python -m venv .venv
```

3. **Activate Virtual Environment**
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. **Install Dependencies**
```bash
pip install -r requirements.txt
```

5. **Setup Environment File**
Create `.env` file in root directory:
```env
MONGO_URL=
DB_NAME=
#--------------------JWT -Credential API----------------------------
SECRET_KEY=
ALGORITHM=
#app name :HomeCare_hospital------------------Email App PassWord----------------
EMAIL_USER=
EMAIL_PASS=
#-------------------GEMINI_API_KEY--------------------
GEMINI_API_KEY=
#----------------Cloudinary CredenSial ---------------
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

TF_ENABLE_ONEDNN_OPTS=0
```

6. **Run Application**
```bash
python run_app.py
```

### Access
- **Backend API:** http://localhost:8000

---

## Future Improvements

* Implement patient profile edit-able and Report and Previous Medical History Add
* Add chatbot for Primary medical Need for Daily Uses
* Include CI/CD and `.env.example` for environment configuration.

