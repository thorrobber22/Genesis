#!/usr/bin/env python3
"""
Check if ChromaDB is caching the wrong API key
Date: 2025-06-05 14:34:15 UTC
Author: thorrobber22
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv(override=True)

print("Checking ChromaDB and API keys...")
print("="*60)

# Check API key
api_key = os.getenv("OPENAI_API_KEY")
print(f"Current OPENAI_API_KEY: {api_key[:20]}...{api_key[-4:]}")

# Check if ChromaDB has cached embeddings
vector_db_dir = Path("data/vector_db")
if vector_db_dir.exists():
    print(f"\nFound vector DB at: {vector_db_dir}")
    
    # List contents
    contents = list(vector_db_dir.iterdir())
    print(f"Contents: {[c.name for c in contents]}")
    
    # Option to clear
    response = input("\nClear ChromaDB cache and start fresh? (y/n): ")
    if response.lower() == 'y':
        shutil.rmtree(vector_db_dir)
        print("Cleared ChromaDB cache")
        vector_db_dir.mkdir(parents=True)
        print("Created fresh vector_db directory")
else:
    print("\nNo vector DB found (this is OK)")

print("\nNow the vector store should use the correct API key.")