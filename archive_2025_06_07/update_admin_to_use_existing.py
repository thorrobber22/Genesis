#!/usr/bin/env python3
"""
Update streamlined admin to use existing IPO scraper
Date: 2025-06-06 12:49:06 UTC
Author: thorrobber22
"""

from pathlib import Path

print("Updating admin_streamlined.py to use existing IPO scraper...")

admin_path = Path("admin_streamlined.py")
if admin_path.exists():
    with open(admin_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the import section
    old_imports = "from process_and_index import process_and_index_document_sync"
    new_imports = """from process_and_index import process_and_index_document_sync
try:
    from core.ipo_scraper import scrape_all_sources
    from ipo_monitor import get_upcoming_ipos
except ImportError:
    try:
        from ipo_scraper import scrape_all_sources
    except ImportError:
        print("Warning: No IPO scraper found")
        scrape_all_sources = None"""
    
    content = content.replace(old_imports, new_imports)
    
    # Update the scrape_ipos function to use existing scraper
    new_scrape_function = '''def scrape_ipos():
    """Use existing IPO scraper or fallback"""
    ipos = []
    
    # Try to use existing scraper
    if 'scrape_all_sources' in globals() and scrape_all_sources:
        try:
            ipos = scrape_all_sources()
            # Convert to expected format if needed
            formatted_ipos = []
            for ipo in ipos:
                formatted_ipos.append({
                    'ticker': ipo.get('ticker', ipo.get('symbol', '')),
                    'company': ipo.get('company', ipo.get('company_name', '')),
                    'expected_date': ipo.get('expected_date', ipo.get('ipo_date', 'TBD')),
                    'source': ipo.get('source', 'Scraper')
                })
            return formatted_ipos
        except Exception as e:
            print(f"Error using existing scraper: {e}")
    
    # Fallback to manual scraping
    try:
        response = requests.get("https://www.iposcoop.com/", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Simple extraction - you may need to adjust based on actual HTML
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) >= 3:
                    ticker = cols[0].text.strip()
                    if ticker and len(ticker) <= 5:  # Basic validation
                        ipos.append({
                            'ticker': ticker.upper(),
                            'company': cols[1].text.strip()[:50],
                            'expected_date': cols[2].text.strip(),
                            'source': 'IPOScoop'
                        })
    except:
        pass
    
    # If still no IPOs, use test data
    if not ipos:
        ipos = [
            {'ticker': 'CRCL', 'company': 'Crescent Capital', 'expected_date': 'This Week', 'source': 'Test'},
        ]
    
    return ipos[:20]  # Limit to 20 IPOs'''
    
    # Find and replace the scrape_ipos function
    import re
    pattern = r'def scrape_ipos\(\):.*?(?=\ndef|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        content = content[:match.start()] + new_scrape_function + content[match.end():]
        
        with open(admin_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ Updated admin_streamlined.py to use existing IPO scraper")
    else:
        print("Could not find scrape_ipos function to update")
else:
    print("admin_streamlined.py not found")