#!/usr/bin/env python3
"""
Test the working scraper
Date: 2025-06-06 22:12:33 UTC
Author: thorrobber22
"""

import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "scrapers" / "sec"))

async def test():
    """Test with multiple companies"""
    from scrapers.sec.working_sec_scraper import WorkingSECDocumentScraper
    
    scraper = WorkingSECDocumentScraper()
    
    # Test companies
    test_cases = [
        ("CRCL", "0001876042"),  # Circle
        ("RDDT", "0001713445"),  # Reddit (known to have docs)
    ]
    
    for ticker, cik in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing {ticker}")
        print(f"{'='*60}")
        
        result = await scraper.scan_and_download_everything(ticker, cik)
        
        if result['success']:
            print(f"\n✅ SUCCESS: Downloaded {result['total_files']} files")
        else:
            print(f"\n❌ FAILED: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test())