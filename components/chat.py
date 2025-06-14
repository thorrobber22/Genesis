"""
Enhanced Chat Component
Date: 2025-06-14 13:09:40 UTC
"""

import streamlit as st
from services.ai_service_enhanced import ai_service
from services.document_indexer import DocumentIndexer
from pathlib import Path

def render_chat_panel():
    """Functional chat connected to indexed documents"""
    
    st.markdown("### Document Assistant")
    
    if st.session_state.selected_company == 'AIRO' and st.session_state.selected_document:
        # Initialize indexer
        indexer = DocumentIndexer()
        
        st.caption(f"AIRO - {st.session_state.selected_document[:30]}...")
        
        # Quick action buttons with real search
        quick_questions = [
            ("What are the key financials?", "financial revenue earnings income statement"),
            ("Show risk factors", "risk factors business risks"),
            ("What are the lockup terms?", "lockup lock-up period shares restriction")
        ]
        
        for question, search_terms in quick_questions:
            if st.button(f"• {question}", key=f"quick_{search_terms[:10]}"):
                # Add user message
                st.session_state.chat_messages.append({
                    'role': 'user',
                    'content': question
                })
                
                # Search the indexed documents
                results = indexer.search(f"AIRO {search_terms}", limit=3)
                
                if results:
                    # Build context from search results
                    context_parts = []
                    citations = []
                    
                    for i, result in enumerate(results):
                        context_parts.append(result['text'][:500])
                        section_title = result['metadata'].get('section_title', 'Document')
                        citations.append(f"[{section_title}]")
                    
                    # Get AI response with context
                    response = ai_service.get_document_response(
                        question,
                        {
                            'document': st.session_state.selected_document,
                            'context': '\n\n'.join(context_parts),
                            'company': 'AIRO Group Holdings'
                        }
                    )
                    
                    # Format response with citations
                    answer = response['answer']
                    if citations:
                        answer += "\n\n**Sources:** " + ", ".join(citations)
                    
                    st.session_state.chat_messages.append({
                        'role': 'assistant',
                        'content': answer
                    })
                else:
                    # Use AI without specific context
                    response = ai_service.get_document_response(
                        question,
                        {
                            'document': st.session_state.selected_document,
                            'company': 'AIRO Group Holdings'
                        }
                    )
                    
                    st.session_state.chat_messages.append({
                        'role': 'assistant',
                        'content': response['answer']
                    })
                
                st.rerun()
        
        # Display chat messages
        st.markdown("---")
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_messages[-5:]:
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['content']}")
                else:
                    st.markdown(f"**Assistant:** {msg['content']}")
        
        # Chat input area
        st.markdown("---")
        user_input = st.text_area("Ask about this document...", height=60, key="chat_input_area")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            send_button = st.button("Send", key="send_chat", use_container_width=True)
        
        if send_button and user_input:
            # Add user message
            st.session_state.chat_messages.append({
                'role': 'user',
                'content': user_input
            })
            
            # Search indexed documents
            search_query = f"AIRO {user_input}"
            results = indexer.search(search_query, limit=5)
            
            if results:
                # Build context from search results
                context_parts = []
                citations = []
                
                for i, result in enumerate(results[:3]):
                    context_parts.append(f"Section {i+1}: {result['text'][:500]}")
                    section_title = result['metadata'].get('section_title', f'Section {i+1}')
                    citations.append(section_title)
                
                # Get AI response
                response = ai_service.get_document_response(
                    user_input,
                    {
                        'document': st.session_state.selected_document,
                        'context': '\n\n'.join(context_parts),
                        'search_results': len(results),
                        'company': 'AIRO Group Holdings'
                    }
                )
                
                # Add citations to response
                answer = response['answer']
                if citations:
                    answer += "\n\n**Found in:** " + ", ".join(set(citations[:3]))
                
                st.session_state.chat_messages.append({
                    'role': 'assistant',
                    'content': answer
                })
            else:
                # Fallback to general AI response
                response = ai_service.get_document_response(
                    user_input,
                    {
                        'document': st.session_state.selected_document,
                        'company': 'AIRO Group Holdings',
                        'note': 'No specific sections found, providing general analysis'
                    }
                )
                
                st.session_state.chat_messages.append({
                    'role': 'assistant',
                    'content': response['answer'] + "\n\n*Note: This is a general response. Try asking about specific topics like financials, risks, or business model.*"
                })
            
            st.rerun()
        
        # Add to Report functionality (visual only for now)
        if len(st.session_state.chat_messages) > 0:
            st.markdown("---")
            if st.button("+ Add Last Response to Report", key="add_to_report"):
                st.success("Added to report! ✓")
                
    else:
        st.info("Select a document to start analyzing")
