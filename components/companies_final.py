"""
components/companies_final.py - File explorer-style company view
Click to select, details load on right
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime

def render_companies_final():
    """Render companies in explorer-style layout"""
    
    # Two-column layout: List (left) and Details (right)
    col_list, col_details = st.columns([1, 2], gap="large")
    
    with col_list:
        st.markdown("#### COMPANIES")
        render_company_list()
    
    with col_details:
        if st.session_state.selected_company:
            render_company_details()
        else:
            st.info("Select a company from the list to view details")

def render_company_list():
    """Render scrollable company list"""
    companies = get_all_companies()
    
    if not companies:
        st.info("No companies tracked yet")
        return
    
    # Create list items
    for company in companies:
        # Check if selected
        is_selected = st.session_state.selected_company == company['ticker']
        
        # Company item container
        with st.container():
            if st.button(
                f"**{company['name']}** ({company['ticker']})",
                key=f"company_{company['ticker']}",
                use_container_width=True,
                help=f"Last filing: {company.get('last_filing', 'N/A')}"
            ):
                st.session_state.selected_company = company['ticker']
                st.rerun()
            
            # Additional info
            col1, col2 = st.columns(2)
            with col1:
                st.caption(company.get('sector', 'Technology'))
            with col2:
                st.caption(f"Files: {company.get('file_count', 0)}")

def render_company_details():
    """Render details for selected company"""
    ticker = st.session_state.selected_company
    
    st.markdown(f"#### {ticker} OVERVIEW")
    
    # Company metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documents", count_company_documents(ticker))
    
    with col2:
        last_filing = get_last_filing_date(ticker)
        st.metric("Last Filing", last_filing if last_filing else "N/A")
    
    with col3:
        lockup_days = get_lockup_days(ticker)
        if lockup_days and lockup_days > 0:
            st.metric("Lockup", f"{lockup_days}d")
        else:
            st.metric("Lockup", "Expired")
    
    st.markdown("---")
    
    # Recent documents
    st.markdown("**Recent Documents**")
    
    documents = get_company_documents(ticker)
    if documents:
        for doc in documents[:5]:
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{doc['type']}**")
                    st.caption(f"Filed {doc['date']} • {doc['size']}")
                
                with col2:
                    if st.button("Open", key=f"doc_{ticker}_{doc['name']}"):
                        st.session_state.selected_document = doc['name']
                        st.info("Document viewer coming in Phase 3")
    else:
        st.info("No documents found")
    
    # Key insights section
    st.markdown("---")
    st.markdown("**Key Insights**")
    st.info("AI-powered insights coming in Phase 4")

# Helper functions
def get_all_companies():
    """Get list of all tracked companies"""
    companies = []
    
    # From SEC documents
    if Path('data/sec_documents').exists():
        for company_dir in Path('data/sec_documents').iterdir():
            if company_dir.is_dir():
                ticker = company_dir.name
                files = list(company_dir.glob('*.html'))
                
                # Get last filing date
                last_filing = None
                if files:
                    latest_file = max(files, key=lambda x: x.stat().st_mtime)
                    # Try to extract date from filename
                    try:
                        date_part = latest_file.stem.split('_')[-1]
                        last_filing = date_part
                    except:
                        last_filing = "Unknown"
                
                companies.append({
                    'ticker': ticker,
                    'name': ticker,  # Would come from company data
                    'sector': 'Technology',  # Would come from company data
                    'file_count': len(files),
                    'last_filing': last_filing
                })
    
    # From IPO data
    if Path('data/ipo_data').exists():
        files = list(Path('data/ipo_data').glob('*.json'))
        if files:
            try:
                with open(max(files, key=lambda x: x.stat().st_mtime), 'r') as f:
                    data = json.load(f)
                    
                    for ipo in data.get('filed', []):
                        ticker = ipo.get('ticker', 'N/A')
                        # Check if not already in list
                        if not any(c['ticker'] == ticker for c in companies):
                            companies.append({
                                'ticker': ticker,
                                'name': ipo.get('company', ticker),
                                'sector': 'IPO',
                                'file_count': 0,
                                'last_filing': ipo.get('date', 'Unknown')
                            })
            except:
                pass
    
    return sorted(companies, key=lambda x: x['name'])

def count_company_documents(ticker):
    """Count documents for a company"""
    if Path(f'data/sec_documents/{ticker}').exists():
        return len(list(Path(f'data/sec_documents/{ticker}').glob('*.html')))
    return 0

def get_last_filing_date(ticker):
    """Get last filing date for company"""
    if Path(f'data/sec_documents/{ticker}').exists():
        files = list(Path(f'data/sec_documents/{ticker}').glob('*.html'))
        if files:
            latest = max(files, key=lambda x: x.stat().st_mtime)
            try:
                return latest.stem.split('_')[-1]
            except:
                pass
    return None

def get_lockup_days(ticker):
    """Get days until lockup expiry"""
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
                                return days_until
                            except:
                                pass
            except:
                pass
    return None

def get_company_documents(ticker):
    """Get documents for a company"""
    documents = []
    
    if Path(f'data/sec_documents/{ticker}').exists():
        for doc_path in Path(f'data/sec_documents/{ticker}').glob('*.html'):
            # Parse document info from filename
            parts = doc_path.stem.split('_')
            doc_type = parts[0] if parts else 'Unknown'
            doc_date = parts[-1] if len(parts) > 1 else 'Unknown'
            
            documents.append({
                'name': doc_path.stem,
                'type': doc_type,
                'date': doc_date,
                'size': f"{doc_path.stat().st_size // 1024}KB",
                'path': str(doc_path)
            })
    
    return sorted(documents, key=lambda x: x['date'], reverse=True)
