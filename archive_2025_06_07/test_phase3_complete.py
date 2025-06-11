#!/usr/bin/env python3
"""
Phase 3.1 Completion Test
Date: 2025-06-05 13:43:40 UTC
Author: thorrobber22

Final verification that admin panel is ready
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"{Colors.GREEN}✓{Colors.ENDC} {description} found at {filepath}")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.ENDC} {description} NOT FOUND at {filepath}")
        return False

def check_admin_functions():
    """Check if admin.py has all required functions"""
    print(f"\n{Colors.BLUE}Checking admin.py functions...{Colors.ENDC}")
    
    try:
        with open('admin.py', 'r') as f:
            content = f.read()
        
        required_functions = [
            "load_ipo_calendar",
            "get_document_coverage",
            "calculate_coverage_percentage",
            "get_uploaded_documents",
            "detect_document_type",
            "extract_ticker_from_filename",
            "categorize_ipo",
            "generate_sec_urls",
            "show_dashboard",
            "show_documents",
            "show_upload",
            "show_coverage_report"
        ]
        
        all_found = True
        for func in required_functions:
            if f"def {func}" in content:
                print(f"{Colors.GREEN}✓{Colors.ENDC} Function '{func}' found")
            else:
                print(f"{Colors.RED}✗{Colors.ENDC} Function '{func}' NOT FOUND")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.ENDC} Error reading admin.py: {e}")
        return False

def check_data_structure():
    """Check if data directories exist"""
    print(f"\n{Colors.BLUE}Checking data structure...{Colors.ENDC}")
    
    required_dirs = [
        "data",
        "data/documents",
        "data/processed",
        "data/cache",
        "data/vectors",
        "exports",
        "logs"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"{Colors.GREEN}✓{Colors.ENDC} Directory '{dir_path}' exists")
        else:
            print(f"{Colors.RED}✗{Colors.ENDC} Directory '{dir_path}' MISSING")
            all_exist = False
    
    return all_exist

def check_config():
    """Check if config.py exists and has required variables"""
    print(f"\n{Colors.BLUE}Checking configuration...{Colors.ENDC}")
    
    if not Path('config.py').exists():
        print(f"{Colors.RED}✗{Colors.ENDC} config.py NOT FOUND")
        return False
    
    try:
        import config
        required_attrs = [
            "BASE_DIR", "DATA_DIR", "DOCUMENTS_DIR", 
            "CACHE_DIR", "SUPPORTED_DOCUMENTS"
        ]
        
        all_found = True
        for attr in required_attrs:
            if hasattr(config, attr):
                print(f"{Colors.GREEN}✓{Colors.ENDC} Config has '{attr}'")
            else:
                print(f"{Colors.RED}✗{Colors.ENDC} Config missing '{attr}'")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.ENDC} Error importing config: {e}")
        return False

def main():
    """Run all checks"""
    print(f"{Colors.BOLD}\nHEDGE INTELLIGENCE - PHASE 3.1 COMPLETION CHECK{Colors.ENDC}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("="*60)
    
    all_checks = []
    
    # Check 1: Core files
    print(f"\n{Colors.BLUE}Checking core files...{Colors.ENDC}")
    all_checks.append(check_file_exists('admin.py', 'Admin panel'))
    all_checks.append(check_file_exists('config.py', 'Configuration'))
    all_checks.append(check_file_exists('requirements.txt', 'Requirements'))
    
    # Check 2: Admin functions
    all_checks.append(check_admin_functions())
    
    # Check 3: Data structure
    all_checks.append(check_data_structure())
    
    # Check 4: Configuration
    all_checks.append(check_config())
    
    # Summary
    print(f"\n{'='*60}")
    if all(all_checks):
        print(f"{Colors.GREEN}{Colors.BOLD}✅ PHASE 3.1 COMPLETE!{Colors.ENDC}")
        print(f"\n{Colors.GREEN}Admin panel is ready to use:{Colors.ENDC}")
        print("1. Run: streamlit run admin.py --server.port 8080")
        print("2. Login with password: hedgeadmin2025")
        print("3. Upload IPO documents")
        print(f"\n{Colors.GREEN}Ready for Phase 3.2: Document Processor{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ PHASE 3.1 INCOMPLETE{Colors.ENDC}")
        print("Please fix the issues above before proceeding")
        return 1

if __name__ == "__main__":
    sys.exit(main())
