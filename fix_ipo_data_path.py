#!/usr/bin/env python3
"""
Fix IPO data path issues
"""

from pathlib import Path
import shutil
import json

# Create necessary directories
Path("data/ipo_pipeline").mkdir(parents=True, exist_ok=True)
Path("data/ipo_data").mkdir(parents=True, exist_ok=True)

# Find any existing IPO data
source_files = [
    Path("data/ipo_data/ipo_calendar_latest.json"),
    Path("data/ipo_data/ipo_calendar.json"),
]

target_file = Path("data/ipo_pipeline/ipo_calendar.json")

# Copy the latest data to where your component expects it
for source in source_files:
    if source.exists():
        print(f"✅ Found IPO data at: {source}")
        
        # Copy to expected location
        shutil.copy2(source, target_file)
        print(f"✅ Copied to: {target_file}")
        
        # Also create a symlink for compatibility
        alt_path = Path("data/ipo_data/ipo_calendar.json")
        if not alt_path.exists():
            shutil.copy2(source, alt_path)
            print(f"✅ Also copied to: {alt_path}")
        
        break
else:
    print("❌ No IPO data found. Running scraper...")
    
    # Run the scraper
    try:
        from scrapers.ipo_scraper_real import IPOScraperReal
        scraper = IPOScraperReal()
        result = scraper.scrape_ipo_calendar()
        
        # Save in expected location
        with open(target_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Scraped and saved IPO data to: {target_file}")
    except Exception as e:
        print(f"❌ Error: {e}")