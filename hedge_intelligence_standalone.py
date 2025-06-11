#!/usr/bin/env python3
"""
Hedge Intelligence - Standalone Version (No Backend Dependencies)
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Hedge Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS remains the same
st.markdown("""
<style>
    .css-1d391kg { background-color: #f8f9fa; }
    .sidebar-menu-item {
        padding: 12px 20px;
        margin: 5px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .sidebar-menu-item:hover { background-color: #e9ecef; }
    .sidebar-menu-item.active { background-color: #007AFF; color: white; }
    .chat-message {
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        background-color: #f1f3f5;
    }
    .user-message {
        background-color: #007AFF;
        color: white;
        margin-left: 20%;
    }
    .company-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px;
        transition: all 0.3s;
    }
    .company-card:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

class HedgeIntelligence:
    def __init__(self):
        self.init_session_state()
    
    def init_session_state(self):
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'IPO Dashboard'
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'watchlist' not in st.session_state:
            st.session_state.watchlist = []
        if 'notifications_enabled' not in st.session_state:
            st.session_state.notifications_enabled = True
    
    def render_sidebar(self):
        with st.sidebar:
            st.markdown("# HEDGE INTELLIGENCE")
            st.markdown("---")
            
            menu_items = [
                ("📊", "IPO Dashboard"),
                ("💬", "New Chat"),
                ("📈", "Available Tickers"),
                ("⭐", "Watch List"),
                ("⚙️", "Settings"),
                ("🚪", "Log Out")
            ]
            
            for icon, label in menu_items:
                if st.button(f"{icon} {label}", key=label, use_container_width=True):
                    if label == "Log Out":
                        st.session_state.clear()
                        st.rerun()
                    else:
                        st.session_state.current_page = label
                        st.rerun()
            
            st.markdown("---")
            st.markdown(f"**User:** thorrobber22")
            st.markdown(f"**Time:** {datetime.now().strftime('%H:%M UTC')}")
    
    def render_ipo_dashboard(self):
        st.title("IPO Dashboard")
        
        # Check for actual companies in data folder
        sec_docs_path = Path("data/sec_documents")
        if sec_docs_path.exists():
            companies = [d.name for d in sec_docs_path.iterdir() if d.is_dir()]
            
            if companies:
                st.subheader("Available Companies")
                
                cols = st.columns(3)
                for idx, company in enumerate(companies[:9]):
                    with cols[idx % 3]:
                        self.render_company_card(company)
            else:
                st.info("No companies found. Run the admin panel to download SEC data.")
        else:
            st.warning("SEC documents folder not found. Please run the scraper first.")
    
    def render_company_card(self, company: str):
        company_path = Path(f"data/sec_documents/{company}")
        doc_count = len(list(company_path.glob("*"))) if company_path.exists() else 0
        
        st.markdown(f"""
        <div class="company-card">
            <h3>{company}</h3>
            <p>{doc_count} documents</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💬", key=f"chat_{company}", help="Chat"):
                st.session_state.current_page = "New Chat"
                st.session_state.chat_context = company
                st.rerun()
        with col2:
            if st.button("📄", key=f"docs_{company}", help="View Docs"):
                st.info(f"Document viewer for {company} coming soon")
        with col3:
            if st.button("⭐", key=f"watch_{company}", help="Add to Watchlist"):
                if company not in st.session_state.watchlist:
                    st.session_state.watchlist.append(company)
                    st.success("Added!")
    
    def render_chat(self):
        st.title("SEC Intelligence Chat")
        
        # Show context if available
        if hasattr(st.session_state, 'chat_context'):
            st.info(f"Chatting about: {st.session_state.chat_context}")
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message">
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
                
                if 'actions' in message and message['actions']:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("View", key=f"view_{len(st.session_state.chat_history)}"):
                            st.info("Document viewer coming soon")
                    with col2:
                        if st.button("Download", key=f"dl_{len(st.session_state.chat_history)}"):
                            st.info("Download feature coming soon")
                    with col3:
                        if st.button("Create Report", key=f"report_{len(st.session_state.chat_history)}"):
                            st.info("Report generator coming soon")
        
        # Chat input
        user_input = st.chat_input("Ask about any SEC filing...")
        
        if user_input:
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Mock AI response
            response = self.get_mock_response(user_input)
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response,
                'actions': True
            })
            
            st.rerun()
    
    def get_mock_response(self, query: str) -> str:
        if "lock-up" in query.lower():
            return "Based on the S-1/A filing, the lock-up periods are:\n• Officers: 180 days\n• Others: 90 days"
        elif "risk" in query.lower():
            return "Key risks include:\n1. Regulatory uncertainty\n2. Market competition\n3. Technology risks"
        else:
            return "I'll help you analyze SEC filings. Try asking about lock-up periods, risks, or financials."
    
    def render_available_tickers(self):
        st.title("Available Tickers")
        
        search = st.text_input("Search tickers...", placeholder="Enter company name")
        
        sec_docs_path = Path("data/sec_documents")
        if sec_docs_path.exists():
            companies = sorted([d.name for d in sec_docs_path.iterdir() if d.is_dir()])
            
            if search:
                companies = [c for c in companies if search.upper() in c.upper()]
            
            cols = st.columns(4)
            for idx, company in enumerate(companies):
                with cols[idx % 4]:
                    st.markdown(f"### {company}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.button("💬", key=f"t_chat_{company}")
                    with col2:
                        st.button("📄", key=f"t_docs_{company}")
                    with col3:
                        if st.button("⭐", key=f"t_watch_{company}"):
                            if company not in st.session_state.watchlist:
                                st.session_state.watchlist.append(company)
        
        st.markdown("---")
        st.subheader("Request New Ticker")
        col1, col2 = st.columns([3, 1])
        with col1:
            ticker = st.text_input("Enter ticker", placeholder="e.g., AAPL")
        with col2:
            if st.button("Request Data"):
                if ticker:
                    st.info(f"Request submitted for {ticker}")
    
    def render_watchlist(self):
        st.title("Watch List")
        
        if not st.session_state.watchlist:
            st.info("No companies in watchlist. Add from IPO Dashboard.")
        else:
            for company in st.session_state.watchlist:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.markdown(f"### {company}")
                with col2:
                    st.metric("Lock-up", "45 days")
                with col3:
                    st.metric("Docs", "127")
                with col4:
                    if st.button("Remove", key=f"rm_{company}"):
                        st.session_state.watchlist.remove(company)
                        st.rerun()
                st.markdown("---")
    
    def render_settings(self):
        st.title("Settings")
        
        notifications = st.checkbox(
            "Receive notifications",
            value=st.session_state.notifications_enabled
        )
        
        if notifications != st.session_state.notifications_enabled:
            st.session_state.notifications_enabled = notifications
            st.success("Settings saved!")
    
    def run(self):
        self.render_sidebar()
        
        if st.session_state.current_page == "IPO Dashboard":
            self.render_ipo_dashboard()
        elif st.session_state.current_page == "New Chat":
            self.render_chat()
        elif st.session_state.current_page == "Available Tickers":
            self.render_available_tickers()
        elif st.session_state.current_page == "Watch List":
            self.render_watchlist()
        elif st.session_state.current_page == "Settings":
            self.render_settings()

if __name__ == "__main__":
    app = HedgeIntelligence()
    app.run()