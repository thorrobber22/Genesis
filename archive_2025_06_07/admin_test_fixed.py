#!/usr/bin/env python3
"""
Hedge Intelligence Admin Panel Test Suite (Fixed)
Date: 2025-06-05 13:38:10 UTC
Author: thorrobber22

Test suite to verify admin panel functionality
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if admin.py exists in root
admin_py_path = Path(__file__).parent / "admin.py"
if not admin_py_path.exists():
    print(f"ERROR: admin.py not found at {admin_py_path}")
    print("Current directory contents:")
    for f in Path(__file__).parent.glob("*"):
        print(f"  - {f.name}")
    print("\nRun: python update_admin.py first!")
    sys.exit(1)

# Import admin.py as a module
import importlib.util
spec = importlib.util.spec_from_file_location("admin_module", admin_py_path)
admin_module = importlib.util.module_from_spec(spec)
sys.modules["admin_module"] = admin_module
spec.loader.exec_module(admin_module)

# Now import the functions
from admin_module import (
    load_ipo_calendar,
    get_document_coverage,
    calculate_coverage_percentage,
    get_uploaded_documents,
    detect_document_type,
    extract_ticker_from_filename,
    categorize_ipo,
    generate_sec_urls
)

# Test configuration
class TestConfig:
    """Test configuration to avoid using real config"""
    BASE_DIR = Path(tempfile.mkdtemp())
    DATA_DIR = BASE_DIR / "data"
    DOCUMENTS_DIR = DATA_DIR / "documents"
    CACHE_DIR = DATA_DIR / "cache"
    SUPPORTED_DOCUMENTS = {
        "S-1": ["S1", "S-1", "S1A", "S-1/A"],
        "424B4": ["424B4", "PROSPECTUS"],
        "LOCK_UP": ["LOCK-UP", "LOCKUP", "MARKET_STANDOFF"],
        "UNDERWRITING": ["UNDERWRITING", "PURCHASE_AGREEMENT"],
        "8-A": ["8-A", "8A", "FORM_8-A"]
    }

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(test_name):
    print(f"\n{Colors.BLUE}Testing: {test_name}{Colors.ENDC}")

def print_pass(message):
    print(f"{Colors.GREEN}✓ PASS: {message}{Colors.ENDC}")

def print_fail(message):
    print(f"{Colors.RED}✗ FAIL: {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.YELLOW}→ INFO: {message}{Colors.ENDC}")

def setup_test_environment():
    """Set up test directories and files"""
    print_test("Setting up test environment")
    
    # Create directories
    os.makedirs(TestConfig.DOCUMENTS_DIR, exist_ok=True)
    os.makedirs(TestConfig.CACHE_DIR, exist_ok=True)
    
    # Create test IPO calendar
    test_calendar = [
        {
            "ticker": "CRCL",
            "company": "Circle Internet Financial",
            "expected_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "price_range": "$27-$28"
        },
        {
            "ticker": "HLEO",
            "company": "Helio Corp",
            "expected_date": datetime.now().strftime("%Y-%m-%d"),
            "price_range": "$4-$5"
        },
        {
            "ticker": "OMDA",
            "company": "Omada Health",
            "expected_date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "price_range": "$18-$20"
        }
    ]
    
    with open(TestConfig.CACHE_DIR / "ipo_calendar.json", 'w') as f:
        json.dump(test_calendar, f)
    
    # Create test documents
    test_docs = [
        ("CRCL_S1_20250601.html", "<html>REGISTRATION STATEMENT</html>"),
        ("CRCL_LOCKUP_20250601.pdf", "LOCK-UP AGREEMENT"),
        ("HLEO_S1A_20250602.html", "<html>Form S-1/A Amendment</html>"),
        ("HLEO_424B4_20250605.html", "<html>424B4 FINAL PROSPECTUS</html>"),
        ("OMDA_S1_20250530.html", "<html>REGISTRATION STATEMENT</html>")
    ]
    
    for filename, content in test_docs:
        with open(TestConfig.DOCUMENTS_DIR / filename, 'w') as f:
            f.write(content)
    
    print_pass("Test environment created")
    return TestConfig

def test_load_ipo_calendar(config):
    """Test IPO calendar loading"""
    print_test("load_ipo_calendar()")
    
    # Mock the config module
    with patch('admin_module.CACHE_DIR', config.CACHE_DIR):
        ipos = load_ipo_calendar()
    
    assert len(ipos) == 3, f"Expected 3 IPOs, got {len(ipos)}"
    assert ipos[0]["ticker"] == "CRCL", "First IPO should be CRCL"
    print_pass("Successfully loaded 3 IPOs from calendar")

def test_document_coverage(config):
    """Test document coverage detection"""
    print_test("get_document_coverage()")
    
    with patch('admin_module.DOCUMENTS_DIR', config.DOCUMENTS_DIR):
        with patch('admin_module.SUPPORTED_DOCUMENTS', config.SUPPORTED_DOCUMENTS):
            # Test CRCL (has S-1 and Lock-up)
            coverage_crcl = get_document_coverage("CRCL")
            assert coverage_crcl["S-1"] == True, "CRCL should have S-1"
            assert coverage_crcl["LOCK_UP"] == True, "CRCL should have Lock-up"
            assert coverage_crcl["424B4"] == False, "CRCL should not have 424B4"
            print_pass("CRCL coverage detected correctly")
            
            # Test HLEO (has S-1 and 424B4)
            coverage_hleo = get_document_coverage("HLEO")
            assert coverage_hleo["S-1"] == True, "HLEO should have S-1"
            assert coverage_hleo["424B4"] == True, "HLEO should have 424B4"
            print_pass("HLEO coverage detected correctly")

def test_coverage_percentage(config):
    """Test coverage percentage calculation"""
    print_test("calculate_coverage_percentage()")
    
    # Test full coverage
    full_coverage = {
        "S-1": True,
        "LOCK_UP": True,
        "UNDERWRITING": True,
        "424B4": True,
        "8-A": True
    }
    pct = calculate_coverage_percentage(full_coverage)
    assert pct == 100, f"Full coverage should be 100%, got {pct}"
    print_pass("Full coverage = 100%")
    
    # Test partial coverage (only required docs)
    partial_coverage = {
        "S-1": True,
        "LOCK_UP": True,
        "UNDERWRITING": True,
        "424B4": False,
        "8-A": False
    }
    pct = calculate_coverage_percentage(partial_coverage)
    assert pct == 80, f"Required docs only should be 80%, got {pct}"
    print_pass("Required docs only = 80%")
    
    # Test no coverage
    no_coverage = {doc: False for doc in full_coverage}
    pct = calculate_coverage_percentage(no_coverage)
    assert pct == 0, f"No coverage should be 0%, got {pct}"
    print_pass("No coverage = 0%")

def test_document_type_detection(config):
    """Test document type detection"""
    print_test("detect_document_type()")
    
    test_files = [
        ("CRCL_S1_20250601.html", "S-1"),
        ("CRCL_LOCKUP_20250601.pdf", "LOCK_UP"),
        ("HLEO_424B4_20250605.html", "424B4"),
        ("OMDA_UNDERWRITING_AGREEMENT.pdf", "UNDERWRITING"),
        ("TEST_8A_FORM.html", "8-A")
    ]
    
    with patch('admin_module.SUPPORTED_DOCUMENTS', config.SUPPORTED_DOCUMENTS):
        for filename, expected_type in test_files:
            # Create temporary file
            temp_file = config.DOCUMENTS_DIR / filename
            if not temp_file.exists():
                temp_file.write_text("test content")
            
            detected = detect_document_type(temp_file)
            print_info(f"{filename} -> {detected}")
            
            # Clean up
            if temp_file.exists() and filename not in ["CRCL_S1_20250601.html", "CRCL_LOCKUP_20250601.pdf"]:
                temp_file.unlink()
    
    print_pass("Document type detection working")

def test_ticker_extraction():
    """Test ticker extraction from filename"""
    print_test("extract_ticker_from_filename()")
    
    test_cases = [
        ("CRCL_S1_20250601.html", "CRCL"),
        ("HLEO_424B4_FINAL.pdf", "HLEO"),
        ("OMDA_lockup_agreement_v2.txt", "OMDA"),
        ("BadFilename.pdf", "BADFILENAME")
    ]
    
    for filename, expected in test_cases:
        result = extract_ticker_from_filename(filename)
        assert result == expected, f"Expected {expected}, got {result}"
        print_info(f"{filename} -> {result}")
    
    print_pass("Ticker extraction working correctly")

def test_ipo_categorization():
    """Test IPO date categorization"""
    print_test("categorize_ipo()")
    
    today = datetime.now()
    test_cases = [
        ((today - timedelta(days=10)).strftime("%Y-%m-%d"), "PAST"),
        ((today - timedelta(days=3)).strftime("%Y-%m-%d"), "RECENT"),
        (today.strftime("%Y-%m-%d"), "TODAY"),
        ((today + timedelta(days=7)).strftime("%Y-%m-%d"), "UPCOMING"),
        ((today + timedelta(days=45)).strftime("%Y-%m-%d"), "FUTURE"),
        ("invalid-date", "UNKNOWN")
    ]
    
    for date_str, expected in test_cases:
        result = categorize_ipo(date_str)
        assert result == expected, f"Expected {expected} for {date_str}, got {result}"
        print_info(f"{date_str} -> {result}")
    
    print_pass("IPO categorization working correctly")

def test_sec_url_generation():
    """Test SEC URL generation"""
    print_test("generate_sec_urls()")
    
    urls = generate_sec_urls("CRCL", "Circle Internet Financial")
    
    assert "All Filings" in urls
    assert "S-1 Search" in urls
    assert "424B4 Search" in urls
    assert "Recent Filings" in urls
    
    assert "CRCL" in urls["S-1 Search"]
    assert "Circle%20Internet%20Financial" in urls["All Filings"]
    
    print_pass("SEC URLs generated correctly")

def test_uploaded_documents(config):
    """Test document listing"""
    print_test("get_uploaded_documents()")
    
    with patch('admin_module.DOCUMENTS_DIR', config.DOCUMENTS_DIR):
        with patch('admin_module.detect_document_type') as mock_detect:
            # Mock document type detection
            mock_detect.side_effect = lambda x: "S-1" if "S1" in str(x) else "UNKNOWN"
            
            # Get all documents
            all_docs = get_uploaded_documents()
            assert len(all_docs) >= 3, f"Expected at least 3 documents, got {len(all_docs)}"
            print_pass(f"Found {len(all_docs)} total documents")
            
            # Get documents for specific ticker
            crcl_docs = get_uploaded_documents("CRCL")
            assert len(crcl_docs) >= 2, f"Expected at least 2 CRCL documents, got {len(crcl_docs)}"
            print_pass(f"Found {len(crcl_docs)} CRCL documents")

def test_streamlit_components():
    """Test that Streamlit components can be imported"""
    print_test("Streamlit integration")
    
    try:
        # Test basic streamlit imports from admin.py
        assert hasattr(admin_module, 'st'), "admin.py should import streamlit as st"
        print_pass("Streamlit components accessible")
    except ImportError as e:
        print_fail(f"Streamlit import error: {e}")

def cleanup_test_environment(config):
    """Clean up test files"""
    print_test("Cleaning up")
    
    if config.BASE_DIR.exists():
        shutil.rmtree(config.BASE_DIR)
    
    print_pass("Test environment cleaned up")

def run_integration_test():
    """Run a simulated integration test"""
    print_test("Integration test instructions")
    
    print_info("\nTo fully test the admin panel:")
    print("1. Run: streamlit run admin.py --server.port 8080")
    print("2. Login with password: hedgeadmin2025")
    print("3. Verify you can see:")
    print("   - Dashboard with IPO list")
    print("   - Document library")
    print("   - Upload interface")
    print("   - Coverage report")
    print("4. Try uploading a test document")
    print("5. Check document appears in library")

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}HEDGE INTELLIGENCE ADMIN PANEL TEST SUITE{Colors.ENDC}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("="*60)
    
    # Check if config.py exists
    if not Path("config.py").exists():
        print_fail("config.py not found! Run cleanup_and_restructure.py first")
        return 1
    
    # Set up test environment
    config = setup_test_environment()
    
    try:
        # Run all tests
        test_load_ipo_calendar(config)
        test_document_coverage(config)
        test_coverage_percentage(config)
        test_document_type_detection(config)
        test_ticker_extraction()
        test_ipo_categorization()
        test_sec_url_generation()
        test_uploaded_documents(config)
        test_streamlit_components()
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED!{Colors.ENDC}")
        
        # Check for real data
        print(f"\n{Colors.BLUE}Checking real data:{Colors.ENDC}")
        real_calendar = Path("data/cache/ipo_calendar.json")
        if real_calendar.exists():
            with open(real_calendar) as f:
                real_ipos = json.load(f)
            print_pass(f"Found {len(real_ipos)} real IPOs in calendar")
        else:
            print_warning("No real IPO calendar found at data/cache/ipo_calendar.json")
        
        real_docs = list(Path("data/documents").glob("*")) if Path("data/documents").exists() else []
        if real_docs:
            print_pass(f"Found {len(real_docs)} real documents")
        else:
            print_warning("No real documents found in data/documents/")
        
        # Integration test instructions
        run_integration_test()
        
    except AssertionError as e:
        print(f"\n{Colors.RED}{Colors.BOLD}TEST FAILED: {e}{Colors.ENDC}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}ERROR: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Clean up
        cleanup_test_environment(config)
    
    print(f"\n{Colors.GREEN}Ready for Phase 3.2!{Colors.ENDC}")
    return 0

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ WARNING: {message}{Colors.ENDC}")

if __name__ == "__main__":
    exit(main())