#!/usr/bin/env python3
"""
Fix pipeline manager to properly use enhanced scraper
Date: 2025-06-06 21:46:22 UTC
Author: thorrobber22
"""

from pathlib import Path

# Read the pipeline manager
pipeline_file = Path("scrapers/sec/pipeline_manager.py")

with open(pipeline_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find where SECDocumentScraper is used
if "download_documents" in content:
    print("🔍 Found download_documents method")
    
    # Check if it's calling the right method
    if "scan_and_download_everything" not in content:
        print("❌ Not using enhanced scraper method!")
        
        # Replace the download call
        # Find the download_documents method
        start = content.find("async def download_documents")
        if start > -1:
            end = content.find("\n    async def", start + 1)
            if end == -1:
                end = content.find("\nclass", start + 1)
            if end == -1:
                end = len(content)
            
            # Replace the method
            new_method = '''async def download_documents(self, ticker: str, cik: str) -> dict:
        """Download all documents for a ticker using enhanced scraper"""
        print(f"🔍 Scanning SEC for {ticker} (CIK: {cik})")
        
        try:
            # Use the enhanced scraper method
            result = await self.sec_scraper.scan_and_download_everything(ticker, cik)
            
            if result['success']:
                print(f"  ✅ Downloaded {result['total_files']} files from {result['filings_downloaded']} filings")
                return {
                    'success': True,
                    'documents_count': result['total_files'],
                    'filings_count': result['filings_downloaded']
                }
            else:
                print(f"  ❌ Download failed: {result.get('error', 'Unknown error')}")
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            print(f"  ❌ Download error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
'''
            
            # Replace the method
            updated_content = content[:start] + new_method + "\n" + content[end:]
            
            # Save
            with open(pipeline_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("✅ Updated download_documents to use enhanced scraper")
    else:
        print("✅ Already using enhanced scraper")
else:
    print("❌ Could not find download_documents method")

# Also ensure the import is correct
if "from enhanced_sec_scraper import" not in content:
    # Fix the import
    lines = content.split('\n')
    import_index = -1
    
    for i, line in enumerate(lines):
        if "from sec_scraper import" in line or "import SECDocumentScraper" in line:
            import_index = i
            break
    
    if import_index > -1:
        lines[import_index] = "from enhanced_sec_scraper import EnhancedSECDocumentScraper as SECDocumentScraper"
        
        with open(pipeline_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print("✅ Fixed import statement")

print("\n🚀 Pipeline integration fixed!")