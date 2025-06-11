#!/usr/bin/env python3
"""
Audit what we already have to avoid duplicates
"""

from pathlib import Path

def audit_hedge_intelligence():
    """Check current app structure"""
    main_app = Path("hedge_intelligence.py")
    
    if not main_app.exists():
        print("ERROR: hedge_intelligence.py not found!")
        return None
    
    with open(main_app, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check what pages/features exist
    features = {
        'sidebar': 'st.sidebar' in content,
        'navigation': 'selectbox' in content or 'radio' in content,
        'document_explorer': 'document' in content.lower() and 'explorer' in content.lower(),
        'ipo_tracker': 'ipo' in content.lower() and 'tracker' in content.lower(),
        'chat': 'chat' in content.lower(),
        'routing': 'session_state' in content and 'page' in content,
        'persistent_chat': 'persistent_chat' in content,
        'dashboard': 'dashboard' in content.lower(),
        'watchlist': 'watchlist' in content.lower(),
        'search': 'search' in content.lower() and 'st.' in content
    }
    
    print("Current App Analysis:")
    print("="*50)
    for feature, exists in features.items():
        status = "EXISTS" if exists else "MISSING"
        print(f"  {feature:<20}: {status}")
    
    # Check for existing functions
    print("\nFunction Analysis:")
    print("="*50)
    functions = [
        'render_dashboard',
        'render_document_explorer', 
        'render_ipo_tracker',
        'render_watchlist',
        'render_search',
        'render_company_management',
        'display_document_explorer',
        'display_ipo_tracker',
        'display_chat_history'
    ]
    
    for func in functions:
        if f'def {func}' in content:
            print(f"  {func:<30}: EXISTS")
        else:
            print(f"  {func:<30}: MISSING")
    
    return features

def check_existing_pages():
    """Check if we have separate page files"""
    pages_dir = Path("pages")
    
    print("\nPages Directory Check:")
    print("="*50)
    
    if pages_dir.exists():
        print("  pages/ directory EXISTS")
        for page_file in pages_dir.glob("*.py"):
            print(f"    - {page_file.name}")
    else:
        print("  pages/ directory MISSING")

if __name__ == "__main__":
    print("HEDGE INTELLIGENCE - STRUCTURE AUDIT")
    print("="*50)
    
    # Audit main app
    features = audit_hedge_intelligence()
    
    # Check pages
    check_existing_pages()
    
    print("\nRECOMMENDATION:")
    if features and not features['sidebar']:
        print("  → Need to add sidebar navigation")
    if features and not features['routing']:
        print("  → Need to add page routing logic")