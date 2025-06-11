# Save as ipo_dashboard/ipo_data_manager.py
"""
IPO Data Manager for tracking and managing IPO information
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IPODataManager:
    """Manage IPO data storage and retrieval"""

    def __init__(self, data_file: str = "./data/ipo_data.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.ipo_data = []
        self.last_updated = None
        self._load_data()

    def _load_data(self) -> None:
        """Load IPO data from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # Handle new format
                        self.ipo_data = data.get('ipos', [])
                        self.last_updated = data.get('last_updated')
                    elif isinstance(data, list):
                        # Handle legacy format
                        self.ipo_data = data
                        self.last_updated = None
            except Exception as e:
                logger.error(f"Error loading IPO data: {e}")
                self.ipo_data = []
                self.last_updated = None
        else:
            self.ipo_data = []
            self.last_updated = None

    def _save_data(self):
        """Save IPO data to file"""
        try:
            data = {
                'ipos': self.ipo_data,
                'last_updated': self.last_updated or datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving IPO data: {e}")

    def add_ipo(self, ipo_info: Dict) -> bool:
        """Add a new IPO to the database"""
        # Check if IPO already exists
        ticker = ipo_info.get('ticker', '').upper()
        if ticker and ticker != 'TBD':
            # Remove existing entry if present
            self.ipo_data = [ipo for ipo in self.ipo_data if ipo.get('ticker', '').upper() != ticker]
        
        # Add the new IPO
        self.ipo_data.append(ipo_info)
        self.last_updated = datetime.now().isoformat()
        self._save_data()
        
        logger.info(f"Added IPO: {ipo_info.get('company', 'Unknown')}")
        return True

    def get_ipo_data(self, upcoming_only: bool = True) -> List[Dict]:
        """Get IPO data, optionally filtered for upcoming IPOs"""
        if not upcoming_only:
            return self.ipo_data
        
        # Filter for upcoming IPOs
        upcoming = []
        today = datetime.now().date()
        
        for ipo in self.ipo_data:
            expected_date = ipo.get('expected_date', '')
            
            # Skip if no date or TBD
            if not expected_date or expected_date == 'TBD':
                upcoming.append(ipo)  # Include TBD dates
                continue
            
            # Parse date
            try:
                ipo_date = datetime.strptime(expected_date, '%Y-%m-%d').date()
                if ipo_date >= today:
                    upcoming.append(ipo)
            except Exception as e:
                logger.error(f"Error parsing date for {ipo.get('company')}: {e}")
                upcoming.append(ipo)
        
        return sorted(upcoming, key=lambda x: x.get('expected_date', 'ZZZ'))

    def get_last_updated(self) -> Optional[str]:
        """Get the last update timestamp"""
        if self.last_updated:
            try:
                # Format the timestamp nicely
                dt = datetime.fromisoformat(self.last_updated.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                return self.last_updated
        return None

    def get_lockup_expirations(self, days_ahead: int = 30) -> List[Dict]:
        """Get IPOs with lock-up periods expiring soon"""
        today = datetime.now().date()
        future_date = today + timedelta(days=days_ahead)
        
        expirations = []
        
        for ipo in self.ipo_data:
            lockup_date = ipo.get('lockup_expiration')
            if lockup_date and lockup_date != 'TBD':
                try:
                    expiry = datetime.strptime(lockup_date, '%Y-%m-%d').date()
                    if today <= expiry <= future_date:
                        ipo['days_until_expiry'] = (expiry - today).days
                        expirations.append(ipo)
                except Exception as e:
                    logger.error(f"Error parsing lockup date: {e}")
        
        return sorted(expirations, key=lambda x: x.get('lockup_expiration', ''))

    def search_ipos(self, query: str) -> List[Dict]:
        """Search IPOs by company name or ticker"""
        query_lower = query.lower()
        
        return [
            ipo for ipo in self.ipo_data
            if query_lower in ipo.get('company', '').lower() or
               query_lower in ipo.get('ticker', '').lower()
        ]

    def update_ipo(self, ticker: str, updates: Dict) -> bool:
        """Update an existing IPO's information"""
        ticker = ticker.upper()
        
        for i, ipo in enumerate(self.ipo_data):
            if ipo.get('ticker', '').upper() == ticker:
                self.ipo_data[i].update(updates)
                self.last_updated = datetime.now().isoformat()
                self._save_data()
                logger.info(f"Updated IPO: {ticker}")
                return True
        
        logger.warning(f"IPO not found: {ticker}")
        return False

    def remove_ipo(self, ticker: str) -> bool:
        """Remove an IPO from the database"""
        ticker = ticker.upper()
        original_count = len(self.ipo_data)
        
        self.ipo_data = [ipo for ipo in self.ipo_data if ipo.get('ticker', '').upper() != ticker]
        
        if len(self.ipo_data) < original_count:
            self.last_updated = datetime.now().isoformat()
            self._save_data()
            logger.info(f"Removed IPO: {ticker}")
            return True
        
        logger.warning(f"IPO not found: {ticker}")
        return False

    def get_stats(self) -> Dict:
        """Get statistics about the IPO database"""
        total = len(self.ipo_data)
        upcoming = len(self.get_ipo_data(upcoming_only=True))
        
        # Count by exchange
        exchange_counts = {}
        for ipo in self.ipo_data:
            exchange = ipo.get('exchange', 'Unknown')
            exchange_counts[exchange] = exchange_counts.get(exchange, 0) + 1
        
        return {
            'total_ipos': total,
            'upcoming_ipos': upcoming,
            'by_exchange': exchange_counts,
            'last_updated': self.last_updated
        }


# Test the manager
if __name__ == "__main__":
    manager = IPODataManager()
    
    # Add sample IPOs
    sample_ipos = [
        {
            'company': 'TechVision AI',
            'ticker': 'TVAI',
            'expected_date': '2025-06-15',
            'price_range': '$18-20',
            'shares': '10M',
            'exchange': 'NASDAQ',
            'lead_underwriter': 'Goldman Sachs',
            'lockup_expiration': '2025-12-15'
        },
        {
            'company': 'Green Energy Corp',
            'ticker': 'GENC',
            'expected_date': '2025-06-20',
            'price_range': '$25-28',
            'shares': '15M',
            'exchange': 'NYSE',
            'lead_underwriter': 'Morgan Stanley',
            'lockup_expiration': '2025-12-20'
        }
    ]
    
    for ipo in sample_ipos:
        manager.add_ipo(ipo)
    
    # Get upcoming IPOs
    upcoming = manager.get_ipo_data()
    print(f"Upcoming IPOs: {len(upcoming)}")
    
    # Get stats
    stats = manager.get_stats()
    print(f"Stats: {stats}")
    
    # Get last updated
    print(f"Last updated: {manager.get_last_updated()}")