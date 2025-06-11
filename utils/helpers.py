"""Helper Functions"""
from datetime import datetime
import re

def format_number(num):
    """Format number with commas"""
    try:
        return f"{int(num):,}"
    except:
        return str(num)
        
def clean_ticker(ticker):
    """Clean and validate ticker symbol"""
    if not ticker:
        return None
    cleaned = re.sub(r'[^A-Z]', '', ticker.upper())
    return cleaned if 1 <= len(cleaned) <= 5 else None
    
def parse_date(date_str):
    """Parse various date formats"""
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d-%b-%Y",
        "%B %d, %Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return None
