#!/usr/bin/env python3
"""
Create document viewer component
Date: 2025-06-06 11:42:32 UTC
Author: thorrobber22
"""

viewer_code = '''"""
Document viewer component for Hedge Intel
Date: 2025-06-06 11:42:32 UTC
Author: thorrobber22
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

def show_document_viewer(doc_path: Path):
    """Display document content in a clean viewer"""
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)
        
        # Header
        st.markdown(f"### {doc_data.get('ticker', 'Unknown')} - {doc_data.get('document_type', 'Unknown')}")
        
        # Metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("Filed Date")
            st.text(doc_data.get('filing_date', 'N/A'))
        with col2:
            st.caption("Pages")
            st.text(str(doc_data.get('page_count', 0)))
        with col3:
            st.caption("Processed")
            st.text(doc_data.get('metadata', {}).get('processed_at', 'N/A')[:10])
        
        st.divider()
        
        # Key data points
        if doc_data.get('document_type') == 'S-1':
            show_s1_data(doc_data)
        elif doc_data.get('document_type') == '424B4':
            show_424b4_data(doc_data)
        
        # Sections
        st.subheader("Document Sections")
        sections = doc_data.get('sections', {})
        
        for section_name, content in sections.items():
            with st.expander(section_name.replace('_', ' ').title()):
                if isinstance(content, str):
                    st.text_area("", content[:1000] + "..." if len(content) > 1000 else content, height=200)
                else:
                    st.json(content)
        
        # Download button
        st.download_button(
            label="Download JSON",
            data=json.dumps(doc_data, indent=2),
            file_name=f"{doc_data.get('ticker')}_{doc_data.get('document_type')}.json",
            mime="application/json"
        )
        
    except Exception as e:
        st.error(f"Error loading document: {e}")

def show_s1_data(doc_data):
    """Display S-1 specific data"""
    st.subheader("Company Information")
    
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Company Name")
        st.text(doc_data.get('company_name', 'N/A'))
        
        st.caption("Industry")
        st.text(doc_data.get('industry', 'N/A'))
        
        st.caption("Exchange")
        st.text(doc_data.get('exchange', 'N/A'))
    
    with col2:
        st.caption("Ticker")
        st.text(doc_data.get('ticker', 'N/A'))
        
        st.caption("Price Range")
        st.text(doc_data.get('price_range', 'N/A'))
        
        st.caption("Shares Offered")
        st.text(doc_data.get('shares_offered', 'N/A'))
    
    # Financial highlights
    if 'financial_highlights' in doc_data:
        st.subheader("Financial Highlights")
        fin_data = doc_data['financial_highlights']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Revenue", fin_data.get('revenue', 'N/A'))
        with col2:
            st.metric("Net Income", fin_data.get('net_income', 'N/A'))
        with col3:
            st.metric("Growth Rate", fin_data.get('growth_rate', 'N/A'))

def show_424b4_data(doc_data):
    """Display 424B4 specific data"""
    st.subheader("Final Pricing Information")
    
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Final Price")
        st.text(doc_data.get('final_price', 'N/A'))
        
        st.caption("Total Shares")
        st.text(doc_data.get('total_shares', 'N/A'))
    
    with col2:
        st.caption("Lock-up Period")
        st.text(doc_data.get('lockup_period', 'N/A'))
        
        st.caption("Lock-up Expiration")
        st.text(doc_data.get('lockup_expiration', 'N/A'))
'''

with open('document_viewer.py', 'w', encoding='utf-8') as f:
    f.write(viewer_code)

print("Created document_viewer.py")