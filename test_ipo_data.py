#!/usr/bin/env python3
"""
Test IPO data availability
"""

from pathlib import Path
import json

# Check all possible IPO data locations
data_locations = [
    Path("data/ipo_data/ipo_calendar_latest.json"),
    Path("data/ipo_pipeline/ipo_calendar.json"),
    Path("data/ipo_data"),
    Path("data/ipo_pipeline")
]

print("🔍 Checking for IPO data files...\n")

for location in data_locations:
    if location.exists():
        if location.is_file():
            print(f"✅ Found: {location}")
            with open(location, 'r') as f:
                data = json.load(f)
            print(f"   Contains: {len(data)} keys")
            for key, value in data.items():
                if isinstance(value, list):
                    print(f"   - {key}: {len(value)} items")
                else:
                    print(f"   - {key}: {value}")
            print()
        else:
            print(f"📁 Directory exists: {location}")
            files = list(location.glob("*.json"))
            print(f"   Contains {len(files)} JSON files")
            for file in files[:5]:
                print(f"   - {file.name}")
            print()
    else:
        print(f"❌ Not found: {location}")

# Run the IPO scraper to get fresh data
print("\n🚀 Running IPO scraper to get fresh data...")
try:
    from scrapers.ipo_scraper_real import IPOScraperReal
    scraper = IPOScraperReal()
    result = scraper.scrape_ipo_calendar()
    print(f"✅ Scraped {len(result.get('filed', []))} filed IPOs")
except Exception as e:
    print(f"❌ Error running scraper: {e}")