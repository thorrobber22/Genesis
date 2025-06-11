#!/usr/bin/env python3
"""
Check how navigation was implemented after our changes
"""

from pathlib import Path
import re

def check_current_navigation():
    """Examine the current navigation setup"""
    
    main_app = Path("hedge_intelligence.py")
    
    with open(main_app, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("NAVIGATION IMPLEMENTATION CHECK")
    print("="*80)
    
    # Check sidebar navigation
    print("\n1. SIDEBAR NAVIGATION:")
    print("-"*40)
    sidebar_section = re.search(r'with st\.sidebar:(.*?)(?=\n\s{0,4}\w)', content, re.DOTALL)
    if sidebar_section:
        print(sidebar_section.group(0)[:500])
    
    # Check main area routing
    print("\n\n2. MAIN AREA ROUTING:")
    print("-"*40)
    main_area = re.search(r'# Main area(.*?)(?=\n\s{0,4}# |\Z)', content, re.DOTALL)
    if main_area:
        print(main_area.group(0)[:500])
    
    # Check if new functions were added
    print("\n\n3. NEW RENDER FUNCTIONS:")
    print("-"*40)
    new_funcs = ['render_ipo_tracker', 'render_search', 'render_watchlist', 'render_company_management']
    for func in new_funcs:
        if f'def {func}' in content:
            print(f"✅ {func} - FOUND")
        else:
            print(f"❌ {func} - MISSING")
    
    # Check session state usage
    print("\n\n4. NAVIGATION STATE:")
    print("-"*40)
    nav_state = re.search(r'main_navigation.*?=.*?st\.selectbox\((.*?)\)', content, re.DOTALL)
    if nav_state:
        print(f"Navigation uses: main_navigation")
        print(nav_state.group(0)[:200])

def check_pending_issues():
    """Check for pending work"""
    print("\n\n5. PENDING WORK:")
    print("-"*40)
    
    # Check company requests
    import json
    requests_file = Path("data/company_requests.json")
    if requests_file.exists():
        with open(requests_file, 'r') as f:
            requests = json.load(f)
        print(f"\nPending company requests: {len(requests)}")
        for req in requests:
            print(f"  - {req.get('ticker', 'Unknown')} ({req.get('status', 'pending')})")
    
    # Check IPO data
    ipo_file = Path("data/ipo_calendar.json")
    if ipo_file.exists():
        with open(ipo_file, 'r') as f:
            ipo_data = json.load(f)
        if isinstance(ipo_data, list):
            fake_companies = ["Stripe", "SpaceX", "Databricks", "Canva", "Instacart"]
            real_ipos = [ipo for ipo in ipo_data if ipo.get('company') not in fake_companies]
            print(f"\nIPO Calendar:")
            print(f"  - Total entries: {len(ipo_data)}")
            print(f"  - Real IPOs: {len(real_ipos)}")
            print(f"  - Fake entries to remove: {len(ipo_data) - len(real_ipos)}")

if __name__ == "__main__":
    check_current_navigation()
    check_pending_issues()