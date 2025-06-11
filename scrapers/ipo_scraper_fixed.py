"""
IPO Scraper - Fixed Version
Scrapes IPOScoop.com for calendar data
"""

import aiohttp
from bs4 import BeautifulSoup
import asyncio
from typing import List, Dict
import re

class IPOScraper:
    def __init__(self):
        self.base_url = "https://www.iposcoop.com/ipo-calendar/"
    
    async def scrape_calendar(self) -> List[Dict]:
        """Scrape IPO calendar from IPOScoop"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._parse_calendar(html)
            except Exception as e:
                print(f"Error scraping IPOScoop: {e}")
                return []
    
    def _parse_calendar(self, html: str) -> List[Dict]:
        """Parse IPO calendar from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        ipos = []
        
        # Find the main table
        table = soup.find('table')
        if not table:
            return []
        
        rows = table.find_all('tr')[1:]  # Skip header
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 6:
                try:
                    ipo = {
                        'company': cols[0].text.strip(),
                        'ticker': cols[1].text.strip(),
                        'managers': cols[2].text.strip(),
                        'shares': cols[3].text.strip(),
                        'price_range': f"${cols[4].text.strip()}-${cols[5].text.strip()}",
                        'date': 'TBD'  # IPOScoop doesn't always show dates
                    }
                    ipos.append(ipo)
                except:
                    continue
        
        return ipos

# Test if running directly
if __name__ == "__main__":
    async def test():
        scraper = IPOScraper()
        ipos = await scraper.scrape_calendar()
        print(f"Found {len(ipos)} IPOs")
        for ipo in ipos[:3]:
            print(ipo)
    
    asyncio.run(test())
