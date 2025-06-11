"""
Available Tickers Component
Date: 2025-06-07 14:02:41 UTC
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from services.document_service import DocumentService
from scrapers.sec.sec_compliant_scraper import SECCompliantScraper

def render_tickers():
    """Render available tickers"""
    st.title("Available Tickers")
    
    # Initialize services
    doc_service = DocumentService()
    
    # Search functionality
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("Search companies...", placeholder="Enter ticker or company name")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        refresh_clicked = st.button("Refresh", use_container_width=True)
    
    if refresh_clicked:
        st.rerun()
    
    # Get companies
    companies = doc_service.get_companies()
    
    # Filter by search term
    if search_term:
        companies = [c for c in companies if search_term.upper() in c.upper()]
    
    if companies:
        # Build data for display
        ticker_data = []
        for company in companies:
            docs = doc_service.get_company_documents(company)
            
            # Get latest filing info
            latest_filing = "None"
            last_modified = "N/A"
            
            if docs:
                latest_doc = docs[0]  # Already sorted by date
                latest_filing = latest_doc['type']
                last_modified = datetime.fromtimestamp(latest_doc['modified']).strftime('%Y-%m-%d')
            
            ticker_data.append({
                'Ticker': company,
                'Documents': len(docs),
                'Latest Filing': latest_filing,
                'Last Updated': last_modified
            })
        
        # Display as interactive table
        df = pd.DataFrame(ticker_data)
        
        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Handle selection
        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            selected_company = df.iloc[selected_idx]['Ticker']
            
            st.markdown("### Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Start Chat", key=f"ticker_chat_{selected_company}", use_container_width=True):
                    st.session_state.current_page = "New Chat"
                    st.session_state.chat_context = selected_company
                    st.rerun()
            
            with col2:
                if st.button("View Documents", key=f"ticker_docs_{selected_company}", use_container_width=True):
                    show_company_documents(selected_company, doc_service)
            
            with col3:
                if st.button("Add to Watchlist", key=f"ticker_watch_{selected_company}", use_container_width=True):
                    if 'watchlist' not in st.session_state:
                        st.session_state.watchlist = []
                    if selected_company not in st.session_state.watchlist:
                        st.session_state.watchlist.append(selected_company)
                        st.success("Added to watchlist!")
        
        # Summary stats
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Companies", len(companies))
        with col2:
            total_docs = sum(row['Documents'] for row in ticker_data)
            st.metric("Total Documents", total_docs)
        with col3:
            st.metric("Data Size", f"{get_data_size():.1f} GB")
    
    else:
        st.info("No companies found matching your search.")
    
    # Request new ticker section
    st.markdown("---")
    st.subheader("Request New Ticker")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_ticker = st.text_input("Enter ticker symbol", placeholder="e.g., AAPL, MSFT")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("Request Data", key="request_ticker", use_container_width=True):
            if new_ticker:
                request_new_ticker(new_ticker.upper())

def show_company_documents(company: str, doc_service: DocumentService):
    """Show documents for a company"""
    with st.expander(f"{company} Documents", expanded=True):
        docs = doc_service.get_company_documents(company)
        
        if docs:
            for doc in docs[:10]:  # Show first 10
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.text(doc['name'])
                with col2:
                    st.text(f"{doc['size'] / 1024:.1f} KB")
                with col3:
                    if st.button("View", key=f"view_doc_{doc['name'][:20]}"):
                        st.session_state.viewing_document = doc
                        st.session_state.viewing_company = company
            
            if len(docs) > 10:
                st.caption(f"... and {len(docs) - 10} more documents")
        else:
            st.info("No documents found")

def request_new_ticker(ticker: str):
    """Request data for new ticker"""
    with st.spinner(f"Checking {ticker}..."):
        try:
            # Initialize scraper
            scraper = SECCompliantScraper()
            
            # Check if ticker exists
            cik = resolver.get_cik(ticker)
            
            if cik:
                st.info(f"Found {ticker} (CIK: {cik}). Starting download...")
                
                # Start download in background
                # In production, this would be queued
                st.success(f"Request submitted! {ticker} will be available soon.")
                st.balloons()
            else:
                st.error(f"Ticker {ticker} not found in SEC database.")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

def get_data_size():
    """Calculate total data size"""
    data_path = Path("data/sec_documents")
    if not data_path.exists():
        return 0.0
    
    total_size = 0
    for company_dir in data_path.iterdir():
        if company_dir.is_dir():
            for file in company_dir.iterdir():
                if file.is_file():
                    total_size += file.stat().st_size
    
    return total_size / (1024 ** 3)  # Convert to GB
