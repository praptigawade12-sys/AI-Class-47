import os
import streamlit as st
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
  raise ValueError("GROQ_API_KEY is missing")