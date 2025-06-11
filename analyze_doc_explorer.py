#!/usr/bin/env python3
"""
Analyze the document explorer to understand current navigation
"""

from pathlib import Path
import re

def analyze_doc_explorer():
    """Check how doc_explorer sidebar works"""
    
    # Check main app first
    main_app = Path("hedge_intelligence.py")
    with open(main_app, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    print("DOCUMENT EXPLORER ANALYSIS")
    print("="*60)
    
    # Find doc_explorer import
    import_match = re.search(r'from\s+(\S+)\s+import\s+.*doc_explorer|import\s+(\S+)\s+as\s+doc_explorer', main_content)
    if import_match:
        print(f"Import found: {import_match.group(0)}")
    
    # Look for document_explorer module
    possible_paths = [
        "components/document_explorer.py",
        "document_explorer.py",
        "services/document_explorer.py"
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            print(f"\nFound module at: {path}")
            with open(path, 'r', encoding='utf-8') as f:
                explorer_content = f.read()
            
            # Find render_sidebar method
            sidebar_match = re.search(r'def render_sidebar\(.*?\):(.*?)(?=\n    def|\nclass|\Z)', explorer_content, re.DOTALL)
            if sidebar_match:
                print("\nrender_sidebar() implementation:")
                print("-"*40)
                print(sidebar_match.group(0)[:500] + "..." if len(sidebar_match.group(0)) > 500 else sidebar_match.group(0))
            break
    
    # Check what persistent_chat is
    print("\n\nPERSISTENT CHAT ANALYSIS:")
    print("-"*40)
    chat_import = re.search(r'from\s+(\S+)\s+import\s+.*persistent_chat|import\s+(\S+)\s+as\s+persistent_chat', main_content)
    if chat_import:
        print(f"Import: {chat_import.group(0)}")
    
    # Find render functions
    print("\n\nEXISTING RENDER FUNCTIONS:")
    print("-"*40)
    render_functions = re.findall(r'def\s+(render_\w+)\s*\(', main_content)
    for func in render_functions:
        print(f"  - {func}")
    
    # Check session state usage
    print("\n\nSESSION STATE USAGE:")
    print("-"*40)
    session_vars = re.findall(r'st\.session_state\[[\'"](.*?)[\'"]\]', main_content)
    unique_vars = list(dict.fromkeys(session_vars))
    for var in unique_vars[:10]:  # Show first 10
        print(f"  - {var}")

if __name__ == "__main__":
    analyze_doc_explorer()