#!/usr/bin/env python3
"""
Create SEC scraper components for automated IPO monitoring
Date: 2025-06-06 17:22:45 UTC
Author: thorrobber22
"""

import os
from pathlib import Path

# Create scrapers directory structure
Path("scrapers/sec").mkdir(parents=True, exist_ok=True)

# 1. IPOScoop Scraper
iposcoop_scraper = '''#!/usr/bin/env python3
"""
IPOScoop Calendar Scraper - Gets all IPO data
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re

class IPOScoopScraper:
    def __init__(self):
        self.base_url = "https://www.iposcoop.com/ipo-calendar/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def scrape_calendar(self):
        """Scrape complete IPO calendar with all fields"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, headers=self.headers) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    ipos = []
                    
                    # Find the calendar table
                    tables = soup.find_all('table', {'class': 'ipo-calendar'}) or soup.find_all('table')
                    
                    for table in tables:
                        rows = table.find_all('tr')[1:]  # Skip header
                        
                        for row in rows:
                            cells = row.find_all('td')
                            if len(cells) >= 4:
                                ipo = {
                                    'company_name': cells[0].text.strip(),
                                    'ticker': cells[1].text.strip().upper(),
                                    'managers': cells[2].text.strip() if len(cells) > 2 else '',
                                    'shares': cells[3].text.strip() if len(cells) > 3 else '',
                                    'price_range': cells[4].text.strip() if len(cells) > 4 else '',
                                    'expected_date': cells[5].text.strip() if len(cells) > 5 else 'TBD',
                                    'status': 'pending',
                                    'scraped_at': datetime.now().isoformat()
                                }
                                
                                # Clean price range
                                if ipo['price_range']:
                                    match = re.search(r'\\$([\\d.]+)\\s*-\\s*\\$([\\d.]+)', ipo['price_range'])
                                    if match:
                                        ipo['price_low'] = float(match.group(1))
                                        ipo['price_high'] = float(match.group(2))
                                
                                if ipo['ticker']:  # Only add if we have a ticker
                                    ipos.append(ipo)
                    
                    return ipos
                    
            except Exception as e:
                print(f"Error scraping IPOScoop: {e}")
                return []

    async def get_ipo_by_ticker(self, ticker):
        """Get specific IPO data"""
        ipos = await self.scrape_calendar()
        for ipo in ipos:
            if ipo['ticker'] == ticker.upper():
                return ipo
        return None
'''

# 2. CIK Resolver
cik_resolver = '''#!/usr/bin/env python3
"""
SEC CIK Resolver - Maps company names to CIK numbers
"""

import aiohttp
import asyncio
import json
from fuzzywuzzy import fuzz
from pathlib import Path

class CIKResolver:
    def __init__(self):
        self.cik_cache_path = Path("data/cik_mappings.json")
        self.sec_api_base = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'Hedge Intelligence (admin@hedgeintel.com)'
        }
        self.load_cache()
    
    def load_cache(self):
        """Load cached CIK mappings"""
        if self.cik_cache_path.exists():
            with open(self.cik_cache_path, 'r') as f:
                self.cache = json.load(f)
        else:
            self.cache = {}
            self.cik_cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save_cache(self):
        """Save CIK mappings"""
        with open(self.cik_cache_path, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    async def resolve_cik(self, company_name, ticker=None):
        """Find CIK for company name"""
        # Check cache first
        cache_key = f"{ticker}:{company_name}" if ticker else company_name
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        async with aiohttp.ClientSession() as session:
            try:
                # Get company tickers JSON
                url = f"{self.sec_api_base}/files/company_tickers.json"
                async with session.get(url, headers=self.headers) as response:
                    data = await response.json()
                    
                    best_match = None
                    best_score = 0
                    
                    # Search through all companies
                    for item in data.values():
                        # Try exact ticker match first
                        if ticker and item.get('ticker', '').upper() == ticker.upper():
                            cik = str(item['cik_str']).zfill(10)
                            self.cache[cache_key] = {
                                'cik': cik,
                                'name': item['title'],
                                'ticker': item['ticker'],
                                'confidence': 100
                            }
                            self.save_cache()
                            return self.cache[cache_key]
                        
                        # Fuzzy match company name
                        score = fuzz.ratio(company_name.lower(), item['title'].lower())
                        if score > best_score:
                            best_score = score
                            best_match = item
                    
                    # Return best match if good enough
                    if best_match and best_score > 80:
                        cik = str(best_match['cik_str']).zfill(10)
                        result = {
                            'cik': cik,
                            'name': best_match['title'],
                            'ticker': best_match.get('ticker', ''),
                            'confidence': best_score
                        }
                        self.cache[cache_key] = result
                        self.save_cache()
                        return result
                    
                    return None
                    
            except Exception as e:
                print(f"Error resolving CIK: {e}")
                return None
'''

# 3. SEC Document Scraper
sec_scraper = '''#!/usr/bin/env python3
"""
SEC EDGAR Document Scraper - Downloads all filings
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from pathlib import Path
import json
from datetime import datetime

class SECDocumentScraper:
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'Hedge Intelligence (admin@hedgeintel.com)',
            'Accept': 'text/html,application/xhtml+xml'
        }
        self.data_dir = Path("data/sec_documents")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_company_filings(self, cik):
        """Get all filings for a CIK"""
        cik = str(cik).zfill(10)
        url = f"{self.base_url}/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=&count=100"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    filings = []
                    
                    # Find filing table
                    table = soup.find('table', class_='tableFile2')
                    if not table:
                        return []
                    
                    rows = table.find_all('tr')[1:]  # Skip header
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 4:
                            filing_type = cells[0].text.strip()
                            
                            # We want these types
                            if filing_type in ['S-1', 'S-1/A', '424B4', '8-K', '8-A', 'EFFECT']:
                                doc_link = cells[1].find('a', id='documentsbutton')
                                if doc_link:
                                    filing = {
                                        'type': filing_type,
                                        'date': cells[3].text.strip(),
                                        'description': cells[2].text.strip(),
                                        'url': self.base_url + doc_link['href'],
                                        'cik': cik
                                    }
                                    filings.append(filing)
                    
                    return filings
                    
            except Exception as e:
                print(f"Error getting filings: {e}")
                return []
    
    async def download_filing(self, filing, ticker):
        """Download specific filing in HTML format"""
        ticker_dir = self.data_dir / ticker.upper()
        ticker_dir.mkdir(exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            try:
                # Get filing detail page
                async with session.get(filing['url'], headers=self.headers) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find HTML document link
                    doc_table = soup.find('table', class_='tableFile')
                    if doc_table:
                        for row in doc_table.find_all('tr')[1:]:
                            cells = row.find_all('td')
                            if len(cells) >= 3:
                                doc_type = cells[1].text.strip()
                                if 'html' in doc_type.lower() or cells[2].text.strip() == filing['type']:
                                    link = cells[2].find('a')
                                    if link:
                                        doc_url = self.base_url + link['href']
                                        
                                        # Download the document
                                        async with session.get(doc_url, headers=self.headers) as doc_response:
                                            content = await doc_response.text()
                                            
                                            # Save the document
                                            filename = f"{filing['type']}_{filing['date']}.html"
                                            filepath = ticker_dir / filename
                                            
                                            with open(filepath, 'w', encoding='utf-8') as f:
                                                f.write(content)
                                            
                                            print(f"✅ Downloaded {ticker}/{filename}")
                                            
                                            return {
                                                'success': True,
                                                'path': str(filepath),
                                                'type': filing['type'],
                                                'date': filing['date']
                                            }
                
                return {'success': False, 'error': 'No HTML document found'}
                
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    async def scan_and_download_all(self, ticker, cik):
        """Download all relevant documents for a ticker"""
        print(f"🔍 Scanning SEC for {ticker} (CIK: {cik})")
        
        # Get all filings
        filings = await self.get_company_filings(cik)
        
        if not filings:
            return {'success': False, 'error': 'No filings found'}
        
        # Download each filing
        results = []
        for filing in filings:
            result = await self.download_filing(filing, ticker)
            results.append(result)
            
            # Be nice to SEC servers
            await asyncio.sleep(0.5)
        
        return {
            'success': True,
            'ticker': ticker,
            'cik': cik,
            'filings_found': len(filings),
            'downloaded': sum(1 for r in results if r.get('success')),
            'results': results
        }
'''

# 4. IPO Pipeline Manager
pipeline_manager = '''#!/usr/bin/env python3
"""
IPO Pipeline Manager - Orchestrates the complete flow
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from scrapers.sec.iposcoop_scraper import IPOScoopScraper
from scrapers.sec.cik_resolver import CIKResolver
from scrapers.sec.sec_scraper import SECDocumentScraper

class IPOPipelineManager:
    def __init__(self):
        self.iposcoop = IPOScoopScraper()
        self.cik_resolver = CIKResolver()
        self.sec_scraper = SECDocumentScraper()
        
        self.pipeline_dir = Path("data/ipo_pipeline")
        self.pipeline_dir.mkdir(parents=True, exist_ok=True)
        
        self.pending_file = self.pipeline_dir / "pending.json"
        self.active_file = self.pipeline_dir / "active.json"
        self.completed_file = self.pipeline_dir / "completed.json"
    
    def load_pipeline_data(self):
        """Load pipeline status"""
        data = {
            'pending': [],
            'active': [],
            'completed': []
        }
        
        for key, file in [('pending', self.pending_file),
                         ('active', self.active_file),
                         ('completed', self.completed_file)]:
            if file.exists():
                with open(file, 'r') as f:
                    data[key] = json.load(f)
        
        return data
    
    def save_pipeline_data(self, data):
        """Save pipeline status"""
        for key, file in [('pending', self.pending_file),
                         ('active', self.active_file),
                         ('completed', self.completed_file)]:
            with open(file, 'w') as f:
                json.dump(data.get(key, []), f, indent=2)
    
    async def scan_new_ipos(self):
        """Scan for new IPOs and add to pipeline"""
        print("📊 Scanning IPOScoop for new IPOs...")
        
        # Get current IPOs
        ipos = await self.iposcoop.scrape_calendar()
        
        if not ipos:
            print("❌ No IPOs found")
            return
        
        # Load existing data
        pipeline = self.load_pipeline_data()
        existing_tickers = set()
        
        for category in ['pending', 'active', 'completed']:
            existing_tickers.update(ipo['ticker'] for ipo in pipeline[category])
        
        # Add new IPOs
        new_count = 0
        for ipo in ipos:
            if ipo['ticker'] not in existing_tickers:
                ipo['added_date'] = datetime.now().isoformat()
                ipo['status'] = 'pending_cik'
                pipeline['pending'].append(ipo)
                new_count += 1
                print(f"✅ New IPO: {ipo['ticker']} - {ipo['company_name']}")
        
        # Save updated pipeline
        self.save_pipeline_data(pipeline)
        
        print(f"📊 Found {new_count} new IPOs")
        return new_count
    
    async def process_pending_ipos(self):
        """Process pending IPOs - resolve CIKs and download documents"""
        pipeline = self.load_pipeline_data()
        
        if not pipeline['pending']:
            print("No pending IPOs to process")
            return
        
        print(f"🔄 Processing {len(pipeline['pending'])} pending IPOs...")
        
        for ipo in pipeline['pending'][:]:  # Process copy to allow removal
            ticker = ipo['ticker']
            company = ipo['company_name']
            
            print(f"\\n📍 Processing {ticker} - {company}")
            
            # Step 1: Resolve CIK
            if ipo['status'] == 'pending_cik':
                cik_data = await self.cik_resolver.get_cik(company, ticker)
                
                if cik_data:
                    ipo['cik'] = cik_data['cik']
                    ipo['sec_name'] = cik_data['name']
                    ipo['cik_confidence'] = cik_data['confidence']
                    ipo['status'] = 'cik_resolved'
                    print(f"  ✅ Found CIK: {cik_data['cik']} (confidence: {cik_data['confidence']}%)")
                else:
                    ipo['status'] = 'cik_not_found'
                    print(f"  ❌ Could not find CIK")
                    continue
            
            # Step 2: Download documents if CIK resolved
            if ipo.get('cik') and ipo['status'] == 'cik_resolved':
                result = await self.sec_scraper.scan_and_download_all(ticker, ipo['cik'])
                
                if result['success']:
                    ipo['status'] = 'documents_downloaded'
                    ipo['documents_count'] = result['downloaded']
                    ipo['last_scan'] = datetime.now().isoformat()
                    
                    # Move to active
                    pipeline['pending'].remove(ipo)
                    pipeline['active'].append(ipo)
                    print(f"  ✅ Downloaded {result['downloaded']} documents")
                else:
                    ipo['status'] = 'download_failed'
                    print(f"  ❌ Download failed: {result.get('error')}")
            
            # Be nice to servers
            await asyncio.sleep(1)
        
        # Save updated pipeline
        self.save_pipeline_data(pipeline)
    
    async def check_for_updates(self):
        """Check active IPOs for new filings"""
        pipeline = self.load_pipeline_data()
        
        for ipo in pipeline['active']:
            if ipo.get('cik'):
                # Check for new filings
                current_filings = await self.sec_scraper.get_company_filings(ipo['cik'])
                
                # Compare with what we have
                # ... implement comparison logic ...
                
                await asyncio.sleep(1)
    
    def get_admin_summary(self):
        """Get summary for admin dashboard"""
        pipeline = self.load_pipeline_data()
        
        summary = {
            'pending': len(pipeline['pending']),
            'active': len(pipeline['active']),
            'completed': len(pipeline['completed']),
            'needs_attention': [],
            'recent_activity': []
        }
        
        # Find issues
        for ipo in pipeline['pending']:
            if ipo['status'] == 'cik_not_found':
                summary['needs_attention'].append({
                    'ticker': ipo['ticker'],
                    'issue': 'Cannot find CIK',
                    'action': 'Manual CIK search needed'
                })
        
        return summary

# Main execution
async def main():
    manager = IPOPipelineManager()
    
    # Scan for new IPOs
    await manager.scan_new_ipos()
    
    # Process pending
    await manager.process_pending_ipos()
    
    # Get summary
    summary = manager.get_admin_summary()
    print(f"\\n📊 Pipeline Summary: {json.dumps(summary, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
'''

# Save all files
files = {
    "scrapers/sec/iposcoop_scraper.py": iposcoop_scraper,
    "scrapers/sec/cik_resolver.py": cik_resolver,
    "scrapers/sec/sec_scraper.py": sec_scraper,
    "scrapers/sec/pipeline_manager.py": pipeline_manager
}

for filepath, content in files.items():
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created {filepath}")

# Create __init__ files
for dir in ["scrapers/sec"]:
    init_file = Path(dir) / "__init__.py"
    init_file.touch()

print("\n✅ SEC scraper system created!")
print("\nNext: Create the updated admin dashboard to use this system")