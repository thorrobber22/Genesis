"""
Hedge Fund Intelligence - USER APPLICATION
Version: 2.0 - Separate from Admin
"""

import streamlit as st
from pathlib import Path
import os

# Page config
st.set_page_config(
    page_title="Hedge Fund Intelligence",
    page_icon="📈",
    layout="wide"
)

# Import only what we tested and know works
from components.persistent_chat_enhanced import PersistentChatEnhanced
from components.document_explorer import render_document_explorer
from components.smart_watchlist_minimal import render_smart_watchlist
from components.ipo_tracker import render_ipo_tracker
from components.dashboard import render_dashboard
from components.tickers import render_tickers

# Navigation
st.sidebar.title("📈 Hedge Fund Intelligence")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navigation",
    ["🏠 Dashboard", "💬 AI Chat", "📁 Documents", "📊 Watchlist", 
     "🚀 IPO Tracker", "🏢 Companies"]
)

# Main content
if page == "🏠 Dashboard":
    render_dashboard()
    
elif page == "💬 AI Chat":
    st.title("💬 AI Analysis Chat")
    st.caption("Chat with AI about SEC documents")
    
    # Use the working persistent chat
    chat = PersistentChatEnhanced()
    chat.render()
    
elif page == "📁 Documents":
    render_document_explorer()
    
elif page == "📊 Watchlist":
    render_smart_watchlist()
    
elif page == "🚀 IPO Tracker":
    render_ipo_tracker()
    
elif page == "🏢 Companies":
    render_tickers()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("User: thorrobber22")
st.sidebar.caption("Version 2.0")
