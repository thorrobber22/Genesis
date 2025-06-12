"""
services/citation_service.py - Handle document citations and SEC links
Date: 2025-06-11 21:35:40 UTC
User: thorrobber22
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

class CitationService:
    def __init__(self):
        self.sec_base_url = "https://www.sec.gov/Archives/edgar/data"
        self.document_index = self.load_document_index()
        
    def load_document_index(self) -> Dict:
        """Load the document index"""
        index_path = Path('data/indexed_documents/document_index.json')
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_sec_url(self, ticker: str, document_type: str, date: str = None) -> Optional[str]:
        """Generate direct SEC URL for a document"""
        # Check if we have downloaded documents
        company_dir = Path(f'data/sec_documents/{ticker}')
        
        if company_dir.exists():
            # Look for CIK in company info
            company_info = company_dir / 'company_info.json'
            if company_info.exists():
                with open(company_info, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    cik = str(info.get('cik', '')).lstrip('0')
            else:
                # Try to extract from filenames
                cik = self._extract_cik_from_files(company_dir)
            
            if cik:
                # Build standard SEC URL
                # Example: https://www.sec.gov/Archives/edgar/data/320193/000032019324000069/aapl-20240330.htm
                return f"{self.sec_base_url}/{cik}/"
        
        return None
    
    def _extract_cik_from_files(self, company_dir: Path) -> str:
        """Try to extract CIK from downloaded files"""
        # Look for patterns in filenames
        for file in company_dir.glob('*.html'):
            # Pattern: numbers that could be CIK
            if match := re.search(r'\d{7,10}', file.name):
                return match.group()
        return ''
    
    def extract_citation_from_chunk(self, chunk: Dict) -> Dict:
        """Extract citation info from document chunk"""
        metadata = chunk.get('metadata', {})
        
        citation = {
            'source': metadata.get('source', 'Unknown'),
            'document_type': self._extract_doc_type(metadata.get('source', '')),
            'page': metadata.get('page', 'N/A'),
            'section': metadata.get('section', ''),
            'ticker': self._extract_ticker(metadata.get('source', '')),
            'text_preview': chunk.get('text', '')[:200] + '...'
        }
        
        # Try to get SEC URL
        if citation['ticker'] and citation['document_type']:
            citation['sec_url'] = self.get_sec_url(
                citation['ticker'], 
                citation['document_type']
            )
        
        return citation
    
    def _extract_doc_type(self, source: str) -> str:
        """Extract document type from source path"""
        doc_types = ['S-1', 'S-1/A', '424B4', '10-K', '10-Q', '8-K', 'DEF 14A']
        
        source_upper = source.upper()
        for doc_type in doc_types:
            if doc_type.replace('/', '') in source_upper:
                return doc_type
        
        # Check filename patterns
        if 'S-1' in source_upper:
            return 'S-1'
        elif '10-Q' in source_upper:
            return '10-Q'
        elif '10-K' in source_upper:
            return '10-K'
        
        return 'Filing'
    
    def _extract_ticker(self, source: str) -> str:
        """Extract ticker from source path"""
        # Pattern: /TICKER/filename or TICKER_doctype
        parts = Path(source).parts
        
        # Look for ticker in path
        for part in parts:
            if part.isupper() and 2 <= len(part) <= 5 and part.isalpha():
                return part
        
        # Try filename
        filename = Path(source).stem
        if match := re.match(r'^([A-Z]{2,5})_', filename):
            return match.group(1)
            
        return ''
    
    def format_citation_markdown(self, citation: Dict) -> str:
        """Format citation for display in chat"""
        ticker = citation.get('ticker', 'Unknown')
        doc_type = citation.get('document_type', 'Filing')
        page = citation.get('page', 'N/A')
        
        if citation.get('sec_url'):
            # Clickable link
            link_text = f"[{ticker} {doc_type}]({citation['sec_url']})"
            if page != 'N/A':
                return f"{link_text} - Page {page}"
            return link_text
        else:
            # No link available
            if page != 'N/A':
                return f"{ticker} {doc_type} - Page {page}"
            return f"{ticker} {doc_type}"
    
    def add_citations_to_response(self, response: str, source_chunks: List[Dict]) -> str:
        """Add citations to AI response"""
        if not source_chunks:
            return response
        
        # Extract unique citations
        citations = []
        seen = set()
        
        for chunk in source_chunks:
            citation = self.extract_citation_from_chunk(chunk)
            
            # Create unique key
            key = f"{citation['ticker']}_{citation['document_type']}_{citation['page']}"
            
            if key not in seen:
                seen.add(key)
                citations.append(citation)
        
        # Add citations section
        if citations:
            response += "\n\n**Sources:**\n"
            for i, citation in enumerate(citations[:5], 1):  # Limit to 5
                formatted = self.format_citation_markdown(citation)
                response += f"{i}. {formatted}\n"
        
        return response
