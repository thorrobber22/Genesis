"""
prepare_github_upload.py - Prepare project for GitHub upload
Date: 2025-06-12 00:22:50 UTC
User: thorrobber22
"""

from pathlib import Path
from datetime import datetime

print("PREPARING HEDGE INTELLIGENCE FOR GITHUB")
print("="*80)
print(f"Date: 2025-06-12 00:22:50 UTC")
print(f"User: thorrobber22")
print("="*80)

# Create essential files for GitHub
files_to_create = []

# 1. Create .gitignore
gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Streamlit
.streamlit/secrets.toml

# Environment
.env
.env.local

# Data files (sensitive)
data/api_keys.json
data/user_sessions.json
data/admin_logs.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Archives
archive_*/
*_backup_*/
*.backup

# Logs
*.log
logs/

# Test files
test_*.py
*_test.py
*_demo.py

# Temporary
*.tmp
*.temp
"""

# 2. Create README.md
readme_content = """# Hedge Intelligence - IPO Intelligence Platform

Professional IPO tracking and analysis platform with AI-powered insights.

## Features

### Phase 1 - Core IPO Intelligence [COMPLETE]
- [x] UI Framework - Terminal-style interface
- [x] IPO Data Pipeline - Real-time SEC scraping
- [x] SEC Integration - Direct EDGAR API
- [x] Basic Chat - AI analysis
- [x] IPO Calendar - Track filings
- [x] Companies View - Detailed info
- [x] Metrics Dashboard - Market stats

### Phase 2 - Enhanced Analytics [IN PROGRESS]
- [ ] Financial Analysis
- [ ] Lockup Tracker
- [x] Watchlist
- [ ] Company Deep Dive

### Phase 3 - AI Intelligence [PLANNED]
- [ ] Smart Summaries
- [ ] Trend Detection
- [ ] Anomaly Alerts
- [ ] Report Generation

## Tech Stack
- **Frontend**: Streamlit
- **Backend**: Python 3.11+
- **AI**: OpenAI GPT-4
- **Data**: SEC EDGAR API
- **Styling**: Custom CSS (Terminal theme)

## Setup

1. Clone repository
```bash
git clone https://github.com/thorrobber22/hedge-intelligence.git
cd hedge-intelligence
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the app
```bash
streamlit run app.py
```
"""

# Write the files
Path(".gitignore").write_text(gitignore_content)
Path("README.md").write_text(readme_content)

print("[DONE] .gitignore and README.md created.")
