#!/usr/bin/env python3
"""
Hedge Intelligence - Super Quick Fix
Just copy your Gemini key to Google key
"""

from pathlib import Path

def copy_gemini_to_google():
    """Copy GEMINI_API_KEY value to GOOGLE_API_KEY"""
    env_path = Path(".env")
    
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    gemini_key = None
    
    # Find the Gemini key value
    for line in lines:
        if line.startswith("GEMINI_API_KEY="):
            gemini_key = line.split('=', 1)[1].strip()
            break
    
    if not gemini_key:
        print("❌ Couldn't find GEMINI_API_KEY")
        return
    
    # Update GOOGLE_API_KEY line
    for i, line in enumerate(lines):
        if line.startswith("GOOGLE_API_KEY="):
            lines[i] = f"GOOGLE_API_KEY={gemini_key}\n"
            break
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print("✅ Copied your Gemini API key to GOOGLE_API_KEY")
    print("🎉 YOU'RE 100% READY TO LAUNCH!")

if __name__ == "__main__":
    copy_gemini_to_google()