#!/usr/bin/env python3
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
                                    match = re.search(r'\$([\d.]+)\s*-\s*\$([\d.]+)', ipo['price_range'])
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
