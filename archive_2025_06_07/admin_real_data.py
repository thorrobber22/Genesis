import streamlit as st
import os
from pathlib import Path
import json
from datetime import datetime, timedelta
from process_and_index import process_and_index_document_sync
import asyncio

# Import the async scraper
try:
    from scrapers.ipo_scraper import IPOScraper
    from scrapers.ipo_scraper_fixed import IPOScraper as FixedScraper
    scraper_available = True
except:
    scraper_available = False
    st.error("❌ IPO Scraper not available - cannot proceed")
    st.stop()

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

# Helper to run async functions
def run_async(coro):
    """Run async function in sync context"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_real_ipo_data():
    """Get REAL IPO data from scraper - no dummy data"""
    if not scraper_available:
        return []
    
    try:
        # Try main scraper first
        scraper = IPOScraper()
        data = run_async(scraper.get_ipo_calendar())
        
        ipos = []
        if data and isinstance(data, dict):
            # Check different possible keys
            ipo_list = data.get('upcoming') or data.get('ipos') or data.get('data', [])
            
            if isinstance(ipo_list, list):
                for ipo in ipo_list:
                    ticker = str(ipo.get('symbol') or ipo.get('ticker', '')).upper().strip()
                    company = str(ipo.get('company') or ipo.get('company_name', '')).strip()
                    date = str(ipo.get('expected_date') or ipo.get('ipo_date') or ipo.get('date', '')).strip()
                    
                    if ticker and len(ticker) <= 5:  # Valid ticker
                        ipos.append({
                            'ticker': ticker,
                            'company': company[:60],
                            'expected_date': date or 'TBD',
                            'source': 'IPO Calendar'
                        })
        
        # If no data from main scraper, try fixed scraper
        if not ipos:
            try:
                fixed_scraper = FixedScraper()
                if hasattr(fixed_scraper, 'scrape_calendar'):
                    alt_data = run_async(fixed_scraper.scrape_calendar())
                    if isinstance(alt_data, list):
                        for ipo in alt_data:
                            ticker = str(ipo.get('ticker', '')).upper().strip()
                            if ticker and len(ticker) <= 5:
                                ipos.append({
                                    'ticker': ticker,
                                    'company': str(ipo.get('company', ''))[:60],
                                    'expected_date': str(ipo.get('date', 'TBD')),
                                    'source': 'Alt Scraper'
                                })
            except:
                pass
        
        return ipos
        
    except Exception as e:
        st.error(f"Scraper error: {str(e)}")
        return []

def get_active_tickers():
    """Get all tickers that need documents or have recent activity"""
    # Get IPO tickers
    ipo_data = get_real_ipo_data()
    ipo_tickers = {ipo['ticker']: ipo for ipo in ipo_data}
    
    # Get tickers from existing documents
    existing_tickers = set()
    processed_dir = Path("data/processed")
    
    if processed_dir.exists():
        for file in processed_dir.glob("*.json"):
            if not file.name.endswith("_chunks.json"):
                parts = file.name.split('_')
                if parts:
                    existing_tickers.add(parts[0].upper())
    
    # Combine all tickers
    all_tickers = sorted(set(ipo_tickers.keys()) | existing_tickers)
    
    # Create ticker info
    ticker_info = []
    for ticker in all_tickers:
        missing = check_missing_documents(ticker)
        info = {
            'ticker': ticker,
            'missing_docs': missing,
            'is_ipo': ticker in ipo_tickers,
            'company': ipo_tickers.get(ticker, {}).get('company', 'Unknown')
        }
        ticker_info.append(info)
    
    # Sort: IPOs with missing docs first, then other IPOs, then existing
    ticker_info.sort(key=lambda x: (
        not x['is_ipo'],  # IPOs first
        len(x['missing_docs']) == 0,  # Missing docs first
        x['ticker']
    ))
    
    return ticker_info

def check_missing_documents(ticker):
    """Check which documents are missing"""
    missing = []
    processed_dir = Path("data/processed")
    
    if not processed_dir.exists():
        return REQUIRED_DOCS
    
    ticker_files = list(processed_dir.glob(f"{ticker}*.json"))
    ticker_files = [f for f in ticker_files if not f.name.endswith("_chunks.json")]
    
    for doc_type in REQUIRED_DOCS:
        found = False
        doc_search = doc_type.lower().replace("-", "")
        
        for file in ticker_files:
            if doc_search in file.name.lower():
                found = True
                break
        
        if not found:
            missing.append(doc_type)
    
    return missing

def get_document_status():
    """Get complete document status"""
    status = {}
    processed_dir = Path("data/processed")
    
    if processed_dir.exists():
        for file in processed_dir.glob("*.json"):
            if not file.name.endswith("_chunks.json"):
                parts = file.name.split('_')
                if parts:
                    ticker = parts[0].upper()
                    if ticker not in status:
                        status[ticker] = {
                            'ticker': ticker,
                            'documents': {},
                            'last_updated': None
                        }
                    
                    # Identify document type
                    file_lower = file.name.lower()
                    for doc_type in REQUIRED_DOCS:
                        if doc_type.lower().replace("-", "") in file_lower:
                            status[ticker]['documents'][doc_type] = {
                                'file': file.name,
                                'date': datetime.fromtimestamp(file.stat().st_mtime)
                            }
                            
                            # Update last updated
                            if not status[ticker]['last_updated'] or                                status[ticker]['documents'][doc_type]['date'] > status[ticker]['last_updated']:
                                status[ticker]['last_updated'] = status[ticker]['documents'][doc_type]['date']
                            break
    
    return status

# Styling
st.markdown("""
<style>
    .ticker-select { font-weight: bold; }
    .missing-doc { color: #dc3545; }
    .available-doc { color: #28a745; }
    .ipo-badge { 
        background: #ffc107; 
        color: #000;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏛️ Hedge Intel Admin")
        st.caption("Real IPO data only - no test data")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            if password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
    st.stop()

# Main app
st.title("🏛️ IPO Document Manager")
st.caption("Real-time IPO data from scrapers")

# Refresh button
col1, col2, col3 = st.columns([3, 3, 1])
with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 IPO Monitor", "📤 Upload Documents", "📁 Document Status"])

with tab1:
    st.subheader("Real-Time IPO Monitor")
    
    # Get real IPO data
    with st.spinner("Fetching live IPO data..."):
        ipos = get_real_ipo_data()
    
    if not ipos:
        st.error("❌ No IPO data available - check scraper connection")
        st.stop()
    
    # Categorize
    action_needed = []
    complete = []
    
    for ipo in ipos:
        missing = check_missing_documents(ipo['ticker'])
        ipo['missing'] = missing
        if missing:
            action_needed.append(ipo)
        else:
            complete.append(ipo)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Live IPOs", len(ipos))
    with col2:
        st.metric("Need Documents", len(action_needed))
    with col3:
        st.metric("Complete", len(complete))
    
    # Show IPOs needing documents
    if action_needed:
        st.markdown("### ⚠️ IPOs Needing Documents")
        
        for ipo in action_needed:
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 3])
                
                with col1:
                    st.markdown(f"**{ipo['ticker']}**")
                
                with col2:
                    st.text(ipo['company'])
                    st.caption(f"Expected: {ipo['expected_date']}")
                
                with col3:
                    st.markdown(f"<span class='missing-doc'>Missing: {', '.join(ipo['missing'])}</span>", 
                              unsafe_allow_html=True)
                
                st.divider()
    
    # Show complete IPOs
    if complete:
        with st.expander(f"✅ {len(complete)} IPOs with Complete Documents"):
            for ipo in complete:
                st.text(f"{ipo['ticker']} - {ipo['company']} ({ipo['expected_date']})")

with tab2:
    st.subheader("Upload Documents - Easy Dropdown Selection")
    
    # Get active tickers
    ticker_info = get_active_tickers()
    
    if not ticker_info:
        st.warning("No active tickers found. Check IPO Monitor tab.")
        st.stop()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Create ticker dropdown with helpful labels
        ticker_options = []
        ticker_labels = []
        
        for info in ticker_info:
            ticker_options.append(info['ticker'])
            
            # Create informative label
            label = f"{info['ticker']}"
            if info['is_ipo']:
                label += " 🆕"
            if info['missing_docs']:
                label += f" (Missing: {len(info['missing_docs'])})"
            else:
                label += " ✓"
            
            ticker_labels.append(label)
        
        # Ticker dropdown
        selected_idx = st.selectbox(
            "Select Ticker",
            range(len(ticker_options)),
            format_func=lambda x: ticker_labels[x],
            key="ticker_select"
        )
        
        selected_ticker = ticker_options[selected_idx]
        selected_info = ticker_info[selected_idx]
    
    with col2:
        # Show what's missing for selected ticker
        if selected_info['missing_docs']:
            st.error(f"Missing: {', '.join(selected_info['missing_docs'])}")
        else:
            st.success("All documents available!")
        
        if selected_info['is_ipo']:
            st.caption(f"IPO: {selected_info['company']}")
    
    st.divider()
    
    # File upload section
    st.markdown(f"### Upload files for **{selected_ticker}**")
    
    uploaded_files = st.file_uploader(
        "Select documents",
        type=['html', 'pdf', 'txt'],
        accept_multiple_files=True,
        help="Upload S-1, 424B4, 8-A, Lock-up agreements, or Financial statements"
    )
    
    if uploaded_files:
        # Show what will be uploaded
        st.markdown("**Files to process:**")
        for file in uploaded_files:
            st.caption(f"📄 {file.name} ({file.size:,} bytes)")
        
        if st.button("Process All Files", type="primary", use_container_width=True):
            progress = st.progress(0)
            results = []
            
            for i, file in enumerate(uploaded_files):
                progress.progress((i + 1) / len(uploaded_files))
                
                # Save file
                save_path = Path(f"data/documents/{selected_ticker}_{file.name}")
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())
                
                # Process
                with st.spinner(f"Processing {file.name}..."):
                    result = process_and_index_document_sync(selected_ticker, save_path)
                    results.append((file.name, result))
            
            progress.empty()
            
            # Show results
            st.markdown("### Processing Results")
            for filename, result in results:
                if result.get("success"):
                    st.success(f"✅ **{filename}** → {result.get('document_type', 'Unknown')}")
                    if result.get("chunks_indexed"):
                        st.caption(f"   Created {result['chunks_indexed']} searchable chunks")
                else:
                    st.error(f"❌ **{filename}** - {result.get('error', 'Failed')}")
            
            # Clear cache to refresh data
            st.cache_data.clear()

with tab3:
    st.subheader("Complete Document Status")
    
    # Get status
    status = get_document_status()
    
    if not status:
        st.info("No documents uploaded yet. Use the Upload tab to add documents.")
        st.stop()
    
    # Search
    search = st.text_input("🔍 Filter by ticker", placeholder="Enter ticker...")
    
    # Filter and sort
    filtered_status = []
    for ticker, info in status.items():
        if not search or search.upper() in ticker:
            # Calculate completeness
            info['complete'] = len(info['documents'])
            info['missing'] = len(REQUIRED_DOCS) - info['complete']
            filtered_status.append(info)
    
    # Sort by completeness (least complete first)
    filtered_status.sort(key=lambda x: (x['complete'], x['ticker']))
    
    st.markdown(f"Showing {len(filtered_status)} ticker(s)")
    st.divider()
    
    # Display
    for info in filtered_status:
        with st.container():
            col1, col2 = st.columns([1, 5])
            
            with col1:
                st.markdown(f"### {info['ticker']}")
                if info['missing'] > 0:
                    st.caption(f"⚠️ Missing: {info['missing']}")
                else:
                    st.caption("✅ Complete")
            
            with col2:
                # Show each document type
                doc_statuses = []
                for doc_type in REQUIRED_DOCS:
                    if doc_type in info['documents']:
                        doc_info = info['documents'][doc_type]
                        doc_statuses.append(f"✅ **{DOC_DISPLAY_NAMES[doc_type]}** ({doc_info['date'].strftime('%m/%d')})")
                    else:
                        doc_statuses.append(f"❌ **{DOC_DISPLAY_NAMES[doc_type]}**")
                
                st.markdown(" | ".join(doc_statuses))
                
                if info['last_updated']:
                    st.caption(f"Last updated: {info['last_updated'].strftime('%Y-%m-%d %H:%M')}")
            
            st.divider()

# Footer
st.caption(f"Last refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
