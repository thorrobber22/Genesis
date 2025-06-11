#!/usr/bin/env python3
"""
Run Hedge Intelligence
"""

import subprocess
import sys
import time
import os

print("=" * 60)
print("STARTING HEDGE INTELLIGENCE")
print("=" * 60)

# Check for .env file
if not os.path.exists(".env"):
    print("\nERROR: .env file not found!")
    print("Please copy .env.template to .env and add your API keys")
    sys.exit(1)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Check API keys
if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "sk-your-openai-key-here":
    print("\nERROR: Please set your OPENAI_API_KEY in .env file")
    sys.exit(1)

# Start scheduler in background
print("\n1. Starting background scheduler...")
scheduler = subprocess.Popen([sys.executable, "-m", "background.scheduler"])
time.sleep(2)

# Start admin panel
print("\n2. Starting admin panel...")
admin = subprocess.Popen([sys.executable, "-m", "uvicorn", "admin:app", "--port", "8080"])
time.sleep(2)

# Start main app
print("\n3. Starting main app...")
print("\n" + "=" * 60)
print("HEDGE INTELLIGENCE IS READY!")
print("=" * 60)
print("\nUser Interface: http://localhost:8501")
print("Admin Panel: http://localhost:8080")
print("\nPress Ctrl+C to stop all services")

try:
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
except KeyboardInterrupt:
    print("\nShutting down...")
    scheduler.terminate()
    admin.terminate()
    print("\nGoodbye!")
