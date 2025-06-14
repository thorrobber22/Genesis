"""
Hedge Intelligence - Native Streamlit Components (FIXED)
Date: 2025-06-14 03:16:55 UTC
Author: thorrobber22
Note: Fixed nested columns error
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import json

# Page configuration
st.set_page_config(
    page_title="Hedge Intelligence",
    page_icon="HI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
/* Dark theme */
.stApp {
    background-color: #1E1E1E;
    color: #F7F7F8;
}

/* Sidebar styling */
.css-1d391kg {
    background-color: #202123;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Button styling */
.stButton > button {
    background-color: transparent;
    border: 1px solid #2E2E2E;
    color: #A3A3A3;
    transition: all 0.3s;
}

.stButton > button:hover {
    border-color: #2E8AF6;
    color: #F7F7F8;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
    background-color: #202123;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(46, 138, 246, 0.1) !important;
}

/* Input styling */
.stTextInput > div > div > input {
    background-color: #40414F;
    color: #ECECF1;
    border: 1px solid #565869;
}

/* Selectbox styling */
.stSelectbox > div > div {
    background-color: #40414F;
}

/* Success message styling */
.stSuccess {
    background-color: rgba(16, 185, 129, 0.1);
    border: 1px solid #10B981;
}

/* Info message styling */
.stInfo {
    background-color: rgba(46, 138, 246, 0.1);
    border: 1px solid #2E8AF6;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = 'AIRO'
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'selected_doc' not in st.session_state:
    st.session_state.selected_doc = None

# Header
st.markdown("# HEDGE INTELLIGENCE")

# Main navigation tabs
tab1, tab2, tab3, tab4 = st.tabs(["IPO Calendar", "Companies", "Watchlist", "My Reports"])

# IPO Calendar Tab
with tab1:
    st.header("IPO Calendar - Real-time filings and market activity")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        # Filters
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            period = st.selectbox("Period", ["This Week", "This Month", "All Time"])
        with filter_col2:
            status = st.selectbox("Status", ["All", "Filed", "Priced", "Trading"])
        with filter_col3:
            st.write("")  # Spacer
            st.caption("Last updated: 2 min ago")
    
    # IPO Data Table
    ipo_data = {
        'Date': ['Today', 'Yesterday', '06/10', '06/09', '06/08'],
        'Ticker': ['TECH', 'BIO', 'FINX', 'AIRO', 'CLOUD'],
        'Company': ['TechCorp International', 'BioMed Solutions', 'FinTech Innovations', 'AIRO Group Holdings', 'CloudBase Systems'],
        'Status': ['Filed', 'Priced', 'Trading', 'Filed', 'Filed'],
        'Documents': [8, 6, 10, 20, 12],
        'Lockup': ['-', '180d', '15d', '-', '-']
    }
    
    df = pd.DataFrame(ipo_data)
    st.dataframe(df, use_container_width=True, hide_index=True, height=300)

# Companies Tab
with tab2:
    # Create three-column layout
    col1, col2, col3 = st.columns([1.2, 2, 1.5])
    
    # File Explorer Column
    with col1:
        st.markdown("### File Explorer")
        
        # Search box
        search = st.text_input("Search", placeholder="Search companies...", label_visibility="collapsed")
        
        # Technology folder
        with st.expander("[F] **Technology** (5)", expanded=True):
            companies = [
                ("AIRO", "AIRO Group Holdings", 20),
                ("BSAAU", "BEST SPAC I Acquisition", 0),
                ("BACCU", "Blue Acquisition Corp", 0),
                ("HCHL", "Happy City Holdings", 0),
                ("JLHL", "Julong Holding Corp", 0)
            ]
            
            for ticker, name, docs in companies:
                button_label = f"[D] {name} ({ticker})"
                if docs > 0:
                    button_label += f" - {docs} docs"
                
                if st.button(button_label, key=f"company_{ticker}", use_container_width=True):
                    st.session_state.selected_company = ticker
            
            # Show documents for selected company
            if st.session_state.selected_company == 'AIRO':
                st.markdown("**Documents:**")
                docs_list = [
                    "S-1 Registration Statement",
                    "S-1/A Amendment 1",
                    "S-1/A Amendment 2",
                    "Correspondence",
                    "Underwriting Agreement"
                ]
                for doc in docs_list:
                    if st.button(f"  - {doc}", key=f"doc_{doc}", use_container_width=True):
                        st.session_state.selected_doc = doc
        
        # Other folders (collapsed)
        with st.expander("[F] **Healthcare** (8)"):
            st.write("BioMed Solutions (BIO)")
            st.write("GeneTech Plus (GENE)")
        
        with st.expander("[F] **Financial** (6)"):
            st.write("FinTech Innovations (FINX)")
            st.write("CryptoBank (CRYP)")
    
    # Document Viewer Column
    with col2:
        st.markdown("### Document Viewer")
        
        # Document controls - FIXED: No nested columns
        control_col1, control_col2, control_col3 = st.columns([3, 2, 2])
        with control_col1:
            if st.session_state.selected_company == 'AIRO':
                st.caption("S-1/A Amendment 1 - AIRO")
            else:
                st.caption("Select a document to view")
        with control_col2:
            st.caption(f"Page {st.session_state.current_page} of 456")
        with control_col3:
            # Page navigation buttons in same column
            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
            with btn_col1:
                if st.button("<", key="prev_page"):
                    if st.session_state.current_page > 1:
                        st.session_state.current_page -= 1
            with btn_col2:
                if st.button(">", key="next_page"):
                    st.session_state.current_page += 1
            with btn_col3:
                if st.button("SEC", key="sec_link"):
                    st.info("Opening SEC filing...")
        
        # Document content area
        if st.session_state.selected_company == 'AIRO' and st.session_state.selected_doc:
            # Simulate document content
            st.markdown("---")
            st.markdown("#### PRELIMINARY PROSPECTUS")
            st.markdown("**AIRO Group Holdings Inc.**")
            st.markdown("**$125,000,000**")
            st.markdown("**Common Stock**")
            st.markdown("---")
            
            if "Amendment" in st.session_state.selected_doc:
                st.markdown("""
                This amendment to our registration statement on Form S-1 is being filed to:
                
                • Update our financial statements for Q2 2025
                • Revise the "Use of Proceeds" section
                • Update risk factors related to market conditions
                • Modify the underwriting discount structure
                
                **Section 7.12 - Lock-Up Agreements**
                
                In connection with this offering, we and our executive officers, directors, 
                and holders of substantially all of our outstanding shares have agreed to a 
                180-day lock-up period...
                """)
            else:
                st.markdown("This is our initial public offering. We are selling shares...")
        else:
            st.info("Select a company and document from the file explorer")
    
    # Chat Panel Column
    with col3:
        st.markdown("### Document Assistant")
        
        if st.session_state.selected_company == 'AIRO':
            st.caption("AIRO S-1/A • 456 pages • Filed Jun 13")
            
            # Quick actions
            st.markdown("**Quick Actions:**")
            
            if st.button("• What are the lockup terms?", use_container_width=True):
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": "What are the lockup terms?"
                })
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": "**Lockup Period** [Page 147]\n\n• Standard: **180 days** from IPO\n• Coverage: **85%** of shares\n• Executive extension: **+90 days**\n• Early release if stock >40% above IPO price for 10 days"
                })
            
            if st.button("• Show me risk factors", use_container_width=True):
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": "Show me risk factors"
                })
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": "**Key Risk Factors** [Pages 52-67]\n\n1. Market competition\n2. Regulatory changes\n3. Key personnel dependency\n4. Technology risks\n5. Customer concentration"
                })
            
            if st.button("• Summarize financials", use_container_width=True):
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": "Summarize financials"
                })
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": "**Financial Highlights** [Page 201]\n\n• Revenue: **$450M** (+67% YoY)\n• Gross Margin: **72%**\n• Operating Loss: **($45M)**\n• Cash: **$125M**"
                })
            
            # Chat messages display
            st.markdown("---")
            st.markdown("**Chat History:**")
            
            # Message container with scrolling
            message_container = st.container()
            with message_container:
                for msg in st.session_state.chat_messages[-5:]:  # Show last 5 messages
                    if msg["role"] == "user":
                        st.markdown(f"**You:** {msg['content']}")
                    else:
                        with st.container():
                            st.markdown(f"**Assistant:** {msg['content']}")
                            if st.button("+ Add to Report", key=f"add_{len(st.session_state.chat_messages)}"):
                                st.success("Added to report!")
            
            # Chat input
            st.markdown("---")
            user_input = st.text_area("Ask about this document...", height=100, key="chat_input")
            if st.button("Send", key="send_chat", use_container_width=True):
                if user_input:
                    st.session_state.chat_messages.append({
                        "role": "user",
                        "content": user_input
                    })
                    # Mock response
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": "I'm analyzing the document for your query..."
                    })
                    st.rerun()
        else:
            st.info("Select a document to start analyzing")

# Watchlist Tab
with tab3:
    st.header("Your Watchlist")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        watchlist_data = {
            'Ticker': ['AIRO', 'TECH', 'BIO'],
            'Company': ['AIRO Group Holdings', 'TechCorp International', 'BioMed Solutions'],
            'Status': ['Filed', 'Filed', 'Priced'],
            'Added': ['Today', 'Yesterday', '2 days ago'],
            'Alerts': ['New amendment filed', 'Pricing expected', 'Lockup in 179 days']
        }
        df_watch = pd.DataFrame(watchlist_data)
        st.dataframe(df_watch, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### Add to Watchlist")
        ticker_input = st.text_input("Enter ticker symbol")
        if st.button("Add to Watchlist", use_container_width=True):
            st.success(f"Added {ticker_input} to watchlist!")

# My Reports Tab
with tab4:
    st.header("My Reports")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        # Report list
        if st.session_state.chat_messages:
            st.markdown("### Current Report: Tech IPO Analysis June 2025")
            st.markdown("**Sections:**")
            st.write("1. Executive Summary")
            st.write("2. AIRO Lockup Analysis")
            st.write("3. Risk Assessment")
            st.write("4. Financial Overview")
            
            if st.button("Export to Word", key="export_word"):
                st.success("Report exported!")
        else:
            st.info("No reports yet. Start by analyzing documents in the Companies tab!")
    
    with col2:
        if st.button("Create New Report", use_container_width=True):
            st.info("New report created!")

# Footer
st.markdown("---")
st.caption("Hedge Intelligence | Real-time SEC data | Powered by AI")
