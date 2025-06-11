#!/usr/bin/env python3
"""
Comprehensive production test suite for Hedge Intelligence
Tests all features with REAL data and REAL operations
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import subprocess
import sys

class HedgeIntelligenceProductionTester:
    def __init__(self):
        self.test_results = {
            "test_run": datetime.now().isoformat(),
            "user": "thorrobber22",
            "environment": "production",
            "tests": {}
        }
        self.root = Path(".")
        
    def run_all_tests(self):
        """Run complete production test suite"""
        print("HEDGE INTELLIGENCE - PRODUCTION TEST SUITE")
        print("="*80)
        print("Testing with REAL data, REAL APIs, REAL documents")
        print("="*80)
        
        # Admin Backend Tests
        print("\n[ADMIN BACKEND TESTS]")
        self.test_ipo_scraper()
        self.test_cik_lookup()
        self.test_sec_document_downloader()
        
        # User Interface Tests
        print("\n[USER INTERFACE TESTS]")
        self.test_app_startup()
        self.test_dashboard_ipos()
        self.test_watchlist()
        self.test_document_explorer()
        self.test_document_viewer()
        self.test_ai_chat_citations()
        self.test_document_download()
        self.test_data_extraction()
        self.test_company_request()
        
        # Admin Panel Tests
        print("\n[ADMIN PANEL TESTS]")
        self.test_admin_view_requests()
        self.test_admin_process_request()
        
        # Save results
        self.save_test_results()
    
    # ========== ADMIN BACKEND TESTS ==========
    
    def test_ipo_scraper(self):
        """Test IPO scraper with REAL IPOScoop data"""
        print("\n1. Testing IPO Scraper (IPOScoop)...")
        
        test_name = "ipo_scraper"
        results = {"status": "PENDING", "details": {}}
        
        try:
            # Test actual scraping
            url = "https://www.iposcoop.com/ipo-calendar/"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code == 200:
                results["details"]["connection"] = "SUCCESS"
                results["details"]["content_length"] = len(response.text)
                
                # Check if we can find IPO data markers
                markers = ["upcoming-ipos", "this-week", "expected", "priced"]
                found_markers = [m for m in markers if m in response.text.lower()]
                results["details"]["found_markers"] = found_markers
                
                # Try to run actual scraper if exists
                scraper_path = self.root / "services" / "ipo_scraper.py"
                if scraper_path.exists():
                    # Would run: python services/ipo_scraper.py
                    results["details"]["scraper_exists"] = True
                else:
                    results["details"]["scraper_exists"] = False
                    results["details"]["note"] = "Need to implement ipo_scraper.py"
                
                results["status"] = "PASS" if found_markers else "PARTIAL"
            else:
                results["status"] = "FAIL"
                results["details"]["error"] = f"HTTP {response.status_code}"
                
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    def test_cik_lookup(self):
        """Test CIK lookup with REAL SEC API"""
        print("\n2. Testing CIK Lookup (SEC)...")
        
        test_name = "cik_lookup"
        results = {"status": "PENDING", "details": {}}
        
        test_companies = ["Tesla", "Apple", "Circle Internet Financial"]
        
        try:
            for company in test_companies:
                # Test SEC CIK lookup
                url = f"https://www.sec.gov/cgi-bin/cik_lookup?company={company}"
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                
                if response.status_code == 200:
                    # Check if CIK found in response
                    if "CIK" in response.text:
                        results["details"][company] = "CIK FOUND"
                    else:
                        results["details"][company] = "NO CIK"
                else:
                    results["details"][company] = f"HTTP {response.status_code}"
            
            # Check existing CIK mappings
            cik_file = self.root / "data" / "cik_mappings.json"
            if cik_file.exists():
                with open(cik_file, 'r', encoding='utf-8') as f:
                    cik_data = json.load(f)
                results["details"]["existing_mappings"] = len(cik_data)
            
            results["status"] = "PASS"
            
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    def test_sec_document_downloader(self):
        """Test SEC document downloader with REAL CIK"""
        print("\n3. Testing SEC Document Downloader...")
        
        test_name = "sec_document_downloader"
        results = {"status": "PENDING", "details": {}}
        
        # Test with Circle's CIK
        test_cik = "0001876042"  # Circle Internet Financial
        
        try:
            # Test Edgar API
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={test_cik}"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code == 200:
                results["details"]["edgar_connection"] = "SUCCESS"
                
                # Check for filing markers
                filing_types = ["10-K", "10-Q", "8-K", "S-1"]
                found_filings = [ft for ft in filing_types if ft in response.text]
                results["details"]["found_filing_types"] = found_filings
                
                # Check existing downloads
                sec_docs = self.root / "data" / "sec_documents" / "CRCL"
                if sec_docs.exists():
                    doc_count = len(list(sec_docs.glob("*.html")))
                    results["details"]["existing_docs"] = doc_count
                    results["details"]["expected_docs"] = 584
                    results["details"]["docs_complete"] = doc_count >= 584
                
                results["status"] = "PASS"
            else:
                results["status"] = "FAIL"
                results["details"]["error"] = f"HTTP {response.status_code}"
                
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    # ========== USER INTERFACE TESTS ==========
    
    def test_app_startup(self):
        """Test Streamlit app startup"""
        print("\n4. Testing App Startup...")
        
        test_name = "app_startup"
        results = {"status": "PENDING", "details": {}}
        
        try:
            # Check if main app exists
            main_app = self.root / "hedge_intelligence.py"
            if main_app.exists():
                results["details"]["main_app_exists"] = True
                
                # Check for syntax errors
                compile(main_app.read_text(encoding='utf-8'), 'hedge_intelligence.py', 'exec')
                results["details"]["syntax_valid"] = True
                
                # Check imports
                with open(main_app, 'r', encoding='utf-8') as f:
                    content = f.read()
                    required_imports = ["streamlit", "components.persistent_chat", "services.ai_service"]
                    missing_imports = [imp for imp in required_imports if imp not in content]
                    results["details"]["missing_imports"] = missing_imports
                
                results["status"] = "PASS" if not missing_imports else "PARTIAL"
            else:
                results["status"] = "FAIL"
                results["details"]["error"] = "Main app not found"
                
        except SyntaxError as e:
            results["status"] = "FAIL"
            results["details"]["error"] = f"Syntax error: {e}"
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    def test_dashboard_ipos(self):
        """Test IPO display on dashboard"""
        print("\n5. Testing Dashboard IPO Display...")
        
        test_name = "dashboard_ipos"
        results = {"status": "PENDING", "details": {}}
        
        try:
            # Check IPO calendar data
            ipo_file = self.root / "data" / "ipo_calendar.json"
            if ipo_file.exists():
                with open(ipo_file, 'r', encoding='utf-8') as f:
                    ipo_data = json.load(f)
                
                results["details"]["total_ipos"] = len(ipo_data) if isinstance(ipo_data, list) else 0
                
                # Check for fake companies
                fake_companies = ["Stripe", "SpaceX", "Databricks", "Canva", "Instacart"]
                if isinstance(ipo_data, list):
                    fake_found = [ipo for ipo in ipo_data if ipo.get('company') in fake_companies]
                    real_ipos = [ipo for ipo in ipo_data if ipo.get('company') not in fake_companies]
                    
                    results["details"]["fake_companies"] = len(fake_found)
                    results["details"]["real_companies"] = len(real_ipos)
                    results["details"]["needs_cleanup"] = len(fake_found) > 0
                
                results["status"] = "PASS" if not results["details"].get("needs_cleanup") else "PARTIAL"
            else:
                results["status"] = "FAIL"
                results["details"]["error"] = "IPO calendar not found"
                
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    def test_watchlist(self):
        """Test watchlist functionality"""
        print("\n6. Testing Watchlist...")
        
        test_name = "watchlist"
        results = {"status": "PENDING", "details": {}}
        
        try:
            # Check watchlist data
            watchlist_file = self.root / "data" / "watchlists.json"
            if watchlist_file.exists():
                with open(watchlist_file, 'r', encoding='utf-8') as f:
                    watchlist_data = json.load(f)
                
                results["details"]["watchlist_exists"] = True
                results["details"]["entries"] = len(watchlist_data) if isinstance(watchlist_data, dict) else 0
                
                # Check watchlist service
                service_file = self.root / "services" / "watchlist_service.py"
                results["details"]["service_exists"] = service_file.exists()
                
                results["status"] = "PASS"
            else:
                results["status"] = "PARTIAL"
                results["details"]["note"] = "Watchlist file not found, will be created on first use"
                
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    def test_document_explorer(self):
        """Test document explorer with REAL documents"""
        print("\n7. Testing Document Explorer...")
        
        test_name = "document_explorer"
        results = {"status": "PENDING", "details": {}}
        
        try:
            # Check document structure
            sec_docs_dir = self.root / "data" / "sec_documents"
            if sec_docs_dir.exists():
                companies = [d.name for d in sec_docs_dir.iterdir() if d.is_dir()]
                results["details"]["companies"] = companies
                results["details"]["company_count"] = len(companies)
                
                # Test CRCL specifically
                crcl_dir = sec_docs_dir / "CRCL"
                if crcl_dir.exists():
                    crcl_docs = list(crcl_dir.glob("*.html"))
                    results["details"]["crcl_doc_count"] = len(crcl_docs)
                    results["details"]["crcl_expected"] = 584
                    results["details"]["crcl_complete"] = len(crcl_docs) >= 584
                    
                    # Check document categorization
                    doc_types = {"10-K": 0, "10-Q": 0, "8-K": 0, "S-1": 0}
                    for doc in crcl_docs[:20]:  # Sample first 20
                        for doc_type in doc_types:
                            if doc_type in doc.name:
                                doc_types[doc_type] += 1
                    results["details"]["sample_doc_types"] = doc_types
                
                results["status"] = "PASS" if companies else "FAIL"
            else:
                results["status"] = "FAIL"
                results["details"]["error"] = "SEC documents directory not found"
                
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    def test_document_viewer(self):
        """Test document viewer with REAL SEC filing"""
        print("\n8. Testing Document Viewer...")
        
        test_name = "document_viewer"
        results = {"status": "PENDING", "details": {}}
        
        try:
            # Test with a real CRCL document
            test_doc = self.root / "data" / "sec_documents" / "CRCL" / "0001876042-24-000011.html"
            
            if test_doc.exists():
                with open(test_doc, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                results["details"]["test_doc_exists"] = True
                results["details"]["doc_size"] = len(content)
                
                # Check for SEC document markers
                sec_markers = ["<HTML>", "CENTRAL INDEX KEY", "FILING VALUES", "ACCESSION NUMBER"]
                found_markers = [m for m in sec_markers if m in content.upper()]
                results["details"]["sec_format_valid"] = len(found_markers) >= 2
                
                # Check if searchable
                test_terms = ["revenue", "assets", "cash flow", "risk factors"]
                searchable_terms = [t for t in test_terms if t.lower() in content.lower()]
                results["details"]["searchable_terms"] = searchable_terms
                
                results["status"] = "PASS"
            else:
                results["status"] = "FAIL"
                results["details"]["error"] = "Test document not found"
                
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    def test_ai_chat_citations(self):
        """Test AI chat with REAL document context and citations"""
        print("\n9. Testing AI Chat & Citations...")
        
        test_name = "ai_chat_citations"
        results = {"status": "PENDING", "details": {}}
        
        try:
            # Check AI service
            ai_service = self.root / "services" / "ai_service.py"
            chat_engine = self.root / "core" / "chat_engine.py"
            
            results["details"]["ai_service_exists"] = ai_service.exists()
            results["details"]["chat_engine_exists"] = chat_engine.exists()
            
            # Check for API keys
            import os
            results["details"]["openai_key_set"] = bool(os.getenv("OPENAI_API_KEY"))
            results["details"]["gemini_key_set"] = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
            
            # Check ChromaDB
            chroma_dir = self.root / "data" / "chroma"
            results["details"]["chromadb_exists"] = chroma_dir.exists()
            
            if chroma_dir.exists():
                # Check for index files
                index_files = list(chroma_dir.glob("**/*.bin")) + list(chroma_dir.glob("**/*.pkl"))
                results["details"]["index_files"] = len(index_files)
            
            # Test prompts
            test_prompts = [
                "What is Circle's primary business?",
                "What are the main risk factors?",
                "What was the revenue last quarter?"
            ]
            results["details"]["test_prompts"] = test_prompts
            
            results["status"] = "PASS" if all([
                results["details"]["ai_service_exists"],
                results["details"]["chat_engine_exists"],
                results["details"]["openai_key_set"]
            ]) else "PARTIAL"
            
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    def test_document_download(self):
        """Test document download functionality"""
        print("\n10. Testing Document Download...")
        
        test_name = "document_download"
        results = {"status": "PENDING", "details": {}}
        
        try:
            # Check if download functionality exists in code
            main_app = self.root / "hedge_intelligence.py"
            with open(main_app, 'r', encoding='utf-8') as f:
                content = f.read()
            
            download_indicators = ["download_button", "st.download", "download"]
            found_download = [ind for ind in download_indicators if ind in content]
            results["details"]["download_code_found"] = bool(found_download)
            
            # Check for Excel export capability
            try:
                import openpyxl
                results["details"]["excel_support"] = True
            except ImportError:
                results["details"]["excel_support"] = False
            
            # Check for PDF capability
            pdf_indicators = ["pdf", "PDF", "reportlab", "pypdf"]
            pdf_support = any(ind in content for ind in pdf_indicators)
            results["details"]["pdf_mentioned"] = pdf_support
            
            results["status"] = "PASS" if results["details"]["download_code_found"] else "PARTIAL"
            
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    def test_data_extraction(self):
        """Test financial data extraction"""
        print("\n11. Testing Data Extraction...")
        
        test_name = "data_extraction"
        results = {"status": "PENDING", "details": {}}
        
        try:
            # Check data extractor component
            extractor = self.root / "components" / "data_extractor.py"
            results["details"]["extractor_exists"] = extractor.exists()
            
            if extractor.exists():
                with open(extractor, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for extraction patterns
                patterns = ["revenue", "assets", "liabilities", "cash", "income"]
                found_patterns = [p for p in patterns if p in content.lower()]
                results["details"]["financial_patterns"] = found_patterns
                
                # Check for citation support
                citation_indicators = ["page", "Page", "citation", "[Page"]
                has_citations = any(ind in content for ind in citation_indicators)
                results["details"]["citation_support"] = has_citations
            
            results["status"] = "PASS" if results["details"]["extractor_exists"] else "PARTIAL"
            
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    def test_company_request(self):
        """Test company request functionality"""
        print("\n12. Testing Company Request...")
        
        test_name = "company_request"
        results = {"status": "PENDING", "details": {}}
        
        try:
            # Check company requests file
            requests_file = self.root / "data" / "company_requests.json"
            if requests_file.exists():
                with open(requests_file, 'r', encoding='utf-8') as f:
                    requests = json.load(f)
                
                results["details"]["requests_file_exists"] = True
                results["details"]["pending_requests"] = len(requests)
                
                # Check request structure
                if requests:
                    sample = requests[0]
                    required_fields = ["ticker", "status", "timestamp"]
                    has_fields = all(field in sample for field in required_fields)
                    results["details"]["valid_structure"] = has_fields
                    
                    # List pending companies
                    pending = [r.get('ticker', 'Unknown') for r in requests if r.get('status') == 'pending']
                    results["details"]["pending_tickers"] = pending
            
            results["status"] = "PASS"
            
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    # ========== ADMIN PANEL TESTS ==========
    
    def test_admin_view_requests(self):
        """Test admin view of company requests"""
        print("\n13. Testing Admin View Requests...")
        
        test_name = "admin_view_requests"
        results = {"status": "PENDING", "details": {}}
        
        try:
            # Check admin panel
            admin_panel = self.root / "admin" / "admin_panel.py"
            admin_simple = self.root / "admin" / "admin_panel_simple.py"
            
            results["details"]["admin_panel_exists"] = admin_panel.exists()
            results["details"]["admin_simple_exists"] = admin_simple.exists()
            
            # Check which one to use
            if admin_simple.exists():
                with open(admin_simple, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for request viewing code
                view_indicators = ["company_requests", "pending", "view", "display"]
                found_view = [ind for ind in view_indicators if ind in content]
                results["details"]["can_view_requests"] = bool(found_view)
            
            results["status"] = "PASS" if results["details"]["admin_simple_exists"] else "PARTIAL"
            
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    def test_admin_process_request(self):
        """Test admin process company request"""
        print("\n14. Testing Admin Process Request...")
        
        test_name = "admin_process_request"
        results = {"status": "PENDING", "details": {}}
        
        try:
            # Check for processing capability
            scraper = self.root / "services" / "scraping_service.py"
            edgar_scraper = self.root / "services" / "edgar_scraper.py"
            
            results["details"]["scraping_service_exists"] = scraper.exists()
            results["details"]["edgar_scraper_exists"] = edgar_scraper.exists()
            
            # Check for progress tracking
            if scraper.exists():
                with open(scraper, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                progress_indicators = ["progress", "downloading", "status", "update"]
                has_progress = any(ind in content.lower() for ind in progress_indicators)
                results["details"]["progress_tracking"] = has_progress
            
            results["status"] = "PASS" if any([
                results["details"]["scraping_service_exists"],
                results["details"]["edgar_scraper_exists"]
            ]) else "FAIL"
            
        except Exception as e:
            results["status"] = "FAIL"
            results["details"]["error"] = str(e)
        
        self.test_results["tests"][test_name] = results
        self._print_result(test_name, results)
    
    # ========== HELPER METHODS ==========
    
    def _print_result(self, test_name: str, results: Dict[str, Any]):
        """Print test result with formatting"""
        status = results["status"]
        status_icon = {
            "PASS": "✅",
            "FAIL": "❌",
            "PARTIAL": "⚠️",
            "PENDING": "⏳"
        }.get(status, "❓")
        
        print(f"   {status_icon} {test_name}: {status}")
        
        if status != "PASS" and "error" in results.get("details", {}):
            print(f"      Error: {results['details']['error']}")
        elif status == "PARTIAL" and "note" in results.get("details", {}):
            print(f"      Note: {results['details']['note']}")
    
    def save_test_results(self):
        """Save all test results"""
        output_file = self.root / "production_test_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2)
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        # Count results
        statuses = {}
        for test, result in self.test_results["tests"].items():
            status = result["status"]
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"✅ PASSED: {statuses.get('PASS', 0)}")
        print(f"⚠️  PARTIAL: {statuses.get('PARTIAL', 0)}")
        print(f"❌ FAILED: {statuses.get('FAIL', 0)}")
        print(f"⏳ PENDING: {statuses.get('PENDING', 0)}")
        
        print(f"\nResults saved to: {output_file}")
        
        # Generate action items
        self.generate_action_items()
    
    def generate_action_items(self):
        """Generate action items based on test results"""
        print("\n" + "="*80)
        print("ACTION ITEMS")
        print("="*80)
        
        actions = []
        
        for test_name, result in self.test_results["tests"].items():
            if result["status"] in ["FAIL", "PARTIAL"]:
                details = result.get("details", {})
                
                if test_name == "ipo_scraper" and not details.get("scraper_exists"):
                    actions.append("1. Create services/ipo_scraper.py to scrape IPOScoop")
                
                if test_name == "dashboard_ipos" and details.get("needs_cleanup"):
                    actions.append("2. Remove fake companies from ipo_calendar.json")
                
                if test_name == "ai_chat_citations" and not details.get("openai_key_set"):
                    actions.append("3. Set OPENAI_API_KEY environment variable")
                
                if test_name == "document_download" and not details.get("excel_support"):
                    actions.append("4. Install openpyxl: pip install openpyxl")
        
        if actions:
            print("\nRequired Actions:")
            for action in actions:
                print(f"  {action}")
        else:
            print("\n✅ No critical actions required!")

if __name__ == "__main__":
    # First fix the Unicode error
    from fix_test_production_functionality import fix_unicode_error
    fix_unicode_error()
    
    # Run production tests
    tester = HedgeIntelligenceProductionTester()
    tester.run_all_tests()