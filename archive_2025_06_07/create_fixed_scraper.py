#!/usr/bin/env python3
"""
Create fixed scraper that actually downloads files
Date: 2025-06-06 22:27:06 UTC
Author: thorrobber22
"""

from pathlib import Path

fixed_scraper = '''#!/usr/bin/env python3
"""
Fixed SEC Scraper - Actually downloads documents
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from pathlib import Path
import json
from datetime import datetime
import re

class FixedSECDocumentScraper:
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; HedgeIntel/1.0)',
            'Accept': '*/*'
        }
        self.data_dir = Path("data/sec_documents")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def scan_and_download_everything(self, ticker, cik):
        """Download all documents for a ticker"""
        ticker = ticker.upper()
        cik = str(cik).zfill(10)
        
        print(f"\\n🔍 Scanning {ticker} (CIK: {cik})")
        print("="*60)
        
        # Create ticker directory
        ticker_dir = self.data_dir / ticker
        ticker_dir.mkdir(exist_ok=True)
        
        # Get filings
        url = f"{self.base_url}/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&count=100"
        
        total_files = 0
        filing_count = 0
        
        async with aiohttp.ClientSession() as session:
            # Get main page
            async with session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    return {'success': False, 'error': f'Failed to get filings: HTTP {response.status}'}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find all filing links
                filing_links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/Archives/edgar/data/' in href and '-index.htm' in href:
                        filing_url = self.base_url + href
                        
                        # Get filing info from parent row
                        parent_tr = link.find_parent('tr')
                        if parent_tr:
                            cells = parent_tr.find_all('td')
                            filing_type = cells[0].text.strip() if cells else 'Unknown'
                            filing_date = cells[3].text.strip() if len(cells) > 3 else 'Unknown'
                            
                            filing_links.append({
                                'url': filing_url,
                                'type': filing_type,
                                'date': filing_date
                            })
                
                print(f"\\n📊 Found {len(filing_links)} filings")
                
                # Process each filing
                for i, filing in enumerate(filing_links[:50]):  # Limit to 50
                    print(f"\\n[{i+1}/{min(len(filing_links), 50)}] {filing['type']} - {filing['date']}")
                    
                    # Get filing page
                    async with session.get(filing['url'], headers=self.headers) as filing_response:
                        if filing_response.status == 200:
                            filing_html = await filing_response.text()
                            filing_soup = BeautifulSoup(filing_html, 'html.parser')
                            
                            # Download documents from this filing
                            downloaded = 0
                            
                            for doc_link in filing_soup.find_all('a', href=True):
                                doc_href = doc_link['href']
                                
                                # Skip index pages and look for actual documents
                                if ('/Archives/edgar/data/' in doc_href and 
                                    '-index.htm' not in doc_href and
                                    any(ext in doc_href for ext in ['.htm', '.html', '.txt', '.xml'])):
                                    
                                    doc_url = self.base_url + doc_href if not doc_href.startswith('http') else doc_href
                                    filename = doc_href.split('/')[-1]
                                    
                                    # Create safe filename
                                    safe_type = re.sub(r'[^a-zA-Z0-9]', '_', filing['type'])
                                    safe_date = re.sub(r'[^a-zA-Z0-9]', '_', filing['date'])
                                    safe_filename = f"{safe_type}_{safe_date}_{filename}"
                                    filepath = ticker_dir / safe_filename
                                    
                                    # Download if not exists
                                    if not filepath.exists():
                                        try:
                                            async with session.get(doc_url, headers=self.headers) as doc_response:
                                                if doc_response.status == 200:
                                                    content = await doc_response.read()
                                                    
                                                    with open(filepath, 'wb') as f:
                                                        f.write(content)
                                                    
                                                    print(f"   ✅ {filename} ({len(content)//1024} KB)")
                                                    downloaded += 1
                                                    total_files += 1
                                                    
                                                    # Rate limit
                                                    await asyncio.sleep(0.1)
                                                    
                                        except Exception as e:
                                            print(f"   ❌ Error downloading {filename}: {e}")
                            
                            if downloaded > 0:
                                print(f"   ✅ Downloaded {downloaded} documents")
                                filing_count += 1
                            else:
                                print(f"   ⚠️  No documents downloaded")
                    
                    # Rate limit between filings
                    await asyncio.sleep(0.2)
        
        # Save metadata
        metadata = {
            'ticker': ticker,
            'cik': cik,
            'last_scan': datetime.now().isoformat(),
            'total_files': total_files,
            'filings_processed': filing_count,
            'scan_version': '5.0-fixed'
        }
        
        with open(ticker_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\\n✅ Complete! Downloaded {total_files} files from {filing_count} filings")
        
        return {
            'success': True,
            'ticker': ticker,
            'cik': cik,
            'total_files': total_files,
            'filings_downloaded': filing_count,
            'metadata': metadata
        }

# Make it available as EnhancedSECDocumentScraper
EnhancedSECDocumentScraper = FixedSECDocumentScraper

# Test
async def test():
    scraper = FixedSECDocumentScraper()
    result = await scraper.scan_and_download_everything("CRCL", "0001876042")
    print(f"\\nResult: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test())
'''

# Save the fixed scraper
with open("scrapers/sec/fixed_sec_scraper.py", 'w', encoding='utf-8') as f:
    f.write(fixed_scraper)

# Update enhanced_sec_scraper.py to use the fixed version
with open("scrapers/sec/enhanced_sec_scraper.py", 'w', encoding='utf-8') as f:
    f.write('''from fixed_sec_scraper import FixedSECDocumentScraper as EnhancedSECDocumentScraper
__all__ = ['EnhancedSECDocumentScraper']
''')

print("✅ Created fixed_sec_scraper.py")
print("✅ Updated enhanced_sec_scraper.py to use fixed version")