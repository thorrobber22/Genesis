#!/usr/bin/env python3
"""
Simple AI test - isolate the issue
"""

import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv()

st.set_page_config(page_title="Simple AI Test")
st.title("🧪 Simple AI Test")

# Test Gemini directly
if st.button("Test Gemini Direct"):
    api_key = os.getenv('GEMINI_API_KEY')
    
    if api_key:
        try:
            # Configure
            genai.configure(api_key=api_key)
            
            # Create model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate
            with st.spinner("Testing..."):
                response = model.generate_content("What is 2+2? Reply with just the number.")
            
            st.success(f"Response: {response.text}")
            
        except Exception as e:
            st.error(f"Error: {e}")
            
            # Show more details
            import traceback
            st.code(traceback.format_exc())
    else:
        st.error("No API key found!")

# Test OpenAI directly
if st.button("Test OpenAI Direct"):
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key:
        try:
            import openai
            
            client = openai.OpenAI(api_key=api_key)
            
            with st.spinner("Testing..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "What is 2+2? Reply with just the number."}],
                    max_tokens=10
                )
            
            st.success(f"Response: {response.choices[0].message.content}")
            
        except Exception as e:
            st.error(f"Error: {e}")
            
            # Show more details
            import traceback
            st.code(traceback.format_exc())
    else:
        st.error("No API key found!")

# Show current API key status
st.markdown("---")
st.markdown("### API Key Status")

col1, col2 = st.columns(2)

with col1:
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        st.success(f"✅ Gemini: {gemini_key[:20]}...")
    else:
        st.error("❌ Gemini: Not found")

with col2:
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        st.success(f"✅ OpenAI: {openai_key[:20]}...")
    else:
        st.error("❌ OpenAI: Not found")