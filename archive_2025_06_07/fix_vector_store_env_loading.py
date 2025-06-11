#!/usr/bin/env python3
"""
Fix environment loading in vector_store.py
Date: 2025-06-05 14:31:58 UTC
Author: thorrobber22
"""

from pathlib import Path

print("🔧 Fixing environment loading in vector_store.py...")

# Read vector_store.py
vs_path = Path("core/vector_store.py")
with open(vs_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the imports section
import_section_end = 0
for i, line in enumerate(lines):
    if line.strip().startswith("# Configuration"):
        import_section_end = i
        break

# Add dotenv import and loading at the top
new_imports = [
    "# Load environment variables first\n",
    "from dotenv import load_dotenv\n",
    "load_dotenv(override=True)\n",
    "\n"
]

# Insert after the AI/ML imports
lines[import_section_end:import_section_end] = new_imports

# Write back
with open(vs_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✓ Added explicit .env loading to vector_store.py")