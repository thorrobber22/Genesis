"""
CIK Resolver - Maps tickers to CIK numbers
Date: 2025-06-07 19:08:29 UTC
"""

import json
from pathlib import Path
from typing import Optional, Dict

class CIKResolver:
    """Resolve company tickers to CIK numbers"""
    
    def __init__(self):
        self.cik_map_file = Path("data/company_cik_map.json")
        self.cik_map = self.load_cik_map()
    
    def load_cik_map(self) -> Dict:
        """Load CIK mappings from file"""
        if self.cik_map_file.exists():
            try:
                with open(self.cik_map_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def get_cik(self, ticker: str) -> Optional[str]:
        """Get CIK for a ticker"""
        ticker = ticker.upper()
        if ticker in self.cik_map:
            return self.cik_map[ticker].get('cik')
        return None
    
    def add_mapping(self, ticker: str, cik: str, name: str = None):
        """Add a new ticker->CIK mapping"""
        self.cik_map[ticker.upper()] = {
            'cik': cik,
            'name': name or ticker,
            'added': datetime.now().isoformat()
        }
        self.save_cik_map()
    
    def save_cik_map(self):
        """Save CIK mappings to file"""
        self.cik_map_file.parent.mkdir(exist_ok=True)
        with open(self.cik_map_file, 'w') as f:
            json.dump(self.cik_map, f, indent=2)
