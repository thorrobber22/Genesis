#!/usr/bin/env python3
"""
Diagnose why downloads are failing
Date: 2025-06-06 22:07:55 UTC
Author: thorrobber22
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pathlib import Path
import json

async def test_sec_download():
    """Test downloading a specific CRCL filing"""
    print("🔍 TESTING SEC DOWNLOAD ISSUE")
    print("="*60)
    
    # Test with a known CRCL filing
    cik = "0001876042"
    ticker = "CRCL"
    
    headers = {
        'User-Agent': 'Hedge Intelligence Bot (admin@hedgeintel.com)',
        'Accept': 'text/html,application/xhtml+xml'
    }
    
    # Step 1: Get the filings list
    print("\n1️⃣ Getting filings list...")
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&count=10"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find the filings table
                table = soup.find('table', class_='tableFile2')
                if table:
                    print("✅ Found filings table")
                    
                    # Get first filing with documents button
                    first_row = table.find('tr')
                    if first_row:
                        doc_button = first_row.find('a', id='documentsbutton')
                        if doc_button:
                            doc_url = "https://www.sec.gov" + doc_button['href']
                            print(f"✅ Found documents URL: {doc_url}")
                            
                            # Step 2: Get the documents page
                            print("\n2️⃣ Getting documents page...")
                            async with session.get(doc_url, headers=headers) as doc_response:
                                if doc_response.status == 200:
                                    doc_html = await doc_response.text()
                                    doc_soup = BeautifulSoup(doc_html, 'html.parser')
                                    
                                    # Find document table
                                    doc_table = doc_soup.find('table', class_='tableFile')
                                    if not doc_table:
                                        doc_table = doc_soup.find('table', summary='Document Format Files')
                                    
                                    if doc_table:
                                        print("✅ Found documents table")
                                        
                                        # Get all document rows
                                        rows = doc_table.find_all('tr')[1:]  # Skip header
                                        print(f"📄 Found {len(rows)} documents")
                                        
                                        # Try to download first HTML document
                                        for row in rows[:3]:  # Check first 3
                                            cells = row.find_all('td')
                                            if len(cells) >= 3:
                                                # Get the document link
                                                link_cell = cells[2]  # Usually 3rd column
                                                doc_link = link_cell.find('a')
                                                
                                                if doc_link and 'html' in doc_link.text.lower():
                                                    file_url = "https://www.sec.gov" + doc_link['href']
                                                    print(f"\n3️⃣ Testing download: {file_url}")
                                                    
                                                    # Try to download
                                                    async with session.get(file_url, headers=headers) as file_response:
                                                        if file_response.status == 200:
                                                            content = await file_response.read()
                                                            print(f"✅ Downloaded {len(content)} bytes")
                                                            
                                                            # Save test file
                                                            test_file = Path(f"test_download_{ticker}.html")
                                                            with open(test_file, 'wb') as f:
                                                                f.write(content)
                                                            print(f"✅ Saved to {test_file}")
                                                            
                                                            return True
                                                        else:
                                                            print(f"❌ Download failed: HTTP {file_response.status}")
                                    else:
                                        print("❌ Could not find documents table")
                                        print("Page structure:")
                                        print(doc_soup.find_all('table')[:2])
                                else:
                                    print(f"❌ Documents page failed: HTTP {doc_response.status}")
                        else:
                            print("❌ No documents button found")
                else:
                    print("❌ No filings table found")
            else:
                print(f"❌ Main page failed: HTTP {response.status}")
    
    return False

async def test_enhanced_scraper_debug():
    """Test enhanced scraper with debug output"""
    print("\n\n🔧 TESTING ENHANCED SCRAPER")
    print("="*60)
    
    from scrapers.sec.enhanced_sec_scraper import EnhancedSECDocumentScraper
    
    # Modify the scraper temporarily to add debug output
    scraper = EnhancedSECDocumentScraper()
    
    # Override the download method to add debugging
    original_download = scraper.download_filing_complete
    
    async def debug_download(filing, ticker):
        print(f"\n📥 DEBUG: Attempting to download {filing['type']} from {filing['date']}")
        print(f"   URL: {filing['url']}")
        
        result = await original_download(filing, ticker)
        
        if result['success']:
            print(f"   ✅ Success: {len(result['files'])} files")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
        
        return result
    
    scraper.download_filing_complete = debug_download
    
    # Test with CRCL
    result = await scraper.scan_and_download_everything("CRCL", "0001876042")
    
    print(f"\n📊 Final Result:")
    print(f"   Success: {result['success']}")
    print(f"   Files: {result.get('total_files', 0)}")
    
    return result

async def main():
    """Run all tests"""
    print("🚀 SEC DOWNLOAD DIAGNOSTIC")
    print(f"Time: 2025-06-06 22:07:55 UTC")
    print(f"User: thorrobber22")
    print("\n")
    
    # Test 1: Basic download
    success = await test_sec_download()
    
    if success:
        print("\n✅ Basic download works!")
    else:
        print("\n❌ Basic download failed")
    
    # Test 2: Enhanced scraper
    await test_enhanced_scraper_debug()
    
    print("\n\n💡 RECOMMENDATIONS:")
    print("1. Check if the document table structure has changed")
    print("2. Verify the download URLs are being constructed correctly")
    print("3. Check for rate limiting or blocking")

if __name__ == "__main__":
    asyncio.run(main())