"""
EDGAR Monitor - Real SEC filing monitoring
"""

import aiohttp
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import re
import asyncio

logger = logging.getLogger(__name__)

class EDGARMonitor:
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'Hedge Intelligence Bot (admin@hedgeintel.com)',
            'Accept': 'application/xml, text/xml, text/html'
        }
        self.rate_limit_delay = 0.1  # SEC rate limit
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def get_recent_filings(self, form_types: List[str], limit: int = 20) -> List[Dict]:
        """Get recent filings from SEC EDGAR RSS feed"""
        filings = []
        
        try:
            for form_type in form_types:
                url = f"{self.base_url}/cgi-bin/browse-edgar?action=getcurrent&type={form_type}&output=atom"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 200:
                            content = await response.text()
                            form_filings = self._parse_rss_feed(content, form_type)
                            filings.extend(form_filings)
                            
                            await asyncio.sleep(self.rate_limit_delay)
            
            filings.sort(key=lambda x: x.get('filed_at', ''), reverse=True)
            
            for filing in filings[:limit]:
                if not filing.get('ticker'):
                    filing['ticker'] = await self._extract_ticker_from_filing(filing)
            
            return filings[:limit]
            
        except Exception as e:
            logger.error(f"EDGAR monitor error: {e}")
            return []
    
    def _parse_rss_feed(self, xml_content: str, form_type: str) -> List[Dict]:
        """Parse SEC RSS/Atom feed"""
        filings = []
        
        try:
            xml_content = re.sub(r'xmlns="[^"]+"', '', xml_content)
            root = ET.fromstring(xml_content)
            
            for entry in root.findall('.//entry'):
                try:
                    title = entry.find('title')
                    link = entry.find('link')
                    updated = entry.find('updated')
                    
                    if title is not None and link is not None:
                        title_text = title.text or ''
                        
                        company_match = re.search(r'-\s*(.+?)\s*\(', title_text)
                        company = company_match.group(1) if company_match else 'Unknown'
                        
                        cik_match = re.search(r'\((\d+)\)', title_text)
                        cik = cik_match.group(1) if cik_match else ''
                        
                        filing = {
                            'company': company.strip(),
                            'form_type': form_type,
                            'cik': cik,
                            'filing_link': link.get('href', ''),
                            'filed_at': updated.text if updated is not None else datetime.now().isoformat(),
                            'accession_number': self._extract_accession_number(link.get('href', ''))
                        }
                        
                        filings.append(filing)
                        
                except Exception as e:
                    logger.debug(f"Error parsing entry: {e}")
                    
        except Exception as e:
            logger.error(f"RSS parse error: {e}")
        
        return filings
    
    async def _extract_ticker_from_filing(self, filing: Dict) -> Optional[str]:
        """Try to extract ticker from filing page"""
        # Implementation would fetch filing page and extract ticker
        # For now, return None to avoid hitting SEC too hard
        return None
    
    def _extract_accession_number(self, url: str) -> str:
        """Extract accession number from URL"""
        match = re.search(r'/(\d{10}-\d{2}-\d{6})', url)
        return match.group(1) if match else ''