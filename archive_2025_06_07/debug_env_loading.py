#!/usr/bin/env python3
"""
Debug environment variable loading
Date: 2025-06-05 14:31:58 UTC
Author: thorrobber22
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("🔍 Debugging Environment Variable Loading")
print("="*60)

# Check current working directory
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[0]}")

# Check if .env exists
env_path = Path('.env')
print(f"\n.env file exists: {env_path.exists()}")
print(f".env absolute path: {env_path.absolute()}")

# Load .env with verbose output
print("\n📋 Loading .env file...")
load_dotenv(env_path, verbose=True, override=True)

# Check what's actually loaded
print("\n🔑 Environment Variables:")
openai_key = os.getenv("OPENAI_API_KEY")
print(f"OPENAI_API_KEY from os.getenv(): {openai_key[:20] if openai_key else 'NOT FOUND'}...")

# Also check os.environ directly
print(f"\nOPENAI_API_KEY from os.environ: {os.environ.get('OPENAI_API_KEY', 'NOT FOUND')[:20]}...")

# Try manual loading
print("\n📄 Manual .env file check:")
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip().startswith('OPENAI_API_KEY='):
                print(f"Found in file: {line.strip()[:40]}...")
                break

# Check if there's another .env file somewhere
print("\n🔍 Searching for other .env files:")
for root, dirs, files in os.walk('.'):
    for file in files:
        if file == '.env':
            full_path = os.path.join(root, file)
            print(f"Found: {full_path}")

# Import test
print("\n🧪 Testing in vector_store context:")
try:
    # Ensure .env is loaded before importing
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    # Now check
    key = os.getenv("OPENAI_API_KEY")
    print(f"Key after fresh load: {key[:20] if key else 'NOT FOUND'}...")
except Exception as e:
    print(f"Error: {e}")