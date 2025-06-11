"""
Hedge Intelligence - Chat Native Interface
Date: 2025-06-04
User: thorrobber22
"""

import streamlit as st
from datetime import datetime
from ui.components.chat_interface import ChatInterface
from ui.components.context_panel import ContextPanel
from ui.components.data_cards import DataCards
from core.chat_engine import ChatEngine
from ui.styles import load_custom_css

# Page config
st.set_page_config(
    page_title="Hedge Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_custom_css()

# Initialize components
@st.cache_resource
def init_chat_engine():
    return ChatEngine()

chat_engine = init_chat_engine()
chat_ui = ChatInterface(chat_engine)
context_panel = ContextPanel()
data_cards = DataCards()

# Check for pending questions
if "pending_question" in st.session_state:
    question = st.session_state.pending_question
    del st.session_state.pending_question
    # Add to messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    st.session_state.messages.append({
        "role": "user",
        "content": question,
        "time": datetime.now()
    })

# Sidebar
with st.sidebar:
    st.markdown("# HEDGE INTELLIGENCE")
    st.markdown("---")
    
    # Navigation (affects context panel)
    view = st.radio(
        "View",
        ["Chat", "Calendar", "Pricing", "Lock-ups", "Filings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### QUICK FILTERS")
    
    filter_option = st.selectbox(
        "Show",
        ["All IPOs (14)", "This Week (3)", "Full Coverage (6)", "Action Needed (2)"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption(f"Last Updated: {datetime.now().strftime('%I:%M %p')}")

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    # Chat is always visible
    st.markdown("### Today's IPO Updates")
    
    # System message if first load
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.messages = [{
            "role": "system",
            "content": "Good morning! 3 new IPOs were added today. CRCL and OMDA have full documentation.",
            "time": datetime.now()
        }]
    
    # Render chat with embedded data views
    if view == "Chat":
        chat_ui.render()
    elif view == "Calendar":
        chat_ui.render_with_card(data_cards.calendar_card())
    elif view == "Pricing":
        chat_ui.render_with_card(data_cards.pricing_card())
    elif view == "Lock-ups":
        chat_ui.render_with_card(data_cards.lockup_card())
    elif view == "Filings":
        chat_ui.render_with_card(data_cards.filings_card())

with col2:
    # Context panel updates based on chat
    current_ticker = chat_ui.get_current_context()
    context_panel.render(current_ticker)
