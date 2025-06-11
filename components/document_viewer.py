#!/usr/bin/env python3
"""
Enhanced Document Viewer - Actually displays SEC documents
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime
from bs4 import BeautifulSoup
import re

class DocumentViewer:
    def __init__(self):
        self.data_dir = Path("data/sec_documents")
        
    def display_document(self, file_path: Path):
        """Display a document with proper formatting"""
        
        if not file_path.exists():
            st.error(f"Document not found: {file_path}")
            return
            
        # Load metadata
        metadata_path = file_path.with_suffix('.json')
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        
        # Display header
        st.markdown("### 📄 Document Viewer")
        
        # Document info bar
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{metadata.get('form_type', 'Unknown')}** - {metadata.get('company_name', 'Unknown Company')}")
        
        with col2:
            st.caption(f"📅 Filed: {metadata.get('filing_date', 'Unknown')}")
        
        with col3:
            # Download button
            with open(file_path, 'r', encoding='utf-8') as f:
                doc_content = f.read()
            
            st.download_button(
                label="📥 Download",
                data=doc_content,
                file_name=file_path.name,
                mime="text/html"
            )
        
        with col4:
            if st.button("🔍 Search in Doc"):
                st.session_state['show_search'] = True
        
        st.divider()
        
        # Search functionality
        if st.session_state.get('show_search'):
            search_term = st.text_input("Search in document", placeholder="Enter search term...")
            if search_term:
                # Highlight search terms
                doc_content = self._highlight_search_terms(doc_content, search_term)
        
        # Parse and display document
        try:
            soup = BeautifulSoup(doc_content, 'html.parser')
            
            # Extract key sections
            sections = self._extract_sections(soup)
            
            # Display table of contents
            if len(sections) > 1:
                with st.expander("📑 Table of Contents", expanded=False):
                    for section in sections:
                        if st.button(f"→ {section['title']}", key=f"toc_{section['id']}"):
                            st.session_state['jump_to_section'] = section['id']
            
            # Display the document content
            self._display_formatted_content(soup, sections)
            
        except Exception as e:
            st.error(f"Error parsing document: {e}")
            # Fallback: show raw content
            st.text_area("Raw Document Content", doc_content, height=600)
    
    def _extract_sections(self, soup):
        """Extract document sections for navigation"""
        sections = []
        section_id = 0
        
        # Look for common section patterns
        patterns = [
            # Standard headers
            (r'(ITEM|Item)\s+\d+[A-Z]?\s*[\.:]?\s*', 'h1,h2,h3,h4,h5,h6,b,strong'),
            # Part sections
            (r'(PART|Part)\s+[IVX]+\s*[\.:]?\s*', 'h1,h2,h3,h4,h5,h6,b,strong'),
            # Numbered sections
            (r'^\s*\d+\.\s+[A-Z]', 'h1,h2,h3,h4,h5,h6,b,strong'),
        ]
        
        for pattern, tags in patterns:
            for element in soup.find_all(tags):
                text = element.get_text(strip=True)
                if re.match(pattern, text):
                    sections.append({
                        'id': f"section_{section_id}",
                        'title': text[:100],  # Truncate long titles
                        'element': element
                    })
                    section_id += 1
        
        return sections
    
    def _display_formatted_content(self, soup, sections):
        """Display formatted document content"""
        
        # Add custom CSS for better formatting
        st.markdown("""
        <style>
        .sec-document {
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
        }
        .sec-document table {
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.9em;
        }
        .sec-document table th,
        .sec-document table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .sec-document table th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .highlight {
            background-color: yellow;
            font-weight: bold;
        }
        .section-header {
            color: #1f4788;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Container for the document
        with st.container():
            # Convert the soup to string with formatting
            html_content = str(soup)
            
            # Clean up the HTML
            html_content = self._clean_html_content(html_content)
            
            # Add section anchors
            for section in sections:
                section_id = section['id']
                html_content = html_content.replace(
                    str(section['element']),
                    f'<div id="{section_id}" class="section-header">{section["element"]}</div>'
                )
            
            # Display the formatted content
            st.markdown(
                f'<div class="sec-document">{html_content}</div>',
                unsafe_allow_html=True
            )
    
    def _clean_html_content(self, html_content):
        """Clean and format HTML content for display"""
        
        # Remove scripts and styles
        html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL)
        
        # Fix common formatting issues
        html_content = re.sub(r'&nbsp;', ' ', html_content)
        html_content = re.sub(r'\s+', ' ', html_content)
        
        # Ensure tables are properly formatted
        html_content = re.sub(r'<table([^>]*)>', r'<table\1 class="dataframe">', html_content)
        
        return html_content
    
    def _highlight_search_terms(self, content, search_term):
        """Highlight search terms in the content"""
        if not search_term:
            return content
            
        # Case-insensitive search
        pattern = re.compile(re.escape(search_term), re.IGNORECASE)
        
        # Replace with highlighted version
        def replace_func(match):
            return f'<span class="highlight">{match.group()}</span>'
        
        return pattern.sub(replace_func, content)
    
    def get_document_summary(self, file_path: Path) -> dict:
        """Get a quick summary of the document"""
        
        summary = {
            'file_name': file_path.name,
            'size_kb': file_path.stat().st_size / 1024,
            'sections': 0,
            'tables': 0,
            'key_terms': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Count sections
            sections = self._extract_sections(soup)
            summary['sections'] = len(sections)
            
            # Count tables
            summary['tables'] = len(soup.find_all('table'))
            
            # Extract key financial terms
            financial_terms = [
                'revenue', 'income', 'assets', 'liabilities', 'equity',
                'cash flow', 'earnings', 'shares', 'outstanding'
            ]
            
            text_lower = soup.get_text().lower()
            found_terms = []
            for term in financial_terms:
                if term in text_lower:
                    count = text_lower.count(term)
                    found_terms.append(f"{term} ({count})")
            
            summary['key_terms'] = found_terms[:5]  # Top 5 terms
            
        except Exception as e:
            st.error(f"Error analyzing document: {e}")
        
        return summary

# Standalone viewer function for integration
def view_document(file_path: str):
    """View a document given its file path"""
    viewer = DocumentViewer()
    viewer.display_document(Path(file_path))

# Test the viewer
if __name__ == "__main__":
    st.set_page_config(page_title="Document Viewer Test", layout="wide")
    
    st.title("SEC Document Viewer Test")
    
    viewer = DocumentViewer()
    
    # List available documents
    if viewer.data_dir.exists():
        companies = [d for d in viewer.data_dir.iterdir() if d.is_dir()]
        
        if companies:
            company = st.selectbox("Select Company", companies, format_func=lambda x: x.name)
            
            if company:
                docs = list(company.glob("*.html"))
                
                if docs:
                    doc = st.selectbox("Select Document", docs, format_func=lambda x: x.name)
                    
                    if st.button("View Document"):
                        viewer.display_document(doc)
                else:
                    st.warning("No documents found for this company")
        else:
            st.warning("No companies found in data directory")
    else:
        st.error("Data directory not found")