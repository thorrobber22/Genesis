#!/usr/bin/env python3
"""
Fix vector store import and constant issues
Date: 2025-06-05 14:22:50 UTC
Author: thorrobber22
"""

from pathlib import Path

print("🔧 Fixing vector_store.py imports and constants...")

vector_store_path = Path("core/vector_store.py")
if not vector_store_path.exists():
    print("✗ core/vector_store.py not found!")
    exit(1)

# Read the file
with open(vector_store_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the import section - ensure MAX_RESULTS is defined
import_fix = """# Import config
try:
    from config import *
    # Ensure MAX_RESULTS is defined
    if 'MAX_RESULTS' not in globals():
        MAX_RESULTS = 10
except ImportError:
    # Fallback config
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    VECTOR_DIR = DATA_DIR / "vectors"
    VECTOR_DB_DIR = DATA_DIR / "vector_db"
    
    EMBEDDING_MODEL = "text-embedding-3-small"
    COLLECTION_NAME = "ipo_documents"
    MAX_RESULTS = 10"""

# Find the import section and replace it
import re
pattern = r'# Import config.*?MAX_RESULTS = 10'
if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, import_fix, content, flags=re.DOTALL)
    print("✓ Fixed import section")
else:
    # Try a simpler fix - just add MAX_RESULTS before the class
    if "MAX_RESULTS = " not in content:
        # Add it after the imports
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('class VectorStore:'):
                insert_idx = i
                break
        
        if insert_idx > 0:
            lines.insert(insert_idx - 1, "\n# Default search results")
            lines.insert(insert_idx, "MAX_RESULTS = 10\n")
            content = '\n'.join(lines)
            print("✓ Added MAX_RESULTS constant")

# Write back
with open(vector_store_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed vector_store.py")

# Also update config.py to include these constants
config_path = Path("config.py")
if config_path.exists():
    print("\n📝 Updating config.py with vector store constants...")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    # Add vector store config if not present
    if "EMBEDDING_MODEL" not in config_content:
        vector_config = """
# Vector Store Configuration
EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "ipo_documents"
MAX_RESULTS = 10
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
"""
        config_content += vector_config
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("✓ Added vector store configuration to config.py")
    else:
        print("✓ Vector store config already in config.py")