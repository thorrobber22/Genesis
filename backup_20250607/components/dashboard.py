"""
Simplified Dashboard Component
Updated: 2025-06-07 21:50:17 UTC
"""
import streamlit as st
from pathlib import Path

def render_dashboard():
    """Render simplified analyst dashboard"""
    st.header("SEC Document Analysis")
    
    # Just show what matters
    doc_path = Path("data/sec_documents")
    if doc_path.exists():
        companies = list(doc_path.iterdir())
        st.info(f"{len(companies)} companies available for analysis")
    else:
        st.warning("No documents loaded yet")
