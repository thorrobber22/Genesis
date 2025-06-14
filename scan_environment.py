"""
scan_py_structure.py - Scan Python files and folder structure
Date: 2025-06-13 21:48:01 UTC
User: thorrobber22
"""

import os
from pathlib import Path
from datetime import datetime

print("🐍 HEDGE INTELLIGENCE - PYTHON STRUCTURE SCANNER")
print("="*60)
print(f"User: thorrobber22")
print(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
print(f"Directory: {Path.cwd()}")
print("="*60)

# Track all Python files
py_files = []
folder_structure = {}

# Ignore patterns
ignore = {'venv', '__pycache__', '.git', 'temp_genesis', 'env'}

def scan_directory(path='.', prefix=''):
    """Recursively scan for .py files and folders"""
    items = []
    
    try:
        for item in sorted(os.listdir(path)):
            if item.startswith('.') and item != '.gitignore':
                continue
                
            item_path = os.path.join(path, item)
            
            if os.path.isdir(item_path):
                if item not in ignore:
                    print(f"{prefix}📁 {item}/")
                    items.append(f"DIR: {item_path}")
                    sub_items = scan_directory(item_path, prefix + "    ")
                    items.extend(sub_items)
            elif item.endswith('.py'):
                size = os.path.getsize(item_path)
                print(f"{prefix}📄 {item} ({size:,} bytes)")
                items.append(f"PY: {item_path}")
                py_files.append(item_path)
    except PermissionError:
        pass
    
    return items

print("\n📂 DIRECTORY STRUCTURE (Folders & .py files only):")
print("-"*60)
all_items = scan_directory()

print(f"\n📊 SUMMARY:")
print("-"*60)
print(f"Total Python files: {len(py_files)}")
print(f"Total folders scanned: {len([i for i in all_items if i.startswith('DIR:')])}")

print(f"\n📋 PYTHON FILES LIST:")
print("-"*60)
for idx, py_file in enumerate(sorted(py_files), 1):
    print(f"{idx:2d}. {py_file}")

print(f"\n🔍 EXPECTED vs FOUND:")
print("-"*60)

expected_files = [
    "app.py",
    "services/ai_service.py",
    "services/data_service.py",
    "services/sec_service.py",
    "components/chat.py",
    "components/companies.py",
    "components/financial_analysis.py",
    "components/ipo_calendar.py",
    "components/metrics.py",
    "components/watchlist.py",
    "scrapers/sec_scraper.py"
]

for expected in expected_files:
    found = any(expected.replace('/', os.sep) in py for py in py_files)
    status = "✅" if found else "❌"
    print(f"{status} {expected}")

print("\n✅ SCAN COMPLETE!")