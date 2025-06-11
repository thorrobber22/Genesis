#!/usr/bin/env python3
"""
Apply updates to admin.py automatically
Date: 2025-06-06 11:51:30 UTC
Author: thorrobber22
"""

from pathlib import Path
import re

admin_path = Path("admin.py")
if not admin_path.exists():
    print("Error: admin.py not found!")
    exit(1)

# Read current admin.py
with open(admin_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup first
backup_path = Path("admin_backup.py")
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Created backup: {backup_path}")

# 1. Add imports if not present
imports_to_add = [
    "from process_and_index import process_and_index_document_sync",
    "from search_interface import show_search_interface", 
    "from document_viewer import show_document_viewer"
]

for imp in imports_to_add:
    if imp not in content:
        # Add after other imports
        pos = content.find("import streamlit as st")
        if pos > 0:
            end_of_line = content.find("\n", pos)
            content = content[:end_of_line+1] + imp + "\n" + content[end_of_line+1:]
            print(f"Added import: {imp}")

# 2. Add style if not present
style_code = """st.markdown('''
<style>
    /* Clean Apple-style sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f5f5f7;
        padding-top: 2rem;
    }
    /* Clean tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f5f5f7;
        padding: 4px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        color: #1d1d1f;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: white;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
''', unsafe_allow_html=True)"""

if "Clean Apple-style" not in content:
    # Add after page config
    pos = content.find('st.set_page_config')
    if pos > 0:
        end_of_line = content.find('\n\n', pos)
        if end_of_line > 0:
            content = content[:end_of_line+2] + style_code + "\n\n" + content[end_of_line+2:]
            print("Added Apple-style CSS")

# 3. Update tabs to include Search
if 'st.tabs(["Upload", "Documents", "Status"])' in content:
    content = content.replace(
        'st.tabs(["Upload", "Documents", "Status"])',
        'st.tabs(["Upload", "Documents", "Status", "Search"])'
    )
    print("Updated tabs to include Search")

# 4. Add Search tab content
if "show_search_interface" not in content:
    # Find where to add the search tab
    status_tab_pattern = r'with tab3:.*?(?=(?:with tab|def|\Z))'
    match = re.search(status_tab_pattern, content, re.DOTALL)
    if match:
        insert_pos = match.end()
        search_tab_code = """
with tab4:
    show_search_interface()
"""
        content = content[:insert_pos] + "\n" + search_tab_code + "\n" + content[insert_pos:]
        print("Added Search tab")

# Write updated content
with open(admin_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nAdmin panel updated successfully!")
print("Run: streamlit run admin.py")