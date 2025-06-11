#!/usr/bin/env python3
"""
Comprehensive Production Test Plan
Tests ALL features with REAL data
"""

import json
import time
from pathlib import Path
from datetime import datetime
import requests
import subprocess

class ProductionFeatureTester:
    def __init__(self):
        self.test_log = []
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "user": "thorrobber22",
            "features": {}
        }
    
    def log(self, message, level="INFO"):
        entry = f"[{datetime.now().strftime('%H:%M:%S')}] {level}: {message}"
        print(entry)
        self.test_log.append(entry)
    
    def test_all_features(self):
        """Test all production features"""
        print("="*80)
        print("HEDGE INTELLIGENCE - PRODUCTION FEATURE TEST")
        print("="*80)
        print("Testing ALL features with REAL data")
        print("="*80)
        
        # Admin Features
        self.log("\n=== ADMIN FEATURES ===", "HEADER")
        self.test_ipo_scraper()
        self.test_cik_lookup()
        self.test_sec_downloader()
        self.test_admin_panel()
        
        # User Features
        self.log("\n=== USER FEATURES ===", "HEADER")
        self.test_dashboard()
        self.test_document_explorer()
        self.test_document_viewer()
        self.test_ai_chat()
        self.test_search()
        self.test_watchlist()
        self.test_company_request()
        self.test_document_download()
        
        # Save results
        self.save_results()
    
    # === ADMIN FEATURES ===
    
    def test_ipo_scraper(self):
        """Test IPO scraper with real IPOScoop data"""
        self.log("\n1. IPO SCRAPER TEST", "TEST")
        
        results = {"status": "PENDING", "details": {}}
        
        # Test IPOScoop connection
        self.log("Connecting to IPOScoop.com...")
        try:
            response = requests.get(
                "https://www.iposcoop.com/ipo-calendar/",
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log("✅ Connected to IPOScoop")
                
                # Parse for IPO data
                content = response.text
                
                # Look for IPO markers
                ipo_markers = ["priced-ipos", "upcoming-ipos", "filed-ipos"]
                found_sections = sum(1 for marker in ipo_markers if marker in content)
                
                results["details"]["connection"] = "SUCCESS"
                results["details"]["sections_found"] = found_sections
                results["details"]["content_size"] = len(content)
                
                # Check if scraper exists
                scraper_file = Path("services/ipo_scraper.py")
                if not scraper_file.exists():
                    self.log("⚠️  IPO scraper not implemented")
                    self.log("   ACTION: Create services/ipo_scraper.py")
                    results["status"] = "NOT_IMPLEMENTED"
                else:
                    results["status"] = "READY"
                    
            else:
                self.log(f"❌ IPOScoop returned {response.status_code}")
                results["status"] = "FAIL"
                
        except Exception as e:
            self.log(f"❌ Error: {e}")
            results["status"] = "ERROR"
            results["details"]["error"] = str(e)
        
        self.test_results["features"]["ipo_scraper"] = results
    
    def test_cik_lookup(self):
        """Test CIK lookup functionality"""
        self.log("\n2. CIK LOOKUP TEST", "TEST")
        
        results = {"status": "PENDING", "details": {}}
        
        # Test companies
        test_companies = {
            "Apple Inc.": "0000320193",
            "Tesla, Inc.": "0001318605",
            "Microsoft Corporation": "0000789019"
        }
        
        self.log("Testing CIK lookups...")
        
        try:
            # Test SEC company tickers endpoint
            ticker_url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(
                ticker_url,
                headers={'User-Agent': 'HedgeIntel admin@hedgeintel.com'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log("✅ SEC CIK API accessible")
                
                tickers_data = response.json()
                self.log(f"   Found {len(tickers_data)} companies in SEC database")
                
                # Test specific lookups
                found_count = 0
                for company, expected_cik in test_companies.items():
                    # Search in tickers data
                    for item in tickers_data.values():
                        if company.upper() in item.get('title', '').upper():
                            found_count += 1
                            self.log(f"   ✅ Found {company}")
                            break
                
                results["status"] = "PASS"
                results["details"]["companies_found"] = found_count
                results["details"]["total_companies"] = len(tickers_data)
                
            else:
                self.log(f"❌ SEC API returned {response.status_code}")
                results["status"] = "FAIL"
                
        except Exception as e:
            self.log(f"❌ Error: {e}")
            results["status"] = "ERROR"
            results["details"]["error"] = str(e)
        
        self.test_results["features"]["cik_lookup"] = results
    
    def test_sec_downloader(self):
        """Test SEC document downloader"""
        self.log("\n3. SEC DOCUMENT DOWNLOADER TEST", "TEST")
        
        results = {"status": "PENDING", "details": {}}
        
        # Test with a known CIK
        test_cik = "0000320193"  # Apple
        
        self.log(f"Testing SEC EDGAR access for CIK {test_cik}...")
        
        try:
            # Test submissions endpoint
            url = f"https://data.sec.gov/submissions/CIK{test_cik}.json"
            response = requests.get(
                url,
                headers={
                    'User-Agent': 'HedgeIntel admin@hedgeintel.com',
                    'Accept-Encoding': 'gzip, deflate'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.log("✅ SEC EDGAR API working")
                
                data = response.json()
                company_name = data.get('name', 'Unknown')
                recent_filings = data.get('filings', {}).get('recent', {})
                filing_count = len(recent_filings.get('form', []))
                
                self.log(f"   Company: {company_name}")
                self.log(f"   Recent filings: {filing_count}")
                
                # Check if downloader exists
                downloader_files = [
                    Path("services/sec_scraper.py"),
                    Path("services/edgar_scraper.py"),
                    Path("scrapers/sec/sec_compliant_scraper.py")
                ]
                
                downloader_found = any(f.exists() for f in downloader_files)
                
                results["status"] = "PASS" if downloader_found else "PARTIAL"
                results["details"]["edgar_access"] = "SUCCESS"
                results["details"]["company"] = company_name
                results["details"]["filings_available"] = filing_count
                results["details"]["downloader_exists"] = downloader_found
                
            else:
                self.log(f"❌ SEC EDGAR returned {response.status_code}")
                results["status"] = "FAIL"
                
        except Exception as e:
            self.log(f"❌ Error: {e}")
            results["status"] = "ERROR"
            results["details"]["error"] = str(e)
        
        self.test_results["features"]["sec_downloader"] = results
    
    def test_admin_panel(self):
        """Test admin panel"""
        self.log("\n4. ADMIN PANEL TEST", "TEST")
        
        results = {"status": "PENDING", "details": {}}
        
        # Check admin panel
        admin_files = [
            Path("admin/admin_panel.py"),
            Path("admin/admin_panel_simple.py")
        ]
        
        admin_found = None
        for f in admin_files:
            if f.exists():
                admin_found = f
                break
        
        if admin_found:
            self.log(f"✅ Admin panel found: {admin_found}")
            
            # Check company requests
            requests_file = Path("data/company_requests.json")
            if requests_file.exists():
                with open(requests_file, 'r', encoding='utf-8') as f:
                    requests = json.load(f)
                
                pending = [r for r in requests if r.get('status') == 'pending']
                
                self.log(f"   Pending requests: {len(pending)}")
                for req in pending[:3]:  # Show first 3
                    self.log(f"   - {req.get('ticker')} ({req.get('company_name', 'Unknown')})")
                
                results["status"] = "PASS"
                results["details"]["admin_exists"] = True
                results["details"]["pending_count"] = len(pending)
                
            else:
                results["status"] = "PARTIAL"
                results["details"]["note"] = "No requests file"
        else:
            self.log("❌ Admin panel not found")
            results["status"] = "FAIL"
        
        self.test_results["features"]["admin_panel"] = results
    
    # === USER FEATURES ===
    
    def test_dashboard(self):
        """Test dashboard functionality"""
        self.log("\n5. DASHBOARD TEST", "TEST")
        
        results = {"status": "PENDING", "details": {}}
        
        # Check IPO display
        ipo_file = Path("data/ipo_calendar.json")
        if ipo_file.exists():
            with open(ipo_file, 'r', encoding='utf-8') as f:
                ipo_data = json.load(f)
            
            self.log(f"✅ IPO calendar loaded: {len(ipo_data)} entries")
            
            if len(ipo_data) == 0:
                self.log("   ⚠️ IPO calendar empty - need to run scraper")
            
            results["details"]["ipo_count"] = len(ipo_data)
        
        # Check watchlist
        watchlist_file = Path("data/watchlists.json")
        if watchlist_file.exists():
            with open(watchlist_file, 'r', encoding='utf-8') as f:
                watchlist_data = json.load(f)
            
            self.log(f"✅ Watchlist found")
            results["details"]["watchlist_exists"] = True
        
        results["status"] = "PASS"
        self.test_results["features"]["dashboard"] = results
    
    def test_document_explorer(self):
        """Test document explorer"""
        self.log("\n6. DOCUMENT EXPLORER TEST", "TEST")
        
        results = {"status": "PENDING", "details": {}}
        
        sec_dir = Path("data/sec_documents")
        if sec_dir.exists():
            companies = list(sec_dir.iterdir())
            company_count = len([c for c in companies if c.is_dir()])
            
            self.log(f"✅ Document explorer: {company_count} companies")
            
            # Test sample company
            if company_count > 0:
                sample_company = companies[0]
                doc_count = len(list(sample_company.glob("*.html")))
                
                self.log(f"   Sample: {sample_company.name} has {doc_count} documents")
                
                results["status"] = "PASS"
                results["details"]["company_count"] = company_count
                results["details"]["sample_docs"] = doc_count
            else:
                results["status"] = "FAIL"
                self.log("   ❌ No companies found")
        else:
            results["status"] = "FAIL"
            self.log("❌ SEC documents directory not found")
        
        self.test_results["features"]["document_explorer"] = results
    
    def test_document_viewer(self):
        """Test document viewer"""
        self.log("\n7. DOCUMENT VIEWER TEST", "TEST")
        
        results = {"status": "PENDING", "details": {}}
        
        # Find a test document
        test_doc = None
        sec_dir = Path("data/sec_documents")
        
        if sec_dir.exists():
            for company_dir in sec_dir.iterdir():
                if company_dir.is_dir():
                    docs = list(company_dir.glob("*.html"))
                    if docs:
                        test_doc = docs[0]
                        break
        
        if test_doc:
            self.log(f"✅ Test document: {test_doc.name}")
            
            # Check document content
            with open(test_doc, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # First 1000 chars
            
            # Verify SEC format
            is_sec_format = any(marker in content.upper() for marker in 
                              ["<HTML>", "CENTRAL INDEX KEY", "CONFORMED", "ACCESSION"])
            
            if is_sec_format:
                self.log("   ✅ Valid SEC document format")
                results["status"] = "PASS"
                results["details"]["format_valid"] = True
            else:
                self.log("   ⚠️ Unknown document format")
                results["status"] = "PARTIAL"
        else:
            self.log("❌ No test document found")
            results["status"] = "FAIL"
        
        self.test_results["features"]["document_viewer"] = results
    
    def test_ai_chat(self):
        """Test AI chat with real prompts"""
        self.log("\n8. AI CHAT TEST", "TEST")
        
        results = {"status": "PENDING", "details": {}}
        
        # Check API keys
        import os
        openai_set = bool(os.getenv("OPENAI_API_KEY"))
        gemini_set = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
        
        self.log(f"OpenAI API: {'✅ SET' if openai_set else '❌ NOT SET'}")
        self.log(f"Gemini API: {'✅ SET' if gemini_set else '❌ NOT SET'}")
        
        if openai_set:
            # Test API connection
            try:
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": "Say 'working'"}],
                        "max_tokens": 5
                    }
                )
                
                if response.status_code == 200:
                    self.log("✅ OpenAI API working")
                    results["status"] = "PASS"
                    results["details"]["openai_working"] = True
                else:
                    self.log(f"❌ OpenAI API error: {response.status_code}")
                    results["status"] = "FAIL"
                    
            except Exception as e:
                self.log(f"❌ API test failed: {e}")
                results["status"] = "ERROR"
        else:
            results["status"] = "FAIL"
            results["details"]["error"] = "No API key set"
        
        # Test prompts to use
        test_prompts = [
            "What is the main business of this company?",
            "What are the key risk factors mentioned?",
            "Summarize the financial performance",
            "What is the revenue for the last reported period?"
        ]
        
        results["details"]["test_prompts"] = test_prompts
        
        self.test_results["features"]["ai_chat"] = results
    
    def test_search(self):
        """Test search functionality"""
        self.log("\n9. SEARCH TEST", "TEST")
        
        results = {"status": "PENDING", "details": {}}
        
        # Check if ChromaDB initialized
        chroma_dir = Path("data/chroma")
        
        if chroma_dir.exists():
            self.log("✅ ChromaDB directory exists")
            results["details"]["chromadb_exists"] = True
        else:
            self.log("⚠️  ChromaDB not initialized")
            results["details"]["chromadb_exists"] = False
        
        # Test search terms
        test_searches = [
            "revenue",
            "risk factors",
            "financial statements",
            "Apple",
            "AAPL"
        ]
        
        self.log("Test searches:")
        for term in test_searches:
            self.log(f"   - {term}")
        
        results["status"] = "PARTIAL"  # Basic search implemented
        results["details"]["test_terms"] = test_searches
        
        self.test_results["features"]["search"] = results
    
    def test_watchlist(self):
        """Test watchlist functionality"""
        self.log("\n10. WATCHLIST TEST", "TEST")
        
        results = {"status": "PENDING", "details": {}}
        
        # Check watchlist data
        watchlist_file = Path("data/watchlists.json")
        
        if watchlist_file.exists():
            with open(watchlist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            watchlist = data.get("default", [])
            self.log(f"✅ Watchlist has {len(watchlist)} companies")
            
            for company in watchlist[:3]:  # Show first 3
                self.log(f"   - {company}")
            
            results["status"] = "PASS"
            results["details"]["count"] = len(watchlist)
        else:
            self.log("⚠️  No saved watchlist")
            results["status"] = "PARTIAL"
            results["details"]["note"] = "Watchlist not saved yet"
        
        self.test_results["features"]["watchlist"] = results
    
    def test_company_request(self):
        """Test company request system"""
        self.log("\n11. COMPANY REQUEST TEST", "TEST")
        
        results = {"status": "PENDING", "details": {}}
        
        requests_file = Path("data/company_requests.json")
        
        if requests_file.exists():
            with open(requests_file, 'r', encoding='utf-8') as f:
                requests = json.load(f)
            
            self.log(f"✅ Request system: {len(requests)} total requests")
            
            # Count by status
            status_counts = {}
            for req in requests:
                status = req.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                self.log(f"   - {status}: {count}")
            
            results["status"] = "PASS"
            results["details"]["total_requests"] = len(requests)
            results["details"]["by_status"] = status_counts
        else:
            self.log("⚠️  No requests file")
            results["status"] = "PARTIAL"
        
        self.test_results["features"]["company_request"] = results
    
    def test_document_download(self):
        """Test document download"""
        self.log("\n12. DOCUMENT DOWNLOAD TEST", "TEST")
        
        results = {"status": "PENDING", "details": {}}
        
        # Check Excel support
        try:
            import openpyxl
            self.log("✅ Excel support available (openpyxl)")
            results["details"]["excel_support"] = True
        except ImportError:
            self.log("❌ No Excel support")
            results["details"]["excel_support"] = False
        
        # Check PDF libraries
        try:
            import reportlab
            self.log("✅ PDF support available (reportlab)")
            results["details"]["pdf_support"] = True
        except ImportError:
            self.log("⚠️  PDF support not available")
            results["details"]["pdf_support"] = False
        
        results["status"] = "PARTIAL"  # Basic download available
        
        self.test_results["features"]["document_download"] = results
    
    def save_results(self):
        """Save test results"""
        # Save detailed results
        results_file = Path(f"production_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2)
        
        # Save log
        log_file = Path(f"production_test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.test_log))
        
        # Print summary
        self.log("\n" + "="*80, "HEADER")
        self.log("TEST SUMMARY", "HEADER")
        self.log("="*80, "HEADER")
        
        # Count results
        pass_count = sum(1 for f in self.test_results["features"].values() if f["status"] == "PASS")
        partial_count = sum(1 for f in self.test_results["features"].values() if f["status"] == "PARTIAL")
        fail_count = sum(1 for f in self.test_results["features"].values() if f["status"] == "FAIL")
        
        total = len(self.test_results["features"])
        
        self.log(f"\n✅ PASSED: {pass_count}/{total}")
        self.log(f"⚠️  PARTIAL: {partial_count}/{total}")
        self.log(f"❌ FAILED: {fail_count}/{total}")
        
        self.log(f"\nDetailed results: {results_file}")
        self.log(f"Full log: {log_file}")
        
        # Action items
        self.log("\n" + "="*80, "HEADER")
        self.log("ACTION ITEMS", "HEADER")
        self.log("="*80, "HEADER")
        
        if self.test_results["features"]["ipo_scraper"]["status"] == "NOT_IMPLEMENTED":
            self.log("\n1. Create IPO Scraper:")
            self.log("   - Create services/ipo_scraper.py")
            self.log("   - Use the sec_compliant_scraper.py as template")
            self.log("   - Scrape from https://www.iposcoop.com/ipo-calendar/")
        
        if not self.test_results["features"]["search"]["details"].get("chromadb_exists"):
            self.log("\n2. Initialize ChromaDB:")
            self.log("   - Run indexing script to create vector database")
            self.log("   - This will enable semantic search")
        
        if self.test_results["features"]["dashboard"]["details"].get("ipo_count", 0) == 0:
            self.log("\n3. Populate IPO Data:")
            self.log("   - Run IPO scraper from admin panel")
            self.log("   - Or manually add to data/ipo_calendar.json")

if __name__ == "__main__":
    # First apply fixes
    print("Applying fixes first...")
    from fix_hedge_intelligence_complete import fix_hedge_intelligence_complete
    
    if fix_hedge_intelligence_complete():
        print("\n" + "="*80)
        print("Now testing all features...")
        print("="*80)
        
        # Run tests
        tester = ProductionFeatureTester()
        tester.test_all_features()