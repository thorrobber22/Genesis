"""
chat.py - AI Chat Interface Component (FIXED)
Date: 2025-06-12 01:40:16 UTC
User: thorrobber22
"""

import streamlit as st
from datetime import datetime
import os

# Import with error handling
try:
    from services.ai_service import get_ai_response
    AI_AVAILABLE = True
except Exception as e:
    print(f"[Chat] Error importing AI service: {e}")
    AI_AVAILABLE = False
    def get_ai_response(prompt, context=None):
        return f"AI Service Error: {str(e)}"

def show_chat():
    """Display AI chat interface"""
    st.header("AI Chat Assistant")
    
    # Debug mode toggle
    debug_mode = st.checkbox("Debug Mode", value=False)
    
    if debug_mode:
        # Show debug info
        st.info("Debug Information:")
        st.write(f"- AI Available: {AI_AVAILABLE}")
        st.write(f"- API Key Set: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
        st.write(f"- Current Time: {datetime.now()}")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your IPO analysis assistant. Ask me about any IPO, company financials, or market trends."}
        ]
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    prompt = st.chat_input("Ask about IPOs, companies, or market analysis...")
    
    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            # Show loading
            with st.spinner("Thinking..."):
                try:
                    # Add context
                    context = f"Current date: {datetime.now().strftime('%Y-%m-%d')}. You are an IPO analysis expert."
                    
                    if debug_mode:
                        st.write(f"Debug: Sending prompt: {prompt[:50]}...")
                    
                    # Get response
                    response = get_ai_response(prompt, context)
                    
                    if debug_mode:
                        st.write(f"Debug: Got response length: {len(response) if response else 0}")
                    
                    # Display response
                    response_placeholder.markdown(response)
                    
                    # Add to history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"Error getting response: {str(e)}"
                    response_placeholder.error(error_msg)
                    if debug_mode:
                        import traceback
                        st.code(traceback.format_exc())
    
    # Chat controls
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("Clear Chat"):
            st.session_state.messages = [
                {"role": "assistant", "content": "Chat cleared. How can I help you with IPO analysis?"}
            ]
            st.rerun()
    
    with col2:
        if st.button("Export Chat"):
            chat_text = "\n\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in st.session_state.messages])
            st.download_button(
                label="Download",
                data=chat_text,
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    with col3:
        # API status
        if not os.getenv('OPENAI_API_KEY'):
            st.warning("No API key found - Add OPENAI_API_KEY to .env file")

if __name__ == "__main__":
    show_chat()
