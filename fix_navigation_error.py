#!/usr/bin/env python3
# fix_navigation_error.py
"""
Fix the broken navigation implementation
"""

from pathlib import Path

def fix_navigation_error():
    """Fix the page variable error"""
    
    main_app = Path("hedge_intelligence.py")
    
    # Read current broken content
    with open(main_app, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("FIXING NAVIGATION ERROR")
    print("-"*40)
    
    # Find the broken sidebar section
    sidebar_start = content.find("with st.sidebar:")
    if sidebar_start == -1:
        print("❌ Cannot find sidebar!")
        return
    
    # Find where the sidebar SHOULD end
    sidebar_end = content.find("# Main area", sidebar_start)
    
    # Replace with correct sidebar code
    fixed_sidebar = '''with st.sidebar:
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

    '''
    
    # Reconstruct the content
    new_content = content[:sidebar_start] + fixed_sidebar + content[sidebar_end:]
    
    # Save fixed version
    with open(main_app, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Fixed navigation error!")
    print("✅ Page variable now properly defined in sidebar")

if __name__ == "__main__":
    fix_navigation_error()