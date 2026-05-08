import os
import streamlit as st

# For local .env usage
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

# For Streamlit Cloud secrets support
if not GROQ_API_KEY:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", None)

if not HF_API_KEY:
    HF_API_KEY = st.secrets.get("HF_API_KEY", None)

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing")

GROQ_MODELS = [
    "llama-3.3-70b-versatile"
]

HF_MODELS = [
    "meta-llama/Llama-3.1-8B-Instruct"
]
