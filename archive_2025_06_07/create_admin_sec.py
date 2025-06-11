#!/usr/bin/env python3
"""
Create admin dashboard with SEC integration
"""

admin_content = """#!/usr/bin/env python3
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
tab1, tab2, tab3 = st.tabs(["🚨 Needs Attention", "📋 Pipeline Status", "📊 Documents"])

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
    
    # Show pipeline files
    pipeline_dir = Path("data/ipo_pipeline")
    if pipeline_dir.exists():
        st.write("**Pipeline Files:**")
        for file in ["pending.json", "active.json", "completed.json"]:
            file_path = pipeline_dir / file
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                st.write(f"• {file}: {len(data)} items")
    else:
        st.info("Pipeline directory not initialized yet. Click 'Scan IPOs' to start.")

with tab3:
    st.subheader("SEC Documents")
    
    # Show downloaded documents
    sec_dir = Path("data/sec_documents")
    if sec_dir.exists():
        tickers = [d.name for d in sec_dir.iterdir() if d.is_dir()]
        
        if tickers:
            st.write(f"**Found documents for {len(tickers)} tickers:**")
            for ticker in tickers[:10]:  # Show first 10
                ticker_dir = sec_dir / ticker
                doc_count = len(list(ticker_dir.glob("*.html")))
                st.write(f"• {ticker}: {doc_count} documents")
        else:
            st.info("No documents downloaded yet")
    else:
        st.info("SEC documents directory not created yet")

# Footer
st.divider()
st.caption("SEC Pipeline Status • Automated IPO Document Collection")
"""

# Save the admin file
with open("admin_sec.py", 'w', encoding='utf-8') as f:
    f.write(admin_content)

print("✅ Created admin_sec.py - SEC integrated admin dashboard")
