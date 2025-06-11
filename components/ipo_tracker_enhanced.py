"""
Enhanced IPO Tracker with Additional Details
Created: 2025-06-07 21:50:17 UTC
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class IPOTrackerEnhanced:
    def __init__(self):
        self.ipo_data_path = Path("data/ipo_pipeline/ipo_calendar.json")
        
    def render_ipo_dashboard(self):
        """Render enhanced IPO dashboard"""
        st.subheader("Upcoming IPOs")
        
        # Load IPO data
        ipos = self.load_ipo_data()
        
        if not ipos:
            st.info("No upcoming IPOs this week")
            return
            
        # Create enhanced dataframe
        df_data = []
        for ipo in ipos:
            df_data.append({
                'Company': ipo.get('company', 'N/A'),
                'Sector': ipo.get('sector', 'N/A'),
                'Expected Date': ipo.get('expected_date', 'TBD'),
                'Valuation': ipo.get('expected_valuation', 'Not Available'),
                'Lead Underwriter': ipo.get('lead_underwriter', 'Not Available'),
                'Lock-up Period': ipo.get('lockup_period', 'Not Available')
            })
            
        df = pd.DataFrame(df_data)
        
        # Display with custom styling
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Add chat prompt
        st.markdown("---")
        st.markdown("💬 **Ask me about any IPO's business model or competitive landscape**")
        
    def load_ipo_data(self):
        """Load IPO data from file"""
        if self.ipo_data_path.exists():
            with open(self.ipo_data_path, 'r') as f:
                return json.load(f)
        
        # Return sample data if file doesn't exist
        return [
            {
                'company': 'Stripe',
                'sector': 'Fintech',
                'expected_date': 'June 12, 2025',
                'expected_valuation': '$65-70B',
                'lead_underwriter': 'Goldman Sachs',
                'lockup_period': '180 days'
            },
            {
                'company': 'Databricks',
                'sector': 'Data/AI',
                'expected_date': 'June 14, 2025',
                'expected_valuation': '$40-45B',
                'lead_underwriter': 'Morgan Stanley',
                'lockup_period': '180 days'
            }
        ]
