import streamlit as st
import os
from pathlib import Path
import json
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time

# Import existing IPO scrapers
try:
    from scrapers.ipo_scraper import IPOScraper
    ipo_scraper = IPOScraper()
except ImportError:
    print("Warning: Could not import IPO scraper")
    ipo_scraper = None

from process_and_index import process_and_index_document_sync
try:
    from core.ipo_scraper import scrape_all_sources
    from ipo_monitor import get_upcoming_ipos
except ImportError:
    try:
        from ipo_scraper import scrape_all_sources
    except ImportError:
        print("Warning: No IPO scraper found")
        scrape_all_sources = None
import requests
from bs4 import BeautifulSoup
import time

# Configuration
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "hedgeadmin2025")

# Document types we track
REQUIRED_DOCS = ["S-1", "424B4", "8-A", "Lock-up", "Financial"]
DOC_DISPLAY_NAMES = {
    "S-1": "S-1 Registration",
    "424B4": "Final Prospectus",
    "8-A": "Exchange Listing",
    "Lock-up": "Lock-up Agreement",
    "Financial": "Financial Statements"
}

st.set_page_config(
    page_title="Hedge Intel Admin - IPO Monitor",
    page_icon="🏛️",
    layout="wide"
)

# Clean styling
st.markdown("""
<style>
    .missing-doc { color: #dc3545; font-weight: bold; }
    .available-doc { color: #28a745; }
    .ticker-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    .new-ipo { border-left: 4px solid #ffc107; }
    .action-required { border-left: 4px solid #dc3545; }
</style>
""", unsafe_allow_html=True)

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.title("🏛️ Hedge Intel Admin")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            if password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
else:
    # Main application
    st.title("🏛️ IPO Document Manager")
    
    # Auto-refresh info
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        if 'last_scrape' in st.session_state:
            st.caption(f"Last IPO check: {st.session_state.last_scrape}")
        else:
            st.caption("No recent IPO check")
    
    with col3:
        if st.button("🔄 Check IPOs Now"):
            st.session_state.check_now = True
            st.rerun()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📊 IPO Monitor", "📤 Upload Documents", "📁 Document Status"])
    
    # Tab 1: IPO Monitor
    with tab1:
        if st.session_state.get('check_now', False) or 'ipos' not in st.session_state:
            with st.spinner("Checking for new IPOs..."):
                ipos = scrape_ipos()
                st.session_state.ipos = ipos
                st.session_state.last_scrape = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
                st.session_state.check_now = False
        
        if 'ipos' in st.session_state:
            st.subheader("Upcoming IPOs")
            
            # Filter for action required
            action_required = []
            upcoming = []
            
            for ipo in st.session_state.ipos:
                ticker = ipo['ticker']
                missing_docs = check_missing_documents(ticker)
                ipo['missing_docs'] = missing_docs
                
                if missing_docs:
                    action_required.append(ipo)
                else:
                    upcoming.append(ipo)
            
            # Show action required first
            if action_required:
                st.warning(f"⚠️ {len(action_required)} IPOs need documents")
                for ipo in action_required:
                    show_ipo_card(ipo, action_required=True)
            
            # Show other upcoming IPOs
            if upcoming:
                st.info(f"📅 {len(upcoming)} IPOs with complete documents")
                with st.expander("View All"):
                    for ipo in upcoming:
                        show_ipo_card(ipo, action_required=False)
    
    # Tab 2: Upload Documents
    with tab2:
        st.subheader("Upload IPO Documents")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Show tickers that need documents
            st.markdown("**Tickers needing docs:**")
            
            tickers_needing_docs = get_tickers_needing_documents()
            if tickers_needing_docs:
                selected_ticker = st.selectbox(
                    "Select ticker",
                    options=tickers_needing_docs,
                    format_func=lambda x: f"{x} ⚠️"
                )
            else:
                selected_ticker = st.text_input("Enter ticker", placeholder="RDDT")
        
        with col2:
            if selected_ticker:
                # Show what's missing
                missing = check_missing_documents(selected_ticker)
                if missing:
                    st.warning(f"Missing for {selected_ticker}: {', '.join(missing)}")
                
                # File upload
                uploaded_files = st.file_uploader(
                    f"Upload files for {selected_ticker}",
                    type=['html', 'pdf', 'txt'],
                    accept_multiple_files=True,
                    help="Upload S-1, 424B4, 8-A, Lock-up agreements, Financial statements"
                )
                
                if uploaded_files:
                    if st.button("Process Files", type="primary"):
                        process_uploaded_files(selected_ticker, uploaded_files)
    
    # Tab 3: Document Status
    with tab3:
        st.subheader("Document Availability by Ticker")
        
        # Get all tickers with documents
        all_tickers = get_all_tickers_with_status()
        
        if all_tickers:
            # Search box
            search = st.text_input("🔍 Search ticker", placeholder="Enter ticker symbol...")
            
            # Filter tickers
            if search:
                filtered_tickers = [t for t in all_tickers if search.upper() in t['ticker'].upper()]
            else:
                filtered_tickers = all_tickers
            
            # Show ticker status grid
            for ticker_info in filtered_tickers:
                show_ticker_status(ticker_info)
        else:
            st.info("No documents uploaded yet")

# Helper Functions
def scrape_ipos():
    """Use existing IPO scraper or fallback"""
    ipos = []
    
    # Try to use existing scraper
    if 'scrape_all_sources' in globals() and scrape_all_sources:
        try:
            ipos = scrape_all_sources()
            # Convert to expected format if needed
            formatted_ipos = []
            for ipo in ipos:
                formatted_ipos.append({
                    'ticker': ipo.get('ticker', ipo.get('symbol', '')),
                    'company': ipo.get('company', ipo.get('company_name', '')),
                    'expected_date': ipo.get('expected_date', ipo.get('ipo_date', 'TBD')),
                    'source': ipo.get('source', 'Scraper')
                })
            return formatted_ipos
        except Exception as e:
            print(f"Error using existing scraper: {e}")
    
    # Fallback to manual scraping
    try:
        response = requests.get("https://www.iposcoop.com/", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Simple extraction - you may need to adjust based on actual HTML
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) >= 3:
                    ticker = cols[0].text.strip()
                    if ticker and len(ticker) <= 5:  # Basic validation
                        ipos.append({
                            'ticker': ticker.upper(),
                            'company': cols[1].text.strip()[:50],
                            'expected_date': cols[2].text.strip(),
                            'source': 'IPOScoop'
                        })
    except:
        pass
    
    # If still no IPOs, use test data
    if not ipos:
        ipos = [
            {'ticker': 'CRCL', 'company': 'Crescent Capital', 'expected_date': 'This Week', 'source': 'Test'},
        ]
    
    return ipos[:20]  # Limit to 20 IPOs
def check_missing_documents(ticker):
    """Check which required documents are missing for a ticker"""
    missing = []
    processed_dir = Path("data/processed")
    
    if not processed_dir.exists():
        return REQUIRED_DOCS
    
    # Check for each required doc type
    for doc_type in REQUIRED_DOCS:
        pattern = f"{ticker}_{doc_type}_*.json"
        if not list(processed_dir.glob(pattern)):
            missing.append(doc_type)
    
    return missing

def show_ipo_card(ipo, action_required=False):
    """Display IPO information card"""
    card_class = "ticker-card action-required" if action_required else "ticker-card"
    
    with st.container():
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
        
        with col1:
            st.markdown(f"**{ipo['ticker']}**")
        
        with col2:
            st.text(ipo['company'][:30] + "..." if len(ipo['company']) > 30 else ipo['company'])
        
        with col3:
            st.text(ipo['expected_date'])
        
        with col4:
            if action_required:
                if st.button("Upload Docs", key=f"upload_{ipo['ticker']}"):
                    st.session_state.selected_ticker = ipo['ticker']
                    st.session_state.active_tab = 1  # Switch to upload tab
                    st.rerun()
        
        if action_required and ipo.get('missing_docs'):
            st.markdown(f"<span class='missing-doc'>Missing: {', '.join(ipo['missing_docs'])}</span>", 
                       unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def get_tickers_needing_documents():
    """Get list of tickers that are missing documents"""
    tickers = set()
    
    # From scraped IPOs
    if 'ipos' in st.session_state:
        for ipo in st.session_state.ipos:
            if check_missing_documents(ipo['ticker']):
                tickers.add(ipo['ticker'])
    
    return sorted(list(tickers))

def process_uploaded_files(ticker, files):
    """Process uploaded files"""
    results = []
    
    for file in files:
        # Save file
        save_path = Path(f"data/documents/{ticker}_{file.name}")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, "wb") as f:
            f.write(file.getbuffer())
        
        # Process and index
        with st.spinner(f"Processing {file.name}..."):
            result = process_and_index_document_sync(ticker.upper(), save_path)
            results.append((file.name, result))
    
    # Show results
    st.divider()
    for filename, result in results:
        if result.get("success"):
            st.success(f"✅ {filename} → {result.get('document_type', 'Unknown')}")
            
            # Show where it's stored
            st.caption(f"📁 Stored in: data/processed/{ticker}_{result.get('document_type')}_{datetime.now().strftime('%Y%m%d')}*.json")
            
            if result.get("chunks_indexed", 0) > 0:
                st.caption(f"🔍 Indexed {result['chunks_indexed']} searchable chunks")
        else:
            st.error(f"❌ {filename}: {result.get('error', 'Processing failed')}")

def get_all_tickers_with_status():
    """Get all tickers and their document status"""
    tickers = {}
    processed_dir = Path("data/processed")
    
    if processed_dir.exists():
        for file in processed_dir.glob("*.json"):
            if not file.name.endswith("_chunks.json"):
                parts = file.name.split('_')
                if len(parts) >= 2:
                    ticker = parts[0]
                    doc_type = parts[1]
                    
                    if ticker not in tickers:
                        tickers[ticker] = {
                            'ticker': ticker,
                            'documents': {},
                            'last_updated': None
                        }
                    
                    tickers[ticker]['documents'][doc_type] = True
                    
                    # Track last update
                    file_time = datetime.fromtimestamp(file.stat().st_mtime)
                    if not tickers[ticker]['last_updated'] or file_time > tickers[ticker]['last_updated']:
                        tickers[ticker]['last_updated'] = file_time
    
    return sorted(tickers.values(), key=lambda x: x['ticker'])

def show_ticker_status(ticker_info):
    """Show document status for a ticker"""
    with st.container():
        col1, col2, col3 = st.columns([2, 5, 3])
        
        with col1:
            st.markdown(f"### {ticker_info['ticker']}")
        
        with col2:
            # Show document status
            doc_status = []
            for doc_type in REQUIRED_DOCS:
                if doc_type in ticker_info['documents']:
                    doc_status.append(f"✅ {DOC_DISPLAY_NAMES.get(doc_type, doc_type)}")
                else:
                    doc_status.append(f"❌ {DOC_DISPLAY_NAMES.get(doc_type, doc_type)}")
            
            st.markdown(" | ".join(doc_status))
        
        with col3:
            if ticker_info['last_updated']:
                st.caption(f"Updated: {ticker_info['last_updated'].strftime('%m/%d %H:%M')}")
        
        st.divider()

# Auto-refresh every 30 minutes
if 'last_auto_check' not in st.session_state:
    st.session_state.last_auto_check = datetime.now()

if datetime.now() - st.session_state.last_auto_check > timedelta(minutes=30):
    st.session_state.check_now = True
    st.session_state.last_auto_check = datetime.now()
    st.rerun()
