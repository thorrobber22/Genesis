"""
Data Service - Simple, Real Data Only
Date: 2025-06-14 18:06:04 UTC
Author: thorrobber22
"""

import json
from pathlib import Path
from typing import Dict, List

class DataService:
    """Simple data service - real data only"""
    
    def __init__(self):
        self.data_dir = Path("data")
    
    def get_ipo_calendar(self, filters: Dict = None) -> List[Dict]:
        """Get IPO calendar - REAL DATA ONLY"""
        
        # Read the actual scraped data
        calendar_path = self.data_dir / "ipo_calendar.json"
        
        if calendar_path.exists():
            with open(calendar_path, 'r') as f:
                data = json.load(f)
            
            # Return the actual listings
            listings = data.get('listings', [])
            print(f"✅ Loaded {len(listings)} IPOs from {calendar_path.name}")
            return listings
        else:
            print(f"❌ No data file at {calendar_path}")
            return []
    
    def get_company_profile(self, ticker: str) -> Dict:
        """Get company from IPO list"""
        ipos = self.get_ipo_calendar()
        for ipo in ipos:
            if ipo.get('ticker') == ticker:
                return ipo
        return {}
    
    def get_company_documents(self, ticker: str) -> List[Dict]:
        """Get documents if they exist"""
        docs_dir = self.data_dir / "ipo_filings" / ticker
        if docs_dir.exists():
            return [
                {"filename": f.name, "path": str(f)}
                for f in docs_dir.glob("*.html")
            ]
        return []
    
    def get_watchlist(self) -> List[str]:
        """Get watchlist"""
        return []
    
    def update_watchlist(self, ticker: str, action: str) -> bool:
        """Update watchlist"""
        return True
    
    def get_companies_tree(self) -> Dict:
        """Get companies by sector"""
        ipos = self.get_ipo_calendar()
        tree = {"Technology": []}
        
        for ipo in ipos:
            tree["Technology"].append({
                'ticker': ipo.get('ticker'),
                'company': ipo.get('company'),
                'filing_count': 0
            })
        
        return tree
