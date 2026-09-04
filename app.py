import streamlit as st
import pandas as pd
import joblib
import time
import json
import hashlib
import os

st.set_page_config(
    page_title="Metabolic Syndrome Risk Predictor",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------------
# Global styling
# ------------------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp { background-color: #F5F8FC; }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2rem;
        max-width: 760px;
    }

    hr { display: none; }

    /* Hide the +/- step buttons on number inputs for a cleaner look */
    button[data-testid="stNumberInputStepDown"],
    button[data-testid="stNumberInputStepUp"] {
        display: none;
    }
    div[data-testid="stNumberInput"] input {
        text-align: left;
    }

    /* ---------- Compact hero header ---------- */
    .hero {
        background: linear-gradient(135deg, #1E3A8A 0%, #172554 100%);
        padding: 1.6rem 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 6px 18px rgba(30, 58, 138, 0.25);
    }
    .hero h1 {
        color: white;
        font-size: 1.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.2px;
    }
    .hero p {
        color: #C7D6F5;
        font-size: 0.85rem;
        margin-top: 0.35rem;
        font-weight: 400;
    }

    /* ---------- Progress steps ---------- */
    .steps-wrap {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding: 0 0.2rem;
    }
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
    }
    .step-circle {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #1E3A8A;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .step-label {
        font-size: 0.68rem;
        color: #475569;
        margin-top: 0.3rem;
        text-align: center;
        font-weight: 500;
    }
    .step-line {
        flex: 1;
        height: 2px;
        background: #C7D6F5;
        margin-bottom: 1.1rem;
    }

    /* ---------- Section cards ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border-radius: 12px !important;
        border: 1px solid #E5EEFB !important;
        box-shadow: 0 2px 8px rgba(30, 58, 138, 0.05);
        margin-bottom: 1rem;
    }
    .section-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.9rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #EAF2FE;
    }

    /* ---------- Inputs ---------- */
    div[data-testid="stNumberInput"] input,
    div[data-baseweb="select"] > div {
        background-color: #F8FAFF !important;
        border: 1px solid #D6E4FA !important;
        border-radius: 8px !important;
        color: #1E293B !important;
    }
    label { color: #334155 !important; font-weight: 500 !important; font-size: 0.87rem !important; }
    div[data-testid="stSlider"] > div > div > div > div { background-color: #1E3A8A !important; }

    /* ---------- Buttons ---------- */
    div.stButton > button, div.stFormSubmitButton > button {
        background: #1E3A8A;
        color: white;
        font-weight: 700;
        font-size: 1.15rem;
        padding: 1.05rem 0;
        border-radius: 10px;
        border: none;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 4px 14px rgba(30, 58, 138, 0.3);
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background: #172554;
        box-shadow: 0 6px 18px rgba(30, 58, 138, 0.45);
        transform: translateY(-1px);
    }
    div.stButton > button p, div.stFormSubmitButton > button p { font-weight: 700 !important; }

    /* Secondary (outline) button for Assess Another Patient */
    .st-key-assess_btn button {
        background: white !important;
        color: #1E3A8A !important;
        border: 1.5px solid #1E3A8A !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 0.85rem 0 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
        transition: all 0.2s ease;
    }
    .st-key-assess_btn button:hover {
        background: #EFF6FF !important;
        transform: none !important;
    }
    .st-key-assess_btn button p {
        font-weight: 700 !important;
    }

    /* Keep both bottom-action columns aligned to the same vertical position */
    div[data-testid="column"] {
        display: flex;
        align-items: flex-start;
    }

    /* Make the Download Report button match the same shape/size as other buttons */
    div[data-testid="stDownloadButton"] > button {
        background: white !important;
        color: #1E3A8A !important;
        border: 1.5px solid #1E3A8A !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 0.85rem 0 !important;
        border-radius: 10px !important;
        width: 100% !important;
        box-shadow: none !important;
        transition: all 0.2s ease;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background: #EFF6FF !important;
        transform: none !important;
    }
    div[data-testid="stDownloadButton"] > button p {
        font-weight: 700 !important;
    }

    /* ---------- Result hero ---------- */
    .result-card {
        background: white;
        border-radius: 16px;
        padding: 2rem 1.8rem;
        text-align: center;
        margin-bottom: 1.2rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    }
    .result-card.high { border-top: 6px solid #DC2626; }
    .result-card.low { border-top: 6px solid #16A34A; }
    .result-icon { font-size: 2.6rem; margin-bottom: 0.2rem; }
    .result-title {
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin: 0.2rem 0 0.6rem 0;
    }
    .result-title.high { color: #DC2626; }
    .result-title.low { color: #16A34A; }
    .prob-value { font-size: 2.4rem; font-weight: 800; color: #1E293B; margin: 0.3rem 0 0.1rem 0; }
    .prob-caption { font-size: 0.85rem; color: #64748B; margin-bottom: 1.1rem; }

    /* ---------- Risk meter ---------- */
    .risk-meter-wrap { padding: 0 0.4rem; }
    .risk-meter-track {
        position: relative;
        height: 10px;
        border-radius: 6px;
        background: linear-gradient(90deg, #16A34A 0%, #F59E0B 50%, #DC2626 100%);
        margin: 0.6rem 0 0.4rem 0;
    }
    .risk-meter-marker {
        position: absolute;
        top: -6px;
        width: 22px;
        height: 22px;
        background: white;
        border: 3px solid #1E293B;
        border-radius: 50%;
        transform: translateX(-50%);
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }
    .risk-meter-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.72rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ---------- Info / explanation cards ---------- */
    .info-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #1E3A8A;
        box-shadow: 0 2px 8px rgba(30, 58, 138, 0.05);
        color: #334155;
        line-height: 1.6;
        font-size: 0.92rem;
    }
    .info-card b { color: #1E3A8A; }
    .info-card.placeholder { border-left-color: #94A3B8; color: #64748B; font-style: italic; }

    /* ---------- Summary grid ---------- */
    .summary-group-title {
        font-size: 0.78rem;
        font-weight: 700;
        color: #1E3A8A;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0.9rem 0 0.4rem 0;
    }
    .summary-group-title:first-child { margin-top: 0; }
    .summary-row {
        display: flex;
        justify-content: space-between;
        padding: 0.4rem 0;
        border-bottom: 1px solid #F1F5F9;
        font-size: 0.88rem;
    }
    .summary-row span:first-child { color: #64748B; }
    .summary-row span:last-child { color: #1E293B; font-weight: 600; }

    .footer-text {
        text-align: center;
        color: #94A3B8;
        font-size: 0.78rem;
        margin-top: 1.3rem;
        line-height: 1.5;
    }

    /* ---------- Auth (Login / Sign Up) ---------- */
    .auth-hero {
        background: linear-gradient(135deg, #1E3A8A 0%, #172554 100%);
        padding: 1.8rem 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1.3rem;
        box-shadow: 0 6px 18px rgba(30, 58, 138, 0.25);
    }
    .auth-hero h1 { color: white; font-size: 1.4rem; font-weight: 800; margin: 0; }
    .auth-hero p { color: #C7D6F5; font-size: 0.82rem; margin-top: 0.3rem; }

    .user-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: white;
        border: 1px solid #E5EEFB;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        margin-bottom: 1rem;
        font-size: 0.85rem;
        color: #334155;
    }

    /* ---------- Auth top bar ---------- */
    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.9rem 0.2rem;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #E2E8F0;
    }
    .topbar-brand {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.05rem;
        font-weight: 800;
        color: #1E3A8A;
    }
    .topbar-tag {
        font-size: 0.72rem;
        font-weight: 600;
        color: #94A3B8;
        letter-spacing: 1px;
        text-transform: uppercase;
        border: 1px solid #DBEAFE;
        background: #EFF6FF;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
    }

    /* ---------- Refined auth hero ---------- */
    .auth-hero-clean {
        text-align: center;
        padding: 1.2rem 0.5rem 1.8rem 0.5rem;
    }
    .auth-hero-clean h1 {
        color: #0F172A;
        font-size: 1.9rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.5px;
        line-height: 1.25;
    }
    .auth-hero-clean h1 span {
        color: #1E3A8A;
    }
    .auth-hero-clean p {
        color: #64748B;
        font-size: 0.95rem;
        max-width: 480px;
        margin: 0 auto;
        line-height: 1.55;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Load model artifacts (unchanged backend)
# ------------------------------------------------------------------
@st.cache_resource
def load_artifacts():
    model = joblib.load("model.pkl")
    scaler = joblib.load("scaler.pkl")
    sex_encoder = joblib.load("sex_encoder.pkl")
    feature_order = joblib.load("feature_order.pkl")
    return model, scaler, sex_encoder, feature_order

model, scaler, sex_encoder, feature_order = load_artifacts()

# ------------------------------------------------------------------
# Simple local user store for patient login/signup (FYP demo purpose)
# ------------------------------------------------------------------
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

if "page" not in st.session_state:
    st.session_state.page = "auth"
if "result" not in st.session_state:
    st.session_state.result = None
if "username" not in st.session_state:
    st.session_state.username = None

def go_to_form():
    st.session_state.page = "form"

def logout():
    st.session_state.username = None
    st.session_state.page = "auth"

# ====================================================================
# PAGE 0: LOGIN / SIGN UP
# ====================================================================
if st.session_state.page == "auth":

    st.markdown("""
        <div class="topbar">
            <div class="topbar-brand">🩺 MetaHealth Predictor</div>
            <div class="topbar-tag">Patient Portal</div>
        </div>
        <div class="auth-hero-clean">
            <h1>Metabolic syndrome<br>risk management, <span>done right</span></h1>
            <p>Log in to assess metabolic syndrome and comorbidity risk using a machine learning based clinical tool.</p>
        </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    # ---------------- LOGIN TAB ----------------
    with tab_login:
        with st.container(border=True):
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", use_container_width=True, key="login_btn"):
                users = load_users()
                if login_username in users and users[login_username] == hash_password(login_password):
                    st.session_state.username = login_username
                    st.session_state.page = "form"
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    # ---------------- SIGN UP TAB ----------------
    with tab_signup:
        with st.container(border=True):
            signup_username = st.text_input("Choose a Username", key="signup_username")
            signup_password = st.text_input("Choose a Password", type="password", key="signup_password")
            signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
            if st.button("Create Account", use_container_width=True, key="signup_btn"):
                users = load_users()
                if not signup_username or not signup_password:
                    st.error("Please fill in all fields.")
                elif signup_username in users:
                    st.error("This username is already taken.")
                elif signup_password != signup_confirm:
                    st.error("Passwords do not match.")
                else:
                    users[signup_username] = hash_password(signup_password)
                    save_users(users)
                    st.success("Account created successfully. Please log in.")

    st.markdown('<div class="footer-text">Final Year Project<br>Predictive Healthcare Analytics for Comorbidity and Metabolic Syndrome Detection</div>', unsafe_allow_html=True)

# ====================================================================
# PAGE 1: FORM
# ====================================================================
elif st.session_state.page == "form":

    st.markdown(f"""
        <div class="user-bar">
            <span>👋 Welcome, <b>{st.session_state.username}</b></span>
        </div>
    """, unsafe_allow_html=True)
    st.button("Logout", on_click=logout, key="logout_btn")


    st.markdown("""
        <div class="hero">
            <h1>🩺 Metabolic Syndrome Risk Predictor</h1>
            <p>Machine learning based assessment of metabolic syndrome and comorbidity risk</p>
        </div>
    """, unsafe_allow_html=True)

    # ---- Progress indicator ----
    steps = ["01\nPatient", "02\nMeasurements", "03\nBlood Tests", "04\nClinical History", "05\nPrediction"]
    steps_html = '<div class="steps-wrap">'
    for i, s in enumerate(steps):
        num, label = s.split("\n")
        steps_html += f'<div class="step"><div class="step-circle">{num}</div><div class="step-label">{label}</div></div>'
        if i < len(steps) - 1:
            steps_html += '<div class="step-line"></div>'
    steps_html += '</div>'
    st.markdown(steps_html, unsafe_allow_html=True)

    with st.form("prediction_form"):

        with st.container(border=True):
            st.markdown('<div class="section-title">👤 Patient Demographics</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age (years)", min_value=1, max_value=120, value=40)
            with col2:
                sex = st.selectbox("Sex", options=list(sex_encoder.classes_))

        with st.container(border=True):
            st.markdown('<div class="section-title">📏 Body Measurements</div>', unsafe_allow_html=True)
            col3, col4 = st.columns(2)
            with col3:
                waist_circ = st.number_input("Waist Circumference (cm)", min_value=30.0, max_value=200.0, value=90.0)
            with col4:
                bmi = st.number_input("BMI (kg/m²)", min_value=10.0, max_value=70.0, value=25.0)

        with st.container(border=True):
            st.markdown('<div class="section-title">🧪 Blood Test Results</div>', unsafe_allow_html=True)
            col5, col6 = st.columns(2)
            with col5:
                blood_glucose = st.number_input("Fasting Blood Glucose (mg/dL)", min_value=50, max_value=400, value=95)
                hdl = st.number_input("HDL Cholesterol (mg/dL)", min_value=10, max_value=150, value=50)
                triglycerides = st.number_input("Triglycerides (mg/dL)", min_value=20.0, max_value=600.0, value=100.0)
            with col6:
                uric_acid = st.number_input("Uric Acid (mg/dL)", min_value=1.0, max_value=15.0, value=5.0)
                ur_alb_cr = st.number_input("Urine Albumin-Creatinine Ratio", min_value=0.0, max_value=50.0, value=6.0)
                albuminuria = st.selectbox("Albuminuria Present", options=["No", "Yes"])

        with st.container(border=True):
            st.markdown('<div class="section-title">📋 Clinical History</div>', unsafe_allow_html=True)
            col7, col8 = st.columns(2)
            with col7:
                hypertension = st.selectbox("Diagnosed with Hypertension", options=["No", "Yes"])
            with col8:
                risk_factor_count = st.slider("Number of Known Risk Factors", min_value=0, max_value=5, value=1)

        st.write("")
        btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
        with btn_col2:
            submitted = st.form_submit_button("🔍  Predict Risk", use_container_width=True)

    if submitted:
        with st.spinner("Analyzing Patient Data..."):
            time.sleep(0.8)

            input_dict = {
                "Age": age,
                "Sex": sex_encoder.transform([sex])[0],
                "WaistCirc": waist_circ,
                "BMI": bmi,
                "Albuminuria": 1 if albuminuria == "Yes" else 0,
                "UrAlbCr": ur_alb_cr,
                "UricAcid": uric_acid,
                "BloodGlucose": blood_glucose,
                "HDL": hdl,
                "Triglycerides": triglycerides,
                "Hypertension": 1 if hypertension == "Yes" else 0,
                "RiskFactorCount": risk_factor_count,
            }

            input_df = pd.DataFrame([input_dict])[feature_order]
            input_scaled = scaler.transform(input_df)

            prediction = model.predict(input_scaled)[0]
            probability = model.predict_proba(input_scaled)[0][1]

            display_values = {
                "Patient Information": {
                    "Age": f"{age} years",
                    "Sex": sex,
                },
                "Body Measurements": {
                    "Waist Circumference": f"{waist_circ} cm",
                    "BMI": f"{bmi} kg/m²",
                },
                "Blood Tests": {
                    "Fasting Blood Glucose": f"{blood_glucose} mg/dL",
                    "HDL Cholesterol": f"{hdl} mg/dL",
                    "Triglycerides": f"{triglycerides} mg/dL",
                    "Uric Acid": f"{uric_acid} mg/dL",
                    "Urine Albumin-Creatinine Ratio": f"{ur_alb_cr}",
                    "Albuminuria Present": albuminuria,
                },
                "Clinical History": {
                    "Hypertension": hypertension,
                    "Known Risk Factors": str(risk_factor_count),
                },
            }

            st.session_state.result = {
                "prediction": prediction,
                "probability": probability,
                "display_values": display_values,
            }
            st.session_state.page = "result"
            st.rerun()

    st.markdown('<div class="footer-text">Final Year Project<br>Predictive Healthcare Analytics for Comorbidity and Metabolic Syndrome Detection</div>', unsafe_allow_html=True)

# ====================================================================
# PAGE 2: RESULT DASHBOARD
# ====================================================================
elif st.session_state.page == "result":

    result = st.session_state.result
    prediction = result["prediction"]
    probability = result["probability"]
    display_values = result["display_values"]
    prob_pct = probability * 100

    st.markdown('<h3 style="text-align:center; color:#1E293B; font-weight:800;">Prediction Result</h3>', unsafe_allow_html=True)

    risk_class = "high" if prediction == 1 else "low"
    icon = "⚠️" if prediction == 1 else "✅"
    label = "HIGH RISK" if prediction == 1 else "LOW RISK"

    st.markdown(f"""
        <div class="result-card {risk_class}">
            <div class="result-icon">{icon}</div>
            <div class="result-title {risk_class}">{label}</div>
            <div class="prob-value">{prob_pct:.1f}%</div>
            <div class="prob-caption">Estimated probability of Metabolic Syndrome</div>
            <div class="risk-meter-wrap">
                <div class="risk-meter-track">
                    <div class="risk-meter-marker" style="left:{prob_pct}%;"></div>
                </div>
                <div class="risk-meter-labels">
                    <span>Low</span><span>Moderate</span><span>High</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ---- Understanding Your Result ----
    st.markdown('<div class="section-title" style="margin-top:0.5rem;">Understanding Your Result</div>', unsafe_allow_html=True)
    if prediction == 1:
        st.markdown("""
            <div class="info-card">
                <b>What this means:</b> The values provided fall into a pattern that the model associates
                with a higher likelihood of metabolic syndrome, based on clinical indicators such as waist
                circumference, blood glucose, triglycerides, and HDL cholesterol.<br><br>
                <b>Recommendation:</b> It is strongly recommended to consult a healthcare professional for
                a complete clinical evaluation, including blood pressure, glucose tolerance, and lipid panel testing.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="info-card">
                <b>What this means:</b> The values provided fall into a pattern that the model associates
                with a lower likelihood of metabolic syndrome, based on clinical indicators such as waist
                circumference, blood glucose, triglycerides, and HDL cholesterol.<br><br>
                <b>Recommendation:</b> Maintaining a balanced diet, regular physical activity, and routine
                health checkups is recommended to keep this risk low.
            </div>
        """, unsafe_allow_html=True)

    # ---- Model Explainability (honest placeholder, no fake data) ----
    st.markdown('<div class="section-title">Model Explainability</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="info-card placeholder">
            Feature-level contribution analysis (e.g. SHAP values) is not currently integrated into this
            model. This section is reserved for future work to explain which individual factors most
            influenced a specific prediction.
        </div>
    """, unsafe_allow_html=True)

    # ---- Input Summary (clean grouped cards, no raw dataframe) ----
    with st.container(border=True):
        st.markdown('<div class="section-title">📄 Input Summary</div>', unsafe_allow_html=True)
        for group_name, fields in display_values.items():
            st.markdown(f'<div class="summary-group-title">{group_name}</div>', unsafe_allow_html=True)
            for k, v in fields.items():
                st.markdown(f'<div class="summary-row"><span>{k}</span><span>{v}</span></div>', unsafe_allow_html=True)

    st.write("")

    # ---- Bottom actions ----
    report_lines = [
        "METABOLIC SYNDROME RISK ASSESSMENT REPORT",
        "=" * 45,
        f"Prediction: {label}",
        f"Estimated Probability: {prob_pct:.1f}%",
        "",
    ]
    for group_name, fields in display_values.items():
        report_lines.append(f"{group_name}:")
        for k, v in fields.items():
            report_lines.append(f"  - {k}: {v}")
        report_lines.append("")
    report_lines.append("Note: This tool is for educational and research purposes only.")
    report_lines.append("It does not replace professional medical advice.")
    report_text = "\n".join(report_lines)

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(key="assess_btn"):
            st.button("↻ Assess Another Patient", on_click=go_to_form, use_container_width=True)
    with col_b:
        st.download_button(
            "📄 Download Report",
            data=report_text,
            file_name="metabolic_syndrome_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.markdown('<div class="footer-text">Final Year Project<br>Predictive Healthcare Analytics for Comorbidity and Metabolic Syndrome Detection</div>', unsafe_allow_html=True)