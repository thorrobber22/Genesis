#!/usr/bin/env python3
"""
IPOScoop Scraper - Complete Implementation
Date: 2025-06-14 17:51:43 UTC
Author: thorrobber22
"""

import httpx
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone
from pathlib import Path
import asyncio
import re
from typing import Optional, Dict, List

class IPOScoopScraper:
    """Scrape complete IPO data from IPOScoop"""
    
    def __init__(self):
        self.base_url = "https://www.iposcoop.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
    
    async def scrape_ipo_calendar(self) -> List[Dict]:
        """Scrape IPO calendar with ALL fields from IPOScoop"""
        
        print("🔍 Scraping IPOScoop calendar...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/ipo-calendar/",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    print(f"❌ Error: Status {response.status_code}")
                    return []
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find the main IPO table
                ipos = []
                tables = soup.find_all('table')
                
                for table in tables:
                    # Look for the IPO calendar table
                    headers = table.find_all('th')
                    if not headers:
                        continue
                    
                    header_texts = [h.text.strip() for h in headers]
                    
                    # Map column indices based on headers
                    col_map = {}
                    for i, header in enumerate(header_texts):
                        header_lower = header.lower()
                        if 'company' in header_lower:
                            col_map['company'] = i
                        elif 'symbol' in header_lower:
                            col_map['ticker'] = i
                        elif 'lead' in header_lower or 'manager' in header_lower:
                            col_map['lead_managers'] = i
                        elif 'shares' in header_lower:
                            col_map['shares'] = i
                        elif 'price low' in header_lower:
                            col_map['price_low'] = i
                        elif 'price high' in header_lower:
                            col_map['price_high'] = i
                        elif 'volume' in header_lower:
                            col_map['volume'] = i
                        elif 'expected' in header_lower or 'trade' in header_lower:
                            col_map['expected_date'] = i
                        elif 'rating' in header_lower and 'change' not in header_lower:
                            col_map['scoop_rating'] = i
                    
                    # If this looks like the IPO table, parse it
                    if 'company' in col_map and 'ticker' in col_map:
                        rows = table.find_all('tr')[1:]  # Skip header row
                        
                        for row in rows:
                            cols = row.find_all('td')
                            if len(cols) < 2:
                                continue
                            
                            # Extract all fields
                            ipo = {
                                'company': self._get_col_text(cols, col_map.get('company', 0)),
                                'ticker': self._get_col_text(cols, col_map.get('ticker', 1)),
                                'lead_managers': self._get_col_text(cols, col_map.get('lead_managers', 2)),
                                'shares_millions': self._parse_shares(self._get_col_text(cols, col_map.get('shares', 3))),
                                'price_low': self._parse_price(self._get_col_text(cols, col_map.get('price_low', 4))),
                                'price_high': self._parse_price(self._get_col_text(cols, col_map.get('price_high', 5))),
                                'volume': self._get_col_text(cols, col_map.get('volume', 6)),
                                'expected_date': self._parse_date(self._get_col_text(cols, col_map.get('expected_date', 7))),
                                'scoop_rating': self._get_col_text(cols, col_map.get('scoop_rating', 8)),
                                'status': self._determine_status(self._get_col_text(cols, col_map.get('expected_date', 7))),
                                'exchange': 'TBD',  # Will be determined later
                                'lockup': '180 days',  # Default, will be extracted from docs
                                'documents': 0,
                                'filing_count': 0,
                                'last_updated': datetime.now(timezone.utc).isoformat()
                            }
                            
                            # Determine price range
                            if ipo['price_low'] and ipo['price_high']:
                                if ipo['price_low'] == ipo['price_high']:
                                    ipo['price_range'] = f"${ipo['price_low']}"
                                else:
                                    ipo['price_range'] = f"${ipo['price_low']}-${ipo['price_high']}"
                            else:
                                ipo['price_range'] = 'TBD'
                            
                            # Determine exchange based on ticker length
                            if ipo['ticker'] and ipo['ticker'] != '--':
                                ipo['exchange'] = 'NASDAQ' if len(ipo['ticker']) <= 4 else 'NYSE'
                            
                            # Only add valid IPOs
                            if ipo['ticker'] and ipo['ticker'] != '--' and ipo['company']:
                                ipos.append(ipo)
                                print(f"  ✅ {ipo['ticker']} - {ipo['company']} ({ipo['expected_date']})")
                        
                        break  # Found the IPO table
                
                print(f"\n✅ Scraped {len(ipos)} IPOs")
                return ipos
                
        except Exception as e:
            print(f"❌ Error scraping: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_col_text(self, cols: List, idx: int) -> str:
        """Safely get column text"""
        if 0 <= idx < len(cols):
            return cols[idx].text.strip()
        return ''
    
    def _parse_shares(self, text: str) -> float:
        """Parse shares from text (e.g., '6.0' -> 6.0)"""
        try:
            # Remove any non-numeric characters except decimal
            cleaned = re.sub(r'[^0-9.]', '', text)
            return float(cleaned) if cleaned else 0.0
        except:
            return 0.0
    
    def _parse_price(self, text: str) -> float:
        """Parse price from text (e.g., '$10.00' -> 10.00)"""
        try:
            # Remove $ and other non-numeric characters
            cleaned = re.sub(r'[^0-9.]', '', text)
            return float(cleaned) if cleaned else 0.0
        except:
            return 0.0
    
    def _parse_date(self, text: str) -> str:
        """Parse and normalize date"""
        if not text or text == '--':
            return 'TBD'
        
        # Check if it says "Priced"
        if 'priced' in text.lower():
            return 'Priced'
        
        # Return as-is for now (could add date parsing logic)
        return text.strip()
    
    def _determine_status(self, date_text: str) -> str:
        """Determine IPO status from date text"""
        if not date_text:
            return 'Expected'
        
        date_lower = date_text.lower()
        if 'priced' in date_lower:
            return 'Priced'
        elif 'trading' in date_lower:
            return 'Trading'
        elif 'withdrawn' in date_lower:
            return 'Withdrawn'
        elif 'postponed' in date_lower:
            return 'Postponed'
        else:
            return 'Expected'
    
    async def save_scraped_data(self, ipos: List[Dict]) -> str:
        """Save scraped data to JSON file"""
        
        output = {
            'listings': ipos,
            'total': len(ipos),
            'source': 'iposcoop.com',
            'updated': datetime.now(timezone.utc).isoformat(),
            'fields': [
                'company', 'ticker', 'lead_managers', 'shares_millions',
                'price_range', 'volume', 'expected_date', 'scoop_rating',
                'status', 'exchange'
            ]
        }
        
        # Save to data directory
        output_path = self.data_dir / "ipo_calendar.json"
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Saved to {output_path}")
        return str(output_path)

async def main():
    """Run the scraper"""
    scraper = IPOScoopScraper()
    
    # Scrape IPO calendar
    ipos = await scraper.scrape_ipo_calendar()
    
    if ipos:
        # Save the data
        output_file = await scraper.save_scraped_data(ipos)
        
        print(f"\n✅ COMPLETE!")
        print(f"📊 Scraped {len(ipos)} IPOs")
        print(f"💾 Data saved to: {output_file}")
        
        # Show sample
        print("\n📋 Sample IPO:")
        sample = ipos[0]
        for key, value in sample.items():
            print(f"  {key}: {value}")
    else:
        print("\n❌ No IPOs scraped")

if __name__ == "__main__":
    asyncio.run(main())
