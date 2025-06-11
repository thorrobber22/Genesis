#!/usr/bin/env python3
# fix_test_production_functionality.py
"""
Fix the Unicode encoding error in test script
"""

from pathlib import Path

def fix_unicode_error():
    """Fix the Unicode encoding issue"""
    
    # Read the file
    with open("test_production_functionality.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the file write to use UTF-8 encoding
    content = content.replace(
        'with open("production_checklist.md", "w") as f:',
        'with open("production_checklist.md", "w", encoding="utf-8") as f:'
    )
    
    content = content.replace(
        'with open("production_test_results.json", "w") as f:',
        'with open("production_test_results.json", "w", encoding="utf-8") as f:'
    )
    
    # Save fixed version
    with open("test_production_functionality.py", 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed Unicode encoding error")

if __name__ == "__main__":
    fix_unicode_error()