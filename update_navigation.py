# update_navigation.py
"""
Update existing app with proper navigation - NO REWRITES
"""

def add_sidebar_navigation():
    """Insert sidebar navigation into existing app"""
    
    # Read current app
    with open("hedge_intelligence.py", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find where to insert sidebar code
    # Look for st.set_page_config or after imports
    
    sidebar_code = '''
# Sidebar Navigation
with st.sidebar:
    st.title("Hedge Intelligence")
    st.markdown("---")
    
    page = st.selectbox(
        "Navigation",
        ["Dashboard", "Document Explorer", "IPO Tracker", 
         "Watchlist", "Search", "Company Management"]
    )
    
    st.markdown("---")
    st.caption("SEC Filing Analysis Platform")

# Page Routing
if page == "Dashboard":
    render_dashboard()
elif page == "Document Explorer":
    render_document_explorer()
elif page == "IPO Tracker":
    render_ipo_tracker()
# ... etc
'''
    
    # Insert at appropriate location
    # This preserves existing code