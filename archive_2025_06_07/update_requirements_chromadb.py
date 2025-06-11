#!/usr/bin/env python3
"""
Update requirements.txt with ChromaDB
Date: 2025-06-05 14:18:15 UTC
Author: thorrobber22
"""

from pathlib import Path

print("📝 Updating requirements.txt...")

# Read current requirements
req_path = Path("requirements.txt")
if req_path.exists():
    with open(req_path, 'r') as f:
        lines = f.readlines()
else:
    lines = []

# Check if chromadb is already there
has_chromadb = any('chromadb' in line for line in lines)

if not has_chromadb:
    # Add chromadb
    lines.append("chromadb==0.4.22\n")
    
    # Sort and write back
    with open(req_path, 'w') as f:
        f.writelines(sorted(lines))
    
    print("✓ Added chromadb to requirements.txt")
else:
    print("✓ chromadb already in requirements.txt")