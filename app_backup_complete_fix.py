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
from components.chat import show_chat

# Terminal configuration
st.set_page_config(
    page_title="Hedge Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Final refined CSS with all fixes
st.markdown("""<style>
    /* ===== SPLIT SCREEN SYSTEM ===== */
    
    /* Base styles - YOUR EXACT THEME */
    html, body, .stApp {
        background-color: #1E1E1E !important;
        color: #F7F7F8 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Hide Streamlit chrome */
    #MainMenu, footer, header, .stDeployButton {
        display: none !important;
    }
    
    /* Main container */
    .main > .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        height: 100vh !important;
    }
    
    /* Smooth transitions for all elements */
    .main-content-area, .chat-panel-container, [data-testid="column"] {
        transition: all 0.3s ease !important;
    }
    
    /* Navigation */
    .stButton > button {
        background-color: transparent !important;
        color: #F7F7F8 !important;
        border: 1px solid #565869 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 6px 12px !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #4B4D5D !important;
        border-color: #2E8AF6 !important;
    }
    
    /* Chat panel styling */
    .chat-panel-container {
        background-color: #202123 !important;
        border-left: 2px solid #2E8AF6 !important;
        height: calc(100vh - 100px) !important;
        border-radius: 8px 0 0 0;
        box-shadow: -4px 0 12px rgba(0,0,0,0.3);
    }
    
    .chat-messages-container {
        height: calc(100vh - 200px);
        overflow-y: auto;
        padding: 16px;
    }
    
    /* Chat messages */
    .stChatMessage {
        margin-bottom: 12px !important;
    }
    
    [data-testid="stChatMessageContent"] {
        background-color: #2A2B2D !important;
        border: 1px solid #2E2E2E !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    
    [data-testid="stChatMessageUser"] [data-testid="stChatMessageContent"] {
        background-color: #40414F !important;
        border-color: #565869 !important;
        margin-left: 20%;
    }
    
    /* Compressed view adjustments */
    .compressed-view {
        font-size: 0.9em;
    }
    
    .compressed-view h1 {
        font-size: 1.5em !important;
    }
    
    .compressed-view h2 {
        font-size: 1.2em !important;
    }
    
    .compressed-view .stButton > button {
        padding: 4px 8px !important;
        font-size: 12px !important;
    }
    
    /* Close button special styling */
    button[key="close_chat"] {
        background: none !important;
        border: none !important;
        color: #A3A3A3 !important;
        font-size: 20px !important;
        padding: 4px !important;
        min-width: 32px !important;
        height: 32px !important;
    }
    
    button[key="close_chat"]:hover {
        background-color: #4B4D5D !important;
        color: #F7F7F8 !important;
        border-radius: 4px !important;
    }
    
    /* Chat input - always at bottom */
    .stChatInput {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background-color: #1E1E1E !important;
        border-top: 1px solid #2E2E2E !important;
        padding: 16px !important;
        z-index: 1000 !important;
    }
    
    .stChatInput > div > div {
        background-color: #40414F !important;
        border: 1px solid #565869 !important;
        border-radius: 8px !important;
        max-width: 800px !important;
        margin: 0 auto !important;
    }
    
    .stChatInput textarea {
        background-color: transparent !important;
        color: #ECECF1 !important;
        border: none !important;
        font-size: 14px !important;
        padding: 12px 16px !important;
    }
    
    /* Sidebar */
    .sidebar-content {
        background-color: #202123;
        padding: 20px;
        height: 100%;
    }
    
    /* Scrollbars */
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
    
    /* Animation overlay effect */
    @keyframes slideIn {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    
    .chat-panel-container {
        animation: slideIn 0.3s ease;
    }
    
    /* Responsive tables for compressed view */
    .compressed-view table {
        font-size: 12px;
    }
    
    .compressed-view th, .compressed-view td {
        padding: 6px !important;
    }
    
    /* Prevent content jump */
    .main {
        overflow-x: hidden !important;
    }
</style>""", unsafe_allow_html=True)

# Initialize session state
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'ipo_calendar'
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'chat_panel_open' not in st.session_state:
    st.session_state.chat_panel_open = False
if 'ai_service' not in st.session_state:
    st.session_state.ai_service = None  # Will initialize on first use
    except Exception as e:
        st.session_state.ai_service = None

def main():
    """Main application with split screen chat"""
    
    # Navigation
    render_navigation()
    
    # Main layout with conditional split
    if st.session_state.chat_panel_open:
        # Split screen layout
        render_split_screen_layout()
    else:
        # Full screen layout
        render_full_screen_layout()
    
    # Persistent chat bar
    render_chat_bar()

def render_full_screen_layout():
    """Full screen layout - normal view"""
    col_left, col_main, col_right = st.columns([1.2, 3, 1.5])
    
    with col_left:
        render_sidebar()
    
    with col_main:
        st.markdown('<div class="main-content-area">', unsafe_allow_html=True)
        render_tab_content()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        render_context_panel()

def render_split_screen_layout():
    """Split screen layout - chat open"""
    # When chat is open, hide context panel for space
    col_left, col_main, col_chat = st.columns([1.2, 2.5, 2.5])
    
    with col_left:
        render_sidebar()
    
    with col_main:
        st.markdown('<div class="main-content-area compressed">', unsafe_allow_html=True)
        render_tab_content_compressed()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_chat:
        render_chat_panel()

def render_tab_content():
    """Render current tab content - full size"""
    if st.session_state.active_tab == 'ipo_calendar':
        render_ipo_calendar()
    elif st.session_state.active_tab == 'companies':
        render_companies_view()
    elif st.session_state.active_tab == 'metrics':
        render_metrics_dashboard()
    elif st.session_state.active_tab == 'watchlist':
        show_watchlist()
    elif st.session_state.active_tab == 'chat':
        render_chat_view()
    elif st.session_state.active_tab == 'financial_analysis':
        show_financial_analysis()

def render_tab_content_compressed():
    """Render current tab content - compressed for split view"""
    # Add responsive wrapper
    st.markdown('<div class="compressed-view">', unsafe_allow_html=True)
    
    if st.session_state.active_tab == 'ipo_calendar':
        render_ipo_calendar_compressed()
    elif st.session_state.active_tab == 'companies':
        render_companies_view_compressed()
    elif st.session_state.active_tab == 'metrics':
        render_metrics_dashboard_compressed()
    elif st.session_state.active_tab == 'watchlist':
        show_watchlist()  # Already compact
    elif st.session_state.active_tab == 'chat':
        st.info("Chat is open in side panel")
    elif st.session_state.active_tab == 'financial_analysis':
        show_financial_analysis()  # Will need compressed version
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_chat_panel():
    """Render chat panel in split screen"""
    st.markdown('<div class="chat-panel-container">', unsafe_allow_html=True)
    
    # Header with close button
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("### 💬 Chat")
    with col2:
        if st.button("✕", key="close_chat", help="Close chat"):
            st.session_state.chat_panel_open = False
            st.rerun()
    
    st.markdown('<div class="chat-messages-container">', unsafe_allow_html=True)
    
    # Display messages
    for idx, msg in enumerate(st.session_state.chat_messages):
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.write(msg["content"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_navigation():
    """Render navigation with proper styling"""
    nav_items = ['IPO Calendar', 'Companies', 'Metrics', 'Watchlist', 'Financial Analysis', 'Chat']
    
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
    elif st.session_state.active_tab == 'chat':
        render_chat_view()
    elif st.session_state.active_tab == 'financial_analysis':
        show_financial_analysis()

def render_context_panel():
    """Render context panel with proper sections"""
    if st.session_state.selected_ticker:
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


def render_chat_view():
    """Render chat view - GPT/Claude style"""
    st.markdown("### Chat")
    
    # Chat messages area with proper scrolling
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    
    # Display all messages
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.write(msg["content"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input is automatically placed at bottom by CSS


def render_ipo_calendar_compressed():
    """IPO Calendar - compressed view for split screen"""
    st.markdown("# IPO Calendar")
    
    # Simplified table for split view
    ipos = [
        {"date": "06/15", "ticker": "TECH", "company": "TechCorp", "size": "$250M"},
        {"date": "06/14", "ticker": "BIO", "company": "BioMed", "size": "$180M"},
        {"date": "06/13", "ticker": "FINX", "company": "FinTech", "size": "$320M"}
    ]
    
    # Compact table
    for ipo in ipos:
        col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
        with col1:
            st.caption(ipo['date'])
        with col2:
            if st.button(ipo['ticker'], key=f"ipo_c_{ipo['ticker']}", use_container_width=True):
                st.session_state.selected_ticker = ipo['ticker']
                st.rerun()
        with col3:
            st.caption(ipo['company'])
        with col4:
            st.caption(ipo['size'])

def render_companies_view_compressed():
    """Companies - compressed view"""
    if st.session_state.selected_ticker:
        ticker = st.session_state.selected_ticker
        st.markdown(f"## {ticker}")
        
        # Key info only
        col1, col2 = st.columns(2)
        with col1:
            st.metric("DOCS", "12")
        with col2:
            st.metric("LOCKUP", "186d")
        
        # Recent docs list
        st.markdown("**Recent Filings**")
        docs = ["S-1 (Jun 01)", "S-1/A (May 15)", "424B4 (May 01)"]
        for doc in docs:
            st.caption(f"• {doc}")
    else:
        st.info("Select a company")

def render_metrics_dashboard_compressed():
    """Metrics - compressed view"""
    st.markdown("# Metrics")
    
    # Grid of metric pills
    metrics = [
        ("Active", "42"), ("This Week", "7"), ("Lockups", "12"),
        ("NYSE", "24"), ("NASDAQ", "18"), ("Tech", "15")
    ]
    
    cols = st.columns(3)
    for idx, (label, value) in enumerate(metrics):
        with cols[idx % 3]:
            st.button(f"**{value}**\n{label}", key=f"m_c_{idx}", use_container_width=True)

def render_chat_bar():
    """Persistent chat bar with split screen trigger"""
    # Create container for chat input
    chat_container = st.container()
    
    with chat_container:
        user_input = st.chat_input("Ask about IPOs, filings, or companies...")
        
        if user_input:
            # Open split screen if not already open
            if not st.session_state.chat_panel_open:
                st.session_state.chat_panel_open = True
            
            # Add user message
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            
            # Get AI response
            try:
                from services.ai_service import get_ai_response
                context = f"Selected: {st.session_state.selected_ticker}" if st.session_state.selected_ticker else "General"
                response = get_ai_response(user_input, context)
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.session_state.chat_messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
            
            st.rerun()
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

if __name__ == "__main__":
    main()
