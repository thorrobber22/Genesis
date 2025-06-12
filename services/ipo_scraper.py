"""
IPO Scraper - Complete data extraction from IPOScoop
"""

import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class IPOScraper:
    def __init__(self):
        self.base_url = "https://www.iposcoop.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def get_ipo_calendar(self) -> List[Dict]:
        """Scrape complete IPO calendar with all fields"""
        try:
            url = f"{self.base_url}/ipo-calendar/"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch IPO calendar: {response.status}")
                        return []
                    
                    html = await response.text()
            
            soup = BeautifulSoup(html, 'html.parser')
            ipos = []
            
            # Find main IPO table
            tables = soup.find_all('table', class_=['table', 'ipo-table', 'calendar-table'])
            
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 5:
                        ipo = self._parse_complete_ipo_row(cells, row)
                        if ipo and ipo.get('ticker'):
                            ipos.append(ipo)
            
            logger.info(f"Scraped {len(ipos)} IPOs with complete data")
            return ipos
            
        except Exception as e:
            logger.error(f"Error scraping IPO calendar: {e}")
            return []
    
    def _parse_complete_ipo_row(self, cells, row) -> Optional[Dict]:
        """Parse all available IPO data"""
        try:
            # Extract all text for additional parsing
            row_text = row.get_text(separator=' ')
            
            # Basic fields
            ticker = self._clean_text(cells[0].text) if len(cells) > 0 else ""
            company = self._clean_text(cells[1].text) if len(cells) > 1 else ""
            price_range = self._clean_text(cells[2].text) if len(cells) > 2 else ""
            shares = self._clean_text(cells[3].text) if len(cells) > 3 else ""
            date = self._clean_text(cells[4].text) if len(cells) > 4 else ""
            
            # Extended fields (adjust indices based on actual table)
            underwriter = self._clean_text(cells[5].text) if len(cells) > 5 else ""
            exchange = self._extract_exchange(row_text)
            sector = self._extract_sector(row_text)
            revenue = self._extract_revenue(row_text)
            market_cap = self._extract_market_cap(row_text, price_range, shares)
            employees = self._extract_employees(row_text)
            founded = self._extract_founded(row_text)
            
            # Parse numeric values
            price_low, price_high = self._parse_price_range(price_range)
            shares_num = self._parse_shares(shares)
            
            # Calculate expected proceeds
            expected_proceeds = 0
            if price_high and shares_num:
                expected_proceeds = price_high * shares_num
            
            return {
                "ticker": ticker.upper(),
                "company": company,
                "price_range": price_range,
                "price_low": price_low,
                "price_high": price_high,
                "shares": shares,
                "shares_number": shares_num,
                "date": date,
                "underwriter": underwriter,
                "exchange": exchange,
                "sector": sector,
                "revenue": revenue,
                "market_cap": market_cap,
                "employees": employees,
                "founded": founded,
                "expected_proceeds": expected_proceeds,
                "source": "iposcoop",
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing IPO row: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        return ' '.join(text.strip().split())
    
    def _parse_price_range(self, price_range: str) -> tuple:
        """Parse price range to numeric values"""
        try:
            # Handle formats: $12-14, $12.00-$14.00, 12-14
            numbers = re.findall(r'\d+\.?\d*', price_range)
            if len(numbers) >= 2:
                return float(numbers[0]), float(numbers[1])
            elif len(numbers) == 1:
                return float(numbers[0]), float(numbers[0])
        except:
            pass
        return 0.0, 0.0
    
    def _parse_shares(self, shares_str: str) -> int:
        """Parse shares string to number"""
        try:
            clean = shares_str.replace(',', '').upper()
            
            # Handle millions/billions
            multiplier = 1
            if 'M' in clean or 'MILLION' in clean:
                multiplier = 1_000_000
            elif 'B' in clean or 'BILLION' in clean:
                multiplier = 1_000_000_000
            
            # Extract number
            numbers = re.findall(r'\d+\.?\d*', clean)
            if numbers:
                return int(float(numbers[0]) * multiplier)
        except:
            pass
        return 0
    
    def _extract_exchange(self, text: str) -> str:
        """Extract exchange from text"""
        exchanges = ['NYSE', 'NASDAQ', 'AMEX', 'NYSE American']
        for exchange in exchanges:
            if exchange in text.upper():
                return exchange
        return "TBD"
    
    def _extract_sector(self, text: str) -> str:
        """Extract sector/industry"""
        sectors = [
            'Technology', 'Healthcare', 'Biotech', 'Financial', 
            'Consumer', 'Energy', 'Industrial', 'Real Estate'
        ]
        text_upper = text.upper()
        for sector in sectors:
            if sector.upper() in text_upper:
                return sector
        return "TBD"
    
    def _extract_revenue(self, text: str) -> str:
        """Extract revenue if available"""
        rev_match = re.search(r'\$?\d+\.?\d*[MB]?\s*(?:revenue|sales)', text, re.IGNORECASE)
        if rev_match:
            return rev_match.group(0)
        return "TBD"
    
    def _extract_market_cap(self, text: str, price_range: str, shares: str) -> str:
        """Calculate or extract market cap"""
        # Try to find existing market cap
        cap_match = re.search(r'\$?\d+\.?\d*[MB]\s*(?:market cap|valuation)', text, re.IGNORECASE)
        if cap_match:
            return cap_match.group(0)
        
        # Calculate from price and shares
        price_low, price_high = self._parse_price_range(price_range)
        shares_num = self._parse_shares(shares)
        
        if price_high and shares_num:
            market_cap = price_high * shares_num
            if market_cap > 1_000_000_000:
                return f"${market_cap / 1_000_000_000:.1f}B"
            else:
                return f"${market_cap / 1_000_000:.0f}M"
        
        return "TBD"
    
    def _extract_employees(self, text: str) -> str:
        """Extract employee count"""
        emp_match = re.search(r'\d+\+?\s*employees?', text, re.IGNORECASE)
        if emp_match:
            return emp_match.group(0)
        return "TBD"
    
    def _extract_founded(self, text: str) -> str:
        """Extract founding year"""
        year_match = re.search(r'(?:founded|established)\s*(?:in\s*)?([12]\d{3})', text, re.IGNORECASE)
        if year_match:
            return year_match.group(1)
        return "TBD"


def scrape_all_ipo_data():
    """Main entry point for IPO scraping"""
    scraper = IPOScraper()
    try:
        # Try to call the main scraping method
        if hasattr(scraper, 'scrape_iposcoop'):
            return scraper.scrape_iposcoop()
        elif hasattr(scraper, 'scrape'):
            return scraper.scrape()
        elif hasattr(scraper, 'run'):
            return scraper.run()
        else:
            # Fallback - create minimal response
            print("Warning: No standard scraping method found")
            return {"ipos": [], "status": "error", "message": "No scraping method found"}
    except Exception as e:
        print(f"Error in scraping: {str(e)}")
        return {"ipos": [], "status": "error", "message": str(e)}


if __name__ == "__main__":
    print("Running IPO scraper...")
    data = scrape_all_ipo_data()
    if isinstance(data, dict):
        ipo_count = len(data.get('ipos', []))
        print(f"Scraped {ipo_count} IPOs")
    else:
        print("Scraper returned:", type(data))
