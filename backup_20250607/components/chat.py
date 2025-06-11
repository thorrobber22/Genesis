"""
Chat Interface Component
Date: 2025-06-07 14:02:41 UTC
"""

import streamlit as st
from datetime import datetime
from services.ai_service import AIService
from services.chat_service import ChatService
from services.document_service import DocumentService
from services.report_service import ReportService

def render_chat():
    """Render chat interface"""
    st.title("SEC Intelligence Chat")
    
    # Initialize services
    ai_service = AIService()
    chat_service = ChatService()
    doc_service = DocumentService()
    report_service = ReportService()
    
    # Sidebar with chat sessions
    with st.sidebar:
        st.subheader("Chat Sessions")
        
        # New chat button
        if st.button("New Chat", use_container_width=True):
            new_session_id = chat_service.create_session()
            st.session_state.current_chat_id = new_session_id
            st.rerun()
        
        # Recent sessions
        recent_sessions = chat_service.get_recent_sessions(10)
        
        for session in recent_sessions:
            if st.button(
                session['title'],
                key=f"session_{session['id']}",
                use_container_width=True,
                type="secondary" if session['id'] != st.session_state.get('current_chat_id') else "primary"
            ):
                st.session_state.current_chat_id = session['id']
                st.rerun()
    
    # Main chat area
    if 'current_chat_id' not in st.session_state:
        st.session_state.current_chat_id = chat_service.create_session()
    
    current_session = chat_service.get_session(st.session_state.current_chat_id)
    
    if not current_session:
        st.error("Session not found")
        return
    
    # Show company context if available
    if hasattr(st.session_state, 'chat_context') and st.session_state.chat_context:
        st.info(f"Analyzing: {st.session_state.chat_context}")
        # Add context to session metadata
        current_session['metadata']['company'] = st.session_state.chat_context
    
    # Display chat messages
    for message in current_session['messages']:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
            
            # Show metadata for assistant messages
            if message['role'] == 'assistant' and message.get('metadata'):
                metadata = message['metadata']
                
                # Confidence score
                if 'confidence' in metadata:
                    confidence = metadata['confidence']
                    if confidence > 0.9:
                        st.success(f"Confidence: {confidence:.0%}")
                    elif confidence > 0.7:
                        st.warning(f"Confidence: {confidence:.0%}")
                    else:
                        st.error(f"Confidence: {confidence:.0%}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("View Sources", key=f"view_{message['timestamp']}"):
                        show_sources(metadata.get('sources', []))
                
                with col2:
                    if st.button("Generate Report", key=f"report_{message['timestamp']}"):
                        generate_report(current_session, report_service)
                
                with col3:
                    if 'sources' in metadata and metadata['sources']:
                        source = metadata['sources'][0]
                        if st.button("Download", key=f"dl_{message['timestamp']}"):
                            st.info("Download feature coming soon")
    
    # Chat input
    if prompt := st.chat_input("Ask about any SEC filing..."):
        # Add user message
        chat_service.add_message(
            st.session_state.current_chat_id,
            "user",
            prompt
        )
        
        # Show user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing SEC filings..."):
                # Detect company from context or query
                company = current_session.get('metadata', {}).get('company')
                if not company:
                    # Try to extract from query
                    companies = doc_service.get_companies()
                    for c in companies:
                        if c.lower() in prompt.lower():
                            company = c
                            break
                
                # Search for relevant documents
                context = ai_service.search_documents(prompt, company)
                
                if context:
                    # Get AI response
                    response, confidence = ai_service.get_ai_response(prompt, context)
                    
                    st.markdown(response)
                    
                    # Save to chat history
                    chat_service.add_message(
                        st.session_state.current_chat_id,
                        "assistant",
                        response,
                        {
                            'sources': context[:3],
                            'confidence': confidence,
                            'company': company
                        }
                    )
                else:
                    no_docs_msg = "I couldn't find any relevant documents for your query. Try being more specific or mentioning a company ticker."
                    st.markdown(no_docs_msg)
                    
                    chat_service.add_message(
                        st.session_state.current_chat_id,
                        "assistant",
                        no_docs_msg
                    )
        
        st.rerun()

def show_sources(sources):
    """Display source documents"""
    if not sources:
        st.info("No sources available")
        return
    
    with st.expander("View Sources"):
        for i, source in enumerate(sources):
            st.markdown(f"**Source {i+1}:** {source['metadata'].get('source', 'Unknown')}")
            st.markdown(f"**Relevance Score:** {source.get('score', 0):.2%}")
            st.text_area(
                "Content Preview",
                source['content'][:500] + "...",
                height=150,
                key=f"source_content_{i}"
            )
            st.markdown("---")

def generate_report(session_data, report_service):
    """Generate and download report"""
    with st.spinner("Generating report..."):
        report_bytes = report_service.generate_chat_report(
            session_data,
            session_data.get('metadata', {}).get('company')
        )
        
        st.download_button(
            label="Download Report (PDF)",
            data=report_bytes,
            file_name=f"hedge_intel_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )
