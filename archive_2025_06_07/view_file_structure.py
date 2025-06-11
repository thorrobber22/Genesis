#!/usr/bin/env python3
"""
Quick view of downloaded file structure
Date: 2025-06-06 22:52:22 UTC
Author: thorrobber22
"""

from pathlib import Path
import json

def show_file_structure():
    """Display the file structure of downloaded documents"""
    sec_dir = Path("data/sec_documents")
    
    if not sec_dir.exists():
        print("❌ No SEC documents directory found")
        return
    
    print("📁 SEC DOCUMENTS FILE STRUCTURE")
    print("="*60)
    
    total_files = 0
    total_size = 0
    
    # Iterate through company directories
    companies = sorted([d for d in sec_dir.iterdir() if d.is_dir()])
    
    for company_dir in companies:
        files = list(company_dir.glob("*.*"))
        company_size = sum(f.stat().st_size for f in files)
        
        print(f"\n📂 {company_dir.name}/")
        
        # Check for metadata
        metadata_file = company_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            print(f"   ℹ️  Last scan: {metadata.get('last_scan', 'Unknown')[:19]}")
            print(f"   ℹ️  Total files: {metadata.get('total_files', len(files))}")
        
        # Group files by type
        file_types = {}
        for file in files:
            if file.name == "metadata.json":
                continue
            
            ext = file.suffix.lower()
            if ext not in file_types:
                file_types[ext] = []
            file_types[ext].append(file)
        
        # Show file breakdown
        for ext, ext_files in sorted(file_types.items()):
            ext_size = sum(f.stat().st_size for f in ext_files)
            print(f"   📄 {ext[1:].upper() if ext else 'FILES'}: {len(ext_files)} files ({ext_size/1024/1024:.1f} MB)")
            
            # Show first few files
            for f in sorted(ext_files)[:3]:
                print(f"      - {f.name} ({f.stat().st_size/1024:.0f} KB)")
            if len(ext_files) > 3:
                print(f"      ... and {len(ext_files) - 3} more")
        
        total_files += len(files)
        total_size += company_size
        
        print(f"   📊 Total: {len(files)} files ({company_size/1024/1024:.1f} MB)")
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY: {len(companies)} companies, {total_files} files, {total_size/1024/1024:.1f} MB total")

if __name__ == "__main__":
    show_file_structure()