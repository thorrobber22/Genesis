#!/usr/bin/env python3
"""
Clean up duplicate files and organize project
"""

from pathlib import Path
import shutil
from datetime import datetime

def cleanup_services():
    """Move backup AI service files to backups folder"""
    
    services_dir = Path("services")
    backups_dir = services_dir / "backups"
    backups_dir.mkdir(exist_ok=True)
    
    print("CLEANING UP SERVICES")
    print("-"*40)
    
    # Files to move to backup
    backup_files = [
        "ai_service_backup.py",
        "ai_service_before_chat_engine.py", 
        "ai_service_broken.py",
        "ai_service_pre_openai_fix.py"
    ]
    
    for filename in backup_files:
        filepath = services_dir / filename
        if filepath.exists():
            backup_path = backups_dir / filename
            shutil.move(str(filepath), str(backup_path))
            print(f"✅ Moved {filename} to backups/")

def verify_navigation():
    """Verify navigation is working"""
    print("\n\nVERIFYING NAVIGATION")
    print("-"*40)
    
    main_app = Path("hedge_intelligence.py")
    with open(main_app, 'r') as f:
        content = f.read()
    
    # Check for navigation elements
    checks = {
        "Sidebar exists": "with st.sidebar:" in content,
        "Navigation selectbox": "main_navigation" in content,
        "Page routing": 'if page == "Dashboard"' in content,
        "IPO Tracker function": "def render_ipo_tracker" in content,
        "Search function": "def render_search" in content,
        "Watchlist function": "def render_watchlist" in content,
        "Company Management": "def render_company_management" in content
    }
    
    all_good = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
        if not result:
            all_good = False
    
    return all_good

def create_missing_data_files():
    """Create any missing data files"""
    print("\n\nCREATING MISSING DATA FILES")
    print("-"*40)
    
    data_files = {
        "data/watchlist.json": [],
        "data/ipo_calendar.json": []
    }
    
    for filepath, default_content in data_files.items():
        path = Path(filepath)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            import json
            with open(path, 'w') as f:
                json.dump(default_content, f, indent=2)
            print(f"✅ Created {filepath}")
        else:
            print(f"✓ {filepath} already exists")

if __name__ == "__main__":
    print("HEDGE INTELLIGENCE - PROJECT CLEANUP")
    print("="*80)
    
    # 1. Clean up services
    cleanup_services()
    
    # 2. Verify navigation
    nav_ok = verify_navigation()
    
    # 3. Create missing files
    create_missing_data_files()
    
    print("\n" + "="*80)
    if nav_ok:
        print("✅ PROJECT READY - Navigation is properly set up!")
        print("\nNEXT STEPS:")
        print("1. Run: streamlit run hedge_intelligence.py")
        print("2. Test each navigation page")
        print("3. Fix any issues found")
    else:
        print("❌ ISSUES FOUND - Check navigation implementation")