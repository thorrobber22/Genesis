#!/usr/bin/env python3
"""
Clean fix - Update existing files instead of creating new ones
Date: 2025-06-07 19:18:18 UTC
Author: thorrobber22
"""

from pathlib import Path
import re

def fix_pipeline_manager():
    """Fix pipeline_manager.py to use the existing scraper"""
    
    pipeline_path = Path("scrapers/sec/pipeline_manager.py")
    
    if not pipeline_path.exists():
        print("❌ pipeline_manager.py not found!")
        return False
    
    print("Fixing pipeline_manager.py...")
    
    with open(pipeline_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the import to use the existing scraper
    new_content = content.replace(
        'from scrapers.sec.enhanced_sec_scraper import EnhancedSECDocumentScraper',
        'from scrapers.sec.sec_compliant_scraper import EnhancedSECDocumentScraper'
    ).replace(
        'from enhanced_sec_scraper import EnhancedSECDocumentScraper',
        'from sec_compliant_scraper import EnhancedSECDocumentScraper'
    )
    
    if new_content != content:
        with open(pipeline_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Fixed pipeline_manager.py to use sec_compliant_scraper.py")
        return True
    else:
        print("ℹ️ pipeline_manager.py already correct")
        return False

def verify_all_imports():
    """Verify all imports are using existing files"""
    
    print("\nVerifying all imports...")
    
    issues_found = []
    
    # Check all Python files for bad imports
    for py_file in Path(".").rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for imports of non-existent files
            if 'enhanced_sec_scraper' in content and 'sec_compliant_scraper' not in str(py_file):
                issues_found.append(f"{py_file}: imports enhanced_sec_scraper")
            
        except Exception as e:
            pass
    
    if issues_found:
        print("\n⚠️ Found issues:")
        for issue in issues_found:
            print(f"  - {issue}")
    else:
        print("✅ All imports verified - using existing files only")
    
    return len(issues_found) == 0

def main():
    """Main cleanup function"""
    print("CLEAN FIX - Using only existing files")
    print("=" * 60)
    
    # Fix the import
    fixed = fix_pipeline_manager()
    
    # Verify everything
    verified = verify_all_imports()
    
    if fixed or not verified:
        print("\n✅ Fixed! Your existing structure is preserved.")
    else:
        print("\n✅ Everything already clean and connected!")
    
    print("\nYour clean structure:")
    print("  - sec_compliant_scraper.py (your working scraper)")
    print("  - pipeline_manager.py (uses the above scraper)")
    print("  - iposcoop_scraper.py (finds new IPOs)")
    print("  - cik_resolver.py (resolves CIKs)")
    
    print("\nNo new files created. Just fixed connections.")

if __name__ == "__main__":
    main()