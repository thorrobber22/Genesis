#!/usr/bin/env python3
"""
View structure of admin_streamlined.py to fix scrape_ipos
Date: 2025-06-06 13:03:28 UTC
Author: thorrobber22
"""

from pathlib import Path

admin_path = Path("admin_streamlined.py")
with open(admin_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Looking for scrape_ipos usage and definition...")
print("-" * 50)

# Find where scrape_ipos is called
for i, line in enumerate(lines):
    if "scrape_ipos" in line:
        print(f"Line {i+1}: {line.strip()}")
        # Show context
        for j in range(max(0, i-2), min(len(lines), i+3)):
            if j != i:
                print(f"  {j+1}: {lines[j].rstrip()}")
        print()

# Check if function is defined
function_defined = False
for i, line in enumerate(lines):
    if "def scrape_ipos" in line:
        function_defined = True
        print(f"Function defined at line {i+1}")
        break

if not function_defined:
    print("❌ Function NOT defined!")
    
    # Find where to insert it
    print("\nLooking for where to insert function...")
    for i, line in enumerate(lines):
        if "# Helper Functions" in line:
            print(f"Found helper functions section at line {i+1}")
            break