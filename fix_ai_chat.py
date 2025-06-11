#!/usr/bin/env python3
"""
Fix AI Chat to work with existing AIService structure
"""

import json
from pathlib import Path

def check_ai_service_structure():
    """First, let's see what methods AIService actually has"""
    print("🔍 Checking AIService structure...")
    
    ai_service_path = Path("services/ai_service.py")
    
    if ai_service_path.exists():
        with open(ai_service_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find method definitions
        import re
        methods = re.findall(r'def\s+(\w+)\s*\(', content)
        
        print("Found methods in AIService:")
        for method in methods:
            print(f"  - {method}")
        
        # Check for chat-related methods
        chat_methods = [m for m in methods if 'chat' in m.lower() or 'query' in m.lower()]
        print(f"\nChat-related methods: {chat_methods}")
        
        return methods

def create_test_ai_chat():
    """Create a test script that uses the correct AIService method"""
    
    test_script = '''#!/usr/bin/env python3
"""
Test AI Chat with proper method calls
"""

from services.ai_service import AIService
from services.document_service import DocumentService

def test_ai_chat_integration():
    print("🧪 TESTING AI CHAT WITH REAL DOCUMENT")
    
    # Get a real document
    doc_service = DocumentService()
    docs = doc_service.get_company_documents('CRCL')
    
    if not docs:
        print("❌ No CRCL documents found")
        return False
    
    # Load document content
    doc_name = docs[0]
    content = doc_service.get_document_content('CRCL', doc_name)
    
    print(f"\\nDocument: {doc_name}")
    print(f"Size: {len(content):,} chars")
    
    # Initialize AI service
    ai_service = AIService()
    
    # Try different methods based on what exists
    test_queries = [
        "What is the company's primary business?",
        "What is the total revenue?",
        "What are the main risk factors?"
    ]
    
    for query in test_queries:
        print(f"\\n📝 Query: {query}")
        
        try:
            # Try method 1: chat
            if hasattr(ai_service, 'chat'):
                response = ai_service.chat(query, content)
            # Try method 2: analyze_document
            elif hasattr(ai_service, 'analyze_document'):
                response = ai_service.analyze_document(query, content)
            # Try method 3: process_document_query
            elif hasattr(ai_service, 'process_document_query'):
                response = ai_service.process_document_query(query, content)
            else:
                print("❌ No suitable method found in AIService")
                return False
            
            # Check for citations
            has_citation = '[Page' in response or 'page' in response.lower()
            
            print(f"Response preview: {response[:200]}...")
            print(f"Has citation: {has_citation}")
            
            if has_citation:
                return True
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    test_ai_chat_integration()
'''
    
    with open("test_ai_chat_fixed.py", 'w') as f:
        f.write(test_script)
    
    print("✅ Created test_ai_chat_fixed.py")

def main():
    # First check what methods exist
    methods = check_ai_service_structure()
    
    # Create test script
    create_test_ai_chat()
    
    print("\n📋 Next step: Run `python test_ai_chat_fixed.py`")

if __name__ == "__main__":
    main()