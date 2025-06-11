#!/usr/bin/env python3
"""
Check API keys configuration
Date: 2025-06-05 14:09:42 UTC
Author: thorrobber22
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path)
    print("✓ Loaded .env file")
else:
    print("✗ No .env file found")

print("\n🔑 API KEY STATUS:")
print("="*50)

# Check OpenAI key (REQUIRED for vector store)
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    print(f"✓ OPENAI_API_KEY: Set ({len(openai_key)} chars)")
    print("  Used for: Vector embeddings in ChromaDB")
else:
    print("✗ OPENAI_API_KEY: NOT SET")
    print("  ⚠️  REQUIRED for vector store functionality")

# Check Google/Gemini key (REQUIRED for document validation)
google_key = os.getenv("GEMINI_API_KEY")
if google_key:
    print(f"\n✓ GEMINI_API_KEY: Set ({len(google_key)} chars)")
    print("  Used for: Document validation with Gemini")
else:
    print("\n✗ GEMINI_API_KEY: NOT SET")
    print("  ⚠️  REQUIRED for document processing validation")

# Check other optional keys
perplexity_key = os.getenv("PERPLEXITY_API_KEY")
if perplexity_key:
    print(f"\n✓ PERPLEXITY_API_KEY: Set ({len(perplexity_key)} chars)")
    print("  Used for: Real-time web searches (optional)")
else:
    print("\n○ PERPLEXITY_API_KEY: Not set (optional)")

print("\n📋 SUMMARY:")
print("="*50)

if openai_key and google_key:
    print("✅ All required API keys are configured!")
    print("\nYour system can:")
    print("  • Process documents with AI validation")
    print("  • Create vector embeddings for search")
    print("  • Perform semantic queries")
else:
    print("❌ Missing required API keys!")
    print("\nTo fix, create or update your .env file:")
    print("\n# Required keys")
    print("OPENAI_API_KEY=your-openai-api-key-here")
    print("GEMINI_API_KEY=your-gemini-api-key-here")
    print("\n# Optional keys")
    print("PERPLEXITY_API_KEY=your-perplexity-key-here")