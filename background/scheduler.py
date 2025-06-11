"""
Simplified Scheduler - IPO Scraping Only
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import logging
from scrapers.ipo_scraper_fixed import IPOScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleScheduler:
    def __init__(self):
        self.running = True
        self.scraper = IPOScraper()
    
    async def start(self):
        """Start scheduler"""
        logger.info("Starting simplified scheduler - IPO scraping only")
        
        while self.running:
            try:
                # Scrape IPOs
                ipos = await self.scraper.scrape_calendar()
                
                if ipos:
                    # Save to cache
                    cache_file = Path("data/cache/ipo_calendar.json")
                    cache_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(cache_file, 'w') as f:
                        json.dump({
                            "updated": datetime.now().isoformat(),
                            "source": "iposcoop",
                            "data": ipos,
                            "count": len(ipos)
                        }, f, indent=2)
                    
                    logger.info(f"Updated calendar: {len(ipos)} IPOs")
                
            except Exception as e:
                logger.error(f"Scraping error: {e}")
            
            # Wait 30 minutes
            await asyncio.sleep(1800)
    
    def stop(self):
        """Stop scheduler"""
        self.running = False

if __name__ == "__main__":
    scheduler = SimpleScheduler()
    try:
        asyncio.run(scheduler.start())
    except KeyboardInterrupt:
        print("\nScheduler stopped")
