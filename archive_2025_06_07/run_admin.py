"""
Run Admin Panel
"""

import subprocess
import sys

print("Starting Hedge Intelligence Admin Panel...")
print("URL: http://localhost:8502")
print("-" * 60)

subprocess.run([
    sys.executable, "-m", "streamlit", "run", "admin_panel.py",
    "--server.port", "8502",
    "--server.headless", "true",
    "--theme.base", "dark"
])
