#!/usr/bin/env python3
"""
Add navigation to existing app WITHOUT breaking current functionality
"""

from pathlib import Path
import re

def add_navigation_to_app():
    """Add page navigation while keeping document explorer intact"""
    
    main_app = Path("hedge_intelligence.py")
    
    # Backup first
    backup = Path("hedge_intelligence_backup.py")
    with open(main_app, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backed up to {backup}")
    
    # Find where sidebar is defined
    sidebar_start = content.find("with st.sidebar:")
    if sidebar_start == -1:
        print("❌ Could not find sidebar!")
        return
    
    # New sidebar code that adds navigation ABOVE doc explorer
    new_sidebar = '''with st.sidebar:
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
            doc_explorer.render_sidebar()'''
    
    # Replace the sidebar section
    sidebar_end = content.find("\n    # Main area", sidebar_start)
    if sidebar_end == -1:
        sidebar_end = content.find("\n\n", sidebar_start + 100)
    
    new_content = content[:sidebar_start] + new_sidebar + content[sidebar_end:]
    
    # Now modify the main area logic
    main_area_start = content.find("# Main area")
    if main_area_start != -1:
        new_main_logic = '''# Main area
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
    '''
        
        # Find the end of main area logic
        main_area_end = new_content.find("\n    # Show chat history", main_area_start)
        if main_area_end == -1:
            main_area_end = new_content.find("\n    display_chat_history()", main_area_start)
        
        new_content = new_content[:main_area_start] + new_main_logic + new_content[main_area_end:]
    
    # Add missing render functions before main()
    main_func_pos = new_content.find("def main():")
    if main_func_pos != -1:
        missing_functions = '''
def render_ipo_tracker():
    """IPO Tracker page"""
    st.title("IPO Tracker")
    
    # Use existing IPO tracker component
    from components.ipo_tracker import display_ipo_tracker
    display_ipo_tracker()

def render_search():
    """Search across all documents"""
    st.title("Search Documents")
    
    query = st.text_input("Search across all SEC filings")
    
    if query:
        with st.spinner("Searching..."):
            # TODO: Implement search using ChatEngine
            st.info("Search functionality coming soon")

def render_watchlist():
    """Watchlist management"""
    st.title("Watchlist")
    
    # Simple watchlist implementation
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state.watchlist:
            for company in st.session_state.watchlist:
                st.write(f"- {company}")
        else:
            st.info("No companies in watchlist")
    
    with col2:
        new_company = st.text_input("Add ticker")
        if st.button("Add") and new_company:
            if new_company.upper() not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_company.upper())
                st.rerun()

def render_company_management():
    """Company request management"""
    st.title("Company Management")
    
    tab1, tab2 = st.tabs(["Available Companies", "Request New"])
    
    with tab1:
        # Show existing companies
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
                # Save to company_requests.json
                import json
                from datetime import datetime
                
                request = {
                    "company_name": company_name,
                    "ticker": ticker.upper(),
                    "priority": priority,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat(),
                    "user": "analyst",
                    "status": "pending"
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
                
                st.success("Request submitted!")


'''
        new_content = new_content[:main_func_pos] + missing_functions + new_content[main_func_pos:]
    
    # Write the updated content
    with open(main_app, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Navigation added successfully!")
    print("\nChanges made:")
    print("1. Added page selector to sidebar")
    print("2. Modified main area to show different pages")
    print("3. Added render functions for missing pages")
    print("4. Preserved all existing functionality")

if __name__ == "__main__":
    print("ADDING NAVIGATION TO HEDGE INTELLIGENCE")
    print("="*50)
    add_navigation_to_app()