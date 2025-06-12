"""
components/persistent_chat_enhanced.py - Fixed chat component
"""

import streamlit as st
from services.ai_service import AIService
from services.document_indexer import DocumentIndexer

def render_chat():
    """Render the AI chat interface"""
    
    st.subheader("🤖 AI Assistant")
    
    # Initialize services
    @st.cache_resource
    def get_services():
        return AIService(), DocumentIndexer()
    
    try:
        ai_service, indexer = get_services()
        
        # Check for company context
        params = st.session_state.get('page_params', {})
        if 'ticker' in params:
            st.info(f"Analyzing {params['ticker']}")
        
        # Chat interface
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Input
        if prompt := st.chat_input("Ask about any company or filing..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Search for relevant context
                    results = indexer.search(prompt, limit=3)
                    
                    # Build context
                    context = "\n\n".join([r.page_content for r in results]) if results else ""
                    
                    # Get response
                    response = ai_service.chat(
                        prompt,
                        context=context,
                        system_prompt="You are a hedge fund analyst assistant. Provide concise, actionable insights."
                    )
                    
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
    except Exception as e:
        st.error(f"AI Service Error: {str(e)}")
        st.info("Make sure your API keys are configured in .env file")
