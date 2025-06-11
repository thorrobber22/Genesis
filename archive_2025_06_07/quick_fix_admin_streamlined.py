#!/usr/bin/env python3
"""
Quick fix for admin_streamlined.py scrape_ipos error
Date: 2025-06-06 13:03:28 UTC
Author: thorrobber22
"""

from pathlib import Path

print("Quick fixing admin_streamlined.py...")

# Read the file
admin_path = Path("admin_streamlined.py")
with open(admin_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if we have the function
if "def scrape_ipos():" not in content:
    print("Adding scrape_ipos function...")
    
    # Find where to insert - look for "# Helper Functions" or before the password check
    if "# Helper Functions" in content:
        insert_point = content.find("# Helper Functions")
        insert_point = content.find("\n", insert_point) + 1
    else:
        # Insert before the main app section
        insert_point = content.find("# Main application")
        if insert_point == -1:
            insert_point = content.find("if check_password():")
        
        # Go back to find a good insertion point
        insert_point = content.rfind("\n\n", 0, insert_point) + 2

    # The function to insert
    scrape_function = '''# Helper Functions
def scrape_ipos():
    """Scrape IPOs from various sources"""
    ipos = []
    
    try:
        # Try to use existing scraper
        from scrapers.ipo_scraper import IPOScraper
        scraper = IPOScraper()
        ipo_data = scraper.get_ipo_calendar()
        
        if ipo_data and 'upcoming' in ipo_data:
            for ipo in ipo_data['upcoming'][:20]:
                ipos.append({
                    'ticker': ipo.get('symbol', '').upper(),
                    'company': ipo.get('company', ''),
                    'expected_date': ipo.get('expected_date', 'TBD'),
                    'source': 'IPO Calendar'
                })
    except:
        # Fallback to test data
        ipos = [
            {'ticker': 'RDDT', 'company': 'Reddit Inc.', 'expected_date': 'Recent', 'source': 'Test'},
            {'ticker': 'ARM', 'company': 'ARM Holdings', 'expected_date': 'Recent', 'source': 'Test'},
            {'ticker': 'CRCL', 'company': 'Crescent Capital', 'expected_date': 'This Week', 'source': 'Test'},
        ]
    
    return ipos

'''
    
    # Insert the function
    content = content[:insert_point] + scrape_function + content[insert_point:]
    
    # Save
    with open(admin_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Added scrape_ipos function")
else:
    print("scrape_ipos function already exists")

print("\nTry again: streamlit run admin_streamlined.py")
print("Password: hedgeadmin2025")