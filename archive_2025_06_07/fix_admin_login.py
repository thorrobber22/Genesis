#!/usr/bin/env python3
"""
Fix admin login issue
Date: 2025-06-06 11:57:16 UTC
Author: thorrobber22
"""

from pathlib import Path

print("Fixing admin.py login structure...")

admin_path = Path("admin.py")
with open(admin_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if the main content is properly indented under password check
if "if check_password():" in content:
    # Find where the password check is
    lines = content.split('\n')
    password_line_idx = None
    
    for i, line in enumerate(lines):
        if "if check_password():" in line:
            password_line_idx = i
            break
    
    if password_line_idx is not None:
        print(f"Found password check at line {password_line_idx + 1}")
        
        # Check if the next content is properly indented
        indent_issue = False
        for i in range(password_line_idx + 1, min(password_line_idx + 10, len(lines))):
            if lines[i].strip() and not lines[i].startswith('    '):
                print(f"Indentation issue at line {i + 1}: {lines[i][:50]}")
                indent_issue = True
                break
        
        if indent_issue:
            print("\nFixing indentation...")
            # Need to indent everything after password check
            fixed_lines = lines[:password_line_idx + 1]
            
            # Add everything else with proper indentation
            in_password_block = True
            for i in range(password_line_idx + 1, len(lines)):
                line = lines[i]
                if in_password_block and line.strip() and not line.startswith('    '):
                    # This line needs indentation
                    fixed_lines.append('    ' + line)
                else:
                    fixed_lines.append(line)
            
            # Write back
            with open(admin_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))
            
            print("✓ Fixed indentation")
else:
    print("Password check structure not found. Creating new structure...")
    
    # Wrap the main content in password check
    new_content = '''import streamlit as st
from config import ADMIN_PASSWORD
from core.document_processor import process_document_sync
from process_and_index import process_and_index_document_sync
from search_interface import show_search_interface
from document_viewer import show_document_viewer
from pathlib import Path
import json
from datetime import datetime

st.set_page_config(page_title="Hedge Intel Admin", page_icon="🏛️", layout="wide")

st.markdown(\'''
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
\''', unsafe_allow_html=True)

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == ADMIN_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True

if check_password():
    st.title("🏛️ Hedge Intelligence Admin Panel")
    
    # Add the rest of your admin panel code here
    # This is where the tabs and functionality go
    
    tab1, tab2, tab3, tab4 = st.tabs(["Upload", "Documents", "Status", "Search"])
    
    with tab1:
        st.header("Upload Documents")
        # Upload functionality here
        
    with tab2:
        st.header("Document Management")
        # Document list here
        
    with tab3:
        st.header("System Status")
        # Status info here
        
    with tab4:
        show_search_interface()
'''
    
    print("\nWould create a new structure, but let's first check what's in your current admin.py")

print("\nRun debug_admin_login.py first to see the issue")