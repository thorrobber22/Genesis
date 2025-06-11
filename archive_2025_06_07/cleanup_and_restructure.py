#!/usr/bin/env python3
"""
Hedge Intelligence - Cleanup and Restructure Script
Date: 2025-06-05 13:15:41 UTC
User: thorrobber22

This script cleans up unnecessary files and restructures the project
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import glob

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}→ {message}{Colors.ENDC}")

def create_backup():
    """Create backup of current state"""
    print_header("PHASE 1.1: Creating Backup")
    
    backup_dir = f"hedge_intel_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
        
        # List of important files to backup
        important_files = [
            'data/cache/ipo_calendar.json',
            'data/cache/lockup_calendar.json',
            'data/processed/*.json',
            'data/documents/*.html',
            'data/documents/*.pdf',
            '.env',
            'requirements.txt'
        ]
        
        backed_up = 0
        for pattern in important_files:
            for file in glob.glob(pattern, recursive=True):
                if os.path.exists(file):
                    dest = os.path.join(backup_dir, file)
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    shutil.copy2(file, dest)
                    backed_up += 1
        
        print_success(f"Backed up {backed_up} important files to {backup_dir}")
        return backup_dir
    
    except Exception as e:
        print_error(f"Backup failed: {e}")
        return None

def remove_unnecessary_files():
    """Remove all unnecessary files"""
    print_header("PHASE 1.2: Removing Unnecessary Files")
    
    # Define patterns to remove
    patterns_to_remove = [
        # Build and fix scripts
        'fix_*.py',
        'build_*.py',
        'complete_*.py',
        'update_*.py',
        'rebuild_*.py',
        'create_*.py',
        
        # Test and debug scripts
        'test_*.py',
        'debug_*.py',
        
        # Analysis scripts
        'analyze_*.py',
        'scan_*.py',
        'show_*.py',
        'code_analysis_report.json',
        
        # Backup files
        'background/scheduler_backup*.py',
        
        # Setup scripts
        'setup_hedge_intel.*',
        'push_to_git.py',
        'launch.py',
        
        # Large text files
        'APP STRUCTURE.txt',
        'project_scan*.txt',
        'structure_*.txt',
        
        # Other unnecessary files
        'clear_queue.py',
        'import os.py',
        'document_pipeline.py',
        
        # PowerShell scripts
        '*.ps1'
    ]
    
    removed_count = 0
    for pattern in patterns_to_remove:
        for file in glob.glob(pattern, recursive=True):
            try:
                os.remove(file)
                print_info(f"Removed: {file}")
                removed_count += 1
            except Exception as e:
                print_warning(f"Could not remove {file}: {e}")
    
    print_success(f"Removed {removed_count} unnecessary files")

def verify_core_files():
    """Verify core files exist"""
    print_header("PHASE 1.3: Verifying Core Files")
    
    core_files = [
        'app.py',
        'admin.py',
        'run.py',
        'requirements.txt',
        'scrapers/ipo_scraper_fixed.py',
        'core/chat_engine.py',
        'background/scheduler.py',
        '.env'
    ]
    
    missing_files = []
    for file in core_files:
        if os.path.exists(file):
            print_success(f"Found: {file}")
        else:
            print_error(f"Missing: {file}")
            missing_files.append(file)
    
    if missing_files:
        print_warning(f"\n{len(missing_files)} core files are missing!")
        return False
    else:
        print_success("\nAll core files present!")
        return True

def create_directory_structure():
    """Create clean directory structure"""
    print_header("PHASE 2.1: Creating Directory Structure")
    
    directories = [
        'data/documents',
        'data/processed',
        'data/cache',
        'data/vectors',
        'static/css',
        'templates/admin',
        'templates/user',
        'logs',
        'exports',
        'core',
        'scrapers',
        'background',
        'ui/components'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print_info(f"Created/verified: {directory}")
    
    # Create __init__.py files
    init_dirs = [
        'data',
        'data/documents',
        'data/processed',
        'data/cache',
        'data/vectors',
        'core',
        'scrapers',
        'background',
        'ui',
        'ui/components'
    ]
    
    for directory in init_dirs:
        init_file = os.path.join(directory, '__init__.py')
        if not os.path.exists(init_file):
            Path(init_file).touch()
            print_info(f"Created: {init_file}")
    
    print_success("Directory structure ready")

def create_config_file():
    """Create configuration file"""
    print_header("PHASE 2.3: Creating Configuration")
    
    config_content = '''"""
Hedge Intelligence Configuration
Generated: 2025-06-05 13:15:41 UTC
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"
VECTOR_DIR = DATA_DIR / "vectors"
EXPORT_DIR = BASE_DIR / "exports"
LOG_DIR = BASE_DIR / "logs"

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Server Configuration
ADMIN_HOST = "0.0.0.0"
ADMIN_PORT = 8080
USER_HOST = "0.0.0.0"
USER_PORT = 8501

# Document Types
SUPPORTED_DOCUMENTS = {
    "S-1": ["S1", "S-1", "S1A", "S-1/A"],
    "424B4": ["424B4", "PROSPECTUS"],
    "LOCK_UP": ["LOCK-UP", "LOCKUP", "MARKET_STANDOFF"],
    "UNDERWRITING": ["UNDERWRITING", "PURCHASE_AGREEMENT"],
    "8-A": ["8-A", "8A", "FORM_8-A"]
}

# Processing Configuration
CHUNK_SIZE = 1000  # tokens
CHUNK_OVERLAP = 100  # tokens
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4"
VALIDATION_MODEL = "gemini-pro"

# Scheduler Configuration
SCRAPE_INTERVAL = 30  # minutes
DOCUMENT_CHECK_INTERVAL = 60  # minutes
MORNING_REPORT_TIME = "06:00"  # UTC

# ChromaDB Configuration
CHROMA_PERSIST_DIR = str(VECTOR_DIR)
COLLECTION_NAME = "ipo_documents"

# Report Configuration
REPORT_FONT_FAMILY = "Helvetica"
REPORT_MARGINS = {
    "top": 72,  # 1 inch
    "bottom": 72,
    "left": 90,  # 1.25 inch
    "right": 90
}
'''
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    
    print_success("Created config.py")

def create_requirements_file():
    """Update requirements.txt with exact versions"""
    print_header("Updating requirements.txt")
    
    requirements = '''# Core Framework
streamlit==1.31.0
fastapi==0.109.0
uvicorn==0.27.0

# AI/ML
openai==1.35.0
google-generativeai==0.3.2
chromadb==0.4.22
numpy==1.26.4
pandas==2.1.4

# Document Processing
beautifulsoup4==4.12.3
lxml==5.1.0
python-multipart==0.0.6

# PDF Generation
reportlab==4.0.4

# Async Operations
aiohttp==3.9.3
aiofiles==23.2.1

# Utilities
python-dotenv==1.0.0
requests==2.31.0
apscheduler==3.10.4

# Development
watchdog==3.0.0
'''
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print_success("Updated requirements.txt")

def migrate_existing_data():
    """Migrate existing data to proper locations"""
    print_header("Migrating Existing Data")
    
    migrations = [
        # Cache files
        ('data/cache/ipo_calendar.json', 'data/cache/ipo_calendar.json.bak'),
        ('data/cache/lockup_calendar.json', 'data/cache/lockup_calendar.json.bak'),
    ]
    
    for src, dst in migrations:
        if os.path.exists(src) and src != dst:
            shutil.copy2(src, dst)
            print_info(f"Backed up: {src} -> {dst}")
    
    # Count existing documents
    doc_count = len(glob.glob('data/documents/*.html'))
    pdf_count = len(glob.glob('data/documents/*.pdf'))
    json_count = len(glob.glob('data/processed/*.json'))
    
    print_success(f"Found {doc_count} HTML documents")
    print_success(f"Found {pdf_count} PDF documents")
    print_success(f"Found {json_count} processed JSON files")

def generate_summary_report():
    """Generate cleanup summary report"""
    print_header("CLEANUP SUMMARY")
    
    # Count remaining files
    py_files = len(glob.glob('**/*.py', recursive=True))
    total_size = sum(os.path.getsize(f) for f in glob.glob('**/*', recursive=True) if os.path.isfile(f))
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "python_files": py_files,
        "total_size_mb": round(total_size / 1024 / 1024, 2),
        "directories": len([d for d in glob.glob('**/', recursive=True)]),
        "status": "cleanup_complete"
    }
    
    with open('logs/cleanup_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nProject Status:")
    print(f"  Python files: {py_files}")
    print(f"  Total size: {summary['total_size_mb']} MB")
    print(f"  Directories: {summary['directories']}")
    
    print_success("\nCleanup complete! Project is ready for implementation.")
    print_info("\nNext steps:")
    print("  1. Run: pip install -r requirements.txt")
    print("  2. Verify .env file has API keys")
    print("  3. Run: python run.py")

def main():
    """Main cleanup function"""
    print(f"\nHEDGE INTELLIGENCE - CLEANUP AND RESTRUCTURE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"User: thorrobber22")
    
    # Ask for confirmation
    response = input(f"\n{Colors.WARNING}This will remove many files and restructure the project. Continue? (yes/no): {Colors.ENDC}")
    
    if response.lower() != 'yes':
        print("Cleanup cancelled.")
        return
    
    # Execute cleanup phases
    backup_dir = create_backup()
    if not backup_dir:
        print_error("Backup failed! Aborting cleanup.")
        return
    
    remove_unnecessary_files()
    
    if not verify_core_files():
        print_warning("\nSome core files are missing. Continue anyway? (yes/no): ")
        if input().lower() != 'yes':
            print("Cleanup aborted. Restore from backup if needed.")
            return
    
    create_directory_structure()
    create_config_file()
    create_requirements_file()
    migrate_existing_data()
    generate_summary_report()
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}Cleanup completed successfully!{Colors.ENDC}")
    print(f"Backup saved to: {backup_dir}")

if __name__ == "__main__":
    main()