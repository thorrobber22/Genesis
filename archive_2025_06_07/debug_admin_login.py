#!/usr/bin/env python3
"""
Debug admin login issue
Date: 2025-06-06 11:57:16 UTC
Author: thorrobber22
"""

from pathlib import Path
import re

print("Debugging admin.py login issue...")

# Check admin.py
admin_path = Path("admin.py")
if admin_path.exists():
    with open(admin_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for the login logic
    if "check_password" in content:
        print("✓ Found check_password function")
    
    # Look for session state
    if "st.session_state" in content:
        print("✓ Found session state usage")
    
    # Check if main content is inside authentication
    if "if check_password():" in content:
        print("✓ Main content is protected by password")
    else:
        print("✗ Main content might not be inside password check")
    
    # Look for the actual password check
    password_pattern = r'if\s+password\s*==\s*["\']([^"\']+)["\']'
    match = re.search(password_pattern, content)
    if match:
        print(f"✓ Password check found: {match.group(1)}")
    
    # Check for ADMIN_PASSWORD import
    if "ADMIN_PASSWORD" in content:
        print("✓ ADMIN_PASSWORD is referenced")
        if "from config import" in content:
            print("✓ Importing from config")
    
    print("\nChecking for common issues...")
    
    # Check indentation after login
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "check_password():" in line:
            print(f"\nFound password check at line {i+1}")
            # Check next few lines
            for j in range(1, 5):
                if i+j < len(lines):
                    next_line = lines[i+j]
                    if next_line.strip():
                        print(f"  Line {i+j+1}: {repr(next_line[:50])}")

# Check config.py
config_path = Path("config.py")
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    if "ADMIN_PASSWORD" in config_content:
        # Extract the password
        match = re.search(r'ADMIN_PASSWORD\s*=\s*["\']([^"\']+)["\']', config_content)
        if match:
            print(f"\nConfig has ADMIN_PASSWORD: {match.group(1)}")