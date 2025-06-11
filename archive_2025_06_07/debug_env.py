#!/usr/bin/env python3
"""
Debug environment variables
Date: 2025-06-05 14:16:30 UTC
Author: thorrobber22
"""

import os
from pathlib import Path
from dotenv import load_dotenv

print("🔍 Debugging Environment Variables")
print("="*50)

# Check .env file
env_path = Path('.env')
if env_path.exists():
    print(f"✓ Found .env file at: {env_path.absolute()}")
    
    # Read raw content
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    print(f"\n📄 .env file has {len(lines)} lines")
    
    # Check for Google API key variations
    google_variations = ['GOOGLE_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_GEMINI_API_KEY']
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # Check each variation
            for var in google_variations:
                if line.startswith(f'{var}='):
                    key_name = line.split('=')[0]
                    key_value = line.split('=', 1)[1] if '=' in line else ''
                    print(f"\n Found: {key_name}={key_value[:10]}...({len(key_value)} chars)")
    
    # Load with dotenv
    load_dotenv(env_path, override=True)
    
    print("\n🔑 After loading with dotenv:")
    for var in google_variations:
        value = os.getenv(var)
        if value:
            print(f"  {var}: {value[:10]}...({len(value)} chars)")
        else:
            print(f"  {var}: NOT SET")
    
    # Also check what OpenAI key looks like
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"\n  OPENAI_API_KEY: {openai_key[:10]}...({len(openai_key)} chars)")
        
else:
    print("✗ No .env file found!")

# Show all environment variables starting with GOOGLE or GEMINI
print("\n🌍 All GOOGLE/GEMINI environment variables:")
for key, value in os.environ.items():
    if 'GOOGLE' in key or 'GEMINI' in key:
        print(f"  {key}: {value[:20]}..." if len(value) > 20 else f"  {key}: {value}")