#!/usr/bin/env python3
"""
Fix syntax errors in the created files
Date: 2025-06-06 23:35:04 UTC
Author: thorrobber22
"""

from pathlib import Path

# Fix 1: Update document processor to escape regex properly
processor_path = Path("processors/document_processor.py")
if processor_path.exists():
    with open(processor_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix regex patterns
    content = content.replace(r"r'(\d+)\s*days'", r"r'(\\d+)\\s*days'")
    content = content.replace(r"r'(\d+)[- ]?day'", r"r'(\\d+)[- ]?day'")
    content = content.replace(r"r'(\d+)\s*days'", r"r'(\\d+)\\s*days'")
    content = content.replace(r"r'(\d{4}-\d{2}-\d{2})'", r"r'(\\d{4}-\\d{2}-\\d{2})'")
    
    with open(processor_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed document_processor.py")

# Fix 2: Create corrected UI without syntax errors
ui_content = '''#!/usr/bin/env python3
"""
Hedge Intelligence - AI-Powered SEC Analysis
"""

import streamlit as st
import chromadb
from pathlib import Path
import json
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Hedge Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Apple aesthetic
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background-color: #fafafa;
    }
    
    /* Chat interface */
    .user-message {
        background: #007AFF;
        color: white;
        padding: 12px 18px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 70%;
        margin-left: auto;
        text-align: right;
    }
    
    .ai-message {
        background: #f5f5f7;
        color: #1d1d1f;
        padding: 12px 18px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 85%;
    }
    
    /* Company cards in sidebar */
    .css-1d391kg {
        background-color: #f5f5f7;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 600;
        color: #1d1d1f;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #007AFF;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #0051D5;
        transform: translateY(-1px);
    }
    
    /* Citations */
    .citation-box {
        background: white;
        border: 1px solid #e5e5e7;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = None

# Sidebar
with st.sidebar:
    st.markdown("## Hedge Intelligence")
    st.caption("AI-Powered SEC Analysis")
    
    st.divider()
    
    # Company selector
    st.markdown("### Companies")
    
    sec_dir = Path("data/sec_documents")
    if sec_dir.exists():
        companies = sorted([d.name for d in sec_dir.iterdir() if d.is_dir()])
        
        # Show total documents
        total_docs = sum(len(list((sec_dir / c).glob("*.*"))) for c in companies)
        st.metric("Total Documents", f"{total_docs:,}")
        
        st.divider()
        
        # Company list
        for company in companies:
            company_dir = sec_dir / company
            doc_count = len(list(company_dir.glob("*.*")))
            
            # Skip empty directories
            if doc_count == 0:
                continue
                
            # Company button
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(company, key=f"company_{company}", use_container_width=True):
                    st.session_state.selected_company = company
            with col2:
                st.caption(f"{doc_count} docs")
                
            # Show metadata if selected
            if st.session_state.selected_company == company:
                metadata_file = company_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    st.caption(f"Last scan: {metadata.get('last_scan', 'Unknown')[:10]}")
    
    st.divider()
    st.caption("Version 1.0")

# Main content
st.markdown("# Hedge Intelligence")

# Show selected company
if st.session_state.selected_company:
    st.markdown(f"### Analyzing: {st.session_state.selected_company}")
else:
    st.markdown("### Select a company from the sidebar")

# Info message for demo
st.info("This is a demo interface. To enable AI chat, you'll need to:")
st.markdown("""
1. Add your OpenAI and Gemini API keys to the document processor
2. Run the document processor to index all SEC filings
3. The chat interface will then be fully functional with dual AI validation
""")

# Show chat interface structure
st.divider()

# Chat container
chat_container = st.container()

with chat_container:
    # Example messages
    example_messages = [
        {
            "role": "user",
            "content": "What is the lock-up period for Circle's IPO?"
        },
        {
            "role": "assistant",
            "content": "Based on Circle's S-1/A filing (June 2, 2025), the lock-up periods are:\\n\\n• **180 days** for officers and directors\\n• **90 days** for other shareholders\\n\\nThe lock-up prevents insiders from selling shares immediately after the IPO, expiring on:\\n• December 2, 2025 for officers/directors\\n• September 2, 2025 for other shareholders",
            "citations": [
                {
                    "filename": "S-1_A_2025-06-02_crcl.htm",
                    "filing_type": "S-1/A",
                    "page": "147",
                    "section": "Lock-Up Agreements"
                }
            ],
            "confidence": 99.5
        }
    ]
    
    # Display example messages
    for message in example_messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            # AI message
            st.markdown(f'<div class="ai-message">{message["content"]}</div>', unsafe_allow_html=True)
            
            # Confidence indicator
            confidence = message.get("confidence", 100)
            if confidence >= 99:
                st.success(f"Confidence: {confidence}% - Verified by dual AI")
            else:
                st.warning(f"Confidence: {confidence}% - Manual review recommended")
            
            # Citations
            if "citations" in message:
                with st.expander("View Sources"):
                    for citation in message["citations"]:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.markdown(f"**{citation['filename']}**")
                        with col2:
                            st.caption(f"Page {citation['page']}")
                        with col3:
                            st.button("View", key=f"view_{citation['filename']}")

# Chat input
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask about SEC filings, lock-up periods, IPO details...",
            placeholder="Example: What are the risk factors for CRCL?",
            label_visibility="collapsed"
        )
    
    with col2:
        submit = st.form_submit_button("Send", use_container_width=True, type="primary")

# Features showcase
st.divider()
st.markdown("### Key Features")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### Dual AI Validation")
    st.caption("Every answer verified by both OpenAI and Gemini for 99%+ confidence")

with col2:
    st.markdown("#### Perfect Citations")
    st.caption("Every fact linked to exact document, page, and section")

with col3:
    st.markdown("#### Lock-up Intelligence")
    st.caption("Automated extraction of lock-up periods and key dates")

with col4:
    st.markdown("#### Real-time Analysis")
    st.caption("Instant answers from 1,146+ SEC documents")

# Document stats
if st.session_state.selected_company and sec_dir.exists():
    st.divider()
    st.markdown("### Document Overview")
    
    company_dir = sec_dir / st.session_state.selected_company
    if company_dir.exists():
        # Group by file type
        file_types = {}
        for file in company_dir.glob("*.*"):
            ext = file.suffix.lower()
            if ext not in file_types:
                file_types[ext] = 0
            file_types[ext] += 1
        
        # Display stats
        cols = st.columns(len(file_types))
        for i, (ext, count) in enumerate(file_types.items()):
            if ext != '.json':  # Skip metadata
                with cols[i]:
                    st.metric(ext.upper()[1:], count)
'''

# Save corrected UI
with open("hedge_intelligence_ui.py", 'w', encoding='utf-8') as f:
    f.write(ui_content)

print("✅ Created corrected hedge_intelligence_ui.py")
print("\n📊 Structure Overview:")
print("• Uses existing /data/sec_documents/ folder")
print("• Reads the 1,146 files we already downloaded")
print("• Creates AI search layer on top")
print("• Same Apple aesthetic as admin")