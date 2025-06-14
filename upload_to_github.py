"""
upload_to_github.py - Upload Hedge Intelligence to GitHub
Date: 2025-06-13 17:52:37 UTC
User: thorrobber22
Repository: thorrobber22/Genesis
"""

import os
import subprocess
import shutil
from pathlib import Path

print("🚀 HEDGE INTELLIGENCE - GITHUB UPLOAD SCRIPT")
print("="*60)
print("Repository: thorrobber22/Genesis")
print("="*60)

# Configuration
REPO_URL = "https://github.com/thorrobber22/Genesis.git"
LOCAL_PATH = Path.cwd()

def run_command(cmd, cwd=None):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

# Step 1: Create a temporary directory for git operations
print("\n📁 Setting up temporary directory...")
temp_dir = LOCAL_PATH / "temp_genesis"
if temp_dir.exists():
    shutil.rmtree(temp_dir)
temp_dir.mkdir()

# Step 2: Clone the repository
print("📥 Cloning repository...")
if not run_command(f"git clone {REPO_URL} {temp_dir}"):
    print("Failed to clone repository")
    exit(1)

# Step 3: Remove all existing content (except .git)
print("🗑️  Removing old content...")
for item in temp_dir.iterdir():
    if item.name != '.git':
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

# Step 4: Copy all Hedge Intelligence files
print("📤 Copying Hedge Intelligence files...")
ignore_patterns = {'.git', '__pycache__', '*.pyc', 'venv', 'temp_genesis', '.env'}

for item in LOCAL_PATH.iterdir():
    if item.name not in ignore_patterns:
        if item.is_dir():
            shutil.copytree(item, temp_dir / item.name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        else:
            shutil.copy2(item, temp_dir / item.name)

# Step 5: Create README using file write
print("📝 Creating README.md...")
readme_lines = [
    "# Hedge Intelligence - IPO Intelligence Terminal",
    "",
    "## 🚀 Overview",
    "Professional-grade IPO tracking and analysis platform with AI-powered insights.",
    "",
    "## ✨ Features",
    "- **Real-time IPO Calendar** - Track all upcoming IPOs",
    "- **SEC Integration** - Direct links to S-1, S-1/A, 424B4 filings",
    "- **AI Research Assistant** - Context-aware analysis powered by GPT-3.5/4",
    "- **Split-screen Interface** - Chat alongside data",
    "- **Dark Theme** - Professional trading terminal aesthetic",
    "",
    "## 🛠️ Technology Stack",
    "- **Frontend**: Streamlit",
    "- **AI Engine**: OpenAI GPT-3.5/4",
    "- **Data Sources**: SEC EDGAR API",
    "- **Theme**: Custom dark theme",
    "",
    "## 📦 Installation",
    "",
    "```bash",
    "# Clone repository",
    "git clone https://github.com/thorrobber22/Genesis.git",
    "cd Genesis",
    "",
    "# Create virtual environment",
    "python -m venv venv",
    "",
    "# Activate virtual environment",
    "# Windows:",
    "venv\\Scripts\\activate",
    "# Mac/Linux:",
    "source venv/bin/activate",
    "",
    "# Install dependencies",
    "pip install -r requirements.txt",
    "",
    "# Create .env file",
    'echo "OPENAI_API_KEY=your_key_here" > .env',
    "",
    "# Run application",
    "streamlit run app.py",
    "```",
    "",
    "## 📄 License",
    "Proprietary - All Rights Reserved",
    "",
    "## 👥 Team",
    "**Lead Developer**: thorrobber22",
    "**Project**: Hedge Intelligence",
]

with open(temp_dir / "README.md", "w", encoding="utf-8") as f:
    f.write('\n'.join(readme_lines))

# Step 6: Create .gitignore
print("📝 Creating .gitignore...")
gitignore_lines = [
    "# Virtual Environment",
    "venv/",
    "env/",
    "",
    "# Python",
    "__pycache__/",
    "*.py[cod]",
    "*.pyc",
    "",
    "# Environment variables",
    ".env",
    ".env.local",
    "",
    "# IDE",
    ".vscode/",
    ".idea/",
    "",
    "# OS",
    ".DS_Store",
    "Thumbs.db",
    "",
    "# Logs",
    "*.log",
    "",
    "# Temporary files",
    "temp_*",
    "*.tmp",
    "",
    "# Backups",
    "*_backup*",
    "*.bak",
]

with open(temp_dir / ".gitignore", "w", encoding="utf-8") as f:
    f.write('\n'.join(gitignore_lines))

# Step 7: Stage all files
print("\n📦 Staging files...")
os.chdir(temp_dir)
run_command("git add -A")

# Step 8: Commit
print("💾 Committing changes...")
commit_msg = "Hedge Intelligence v1.0 - IPO Intelligence Terminal with AI"
run_command(f'git commit -m "{commit_msg}"')

# Step 9: Push to GitHub
print("\n🚀 Pushing to GitHub...")
if run_command("git push origin main"):
    print("✅ Successfully pushed to GitHub!")
else:
    print("🔄 Trying master branch...")
    if run_command("git push origin master"):
        print("✅ Successfully pushed to GitHub (master branch)!")
    else:
        print("❌ Push failed. You may need to set up authentication.")
        print("   Try: git config --global credential.helper manager")

# Step 10: Cleanup
os.chdir(LOCAL_PATH)
print("\n🧹 Cleaning up temporary files...")
shutil.rmtree(temp_dir)

print("\n✅ UPLOAD COMPLETE!")
print(f"🌐 View your repository: https://github.com/thorrobber22/Genesis")