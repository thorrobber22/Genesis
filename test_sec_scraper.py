#!/usr/bin/env python3
"""
Comprehensive Test Script for SEC-Compliant Document Scraper
Tests all major functionality and edge cases
"""

import asyncio
import json
import shutil
from pathlib import Path
from datetime import datetime
import logging
import sys

# Add parent directory to path if running from test directory
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.sec.sec_compliant_scraper import SECCompliantScraper

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sec_scraper_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SECScraperTester:
    def __init__(self):
        self.scraper = SECCompliantScraper()
        self.test_results = []
        self.test_data_dir = Path("test_data/sec_documents")
        
    def setup(self):
        """Setup test environment"""
        # Backup existing data if it exists
        if self.scraper.data_dir.exists():
            backup_dir = Path(f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copytree(self.scraper.data_dir, backup_dir)
            logger.info(f"Backed up existing data to {backup_dir}")
        
        # Use test directory for scraper
        self.scraper.data_dir = self.test_data_dir
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        
    def cleanup(self):
        """Cleanup test environment"""
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
            logger.info("Cleaned up test data")
    
    async def test_single_company(self, ticker: str, cik: str, expected_forms: list = None):
        """Test downloading documents for a single company"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 Testing {ticker} (CIK: {cik})")
        logger.info(f"{'='*60}")
        
        start_time = datetime.now()
        
        try:
            result = await self.scraper.scan_and_download_everything(ticker, cik)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            test_result = {
                'ticker': ticker,
                'cik': cik,
                'success': result.get('success', False),
                'duration_seconds': duration,
                'total_files': result.get('total_files', 0),
                'forms_downloaded': result.get('forms_downloaded', {}),
                'errors': result.get('errors', [])
            }
            
            # Verify results
            if result['success']:
                logger.info(f"✅ SUCCESS: Downloaded {result['total_files']} files in {duration:.1f} seconds")
                
                # Check if expected forms were downloaded
                if expected_forms:
                    forms_found = list(result.get('forms_downloaded', {}).keys())
                    missing_forms = [f for f in expected_forms if f not in forms_found]
                    if missing_forms:
                        logger.warning(f"⚠️  Missing expected forms: {missing_forms}")
                        test_result['missing_forms'] = missing_forms
                
                # Verify files exist
                ticker_dir = self.test_data_dir / ticker
                if ticker_dir.exists():
                    actual_files = list(ticker_dir.glob("*.html"))
                    metadata_files = list(ticker_dir.glob("*.json"))
                    
                    logger.info(f"📁 Found {len(actual_files)} HTML files and {len(metadata_files)} metadata files")
                    
                    # Verify file contents
                    valid_files = 0
                    invalid_files = []
                    
                    for file_path in actual_files[:5]:  # Check first 5 files
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            # Check for error indicators
                            if 'This page contains the following errors:' in content:
                                invalid_files.append(file_path.name)
                            elif len(content) < 1000:
                                invalid_files.append(file_path.name)
                            else:
                                valid_files += 1
                                
                        except Exception as e:
                            logger.error(f"Error reading {file_path}: {e}")
                            invalid_files.append(file_path.name)
                    
                    test_result['valid_files_checked'] = valid_files
                    test_result['invalid_files'] = invalid_files
                    
                    if invalid_files:
                        logger.warning(f"⚠️  Found {len(invalid_files)} invalid files: {invalid_files}")
                    else:
                        logger.info(f"✅ All checked files are valid")
                        
            else:
                logger.error(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ EXCEPTION: {str(e)}")
            test_result = {
                'ticker': ticker,
                'cik': cik,
                'success': False,
                'error': str(e),
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
        
        self.test_results.append(test_result)
        return test_result
    
    async def test_rate_limiting(self):
        """Test that rate limiting is working correctly"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 Testing Rate Limiting")
        logger.info(f"{'='*60}")
        
        # Make 3 requests and measure timing
        times = []
        
        async with self.scraper:
            for i in range(3):
                start = datetime.now()
                await self.scraper.wait_for_rate_limit()
                end = datetime.now()
                
                if i > 0:  # Skip first request
                    elapsed = (end - times[-1]).total_seconds()
                    logger.info(f"Request {i+1}: {elapsed:.1f} seconds since last request")
                    
                    if elapsed < self.scraper.rate_limit_delay:
                        logger.error(f"❌ Rate limit violated! Only {elapsed:.1f}s between requests")
                    else:
                        logger.info(f"✅ Rate limit respected")
                
                times.append(end)
    
    async def test_error_handling(self):
        """Test error handling with invalid inputs"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 Testing Error Handling")
        logger.info(f"{'='*60}")
        
        # Test with invalid CIK
        result = await self.test_single_company("INVALID", "0000000000")
        assert not result['success'], "Should fail with invalid CIK"
        
        # Test with malformed CIK
        result = await self.test_single_company("TEST", "ABC123")
        assert result['cik'] == "0000ABC123", "Should pad CIK to 10 digits"
    
    async def test_all_form_types(self):
        """Test downloading different form types"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 Testing Multiple Form Types")
        logger.info(f"{'='*60}")
        
        # Use a company known to have multiple form types
        result = await self.test_single_company(
            "TSLA", 
            "0001318605",  # Tesla
            expected_forms=['10-K', '10-Q', '8-K']
        )
        
        if result['success']:
            forms = result.get('forms_downloaded', {})
            logger.info(f"Downloaded form types: {list(forms.keys())}")
    
    async def test_document_validation(self):
        """Test that downloaded documents are valid"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 Testing Document Validation")
        logger.info(f"{'='*60}")
        
        # Download a small set of documents
        result = await self.test_single_company("AAPL", "0000320193")
        
        if result['success']:
            ticker_dir = self.test_data_dir / "AAPL"
            html_files = list(ticker_dir.glob("*.html"))
            
            validation_results = {
                'total_files': len(html_files),
                'valid': 0,
                'invalid': 0,
                'too_small': 0,
                'error_pages': 0
            }
            
            for file_path in html_files[:10]:  # Check first 10
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Validate content
                    if 'This page contains the following errors:' in content:
                        validation_results['error_pages'] += 1
                        logger.warning(f"❌ Error page: {file_path.name}")
                    elif len(content) < 1000:
                        validation_results['too_small'] += 1
                        logger.warning(f"❌ Too small: {file_path.name} ({len(content)} bytes)")
                    elif 'companysearch' in content.lower():
                        validation_results['invalid'] += 1
                        logger.warning(f"❌ Search page: {file_path.name}")
                    else:
                        validation_results['valid'] += 1
                        logger.info(f"✅ Valid: {file_path.name} ({len(content)//1024} KB)")
                        
                except Exception as e:
                    validation_results['invalid'] += 1
                    logger.error(f"❌ Error reading {file_path.name}: {e}")
            
            logger.info(f"\nValidation Summary: {validation_results}")
    
    async def run_all_tests(self):
        """Run all tests"""
        self.setup()
        
        try:
            # Test 1: Basic functionality with well-known companies
            logger.info("\n" + "="*80)
            logger.info("PHASE 1: Basic Functionality Tests")
            logger.info("="*80)
            
            test_companies = [
                ("AAPL", "0000320193"),  # Apple
                ("MSFT", "0000789019"),  # Microsoft
                ("GOOGL", "0001652044"), # Alphabet
            ]
            
            for ticker, cik in test_companies:
                await self.test_single_company(ticker, cik)
                await asyncio.sleep(15)  # Wait between companies
            
            # Test 2: Rate limiting
            logger.info("\n" + "="*80)
            logger.info("PHASE 2: Rate Limiting Test")
            logger.info("="*80)
            await self.test_rate_limiting()
            
            # Test 3: Error handling
            logger.info("\n" + "="*80)
            logger.info("PHASE 3: Error Handling Tests")
            logger.info("="*80)
            await self.test_error_handling()
            
            # Test 4: Document validation
            logger.info("\n" + "="*80)
            logger.info("PHASE 4: Document Validation")
            logger.info("="*80)
            await self.test_document_validation()
            
            # Generate test report
            self.generate_report()
            
        finally:
            self.cleanup()
    
    def generate_report(self):
        """Generate test report"""
        logger.info("\n" + "="*80)
        logger.info("TEST REPORT")
        logger.info("="*80)
        
        successful_tests = [r for r in self.test_results if r.get('success', False)]
        failed_tests = [r for r in self.test_results if not r.get('success', False)]
        
        logger.info(f"\n📊 Summary:")
        logger.info(f"  Total tests: {len(self.test_results)}")
        logger.info(f"  Successful: {len(successful_tests)}")
        logger.info(f"  Failed: {len(failed_tests)}")
        
        if successful_tests:
            logger.info(f"\n✅ Successful Tests:")
            for result in successful_tests:
                logger.info(f"  - {result['ticker']}: {result['total_files']} files in {result['duration_seconds']:.1f}s")
                if result.get('forms_downloaded'):
                    forms_summary = ', '.join([f"{k}({v})" for k, v in result['forms_downloaded'].items()])
                    logger.info(f"    Forms: {forms_summary}")
        
        if failed_tests:
            logger.info(f"\n❌ Failed Tests:")
            for result in failed_tests:
                logger.info(f"  - {result['ticker']}: {result.get('error', 'Unknown error')}")
        
        # Save detailed report
        report_path = Path("sec_scraper_test_report.json")
        with open(report_path, 'w') as f:
            json.dump({
                'test_date': datetime.now().isoformat(),
                'summary': {
                    'total': len(self.test_results),
                    'successful': len(successful_tests),
                    'failed': len(failed_tests)
                },
                'results': self.test_results
            }, f, indent=2)
        
        logger.info(f"\n📄 Detailed report saved to: {report_path}")

async def quick_test():
    """Quick test with just one company"""
    logger.info("Running quick test with Apple (AAPL)...")
    
    scraper = SECCompliantScraper()
    result = await scraper.scan_and_download_everything("AAPL", "0000320193")
    
    logger.info(f"\nResult: {json.dumps(result, indent=2)}")
    
    # Check downloaded files
    if result['success']:
        ticker_dir = scraper.data_dir / "AAPL"
        if ticker_dir.exists():
            files = list(ticker_dir.glob("*"))
            logger.info(f"\nDownloaded files:")
            for f in files[:10]:  # Show first 10
                logger.info(f"  - {f.name} ({f.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test SEC Scraper')
    parser.add_argument('--quick', action='store_true', help='Run quick test with one company')
    parser.add_argument('--full', action='store_true', help='Run full test suite')
    
    args = parser.parse_args()
    
    if args.quick:
        asyncio.run(quick_test())
    else:
        # Default to full test
        tester = SECScraperTester()
        asyncio.run(tester.run_all_tests())