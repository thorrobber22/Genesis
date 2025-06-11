#!/usr/bin/env python3
"""
Fix admin.py indentation issue
Date: 2025-06-06 12:09:22 UTC
Author: thorrobber22
"""

from pathlib import Path

print("Fixing admin.py indentation...")

# Read the file
with open("admin.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the line with "if check_password():"
auth_line = None
for i, line in enumerate(lines):
    if "if check_password():" in line:
        auth_line = i
        print(f"Found auth check at line {i+1}")
        break

if auth_line is None:
    print("Could not find authentication check!")
    exit(1)

# Check indentation of next lines
print(f"Checking indentation after line {auth_line+1}...")

# Count current indent of the if statement
current_indent = len(lines[auth_line]) - len(lines[auth_line].lstrip())
print(f"Current indent of if statement: {current_indent} spaces")

# Everything after should be indented by 4 more spaces
required_indent = current_indent + 4

# Fix indentation for all lines after auth check
fixed_lines = lines[:auth_line+1]  # Keep everything up to auth check

for i in range(auth_line+1, len(lines)):
    line = lines[i]
    
    # Skip empty lines
    if line.strip() == "":
        fixed_lines.append(line)
        continue
    
    # Get current indentation
    line_indent = len(line) - len(line.lstrip())
    
    # If it's a def statement at the wrong level, fix it
    if line.strip().startswith("def ") and line_indent < required_indent:
        # This function should be inside the auth block
        fixed_lines.append(" " * required_indent + line.lstrip())
        print(f"Fixed indentation for line {i+1}: {line.strip()[:50]}")
    elif line_indent < required_indent and i < auth_line + 10:
        # Lines immediately after auth should be indented
        fixed_lines.append(" " * required_indent + line.lstrip())
    else:
        # Keep the line as is
        fixed_lines.append(line)

# Write back
with open("admin.py", "w", encoding="utf-8") as f:
    f.writelines(fixed_lines)

print("\nFixed indentation!")
print(f"\nThe correct password is: hedgeadmin2025")
print("\nRun: streamlit run admin.py")