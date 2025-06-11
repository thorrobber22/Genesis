"""IPO Scoop Scraper - Dummy Implementation"""
import json
from datetime import datetime, timedelta

def scrape_ipo_calendar():
    """Scrape IPO calendar - returns dummy data"""
    # In production, this would scrape from iposcoop.com
    dummy_data = [
        {
            "company": "TechCorp AI",
            "ticker": "TCAI",
            "exchange": "NASDAQ",
            "date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "price_range": "$18-22",
            "shares": "10M",
            "underwriter": "Goldman Sachs"
        },
        {
            "company": "BioHealth Inc",
            "ticker": "BIOH",
            "exchange": "NYSE",
            "date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "price_range": "$25-28",
            "shares": "8M",
            "underwriter": "Morgan Stanley"
        }
    ]
    
    return dummy_data

if __name__ == "__main__":
    data = scrape_ipo_calendar()
    print(json.dumps(data, indent=2))
