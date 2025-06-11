#!/usr/bin/env python3
"""
Update main app to use Smart Watchlist
"""

print("""
📝 Manual Update Instructions for hedge_intelligence.py:

1. Add to imports section:
   from components.smart_watchlist import render_smart_watchlist, get_watchlist_alert_count

2. Replace the render_watchlist() function with:
   def render_watchlist():
       '''Smart Watchlist page'''
       render_smart_watchlist()

3. In the page navigation, update the watchlist option to show alert count:
   # Get alert count
   alert_count = get_watchlist_alert_count()
   watchlist_label = "Watchlist" if alert_count == 0 else f"Watchlist ({alert_count})"
   
   # In the selectbox
   page = st.selectbox(
       "Navigate to",
       ["Dashboard", "Document Explorer", "IPO Tracker", "Search", watchlist_label, "Company Management"],
       key="main_navigation"
   )

4. Test the integration:
   streamlit run hedge_intelligence.py
""")

# Create test file
test_content = '''import streamlit as st
from components.smart_watchlist import render_smart_watchlist

st.set_page_config(page_title="Smart Watchlist Test", layout="wide")
st.title("🔔 Smart Watchlist Test")

# Add some test data
if st.button("Add Test Alert"):
    from components.smart_watchlist import SmartWatchlist
    watchlist = SmartWatchlist()
    watchlist._create_alert(
        ticker="AAPL",
        title="Test Alert",
        message="This is a test alert",
        alert_type="new_filing"
    )
    st.success("Test alert created!")
    st.rerun()

# Render watchlist
render_smart_watchlist()
'''

with open("test_smart_watchlist.py", 'w') as f:
    f.write(test_content)

print("\n✅ Smart Watchlist component created!")
print("\n🧪 Test it first:")
print("streamlit run test_smart_watchlist.py")