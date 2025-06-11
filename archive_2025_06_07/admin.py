"""
Hedge Intelligence Admin Panel
Updated: 2025-06-05 13:33:22 UTC
Author: thorrobber22

Admin interface for document management and IPO monitoring
"""

import streamlit as st
from document_viewer import show_document_viewer
from search_interface import show_search_interface
from process_and_index import process_and_index_document_sync
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import requests
from typing import Dict, List, Tuple
import hashlib
import asyncio

# Import config - create if doesn't exist
try:
    from config import *
except ImportError:
    # Default config values
    from pathlib import Path
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    DOCUMENTS_DIR = DATA_DIR / "documents"
    PROCESSED_DIR = DATA_DIR / "processed"
    CACHE_DIR = DATA_DIR / "cache"
    VECTOR_DIR = DATA_DIR / "vectors"
    EXPORT_DIR = BASE_DIR / "exports"
    
    SUPPORTED_DOCUMENTS = {
        "S-1": ["S1", "S-1", "S1A", "S-1/A"],
        "424B4": ["424B4", "PROSPECTUS"],
        "LOCK_UP": ["LOCK-UP", "LOCKUP", "MARKET_STANDOFF"],
        "UNDERWRITING": ["UNDERWRITING", "PURCHASE_AGREEMENT"],
        "8-A": ["8-A", "8A", "FORM_8-A"]
    }

# Page configuration
st.set_page_config(
    page_title="Hedge Intel Admin",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown('''
<style>
    /* Clean Apple-style sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f5f5f7;
        padding-top: 2rem;
    }
    /* Clean tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f5f5f7;
        padding: 4px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        color: #1d1d1f;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: white;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
''', unsafe_allow_html=True)

# Authentication check
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_auth():
    """Simple authentication for admin panel"""
    if not st.session_state.authenticated:
        password = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if password == os.getenv("ADMIN_PASSWORD", "hedgeadmin2025"):
                st.session_state.authenticated = True
                st.rerun()
        st.stop()

def load_ipo_calendar() -> List[Dict]:
    """Load IPO calendar from cache"""
    calendar_path = CACHE_DIR / "ipo_calendar.json"
    if calendar_path.exists():
        with open(calendar_path, 'r') as f:
            return json.load(f)
    return []

def get_document_coverage(ticker: str) -> Dict[str, bool]:
    """Check which document types exist for a ticker"""
    coverage = {
        "S-1": False,
        "424B4": False,
        "LOCK_UP": False,
        "UNDERWRITING": False,
        "8-A": False
    }
    
    # Check for each document type
    for doc_type, patterns in SUPPORTED_DOCUMENTS.items():
        for pattern in patterns:
            files = list(DOCUMENTS_DIR.glob(f"{ticker}*{pattern}*"))
            if files:
                coverage[doc_type] = True
                break
    
    return coverage

def calculate_coverage_percentage(coverage: Dict[str, bool]) -> float:
    """Calculate document coverage percentage"""
    required_docs = ["S-1", "LOCK_UP", "UNDERWRITING"]  # Core required docs
    optional_docs = ["424B4", "8-A"]  # Post-IPO docs
    
    # Count required documents
    required_count = sum(1 for doc in required_docs if coverage.get(doc, False))
    required_percentage = (required_count / len(required_docs)) * 80  # 80% weight
    
    # Count optional documents
    optional_count = sum(1 for doc in optional_docs if coverage.get(doc, False))
    optional_percentage = (optional_count / len(optional_docs)) * 20  # 20% weight
    
    return required_percentage + optional_percentage

def get_uploaded_documents(ticker: str = None) -> List[Dict]:
    """Get list of all uploaded documents"""
    documents = []
    pattern = f"{ticker}*" if ticker else "*"
    
    for file_path in DOCUMENTS_DIR.glob(pattern):
        if file_path.is_file():
            stat = file_path.stat()
            doc_type = detect_document_type(file_path)
            
            documents.append({
                "filename": file_path.name,
                "ticker": extract_ticker_from_filename(file_path.name),
                "type": doc_type,
                "size_mb": round(stat.st_size / 1024 / 1024, 2),
                "uploaded": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "path": str(file_path)
            })
    
    return sorted(documents, key=lambda x: x["uploaded"], reverse=True)

def detect_document_type(file_path: Path) -> str:
    """Detect document type from filename and content"""
    filename = file_path.name.upper()
    
    # Check filename patterns
    for doc_type, patterns in SUPPORTED_DOCUMENTS.items():
        for pattern in patterns:
            if pattern in filename:
                return doc_type
    
    # If not detected from filename, check content (first 1000 chars)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1000).upper()
            
        if "REGISTRATION STATEMENT" in content:
            return "S-1"
        elif "424B4" in content or "FINAL PROSPECTUS" in content:
            return "424B4"
        elif "LOCK-UP" in content or "MARKET STAND-OFF" in content:
            return "LOCK_UP"
        elif "UNDERWRITING AGREEMENT" in content:
            return "UNDERWRITING"
        elif "FORM 8-A" in content:
            return "8-A"
    except:
        pass
    
    return "UNKNOWN"

def extract_ticker_from_filename(filename: str) -> str:
    """Extract ticker from filename"""
    # Remove file extension first
    name_without_ext = filename.rsplit('.', 1)[0]
    
    # Try to extract ticker from common patterns
    # Pattern 1: TICKER_doctype_timestamp
    if '_' in name_without_ext:
        parts = name_without_ext.split('_')
        if parts:
            return parts[0].upper()
    
    # Pattern 2: No underscore, just use the whole name
    return name_without_ext.upper()

def generate_sec_urls(ticker: str, company_name: str) -> Dict[str, str]:
    """Generate SEC EDGAR search URLs"""
    return {
        "All Filings": f"https://www.sec.gov/edgar/search/#/q={company_name.replace(' ', '%20')}",
        "S-1 Search": f"https://www.sec.gov/edgar/search/#/q={ticker}%20S-1",
        "424B4 Search": f"https://www.sec.gov/edgar/search/#/q={ticker}%20424B4",
        "Recent Filings": f"https://www.sec.gov/edgar/search/#/dateRange=30d&q={ticker}"
    }

def categorize_ipo(ipo_date_str: str) -> str:
    """Categorize IPO based on date"""
    try:
        ipo_date = datetime.strptime(ipo_date_str, "%Y-%m-%d")
        today = datetime.now()
        
        # Compare dates only, not times
        ipo_date_only = ipo_date.date()
        today_only = today.date()
        
        days_diff = (ipo_date_only - today_only).days
        
        if days_diff < -7:
            return "PAST"
        elif days_diff < 0:
            return "RECENT"
        elif days_diff == 0:
            return "TODAY"
        elif days_diff <= 30:
            return "UPCOMING"
        else:
            return "FUTURE"
    except:
        return "UNKNOWN"

def main():
    """Main admin panel interface"""
    check_auth()
    

if check_password():
        st.title("🏛️ Hedge Intelligence Admin Panel")
        st.caption(f"Last refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
        # Sidebar
        with st.sidebar:
            st.header("Navigation")
            page = st.radio("Select Page", ["Dashboard", "Documents", "Upload", "Coverage Report"])
    
        if page == "Dashboard":
            show_dashboard()
        elif page == "Documents":
            show_documents()
        elif page == "Upload":
            show_upload()
        elif page == "Coverage Report":
            show_coverage_report()

    def show_dashboard():
        """Show main dashboard with IPO overview"""
        st.header("IPO Dashboard")
    
        # Load IPO calendar
        ipos = load_ipo_calendar()
    
        if not ipos:
            st.warning("No IPO data found. Make sure ipo_calendar.json exists in data/cache/")
            return
    
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total IPOs", len(ipos))
        with col2:
            upcoming = sum(1 for ipo in ipos if categorize_ipo(ipo.get("expected_date", "")) == "UPCOMING")
            st.metric("Upcoming (30d)", upcoming)
        with col3:
            today = sum(1 for ipo in ipos if categorize_ipo(ipo.get("expected_date", "")) == "TODAY")
            st.metric("Today", today)
        with col4:
            total_docs = len(get_uploaded_documents())
            st.metric("Total Documents", total_docs)
    
        # IPO List with document status
        st.subheader("IPO Status")
    
        # Filter by category
        category = st.selectbox("Filter by", ["All", "TODAY", "UPCOMING", "RECENT", "PAST"])
    
        for ipo in ipos:
            ipo_category = categorize_ipo(ipo.get("expected_date", ""))
        
            if category != "All" and ipo_category != category:
                continue
        
            ticker = ipo.get("ticker", "")
            company = ipo.get("company", "Unknown")
            expected_date = ipo.get("expected_date", "TBD")
            price_range = ipo.get("price_range", "TBD")
        
            # Get document coverage
            coverage = get_document_coverage(ticker)
            coverage_pct = calculate_coverage_percentage(coverage)
        
            # Status color based on coverage
            if coverage_pct >= 80:
                status_color = "🟢"
            elif coverage_pct >= 50:
                status_color = "🟡"
            else:
                status_color = "🔴"
        
            with st.expander(f"{status_color} {ticker} - {company} ({coverage_pct:.0f}% coverage)"):
                col1, col2 = st.columns([2, 1])
            
                with col1:
                    st.write(f"**Expected Date:** {expected_date}")
                    st.write(f"**Price Range:** {price_range}")
                    st.write(f"**Category:** {ipo_category}")
                
                    # Document coverage indicators
                    st.write("**Document Coverage:**")
                    doc_cols = st.columns(5)
                    for i, (doc_type, exists) in enumerate(coverage.items()):
                        with doc_cols[i]:
                            if exists:
                                st.success(f"✓ {doc_type}")
                            else:
                                st.error(f"✗ {doc_type}")
            
                with col2:
                    st.write("**SEC EDGAR Links:**")
                    urls = generate_sec_urls(ticker, company)
                    for label, url in urls.items():
                        st.link_button(label, url)
                
                    if coverage_pct < 100:
                        st.warning("Missing documents!")
                        if st.button(f"Upload for {ticker}", key=f"upload_{ticker}"):
                            st.session_state.upload_ticker = ticker
                            st.session_state.page = "Upload"
                            st.rerun()

    def show_documents():
        """Show all uploaded documents"""
        st.header("Document Library")
    
        documents = get_uploaded_documents()
    
        if not documents:
            st.info("No documents uploaded yet. Go to Upload page to add documents.")
            return
    
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            ticker_filter = st.selectbox("Filter by Ticker", ["All"] + list(set(d["ticker"] for d in documents)))
        with col2:
            type_filter = st.selectbox("Filter by Type", ["All"] + list(SUPPORTED_DOCUMENTS.keys()))
        with col3:
            sort_by = st.selectbox("Sort by", ["Upload Date", "Ticker", "Type", "Size"])
    
        # Apply filters
        filtered_docs = documents
        if ticker_filter != "All":
            filtered_docs = [d for d in filtered_docs if d["ticker"] == ticker_filter]
        if type_filter != "All":
            filtered_docs = [d for d in filtered_docs if d["type"] == type_filter]
    
        # Sort
        if sort_by == "Upload Date":
            filtered_docs.sort(key=lambda x: x["uploaded"], reverse=True)
        elif sort_by == "Ticker":
            filtered_docs.sort(key=lambda x: x["ticker"])
        elif sort_by == "Type":
            filtered_docs.sort(key=lambda x: x["type"])
        elif sort_by == "Size":
            filtered_docs.sort(key=lambda x: x["size_mb"], reverse=True)
    
        # Display documents
        if filtered_docs:
            for doc in filtered_docs:
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
                with col1:
                    st.write(f"**{doc['filename']}**")
                with col2:
                    st.write(f"{doc['ticker']}")
                with col3:
                    st.write(f"{doc['type']}")
                with col4:
                    st.write(f"{doc['size_mb']} MB")
                with col5:
                    # Download button
                    with open(doc['path'], 'rb') as f:
                        st.download_button(
                            "Download",
                            f.read(),
                            file_name=doc['filename'],
                            key=f"download_{doc['filename']}"
                        )
        else:
            st.info("No documents found matching filters")

    def show_upload():
        """Show document upload interface"""
        st.header("Document Upload")
    
        # Pre-fill ticker if coming from dashboard
        default_ticker = st.session_state.get("upload_ticker", "")
    
        ticker = st.text_input("Ticker Symbol", value=default_ticker).upper()
    
        if ticker:
            # Multiple file upload
            uploaded_files = st.file_uploader(
                f"Upload documents for {ticker}",
                type=['html', 'htm', 'pdf', 'txt'],
                accept_multiple_files=True
            )
        
            if uploaded_files:
                st.write(f"Selected {len(uploaded_files)} files")
            
                # Show file details
                for file in uploaded_files:
                    doc_type = detect_document_type(Path(file.name))
                    st.write(f"- {file.name} ({doc_type})")
            
                if st.button("Process All Files"):
                    progress = st.progress(0)
                    status = st.empty()
                
                    for i, file in enumerate(uploaded_files):
                        # Save file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{ticker}_{file.name.replace(' ', '_')}_{timestamp}"
                        file_path = DOCUMENTS_DIR / filename
                    
                        # Ensure directory exists
                        DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
                    
                        with open(file_path, 'wb') as f:
                            f.write(file.read())
                    
                        status.info(f"Processing {file.name}...")
                    
                        # Trigger processing (will be implemented in document_processor.py)
                        # process_document(ticker, file_path)
                    
                        progress.progress((i + 1) / len(uploaded_files))
                
                    status.success(f"Successfully uploaded {len(uploaded_files)} documents!")
                
                    # Clear upload ticker
                    if "upload_ticker" in st.session_state:
                        del st.session_state.upload_ticker

    def show_coverage_report():
        """Show document coverage report"""
        st.header("Coverage Report")
    
        ipos = load_ipo_calendar()
    
        if not ipos:
            st.warning("No IPO data found")
            return
    
        # Calculate coverage for all IPOs
        coverage_data = []
        for ipo in ipos:
            ticker = ipo.get("ticker", "")
            coverage = get_document_coverage(ticker)
            coverage_pct = calculate_coverage_percentage(coverage)
        
            coverage_data.append({
                "Ticker": ticker,
                "Company": ipo.get("company", ""),
                "Expected Date": ipo.get("expected_date", ""),
                "Coverage %": coverage_pct,
                "S-1": "✓" if coverage["S-1"] else "✗",
                "424B4": "✓" if coverage["424B4"] else "✗",
                "Lock-up": "✓" if coverage["LOCK_UP"] else "✗",
                "Underwriting": "✓" if coverage["UNDERWRITING"] else "✗",
                "8-A": "✓" if coverage["8-A"] else "✗"
            })
    
        # Convert to DataFrame
        df = pd.DataFrame(coverage_data)
    
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_coverage = df["Coverage %"].mean()
            st.metric("Average Coverage", f"{avg_coverage:.1f}%")
        with col2:
            full_coverage = len(df[df["Coverage %"] >= 80])
            st.metric("Full Coverage", f"{full_coverage}/{len(df)}")
        with col3:
            no_docs = len(df[df["Coverage %"] == 0])
            st.metric("No Documents", no_docs)
    
        # Display table
        st.dataframe(
            df.sort_values("Coverage %", ascending=False),
            use_container_width=True,
            hide_index=True
        )
    
        # Export option
        if st.button("Export Report"):
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                file_name=f"coverage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    if __name__ == "__main__":
        main()
