#!/usr/bin/env python3
"""
Fix missing dependencies and test what's working
Date: 2025-06-07 19:01:20 UTC
"""

import subprocess
import sys
import os
from pathlib import Path

def install_missing_packages():
    """Install missing Python packages"""
    
    required_packages = [
        'streamlit',
        'pandas',
        'openai',
        'google-generativeai',
        'chromadb',
        'PyPDF2',
        'python-docx',
        'reportlab',
        'humanize',
        'scrapy',
        'requests',
        'beautifulsoup4'
    ]
    
    print("Checking and installing required packages...")
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} already installed")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed")

if __name__ == "__main__":
    install_missing_packages()