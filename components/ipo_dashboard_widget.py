#!/usr/bin/env python3
"""
IPO Dashboard Widget - Displays real IPO data from scraper
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List

class IPODashboardWidget:
    def __init__(self):
        self.data_dir = Path("data/ipo_data")
        self.ipo_data = self._load_latest_ipo_data()
        
    def _load_latest_ipo_data(self) -> Dict:
        """Load the latest IPO data from scraper"""
        latest_file = self.data_dir / "ipo_calendar_latest.json"
        
        if latest_file.exists():
            with open(latest_file, 'r') as f:
                return json.load(f)
        else:
            return {
                'scraped_at': 'Never',
                'recently_priced': [],
                'upcoming': [],
                'filed': []
            }
    
    def render_dashboard(self):
        """Render the full IPO dashboard"""
        st.title("📈 IPO Intelligence Dashboard")
        
        # Last update info
        scraped_time = self.ipo_data.get('scraped_at', 'Never')
        if scraped_time != 'Never':
            scraped_dt = datetime.fromisoformat(scraped_time.replace('Z', '+00:00'))
            time_ago = datetime.now() - scraped_dt.replace(tzinfo=None)
            
            if time_ago < timedelta(hours=1):
                update_text = f"Updated {int(time_ago.seconds / 60)} minutes ago"
            elif time_ago < timedelta(days=1):
                update_text = f"Updated {int(time_ago.seconds / 3600)} hours ago"
            else:
                update_text = f"Updated {time_ago.days} days ago"
        else:
            update_text = "No data available"
        
        st.caption(f"🕒 {update_text}")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            recent_count = len(self.ipo_data.get('recently_priced', []))
            st.metric("Recently Priced", recent_count, delta="This Week")
        
        with col2:
            upcoming_count = len(self.ipo_data.get('upcoming', []))
            st.metric("Upcoming IPOs", upcoming_count, delta="Next 30 Days")
        
        with col3:
            filed_count = len(self.ipo_data.get('filed', []))
            st.metric("Filed (S-1)", filed_count)
        
        with col4:
            # Count IPOs with CIKs (have documents)
            with_docs = sum(1 for ipo in self._get_all_ipos() if ipo.get('cik'))
            st.metric("With SEC Docs", with_docs)
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔥 Hot IPOs", 
            "📅 Upcoming", 
            "📄 Recently Filed",
            "📊 Analysis"
        ])
        
        with tab1:
            self._render_hot_ipos()
        
        with tab2:
            self._render_upcoming_ipos()
        
        with tab3:
            self._render_filed_ipos()
        
        with tab4:
            self._render_ipo_analysis()
    
    def render_compact_widget(self):
        """Render a compact widget for the main dashboard"""
        st.markdown("### 📈 IPO Tracker")
        
        # Quick stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            recent = len(self.ipo_data.get('recently_priced', []))
            st.metric("Recent IPOs", recent)
        
        with col2:
            upcoming = len(self.ipo_data.get('upcoming', []))
            st.metric("Upcoming", upcoming)
        
        with col3:
            if st.button("View All →", use_container_width=True):
                st.session_state['page'] = 'ipo_dashboard'
                st.rerun()
        
        # Show top 5 hot IPOs
        st.markdown("#### 🔥 Hot IPOs")
        
        # Combine recently priced and upcoming
        hot_ipos = []
        
        # Add recently priced
        for ipo in self.ipo_data.get('recently_priced', [])[:3]:
            ipo['category'] = 'Recently Priced'
            ipo['priority'] = 1
            hot_ipos.append(ipo)
        
        # Add upcoming
        for ipo in self.ipo_data.get('upcoming', [])[:2]:
            ipo['category'] = 'Upcoming'
            ipo['priority'] = 2
            hot_ipos.append(ipo)
        
        if hot_ipos:
            for ipo in hot_ipos:
                self._render_ipo_card_compact(ipo)
        else:
            st.info("No IPO data available. Run the IPO scraper to fetch latest data.")
    
    def _render_hot_ipos(self):
        """Render the hot IPOs section"""
        st.markdown("### 🔥 Recently Priced IPOs")
        
        recent_ipos = self.ipo_data.get('recently_priced', [])
        
        if not recent_ipos:
            st.info("No recently priced IPOs found.")
            return
        
        # Create columns for cards
        for i in range(0, len(recent_ipos), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                if i < len(recent_ipos):
                    self._render_ipo_card(recent_ipos[i])
            
            with col2:
                if i + 1 < len(recent_ipos):
                    self._render_ipo_card(recent_ipos[i + 1])
    
    def _render_upcoming_ipos(self):
        """Render upcoming IPOs"""
        st.markdown("### 📅 Upcoming IPOs")
        
        upcoming = self.ipo_data.get('upcoming', [])
        
        if not upcoming:
            st.info("No upcoming IPOs found.")
            return
        
        # Display as a table
        df_data = []
        for ipo in upcoming:
            df_data.append({
                'Company': ipo.get('company_name', 'Unknown'),
                'Ticker': ipo.get('ticker', 'TBD'),
                'Exchange': ipo.get('exchange', 'N/A'),
                'Price Range': ipo.get('price_range', 'TBD'),
                'Expected Date': ipo.get('expected_date', 'TBD'),
                'Has Docs': '✅' if ipo.get('cik') else '❌'
            })
        
        df = pd.DataFrame(df_data)
        
        # Style the dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Company": st.column_config.TextColumn("Company", width="large"),
                "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                "Has Docs": st.column_config.TextColumn("Docs", width="small")
            }
        )
        
        # Action buttons
        st.markdown("#### Quick Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download All S-1s", use_container_width=True):
                with_cik = [ipo for ipo in upcoming if ipo.get('cik')]
                st.info(f"Found {len(with_cik)} companies with CIKs. Go to Admin Panel to download.")
        
        with col2:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.info("Go to Admin Panel → IPO Scraper to refresh data")
    
    def _render_filed_ipos(self):
        """Render recently filed IPOs"""
        st.markdown("### 📄 Recently Filed (S-1)")
        
        filed = self.ipo_data.get('filed', [])
        
        if not filed:
            st.info("No recently filed IPOs found.")
            return
        
        # Group by filing date if available
        for ipo in filed[:10]:  # Show top 10
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{ipo.get('company_name', 'Unknown')}**")
                if ipo.get('ticker'):
                    st.caption(f"Proposed ticker: {ipo['ticker']}")
            
            with col2:
                if ipo.get('cik'):
                    st.success("CIK Available")
                else:
                    st.warning("No CIK")
            
            with col3:
                if ipo.get('cik'):
                    if st.button("View S-1", key=f"s1_{ipo.get('ticker', ipo.get('company_name'))}"):
                        # Navigate to document explorer with this company
                        st.session_state['selected_company'] = ipo.get('ticker')
                        st.session_state['page'] = 'document_explorer'
                        st.rerun()
            
            st.divider()
    
    def _render_ipo_analysis(self):
        """Render IPO market analysis"""
        st.markdown("### 📊 IPO Market Analysis")
        
        # Calculate statistics
        all_ipos = self._get_all_ipos()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Market Activity")
            
            # IPOs by category
            categories = {
                'Recently Priced': len(self.ipo_data.get('recently_priced', [])),
                'Upcoming': len(self.ipo_data.get('upcoming', [])),
                'Filed': len(self.ipo_data.get('filed', []))
            }
            
            # Create a bar chart
            df_cat = pd.DataFrame(
                list(categories.items()),
                columns=['Category', 'Count']
            )
            
            st.bar_chart(df_cat.set_index('Category'))
        
        with col2:
            st.markdown("#### 🏢 By Exchange")
            
            # Count by exchange
            exchanges = {}
            for ipo in all_ipos:
                exchange = ipo.get('exchange', 'Unknown')
                exchanges[exchange] = exchanges.get(exchange, 0) + 1
            
            # Show top exchanges
            for exchange, count in sorted(exchanges.items(), key=lambda x: x[1], reverse=True)[:5]:
                st.metric(exchange, count)
        
        # Sector analysis (if we had sector data)
        st.markdown("#### 🏭 Sector Breakdown")
        st.info("Sector analysis will be available once we parse S-1 filings for industry classification.")
        
        # Price range analysis
        st.markdown("#### 💰 Price Range Analysis")
        
        price_ranges = []
        for ipo in all_ipos:
            if ipo.get('price_range') and '$' in ipo['price_range']:
                # Parse price range
                try:
                    # Extract numbers from format like "$15-$17"
                    import re
                    numbers = re.findall(r'\d+', ipo['price_range'])
                    if len(numbers) >= 2:
                        low = int(numbers[0])
                        high = int(numbers[1])
                        mid = (low + high) / 2
                        price_ranges.append({
                            'Company': ipo.get('ticker', ipo.get('company_name', 'Unknown'))[:10],
                            'Low': low,
                            'High': high,
                            'Midpoint': mid
                        })
                except:
                    pass
        
        if price_ranges:
            df_prices = pd.DataFrame(price_ranges[:10])  # Top 10
            st.dataframe(df_prices, use_container_width=True, hide_index=True)
        else:
            st.info("No price range data available")
    
    def _render_ipo_card(self, ipo: Dict):
        """Render a detailed IPO card"""
        with st.container():
            # Card styling
            st.markdown("""
            <style>
            .ipo-card {
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
                background-color: #f9f9f9;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Card content
            st.markdown(f"### {ipo.get('company_name', 'Unknown Company')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.caption("**Ticker**")
                st.write(ipo.get('ticker', 'TBD'))
                
                st.caption("**Exchange**")
                st.write(ipo.get('exchange', 'N/A'))
            
            with col2:
                st.caption("**Price Range**")
                st.write(ipo.get('price_range', 'TBD'))
                
                st.caption("**Expected Date**")
                st.write(ipo.get('expected_date', 'TBD'))
            
            # Document status
            if ipo.get('cik'):
                st.success(f"✅ SEC Documents Available (CIK: {ipo['cik'][:6]}...)")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📄 View S-1", key=f"view_{ipo.get('ticker')}_{ipo.get('cik')}"):
                        st.session_state['selected_company'] = ipo.get('ticker')
                        st.session_state['page'] = 'document_explorer'
                        st.rerun()
                
                with col2:
                    if st.button("💬 Analyze", key=f"analyze_{ipo.get('ticker')}_{ipo.get('cik')}"):
                        st.session_state['chat_context'] = {
                            'current_company': ipo.get('ticker'),
                            'current_document': None,
                            'conversation_id': datetime.now().isoformat()
                        }
                        st.session_state['page'] = 'ai_chat'
                        st.rerun()
                
                with col3:
                    if st.button("➕ Watchlist", key=f"watch_{ipo.get('ticker')}_{ipo.get('cik')}"):
                        self._add_to_watchlist(ipo)
            else:
                st.warning("⏳ SEC documents not yet available")
            
            st.divider()
    
    def _render_ipo_card_compact(self, ipo: Dict):
        """Render a compact IPO card for dashboard"""
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{ipo.get('company_name', 'Unknown')}**")
            st.caption(f"{ipo.get('ticker', 'TBD')} • {ipo.get('category', '')}")
        
        with col2:
            st.caption(ipo.get('price_range', 'TBD'))
        
        with col3:
            if ipo.get('cik'):
                st.caption("📄 Docs ✅")
            else:
                st.caption("📄 Docs ❌")
        
        with col4:
            if st.button("→", key=f"compact_{ipo.get('ticker')}_{datetime.now().timestamp()}"):
                st.session_state['page'] = 'ipo_dashboard'
                st.rerun()
    
    def _get_all_ipos(self) -> List[Dict]:
        """Get all IPOs from all categories"""
        all_ipos = []
        all_ipos.extend(self.ipo_data.get('recently_priced', []))
        all_ipos.extend(self.ipo_data.get('upcoming', []))
        all_ipos.extend(self.ipo_data.get('filed', []))
        return all_ipos
    
    def _add_to_watchlist(self, ipo: Dict):
        """Add IPO to user's watchlist"""
        watchlist_file = Path("data/watchlists.json")
        
        # Load existing watchlist
        if watchlist_file.exists():
            with open(watchlist_file, 'r') as f:
                watchlists = json.load(f)
        else:
            watchlists = {}
        
        # Add to default user watchlist
        user = "default_user"  # In production, use actual user ID
        
        if user not in watchlists:
            watchlists[user] = []
        
        # Check if already in watchlist
        ticker = ipo.get('ticker', ipo.get('company_name'))
        if not any(w.get('ticker') == ticker for w in watchlists[user]):
            watchlists[user].append({
                'ticker': ticker,
                'company_name': ipo.get('company_name'),
                'cik': ipo.get('cik'),
                'added_date': datetime.now().isoformat(),
                'ipo_data': ipo
            })
            
            # Save
            watchlist_file.parent.mkdir(parents=True, exist_ok=True)
            with open(watchlist_file, 'w') as f:
                json.dump(watchlists, f, indent=2)
            
            st.success(f"✅ Added {ticker} to watchlist!")
        else:
            st.info(f"{ticker} is already in your watchlist")

# Standalone function for integration
def render_ipo_dashboard():
    """Render the full IPO dashboard"""
    dashboard = IPODashboardWidget()
    dashboard.render_dashboard()

def render_ipo_widget():
    """Render the compact IPO widget for main dashboard"""
    widget = IPODashboardWidget()
    widget.render_compact_widget()

# Test the dashboard
if __name__ == "__main__":
    st.set_page_config(page_title="IPO Dashboard Test", layout="wide")
    
    # Test both views
    view = st.radio("Select View", ["Full Dashboard", "Compact Widget"])
    
    if view == "Full Dashboard":
        render_ipo_dashboard()
    else:
        st.title("Main Dashboard")
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            render_ipo_widget()
        
        with col2:
            st.markdown("### 📊 Other Widgets")
            st.info("Market stats would go here")