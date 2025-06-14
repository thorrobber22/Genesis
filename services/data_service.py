"""
Data Service - Unified data management layer
Date: 2025-06-14 02:43:30 UTC
Author: thorrobber22
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class DataService:
    """Centralized data access and management"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.cache = {}
        self.last_update = {}
        
    def get_ipo_calendar(self, filters: Dict = None) -> pd.DataFrame:
        """Get IPO calendar data with optional filters"""
        calendar_path = self.data_dir / "ipo_calendar.json"
        
        if calendar_path.exists():
            with open(calendar_path, 'r') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            
            # Apply filters
            if filters:
                if filters.get('period') == 'This Week':
                    # Filter to current week
                    today = pd.Timestamp.now()
                    week_start = today - pd.Timedelta(days=today.dayofweek)
                    week_end = week_start + pd.Timedelta(days=6)
                    # Add date filtering logic here
                
                if filters.get('status') and filters['status'] != 'All':
                    df = df[df['status'] == filters['status']]
            
            return df
        
        return pd.DataFrame()
    
    def get_company_profile(self, ticker: str) -> Dict:
        """Get detailed company profile"""
        profiles_path = self.data_dir / "company_profiles.json"
        
        if profiles_path.exists():
            with open(profiles_path, 'r') as f:
                profiles = json.load(f)
            return profiles.get(ticker, {})
        
        return {}
    
    def get_company_documents(self, ticker: str) -> List[Dict]:
        """Get list of documents for a company"""
        docs = []
        company_dir = self.data_dir / "ipo_filings" / ticker
        
        if company_dir.exists():
            for file_path in company_dir.glob("*"):
                if file_path.suffix in ['.pdf', '.html']:
                    doc = {
                        'filename': file_path.name,
                        'path': str(file_path),
                        'type': self._get_doc_type(file_path.name),
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                    }
                    docs.append(doc)
        
        return sorted(docs, key=lambda x: x['modified'], reverse=True)
    
    def _get_doc_type(self, filename: str) -> str:
        """Determine document type from filename"""
        if 'S-1' in filename and '/A' in filename:
            return 'S-1/A Amendment'
        elif 'S-1' in filename:
            return 'S-1 Registration'
        elif '424B' in filename:
            return 'Prospectus'
        elif '10-K' in filename:
            return '10-K Annual Report'
        else:
            return 'Other Filing'
    
    def update_watchlist(self, ticker: str, action: str = 'add') -> bool:
        """Add/remove ticker from watchlist"""
        watchlist_path = self.data_dir / "watchlist.json"
        
        if watchlist_path.exists():
            with open(watchlist_path, 'r') as f:
                watchlist = json.load(f)
        else:
            watchlist = {'tickers': [], 'alerts': {}}
        
        if action == 'add' and ticker not in watchlist['tickers']:
            watchlist['tickers'].append(ticker)
        elif action == 'remove' and ticker in watchlist['tickers']:
            watchlist['tickers'].remove(ticker)
            watchlist['alerts'].pop(ticker, None)
        
        with open(watchlist_path, 'w') as f:
            json.dump(watchlist, f, indent=2)
        
        return True
    
    def get_document_index(self, ticker: str, doc_name: str) -> Dict:
        """Get document index with section mappings"""
        index_path = self.data_dir / "document_index.json"
        
        if index_path.exists():
            with open(index_path, 'r') as f:
                index = json.load(f)
            
            if ticker in index and doc_name in index[ticker]:
                return index[ticker][doc_name]
        
        # Return default structure
        return {
            'pages': 0,
            'sections': {
                'lockup': {'page': 0, 'section': ''},
                'risks': {'page': 0, 'section': ''},
                'financials': {'page': 0, 'section': ''}
            }
        }
    
    def save_to_report(self, report_data: Dict) -> str:
        """Save report data and return report ID"""
        reports_dir = self.data_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Generate report ID
        report_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"report_{report_id}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return report_id

# Create singleton instance
data_service = DataService()
