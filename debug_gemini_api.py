#!/usr/bin/env python3
"""
Debug Gemini API connection and test basic functionality
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Debugging Gemini Integration\n")

# Check API key
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    print(f"✅ API Key found: {api_key[:20]}...")
else:
    print("❌ API Key not found!")
    sys.exit(1)

# Test basic Gemini connection
try:
    import google.generativeai as genai
    
    # Configure with API key
    genai.configure(api_key=api_key)
    
    # List available models
    print("\n📋 Available models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name}")
    
    # Test with a simple prompt
    print("\n🧪 Testing basic generation...")
    model = genai.GenerativeModel('gemini-1.5-flash')  # Using flash for quick test
    
    response = model.generate_content("Say 'Hello, Hedge Intelligence!' if you're working.")
    print(f"✅ Response: {response.text}")
    
    # Test with gemini-1.5-pro
    print("\n🧪 Testing Gemini 1.5 Pro...")
    model_pro = genai.GenerativeModel('gemini-1.5-pro')
    
    response_pro = model_pro.generate_content("What is 2+2? Reply with just the number.")
    print(f"✅ Response: {response_pro.text}")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    
    # More detailed error info
    import traceback
    print("\n📋 Full traceback:")
    traceback.print_exc()

print("\n✅ Debug complete!")