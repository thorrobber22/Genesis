"""
components/dashboard_analyst.py - One-page dashboard with IPO tracker
70/30 split layout as specified
"""

import streamlit as st
from pathlib import Path
import pandas as pd
import json
from datetime import datetime, timedelta

def render_dashboard_analyst():
    """Render unified dashboard with analyst-grade layout"""
    
    # Metrics row - clean and compact
    render_metrics_row()
    
    # Main content - 70/30 split
    col_left, col_right = st.columns([3, 1], gap="large")
    
    # LEFT: High Priority Events
    with col_left:
        st.markdown("##### HIGH PRIORITY EVENTS")
        render_priority_events()
    
    # RIGHT: Lockup Tracker + System Status
    with col_right:
        st.markdown("##### UPCOMING LOCKUPS")
        render_lockup_sidebar()
        
        st.markdown("")  # Spacing
        st.markdown("##### SYSTEM STATUS")
        render_system_status()

def render_metrics_row():
    """Render top metrics in a clean row"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        doc_count = sum(1 for _ in Path('data/sec_documents').rglob('*.html')) if Path('data/sec_documents').exists() else 0
        st.metric("Documents", f"{doc_count:,}")
    
    with col2:
        company_count = len(list(Path('data/sec_documents').iterdir())) if Path('data/sec_documents').exists() else 0
        st.metric("Companies", company_count)
    
    with col3:
        ipo_count = count_active_ipos()
        st.metric("Active IPOs", ipo_count)
    
    with col4:
        lockup_count = count_upcoming_lockups(30)
        st.metric("30d Lockups", lockup_count)
    
    st.markdown("---")

def render_priority_events():
    """Render priority events in clean cards"""
    events = get_priority_events()
    
    if not events:
        st.info("No high priority events. Run scrapers to populate data.")
        return
    
    # Recent filings section
    recent_filings = [e for e in events if e['type'].startswith('New')]
    if recent_filings:
        st.markdown("**Recent S-1 Filings**")
        for event in recent_filings[:3]:
            render_event_card(event)
    
    # Upcoming lockups section
    upcoming_lockups = [e for e in events if 'Lockup' in e['type']]
    if upcoming_lockups:
        st.markdown("**Lockup Expirations**")
        for event in upcoming_lockups[:3]:
            render_event_card(event)

def render_event_card(event):
    """Render a single event as a clean card"""
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"**{event['company']}** ({event['ticker']})")
            st.caption(f"{event['type']} • {event['date']}")
        
        with col2:
            if st.button("Analyze", key=f"evt_{event['ticker']}_{event['date']}", 
                        use_container_width=True):
                st.session_state.selected_company = event['ticker']
                st.session_state.current_view = 'companies'
                st.rerun()

def render_lockup_sidebar():
    """Render compact lockup calendar in sidebar"""
    lockups = get_upcoming_lockups(60)  # Next 60 days
    
    if not lockups:
        st.info("No lockups in next 60 days")
        return
    
    # Group by urgency
    urgent = [l for l in lockups if l['days'] <= 7]
    soon = [l for l in lockups if 7 < l['days'] <= 30]
    later = [l for l in lockups if 30 < l['days'] <= 60]
    
    if urgent:
        st.markdown("**This Week**")
        for lockup in urgent[:3]:
            st.caption(f"• {lockup['ticker']} - {lockup['days']}d")
    
    if soon:
        st.markdown("**This Month**")
        for lockup in soon[:3]:
            st.caption(f"• {lockup['ticker']} - {lockup['days']}d")
    
    if later:
        st.markdown("**Next Month**")
        for lockup in later[:2]:
            st.caption(f"• {lockup['ticker']} - {lockup['days']}d")

def render_system_status():
    """Render compact system status"""
    status_items = check_system_status()
    
    for item in status_items:
        if item['status'] == 'active':
            st.success(f"{item['name']}: Active")
        elif item['status'] == 'error':
            st.error(f"{item['name']}: Error")
        else:
            st.warning(f"{item['name']}: {item['status']}")

# Helper functions
def count_active_ipos():
    """Count active IPOs from data"""
    count = 0
    if Path('data/ipo_data').exists():
        ipo_files = list(Path('data/ipo_data').glob('*.json'))
        if ipo_files:
            try:
                latest_file = max(ipo_files, key=lambda x: x.stat().st_mtime)
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    count = len(data.get('filed', []))
            except:
                pass
    return count

def count_upcoming_lockups(days):
    """Count lockups expiring in next N days"""
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
                                if 0 < days_until <= days:
                                    count += 1
                            except:
                                pass
            except:
                pass
    return count

def get_priority_events():
    """Get all priority events"""
    events = []
    
    if Path('data/ipo_data').exists():
        ipo_files = list(Path('data/ipo_data').glob('*.json'))
        if ipo_files:
            try:
                latest_file = max(ipo_files, key=lambda x: x.stat().st_mtime)
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    
                # Recent filings (last 7 days)
                for ipo in data.get('filed', []):
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
                
                # Upcoming lockups (next 30 days)
                for ipo in data.get('filed', []):
                    if 'date' in ipo:
                        try:
                            ipo_date = datetime.strptime(ipo['date'], '%Y-%m-%d')
                            lockup_date = ipo_date + timedelta(days=180)
                            days_until = (lockup_date - datetime.now()).days
                            
                            if 0 < days_until <= 30:
                                events.append({
                                    'type': f'Lockup in {days_until} days',
                                    'company': ipo.get('company', 'Unknown'),
                                    'ticker': ipo.get('ticker', 'N/A'),
                                    'date': lockup_date.strftime('%Y-%m-%d'),
                                    'priority': 2 if days_until <= 7 else 3
                                })
                        except:
                            pass
            except:
                pass
    
    return sorted(events, key=lambda x: x['priority'])

def get_upcoming_lockups(days):
    """Get lockups expiring in next N days"""
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
                            
                            if 0 < days_until <= days:
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

def check_system_status():
    """Check system component status"""
    status = []
    
    # Check IPO scraper
    if Path('services/ipo_scraper.py').exists():
        status.append({'name': 'IPO Scraper', 'status': 'active'})
    else:
        status.append({'name': 'IPO Scraper', 'status': 'missing'})
    
    # Check document indexer
    if Path('services/document_indexer.py').exists():
        status.append({'name': 'Indexer', 'status': 'active'})
    else:
        status.append({'name': 'Indexer', 'status': 'missing'})
    
    # Check API keys
    if Path('.env').exists():
        status.append({'name': 'API Keys', 'status': 'active'})
    else:
        status.append({'name': 'API Keys', 'status': 'not configured'})
    
    return status
