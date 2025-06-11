#!/usr/bin/env python3
import subprocess
import webbrowser
import time

print("Starting SEC Pipeline Admin...")
print("="*60)
print("Password: hedgeadmin2025")
print("="*60)

# Start admin
proc = subprocess.Popen(["streamlit", "run", "admin/admin_panel.py", "--server.port=8502"])

time.sleep(3)
webbrowser.open("http://localhost:8502")

print("\nAdmin running at: http://localhost:8502")
print("Press Ctrl+C to stop")

try:
    proc.wait()
except KeyboardInterrupt:
    print("\nStopping...")
    proc.terminate()
