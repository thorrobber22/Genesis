"""
navigation.py - Centralized navigation system
REASONING: Replace all switch_page calls with session state navigation
to prevent crashes and maintain consistency
"""

import streamlit as st

def init_navigation():
    """Initialize navigation in session state"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard'
    
    if 'page_params' not in st.session_state:
        st.session_state.page_params = {}

def navigate_to(page, **params):
    """Navigate to a page with optional parameters"""
    st.session_state.current_page = page
    st.session_state.page_params = params
    st.rerun()

def get_current_page():
    """Get current page and parameters"""
    return st.session_state.get('current_page', 'Dashboard'), st.session_state.get('page_params', {})

def render_sidebar():
    """Render navigation sidebar"""
    st.sidebar.title("🏢 Hedge Intelligence")
    
    pages = {
        'Dashboard': '📊',
        'IPO Tracker': '📈', 
        'Companies': '🏢',
        'AI Assistant': '🤖'
    }
    
    for page, icon in pages.items():
        if st.sidebar.button(f"{icon} {page}", key=f"nav_{page}", use_container_width=True):
            navigate_to(page)
    
    # Show current page
    current, _ = get_current_page()
    st.sidebar.markdown(f"**Current: {current}**")
