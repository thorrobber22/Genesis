"""
cleanup_genesis_working.py - Working cleanup script for Genesis
Date: 2025-06-12 00:52:17 UTC
User: thorrobber22
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

# Configuration
CURRENT_TIME = datetime(2025, 6, 12, 0, 52, 17)
ARCHIVE_DIR = f"archive_{CURRENT_TIME.strftime('%Y%m%d_%H%M%S')}"

# Terminal theme colors
THEME_COLORS = {
    "background": "#212121",
    "card_background": "#2A2B2D",
    "text_primary": "#F7F7F8",
    "text_secondary": "#A3A3A3",
    "accent_green": "#10A37F",
    "link_hover": "#2E8AF6",
    "divider": "#2E2E2E",
    "input_background": "#40414F",
    "input_text": "#ECECF1",
    "input_border": "#565869",
    "input_hover": "#4B4D5D",
    "icon_muted": "#C5C5D2",
    "scrollbar_track": "#2B2B2F",
    "scrollbar_thumb": "#4D4D4D"
}

# Required files based on roadmap
REQUIRED_FILES = {
    "app.py": "Main Streamlit application",
    "requirements.txt": "Dependencies",
    ".env": "Environment variables",
    ".gitignore": "Git rules",
    "README.md": "Documentation",
    "services/ai_service.py": "AI service",
    "services/data_service.py": "Data service",
    "services/sec_service.py": "SEC service",
    "components/ipo_calendar.py": "IPO calendar",
    "components/companies.py": "Companies view",
    "components/metrics.py": "Metrics dashboard",
    "components/chat.py": "Chat interface",
    "components/watchlist.py": "Watchlist",
    "components/lockup_tracker.py": "Lockup tracker",
    "components/financial_analysis.py": "Financial analysis",
    "scrapers/ipo_scraper.py": "IPO scraper",
    "scrapers/sec_scraper.py": "SEC scraper",
    "data/ipo_calendar.json": "IPO data",
    "data/watchlists.json": "Watchlists",
    "data/company_profiles.json": "Company data",
    "config/ui_theme.json": "Theme config",
    "config/app_config.json": "App config"
}

# Archive patterns
ARCHIVE_PATTERNS = [
    "test", "backup", "old", "copy", "fix", 
    "demo", "example", "_original", "_working", 
    ".log", "__pycache__", ".pytest_cache"
]

print("GENESIS REPOSITORY CLEANUP")
print("="*80)
print(f"Date: {CURRENT_TIME.strftime('%Y-%m-%d %H:%M:%S')} UTC")
print(f"User: thorrobber22")
print("="*80)

# Create archive directory
archive_path = Path(ARCHIVE_DIR)
archive_path.mkdir(exist_ok=True)

manifest = {
    "timestamp": CURRENT_TIME.isoformat(),
    "user": "thorrobber22",
    "archived_files": [],
    "kept_files": [],
    "created_files": []
}

# Step 1: Archive old files
print("\n[ARCHIVING] Processing files...")
archived_count = 0

for path in list(Path.cwd().rglob('*')):
    if path.is_file():
        relative_path = str(path.relative_to(Path.cwd())).replace('\\', '/')
        
        # Skip special directories
        if any(skip in relative_path for skip in ['.git', 'venv', ARCHIVE_DIR, '__pycache__']):
            continue
        
        # Check if required file
        if relative_path in REQUIRED_FILES:
            manifest['kept_files'].append(relative_path)
            continue
        
        # Check archive patterns
        should_archive = any(pattern in str(path).lower() for pattern in ARCHIVE_PATTERNS)
        
        # Archive if needed
        if should_archive:
            archive_dest = archive_path / path.relative_to(Path.cwd())
            archive_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(archive_dest))
            manifest['archived_files'].append({
                'original': relative_path,
                'archived': str(archive_dest.relative_to(Path.cwd()))
            })
            archived_count += 1
            print(f"  [ARCHIVED] {relative_path}")

print(f"\n[SUMMARY] Archived {archived_count} files")

# Step 2: Create required directories
print("\n[CREATING] Required structure...")
for dir_name in ['services', 'components', 'scrapers', 'data', 'config', 'static/css']:
    Path(dir_name).mkdir(parents=True, exist_ok=True)

# Step 3: Create theme files
theme_path = Path('config/ui_theme.json')
with open(theme_path, 'w') as f:
    json.dump(THEME_COLORS, f, indent=2)
manifest['created_files'].append('config/ui_theme.json')
print("  [CREATED] config/ui_theme.json")

# Step 4: Create CSS
css_content = f"""/* Terminal Theme - Generated {CURRENT_TIME} */
.stApp {{ background-color: {THEME_COLORS['background']}; color: {THEME_COLORS['text_primary']}; }}
.stButton > button {{ background-color: {THEME_COLORS['accent_green']}; color: {THEME_COLORS['background']}; }}
.stTextInput > div > div > input {{ background-color: {THEME_COLORS['input_background']}; color: {THEME_COLORS['input_text']}; }}
"""

css_path = Path('static/css/terminal_theme.css')
css_path.parent.mkdir(parents=True, exist_ok=True)
with open(css_path, 'w') as f:
    f.write(css_content)
manifest['created_files'].append('static/css/terminal_theme.css')
print("  [CREATED] static/css/terminal_theme.css")

# Step 5: Save manifest
manifest_path = archive_path / 'manifest.json'
with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2)
print(f"  [SAVED] {manifest_path}")

# Step 6: Create reversal script
with open('reverse_cleanup.py', 'w') as f:
    f.write(f'''"""Reverse cleanup - Generated {CURRENT_TIME}"""
import shutil
import json
from pathlib import Path

manifest_path = Path("{ARCHIVE_DIR}") / "manifest.json"
with open(manifest_path, 'r') as f:
    manifest = json.load(f)

for item in manifest['archived_files']:
    src = Path(item['archived'])
    dst = Path(item['original'])
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        print(f"[RESTORED] {{dst}}")

print("Reversal complete!")
''')

print("\n" + "="*80)
print("CLEANUP COMPLETE!")
print(f"Archive: {ARCHIVE_DIR}/")
print("To reverse: python reverse_cleanup.py")
print("="*80)