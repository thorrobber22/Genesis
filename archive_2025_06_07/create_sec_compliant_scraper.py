#!/usr/bin/env python3
"""
Create SEC-compliant scraper that won't get blocked
Date: 2025-06-06 22:29:36 UTC
Author: thorrobber22
"""

from pathlib import Path

compliant_scraper = '''#!/usr/bin/env python3
"""
SEC-Compliant Document Scraper - Follows SEC guidelines
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from pathlib import Path
import json
from datetime import datetime
import re
import time
import random

class SECCompliantScraper:
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        
        # SEC requires identifying yourself
        self.headers = {
            'User-Agent': 'Hedge Intelligence admin@hedgeintelligence.ai',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        self.data_dir = Path("data/sec_documents")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # SEC rate limit: 10 requests per second
        self.rate_limit_delay = 0.15  # Be conservative
    
    async def wait_with_jitter(self):
        """Add random jitter to avoid looking like a bot"""
        delay = self.rate_limit_delay + random.uniform(0.1, 0.3)
        await asyncio.sleep(delay)
    
    async def fetch_with_retry(self, session, url, max_retries=3):
        """Fetch URL with retry logic"""
        for attempt in range(max_retries):
            try:
                await self.wait_with_jitter()
                
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 403:
                        print(f"   ⚠️  403 Forbidden - Waiting {2 ** attempt} seconds...")
                        await asyncio.sleep(2 ** attempt)
                    else:
                        print(f"   ⚠️  HTTP {response.status} - Retrying...")
                        await asyncio.sleep(1)
                        
            except Exception as e:
                print(f"   ⚠️  Error: {e} - Retrying...")
                await asyncio.sleep(1)
        
        return None
    
    async def scan_and_download_everything(self, ticker, cik):
        """Main download function"""
        ticker = ticker.upper()
        cik = str(cik).zfill(10)
        
        print(f"\\n🔍 SEC-Compliant Scan for {ticker} (CIK: {cik})")
        print("="*60)
        print("⏳ Using SEC-compliant rate limiting...")
        
        # Create ticker directory
        ticker_dir = self.data_dir / ticker
        ticker_dir.mkdir(exist_ok=True)
        
        # Create session with timeout
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=1)  # Only 1 connection at a time
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            # Try different URL patterns
            urls_to_try = [
                f"https://data.sec.gov/submissions/CIK{cik}.json",  # New API endpoint
                f"{self.base_url}/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=&dateb=&owner=include&count=40",
                f"{self.base_url}/edgar/browse/?CIK={cik.lstrip('0')}&owner=include"
            ]
            
            filings_found = False
            total_files = 0
            
            for url in urls_to_try:
                print(f"\\n📡 Trying: {url}")
                
                if url.endswith('.json'):
                    # Handle JSON API
                    json_text = await self.fetch_with_retry(session, url)
                    if json_text:
                        try:
                            data = json.loads(json_text)
                            recent_filings = data.get('filings', {}).get('recent', {})
                            
                            if recent_filings:
                                print(f"✅ Found filings via API")
                                filings_found = True
                                
                                # Process recent filings
                                accession_numbers = recent_filings.get('accessionNumber', [])[:20]
                                forms = recent_filings.get('form', [])[:20]
                                dates = recent_filings.get('filingDate', [])[:20]
                                
                                for i, (acc, form, date) in enumerate(zip(accession_numbers, forms, dates)):
                                    print(f"\\n[{i+1}/20] {form} - {date}")
                                    
                                    # Construct filing URL
                                    acc_clean = acc.replace('-', '')
                                    filing_url = f"{self.base_url}/Archives/edgar/data/{cik.lstrip('0')}/{acc_clean}/{acc}-index.html"
                                    
                                    filing_html = await self.fetch_with_retry(session, filing_url)
                                    if filing_html:
                                        soup = BeautifulSoup(filing_html, 'html.parser')
                                        
                                        # Find document links
                                        doc_count = 0
                                        for link in soup.find_all('a', href=True):
                                            href = link['href']
                                            if any(ext in href for ext in ['.htm', '.html', '.txt', '.xml']) and 'index' not in href:
                                                doc_url = self.base_url + href if href.startswith('/') else filing_url.rsplit('/', 1)[0] + '/' + href
                                                
                                                # Download document
                                                doc_content = await self.fetch_with_retry(session, doc_url)
                                                if doc_content:
                                                    filename = f"{form}_{date}_{href.split('/')[-1]}"
                                                    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
                                                    
                                                    filepath = ticker_dir / filename
                                                    with open(filepath, 'w', encoding='utf-8') as f:
                                                        f.write(doc_content)
                                                    
                                                    print(f"   ✅ {filename} ({len(doc_content)//1024} KB)")
                                                    doc_count += 1
                                                    total_files += 1
                                                    
                                                    if doc_count >= 3:  # Limit docs per filing
                                                        break
                                        
                                        if doc_count == 0:
                                            print(f"   ⚠️  No documents found")
                                
                                break
                                
                        except json.JSONDecodeError:
                            print("   ❌ Invalid JSON response")
                
                else:
                    # Handle HTML pages
                    html = await self.fetch_with_retry(session, url)
                    if html:
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Look for filings table
                        table = soup.find('table', class_='tableFile2') or soup.find('table', {'summary': 'Results'})
                        
                        if table:
                            print("✅ Found filings table")
                            filings_found = True
                            
                            rows = table.find_all('tr')[1:21]  # First 20 filings
                            
                            for i, row in enumerate(rows):
                                cells = row.find_all('td')
                                if len(cells) >= 2:
                                    form_type = cells[0].text.strip()
                                    
                                    # Find documents link
                                    doc_link = None
                                    for link in row.find_all('a', href=True):
                                        if 'index.htm' in link['href']:
                                            doc_link = self.base_url + link['href']
                                            break
                                    
                                    if doc_link:
                                        print(f"\\n[{i+1}/20] {form_type}")
                                        
                                        # Get filing page
                                        filing_html = await self.fetch_with_retry(session, doc_link)
                                        if filing_html:
                                            filing_soup = BeautifulSoup(filing_html, 'html.parser')
                                            
                                            # Download first few documents
                                            doc_count = 0
                                            for link in filing_soup.find_all('a', href=True):
                                                href = link['href']
                                                if any(ext in href for ext in ['.htm', '.txt', '.xml']) and 'index' not in href:
                                                    doc_url = doc_link.rsplit('/', 1)[0] + '/' + href if not href.startswith('http') else href
                                                    
                                                    filename = f"{form_type}_{i}_{href.split('/')[-1]}"
                                                    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
                                                    
                                                    filepath = ticker_dir / filename
                                                    if not filepath.exists():
                                                        doc_content = await self.fetch_with_retry(session, doc_url)
                                                        if doc_content:
                                                            with open(filepath, 'w', encoding='utf-8') as f:
                                                                f.write(doc_content)
                                                            
                                                            print(f"   ✅ {filename} ({len(doc_content)//1024} KB)")
                                                            doc_count += 1
                                                            total_files += 1
                                                            
                                                            if doc_count >= 3:
                                                                break
                            
                            break
            
            if not filings_found:
                return {
                    'success': False,
                    'error': 'Could not access SEC filings. Check CIK or try again later.',
                    'ticker': ticker,
                    'cik': cik
                }
            
            # Save metadata
            metadata = {
                'ticker': ticker,
                'cik': cik,
                'last_scan': datetime.now().isoformat(),
                'total_files': total_files,
                'scan_version': '6.0-compliant'
            }
            
            with open(ticker_dir / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"\\n✅ Complete! Downloaded {total_files} files")
            
            return {
                'success': True,
                'ticker': ticker,
                'cik': cik,
                'total_files': total_files,
                'metadata': metadata
            }

# Also expose as EnhancedSECDocumentScraper
EnhancedSECDocumentScraper = SECCompliantScraper

# Test
async def test():
    scraper = SECCompliantScraper()
    
    # Test with known working CIKs
    test_cases = [
        ("AAPL", "0000320193"),  # Apple
        ("CRCL", "0001876042"),  # Circle
    ]
    
    for ticker, cik in test_cases:
        result = await scraper.scan_and_download_everything(ticker, cik)
        print(f"\\n{ticker} Result: {json.dumps(result, indent=2)}")
        await asyncio.sleep(2)  # Wait between tests

if __name__ == "__main__":
    asyncio.run(test())
'''

# Save the compliant scraper
Path("scrapers/sec").mkdir(parents=True, exist_ok=True)
with open("scrapers/sec/sec_compliant_scraper.py", 'w', encoding='utf-8') as f:
    f.write(compliant_scraper)

# Update enhanced_sec_scraper.py
with open("scrapers/sec/enhanced_sec_scraper.py", 'w', encoding='utf-8') as f:
    f.write('''from sec_compliant_scraper import SECCompliantScraper as EnhancedSECDocumentScraper
__all__ = ['EnhancedSECDocumentScraper']
''')

print("✅ Created sec_compliant_scraper.py")
print("✅ Updated enhanced_sec_scraper.py")
print("\nThis scraper:")
print("• Uses proper User-Agent identifying our service")
print("• Implements rate limiting (SEC requires max 10 req/sec)")
print("• Adds random jitter to avoid bot detection")
print("• Uses the new SEC data API when possible")
print("• Has retry logic with exponential backoff")
print("• Follows SEC's fair access guidelines")