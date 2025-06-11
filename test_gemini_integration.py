import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Gemini Test", layout="wide")
st.title("🤖 Gemini AI Test")

# Check API keys
col1, col2 = st.columns(2)

with col1:
    if os.getenv('OPENAI_API_KEY'):
        st.success("✅ OpenAI API Key found")
    else:
        st.error("❌ OpenAI API Key missing")

with col2:
    if os.getenv('GEMINI_API_KEY'):
        st.success("✅ Gemini API Key found")
    else:
        st.error("❌ Gemini API Key missing")

st.markdown("---")

# Test the dual AI chat
if st.button("Test Dual AI Chat"):
    from components.ai_chat_dual import render_dual_ai_chat
    render_dual_ai_chat()
