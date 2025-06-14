"""
IPO Scraper - Real IPOScoop Integration
Date: 2025-06-13 23:59:05 UTC
Author: thorrobber22
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from pathlib import Path
from typing import List, Dict, Optional
import time
from services.sec_service import sec_service

class IPOScraper:
    """Scrape real IPO data from IPOScoop"""
    
    def __init__(self):
        self.base_url = "https://www.iposcoop.com"
        self.data_dir = Path("data")
        self.filings_dir = self.data_dir / "ipo_filings"
        self.filings_dir.mkdir(parents=True, exist_ok=True)
        
    def scrape_recent_ipos(self, limit: int = 10) -> List[Dict]:
        """Scrape recent IPO filings from IPOScoop"""
        try:
            # Get IPO calendar page
            url = f"{self.base_url}/ipo-calendar/"
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch IPOScoop: {response.status_code}")
                return self.get_demo_data()
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find IPO table (adjust selectors based on actual HTML)
            ipos = []
            
            # Look for IPO entries - these selectors may need adjustment
            ipo_rows = soup.find_all('tr', class_='ipo-row')  # Example selector
            
            if not ipo_rows:
                # Try alternative selectors
                table = soup.find('table', {'class': 'ipo-table'})
                if table:
                    ipo_rows = table.find_all('tr')[1:]  # Skip header
            
            for row in ipo_rows[:limit]:
                try:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        ipo = {
                            'ticker': cells[0].text.strip(),
                            'company': cells[1].text.strip(),
                            'date': cells[2].text.strip(),
                            'status': 'Filed',
                            'exchange': cells[3].text.strip() if len(cells) > 3 else 'NYSE'
                        }
                        ipos.append(ipo)
                        
                except Exception as e:
                    print(f"❌ Error parsing row: {e}")
                    continue
                    
            # If no real data found, use demo data
            if not ipos:
                print("⚠️ Using demo IPO data")
                return self.get_demo_data()
                
            return ipos
            
        except Exception as e:
            print(f"❌ Error scraping IPOScoop: {e}")
            return self.get_demo_data()
            
    def get_demo_data(self) -> List[Dict]:
        """Return demo IPO data for testing"""
        return [
            {'ticker': 'TECH', 'company': 'TechCorp International', 'date': '2025-06-13', 'status': 'Filed'},
            {'ticker': 'BIO', 'company': 'BioMed Solutions', 'date': '2025-06-12', 'status': 'Priced'},
            {'ticker': 'FINX', 'company': 'FinTech Innovations', 'date': '2025-06-10', 'status': 'Trading'},
            {'ticker': 'CLOUD', 'company': 'CloudBase Systems', 'date': '2025-06-09', 'status': 'Filed'},
            {'ticker': 'GENE', 'company': 'GeneTech Research', 'date': '2025-06-08', 'status': 'Filed'}
        ]
            
    def process_ipo_data(self, ipo: Dict) -> Dict:
        """Process IPO data with CIK lookup and document count"""
        try:
            print(f"\n📊 Processing {ipo['ticker']} - {ipo['company']}")
            
            # Look up CIK
            cik = sec_service.lookup_cik(ipo['company'])
            
            if cik:
                ipo['cik'] = cik
                
                # Get filing count
                filings = sec_service.get_filings(cik, "S-1")
                ipo['documents'] = len(filings)
                ipo['latest_filing'] = filings[0]['filing_date'] if filings else None
                
                # Download latest S-1 if available
                if filings:
                    latest = filings[0]
                    save_path = sec_service.download_filing(
                        cik,
                        latest['accession'],
                        latest['primary_doc'],
                        str(self.filings_dir)
                    )
                    
                    if save_path:
                        ipo['local_filing_path'] = save_path
                        
            else:
                print(f"⚠️ No CIK found for {ipo['company']}")
                ipo['cik'] = None
                ipo['documents'] = 0
                
            return ipo
            
        except Exception as e:
            print(f"❌ Error processing {ipo['ticker']}: {e}")
            return ipo
            
    def update_ipo_data(self):
        """Full pipeline: Scrape → CIK → Download → Save"""
        print("\n🔄 Starting IPO data update...")
        
        # Scrape recent IPOs
        ipos = self.scrape_recent_ipos(limit=5)
        print(f"✅ Found {len(ipos)} IPOs")
        
        # Process each IPO
        processed_ipos = []
        for ipo in ipos:
            processed = self.process_ipo_data(ipo)
            processed_ipos.append(processed)
            time.sleep(0.5)  # Rate limiting
            
        # Save to JSON
        output_file = self.data_dir / "ipo_calendar.json"
        with open(output_file, 'w') as f:
            json.dump(processed_ipos, f, indent=2)
            
        print(f"\n✅ Saved {len(processed_ipos)} IPOs to {output_file}")
        
        # Update company profiles
        self.update_company_profiles(processed_ipos)
        
        return processed_ipos
        
    def update_company_profiles(self, ipos: List[Dict]):
        """Update company profiles with IPO data"""
        profiles_file = self.data_dir / "company_profiles.json"
        
        # Load existing profiles
        if profiles_file.exists():
            with open(profiles_file, 'r') as f:
                profiles = json.load(f)
        else:
            profiles = {}
            
        # Update with new data
        for ipo in ipos:
            ticker = ipo['ticker']
            profiles[ticker] = {
                'name': ipo['company'],
                'sector': self.determine_sector(ipo['company']),
                'cik': ipo.get('cik'),
                'documents': ipo.get('documents', 0),
                'last_update': datetime.now().isoformat(),
                'status': ipo['status'],
                'latest_filing': ipo.get('latest_filing'),
                'local_filing_path': ipo.get('local_filing_path')
            }
            
        # Save updated profiles
        with open(profiles_file, 'w') as f:
            json.dump(profiles, f, indent=2)
            
        print(f"✅ Updated {len(profiles)} company profiles")
        
    def determine_sector(self, company_name: str) -> str:
        """Simple sector determination based on company name"""
        name_lower = company_name.lower()
        
        if any(term in name_lower for term in ['tech', 'software', 'cloud', 'data', 'cyber']):
            return 'Technology'
        elif any(term in name_lower for term in ['bio', 'med', 'pharma', 'health', 'gene']):
            return 'Healthcare'
        elif any(term in name_lower for term in ['fin', 'bank', 'capital', 'invest']):
            return 'Financial'
        elif any(term in name_lower for term in ['energy', 'oil', 'gas', 'solar']):
            return 'Energy'
        else:
            return 'Consumer'

# Create scraper instance
ipo_scraper = IPOScraper()
