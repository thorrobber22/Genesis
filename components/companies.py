"""
components/companies_terminal.py - Companies explorer view
Collapsible sectors with instant ticker access
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime, timedelta

def render_companies():
    """Render companies terminal layout"""
    
    # Three-column layout
    col_left, col_main, col_right = st.columns([1, 4, 1.5])
    
    # Left nav - Sectors
    with col_left:
        render_sector_nav()
    
    # Main viewport - Company details
    with col_main:
        if st.session_state.selected_ticker:
            render_company_view()
        else:
            st.info("Select a company from the left sidebar")
    
    # Right context panel
    with col_right:
        if st.session_state.selected_ticker:
            render_company_context()
        else:
            st.markdown("## CONTEXT")
            st.caption("Select a company to view context")

def render_sector_nav():
    """Render sector navigation"""
    st.markdown("## SECTORS")
    
    # Get companies by sector
    sectors = get_companies_by_sector()
    
    for sector, companies in sectors.items():
        with st.expander(f"{sector} ({len(companies)})", expanded=(sector == "Technology")):
            for company in companies:
                if st.button(
                    company['ticker'],
                    key=f"company_{company['ticker']}",
                    use_container_width=True,
                    help=company['name']
                ):
                    st.session_state.selected_ticker = company['ticker']
                    st.session_state.context_data = company
                    st.rerun()

def render_company_view():
    """Render main company view"""
    ticker = st.session_state.selected_ticker
    
    # Company header
    col1, col2, col3, col4 = st.columns([3, 1, 1.5, 1.5])
    
    with col1:
        st.markdown(f"# {ticker}")
        company_name = st.session_state.context_data.get('name', ticker)
        st.caption(company_name)
    
    with col2:
        doc_count = count_company_docs(ticker)
        st.metric("DOCS", doc_count)
    
    with col3:
        last_filing = get_last_filing(ticker)
        st.metric("LAST FILING", last_filing)
    
    with col4:
        lockup_days = get_lockup_days(ticker)
        if lockup_days and lockup_days > 0:
            st.metric("LOCKUP", f"{lockup_days} DAYS")
        else:
            st.metric("LOCKUP", "EXPIRED")
    
    st.markdown("---")
    
    # Recent documents table
    st.markdown("## RECENT DOCUMENTS")
    
    docs = get_company_documents(ticker)
    
    if docs:
        # Table header
        cols = st.columns([2, 2, 1, 1])
        headers = ["TYPE", "DATE", "SIZE", ""]
        
        for col, header in zip(cols, headers):
            with col:
                if header:
                    st.markdown(f"**{header}**")
        
        st.markdown("---")
        
        # Document rows
        for doc in docs[:10]:
            cols = st.columns([2, 2, 1, 1])
            
            with cols[0]:
                st.text(doc['type'])
            
            with cols[1]:
                st.text(doc['date'])
            
            with cols[2]:
                st.text(doc['size'])
            
            with cols[3]:
                if st.button("OPEN", key=f"open_{doc['name']}"):
                    st.info("Document viewer in Phase 3")
    else:
        st.info("No documents found for this company")

def render_company_context():
    """Render company context panel"""
    ticker = st.session_state.selected_ticker
    
    st.markdown(f"## {ticker} CONTEXT")
    
    # Get company details
    details = get_company_full_details(ticker)
    
    # Context items
    context_items = [
        ("LEAD UNDERWRITER", details.get('lead_underwriter', 'Goldman Sachs')),
        ("LOCKUP END DATE", calculate_lockup_date(details.get('ipo_date'))),
        ("SECTOR / INDUSTRY", details.get('sector', 'Technology')),
        ("EXCHANGE", details.get('exchange', 'NYSE')),
        ("IPO DATE", details.get('ipo_date', 'N/A'))
    ]
    
    for label, value in context_items:
        st.markdown(f"**{label}**")
        st.text(value)
        st.markdown("")
    
    # Quick docs
    st.markdown("**QUICK DOCS (TOP 3)**")
    docs = get_company_documents(ticker)
    
    for doc in docs[:3]:
        if st.button(f"→ {doc['type']}", key=f"ctx_doc_{doc['name']}"):
            st.info("Document viewer in Phase 3")

def get_companies_by_sector():
    """Get companies organized by sector"""
    sectors = {
        'Technology': [],
        'Healthcare': [],
        'Financial': [],
        'Energy': [],
        'Consumer': [],
        'Industrial': []
    }
    
    # From SEC documents
    if Path('data/sec_documents').exists():
        for company_dir in Path('data/sec_documents').iterdir():
            if company_dir.is_dir():
                ticker = company_dir.name
                # Default to Technology (would come from real data)
                sectors['Technology'].append({
                    'ticker': ticker,
                    'name': f"{ticker} Inc."  # Would come from real data
                })
    
    # From IPO data
    if Path('data/ipo_data').exists():
        files = list(Path('data/ipo_data').glob('*.json'))
        if files:
            try:
                with open(max(files, key=lambda x: x.stat().st_mtime), 'r') as f:
                    data = json.load(f)
                    
                    for ipo in data.get('filed', []):
                        ticker = ipo.get('ticker')
                        if ticker:
                            # Check if not already added
                            already_added = any(
                                ticker == company['ticker'] 
                                for companies in sectors.values() 
                                for company in companies
                            )
                            
                            if not already_added:
                                # Default to Technology
                                sectors['Technology'].append({
                                    'ticker': ticker,
                                    'name': ipo.get('company', f"{ticker} Inc.")
                                })
            except:
                pass
    
    # Remove empty sectors
    return {k: v for k, v in sectors.items() if v}

def count_company_docs(ticker):
    """Count documents for company"""
    doc_path = Path(f'data/sec_documents/{ticker}')
    if doc_path.exists():
        return len(list(doc_path.glob('*.html')))
    return 0

def get_last_filing(ticker):
    """Get last filing date"""
    doc_path = Path(f'data/sec_documents/{ticker}')
    if doc_path.exists():
        files = list(doc_path.glob('*.html'))
        if files:
            latest = max(files, key=lambda x: x.stat().st_mtime)
            # Extract date from filename
            parts = latest.stem.split('_')
            if len(parts) > 1:
                return parts[-1]
    return "N/A"

def get_lockup_days(ticker):
    """Get days until lockup expiry"""
    # Check IPO data for this ticker
    if Path('data/ipo_data').exists():
        files = list(Path('data/ipo_data').glob('*.json'))
        if files:
            try:
                with open(max(files, key=lambda x: x.stat().st_mtime), 'r') as f:
                    data = json.load(f)
                    
                    for ipo in data.get('filed', []):
                        if ipo.get('ticker') == ticker and 'date' in ipo:
                            try:
                                ipo_date = datetime.strptime(ipo['date'], '%Y-%m-%d')
                                lockup_date = ipo_date + timedelta(days=180)
                                days_until = (lockup_date - datetime.now()).days
                                return days_until if days_until > 0 else 0
                            except:
                                pass
            except:
                pass
    return None

def get_company_documents(ticker):
    """Get all documents for company"""
    docs = []
    
    doc_path = Path(f'data/sec_documents/{ticker}')
    if doc_path.exists():
        for doc_file in sorted(doc_path.glob('*.html'), key=lambda x: x.stat().st_mtime, reverse=True):
            parts = doc_file.stem.split('_')
            docs.append({
                'name': doc_file.stem,
                'type': parts[0] if parts else 'Unknown',
                'date': parts[-1] if len(parts) > 1 else 'Unknown',
                'size': f"{doc_file.stat().st_size // 1024}KB"
            })
    
    return docs

def get_company_full_details(ticker):
    """Get full company details"""
    details = {
        'ticker': ticker,
        'sector': 'Technology',
        'exchange': 'NYSE'
    }
    
    # Try to get from IPO data
    if Path('data/ipo_data').exists():
        files = list(Path('data/ipo_data').glob('*.json'))
        if files:
            try:
                with open(max(files, key=lambda x: x.stat().st_mtime), 'r') as f:
                    data = json.load(f)
                    
                    for ipo in data.get('filed', []):
                        if ipo.get('ticker') == ticker:
                            details.update({
                                'ipo_date': ipo.get('date', 'N/A'),
                                'lead_underwriter': ipo.get('lead_manager', 'Goldman Sachs'),
                                'exchange': ipo.get('exchange', 'NYSE')
                            })
                            break
            except:
                pass
    
    return details

def calculate_lockup_date(ipo_date_str):
    """Calculate lockup expiration date"""
    if not ipo_date_str or ipo_date_str == 'N/A':
        return "N/A"
    
    try:
        ipo_date = datetime.strptime(ipo_date_str, '%Y-%m-%d')
        lockup_date = ipo_date + timedelta(days=180)
        days_until = (lockup_date - datetime.now()).days
        
        if days_until > 0:
            return f"{lockup_date.strftime('%m/%d/%Y')} ({days_until}d)"
        else:
            return "Expired"
    except:
        return "N/A"
