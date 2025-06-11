#!/usr/bin/env python3
"""
Fix the enhanced scraper download issue
Date: 2025-06-06 22:07:55 UTC
Author: thorrobber22
"""

from pathlib import Path

# Create fixed version
fixed_scraper = '''#!/usr/bin/env python3
"""
Fixed Enhanced SEC Document Scraper
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from pathlib import Path
import json
from datetime import datetime
import re

class EnhancedSECDocumentScraper:
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        self.data_dir = Path("data/sec_documents")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def scan_and_download_everything(self, ticker, cik):
        """Download ALL documents for a ticker"""
        ticker = ticker.upper()
        cik = str(cik).zfill(10)
        
        print(f"\\n🔍 Scanning {ticker} (CIK: {cik})")
        print("="*60)
        
        # Get all filings
        filings = await self.get_all_filings(cik)
        
        if not filings:
            return {'success': False, 'error': 'No filings found'}
        
        print(f"📊 Found {len(filings)} filings")
        
        # Create ticker directory
        ticker_dir = self.data_dir / ticker
        ticker_dir.mkdir(exist_ok=True)
        
        # Download each filing
        total_files = 0
        successful_filings = 0
        
        for i, filing in enumerate(filings):
            print(f"\\n[{i+1}/{len(filings)}] {filing['type']} - {filing['date']}")
            
            try:
                # Get filing detail page
                files = await self.download_filing_documents(filing, ticker_dir)
                
                if files:
                    total_files += len(files)
                    successful_filings += 1
                    print(f"  ✅ Downloaded {len(files)} files")
                else:
                    print(f"  ⚠️  No files downloaded")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
            
            # Rate limiting
            await asyncio.sleep(0.2)
        
        # Save metadata
        metadata = {
            'ticker': ticker,
            'cik': cik,
            'last_scan': datetime.now().isoformat(),
            'total_filings': len(filings),
            'downloaded_filings': successful_filings,
            'total_files': total_files,
            'scan_version': '3.0'
        }
        
        with open(ticker_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\\n✅ Complete! Downloaded {total_files} files from {successful_filings} filings")
        
        return {
            'success': True,
            'ticker': ticker,
            'cik': cik,
            'filings_found': len(filings),
            'filings_downloaded': successful_filings,
            'total_files': total_files,
            'metadata': metadata
        }
    
    async def get_all_filings(self, cik):
        """Get list of all filings"""
        url = f"{self.base_url}/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&count=100"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find filings table
                    table = soup.find('table', class_='tableFile2')
                    if not table:
                        return []
                    
                    filings = []
                    rows = table.find_all('tr')[1:]  # Skip header
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 4:
                            # Get the documents button
                            doc_button = cells[1].find('a', id='documentsbutton')
                            if doc_button:
                                filing = {
                                    'type': cells[0].text.strip(),
                                    'date': cells[3].text.strip(),
                                    'description': cells[2].text.strip(),
                                    'documents_url': self.base_url + doc_button['href']
                                }
                                filings.append(filing)
                    
                    return filings
                    
            except Exception as e:
                print(f"Error getting filings: {e}")
                return []
    
    async def download_filing_documents(self, filing, save_dir):
        """Download all documents for a filing"""
        downloaded_files = []
        
        async with aiohttp.ClientSession() as session:
            try:
                # Get documents page
                async with session.get(filing['documents_url'], headers=self.headers) as response:
                    if response.status != 200:
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find documents table - try multiple selectors
                    doc_table = None
                    for selector in ['table.tableFile', 'table[summary="Document Format Files"]', 'table']:
                        doc_table = soup.find('table', class_='tableFile') or soup.find('table', summary='Document Format Files')
                        if doc_table:
                            break
                    
                    if not doc_table:
                        # Try any table with document links
                        tables = soup.find_all('table')
                        for table in tables:
                            if table.find('a', href=True, text=re.compile(r'\\.(htm|html|txt|xml)', re.I)):
                                doc_table = table
                                break
                    
                    if not doc_table:
                        return []
                    
                    # Process each row
                    rows = doc_table.find_all('tr')
                    
                    for row_idx, row in enumerate(rows[1:]):  # Skip header
                        cells = row.find_all('td')
                        
                        # Find the cell with the document link
                        for cell in cells:
                            link = cell.find('a', href=True)
                            if link and any(ext in link.get('href', '').lower() for ext in ['.htm', '.html', '.txt', '.xml']):
                                doc_url = link['href']
                                if not doc_url.startswith('http'):
                                    doc_url = self.base_url + doc_url
                                
                                # Generate filename
                                doc_type = cells[1].text.strip() if len(cells) > 1 else "document"
                                ext = 'html' if '.htm' in doc_url else doc_url.split('.')[-1][:4]
                                filename = f"{filing['type']}_{filing['date']}_{row_idx}.{ext}"
                                filename = re.sub(r'[<>:"/\\\\|?*]', '_', filename)
                                
                                filepath = save_dir / filename
                                
                                # Download if not exists
                                if not filepath.exists():
                                    try:
                                        async with session.get(doc_url, headers=self.headers) as doc_response:
                                            if doc_response.status == 200:
                                                content = await doc_response.read()
                                                
                                                with open(filepath, 'wb') as f:
                                                    f.write(content)
                                                
                                                downloaded_files.append({
                                                    'path': str(filepath),
                                                    'size': len(content),
                                                    'type': doc_type
                                                })
                                                
                                                # Rate limit
                                                await asyncio.sleep(0.1)
                                                
                                    except Exception as e:
                                        print(f"    Error downloading {filename}: {e}")
                
                return downloaded_files
                
            except Exception as e:
                print(f"  Error processing filing: {e}")
                return []

# Test function
async def test():
    """Test with CRCL"""
    scraper = EnhancedSECDocumentScraper()
    result = await scraper.scan_and_download_everything("CRCL", "0001876042")
    print(f"\\nResult: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test())
'''

# Save fixed scraper
scraper_path = Path("scrapers/sec/enhanced_sec_scraper_v3.py")
with open(scraper_path, 'w', encoding='utf-8') as f:
    f.write(fixed_scraper)

print("✅ Created enhanced_sec_scraper_v3.py with fixes")

# Update the wrapper
wrapper_path = Path("scrapers/sec/enhanced_sec_scraper.py")
wrapper_content = '''from enhanced_sec_scraper_v3 import EnhancedSECDocumentScraper
__all__ = ['EnhancedSECDocumentScraper']
'''

with open(wrapper_path, 'w', encoding='utf-8') as f:
    f.write(wrapper_content)

print("✅ Updated enhanced_sec_scraper.py to use v3")