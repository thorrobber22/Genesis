"""
Chat Interface Component
"""

import streamlit as st
from datetime import datetime
import re

class ChatInterface:
    def __init__(self, chat_engine):
        self.chat_engine = chat_engine
        
    def render(self):
        """Render chat interface"""
        # Display message history
        for msg in st.session_state.get("messages", []):
            self._render_message(msg)
        
        # Persistent input bar
        self._render_input()
    
    def render_with_card(self, card_content):
        """Render chat with embedded data card"""
        # Show existing messages
        for msg in st.session_state.get("messages", []):
            self._render_message(msg)
        
        # Add card as system message
        with st.chat_message("assistant"):
            st.markdown(card_content)
        
        # Input bar
        self._render_input()
    
    def _render_message(self, msg):
        """Render a single message"""
        with st.chat_message(msg["role"]):
            # Time stamp
            if "time" in msg:
                st.caption(msg["time"].strftime("%I:%M %p"))
            
            # Message content
            st.markdown(msg["content"])
            
            # Action buttons for AI messages
            if msg["role"] == "assistant" and "actions" in msg:
                cols = st.columns(len(msg["actions"]))
                for idx, action in enumerate(msg["actions"]):
                    with cols[idx]:
                        if st.button(action["label"], key=f"{action['key']}_{msg.get('id', '')}"):
                            action["callback"]()
    
    def _render_input(self):
        """Render persistent input bar"""
        prompt = st.chat_input("Ask about IPOs, lock-ups, or pricing...")
        
        if prompt:
            # Add user message
            user_msg = {
                "role": "user",
                "content": prompt,
                "time": datetime.now()
            }
            st.session_state.messages.append(user_msg)
            
            # Get AI response
            response = self.chat_engine.get_response(prompt)
            
            # Add AI message
            ai_msg = {
                "role": "assistant",
                "content": response["content"],
                "time": datetime.now(),
                "actions": response.get("actions", [])
            }
            st.session_state.messages.append(ai_msg)
            
            # Rerun to show new messages
            st.rerun()
    
    def get_current_context(self):
        """Extract current ticker from conversation"""
        if "messages" not in st.session_state:
            return None
        
        # Look for tickers in recent messages
        for msg in reversed(st.session_state.messages[-5:]):
            tickers = re.findall(r'\b[A-Z]{2,5}\b', msg["content"])
            # Filter out common words
            tickers = [t for t in tickers if t not in ["IPO", "CEO", "NYSE", "NASDAQ", "AI", "PDF"]]
            if tickers:
                return tickers[0]
        
        return None
