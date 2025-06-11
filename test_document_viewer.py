#!/usr/bin/env python3
"""
Test the Document Viewer component
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from components.document_viewer import DocumentViewer

def test_document_viewer():
    st.set_page_config(page_title="Document Viewer Test", layout="wide")
    
    st.title("🧪 Document Viewer Test")
    
    viewer = DocumentViewer()
    
    # Check if we have any documents
    data_dir = Path("data/sec_documents")
    
    if not data_dir.exists():
        st.error("❌ No data directory found!")
        st.info("Please run the SEC scraper first to download some documents")
        return
    
    # Find a test document
    test_doc = None
    for company_dir in data_dir.iterdir():
        if company_dir.is_dir():
            docs = list(company_dir.glob("*.html"))
            if docs:
                test_doc = docs[0]
                break
    
    if not test_doc:
        st.error("❌ No documents found to test!")
        st.info("Please download at least one company's documents")
        return
    
    st.success(f"✅ Found test document: {test_doc.name}")
    st.info(f"Company: {test_doc.parent.name}")
    
    # Test 1: Basic display
    with st.expander("Test 1: Basic Document Display", expanded=True):
        try:
            viewer.display_document(test_doc)
            st.success("✅ Document displayed successfully!")
        except Exception as e:
            st.error(f"❌ Error displaying document: {e}")
    
    # Test 2: Document summary
    with st.expander("Test 2: Document Summary"):
        try:
            summary = viewer.get_document_summary(test_doc)
            st.json(summary)
            st.success("✅ Summary generated successfully!")
        except Exception as e:
            st.error(f"❌ Error generating summary: {e}")
    
    # Test 3: Search functionality
    with st.expander("Test 3: Search Test"):
        search_term = st.text_input("Enter search term", value="financial")
        if search_term:
            try:
                with open(test_doc, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                highlighted = viewer._highlight_search_terms(content, search_term)
                if '<span class="highlight">' in highlighted:
                    st.success(f"✅ Found and highlighted '{search_term}'")
                else:
                    st.warning(f"⚠️ Term '{search_term}' not found")
            except Exception as e:
                st.error(f"❌ Error in search: {e}")

if __name__ == "__main__":
    test_document_viewer()