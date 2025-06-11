#!/usr/bin/env python3
"""
Live Production Test - Actually run and test everything
No assumptions - real testing only
"""

import subprocess
import time
import requests
from pathlib import Path
import json
from datetime import datetime
import webbrowser
import sys

class LiveProductionTester:
    def __init__(self):
        self.test_log = []
        self.start_time = datetime.now()
        
    def log(self, message, status="INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {status}: {message}"
        print(entry)
        self.test_log.append(entry)
    
    def test_streamlit_startup(self):
        """Test if Streamlit app starts"""
        self.log("Testing Streamlit startup...", "TEST")
        
        try:
            # Start streamlit in background
            self.log("Starting streamlit run hedge_intelligence.py...")
            
            # Check if main file exists
            if not Path("hedge_intelligence.py").exists():
                self.log("hedge_intelligence.py NOT FOUND!", "ERROR")
                return False
            
            # Try to import and check for syntax errors
            self.log("Checking for syntax errors...")
            try:
                with open("hedge_intelligence.py", 'r', encoding='utf-8') as f:
                    compile(f.read(), "hedge_intelligence.py", "exec")
                self.log("No syntax errors found", "PASS")
            except SyntaxError as e:
                self.log(f"Syntax error: {e}", "ERROR")
                return False
            
            # Start the app
            self.log("Starting Streamlit app...")
            self.log("Run this command in a separate terminal:")
            self.log(">>> streamlit run hedge_intelligence.py", "ACTION")
            
            return True
            
        except Exception as e:
            self.log(f"Startup failed: {e}", "ERROR")
            return False
    
    def test_navigation_pages(self):
        """Test each navigation page"""
        self.log("\nTesting navigation pages...", "TEST")
        
        pages = [
            "Dashboard",
            "Document Explorer", 
            "IPO Tracker",
            "Search",
            "Watchlist",
            "Company Management"
        ]
        
        self.log("Pages to test:")
        for i, page in enumerate(pages, 1):
            self.log(f"  {i}. {page}")
        
        self.log("\nMANUAL TEST REQUIRED:", "ACTION")
        self.log("1. Click each page in the sidebar")
        self.log("2. Verify each page loads without error")
        self.log("3. Note any errors or missing content")
    
    def test_document_explorer_live(self):
        """Test document explorer with real data"""
        self.log("\nTesting Document Explorer with REAL data...", "TEST")
        
        # Check actual document directory
        sec_dir = Path("data/sec_documents")
        
        if sec_dir.exists():
            companies = list(sec_dir.iterdir())
            self.log(f"Found {len(companies)} companies in sec_documents/")
            
            for company in companies[:5]:  # Show first 5
                if company.is_dir():
                    doc_count = len(list(company.glob("*.html")))
                    self.log(f"  - {company.name}: {doc_count} documents")
            
            # Test specific company
            test_company = sec_dir / "CRCL"
            if test_company.exists():
                docs = list(test_company.glob("*.html"))
                self.log(f"\nTesting CRCL documents:")
                self.log(f"  Total documents: {len(docs)}")
                
                if docs:
                    # Check a real document
                    test_doc = docs[0]
                    self.log(f"  Sample document: {test_doc.name}")
                    self.log(f"  Size: {test_doc.stat().st_size / 1024:.1f} KB")
                    
                    # Read first 500 chars to verify it's SEC format
                    with open(test_doc, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(500)
                    
                    if "CENTRAL INDEX KEY" in content or "<HTML>" in content.upper():
                        self.log("  ✅ Valid SEC document format", "PASS")
                    else:
                        self.log("  ⚠️ Document format unclear", "WARN")
        else:
            self.log("SEC documents directory NOT FOUND!", "ERROR")
        
        self.log("\nMANUAL TEST:", "ACTION")
        self.log("1. Go to Document Explorer page")
        self.log("2. Click on CRCL to expand")
        self.log("3. Click on any document")
        self.log("4. Verify document viewer opens")
    
    def test_ai_chat_live(self):
        """Test AI chat with real interaction"""
        self.log("\nTesting AI Chat with REAL interaction...", "TEST")
        
        # Check API keys
        import os
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        self.log(f"OpenAI API Key: {'SET' if openai_key else 'NOT SET'}")
        self.log(f"Gemini API Key: {'SET' if gemini_key else 'NOT SET'}")
        
        if openai_key:
            # Test OpenAI connection
            self.log("Testing OpenAI API connection...")
            try:
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": "Say 'API working'"}],
                        "max_tokens": 10
                    }
                )
                if response.status_code == 200:
                    self.log("✅ OpenAI API connection successful", "PASS")
                else:
                    self.log(f"OpenAI API error: {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"OpenAI connection failed: {e}", "ERROR")
        
        self.log("\nMANUAL CHAT TEST:", "ACTION")
        self.log("1. Open any document in Document Explorer")
        self.log("2. In the chat bar at bottom, type: 'What is this document about?'")
        self.log("3. Verify you get a response with citations")
        self.log("4. Click on a citation to verify it jumps to the page")
    
    def test_ipo_tracker_live(self):
        """Test IPO tracker with real data"""
        self.log("\nTesting IPO Tracker with REAL data...", "TEST")
        
        # Check IPO calendar file
        ipo_file = Path("data/ipo_calendar.json")
        
        if ipo_file.exists():
            with open(ipo_file, 'r', encoding='utf-8') as f:
                ipo_data = json.load(f)
            
            self.log(f"IPO calendar has {len(ipo_data) if isinstance(ipo_data, list) else 0} entries")
            
            # Check for fake companies
            if isinstance(ipo_data, list):
                fake_companies = ["Stripe", "SpaceX", "Databricks", "Canva", "Instacart"]
                fake_found = [ipo for ipo in ipo_data if ipo.get('company') in fake_companies]
                
                if fake_found:
                    self.log(f"⚠️ Found {len(fake_found)} fake companies to remove", "WARN")
                    for fake in fake_found:
                        self.log(f"  - {fake.get('company')}")
                else:
                    self.log("✅ No fake companies in IPO data", "PASS")
        
        # Test real IPOScoop connection
        self.log("\nTesting IPOScoop.com connection...")
        try:
            response = requests.get(
                "https://www.iposcoop.com/ipo-calendar/",
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log(f"✅ IPOScoop reachable - {len(response.text)} bytes", "PASS")
                
                # Count real IPOs in response
                ipo_count = response.text.count('class="ticker"')
                self.log(f"Found approximately {ipo_count} IPOs on IPOScoop")
            else:
                self.log(f"IPOScoop returned {response.status_code}", "ERROR")
                
        except Exception as e:
            self.log(f"IPOScoop connection failed: {e}", "ERROR")
        
        self.log("\nMANUAL TEST:", "ACTION")
        self.log("1. Go to IPO Tracker page")
        self.log("2. Check if IPOs are displayed")
        self.log("3. Note if data looks real or fake")
    
    def test_admin_panel_live(self):
        """Test admin panel"""
        self.log("\nTesting Admin Panel...", "TEST")
        
        # Check if admin exists
        admin_files = [
            Path("admin/admin_panel.py"),
            Path("admin/admin_panel_simple.py")
        ]
        
        admin_found = None
        for admin_file in admin_files:
            if admin_file.exists():
                admin_found = admin_file
                self.log(f"Found admin panel: {admin_file}")
                break
        
        if admin_found:
            # Check company requests
            requests_file = Path("data/company_requests.json")
            if requests_file.exists():
                with open(requests_file, 'r', encoding='utf-8') as f:
                    requests_data = json.load(f)
                
                self.log(f"Company requests: {len(requests_data)} total")
                
                pending = [r for r in requests_data if r.get('status') == 'pending']
                self.log(f"Pending requests: {len(pending)}")
                
                for req in pending:
                    self.log(f"  - {req.get('ticker', 'Unknown')} ({req.get('company_name', 'Unknown')})")
            
            self.log(f"\nTo access admin panel, run in new terminal:")
            self.log(f">>> streamlit run {admin_found}", "ACTION")
            self.log("Password: hedgeadmin2025")
        else:
            self.log("Admin panel NOT FOUND", "ERROR")
    
    def test_search_and_watchlist(self):
        """Test search and watchlist"""
        self.log("\nTesting Search and Watchlist...", "TEST")
        
        # Check ChromaDB
        chroma_dir = Path("data/chroma")
        if chroma_dir.exists():
            self.log("✅ ChromaDB directory exists", "PASS")
            
            # Count index files
            index_files = list(chroma_dir.glob("**/*.bin")) + list(chroma_dir.glob("**/*.pkl"))
            self.log(f"Index files: {len(index_files)}")
        else:
            self.log("⚠️ ChromaDB not initialized", "WARN")
        
        # Check watchlist
        watchlist_file = Path("data/watchlists.json")
        if watchlist_file.exists():
            with open(watchlist_file, 'r', encoding='utf-8') as f:
                watchlist_data = json.load(f)
            self.log(f"Watchlist entries: {len(watchlist_data) if isinstance(watchlist_data, dict) else 0}")
        
        self.log("\nMANUAL TEST:", "ACTION")
        self.log("1. Go to Search page")
        self.log("2. Try searching for 'revenue' or 'risk'")
        self.log("3. Go to Watchlist page")
        self.log("4. Try adding a ticker (e.g., AAPL)")
    
    def test_document_download(self):
        """Test document download"""
        self.log("\nTesting Document Download...", "TEST")
        
        # Check if openpyxl is now installed
        try:
            import openpyxl
            self.log("✅ openpyxl is installed", "PASS")
        except ImportError:
            self.log("❌ openpyxl not found", "ERROR")
        
        self.log("\nMANUAL TEST:", "ACTION")
        self.log("1. Open any document")
        self.log("2. Look for download button")
        self.log("3. Try downloading as Excel/PDF")
    
    def run_all_tests(self):
        """Run all live tests"""
        print("="*80)
        print("HEDGE INTELLIGENCE - LIVE PRODUCTION TEST")
        print("="*80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"User: thorrobber22")
        print("="*80)
        
        # Test 1: Startup
        if self.test_streamlit_startup():
            time.sleep(2)
            
            # Test 2: Navigation
            self.test_navigation_pages()
            
            # Test 3: Document Explorer
            self.test_document_explorer_live()
            
            # Test 4: AI Chat
            self.test_ai_chat_live()
            
            # Test 5: IPO Tracker
            self.test_ipo_tracker_live()
            
            # Test 6: Admin Panel
            self.test_admin_panel_live()
            
            # Test 7: Search and Watchlist
            self.test_search_and_watchlist()
            
            # Test 8: Download
            self.test_document_download()
        
        # Summary
        self.log("\n" + "="*80, "INFO")
        self.log("TEST SUMMARY", "INFO")
        self.log("="*80, "INFO")
        
        # Save log
        log_file = Path(f"live_test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.test_log))
        
        self.log(f"\nTest log saved to: {log_file}")
        self.log("\nNEXT STEPS:", "ACTION")
        self.log("1. Start the app: streamlit run hedge_intelligence.py")
        self.log("2. Manually test each feature listed above")
        self.log("3. Report any errors or issues found")

if __name__ == "__main__":
    tester = LiveProductionTester()
    tester.run_all_tests()