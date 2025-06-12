"""
components/company_analysis.py - Professional company analysis view
"""

import streamlit as st
from pathlib import Path
import pandas as pd

def render_company_analysis():
    """Render company analysis page"""
    
    if st.session_state.selected_company:
        st.markdown(f"# {st.session_state.selected_company} Analysis")
        
        # Company metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Market Cap", "$45.2B")
        with col2:
            st.metric("P/E Ratio", "18.5")
        with col3:
            st.metric("52W Range", "$120-180")
        with col4:
            st.metric("Avg Volume", "2.3M")
            
        # Document list
        st.markdown("### Recent Filings")
        
        # Check for actual documents
        company_dir = Path(f'data/sec_documents/{st.session_state.selected_company}')
        if company_dir.exists():
            docs = list(company_dir.glob('*.html'))
            if docs:
                for doc in docs[:5]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📄 {doc.stem}")
                    with col2:
                        if st.button("View", key=f"view_{doc.stem}"):
                            st.session_state.ai_context = {"document": doc.stem}
        else:
            st.info("No documents found for this company")
    else:
        # Company selector
        st.markdown("# Company Analysis")
        
        companies = []
        if Path('data/sec_documents').exists():
            companies = [d.name for d in Path('data/sec_documents').iterdir() if d.is_dir()]
            
        if companies:
            selected = st.selectbox("Select a company:", companies)
            if st.button("Analyze"):
                st.session_state.selected_company = selected
                st.rerun()
        else:
            st.info("No companies found. Run the scrapers to populate data.")
