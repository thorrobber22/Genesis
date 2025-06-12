"""
reverse_cleanup.py - Reverse the cleanup operation
Generated: 2025-06-11 23:55:29 UTC
User: thorrobber22
"""

import shutil
import json
from pathlib import Path

ARCHIVE_NAME = "archive_20250611_235529"
MANIFEST_FILE = "archive_20250611_235529/cleanup_manifest.json"

def reverse_cleanup():
    """Restore all archived files to original locations"""
    print("REVERSING CLEANUP OPERATION...")
    print("="*60)
    
    # Load manifest
    with open(MANIFEST_FILE, 'r') as f:
        manifest = json.load(f)
    
    restored_count = 0
    
    # Restore each archived file
    for file_info in manifest['archived_files']:
        archive_path = Path(file_info['archive_path'])
        original_path = Path(file_info['original_path'])
        
        if archive_path.exists():
            # Create parent directory if needed
            original_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file back
            shutil.move(str(archive_path), str(original_path))
            restored_count += 1
            print(f"[OK] Restored: {original_path}")
    
    # Remove archive directory if empty
    archive_dir = Path(ARCHIVE_NAME)
    if archive_dir.exists() and not any(archive_dir.iterdir()):
        archive_dir.rmdir()
        print(f"\n[CLEANUP] Removed empty archive directory")
    
    print(f"\n[DONE] Restored {restored_count} files")
    print("Reversal complete!")

if __name__ == "__main__":
    reverse_cleanup()
