#!/usr/bin/env python3
"""
Fix ChromaDB where clause issue
Date: 2025-06-05 14:27:43 UTC
Author: thorrobber22
"""

from pathlib import Path

print("🔧 Fixing ChromaDB where clause syntax...")

# Read vector_store.py
vs_path = Path("core/vector_store.py")
with open(vs_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the get_document_chunks method
old_pattern = '''where_clause = {
            "ticker": ticker,
            "document_type": doc_type
        }'''

new_pattern = '''where_clause = {
            "$and": [
                {"ticker": {"$eq": ticker}},
                {"document_type": {"$eq": doc_type}}
            ]
        }'''

content = content.replace(old_pattern, new_pattern)

# Fix delete_document method too
content = content.replace(
    'where_clause = {\n            "ticker": ticker,\n            "document_type": doc_type\n        }',
    'where_clause = {\n            "$and": [\n                {"ticker": {"$eq": ticker}},\n                {"document_type": {"$eq": doc_type}}\n            ]\n        }'
)

# Write back
with open(vs_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed ChromaDB where clause syntax")
print("  Now using proper operator syntax for multiple conditions")