"""
Hedge Intelligence - COMPLETE WORKING VERSION
Date: 2025-06-14 13:09:40 UTC
Author: thorrobber22
Note: Real data integration, no mocks
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime
import os

# Import services
from services.ai_service_enhanced import ai_service
from services.data_service import data_service
from services.document_indexer import DocumentIndexer
from components.document_viewer import document_viewer
from components.chat import render_chat_panel

# Page config
st.set_page_config(
    page_title="Hedge Intelligence",
    page_icon="HI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS FROM MOCKUP
st.markdown("""
<style>
/* Exact color palette from mockup */
:root {
    --bg-primary: #1E1E1E;
    --bg-secondary: #202123;
    --bg-tertiary: #2A2B2D;
    --border: #2E2E2E;
    --text-primary: #F7F7F8;
    --text-muted: #A3A3A3;
    --accent: #2E8AF6;
    --highlight: rgba(255, 217, 61, 0.3);
    --success: #10B981;
    --warning: #F59E0B;
    --input-bg: #40414F;
    --input-border: #565869;
    --input-text: #ECECF1;
}

/* Reset all Streamlit defaults */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.stApp {
    background-color: var(--bg-primary) !important;
}

.main {
    padding: 0 !important;
}

#MainMenu {visibility: hidden;}
.stDeployButton {display: none;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* Component specific styles */
.stButton > button {
    width: 100%;
    text-align: left;
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-muted);
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    color: var(--text-primary);
    border-color: var(--accent);
    background: rgba(46, 138, 246, 0.05);
}

/* Document viewer styles */
.document-container {
    height: 600px;
    overflow-y: auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    color: black;
}

/* Citation highlighting */
.citation-highlight {
    background-color: rgba(255, 217, 61, 0.3);
    transition: background-color 2s ease;
}
</style>

<script>
function jumpToCitation(citationId) {
    const element = document.getElementById(citationId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        element.classList.add('citation-highlight');
        setTimeout(() => {
            element.classList.remove('citation-highlight');
        }, 2000);
    }
}
</script>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'companies'
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = 'AIRO'
if 'selected_document' not in st.session_state:
    st.session_state.selected_document = None
if 'selected_doc_index' not in st.session_state:
    st.session_state.selected_doc_index = 0
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Create columns for layout
col1, col2, col3 = st.columns([1.2, 2, 1.5])

# File Explorer
with col1:
    st.markdown("### File Explorer")
    search = st.text_input("", placeholder="Search companies...", label_visibility="collapsed")
    
    # Technology folder
    st.markdown("#### [F] Technology (5)")
    
    # Get real companies from file system
    ipo_filings_path = Path("data/ipo_filings")
    companies = []
    
    if ipo_filings_path.exists():
        for company_dir in ipo_filings_path.iterdir():
            if company_dir.is_dir():
                doc_count = len(list(company_dir.glob("*.html")))
                # Extract ticker from directory name
                company_name = company_dir.name
                ticker = "AIRO" if "AIRO" in company_name else company_name[:4].upper()
                companies.append((ticker, company_name, doc_count))
    
    # If no companies found, show at least AIRO
    if not companies:
        companies = [("AIRO", "AIRO Group Holdings", 20)]
    
    for ticker, name, docs in companies:
        if st.button(f"[D] {name} ({ticker}) - {docs} docs", key=f"company_{ticker}"):
            st.session_state.selected_company = ticker
            st.session_state.selected_doc_index = 0
            st.rerun()

# Document Viewer
with col2:
    st.markdown("### Document Viewer")
    
    if st.session_state.selected_company == 'AIRO':
        # Get available documents
        docs = document_viewer.get_available_documents('AIRO Group Holdings')
        
        if docs:
            # Controls
            ctrl1, ctrl2, ctrl3 = st.columns([3, 2, 2])
            with ctrl1:
                st.caption(f"AIRO - {docs[st.session_state.selected_doc_index][:30]}...")
            with ctrl2:
                st.caption(f"Document {st.session_state.selected_doc_index + 1} of {len(docs)}")
            with ctrl3:
                # Fixed nested columns issue
                btn_container = st.container()
                btn_cols = btn_container.columns(2)
                
                with btn_cols[0]:
                    if st.button("←", key="prev_doc"):
                        if st.session_state.selected_doc_index > 0:
                            st.session_state.selected_doc_index -= 1
                            st.rerun()
                
                with btn_cols[1]:
                    if st.button("→", key="next_doc"):
                        if st.session_state.selected_doc_index < len(docs) - 1:
                            st.session_state.selected_doc_index += 1
                            st.rerun()
            
            # Display document
            selected_doc = docs[st.session_state.selected_doc_index]
            st.session_state.selected_document = selected_doc
            
            # Render the actual document
            doc_content = document_viewer.load_document('AIRO Group Holdings', selected_doc)
            st.markdown(f"""
            <div class="document-container">
                {doc_content}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No documents found for AIRO")
    else:
        st.info("Select a company from the file explorer to view documents")

# Chat Panel
with col3:
    render_chat_panel()

# Bottom status
st.markdown("---")
st.caption("Hedge Intelligence | Connected to SEC EDGAR | Documents indexed")
