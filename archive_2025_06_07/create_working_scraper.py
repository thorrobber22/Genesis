#!/usr/bin/env python3
"""
Create a working SEC scraper that actually downloads documents
Date: 2025-06-06 22:12:33 UTC
Author: thorrobber22
"""

from pathlib import Path

working_scraper = '''#!/usr/bin/env python3
"""
Working SEC Document Scraper - Actually Downloads Files
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from pathlib import Path
import json
from datetime import datetime
import re
from urllib.parse import urljoin

class WorkingSECDocumentScraper:
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'Hedge Intelligence Bot (admin@hedgeintel.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml'
        }
        self.data_dir = Path("data/sec_documents")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    async def scan_and_download_everything(self, ticker, cik):
        """Main entry point - download all documents for a ticker"""
        ticker = ticker.upper()
        cik = str(cik).zfill(10)
        
        print(f"\\n🔍 Scanning {ticker} (CIK: {cik})")
        print("="*60)
        
        # Create ticker directory
        ticker_dir = self.data_dir / ticker
        ticker_dir.mkdir(exist_ok=True)
        
        # Get list of filings
        filings_data = await self.get_filings_list(cik)
        
        if not filings_data['filings']:
            return {
                'success': False,
                'error': 'No filings found',
                'ticker': ticker,
                'cik': cik
            }
        
        print(f"\\n📊 Found {len(filings_data['filings'])} filings")
        
        # Count filing types
        filing_types = {}
        for filing in filings_data['filings']:
            ftype = filing['type']
            filing_types[ftype] = filing_types.get(ftype, 0) + 1
        
        print("\\n📋 Filing Summary:")
        for ftype, count in sorted(filing_types.items()):
            print(f"   • {ftype}: {count}")
        
        # Download documents from each filing
        print(f"\\n📥 Downloading documents...")
        total_files = 0
        successful_filings = 0
        
        for i, filing in enumerate(filings_data['filings']):
            print(f"\\n[{i+1}/{len(filings_data['filings'])}] {filing['type']} - {filing['date']}")
            
            # Download documents for this filing
            downloaded = await self.download_filing_documents(filing, ticker_dir)
            
            if downloaded > 0:
                total_files += downloaded
                successful_filings += 1
                print(f"   ✅ Downloaded {downloaded} documents")
            else:
                print(f"   ⚠️  No documents downloaded")
            
            # Rate limiting
            await asyncio.sleep(0.2)
        
        # Save metadata
        metadata = {
            'ticker': ticker,
            'cik': cik,
            'last_scan': datetime.now().isoformat(),
            'total_filings': len(filings_data['filings']),
            'downloaded_filings': successful_filings,
            'total_files': total_files,
            'filing_types': filing_types,
            'scan_version': '4.0'
        }
        
        with open(ticker_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\\n✅ Complete! Downloaded {total_files} files from {successful_filings} filings")
        
        return {
            'success': True,
            'ticker': ticker,
            'cik': cik,
            'filings_found': len(filings_data['filings']),
            'filings_downloaded': successful_filings,
            'total_files': total_files,
            'metadata': metadata
        }
    
    async def get_filings_list(self, cik):
        """Get list of all filings with their document URLs"""
        cik_num = cik.lstrip('0')
        
        # Try multiple URL patterns
        urls_to_try = [
            f"{self.base_url}/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&count=100",
            f"{self.base_url}/edgar/browse/?CIK={cik_num}"
        ]
        
        async with aiohttp.ClientSession() as session:
            for url in urls_to_try:
                try:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status != 200:
                            continue
                        
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Look for filings table
                        filings = []
                        
                        # Method 1: Traditional table
                        table = soup.find('table', class_='tableFile2')
                        if table:
                            rows = table.find_all('tr')[1:]  # Skip header
                            
                            for row in rows:
                                cells = row.find_all('td')
                                if len(cells) >= 2:
                                    # Look for link to filing documents
                                    links = cells[1].find_all('a', href=True)
                                    
                                    for link in links:
                                        if 'Archives/edgar/data' in link['href']:
                                            # This is a link to the filing
                                            filing_url = urljoin(self.base_url, link['href'])
                                            
                                            # Convert index URL to get actual documents
                                            if '-index.htm' in filing_url:
                                                # Already an index page
                                                doc_url = filing_url
                                            else:
                                                # Need to add -index.htm
                                                doc_url = filing_url.replace('.txt', '-index.htm')
                                                if not doc_url.endswith('-index.htm'):
                                                    doc_url = filing_url + '-index.htm'
                                            
                                            filing = {
                                                'type': cells[0].text.strip() if cells else 'Unknown',
                                                'date': cells[3].text.strip() if len(cells) > 3 else 'Unknown',
                                                'documents_url': doc_url,
                                                'description': cells[2].text.strip() if len(cells) > 2 else ''
                                            }
                                            filings.append(filing)
                                            break
                        
                        if filings:
                            return {'success': True, 'filings': filings}
                        
                except Exception as e:
                    print(f"   Error with {url}: {e}")
                    continue
            
            return {'success': False, 'filings': []}
    
    async def download_filing_documents(self, filing, save_dir):
        """Download all documents from a filing"""
        downloaded_count = 0
        
        async with aiohttp.ClientSession() as session:
            try:
                # Get the filing index page
                async with session.get(filing['documents_url'], headers=self.headers) as response:
                    if response.status != 200:
                        print(f"   ❌ Failed to get filing page: HTTP {response.status}")
                        return 0
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for document links
                    doc_links = []
                    
                    # Method 1: Look for table with document links
                    tables = soup.find_all('table')
                    for table in tables:
                        rows = table.find_all('tr')
                        for row in rows:
                            # Look for links to actual documents
                            links = row.find_all('a', href=True)
                            for link in links:
                                href = link['href']
                                link_text = link.text.strip().lower()
                                
                                # Check if this is a document link
                                if any(ext in href.lower() for ext in ['.htm', '.html', '.txt', '.xml', '.pdf']):
                                    if 'Archives/edgar/data' in href:
                                        doc_url = urljoin(self.base_url, href)
                                        
                                        # Get document info
                                        cells = row.find_all('td')
                                        doc_type = 'document'
                                        if len(cells) >= 2:
                                            doc_type = cells[1].text.strip() or cells[0].text.strip()
                                        
                                        doc_links.append({
                                            'url': doc_url,
                                            'type': doc_type,
                                            'filename': href.split('/')[-1]
                                        })
                    
                    # Method 2: Direct links in the page
                    if not doc_links:
                        all_links = soup.find_all('a', href=re.compile(r'Archives/edgar/data.*\\.(htm|html|txt|xml|pdf)', re.I))
                        for link in all_links:
                            doc_url = urljoin(self.base_url, link['href'])
                            doc_links.append({
                                'url': doc_url,
                                'type': 'document',
                                'filename': link['href'].split('/')[-1]
                            })
                    
                    # Download each document
                    for doc_info in doc_links:
                        try:
                            # Generate safe filename
                            base_name = Path(doc_info['filename']).stem
                            ext = Path(doc_info['filename']).suffix or '.html'
                            
                            # Create filename with filing info
                            safe_type = re.sub(r'[^a-zA-Z0-9]', '_', filing['type'])
                            safe_date = re.sub(r'[^a-zA-Z0-9]', '_', filing['date'])
                            
                            filename = f"{safe_type}_{safe_date}_{base_name}{ext}"
                            filename = re.sub(r'[<>:"/\\\\|?*]', '_', filename)
                            
                            filepath = save_dir / filename
                            
                            # Skip if already downloaded
                            if filepath.exists():
                                continue
                            
                            # Download the document
                            async with session.get(doc_info['url'], headers=self.headers) as doc_response:
                                if doc_response.status == 200:
                                    content = await doc_response.read()
                                    
                                    # Save the file
                                    with open(filepath, 'wb') as f:
                                        f.write(content)
                                    
                                    print(f"   ✅ {filename} ({len(content)//1024} KB)")
                                    downloaded_count += 1
                                    
                                    # Rate limiting
                                    await asyncio.sleep(0.1)
                                else:
                                    print(f"   ❌ Failed to download {filename}: HTTP {doc_response.status}")
                        
                        except Exception as e:
                            print(f"   ❌ Error downloading document: {e}")
                            continue
                
                return downloaded_count
                
            except Exception as e:
                print(f"   ❌ Error processing filing: {e}")
                return 0

# Test function
async def test():
    """Test with Circle (CRCL)"""
    print("🧪 Testing Working SEC Scraper")
    print("="*60)
    
    scraper = WorkingSECDocumentScraper()
    
    # Test with Circle
    result = await scraper.scan_and_download_everything("CRCL", "0001876042")
    
    print("\\n" + "="*60)
    print("📊 Final Result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test())
'''

# Save the working scraper
scraper_path = Path("scrapers/sec/working_sec_scraper.py")
with open(scraper_path, 'w', encoding='utf-8') as f:
    f.write(working_scraper)

print("✅ Created working_sec_scraper.py")

# Update the enhanced scraper to use the working version
update_content = '''#!/usr/bin/env python3
"""
Enhanced SEC Scraper - Wrapper for working version
"""
from working_sec_scraper import WorkingSECDocumentScraper as EnhancedSECDocumentScraper

__all__ = ['EnhancedSECDocumentScraper']
'''

enhanced_path = Path("scrapers/sec/enhanced_sec_scraper.py")
with open(enhanced_path, 'w', encoding='utf-8') as f:
    f.write(update_content)

print("✅ Updated enhanced_sec_scraper.py to use working version")