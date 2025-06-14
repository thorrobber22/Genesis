"""
watchlist.py - Watchlist management component
Date: 2025-06-12 01:25:00 UTC
User: thorrobber22
"""

import streamlit as st
from services.data_service import get_watchlist, update_watchlist, get_company_data

def show_watchlist():
    """Display and manage user watchlist"""
    st.header("My Watchlist")
    
    # Get current watchlist
    watchlist = get_watchlist()
    
    if not watchlist:
        st.info("Your watchlist is empty. Add companies from the IPO Calendar or Company pages.")
        return
    
    # Display watchlist
    st.write(f"Tracking {len(watchlist)} companies")
    
    # Create columns for display
    for i in range(0, len(watchlist), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(watchlist):
                ticker = watchlist[i + j]
                with col:
                    with st.container():
                        # Get company data
                        company_data = get_company_data(ticker)
                        
                        # Display card
                        st.markdown(f"""
                        <div style="background-color: #2A2B2D; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                            <h4 style="color: #F7F7F8; margin: 0;">{ticker}</h4>
                            <p style="color: #A3A3A3; margin: 5px 0; font-size: 14px;">
                                {company_data.get('name', 'Company Name')}
                            </p>
                            <p style="color: #10A37F; margin: 5px 0; font-size: 12px;">
                                {company_data.get('sector', 'Sector')}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Remove button
                        if st.button(f"Remove {ticker}", key=f"remove_{ticker}"):
                            update_watchlist(ticker, "remove")
                            st.rerun()
    
    # Export watchlist
    st.divider()
    if st.button("Export Watchlist"):
        watchlist_text = "\n".join(watchlist)
        st.download_button(
            label="Download as TXT",
            data=watchlist_text,
            file_name=f"watchlist_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    # For testing
    show_watchlist()
