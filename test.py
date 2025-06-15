#!/usr/bin/env python3
"""
Git update script - commit and push recent changes
Date: 2025-06-15 14:25:33 UTC
User: thorrobber22
"""

import subprocess
import sys
from pathlib import Path

def run_git_command(cmd):
    """Run a git command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        print(f"✅ {cmd}")
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def update_github():
    """Commit and push all changes"""
    print("🚀 UPDATING GITHUB")
    print("=" * 50)
    
    # Check git status
    print("\n📊 Checking status...")
    run_git_command("git status --short")
    
    # Add all changes
    print("\n📁 Adding changes...")
    if not run_git_command("git add -A"):
        return
    
    # Commit with descriptive message
    commit_msg = """Fix: Frontend now displays real IPO data

- Fixed app.js syntax errors and duplicate functions
- Table now shows all 17 scraped IPOs correctly
- Added missing UI functions (showView, toggleChat, etc)
- IPO calendar loads on page refresh
- Navigation between views working
- Real-time data from ipo_calendar.json displayed"""
    
    print("\n💾 Committing...")
    if not run_git_command(f'git commit -m "{commit_msg}"'):
        print("   (No changes to commit)")
    
    # Push to GitHub
    print("\n📤 Pushing to GitHub...")
    if run_git_command("git push origin main"):
        print("\n✅ GitHub updated successfully!")
    else:
        print("\n⚠️  Push failed - you may need to pull first or set upstream")
        print("   Try: git pull origin main --rebase")
        print("   Then: git push origin main")

if __name__ == "__main__":
    update_github()