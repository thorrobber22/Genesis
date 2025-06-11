"""
Hedge Intelligence - SEC Document Analysis Platform
Refactored: 2025-06-07 21:50:17 UTC
Author: thorrobber22
"""

import streamlit as st
from pathlib import Path
import json

# Import components
from components.document_explorer import DocumentExplorer
from components.persistent_chat import PersistentChat
from components.ipo_tracker_enhanced import IPOTrackerEnhanced
from components.data_extractor import DataExtractor
from services.document_service import DocumentService
from services.ai_service import AIService

def apply_cream_theme():
    """Apply Apple-style cream theme"""
    st.markdown("""
    <style>
    /* Hedge Intelligence - Premium Apple Theme */
    
    /* Remove Streamlit defaults */
    .stApp {
        background-color: #FAFAF8;
    }
    
    /* Main content area */
    .main {
        background-color: #FAFAF8;
        color: #1A1A1A;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1A1A1A !important;
        font-weight: 600;
    }
    
    /* Text */
    p, span, div {
        color: #1A1A1A;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #F5F5F3;
    }
    
    /* Buttons - Dark with blue hover */
    .stButton > button {
        background-color: #2D2D2D;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #007AFF;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 122, 255, 0.15);
    }
    
    /* Cards and containers */
    .css-1r6slb0, .css-12oz5g7 {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    /* Input fields */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        color: #1A1A1A;
        border-radius: 8px;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
        border-color: #007AFF;
        box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.1);
    }
    
    /* Links */
    a {
        color: #1A1A1A;
        text-decoration: none;
        transition: color 0.2s;
    }
    
    a:hover {
        color: #007AFF;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    
    /* Remove blue progress bars */
    .stProgress > div > div > div {
        background-color: #34C759;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        border-radius: 12px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #F5F5F3;
        color: #1A1A1A;
        border-radius: 8px;
    }
    
    /* Data editor/tables */
    .glideDataEditor {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }
    
    /* Remove all remaining blue */
    .css-1cpxqw2, .css-1v0mbdj > img {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
def render_document_viewer():
    """Render document viewer"""
    if 'selected_doc' not in st.session_state:
        return
        
    doc = st.session_state.selected_doc
    st.header(f"{doc['company']} - {doc['document']}")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("View PDF"):
            st.info("PDF export available in premium version")
    with col2:
        if st.button("Download"):
            st.info("Download ready")
    
    # Load and display document
    try:
        with open(doc['path'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract key data
        with st.expander("Quick Extractions"):
            extractor = DataExtractor()
            
            col1, col2 = st.columns(2)
            with col1:
                revenue = extractor.extract_with_citations(content, 'revenue')
                if revenue['status'] == 'found':
                    st.metric(
                        "Revenue", 
                        f"${revenue['value']} {revenue.get('unit', '')}",
                        help=f"Source: {revenue['citation']}"
                    )
                    
            with col2:
                employees = extractor.extract_with_citations(content, 'employees')
                if employees['status'] == 'found':
                    st.metric(
                        "Employees",
                        employees['value'],
                        help=f"Source: {employees['citation']}"
                    )
        
        # Show document content
        st.markdown("### Document Content")
        # Show first 5000 chars in a scrollable container
        st.markdown(
            f'<div style="height: 400px; overflow-y: scroll; padding: 1rem; '
            f'background-color: #1A1D23; border: 1px solid #2D3748; border-radius: 4px;">'
            f'{content[:5000]}...</div>',
            unsafe_allow_html=True
        )
        
    except Exception as e:
        st.error(f"Error loading document: {e}")

def render_analyst_dashboard():
    """Render simplified analyst dashboard"""
    st.header("SEC Document Analysis Platform")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    doc_path = Path("data/sec_documents")
    if doc_path.exists():
        companies = len(list(doc_path.iterdir()))
        total_docs = sum(
            len(list(Path(f"data/sec_documents/{c}").glob("*.html")))
            for c in doc_path.iterdir() if c.is_dir()
        )
    else:
        companies = 0
        total_docs = 0
    
    with col1:
        st.metric("Companies Available", companies)
    with col2:
        st.metric("Total Documents", f"{total_docs:,}")
    with col3:
        if st.button("Request New Company"):
            st.session_state.show_company_request = True
            
    # IPO Tracker
    st.markdown("---")
    ipo_tracker = IPOTrackerEnhanced()
    ipo_tracker.render_ipo_dashboard()
    
    # Company Request Form
    if st.session_state.get('show_company_request', False):
        with st.form("company_request"):
            st.subheader("Request New Company")
            company = st.text_input("Company Name")
            ticker = st.text_input("Ticker Symbol")
            priority = st.radio("Priority", ["High", "Medium", "Low"])
            reason = st.text_area("Reason for Request")
            
            if st.form_submit_button("Submit Request"):
                # Save request
                request = {
                    'company': company,
                    'ticker': ticker,
                    'priority': priority,
                    'reason': reason,
                    'status': 'pending',
                    'timestamp': pd.Timestamp.now().isoformat()
                }
                
                requests_file = Path("data/company_requests.json")
                if requests_file.exists():
                    with open(requests_file, 'r') as f:
                        requests = json.load(f)
                else:
                    requests = []
                    
                requests.append(request)
                
                with open(requests_file, 'w') as f:
                    json.dump(requests, f, indent=2)
                    
                st.success("Request submitted! Will be processed within 30 minutes.")
                st.session_state.show_company_request = False
                st.rerun()

def display_chat_history():
    """Display chat history in main area"""
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        st.markdown("### Recent Analysis")
        for item in st.session_state.chat_history[-3:]:
            with st.container():
                st.markdown(f"**Q:** {item['query']}")
                st.markdown(f"**A:** {item['response']}")
                if item.get('document'):
                    st.caption(f"Context: {item['document']['company']} - {item['document']['document']}")
                st.markdown("---")

def main():
    st.set_page_config(
        page_title="Hedge Intelligence - SEC Analysis",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply theme
    apply_cream_theme()
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize components
    doc_explorer = DocumentExplorer()
    persistent_chat = PersistentChat()
    
    # Sidebar - Document Explorer
    with st.sidebar:
        st.title("Hedge Intelligence")
        st.caption("SEC Document Analysis Platform")
        st.markdown("---")
        doc_explorer.render_sidebar()
    
    # Main area
    if 'selected_doc' in st.session_state:
        render_document_viewer()
    else:
        render_analyst_dashboard()
    
    # Show chat history
    display_chat_history()
    
    # Bottom - Persistent chat
    persistent_chat.render_chat_bar()

if __name__ == "__main__":
    main()
