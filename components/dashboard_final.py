"""
components/dashboard_final.py - Unified dashboard view
Everything in one viewport, no scrolling
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime, timedelta

def render_dashboard_final():
    """Render unified dashboard - all IPO data in one view"""
    
    # Top metrics bar
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active IPOs", count_active_ipos())
    
    with col2:
        st.metric("This Week", count_events_this_week())
    
    with col3:
        st.metric("30d Lockups", count_lockups(30))
    
    with col4:
        st.metric("Documents", count_documents())
    
    st.markdown("---")
    
    # Two-column layout: Events (left) and Lockups (right)
    col_left, col_right = st.columns([2, 1], gap="large")
    
    with col_left:
        render_events_column()
    
    with col_right:
        render_lockups_column()

def render_events_column():
    """Left column - all events in priority order"""
    st.markdown("#### HIGH PRIORITY EVENTS")
    
    events = get_all_events()
    
    if not events:
        st.info("No events. Run scrapers to populate data.")
        return
    
    # Group by type
    new_filings = [e for e in events if e['type'] == 'filing']
    lockup_soon = [e for e in events if e['type'] == 'lockup' and e['days'] <= 7]
    other_events = [e for e in events if e not in new_filings + lockup_soon]
    
    # New S-1 Filings
    if new_filings:
        st.markdown("**New S-1 Filings**")
        for event in new_filings[:3]:
            with st.container():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**{event['company']}** ({event['ticker']})")
                    st.caption(f"Filed {event['date']} • {event.get('lead_manager', 'N/A')}")
                with col2:
                    if st.button("View", key=f"view_{event['ticker']}_{event['date']}"):
                        st.session_state.selected_company = event['ticker']
                        st.session_state.current_view = 'companies'
                        st.rerun()
    
    # Urgent Lockups
    if lockup_soon:
        st.markdown("**Lockups This Week**")
        for event in lockup_soon[:3]:
            with st.container():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**{event['company']}**")
                    st.caption(f"Expires in {event['days']} days • {event['date']}")
                with col2:
                    if st.button("Track", key=f"track_{event['ticker']}_{event['days']}"):
                        st.session_state.selected_company = event['ticker']
                        st.session_state.current_view = 'companies'
                        st.rerun()

def render_lockups_column():
    """Right column - lockup calendar"""
    st.markdown("#### THIS MONTH'S LOCKUPS")
    
    lockups = get_lockups_grouped()
    
    if not lockups:
        st.info("No upcoming lockups")
        return
    
    # Week 1
    if lockups.get('week1'):
        st.markdown("**Days 1-7**")
        for lockup in lockups['week1'][:5]:
            st.caption(f"• {lockup['ticker']} - Day {lockup['days']}")
    
    # Week 2-4
    if lockups.get('week2_4'):
        st.markdown("**Days 8-30**")
        for lockup in lockups['week2_4'][:5]:
            st.caption(f"• {lockup['ticker']} - Day {lockup['days']}")
    
    # Next month preview
    if lockups.get('next_month'):
        st.markdown("**Next Month**")
        st.caption(f"{len(lockups['next_month'])} lockups scheduled")

# Helper functions
def count_active_ipos():
    """Count IPOs from data files"""
    if Path('data/ipo_data').exists():
        files = list(Path('data/ipo_data').glob('*.json'))
        if files:
            try:
                with open(max(files, key=lambda x: x.stat().st_mtime), 'r') as f:
                    data = json.load(f)
                    return len(data.get('filed', []))
            except:
                pass
    return 0

def count_events_this_week():
    """Count events in next 7 days"""
    count = 0
    events = get_all_events()
    for event in events:
        if event.get('days', 999) <= 7 or event.get('days_ago', 999) <= 7:
            count += 1
    return count

def count_lockups(days):
    """Count lockups in next N days"""
    count = 0
    lockups = get_all_lockups()
    for lockup in lockups:
        if lockup['days'] <= days:
            count += 1
    return count

def count_documents():
    """Count total documents"""
    if Path('data/sec_documents').exists():
        return sum(1 for _ in Path('data/sec_documents').rglob('*.html'))
    return 0

def get_all_events():
    """Get all events sorted by priority"""
    events = []
    
    if Path('data/ipo_data').exists():
        files = list(Path('data/ipo_data').glob('*.json'))
        if files:
            try:
                with open(max(files, key=lambda x: x.stat().st_mtime), 'r') as f:
                    data = json.load(f)
                    
                    # Process filings
                    for ipo in data.get('filed', []):
                        if 'date' in ipo:
                            try:
                                filing_date = datetime.strptime(ipo['date'], '%Y-%m-%d')
                                days_ago = (datetime.now() - filing_date).days
                                
                                if days_ago <= 7:
                                    events.append({
                                        'type': 'filing',
                                        'company': ipo.get('company', 'Unknown'),
                                        'ticker': ipo.get('ticker', 'N/A'),
                                        'date': ipo['date'],
                                        'days_ago': days_ago,
                                        'lead_manager': ipo.get('lead_manager', 'N/A'),
                                        'priority': 1
                                    })
                                
                                # Also check for lockups
                                lockup_date = filing_date + timedelta(days=180)
                                days_until = (lockup_date - datetime.now()).days
                                
                                if 0 < days_until <= 30:
                                    events.append({
                                        'type': 'lockup',
                                        'company': ipo.get('company', 'Unknown'),
                                        'ticker': ipo.get('ticker', 'N/A'),
                                        'date': lockup_date.strftime('%Y-%m-%d'),
                                        'days': days_until,
                                        'priority': 2 if days_until <= 7 else 3
                                    })
                            except:
                                pass
            except:
                pass
    
    return sorted(events, key=lambda x: x['priority'])

def get_all_lockups():
    """Get all upcoming lockups"""
    lockups = []
    
    if Path('data/ipo_data').exists():
        files = list(Path('data/ipo_data').glob('*.json'))
        if files:
            try:
                with open(max(files, key=lambda x: x.stat().st_mtime), 'r') as f:
                    data = json.load(f)
                    
                    for ipo in data.get('filed', []):
                        if 'date' in ipo:
                            try:
                                ipo_date = datetime.strptime(ipo['date'], '%Y-%m-%d')
                                lockup_date = ipo_date + timedelta(days=180)
                                days_until = (lockup_date - datetime.now()).days
                                
                                if days_until > 0:
                                    lockups.append({
                                        'company': ipo.get('company', 'Unknown'),
                                        'ticker': ipo.get('ticker', 'N/A'),
                                        'date': lockup_date.strftime('%Y-%m-%d'),
                                        'days': days_until
                                    })
                            except:
                                pass
            except:
                pass
    
    return sorted(lockups, key=lambda x: x['days'])

def get_lockups_grouped():
    """Get lockups grouped by time period"""
    all_lockups = get_all_lockups()
    
    grouped = {
        'week1': [l for l in all_lockups if l['days'] <= 7],
        'week2_4': [l for l in all_lockups if 7 < l['days'] <= 30],
        'next_month': [l for l in all_lockups if 30 < l['days'] <= 60]
    }
    
    return grouped
