"""
components/chat_minimal.py - Minimal working chat
Date: 2025-06-11 22:36:14 UTC
User: thorrobber22
"""

import streamlit as st

def show_chat():
    """Minimal chat that definitely works"""
    
    # Initialize messages in session state
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "👋 Hello! Ask me about IPOs."}
        ]
    
    # Display all messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Get user input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Add assistant response
        response = f"You said: {prompt}. (This is a test response)"
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        # Force rerun to show new messages
        st.rerun()
