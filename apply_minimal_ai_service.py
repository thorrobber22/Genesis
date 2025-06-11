#!/usr/bin/env python3
"""
Apply the minimal working AI Service
"""

from pathlib import Path
import shutil

def apply_minimal_service():
    """Copy the minimal service over"""
    print("🔧 APPLYING MINIMAL AI SERVICE")
    print("="*70)
    
    source = Path("services/backups/ai_service_minimal.py")
    dest = Path("services/ai_service.py")
    
    if not source.exists():
        print("❌ Minimal service not found!")
        return False
    
    # Backup current
    backup = Path("services/ai_service_broken.py")
    shutil.copy2(dest, backup)
    print(f"📄 Backed up current (broken) version to: {backup}")
    
    # Copy minimal version
    shutil.copy2(source, dest)
    print(f"✅ Copied minimal AI service to: {dest}")
    
    return True

def verify_api_key():
    """Check if OpenAI API key is set"""
    print("\n🔍 Checking OpenAI API key...")
    
    import os
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if api_key:
        print(f"  ✅ API key found (starts with: {api_key[:8]}...)")
    else:
        print("  ❌ No API key found!")
        print("  Set it with: set OPENAI_API_KEY=your-key-here")
        
        # Check .env file
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
            if 'OPENAI_API_KEY' in content:
                print("  ℹ️  Found in .env file - loading...")
                from dotenv import load_dotenv
                load_dotenv()

def main():
    print("🚀 FINAL AI SERVICE FIX")
    print("="*70)
    
    # Apply minimal service
    if apply_minimal_service():
        verify_api_key()
        
        print("\n✅ Minimal AI service applied!")
        print("\nRun: python test_complete_system.py")
    else:
        print("\n❌ Failed to apply minimal service")

if __name__ == "__main__":
    main()