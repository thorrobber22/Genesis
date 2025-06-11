#!/usr/bin/env python3
"""
Simple test of SEC pipeline
"""

import sys
from pathlib import Path

# Add both possible paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scrapers" / "sec"))

# Now import
from scrapers.sec.iposcoop_scraper import IPOScoopScraper
from scrapers.sec.cik_resolver import CIKResolver
from scrapers.sec.sec_scraper import SECDocumentScraper
from scrapers.sec.pipeline_manager import IPOPipelineManager

import asyncio

async def test():
    print("✅ All imports successful!")
    
    # Test IPOScoop scraper
    print("\n🧪 Testing IPOScoop scraper...")
    scraper = IPOScoopScraper()
    print("   ✅ IPOScoopScraper initialized")
    
    # Test CIK resolver
    print("\n🧪 Testing CIK resolver...")
    resolver = CIKResolver()
    print("   ✅ CIKResolver initialized")
    
    # Test SEC scraper
    print("\n🧪 Testing SEC scraper...")
    sec = SECDocumentScraper()
    print("   ✅ SECDocumentScraper initialized")
    
    # Test pipeline manager
    print("\n🧪 Testing pipeline manager...")
    manager = IPOPipelineManager()
    summary = manager.get_admin_summary()
    print(f"   ✅ Pipeline status: {summary}")

if __name__ == "__main__":
    asyncio.run(test())
