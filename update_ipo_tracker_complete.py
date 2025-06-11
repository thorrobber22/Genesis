#!/usr/bin/env python3
"""
Complete IPO Tracker Update - Minimalist Design + Main App Integration
"""

import shutil
from pathlib import Path

print("🚀 Updating IPO Tracker with Minimalist Design...\n")

# 1. Create the updated minimalist IPO tracker
ipo_tracker_content = '''#!/usr/bin/env python3
"""IPO Tracker Component - Minimalist Design"""

import streamlit as st
import json
from pathlib import Path
import pandas as pd
from datetime import datetime

class IPOTracker:
    def __init__(self):
        # Try multiple possible paths
        self.ipo_paths = [
            Path("data/ipo_data/ipo_calendar_latest.json"),
            Path("data/ipo_pipeline/ipo_calendar.json"),
            Path("data/ipo_data/ipo_calendar.json")
        ]
        self.ipo_data = self._load_ipo_data()
        
    def _load_ipo_data(self):
        """Load IPO data from available sources"""
        for path in self.ipo_paths:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                    
                    # Convert to simple format
                    if 'recently_priced' in data or 'upcoming' in data or 'filed' in data:
                        return self._convert_scraped_data(data)
                    else:
                        return data
                except Exception as e:
                    continue
        
        return None
    
    def _convert_scraped_data(self, scraped_data):
        """Convert scraped data to simple format for display"""
        simple_data = []
        
        # Add recently priced
        for ipo in scraped_data.get('recently_priced', []):
            simple_data.append({
                'company': ipo.get('company_name', 'Unknown'),
                'ticker': ipo.get('ticker', 'N/A'),
                'date': ipo.get('expected_date', 'Recent'),
                'exchange': ipo.get('exchange', 'N/A'),
                'status': '🟢 Priced',
                'price_range': ipo.get('price_range', 'N/A'),
                'has_docs': '✅' if ipo.get('cik') else '❌'
            })
        
        # Add upcoming
        for ipo in scraped_data.get('upcoming', []):
            simple_data.append({
                'company': ipo.get('company_name', 'Unknown'),
                'ticker': ipo.get('ticker', 'N/A'),
                'date': ipo.get('expected_date', 'TBD'),
                'exchange': ipo.get('exchange', 'N/A'),
                'status': '🔵 Upcoming',
                'price_range': ipo.get('price_range', 'TBD'),
                'has_docs': '✅' if ipo.get('cik') else '❌'
            })
        
        # Add filed (limit to recent ones)
        for ipo in scraped_data.get('filed', [])[:15]:
            simple_data.append({
                'company': ipo.get('company_name', 'Unknown'),
                'ticker': ipo.get('ticker', 'TBD'),
                'date': 'Filed',
                'exchange': ipo.get('exchange', 'N/A'),
                'status': '🟡 Filed',
                'price_range': ipo.get('price_range', 'TBD'),
                'has_docs': '✅' if ipo.get('cik') else '❌'
            })
        
        return simple_data
        
    def render_ipo_tracker(self):
        """Render IPO tracker dashboard - minimalist style"""
        st.subheader("📈 IPO Pipeline Tracker")
        
        if self.ipo_data:
            # Convert to DataFrame
            df = pd.DataFrame(self.ipo_data)
            
            # Simple metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                priced = len([x for x in self.ipo_data if '🟢' in x.get('status', '')])
                st.metric("Recently Priced", priced)
            with col2:
                upcoming = len([x for x in self.ipo_data if '🔵' in x.get('status', '')])
                st.metric("Upcoming", upcoming)
            with col3:
                filed = len([x for x in self.ipo_data if '🟡' in x.get('status', '')])
                st.metric("Filed S-1", filed)
            with col4:
                with_docs = len([x for x in self.ipo_data if x.get('has_docs') == '✅'])
                st.metric("With Docs", with_docs)
            
            # Clean table display
            display_df = df[['company', 'ticker', 'exchange', 'status', 'price_range', 'has_docs']]
            
            # Style the dataframe
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "company": st.column_config.TextColumn("Company", width="large"),
                    "ticker": st.column_config.TextColumn("Ticker", width="small"),
                    "exchange": st.column_config.TextColumn("Exchange", width="small"),
                    "status": st.column_config.TextColumn("Status", width="small"),
                    "price_range": st.column_config.TextColumn("Price Range", width="medium"),
                    "has_docs": st.column_config.TextColumn("Docs", width="small")
                }
            )
            
            # Last update from scraped data
            if isinstance(self.ipo_data, list) and len(self.ipo_data) > 0:
                # Try to get scraped_at from original data
                for path in self.ipo_paths:
                    if path.exists():
                        try:
                            with open(path, 'r') as f:
                                raw_data = json.load(f)
                                if 'scraped_at' in raw_data:
                                    scraped_at = raw_data['scraped_at']
                                    st.caption(f"Last updated: {scraped_at}")
                                    break
                        except:
                            pass
            
        else:
            st.info("No IPO data found in pipeline")
            
            # Show sample data
            st.caption("Sample data:")
            sample_ipos = [
                {"company": "Example Corp", "ticker": "EXMP", "exchange": "NASDAQ", 
                 "status": "🔵 Upcoming", "price_range": "$15-17", "has_docs": "✅"},
                {"company": "Sample Inc", "ticker": "SMPL", "exchange": "NYSE", 
                 "status": "🟡 Filed", "price_range": "TBD", "has_docs": "❌"}
            ]
            df = pd.DataFrame(sample_ipos)
            st.dataframe(df, use_container_width=True, hide_index=True)

# For backward compatibility
def render_ipo_tracker():
    """Render the IPO tracker"""
    tracker = IPOTracker()
    tracker.render_ipo_tracker()

# Test standalone
if __name__ == "__main__":
    st.set_page_config(page_title="IPO Tracker Test", layout="wide")
    st.title("🚀 IPO Tracker - Minimalist")
    
    tracker = IPOTracker()
    tracker.render_ipo_tracker()
'''

# Save the updated IPO tracker
tracker_path = Path("components/ipo_tracker.py")
tracker_path.parent.mkdir(parents=True, exist_ok=True)

# Backup old tracker if exists
if tracker_path.exists():
    backup_path = tracker_path.with_suffix('.py.backup')
    shutil.copy2(tracker_path, backup_path)
    print(f"✅ Backed up old tracker to: {backup_path}")

# Write new tracker
with open(tracker_path, 'w', encoding='utf-8') as f:
    f.write(ipo_tracker_content)
print(f"✅ Updated IPO tracker: {tracker_path}")

# 2. Check if main app needs the import
main_app_path = Path("hedge_intelligence.py")

if main_app_path.exists():
    with open(main_app_path, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Check if IPOTracker is already imported
    if 'from components.ipo_tracker import' not in main_content:
        print("\n⚠️  IPOTracker not imported in main app")
        print("Add this import to hedge_intelligence.py:")
        print("from components.ipo_tracker import IPOTracker")
        print("\nAnd in your dashboard section, add:")
        print("tracker = IPOTracker()")
        print("tracker.render_ipo_tracker()")
    else:
        print("\n✅ IPOTracker already imported in main app")
        
    # Check if it's being used
    if 'IPOTracker()' not in main_content:
        print("\n📝 To use the IPO tracker in your dashboard, add:")
        print("""
# In the Dashboard section of hedge_intelligence.py:
st.markdown("---")
tracker = IPOTracker()
tracker.render_ipo_tracker()
""")
else:
    print("\n⚠️  Main app (hedge_intelligence.py) not found")

print("\n✨ Update complete!")
print("\nTest the updated tracker:")
print("streamlit run components/ipo_tracker.py")

# 3. Create a test file to verify everything works
test_content = '''import streamlit as st
from components.ipo_tracker import IPOTracker

st.set_page_config(page_title="IPO Test", layout="wide")
st.title("IPO Tracker Test")

tracker = IPOTracker()
tracker.render_ipo_tracker()
'''

with open("test_ipo_integration.py", 'w') as f:
    f.write(test_content)

print("\nOr test the integration:")
print("streamlit run test_ipo_integration.py")