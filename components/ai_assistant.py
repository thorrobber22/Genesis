"""
components/ai_assistant.py - Professional AI interface per spec
"""

import streamlit as st

def render_ai_assistant():
    """Render AI assistant interface - fixed bottom, context-aware"""
    
    # Context indicator
    context_parts = []
    if st.session_state.selected_company:
        context_parts.append(st.session_state.selected_company)
    if st.session_state.ai_context.get('document'):
        context_parts.append(st.session_state.ai_context['document'])
    
    if context_parts:
        st.caption(f"Currently analyzing: {' > '.join(context_parts)}")
    else:
        st.caption("Search for a company to begin")
    
    # Chat interface - max width 700px as per spec
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        col_input, col_send = st.columns([5, 1])
        
        with col_input:
            user_input = st.text_input(
                label="AI Assistant",
                placeholder="Ask a question..." if context_parts else "Search for a company to begin",
                key="ai_input",
                label_visibility="collapsed"
            )
        
        with col_send:
            send_button = st.button("Send", type="primary", use_container_width=True)
            
        if send_button and user_input and context_parts:
            # Will connect to AI service in Phase 4
            st.info("AI integration coming in Phase 4. Your query has been recorded.")
