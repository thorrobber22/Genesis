#!/usr/bin/env python3
import subprocess
import webbrowser
import time

print("Starting Hedge Intelligence...")
print("="*60)

# Start main app
proc = subprocess.Popen(["streamlit", "run", "hedge_intelligence.py"])

time.sleep(3)
webbrowser.open("http://localhost:8501")

print("\nApp running at: http://localhost:8501")
print("Press Ctrl+C to stop")

try:
    proc.wait()
except KeyboardInterrupt:
    print("\nStopping...")
    proc.terminate()
