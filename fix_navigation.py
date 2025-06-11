# fix_navigation.py
#!/usr/bin/env python3
"""
Add sidebar navigation to hedge_intelligence.py
"""

from pathlib import Path

def update_main_app_navigation():
    """Add sidebar and page routing to main app"""
    
    # Read current app
    app_path = Path("hedge_intelligence.py")
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if sidebar already exists
    if 'st.sidebar' in content:
        print("Sidebar already exists - updating...")
    
    # Insert navigation code after imports
    navigation_code = '''
# Page state management
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# Sidebar Navigation
with st.sidebar:
    st.title("Hedge Intelligence")
    st.markdown("---")
    
    # Navigation menu
    st.session_state.current_page = st.selectbox(
        "Navigation",
        ["Dashboard", "Document Explorer", "IPO Tracker", 
         "Watchlist", "Search", "Company Management"],
        index=["Dashboard", "Document Explorer", "IPO Tracker", 
               "Watchlist", "Search", "Company Management"].index(st.session_state.current_page)
    )
    
    st.markdown("---")
    
    # Quick stats
    if doc_service:
        companies = doc_service.get_companies()
        total_docs = sum(len(doc_service.get_company_documents(c)) for c in companies)
        st.caption(f"Companies: {len(companies)}")
        st.caption(f"Documents: {total_docs}")
    
    st.caption("Updated: Every 30 min")
'''
    
    # Add page routing
    routing_code = '''
# Main content area based on navigation
if st.session_state.current_page == "Dashboard":
    render_dashboard()
elif st.session_state.current_page == "Document Explorer":
    render_document_explorer()
elif st.session_state.current_page == "IPO Tracker":
    render_ipo_tracker()
elif st.session_state.current_page == "Watchlist":
    render_watchlist()
elif st.session_state.current_page == "Search":
    render_search()
elif st.session_state.current_page == "Company Management":
    render_company_management()
'''
    
    # Create page functions
    page_functions = '''
def render_dashboard():
    """Dashboard with IPO calendar and watchlist updates"""
    st.title("Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("IPO Calendar")
        # Load IPO data
        ipo_data = load_ipo_calendar()
        if ipo_data:
            for ipo in ipo_data[:5]:  # Show top 5
                with st.container():
                    st.write(f"**{ipo.get('company', 'Unknown')}**")
                    st.caption(f"{ipo.get('date', 'TBD')} | {ipo.get('underwriter', 'N/A')} | ${ipo.get('valuation', 'N/A')}")
        else:
            st.info("No upcoming IPOs")
    
    with col2:
        st.subheader("Watchlist Updates")
        # TODO: Implement watchlist updates
        st.info("No new filings")

def render_document_explorer():
    """Document Explorer page"""
    st.title("Document Explorer")
    
    if doc_service:
        companies = doc_service.get_companies()
        
        # Company selector
        selected_company = st.selectbox("Select Company", companies)
        
        if selected_company:
            # Get documents
            documents = doc_service.get_company_documents(selected_company)
            
            # Group by type
            doc_types = {}
            for doc in documents:
                doc_type = doc.get('type', 'Other')
                if doc_type not in doc_types:
                    doc_types[doc_type] = []
                doc_types[doc_type].append(doc)
            
            # Display by type
            for doc_type, docs in doc_types.items():
                with st.expander(f"{doc_type} ({len(docs)} documents)"):
                    for doc in docs:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(doc['name'])
                        with col2:
                            if st.button("View", key=f"view_{doc['name']}"):
                                st.session_state.selected_document = doc
                                # TODO: Open document viewer

def render_ipo_tracker():
    """IPO Tracker page"""
    st.title("IPO Tracker")
    
    # Load IPO data
    ipo_data = load_ipo_calendar()
    
    if ipo_data:
        # Create dataframe for display
        df = pd.DataFrame(ipo_data)
        st.dataframe(df)
    else:
        st.info("No IPO data available")

def render_watchlist():
    """Watchlist page"""
    st.title("Watchlist")
    
    # Load watchlist
    watchlist = load_watchlist()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if watchlist:
            for company in watchlist:
                st.write(f"- {company}")
        else:
            st.info("No companies in watchlist")
    
    with col2:
        # Add company
        new_company = st.text_input("Add Company (Ticker)")
        if st.button("Add") and new_company:
            add_to_watchlist(new_company.upper())
            st.rerun()

def render_search():
    """Search page"""
    st.title("Search Documents")
    
    # Search input
    query = st.text_input("Search across all documents")
    
    if query and st.button("Search"):
        with st.spinner("Searching..."):
            # Use ChatEngine's search
            results = search_documents(query)
            
            if results:
                st.write(f"Found {len(results)} results")
                for result in results:
                    with st.expander(f"{result['company']} - {result['document']}"):
                        st.write(result['excerpt'])
                        if st.button("Open Document", key=f"open_{result['id']}"):
                            # TODO: Open document
                            pass
            else:
                st.info("No results found")

def render_company_management():
    """Company Management page"""
    st.title("Company Management")
    
    tab1, tab2 = st.tabs(["Available Companies", "Request New Company"])
    
    with tab1:
        if doc_service:
            companies = doc_service.get_companies()
            
            for company in companies:
                docs = doc_service.get_company_documents(company)
                st.write(f"**{company}** - {len(docs)} documents")
    
    with tab2:
        st.subheader("Request New Company")
        
        with st.form("company_request"):
            company_name = st.text_input("Company Name")
            ticker = st.text_input("Ticker Symbol")
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            reason = st.text_area("Reason for Request")
            
            if st.form_submit_button("Submit Request"):
                save_company_request({
                    "company_name": company_name,
                    "ticker": ticker.upper(),
                    "priority": priority,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat(),
                    "user": "analyst"
                })
                st.success("Request submitted!")
'''

def create_helper_functions():
    """Create helper functions for data loading"""
    
    helpers = '''
# helper_functions.py
import json
from pathlib import Path
import pandas as pd

def load_ipo_calendar():
    """Load IPO calendar data"""
    ipo_file = Path("data/ipo_calendar.json")
    if ipo_file.exists():
        with open(ipo_file, 'r') as f:
            data = json.load(f)
            # Filter out fake companies
            fake_companies = ["Stripe", "SpaceX", "Databricks", "Canva", "Instacart"]
            return [ipo for ipo in data if ipo.get('company') not in fake_companies]
    return []

def load_watchlist():
    """Load user watchlist"""
    watchlist_file = Path("data/watchlist.json")
    if watchlist_file.exists():
        with open(watchlist_file, 'r') as f:
            return json.load(f)
    return []

def add_to_watchlist(ticker):
    """Add company to watchlist"""
    watchlist_file = Path("data/watchlist.json")
    watchlist = load_watchlist()
    
    if ticker not in watchlist:
        watchlist.append(ticker)
        with open(watchlist_file, 'w') as f:
            json.dump(watchlist, f, indent=2)

def save_company_request(request_data):
    """Save company request"""
    requests_file = Path("data/company_requests.json")
    
    if requests_file.exists():
        with open(requests_file, 'r') as f:
            requests = json.load(f)
    else:
        requests = []
    
    requests.append(request_data)
    
    with open(requests_file, 'w') as f:
        json.dump(requests, f, indent=2)

def search_documents(query):
    """Search documents using ChatEngine"""
    # TODO: Implement using ChatEngine's ChromaDB
    return []
'''
    
    with open("helper_functions.py", 'w', encoding='utf-8') as f:
        f.write(helpers)

# Execute
if __name__ == "__main__":
    create_helper_functions()
    print("Created helper_functions.py")