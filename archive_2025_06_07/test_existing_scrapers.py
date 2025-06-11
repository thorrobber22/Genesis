#!/usr/bin/env python3
"""
Test existing IPO scrapers
Date: 2025-06-06 13:21:27 UTC
Author: thorrobber22
"""

import sys
from pathlib import Path

print("Testing existing IPO scrapers...")
print("-" * 50)

# Test 1: Import and test ipo_scraper.py
try:
    from scrapers.ipo_scraper import IPOScraper
    print("✓ Successfully imported IPOScraper")
    
    # Test instantiation
    scraper = IPOScraper()
    print("✓ Created IPOScraper instance")
    
    # Test scraping
    print("\nTesting get_ipo_calendar()...")
    result = scraper.get_ipo_calendar()
    
    if result:
        print(f"✓ Got IPO data: {type(result)}")
        if isinstance(result, dict):
            print(f"  Keys: {list(result.keys())}")
            if 'upcoming' in result:
                print(f"  Upcoming IPOs: {len(result['upcoming'])}")
                # Show first IPO
                if result['upcoming']:
                    first_ipo = result['upcoming'][0]
                    print(f"  First IPO: {first_ipo.get('symbol', 'N/A')} - {first_ipo.get('company', 'N/A')}")
    else:
        print("✗ No data returned from scraper")
        
except Exception as e:
    print(f"✗ Error with ipo_scraper: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "-" * 50)

# Test 2: Try the fixed version
try:
    from scrapers.ipo_scraper_fixed import IPOScraper as FixedScraper
    print("✓ Found ipo_scraper_fixed.py")
    
    scraper2 = FixedScraper()
    print("✓ Created FixedScraper instance")
    
    # Check if it has different methods
    if hasattr(scraper2, 'scrape_calendar'):
        print("  Has scrape_calendar() method")
        result2 = scraper2.scrape_calendar()
        if result2:
            print(f"  ✓ Got {len(result2)} IPOs")
            if result2:
                print(f"  First: {result2[0].get('ticker', 'N/A')} - {result2[0].get('company', 'N/A')}")
    
except Exception as e:
    print(f"✗ Error with ipo_scraper_fixed: {e}")

print("\n" + "-" * 50)

# Test 3: Check admin_streamlined structure
print("\nChecking admin_streamlined.py structure...")

admin_path = Path("admin_streamlined.py")
with open(admin_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if function is inside a class or another function
lines = content.split('\n')
in_class = False
in_function = False
current_indent = 0

for i, line in enumerate(lines):
    if line.strip().startswith('class '):
        in_class = True
        current_indent = len(line) - len(line.lstrip())
        
    if line.strip().startswith('def ') and not line.strip().startswith('def scrape_ipos'):
        if len(line) - len(line.lstrip()) == 0:
            in_function = False
        else:
            in_function = True
            current_indent = len(line) - len(line.lstrip())
    
    if "def scrape_ipos():" in line:
        line_num = i + 1
        indent = len(line) - len(line.lstrip())
        print(f"Found scrape_ipos at line {line_num} with indent {indent}")
        
        if in_class:
            print("  ⚠️ Inside a class!")
        if in_function:
            print("  ⚠️ Inside another function!")
        if indent > 0:
            print(f"  ⚠️ Indented {indent} spaces!")
            
        # Check what's around it
        print(f"\nContext around line {line_num}:")
        for j in range(max(0, i-5), min(len(lines), i+10)):
            marker = ">>>" if j == i else "   "
            print(f"{marker} {j+1}: {lines[j]}")
        break

# Check where it's called
print("\n" + "-" * 50)
print("Where scrape_ipos is called:")

for i, line in enumerate(lines):
    if "scrape_ipos()" in line and "def scrape_ipos" not in line:
        print(f"Line {i+1}: {line.strip()}")
        # Is it inside the main code?
        indent = len(line) - len(line.lstrip())
        print(f"  Indent: {indent}")