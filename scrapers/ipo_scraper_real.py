#!/usr/bin/env python3
"""
REAL IPO Scraper for IPOScoop.com
Actually scrapes data, not dummy returns
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IPOScraperReal:
    def __init__(self):
        self.base_url = "https://www.iposcoop.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.data_dir = Path("data/ipo_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def scrape_ipo_calendar(self):
        """Actually scrape the IPO calendar - no dummy data!"""
        logger.info("🚀 Starting REAL IPO scrape from IPOScoop...")
        
        results = {
            "scraped_at": datetime.now().isoformat(),
            "recently_priced": [],
            "upcoming": [],
            "filed": [],
            "withdrawn": []
        }
        
        try:
            # Fetch the main calendar page
            response = requests.get(f"{self.base_url}/ipo-calendar/", headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all tables on the page
            tables = soup.find_all('table')
            
            for table in tables:
                # Check what type of table this is by looking at preceding text
                prev_elem = table.find_previous(['h2', 'h3', 'strong'])
                if not prev_elem:
                    continue
                    
                section_title = prev_elem.text.strip().lower()
                
                # Parse the table
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 2:
                        continue
                    
                    ipo_info = self._parse_row(cells, section_title)
                    
                    if ipo_info:
                        # Categorize based on section
                        if 'priced' in section_title or 'recent' in section_title:
                            results['recently_priced'].append(ipo_info)
                        elif 'upcoming' in section_title or 'expected' in section_title:
                            results['upcoming'].append(ipo_info)
                        elif 'filed' in section_title or 'filing' in section_title:
                            results['filed'].append(ipo_info)
                        elif 'withdrawn' in section_title or 'postponed' in section_title:
                            results['withdrawn'].append(ipo_info)
                        else:
                            # Default to filed
                            results['filed'].append(ipo_info)
            
            # Log what we found
            logger.info(f"✅ Scraped {len(results['recently_priced'])} recently priced IPOs")
            logger.info(f"✅ Scraped {len(results['upcoming'])} upcoming IPOs")
            logger.info(f"✅ Scraped {len(results['filed'])} filed IPOs")
            
            # Save results
            output_file = self.data_dir / f"ipo_calendar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Also save as latest
            latest_file = self.data_dir / "ipo_calendar_latest.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Saved to {output_file}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error scraping IPOScoop: {e}")
            return results
    
    def _parse_row(self, cells, section_type):
        """Parse a table row into IPO data"""
        try:
            # Different tables have different formats
            ipo_data = {
                'scraped_at': datetime.now().isoformat(),
                'source': 'IPOScoop',
                'section': section_type
            }
            
            # Try to extract company and ticker
            company_cell = cells[0].text.strip()
            
            # Extract ticker if in parentheses
            ticker_match = re.search(r'\(([A-Z]+)\)', company_cell)
            if ticker_match:
                ipo_data['ticker'] = ticker_match.group(1)
                ipo_data['company_name'] = company_cell.replace(ticker_match.group(0), '').strip()
            else:
                ipo_data['company_name'] = company_cell
                ipo_data['ticker'] = None
            
            # Extract other fields based on number of cells
            if len(cells) >= 2:
                ipo_data['exchange'] = cells[1].text.strip()
            
            if len(cells) >= 3:
                # Could be shares or price
                text = cells[2].text.strip()
                if '$' in text:
                    ipo_data['price_range'] = text
                else:
                    ipo_data['shares'] = text
            
            if len(cells) >= 4:
                text = cells[3].text.strip()
                if '$' in text:
                    ipo_data['price_range'] = text
                else:
                    ipo_data['expected_date'] = text
            
            if len(cells) >= 5:
                ipo_data['expected_date'] = cells[4].text.strip()
            
            # Extract link if available
            link = cells[0].find('a')
            if link and link.get('href'):
                ipo_data['detail_url'] = self.base_url + link['href']
            
            return ipo_data
            
        except Exception as e:
            logger.error(f"Error parsing row: {e}")
            return None
    
    def lookup_ciks(self, ipo_data):
        """Look up CIKs for scraped companies"""
        logger.info("\n🔍 Looking up CIKs from SEC...")
        
        # Load SEC company tickers
        try:
            response = requests.get(
                "https://www.sec.gov/files/company_tickers.json",
                headers={'User-Agent': 'HedgeIntel admin@hedgeintel.com'}
            )
            response.raise_for_status()
            
            tickers_db = response.json()
            
            # Create lookup dictionaries
            ticker_to_cik = {}
            name_to_cik = {}
            
            for item in tickers_db.values():
                ticker = item.get('ticker', '').upper()
                name = item.get('title', '').upper()
                cik = str(item.get('cik_str', '')).zfill(10)
                
                ticker_to_cik[ticker] = (cik, item.get('title'))
                # Clean company name for matching
                clean_name = re.sub(r'\s+(INC|CORP|LLC|LTD|CO)\.?$', '', name)
                name_to_cik[clean_name] = (cik, item.get('title'))
            
            # Match IPOs to CIKs
            matched = 0
            all_ipos = (
                ipo_data.get('recently_priced', []) +
                ipo_data.get('upcoming', []) +
                ipo_data.get('filed', [])
            )
            
            for ipo in all_ipos:
                # Try ticker match first
                if ipo.get('ticker'):
                    ticker_upper = ipo['ticker'].upper()
                    if ticker_upper in ticker_to_cik:
                        ipo['cik'], ipo['sec_name'] = ticker_to_cik[ticker_upper]
                        ipo['cik_match_type'] = 'ticker'
                        matched += 1
                        logger.info(f"✅ Matched {ipo['ticker']} to CIK {ipo['cik']}")
                        continue
                
                # Try name match
                if ipo.get('company_name'):
                    # Clean the name
                    clean_name = re.sub(r'\s+(INC|CORP|LLC|LTD|CO)\.?$', '', 
                                      ipo['company_name'].upper())
                    
                    if clean_name in name_to_cik:
                        ipo['cik'], ipo['sec_name'] = name_to_cik[clean_name]
                        ipo['cik_match_type'] = 'name'
                        matched += 1
                        logger.info(f"✅ Matched {ipo['company_name']} to CIK {ipo['cik']}")
            
            logger.info(f"\n📊 CIK Match Summary:")
            logger.info(f"   Total IPOs: {len(all_ipos)}")
            logger.info(f"   Matched: {matched} ({matched/len(all_ipos)*100:.1f}%)")
            
        except Exception as e:
            logger.error(f"❌ Error looking up CIKs: {e}")
        
        return ipo_data

# Test it
if __name__ == "__main__":
    scraper = IPOScraperReal()
    
    # Scrape IPOs
    ipo_data = scraper.scrape_ipo_calendar()
    
    # Look up CIKs
    ipo_data = scraper.lookup_ciks(ipo_data)
    
    # Show sample results
    print("\n📋 Sample Recently Priced IPOs:")
    for ipo in ipo_data.get('recently_priced', [])[:3]:
        print(f"\n{ipo.get('company_name')} ({ipo.get('ticker', 'N/A')})")
        print(f"  CIK: {ipo.get('cik', 'Not found')}")
        print(f"  Price: {ipo.get('price_range', 'N/A')}")
        print(f"  Exchange: {ipo.get('exchange', 'N/A')}")