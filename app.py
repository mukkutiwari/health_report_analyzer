from extractor import extract_text_from_pdf
from Analysis import analyze_report, chat_with_report
from Model_list import Available_Models
from prompts import ANALYSIS_PROMPT

import streamlit as st
from PIL import Image
import base64

# --------------------------------
# Cache PDF extraction (ADD HERE)
# --------------------------------
@st.cache_data(show_spinner=False)
def cached_extract(uploaded_file):
    return extract_text_from_pdf(uploaded_file)

# --------------------------
# Function to add background
# --------------------------
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
        }}
        
        .glass {{
            background: rgba(255, 255, 255, 0.70);
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0px 4px 30px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
        }}

        .chat-box {{
            border: 1px solid #ddd;
            border-radius: 12px;
            padding: 15px;
            background: rgba(255,255,255,0.85);
            margin-bottom: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Correct image path
add_bg_from_local("bg.jpg")

# --------------------------
# Streamlit UI
# --------------------------
st.markdown("<h1 style='text-align:center; color:orange;'>🩺 Health Report Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:orange; font-size:18px;'>Upload your health report and get simple highlights</p>", unsafe_allow_html=True)

# --------------------------
# LLM Selection
# --------------------------
selected_model_label = st.selectbox(
    "🧠 Select LLM Model",
    options=Available_Models.keys()
)

model_cfg = Available_Models[selected_model_label]

# --------------------------
# Upload Section
# --------------------------
with st.container():
    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Health Report (PDF)", type=["pdf"])

    if uploaded_file:
        st.success("Report uploaded successfully! Extracting highlights...")

        # Extract text
        extracted_text = cached_extract(uploaded_file)


        with st.spinner("Analyzing report…"):
            analysis_result = analyze_report(
               extracted_text,
               model_cfg,
               temperature=0.3,
               max_tokens=512
        )

        st.subheader("📌 Report Highlights")
        st.markdown(analysis_result, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------
# Chatbot Section
# --------------------------
st.markdown("<h2 style='color: orange;'>🤖 Chat with the Report Assistant</h2>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "report_text" not in st.session_state:
    st.session_state.report_text = ""

if uploaded_file:
    st.session_state.report_text = extracted_text


# Native Streamlit Chat UI
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


user_prompt = st.chat_input("Ask about your health report...")

if user_prompt:
    if not st.session_state.report_text:
        st.warning("Please upload a report first.")
    else:
        # User message
        st.session_state.chat_history.append(
            {"role": "user", "content": user_prompt}
        )

        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = chat_with_report(
                   st.session_state.report_text,
                   st.session_state.chat_history,
                   model_cfg,
                   temperature=0.3,
                   max_tokens=512
                )

  
                st.markdown(reply)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )
