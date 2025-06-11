#!/usr/bin/env python3
"""
Fix the os import error in validator
"""

# fix_validator_os.py
from pathlib import Path

validator_file = Path("comprehensive_production_validator.py")

with open(validator_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the imports section and add os
for i, line in enumerate(lines):
    if line.strip().startswith("import sys"):
        lines.insert(i+1, "import os\n")
        break

with open(validator_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fixed os import in validator")

# Now run the validator
import subprocess
subprocess.run(["python", "comprehensive_production_validator.py"])