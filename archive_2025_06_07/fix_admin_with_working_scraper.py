#!/usr/bin/env python3
"""
Fix admin to use working scraper
Date: 2025-06-06 13:21:27 UTC
Author: thorrobber22
"""

from pathlib import Path

print("Creating fixed admin with working scraper...")

# First, let's make a simple working IPO scraper function
working_admin = '''import streamlit as st
import os
from pathlib import Path
import json
from datetime import datetime, timedelta
from process_and_index import process_and_index_document_sync

# Import the working scraper
try:
    from scrapers.ipo_scraper import IPOScraper
    ipo_scraper_available = True
except:
    ipo_scraper_available = False
    print("IPO scraper not available, using fallback data")

# Configuration
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "hedgeadmin2025")

# Document types
REQUIRED_DOCS = ["S-1", "424B4", "8-A", "Lock-up", "Financial"]
DOC_DISPLAY_NAMES = {
    "S-1": "S-1 Registration",
    "424B4": "Final Prospectus", 
    "8-A": "Exchange Listing",
    "Lock-up": "Lock-up Agreement",
    "Financial": "Financial Statements"
}

st.set_page_config(
    page_title="Hedge Intel Admin",
    page_icon="🏛️",
    layout="wide"
)

# Helper function at module level
def get_ipo_data():
    """Get IPO data from scraper or fallback"""
    if ipo_scraper_available:
        try:
            scraper = IPOScraper()
            data = scraper.get_ipo_calendar()
            
            ipos = []
            if data and isinstance(data, dict) and 'upcoming' in data:
                for ipo in data['upcoming'][:15]:
                    ipos.append({
                        'ticker': str(ipo.get('symbol', '')).upper(),
                        'company': str(ipo.get('company', ''))[:50],
                        'expected_date': str(ipo.get('expected_date', 'TBD')),
                        'source': 'IPO Calendar'
                    })
            
            if ipos:
                return ipos
        except Exception as e:
            st.error(f"Scraper error: {str(e)}")
    
    # Fallback data
    return [
        {'ticker': 'RDDT', 'company': 'Reddit Inc.', 'expected_date': 'Recent IPO', 'source': 'Manual'},
        {'ticker': 'ARM', 'company': 'ARM Holdings', 'expected_date': 'Recent IPO', 'source': 'Manual'},
        {'ticker': 'CRCL', 'company': 'Crescent Capital BDC', 'expected_date': 'This Week', 'source': 'Manual'},
        {'ticker': 'GCBC', 'company': 'Greene County Bancorp', 'expected_date': 'This Week', 'source': 'Manual'},
    ]

def check_missing_documents(ticker):
    """Check which documents are missing"""
    missing = []
    processed_dir = Path("data/processed")
    
    if not processed_dir.exists():
        return REQUIRED_DOCS
    
    # Get all files for this ticker
    ticker_files = list(processed_dir.glob(f"{ticker}*.json"))
    ticker_files = [f for f in ticker_files if not f.name.endswith("_chunks.json")]
    
    # Check each required doc
    for doc_type in REQUIRED_DOCS:
        found = False
        for file in ticker_files:
            if doc_type.lower() in file.name.lower():
                found = True
                break
        if not found:
            missing.append(doc_type)
    
    return missing

def get_all_tickers():
    """Get all tickers with documents"""
    tickers = {}
    processed_dir = Path("data/processed")
    
    if processed_dir.exists():
        for file in processed_dir.glob("*.json"):
            if not file.name.endswith("_chunks.json"):
                # Extract ticker (first part before underscore)
                parts = file.name.split('_')
                if parts:
                    ticker = parts[0].upper()
                    if ticker not in tickers:
                        tickers[ticker] = {
                            'ticker': ticker,
                            'documents': [],
                            'last_updated': datetime.fromtimestamp(file.stat().st_mtime)
                        }
                    
                    # Identify document type
                    for doc_type in REQUIRED_DOCS:
                        if doc_type.lower() in file.name.lower():
                            if doc_type not in tickers[ticker]['documents']:
                                tickers[ticker]['documents'].append(doc_type)
                            break
    
    return sorted(tickers.values(), key=lambda x: x['ticker'])

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🏛️ Hedge Intel Admin")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()

# Main app
st.title("🏛️ IPO Document Manager")

tab1, tab2, tab3 = st.tabs(["📊 IPO Monitor", "📤 Upload", "📁 Status"])

with tab1:
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh"):
            st.session_state.refresh = True
            st.rerun()
    
    # Get IPOs
    if 'ipos' not in st.session_state or st.session_state.get('refresh'):
        with st.spinner("Loading IPO data..."):
            st.session_state.ipos = get_ipo_data()
            st.session_state.refresh = False
    
    ipos = st.session_state.ipos
    
    # Split by status
    action_needed = []
    complete = []
    
    for ipo in ipos:
        missing = check_missing_documents(ipo['ticker'])
        if missing:
            ipo['missing'] = missing
            action_needed.append(ipo)
        else:
            complete.append(ipo)
    
    # Show action needed
    if action_needed:
        st.error(f"⚠️ {len(action_needed)} IPOs need documents")
        for ipo in action_needed:
            col1, col2, col3 = st.columns([2, 5, 2])
            with col1:
                st.markdown(f"**{ipo['ticker']}**")
            with col2:
                st.text(ipo['company'])
                st.caption(f"Missing: {', '.join(ipo['missing'])}")
            with col3:
                st.text(ipo['expected_date'])
    
    # Show complete
    if complete:
        st.success(f"✅ {len(complete)} IPOs ready")
        with st.expander("View"):
            for ipo in complete:
                st.text(f"{ipo['ticker']} - {ipo['company']}")

with tab2:
    st.subheader("Upload Documents")
    
    ticker = st.text_input("Ticker Symbol").upper()
    
    if ticker:
        missing = check_missing_documents(ticker)
        if missing:
            st.warning(f"Missing: {', '.join(missing)}")
        
        files = st.file_uploader("Select files", type=['html', 'pdf', 'txt'], accept_multiple_files=True)
        
        if files and st.button("Process", type="primary"):
            for file in files:
                save_path = Path(f"data/documents/{ticker}_{file.name}")
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())
                
                with st.spinner(f"Processing {file.name}..."):
                    result = process_and_index_document_sync(ticker, save_path)
                
                if result.get("success"):
                    st.success(f"✅ {file.name}")
                else:
                    st.error(f"❌ {file.name}: {result.get('error', 'Failed')}")

with tab3:
    st.subheader("Document Status")
    
    tickers = get_all_tickers()
    
    for ticker_info in tickers:
        col1, col2 = st.columns([2, 8])
        
        with col1:
            st.markdown(f"**{ticker_info['ticker']}**")
        
        with col2:
            status = []
            for doc in REQUIRED_DOCS:
                if doc in ticker_info['documents']:
                    status.append(f"✅ {DOC_DISPLAY_NAMES[doc]}")
                else:
                    status.append(f"❌ {DOC_DISPLAY_NAMES[doc]}")
            st.markdown(" | ".join(status))
        
        st.divider()
'''

# Save as new file
with open("admin_fixed.py", "w", encoding="utf-8") as f:
    f.write(working_admin)

print("✓ Created admin_fixed.py with working IPO data function")
print("\nThis version:")
print("- Defines get_ipo_data() at module level (not inside anything)")
print("- Imports scraper at the top")
print("- Has fallback data if scraper fails")
print("- Simple, clean structure")
print("\nRun: streamlit run admin_fixed.py")
print("Password: hedgeadmin2025")