#!/usr/bin/env python3
"""
Fix production test method calls
Date: 2025-06-07 20:52:55 UTC
Author: thorrobber22
"""

from pathlib import Path

def fix_production_test():
    """Fix method names in production test"""
    
    prod_test_path = Path("production_test.py")
    
    if not prod_test_path.exists():
        print("❌ production_test.py not found!")
        return
    
    with open(prod_test_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix method names based on actual implementations
    fixes = [
        # CIKResolver: resolve_cik → resolve_for_ticker or search_cik
        ('await resolver.get_cik(', 'await resolver.resolve_for_ticker('),
        
        # AIService: chat → generate_response
        ('response = ai_service.get_ai_response(', 'response = ai_service.generate_response('),
        
        # DocumentService: get_documents → get_company_documents
        ('docs = doc_service.get_company_documents(', 'docs = doc_service.get_company_documents('),
    ]
    
    for old, new in fixes:
        content = content.replace(old, new)
    
    # Also need to check the actual method signatures
    # Let's look at the actual service files first
    
    print("Checking actual service methods...")
    
    # Check AIService
    ai_service_path = Path("services/ai_service.py")
    if ai_service_path.exists():
        with open(ai_service_path, 'r') as f:
            ai_content = f.read()
            if 'def chat' in ai_content:
                print("✓ AIService has 'chat' method")
            elif 'def generate_response' in ai_content:
                print("✓ AIService has 'generate_response' method")
                content = content.replace('ai_service.get_ai_response(', 'ai_service.generate_response(')
            else:
                print("! Need to check AIService methods")
    
    # Save fixed version
    with open(prod_test_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed production test!")

if __name__ == "__main__":
    fix_production_test()