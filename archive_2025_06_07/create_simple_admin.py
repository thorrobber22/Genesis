#!/usr/bin/env python3
"""
Create simple, focused admin that actually works
Date: 2025-06-06 22:24:58 UTC
Author: thorrobber22
"""

from pathlib import Path

admin_content = '''#!/usr/bin/env python3
"""
Simple SEC Pipeline Admin - Focus on Downloads
"""

import streamlit as st
import asyncio
from pathlib import Path
import json
from datetime import datetime
import sys

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "scrapers" / "sec"))

# Import working scraper directly
from scrapers.sec.working_sec_scraper import WorkingSECDocumentScraper
from scrapers.sec.pipeline_manager import IPOPipelineManager

st.set_page_config(page_title="SEC Pipeline Admin", page_icon="🏛️", layout="wide")

# Password
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🏛️ SEC Pipeline Admin")
    if st.text_input("Password", type="password") == "hedgeadmin2025":
        st.session_state.authenticated = True
        st.rerun()
    st.stop()

# Helper function
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Initialize
manager = IPOPipelineManager()
scraper = WorkingSECDocumentScraper()

# Header
st.title("🏛️ SEC Pipeline Admin")
st.caption(f"Working Scraper v4.0 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

# Load data
data = manager.load_pipeline_data()

# Action buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Scan for New IPOs", use_container_width=True):
        with st.spinner("Scanning IPOScoop..."):
            count = run_async(manager.scan_new_ipos())
            st.success(f"Found {count} new IPOs")
            st.rerun()

with col2:
    if st.button("⚡ Process All Pending", use_container_width=True):
        with st.spinner("Processing..."):
            run_async(manager.process_pending_ipos())
            st.success("Processing complete")
            st.rerun()

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Pending", len(data['pending']))
with col2:
    st.metric("Active", len(data['active']))
with col3:
    st.metric("Completed", len(data['completed']))
with col4:
    total_docs = sum(ipo.get('documents_count', 0) for ipo in data['active'] + data['completed'])
    st.metric("Total Docs", total_docs)

# Main content
tab1, tab2 = st.tabs(["🔄 Process IPOs", "📊 Downloaded Documents"])

with tab1:
    st.subheader("Pending IPOs")
    
    if data['pending']:
        for ipo in data['pending']:
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                
                with col1:
                    st.write(f"**{ipo['ticker']}**")
                
                with col2:
                    st.write(ipo['company_name'])
                
                with col3:
                    if 'cik' in ipo:
                        st.caption(f"CIK: {ipo['cik']}")
                    else:
                        st.caption("No CIK")
                
                with col4:
                    if st.button("Download", key=f"dl_{ipo['ticker']}"):
                        if 'cik' in ipo:
                            with st.spinner(f"Downloading {ipo['ticker']}..."):
                                # Use the working scraper directly
                                result = run_async(scraper.scan_and_download_everything(
                                    ipo['ticker'], 
                                    ipo['cik']
                                ))
                                
                                if result['success']:
                                    st.success(f"✅ Downloaded {result['total_files']} files")
                                    
                                    # Update IPO status
                                    ipo['documents_count'] = result['total_files']
                                    ipo['filings_count'] = result['filings_downloaded']
                                    ipo['status'] = 'active'
                                    
                                    # Move to active
                                    data['pending'].remove(ipo)
                                    data['active'].append(ipo)
                                    manager.save_pipeline_data(data)
                                    
                                    st.rerun()
                                else:
                                    st.error(f"Failed: {result.get('error', 'Unknown error')}")
                        else:
                            st.error("Need CIK first")
                
                st.divider()
    else:
        st.info("No pending IPOs. Click 'Scan for New IPOs' to find some.")
    
    # Active IPOs
    st.subheader("Active IPOs")
    
    if data['active']:
        for ipo in data['active']:
            col1, col2, col3 = st.columns([1, 3, 2])
            with col1:
                st.write(f"**{ipo['ticker']}**")
            with col2:
                st.write(ipo['company_name'])
            with col3:
                st.caption(f"📄 {ipo.get('documents_count', 0)} documents")

with tab2:
    st.subheader("Downloaded Documents")
    
    # Manual download section
    st.markdown("#### Manual Download")
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        ticker = st.text_input("Ticker", placeholder="CRCL")
    with col2:
        cik = st.text_input("CIK", placeholder="0001876042")
    with col3:
        st.write("")  # Spacer
        if st.button("Download Now", use_container_width=True):
            if ticker and cik:
                with st.spinner(f"Downloading {ticker}..."):
                    result = run_async(scraper.scan_and_download_everything(ticker.upper(), cik))
                    
                    if result['success']:
                        st.success(f"✅ Downloaded {result['total_files']} files from {result['filings_downloaded']} filings")
                        st.json(result['metadata'])
                    else:
                        st.error(f"Failed: {result.get('error', 'Unknown error')}")
    
    st.divider()
    
    # Browse downloaded files
    st.markdown("#### Downloaded Files")
    sec_dir = Path("data/sec_documents")
    
    if sec_dir.exists():
        tickers = sorted([d.name for d in sec_dir.iterdir() if d.is_dir()])
        
        if tickers:
            selected = st.selectbox("Select Company", tickers)
            
            if selected:
                ticker_dir = sec_dir / selected
                
                # Load metadata
                metadata_file = ticker_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Files", metadata.get('total_files', 0))
                    with col2:
                        st.metric("Filings", metadata.get('total_filings', 0))
                    with col3:
                        st.metric("Last Scan", metadata.get('last_scan', 'Never')[:10])
                
                # List files
                files = list(ticker_dir.glob("*.*"))
                st.write(f"**Files ({len(files)}):**")
                
                for file in sorted(files)[:20]:  # Show first 20
                    if file.suffix in ['.html', '.htm', '.txt', '.xml']:
                        st.caption(f"📄 {file.name} ({file.stat().st_size // 1024} KB)")
        else:
            st.info("No documents downloaded yet")

# Footer
st.divider()
st.caption("🏛️ SEC Pipeline • Working Scraper v4.0")
'''

# Save
with open("admin_simple.py", 'w', encoding='utf-8') as f:
    f.write(admin_content)

print("✅ Created admin_simple.py - Simple focused admin")