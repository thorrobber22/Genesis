"""
Watch List Component
Date: 2025-06-07 14:02:41 UTC
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from services.document_service import DocumentService
from services.ai_service import AIService
import json
from pathlib import Path

def render_watchlist():
    """Render watchlist"""
    st.title("Watch List")
    
    # Initialize watchlist if not exists
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []
    
    if not st.session_state.watchlist:
        st.info("Your watchlist is empty. Add companies from the IPO Dashboard or Available Tickers.")
        return
    
    # Initialize services
    doc_service = DocumentService()
    ai_service = AIService()
    
    # Get watchlist data
    watchlist_data = []
    
    for company in st.session_state.watchlist:
        # Get company metrics
        metrics = get_company_metrics(company, doc_service, ai_service)
        watchlist_data.append(metrics)
    
    # Display as table
    if watchlist_data:
        df = pd.DataFrame(watchlist_data)
        
        # Reorder columns
        column_order = ['Company', 'Documents', 'Lock-up Status', 'Days Until', 'Latest Filing', 'Last Updated']
        df = df[column_order]
        
        # Display dataframe
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
            selected_company = df.iloc[selected_idx]['Company']
            
            st.markdown(f"### {selected_company} Actions")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("Start Chat", key=f"watch_chat_{selected_company}"):
                    st.session_state.current_page = "New Chat"
                    st.session_state.chat_context = selected_company
                    st.rerun()
            
            with col2:
                if st.button("View Analysis", key=f"watch_analysis_{selected_company}"):
                    show_company_analysis(selected_company, ai_service)
            
            with col3:
                if st.button("Set Alert", key=f"watch_alert_{selected_company}"):
                    set_alert(selected_company)
            
            with col4:
                if st.button("Remove", key=f"watch_remove_{selected_company}"):
                    st.session_state.watchlist.remove(selected_company)
                    st.rerun()
    
    # Watchlist settings
    st.markdown("---")
    st.subheader("Watchlist Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        alert_days = st.number_input(
            "Alert me X days before lock-up expiry",
            min_value=1,
            max_value=30,
            value=7,
            key="alert_days_before"
        )
    
    with col2:
        export_format = st.selectbox(
            "Export format",
            ["CSV", "Excel", "PDF"],
            key="export_format"
        )
    
    if st.button("Export Watchlist"):
        export_watchlist(watchlist_data, export_format)

def get_company_metrics(company: str, doc_service: DocumentService, ai_service: AIService) -> dict:
    """Get key metrics for a company"""
    # Get basic document info
    docs = doc_service.get_company_documents(company)
    
    metrics = {
        'Company': company,
        'Documents': len(docs),
        'Latest Filing': 'None',
        'Last Updated': 'N/A',
        'Lock-up Status': 'Checking...',
        'Days Until': 'N/A'
    }
    
    if docs:
        latest_doc = docs[0]
        metrics['Latest Filing'] = latest_doc['type']
        metrics['Last Updated'] = datetime.fromtimestamp(latest_doc['modified']).strftime('%Y-%m-%d')
        
        # Try to get lock-up info from cached data or AI
        lockup_info = get_lockup_info(company, ai_service)
        if lockup_info:
            metrics['Lock-up Status'] = lockup_info['status']
            metrics['Days Until'] = lockup_info['days_until']
    
    return metrics

def get_lockup_info(company: str, ai_service: AIService) -> dict:
    """Get lock-up information for company"""
    # Check if we have cached lock-up data
    cache_file = Path(f"data/lockup_cache/{company}.json")
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                
            # Calculate days until expiry
            expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
            days_until = (expiry_date - datetime.now()).days
            
            return {
                'status': f"Expires {data['expiry_date']}",
                'days_until': str(days_until) if days_until > 0 else 'Expired'
            }
        except:
            pass
    
    # If no cache, return placeholder
    # In production, this would trigger an AI analysis
    return {
        'status': 'Analysis pending',
        'days_until': 'TBD'
    }

def show_company_analysis(company: str, ai_service: AIService):
    """Show detailed company analysis"""
    with st.expander(f"{company} Analysis", expanded=True):
        st.markdown("### Quick Analysis")
        
        # Placeholder for AI-generated analysis
        analysis_points = [
            "Lock-up period: 180 days from IPO date",
            "Major shareholders subject to lock-up: 85%",
            "Key risk factors: Market volatility, competition",
            "Recent filing: S-1/A Amendment filed last week"
        ]
        
        for point in analysis_points:
            st.markdown(f"• {point}")
        
        if st.button("Generate Full Report", key=f"full_report_{company}"):
            st.info("Full report generation coming soon")

def set_alert(company: str):
    """Set alert for company"""
    with st.form(f"alert_form_{company}"):
        st.markdown(f"### Set Alert for {company}")
        
        alert_type = st.selectbox(
            "Alert type",
            ["Lock-up expiry", "New filing", "Price target", "Custom"]
        )
        
        if alert_type == "Lock-up expiry":
            days_before = st.slider("Days before expiry", 1, 30, 7)
        elif alert_type == "New filing":
            filing_types = st.multiselect(
                "Filing types",
                ["10-K", "10-Q", "8-K", "S-1", "Any"]
            )
        
        alert_method = st.radio(
            "Alert method",
            ["Email", "In-app notification", "Both"]
        )
        
        if st.form_submit_button("Set Alert"):
            st.success(f"Alert set for {company}")

def export_watchlist(data: list, format: str):
    """Export watchlist data"""
    df = pd.DataFrame(data)
    
    if format == "CSV":
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"watchlist_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    elif format == "Excel":
        # Would need to implement Excel export
        st.info("Excel export coming soon")
    elif format == "PDF":
        # Would need to implement PDF export
        st.info("PDF export coming soon")
