#!/usr/bin/env python3
"""
Examine the current navigation structure before making changes
"""

from pathlib import Path
import re

def examine_navigation():
    """Look at how navigation is currently implemented"""
    
    main_app = Path("hedge_intelligence.py")
    
    with open(main_app, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("CURRENT NAVIGATION ANALYSIS")
    print("="*60)
    
    # Find sidebar implementation
    sidebar_match = re.search(r'with st\.sidebar:(.*?)(?=\n(?:def|class|if|with|$))', content, re.DOTALL)
    if sidebar_match:
        print("\nSIDEBAR IMPLEMENTATION:")
        print("-"*40)
        sidebar_code = sidebar_match.group(0)
        # Show first 500 chars
        print(sidebar_code[:500] + "..." if len(sidebar_code) > 500 else sidebar_code)
    
    # Find navigation variable
    nav_patterns = [
        r'selected_page\s*=\s*st\.\w+\((.*?)\)',
        r'page\s*=\s*st\.\w+\((.*?)\)',
        r'current_page\s*=\s*st\.\w+\((.*?)\)',
        r'nav_selection\s*=\s*st\.\w+\((.*?)\)'
    ]
    
    print("\n\nNAVIGATION VARIABLE:")
    print("-"*40)
    for pattern in nav_patterns:
        nav_match = re.search(pattern, content, re.DOTALL)
        if nav_match:
            print(f"Found: {nav_match.group(0)[:100]}")
            break
    
    # Find routing logic
    routing_patterns = [
        r'if\s+selected_page\s*==',
        r'if\s+page\s*==',
        r'if\s+current_page\s*==',
        r'if\s+nav_selection\s*=='
    ]
    
    print("\n\nROUTING LOGIC:")
    print("-"*40)
    for pattern in routing_patterns:
        matches = re.findall(pattern + r'.*?:.*?(?=\n(?:if|elif|else|def|class|$))', content, re.DOTALL)
        if matches:
            for match in matches[:3]:  # Show first 3
                print(f"- {match.strip()[:80]}...")
            break
    
    # Find what pages are available
    print("\n\nAVAILABLE PAGES:")
    print("-"*40)
    page_options = re.findall(r'["\'](Dashboard|Document Explorer|IPO Tracker|Watchlist|Search|Company Management|Chat History)["\']', content)
    unique_pages = list(dict.fromkeys(page_options))  # Remove duplicates while preserving order
    for page in unique_pages:
        print(f"  - {page}")
    
    return content

def find_insertion_points(content):
    """Find where to add missing functionality"""
    
    print("\n\nINSERTION POINTS:")
    print("="*60)
    
    # Find where to add missing render functions
    last_function = None
    for match in re.finditer(r'def\s+(\w+)\s*\(', content):
        last_function = match
    
    if last_function:
        print(f"Last function ends at position: {last_function.end()}")
        print(f"Can add new functions after: {last_function.group(1)}")
    
    # Find main() function
    main_match = re.search(r'def main\(\):', content)
    if main_match:
        print(f"\nmain() function found at position: {main_match.start()}")

if __name__ == "__main__":
    content = examine_navigation()
    find_insertion_points(content)