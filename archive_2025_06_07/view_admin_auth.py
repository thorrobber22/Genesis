#!/usr/bin/env python3
"""
View admin authentication structure
Date: 2025-06-06 12:08:12 UTC
Author: thorrobber22
"""

from pathlib import Path

admin_path = Path("admin.py")
with open(admin_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Look for authentication
print("Looking for authentication setup...")
print("-" * 50)

# Check for password/auth related code
auth_keywords = ["password", "authenticate", "login", "ADMIN_PASSWORD", "check_password"]
lines = content.split('\n')

for i, line in enumerate(lines):
    for keyword in auth_keywords:
        if keyword in line.lower():
            print(f"Line {i+1}: {line.strip()}")

print("\n" + "-" * 50)
print("Looking for session state...")

for i, line in enumerate(lines):
    if "session_state" in line:
        print(f"Line {i+1}: {line.strip()}")
        # Show next few lines for context
        for j in range(1, 3):
            if i+j < len(lines):
                print(f"Line {i+j+1}: {lines[i+j].strip()}")