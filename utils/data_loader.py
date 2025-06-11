"""
Data Loader Utility
Date: 2025-06-07 14:02:41 UTC
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class DataLoader:
    """Load data from various sources"""
    
    def __init__(self):
        self.data_path = Path("data")
    
    def load_pipeline_data(self) -> Dict:
        """Load pipeline data"""
        pipeline_file = self.data_path / "pipeline_data.json"
        
        if pipeline_file.exists():
            try:
                with open(pipeline_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading pipeline data: {e}")
        
        return {}
    
    def load_company_cik_map(self) -> Dict:
        """Load company CIK mapping"""
        cik_file = self.data_path / "company_cik_map.json"
        
        if cik_file.exists():
            try:
                with open(cik_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading CIK map: {e}")
        
        return {}
    
    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """Get company information"""
        cik_map = self.load_company_cik_map()
        
        if ticker in cik_map:
            return {
                'ticker': ticker,
                'cik': cik_map[ticker].get('cik'),
                'name': cik_map[ticker].get('name'),
                'exchange': cik_map[ticker].get('exchange')
            }
        
        return None
    
    def get_pipeline_summary(self) -> Dict:
        """Get pipeline summary statistics"""
        pipeline_data = self.load_pipeline_data()
        
        return {
            'total': len(pipeline_data.get('all', [])),
            'pending': len(pipeline_data.get('pending', [])),
            'downloading': len(pipeline_data.get('downloading', [])),
            'completed': len(pipeline_data.get('completed', [])),
            'failed': len(pipeline_data.get('failed', [])),
            'last_update': pipeline_data.get('last_update', 'Unknown')
        }
    
    def get_recent_additions(self, limit: int = 10) -> List[Dict]:
        """Get recently added companies"""
        pipeline_data = self.load_pipeline_data()
        completed = pipeline_data.get('completed', [])
        
        # Sort by completion date
        sorted_completed = sorted(
            completed,
            key=lambda x: x.get('completed_date', ''),
            reverse=True
        )
        
        return sorted_completed[:limit]
