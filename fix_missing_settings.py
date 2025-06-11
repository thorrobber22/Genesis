#!/usr/bin/env python3
"""
Fix Missing Settings Component
Date: 2025-06-07 22:23:22 UTC
Author: thorrobber22
Description: Quick fix to remove settings import causing error
"""

import re
from pathlib import Path

def fix_settings_import():
    """Remove settings import from hedge_intelligence.py"""
    print("🔧 Fixing missing settings import...")
    
    main_file = Path("hedge_intelligence.py")
    
    if not main_file.exists():
        print("❌ hedge_intelligence.py not found!")
        return False
    
    # Read current content
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup original
    backup_file = main_file.with_suffix('.py.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup created: {backup_file}")
    
    # Remove settings imports
    original_content = content
    
    # Remove import lines
    content = re.sub(r'from components\.settings import.*\n', '', content)
    content = re.sub(r'import components\.settings.*\n', '', content)
    
    # Remove any render_settings() calls
    content = re.sub(r'render_settings\(\).*\n', '', content)
    
    # Remove settings from any navigation/menu
    content = re.sub(r'.*["\']Settings["\'].*\n', '', content)
    content = re.sub(r'.*["\']⚙️ Settings["\'].*\n', '', content)
    
    # Remove settings page logic
    content = re.sub(r'if selected == ["\']Settings["\']:.*\n.*render_settings\(\).*\n', '', content)
    content = re.sub(r'elif selected == ["\']Settings["\']:.*\n.*render_settings\(\).*\n', '', content)
    
    # Check if changes were made
    if content != original_content:
        # Write fixed content
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Fixed hedge_intelligence.py - removed settings imports")
        print("\nChanges made:")
        print("- Removed settings import")
        print("- Removed render_settings() calls")
        print("- Removed Settings from navigation")
        return True
    else:
        print("ℹ️ No settings imports found to remove")
        return False

def create_dummy_settings():
    """Alternative: Create a dummy settings file"""
    print("\n📄 Creating dummy settings component...")
    
    settings_content = '''"""
Dummy Settings Component
Created: 2025-06-07 22:23:22 UTC
Note: Settings have been removed from the analyst platform
"""

import streamlit as st

def render_settings():
    """Dummy settings function"""
    st.info("Settings have been removed from the analyst platform. All configuration is automatic.")
    
def load_settings():
    """Dummy load function"""
    return {}
    
def save_settings(settings):
    """Dummy save function"""
    pass
'''
    
    # Create components directory if needed
    Path("components").mkdir(exist_ok=True)
    
    # Write dummy file
    with open("components/settings.py", 'w', encoding='utf-8') as f:
        f.write(settings_content)
    
    print("✅ Created dummy components/settings.py")

def main():
    print("🔍 HEDGE INTELLIGENCE - Settings Fix")
    print("=" * 60)
    
    print("\nOption 1: Remove settings imports (recommended)")
    fixed = fix_settings_import()
    
    if not fixed:
        print("\nOption 2: Create dummy settings file")
        response = input("Create dummy settings.py? (y/n): ")
        if response.lower() == 'y':
            create_dummy_settings()
    
    print("\n✅ Fix complete!")
    print("\nNext steps:")
    print("1. Run: streamlit run hedge_intelligence.py")
    print("2. Or run the full refactor: python apply_refactor.py")

if __name__ == "__main__":
    main()