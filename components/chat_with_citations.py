"""
components/chat_with_citations.py - Enhanced chat with citations
Date: 2025-06-11 21:35:40 UTC
User: thorrobber22
"""

import streamlit as st
from services.ai_service import AIService
from services.citation_service import CitationService

def show_chat_with_citations():
    """Enhanced chat interface with citations"""
    
    # Initialize services
    if 'ai_service' not in st.session_state:
        try:
            st.session_state.ai_service = AIService()
        except Exception as e:
            st.error(f"Error initializing AI service: {str(e)}")
            return
            
    if 'citation_service' not in st.session_state:
        st.session_state.citation_service = CitationService()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    ai_service = st.session_state.ai_service
    citation_service = st.session_state.citation_service
    
    # Chat interface
    st.markdown("### 💬 AI Assistant with Citations")
    
    # Context indicator
    if 'selected_company' in st.session_state and st.session_state.selected_company:
        st.info(f"📊 Context: {st.session_state.selected_company}")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if user_input := st.chat_input("Ask about IPOs, companies, or financial data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get AI response with sources
        with st.chat_message("assistant"):
            with st.spinner("Searching documents..."):
                try:
                    # Get response and source chunks
                    response_data = ai_service.get_response_with_sources(
                        user_input,
                        context=st.session_state.get('selected_company')
                    )
                    
                    response = response_data.get('response', 'I apologize, but I encountered an error.')
                    source_chunks = response_data.get('sources', [])
                    
                    # Add citations to response
                    response_with_citations = citation_service.add_citations_to_response(
                        response, 
                        source_chunks
                    )
                    
                    # Display response
                    st.markdown(response_with_citations)
                    
                    # Store in history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response_with_citations
                    })
                    
                    # Store sources for sidebar
                    if source_chunks:
                        st.session_state.last_sources = [
                            citation_service.extract_citation_from_chunk(chunk)
                            for chunk in source_chunks
                        ]
                        
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Citation sidebar
    with st.sidebar:
        st.markdown("### 📚 Recent Sources")
        
        if 'last_sources' in st.session_state and st.session_state.last_sources:
            for source in st.session_state.last_sources[:5]:
                ticker = source.get('ticker', 'Unknown')
                doc_type = source.get('document_type', 'Filing')
                
                if source.get('sec_url'):
                    st.markdown(f"🔗 [{ticker} {doc_type}]({source['sec_url']})")
                else:
                    st.markdown(f"📄 {ticker} {doc_type}")
        else:
            st.caption("No sources yet. Ask a question!")

# Fallback to regular chat
def show_chat():
    """Wrapper for compatibility"""
    show_chat_with_citations()
