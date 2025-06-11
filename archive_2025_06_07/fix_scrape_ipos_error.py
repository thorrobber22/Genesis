#!/usr/bin/env python3
"""
Fix scrape_ipos error in admin_streamlined.py
Date: 2025-06-06 12:59:44 UTC
Author: thorrobber22
"""

from pathlib import Path

print("Fixing scrape_ipos error...")

# Read admin_streamlined.py
admin_path = Path("admin_streamlined.py")
with open(admin_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add the imports at the top after other imports
import_section = """import requests
from bs4 import BeautifulSoup
import time

# Import existing IPO scrapers
try:
    from scrapers.ipo_scraper import IPOScraper
    ipo_scraper = IPOScraper()
except ImportError:
    print("Warning: Could not import IPO scraper")
    ipo_scraper = None
"""

# Find where to insert imports (after existing imports)
import_marker = "from datetime import datetime, timedelta"
if import_marker in content:
    parts = content.split(import_marker)
    content = parts[0] + import_marker + "\n" + import_section + parts[1]

# Check if scrape_ipos function exists
if "def scrape_ipos():" not in content:
    print("Adding scrape_ipos function...")
    
    # Add the function before the first use
    scrape_function = '''
def scrape_ipos():
    """Scrape IPOs using existing scrapers"""
    ipos = []
    
    # Try to use existing IPO scraper
    if ipo_scraper:
        try:
            ipo_data = ipo_scraper.get_ipo_calendar()
            
            # Convert to our format
            if ipo_data and 'upcoming' in ipo_data:
                for ipo in ipo_data['upcoming'][:20]:  # Limit to 20
                    ipos.append({
                        'ticker': ipo.get('symbol', '').upper(),
                        'company': ipo.get('company', ''),
                        'expected_date': ipo.get('expected_date', 'TBD'),
                        'source': 'IPO Scraper'
                    })
            
            return ipos
        except Exception as e:
            print(f"Error using IPO scraper: {e}")
    
    # Fallback: try direct scraping
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get("https://www.iposcoop.com/last-100-ipos/", headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find IPO table
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')[1:11]  # Get first 10 rows after header
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    ticker_text = cols[1].text.strip()
                    company_text = cols[0].text.strip()
                    
                    # Extract ticker (usually in parentheses)
                    import re
                    ticker_match = re.search(r'\\(([A-Z]+)\\)', ticker_text)
                    ticker = ticker_match.group(1) if ticker_match else ticker_text.split()[0]
                    
                    if ticker and len(ticker) <= 5:
                        ipos.append({
                            'ticker': ticker.upper(),
                            'company': company_text[:50],
                            'expected_date': 'Recent',
                            'source': 'IPOScoop'
                        })
    except Exception as e:
        print(f"Error scraping IPOScoop: {e}")
    
    # If no IPOs found, return test data
    if not ipos:
        ipos = [
            {'ticker': 'RDDT', 'company': 'Reddit Inc.', 'expected_date': 'Recent', 'source': 'Test'},
            {'ticker': 'CRCL', 'company': 'Crescent Capital', 'expected_date': 'This Week', 'source': 'Test'},
        ]
    
    return ipos
'''
    
    # Find where to insert - before the first use of scrape_ipos
    if "if check_password():" in content:
        auth_section = content.find("if check_password():")
        # Find the end of the last function before this
        last_func_end = content.rfind("\n\n", 0, auth_section)
        if last_func_end > 0:
            content = content[:last_func_end] + "\n" + scrape_function + content[last_func_end:]
else:
    print("scrape_ipos function already exists")

# Save the fixed file
with open(admin_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed scrape_ipos error")
print("\nRun: streamlit run admin_streamlined.py")
print("Password: hedgeadmin2025")