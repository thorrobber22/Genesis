#!/usr/bin/env python3
"""
Fix the validator error and show results
"""

from pathlib import Path

def fix_validator():
    """Fix the os import error in validator"""
    
    print("FIXING VALIDATOR")
    print("="*60)
    
    validator_file = Path("comprehensive_production_validator.py")
    
    if validator_file.exists():
        with open(validator_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add os import at the top with other imports
        if "import os" not in content:
            # Find where to insert
            insert_point = content.find("import sys")
            if insert_point != -1:
                insert_point = content.find("\n", insert_point) + 1
                content = content[:insert_point] + "import os\n" + content[insert_point:]
                
                with open(validator_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ Fixed os import")
        
    return True

if __name__ == "__main__":
    fix_validator()
    print("\nNow running validator again...")
    print("="*60)
    
    import subprocess
    subprocess.run(["python", "comprehensive_production_validator.py"])