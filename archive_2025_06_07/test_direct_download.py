#!/usr/bin/env python3
"""
Test direct download to confirm it works
Date: 2025-06-06 22:24:58 UTC
Author: thorrobber22
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scrapers" / "sec"))

async def test():
    from working_sec_scraper import WorkingSECDocumentScraper
    
    scraper = WorkingSECDocumentScraper()
    
    print("Testing Circle (CRCL) download...")
    result = await scraper.scan_and_download_everything("CRCL", "0001876042")
    
    if result['success']:
        print(f"\n✅ SUCCESS! Downloaded {result['total_files']} files")
    else:
        print(f"\n❌ FAILED: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test())