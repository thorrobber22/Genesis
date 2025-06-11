#!/usr/bin/env python3
"""
Fix API key naming in code
Date: 2025-06-05 14:18:15 UTC
Author: thorrobber22
"""

import os
from pathlib import Path

print("🔧 Fixing API key references in code...")

# Files to update
files_to_update = [
    "core/document_processor.py",
    "check_api_keys.py"
]

# Also check if vector_store.py exists
if Path("core/vector_store.py").exists():
    files_to_update.append("core/vector_store.py")

replacements = {
    'os.getenv("GOOGLE_API_KEY")': 'os.getenv("GEMINI_API_KEY")',
    'GOOGLE_API_KEY': 'GEMINI_API_KEY',  # For error messages and checks
}

for file_path in files_to_update:
    if Path(file_path).exists():
        print(f"\n📄 Updating {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply replacements
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                print(f"  ✓ Replaced '{old}' with '{new}'")
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ File updated")
        else:
            print(f"  ℹ️  No changes needed")
    else:
        print(f"\n⚠️  File not found: {file_path}")

print("\n✅ Done! API key references updated.")