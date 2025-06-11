#!/usr/bin/env python3
"""
Enhanced SEC Document Scraper - Downloads ALL filings
Date: 2025-06-06 21:34:49 UTC
Author: thorrobber22
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
            'User-Agent': 'Hedge Intelligence Bot 2.0 (admin@hedgeintel.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml'
        }
        self.data_dir = Path("data/sec_documents")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Track all document types we want
        self.target_forms = [
            'S-1', 'S-1/A',           # Registration statements
            '424B4', '424B1', '424B3', # Prospectuses
            '8-K', '8-K/A',           # Current reports
            '8-A', '8-A/A',           # Securities registration
            'EFFECT',                  # Effectiveness
            '10-Q', '10-K',           # Quarterly/Annual
            'SC 13G', 'SC 13G/A',     # Beneficial ownership
            'SC 13D', 'SC 13D/A',     # Active investor
            'DEF 14A', 'DEFM14A',     # Proxy statements
            '4', '3', '5',            # Insider forms
            'S-8', 'S-3',             # Additional offerings
            '425',                     # Business combinations
            'UPLOAD',                  # Correspondence
            'CORRESP',                 # SEC correspondence
        ]
    
    async def get_all_company_filings(self, cik, limit=200):
        """Get ALL filings for a company"""
        cik = str(cik).zfill(10)
        
        # Multiple endpoints to ensure we get everything
        urls = [
            # Primary endpoint - gets most recent
            f"{self.base_url}/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&count={limit}",
            # Archive endpoint for older filings
            f"{self.base_url}/Archives/edgar/data/{cik.lstrip('0')}/"
        ]
        
        all_filings = []
        
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 200:
                            html = await response.text()
                            filings = await self._parse_filings_page(html, cik)
                            all_filings.extend(filings)
                            
                except Exception as e:
                    print(f"Error fetching {url}: {e}")
            
            # Remove duplicates
            seen = set()
            unique_filings = []
            for filing in all_filings:
                key = f"{filing['type']}_{filing['date']}"
                if key not in seen:
                    seen.add(key)
                    unique_filings.append(filing)
            
            return unique_filings
    
    async def _parse_filings_page(self, html, cik):
        """Parse filings from HTML page"""
        soup = BeautifulSoup(html, 'html.parser')
        filings = []
        
        # Method 1: Standard table parsing
        filing_table = soup.find('table', class_='tableFile2') or soup.find('table', summary='Results')
        
        if filing_table:
            rows = filing_table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    filing_type = cells[0].text.strip()
                    
                    # Get ALL document types (not just our target list)
                    doc_link = cells[1].find('a', id='documentsbutton')
                    if doc_link:
                        filing = {
                            'type': filing_type,
                            'date': cells[3].text.strip(),
                            'description': cells[2].text.strip(),
                            'url': self.base_url + doc_link['href'],
                            'cik': cik,
                            'filing_number': cells[4].text.strip() if len(cells) > 4 else ''
                        }
                        filings.append(filing)
        
        # Method 2: Archive directory parsing
        else:
            # Look for any links that might be filings
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if '/Archives/edgar/data/' in href and any(form in link.text for form in self.target_forms):
                    filing = {
                        'type': self._extract_form_type(link.text),
                        'date': self._extract_date(link.text) or 'Unknown',
                        'description': link.text.strip(),
                        'url': self.base_url + href if not href.startswith('http') else href,
                        'cik': cik
                    }
                    filings.append(filing)
        
        return filings
    
    def _extract_form_type(self, text):
        """Extract form type from text"""
        for form in self.target_forms:
            if form in text:
                return form
        return 'OTHER'
    
    def _extract_date(self, text):
        """Try to extract date from text"""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{1,2}-\w{3}-\d{4}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return None
    
    async def download_filing_complete(self, filing, ticker):
        """Download complete filing with all exhibits"""
        ticker_dir = self.data_dir / ticker.upper()
        ticker_dir.mkdir(exist_ok=True)
        
        downloaded_files = []
        
        async with aiohttp.ClientSession() as session:
            try:
                # Get filing detail page
                async with session.get(filing['url'], headers=self.headers) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find all documents in the filing
                    doc_table = soup.find('table', class_='tableFile') or soup.find('table', summary='Document Format Files')
                    
                    if doc_table:
                        doc_rows = doc_table.find_all('tr')[1:]  # Skip header
                        
                        for i, row in enumerate(doc_rows):
                            cells = row.find_all('td')
                            if len(cells) >= 3:
                                doc_description = cells[1].text.strip()
                                doc_link = cells[2].find('a')
                                
                                if doc_link:
                                    doc_url = self.base_url + doc_link['href']
                                    
                                    # Determine file type and name
                                    if 'Complete submission' in doc_description:
                                        filename = f"{filing['type']}_{filing['date']}_complete.txt"
                                    elif 'html' in doc_link.text.lower():
                                        filename = f"{filing['type']}_{filing['date']}_{i}.html"
                                    else:
                                        ext = doc_url.split('.')[-1][:4]  # Get extension
                                        filename = f"{filing['type']}_{filing['date']}_{i}.{ext}"
                                    
                                    # Clean filename
                                    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                                    filepath = ticker_dir / filename
                                    
                                    # Download if not exists
                                    if not filepath.exists():
                                        async with session.get(doc_url, headers=self.headers) as doc_response:
                                            if doc_response.status == 200:
                                                content = await doc_response.read()
                                                
                                                with open(filepath, 'wb') as f:
                                                    f.write(content)
                                                
                                                downloaded_files.append({
                                                    'path': str(filepath),
                                                    'type': filing['type'],
                                                    'date': filing['date'],
                                                    'description': doc_description,
                                                    'size': len(content)
                                                })
                                                
                                                print(f"    ✅ Downloaded: {filename} ({len(content)//1024}KB)")
                                            
                                            # Rate limiting
                                            await asyncio.sleep(0.2)
                
                return {
                    'success': True,
                    'filing': filing,
                    'files': downloaded_files,
                    'count': len(downloaded_files)
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'filing': filing
                }
    
    async def scan_and_download_everything(self, ticker, cik):
        """Download ALL documents for a ticker"""
        print(f"\n🔍 Complete scan for {ticker} (CIK: {cik})")
        print("="*60)
        
        # Get all filings
        filings = await self.get_all_company_filings(cik)
        
        if not filings:
            return {'success': False, 'error': 'No filings found', 'ticker': ticker}
        
        print(f"📊 Found {len(filings)} total filings")
        
        # Group by type for summary
        filing_types = {}
        for filing in filings:
            ftype = filing['type']
            filing_types[ftype] = filing_types.get(ftype, 0) + 1
        
        print("\n📋 Filing Summary:")
        for ftype, count in sorted(filing_types.items()):
            print(f"   • {ftype}: {count}")
        
        # Download each filing
        print(f"\n📥 Downloading all documents...")
        results = []
        total_files = 0
        
        for i, filing in enumerate(filings):
            print(f"\n[{i+1}/{len(filings)}] {filing['type']} - {filing['date']}")
            result = await self.download_filing_complete(filing, ticker)
            
            if result['success']:
                results.append(result)
                total_files += result['count']
            else:
                print(f"    ❌ Failed: {result.get('error', 'Unknown error')}")
            
            # Rate limiting
            await asyncio.sleep(0.5)
        
        # Save metadata
        metadata_file = self.data_dir / ticker.upper() / "metadata.json"
        metadata = {
            'ticker': ticker,
            'cik': cik,
            'last_scan': datetime.now().isoformat(),
            'total_filings': len(filings),
            'downloaded_filings': len(results),
            'total_files': total_files,
            'filing_types': filing_types,
            'scan_version': '2.0'
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Complete! Downloaded {total_files} files from {len(results)} filings")
        
        return {
            'success': True,
            'ticker': ticker,
            'cik': cik,
            'filings_found': len(filings),
            'filings_downloaded': len(results),
            'total_files': total_files,
            'metadata': metadata
        }

# Test function
async def test_enhanced_scraper():
    """Test with Circle (CRCL)"""
    scraper = EnhancedSECDocumentScraper()
    
    # Test with Circle which we know has filings
    result = await scraper.scan_and_download_everything("CRCL", "0001876042")
    
    print("\n" + "="*60)
    print("🏁 TEST COMPLETE")
    print("="*60)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_enhanced_scraper())