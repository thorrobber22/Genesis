"""
Calendar Tool - IPO calendar data access
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict

class CalendarTool:
    def __init__(self):
        self.cache_dir = Path("data/cache")
    
    def process(self, query: str, intent: Dict) -> Dict:
        """Process calendar query"""
        
        calendar_file = self.cache_dir / "ipo_calendar.json"
        
        if not calendar_file.exists():
            return {
                "status": "loading",
                "message": "IPO calendar is being populated. Please wait 1-2 minutes.",
                "data": []
            }
        
        with open(calendar_file) as f:
            data = json.load(f)
        
        ipos = data.get("data", [])
        
        # Filter based on query
        if "this week" in query.lower():
            # Already filtered to this week
            pass
        elif "today" in query.lower():
            today = datetime.now().strftime("%m/%d")
            ipos = [ipo for ipo in ipos if today in ipo.get('date', '')]
        
        return {
            "status": "success",
            "data": ipos,
            "updated": data.get("updated"),
            "source": "iposcoop",
            "count": len(ipos)
        }
