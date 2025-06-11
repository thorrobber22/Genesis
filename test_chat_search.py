#!/usr/bin/env python3
"""
Test the enhanced chat with real document search
"""

import streamlit as st
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Set OpenAI API key if available
if 'OPENAI_API_KEY' in os.environ:
    import openai
    openai.api_key = os.environ['OPENAI_API_KEY']

from services.document_indexer import DocumentIndexer
from components.persistent_chat_enhanced import render_persistent_chat

def test_chat_with_search():
    st.set_page_config(page_title="Chat Search Test", layout="wide")
    
    st.title("🧪 Chat with Document Search Test")
    
    # Test status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("1️⃣ Index Documents", use_container_width=True):
            with st.spinner("Indexing all documents..."):
                indexer = DocumentIndexer()
                result = indexer.index_all_documents()
                st.success(f"✅ Indexed {result['indexed']} documents!")
                st.json(result)
    
    with col2:
        if st.button("2️⃣ Test Search", use_container_width=True):
            indexer = DocumentIndexer()
            
            test_queries = [
                "revenue",
                "risk factors",
                "financial statements",
                "cash flow"
            ]
            
            for query in test_queries:
                results = indexer.search(query, limit=3)
                st.write(f"**Query:** {query}")
                st.write(f"Found: {results['count']} results")
                
                if results['results']:
                    for r in results['results'][:2]:
                        st.caption(f"- {r['metadata']['company']} - {r['metadata']['section_title']}")
    
    with col3:
        # Get list of companies
        data_dir = Path("data/sec_documents")
        companies = []
        if data_dir.exists():
            companies = [d.name for d in data_dir.iterdir() if d.is_dir()]
        
        test_company = st.selectbox("Select Company", companies if companies else ["No companies"])
    
    st.divider()
    
    # Instructions
    with st.expander("📝 Test Instructions", expanded=True):
        st.markdown("""
        1. **First**, click "Index Documents" to build the search index (✅ Already done!)
        2. **Second**, click "Test Search" to verify search is working
        3. **Then**, try these test questions in the chat:
           - "What is Circle's revenue?"
           - "What are the main risk factors for CRCL?"
           - "What is Circle's business model?"
           - "Tell me about USDC"
        
        The chat should:
        - Find relevant document sections
        - Provide answers with citations
        - Show source documents
        """)
    
    # API Key check
    if 'OPENAI_API_KEY' not in os.environ and not st.session_state.get('api_key'):
        st.warning("⚠️ OpenAI API key not set. Add to your .env file or set OPENAI_API_KEY environment variable")
        api_key = st.text_input("Enter OpenAI API Key", type="password", key="api_key_input")
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            st.session_state['api_key'] = api_key
            st.success("✅ API key set for this session")
            st.rerun()
    
    # Show current index stats
    st.sidebar.markdown("### 📊 Index Stats")
    indexer = DocumentIndexer()
    collection_count = indexer.collection.count()
    st.sidebar.metric("Total Sections Indexed", collection_count)
    st.sidebar.caption("Each document is split into searchable sections")
    
    # Render the chat
    st.divider()
    render_persistent_chat(company=test_company if companies else None)

if __name__ == "__main__":
    test_chat_with_search()