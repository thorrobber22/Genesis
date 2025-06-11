#!/usr/bin/env python3
"""
Fix document viewer TypeError
"""

from pathlib import Path

def fix_document_viewer():
    """Fix the document viewer path issue"""
    
    print("FIXING DOCUMENT VIEWER")
    print("="*60)
    
    # Read main file
    main_file = Path("hedge_intelligence.py")
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find render_document_viewer function
    func_start = content.find("def render_document_viewer():")
    
    if func_start != -1:
        # Find the problematic line
        problem_line = "doc_path = Path(st.session_state.selected_doc)"
        
        # Replace with proper handling
        fix = '''def render_document_viewer():
    """Render document viewer in main area"""
    if 'selected_doc' not in st.session_state or not st.session_state.selected_doc:
        return
    
    # Handle both string paths and dict objects
    selected_doc = st.session_state.selected_doc
    
    # If it's a dict (from search results), extract the path
    if isinstance(selected_doc, dict):
        doc_path = Path(selected_doc.get('path', ''))
    else:
        doc_path = Path(selected_doc)
    
    if not doc_path.exists():
        st.error(f"Document not found: {doc_path}")
        return'''
        
        # Find end of function
        func_end = content.find("\ndef ", func_start + 1)
        if func_end == -1:
            func_end = content.find("\n# Chat", func_start)
        
        # Get the rest of the function
        current_func = content[func_start:func_end]
        
        # Replace just the beginning
        new_func = fix + current_func[current_func.find("if not doc_path.exists():"):]
        
        # Replace in content
        content = content[:func_start] + new_func + content[func_end:]
        
        # Save
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed document viewer path handling")
        return True
    else:
        print("❌ Could not find render_document_viewer function")
        return False

if __name__ == "__main__":
    fix_document_viewer()