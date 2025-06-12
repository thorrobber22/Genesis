"""
components/chat.py - Minimal persistent chat
"""

import streamlit as st
from services.ai_service import AIService

def show_chat():
    if 'ai_service' not in st.session_state:
        st.session_state.ai_service = AIService()
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

    prompt = st.chat_input("Ask about IPOs...")
    if prompt:
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        with st.chat_message('user'):
            st.markdown(prompt)

        with st.chat_message('assistant'):
            with st.spinner("Thinking..."):
                response = st.session_state.ai_service.chat(prompt)
                st.markdown(response)
                st.session_state.messages.append({'role': 'assistant', 'content': response})
