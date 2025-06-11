#!/usr/bin/env python3
"""
Create a simple test script
Date: 2025-06-05 14:31:58 UTC
Author: thorrobber22
"""

test_content = '''#!/usr/bin/env python3
"""Test OpenAI API key directly"""

from dotenv import load_dotenv
import os
import openai

# Load .env file
load_dotenv(override=True)

# Get key
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key: {api_key[:20]}...{api_key[-4:] if api_key else 'NOT FOUND'}")

if api_key:
    try:
        # Test with OpenAI
        client = openai.OpenAI(api_key=api_key)
        models = client.models.list()
        print("✓ OpenAI API key is valid!")
    except Exception as e:
        print(f"✗ OpenAI API error: {e}")
else:
    print("✗ No API key found!")
'''

with open('test_openai_direct.py', 'w') as f:
    f.write(test_content)

print("Created test_openai_direct.py")
print("Run: python test_openai_direct.py")