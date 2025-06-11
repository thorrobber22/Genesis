#!/usr/bin/env python3
"""
Test admin pipeline with detailed logging
Date: 2025-06-06 21:46:22 UTC
Author: thorrobber22
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "scrapers" / "sec"))

async def test_pipeline_processing():
    """Test the complete pipeline with logging"""
    logger.info("="*60)
    logger.info("🧪 TESTING PIPELINE PROCESSING")
    logger.info("="*60)
    
    try:
        # Import pipeline manager
        from scrapers.sec.pipeline_manager import IPOPipelineManager
        logger.info("✅ Imported IPOPipelineManager")
        
        # Check which scraper is being used
        from scrapers.sec import sec_scraper
        logger.info(f"📌 Using scraper module: {sec_scraper.__file__}")
        
        # Create manager
        manager = IPOPipelineManager()
        logger.info("✅ Created pipeline manager")
        
        # Load current data
        data = manager.load_pipeline_data()
        logger.info(f"📊 Current pipeline state:")
        logger.info(f"   - Pending: {len(data['pending'])}")
        logger.info(f"   - Active: {len(data['active'])}")
        logger.info(f"   - Completed: {len(data['completed'])}")
        
        # Show pending IPOs
        if data['pending']:
            logger.info("\n📋 Pending IPOs:")
            for ipo in data['pending']:
                logger.info(f"   • {ipo['ticker']} - {ipo['company_name']} (CIK: {ipo.get('cik', 'None')})")
        
        # Test processing one specific company
        test_ticker = "CRCL"
        test_cik = "0001876042"
        
        logger.info(f"\n🧪 Testing download for {test_ticker}")
        
        # Import scraper directly
        from scrapers.sec.enhanced_sec_scraper import EnhancedSECDocumentScraper
        scraper = EnhancedSECDocumentScraper()
        logger.info("✅ Created enhanced scraper instance")
        
        # Test the download
        logger.info(f"📥 Starting download for {test_ticker}...")
        result = await scraper.scan_and_download_everything(test_ticker, test_cik)
        
        logger.info(f"\n📊 Download Result:")
        logger.info(f"   - Success: {result['success']}")
        logger.info(f"   - Files downloaded: {result.get('total_files', 0)}")
        logger.info(f"   - Filings processed: {result.get('filings_downloaded', 0)}")
        
    except Exception as e:
        logger.error(f"❌ Error in pipeline test: {e}", exc_info=True)

async def test_single_ipo_processing():
    """Test processing a single IPO through the pipeline"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TESTING SINGLE IPO PROCESSING")
    logger.info("="*60)
    
    try:
        from scrapers.sec.pipeline_manager import IPOPipelineManager
        manager = IPOPipelineManager()
        
        # Get a pending IPO
        data = manager.load_pipeline_data()
        
        if data['pending']:
            test_ipo = data['pending'][0]
            logger.info(f"📍 Testing with: {test_ipo['ticker']} - {test_ipo['company_name']}")
            
            # Process it
            if 'cik' in test_ipo:
                logger.info(f"   CIK: {test_ipo['cik']}")
                
                # Call the download method directly
                from scrapers.sec.enhanced_sec_scraper import EnhancedSECDocumentScraper
                scraper = EnhancedSECDocumentScraper()
                
                result = await scraper.scan_and_download_everything(
                    test_ipo['ticker'],
                    test_ipo['cik']
                )
                
                logger.info(f"   Result: {result['success']}")
                if result['success']:
                    logger.info(f"   Downloaded: {result['total_files']} files")
                else:
                    logger.info(f"   Error: {result.get('error', 'Unknown')}")
            else:
                logger.info("   ❌ No CIK found - needs resolution first")
        else:
            logger.info("❌ No pending IPOs to test")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)

async def check_scraper_integration():
    """Check if the enhanced scraper is properly integrated"""
    logger.info("\n" + "="*60)
    logger.info("🔍 CHECKING SCRAPER INTEGRATION")
    logger.info("="*60)
    
    # Check files
    files_to_check = [
        "scrapers/sec/enhanced_sec_scraper.py",
        "scrapers/sec/sec_scraper.py",
        "scrapers/sec/pipeline_manager.py"
    ]
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            logger.info(f"✅ {file_path} exists")
            
            # Check content
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "enhanced_sec_scraper" in content.lower():
                logger.info(f"   ✅ References enhanced scraper")
            elif "EnhancedSECDocumentScraper" in content:
                logger.info(f"   ✅ Has enhanced scraper class")
            else:
                logger.warning(f"   ⚠️  May not be using enhanced scraper")
        else:
            logger.error(f"❌ {file_path} NOT FOUND")

async def main():
    """Run all tests"""
    logger.info(f"🚀 HEDGE INTELLIGENCE - Pipeline Diagnostic")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info(f"User: thorrobber22")
    
    # Run tests
    await check_scraper_integration()
    await test_pipeline_processing()
    await test_single_ipo_processing()
    
    logger.info("\n" + "="*60)
    logger.info("✅ DIAGNOSTIC COMPLETE")
    logger.info("Check pipeline_test.log for full details")

if __name__ == "__main__":
    asyncio.run(main())