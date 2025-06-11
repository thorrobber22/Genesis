#!/usr/bin/env python3
"""
Move admin.py to correct location
Date: 2025-06-05 13:33:22 UTC
Author: thorrobber22
"""

import shutil
from pathlib import Path

# Check current structure
admin_dir = Path("admin")
admin_py_in_dir = admin_dir / "admin.py"
admin_py_root = Path("admin.py")

if admin_py_in_dir.exists() and not admin_py_root.exists():
    print("Moving admin/admin.py to root directory...")
    shutil.copy2(admin_py_in_dir, admin_py_root)
    print("✓ Moved admin.py to root")
    
    # Also check if we need the updated admin.py content
    print("\nChecking if admin.py needs updating...")
    with open(admin_py_root, 'r') as f:
        content = f.read()
        if "load_ipo_calendar" not in content:
            print("⚠ admin.py needs to be updated with new content")
            print("Run: python update_admin.py")
else:
    print("admin.py already in correct location or not found")