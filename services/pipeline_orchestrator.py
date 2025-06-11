#!/usr/bin/env python3
"""
Pipeline Orchestrator - Fixed imports
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
import logging
import sys

# Fix the import path
sys.path.append(str(Path(__file__).parent.parent))

# Now import our components
from scrapers.ipo_scraper_real import IPOScraperReal
from scrapers.sec.sec_compliant_scraper import SECCompliantScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    def __init__(self):
        self.ipo_scraper = IPOScraperReal()
        self.sec_scraper = SECCompliantScraper()
        self.data_dir = Path("data")
        
    async def run_full_pipeline(self, auto_download=False):
        """Run the complete data pipeline"""
        logger.info("🚀 Starting Full Pipeline")
        logger.info("="*60)
        
        # Step 1: Scrape IPOs
        logger.info("\n📋 Step 1: Scraping IPOs from IPOScoop...")
        ipo_data = self.ipo_scraper.scrape_ipo_calendar()
        
        # Step 2: Look up CIKs
        logger.info("\n🔍 Step 2: Looking up CIKs...")
        ipo_data = self.ipo_scraper.lookup_ciks(ipo_data)
        
        # Step 3: Create company requests for new IPOs
        logger.info("\n📝 Step 3: Creating company requests...")
        requests_file = self.data_dir / "company_requests.json"
        
        # Load existing requests
        existing_requests = []
        if requests_file.exists():
            with open(requests_file, 'r') as f:
                existing_requests = json.load(f)
        
        # Get all IPOs with CIKs
        new_requests = []
        all_ipos = ipo_data.get('recently_priced', [])[:5]  # Top 5 recent
        all_ipos += ipo_data.get('upcoming', [])[:5]  # Top 5 upcoming
        
        for ipo in all_ipos:
            if ipo.get('cik') and ipo.get('ticker'):
                # Check if already requested
                already_exists = any(
                    req.get('ticker') == ipo['ticker'] 
                    for req in existing_requests
                )
                
                if not already_exists:
                    new_request = {
                        'ticker': ipo['ticker'],
                        'company_name': ipo.get('company_name', ''),
                        'cik': ipo['cik'],
                        'status': 'pending',
                        'priority': 'high' if 'recently_priced' in ipo.get('section', '') else 'normal',
                        'source': 'ipo_pipeline',
                        'timestamp': datetime.now().isoformat(),
                        'ipo_data': {
                            'price_range': ipo.get('price_range'),
                            'expected_date': ipo.get('expected_date'),
                            'exchange': ipo.get('exchange')
                        }
                    }
                    new_requests.append(new_request)
                    existing_requests.append(new_request)
        
        # Save updated requests
        with open(requests_file, 'w') as f:
            json.dump(existing_requests, f, indent=2)
        
        logger.info(f"✅ Added {len(new_requests)} new company requests")
        
        # Step 4: Auto-download if enabled
        if auto_download and new_requests:
            logger.info("\n📥 Step 4: Auto-downloading SEC documents...")
            
            for req in new_requests[:3]:  # Limit to 3 for testing
                logger.info(f"\nDownloading {req['ticker']}...")
                
                result = await self.sec_scraper.scan_and_download_everything(
                    req['ticker'],
                    req['cik']
                )
                
                if result['success']:
                    logger.info(f"✅ Downloaded {result['total_files']} files for {req['ticker']}")
                    
                    # Update request status
                    for r in existing_requests:
                        if r['ticker'] == req['ticker']:
                            r['status'] = 'completed'
                            r['documents_count'] = result['total_files']
                            r['completed_at'] = datetime.now().isoformat()
                            break
                else:
                    logger.error(f"❌ Failed to download {req['ticker']}: {result.get('error')}")
            
            # Save updated statuses
            with open(requests_file, 'w') as f:
                json.dump(existing_requests, f, indent=2)
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("📊 PIPELINE SUMMARY")
        logger.info("="*60)
        logger.info(f"IPOs Scraped: {len(all_ipos)}")
        logger.info(f"CIKs Found: {len([i for i in all_ipos if i.get('cik')])}")
        logger.info(f"New Requests: {len(new_requests)}")
        if auto_download:
            logger.info(f"Documents Downloaded: Yes")
        
        return {
            'ipo_data': ipo_data,
            'new_requests': new_requests,
            'summary': {
                'total_ipos': len(all_ipos),
                'with_ciks': len([i for i in all_ipos if i.get('cik')]),
                'new_requests': len(new_requests)
            }
        }

# Test it
if __name__ == "__main__":
    orchestrator = PipelineOrchestrator()
    
    # Run with auto-download disabled for testing
    asyncio.run(orchestrator.run_full_pipeline(auto_download=False))