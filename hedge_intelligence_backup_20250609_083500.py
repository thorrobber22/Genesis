"""
Hedge Intelligence - SEC Document Analysis Platform
Refactored: 2025-06-07 21:50:17 UTC
Author: thorrobber22
"""

import streamlit as st
from pathlib import Path
import json

# Import components
from components.document_explorer import DocumentExplorer
from components.persistent_chat import PersistentChat
from components.ipo_tracker_enhanced import IPOTrackerEnhanced
from components.data_extractor import DataExtractor
from services.document_service import DocumentService
from services.ai_service import AIService
import pandas as pd
from datetime import datetime

def apply_cream_theme():
    """Apply Apple-style cream theme"""
    st.markdown("""
    <style>
    /* Hedge Intelligence - Premium Apple Theme */
    
    /* Remove Streamlit defaults */
    .stApp {
        background-color: #FAFAF8;
    }
    
    /* Main content area */
    .main {
        background-color: #FAFAF8;
        color: #1A1A1A;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1A1A1A !important;
        font-weight: 600;
    }
    
    /* Text */
    p, span, div {
        color: #1A1A1A;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #F5F5F3;
    }
    
    /* Buttons - Dark with blue hover */
    .stButton > button {
        background-color: #2D2D2D;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #007AFF;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 122, 255, 0.15);
    }
    
    /* Cards and containers */
    .css-1r6slb0, .css-12oz5g7 {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    /* Input fields */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        color: #1A1A1A;
        border-radius: 8px;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
        border-color: #007AFF;
        box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.1);
    }
    
    /* Links */
    a {
        color: #1A1A1A;
        text-decoration: none;
        transition: color 0.2s;
    }
    
    a:hover {
        color: #007AFF;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    
    /* Remove blue progress bars */
    .stProgress > div > div > div {
        background-color: #34C759;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        border-radius: 12px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #F5F5F3;
        color: #1A1A1A;
        border-radius: 8px;
    }
    
    /* Data editor/tables */
    .glideDataEditor {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }
    
    /* Remove all remaining blue */
    .css-1cpxqw2, .css-1v0mbdj > img {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
def render_document_viewer():

    # Update chat context when document is selected
    if 'selected_doc' in st.session_state and st.session_state.selected_doc:
        doc_path = Path(st.session_state.selected_doc)
        if doc_path.exists():
            st.session_state['current_document'] = doc_path.name
            st.session_state['current_company'] = doc_path.parent.name
    """Render document viewer"""
    if 'selected_doc' not in st.session_state:
        return
        
    doc = st.session_state.selected_doc
    st.header(f"{doc['company']} - {doc['document']}")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("View PDF"):
            st.info("PDF export available in premium version")
    with col2:
        if st.button("Download"):
            st.info("Download ready")
    
    # Load and display document
    try:
        with open(doc['path'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract key data
        with st.expander("Quick Extractions"):
            extractor = DataExtractor()
            
            col1, col2 = st.columns(2)
            with col1:
                revenue = extractor.extract_with_citations(content, 'revenue')
                if revenue['status'] == 'found':
                    st.metric(
                        "Revenue", 
                        f"${revenue['value']} {revenue.get('unit', '')}",
                        help=f"Source: {revenue['citation']}"
                    )
                    
            with col2:
                employees = extractor.extract_with_citations(content, 'employees')
                if employees['status'] == 'found':
                    st.metric(
                        "Employees",
                        employees['value'],
                        help=f"Source: {employees['citation']}"
                    )
        
        # Show document content
        st.markdown("### Document Content")
        # Show first 5000 chars in a scrollable container
        st.markdown(
            f'<div style="height: 400px; overflow-y: scroll; padding: 1rem; '
            f'background-color: #1A1D23; border: 1px solid #2D3748; border-radius: 4px;">'
            f'{content[:5000]}...</div>',
            unsafe_allow_html=True
        )
        
    except Exception as e:
        st.error(f"Error loading document: {e}")

def render_analyst_dashboard():
    """Render simplified analyst dashboard"""
    st.header("SEC Document Analysis Platform")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    doc_path = Path("data/sec_documents")
    if doc_path.exists():
        companies = len(list(doc_path.iterdir()))
        total_docs = sum(
            len(list(Path(f"data/sec_documents/{c}").glob("*.html")))
            for c in doc_path.iterdir() if c.is_dir()
        )
    else:
        companies = 0
        total_docs = 0
    
    with col1:
        st.metric("Companies Available", companies)
    with col2:
        st.metric("Total Documents", f"{total_docs:,}")
    with col3:
        if st.button("Request New Company"):
            st.session_state.show_company_request = True
            
    # IPO Tracker
    st.markdown("---")
    ipo_tracker = IPOTrackerEnhanced()
    ipo_tracker.render_ipo_dashboard()
    
    # Company Request Form
    if st.session_state.get('show_company_request', False):
        with st.form("company_request"):
            st.subheader("Request New Company")
            company = st.text_input("Company Name")
            ticker = st.text_input("Ticker Symbol")
            priority = st.radio("Priority", ["High", "Medium", "Low"])
            reason = st.text_area("Reason for Request")
            
            if st.form_submit_button("Submit Request"):
                # Save request
                request = {
                    'company': company,
                    'ticker': ticker,
                    'priority': priority,
                    'reason': reason,
                    'status': 'pending',
                    'timestamp': datetime.now().isoformat()
                }
                
                requests_file = Path("data/company_requests.json")
                if requests_file.exists():
                    with open(requests_file, 'r') as f:
                        requests = json.load(f)
                else:
                    requests = []
                    
                requests.append(request)
                
                with open(requests_file, 'w') as f:
                    json.dump(requests, f, indent=2)
                    
                st.success("Request submitted! Will be processed within 30 minutes.")
                st.session_state.show_company_request = False
                st.rerun()

def display_chat_history():
    """Display chat history in main area"""
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        st.markdown("### Recent Analysis")
        for item in st.session_state.chat_history[-3:]:
            with st.container():
                st.markdown(f"**Q:** {item['query']}")
                st.markdown(f"**A:** {item['response']}")
                if item.get('document'):
                    st.caption(f"Context: {item['document']['company']} - {item['document']['document']}")
                st.markdown("---")


def render_ipo_tracker():
    """IPO Tracker page"""
    st.header("📈 IPO Tracker")
    st.caption("Track upcoming and recent IPOs")
    
    # Load IPO data
    ipo_file = Path("data/ipo_calendar.json")
    
    if ipo_file.exists():
        with open(ipo_file, 'r', encoding='utf-8') as f:
            ipo_data = json.load(f)
        
        if ipo_data:
            # Display IPOs in a table
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Current & Upcoming IPOs")
                
                # Convert to DataFrame for display
                df = pd.DataFrame(ipo_data)
                
                # Display key columns if they exist
                display_cols = ['company', 'symbol', 'price_range', 'shares', 'expected_date']
                available_cols = [col for col in display_cols if col in df.columns]
                
                if available_cols:
                    st.dataframe(df[available_cols], use_container_width=True)
                else:
                    st.dataframe(df, use_container_width=True)
            
            with col2:
                st.metric("Total IPOs", len(ipo_data))
                
                # Add refresh button
                if st.button("🔄 Refresh IPO Data", use_container_width=True):
                    st.info("Run IPO scraper from admin panel to update data")
        else:
            st.info("No IPO data available. Run the IPO scraper from the admin panel to populate data.")
            
            # Show sample of what it would look like
            st.subheader("Sample IPO Data")
            sample_data = [
                {"company": "Example Corp", "symbol": "EXMP", "price_range": "$15-17", "shares": "10M", "expected_date": "2025-01-15"},
                {"company": "Tech Startup Inc", "symbol": "TECH", "price_range": "$22-25", "shares": "5M", "expected_date": "2025-01-20"}
            ]
            st.dataframe(pd.DataFrame(sample_data), use_container_width=True)
    else:
        st.warning("IPO calendar file not found. Initialize from admin panel.")

def render_search():
    """Search page"""
    st.header("🔍 Search Documents")
    st.caption("Search across all SEC filings")
    
    # Search input
    search_query = st.text_input("", placeholder="Search for companies, tickers, or content...", 
                                key="search_input", label_visibility="collapsed")
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        search_button = st.button("🔍 Search", use_container_width=True, type="primary")
    with col2:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state.search_results = None
            st.rerun()
    
    # Perform search
    if search_button and search_query:
        with st.spinner("Searching documents..."):
            # Simple file-based search for now
            results = []
            sec_dir = Path("data/sec_documents")
            
            if sec_dir.exists():
                for company_dir in sec_dir.iterdir():
                    if company_dir.is_dir():
                        for doc_file in company_dir.glob("*.html"):
                            try:
                                with open(doc_file, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read().lower()
                                
                                if search_query.lower() in content:
                                    results.append({
                                        'company': company_dir.name,
                                        'document': doc_file.name,
                                        'path': str(doc_file),
                                        'size': doc_file.stat().st_size
                                    })
                                    
                                    if len(results) >= 20:  # Limit results
                                        break
                            except:
                                continue
                    
                    if len(results) >= 20:
                        break
            
            st.session_state.search_results = results
    
    # Display results
    if 'search_results' in st.session_state and st.session_state.search_results:
        st.subheader(f"Found {len(st.session_state.search_results)} results")
        
        for result in st.session_state.search_results:
            with st.container():
                col1, col2, col3 = st.columns([2, 3, 1])
                
                with col1:
                    st.markdown(f"**{result['company']}**")
                
                with col2:
                    st.caption(result['document'])
                
                with col3:
                    if st.button("View", key=f"view_{result['document']}", use_container_width=True):
                        st.session_state.selected_doc = result['path']
                        st.session_state.selected_company = result['company']
                        st.session_state.main_navigation = "Document Explorer"
                        st.rerun()
                
                st.divider()
    elif search_query:
        st.info("No results found. Try a different search term.")
    
    # Search tips
    with st.expander("Search Tips"):
        st.write("""
        - Search for company names: "Apple", "Tesla", "Circle"
        - Search for tickers: "AAPL", "TSLA", "CRCL"
        - Search for content: "revenue", "risk factors", "financial statements"
        - Search is case-insensitive
        """)

def render_watchlist():
    """Watchlist page"""
    st.header("⭐ Watchlist")
    st.caption("Track your favorite companies")
    
    # Initialize watchlist in session state
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []
    
    # Add company form
    with st.expander("➕ Add to Watchlist", expanded=False):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Get available companies
            sec_dir = Path("data/sec_documents")
            companies = []
            if sec_dir.exists():
                companies = [d.name for d in sec_dir.iterdir() if d.is_dir()]
            
            new_company = st.selectbox("Select Company", [""] + companies)
        
        with col2:
            if st.button("Add", use_container_width=True, disabled=not new_company):
                if new_company and new_company not in st.session_state.watchlist:
                    st.session_state.watchlist.append(new_company)
                    st.success(f"Added {new_company} to watchlist!")
                    st.rerun()
    
    # Display watchlist
    if st.session_state.watchlist:
        st.subheader("Your Watched Companies")
        
        for company in st.session_state.watchlist:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**{company}**")
                
                with col2:
                    # Count documents
                    company_dir = Path(f"data/sec_documents/{company}")
                    if company_dir.exists():
                        doc_count = len(list(company_dir.glob("*.html")))
                        st.caption(f"{doc_count} documents")
                
                with col3:
                    if st.button("View", key=f"view_watch_{company}", use_container_width=True):
                        st.session_state.selected_company = company
                        st.session_state.main_navigation = "Document Explorer"
                        st.rerun()
                
                with col4:
                    if st.button("Remove", key=f"remove_watch_{company}", use_container_width=True):
                        st.session_state.watchlist.remove(company)
                        st.rerun()
                
                # Show recent filings
                if company_dir.exists():
                    recent_files = sorted(company_dir.glob("*.html"), 
                                        key=lambda x: x.stat().st_mtime, reverse=True)[:3]
                    if recent_files:
                        st.caption("Recent filings:")
                        for f in recent_files:
                            st.caption(f"  • {f.name}")
                
                st.divider()
        
        # Save watchlist button
        if st.button("💾 Save Watchlist", use_container_width=True):
            watchlist_file = Path("data/watchlists.json")
            watchlist_file.parent.mkdir(exist_ok=True)
            
            with open(watchlist_file, 'w', encoding='utf-8') as f:
                json.dump({"default": st.session_state.watchlist}, f, indent=2)
            
            st.success("Watchlist saved!")
    else:
        st.info("Your watchlist is empty. Add companies to start tracking them.")

def render_company_management():
    """Company Management page"""
    st.header("🏢 Company Management")
    st.caption("Request new companies to be added")
    
    # Initialize requests file
    requests_file = Path("data/company_requests.json")
    requests_file.parent.mkdir(exist_ok=True)
    
    # Load existing requests
    if requests_file.exists():
        with open(requests_file, 'r', encoding='utf-8') as f:
            requests = json.load(f)
    else:
        requests = []
    
    # Request form
    st.subheader("📝 Request New Company")
    
    with st.form("company_request_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name", placeholder="e.g., Microsoft Corporation")
            ticker = st.text_input("Ticker Symbol", placeholder="e.g., MSFT")
        
        with col2:
            priority = st.selectbox("Priority", ["Normal", "High", "Urgent"])
            reason = st.text_area("Reason for Request", placeholder="Why do you need this company's documents?")
        
        submitted = st.form_submit_button("Submit Request", use_container_width=True, type="primary")
        
        if submitted and company_name and ticker:
            new_request = {
                'company_name': company_name,
                'ticker': ticker.upper(),
                'priority': priority,
                'reason': reason,
                'status': 'pending',
                'requested_by': 'user',
                'timestamp': datetime.now().isoformat()
            }
            
            requests.append(new_request)
            
            # Save requests
            with open(requests_file, 'w', encoding='utf-8') as f:
                json.dump(requests, f, indent=2)
            
            st.success(f"Request submitted for {company_name} ({ticker})!")
            st.rerun()
    
    # Show existing requests
    st.subheader("📋 Your Requests")
    
    user_requests = [r for r in requests if r.get('requested_by') == 'user']
    
    if user_requests:
        # Group by status
        pending = [r for r in user_requests if r.get('status') == 'pending']
        processing = [r for r in user_requests if r.get('status') == 'processing']
        completed = [r for r in user_requests if r.get('status') == 'completed']
        
        # Show pending
        if pending:
            st.write("**Pending Requests**")
            for req in pending:
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.write(f"**{req['ticker']}** - {req['company_name']}")
                    with col2:
                        st.caption(f"Priority: {req['priority']}")
                    with col3:
                        st.caption("⏳ Pending")
                    st.caption(f"Requested: {req['timestamp'][:10]}")
                st.divider()
        
        # Show processing
        if processing:
            st.write("**Processing**")
            for req in processing:
                st.info(f"🔄 {req['ticker']} - Currently downloading documents...")
        
        # Show completed
        if completed:
            st.write("**Completed**")
            for req in completed:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.success(f"✅ {req['ticker']} - {req['company_name']}")
                with col2:
                    if st.button("View", key=f"view_completed_{req['ticker']}"):
                        st.session_state.selected_company = req['ticker']
                        st.session_state.main_navigation = "Document Explorer"
                        st.rerun()
    else:
        st.info("No requests yet. Submit a company request above.")
    
    # Show available companies
    with st.expander("📚 Already Available Companies"):
        sec_dir = Path("data/sec_documents")
        if sec_dir.exists():
            companies = sorted([d.name for d in sec_dir.iterdir() if d.is_dir()])
            
            cols = st.columns(3)
            for i, company in enumerate(companies):
                with cols[i % 3]:
                    doc_count = len(list((sec_dir / company).glob("*.html")))
                    st.caption(f"• {company} ({doc_count} docs)")

def main():
    st.set_page_config(
        page_title="Hedge Intelligence - SEC Analysis",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply theme
    apply_cream_theme()
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize components
    doc_explorer = DocumentExplorer()
    persistent_chat = PersistentChat()
    
    # Sidebar - Document Explorer
    with st.sidebar:
        st.title("Hedge Intelligence")
        st.caption("SEC Document Analysis Platform")
        st.markdown("---")
        
        # Page Navigation
        page = st.selectbox(
            "Navigate to",
            ["Dashboard", "Document Explorer", "IPO Tracker", "Search", "Watchlist", "Company Management"],
            key="main_navigation"
        )
        
        st.markdown("---")
        
        # Show doc explorer only on Document Explorer page
        if page == "Document Explorer":
            doc_explorer.render_sidebar()

    # Main area
    page = st.session_state.get('main_navigation', 'Dashboard')
    
    if page == "Dashboard":
        render_analyst_dashboard()
    elif page == "Document Explorer":
        if 'selected_doc' in st.session_state:
            render_document_viewer()
        else:
            st.info("Select a document from the sidebar to view")
    elif page == "IPO Tracker":
        render_ipo_tracker()
    elif page == "Search":
        render_search()
    elif page == "Watchlist":
        render_watchlist()
    elif page == "Company Management":
        render_company_management()
    
    # Show chat history
    display_chat_history()
    
    # Bottom - Persistent chat
    persistent_chat.render_chat_bar()

if __name__ == "__main__":
    main()
