#!/usr/bin/env python3
"""
Test Smart Watchlist - Clean and Simple
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import the watchlist component
from components.smart_watchlist_minimal import SmartWatchlist, render_smart_watchlist

def main():
    st.set_page_config(
        page_title="Watchlist Test",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.title("🧪 Smart Watchlist Test")
    
    # Test controls in sidebar
    with st.sidebar:
        st.header("Test Controls")
        
        # Add test companies
        if st.button("➕ Add Test Companies", use_container_width=True):
            watchlist = SmartWatchlist()
            
            # Add some test companies
            test_companies = [
                ("AAPL", "Apple Inc.", "Stock"),
                ("CRCL", "Circle Internet", "IPO"),
                ("TSLA", "Tesla Inc.", "Stock"),
                ("RDDT", "Reddit Inc.", "IPO")
            ]
            
            for ticker, name, type_ in test_companies:
                if ticker not in watchlist.watchlist:
                    watchlist.watchlist[ticker] = {
                        'ticker': ticker,
                        'company_name': name,
                        'added_date': '2025-06-10T04:00:00',
                        'type': type_,
                        'last_checked': '2025-06-09T00:00:00',
                        'status': 'Filed' if type_ == 'IPO' else ''
                    }
            
            watchlist._save_watchlist()
            st.success("✅ Added 4 test companies!")
            st.rerun()
        
        # Add test alerts
        if st.button("🔔 Add Test Alerts", use_container_width=True):
            watchlist = SmartWatchlist()
            
            # Create different types of alerts
            test_alerts = [
                ("AAPL", "New Filing: AAPL", "10-K_2025-06-09_companysearch.html", "filing"),
                ("CRCL", "IPO Priced: CRCL", "Priced at $15-17", "ipo_priced"),
                ("TSLA", "New Filing: TSLA", "8-K_2025-06-10_companysearch.html", "filing"),
                ("RDDT", "New Filing: RDDT", "S-1_A_2025-06-10_companysearch.html", "filing")
            ]
            
            for ticker, title, message, alert_type in test_alerts:
                watchlist._create_alert(ticker, title, message, alert_type)
            
            st.success("✅ Added 4 test alerts!")
            st.rerun()
        
        # Clear all data
        if st.button("🗑️ Clear All Data", use_container_width=True):
            watchlist = SmartWatchlist()
            watchlist.watchlist = {}
            watchlist.alerts = []
            watchlist._save_watchlist()
            watchlist._save_alerts()
            st.success("✅ Cleared all data!")
            st.rerun()
        
        st.divider()
        
        # Show current stats
        watchlist = SmartWatchlist()
        st.metric("Companies", len(watchlist.watchlist))
        st.metric("Total Alerts", len(watchlist.alerts))
        st.metric("Unread Alerts", watchlist.get_alert_count())
    
    # Main area - render the watchlist
    render_smart_watchlist()
    
    # Footer with tips
    with st.expander("💡 Testing Tips", expanded=False):
        st.markdown("""
        1. **Start Fresh**: Click "Clear All Data" to start with empty watchlist
        2. **Add Test Data**: Use "Add Test Companies" and "Add Test Alerts" 
        3. **Test Features**:
           - Add/remove companies manually
           - Mark alerts as read
           - Check for updates
           - View companies (will redirect to Document Explorer)
        4. **Check Clean Design**: 
           - Simple table layout
           - Clear alert indicators
           - No clutter
        """)

if __name__ == "__main__":
    main()