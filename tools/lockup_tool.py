"""
Lock-up Tool - Track lock-up expirations
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict

class LockupTool:
    def __init__(self):
        self.cache_dir = Path("data/cache")
    
    def process(self, query: str, intent: Dict) -> Dict:
        """Process lock-up query"""
        
        lockup_file = self.cache_dir / "lockup_calendar.json"
        
        if not lockup_file.exists():
            return {
                "status": "loading",
                "message": "Lock-up data is being calculated.",
                "data": []
            }
        
        with open(lockup_file) as f:
            data = json.load(f)
        
        lockups = data.get("data", [])
        
        # Filter based on query
        if "next 30" in query.lower() or "this month" in query.lower():
            lockups = [l for l in lockups if 0 <= l["days_until"] <= 30]
        elif "this week" in query.lower():
            lockups = [l for l in lockups if 0 <= l["days_until"] <= 7]
        
        # Sort by days until
        lockups.sort(key=lambda x: x["days_until"])
        
        return {
            "status": "success",
            "data": lockups,
            "updated": data.get("updated"),
            "count": len(lockups)
        }
