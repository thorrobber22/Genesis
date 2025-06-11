#!/usr/bin/env python3
"""
SEC Pipeline Admin - Updated with Real IPO Scraper Integration
"""

import streamlit as st
import asyncio
from pathlib import Path
import json
from datetime import datetime
import sys
import pandas as pd

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the working scrapers
from scrapers.sec.sec_compliant_scraper import SECCompliantScraper
from scrapers.ipo_scraper_real import IPOScraperReal
from services.pipeline_orchestrator import PipelineOrchestrator

st.set_page_config(page_title="SEC Pipeline Admin", page_icon="🏛️", layout="wide")

# Password protection
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🏛️ SEC Pipeline Admin")
    password = st.text_input("Password", type="password")
    if password == "hedgeadmin2025":
        st.session_state.authenticated = True
        st.rerun()
    else:
        if password:
            st.error("Invalid password")
        st.stop()

# Helper to run async
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Initialize
scraper = SECCompliantScraper()
ipo_scraper = IPOScraperReal()
orchestrator = PipelineOrchestrator()

# Header
st.title("🏛️ SEC Pipeline Admin")
st.caption("Manage company requests and download SEC documents")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Company Requests", 
    "📥 Manual Download", 
    "🔍 CIK Lookup", 
    "📈 IPO Scraper",
    "🚀 Full Pipeline"
])

with tab1:
    st.header("Company Requests")
    
    # Load requests
    requests_file = Path("data/company_requests.json")
    if requests_file.exists():
        with open(requests_file, 'r', encoding='utf-8') as f:
            requests = json.load(f)
        
        # Filter by status
        col1, col2, col3 = st.columns(3)
        with col1:
            show_pending = st.checkbox("Show Pending", value=True)
        with col2:
            show_completed = st.checkbox("Show Completed", value=False)
        with col3:
            show_failed = st.checkbox("Show Failed", value=False)
        
        # Filter requests
        filtered_requests = []
        if show_pending:
            filtered_requests.extend([r for r in requests if r.get('status') == 'pending'])
        if show_completed:
            filtered_requests.extend([r for r in requests if r.get('status') == 'completed'])
        if show_failed:
            filtered_requests.extend([r for r in requests if r.get('status') == 'failed'])
        
        if filtered_requests:
            st.subheader(f"Requests ({len(filtered_requests)})")
            
            # Batch operations
            if st.button("🔄 Process All Pending", type="primary"):
                pending = [r for r in requests if r.get('status') == 'pending' and r.get('cik')]
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, req in enumerate(pending[:5]):  # Limit to 5 for safety
                    status_text.text(f"Processing {req['ticker']}...")
                    progress_bar.progress((i + 1) / len(pending[:5]))
                    
                    result = run_async(scraper.scan_and_download_everything(
                        req['ticker'],
                        req['cik']
                    ))
                    
                    if result['success']:
                        req['status'] = 'completed'
                        req['documents_count'] = result['total_files']
                        req['completed_at'] = datetime.now().isoformat()
                    else:
                        req['status'] = 'failed'
                        req['error'] = result.get('error', 'Unknown error')
                
                # Save updated requests
                with open(requests_file, 'w', encoding='utf-8') as f:
                    json.dump(requests, f, indent=2)
                
                st.success("✅ Batch processing complete!")
                st.rerun()
            
            # Display requests
            for req in filtered_requests:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{req.get('ticker', 'N/A')}**")
                        
                        # Status badge
                        status = req.get('status', 'unknown')
                        if status == 'pending':
                            st.caption("🟡 Pending")
                        elif status == 'completed':
                            st.caption("✅ Completed")
                        elif status == 'failed':
                            st.caption("❌ Failed")
                    
                    with col2:
                        st.write(req.get('company_name', 'Unknown'))
                        st.caption(f"CIK: {req.get('cik', 'Not found')}")
                        
                        # Show IPO data if available
                        if req.get('ipo_data'):
                            ipo = req['ipo_data']
                            if ipo.get('price_range'):
                                st.caption(f"💰 {ipo['price_range']}")
                    
                    with col3:
                        st.caption(f"Priority: {req.get('priority', 'Normal')}")
                        st.caption(f"Source: {req.get('source', 'Manual')}")
                    
                    with col4:
                        st.caption(f"By: {req.get('requested_by', 'System')}")
                        st.caption(req.get('timestamp', '')[:10])
                    
                    with col5:
                        if req.get('status') == 'pending' and req.get('cik'):
                            if st.button("Process", key=f"proc_{req.get('ticker')}_{req.get('timestamp')}"):
                                with st.spinner(f"Downloading {req.get('ticker')}..."):
                                    result = run_async(scraper.scan_and_download_everything(
                                        req.get('ticker'),
                                        req.get('cik')
                                    ))
                                    
                                    if result['success']:
                                        st.success(f"✅ Downloaded {result['total_files']} files!")
                                        
                                        # Update request
                                        req['status'] = 'completed'
                                        req['documents_count'] = result['total_files']
                                        req['completed_at'] = datetime.now().isoformat()
                                        
                                        # Save
                                        with open(requests_file, 'w', encoding='utf-8') as f:
                                            json.dump(requests, f, indent=2)
                                        
                                        st.rerun()
                                    else:
                                        st.error(f"Failed: {result.get('error')}")
                        elif req.get('status') == 'completed':
                            st.caption(f"📄 {req.get('documents_count', 0)} docs")
                    
                    st.divider()
        else:
            st.info("No requests match the selected filters")
    else:
        st.warning("No requests file found")
        if st.button("Initialize Request System"):
            requests_file.parent.mkdir(parents=True, exist_ok=True)
            with open(requests_file, 'w') as f:
                json.dump([], f)
            st.success("✅ Request system initialized!")
            st.rerun()

with tab2:
    st.header("Manual SEC Download")
    
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Ticker Symbol", placeholder="AAPL")
    with col2:
        cik = st.text_input("CIK Number", placeholder="0000320193")
    
    if st.button("📥 Download Documents", use_container_width=True, type="primary"):
        if ticker and cik:
            with st.spinner(f"Downloading {ticker}..."):
                result = run_async(scraper.scan_and_download_everything(
                    ticker.upper(),
                    cik
                ))
                
                if result['success']:
                    st.success(f"✅ Downloaded {result['total_files']} files for {ticker}!")
                    
                    # Show what was downloaded
                    if result.get('forms_downloaded'):
                        st.subheader("Downloaded Forms")
                        forms_df = pd.DataFrame(
                            result['forms_downloaded'].items(),
                            columns=['Form Type', 'Count']
                        )
                        st.dataframe(forms_df)
                    
                    # Show company info
                    if result.get('company_name'):
                        st.info(f"**Company:** {result['company_name']}")
                else:
                    st.error(f"Failed: {result.get('error')}")
        else:
            st.warning("Please enter both ticker and CIK")

with tab3:
    st.header("CIK Lookup")
    
    company_name = st.text_input("Company Name", placeholder="Apple Inc")
    
    if st.button("🔍 Lookup CIK", use_container_width=True):
        if company_name:
            # Download company tickers
            import requests
            
            with st.spinner("Searching SEC database..."):
                try:
                    response = requests.get(
                        "https://www.sec.gov/files/company_tickers.json",
                        headers={'User-Agent': 'HedgeIntel admin@hedgeintel.com'}
                    )
                    
                    if response.status_code == 200:
                        tickers = response.json()
                        
                        # Search for company
                        matches = []
                        search_term = company_name.upper()
                        
                        for item in tickers.values():
                            if search_term in item.get('title', '').upper():
                                matches.append({
                                    'ticker': item.get('ticker'),
                                    'name': item.get('title'),
                                    'cik': str(item.get('cik_str')).zfill(10)
                                })
                        
                        if matches:
                            st.success(f"Found {len(matches)} matches:")
                            
                            # Display as table
                            matches_df = pd.DataFrame(matches)
                            st.dataframe(matches_df, use_container_width=True)
                            
                            # Quick add buttons
                            st.subheader("Quick Actions")
                            for match in matches[:5]:
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"**{match['ticker']}** - {match['name']}")
                                with col2:
                                    if st.button(f"Add {match['ticker']}", key=f"add_{match['cik']}"):
                                        # Add to requests
                                        requests_file = Path("data/company_requests.json")
                                        requests = []
                                        if requests_file.exists():
                                            with open(requests_file, 'r') as f:
                                                requests = json.load(f)
                                        
                                        requests.append({
                                            'ticker': match['ticker'],
                                            'company_name': match['name'],
                                            'cik': match['cik'],
                                            'status': 'pending',
                                            'priority': 'normal',
                                            'source': 'manual_lookup',
                                            'requested_by': 'admin',
                                            'timestamp': datetime.now().isoformat()
                                        })
                                        
                                        with open(requests_file, 'w') as f:
                                            json.dump(requests, f, indent=2)
                                        
                                        st.success(f"✅ Added {match['ticker']} to requests!")
                        else:
                            st.warning("No matches found")
                    else:
                        st.error(f"SEC API error: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a company name")

with tab4:
    st.header("IPO Scraper")
    
    # Show last scrape info
    ipo_data_dir = Path("data/ipo_data")
    if ipo_data_dir.exists():
        latest_file = ipo_data_dir / "ipo_calendar_latest.json"
        if latest_file.exists():
            with open(latest_file, 'r') as f:
                last_data = json.load(f)
            
            st.info(f"📅 Last scraped: {last_data.get('scraped_at', 'Unknown')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Scrape IPOScoop", use_container_width=True, type="primary"):
            with st.spinner("Scraping real IPO data from IPOScoop.com..."):
                try:
                    # Run the real scraper
                    ipo_data = ipo_scraper.scrape_ipo_calendar()
                    
                    if ipo_data:
                        # Look up CIKs
                        ipo_data = ipo_scraper.lookup_ciks(ipo_data)
                        
                        # Display results
                        st.success("✅ IPO Scraping Complete!")
                        
                        # Summary metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Recently Priced", len(ipo_data.get('recently_priced', [])))
                        with col2:
                            st.metric("Upcoming", len(ipo_data.get('upcoming', [])))
                        with col3:
                            st.metric("Filed", len(ipo_data.get('filed', [])))
                        
                        # Show recent IPOs
                        if ipo_data.get('recently_priced'):
                            st.subheader("📊 Recently Priced IPOs")
                            
                            for ipo in ipo_data['recently_priced'][:5]:
                                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                                
                                with col1:
                                    st.write(f"**{ipo.get('company_name', 'Unknown')}**")
                                    if ipo.get('ticker'):
                                        st.caption(f"Ticker: {ipo['ticker']}")
                                
                                with col2:
                                    if ipo.get('cik'):
                                        st.caption(f"✅ CIK: {ipo['cik'][:6]}...")
                                    else:
                                        st.caption("❌ No CIK")
                                
                                with col3:
                                    st.caption(ipo.get('price_range', 'N/A'))
                                
                                with col4:
                                    if ipo.get('cik'):
                                        if st.button("Download", key=f"dl_ipo_{ipo.get('ticker', ipo.get('company_name'))}"):
                                            with st.spinner(f"Downloading {ipo['ticker']}..."):
                                                result = run_async(scraper.scan_and_download_everything(
                                                    ipo['ticker'],
                                                    ipo['cik']
                                                ))
                                                if result['success']:
                                                    st.success(f"✅ {result['total_files']} files")
                        
                        # Show upcoming IPOs
                        if ipo_data.get('upcoming'):
                            st.subheader("🚀 Upcoming IPOs")
                            
                            upcoming_df = pd.DataFrame(ipo_data['upcoming'][:10])
                            display_cols = ['company_name', 'ticker', 'exchange', 'expected_date']
                            available_cols = [col for col in display_cols if col in upcoming_df.columns]
                            if available_cols:
                                st.dataframe(upcoming_df[available_cols], use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Error scraping IPOs: {str(e)}")
                    st.exception(e)
    
    with col2:
        if st.button("📋 View Last Scrape", use_container_width=True):
            latest_file = Path("data/ipo_data/ipo_calendar_latest.json")
            if latest_file.exists():
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                
                st.json(data)
            else:
                st.warning("No previous scrape data found")

with tab5:
    st.header("Full Pipeline Automation")
    st.caption("Run the complete IPO → CIK → SEC download pipeline")
    
    # Options
    col1, col2, col3 = st.columns(3)
    with col1:
        auto_download = st.checkbox("Auto-download SEC documents", value=False)
    with col2:
        max_downloads = st.number_input("Max downloads", min_value=1, max_value=10, value=3)
    with col3:
        priority_only = st.checkbox("High priority only", value=True)
    
    if st.button("🚀 Run Full Pipeline", use_container_width=True, type="primary"):
        with st.spinner("Running full pipeline..."):
            try:
                # Run the pipeline
                result = run_async(orchestrator.run_full_pipeline(auto_download=auto_download))
                
                if result:
                    st.success("✅ Pipeline Complete!")
                    
                    # Show summary
                    summary = result['summary']
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("IPOs Found", summary['total_ipos'])
                    with col2:
                        st.metric("CIKs Matched", summary['with_ciks'])
                    with col3:
                        st.metric("New Requests", summary['new_requests'])
                    
                    # Show new requests
                    if result['new_requests']:
                        st.subheader("📝 New Company Requests Created")
                        
                        for req in result['new_requests']:
                            st.write(f"**{req['ticker']}** - {req['company_name']}")
                            if req.get('ipo_data'):
                                ipo = req['ipo_data']
                                cols = st.columns(3)
                                with cols[0]:
                                    st.caption(f"Price: {ipo.get('price_range', 'N/A')}")
                                with cols[1]:
                                    st.caption(f"Date: {ipo.get('expected_date', 'N/A')}")
                                with cols[2]:
                                    st.caption(f"Exchange: {ipo.get('exchange', 'N/A')}")
                    
                    st.info("✅ Check the Company Requests tab to process the new additions!")
                    
            except Exception as e:
                st.error(f"Pipeline error: {str(e)}")
                st.exception(e)

# Show current stats
st.divider()
st.subheader("📊 System Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    sec_dir = Path("data/sec_documents")
    if sec_dir.exists():
        company_count = len([d for d in sec_dir.iterdir() if d.is_dir()])
        st.metric("Companies", company_count)
    else:
        st.metric("Companies", 0)

with col2:
    total_docs = 0
    if sec_dir.exists():
        for company in sec_dir.iterdir():
            if company.is_dir():
                total_docs += len(list(company.glob("*.html")))
    st.metric("Total Documents", total_docs)

with col3:
    if requests_file.exists():
        with open(requests_file, 'r', encoding='utf-8') as f:
            all_requests = json.load(f)
        pending_count = len([r for r in all_requests if r.get('status') == 'pending'])
        st.metric("Pending Requests", pending_count)
    else:
        st.metric("Pending Requests", 0)

with col4:
    ipo_latest = Path("data/ipo_data/ipo_calendar_latest.json")
    if ipo_latest.exists():
        with open(ipo_latest, 'r') as f:
            ipo_data = json.load(f)
        total_ipos = (
            len(ipo_data.get('recently_priced', [])) +
            len(ipo_data.get('upcoming', [])) +
            len(ipo_data.get('filed', []))
        )
        st.metric("IPOs Tracked", total_ipos)
    else:
        st.metric("IPOs Tracked", 0)

# Footer
st.divider()
st.caption("SEC Pipeline Admin v2.0 - Real Data Edition 🚀")