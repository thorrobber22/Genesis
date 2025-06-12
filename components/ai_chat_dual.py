#!/usr/bin/env python3
"""
Enhanced AI Chat with Dual AI Support (GPT-4 + Gemini)
Fixed version - handles DocumentIndexer.search() properly
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional
import os

# Import AI services
from services.ai_service import AIService
from services.gemini_service import GeminiService
from services.document_indexer import DocumentIndexer

class DualAIChat:
    def __init__(self):
        self.indexer = DocumentIndexer()
        
        # Initialize AI services
        self.gpt_service = None
        self.gemini_service = None
        
        # Check API keys
        self.gpt_available = bool(os.getenv('OPENAI_API_KEY'))
        self.gemini_available = bool(os.getenv('GEMINI_API_KEY'))
        
        if self.gpt_available:
            self.gpt_service = AIService()
        
        if self.gemini_available:
            try:
                self.gemini_service = GeminiService()
            except Exception as e:
                st.error(f"Gemini initialization error: {e}")
                self.gemini_available = False
        
        # Chat history
        self.history_file = Path("data/chat_history/dual_ai_history.json")
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
    
    def render_chat_interface(self):
        """Render the dual AI chat interface"""
        st.header("🤖 AI Analysis with Validation")
        
        # Model selection and status
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Show available models
            available_models = []
            if self.gpt_available:
                available_models.append("GPT-4")
            if self.gemini_available:
                available_models.append("Gemini")
            
            if not available_models:
                st.error("No AI models available. Please set API keys.")
                return
            
            if len(available_models) == 2:
                st.success("✅ Both AI models available for cross-validation")
            else:
                st.info(f"Using: {', '.join(available_models)}")
        
        with col2:
            use_validation = st.checkbox(
                "Cross-validate", 
                value=len(available_models) == 2,
                disabled=len(available_models) < 2
            )
        
        with col3:
            if st.button("Clear History", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        # Context info
        if 'selected_company' in st.session_state and st.session_state.selected_company:
            st.info(f"📄 Analyzing: {st.session_state.selected_company}")
        
        st.markdown("---")
        
        # Chat messages
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    # Show response with model info
                    if "model" in message:
                        st.caption(f"via {message['model']}")
                    
                    st.markdown(message["content"])
                    
                    # Show citations if available
                    if "citations" in message and message["citations"]:
                        with st.expander(f"📚 Sources ({len(message['citations'])})"):
                            for citation in message["citations"]:
                                st.markdown(f"**{citation.get('title', 'Untitled')}**")
                                st.caption(f"{citation.get('company', '')} - {citation.get('document', '')}")
                                st.caption(citation.get('text', '')[:200] + "...")
                                st.divider()
                    
                    # Show validation if available
                    if "validation" in message:
                        with st.expander("🔍 Cross-Validation"):
                            st.markdown(message["validation"])
                else:
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about the documents..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing documents..."):
                    response = self._get_ai_response(prompt, use_validation)
                    
                    # Show primary response
                    if response and "model" in response and response["model"]:
                        st.caption(f"via {response['model']}")
                    
                    st.markdown(response["content"])
                    
                    # Add to messages
                    message_data = {
                        "role": "assistant",
                        "content": response["content"],
                        "model": response["model"]
                    }
                    
                    # Show citations
                    if response.get("citations"):
                        message_data["citations"] = response["citations"]
                        with st.expander(f"📚 Sources ({len(response['citations'])})"):
                            for citation in response["citations"]:
                                st.markdown(f"**{citation.get('title', 'Untitled')}**")
                                st.caption(f"{citation.get('company', '')} - {citation.get('document', '')}")
                                st.divider()
                    
                    # Show validation if available
                    if response.get("validation"):
                        message_data["validation"] = response["validation"]
                        with st.expander("🔍 Cross-Validation", expanded=True):
                            st.markdown(response["validation"])
                    
                    st.session_state.messages.append(message_data)
                    
                    # Save to history
                    self._save_to_history(prompt, response)
    
    def _get_ai_response(self, query: str, use_validation: bool) -> Dict:
        """Get AI response with optional validation"""
    
    def _create_validation_summary(self, response1: Dict, response2: Dict, 
                                 model1: str, model2: str) -> str:
        """Create a validation summary comparing two responses"""
        summary = f"**Validation Summary**\n\n"
        
        # Compare citation counts
        citations1 = len(response1.get('citations', []))
        citations2 = len(response2.get('citations', []))
        
        summary += f"📚 **Citations**: {model1} used {citations1} sources, {model2} used {citations2} sources\n\n"
        
        # Note any major differences
        if abs(citations1 - citations2) > 3:
            summary += "⚠️ **Note**: Significant difference in source usage\n\n"
        
        summary += "✅ **Agreement Level**: "
        if citations1 > 0 and citations2 > 0:
            summary += "Both models found relevant information\n"
        else:
            summary += "One model may have found more relevant data\n"
        
        return summary
    
    def _save_to_history(self, query: str, response: Dict):
        """Save chat to history"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response['content'],
            'model': response['model'],
            'citations_count': len(response.get('citations', [])),
            'company': st.session_state.get('selected_company', 'Unknown')
        }
        
        # Load existing history
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(history_entry)
        
        # Keep last 100 entries
        history = history[-100:]
        
        # Save
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)

# Integration function
def render_dual_ai_chat():
    """Render the dual AI chat interface"""
    chat = DualAIChat()
    chat.render_chat_interface()

# Add this for the enhanced version
def render_enhanced_ai_chat():
    """Render the enhanced AI chat interface"""
    chat = DualAIChat()
    chat.render_chat_interface()

# Test
if __name__ == "__main__":
    st.set_page_config(page_title="Dual AI Chat Test", layout="wide")
    
    # Test with mock data
    st.session_state['selected_company'] = "AAPL"
    
    render_dual_ai_chat()