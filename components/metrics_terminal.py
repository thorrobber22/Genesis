"""
components/metrics_terminal.py - Interactive metrics dashboard
Click any metric to filter IPO calendar
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime, timedelta

def render_metrics():
    """Render interactive metrics view"""
    
    st.markdown("# METRICS")
    st.caption("Click any metric to filter the IPO calendar")
    
    # Top-level KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_ipos = count_active_ipos()
        if st.button(
            f"**{active_ipos}**\n\nACTIVE IPOS",
            key="metric_active",
            use_container_width=True,
            help="View all active IPOs"
        ):
            st.session_state.active_tab = 'ipo_calendar'
            st.session_state.period_filter = 'All'
            st.session_state.status_filter = 'Filed'
            st.rerun()
    
    with col2:
        this_week = count_this_week()
        if st.button(
            f"**{this_week}**\n\nTHIS WEEK",
            key="metric_week",
            use_container_width=True,
            help="View this week's IPOs"
        ):
            st.session_state.active_tab = 'ipo_calendar'
            st.session_state.period_filter = 'This Week'
            st.rerun()
    
    with col3:
        lockups_30d = count_30d_lockups()
        if st.button(
            f"**{lockups_30d}**\n\n30D LOCKUPS",
            key="metric_lockups",
            use_container_width=True,
            help="View upcoming lockup expirations"
        ):
            st.session_state.active_tab = 'ipo_calendar'
            st.session_state.filter_lockups = True
            st.rerun()
    
    with col4:
        total_docs = count_total_documents()
        if st.button(
            f"**{total_docs}**\n\nDOCUMENTS",
            key="metric_docs",
            use_container_width=True,
            help="View companies by document volume"
        ):
            st.session_state.active_tab = 'companies'
            st.session_state.sort_by = 'docs'
            st.rerun()
    
    st.markdown("---")
    
    # Detailed metrics
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        render_detailed_metrics()
    
    with col_right:
        render_system_health()

def render_detailed_metrics():
    """Render detailed metric breakdowns"""
    
    # IPO Pipeline
    st.markdown("## IPO PIPELINE")
    
    pipeline = get_ipo_pipeline()
    
    for stage, count in pipeline.items():
        cols = st.columns([3, 1, 1])
        
        with cols[0]:
            st.text(stage)
        
        with cols[1]:
            st.text(str(count))
        
        with cols[2]:
            if count > 0:
                if st.button("VIEW", key=f"view_{stage}"):
                    st.session_state.active_tab = 'ipo_calendar'
                    st.session_state.status_filter = stage
                    st.rerun()
    
    st.markdown("")
    
    # Document Types
    st.markdown("## DOCUMENT TYPES")
    
    doc_types = get_document_types()
    
    for doc_type, count in doc_types.items():
        cols = st.columns([3, 1, 1])
        
        with cols[0]:
            st.text(doc_type)
        
        with cols[1]:
            st.text(str(count))
        
        with cols[2]:
            if count > 0:
                if st.button("VIEW", key=f"view_doc_{doc_type}"):
                    st.session_state.active_tab = 'companies'
                    st.session_state.doc_filter = doc_type
                    st.rerun()

def render_system_health():
    """Render system health indicators"""
    st.markdown("## SYSTEM HEALTH")
    
    # Check services
    services = [
        ("IPO Scraper", check_service_status('services/ipo_scraper.py')),
        ("SEC Indexer", check_service_status('services/document_indexer.py')),
        ("API Keys", check_service_status('.env')),
        ("Vector DB", check_service_status('data/vector_store'))
    ]
    
    for service, status in services:
        st.markdown(f"**{service}**")
        
        if status == "Active":
            st.markdown(
                f'<div style="color: #10B981; font-size: 12px;">● {status}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="color: #EF4444; font-size: 12px;">● {status}</div>',
                unsafe_allow_html=True
            )
        st.markdown("")
    
    # Last update
    st.markdown("**LAST UPDATE**")
    last_update = get_last_update_time()
    st.text(last_update)

# Helper functions
def count_active_ipos():
    """Count active IPOs"""
    count = 0
    if Path('data/ipo_data').exists():
        files = list(Path('data/ipo_data').glob('*.json'))
        if files:
            try:
                with open(max(files, key=lambda x: x.stat().st_mtime), 'r') as f:
                    data = json.load(f)
                    count = len(data.get('filed', []))
            except:
                pass
    return count

def count_this_week():
    """Count IPOs filed this week"""
    count = 0
    if Path('data/ipo_data').exists():
        files = list(Path('data/ipo_data').glob('*.json'))
        if files:
            try:
                with open(max(files, key=lambda x: x.stat().st_mtime), 'r') as f:
                    data = json.load(f)
                    
                    for ipo in data.get('filed', []):
                        if 'date' in ipo:
                            try:
                                filing_date = datetime.strptime(ipo['date'], '%Y-%m-%d')
                                days_ago = (datetime.now() - filing_date).days
                                if days_ago <= 7:
                                    count += 1
                            except:
                                pass
            except:
                pass
    return count

def count_30d_lockups():
    """Count lockups expiring in 30 days"""
    count = 0
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
                                
                                if 0 < days_until <= 30:
                                    count += 1
                            except:
                                pass
            except:
                pass
    return count

def count_total_documents():
    """Count total documents indexed"""
    count = 0
    if Path('data/sec_documents').exists():
        count = sum(1 for _ in Path('data/sec_documents').rglob('*.html'))
    return count

def get_ipo_pipeline():
    """Get IPO pipeline breakdown"""
    pipeline = {
        "Filed S-1": count_active_ipos(),
        "Amended S-1/A": 0,  # Would parse from real data
        "Priced": 0,
        "Withdrawn": 0
    }
    return pipeline

def get_document_types():
    """Get document type breakdown"""
    doc_types = {}
    
    if Path('data/sec_documents').exists():
        for doc in Path('data/sec_documents').rglob('*.html'):
            # Extract type from filename
            doc_type = doc.stem.split('_')[0] if '_' in doc.stem else 'Unknown'
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
    
    # Return top 5 document types
    return dict(sorted(doc_types.items(), key=lambda x: x[1], reverse=True)[:5])

def check_service_status(path):
    """Check if service file exists"""
    return "Active" if Path(path).exists() else "Missing"

def get_last_update_time():
    """Get time of last data update"""
    if Path('data/ipo_data').exists():
        files = list(Path('data/ipo_data').glob('*.json'))
        if files:
            latest = max(files, key=lambda x: x.stat().st_mtime)
            mtime = datetime.fromtimestamp(latest.stat().st_mtime)
            return mtime.strftime('%m/%d %H:%M')
    return "Never"
