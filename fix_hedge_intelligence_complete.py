#!/usr/bin/env python3
"""
Complete fix for all Hedge Intelligence errors
Fixes imports, navigation, chat context, and all runtime errors
"""

from pathlib import Path
import json
from datetime import datetime

def fix_hedge_intelligence_complete():
    """Fix all errors in the main app"""
    
    print("HEDGE INTELLIGENCE - COMPLETE FIX")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("="*80)
    
    # Read main file
    main_file = Path("hedge_intelligence.py")
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_file = Path(f"hedge_intelligence_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backed up to {backup_file}")
    
    # FIX 1: Add all missing imports at the top
    print("\n1. Fixing imports...")
    
    # Find where to insert imports (after existing imports)
    import_insert_point = content.find("from services.ai_service import AIService")
    if import_insert_point != -1:
        import_insert_point = content.find("\n", import_insert_point) + 1
        
        # Add missing imports
        missing_imports = """import pandas as pd
from datetime import datetime
"""
        
        # Only add if not already present
        if "import pandas as pd" not in content:
            content = content[:import_insert_point] + missing_imports + content[import_insert_point:]
            print("   ✅ Added pandas import")
    
    # FIX 2: Fix render_ipo_tracker
    print("\n2. Fixing IPO Tracker...")
    
    new_ipo_tracker = '''def render_ipo_tracker():
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
        st.warning("IPO calendar file not found. Initialize from admin panel.")'''
    
    # Replace the function
    func_start = content.find("def render_ipo_tracker():")
    if func_start != -1:
        func_end = content.find("\ndef ", func_start + 1)
        if func_end == -1:
            func_end = len(content)
        content = content[:func_start] + new_ipo_tracker + "\n" + content[func_end:]
        print("   ✅ Fixed IPO Tracker")
    
    # FIX 3: Fix render_search
    print("\n3. Fixing Search...")
    
    new_search = '''def render_search():
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
        """)'''
    
    # Replace the function
    func_start = content.find("def render_search():")
    if func_start != -1:
        func_end = content.find("\ndef ", func_start + 1)
        if func_end == -1:
            func_end = len(content)
        content = content[:func_start] + new_search + "\n" + content[func_end:]
        print("   ✅ Fixed Search")
    
    # FIX 4: Fix render_watchlist
    print("\n4. Fixing Watchlist...")
    
    new_watchlist = '''def render_watchlist():
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
        st.info("Your watchlist is empty. Add companies to start tracking them.")'''
    
    # Replace the function
    func_start = content.find("def render_watchlist():")
    if func_start != -1:
        func_end = content.find("\ndef ", func_start + 1)
        if func_end == -1:
            func_end = len(content)
        content = content[:func_start] + new_watchlist + "\n" + content[func_end:]
        print("   ✅ Fixed Watchlist")
    
    # FIX 5: Fix render_company_management
    print("\n5. Fixing Company Management...")
    
    new_company_mgmt = '''def render_company_management():
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
                    st.caption(f"• {company} ({doc_count} docs)")'''
    
    # Replace the function
    func_start = content.find("def render_company_management():")
    if func_start != -1:
        func_end = content.find("\ndef ", func_start + 1)
        if func_end == -1:
            func_end = len(content)
        content = content[:func_start] + new_company_mgmt + "\n" + content[func_end:]
        print("   ✅ Fixed Company Management")
    
    # FIX 6: Fix render_analyst_dashboard
    print("\n6. Fixing Dashboard...")
    
    # Find the dashboard function and fix the pd.Timestamp error
    dashboard_fix = content.replace(
        "'timestamp': pd.Timestamp.now().isoformat()",
        "'timestamp': datetime.now().isoformat()"
    )
    content = dashboard_fix
    print("   ✅ Fixed Dashboard timestamp")
    
    # FIX 7: Fix persistent chat context
    print("\n7. Fixing Chat Context...")
    
    # Find where chat is initialized and ensure it uses current document
    chat_context_fix = '''
    # Update chat context when document is selected
    if 'selected_doc' in st.session_state and st.session_state.selected_doc:
        doc_path = Path(st.session_state.selected_doc)
        if doc_path.exists():
            st.session_state['current_document'] = doc_path.name
            st.session_state['current_company'] = doc_path.parent.name
'''
    
    # Add this after document viewer render
    viewer_section = content.find("render_document_viewer()")
    if viewer_section != -1:
        insert_point = content.find("\n", viewer_section) + 1
        content = content[:insert_point] + chat_context_fix + content[insert_point:]
        print("   ✅ Added chat context update")
    
    # Save the fixed file
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "="*80)
    print("✅ ALL FIXES APPLIED!")
    print("="*80)
    print("\nFixed:")
    print("1. ✅ Missing imports (pandas)")
    print("2. ✅ IPO Tracker function")
    print("3. ✅ Search functionality")
    print("4. ✅ Watchlist page")
    print("5. ✅ Company Management")
    print("6. ✅ Dashboard timestamp")
    print("7. ✅ Chat context tracking")
    
    return True

if __name__ == "__main__":
    fix_hedge_intelligence_complete()