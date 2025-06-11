#!/usr/bin/env python3
"""
Enhanced Admin Dashboard with Logging
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

# Import with error handling
try:
    from scrapers.sec.pipeline_manager import IPOPipelineManager
    from process_and_index import process_and_index_document_sync
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Configuration
ADMIN_PASSWORD = "hedgeadmin2025"

st.set_page_config(
    page_title="Hedge Intel Admin - SEC Enhanced",
    page_icon="🏛️",
    layout="wide"
)

# Initialize session state for logs
if 'logs' not in st.session_state:
    st.session_state.logs = []

def add_log(message, level="info"):
    """Add log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")
    # Keep last 50 logs
    st.session_state.logs = st.session_state.logs[-50:]

# Helper to run async
def run_async(coro):
    """Run async function in sync context"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Initialize pipeline manager
@st.cache_resource
def get_pipeline_manager():
    try:
        manager = IPOPipelineManager()
        add_log("✅ Pipeline manager initialized")
        return manager
    except Exception as e:
        add_log(f"❌ Error initializing pipeline: {e}", "error")
        raise

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🏛️ Hedge Intel Admin - SEC Enhanced")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()

# Main Admin Interface
st.title("🏛️ SEC Pipeline Monitor - Enhanced")
st.caption(f"Last refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Sidebar for logs
with st.sidebar:
    st.subheader("📋 System Logs")
    log_container = st.container()
    with log_container:
        for log in reversed(st.session_state.logs[-20:]):  # Show last 20
            st.text(log)
    
    if st.button("Clear Logs"):
        st.session_state.logs = []
        st.rerun()

# Get pipeline manager
try:
    manager = get_pipeline_manager()
    summary = manager.get_admin_summary()
except Exception as e:
    st.error(f"Error: {e}")
    add_log(f"❌ Error getting summary: {e}", "error")
    summary = {'pending': 0, 'active': 0, 'completed': 0, 'needs_attention': []}

# Action buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 Scan IPOs", use_container_width=True):
        with st.spinner("Scanning IPOScoop..."):
            try:
                add_log("🔄 Starting IPO scan...")
                new_count = run_async(manager.scan_new_ipos())
                add_log(f"✅ Found {new_count} new IPOs")
                st.success(f"Found {new_count} new IPOs")
                st.rerun()
            except Exception as e:
                error_msg = f"Error scanning: {str(e)}"
                st.error(error_msg)
                add_log(f"❌ {error_msg}", "error")

with col2:
    if st.button("⚡ Process All", use_container_width=True):
        with st.spinner("Processing pending IPOs..."):
            try:
                add_log("⚡ Processing all pending IPOs...")
                run_async(manager.process_pending_ipos())
                add_log("✅ Processing complete")
                st.success("Processing complete")
                st.rerun()
            except Exception as e:
                error_msg = f"Error processing: {str(e)}"
                st.error(error_msg)
                add_log(f"❌ {error_msg}", "error")

with col3:
    if st.button("🧪 Test CRCL", use_container_width=True):
        with st.spinner("Testing Circle download..."):
            try:
                add_log("🧪 Testing CRCL download...")
                from scrapers.sec.enhanced_sec_scraper import EnhancedSECDocumentScraper
                scraper = EnhancedSECDocumentScraper()
                result = run_async(scraper.scan_and_download_everything("CRCL", "0001876042"))
                
                if result['success']:
                    msg = f"✅ Downloaded {result['total_files']} files"
                    st.success(msg)
                    add_log(msg)
                else:
                    st.error(f"Failed: {result.get('error')}")
                    add_log(f"❌ Test failed: {result.get('error')}", "error")
                    
            except Exception as e:
                error_msg = f"Test error: {str(e)}"
                st.error(error_msg)
                add_log(f"❌ {error_msg}", "error")
                add_log(f"Traceback: {traceback.format_exc()}", "error")

with col4:
    if st.button("🔍 Check Setup", use_container_width=True):
        # Check if enhanced scraper is properly set up
        try:
            from scrapers.sec import enhanced_sec_scraper
            from scrapers.sec import sec_scraper
            from scrapers.sec import pipeline_manager
            
            st.success("✅ All modules found")
            add_log("✅ Module check passed")
            
            # Check which scraper is being used
            with open("scrapers/sec/pipeline_manager.py", 'r') as f:
                pm_content = f.read()
                if "enhanced_sec_scraper" in pm_content:
                    st.success("✅ Using enhanced scraper")
                    add_log("✅ Enhanced scraper integrated")
                else:
                    st.warning("⚠️ Not using enhanced scraper")
                    add_log("⚠️ Enhanced scraper not integrated", "warning")
                    
        except Exception as e:
            st.error(f"Setup issue: {e}")
            add_log(f"❌ Setup check failed: {e}", "error")

# Display metrics
st.markdown("### 📊 Pipeline Status")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📋 Pending", summary['pending'])
with col2:
    st.metric("✅ Active", summary['active'])
with col3:
    st.metric("📚 Completed", summary['completed'])
with col4:
    st.metric("⚠️ Need Attention", len(summary['needs_attention']))

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Pipeline", "📊 Documents", "🔧 Manual Process", "🧪 Debug"])

with tab1:
    st.subheader("Pipeline Status")
    
    # Load pipeline data
    try:
        pipeline_data = manager.load_pipeline_data()
        
        # Pending
        with st.expander(f"📋 Pending ({len(pipeline_data['pending'])})"):
            for ipo in pipeline_data['pending']:
                col1, col2, col3 = st.columns([2, 3, 2])
                with col1:
                    st.write(f"**{ipo['ticker']}**")
                with col2:
                    st.write(ipo['company_name'])
                    if 'cik' in ipo:
                        st.caption(f"CIK: {ipo['cik']}")
                with col3:
                    if st.button(f"Process", key=f"proc_{ipo['ticker']}"):
                        with st.spinner(f"Processing {ipo['ticker']}..."):
                            try:
                                add_log(f"Processing {ipo['ticker']}...")
                                # Process this specific IPO
                                if 'cik' in ipo:
                                    from scrapers.sec.enhanced_sec_scraper import EnhancedSECDocumentScraper
                                    scraper = EnhancedSECDocumentScraper()
                                    result = run_async(scraper.scan_and_download_everything(ipo['ticker'], ipo['cik']))
                                    
                                    if result['success']:
                                        st.success(f"Downloaded {result['total_files']} files")
                                        add_log(f"✅ {ipo['ticker']}: {result['total_files']} files")
                                    else:
                                        st.error(f"Failed: {result.get('error')}")
                                        add_log(f"❌ {ipo['ticker']}: {result.get('error')}", "error")
                                else:
                                    st.error("No CIK found")
                                    add_log(f"❌ {ipo['ticker']}: No CIK", "error")
                                    
                            except Exception as e:
                                st.error(f"Error: {e}")
                                add_log(f"❌ Error processing {ipo['ticker']}: {e}", "error")
        
        # Active
        with st.expander(f"✅ Active ({len(pipeline_data['active'])})"):
            for ipo in pipeline_data['active']:
                st.write(f"**{ipo['ticker']}** - {ipo['company_name']}")
                if 'documents_count' in ipo:
                    st.caption(f"Documents: {ipo['documents_count']}")
                    
    except Exception as e:
        st.error(f"Error loading pipeline: {e}")
        add_log(f"❌ Pipeline load error: {e}", "error")

with tab2:
    st.subheader("Downloaded Documents")
    
    sec_dir = Path("data/sec_documents")
    if sec_dir.exists():
        tickers = sorted([d.name for d in sec_dir.iterdir() if d.is_dir()])
        
        if tickers:
            selected = st.selectbox("Select Ticker", tickers)
            
            if selected:
                ticker_dir = sec_dir / selected
                
                # Load metadata if exists
                metadata_file = ticker_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Files", metadata.get('total_files', 0))
                        st.metric("Total Filings", metadata.get('total_filings', 0))
                    with col2:
                        st.metric("Last Scan", metadata.get('last_scan', 'Never')[:10])
                        st.metric("Downloaded", metadata.get('downloaded_filings', 0))
                    
                    # Show filing types
                    if 'filing_types' in metadata:
                        st.write("**Filing Types:**")
                        for ftype, count in sorted(metadata['filing_types'].items()):
                            st.write(f"• {ftype}: {count}")
                
                # List files
                files = list(ticker_dir.glob("*"))
                st.write(f"**Files ({len(files)}):**")
                for file in sorted(files)[:20]:  # Show first 20
                    if file.suffix in ['.html', '.txt']:
                        size_kb = file.stat().st_size / 1024
                        st.caption(f"📄 {file.name} ({size_kb:.1f} KB)")
        else:
            st.info("No documents downloaded yet")

with tab3:
    st.subheader("Manual Processing")
    
    ticker = st.text_input("Ticker Symbol").upper()
    cik = st.text_input("CIK Number")
    
    if st.button("Download All Documents"):
        if ticker and cik:
            with st.spinner(f"Downloading all documents for {ticker}..."):
                try:
                    add_log(f"Manual download: {ticker} (CIK: {cik})")
                    
                    from scrapers.sec.enhanced_sec_scraper import EnhancedSECDocumentScraper
                    scraper = EnhancedSECDocumentScraper()
                    result = run_async(scraper.scan_and_download_everything(ticker, cik))
                    
                    if result['success']:
                        st.success(f"✅ Downloaded {result['total_files']} files from {result['filings_downloaded']} filings")
                        add_log(f"✅ Manual download complete: {result['total_files']} files")
                        
                        # Show summary
                        st.json(result['metadata'])
                    else:
                        st.error(f"Failed: {result.get('error')}")
                        add_log(f"❌ Manual download failed: {result.get('error')}", "error")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
                    add_log(f"❌ Manual download error: {e}", "error")
                    st.text(traceback.format_exc())
        else:
            st.warning("Please enter both ticker and CIK")

with tab4:
    st.subheader("Debug Information")
    
    # Show Python path
    st.write("**Python Path:**")
    for p in sys.path[:5]:
        st.code(p)
    
    # Show module locations
    st.write("**Module Locations:**")
    modules_to_check = [
        "scrapers.sec.pipeline_manager",
        "scrapers.sec.enhanced_sec_scraper",
        "scrapers.sec.sec_scraper"
    ]
    
    for module_name in modules_to_check:
        try:
            module = __import__(module_name, fromlist=[''])
            st.write(f"• {module_name}: {module.__file__}")
        except Exception as e:
            st.write(f"• {module_name}: ❌ {e}")
    
    # Show recent logs
    st.write("**Recent Logs:**")
    for log in st.session_state.logs[-10:]:
        st.text(log)

# Footer
st.divider()
st.caption("🏛️ SEC Pipeline Enhanced • Real-time document collection")
