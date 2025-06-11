#!/usr/bin/env python3
"""
Fix scrape_ipos indentation in admin_streamlined.py
Date: 2025-06-06 13:15:16 UTC
Author: thorrobber22
"""

from pathlib import Path

print("Fixing scrape_ipos function placement...")

# Read the file
admin_path = Path("admin_streamlined.py")
with open(admin_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where scrape_ipos is defined
scrape_start = None
for i, line in enumerate(lines):
    if "def scrape_ipos():" in line:
        scrape_start = i
        print(f"Found scrape_ipos at line {i+1}")
        # Check indentation
        indent = len(line) - len(line.lstrip())
        print(f"Current indentation: {indent} spaces")
        
        # Check what's above it
        print(f"\nLine before: {lines[i-1].strip()}")
        
        # If it's indented, it's inside something else
        if indent > 0:
            print("ERROR: Function is indented - it's inside another function!")
            
            # Find the function end (next line with same or less indentation)
            func_end = i + 1
            while func_end < len(lines):
                line_indent = len(lines[func_end]) - len(lines[func_end].lstrip())
                if lines[func_end].strip() and line_indent <= indent:
                    break
                func_end += 1
            
            print(f"Function ends around line {func_end}")
            
            # Extract the function
            function_lines = []
            for j in range(scrape_start, func_end):
                # Remove extra indentation
                line = lines[j]
                if line.strip():
                    line = line[indent:]  # Remove the extra indent
                function_lines.append(line)
            
            # Remove the function from its current location
            del lines[scrape_start:func_end]
            
            # Find where to place it (before the authentication section)
            insert_point = None
            for i, line in enumerate(lines):
                if "# Authentication" in line or "if 'authenticated' not in st.session_state:" in line:
                    insert_point = i
                    break
            
            if insert_point is None:
                # Try to find the main app section
                for i, line in enumerate(lines):
                    if "# Main application" in line:
                        insert_point = i
                        break
            
            if insert_point:
                print(f"\nMoving function to line {insert_point}")
                # Insert the function at module level
                lines.insert(insert_point, "\n")
                for j, func_line in enumerate(reversed(function_lines)):
                    lines.insert(insert_point, func_line)
                lines.insert(insert_point, "# Helper function moved to module level\n")
            
            # Write back
            with open(admin_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print("\n✓ Fixed function placement!")
        else:
            print("Function is already at module level")
        break

print("\nRun: streamlit run admin_streamlined.py")
print("Password: hedgeadmin2025")