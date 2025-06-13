"""
data_service.py - Data management service
Date: 2025-06-12 01:25:00 UTC
User: thorrobber22
"""

import json
from pathlib import Path
from datetime import datetime

# Data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def load_ipo_data():
    """Load IPO calendar data"""
    try:
        with open(DATA_DIR / "ipo_calendar.json", "r") as f:
            return json.load(f)
    except:
        return {"ipos": [], "last_updated": datetime.now().isoformat()}

def save_ipo_data(data):
    """Save IPO calendar data"""
    data["last_updated"] = datetime.now().isoformat()
    with open(DATA_DIR / "ipo_calendar.json", "w") as f:
        json.dump(data, f, indent=2)

def get_company_data(ticker):
    """Get company profile data"""
    try:
        with open(DATA_DIR / "company_profiles.json", "r") as f:
            profiles = json.load(f)
            return profiles.get(ticker, {})
    except:
        return {}

def update_watchlist(ticker, action="add"):
    """Update user watchlist"""
    try:
        with open(DATA_DIR / "watchlists.json", "r") as f:
            data = json.load(f)
    except:
        data = {"watchlist": [], "last_updated": ""}
    
    if action == "add" and ticker not in data["watchlist"]:
        data["watchlist"].append(ticker)
    elif action == "remove" and ticker in data["watchlist"]:
        data["watchlist"].remove(ticker)
    
    data["last_updated"] = datetime.now().isoformat()
    
    with open(DATA_DIR / "watchlists.json", "w") as f:
        json.dump(data, f, indent=2)
    
    return data["watchlist"]

def get_watchlist():
    """Get current watchlist"""
    try:
        with open(DATA_DIR / "watchlists.json", "r") as f:
            return json.load(f).get("watchlist", [])
    except:
        return []
