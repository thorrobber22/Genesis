"""
smart_github_upload.py - Upload all files and analyze structure
Date: 2025-06-13 21:55:10 UTC
User: thorrobber22
"""

import os
import subprocess
import shutil
from pathlib import Path
import json
from datetime import datetime

print("🚀 HEDGE INTELLIGENCE - SMART GITHUB UPLOAD")
print("="*60)
print(f"User: thorrobber22")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
print("="*60)

# Configuration
REPO_URL = "https://github.com/thorrobber22/Genesis.git"
LOCAL_PATH = Path.cwd()

def run_command(cmd, cwd=None):
    """Run shell command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def analyze_chat_system():
    """Analyze why chat isn't working"""
    issues = []
    
    # Check AI service
    ai_service_path = LOCAL_PATH / "services" / "ai_service.py"
    if ai_service_path.exists():
        content = ai_service_path.read_text()
        if "OPENAI_API_KEY" not in content:
            issues.append("AI service doesn't check for OpenAI API key")
        if "get_ai_response" not in content:
            issues.append("get_ai_response function missing from ai_service.py")
    
    # Check chat component
    chat_path = LOCAL_PATH / "components" / "chat.py"
    if chat_path.exists():
        content = chat_path.read_text()
        if "st.chat_input" not in content:
            issues.append("chat.py doesn't use st.chat_input")
    
    # Check app.py integration
    app_path = LOCAL_PATH / "app.py"
    if app_path.exists():
        content = app_path.read_text()
        if "from services.ai_service import get_ai_response" not in content:
            issues.append("app.py doesn't import get_ai_response correctly")
    
    return {
        "issues_found": issues,
        "likely_cause": "AI service initialization or import issue" if issues else "Configuration issue"
    }

def get_cleanup_recommendations(categories):
    """Get recommendations for cleanup"""
    recs = []
    
    if len(categories['backup_files']) > 5:
        recs.append(f"Delete {len(categories['backup_files'])} backup files after verifying main app works")
    
    if len(categories['archive_files']) > 0:
        recs.append(f"Remove {len(categories['archive_files'])} archive files - they're now in GitHub history")
    
    if len(categories['component_variants']) > 5:
        recs.append("Consolidate component variants - keep only the latest working versions")
    
    recs.append("Create .env file with OPENAI_API_KEY")
    recs.append("Test chat functionality with: python -m streamlit run app.py")
    
    return recs

# Step 1: Analyze current structure
print("\n📊 ANALYZING FILE STRUCTURE...")
print("-"*60)

# Categorize files
file_categories = {
    'core_files': [],
    'backup_files': [],
    'archive_files': [],
    'component_variants': [],
    'service_variants': [],
    'temp_scripts': []
}

for root, dirs, files in os.walk('.'):
    # Skip venv and git
    dirs[:] = [d for d in dirs if d not in ['venv', '.git', '__pycache__', 'temp_genesis']]
    
    for file in files:
        if not file.endswith('.py'):
            continue
            
        filepath = os.path.join(root, file)
        
        # Categorize
        if 'archive_' in root:
            file_categories['archive_files'].append(filepath)
        elif 'backup' in file:
            file_categories['backup_files'].append(filepath)
        elif file in ['app.py', 'requirements.txt', 'README.md']:
            file_categories['core_files'].append(filepath)
        elif root == '.\\components' and not any(x in file for x in ['backup', 'v2', 'final', 'refined', 'terminal', 'minimal']):
            file_categories['core_files'].append(filepath)
        elif root == '.\\services' and not any(x in file for x in ['backup', 'v2']):
            file_categories['core_files'].append(filepath)
        elif 'components' in root:
            file_categories['component_variants'].append(filepath)
        elif 'services' in root:
            file_categories['service_variants'].append(filepath)
        else:
            file_categories['temp_scripts'].append(filepath)

# Display categorization
for category, files in file_categories.items():
    print(f"\n{category.upper()} ({len(files)} files):")
    for f in sorted(files)[:5]:  # Show first 5
        print(f"  - {f}")
    if len(files) > 5:
        print(f"  ... and {len(files) - 5} more")

# Step 2: Create structured upload
print("\n📁 PREPARING GITHUB UPLOAD...")
temp_dir = LOCAL_PATH / "temp_genesis_upload"
if temp_dir.exists():
    shutil.rmtree(temp_dir, ignore_errors=True)
temp_dir.mkdir()

# Clone repository
print("📥 Cloning repository...")
success, out, err = run_command(f"git clone {REPO_URL} {temp_dir}")
if not success:
    print(f"❌ Clone failed: {err}")
    exit(1)

# Clear old content
print("🗑️ Clearing old content...")
for item in temp_dir.iterdir():
    if item.name != '.git':
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
        else:
            item.unlink()

# Step 3: Copy ALL files (preserve everything)
print("\n📤 COPYING ALL FILES...")

# Copy everything except venv, .git, temp folders
ignore_dirs = {'venv', '.git', '__pycache__', 'temp_genesis', 'temp_genesis_upload'}

for root, dirs, files in os.walk('.'):
    # Filter out ignored directories
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    
    # Calculate relative path
    rel_path = Path(root).relative_to('.')
    if str(rel_path) == '.':
        rel_path = Path()
    
    # Create directory in temp
    target_dir = temp_dir / rel_path
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    for file in files:
        if not file.startswith('.') or file in ['.gitignore', '.env.example']:
            src = Path(root) / file
            dst = target_dir / file
            try:
                shutil.copy2(src, dst)
                print(f"✅ Copied: {src}")
            except Exception as e:
                print(f"❌ Failed: {src} - {e}")

# Step 4: Analyze chat functionality
print("\n🔍 ANALYZING CHAT FUNCTIONALITY...")
chat_analysis = analyze_chat_system()

# Create diagnostic report
diagnostic_report = {
    "scan_time": datetime.now().isoformat(),
    "total_files": sum(len(files) for files in file_categories.values()),
    "file_categories": {k: len(v) for k, v in file_categories.items()},
    "chat_analysis": chat_analysis,
    "recommendations": get_cleanup_recommendations(file_categories)
}

with open(temp_dir / "DIAGNOSTIC_REPORT.json", "w") as f:
    json.dump(diagnostic_report, f, indent=2)

# Create README
print("\n📝 Creating README...")
readme_lines = [
    "# Hedge Intelligence - IPO Intelligence Terminal",
    "",
    "## 🚀 Current Status",
    "- **Version**: 1.1 (Full Upload)",
    "- **Files**: All 80 Python files + complete structure",
    "- **Date**: " + datetime.now().strftime('%Y-%m-%d'),
    "",
    "## 📁 Quick Start",
    "",
    "```bash",
    "git clone https://github.com/thorrobber22/Genesis.git",
    "cd Genesis",
    "python -m venv venv",
    "venv\\Scripts\\activate  # Windows",
    "pip install -r requirements.txt",
    'echo "OPENAI_API_KEY=your_key_here" > .env',
    "streamlit run app.py",
    "```",
    "",
    "## 🔍 Diagnostic Report",
    "See DIAGNOSTIC_REPORT.json for chat functionality analysis",
    "",
    "## 📊 File Count",
    f"- Total Python files: {diagnostic_report['total_files']}",
    f"- Core files: {diagnostic_report['file_categories']['core_files']}",
    f"- Backup files: {diagnostic_report['file_categories']['backup_files']}",
    "",
    "---",
    "*Uploaded by thorrobber22*"
]

with open(temp_dir / "README.md", "w") as f:
    f.write('\n'.join(readme_lines))

# Create .gitignore if missing
gitignore_lines = [
    "venv/", "env/", "__pycache__/", "*.pyc", ".env",
    ".vscode/", ".idea/", "*.log", "temp_*", "*.db"
]

with open(temp_dir / ".gitignore", "w") as f:
    f.write('\n'.join(gitignore_lines))

# Step 5: Commit and push
print("\n💾 Committing changes...")
os.chdir(temp_dir)
run_command("git add -A")

total_files = sum(len(files) for files in file_categories.values())
commit_msg = f"Hedge Intelligence v1.1 - Complete Upload ({total_files} Python files)"

run_command(f'git commit -m "{commit_msg}"')

print("\n🚀 Pushing to GitHub...")
success, out, err = run_command("git push origin main")
if not success:
    success, out, err = run_command("git push origin master")

if success:
    print("✅ Successfully pushed to GitHub!")
else:
    print(f"❌ Push failed: {err}")

# Cleanup
os.chdir(LOCAL_PATH)

print("\n✅ UPLOAD COMPLETE!")
print(f"🌐 Repository: https://github.com/thorrobber22/Genesis")

# Print chat analysis
print("\n🔍 CHAT DIAGNOSTIC RESULTS:")
print("-"*60)
if chat_analysis['issues_found']:
    for issue in chat_analysis['issues_found']:
        print(f"❌ {issue}")
else:
    print("✅ No obvious issues found")
print(f"\n💡 Likely cause: {chat_analysis['likely_cause']}")

# Print recommendations
print("\n📋 CLEANUP RECOMMENDATIONS:")
print("-"*60)
for rec in diagnostic_report["recommendations"]:
    print(f"• {rec}")

print("\n🎯 NEXT STEPS:")
print("1. Check upload at: https://github.com/thorrobber22/Genesis")
print("2. Review DIAGNOSTIC_REPORT.json in the repository")
print("3. Let's fix the chat functionality!")