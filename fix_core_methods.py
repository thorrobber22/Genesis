#!/usr/bin/env python3
"""
Fix all method mismatches for working app
Date: 2025-06-07 21:16:34 UTC
"""

from pathlib import Path

def fix_all_methods():
    """Fix all method calls across the application"""
    
    fixes_needed = {
        # AI Service - wrong method name
        ('ai_service.get_ai_response(', 'ai_service.get_ai_response('),
        
        # CIK Resolver - wrong method
        ('resolver.get_cik(', 'resolver.get_cik('),
        ('resolver.get_cik(', 'resolver.get_cik('),  # Fix the scraper error
        
        # Document Service - already correct
        ('doc_service.get_company_documents(', 'doc_service.get_company_documents('),
    }
    
    # Fix in all Python files
    for py_file in Path('.').rglob('*.py'):
        if 'venv' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            changed = False
            for old, new in fixes_needed:
                if old in content:
                    content = content.replace(old, new)
                    changed = True
            
            if changed:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed: {py_file}")
                
        except:
            pass

if __name__ == "__main__":
    fix_all_methods()