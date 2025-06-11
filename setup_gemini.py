#!/usr/bin/env python3
"""
Setup Gemini AI integration
"""

import os
from pathlib import Path

print("🤖 Setting up Gemini AI Integration\n")

# Check for API key
if os.getenv('GEMINI_API_KEY'):
    print("✅ GEMINI_API_KEY found in environment")
else:
    print("❌ GEMINI_API_KEY not found")
    print("\nTo get a Gemini API key:")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Add to your .env file:")
    print("   GEMINI_API_KEY=your-key-here")

# Install required package
print("\n📦 Installing Google Generative AI package...")
os.system("pip install google-generativeai")

# Create test script
test_script = '''import streamlit as st
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
'''

with open("test_gemini_integration.py", "w", encoding="utf-8") as f:
    f.write(test_script)

print("\n✅ Setup complete!")
print("\n📝 Next steps:")
print("1. Get your Gemini API key from Google")
print("2. Add to .env file: GEMINI_API_KEY=your-key")
print("3. Test: streamlit run test_gemini_integration.py")