#!/usr/bin/env python3
"""
fix_document_location.py - Move documents to correct location
"""

import shutil
from pathlib import Path
import json

def fix_document_locations():
    """Move documents from scraper location to app location"""
    print("🔧 FIXING DOCUMENT LOCATIONS")
    print("="*70)
    
    # Paths
    source_path = Path("scrapers/sec/data/sec_documents")
    dest_path = Path("data/sec_documents")
    
    if not source_path.exists():
        print(f"❌ Source path not found: {source_path}")
        return
    
    # Create destination if needed
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Move each company folder
    companies_moved = 0
    files_moved = 0
    
    for company_dir in source_path.iterdir():
        if company_dir.is_dir():
            company_name = company_dir.name
            dest_company = dest_path / company_name
            
            # Count files
            files = list(company_dir.glob("*.html"))
            
            print(f"\n{company_name}:")
            print(f"  Files to move: {len(files)}")
            
            if dest_company.exists():
                # Merge with existing
                print(f"  ⚠️  Destination exists, merging...")
                for file in files:
                    dest_file = dest_company / file.name
                    if not dest_file.exists():
                        shutil.copy2(file, dest_file)
                        files_moved += 1
            else:
                # Move entire directory
                shutil.move(str(company_dir), str(dest_company))
                files_moved += len(files)
                print(f"  ✅ Moved entire directory")
            
            companies_moved += 1
    
    print(f"\n📊 SUMMARY:")
    print(f"  Companies processed: {companies_moved}")
    print(f"  Files moved: {files_moved}")
    
    # Update scraper config to use correct path
    update_scraper_config()

def update_scraper_config():
    """Update scraper to save to correct location"""
    print("\n🔧 Updating scraper configuration...")
    
    scraper_path = Path("scrapers/sec/sec_compliant_scraper.py")
    
    if scraper_path.exists():
        try:
            with open(scraper_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Update the base path
            old_path = 'scrapers/sec/data/sec_documents'
            new_path = 'data/sec_documents'
            
            if old_path in content:
                content = content.replace(old_path, new_path)
                
                with open(scraper_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("  ✅ Updated scraper to use correct path")
            else:
                print("  ⚠️  Path not found in scraper, manual update needed")
                
        except Exception as e:
            print(f"  ❌ Error updating scraper: {e}")

def verify_documents():
    """Quick check of moved documents"""
    print("\n🔍 VERIFYING DOCUMENTS")
    print("="*70)
    
    app_path = Path("data/sec_documents")
    
    total_valid = 0
    for company_dir in app_path.iterdir():
        if company_dir.is_dir():
            files = list(company_dir.glob("*.html"))
            
            # Quick validation of first file
            valid = 0
            if files:
                try:
                    with open(files[0], 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if len(content) > 10000 and 'SECURITIES AND EXCHANGE' in content.upper():
                        valid = len(files)  # Assume all are valid if first is
                except:
                    pass
            
            total_valid += valid
            print(f"{company_dir.name}: {len(files)} files ({valid} appear valid)")
    
    print(f"\n✅ Total valid documents: {total_valid}")

if __name__ == "__main__":
    print("📂 DOCUMENT LOCATION FIX")
    print("This will move documents to the correct location")
    print("="*70)
    
    response = input("\nProceed with moving documents? (y/n): ")
    if response.lower() == 'y':
        fix_document_locations()
        verify_documents()
    else:
        print("Cancelled.")