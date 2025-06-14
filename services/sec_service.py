"""
<<<<<<< HEAD
SEC Service - Following Manual CIK Lookup Flow
Date: 2025-06-14 00:39:40 UTC
Author: thorrobber22
"""
import requests
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup

class SECService:
    """SEC service following exact manual lookup flow"""
    
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        self.rate_limit_delay = 0.1
        
    def search_cik(self, company_name: str) -> Optional[str]:
        """Search CIK using variations of company name"""
        print(f"  🔍 Searching CIK for: {company_name}")
        
        # Try different variations of the name
        name_variations = [
            company_name,  # Full name
            company_name.replace(" Holdings", ""),
            company_name.replace(" Limited", ""),
            company_name.replace(" Ltd.", ""),
            company_name.replace(" Corp.", ""),
            company_name.replace(" Corporation", ""),
            company_name.replace(" Inc.", ""),
            company_name.replace(" LLC", ""),
            company_name.replace("/Cayman", ""),
            company_name.replace(" Acquisition", ""),
            company_name.split()[0] if len(company_name.split()) > 1 else company_name,  # First word only
        ]
        
        # Remove duplicates while preserving order
        name_variations = list(dict.fromkeys([v.strip() for v in name_variations if v.strip()]))
        
        for variation in name_variations:
            print(f"    → Trying: {variation}")
            cik = self._search_cik_variation(variation)
            if cik:
                return cik
            time.sleep(self.rate_limit_delay)
        
        print(f"    ⚠️ No CIK found after trying {len(name_variations)} variations")
        return None
    
    def _search_cik_variation(self, search_term: str) -> Optional[str]:
        """Search for a specific name variation"""
        try:
            # Method 1: Use the CIK lookup JSON endpoint
            lookup_url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(lookup_url, headers=self.headers)
            
            if response.status_code == 200:
                companies = response.json()
                search_lower = search_term.lower()
                
                # Search through all companies
                for _, company in companies.items():
                    company_title = company.get('title', '').lower()
                    if search_lower in company_title or company_title in search_lower:
                        cik = str(company['cik_str']).zfill(10)
                        print(f"      ✅ Found CIK: {cik} ({company['title']})")
                        return cik
            
            # Method 2: Try the autocomplete endpoint
            time.sleep(self.rate_limit_delay)
            autocomplete_url = f"https://www.sec.gov/cgi-bin/cik_lookup"
            params = {
                'company': search_term
            }
            
            response = requests.get(autocomplete_url, params=params, headers=self.headers)
            if response.status_code == 200:
                # Parse the response (it's HTML)
                soup = BeautifulSoup(response.text, 'html.parser')
                pre_tag = soup.find('pre')
                if pre_tag:
                    lines = pre_tag.text.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            # Format: COMPANY NAME:CIK:FORM COUNT
                            parts = line.split(':')
                            if len(parts) >= 2:
                                cik = parts[1].strip().zfill(10)
                                print(f"      ✅ Found CIK: {cik} (via lookup)")
                                return cik
            
        except Exception as e:
            print(f"      ❌ Error in search: {e}")
        
        return None
    
    def get_edgar_filings(self, cik: str) -> Tuple[List[Dict], str]:
        """Get filings from EDGAR browse page"""
        try:
            print(f"  📄 Getting filings from EDGAR for CIK: {cik}")
            
            # Browse URL like you showed
            browse_url = f"{self.base_url}/edgar/browse/"
            params = {
                'CIK': cik.lstrip('0')  # Remove leading zeros
            }
            
            time.sleep(self.rate_limit_delay)
            response = requests.get(browse_url, params=params, headers=self.headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Get company name from page
                company_info = soup.find('span', {'class': 'companyName'})
                if not company_info:
                    company_info = soup.find('div', {'class': 'companyInfo'})
                
                company_name = "Unknown"
                if company_info:
                    company_name = company_info.text.strip().split('\n')[0]
                    print(f"    📌 Company: {company_name}")
                
                # Look for filings table
                filings_table = soup.find('table', {'class': 'tableFile2'})
                if not filings_table:
                    # Try data endpoint
                    return self._get_filings_from_api(cik)
                
                filings = []
                rows = filings_table.find_all('tr')[1:]  # Skip header
                
                for row in rows[:20]:  # Get latest 20
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        # Extract filing info
                        form_type = cells[0].text.strip()
                        
                        # Get document links
                        doc_links = cells[1].find_all('a')
                        doc_href = doc_links[0]['href'] if doc_links else ''
                        
                        # Full URL
                        if doc_href and not doc_href.startswith('http'):
                            doc_href = f"{self.base_url}{doc_href}"
                        
                        filing = {
                            'form_type': form_type,
                            'form_description': cells[1].text.strip(),
                            'filing_date': cells[3].text.strip(),
                            'document_url': doc_href,
                            'accession_number': self._extract_accession(doc_href)
                        }
                        filings.append(filing)
                
                if filings:
                    print(f"    ✅ Found {len(filings)} filings")
                    for f in filings[:3]:
                        print(f"      - {f['form_type']}: {f['form_description']} ({f['filing_date']})")
                
                return filings, company_name
            
        except Exception as e:
            print(f"    ❌ Error getting filings: {e}")
        
        return [], "Unknown"
    
    def _get_filings_from_api(self, cik: str) -> Tuple[List[Dict], str]:
        """Fallback to API endpoint for filings"""
        try:
            api_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            time.sleep(self.rate_limit_delay)
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                company_name = data.get('name', 'Unknown')
                
                filings = []
                recent = data.get('filings', {}).get('recent', {})
                
                if recent:
                    forms = recent.get('form', [])
                    dates = recent.get('filingDate', [])
                    accessions = recent.get('accessionNumber', [])
                    documents = recent.get('primaryDocument', [])
                    
                    for i in range(min(len(forms), 20)):
                        accession = accessions[i].replace('-', '')
                        doc_url = f"{self.base_url}/Archives/edgar/data/{cik.lstrip('0')}/{accession}/{documents[i]}"
                        
                        filing = {
                            'form_type': forms[i],
                            'form_description': documents[i],
                            'filing_date': dates[i],
                            'document_url': doc_url,
                            'accession_number': accession
                        }
                        filings.append(filing)
                
                return filings, company_name
                
        except Exception as e:
            print(f"    ❌ API error: {e}")
        
        return [], "Unknown"
    
    def _extract_accession(self, url: str) -> str:
        """Extract accession number from URL"""
        import re
        match = re.search(r'/Archives/edgar/data/\d+/(\d+)/', url)
        return match.group(1) if match else ''
    
    def download_all_filings(self, cik: str, ticker: str, filings: List[Dict], save_dir: str) -> List[Dict]:
        """Download all filings for a company"""
        downloaded = []
        company_dir = Path(save_dir) / ticker
        company_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"  📥 Downloading {len(filings)} filings...")
        
        for i, filing in enumerate(filings):
            try:
                if not filing.get('document_url'):
                    continue
                
                # Create filename
                form_type = filing['form_type'].replace('/', '-')
                date = filing['filing_date']
                filename = f"{form_type}_{date}_{i+1}.html"
                file_path = company_dir / filename
                
                # Download
                print(f"    Downloading {i+1}/{len(filings)}: {form_type} ({date})")
                time.sleep(self.rate_limit_delay)
                response = requests.get(filing['document_url'], headers=self.headers)
                
                if response.status_code == 200:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    downloaded.append({
                        'path': str(file_path),
                        'form_type': filing['form_type'],
                        'filing_date': filing['filing_date'],
                        'url': filing['document_url']
                    })
                    
            except Exception as e:
                print(f"      ❌ Error downloading: {e}")
        
        print(f"    ✅ Downloaded {len(downloaded)} filings")
        return downloaded

# Singleton instance
sec_service = SECService()
=======
sec_service.py - SEC EDGAR API integration
Date: 2025-06-12 01:25:00 UTC
User: thorrobber22
"""

import requests
import json
from datetime import datetime

# SEC EDGAR base URL
EDGAR_BASE = "https://data.sec.gov"
EDGAR_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"

# Headers required by SEC
HEADERS = {
    'User-Agent': 'Hedge Intelligence thorrobber22@email.com',
    'Accept': 'application/json'
}

def get_company_filings(cik, form_type=None):
    """Get company filings from SEC EDGAR"""
    try:
        # Pad CIK to 10 digits
        cik = str(cik).zfill(10)
        
        # Get submissions
        url = f"{EDGAR_BASE}/submissions/CIK{cik}.json"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            filings = []
            
            recent = data.get('filings', {}).get('recent', {})
            forms = recent.get('form', [])
            dates = recent.get('filingDate', [])
            accessions = recent.get('accessionNumber', [])
            
            for i in range(min(len(forms), 20)):  # Last 20 filings
                if not form_type or forms[i] == form_type:
                    filings.append({
                        'form': forms[i],
                        'filing_date': dates[i],
                        'accession': accessions[i].replace('-', ''),
                        'url': f"{EDGAR_ARCHIVES}/{cik}/{accessions[i].replace('-', '')}/{accessions[i]}.txt"
                    })
            
            return filings
        else:
            return []
    except Exception as e:
        print(f"SEC API Error: {e}")
        return []

def get_filing_content(url):
    """Get filing content from URL"""
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.text
        return ""
    except:
        return ""

def search_company(name):
    """Search for company by name"""
    try:
        url = f"{EDGAR_BASE}/cgi-bin/cik_lookup"
        params = {'company': name}
        response = requests.get(url, params=params, headers=HEADERS)
        # Parse response and return CIK
        return "0001234567"  # Placeholder
    except:
        return None

def get_recent_s1_filings(days=30):
    """Get recent S-1 filings"""
    # Placeholder - would use EDGAR full-text search
    return [
        {
            'company': 'Recent IPO Corp',
            'cik': '0001234567',
            'filing_date': '2025-06-10',
            'form': 'S-1'
        }
    ]


def extract_financial_data(filing_content):
    """Extract financial data from SEC filing"""
    try:
        # This would use regex/parsing to extract financial tables
        # For now, return mock data
        return {
            "revenue": {
                "2024": 580000000,
                "2023": 380000000,
                "2022": 210000000
            },
            "net_income": {
                "2024": -120000000,
                "2023": -95000000,
                "2022": -78000000
            },
            "cash_burn": {
                "quarterly": 45000000,
                "runway_months": 18
            }
        }
    except Exception as e:
        return {}

def get_s1_financial_summary(cik):
    """Get financial summary from S-1 filing"""
    filings = get_company_filings(cik, "S-1")
    if filings:
        content = get_filing_content(filings[0]["url"])
        return extract_financial_data(content)
    return {}
>>>>>>> 7bda5bb3f199dc2d74016e366f0a956b33545e5c
