#!/usr/bin/env python3
"""
Investigate and fix AIService parameter issue
"""

import os
import sys
from pathlib import Path

def investigate_ai_service():
    """Deep dive into AIService to understand the issue"""
    print("🔍 INVESTIGATING AI SERVICE")
    print("="*70)
    
    ai_service_path = Path("services/ai_service.py")
    
    with open(ai_service_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find get_ai_response method
    lines = content.split('\n')
    in_method = False
    method_lines = []
    indent_level = 0
    
    for i, line in enumerate(lines):
        if 'def get_ai_response' in line:
            in_method = True
            indent_level = len(line) - len(line.lstrip())
            method_lines.append(f"Line {i+1}: {line}")
            continue
        
        if in_method:
            current_indent = len(line) - len(line.lstrip())
            if line.strip() and current_indent <= indent_level and 'def ' in line:
                break
            method_lines.append(f"Line {i+1}: {line}")
            
            # Look for specific issues
            if 'query[' in line or 'context[' in line:
                print(f"⚠️  Found dictionary access at line {i+1}: {line.strip()}")
    
    print("\n📄 get_ai_response method:")
    for line in method_lines[:20]:  # First 20 lines
        print(line)
    
    # Check how it's being called in chat.py
    check_chat_usage()

def check_chat_usage():
    """See how chat.py calls get_ai_response"""
    print("\n🔍 Checking chat.py usage...")
    
    chat_path = Path("components/chat.py")
    
    if chat_path.exists():
        with open(chat_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find calls to get_ai_response
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'get_ai_response' in line:
                print(f"\nLine {i+1}: {line.strip()}")
                # Show context
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    print(f"  {j+1}: {lines[j]}")

def create_ai_service_wrapper():
    """Create a wrapper that handles both parameter types"""
    print("\n🔧 Creating AI Service wrapper...")
    
    wrapper_content = '''#!/usr/bin/env python3
"""
AI Service Wrapper - Handles parameter compatibility
"""

from services.ai_service import AIService as OriginalAIService

class AIServiceWrapper:
    """Wrapper that handles different parameter formats"""
    
    def __init__(self):
        self.original_service = OriginalAIService()
        
    def get_ai_response(self, query_or_dict, context=None):
        """Handle both dictionary and separate parameters"""
        
        # If it's a dictionary
        if isinstance(query_or_dict, dict):
            return self.original_service.get_ai_response(query_or_dict)
        
        # If it's separate parameters
        elif isinstance(query_or_dict, str) and context is not None:
            # Convert to expected format
            params = {
                'query': query_or_dict,
                'context': context
            }
            return self.original_service.get_ai_response(params)
        
        # If just a query string
        elif isinstance(query_or_dict, str):
            params = {
                'query': query_or_dict,
                'context': ''
            }
            return self.original_service.get_ai_response(params)
        
        else:
            raise ValueError(f"Unexpected parameter type: {type(query_or_dict)}")
    
    def __getattr__(self, name):
        """Pass through other methods"""
        return getattr(self.original_service, name)

# Export wrapper as AIService
AIService = AIServiceWrapper
'''
    
    with open("services/ai_service_wrapper.py", 'w', encoding='utf-8') as f:
        f.write(wrapper_content)
    
    print("✅ Created ai_service_wrapper.py")

def patch_ai_service_directly():
    """Directly patch the AIService to handle both formats"""
    print("\n🔧 Patching AIService directly...")
    
    ai_service_path = Path("services/ai_service.py")
    
    with open(ai_service_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Backup original
    backup_path = Path("services/ai_service_backup.py")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Backed up to {backup_path}")
    
    # Find and patch get_ai_response
    lines = content.split('\n')
    patched_lines = []
    in_method = False
    method_indent = 0
    
    for i, line in enumerate(lines):
        if 'def get_ai_response' in line and 'self' in line:
            in_method = True
            method_indent = len(line) - len(line.lstrip())
            
            # Replace the method signature
            patched_lines.append(f"{' ' * method_indent}def get_ai_response(self, query, context=None):")
            patched_lines.append(f"{' ' * (method_indent + 4)}\"\"\"Get AI response with flexible parameters\"\"\"")
            patched_lines.append(f"{' ' * (method_indent + 4)}# Handle different parameter formats")
            patched_lines.append(f"{' ' * (method_indent + 4)}if isinstance(query, dict):")
            patched_lines.append(f"{' ' * (method_indent + 8)}# Dictionary format")
            patched_lines.append(f"{' ' * (method_indent + 8)}query_text = query.get('query', '')")
            patched_lines.append(f"{' ' * (method_indent + 8)}context_text = query.get('context', '')")
            patched_lines.append(f"{' ' * (method_indent + 4)}else:")
            patched_lines.append(f"{' ' * (method_indent + 8)}# Separate parameters")
            patched_lines.append(f"{' ' * (method_indent + 8)}query_text = str(query)")
            patched_lines.append(f"{' ' * (method_indent + 8)}context_text = str(context) if context else ''")
            patched_lines.append(f"{' ' * (method_indent + 4)}")
            
            # Skip original method signature
            continue
            
        elif in_method and line.strip() and len(line) - len(line.lstrip()) <= method_indent:
            # End of method, now we need to use query_text and context_text
            in_method = False
        
        if in_method and ('query[' in line or "query['" in line):
            # Replace query['key'] with query_text or context_text
            line = line.replace("query['query']", "query_text")
            line = line.replace('query["query"]', "query_text")
            line = line.replace("query['context']", "context_text")
            line = line.replace('query["context"]', "context_text")
            line = line.replace("query.get('query'", "query_text or ''")
            line = line.replace("query.get('context'", "context_text or ''")
        
        patched_lines.append(line)
    
    # Write patched version
    with open(ai_service_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(patched_lines))
    
    print("✅ Patched AIService to handle both parameter formats")

def create_simple_test():
    """Create a simple test to verify the fix"""
    
    test_content = '''#!/usr/bin/env python3
"""
Simple AI Service Test
"""

from services.ai_service import AIService

def test_simple():
    print("🧪 SIMPLE AI SERVICE TEST")
    
    ai = AIService()
    
    # Test 1: String parameters
    try:
        response = ai.get_ai_response(
            "What is 2+2?",
            "This is a math question."
        )
        print("✅ Test 1 (strings): PASS")
        print(f"   Response: {response[:100]}...")
    except Exception as e:
        print(f"❌ Test 1 (strings): FAIL - {e}")
    
    # Test 2: Dictionary parameter
    try:
        response = ai.get_ai_response({
            'query': "What is 2+2?",
            'context': "This is a math question."
        })
        print("✅ Test 2 (dict): PASS")
        print(f"   Response: {response[:100]}...")
    except Exception as e:
        print(f"❌ Test 2 (dict): FAIL - {e}")

if __name__ == "__main__":
    test_simple()
'''
    
    with open("test_ai_simple.py", 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ Created test_ai_simple.py")

def main():
    print("🔧 AI SERVICE DEEP FIX")
    print("="*70)
    
    # First investigate
    investigate_ai_service()
    
    # Create wrapper
    create_ai_service_wrapper()
    
    # Patch directly
    response = input("\nPatch AIService directly? (y/n): ")
    if response.lower() == 'y':
        patch_ai_service_directly()
    
    # Create test
    create_simple_test()
    
    print("\n📋 Next steps:")
    print("1. Run: python test_ai_simple.py")
    print("2. If that works, run: python test_complete_system.py")

if __name__ == "__main__":
    main()