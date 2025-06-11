#!/usr/bin/env python3
"""
SEC Pipeline Admin Dashboard - Final Version
"""

import streamlit as st
import asyncio
from pathlib import Path
import json
from datetime import datetime
import sys
import traceback

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scrapers" / "sec"))

# Import modules
from scrapers.sec.pipeline_manager import IPOPipelineManager
from scrapers.sec.enhanced_sec_scraper import EnhancedSECDocumentScraper

# Configuration
ADMIN_PASSWORD = "hedgeadmin2025"

st.set_page_config(
    page_title="Hedge Intel Admin - SEC Pipeline",
    page_icon="🏛️",
    layout="wide"
)

# Initialize session state
if 'logs' not in st.session_state:
    st.session_state.logs = []

def log(message):
    """Add log entry"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")
    st.session_state.logs = st.session_state.logs[-50:]  # Keep last 50

# Helper to run async
def run_async(coro):
    """Run async function"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🏛️ Hedge Intel Admin - SEC Pipeline")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()

# Initialize pipeline manager
@st.cache_resource
def get_pipeline_manager():
    return IPOPipelineManager()

# Main Interface
st.title("🏛️ SEC Pipeline Monitor")
st.caption(f"Enhanced Scraper Active • {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

# Sidebar logs
with st.sidebar:
    st.subheader("📋 Activity Log")
    for entry in reversed(st.session_state.logs[-15:]):
        st.text(entry)
    if st.button("Clear"):
        st.session_state.logs = []

# Get manager and summary
try:
    manager = get_pipeline_manager()
    summary = manager.get_admin_summary()
    log("✅ Pipeline loaded")
except Exception as e:
    st.error(f"Error: {e}")
    log(f"❌ Error: {e}")
    summary = {'pending': 0, 'active': 0, 'completed': 0, 'needs_attention': []}

# Action buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 Scan IPOs", use_container_width=True):
        with st.spinner("Scanning..."):
            try:
                log("Scanning IPOScoop...")
                count = run_async(manager.scan_new_ipos())
                log(f"Found {count} new IPOs")
                st.success(f"Found {count} new IPOs")
                st.rerun()
            except Exception as e:
                st.error(str(e))
                log(f"❌ Scan error: {e}")

with col2:
    if st.button("⚡ Process All", use_container_width=True):
        with st.spinner("Processing..."):
            try:
                log("Processing pending IPOs...")
                run_async(manager.process_pending_ipos())
                log("Processing complete")
                st.success("Complete!")
                st.rerun()
            except Exception as e:
                st.error(str(e))
                log(f"❌ Process error: {e}")

with col3:
    if st.button("🧪 Test CRCL", use_container_width=True):
        with st.spinner("Testing..."):
            try:
                log("Testing CRCL...")
                scraper = EnhancedSECDocumentScraper()
                result = run_async(scraper.scan_and_download_everything("CRCL", "0001876042"))
                if result['success']:
                    st.success(f"✅ {result['total_files']} files")
                    log(f"CRCL test: {result['total_files']} files")
                else:
                    st.error("Failed")
                    log(f"CRCL test failed: {result.get('error')}")
            except Exception as e:
                st.error(str(e))
                log(f"❌ Test error: {e}")

with col4:
    if st.button("🔍 Refresh", use_container_width=True):
        st.rerun()

# Metrics
st.markdown("### 📊 Pipeline Status")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📋 Pending", summary['pending'])
with col2:
    st.metric("✅ Active", summary['active'])
with col3:
    st.metric("📚 Completed", summary['completed'])
with col4:
    st.metric("⚠️ Issues", len(summary['needs_attention']))

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Pipeline", "📊 Documents", "🔧 Manual"])

with tab1:
    # Load pipeline data
    data = manager.load_pipeline_data()
    
    # Pending IPOs
    st.subheader(f"Pending IPOs ({len(data['pending'])})")
    if data['pending']:
        for ipo in data['pending']:
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
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
                    if st.button("Process", key=f"p_{ipo['ticker']}"):
                        with st.spinner("Processing..."):
                            try:
                                log(f"Processing {ipo['ticker']}...")
                                if 'cik' in ipo:
                                    scraper = EnhancedSECDocumentScraper()
                                    result = run_async(scraper.scan_and_download_everything(
                                        ipo['ticker'], ipo['cik']
                                    ))
                                    if result['success']:
                                        st.success(f"{result['total_files']} files")
                                        log(f"✅ {ipo['ticker']}: {result['total_files']} files")
                                        # Update status
                                        ipo['documents_count'] = result['total_files']
                                        ipo['status'] = 'active'
                                        data['pending'].remove(ipo)
                                        data['active'].append(ipo)
                                        manager.save_pipeline_data(data)
                                        st.rerun()
                                    else:
                                        st.error("Failed")
                                        log(f"❌ {ipo['ticker']} failed")
                                else:
                                    st.error("No CIK")
                            except Exception as e:
                                st.error(str(e))
                                log(f"❌ Error: {e}")
    else:
        st.info("No pending IPOs. Click 'Scan IPOs' to find new ones.")
    
    # Active IPOs
    st.subheader(f"Active IPOs ({len(data['active'])})")
    if data['active']:
        for ipo in data['active']:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.write(f"**{ipo['ticker']}**")
            with col2:
                st.write(ipo['company_name'])
                st.caption(f"Files: {ipo.get('documents_count', 0)}")
            with col3:
                if st.button("Re-scan", key=f"r_{ipo['ticker']}"):
                    st.info("Re-scanning...")

with tab2:
    st.subheader("Downloaded Documents")
    
    sec_dir = Path("data/sec_documents")
    if sec_dir.exists():
        tickers = sorted([d.name for d in sec_dir.iterdir() if d.is_dir()])
        
        if tickers:
            selected = st.selectbox("Select Ticker", [""] + tickers)
            
            if selected:
                ticker_dir = sec_dir / selected
                
                # Show metadata
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
                    
                    # Filing types
                    if 'filing_types' in metadata:
                        st.write("**Filing Types:**")
                        cols = st.columns(4)
                        for i, (ftype, count) in enumerate(sorted(metadata['filing_types'].items())):
                            cols[i % 4].write(f"{ftype}: {count}")
                
                # List files
                files = list(ticker_dir.glob("*.htm*")) + list(ticker_dir.glob("*.txt"))
                st.write(f"**Sample Files ({len(files)} total):**")
                for file in sorted(files)[:10]:
                    st.caption(f"📄 {file.name} ({file.stat().st_size // 1024} KB)")

with tab3:
    st.subheader("Manual Download")
    
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Ticker Symbol")
    with col2:
        cik = st.text_input("CIK Number")
    
    if st.button("Download All Documents", use_container_width=True):
        if ticker and cik:
            with st.spinner(f"Downloading {ticker}..."):
                try:
                    log(f"Manual download: {ticker}")
                    scraper = EnhancedSECDocumentScraper()
                    result = run_async(scraper.scan_and_download_everything(ticker.upper(), cik))
                    
                    if result['success']:
                        st.success(f"✅ Downloaded {result['total_files']} files")
                        log(f"✅ {ticker}: {result['total_files']} files")
                        
                        # Show details
                        st.json(result['metadata'])
                    else:
                        st.error(f"Failed: {result.get('error')}")
                        log(f"❌ {ticker} failed: {result.get('error')}")
                except Exception as e:
                    st.error(str(e))
                    log(f"❌ Error: {e}")

# Footer
st.divider()
st.caption("🏛️ SEC Pipeline Enhanced • Downloading ALL documents for competitive advantage")
