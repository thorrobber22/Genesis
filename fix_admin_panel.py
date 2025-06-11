#!/usr/bin/env python3
"""
Fix admin panel to use the correct file
"""

from pathlib import Path
import shutil

def fix_admin_panel():
    """Fix admin panel to use the working version"""
    
    print("FIXING ADMIN PANEL")
    print("="*60)
    
    # The working admin panel
    admin_final = Path("admin/admin_final_browser.py")
    admin_main = Path("admin/admin_panel.py")
    
    if admin_final.exists():
        # Backup current
        if admin_main.exists():
            backup = Path("admin/admin_panel_broken.py")
            shutil.copy(admin_main, backup)
            print(f"✅ Backed up broken version to {backup}")
        
        # Copy working version
        shutil.copy(admin_final, admin_main)
        print(f"✅ Replaced with working admin_final_browser.py")
        
        # Also create a simple launcher
        launcher_content = '''#!/usr/bin/env python3
"""
Admin Panel Launcher
"""

import subprocess
import sys

if __name__ == "__main__":
    print("Starting SEC Pipeline Admin...")
    print("Password: hedgeadmin2025")
    print("-"*40)
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", "admin/admin_panel.py", "--server.port=8502"])
'''
        
        launcher = Path("run_admin.py")
        with open(launcher, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        print(f"✅ Created launcher: run_admin.py")
        
        return True
    else:
        print("❌ admin_final_browser.py not found!")
        print("Let me create a working admin panel from scratch...")
        
        # Create a working admin panel
        working_admin = '''#!/usr/bin/env python3
"""
SEC Pipeline Admin - Working Version
"""

import streamlit as st
import asyncio
from pathlib import Path
import json
from datetime import datetime
import sys

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the working scraper
from scrapers.sec.sec_compliant_scraper import SECCompliantScraper

st.set_page_config(page_title="SEC Pipeline Admin", page_icon="🏛️", layout="wide")

# Password protection
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🏛️ SEC Pipeline Admin")
    password = st.text_input("Password", type="password")
    if password == "hedgeadmin2025":
        st.session_state.authenticated = True
        st.rerun()
    else:
        if password:
            st.error("Invalid password")
        st.stop()

# Helper to run async
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Initialize
scraper = SECCompliantScraper()

# Header
st.title("🏛️ SEC Pipeline Admin")
st.caption("Manage company requests and download SEC documents")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Company Requests", "📥 Manual Download", "🔍 CIK Lookup", "📈 IPO Scraper"])

with tab1:
    st.header("Company Requests")
    
    # Load requests
    requests_file = Path("data/company_requests.json")
    if requests_file.exists():
        with open(requests_file, 'r', encoding='utf-8') as f:
            requests = json.load(f)
        
        # Filter pending
        pending = [r for r in requests if r.get('status') == 'pending']
        
        if pending:
            st.subheader(f"Pending Requests ({len(pending)})")
            
            for req in pending:
                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**{req.get('ticker', 'N/A')}**")
                    
                    with col2:
                        st.write(req.get('company_name', 'Unknown'))
                        st.caption(f"Priority: {req.get('priority', 'Normal')}")
                    
                    with col3:
                        st.caption(f"By: {req.get('requested_by', 'Unknown')}")
                        st.caption(req.get('timestamp', '')[:10])
                    
                    with col4:
                        if st.button("Process", key=f"proc_{req.get('ticker')}"):
                            # Need CIK first
                            st.info("Enter CIK below to process")
                            
                    # CIK input for this request
                    cik = st.text_input(f"CIK for {req.get('ticker')}", key=f"cik_{req.get('ticker')}")
                    
                    if cik and st.button(f"Download {req.get('ticker')}", key=f"dl_{req.get('ticker')}"):
                        with st.spinner(f"Downloading {req.get('ticker')}..."):
                            result = run_async(scraper.scan_and_download_everything(
                                req.get('ticker'),
                                cik
                            ))
                            
                            if result['success']:
                                st.success(f"✅ Downloaded {result['total_files']} files!")
                                
                                # Update request status
                                req['status'] = 'completed'
                                req['cik'] = cik
                                req['documents_count'] = result['total_files']
                                
                                # Save
                                with open(requests_file, 'w', encoding='utf-8') as f:
                                    json.dump(requests, f, indent=2)
                                
                                st.rerun()
                            else:
                                st.error(f"Failed: {result.get('error')}")
                    
                    st.divider()
        else:
            st.info("No pending requests")
    else:
        st.warning("No requests file found")

with tab2:
    st.header("Manual SEC Download")
    
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Ticker Symbol", placeholder="AAPL")
    with col2:
        cik = st.text_input("CIK Number", placeholder="0000320193")
    
    if st.button("📥 Download Documents", use_container_width=True, type="primary"):
        if ticker and cik:
            with st.spinner(f"Downloading {ticker}..."):
                result = run_async(scraper.scan_and_download_everything(
                    ticker.upper(),
                    cik
                ))
                
                if result['success']:
                    st.success(f"✅ Downloaded {result['total_files']} files for {ticker}!")
                    st.json(result['metadata'])
                else:
                    st.error(f"Failed: {result.get('error')}")
        else:
            st.warning("Please enter both ticker and CIK")

with tab3:
    st.header("CIK Lookup")
    
    company_name = st.text_input("Company Name", placeholder="Apple Inc")
    
    if st.button("🔍 Lookup CIK", use_container_width=True):
        if company_name:
            # Download company tickers
            import requests
            
            with st.spinner("Searching SEC database..."):
                try:
                    response = requests.get(
                        "https://www.sec.gov/files/company_tickers.json",
                        headers={'User-Agent': 'HedgeIntel admin@hedgeintel.com'}
                    )
                    
                    if response.status_code == 200:
                        tickers = response.json()
                        
                        # Search for company
                        matches = []
                        search_term = company_name.upper()
                        
                        for item in tickers.values():
                            if search_term in item.get('title', '').upper():
                                matches.append({
                                    'ticker': item.get('ticker'),
                                    'name': item.get('title'),
                                    'cik': str(item.get('cik_str')).zfill(10)
                                })
                        
                        if matches:
                            st.success(f"Found {len(matches)} matches:")
                            for match in matches[:10]:  # Show first 10
                                st.write(f"**{match['ticker']}** - {match['name']}")
                                st.code(f"CIK: {match['cik']}")
                        else:
                            st.warning("No matches found")
                    else:
                        st.error(f"SEC API error: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a company name")

with tab4:
    st.header("IPO Scraper")
    st.info("IPO scraping will be implemented here")
    
    if st.button("🔄 Scrape IPOScoop", use_container_width=True, type="primary"):
        st.warning("IPO scraper not yet implemented. Create services/ipo_scraper.py first.")
        
        # Show what would be scraped
        st.subheader("Target: IPOScoop.com")
        st.write("Would scrape from: https://www.iposcoop.com/ipo-calendar/")
        st.write("Sections to scrape:")
        st.write("- Recently Priced IPOs")
        st.write("- Upcoming IPOs")
        st.write("- Filed IPOs")

# Show current stats
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    sec_dir = Path("data/sec_documents")
    if sec_dir.exists():
        company_count = len([d for d in sec_dir.iterdir() if d.is_dir()])
        st.metric("Companies", company_count)

with col2:
    total_docs = 0
    if sec_dir.exists():
        for company in sec_dir.iterdir():
            if company.is_dir():
                total_docs += len(list(company.glob("*.html")))
    st.metric("Total Documents", total_docs)

with col3:
    if requests_file.exists():
        with open(requests_file, 'r', encoding='utf-8') as f:
            all_requests = json.load(f)
        pending_count = len([r for r in all_requests if r.get('status') == 'pending'])
        st.metric("Pending Requests", pending_count)
'''
        
        with open(admin_main, 'w', encoding='utf-8') as f:
            f.write(working_admin)
        
        print(f"✅ Created working admin panel")
        return True

if __name__ == "__main__":
    fix_admin_panel()