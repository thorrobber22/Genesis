"""
Hedge Intelligence - IPO Intelligence Terminal
Final Refinements - June 11, 2025 20:18:25 UTC
User: thorrobber22
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime

# Import modular components
from components.financial_analysis import show_financial_analysis
from components.watchlist import show_watchlist
from components.chat import show_chat as show_chat_v2

# Terminal configuration
st.set_page_config(
    page_title="Hedge Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Final refined CSS with all fixes
st.markdown("""
<style>
    /* ===== FINAL REFINED STYLING ===== */
    
    /* Base styles - NO CHANGES to color scheme */
    html, body, .stApp {
        background-color: #1E1E1E !important;
        color: #F7F7F8 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        height: 100vh;
        overflow: hidden;
    }
    
    /* Hide Streamlit chrome */
    #MainMenu, footer, header, .stDeployButton, .viewerBadge_container__1QSob {
        display: none !important;
    }
    
    /* Prevent main scroll - ONLY chat scrolls */
    .main > .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    
    /* Fixed viewport container */
    .app-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        flex-direction: column;
        background-color: #1E1E1E;
    }
    
    /* Navigation bar - fixed positioning */
    .nav-container {
        height: 48px;
        background-color: #202123;
        border-bottom: 1px solid #2E2E2E;
        display: flex;
        align-items: center;
        padding: 0 24px;
        flex-shrink: 0;
        z-index: 100;
    }
    
    /* Content wrapper - fills remaining space */
    .content-wrapper {
        flex: 1;
        display: flex;
        overflow: hidden;
        position: relative;
    }
    
    /* Sidebar - no scroll issues */
    .sidebar-left {
        width: 260px;
        background-color: #202123;
        border-right: 1px solid #2E2E2E;
        padding: 20px;
        overflow-y: auto;
        flex-shrink: 0;
    }
    
    /* Main content */
    .main-content {
        flex: 1;
        background-color: #1E1E1E;
        padding: 24px;
        overflow-y: auto;
        position: relative;
    }
    
    /* Context panel */
    .context-panel {
        width: 320px;
        background-color: #202123;
        border-left: 1px solid #2E2E2E;
        padding: 20px;
        overflow-y: auto;
        flex-shrink: 0;
    }
    
    /* ===== CHAT BAR - FIXED TO BOTTOM ===== */
    .chat-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 80px;
        background-color: #40414F;
        border-top: 1px solid #565869;
        padding: 16px 24px;
        display: flex;
        align-items: center;
        gap: 16px;
        z-index: 1000;
    }
    
    /* Chat input styling */
    .stChatInput {
        background-color: transparent !important;
        border: none !important;
    }
    
    .stChatInput > div {
        background-color: #40414F !important;
        border: 1px solid #565869 !important;
        border-radius: 8px !important;
        transition: all 0.2s !important;
    }
    
    .stChatInput > div:hover {
        background-color: #4B4D5D !important;
        border-color: #4B4D5D !important;
    }
    
    .stChatInput textarea {
        background-color: transparent !important;
        color: #ECECF1 !important;
        border: none !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
        padding: 8px 12px !important;
    }
    
    /* ===== BUTTONS - AUTO-RESIZE, NO WORD BREAK ===== */
    .stButton > button {
        background-color: transparent !important;
        color: #F7F7F8 !important;
        border: 1px solid #565869 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 6px 12px !important;
        min-width: auto !important;
        width: auto !important;
        height: auto !important;
        line-height: 1.5 !important;
        border-radius: 6px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    
    .stButton > button:hover {
        background-color: #4B4D5D !important;
        color: #F7F7F8 !important;
        border-color: #2E8AF6 !important;
    }
    
    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background-color: #2E8AF6 !important;
        border-color: #2E8AF6 !important;
        color: #F7F7F8 !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #2563EB !important;
        border-color: #2563EB !important;
    }
    
    /* ===== NAVIGATION TABS ===== */
    .nav-tab {
        color: #A3A3A3;
        font-size: 14px;
        font-weight: 500;
        padding: 8px 16px;
        margin-right: 8px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid transparent;
        white-space: nowrap;
    }
    
    .nav-tab:hover {
        color: #F7F7F8;
        background-color: #2A2B2D;
    }
    
    .nav-tab.active {
        color: #2E8AF6;
        background-color: #2A2B2D;
        border-bottom: 2px solid #2E8AF6;
    }
    
    /* ===== METRICS PAGE - PILL STYLE ===== */
    .metrics-container {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 24px;
    }
    
    .metric-pill {
        display: inline-flex;
        align-items: center;
        background-color: #2A2B2D;
        border: 1px solid #2E2E2E;
        border-radius: 24px;
        padding: 12px 20px;
        cursor: pointer;
        transition: all 0.2s;
        gap: 8px;
    }
    
    .metric-pill:hover {
        background-color: #4B4D5D;
        border-color: #2E8AF6;
        transform: translateY(-1px);
    }
    
    .metric-pill-value {
        font-size: 18px;
        font-weight: 600;
        color: #2E8AF6;
    }
    
    .metric-pill-label {
        font-size: 13px;
        color: #A3A3A3;
        font-weight: 500;
    }
    
    /* ===== TEXT HOVER STATES ===== */
    a, .clickable-text {
        color: #2E8AF6 !important;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    a:hover, .clickable-text:hover {
        color: #F7F7F8 !important;
        text-decoration: underline;
        opacity: 0.9;
    }
    
    /* ===== SECTOR DROPDOWNS - NO SHIFT ===== */
    .streamlit-expanderHeader {
        background-color: #2A2B2D !important;
        border: 1px solid #2E2E2E !important;
        border-radius: 6px !important;
        color: #F7F7F8 !important;
        font-size: 14px !important;
        padding: 12px 16px !important;
        margin-bottom: 8px !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #4B4D5D !important;
        border-color: #2E8AF6 !important;
    }
    
    .streamlit-expanderContent {
        background-color: transparent !important;
        padding: 0 !important;
        margin-top: -8px !important;
    }
    
    /* ===== CONTEXT PANEL STYLING ===== */
    .context-section {
        margin-bottom: 20px;
        padding-bottom: 20px;
        border-bottom: 1px solid #2E2E2E;
    }
    
    .context-section:last-child {
        border-bottom: none;
    }
    
    .context-label {
        font-size: 11px;
        font-weight: 600;
        color: #A3A3A3;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    
    .context-value {
        font-size: 13px;
        color: #F7F7F8;
        font-weight: 400;
    }
    
    /* ===== TABLE STYLING ===== */
    .data-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .data-table th {
        background-color: transparent;
        color: #A3A3A3;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 8px 12px;
        border-bottom: 1px solid #2E2E2E;
        text-align: left;
    }
    
    .data-table td {
        padding: 12px;
        border-bottom: 1px solid #2E2E2E;
        color: #F7F7F8;
        font-size: 13px;
    }
    
    .data-table tr:hover td {
        background-color: #2A2B2D;
        cursor: pointer;
    }
    
    /* ===== SCROLLBAR STYLING ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #2B2B2F;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4D4D4D;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #565869;
    }
    
    /* ===== CHAT LOG SCROLL ===== */
    .chat-messages {
        max-height: calc(100vh - 200px);
        overflow-y: auto;
        padding: 16px;
    }
    
    /* ===== INPUT FIELDS ===== */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #40414F !important;
        border: 1px solid #565869 !important;
        color: #ECECF1 !important;
        font-size: 13px !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        transition: all 0.2s !important;
    }
    
    .stTextInput > div > div > input:hover,
    .stSelectbox > div > div > select:hover {
        background-color: #4B4D5D !important;
        border-color: #4B4D5D !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        background-color: #4B4D5D !important;
        border-color: #2E8AF6 !important;
        outline: none !important;
    }
    
    /* ===== SPACING FIXES ===== */
    .element-container {
        margin-bottom: 0.75rem !important;
    }
    
    .stMarkdown {
        margin-bottom: 0 !important;
    }
    
    h1, h2, h3 {
        margin-top: 0 !important;
        margin-bottom: 16px !important;
    }
    
    /* ===== TICKER BADGES ===== */
    .ticker-badge {
        display: inline-block;
        padding: 4px 8px;
        background-color: #2A2B2D;
        border: 1px solid #2E8AF6;
        border-radius: 4px;
        color: #2E8AF6;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .ticker-badge:hover {
        background-color: #2E8AF6;
        color: #F7F7F8;
    }
    
    /* ===== PREVENT LAYOUT SHIFT ===== */
    .main > div {
        overflow: hidden !important;
        position: relative !important;
    }
    
    /* Status indicators */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    
    .status-active {
        background-color: #2E8AF6;
    }
    
    .status-inactive {
        background-color: #A3A3A3;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'ipo_calendar'
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'ai_service' not in st.session_state:
    try:
        from services.ai_service import AIService
        st.session_state.ai_service = AIService()
    except Exception as e:
        st.session_state.ai_service = None

def main():
    """Main application with final refinements"""
    
    # Create app container
    st.markdown('<div class="app-container">', unsafe_allow_html=True)
    
    # Navigation
    render_navigation()
    
    # Content area
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    # Three-column layout
    col_left, col_main, col_right = st.columns([1.2, 3, 1.5])
    
    with col_left:
        render_sidebar()
    
    with col_main:
        render_main_content()
    
    with col_right:
        render_context_panel()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fixed chat bar
    render_chat_bar()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_navigation():
    """Render navigation with proper styling"""
    nav_items = ['IPO Calendar', 'Companies', 'Metrics', 'Watchlist', 'Financial Analysis']
    
    cols = st.columns(len(nav_items))
    for idx, item in enumerate(nav_items):
        with cols[idx]:
            key = item.lower().replace(' ', '_')
            is_active = st.session_state.active_tab == key
            
            if st.button(
                item.upper(),
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.active_tab = key
                st.rerun()

def render_sidebar():
    """Render sidebar with no shift issues"""
    if st.session_state.active_tab == 'ipo_calendar':
        st.markdown("### FILTERS")
        
        # Compact filter options
        st.selectbox("Period", ["This Week", "Next Week", "This Month", "All"], key="period_filter")
        st.selectbox("Status", ["All", "Filed", "Priced", "Withdrawn"], key="status_filter")
        st.selectbox("Exchange", ["All", "NYSE", "NASDAQ"], key="exchange_filter")
        
    elif st.session_state.active_tab == 'companies':
        st.markdown("### SECTORS")
        
        # Sector navigation with no shift
        sectors = {
            "Technology": 12,
            "Healthcare": 8,
            "Financial": 6,
            "Energy": 4,
            "Consumer": 5
        }
        
        for sector, count in sectors.items():
            with st.expander(f"{sector} ({count})", expanded=False):
                companies = get_companies_by_sector(sector)
                for company in companies:
                    if st.button(
                        f"{company['ticker']}",
                        key=f"co_{company['ticker']}",
                        use_container_width=True
                    ):
                        st.session_state.selected_ticker = company['ticker']
                        st.rerun()

def render_main_content():
    """Render main content area"""
    if st.session_state.active_tab == 'ipo_calendar':
        render_ipo_calendar()
    elif st.session_state.active_tab == 'companies':
        render_companies_view()
    elif st.session_state.active_tab == 'metrics':
        render_metrics_dashboard()
    elif st.session_state.active_tab == 'watchlist':
        show_watchlist()

def render_context_panel():
    """Render context panel with proper sections"""    if st.session_state.selected_ticker:
        ticker = st.session_state.selected_ticker
        st.markdown(f"### {ticker}")
        
        # Context sections with dividers
        sections = [
            {
                "title": "OVERVIEW",
                "items": [
                    ("Exchange", "NYSE"),
                    ("Sector", "Technology"),
                    ("IPO Date", "2025-01-15")
                ]
            },
            {
                "title": "FINANCIALS",
                "items": [
                    ("IPO Price", "$24.00"),
                    ("Current", "$31.50"),
                    ("Change", "+31.25%")
                ]
            },
            {
                "title": "KEY DATES",
                "items": [
                    ("Lockup Ends", "2025-07-15"),
                    ("Days Remaining", "186"),
                    ("Lead Underwriter", "Goldman Sachs")
                ]
            }
        ]
        
        for section in sections:
            st.markdown(f"**{section['title']}**")
            for label, value in section['items']:
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown(f"<p class='context-label'>{label}</p>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<p class='context-value'>{value}</p>", unsafe_allow_html=True)
            st.markdown("---")
        
        # Quick actions
        st.markdown("**QUICK ACTIONS**")
        col1, col2 = st.columns(2)
        with col1:
            st.button("→ S-1", use_container_width=True, key="action_s1")
        with col2:
            st.button("→ 424B4", use_container_width=True, key="action_424b4")
    else:
        st.markdown("### CONTEXT")
        st.caption("Select a ticker to view details")

def render_chat_bar():
    """Render fixed chat bar - WORKING VERSION"""
    # Spacing for fixed chat
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Chat interface
    col1, col2, col3 = st.columns([2, 6, 1])
    
    with col1:
        if st.session_state.selected_ticker:
            st.markdown(f"<span class='ticker-badge'>{st.session_state.selected_ticker}</span> selected", unsafe_allow_html=True)
        else:
            st.caption("Chat available for all queries")
    
    with col2:
        # Chat input that actually works
        user_query = st.chat_input(
            placeholder="Ask about any IPO, filing, or market trend..."
        )
        
        if user_query:
            # Add to chat history
            st.session_state.chat_messages.append({"role": "user", "content": user_query})
            
            # Get AI response if service is available
            if st.session_state.ai_service:
                try:
                    # Add context if ticker selected
                    if st.session_state.selected_ticker:
                        context_query = f"[Context: {st.session_state.selected_ticker}] {user_query}"
                        response = st.session_state.ai_service.chat(context_query)
                    else:
                        response = st.session_state.ai_service.chat(user_query)
                    
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.session_state.chat_messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
            else:
                # Fallback response
                st.session_state.chat_messages.append({"role": "assistant", "content": "AI service initializing..."})
            
            st.rerun()
    
    with col3:
        status_class = "status-active" if st.session_state.ai_service else "status-inactive"
        st.markdown(f"<span class='status-dot {status_class}'></span>AI Active", unsafe_allow_html=True)

def render_ipo_calendar():
    """IPO Calendar view"""
    st.markdown("# IPO Calendar")
    st.caption("Real-time tracking of IPO filings and market activity")
    
    # Sample data
    ipos = [
        {"date": "2025-06-15", "ticker": "TECH", "company": "TechCorp International", "exchange": "NYSE", 
         "lead": "Goldman Sachs", "size": "$250M", "cap": "$2.5B", "docs": 8},
        {"date": "2025-06-14", "ticker": "BIO", "company": "BioMed Solutions", "exchange": "NASDAQ",
         "lead": "Morgan Stanley", "size": "$180M", "cap": "$1.8B", "docs": 6},
        {"date": "2025-06-13", "ticker": "FINX", "company": "FinTech Innovations", "exchange": "NYSE",
         "lead": "J.P. Morgan", "size": "$320M", "cap": "$3.2B", "docs": 10}
    ]
    
    # Table
    for ipo in ipos:
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 2.5, 1, 2, 1, 1, 0.5])
        
        with col1:
            st.caption(ipo['date'])
        with col2:
            if st.button(ipo['ticker'], key=f"ipo_{ipo['ticker']}"):
                st.session_state.selected_ticker = ipo['ticker']
                st.rerun()
        with col3:
            st.text(ipo['company'])
        with col4:
            st.text(ipo['exchange'])
        with col5:
            st.text(ipo['lead'])
        with col6:
            st.text(ipo['size'])
        with col7:
            st.text(ipo['cap'])
        with col8:
            st.text(str(ipo['docs']))

def render_companies_view():
    """Companies detail view"""
    if st.session_state.selected_ticker:
        ticker = st.session_state.selected_ticker
        
        # Header with metrics
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.markdown(f"# {ticker}")
            st.caption("Technology • NYSE")
        
        with col2:
            st.metric("DOCUMENTS", "12")
        
        with col3:
            st.metric("LAST FILING", "Jun 01")
        
        with col4:
            st.metric("LOCKUP", "186d")
        
        st.markdown("---")
        
        # Documents
        st.markdown("### Recent Documents")
        
        docs = [
            {"type": "S-1", "date": "2025-06-01", "size": "2.4MB"},
            {"type": "S-1/A", "date": "2025-05-15", "size": "2.1MB"},
            {"type": "424B4", "date": "2025-05-01", "size": "1.8MB"}
        ]
        
        for doc in docs:
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                st.text(doc['type'])
            with col2:
                st.caption(doc['date'])
            with col3:
                st.text(doc['size'])
            with col4:
                st.button("OPEN", key=f"open_{doc['type']}_{doc['date']}")
    else:
        st.info("Select a company from the sidebar")

def render_metrics_dashboard():
    """Metrics dashboard with pill-style layout"""
    st.markdown("# Metrics Dashboard")
    st.caption("Click any metric to filter data")
    
    # Metrics in pill format
    st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
    
    metrics = [
        ("Active IPOs", "42", "ipo_active"),
        ("This Week", "7", "ipo_week"),
        ("Next Week", "5", "ipo_next"),
        ("30d Lockups", "12", "lockup_30"),
        ("60d Lockups", "18", "lockup_60"),
        ("NYSE", "24", "nyse"),
        ("NASDAQ", "18", "nasdaq"),
        ("Tech Sector", "15", "tech"),
        ("Healthcare", "10", "health"),
        ("Financial", "8", "fin"),
        ("Total Docs", "384", "docs"),
        ("S-1 Filings", "42", "s1")
    ]
    
    # Create metric pills
    cols = st.columns(6)
    for idx, (label, value, key) in enumerate(metrics):
        with cols[idx % 6]:
            if st.button(
                f"**{value}** {label}",
                key=f"metric_{key}",
                use_container_width=True
            ):
                st.session_state.active_tab = 'ipo_calendar'
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional analytics
    st.markdown("---")
    st.markdown("### Trend Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**IPO Volume by Week**")
        st.caption("Weekly filing trends")
        # Placeholder for chart
        st.info("Chart visualization coming in Phase 4")
    
    with col2:
        st.markdown("**Sector Distribution**")
        st.caption("Active IPOs by sector")
        # Placeholder for chart
        st.info("Chart visualization coming in Phase 4")

def get_companies_by_sector(sector):
    """Get companies for a sector"""
    companies = {
        "Technology": [
            {"ticker": "TECH", "name": "TechCorp"},
            {"ticker": "SOFT", "name": "SoftwareOne"},
            {"ticker": "CLOU", "name": "CloudBase"}
        ],
        "Healthcare": [
            {"ticker": "BIO", "name": "BioMed"},
            {"ticker": "PHRM", "name": "PharmaTech"}
        ],
        "Financial": [
            {"ticker": "FINX", "name": "FinTech"},
            {"ticker": "BANK", "name": "BankCorp"}
        ]
    }
    return companies.get(sector, [])

# Display chat messages if any
if st.session_state.chat_messages:
    st.markdown("### Chat History")
    for msg in st.session_state.chat_messages[-5:]:  # Show last 5 messages
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**AI:** {msg['content']}")

if __name__ == "__main__":
    main()
