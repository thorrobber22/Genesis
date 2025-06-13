"""
Hedge Fund Intelligence System
Version: 2.0
User: thorrobber22
Date: 2025-06-11
"""

import streamlit as st
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Hedge Fund Intelligence",
    page_icon="📈",
    layout="wide"
)

# Import services
from services.document_indexer import DocumentIndexer
from services.ai_chat import AIChat

# Import components
from components.dashboard import render_dashboard
from components.ai_chat_dual import render_enhanced_ai_chat
from components.document_explorer import render_document_explorer
from components.persistent_chat_enhanced import PersistentChatEnhanced
from components.smart_watchlist_minimal import render_smart_watchlist
from components.ipo_tracker import render_ipo_tracker
from components.tickers import render_tickers

# Import admin
try:
    from admin.admin_panel import render_admin_panel
    has_admin = True
except ImportError:
    has_admin = False

# Initialize services
@st.cache_resource
def init_services():
    return DocumentIndexer(), AIChat()

indexer, ai_chat = init_services()

# Sidebar
with st.sidebar:
    st.title("📈 Hedge Fund Intel")
    
    # Document count
    doc_count = indexer.collection.count()
    st.metric("Documents", f"{doc_count:,}")
    
    # Navigation
    pages = ["Dashboard", "AI Chat", "Documents", "Watchlist", "IPO Tracker", "Companies"]
    if has_admin:
        pages.append("Admin")
    
    page = st.selectbox("Navigation", pages)
    
    # Info
    st.markdown("---")
    st.caption("**Version 2.0**")
    st.caption("User: thorrobber22")

# Route to pages
if page == "Dashboard":
    render_dashboard()
elif page == "AI Chat":
    render_enhanced_ai_chat()
elif page == "Documents":
    render_document_explorer()
elif page == "Watchlist":
    render_smart_watchlist()
elif page == "IPO Tracker":
    render_ipo_tracker()
elif page == "Companies":
    render_tickers()
elif page == "Admin" and has_admin:
    render_admin_panel()
