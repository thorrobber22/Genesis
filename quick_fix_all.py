#!/usr/bin/env python3
"""
Hedge Intelligence - Final Fix for Remaining Issues
Date: 2025-06-09 00:24:45 UTC
Author: thorrobber22
"""

import subprocess
import sys
from pathlib import Path

def install_remaining_packages():
    """Install the 3 missing packages"""
    print("📦 Installing remaining packages...")
    
    # Force reinstall to ensure they work
    packages = [
        "google-generativeai",
        "beautifulsoup4", 
        "python-dotenv"
    ]
    
    for package in packages:
        print(f"\nInstalling {package}...")
        try:
            # Use --force-reinstall to ensure clean install
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--force-reinstall", package
            ])
            print(f"✅ {package} installed")
        except Exception as e:
            print(f"❌ Error installing {package}: {e}")

def fix_document_service_properly():
    """Fix the persistent document service bug"""
    print("\n🔧 Fixing document service bug (take 2)...")
    
    service_content = '''"""
Document Service - Fixed Version
Date: 2025-06-09 00:24:45 UTC
"""
import os
from pathlib import Path
from typing import List, Dict, Optional

class DocumentService:
    def __init__(self):
        self.doc_path = Path("data/sec_documents")
        
    def get_companies(self) -> List[str]:
        """Get list of available companies"""
        if not self.doc_path.exists():
            return []
        
        companies = [d.name for d in self.doc_path.iterdir() if d.is_dir()]
        return sorted(companies)
    
    def get_company_documents(self, company: str) -> List[str]:
        """Get list of documents for a company - returns list of strings"""
        company_path = self.doc_path / company
        if not company_path.exists():
            return []
        
        # Return list of filenames as STRINGS, not dicts
        documents = []
        for file in company_path.glob("*.html"):
            documents.append(file.name)  # Just the filename string
            
        return sorted(documents)
    
    def get_document_content(self, company: str, filename: str) -> Optional[str]:
        """Get content of a specific document"""
        # Handle if filename is accidentally a dict
        if isinstance(filename, dict):
            # Try to extract filename from dict
            filename = filename.get('filename', filename.get('name', str(filename)))
            
        # Ensure filename is a string
        filename = str(filename)
        
        filepath = self.doc_path / company / filename
        
        if not filepath.exists():
            return None
            
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None
    
    def search_documents(self, query: str) -> List[Dict]:
        """Search across all documents"""
        results = []
        query_lower = query.lower()
        
        for company in self.get_companies():
            for doc in self.get_company_documents(company):
                content = self.get_document_content(company, doc)
                if content and query_lower in content.lower():
                    results.append({
                        'company': company,
                        'document': doc,
                        'preview': content[:200] + '...'
                    })
                    
        return results[:10]  # Return top 10 results
'''
    
    # Write the fixed version
    with open("services/document_service.py", 'w', encoding='utf-8') as f:
        f.write(service_content)
    
    print("✅ Document service completely rewritten")

def check_google_api():
    """Remind about Google API key"""
    print("\n🔑 Google API Key Status:")
    
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
            
        if "your_google_api_key_here" in content:
            print("⚠️  GOOGLE_API_KEY still has placeholder value!")
            print("   Get your key from: https://makersuite.google.com/app/apikey")
            print("   Then update in .env file")
        else:
            print("✅ GOOGLE_API_KEY appears to be set")

def verify_installation():
    """Verify all packages are installed"""
    print("\n🧪 Verifying installations...")
    
    packages = {
        "google.generativeai": "Google Gemini",
        "bs4": "BeautifulSoup",
        "dotenv": "python-dotenv",
        "openai": "OpenAI",
        "streamlit": "Streamlit",
        "pandas": "Pandas"
    }
    
    all_good = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"✅ {name} working")
        except ImportError:
            print(f"❌ {name} not working")
            all_good = False
            
    return all_good

def main():
    print("🚀 HEDGE INTELLIGENCE - FINAL FIX")
    print("="*60)
    
    # 1. Install missing packages
    install_remaining_packages()
    
    # 2. Fix document service
    fix_document_service_properly()
    
    # 3. Check API key
    check_google_api()
    
    # 4. Verify everything
    all_good = verify_installation()
    
    print("\n" + "="*60)
    if all_good:
        print("✅ ALL ISSUES FIXED!")
        print("\nNext steps:")
        print("1. Update GOOGLE_API_KEY in .env (if needed)")
        print("2. Run: streamlit run hedge_intelligence.py")
    else:
        print("⚠️  Some issues remain - check errors above")

if __name__ == "__main__":
    main()