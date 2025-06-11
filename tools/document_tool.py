"""
Document Tool - S-1 document access
"""

import json
from pathlib import Path
from typing import Dict, Optional, List
import re

class DocumentTool:
    def __init__(self):
        self.processed_dir = Path("data/processed")
        self.documents_dir = Path("data/documents")
    
    def process(self, query: str, intent: Dict) -> Dict:
        """Process document query"""
        
        # Extract ticker
        ticker = self._extract_ticker(query)
        
        if not ticker:
            return {
                "status": "error",
                "message": "Please specify a ticker symbol"
            }
        
        # Look for documents
        doc_files = list(self.processed_dir.glob(f"{ticker}_*.json"))
        
        if not doc_files:
            return {
                "status": "not_found",
                "message": f"No S-1 filing found for {ticker}",
                "suggestion": "Try another ticker or wait for documents to process"
            }
        
        # Get most recent
        latest_file = max(doc_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file) as f:
            doc_data = json.load(f)
        
        return {
            "status": "success",
            "ticker": ticker,
            "document": doc_data,
            "file": latest_file.name
        }
    
    def _extract_ticker(self, query: str) -> Optional[str]:
        """Extract ticker from query"""
        words = query.split()
        for word in words:
            if len(word) >= 2 and len(word) <= 5 and word.isupper() and word.isalpha():
                return word
        return None
