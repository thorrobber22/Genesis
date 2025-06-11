#!/usr/bin/env python3
"""
SEC-Compliant Document Scraper - Using direct API endpoints
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from pathlib import Path
import json
from datetime import datetime
import re
import time
import logging
from typing import Dict, List, Optional
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SECCompliantScraper:
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.data_sec_url = "https://data.sec.gov"
        
        # SEC REQUIRES proper identification with email
        self.headers = {
            'User-Agent': 'Mozilla/5.0 HedgeIntelligence/1.0 (admin@hedgeintelligence.ai)',
            'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        self.data_dir = Path("data/sec_documents")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # SEC rate limit: Be conservative
        self.rate_limit_delay = 2.0  # More reasonable 2 seconds
        self.last_request_time = 0
        
        # Document types to download (in priority order)
        self.priority_forms = ['S-1', 'S-1/A', '10-K', '10-Q', '8-K', 'DEF 14A', '424B', 'S-3', 'S-4', 'S-8']
        self.all_forms = self.priority_forms + ['20-F', '11-K', '3', '4', '5', 'SC 13G', 'SC 13D', 'F-1', 'EFFECT']
        
    async def wait_for_rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last
            logger.info(f"⏳ Rate limiting: waiting {wait_time:.1f} seconds...")
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def fetch_with_retry(self, session: aiohttp.ClientSession, url: str, max_retries: int = 3) -> Optional[str]:
        """Fetch URL with retry logic"""
        for attempt in range(max_retries):
            try:
                await self.wait_for_rate_limit()
                
                # Update host header based on URL
                headers = self.headers.copy()
                if 'data.sec.gov' in url:
                    headers['Host'] = 'data.sec.gov'
                else:
                    headers['Host'] = 'www.sec.gov'
                
                logger.debug(f"Fetching: {url}")
                
                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    if response.status == 200:
                        content = await response.text()
                        return content
                    elif response.status == 403:
                        logger.warning(f"403 Forbidden - Waiting {10 * (attempt + 1)} seconds...")
                        await asyncio.sleep(10 * (attempt + 1))
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        await asyncio.sleep(5)
                        
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                await asyncio.sleep(5)
        
        return None
    
    def is_valid_document(self, content: str, filename: str) -> bool:
        """Check if the document is valid and not junk"""
        if not content or len(content) < 1000:
            return False
            
        content_lower = content.lower()
        
        # Skip error pages
        error_indicators = [
            'this page contains the following errors',
            'companysearch',
            '404 not found',
            'access denied'
        ]
        
        if any(indicator in content_lower for indicator in error_indicators):
            return False
        
        # Must contain SEC document indicators
        required_indicators = [
            'securities and exchange commission',
            'united states',
            'form',
            'washington, d.c.'
        ]
        
        return any(indicator in content_lower for indicator in required_indicators)
    
    async def download_document(self, session: aiohttp.ClientSession, url: str, 
                              form_type: str, filing_date: str, doc_description: str,
                              ticker_dir: Path, company_name: str) -> bool:
        """Download a single document"""
        try:
            content = await self.fetch_with_retry(session, url)
            
            if content and self.is_valid_document(content, doc_description):
                # Generate filename
                date_str = filing_date.replace('-', '')
                doc_hash = hashlib.md5(url.encode()).hexdigest()[:6]
                
                # Clean description for filename
                desc_clean = re.sub(r'[^a-zA-Z0-9\s]', '', doc_description)[:50]
                desc_clean = re.sub(r'\s+', '_', desc_clean.strip())
                
                filename = f"{form_type}_{date_str}_{desc_clean}_{doc_hash}.html"
                filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
                
                filepath = ticker_dir / filename
                
                # Save document
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Save metadata
                metadata = {
                    'form_type': form_type,
                    'filing_date': filing_date,
                    'description': doc_description,
                    'download_date': datetime.now().isoformat(),
                    'source_url': url,
                    'company_name': company_name
                }
                
                metadata_path = filepath.with_suffix('.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"   ✅ Downloaded: {filename} ({len(content)//1024} KB)")
                return True
            else:
                logger.info(f"   ⚠️  Skipped invalid document")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Error downloading document: {e}")
            return False
    
    async def scan_and_download_everything(self, ticker: str, cik: str) -> Dict:
        """Main download function using SEC API"""
        ticker = ticker.upper()
        cik_padded = str(cik).zfill(10)  # Pad with zeros for API
        cik_clean = str(cik).lstrip('0')  # Clean for display
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🔍 SEC-Compliant Download for {ticker} (CIK: {cik_clean})")
        logger.info(f"{'='*60}")
        logger.info("⏳ Using 2-second rate limiting")
        
        # Create ticker directory
        ticker_dir = self.data_dir / ticker
        ticker_dir.mkdir(exist_ok=True)
        
        # Track downloads
        downloaded_forms = {}
        total_files = 0
        
        # Create session
        timeout = aiohttp.ClientTimeout(total=60)
        connector = aiohttp.TCPConnector(limit=1, force_close=True)
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            # First, get company info and recent filings from submissions endpoint
            submissions_url = f"{self.data_sec_url}/submissions/CIK{cik_padded}.json"
            
            logger.info(f"\n📡 Fetching company data from: {submissions_url}")
            
            submissions_json = await self.fetch_with_retry(session, submissions_url)
            
            if not submissions_json:
                logger.error("Failed to fetch company data")
                return {
                    'success': False,
                    'error': 'Could not access SEC data',
                    'ticker': ticker,
                    'cik': cik_clean
                }
            
            try:
                data = json.loads(submissions_json)
                
                # Extract company info
                company_name = data.get('name', ticker)
                sic_desc = data.get('sicDescription', 'Unknown')
                
                # Save company info
                company_info = {
                    'ticker': ticker,
                    'cik': cik_clean,
                    'name': company_name,
                    'industry': sic_desc,
                    'last_updated': datetime.now().isoformat()
                }
                
                with open(ticker_dir / 'company_info.json', 'w') as f:
                    json.dump(company_info, f, indent=2)
                
                logger.info(f"📊 Company: {company_name}")
                logger.info(f"🏭 Industry: {sic_desc}")
                
                # Get recent filings
                recent_filings = data.get('filings', {}).get('recent', {})
                
                if not recent_filings:
                    logger.error("No recent filings found")
                    return {
                        'success': False,
                        'error': 'No filings found',
                        'ticker': ticker,
                        'cik': cik_clean
                    }
                
                # Extract filing data
                forms = recent_filings.get('form', [])
                filing_dates = recent_filings.get('filingDate', [])
                accession_numbers = recent_filings.get('accessionNumber', [])
                primary_documents = recent_filings.get('primaryDocument', [])
                primary_doc_descriptions = recent_filings.get('primaryDocDescription', [])
                
                logger.info(f"\n📄 Found {len(forms)} total filings")
                
                # Process each filing
                for i in range(min(len(forms), 100)):  # Limit to 100 most recent
                    form_type = forms[i]
                    
                    # Only process forms we want
                    if form_type not in self.all_forms:
                        continue
                    
                    filing_date = filing_dates[i] if i < len(filing_dates) else 'Unknown'
                    accession_no = accession_numbers[i] if i < len(accession_numbers) else None
                    primary_doc = primary_documents[i] if i < len(primary_documents) else None
                    doc_description = primary_doc_descriptions[i] if i < len(primary_doc_descriptions) else form_type
                    
                    if not accession_no or not primary_doc:
                        continue
                    
                    logger.info(f"\n[{i+1}] Processing {form_type} filed on {filing_date}")
                    logger.info(f"   Description: {doc_description}")
                    
                    # Construct document URL
                    accession_no_clean = accession_no.replace('-', '')
                    doc_url = f"{self.base_url}/Archives/edgar/data/{cik_clean}/{accession_no_clean}/{primary_doc}"
                    
                    # Download the document
                    success = await self.download_document(
                        session, doc_url, form_type, filing_date, 
                        doc_description, ticker_dir, company_name
                    )
                    
                    if success:
                        downloaded_forms[form_type] = downloaded_forms.get(form_type, 0) + 1
                        total_files += 1
                    
                    # For S-1 and amendments, also try to get exhibits
                    if form_type in ['S-1', 'S-1/A'] and accession_no:
                        # Get the filing detail page
                        filing_detail_url = f"{self.base_url}/Archives/edgar/data/{cik_clean}/{accession_no_clean}/{accession_no}-index.htm"
                        
                        detail_content = await self.fetch_with_retry(session, filing_detail_url)
                        if detail_content:
                            soup = BeautifulSoup(detail_content, 'html.parser')
                            
                            # Look for important exhibits
                            table = soup.find('table', class_='tableFile')
                            if table:
                                rows = table.find_all('tr')[1:]  # Skip header
                                
                                for row in rows[:5]:  # Limit exhibits
                                    cells = row.find_all('td')
                                    if len(cells) >= 3:
                                        doc_desc = cells[1].text.strip()
                                        
                                        # Look for important exhibits
                                        important_keywords = ['underwriting', 'lock-up', 'lockup', 'share', 'purchase']
                                        if any(kw in doc_desc.lower() for kw in important_keywords):
                                            doc_link = row.find('a', href=True)
                                            if doc_link:
                                                exhibit_url = f"{self.base_url}{doc_link['href']}"
                                                
                                                await self.download_document(
                                                    session, exhibit_url, f"{form_type}_EXHIBIT",
                                                    filing_date, doc_desc, ticker_dir, company_name
                                                )
                
                # Save summary
                summary = {
                    'ticker': ticker,
                    'cik': cik_clean,
                    'company_name': company_name,
                    'industry': sic_desc,
                    'last_scan': datetime.now().isoformat(),
                    'total_files': total_files,
                    'forms_downloaded': downloaded_forms,
                    'scan_version': '9.0-api-direct'
                }
                
                with open(ticker_dir / "scan_summary.json", 'w') as f:
                    json.dump(summary, f, indent=2)
                
                logger.info(f"\n{'='*60}")
                logger.info(f"✅ Download Complete!")
                logger.info(f"📊 Total valid files: {total_files}")
                logger.info(f"📁 Forms downloaded: {downloaded_forms}")
                logger.info(f"{'='*60}")
                
                return {
                    'success': True,
                    'ticker': ticker,
                    'cik': cik_clean,
                    'total_files': total_files,
                    'forms_downloaded': downloaded_forms,
                    'company_name': company_name,
                    'summary': summary
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse SEC data: {e}")
                return {
                    'success': False,
                    'error': 'Invalid data format from SEC',
                    'ticker': ticker,
                    'cik': cik_clean
                }

# Also expose as EnhancedSECDocumentScraper for compatibility
EnhancedSECDocumentScraper = SECCompliantScraper

# Test function
async def test_crcl():
    """Test with Circle (CRCL)"""
    scraper = SECCompliantScraper()
    
    logger.info("🧪 Testing Circle (CRCL) - IPO Company")
    result = await scraper.scan_and_download_everything("CRCL", "0001876042")
    
    if result['success']:
        # Show what types of documents we found
        forms = result.get('forms_downloaded', {})
        if 'S-1' in forms or 'S-1/A' in forms:
            logger.info("\n🎯 IPO Documents Found!")
            logger.info("This company has S-1 registration statements")
        
        # Check the downloaded files
        crcl_dir = Path("data/sec_documents/CRCL")
        if crcl_dir.exists():
            s1_files = list(crcl_dir.glob("S-1*.html"))
            if s1_files:
                logger.info(f"\n📋 S-1 Documents ({len(s1_files)} files):")
                for f in s1_files[:5]:
                    logger.info(f"  - {f.name}")

if __name__ == "__main__":
    asyncio.run(test_crcl())