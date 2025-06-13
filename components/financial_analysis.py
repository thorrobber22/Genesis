"""
financial_analysis.py - Financial analysis component
Date: 2025-06-12 01:33:04 UTC
User: thorrobber22
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
from services.sec_service import get_company_filings, get_filing_content
from services.ai_service import get_ai_response
from services.data_service import get_company_data

def show_financial_analysis():
    """Display financial analysis dashboard"""
    st.header("Financial Analysis")
    
    # Company selector
    col1, col2 = st.columns([3, 1])
    with col1:
        ticker = st.text_input("Enter Ticker Symbol", placeholder="e.g., AAPL, GOOGL")
    with col2:
        st.write("")  # Spacer
        analyze_btn = st.button("Analyze", type="primary", use_container_width=True)
    
    if ticker and analyze_btn:
        analyze_company_financials(ticker.upper())
    
    # Show example companies
    st.divider()
    st.subheader("Recent IPO Analysis")
    show_recent_ipo_analysis()

def analyze_company_financials(ticker):
    """Analyze company financial data"""
    with st.spinner(f"Analyzing {ticker}..."):
        # Get company data
        company_data = get_company_data(ticker)
        
        if not company_data:
            st.error(f"No data found for {ticker}")
            return
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Revenue Analysis", "Risk Assessment", "AI Insights"])
        
        with tab1:
            show_company_overview(ticker, company_data)
        
        with tab2:
            show_revenue_analysis(ticker, company_data)
        
        with tab3:
            show_risk_assessment(ticker, company_data)
        
        with tab4:
            show_ai_insights(ticker, company_data)

def show_company_overview(ticker, company_data):
    """Show company overview"""
    st.subheader(f"{ticker} - Company Overview")
    
    # Key metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = extract_financial_metrics(company_data)
    
    with col1:
        st.metric("Market Cap", metrics.get("market_cap", "N/A"))
    with col2:
        st.metric("Revenue (TTM)", metrics.get("revenue_ttm", "N/A"))
    with col3:
        st.metric("Growth Rate", metrics.get("growth_rate", "N/A"))
    with col4:
        st.metric("Burn Rate", metrics.get("burn_rate", "N/A"))
    
    # Company description
    st.write("**About**")
    st.write(company_data.get("description", "No description available"))
    
    # Quick facts
    with st.expander("Quick Facts"):
        facts = {
            "Sector": company_data.get("sector", "N/A"),
            "Industry": company_data.get("industry", "N/A"),
            "Founded": company_data.get("founded", "N/A"),
            "Headquarters": company_data.get("headquarters", "N/A"),
            "Employees": company_data.get("employees", "N/A")
        }
        for key, value in facts.items():
            st.write(f"**{key}:** {value}")

def show_revenue_analysis(ticker, company_data):
    """Show revenue analysis with charts"""
    st.subheader("Revenue Analysis")
    
    # Mock financial data (would be extracted from S-1)
    quarters = ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"]
    revenue = [125, 142, 168, 195]
    costs = [98, 105, 115, 125]
    
    # Revenue chart
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Revenue", x=quarters, y=revenue, marker_color="#10A37F"))
    fig.add_trace(go.Bar(name="Costs", x=quarters, y=costs, marker_color="#E74C3C"))
    
    fig.update_layout(
        title="Quarterly Revenue vs Costs (in millions)",
        barmode="group",
        plot_bgcolor="#2A2B2D",
        paper_bgcolor="#212121",
        font=dict(color="#F7F7F8"),
        xaxis=dict(gridcolor="#565869"),
        yaxis=dict(gridcolor="#565869")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Growth metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # YoY growth chart
        growth_fig = go.Figure()
        growth_rates = [45, 52, 48, 55]
        growth_fig.add_trace(go.Scatter(
            x=quarters, 
            y=growth_rates,
            mode="lines+markers",
            line=dict(color="#10A37F", width=3),
            marker=dict(size=10)
        ))
        growth_fig.update_layout(
            title="YoY Growth Rate (%)",
            plot_bgcolor="#2A2B2D",
            paper_bgcolor="#212121",
            font=dict(color="#F7F7F8"),
            xaxis=dict(gridcolor="#565869"),
            yaxis=dict(gridcolor="#565869")
        )
        st.plotly_chart(growth_fig, use_container_width=True)
    
    with col2:
        # Margin analysis
        margins = [21.6, 26.1, 31.5, 35.9]
        margin_fig = go.Figure()
        margin_fig.add_trace(go.Scatter(
            x=quarters,
            y=margins,
            mode="lines+markers",
            fill="tozeroy",
            line=dict(color="#2E8AF6", width=3),
            fillcolor="rgba(46, 138, 246, 0.2)"
        ))
        margin_fig.update_layout(
            title="Gross Margin (%)",
            plot_bgcolor="#2A2B2D",
            paper_bgcolor="#212121",
            font=dict(color="#F7F7F8"),
            xaxis=dict(gridcolor="#565869"),
            yaxis=dict(gridcolor="#565869")
        )
        st.plotly_chart(margin_fig, use_container_width=True)

def show_risk_assessment(ticker, company_data):
    """Show risk assessment"""
    st.subheader("Risk Assessment")
    
    # Risk score calculation
    risk_factors = {
        "Market Risk": 7.5,
        "Competition Risk": 8.2,
        "Regulatory Risk": 5.5,
        "Financial Risk": 6.8,
        "Operational Risk": 6.0
    }
    
    # Overall risk score
    overall_risk = sum(risk_factors.values()) / len(risk_factors)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Risk gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=overall_risk,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Overall Risk Score"},
            gauge={
                "axis": {"range": [None, 10]},
                "bar": {"color": "#E74C3C" if overall_risk > 7 else "#F7B500" if overall_risk > 5 else "#10A37F"},
                "steps": [
                    {"range": [0, 3], "color": "#2A2B2D"},
                    {"range": [3, 7], "color": "#40414F"},
                    {"range": [7, 10], "color": "#565869"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 9
                }
            }
        ))
        fig.update_layout(
            paper_bgcolor="#212121",
            font={"color": "#F7F7F8", "size": 16}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk breakdown
        risk_df = pd.DataFrame(list(risk_factors.items()), columns=["Risk Type", "Score"])
        fig = px.bar(
            risk_df, 
            x="Score", 
            y="Risk Type", 
            orientation="h",
            color="Score",
            color_continuous_scale=["#10A37F", "#F7B500", "#E74C3C"]
        )
        fig.update_layout(
            title="Risk Factor Breakdown",
            plot_bgcolor="#2A2B2D",
            paper_bgcolor="#212121",
            font=dict(color="#F7F7F8"),
            xaxis=dict(gridcolor="#565869"),
            yaxis=dict(gridcolor="#565869"),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk details
    st.write("**Key Risk Factors:**")
    for risk, score in risk_factors.items():
        severity = "High" if score > 7 else "Medium" if score > 5 else "Low"
        color = "#E74C3C" if score > 7 else "#F7B500" if score > 5 else "#10A37F"
        st.markdown(f"- **{risk}**: <span style='color: {color}'>{severity} ({score:.1f}/10)</span>", unsafe_allow_html=True)

def show_ai_insights(ticker, company_data):
    """Show AI-generated insights"""
    st.subheader("AI Analysis")
    
    # Generate AI insights
    if st.button("Generate AI Insights"):
        with st.spinner("Analyzing with AI..."):
            prompt = f"""
            Analyze {ticker} as an IPO investment opportunity. Consider:
            1. Revenue growth trends
            2. Market opportunity
            3. Competitive position
            4. Key risks
            5. Investment recommendation
            
            Company data: {json.dumps(company_data, indent=2)[:1000]}
            """
            
            insights = get_ai_response(prompt)
            
            st.markdown("### AI Investment Analysis")
            st.write(insights)
            
            # Save insights
            if st.button("Save Analysis"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{ticker}_analysis_{timestamp}.txt"
                st.download_button(
                    label="Download Analysis",
                    data=insights,
                    file_name=filename,
                    mime="text/plain"
                )

def show_recent_ipo_analysis():
    """Show analysis of recent IPOs"""
    recent_ipos = [
        {"ticker": "RDDT", "name": "Reddit Inc.", "ipo_date": "2024-03-21", "performance": "+48%"},
        {"ticker": "BFRG", "name": "BurgerFi", "ipo_date": "2024-06-05", "performance": "-12%"},
        {"ticker": "ASNS", "name": "Asana Inc.", "ipo_date": "2024-09-15", "performance": "+22%"}
    ]
    
    for ipo in recent_ipos:
        with st.expander(f"{ipo['ticker']} - {ipo['name']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**IPO Date:** {ipo['ipo_date']}")
            with col2:
                color = "#10A37F" if ipo['performance'].startswith('+') else "#E74C3C"
                st.markdown(f"**Performance:** <span style='color: {color}'>{ipo['performance']}</span>", unsafe_allow_html=True)
            with col3:
                if st.button(f"Analyze {ipo['ticker']}", key=f"analyze_{ipo['ticker']}"):
                    analyze_company_financials(ipo['ticker'])

def extract_financial_metrics(company_data):
    """Extract financial metrics from company data"""
    # This would parse actual S-1 data
    return {
        "market_cap": "$2.5B",
        "revenue_ttm": "$580M",
        "growth_rate": "+52% YoY",
        "burn_rate": "$45M/quarter"
    }

if __name__ == "__main__":
    show_financial_analysis()
