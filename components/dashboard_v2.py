"""
components/dashboard_v2.py - Unified dashboard + IPO tracker view
Single-screen, split-panel layout per feedback
"""

import streamlit as st
from pathlib import Path
import pandas as pd
import json
from datetime import datetime, timedelta

def render_dashboard_v2():
    """Render unified dashboard with split panel layout"""
    
    # Top metrics bar - more compact
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        doc_count = sum(1 for _ in Path('data/sec_documents').rglob('*.html')) if Path('data/sec_documents').exists() else 0
        st.metric("Documents", f"{doc_count:,}")
        
    with col2:
        company_count = len(list(Path('data/sec_documents').iterdir())) if Path('data/sec_documents').exists() else 0
        st.metric("Companies", company_count)
        
    with col3:
        ipo_count = 0
        if Path('data/ipo_data').exists():
            ipo_files = list(Path('data/ipo_data').glob('*.json'))
            if ipo_files:
                try:
                    latest_file = max(ipo_files, key=lambda x: x.stat().st_mtime)
                    with open(latest_file, 'r') as f:
                        data = json.load(f)
                        ipo_count = len(data.get('filed', []))
                except:
                    pass
        st.metric("Active IPOs", ipo_count)
        
    with col4:
        lockup_count = calculate_lockup_count()
        st.metric("Lockups (30d)", lockup_count)
    
    # Split panel layout
    left_col, right_col = st.columns([1, 1], gap="large")
    
    # LEFT PANEL: High Priority Events
    with left_col:
        st.markdown("## High Priority Events")
        render_events_panel()
    
    # RIGHT PANEL: IPO Tracker Table
    with right_col:
        st.markdown("## IPO Activity")
        render_ipo_panel()

def calculate_lockup_count():
    """Calculate lockups expiring in next 30 days"""
    count = 0
    if Path('data/ipo_data').exists():
        ipo_files = list(Path('data/ipo_data').glob('*.json'))
        if ipo_files:
            try:
                latest_file = max(ipo_files, key=lambda x: x.stat().st_mtime)
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    for ipo in data.get('filed', []):
                        if 'date' in ipo:
                            try:
                                ipo_date = datetime.strptime(ipo['date'], '%Y-%m-%d')
                                lockup_date = ipo_date + timedelta(days=180)
                                days_until = (lockup_date - datetime.now()).days
                                if 0 < days_until <= 30:
                                    count += 1
                            except:
                                pass
            except:
                pass
    return count

def render_events_panel():
    """Render high priority events in cards"""
    events = get_priority_events()
    
    if events:
        for idx, event in enumerate(events[:4]):  # Max 4 to fit screen
            # Create a card for each event
            with st.container():
                col_content, col_action = st.columns([3, 1])
                
                with col_content:
                    st.markdown(f"**{event['company']} ({event['ticker']})**")
                    st.caption(f"{event['type']} • {event['date']}")
                
                with col_action:
                    if st.button("Analyze", key=f"analyze_{idx}", type="primary"):
                        st.session_state.selected_company = event['ticker']
                        st.session_state.current_view = 'companies'
                        st.rerun()
                        
            # Add separator between cards
            if idx < len(events) - 1:
                st.markdown("---")
    else:
        st.info("No high priority events. Run scrapers to populate data.")

def render_ipo_panel():
    """Render IPO tracker table"""
    # Tabs for different views
    tab1, tab2 = st.tabs(["Recent Filings", "Lockup Calendar"])
    
    with tab1:
        render_recent_filings()
    
    with tab2:
        render_lockup_calendar()

def render_recent_filings():
    """Render recent IPO filings table"""
    if Path('data/ipo_data').exists():
        ipo_files = list(Path('data/ipo_data').glob('*.json'))
        if ipo_files:
            try:
                latest_file = max(ipo_files, key=lambda x: x.stat().st_mtime)
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    
                if 'filed' in data and data['filed']:
                    # Create clean dataframe
                    filing_data = []
                    for ipo in data['filed'][:10]:  # Top 10
                        filing_data.append({
                            'Company': ipo.get('company', 'Unknown'),
                            'Ticker': ipo.get('ticker', 'N/A'),
                            'Exchange': ipo.get('exchange', 'N/A'),
                            'Filing Date': ipo.get('date', 'N/A')
                        })
                    
                    df = pd.DataFrame(filing_data)
                    
                    # Display compact table
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                        height=300  # Fixed height to prevent scroll
                    )
                else:
                    st.info("No recent filings")
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
    else:
        st.info("No IPO data available")

def render_lockup_calendar():
    """Render lockup expiration calendar"""
    lockups = []
    
    if Path('data/ipo_data').exists():
        ipo_files = list(Path('data/ipo_data').glob('*.json'))
        if ipo_files:
            try:
                latest_file = max(ipo_files, key=lambda x: x.stat().st_mtime)
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    
                for ipo in data.get('filed', []):
                    if 'date' in ipo:
                        try:
                            ipo_date = datetime.strptime(ipo['date'], '%Y-%m-%d')
                            lockup_date = ipo_date + timedelta(days=180)
                            days_until = (lockup_date - datetime.now()).days
                            
                            if days_until > 0:
                                lockups.append({
                                    'Company': ipo.get('company', 'Unknown'),
                                    'Ticker': ipo.get('ticker', 'N/A'),
                                    'Lockup Date': lockup_date.strftime('%Y-%m-%d'),
                                    'Days': days_until
                                })
                        except:
                            pass
            except:
                pass
    
    if lockups:
        lockup_df = pd.DataFrame(lockups).sort_values('Days')
        
        # Display compact table
        st.dataframe(
            lockup_df,
            use_container_width=True,
            hide_index=True,
            height=300  # Fixed height
        )
    else:
        st.info("No upcoming lockup expirations")

def get_priority_events():
    """Get high priority events for display"""
    events = []
    
    if Path('data/ipo_data').exists():
        ipo_files = list(Path('data/ipo_data').glob('*.json'))
        if ipo_files:
            try:
                latest_file = max(ipo_files, key=lambda x: x.stat().st_mtime)
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    
                # Recent filings
                for ipo in data.get('filed', [])[:3]:
                    if 'date' in ipo:
                        try:
                            filing_date = datetime.strptime(ipo['date'], '%Y-%m-%d')
                            days_ago = (datetime.now() - filing_date).days
                            
                            if days_ago <= 7:
                                events.append({
                                    'type': 'New S-1 Filing',
                                    'company': ipo.get('company', 'Unknown'),
                                    'ticker': ipo.get('ticker', 'N/A'),
                                    'date': ipo['date'],
                                    'priority': 1
                                })
                        except:
                            pass
                
                # Upcoming lockups
                for ipo in data.get('filed', []):
                    if 'date' in ipo:
                        try:
                            ipo_date = datetime.strptime(ipo['date'], '%Y-%m-%d')
                            lockup_date = ipo_date + timedelta(days=180)
                            days_until = (lockup_date - datetime.now()).days
                            
                            if 0 < days_until <= 14:
                                events.append({
                                    'type': f'Lockup in {days_until}d',
                                    'company': ipo.get('company', 'Unknown'),
                                    'ticker': ipo.get('ticker', 'N/A'),
                                    'date': lockup_date.strftime('%Y-%m-%d'),
                                    'priority': 2 if days_until <= 7 else 3
                                })
                        except:
                            pass
            except:
                pass
    
    return sorted(events, key=lambda x: x['priority'])[:4]
