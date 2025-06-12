"""
create_minimal_gitignore.py - Minimal gitignore to push almost everything
Date: 2025-06-12 00:31:56 UTC
User: thorrobber22
"""

print("CREATING MINIMAL .gitignore")
print("="*60)
print("Date: 2025-06-12 00:31:56 UTC")
print("User: thorrobber22")
print("="*60)

# Only exclude truly sensitive/unnecessary files
gitignore_content = """# Virtual Environment (too large)
venv/
env/
.venv/

# Python cache (regenerated)
__pycache__/
*.pyc
.pytest_cache/

# Environment secrets
.env
.streamlit/secrets.toml

# OS files
.DS_Store
Thumbs.db
desktop.ini

# IDE
.vscode/settings.json
.idea/

# Large data files (if any)
*.db
*.sqlite
*.log

# But INCLUDE everything else for visibility
# !data/*.json
# !archive_*/
"""

with open('.gitignore', 'w') as f:
    f.write(gitignore_content)

print("[CREATED] Minimal .gitignore")
print("\nThis will push:")
print("- All Python files (including tests, backups)")
print("- All data JSON files")
print("- All archive folders")
print("- Everything except venv and secrets")