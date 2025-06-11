#!/usr/bin/env python3
"""
Fix document processor validation logic
Date: 2025-06-06 11:51:30 UTC
Author: thorrobber22
"""

from pathlib import Path

print("Checking document processor validation logic...")

# Read the processor
dp_path = Path("core/document_processor.py")
with open(dp_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find where validation_status is set to ERROR
if "validation_status" in content:
    print("Found validation_status references")
    
    # Update to be less strict about validation errors
    # Look for the part that sets status based on validation
    
    # Create a patch that allows indexing even with validation errors
    patch = '''
# Allow indexing even with validation errors
# The data might be partially extracted which is still useful
if result.get("validation_status") == "ERROR":
    print("Warning: Document had validation errors but will continue processing")
    # Don't block processing, just note the issue
'''
    
    print("\nTo fix validation being too strict:")
    print("1. The document processor should continue even with partial data")
    print("2. We can improve extraction accuracy later")
    print("3. For now, index whatever data we can extract")

print("\nFor now, let's see if the indexing works with the current data...")