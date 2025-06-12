"""
SEC Document Scraper
Downloads SEC filings following the proper EDGAR flow
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SECScraper:
    """Scrapes SEC documents from EDGAR"""
    
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'HedgeIntelligence/1.0 (contact@hedgeintel.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.data_dir = Path("data/sec_documents")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def download_company_filings(self, company_name: str, ticker: str, cik: str, 
                               filing_types: List[str] = None, max_filings: int = 10) -> int:
        """Download SEC filings for a company"""
        if filing_types is None:
            filing_types = ['10-K', '10-Q', '8-K', 'DEF 14A', 'S-1', '424B4', '424B5']
            
        logger.info(f"Downloading filings for {company_name} ({ticker})")
        
        company_dir = self.data_dir / ticker
        company_dir.mkdir(exist_ok=True)
        
        try:
            filings_url = f"{self.base_url}/cgi-bin/browse-edgar"
            params = {
                'action': 'getcompany',
                'CIK': cik.lstrip('0'),
                'type': '',
                'dateb': '',
                'owner': 'exclude',
                'count': '100'
            }
            
            response = requests.get(filings_url, params=params, headers=self.headers, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Failed to get filings for {ticker}: HTTP {response.status_code}")
                return 0
                
            soup = BeautifulSoup(response.text, 'html.parser')
            filings_table = soup.find('table', {'class': 'tableFile2'})
            
            if not filings_table:
                logger.error(f"No filings table found for {ticker}")
                return 0
                
            rows = filings_table.find_all('tr')[1:]
            downloaded = 0
            
            for row in rows:
                if downloaded >= max_filings:
                    break
                    
                cells = row.find_all('td')
                
                if len(cells) >= 4:
                    filing_type = cells[0].text.strip()
                    
                    if filing_type in filing_types:
                        doc_cell = cells[1]
                        doc_link = None
                        
                        for link in doc_cell.find_all('a'):
                            href = link.get('href', '')
                            if 'Archives/edgar/data' in href:
                                doc_link = link
                                break
                                
                        if doc_link:
                            filing_detail_url = self.base_url + doc_link['href']
                            filing_date = cells[3].text.strip() if len(cells) > 3 else ''
                            
                            if self._download_filing(filing_detail_url, filing_type, filing_date, company_dir, ticker):
                                downloaded += 1
                                logger.info(f"Downloaded {filing_type} for {ticker}")
                                time.sleep(0.5)
                                
            logger.info(f"Downloaded {downloaded} documents for {ticker}")
            return downloaded
            
        except Exception as e:
            logger.error(f"Error downloading filings for {ticker}: {str(e)}")
            return 0
            
    def _download_filing(self, filing_url: str, filing_type: str, filing_date: str, 
                        save_dir: Path, ticker: str) -> bool:
        """Download the actual filing document"""
        try:
            response = requests.get(filing_url, headers=self.headers, timeout=30)
            
            if response.status_code != 200:
                return False
                
            soup = BeautifulSoup(response.text, 'html.parser')
            doc_table = soup.find('table', {'class': 'tableFile'})
            
            if not doc_table:
                return False
                
            for row in doc_table.find_all('tr')[1:]:
                cells = row.find_all('td')
                
                if len(cells) >= 4:
                    sequence = cells[0].text.strip()
                    description = cells[1].text.strip()
                    doc_link_cell = cells[2]
                    
                    is_main_doc = (
                        sequence == "1" or
                        filing_type in description or
                        filing_type.replace(' ', '') in description.replace(' ', '') or
                        'Complete submission' in description
                    )
                    
                    if is_main_doc:
                        doc_link = doc_link_cell.find('a')
                        
                        if doc_link:
                            doc_url = self.base_url + doc_link['href']
                            doc_response = requests.get(doc_url, headers=self.headers, timeout=60)
                            
                            if doc_response.status_code == 200:
                                if filing_date:
                                    try:
                                        date_obj = datetime.strptime(filing_date, '%Y-%m-%d')
                                        date_str = date_obj.strftime('%Y%m%d')
                                    except:
                                        date_str = filing_date.replace('-', '')
                                else:
                                    date_str = datetime.now().strftime('%Y%m%d')
                                    
                                filename = f"{filing_type.replace(' ', '')}_{date_str}_{ticker}.html"
                                file_path = save_dir / filename
                                
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(doc_response.text)
                                    
                                return True
                                
        except Exception as e:
            logger.error(f"Error downloading filing: {str(e)}")
            
        return False
        
    def download_multiple_companies(self, companies: List[Dict[str, str]], 
                                  filing_types: List[str] = None,
                                  max_per_company: int = 10) -> Dict[str, int]:
        """Download filings for multiple companies"""
        results = {}
        
        for company in companies:
            downloaded = self.download_company_filings(
                company_name=company['name'],
                ticker=company['ticker'],
                cik=company['cik'],
                filing_types=filing_types,
                max_filings=max_per_company
            )
            results[company['ticker']] = downloaded
            time.sleep(1)
            
        return results
