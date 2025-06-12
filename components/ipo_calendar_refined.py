"""
components/ipo_calendar_refined.py - IPO Calendar with refined color scheme
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import json
from datetime import datetime, timedelta

def render_ipo_calendar():
    """Render IPO calendar with refined styling"""
    
    # Three-column layout
    col_left, col_main, col_right = st.columns([1, 4, 1.5])
    
    # Left nav - Filters
    with col_left:
        render_filters()
    
    # Main viewport - IPO table
    with col_main:
        render_ipo_table()
    
    # Right context panel
    with col_right:
        render_context_panel()

def render_filters():
    """Render filter sidebar"""
    st.markdown("## FILTERS")
    
    # Period filter
    st.markdown("**PERIOD**")
    period = st.radio(
        "Period",
        ["This Week", "Next Week", "This Month", "All"],
        label_visibility="collapsed",
        key="period_filter"
    )
    
    st.markdown("")
    
    # Status filter
    st.markdown("**STATUS**")
    status = st.radio(
        "Status",
        ["All", "Filed", "Priced", "Withdrawn"],
        label_visibility="collapsed",
        key="status_filter"
    )
    
    st.markdown("")
    
    # Exchange filter
    st.markdown("**EXCHANGE**")
    exchange = st.radio(
        "Exchange",
        ["All", "NYSE", "NASDAQ"],
        label_visibility="collapsed",
        key="exchange_filter"
    )

def render_ipo_table():
    """Render main IPO calendar table"""
    st.markdown("# IPO CALENDAR")
    
    # Get filtered IPOs
    ipos = get_filtered_ipos(
        st.session_state.get('period_filter', 'This Week'),
        st.session_state.get('status_filter', 'All'),
        st.session_state.get('exchange_filter', 'All')
    )
    
    if not ipos:
        st.info("No IPOs match current filters")
        return
    
    # Create table container
    st.markdown('<div class="data-table-container">', unsafe_allow_html=True)
    
    # Table with refined styling
    df = pd.DataFrame(ipos)
    
    # Display each row
    for idx, row in df.iterrows():
        col_date, col_ticker, col_company, col_exchange, col_lead, col_size, col_cap, col_docs = st.columns([1, 1, 2.5, 1, 2, 1, 1, 0.5])
        
        with col_date:
            st.text(row['date'])
        
        with col_ticker:
            if st.button(
                row['ticker'],
                key=f"ticker_{row['ticker']}_{idx}",
                help=f"View {row['ticker']} details"
            ):
                st.session_state.selected_ticker = row['ticker']
                st.session_state.context_data = row.to_dict()
                st.rerun()
        
        with col_company:
            st.text(row['company'][:30] + "..." if len(row['company']) > 30 else row['company'])
        
        with col_exchange:
            st.text(row['exchange'])
        
        with col_lead:
            st.text(row['lead_bookrunner'][:20] + "..." if len(row['lead_bookrunner']) > 20 else row['lead_bookrunner'])
        
        with col_size:
            st.text(row['deal_size'])
        
        with col_cap:
            st.text(row['market_cap'])
        
        with col_docs:
            st.text(str(row['docs']))
        
        # Add subtle divider
        st.markdown('<hr style="margin: 8px 0; border-color: #30363D;">', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_context_panel():
    """Render context panel for selected IPO"""
    if not st.session_state.selected_ticker:
        st.markdown("## CONTEXT")
        st.caption("Select a ticker to view details")
        return
    
    st.markdown(f"## {st.session_state.selected_ticker}")
    
    # Get context data
    context = st.session_state.context_data
    
    # Context sections with refined styling
    context_items = [
        ("LEAD UNDERWRITER", context.get('lead_bookrunner', 'N/A')),
        ("LOCKUP END DATE", calculate_lockup(context.get('date'))),
        ("SECTOR / INDUSTRY", context.get('sector', 'Technology')),
        ("EXCHANGE", context.get('exchange', 'NYSE')),
        ("FILING STATUS", "Active")
    ]
    
    for label, value in context_items:
        st.markdown(f'<div class="context-label">{label}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="context-value">{value}</div>', unsafe_allow_html=True)
        st.markdown("")
    
    # Quick docs section
    st.markdown("**QUICK DOCS (TOP 3)**")
    docs = get_company_docs(st.session_state.selected_ticker)
    
    if docs:
        for doc in docs[:3]:
            if st.button(f"→ {doc['type']}", key=f"doc_{doc['name']}"):
                st.info("Document viewer in Phase 3")
    else:
        st.caption("No documents found")

def get_filtered_ipos(period, status, exchange):
    """Get IPOs based on filters"""
    ipos = []
    
    # Load IPO data
    if Path('data/ipo_data').exists():
        files = list(Path('data/ipo_data').glob('*.json'))
        if files:
            try:
                with open(max(files, key=lambda x: x.stat().st_mtime), 'r') as f:
                    data = json.load(f)
                    
                    for ipo in data.get('filed', []):
                        # Build IPO record
                        ipo_record = {
                            'date': ipo.get('date', 'TBD'),
                            'ticker': ipo.get('ticker', 'N/A'),
                            'company': ipo.get('company', 'Unknown'),
                            'exchange': ipo.get('exchange', 'NYSE'),
                            'lead_bookrunner': ipo.get('lead_manager', 'Goldman Sachs'),
                            'deal_size': '$100M',
                            'market_cap': '$1.2B',
                            'docs': count_docs(ipo.get('ticker')),
                            'sector': 'Technology'
                        }
                        
                        # Apply filters
                        if exchange != 'All' and ipo_record['exchange'] != exchange:
                            continue
                        
                        if period == 'This Week':
                            try:
                                ipo_date = datetime.strptime(ipo_record['date'], '%Y-%m-%d')
                                if (ipo_date - datetime.now()).days > 7:
                                    continue
                            except:
                                pass
                        
                        ipos.append(ipo_record)
            except Exception as e:
                st.error(f"Error loading IPO data: {str(e)}")
    
    return ipos[:20]

def calculate_lockup(ipo_date_str):
    """Calculate lockup expiration"""
    if not ipo_date_str or ipo_date_str == 'TBD':
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

def count_docs(ticker):
    """Count documents for ticker"""
    if not ticker or ticker == 'N/A':
        return 0
    
    doc_path = Path(f'data/sec_documents/{ticker}')
    if doc_path.exists():
        return len(list(doc_path.glob('*.html')))
    return 0

def get_company_docs(ticker):
    """Get top 3 documents for company"""
    docs = []
    
    doc_path = Path(f'data/sec_documents/{ticker}')
    if doc_path.exists():
        for doc_file in sorted(doc_path.glob('*.html'), key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
            parts = doc_file.stem.split('_')
            docs.append({
                'name': doc_file.stem,
                'type': parts[0] if parts else 'Document'
            })
    
    return docs
