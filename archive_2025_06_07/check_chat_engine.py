#!/usr/bin/env python3
"""
Check chat engine structure and add multi-doc support
Date: 2025-06-06 17:36:32 UTC
Author: thorrobber22
"""

from pathlib import Path

chat_file = Path("core/chat_engine.py")

if chat_file.exists():
    with open(chat_file, 'r') as f:
        content = f.read()
    
    print("📄 Analyzing chat_engine.py...")
    print("-" * 50)
    
    # Look for class definition
    if "class ChatEngine" in content:
        print("✅ Found ChatEngine class")
    else:
        print("⚠️  No ChatEngine class found")
    
    # Look for methods
    methods = []
    for line in content.split('\n'):
        if 'def ' in line and '(' in line:
            method_name = line.strip().split('def ')[1].split('(')[0]
            methods.append(method_name)
    
    print(f"\n🔧 Found {len(methods)} methods:")
    for method in methods[:10]:  # Show first 10
        print(f"   - {method}()")
    
    # Check for multi-doc support
    if "document_type" in content or "doc_type" in content:
        print("\n✅ Already has document type support")
    else:
        print("\n❌ Missing document type support")
        print("\n💡 Would you like to see the current structure?")
        
        # Show first 50 lines to understand structure
        lines = content.split('\n')
        print("\nFirst 50 lines of chat_engine.py:")
        print("-" * 50)
        for i, line in enumerate(lines[:50]):
            print(f"{i+1:3}: {line[:80]}")
else:
    print("❌ core/chat_engine.py not found!")