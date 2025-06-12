"""
components/ipo_tracker.py - Professional IPO tracking interface
NO EMOJIS. Clean tables. Bloomberg-style.
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta

def render_ipo_tracker():
    """Render IPO tracker with lockup monitoring"""
    
    st.markdown("## IPO Tracker", unsafe_allow_html=True)
    
    # Load IPO data
    ipo_files = list(Path("data/ipo_data").glob("*.json")) if Path("data/ipo_data").exists() else []
    
    if not ipo_files:
        st.info("No IPO data available. Run the IPO scraper to populate.")
        return
        
    # Get latest file
    latest_file = max(ipo_files, key=lambda x: x.stat().st_mtime)
    
    with open(latest_file, 'r') as f:
        ipo_data = json.load(f)
    
    # Recent Filings Table
    st.markdown("### Recent Filings")
    
    if 'filed' in ipo_data and ipo_data['filed']:
        # Create DataFrame
        filing_data = []
        for idx, ipo in enumerate(ipo_data['filed']):
            filing_data.append({
                'Company': ipo.get('company', 'Unknown'),
                'Ticker': ipo.get('ticker', 'N/A'),
                'Exchange': ipo.get('exchange', 'N/A'),
                'Filing Date': ipo.get('date', 'Unknown'),
                'Lead Manager': ipo.get('lead_manager', 'N/A')
            })
        
        df = pd.DataFrame(filing_data)
        
        # Display as clean table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Company": st.column_config.TextColumn("Company", width="medium"),
                "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                "Exchange": st.column_config.TextColumn("Exchange", width="small"),
                "Filing Date": st.column_config.TextColumn("Filing Date", width="small"),
                "Lead Manager": st.column_config.TextColumn("Lead Manager", width="medium")
            }
        )
        
        # Selection interface
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_idx = st.selectbox(
                "Select company to analyze:",
                options=range(len(filing_data)),
                format_func=lambda x: f"{filing_data[x]['Company']} ({filing_data[x]['Ticker']})"
            )
        with col2:
            if st.button("Analyze", type="primary", use_container_width=True):
                st.session_state.selected_company = filing_data[selected_idx]['Ticker']
                st.session_state.current_view = 'companies'
                st.rerun()
    else:
        st.info("No recent filings found")
    
    # Lockup Expirations Table
    st.markdown("### Upcoming Lockup Expirations")
    
    lockup_data = []
    if 'filed' in ipo_data:
        for ipo in ipo_data['filed']:
            if 'date' in ipo:
                try:
                    ipo_date = datetime.strptime(ipo['date'], '%Y-%m-%d')
                    lockup_date = ipo_date + timedelta(days=180)
                    days_until = (lockup_date - datetime.now()).days
                    
                    if days_until > 0:
                        lockup_data.append({
                            'Company': ipo.get('company', 'Unknown'),
                            'Ticker': ipo.get('ticker', 'N/A'),
                            'IPO Date': ipo['date'],
                            'Lockup Expiry': lockup_date.strftime('%Y-%m-%d'),
                            'Days Until': days_until
                        })
                except:
                    pass
    
    if lockup_data:
        lockup_df = pd.DataFrame(lockup_data).sort_values('Days Until')
        
        # Professional table styling
        st.dataframe(
            lockup_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Company": st.column_config.TextColumn("Company", width="medium"),
                "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                "IPO Date": st.column_config.TextColumn("IPO Date", width="small"),
                "Lockup Expiry": st.column_config.TextColumn("Lockup Expiry", width="small"),
                "Days Until": st.column_config.NumberColumn("Days Until", width="small")
            }
        )
    else:
        st.info("No upcoming lockup expirations")
