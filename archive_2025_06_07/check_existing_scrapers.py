#!/usr/bin/env python3
"""
Check for existing IPO scrapers
Date: 2025-06-06 12:49:06 UTC
Author: thorrobber22
"""

from pathlib import Path
import os

print("Checking for existing IPO scrapers...")
print("-" * 50)

# Check common locations
possible_files = [
    "ipo_scraper.py",
    "core/ipo_scraper.py",
    "scrapers/ipo_scraper.py",
    "ipo_monitor.py",
    "core/ipo_monitor.py",
    "edgar_scraper.py",
    "core/edgar_scraper.py"
]

found_scrapers = []

# Search in current directory and subdirectories
for root, dirs, files in os.walk("."):
    # Skip venv and __pycache__
    if "venv" in root or "__pycache__" in root:
        continue
    
    for file in files:
        if "ipo" in file.lower() or "scraper" in file.lower() or "edgar" in file.lower():
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                found_scrapers.append(full_path)

if found_scrapers:
    print("Found existing scrapers:")
    for scraper in found_scrapers:
        print(f"  ✓ {scraper}")
        
        # Check if it has IPO-related functions
        try:
            with open(scraper, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for IPO-related functions
            if any(term in content.lower() for term in ['iposcoop', 'ipo', 'upcoming', 'edgar']):
                print(f"    → Contains IPO-related code")
                
                # Extract function names
                import re
                functions = re.findall(r'def\s+(\w+)\s*\(', content)
                if functions:
                    print(f"    → Functions: {', '.join(functions[:5])}")
        except:
            pass
        
        print()
else:
    print("No existing IPO scrapers found")

# Check if we have any monitoring scripts
print("\nChecking for monitoring scripts...")
monitor_files = []

for root, dirs, files in os.walk("."):
    if "venv" in root or "__pycache__" in root:
        continue
    
    for file in files:
        if "monitor" in file.lower() and file.endswith(".py"):
            monitor_files.append(os.path.join(root, file))

if monitor_files:
    print("Found monitoring scripts:")
    for monitor in monitor_files:
        print(f"  ✓ {monitor}")