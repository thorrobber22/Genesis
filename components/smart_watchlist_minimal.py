#!/usr/bin/env python3
"""
Smart Watchlist - Minimal, Clean Design
Focus on alerts and essential information
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List

class SmartWatchlist:
    def __init__(self):
        self.data_dir = Path("data/watchlists")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.watchlist_file = self.data_dir / "watchlist.json"
        self.alerts_file = self.data_dir / "alerts.json"
        
        self.watchlist = self._load_watchlist()
        self.alerts = self._load_alerts()
        
    def _load_watchlist(self) -> Dict:
        """Load watchlist data"""
        if self.watchlist_file.exists():
            with open(self.watchlist_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_alerts(self) -> List:
        """Load alerts"""
        if self.alerts_file.exists():
            with open(self.alerts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_watchlist(self):
        """Save watchlist data"""
        with open(self.watchlist_file, 'w', encoding='utf-8') as f:
            json.dump(self.watchlist, f, indent=2)
    
    def _save_alerts(self):
        """Save alerts"""
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(self.alerts, f, indent=2)
    
    def render_watchlist_page(self):
        """Render the watchlist page"""
        st.header("⭐ Smart Watchlist")
        
        # Alert banner if there are unread alerts
        unread_count = len([a for a in self.alerts if not a.get('read', False)])
        if unread_count > 0:
            st.warning(f"🔔 You have {unread_count} unread alerts")
        
        # Simple tabs
        tab1, tab2 = st.tabs(["Watchlist", "Alerts"])
        
        with tab1:
            self._render_watchlist()
        
        with tab2:
            self._render_alerts()
    
    def _render_watchlist(self):
        """Render the main watchlist"""
        # Add company section
        with st.expander("➕ Add Company", expanded=False):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                ticker = st.text_input("Ticker", placeholder="AAPL")
            
            with col2:
                company_name = st.text_input("Company Name", placeholder="Apple Inc.")
            
            with col3:
                st.write("")  # Spacer
                st.write("")  # Spacer
                if st.button("Add", use_container_width=True, type="primary"):
                    if ticker:
                        self._add_to_watchlist(ticker.upper(), company_name or ticker)
                        st.rerun()
        
        st.markdown("---")
        
        # Display watchlist
        if not self.watchlist:
            st.info("Your watchlist is empty. Add companies to track new filings and IPO updates.")
            return
        
        # Stats row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tracking", len(self.watchlist))
        with col2:
            # Count IPO candidates
            ipo_count = sum(1 for w in self.watchlist.values() if w.get('type') == 'IPO')
            st.metric("IPO Candidates", ipo_count)
        with col3:
            if st.button("🔄 Check All", use_container_width=True):
                self._check_all_updates()
        
        st.markdown("---")
        
        # Company list - clean table view
        watchlist_data = []
        for ticker, data in sorted(self.watchlist.items()):
            # Check for recent activity
            has_recent = self._has_recent_filings(ticker, days=7)
            
            watchlist_data.append({
                'Ticker': ticker,
                'Company': data.get('company_name', ticker),
                'Type': data.get('type', 'Stock'),
                'Added': data.get('added_date', '')[:10],
                'Recent': '🟢' if has_recent else '',
                'Status': data.get('status', '')
            })
        
        df = pd.DataFrame(watchlist_data)
        
        # Display as interactive table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                "Company": st.column_config.TextColumn("Company", width="large"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Added": st.column_config.TextColumn("Added", width="medium"),
                "Recent": st.column_config.TextColumn("", width="small", help="Recent filing in last 7 days"),
                "Status": st.column_config.TextColumn("Status", width="medium")
            }
        )
        
        # Quick actions
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            remove_ticker = st.selectbox(
                "Remove from watchlist",
                [""] + list(self.watchlist.keys())
            )
        
        with col2:
            st.write("")  # Spacer
            if st.button("Remove", use_container_width=True, disabled=not remove_ticker):
                if remove_ticker:
                    del self.watchlist[remove_ticker]
                    self._save_watchlist()
                    st.success(f"Removed {remove_ticker}")
                    st.rerun()
    
    def _render_alerts(self):
        """Render alerts section"""
        if not self.alerts:
            st.info("No alerts yet. Alerts will appear when watched companies have new filings or IPO updates.")
            return
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("Mark All Read", use_container_width=True):
                for alert in self.alerts:
                    alert['read'] = True
                self._save_alerts()
                st.rerun()
        
        with col2:
            if st.button("Clear Read", use_container_width=True):
                self.alerts = [a for a in self.alerts if not a.get('read', False)]
                self._save_alerts()
                st.rerun()
        
        st.markdown("---")
        
        # Display alerts - newest first
        self.alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        for i, alert in enumerate(self.alerts[:20]):  # Show latest 20
            # Skip read alerts if too many
            if i > 10 and alert.get('read', False):
                continue
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                # Alert styling based on read status
                if not alert.get('read', False):
                    st.markdown(f"**🔴 {alert['title']}**")
                else:
                    st.markdown(f"⚪ {alert['title']}")
                
                st.caption(alert['message'])
                
                # Time ago
                alert_time = datetime.fromisoformat(alert['timestamp'])
                time_diff = datetime.now() - alert_time
                
                if time_diff < timedelta(hours=1):
                    time_str = f"{int(time_diff.seconds / 60)}m ago"
                elif time_diff < timedelta(days=1):
                    time_str = f"{int(time_diff.seconds / 3600)}h ago"
                else:
                    time_str = f"{time_diff.days}d ago"
                
                st.caption(f"⏰ {time_str}")
            
            with col2:
                if alert.get('ticker'):
                    if st.button("View", key=f"view_{i}", use_container_width=True):
                        st.session_state.selected_company = alert['ticker']
                        st.session_state.main_navigation = "Document Explorer"
                        # Mark as read
                        self.alerts[i]['read'] = True
                        self._save_alerts()
                        st.rerun()
            
            with col3:
                if not alert.get('read', False):
                    if st.button("✓", key=f"read_{i}", use_container_width=True, help="Mark as read"):
                        self.alerts[i]['read'] = True
                        self._save_alerts()
                        st.rerun()
            
            st.divider()
    
    def _add_to_watchlist(self, ticker: str, company_name: str):
        """Add company to watchlist"""
        if ticker in self.watchlist:
            st.warning(f"{ticker} already in watchlist")
            return
        
        # Determine if it's an IPO
        ipo_data = self._load_ipo_data()
        is_ipo = False
        
        for ipo in ipo_data.get('filed', []) + ipo_data.get('upcoming', []):
            if ipo.get('ticker') == ticker:
                is_ipo = True
                break
        
        self.watchlist[ticker] = {
            'ticker': ticker,
            'company_name': company_name,
            'added_date': datetime.now().isoformat(),
            'type': 'IPO' if is_ipo else 'Stock',
            'last_checked': datetime.now().isoformat()
        }
        
        self._save_watchlist()
        
        # Create welcome alert
        self._create_alert(
            ticker=ticker,
            title=f"Added {ticker}",
            message=f"Now tracking {company_name}",
            alert_type="added"
        )
        
        st.success(f"✅ Added {ticker} to watchlist")
    
    def _has_recent_filings(self, ticker: str, days: int = 7) -> bool:
        """Check if company has recent filings"""
        company_dir = Path(f"data/sec_documents/{ticker}")
        if not company_dir.exists():
            return False
        
        cutoff = datetime.now() - timedelta(days=days)
        
        for doc in company_dir.glob("*.html"):
            if datetime.fromtimestamp(doc.stat().st_mtime) > cutoff:
                return True
        
        return False
    
    def _check_all_updates(self):
        """Check all companies for updates"""
        updates_found = 0
        
        with st.spinner("Checking for updates..."):
            for ticker, data in self.watchlist.items():
                # Check for new filings
                last_checked = datetime.fromisoformat(data.get('last_checked', '2020-01-01'))
                company_dir = Path(f"data/sec_documents/{ticker}")
                
                if company_dir.exists():
                    for doc in company_dir.glob("*.html"):
                        file_time = datetime.fromtimestamp(doc.stat().st_mtime)
                        
                        if file_time > last_checked:
                            self._create_alert(
                                ticker=ticker,
                                title=f"New Filing: {ticker}",
                                message=f"{doc.name}",
                                alert_type="filing"
                            )
                            updates_found += 1
                
                # Check IPO status
                if data.get('type') == 'IPO':
                    ipo_update = self._check_ipo_status(ticker)
                    if ipo_update:
                        updates_found += 1
                
                # Update last checked
                self.watchlist[ticker]['last_checked'] = datetime.now().isoformat()
        
        self._save_watchlist()
        
        if updates_found > 0:
            st.success(f"Found {updates_found} new updates!")
        else:
            st.info("No new updates")
    
    def _check_ipo_status(self, ticker: str) -> bool:
        """Check if IPO status changed"""
        ipo_data = self._load_ipo_data()
        
        # Check if priced
        for ipo in ipo_data.get('recently_priced', []):
            if ipo.get('ticker') == ticker:
                if self.watchlist[ticker].get('status') != 'Priced':
                    self.watchlist[ticker]['status'] = 'Priced'
                    
                    self._create_alert(
                        ticker=ticker,
                        title=f"IPO Priced: {ticker}",
                        message=f"Priced at {ipo.get('price_range', 'Unknown')}",
                        alert_type="ipo_priced"
                    )
                    return True
        
        return False
    
    def _create_alert(self, ticker: str, title: str, message: str, alert_type: str):
        """Create a new alert"""
        alert = {
            'ticker': ticker,
            'title': title,
            'message': message,
            'type': alert_type,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        self.alerts.append(alert)
        self._save_alerts()
    
    def _load_ipo_data(self) -> Dict:
        """Load IPO data"""
        ipo_paths = [
            Path("data/ipo_data/ipo_calendar_latest.json"),
            Path("data/ipo_pipeline/ipo_calendar.json")
        ]
        
        for path in ipo_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    pass
        
        return {}
    
    def get_alert_count(self) -> int:
        """Get unread alert count"""
        return len([a for a in self.alerts if not a.get('read', False)])

# Integration functions
def render_smart_watchlist():
    """Render the smart watchlist page"""
    watchlist = SmartWatchlist()
    watchlist.render_watchlist_page()

def get_watchlist_alert_count() -> int:
    """Get alert count for navigation badge"""
    watchlist = SmartWatchlist()
    return watchlist.get_alert_count()

# Test
if __name__ == "__main__":
    st.set_page_config(page_title="Smart Watchlist", layout="wide")
    render_smart_watchlist()