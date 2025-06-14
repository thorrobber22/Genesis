# Reversal Script for Genesis Cleanup
# Generated: 2025-06-12 00:58:16
import shutil
import json
from pathlib import Path

ARCHIVE_DIR = "archive_20250612_005816"

def reverse():
    manifest_path = Path(ARCHIVE_DIR) / "manifest.json"
    
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    print("REVERSING CLEANUP")
    print("="*60)
    
    restored = 0
    for item in manifest["archived_files"]:
        src = Path(item["archived"])
        dst = Path(item["original"])
        
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            print(f"[RESTORED] {dst}")
            restored += 1
    
    print(f"\nRestored {restored} files")
    print("Reversal complete!")

if __name__ == "__main__":
    reverse()