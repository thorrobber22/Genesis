"""
components/ai_assistant_v2.py - Refined contextual AI interface
"""

import streamlit as st

def render_ai_assistant_v2():
    """Render contextual AI assistant per feedback"""
    
    # Determine context
    context_parts = []
    if st.session_state.selected_company:
        context_parts.append(st.session_state.selected_company)
    if st.session_state.ai_context.get('document'):
        context_parts.append(st.session_state.ai_context['document'])
    
    # Centered container with max width
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if context_parts:
            # Context indicator
            context_text = " > ".join(context_parts)
            st.caption(f"Ready to answer questions about {context_text}")
            
            # Input with send button
            col_input, col_send = st.columns([5, 1])
            
            with col_input:
                user_input = st.text_input(
                    label="Ask a question",
                    placeholder="What are the key risks? What's the revenue trend?",
                    key="ai_input_contextual",
                    label_visibility="collapsed"
                )
            
            with col_send:
                if st.button("Send", type="primary", use_container_width=True):
                    if user_input:
                        st.info("AI integration coming in Phase 4")
        else:
            # No context - centered prompt
            st.markdown(
                '<div style="text-align: center; padding: 40px 0;">'
                '<p style="color: #666; margin-bottom: 16px;">Search for a company to begin</p>'
                '</div>',
                unsafe_allow_html=True
            )
