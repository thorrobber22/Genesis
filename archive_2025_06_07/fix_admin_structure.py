#!/usr/bin/env python3
"""
Fix admin.py structure properly
Date: 2025-06-06 12:06:26 UTC
Author: thorrobber22
"""

from pathlib import Path

print("Fixing admin.py structure...")

# Read current admin.py
admin_path = Path("admin.py")
with open(admin_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find where authentication check should wrap content
lines = content.split('\n')

# Look for where main content starts (usually after imports and auth function)
main_content_start = None
for i, line in enumerate(lines):
    if "st.title" in line and "Admin" in line:
        main_content_start = i
        break

if main_content_start is None:
    print("Could not find main content start")
    exit(1)

print(f"Found main content starting at line {main_content_start + 1}")

# Build new structure
new_lines = []
auth_added = False

# Copy imports and functions
for i in range(main_content_start):
    line = lines[i]
    new_lines.append(line)
    
    # After the check_password function, add the auth check
    if "return True" in line and not auth_added:
        # This is likely the end of check_password function
        new_lines.append("")
        new_lines.append("# Main application")
        new_lines.append("if check_password():")
        auth_added = True
        print("Added authentication wrapper")

# Add the rest with proper indentation
if auth_added:
    for i in range(main_content_start, len(lines)):
        line = lines[i]
        if line.strip():  # Non-empty line
            new_lines.append("    " + line)
        else:
            new_lines.append(line)
else:
    print("Warning: Could not add authentication wrapper")
    # Fallback: just ensure there's an auth check
    new_lines.append("")
    new_lines.append("if check_password():")
    for i in range(main_content_start, len(lines)):
        line = lines[i]
        if line.strip():
            new_lines.append("    " + line)
        else:
            new_lines.append(line)

# Write the fixed version
with open(admin_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("Fixed admin.py structure!")
print("\nThe main content is now inside the authentication check.")
print("Run: streamlit run admin.py")