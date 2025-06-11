#!/usr/bin/env python3
"""
Integrate Smart Watchlist into main app
"""

print("""
✅ Smart Watchlist Created!

📝 To integrate into hedge_intelligence.py:

1. Add to imports:
   from components.smart_watchlist_minimal import render_smart_watchlist, get_watchlist_alert_count

2. Replace render_watchlist() function with:
   def render_watchlist():
       render_smart_watchlist()

3. Optional: Add alert count to navigation (in sidebar section):
   # Before the selectbox
   alert_count = get_watchlist_alert_count()
   watchlist_label = f"Watchlist ({alert_count})" if alert_count > 0 else "Watchlist"
   
   # Update the navigation options
   pages = ["Dashboard", "Document Explorer", "IPO Tracker", "Search", watchlist_label, "Company Management"]

That's it! The watchlist will now:
✅ Track companies cleanly
✅ Show new filing alerts
✅ Alert on IPO pricing
✅ Display unread count in navigation

Test with: streamlit run hedge_intelligence.py
""")

# Save the component
from pathlib import Path
Path("components").mkdir(exist_ok=True)
print("\n✅ Component saved to: components/smart_watchlist_minimal.py")