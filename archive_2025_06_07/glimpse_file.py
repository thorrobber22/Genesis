#!/usr/bin/env python3
"""
Quick glimpse into file structure and key functions
"""

import sys
from pathlib import Path
import ast

def glimpse_file(filepath):
    """Show structure of a Python file"""
    path = Path(filepath)
    
    if not path.exists():
        print(f"❌ File not found: {filepath}")
        return
    
    print(f"\n📄 FILE: {filepath}")
    print("=" * 60)
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Basic stats
    lines = content.split('\n')
    print(f"Lines: {len(lines)}")
    print(f"Size: {len(content):,} bytes")
    
    # Try to parse Python structure
    try:
        tree = ast.parse(content)
        
        # Find imports
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        print(f"\n📦 Key Imports ({len(imports)}):")
        shown = set()
        for imp in imports[:10]:
            if isinstance(imp, ast.ImportFrom):
                module = imp.module or ''
                if module not in shown:
                    print(f"  - from {module}")
                    shown.add(module)
        
        # Find classes
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        if classes:
            print(f"\n🏗️ Classes ({len(classes)}):")
            for cls in classes:
                print(f"  - {cls.name}")
                # Show methods
                methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)]
                for method in methods[:5]:
                    print(f"    └─ {method.name}()")
        
        # Find functions
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        if functions:
            print(f"\n🔧 Top-level Functions ({len(functions)}):")
            for func in functions[:10]:
                args = ', '.join(arg.arg for arg in func.args.args)
                print(f"  - {func.name}({args})")
        
        # Find key patterns
        print(f"\n🔍 Key Patterns:")
        if 'streamlit' in content or 'st.' in content:
            print("  - Uses Streamlit")
        if 'async def' in content:
            print("  - Has async functions")
        if 'ChromaDB' in content or 'chromadb' in content:
            print("  - Uses ChromaDB")
        if 'document_type' in content:
            print("  - Has document type handling")
        if 'accept_multiple_files' in content:
            print("  - Supports multiple file upload")
        
    except SyntaxError as e:
        print(f"\n⚠️ Syntax Error: {e}")
        print("Showing raw content preview instead...")
        
    # Show first few meaningful lines
    print(f"\n📝 First Few Lines:")
    print("-" * 40)
    shown = 0
    for line in lines[:50]:
        if line.strip() and not line.strip().startswith('#'):
            print(line[:80])
            shown += 1
            if shown >= 10:
                break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python glimpse_file.py <filepath>")
        sys.exit(1)
    
    glimpse_file(sys.argv[1])