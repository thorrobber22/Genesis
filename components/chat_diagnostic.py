"""
chat_diagnostic.py - Diagnostic version of chat
Date: 2025-06-12 01:45:22 UTC
User: thorrobber22
"""

import streamlit as st
from datetime import datetime

def show_chat():
    """Display AI chat interface with diagnostics"""
    st.header("AI Chat Assistant - DIAGNOSTIC MODE")
    
    # Show function was called
    st.success("show_chat() function called successfully!")
    
    # Show session state
    st.write("Session State:", st.session_state)
    
    # Test basic chat functionality
    if 'test_messages' not in st.session_state:
        st.session_state.test_messages = []
    
    # Simple input
    test_input = st.text_input("Test Input (no AI):")
    if test_input:
        st.session_state.test_messages.append(test_input)
        st.write("You typed:", test_input)
    
    # Show messages
    st.write("All messages:", st.session_state.test_messages)
    
    # Now test AI import
    st.divider()
    st.subheader("AI Service Test")
    
    try:
        from services.ai_service import get_ai_response
        st.success("AI service imported OK")
        
        if st.button("Test AI Response"):
            with st.spinner("Testing AI..."):
                response = get_ai_response("Say hello", "test")
                st.write("AI Response:", response)
                
    except Exception as e:
        st.error(f"AI import error: {e}")
        import traceback
        st.code(traceback.format_exc())
