"""
cleanup_genesis_final.py - Final cleanup for Genesis repository
Date: 2025-06-12 00:47:11 UTC
User: thorrobber22
Repository: thorrobber22/Genesis

This script will:
1. Archive all unnecessary files
2. Keep only required files from roadmap
3. Update timestamps on core files
4. Fix imports and dependencies
5. Create reversal script
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

# Configuration
CURRENT_TIME = datetime(2025, 6, 12, 0, 47, 11)
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
REQUIRED_FILES = {'app.py': 'Main Streamlit application with terminal UI', 'requirements.txt': 'Python dependencies', '.env': 'Environment variables (API keys)', '.gitignore': 'Git ignore rules', 'README.md': 'Project documentation', 'services/ai_service.py': 'AI chat integration with OpenAI', 'services/data_service.py': 'Data management and caching', 'services/sec_service.py': 'SEC EDGAR API integration', 'components/ipo_calendar.py': 'IPO calendar view (Phase 1)', 'components/companies.py': 'Companies detailed view (Phase 1)', 'components/metrics.py': 'Metrics dashboard (Phase 1)', 'components/chat.py': 'AI chat interface (Phase 1)', 'components/watchlist.py': 'Watchlist management (Phase 2)', 'components/lockup_tracker.py': 'Lockup expiration tracker (Phase 2)', 'components/financial_analysis.py': 'Financial analysis view (Phase 2)', 'scrapers/ipo_scraper.py': 'IPO data pipeline from IPOScoop', 'scrapers/sec_scraper.py': 'SEC document scraper', 'data/ipo_calendar.json': 'Current IPO data', 'data/watchlists.json': 'User watchlists', 'data/company_profiles.json': 'Company information cache', 'config/ui_theme.json': 'Terminal theme colors', 'config/app_config.json': 'Application settings'}

# Archive patterns
ARCHIVE_PATTERNS = [
    "*test*.py", "*backup*", "*old*", "*copy*", "*fix*", 
    "*demo*", "*example*", "app_v*.py", "*_original*", 
    "*_working*", "*.log", "__pycache__", ".pytest_cache"
]

class GenesisCleanup:
    def __init__(self):
        self.root = Path.cwd()
        self.archive_dir = self.root / ARCHIVE_DIR
        self.manifest = {
            "timestamp": CURRENT_TIME.isoformat(),
            "user": "thorrobber22",
            "archived_files": [],
            "kept_files": [],
            "created_files": [],
            "deleted_folders": [],
            "theme_colors": THEME_COLORS
        }
        
    def run(self):
        """Execute complete cleanup"""
        print("GENESIS REPOSITORY FINAL CLEANUP")
        print("="*80)
        print(f"Date: {CURRENT_TIME.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"User: thorrobber22")
        print("="*80)
        
        # Create archive directory
        self.archive_dir.mkdir(exist_ok=True)
        
        # Step 1: Archive unnecessary files
        self.archive_old_files()
        
        # Step 2: Clean up empty directories
        self.cleanup_empty_dirs()
        
        # Step 3: Ensure required structure
        self.create_required_structure()
        
        # Step 4: Update core files
        self.update_core_files()
        
        # Step 5: Apply theme
        self.apply_terminal_theme()
        
        # Step 6: Create reversal script
        self.create_reversal_script()
        
        # Step 7: Save manifest
        self.save_manifest()
        
        # Step 8: Final report
        self.final_report()
        
        print("\n" + "="*80)
        print("CLEANUP COMPLETE!")
        print("="*80)
        
    def archive_old_files(self):
        """Archive all files not in required list"""
        print("\n[ARCHIVING] Processing files...")
        
        archived_count = 0
        kept_count = 0
        
        # Process all files
        for path in list(self.root.rglob('*')):
            if path.is_file():
                relative_path = str(path.relative_to(self.root))
                
                # Skip archive directory
                if relative_path.startswith(ARCHIVE_DIR):
                    continue
                
                # Skip .git and venv
                if any(skip in relative_path for skip in ['.git', 'venv', '__pycache__']):
                    continue
                
                # Check if it's a required file
                if relative_path.replace('\\', '/') in REQUIRED_FILES:
                    kept_count += 1
                    self.manifest['kept_files'].append(relative_path)
                    continue
                
                # Check against archive patterns
                should_archive = False
                for pattern in ARCHIVE_PATTERNS:
                    if pattern.replace('*', '') in str(path).lower():
                        should_archive = True
                        break
                
                # Check age
                if not should_archive:
                    try:
                        mtime = datetime.fromtimestamp(path.stat().st_mtime)
                        if mtime < CURRENT_TIME - timedelta(days=2):
                            should_archive = True
                    except:
                        pass
                
                # Archive if needed
                if should_archive:
                    self.archive_file(path)
                    archived_count += 1
                    
        print(f"  [SUMMARY] Archived: {archived_count}, Kept: {kept_count}")
                    
    def archive_file(self, path):
        """Archive a single file"""
        relative_path = path.relative_to(self.root)
        archive_path = self.archive_dir / relative_path
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(path), str(archive_path))
        self.manifest['archived_files'].append({
            'original': str(relative_path),
            'archived': str(archive_path.relative_to(self.root))
        })
        print(f"  [ARCHIVED] {relative_path}")
        
    def cleanup_empty_dirs(self):
        """Remove empty directories"""
        print("\n[CLEANUP] Removing empty directories...")
        
        # Get all directories
        dirs = [d for d in self.root.rglob('*') if d.is_dir()]
        dirs.sort(key=lambda x: len(str(x)), reverse=True)  # Process deepest first
        
        for dir_path in dirs:
            if dir_path.name in ['.git', 'venv', ARCHIVE_DIR]:
                continue
                
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    self.manifest['deleted_folders'].append(str(dir_path.relative_to(self.root)))
                    print(f"  [REMOVED] {dir_path.relative_to(self.root)}/")
            except:
                pass
        
    def create_required_structure(self):
        """Create all required directories and files"""
        print("\n[CREATING] Required structure...")
        
        # Create directories
        dirs = ['services', 'components', 'scrapers', 'data', 'config', 'static/css']
        for dir_name in dirs:
            Path(dir_name).mkdir(parents=True, exist_ok=True)
            
        # Create UI theme config
        theme_config = Path('config/ui_theme.json')
        with open(theme_config, 'w') as f:
            json.dump(THEME_COLORS, f, indent=2)
        self.manifest['created_files'].append('config/ui_theme.json')
        print("  [CREATED] config/ui_theme.json")
        
        # Create app config
        app_config = Path('config/app_config.json')
        with open(app_config, 'w') as f:
            json.dump({
                "app_name": "Hedge Intelligence",
                "version": "1.0.0",
                "phase": "2",
                "theme": "terminal",
                "created": CURRENT_TIME.isoformat()
            }, f, indent=2)
        self.manifest['created_files'].append('config/app_config.json')
        print("  [CREATED] config/app_config.json")
        
    def update_core_files(self):
        """Update timestamps on core files"""
        print("\n[UPDATING] Core file timestamps...")
        
        core_files = ['app.py', 'services/ai_service.py', 'services/data_service.py']
        for file_path in core_files:
            if Path(file_path).exists():
                os.utime(file_path, (CURRENT_TIME.timestamp(), CURRENT_TIME.timestamp()))
                print(f"  [UPDATED] {file_path}")
                
    def apply_terminal_theme(self):
        """Create terminal theme CSS"""
        print("\n[THEMING] Applying terminal theme...")
        
        css_content = """/* Terminal Theme for Hedge Intelligence */
/* Generated: 2025-06-12 00:47:11 UTC */

.stApp {
    background-color: #212121;
    color: #F7F7F8;
}

.stMarkdown {
    color: #F7F7F8;
}

.stButton > button {
    background-color: #10A37F;
    color: #212121;
    border: none;
    font-weight: bold;
    transition: all 0.3s;
}

.stButton > button:hover {
    background-color: #0E8A6A;
}

.stTextInput > div > div > input {
    background-color: #40414F;
    color: #ECECF1;
    border: 1px solid #565869;
}

.stTextInput > div > div > input:focus {
    background-color: #4B4D5D;
    border-color: #10A37F;
}

/* Card styling */
.element-container {
    background-color: #2A2B2D;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}

/* Dividers */
hr {
    border-color: #2E2E2E;
}

/* Links */
a {
    color: #2E8AF6;
}

a:hover {
    color: #10A37F;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    background-color: #2B2B2F;
}

::-webkit-scrollbar-thumb {
    background-color: #4D4D4D;
    border-radius: 4px;
}
"""
        
        css_path = Path('static/css/terminal_theme.css')
        css_path.parent.mkdir(parents=True, exist_ok=True)
        with open(css_path, 'w') as f:
            f.write(css_content)
        self.manifest['created_files'].append('static/css/terminal_theme.css')
        print("  [CREATED] static/css/terminal_theme.css")
        
    def create_reversal_script(self):
        """Create script to reverse the cleanup"""
        reversal_content = """
reverse_genesis_cleanup.py - Reverse the cleanup operation
Generated: {CURRENT_TIME.strftime('%Y-%m-%d %H:%M:%S')} UTC
"""

import shutil
import json
from pathlib import Path

ARCHIVE_DIR = "archive_20250612004711"

def reverse():
    manifest_path = Path(ARCHIVE_DIR) / 'manifest.json'
    
    if not manifest_path.exists():
        print("[ERROR] No manifest found!")
        return
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    print("REVERSING GENESIS CLEANUP")
    print("="*60)
    
    # Restore archived files
    restored = 0
    for item in manifest['archived_files']:
        src = Path(item['archived'])
        dst = Path(item['original'])
        
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            print(f"[RESTORED] {item['original']}")
            restored += 1
    
    # Remove created files
    for created_file in manifest.get('created_files', []):
        file_path = Path(created_file)
        if file_path.exists():
            file_path.unlink()
            print(f"[REMOVED] {created_file}")
    
    print(f"\n[COMPLETE] Restored {restored} files")
    print("Reversal complete!")

if __name__ == "__main__":
    reverse()
"""
        
        with open('reverse_genesis_cleanup.py', 'w') as f:
            f.write(reversal_content)
        print("  [CREATED] reverse_genesis_cleanup.py")
        
    def save_manifest(self):
        """Save cleanup manifest"""
        manifest_path = self.archive_dir / 'manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
        print(f"  [SAVED] {manifest_path}")
        
    def final_report(self):
        """Generate final report"""
        print("\n" + "="*80)
        print("FINAL REPORT")
        print("="*80)
        print(f"Files archived: {len(self.manifest['archived_files'])}")
        print(f"Files kept: {len(self.manifest['kept_files'])}")
        print(f"Files created: {len(self.manifest['created_files'])}")
        print(f"Folders removed: {len(self.manifest['deleted_folders'])}")
        print(f"\nArchive location: {ARCHIVE_DIR}/")
        print(f"Reversal script: reverse_genesis_cleanup.py")

if __name__ == "__main__":
    cleanup = GenesisCleanup()
    cleanup.run()
