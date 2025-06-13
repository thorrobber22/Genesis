"""
restore_chat.py - Restore original chat component
Date: 2025-06-12 01:47:34 UTC
User: thorrobber22
"""

import shutil
import os

if os.path.exists("components/chat_backup.py"):
    shutil.copy("components/chat_backup.py", "components/chat.py")
    print("RESTORED: Original chat.py from backup")
else:
    print("ERROR: No backup found")
    
# If no backup, use the fixed version
if not os.path.exists("components/chat_backup.py"):
    chat_content = '''"""
chat.py - AI Chat Interface Component
Date: 2025-06-12 01:47:34 UTC
User: thorrobber22
"""

import streamlit as st
from datetime import datetime
from services.ai_service import get_ai_response

def show_chat():
    """Display AI chat interface"""
    st.header("AI Chat Assistant")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about IPOs or companies..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_ai_response(prompt)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Clear button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
'''
    
    with open("components/chat.py", "w", encoding="utf-8") as f:
        f.write(chat_content)
    print("CREATED: Simple working chat.py")