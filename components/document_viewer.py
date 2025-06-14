# components/document_viewer.py - NEW FILE
import streamlit as st
from pathlib import Path
from bs4 import BeautifulSoup
import os

class DocumentViewer:
    def __init__(self):
        self.doc_path = Path("data/ipo_filings/AIRO")
        
    def get_available_documents(self, company: str) -> list:
        """Get list of HTML documents for a company"""
        company_path = Path(f"data/ipo_filings/{company}")
        if company_path.exists():
            return sorted([f.name for f in company_path.glob("*.html")])
        return []
    
    def load_document(self, company: str, filename: str) -> str:
        """Load and clean HTML document"""
        file_path = Path(f"data/ipo_filings/{company}/{filename}")
        
        if not file_path.exists():
            return "<p>Document not found</p>"
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get body content or full content
            body = soup.find('body')
            if body:
                return str(body)
            else:
                return str(soup)
                
        except Exception as e:
            return f"<p>Error loading document: {str(e)}</p>"
    
    def render(self, company: str, selected_doc: str = None):
        """Render the document viewer component"""
        docs = self.get_available_documents(company)
        
        if not docs:
            st.info(f"No documents found for {company}")
            return
        
        # Document selector
        if not selected_doc:
            selected_doc = docs[0]
        
        # Display the document
        doc_content = self.load_document(company, selected_doc)
        
        # Create an iframe-style container
        st.markdown(f"""
        <div style="
            height: 600px;
            overflow-y: auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            color: black;
        ">
            {doc_content}
        </div>
        """, unsafe_allow_html=True)

# Initialize
document_viewer = DocumentViewer()