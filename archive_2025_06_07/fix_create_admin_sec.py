#!/usr/bin/env python3
"""
Create admin dashboard with SEC integration - Fixed
Date: 2025-06-06 17:46:06 UTC
Author: thorrobber22
"""

from pathlib import Path

admin_content = '''#!/usr/bin/env python3
"""
Admin Dashboard with SEC Scraper Integration
"""

import streamlit as st
import asyncio
from pathlib import Path
import json
from datetime import datetime
import sys

# Add paths for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scrapers" / "sec"))

# Import our modules
try:
    from scrapers.sec.pipeline_manager import IPOPipelineManager
    from process_and_index import process_and_index_document_sync
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Configuration
ADMIN_PASSWORD = "hedgeadmin2025"

st.set_page_config(
    page_title="Hedge Intel Admin - SEC",
    page_icon="🏛️",
    layout="wide"
)

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
    return IPOPipelineManager()

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🏛️ Hedge Intel Admin - SEC Integration")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()

# Main Admin Interface
st.title("🏛️ SEC Pipeline Monitor")
st.caption(f"Last refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Get pipeline manager
try:
    manager = get_pipeline_manager()
    summary = manager.get_admin_summary()
except Exception as e:
    st.error(f"Error initializing pipeline: {e}")
    summary = {'pending': 0, 'active': 0, 'completed': 0, 'needs_attention': []}

# Action buttons
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    if st.button("🔄 Scan IPOs", use_container_width=True):
        with st.spinner("Scanning IPOScoop..."):
            try:
                new_count = run_async(manager.scan_new_ipos())
                st.success(f"Found {new_count} new IPOs")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

with col2:
    if st.button("⚡ Process Pending", use_container_width=True):
        with st.spinner("Processing pending IPOs..."):
            try:
                run_async(manager.process_pending_ipos())
                st.success("Processing complete")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# Display metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📋 Pending", summary['pending'])
with col2:
    st.metric("✅ Active", summary['active'])
with col3:
    st.metric("📚 Completed", summary['completed'])
with col4:
    st.metric("⚠️ Need Attention", len(summary['needs_attention']))

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🚨 Needs Attention", "📋 Pipeline Status", "📊 Documents", "🔍 Manual Tools"])

with tab1:
    st.subheader("Issues Requiring Manual Intervention")
    
    if summary['needs_attention']:
        for issue in summary['needs_attention']:
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"**{issue['ticker']}**")
                
                with col2:
                    st.error(issue['issue'])
                    st.caption(issue['action'])
                
                st.divider()
    else:
        st.success("✅ No issues - all systems operational!")

with tab2:
    st.subheader("IPO Pipeline Status")
    
    # Load pipeline data
    pipeline_data = manager.load_pipeline_data()
    
    # Pending IPOs
    st.markdown("### 📋 Pending IPOs")
    if pipeline_data['pending']:
        for ipo in pipeline_data['pending']:
            with st.expander(f"{ipo['ticker']} - {ipo['company_name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Status:** {ipo.get('status', 'pending')}")
                    st.write(f"**Expected Date:** {ipo.get('expected_date', 'TBD')}")
                    st.write(f"**Price Range:** {ipo.get('price_range', 'TBD')}")
                with col2:
                    st.write(f"**Added:** {ipo.get('added_date', 'Unknown')}")
                    if 'cik' in ipo:
                        st.write(f"**CIK:** {ipo['cik']}")
                        st.write(f"**Confidence:** {ipo.get('cik_confidence', 0)}%")
    else:
        st.info("No pending IPOs")
    
    # Active IPOs
    st.markdown("### ✅ Active IPOs")
    if pipeline_data['active']:
        for ipo in pipeline_data['active']:
            with st.container():
                col1, col2, col3 = st.columns([2, 3, 2])
                with col1:
                    st.write(f"**{ipo['ticker']}**")
                    st.caption(ipo['company_name'])
                with col2:
                    st.write(f"📄 Documents: {ipo.get('documents_count', 0)}")
                    st.write(f"🕒 Last scan: {ipo.get('last_scan', 'Never')}")
                with col3:
                    if st.button(f"Re-scan", key=f"rescan_{ipo['ticker']}"):
                        st.info("Re-scanning...")
    else:
        st.info("No active IPOs")

with tab3:
    st.subheader("SEC Documents Browser")
    
    # Show downloaded documents
    sec_dir = Path("data/sec_documents")
    if sec_dir.exists():
        tickers = [d.name for d in sec_dir.iterdir() if d.is_dir()]
        
        if tickers:
            selected_ticker = st.selectbox("Select Ticker", [""] + tickers)
            
            if selected_ticker:
                ticker_dir = sec_dir / selected_ticker
                docs = list(ticker_dir.glob("*.html"))
                
                st.write(f"**{len(docs)} documents for {selected_ticker}:**")
                
                for doc in docs:
                    col1, col2, col3 = st.columns([4, 1, 1])
                    with col1:
                        st.caption(f"📄 {doc.name}")
                    with col2:
                        size_kb = doc.stat().st_size / 1024
                        st.caption(f"{size_kb:.1f} KB")
                    with col3:
                        if st.button("Process", key=f"proc_{doc.name}"):
                            with st.spinner("Processing..."):
                                try:
                                    result = process_and_index_document_sync(selected_ticker, str(doc))
                                    if result.get('success'):
                                        st.success("✅")
                                    else:
                                        st.error("❌")
                                except Exception as e:
                                    st.error(f"Error: {e}")
        else:
            st.info("No documents downloaded yet")
    else:
        st.info("SEC documents directory not created yet")

with tab4:
    st.subheader("Manual Tools")
    
    # Manual IPO addition
    st.markdown("### Add IPO Manually")
    col1, col2 = st.columns(2)
    with col1:
        manual_ticker = st.text_input("Ticker Symbol")
        manual_company = st.text_input("Company Name")
    with col2:
        manual_date = st.text_input("Expected Date", placeholder="YYYY-MM-DD")
        manual_price = st.text_input("Price Range", placeholder="$10-$12")
    
    if st.button("Add IPO"):
        if manual_ticker and manual_company:
            # Add to pending
            pipeline_data = manager.load_pipeline_data()
            new_ipo = {
                'ticker': manual_ticker.upper(),
                'company_name': manual_company,
                'expected_date': manual_date or 'TBD',
                'price_range': manual_price or 'TBD',
                'status': 'pending_cik',
                'added_date': datetime.now().isoformat(),
                'source': 'manual'
            }
            pipeline_data['pending'].append(new_ipo)
            manager.save_pipeline_data(pipeline_data)
            st.success(f"Added {manual_ticker} to pipeline")
            st.rerun()
    
    # Manual CIK search
    st.markdown("### Search for CIK")
    search_company = st.text_input("Company Name to Search")
    if st.button("Search SEC"):
        if search_company:
            with st.spinner("Searching..."):
                try:
                    from scrapers.sec.cik_resolver import CIKResolver
                    resolver = CIKResolver()
                    result = run_async(resolver.get_cik(search_company))
                    if result:
                        st.success(f"Found: {result['name']} (CIK: {result['cik']})")
                        st.write(f"Ticker: {result.get('ticker', 'N/A')}")
                        st.write(f"Confidence: {result['confidence']}%")
                    else:
                        st.warning("No matches found")
                except Exception as e:
                    st.error(f"Error: {e}")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🏛️ SEC Pipeline Status")
with col2:
    st.caption("🤖 Automated IPO Collection")
with col3:
    st.caption(f"🕒 {datetime.now().strftime('%H:%M:%S UTC')}")
'''

# Save the admin file
with open("admin_sec.py", 'w', encoding='utf-8') as f:
    f.write(admin_content)

print("✅ Created admin_sec.py - SEC integrated admin dashboard")
print("\nNow run: streamlit run admin_sec.py")
print("\nPassword: hedgeadmin2025")