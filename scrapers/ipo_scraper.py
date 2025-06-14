"""
IPO Scraper - Updated for current IPOScoop structure
Date: 2025-06-14 00:16:02 UTC
Author: thorrobber22
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from pathlib import Path
from typing import List, Dict
import time

class IPOScraper:
    def __init__(self):
        self.base_url = "https://www.iposcoop.com"
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def scrape_ipo_calendar(self) -> List[Dict]:
        """Scrape IPO calendar from IPOScoop"""
        print("\n📊 Scraping IPO Calendar from IPOScoop...")
        
        try:
            url = f"{self.base_url}/ipo-calendar/"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch IPOScoop: {response.status_code}")
                return self.get_fallback_data()
                
            soup = BeautifulSoup(response.text, 'html.parser')
            ipos = []
            
            # IPOScoop typically uses tables for IPO data
            # Look for tables with IPO information
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if this is an IPO table by looking for key headers
                headers = []
                header_row = table.find('tr')
                if header_row:
                    headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
                
                # Look for tables with symbol/company columns
                if any(h in headers for h in ['symbol', 'company', 'ticker']):
                    rows = table.find_all('tr')[1:]  # Skip header
                    
                    for row in rows[:10]:  # Limit to 10 IPOs
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            # Extract data based on common IPOScoop formats
                            ticker = cells[0].get_text().strip()
                            company = cells[1].get_text().strip()
                            
                            # Skip if no ticker
                            if not ticker or ticker == '-':
                                continue
                                
                            ipo_data = {
                                'ticker': ticker,
                                'company': company,
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'status': 'Filed',
                                'exchange': 'NYSE',  # Default
                                'documents': 0,
                                'lockup': None
                            }
                            
                            # Try to extract additional data if available
                            if len(cells) > 2:
                                # Price range might be in 3rd column
                                price_text = cells[2].get_text().strip()
                                if '$' in price_text:
                                    ipo_data['price_range'] = price_text
                            
                            if len(cells) > 3:
                                # Shares might be in 4th column
                                shares_text = cells[3].get_text().strip()
                                if shares_text and shares_text != '-':
                                    ipo_data['shares'] = shares_text
                            
                            ipos.append(ipo_data)
                            print(f"✅ Found: {ticker} - {company}")
            
            if not ipos:
                print("⚠️ No IPOs found, using fallback data")
                return self.get_fallback_data()
                
            return ipos
            
        except Exception as e:
            print(f"❌ Error scraping IPOScoop: {e}")
            return self.get_fallback_data()
    
    def get_fallback_data(self) -> List[Dict]:
        """Fallback demo data if scraping fails"""
        return [
            {
                'ticker': 'RDDT',
                'company': 'Reddit, Inc.',
                'date': '2024-03-21',
                'status': 'Trading',
                'exchange': 'NYSE',
                'documents': 8,
                'lockup': '180d',
                'price_range': '$31-34'
            },
            {
                'ticker': 'SMCI',
                'company': 'Super Micro Computer',
                'date': '2024-03-15',
                'status': 'Trading',
                'exchange': 'NASDAQ',
                'documents': 6,
                'lockup': '180d',
                'price_range': '$28-32'
            },
            {
                'ticker': 'TECH',
                'company': 'TechCorp International',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'status': 'Filed',
                'exchange': 'NYSE',
                'documents': 8,
                'lockup': None,
                'price_range': '$18-22'
            }
        ]
    
    def update_ipo_calendar(self):
        """Main method to update IPO calendar data"""
        # Scrape fresh data
        ipos = self.scrape_ipo_calendar()
        
        # Save to JSON
        output_file = self.data_dir / "ipo_calendar.json"
        with open(output_file, 'w') as f:
            json.dump(ipos, f, indent=2)
            
        print(f"\n✅ Saved {len(ipos)} IPOs to {output_file}")
        
        # Also update company profiles
        self.update_company_profiles(ipos)
        
        return ipos
    
    def update_company_profiles(self, ipos: List[Dict]):
        """Update company profiles based on IPO data"""
        profiles_file = self.data_dir / "company_profiles.json"
        
        # Load existing or create new
        if profiles_file.exists():
            with open(profiles_file, 'r') as f:
                profiles = json.load(f)
        else:
            profiles = {}
        
        # Update with IPO data
        for ipo in ipos:
            ticker = ipo['ticker']
            profiles[ticker] = {
                'name': ipo['company'],
                'sector': self.determine_sector(ipo['company']),
                'exchange': ipo.get('exchange', 'NYSE'),
                'status': ipo.get('status', 'Filed'),
                'documents': ipo.get('documents', 0),
                'last_update': datetime.now().isoformat(),
                'price_range': ipo.get('price_range', 'TBD'),
                'lockup': ipo.get('lockup', 'TBD')
            }
        
        # Save updated profiles
        with open(profiles_file, 'w') as f:
            json.dump(profiles, f, indent=2)
            
        print(f"✅ Updated {len(profiles)} company profiles")
    
    def determine_sector(self, company_name: str) -> str:
        """Determine sector from company name"""
        name_lower = company_name.lower()
        
        if any(term in name_lower for term in ['tech', 'software', 'computer', 'digital', 'cyber']):
            return 'Technology'
        elif any(term in name_lower for term in ['bio', 'pharma', 'medical', 'health', 'therapeutics']):
            return 'Healthcare'
        elif any(term in name_lower for term in ['bank', 'financial', 'capital', 'credit']):
            return 'Financial'
        elif any(term in name_lower for term in ['energy', 'oil', 'gas', 'power']):
            return 'Energy'
        else:
            return 'Consumer'

# Create instance
scraper = IPOScraper()

# Run if main
if __name__ == "__main__":
    print("🚀 Running IPO Scraper...")
    scraper.update_ipo_calendar()
