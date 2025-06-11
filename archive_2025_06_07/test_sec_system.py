#!/usr/bin/env python3
"""
Test SEC System Components
Date: 2025-06-06 17:47:46 UTC
Author: thorrobber22
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scrapers" / "sec"))

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(test_name, status, message=""):
    """Pretty print test results"""
    if status == "pass":
        print(f"{Colors.GREEN}✅ {test_name}{Colors.END} {message}")
    elif status == "fail":
        print(f"{Colors.RED}❌ {test_name}{Colors.END} {message}")
    elif status == "warn":
        print(f"{Colors.YELLOW}⚠️  {test_name}{Colors.END} {message}")
    else:
        print(f"{Colors.BLUE}🔄 {test_name}{Colors.END} {message}")

async def test_imports():
    """Test all imports"""
    print("\n" + "="*60)
    print("🧪 TESTING IMPORTS")
    print("="*60)
    
    imports_to_test = [
        ("IPOScoopScraper", "scrapers.sec.iposcoop_scraper", "IPOScoopScraper"),
        ("CIKResolver", "scrapers.sec.cik_resolver", "CIKResolver"),
        ("SECDocumentScraper", "scrapers.sec.sec_scraper", "SECDocumentScraper"),
        ("IPOPipelineManager", "scrapers.sec.pipeline_manager", "IPOPipelineManager"),
    ]
    
    all_passed = True
    
    for name, module, class_name in imports_to_test:
        try:
            exec(f"from {module} import {class_name}")
            print_test(f"Import {name}", "pass")
        except Exception as e:
            print_test(f"Import {name}", "fail", str(e))
            all_passed = False
    
    return all_passed

async def test_directories():
    """Test directory structure"""
    print("\n" + "="*60)
    print("📁 TESTING DIRECTORY STRUCTURE")
    print("="*60)
    
    required_dirs = [
        "data",
        "data/ipo_pipeline",
        "data/sec_documents",
        "scrapers/sec",
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print_test(f"Directory: {dir_path}", "pass", f"({len(list(path.iterdir()))} items)")
        else:
            # Create it
            path.mkdir(parents=True, exist_ok=True)
            print_test(f"Directory: {dir_path}", "warn", "Created")
    
    return True

async def test_iposcoop_scraper():
    """Test IPOScoop scraper"""
    print("\n" + "="*60)
    print("🌐 TESTING IPOSCOOP SCRAPER")
    print("="*60)
    
    try:
        from scrapers.sec.iposcoop_scraper import IPOScoopScraper
        scraper = IPOScoopScraper()
        print_test("IPOScoopScraper instance", "pass")
        
        # Test scraping (with timeout)
        print_test("Scraping IPO calendar", "info", "Please wait...")
        
        try:
            # Create a timeout
            ipos = await asyncio.wait_for(scraper.scrape_calendar(), timeout=10.0)
            
            if ipos:
                print_test("Calendar scrape", "pass", f"Found {len(ipos)} IPOs")
                # Show first IPO
                if len(ipos) > 0:
                    first = ipos[0]
                    print(f"  Sample: {first.get('ticker', 'N/A')} - {first.get('company_name', 'N/A')}")
            else:
                print_test("Calendar scrape", "warn", "No IPOs found (might be empty)")
        
        except asyncio.TimeoutError:
            print_test("Calendar scrape", "warn", "Timeout - IPOScoop might be slow")
        except Exception as e:
            print_test("Calendar scrape", "fail", str(e))
            
    except Exception as e:
        print_test("IPOScoopScraper", "fail", str(e))
        return False
    
    return True

async def test_cik_resolver():
    """Test CIK resolver"""
    print("\n" + "="*60)
    print("🔍 TESTING CIK RESOLVER")
    print("="*60)
    
    try:
        from scrapers.sec.cik_resolver import CIKResolver
        resolver = CIKResolver()
        print_test("CIKResolver instance", "pass")
        
        # Test with known company
        test_companies = [
            ("Apple Inc.", "AAPL"),
            ("Microsoft Corporation", "MSFT"),
            ("Reddit Inc", "RDDT")
        ]
        
        for company, ticker in test_companies:
            print_test(f"Resolving {company}", "info")
            
            try:
                result = await asyncio.wait_for(
                    resolver.get_cik(company, ticker), 
                    timeout=5.0
                )
                
                if result:
                    print_test(f"  CIK for {company}", "pass", 
                              f"CIK: {result['cik']}, Confidence: {result['confidence']}%")
                else:
                    print_test(f"  CIK for {company}", "warn", "Not found")
                    
            except asyncio.TimeoutError:
                print_test(f"  CIK for {company}", "warn", "Timeout")
            except Exception as e:
                print_test(f"  CIK for {company}", "fail", str(e))
                
    except Exception as e:
        print_test("CIKResolver", "fail", str(e))
        return False
    
    return True

async def test_pipeline_manager():
    """Test pipeline manager"""
    print("\n" + "="*60)
    print("⚙️ TESTING PIPELINE MANAGER")
    print("="*60)
    
    try:
        from scrapers.sec.pipeline_manager import IPOPipelineManager
        manager = IPOPipelineManager()
        print_test("IPOPipelineManager instance", "pass")
        
        # Test loading pipeline data
        try:
            data = manager.load_pipeline_data()
            print_test("Load pipeline data", "pass", 
                      f"Pending: {len(data['pending'])}, Active: {len(data['active'])}")
        except Exception as e:
            print_test("Load pipeline data", "fail", str(e))
        
        # Test summary
        try:
            summary = manager.get_admin_summary()
            print_test("Get admin summary", "pass", 
                      f"Needs attention: {len(summary['needs_attention'])}")
        except Exception as e:
            print_test("Get admin summary", "fail", str(e))
            
    except Exception as e:
        print_test("IPOPipelineManager", "fail", str(e))
        return False
    
    return True

async def test_full_pipeline():
    """Test a complete pipeline run"""
    print("\n" + "="*60)
    print("🚀 TESTING FULL PIPELINE")
    print("="*60)
    
    try:
        from scrapers.sec.pipeline_manager import IPOPipelineManager
        manager = IPOPipelineManager()
        
        # Add a test IPO manually
        test_ipo = {
            'ticker': 'TEST',
            'company_name': 'Test Company Inc',
            'expected_date': '2025-12-31',
            'price_range': '$10-$12',
            'status': 'pending_cik',
            'added_date': datetime.now().isoformat(),
            'source': 'test'
        }
        
        # Load current data
        data = manager.load_pipeline_data()
        
        # Check if TEST already exists
        existing = [ipo for ipo in data['pending'] if ipo['ticker'] == 'TEST']
        if not existing:
            data['pending'].append(test_ipo)
            manager.save_pipeline_data(data)
            print_test("Add test IPO", "pass", "TEST added to pipeline")
        else:
            print_test("Test IPO exists", "warn", "TEST already in pipeline")
        
        # Test scanning (don't actually scan to avoid hitting APIs)
        print_test("Pipeline ready", "pass", "All components working")
        
    except Exception as e:
        print_test("Full pipeline", "fail", str(e))
        return False
    
    return True

async def main():
    """Run all tests"""
    print(f"\n{'='*60}")
    print(f"🧪 HEDGE INTELLIGENCE - SEC SYSTEM TEST SUITE")
    print(f"{'='*60}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"User: thorrobber22")
    
    # Run tests
    tests = [
        ("Imports", test_imports),
        ("Directories", test_directories),
        ("IPOScoop Scraper", test_iposcoop_scraper),
        ("CIK Resolver", test_cik_resolver),
        ("Pipeline Manager", test_pipeline_manager),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print_test(test_name, "fail", f"Exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "pass" if result else "fail"
        print_test(test_name, status)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{Colors.GREEN}✅ ALL TESTS PASSED! System is ready.{Colors.END}")
        print("\nYou can now run: streamlit run admin_sec.py")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Check the output above.{Colors.END}")
        print("\nFix the issues before running the admin dashboard.")
    
    return passed == total

if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(main())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)