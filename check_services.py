#!/usr/bin/env python3
"""
Check actual service method names
Date: 2025-06-07 20:52:55 UTC
"""

from pathlib import Path
import ast
import inspect

def check_service_methods():
    """Check what methods each service actually has"""
    
    services = {
        'services/ai_service.py': 'AIService',
        'services/document_service.py': 'DocumentService',
        'services/chat_service.py': 'ChatService',
        'scrapers/sec/cik_resolver.py': 'CIKResolver'
    }
    
    for file_path, class_name in services.items():
        path = Path(file_path)
        if path.exists():
            print(f"\n📁 {file_path}")
            print(f"   Class: {class_name}")
            
            try:
                # Import and inspect
                module_name = file_path.replace('/', '.').replace('.py', '')
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
                
                # Get methods
                methods = [method for method in dir(cls) if not method.startswith('_')]
                print("   Methods:")
                for method in sorted(methods):
                    print(f"     - {method}")
                    
            except Exception as e:
                # Fallback: parse the file
                with open(path, 'r') as f:
                    content = f.read()
                
                print("   Methods found in code:")
                import re
                methods = re.findall(r'def\s+([a-zA-Z_]\w*)\s*\(', content)
                for method in set(methods):
                    if not method.startswith('_'):
                        print(f"     - {method}")

if __name__ == "__main__":
    check_service_methods()