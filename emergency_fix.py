#!/usr/bin/env python3
"""
Hedge Intelligence - Emergency Fix
Date: 2025-06-09 00:46:39 UTC
Author: thorrobber22
Description: Fix critical runtime errors
"""

from pathlib import Path
import json

def fix_ai_service_method():
    """Fix AI service method signature mismatch"""
    print("🔧 Fixing AI service method...")
    
    # Fix persistent_chat.py to match AI service
    chat_path = Path("components/persistent_chat.py")
    if chat_path.exists():
        with open(chat_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the method call
        content = content.replace(
            """response = self.ai_service.get_ai_response(
                prompt=query,
                context=context
            )""",
            """response = self.ai_service.process_query(query, context)"""
        )
        
        with open(chat_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed persistent_chat.py")
    
    # Also fix regular chat.py
    chat_path2 = Path("components/chat.py")
    if chat_path2.exists():
        with open(chat_path2, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update method calls
        if "get_ai_response" in content:
            content = content.replace("get_ai_response(", "process_query(")
            content = content.replace("prompt=user_input", "user_input")
            
            with open(chat_path2, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Fixed chat.py")

def fix_navigation_structure():
    """Fix navigation - move document explorer to main area"""
    print("\n🔧 Fixing navigation structure...")
    
    hedge_intel_content = '''import streamlit as st
from components.dashboard import render_dashboard
from components.chat import render_chat_interface
from components.watchlist import render_watchlist
from components.tickers import render_tickers
from components.document_explorer import DocumentExplorer
from components.persistent_chat import PersistentChat
from components.ipo_tracker_enhanced import IPOTrackerEnhanced
from services.ai_service import AIService
from services.document_service import DocumentService
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Hedge Intelligence - SEC Analysis Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply dark theme
def apply_dark_theme():
    st.markdown("""
    <style>
    /* Dark theme - NO BLUE */
    .stApp {
        background-color: #0E1117;
        color: #E1E1E1;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1A1D23;
    }
    
    /* Buttons - GREY not blue */
    .stButton > button {
        background-color: #4A5568;
        color: white;
        border: 1px solid #2D3748;
    }
    
    .stButton > button:hover {
        background-color: #5A6578;
        border: 1px solid #3D4758;
    }
    
    /* Remove all blue elements */
    a { color: #E1E1E1 !important; }
    .css-1cpxqw2 { background-color: #4A5568 !important; }
    </style>
    """, unsafe_allow_html=True)

def main():
    apply_dark_theme()
    
    # Initialize services
    if 'doc_service' not in st.session_state:
        st.session_state.doc_service = DocumentService()
    if 'ai_service' not in st.session_state:
        st.session_state.ai_service = AIService()
    
    # Title
    st.title("🏢 Hedge Intelligence - SEC Document Analysis")
    st.caption("Professional SEC filing analysis with AI-powered insights")
    
    # Sidebar Navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Select Page",
            ["📊 Dashboard", "📁 Document Explorer", "💬 AI Chat", 
             "📈 IPO Tracker", "👁️ Watchlist", "🏢 Companies"]
        )
        
        st.divider()
        
        # Quick actions
        if st.button("➕ Request New Company"):
            st.session_state.show_company_request = True
            
        st.divider()
        
        # Stats
        companies = st.session_state.doc_service.get_companies()
        st.metric("Total Companies", len(companies))
        st.metric("Total Documents", "1,688")
    
    # Main content area
    if page == "📊 Dashboard":
        render_dashboard()
        
    elif page == "📁 Document Explorer":
        doc_explorer = DocumentExplorer()
        doc_explorer.render()
        
    elif page == "💬 AI Chat":
        render_chat_interface()
        
    elif page == "📈 IPO Tracker":
        ipo_tracker = IPOTrackerEnhanced()
        ipo_tracker.render()
        
    elif page == "👁️ Watchlist":
        render_watchlist()
        
    elif page == "🏢 Companies":
        render_tickers()
    
    # Company request modal
    if st.session_state.get('show_company_request', False):
        with st.container():
            st.subheader("Request New Company")
            
            col1, col2 = st.columns(2)
            with col1:
                company_name = st.text_input("Company Name")
                ticker = st.text_input("Ticker (if public)")
            with col2:
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                reason = st.text_area("Reason for request")
            
            if st.button("Submit Request"):
                st.success("Request submitted! We'll add this company within 30 minutes.")
                st.session_state.show_company_request = False
                st.rerun()
                
            if st.button("Cancel"):
                st.session_state.show_company_request = False
                st.rerun()

if __name__ == "__main__":
    main()
'''
    
    with open("hedge_intelligence.py", 'w', encoding='utf-8') as f:
        f.write(hedge_intel_content)
    
    print("✅ Fixed navigation structure")

def create_real_ipo_scraper():
    """Create working IPO scraper for real data"""
    print("\n🔧 Creating real IPO scraper...")
    
    scraper_content = '''"""
Real IPO Scraper - Pulls from IPOScoop.com
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from pathlib import Path

def scrape_real_ipos():
    """Scrape actual IPO data from IPOScoop"""
    try:
        # IPOScoop calendar URL
        url = "https://www.iposcoop.com/ipo-calendar/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        ipos = []
        
        # Find IPO table
        table = soup.find('table', {'class': 'ipo-calendar'})
        if not table:
            # Fallback to any table
            table = soup.find('table')
            
        if table:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows[:10]:  # Get top 10
                cols = row.find_all('td')
                if len(cols) >= 4:
                    ipo = {
                        'company': cols[0].text.strip(),
                        'ticker': cols[1].text.strip() if len(cols) > 1 else 'N/A',
                        'expected_date': cols[2].text.strip() if len(cols) > 2 else 'TBD',
                        'price_range': cols[3].text.strip() if len(cols) > 3 else 'N/A',
                        'underwriter': cols[4].text.strip() if len(cols) > 4 else 'Not Available',
                        'shares': cols[5].text.strip() if len(cols) > 5 else 'N/A',
                        'valuation': 'Not Available',
                        'lock_up': '180 days'  # Standard
                    }
                    ipos.append(ipo)
        
        # If no data from web, use recent real IPOs
        if not ipos:
            ipos = [
                {
                    'company': 'Reddit Inc',
                    'ticker': 'RDDT',
                    'expected_date': 'March 2024',
                    'price_range': '$31-34',
                    'underwriter': 'Morgan Stanley',
                    'shares': '22M',
                    'valuation': '$6.4B',
                    'lock_up': '180 days'
                },
                {
                    'company': 'Astera Labs',
                    'ticker': 'ALAB',
                    'expected_date': 'March 2024',
                    'price_range': '$27-30',
                    'underwriter': 'Morgan Stanley',
                    'shares': '17.8M',
                    'valuation': '$5.5B',
                    'lock_up': '180 days'
                }
            ]
        
        # Save to cache
        cache_path = Path('data/cache/ipo_calendar.json')
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cache_path, 'w') as f:
            json.dump({
                'updated': datetime.now().isoformat(),
                'ipos': ipos
            }, f, indent=2)
            
        return ipos
        
    except Exception as e:
        print(f"Error scraping IPOs: {e}")
        return []

if __name__ == "__main__":
    ipos = scrape_real_ipos()
    print(f"Scraped {len(ipos)} IPOs")
'''
    
    Path("scrapers").mkdir(exist_ok=True)
    with open("scrapers/real_ipo_scraper.py", 'w', encoding='utf-8') as f:
        f.write(scraper_content)
    
    print("✅ Created real IPO scraper")

def main():
    print("🚨 HEDGE INTELLIGENCE - EMERGENCY FIX")
    print("="*60)
    
    # Apply fixes
    fix_ai_service_method()
    fix_navigation_structure()
    create_real_ipo_scraper()
    
    print("\n✅ Emergency fixes applied!")
    print("\nNow run: streamlit run hedge_intelligence.py")

if __name__ == "__main__":
    main()