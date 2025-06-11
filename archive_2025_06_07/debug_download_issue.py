#!/usr/bin/env python3
"""
Debug why downloads are failing
Date: 2025-06-06 22:27:06 UTC
Author: thorrobber22
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pathlib import Path

async def debug_single_filing():
    """Debug a single filing download"""
    print("🔍 DEBUG: Testing single filing download")
    print("="*60)
    
    # Test with a known CRCL 8-K filing
    test_url = "https://www.sec.gov/Archives/edgar/data/1876042/000095010325007107/0000950103-25-007107-index.htm"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml'
    }
    
    async with aiohttp.ClientSession() as session:
        print(f"\n1️⃣ Fetching: {test_url}")
        
        try:
            async with session.get(test_url, headers=headers) as response:
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    html = await response.text()
                    print(f"   Downloaded: {len(html)} bytes")
                    
                    # Parse the page
                    soup = BeautifulSoup(html, 'html.parser')
                    print(f"   Title: {soup.title.string if soup.title else 'No title'}")
                    
                    # Look for document links
                    print("\n2️⃣ Looking for document links...")
                    
                    # Method 1: Look for all tables
                    tables = soup.find_all('table')
                    print(f"   Found {len(tables)} tables")
                    
                    # Method 2: Look for all links
                    all_links = soup.find_all('a', href=True)
                    doc_links = [link for link in all_links if any(ext in link['href'] for ext in ['.htm', '.html', '.txt', '.xml'])]
                    print(f"   Found {len(doc_links)} document links")
                    
                    # Show first few links
                    for i, link in enumerate(doc_links[:5]):
                        print(f"   Link {i+1}: {link.get('href', 'No href')}")
                        print(f"          Text: {link.text.strip()}")
                    
                    # Try to find the actual document table
                    print("\n3️⃣ Looking for document table...")
                    
                    # Look for table by content
                    for table in tables:
                        # Check if table has document-related content
                        table_text = table.get_text()
                        if any(word in table_text.lower() for word in ['document', 'type', 'description']):
                            print("   Found potential document table!")
                            
                            # Get rows
                            rows = table.find_all('tr')
                            print(f"   Table has {len(rows)} rows")
                            
                            # Show first few rows
                            for j, row in enumerate(rows[:3]):
                                cells = row.find_all(['td', 'th'])
                                print(f"   Row {j}: {[cell.text.strip()[:30] for cell in cells]}")
                            
                            break
                    
                    # Save debug HTML
                    debug_file = Path("debug_filing_page.html")
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(html)
                    print(f"\n✅ Saved debug HTML to {debug_file}")
                    
                    return True
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

async def test_fixed_download():
    """Test a fixed download approach"""
    print("\n\n🔧 TESTING FIXED DOWNLOAD APPROACH")
    print("="*60)
    
    cik = "0001876042"
    
    # Get main filings page
    main_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&count=10"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; HedgeIntel/1.0)',
        'Accept': '*/*'
    }
    
    async with aiohttp.ClientSession() as session:
        # Get filings list
        async with session.get(main_url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find first filing link
                filing_link = None
                for link in soup.find_all('a', href=True):
                    if '/Archives/edgar/data/' in link['href'] and '-index.htm' in link['href']:
                        filing_link = 'https://www.sec.gov' + link['href']
                        break
                
                if filing_link:
                    print(f"Found filing: {filing_link}")
                    
                    # Get filing page
                    async with session.get(filing_link, headers=headers) as filing_response:
                        if filing_response.status == 200:
                            filing_html = await filing_response.text()
                            filing_soup = BeautifulSoup(filing_html, 'html.parser')
                            
                            # Find actual documents
                            doc_count = 0
                            for link in filing_soup.find_all('a', href=True):
                                href = link['href']
                                if '/Archives/edgar/data/' in href and any(ext in href for ext in ['.htm', '.txt', '.xml']):
                                    if '-index.htm' not in href:  # Skip index pages
                                        doc_url = 'https://www.sec.gov' + href if not href.startswith('http') else href
                                        print(f"\n📄 Found document: {href.split('/')[-1]}")
                                        
                                        # Try to download
                                        async with session.get(doc_url, headers=headers) as doc_response:
                                            if doc_response.status == 200:
                                                content = await doc_response.read()
                                                print(f"   ✅ Downloaded: {len(content)} bytes")
                                                doc_count += 1
                                                
                                                if doc_count >= 3:  # Just test first 3
                                                    break
                            
                            print(f"\n✅ Successfully downloaded {doc_count} documents")

async def main():
    """Run all debug tests"""
    await debug_single_filing()
    await test_fixed_download()

if __name__ == "__main__":
    asyncio.run(main())