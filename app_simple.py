import streamlit as st
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path.cwd()))

st.set_page_config(page_title="Hedge Intelligence", layout="wide")

# Navigation
page = st.sidebar.selectbox("Navigation", ["Home", "AI Chat"])

if page == "Home":
    st.title("Hedge Intelligence")
    st.write("IPO Analysis Platform")

elif page == "AI Chat":
    st.title("AI Chat")
    
    # Initialize messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Initialize AI
    if 'ai_service' not in st.session_state:
        try:
            from services.ai_service import AIService
            st.session_state.ai_service = AIService()
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Show messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Input
    if prompt := st.chat_input("Ask about IPOs..."):
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # AI response
        if 'ai_service' in st.session_state:
            try:
                response = st.session_state.ai_service.chat(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.write(response)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        st.rerun()
