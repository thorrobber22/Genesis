#!/usr/bin/env python3
"""
Test AI Service with Document Context
"""

import streamlit as st
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from services.ai_service import AIService
from components.ai_chat_dual import render_enhanced_ai_chat

st.set_page_config(page_title="Document Context Test", layout="wide")
st.title("🧪 AI Document Context Test")

# Test tabs
tab1, tab2, tab3 = st.tabs(["AI Service Test", "Enhanced Chat Test", "Document Preview"])

with tab1:
    st.header("Test AI Service Document Context")
    
    # Initialize AI Service
    ai_service = AIService()
    
    # Select a test document
    companies = ["AAPL", "TSLA", "CRCL", "RDDT"]
    selected_company = st.selectbox("Select Company", companies)
    
    # Find documents
    doc_path = Path(f"data/sec_documents/{selected_company}")
    if doc_path.exists():
        docs = list(doc_path.glob("*.html"))
        if docs:
            selected_doc = st.selectbox("Select Document", [d.name for d in docs])
            
            if st.button("Load Document Context"):
                # Load document
                full_path = doc_path / selected_doc
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Set context
                ai_service.set_document_context(selected_company, selected_doc, content[:5000])
                st.success(f"✅ Loaded context: {selected_company} - {selected_doc}")
                
                # Show current context
                st.json(ai_service.current_context)
            
            # Test query
            query = st.text_input("Ask about this document:", "What are the key financial metrics?")
            
            if st.button("Get AI Response"):
                with st.spinner("Analyzing..."):
                    response = ai_service.get_contextual_response(query)
                
                if response['success']:
                    st.success(f"Confidence: {response['confidence']}")
                    st.markdown(response['response'])
                    
                    if response['sources']:
                        st.subheader("Sources")
                        for source in response['sources']:
                            st.write(f"- {source['type']}: {source['reference']}")
                else:
                    st.error(response['response'])
        else:
            st.warning(f"No documents found for {selected_company}")
    else:
        st.error(f"Company directory not found: {selected_company}")

with tab2:
    st.header("Test Enhanced Chat")
    # Set company context
    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = "AAPL"
    
    # Render the enhanced chat
    render_enhanced_ai_chat()

with tab3:
    st.header("Document Preview")
    
    # Quick document viewer
    company = st.selectbox("Company", ["AAPL", "TSLA", "CRCL", "RDDT"], key="preview_company")
    doc_dir = Path(f"data/sec_documents/{company}")
    
    if doc_dir.exists():
        docs = list(doc_dir.glob("*.html"))
        if docs:
            doc = st.selectbox("Document", [d.name for d in docs])
            
            if st.button("Preview"):
                with open(doc_dir / doc, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Show first 2000 chars
                st.text_area("Content Preview", content[:2000], height=400)
                st.info(f"Document size: {len(content):,} characters")
    else:
        st.warning(f"No documents for {company}")

# Quick status check
st.sidebar.header("🔍 Status Check")

# Check AI Service
ai_service = AIService()
if ai_service.openai_client:
    st.sidebar.success("✅ OpenAI Connected")
else:
    st.sidebar.error("❌ OpenAI Not Connected")

# Check documents
doc_count = sum(len(list(Path(f"data/sec_documents/{c}").glob("*.html"))) 
                for c in ["AAPL", "TSLA", "CRCL", "RDDT"] 
                if Path(f"data/sec_documents/{c}").exists())
st.sidebar.metric("Total Documents", doc_count)

# Check index
index_path = Path("data/indexed_documents/document_index.json")
if index_path.exists():
    import json
    with open(index_path, 'r') as f:
        index_data = json.load(f)
    st.sidebar.metric("Indexed Sections", len(index_data.get('sections', [])))
else:
    st.sidebar.warning("No index found")