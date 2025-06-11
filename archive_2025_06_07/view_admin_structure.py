#!/usr/bin/env python3
"""
View admin.py structure to diagnose issue
Date: 2025-06-06 12:06:26 UTC
Author: thorrobber22
"""

from pathlib import Path

admin_path = Path("admin.py")
if admin_path.exists():
    with open(admin_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("First 50 lines of admin.py:")
    print("-" * 50)
    for i, line in enumerate(lines[:50]):
        print(f"{i+1:3}: {line.rstrip()}")
    
    print("\n" + "-" * 50)
    print("Looking for key structures...")
    
    # Find where main content starts
    for i, line in enumerate(lines):
        if "st.title" in line and "Admin" in line:
            print(f"\nFound admin title at line {i+1}: {line.strip()}")
            print("Next 5 lines:")
            for j in range(1, 6):
                if i+j < len(lines):
                    print(f"  {i+j+1}: {lines[i+j].rstrip()}")
            break