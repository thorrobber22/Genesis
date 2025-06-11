#!/usr/bin/env python3
"""
Document Explorer with integrated viewer
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime
from components.document_viewer import DocumentViewer

def render_document_explorer():
    """Render the document explorer with clickable documents"""
    
    st.title("📁 Document Explorer")
    
    # Initialize viewer
    viewer = DocumentViewer()
    data_dir = Path("data/sec_documents")
    
    if not data_dir.exists():
        st.error("No documents found. Please download some companies first.")
        return
    
    # Layout: Explorer on left, viewer on right
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Companies")
        
        # Get all companies
        companies = sorted([d for d in data_dir.iterdir() if d.is_dir()], 
                          key=lambda x: x.name)
        
        if not companies:
            st.info("No companies downloaded yet")
            return
        
        # Company selector
        selected_company = st.selectbox(
            "Select Company",
            companies,
            format_func=lambda x: f"{x.name} ({len(list(x.glob('*.html')))} docs)"
        )
        
        if selected_company:
            # Show company info if available
            company_info_path = selected_company / "company_info.json"
            if company_info_path.exists():
                with open(company_info_path, 'r') as f:
                    info = json.load(f)
                st.caption(f"**{info.get('name', 'Unknown')}**")
                st.caption(f"CIK: {info.get('cik', 'N/A')}")
            
            st.divider()
            
            # List documents
            st.markdown("### Documents")
            
            # Group documents by type
            docs_by_type = {}
            for doc in selected_company.glob("*.html"):
                # Get metadata
                meta_path = doc.with_suffix('.json')
                if meta_path.exists():
                    with open(meta_path, 'r') as f:
                        metadata = json.load(f)
                    form_type = metadata.get('form_type', 'Other')
                else:
                    # Extract from filename
                    form_type = doc.name.split('_')[0] if '_' in doc.name else 'Other'
                
                if form_type not in docs_by_type:
                    docs_by_type[form_type] = []
                docs_by_type[form_type].append(doc)
            
            # Display documents by type
            for form_type, docs in sorted(docs_by_type.items()):
                with st.expander(f"{form_type} ({len(docs)} documents)", expanded=True):
                    for doc in sorted(docs, key=lambda x: x.name, reverse=True):
                        # Get metadata
                        meta_path = doc.with_suffix('.json')
                        metadata = {}
                        if meta_path.exists():
                            with open(meta_path, 'r') as f:
                                metadata = json.load(f)
                        
                        # Create clickable document entry
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            # Make the document name clickable
                            if st.button(
                                f"📄 {doc.name[:50]}...",
                                key=f"doc_{doc.name}",
                                help=f"Filed: {metadata.get('filing_date', 'Unknown')}",
                                use_container_width=True
                            ):
                                st.session_state['selected_document'] = str(doc)
                        
                        with col_b:
                            st.caption(f"{doc.stat().st_size // 1024} KB")
    
    with col2:
        # Document viewer area
        if 'selected_document' in st.session_state:
            viewer.display_document(Path(st.session_state['selected_document']))
        else:
            st.info("👈 Select a document from the explorer to view it")
            
            # Show some stats
            st.markdown("### 📊 Quick Stats")
            
            total_companies = len(companies)
            total_docs = sum(len(list(c.glob("*.html"))) for c in companies)
            
            col_1, col_2 = st.columns(2)
            with col_1:
                st.metric("Total Companies", total_companies)
            with col_2:
                st.metric("Total Documents", total_docs)
            
            # Recent documents
            st.markdown("### 📅 Recent Documents")
            all_docs = []
            for company in companies:
                for doc in company.glob("*.html"):
                    meta_path = doc.with_suffix('.json')
                    if meta_path.exists():
                        with open(meta_path, 'r') as f:
                            metadata = json.load(f)
                        all_docs.append({
                            'company': company.name,
                            'doc': doc,
                            'date': metadata.get('download_date', ''),
                            'form_type': metadata.get('form_type', 'Unknown')
                        })
            
            # Sort by download date
            all_docs.sort(key=lambda x: x['date'], reverse=True)
            
            # Show top 5
            for item in all_docs[:5]:
                if st.button(
                    f"{item['company']} - {item['form_type']}",
                    key=f"recent_{item['doc'].name}",
                    use_container_width=True
                ):
                    st.session_state['selected_document'] = str(item['doc'])
                    st.rerun()

# For integration with main app
if __name__ == "__main__":
    st.set_page_config(page_title="Document Explorer", layout="wide")
    render_document_explorer()