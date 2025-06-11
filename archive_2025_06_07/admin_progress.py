#!/usr/bin/env python3
"""
SEC Pipeline Admin with Progress & Logs
"""

import streamlit as st
import asyncio
from pathlib import Path
import json
from datetime import datetime
import sys
import time

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "scrapers" / "sec"))

# Import working scraper
from scrapers.sec.sec_compliant_scraper import SECCompliantScraper
from scrapers.sec.pipeline_manager import IPOPipelineManager

st.set_page_config(page_title="SEC Pipeline Admin", page_icon="🏛️", layout="wide")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'download_progress' not in st.session_state:
    st.session_state.download_progress = {}

def log(message):
    """Add log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")
    # Keep last 50 logs
    st.session_state.logs = st.session_state.logs[-50:]

# Password
if not st.session_state.authenticated:
    st.title("🏛️ SEC Pipeline Admin")
    if st.text_input("Password", type="password") == "hedgeadmin2025":
        st.session_state.authenticated = True
        log("✅ Admin logged in")
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
scraper = SECCompliantScraper()

# Header
st.title("🏛️ SEC Pipeline Monitor")
st.caption(f"SEC-Compliant Scraper • {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

# Sidebar with logs
with st.sidebar:
    st.subheader("📋 Activity Log")
    
    # Clear button
    if st.button("Clear Logs"):
        st.session_state.logs = []
        log("Logs cleared")
    
    # Show logs
    log_container = st.container(height=400)
    with log_container:
        for entry in reversed(st.session_state.logs):
            st.text(entry)

# Load data
data = manager.load_pipeline_data()

# Action buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 Scan IPOs", use_container_width=True):
        log("Scanning IPOScoop...")
        with st.spinner("Scanning..."):
            count = run_async(manager.scan_new_ipos())
            log(f"Found {count} new IPOs")
            st.success(f"Found {count} new IPOs")
            time.sleep(1)
            st.rerun()

with col2:
    if st.button("⚡ Process All", use_container_width=True):
        log("Processing all pending IPOs...")
        with st.spinner("Processing..."):
            run_async(manager.process_pending_ipos())
            log("Batch processing complete")
            st.success("Complete!")
            time.sleep(1)
            st.rerun()

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        log("Refreshing dashboard...")
        st.rerun()

with col4:
    # Show current time
    st.caption(f"🕒 {datetime.now().strftime('%H:%M:%S')}")

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📋 Pending", len(data['pending']))
with col2:
    st.metric("✅ Active", len(data['active']))
with col3:
    st.metric("📚 Completed", len(data['completed']))
with col4:
    total_docs = sum(ipo.get('documents_count', 0) for ipo in data['active'] + data['completed'])
    st.metric("📄 Total Docs", f"{total_docs:,}")

# Main tabs
tab1, tab2, tab3 = st.tabs(["🔄 Process IPOs", "📊 Active IPOs", "🔧 Manual Download"])

with tab1:
    st.subheader("Pending IPOs - Ready to Download")
    
    if data['pending']:
        # Add select all checkbox
        select_all = st.checkbox("Select all for batch processing")
        
        for ipo in data['pending']:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([0.5, 1.5, 2, 1.5, 1])
                
                with col1:
                    if select_all:
                        st.checkbox("", value=True, key=f"sel_{ipo['ticker']}", disabled=True)
                    else:
                        st.checkbox("", key=f"sel_{ipo['ticker']}")
                
                with col2:
                    st.markdown(f"**{ipo['ticker']}**")
                
                with col3:
                    st.text(ipo['company_name'])
                    if 'expected_date' in ipo:
                        st.caption(f"Expected: {ipo['expected_date']}")
                
                with col4:
                    if 'cik' in ipo:
                        st.caption(f"CIK: {ipo['cik']}")
                        if 'cik_confidence' in ipo:
                            st.progress(ipo['cik_confidence'] / 100)
                    else:
                        st.warning("No CIK")
                
                with col5:
                    if st.button("Download", key=f"dl_{ipo['ticker']}", use_container_width=True):
                        if 'cik' in ipo:
                            # Show progress
                            progress_container = st.empty()
                            
                            with progress_container.container():
                                st.info(f"🔄 Downloading {ipo['ticker']}...")
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                log(f"Starting download for {ipo['ticker']}...")
                                
                                # Run download
                                result = run_async(scraper.scan_and_download_everything(
                                    ipo['ticker'], 
                                    ipo['cik']
                                ))
                                
                                if result['success']:
                                    progress_bar.progress(100)
                                    status_text.success(f"✅ Downloaded {result['total_files']} files!")
                                    log(f"✅ {ipo['ticker']}: Downloaded {result['total_files']} files")
                                    
                                    # Update IPO status
                                    ipo['documents_count'] = result['total_files']
                                    ipo['status'] = 'active'
                                    ipo['last_scan'] = datetime.now().isoformat()
                                    
                                    # Move to active
                                    data['pending'].remove(ipo)
                                    data['active'].append(ipo)
                                    manager.save_pipeline_data(data)
                                    
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    status_text.error(f"Failed: {result.get('error', 'Unknown')}")
                                    log(f"❌ {ipo['ticker']}: Download failed - {result.get('error', 'Unknown')}")
                        else:
                            st.error("Need CIK first")
                            log(f"❌ {ipo['ticker']}: No CIK available")
                
                st.divider()
        
        # Batch download selected
        if st.button("📥 Download Selected", use_container_width=True, type="primary"):
            selected = [ipo for ipo in data['pending'] if st.session_state.get(f"sel_{ipo['ticker']}", False)]
            if selected:
                log(f"Starting batch download of {len(selected)} IPOs...")
                
                progress_container = st.container()
                with progress_container:
                    overall_progress = st.progress(0)
                    current_status = st.empty()
                    
                    for i, ipo in enumerate(selected):
                        if 'cik' in ipo:
                            current_status.info(f"Downloading {ipo['ticker']}... ({i+1}/{len(selected)})")
                            
                            result = run_async(scraper.scan_and_download_everything(
                                ipo['ticker'], 
                                ipo['cik']
                            ))
                            
                            if result['success']:
                                log(f"✅ {ipo['ticker']}: {result['total_files']} files")
                                ipo['documents_count'] = result['total_files']
                                ipo['status'] = 'active'
                                data['pending'].remove(ipo)
                                data['active'].append(ipo)
                            else:
                                log(f"❌ {ipo['ticker']}: Failed")
                        
                        overall_progress.progress((i + 1) / len(selected))
                    
                    manager.save_pipeline_data(data)
                    current_status.success(f"✅ Batch complete! Processed {len(selected)} IPOs")
                    time.sleep(2)
                    st.rerun()
            else:
                st.warning("No IPOs selected")
    else:
        st.info("No pending IPOs. Click 'Scan IPOs' to find new ones.")

with tab2:
    st.subheader("Active IPOs - Already Downloaded")
    
    if data['active']:
        # Add re-download all button
        if st.button("🔄 Re-download All Active", use_container_width=True):
            log("Re-downloading all active IPOs...")
            for ipo in data['active']:
                result = run_async(scraper.scan_and_download_everything(
                    ipo['ticker'], 
                    ipo['cik']
                ))
                if result['success']:
                    ipo['documents_count'] = result['total_files']
                    ipo['last_scan'] = datetime.now().isoformat()
                    log(f"✅ {ipo['ticker']}: Updated with {result['total_files']} files")
            manager.save_pipeline_data(data)
            st.success("Re-download complete!")
            st.rerun()
        
        # Show active IPOs
        for ipo in data['active']:
            col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
            with col1:
                st.markdown(f"**{ipo['ticker']}**")
            with col2:
                st.text(ipo['company_name'])
                if 'last_scan' in ipo:
                    st.caption(f"Last scan: {ipo.get('last_scan', 'Never')[:19]}")
            with col3:
                st.metric("Documents", ipo.get('documents_count', 0))
            with col4:
                if st.button("Re-scan", key=f"rescan_{ipo['ticker']}"):
                    log(f"Re-scanning {ipo['ticker']}...")
                    result = run_async(scraper.scan_and_download_everything(
                        ipo['ticker'], 
                        ipo['cik']
                    ))
                    if result['success']:
                        ipo['documents_count'] = result['total_files']
                        ipo['last_scan'] = datetime.now().isoformat()
                        manager.save_pipeline_data(data)
                        log(f"✅ {ipo['ticker']}: Updated with {result['total_files']} files")
                        st.success(f"Updated: {result['total_files']} files")
                        time.sleep(1)
                        st.rerun()
            st.divider()
    else:
        st.info("No active IPOs yet. Process some pending IPOs first.")

with tab3:
    st.subheader("Manual Download")
    
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Ticker Symbol", placeholder="AAPL")
    with col2:
        cik = st.text_input("CIK Number", placeholder="0000320193")
    
    if st.button("📥 Download Now", use_container_width=True, type="primary"):
        if ticker and cik:
            log(f"Manual download: {ticker.upper()} (CIK: {cik})")
            
            # Progress container
            progress_container = st.container()
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.status("Downloading...", expanded=True)
                
                # Run download
                result = run_async(scraper.scan_and_download_everything(ticker.upper(), cik))
                
                if result['success']:
                    progress_bar.progress(100)
                    status_text.update(label=f"✅ Success! Downloaded {result['total_files']} files", state="complete")
                    log(f"✅ Manual download complete: {ticker.upper()} - {result['total_files']} files")
                    
                    # Show results
                    st.success(f"Downloaded {result['total_files']} files")
                    
                    # Show metadata
                    with st.expander("Download Details"):
                        st.json(result['metadata'])
                else:
                    status_text.update(label=f"❌ Failed: {result.get('error', 'Unknown')}", state="error")
                    log(f"❌ Manual download failed: {ticker.upper()}")
        else:
            st.warning("Please enter both ticker and CIK")
    
    # Show some examples
    st.markdown("#### Examples:")
    examples = [
        ("AAPL", "0000320193", "Apple Inc."),
        ("MSFT", "0000789019", "Microsoft Corp."),
        ("GOOGL", "0001652044", "Alphabet Inc."),
        ("TSLA", "0001318605", "Tesla Inc.")
    ]
    
    for ticker, cik, name in examples:
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            st.caption(ticker)
        with col2:
            st.caption(cik)
        with col3:
            st.caption(name)

# Footer
st.divider()
st.caption("🏛️ SEC Pipeline • Real-time document collection • SEC-compliant rate limiting")
