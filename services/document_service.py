"""
Document Service - Fixed Version
Date: 2025-06-09 00:24:45 UTC
"""
import os
from pathlib import Path
from typing import List, Dict, Optional

class DocumentService:
    def __init__(self):
        self.doc_path = Path("data/sec_documents")
        
    def get_companies(self) -> List[str]:
        """Get list of available companies"""
        if not self.doc_path.exists():
            return []
        
        companies = [d.name for d in self.doc_path.iterdir() if d.is_dir()]
        return sorted(companies)
    
    def get_company_documents(self, company: str) -> List[str]:
        """Get list of documents for a company - returns list of strings"""
        company_path = self.doc_path / company
        if not company_path.exists():
            return []
        
        # Return list of filenames as STRINGS, not dicts
        documents = []
        for file in company_path.glob("*.html"):
            documents.append(file.name)  # Just the filename string
            
        return sorted(documents)
    
    def get_document_content(self, company: str, filename: str) -> Optional[str]:
        """Get content of a specific document"""
        # Handle if filename is accidentally a dict
        if isinstance(filename, dict):
            # Try to extract filename from dict
            filename = filename.get('filename', filename.get('name', str(filename)))
            
        # Ensure filename is a string
        filename = str(filename)
        
        filepath = self.doc_path / company / filename
        
        if not filepath.exists():
            return None
            
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None
    
    def search_documents(self, query: str) -> List[Dict]:
        """Search across all documents"""
        results = []
        query_lower = query.lower()
        
        for company in self.get_companies():
            for doc in self.get_company_documents(company):
                content = self.get_document_content(company, doc)
                if content and query_lower in content.lower():
                    results.append({
                        'company': company,
                        'document': doc,
                        'preview': content[:200] + '...'
                    })
                    
        return results[:10]  # Return top 10 results
