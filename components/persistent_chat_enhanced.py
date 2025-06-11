#!/usr/bin/env python3
"""
Enhanced Persistent Chat with Document Awareness and Citations - Fixed for OpenAI v1.0+
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime
from openai import OpenAI
from typing import List, Dict, Optional
import re
import os

from services.document_indexer import DocumentIndexer
from services.ai_service import AIService

class PersistentChatEnhanced:
    def __init__(self):
        self.indexer = DocumentIndexer()
        
        # Initialize OpenAI client
        api_key = os.environ.get('OPENAI_API_KEY') or st.session_state.get('api_key')
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
        
        # Initialize session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'chat_context' not in st.session_state:
            st.session_state.chat_context = {
                'current_document': None,
                'current_company': None,
                'conversation_id': datetime.now().isoformat()
            }
    
    def render(self, container=None):
        """Render the chat interface"""
        if container:
            with container:
                self._render_chat_ui()
        else:
            self._render_chat_ui()
    
    def _render_chat_ui(self):
        """Render the chat UI components"""
        # Chat header with context
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 💬 AI Assistant")
            
            # Show current context
            if st.session_state.chat_context['current_company']:
                st.caption(f"📊 Analyzing: {st.session_state.chat_context['current_company']}")
            
            if st.session_state.chat_context['current_document']:
                doc_name = Path(st.session_state.chat_context['current_document']).name
                st.caption(f"📄 Document: {doc_name[:50]}...")
        
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for message in st.session_state.chat_history:
                self._display_message(message)
        
        # Input area
        with st.container():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                user_input = st.text_input(
                    "Ask about the documents...",
                    key="chat_input",
                    placeholder="e.g., What is the company's revenue? Show me risk factors."
                )
            
            with col2:
                send_button = st.button("Send", use_container_width=True, type="primary")
            
            if send_button and user_input:
                self._process_user_input(user_input)
    
    def _display_message(self, message: Dict):
        """Display a chat message with proper formatting"""
        if message['role'] == 'user':
            with st.chat_message("user"):
                st.write(message['content'])
        else:
            with st.chat_message("assistant"):
                # Display main content
                st.write(message['content'])
                
                # Display citations if available
                if 'citations' in message and message['citations']:
                    with st.expander("📚 Sources", expanded=False):
                        for citation in message['citations']:
                            col1, col2 = st.columns([4, 1])
                            
                            with col1:
                                st.caption(
                                    f"**{citation['company']}** - {citation['form_type']} "
                                    f"({citation['filing_date']})"
                                )
                                st.caption(f"Section: {citation['section_title']}")
                                
                                # Show snippet
                                snippet = citation.get('snippet', '')[:200] + '...'
                                st.caption(f"*\"{snippet}\"*")
                            
                            with col2:
                                # View button
                                if st.button(
                                    "View",
                                    key=f"view_{citation.get('id', '')}_{message.get('timestamp', '')}",
                                    use_container_width=True
                                ):
                                    # Set the document in session state
                                    st.session_state['selected_document'] = citation['file_path']
                                    st.session_state['jump_to_section'] = citation.get('section_title')
                                    st.rerun()
    
    def _process_user_input(self, user_input: str):
        """Process user input and generate response"""
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Show thinking message
        with st.spinner("🤔 Analyzing documents..."):
            # Search for relevant content
            search_results = self._search_relevant_content(user_input)
            
            # Generate response with citations
            response = self._generate_response_with_citations(user_input, search_results)
            
            # Add to history
            st.session_state.chat_history.append(response)
        
        # Rerun to show new message
        st.rerun()
    
    def _search_relevant_content(self, query: str) -> Dict:
        """Search for relevant content in indexed documents"""
        # Add context to search
        enhanced_query = query
        
        # If we have a current company, prioritize it
        ticker = None
        if st.session_state.chat_context['current_company']:
            ticker = st.session_state.chat_context['current_company']
        
        # Search
        results = self.indexer.search(
            query=enhanced_query,
            ticker=ticker,
            limit=5
        )
        
        return results
    
    def _generate_response_with_citations(self, user_input: str, search_results: Dict) -> Dict:
        """Generate AI response with citations"""
        # Check if OpenAI client is available
        if not self.client:
            return {
                'role': 'assistant',
                'content': "Please configure your OpenAI API key to use the AI assistant.",
                'citations': [],
                'timestamp': datetime.now().isoformat()
            }
        
        # Prepare context from search results
        context_pieces = []
        citations = []
        
        for i, result in enumerate(search_results.get('results', [])):
            # Add to context
            context_pieces.append(
                f"[Source {i+1}] {result['metadata']['company']} - "
                f"{result['metadata']['form_type']} - "
                f"{result['metadata']['section_title']}:\n"
                f"{result['content']}\n"
            )
            
            # Prepare citation
            citations.append({
                'id': result['id'],
                'company': result['metadata']['company'],
                'form_type': result['metadata']['form_type'],
                'filing_date': result['metadata']['filing_date'],
                'section_title': result['metadata']['section_title'],
                'file_path': result['metadata']['file_path'],
                'snippet': result['content'][:200]
            })
        
        # Build prompt
        context = "\n\n".join(context_pieces) if context_pieces else "No specific documents found."
        
        prompt = f"""You are a financial analyst assistant analyzing SEC documents.

Current context:
- Company: {st.session_state.chat_context.get('current_company', 'Multiple companies')}
- Available documents: {context}

User question: {user_input}

Instructions:
1. Answer based on the provided document context
2. Be specific and cite the source number [Source N] when referencing information
3. If the documents don't contain relevant information, say so
4. Focus on facts from the documents, not general knowledge

Response:"""

        # Get AI response
        try:
            # Use the new OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful financial analyst assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
            
        except Exception as e:
            ai_response = f"I encountered an error: {str(e)}. Please make sure the OpenAI API key is configured correctly."
        
        # Create response message
        return {
            'role': 'assistant',
            'content': ai_response,
            'citations': citations if context_pieces else [],
            'timestamp': datetime.now().isoformat(),
            'search_query': user_input,
            'results_found': len(search_results.get('results', []))
        }
    
    def set_context(self, company: Optional[str] = None, document: Optional[str] = None):
        """Set the current context for the chat"""
        if company:
            st.session_state.chat_context['current_company'] = company
        
        if document:
            st.session_state.chat_context['current_document'] = document

# Function to integrate with main app
def render_persistent_chat(company=None, document=None):
    """Render the persistent chat component"""
    chat = PersistentChatEnhanced()
    
    # Set context if provided
    if company or document:
        chat.set_context(company=company, document=document)
    
    chat.render()

# Test the chat
if __name__ == "__main__":
    st.set_page_config(page_title="Chat Test", layout="wide")
    
    st.title("🧪 Enhanced Chat Test")
    
    # Test controls
    col1, col2 = st.columns(2)
    
    with col1:
        test_company = st.text_input("Test Company", value="AAPL")
    
    with col2:
        if st.button("Set Context"):
            st.session_state.chat_context = {
                'current_company': test_company,
                'current_document': None,
                'conversation_id': datetime.now().isoformat()
            }
            st.success(f"Context set to {test_company}")
    
    # Render chat
    render_persistent_chat(company=test_company)