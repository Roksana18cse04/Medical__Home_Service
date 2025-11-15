import streamlit as st
import requests
import json
from io import BytesIO
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os

# Load specialist and designation data
@st.cache_data
def load_specialists():
    try:
        with open('app/data/Spesalist.json', 'r') as f:
            data = json.load(f)
            return [spec['canonical'].replace('_', ' ').title() for spec in data['specialists']]
    except:
        return ["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Internal Medicine"]

@st.cache_data
def load_designations():
    try:
        with open('app/data/designations.json', 'r') as f:
            data = json.load(f)
            return data['designations']
    except:
        return ["Consultant", "Senior Consultant", "Specialist Doctor", "Medical Officer"]

# Configure Streamlit page
st.set_page_config(
    page_title="MediUrgency - Healthcare Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def show_doctor_main_dashboard():
    st.markdown("""
    <div class="main-header">
        <h1>👨⚕️ Doctor Dashboard</h1>
        <p>Welcome to your medical practice management system</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Logout"):
        del st.session_state.doctor_token
        st.rerun()
    
    page = st.sidebar.selectbox("Navigation", ["📊 Dashboard", "👥 My Patients", "📋 Analytics", "🔊 Audio Analysis", "📅 Patient History"])
    
    if page == "📊 Dashboard":
        show_doctor_overview()
    elif page == "👥 My Patients":
        show_doctor_patients()
    elif page == "📋 Analytics":
        show_doctor_analytics()
    elif page == "🔊 Audio Analysis":
        show_audio_analysis()
    elif page == "📅 Patient History":
        show_doctor_patient_history()

def show_patient_main_dashboard():
    st.markdown("""
    <div class="main-header">
        <h1>👤 Patient Dashboard</h1>
        <p>Your personal health management portal</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Logout"):
        del st.session_state.patient_token
        st.rerun()
    
    page = st.sidebar.selectbox("Navigation", ["📊 Dashboard", "🏥 My Visits", "👨⚕️ Specialists", "🔊 Audio Analysis", "📋 Audio History"])
    
    if page == "📊 Dashboard":
        show_patient_overview()
    elif page == "🏥 My Visits":
        show_patient_visits()
    elif page == "👨⚕️ Specialists":
        show_patient_specialists()
    elif page == "🔊 Audio Analysis":
        show_audio_analysis()
    elif page == "📋 Audio History":
        show_audio_history()

def show_doctor_overview():
    st.header("📊 Doctor Overview")
    col1, col2, col3 = st.columns(3)
    
    try:
        response = requests.get(f"{API_BASE}/doctor/patients", params={"token": st.session_state.doctor_token})
        if response.status_code == 200:
            data = response.json()
            with col1:
                st.metric("Total Patients", data['total_patients'])
    except:
        pass
    
    with col2:
        st.metric("Today's Appointments", "5")
    with col3:
        st.metric("Pending Reviews", "3")

def show_doctor_patients():
    st.header("👥 My Patients")
    try:
        response = requests.get(f"{API_BASE}/doctor/patients", params={"token": st.session_state.doctor_token})
        if response.status_code == 200:
            data = response.json()
            if data["patients"]:
                # Display patients in cards with action buttons
                for i, patient in enumerate(data["patients"]):
                    with st.expander(f"Patient {i+1} - {patient.get('patient_name', 'N/A')}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**👤 Name:** {patient.get('patient_name', 'N/A')}")
                            st.write(f"**📧 Email:** {patient.get('patient_email', 'N/A')}")
                        
                        with col2:
                            st.write(f"**📅 Visit Date:** {patient.get('visit_date', 'N/A')}")
                            st.write(f"**🎯 Status:** {patient.get('status', 'N/A')}")
                        
                        with col3:
                            if st.button(f"📄 View History", key=f"history_{i}"):
                                st.session_state.selected_patient_id = patient.get('patient_id')
                                st.session_state.show_patient_detail = True
                                st.rerun()
            else:
                st.info("No patients assigned yet.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def show_doctor_patient_history():
    st.header("📅 Patient History Management")
    
    # Patient selection
    try:
        response = requests.get(f"{API_BASE}/doctor/patients", params={"token": st.session_state.doctor_token})
        if response.status_code == 200:
            data = response.json()
            if data["patients"]:
                # Create patient selection dropdown
                patient_options = {}
                for patient in data["patients"]:
                    patient_name = patient.get('patient_name', 'Unknown')
                    patient_id = patient.get('patient_id', '')
                    patient_options[f"{patient_name} ({patient_id})"] = patient_id
                
                selected_patient = st.selectbox(
                    "👥 Select Patient to View History:",
                    options=list(patient_options.keys())
                )
                
                if selected_patient:
                    patient_id = patient_options[selected_patient]
                    
                    # Get patient detailed history
                    try:
                        history_response = requests.get(f"{API_BASE}/doctor/patient/{patient_id}/history", 
                                                      params={"token": st.session_state.doctor_token})
                        
                        if history_response.status_code == 200:
                            history_data = history_response.json()
                            
                            st.subheader(f"📈 Complete History for {selected_patient}")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📅 Total Visits", history_data.get('total_visits', 0))
                            with col2:
                                st.metric("🎤 Audio Sessions", len([v for v in history_data.get('visits', []) if 'audio' in v.get('consultation_type', '').lower()]))
                            with col3:
                                st.metric("✅ Completed", len([v for v in history_data.get('visits', []) if v.get('status') == 'Completed']))
                            
                            # Display detailed visit history
                            if history_data.get('visits'):
                                st.subheader("📋 Detailed Visit History")
                                
                                for i, visit in enumerate(history_data['visits']):
                                    with st.expander(f"Visit {i+1} - {visit.get('visit_date', 'N/A')}"):
                                        col_a, col_b = st.columns(2)
                                        
                                        with col_a:
                                            st.write(f"**📅 Date:** {visit.get('visit_date', 'N/A')}")
                                            st.write(f"**🎯 Reason:** {visit.get('visit_reason', 'N/A')}")
                                            st.write(f"**🔍 Type:** {visit.get('consultation_type', 'N/A')}")
                                            st.write(f"**📊 Status:** {visit.get('status', 'N/A')}")
                                        
                                        with col_b:
                                            if visit.get('symptoms_reported'):
                                                st.write(f"**🩸 Symptoms:** {', '.join(visit.get('symptoms_reported', []))}")
                                            
                                            if visit.get('diagnosis_given'):
                                                st.write(f"**🔬 Diagnosis:** {visit.get('diagnosis_given', 'N/A')}")
                                            
                                            if visit.get('assigned_doctor_name'):
                                                st.write(f"**👨⚕️ Doctor:** {visit.get('assigned_doctor_name', 'N/A')}")
                            else:
                                st.info("No visit history found for this patient.")
                        else:
                            st.error("Failed to fetch patient history")
                    
                    except Exception as e:
                        st.error(f"Error fetching patient history: {str(e)}")
            else:
                st.info("No patients assigned to you yet.")
    
    except Exception as e:
        st.error(f"Error loading patients: {str(e)}")

def show_doctor_analytics():
    st.header("📋 Analytics")
    try:
        response = requests.get(f"{API_BASE}/doctor/audit-patients", params={"token": st.session_state.doctor_token})
        if response.status_code == 200:
            data = response.json()
            if data["patients"]:
                st.dataframe(data["patients"])
    except Exception as e:
        st.error(f"Error: {str(e)}")

def show_patient_overview():
    st.header("📊 Patient Overview")
    col1, col2, col3 = st.columns(3)
    
    try:
        response = requests.get(f"{API_BASE}/patient/my-visits", params={"token": st.session_state.patient_token})
        if response.status_code == 200:
            data = response.json()
            with col1:
                st.metric("Total Visits", data['total_visits'])
    except:
        pass
    
    with col2:
        st.metric("Next Appointment", "Tomorrow")
    with col3:
        st.metric("Health Score", "85%")

def show_patient_visits():
    st.header("🏥 My Visit History")
    try:
        response = requests.get(f"{API_BASE}/patient/my-visits", params={"token": st.session_state.patient_token})
        if response.status_code == 200:
            data = response.json()
            if data["visits"]:
                st.dataframe(data["visits"])
            else:
                st.info("No visits recorded yet.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def show_patient_specialists():
    st.header("👨⚕️ Available Specialists")
    try:
        response = requests.get(f"{API_BASE}/patient/specialists")
        if response.status_code == 200:
            data = response.json()
            if data["specialists"]:
                for specialist in data["specialists"]:
                    with st.expander(f"Dr. {specialist.get('name', 'N/A')} - {specialist.get('specialist', 'N/A')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**📧 Email:** {specialist.get('email', 'N/A')}")
                            st.write(f"**📱 Phone:** {specialist.get('phone', 'N/A')}")
                        with col2:
                            st.write(f"**🏥 Type:** {specialist.get('type', 'N/A')}")
                            st.write(f"**🔬 Sub-Specialist:** {specialist.get('sub_specialist', 'N/A')}")
            else:
                st.info("No specialists available.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def show_audio_analysis():
    st.header("🔊 Real-time Audio Analysis")
    
    if "patient_token" not in st.session_state:
        st.warning("⚠️ Please login as a patient first to use audio analysis.")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎤 Audio Recording")
        duration = st.slider("Recording Duration (seconds)", 5, 30, 10)
        sample_rate = 44100
        
        if st.button("🔴 Start Recording", type="primary"):
            with st.spinner("Recording... Please speak clearly about your symptoms"):
                try:
                    # Record audio
                    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.float32)
                    sd.wait()
                    
                    # Convert to bytes
                    audio_bytes = (audio_data * 32767).astype(np.int16)
                    
                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        with wave.open(tmp_file.name, 'wb') as wav_file:
                            wav_file.setnchannels(1)
                            wav_file.setsampwidth(2)
                            wav_file.setframerate(sample_rate)
                            wav_file.writeframes(audio_bytes.tobytes())
                        
                        st.success("✅ Recording completed!")
                        
                        # Play back recorded audio
                        st.audio(tmp_file.name)
                        
                        # Upload and analyze
                        if st.button("📤 Upload & Analyze"):
                            with st.spinner("Analyzing audio..."):
                                try:
                                    with open(tmp_file.name, 'rb') as audio_file:
                                        files = {"voice_file": audio_file}
                                        params = {"token": st.session_state.patient_token}
                                        
                                        response = requests.post(
                                            f"{API_BASE}/patient/audio_stream",
                                            files=files,
                                            params=params
                                        )
                                    
                                    if response.status_code == 200:
                                        result = response.json()
                                        st.session_state.analysis_result = result
                                        st.success("✅ Analysis completed!")
                                    else:
                                        st.error(f"❌ Analysis failed: {response.json().get('detail', 'Unknown error')}")
                                
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                                
                                finally:
                                    # Clean up temp file
                                    os.unlink(tmp_file.name)
                except Exception as e:
                    st.error(f"❌ Recording failed: {str(e)}")
    
    with col2:
        st.subheader("📊 Analysis Results")
        
        if "analysis_result" in st.session_state:
            result = st.session_state.analysis_result
            
            # Patient Info
            st.markdown("**👤 Patient Information:**")
            st.write(f"- **Name:** {result.get('patient_name', 'N/A')}")
            st.write(f"- **ID:** {result.get('patient_id', 'N/A')}")
            st.write(f"- **Email:** {result.get('patient_email', 'N/A')}")
            
            # Transcript
            st.markdown("**📝 Transcript:**")
            st.text_area("", value=result.get('transcript', 'No transcript available'), height=100, disabled=True)
            
            # Analysis
            if result.get('analysis'):
                analysis = result['analysis'][0] if isinstance(result['analysis'], list) else result['analysis']
                
                st.markdown("**🔍 AI Analysis:**")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.write(f"**Disease:** {analysis.get('disease', 'N/A')}")
                    st.write(f"**Urgency:** {analysis.get('urgency', 'N/A')}")
                
                with col_b:
                    st.write(f"**Probability:** {analysis.get('probability', 'N/A')}")
                    st.write(f"**Specialist:** {analysis.get('recommended_specialist', 'N/A')}")
                
                st.markdown("**💡 Advice:**")
                st.info(analysis.get('advice', 'No advice available'))
            
            # Doctor Assignment
            if result.get('doctor_assigned'):
                st.markdown("**👨⚕️ Assigned Doctor:**")
                st.write(f"- **Name:** {result.get('doctor_name', 'N/A')}")
                st.write(f"- **Email:** {result.get('doctor_email', 'N/A')}")
                
                if result.get('alert_sent'):
                    st.success("✅ Doctor has been notified!")
                else:
                    st.info("ℹ️ Doctor notification pending")
        else:
            st.info("No analysis results yet. Please record and analyze audio first.")

def show_home():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>🎯 Platform Features</h3>
            <ul>
                <li>🤖 AI-Powered Health Analysis</li>
                <li>🔊 Real-time Audio Monitoring</li>
                <li>👨⚕️ Doctor-Patient Management</li>
                <li>📊 Health Analytics Dashboard</li>
                <li>🚨 Emergency Alert System</li>
                <li>📱 Multi-platform Access</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h3>📈 System Statistics</h3>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            patients_resp = requests.get(f"{API_BASE}/admin/patients")
            visits_resp = requests.get(f"{API_BASE}/admin/patient-visits")
            
            if patients_resp.status_code == 200 and visits_resp.status_code == 200:
                patients_data = patients_resp.json()
                visits_data = visits_resp.json()
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Total Patients", patients_data.get("total_patients", 0))
                with col_b:
                    st.metric("Total Visits", visits_data.get("total_visits", 0))
        except:
            st.warning("Unable to fetch system statistics")

def show_doctor_dashboard():
    st.header("👨⚕️ Doctor Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Doctor Registration")
        with st.form("doctor_signup"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            type_sel = st.selectbox("Type", ["Medicine", "Surgery"])
            
            specialists = load_specialists()
            designations = load_designations()
            
            specialist = st.selectbox("Specialist", specialists)
            sub_specialist = st.selectbox("Sub Specialist", specialists)
            designation = st.selectbox("Designation", designations)
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Register"):
                data = {
                    "name": name, "email": email, "phone": phone,
                    "type": type_sel, "specialist": specialist,
                    "sub_specialist": sub_specialist, "designation": designation,
                    "password": password, "confirm_password": confirm_password
                }
                
                try:
                    response = requests.post(f"{API_BASE}/doctor/signup", json=data)
                    if response.status_code == 200:
                        st.success("✅ Registration successful! Check email for OTP.")
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Registration failed')}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
    
    with col2:
        st.subheader("🔑 Doctor Login")
        with st.form("doctor_login"):
            login_email = st.text_input("Email", key="doc_login_email")
            login_password = st.text_input("Password", type="password", key="doc_login_pass")
            
            if st.form_submit_button("Login"):
                data = {"email": login_email, "password": login_password}
                
                try:
                    response = requests.post(f"{API_BASE}/doctor/login", json=data)
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.doctor_token = result["access_token"]
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ Login failed: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
        
        st.subheader("📧 Email Verification")
        with st.form("doctor_verify"):
            verify_email = st.text_input("Email", key="doc_verify_email")
            otp = st.text_input("OTP Code")
            
            if st.form_submit_button("Verify"):
                try:
                    response = requests.post(f"{API_BASE}/doctor/verify", params={"email": verify_email, "otp": otp})
                    if response.status_code == 200:
                        st.success("✅ Email verified successfully!")
                    else:
                        st.error(f"❌ Verification failed: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")

def show_patient_dashboard():
    st.header("👤 Patient Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Patient Registration")
        with st.form("patient_signup"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            age = st.number_input("Age", min_value=0, max_value=150)
            gender = st.selectbox("Gender", ["male", "female", "other"])
            symptoms = st.text_area("Symptoms (comma separated)", placeholder="e.g., headache, fever, cough")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Register"):
                symptoms_list = [s.strip() for s in symptoms.split(",") if s.strip()] if symptoms else []
                data = {
                    "name": name, "email": email, "phone": phone,
                    "age": age, "gender": gender, "symptoms": symptoms_list,
                    "password": password, "confirm_password": confirm_password
                }
                
                try:
                    response = requests.post(f"{API_BASE}/patient/signup", json=data)
                    if response.status_code == 200:
                        st.success("✅ Registration successful! Check email for OTP.")
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Registration failed')}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
    
    with col2:
        st.subheader("🔑 Patient Login")
        with st.form("patient_login"):
            login_email = st.text_input("Email", key="pat_login_email")
            login_password = st.text_input("Password", type="password", key="pat_login_pass")
            
            if st.form_submit_button("Login"):
                data = {"email": login_email, "password": login_password}
                
                try:
                    response = requests.post(f"{API_BASE}/patient/login", json=data)
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.patient_token = result["access_token"]
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ Login failed: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
        
        st.subheader("📧 Email Verification")
        with st.form("patient_verify"):
            verify_email = st.text_input("Email", key="pat_verify_email")
            otp = st.text_input("OTP Code")
            
            if st.form_submit_button("Verify"):
                try:
                    response = requests.post(f"{API_BASE}/patient/verify", params={"email": verify_email, "otp": otp})
                    if response.status_code == 200:
                        st.success("✅ Email verified successfully!")
                    else:
                        st.error(f"❌ Verification failed: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")

def show_audio_history():
    st.header("📋 Audio Analysis History")
    
    if "patient_token" not in st.session_state:
        st.warning("⚠️ Please login as a patient first to view audio history.")
        return
    
    try:
        # Get patient audit records
        response = requests.get(f"{API_BASE}/patient/my-visits", params={"token": st.session_state.patient_token})
        if response.status_code == 200:
            data = response.json()
            
            st.write(f"**Total Audio Sessions:** {data['total_visits']}")
            
            if data["visits"]:
                # Display audio history in cards
                for i, visit in enumerate(data["visits"]):
                    with st.expander(f"Session {i+1} - {visit.get('visit_date', 'N/A')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**📅 Date:** {visit.get('visit_date', 'N/A')}")
                            st.write(f"**🎯 Reason:** {visit.get('visit_reason', 'N/A')}")
                            st.write(f"**🔍 Type:** {visit.get('consultation_type', 'N/A')}")
                        
                        with col2:
                            st.write(f"**👨⚕️ Doctor:** {visit.get('assigned_doctor_name', 'Not Assigned')}")
                            st.write(f"**📊 Status:** {visit.get('status', 'N/A')}")
                        
                        # Show symptoms and diagnosis
                        if visit.get('symptoms_reported'):
                            st.write(f"**🩸 Symptoms:** {', '.join(visit.get('symptoms_reported', []))}")
                        
                        if visit.get('diagnosis_given'):
                            st.write(f"**🔬 Diagnosis:** {visit.get('diagnosis_given', 'N/A')}")
            else:
                st.info("💭 No audio analysis history found. Start by recording your first audio session!")
                
                # Quick link to audio analysis
                if st.button("🎤 Start Audio Analysis"):
                    st.session_state.redirect_to_audio = True
                    st.rerun()
        else:
            st.error("Failed to fetch audio history")
            
    except Exception as e:
        st.error(f"Error loading audio history: {str(e)}")
    
    # Summary statistics
    st.subheader("📊 Audio Analysis Summary")
    
    try:
        response = requests.get(f"{API_BASE}/patient/my-visits", params={"token": st.session_state.patient_token})
        if response.status_code == 200:
            data = response.json()
            visits = data.get("visits", [])
            
            if visits:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_sessions = len(visits)
                    st.metric("🎤 Total Sessions", total_sessions)
                
                with col2:
                    assigned_sessions = len([v for v in visits if v.get('assigned_doctor_name')])
                    st.metric("👨⚕️ Doctor Assigned", assigned_sessions)
                
                with col3:
                    completed_sessions = len([v for v in visits if v.get('status') == 'Completed'])
                    st.metric("✅ Completed", completed_sessions)
    except:
        pass

def show_admin_dashboard():
    st.header("👑 Admin Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["👥 All Patients", "🏥 Patient Visits", "📋 Audit Reviews"])
    
    with tab1:
        st.subheader("👥 All Patients")
        try:
            response = requests.get(f"{API_BASE}/admin/patients")
            if response.status_code == 200:
                data = response.json()
                st.write(f"**Total Patients:** {data['total_patients']}")
                if data["patients"]:
                    st.dataframe(data["patients"])
                else:
                    st.info("No patients registered yet.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.subheader("🏥 All Patient Visits")
        try:
            response = requests.get(f"{API_BASE}/admin/patient-visits")
            if response.status_code == 200:
                data = response.json()
                st.write(f"**Total Visits:** {data['total_visits']}")
                if data["visits"]:
                    st.dataframe(data["visits"])
                else:
                    st.info("No visits recorded yet.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab3:
        st.subheader("📋 Audit Reviews")
        try:
            response = requests.get(f"{API_BASE}/admin/audit-reviews")
            if response.status_code == 200:
                data = response.json()
                st.write(f"**Total Audits:** {data['total_audits']}")
                if data["audits"]:
                    st.dataframe(data["audits"])
                else:
                    st.info("No audit records yet.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def main():
    if "doctor_token" in st.session_state:
        show_doctor_main_dashboard()
    elif "patient_token" in st.session_state:
        show_patient_main_dashboard()
    else:
        st.markdown("""
        <div class="main-header">
            <h1>🏥 MediUrgency Healthcare Platform</h1>
            <p>AI-Powered Healthcare Monitoring & Management System</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.title("🔧 Navigation")
        page = st.sidebar.selectbox("Choose Dashboard", [
            "🏠 Home",
            "👨⚕️ Doctor Dashboard", 
            "👤 Patient Dashboard",
            "👑 Admin Dashboard"
        ])
        
        if page == "🏠 Home":
            show_home()
        elif page == "👨⚕️ Doctor Dashboard":
            show_doctor_dashboard()
        elif page == "👤 Patient Dashboard":
            show_patient_dashboard()
        elif page == "👑 Admin Dashboard":
            show_admin_dashboard()

if __name__ == "__main__":
    main()