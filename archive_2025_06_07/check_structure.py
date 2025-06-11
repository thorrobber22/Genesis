# check_structure.py
from pathlib import Path

print("Current directory structure:")
for p in Path(".").glob("*"):
    if p.is_dir():
        print(f"[DIR]  {p.name}/")
        # Show first level of subdirectory
        for sp in p.glob("*"):
            print(f"       - {sp.name}")
    else:
        print(f"[FILE] {p.name}")

# Check specifically for admin files
print("\nLooking for admin-related files:")
for p in Path(".").rglob("admin*"):
    print(f"  {p}")