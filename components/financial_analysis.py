"""
components/financial_analysis.py - Financial analysis visualization
Date: 2025-06-11 21:40:33 UTC
User: thorrobber22
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from services.financial_parser import FinancialParser
import pandas as pd

def show_financial_analysis(ticker: str = None):
    """Show financial analysis for a company"""
    
    # Initialize parser
    if 'financial_parser' not in st.session_state:
        st.session_state.financial_parser = FinancialParser()
    
    parser = st.session_state.financial_parser
    
    # Get ticker from session or parameter
    if not ticker and 'selected_company' in st.session_state:
        ticker = st.session_state.selected_company
    
    if not ticker:
        st.info("💡 Select a company from the Companies tab to see financial analysis")
        return
    
    st.title(f"💰 Financial Analysis: {ticker}")
    
    # Parse financials
    with st.spinner(f"Analyzing {ticker} financials..."):
        financials = parser.parse_s1_financials(ticker)
    
    if not any([financials['revenue'], financials['net_loss'], financials['cash_position']]):
        st.warning(f"No financial data found for {ticker}. Make sure S-1 documents are downloaded.")
        return
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if financials['revenue']:
            latest_revenue = max(financials['revenue'], key=lambda x: x['value'])
            st.metric(
                "Latest Revenue",
                f"${latest_revenue['value']:,.0f}",
                help="Most recent revenue figure from S-1"
            )
    
    with col2:
        if financials['net_loss']:
            latest_loss = max(financials['net_loss'], key=lambda x: x['value'])
            st.metric(
                "Net Loss",
                f"${latest_loss['value']:,.0f}",
                delta=None,
                delta_color="inverse",
                help="Most recent net loss"
            )
    
    with col3:
        if financials['cash_position']:
            st.metric(
                "Cash Position",
                f"${financials['cash_position']:,.0f}",
                help="Current cash and equivalents"
            )
    
    with col4:
        if financials['runway_months']:
            st.metric(
                "Runway",
                f"{financials['runway_months']} months",
                help="Months of cash remaining at current burn rate"
            )
    
    # Visualizations
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Burn Rate Gauge
        if financials['burn_rate']:
            fig = create_burn_rate_gauge(financials['burn_rate'])
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Cash Runway Chart
        if financials['cash_position'] and financials['burn_rate']:
            fig = create_runway_chart(
                financials['cash_position'],
                financials['burn_rate'],
                financials['runway_months']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Financial Details
    if financials['revenue'] or financials['net_loss']:
        st.markdown("### 📊 Financial Details")
        
        tabs = st.tabs(["Revenue", "Losses", "Valuation Metrics"])
        
        with tabs[0]:
            if financials['revenue']:
                st.markdown("**Revenue Figures Found:**")
                for i, rev in enumerate(financials['revenue'][:5], 1):
                    st.markdown(f"{i}. ${rev['value']:,.0f}")
                    st.caption(f"Context: ...{rev['context'][-100:]}...")
        
        with tabs[1]:
            if financials['net_loss']:
                st.markdown("**Net Loss Figures Found:**")
                for i, loss in enumerate(financials['net_loss'][:5], 1):
                    st.markdown(f"{i}. ${loss['value']:,.0f}")
                    st.caption(f"Context: ...{loss['context'][-100:]}...")
        
        with tabs[2]:
            if financials['valuation_metrics']:
                for metric, value in financials['valuation_metrics'].items():
                    st.metric(metric.replace('_', ' ').title(), value)
    
    # Export button
    st.markdown("---")
    if st.button("📄 Export Financial Summary", type="secondary"):
        summary = parser.generate_financial_summary(ticker)
        st.text_area("Financial Summary", summary, height=300)

def create_burn_rate_gauge(burn_rate: float):
    """Create burn rate gauge chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = burn_rate,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Monthly Burn Rate"},
        number = {'prefix': "$", 'valueformat': ",.0f"},
        gauge = {
            'axis': {'range': [None, burn_rate * 2], 'tickformat': "$,.0f"},
            'bar': {'color': "#FF6B6B"},
            'steps': [
                {'range': [0, burn_rate * 0.5], 'color': "#4ECDC4"},
                {'range': [burn_rate * 0.5, burn_rate], 'color': "#FFE66D"},
                {'range': [burn_rate, burn_rate * 2], 'color': "#FF6B6B"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': burn_rate
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_runway_chart(cash: float, burn_rate: float, months: int):
    """Create cash runway projection chart"""
    # Generate monthly projections
    months_list = list(range(months + 1))
    cash_remaining = [cash - (burn_rate * m) for m in months_list]
    cash_remaining = [max(0, c) for c in cash_remaining]  # Don't go negative
    
    df = pd.DataFrame({
        'Month': months_list,
        'Cash Remaining': cash_remaining
    })
    
    fig = px.area(
        df, 
        x='Month', 
        y='Cash Remaining',
        title='Cash Runway Projection',
        labels={'Cash Remaining': 'Cash ($)'}
    )
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    
    # Style
    fig.update_traces(fillcolor='rgba(78, 205, 196, 0.3)', line_color='#4ECDC4')
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_tickformat='$,.0f'
    )
    
    return fig
