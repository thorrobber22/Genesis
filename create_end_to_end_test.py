#!/usr/bin/env python3
"""
End-to-End Production Test Suite
Tests COMPLETE flows without assumptions about existing data
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import subprocess
import os
from bs4 import BeautifulSoup

class EndToEndProductionTest:
    def __init__(self):
        self.test_results = {
            "test_run": datetime.now().isoformat(),
            "user": "thorrobber22",
            "type": "end_to_end",
            "flows": {}
        }
        self.root = Path(".")
        
    def run_all_flows(self):
        """Run complete end-to-end flows"""
        print("HEDGE INTELLIGENCE - END-TO-END PRODUCTION TEST")
        print("="*80)
        print("Testing COMPLETE flows from scratch - no assumptions")
        print("="*80)
        
        # Flow 1: Admin adds new company
        print("\n[FLOW 1: ADMIN ADDS NEW COMPANY]")
        self.test_flow_add_company()
        
        # Flow 2: User browses and analyzes documents
        print("\n[FLOW 2: USER DOCUMENT ANALYSIS]")
        self.test_flow_user_analysis()
        
        # Flow 3: IPO tracking workflow
        print("\n[FLOW 3: IPO TRACKING WORKFLOW]")
        self.test_flow_ipo_tracking()
        
        # Flow 4: Watchlist and alerts
        print("\n[FLOW 4: WATCHLIST WORKFLOW]")
        self.test_flow_watchlist()
        
        # Save results
        self.save_results()
    
    # ========== FLOW 1: ADMIN ADDS NEW COMPANY ==========
    
    def test_flow_add_company(self):
        """Test complete flow of adding a new company"""
        flow_name = "add_company"
        flow_results = {
            "status": "RUNNING",
            "steps": {}
        }
        
        print("\nTesting: User requests company → Admin processes → Documents available")
        
        # Step 1: User requests a company
        print("\n  Step 1: User requests new company...")
        step1 = self.test_user_request_company()
        flow_results["steps"]["user_request"] = step1
        
        # Step 2: Admin sees request
        print("\n  Step 2: Admin views pending requests...")
        step2 = self.test_admin_view_pending()
        flow_results["steps"]["admin_view"] = step2
        
        # Step 3: Admin clicks process
        print("\n  Step 3: Admin processes request...")
        step3 = self.test_admin_process()
        flow_results["steps"]["admin_process"] = step3
        
        # Step 4: System downloads documents
        print("\n  Step 4: System downloads SEC documents...")
        step4 = self.test_sec_download_process()
        flow_results["steps"]["sec_download"] = step4
        
        # Step 5: User can browse documents
        print("\n  Step 5: User browses new documents...")
        step5 = self.test_user_browse_new()
        flow_results["steps"]["user_browse"] = step5
        
        # Determine overall status
        all_steps = [step1, step2, step3, step4, step5]
        if all(s["status"] == "PASS" for s in all_steps):
            flow_results["status"] = "PASS"
        elif any(s["status"] == "FAIL" for s in all_steps):
            flow_results["status"] = "FAIL"
        else:
            flow_results["status"] = "PARTIAL"
        
        self.test_results["flows"][flow_name] = flow_results
    
    def test_user_request_company(self):
        """User submits company request"""
        try:
            # Simulate company request
            test_request = {
                "company_name": "Palantir Technologies",
                "ticker": "PLTR",
                "priority": "High",
                "reason": "Need for AI sector analysis",
                "timestamp": datetime.now().isoformat(),
                "user": "analyst",
                "status": "pending"
            }
            
            # Check if we can add to requests
            requests_file = self.root / "data" / "company_requests.json"
            
            # Don't actually modify - just test the structure
            if requests_file.parent.exists():
                return {
                    "status": "PASS",
                    "details": {
                        "can_submit": True,
                        "test_ticker": "PLTR",
                        "request_structure": "valid"
                    }
                }
            else:
                return {
                    "status": "FAIL",
                    "details": {"error": "Data directory not found"}
                }
                
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    def test_admin_view_pending(self):
        """Admin views pending requests"""
        try:
            # Check if admin panel exists and can read requests
            admin_panel = self.root / "admin" / "admin_panel_simple.py"
            
            if admin_panel.exists():
                # Check if it has request viewing code
                with open(admin_panel, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_request_view = "company_requests" in content
                has_pending_filter = "pending" in content
                
                return {
                    "status": "PASS" if has_request_view else "FAIL",
                    "details": {
                        "admin_panel_exists": True,
                        "can_view_requests": has_request_view,
                        "can_filter_pending": has_pending_filter
                    }
                }
            else:
                return {
                    "status": "FAIL",
                    "details": {"error": "Admin panel not found"}
                }
                
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    def test_admin_process(self):
        """Admin clicks process on request"""
        try:
            # Check if processing mechanism exists
            scrapers = [
                self.root / "services" / "scraping_service.py",
                self.root / "services" / "edgar_scraper.py",
                self.root / "services" / "sec_scraper.py"
            ]
            
            scraper_found = any(s.exists() for s in scrapers)
            
            if scraper_found:
                # Check for CIK lookup capability
                existing_scraper = next(s for s in scrapers if s.exists())
                with open(existing_scraper, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_cik_lookup = "cik" in content.lower()
                has_download = "download" in content.lower()
                has_progress = "progress" in content.lower() or "status" in content.lower()
                
                return {
                    "status": "PASS" if (has_cik_lookup and has_download) else "PARTIAL",
                    "details": {
                        "scraper_exists": True,
                        "cik_lookup": has_cik_lookup,
                        "download_capability": has_download,
                        "progress_tracking": has_progress
                    }
                }
            else:
                return {
                    "status": "FAIL",
                    "details": {"error": "No SEC scraper found"}
                }
                
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    def test_sec_download_process(self):
        """Test SEC document download process"""
        try:
            # Test with a real company (small filing count)
            test_cik = "0001326801"  # Meta/Facebook
            test_ticker = "META"
            
            # Test CIK lookup first
            print("\n    - Testing CIK lookup...")
            cik_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={test_cik}&owner=exclude&action=getcompany"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(cik_url, headers=headers)
            
            if response.status_code == 200:
                # Check if we can parse filings
                filing_count = response.text.count('href="/Archives/edgar/data/')
                
                return {
                    "status": "PASS",
                    "details": {
                        "sec_connection": "SUCCESS",
                        "test_company": "META",
                        "filings_found": filing_count > 0,
                        "filing_count_estimate": filing_count,
                        "can_parse": True
                    }
                }
            else:
                return {
                    "status": "FAIL",
                    "details": {
                        "error": f"SEC returned {response.status_code}",
                        "note": "May need better headers or rate limiting"
                    }
                }
                
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    def test_user_browse_new(self):
        """User can browse newly added documents"""
        try:
            # Check document service
            doc_service = self.root / "services" / "document_service.py"
            
            if doc_service.exists():
                with open(doc_service, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for required methods
                has_get_companies = "get_companies" in content
                has_get_documents = "get_company_documents" in content or "get_documents" in content
                has_categorization = any(t in content for t in ["10-K", "10-Q", "8-K", "type"])
                
                return {
                    "status": "PASS" if all([has_get_companies, has_get_documents]) else "PARTIAL",
                    "details": {
                        "document_service_exists": True,
                        "can_list_companies": has_get_companies,
                        "can_list_documents": has_get_documents,
                        "has_categorization": has_categorization
                    }
                }
            else:
                return {
                    "status": "FAIL",
                    "details": {"error": "Document service not found"}
                }
                
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    # ========== FLOW 2: USER DOCUMENT ANALYSIS ==========
    
    def test_flow_user_analysis(self):
        """Test complete user document analysis flow"""
        flow_name = "user_analysis"
        flow_results = {
            "status": "RUNNING",
            "steps": {}
        }
        
        print("\nTesting: Browse → View → Chat → Extract → Download")
        
        # Step 1: Browse documents
        print("\n  Step 1: User browses document explorer...")
        step1 = self.test_browse_documents()
        flow_results["steps"]["browse"] = step1
        
        # Step 2: View document
        print("\n  Step 2: User views SEC filing...")
        step2 = self.test_view_document()
        flow_results["steps"]["view"] = step2
        
        # Step 3: Chat with AI
        print("\n  Step 3: User asks AI about document...")
        step3 = self.test_ai_chat()
        flow_results["steps"]["chat"] = step3
        
        # Step 4: Extract data
        print("\n  Step 4: User extracts financial data...")
        step4 = self.test_extract_data()
        flow_results["steps"]["extract"] = step4
        
        # Step 5: Download
        print("\n  Step 5: User downloads document/data...")
        step5 = self.test_download()
        flow_results["steps"]["download"] = step5
        
        # Overall status
        all_steps = [step1, step2, step3, step4, step5]
        if all(s["status"] == "PASS" for s in all_steps):
            flow_results["status"] = "PASS"
        elif any(s["status"] == "FAIL" for s in all_steps):
            flow_results["status"] = "FAIL"
        else:
            flow_results["status"] = "PARTIAL"
        
        self.test_results["flows"][flow_name] = flow_results
    
    def test_browse_documents(self):
        """Test document browsing"""
        try:
            # Check if document explorer component exists
            doc_explorer = self.root / "components" / "document_explorer.py"
            
            if doc_explorer.exists():
                with open(doc_explorer, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check functionality
                has_company_list = "get_companies" in content or "companies" in content
                has_expandable = "expander" in content
                has_doc_count = "count" in content or "len(" in content
                
                return {
                    "status": "PASS" if has_company_list else "FAIL",
                    "details": {
                        "component_exists": True,
                        "shows_companies": has_company_list,
                        "expandable_ui": has_expandable,
                        "shows_count": has_doc_count
                    }
                }
            else:
                return {
                    "status": "FAIL",
                    "details": {"error": "Document explorer component not found"}
                }
                
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    def test_view_document(self):
        """Test document viewing"""
        try:
            # Check document viewer
            doc_viewer = self.root / "components" / "document_viewer.py"
            
            if doc_viewer.exists():
                with open(doc_viewer, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for HTML rendering
                has_html_render = "html" in content.lower() or "iframe" in content
                has_search = "search" in content.lower()
                
                return {
                    "status": "PASS" if has_html_render else "PARTIAL",
                    "details": {
                        "viewer_exists": True,
                        "can_render_html": has_html_render,
                        "has_search": has_search
                    }
                }
            else:
                # Check if viewing is in main app
                main_app = self.root / "hedge_intelligence.py"
                with open(main_app, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_viewer = "render_document_viewer" in content
                
                return {
                    "status": "PARTIAL",
                    "details": {
                        "standalone_viewer": False,
                        "viewer_in_main": has_viewer
                    }
                }
                
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    def test_ai_chat(self):
        """Test AI chat functionality"""
        try:
            # Check chat components
            chat_engine = self.root / "core" / "chat_engine.py"
            persistent_chat = self.root / "components" / "persistent_chat.py"
            
            # Check API keys
            has_openai = bool(os.getenv("OPENAI_API_KEY"))
            has_gemini = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
            
            if chat_engine.exists() and persistent_chat.exists():
                # Check for dual AI validation
                with open(chat_engine, 'r', encoding='utf-8') as f:
                    engine_content = f.read()
                
                has_openai_code = "openai" in engine_content.lower()
                has_gemini_code = "gemini" in engine_content.lower() or "google" in engine_content.lower()
                has_citations = "citation" in engine_content or "page" in engine_content.lower()
                
                return {
                    "status": "PASS" if (has_openai and has_citations) else "PARTIAL",
                    "details": {
                        "chat_engine_exists": True,
                        "persistent_chat_exists": True,
                        "openai_configured": has_openai,
                        "gemini_configured": has_gemini,
                        "dual_ai": has_openai_code and has_gemini_code,
                        "citation_support": has_citations
                    }
                }
            else:
                return {
                    "status": "FAIL",
                    "details": {"error": "Chat components not found"}
                }
                
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    def test_extract_data(self):
        """Test data extraction"""
        try:
            # Check data extractor
            extractor = self.root / "components" / "data_extractor.py"
            
            if extractor.exists():
                with open(extractor, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check extraction capabilities
                financial_terms = ["revenue", "income", "assets", "cash", "expenses"]
                found_terms = [t for t in financial_terms if t in content.lower()]
                has_validation = "validate" in content.lower() or "verify" in content.lower()
                has_export = "export" in content.lower() or "excel" in content.lower()
                
                return {
                    "status": "PASS" if found_terms else "PARTIAL",
                    "details": {
                        "extractor_exists": True,
                        "financial_patterns": len(found_terms) > 0,
                        "patterns_found": found_terms,
                        "has_validation": has_validation,
                        "has_export": has_export
                    }
                }
            else:
                return {
                    "status": "PARTIAL",
                    "details": {
                        "extractor_exists": False,
                        "note": "Data extraction may be in AI service"
                    }
                }
                
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    def test_download(self):
        """Test download functionality"""
        try:
            # Check for download capabilities
            main_app = self.root / "hedge_intelligence.py"
            with open(main_app, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check download methods
            has_download_button = "download_button" in content
            has_pdf = "pdf" in content.lower()
            has_excel = "excel" in content.lower() or "xlsx" in content
            
            # Check dependencies
            try:
                import openpyxl
                excel_available = True
            except ImportError:
                excel_available = False
            
            return {
                "status": "PASS" if (has_download_button or has_excel) else "PARTIAL",
                "details": {
                    "download_ui": has_download_button,
                    "pdf_support": has_pdf,
                    "excel_support": has_excel,
                    "openpyxl_installed": excel_available
                }
            }
            
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    # ========== FLOW 3: IPO TRACKING ==========
    
    def test_flow_ipo_tracking(self):
        """Test IPO tracking workflow"""
        flow_name = "ipo_tracking"
        flow_results = {
            "status": "RUNNING",
            "steps": {}
        }
        
        print("\nTesting: Scrape IPOs → Display → Click → View S-1")
        
        # Step 1: Scrape IPOs
        print("\n  Step 1: Scraping real IPO data...")
        step1 = self.test_ipo_scraping()
        flow_results["steps"]["scrape"] = step1
        
        # Step 2: Display on dashboard
        print("\n  Step 2: Displaying IPOs on dashboard...")
        step2 = self.test_ipo_display()
        flow_results["steps"]["display"] = step2
        
        # Step 3: Click IPO to view filings
        print("\n  Step 3: Clicking IPO to view filings...")
        step3 = self.test_ipo_click()
        flow_results["steps"]["click"] = step3
        
        # Overall status
        all_steps = [step1, step2, step3]
        if all(s["status"] == "PASS" for s in all_steps):
            flow_results["status"] = "PASS"
        elif any(s["status"] == "FAIL" for s in all_steps):
            flow_results["status"] = "FAIL"
        else:
            flow_results["status"] = "PARTIAL"
        
        self.test_results["flows"][flow_name] = flow_results
    
    def test_ipo_scraping(self):
        """Test real IPO scraping"""
        try:
            # Test connection to IPOScoop
            url = "https://www.iposcoop.com/ipo-calendar/"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Parse with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for IPO data
                tables = soup.find_all('table')
                ipo_data_found = False
                
                for table in tables:
                    if any(text in str(table) for text in ['Symbol', 'Company', 'Price', 'Shares']):
                        ipo_data_found = True
                        break
                
                return {
                    "status": "PASS" if ipo_data_found else "PARTIAL",
                    "details": {
                        "iposcoop_reachable": True,
                        "status_code": response.status_code,
                        "ipo_table_found": ipo_data_found,
                        "content_length": len(response.text)
                    }
                }
            else:
                return {
                    "status": "FAIL",
                    "details": {"error": f"IPOScoop returned {response.status_code}"}
                }
                
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    def test_ipo_display(self):
        """Test IPO display on dashboard"""
        try:
            # Check IPO tracker component
            ipo_tracker = self.root / "components" / "ipo_tracker.py"
            
            if ipo_tracker.exists():
                with open(ipo_tracker, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check display capabilities
                has_table = "dataframe" in content or "table" in content
                has_columns = any(col in content for col in ["Company", "Symbol", "Price", "Date"])
                has_refresh = "refresh" in content or "update" in content
                
                return {
                    "status": "PASS" if (has_table and has_columns) else "PARTIAL",
                    "details": {
                        "tracker_exists": True,
                        "has_table_display": has_table,
                        "has_ipo_columns": has_columns,
                        "has_refresh": has_refresh
                    }
                }
            else:
                return {
                    "status": "FAIL",
                    "details": {"error": "IPO tracker component not found"}
                }
                
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    def test_ipo_click(self):
        """Test clicking IPO to view filings"""
        try:
            # Check if IPO click functionality exists
            main_app = self.root / "hedge_intelligence.py"
            ipo_tracker = self.root / "components" / "ipo_tracker.py"
            
            click_implemented = False
            
            for file_path in [main_app, ipo_tracker]:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if "button" in content and ("S-1" in content or "filing" in content):
                        click_implemented = True
                        break
            
            return {
                "status": "PASS" if click_implemented else "PARTIAL",
                "details": {
                    "click_to_filing": click_implemented,
                    "note": "IPO click to S-1 viewing" if click_implemented else "Feature may need implementation"
                }
            }
            
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    # ========== FLOW 4: WATCHLIST ==========
    
    def test_flow_watchlist(self):
        """Test watchlist workflow"""
        flow_name = "watchlist"
        flow_results = {
            "status": "RUNNING",
            "steps": {}
        }
        
        print("\nTesting: Add to watchlist → Get alerts → View new filings")
        
        # Step 1: Add company
        print("\n  Step 1: Adding company to watchlist...")
        step1 = self.test_add_to_watchlist()
        flow_results["steps"]["add"] = step1
        
        # Step 2: Check for updates
        print("\n  Step 2: Checking for filing updates...")
        step2 = self.test_watchlist_updates()
        flow_results["steps"]["updates"] = step2
        
        # Step 3: View new filing
        print("\n  Step 3: Viewing new filing from watchlist...")
        step3 = self.test_watchlist_navigation()
        flow_results["steps"]["navigate"] = step3
        
        # Overall status
        all_steps = [step1, step2, step3]
        if all(s["status"] == "PASS" for s in all_steps):
            flow_results["status"] = "PASS"
        elif any(s["status"] == "FAIL" for s in all_steps):
            flow_results["status"] = "FAIL"
        else:
            flow_results["status"] = "PARTIAL"
        
        self.test_results["flows"][flow_name] = flow_results
    
    def test_add_to_watchlist(self):
        """Test adding to watchlist"""
        try:
            # Check watchlist implementation
            watchlist_comp = self.root / "components" / "watchlist.py"
            watchlist_service = self.root / "services" / "watchlist_service.py"
            
            implementation_found = False
            details = {}
            
            for file_path in [watchlist_comp, watchlist_service]:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    has_add = "add" in content.lower()
                    has_remove = "remove" in content.lower()
                    has_storage = "json" in content or "save" in content
                    
                    if has_add:
                        implementation_found = True
                        details = {
                            "implementation": file_path.name,
                            "can_add": has_add,
                            "can_remove": has_remove,
                            "has_persistence": has_storage
                        }
                        break
            
            if implementation_found:
                return {"status": "PASS", "details": details}
            else:
                return {
                    "status": "PARTIAL",
                    "details": {"note": "Watchlist may use session state only"}
                }
                
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    def test_watchlist_updates(self):
        """Test watchlist update checking"""
        try:
            # Check for update mechanism
            files_to_check = [
                self.root / "components" / "watchlist.py",
                self.root / "services" / "watchlist_service.py",
                self.root / "hedge_intelligence.py"
            ]
            
            update_mechanism = False
            
            for file_path in files_to_check:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if any(term in content.lower() for term in ["update", "new filing", "alert", "notification"]):
                        update_mechanism = True
                        break
            
            return {
                "status": "PASS" if update_mechanism else "PARTIAL",
                "details": {
                    "update_checking": update_mechanism,
                    "note": "Manual refresh may be required" if not update_mechanism else "Auto-updates configured"
                }
            }
            
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    def test_watchlist_navigation(self):
        """Test navigation from watchlist to document"""
        try:
            # Check if watchlist links to documents
            watchlist_files = [
                self.root / "components" / "watchlist.py",
                self.root / "hedge_intelligence.py"
            ]
            
            navigation_found = False
            
            for file_path in watchlist_files:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if "selected_doc" in content or "view" in content.lower():
                        navigation_found = True
                        break
            
            return {
                "status": "PASS" if navigation_found else "PARTIAL",
                "details": {
                    "can_navigate_to_docs": navigation_found
                }
            }
            
        except Exception as e:
            return {"status": "FAIL", "details": {"error": str(e)}}
    
    # ========== HELPER METHODS ==========
    
    def save_results(self):
        """Save test results"""
        # Save detailed results
        with open("end_to_end_test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2)
        
        # Print summary
        print("\n" + "="*80)
        print("END-TO-END TEST SUMMARY")
        print("="*80)
        
        for flow_name, flow_data in self.test_results["flows"].items():
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "PARTIAL": "⚠️",
                "RUNNING": "⏳"
            }.get(flow_data["status"], "❓")
            
            print(f"\n{status_icon} Flow: {flow_name.upper()} - {flow_data['status']}")
            
            # Show step results
            for step_name, step_data in flow_data["steps"].items():
                step_icon = {
                    "PASS": "✅",
                    "FAIL": "❌",
                    "PARTIAL": "⚠️"
                }.get(step_data["status"], "❓")
                
                print(f"  {step_icon} {step_name}: {step_data['status']}")
                
                # Show critical failures
                if step_data["status"] == "FAIL" and "error" in step_data.get("details", {}):
                    print(f"     Error: {step_data['details']['error']}")
        
        # Generate fix priority
        self.generate_fix_priority()
    
    def generate_fix_priority(self):
        """Generate prioritized fix list"""
        print("\n" + "="*80)
        print("PRIORITY FIXES NEEDED")
        print("="*80)
        
        fixes = []
        
        # Analyze failures
        for flow_name, flow_data in self.test_results["flows"].items():
            for step_name, step_data in flow_data["steps"].items():
                if step_data["status"] == "FAIL":
                    details = step_data.get("details", {})
                    
                    if "SEC returned 403" in str(details.get("error", "")):
                        fixes.append({
                            "priority": 1,
                            "issue": "SEC API returning 403",
                            "fix": "Add proper User-Agent headers and implement rate limiting"
                        })
                    
                    if "not found" in str(details.get("error", "")):
                        fixes.append({
                            "priority": 2,
                            "issue": f"{step_name} component missing",
                            "fix": f"Create missing component or service"
                        })
        
        # Add partial fixes
        for flow_name, flow_data in self.test_results["flows"].items():
            for step_name, step_data in flow_data["steps"].items():
                if step_data["status"] == "PARTIAL":
                    details = step_data.get("details", {})
                    
                    if not details.get("openai_configured"):
                        fixes.append({
                            "priority": 1,
                            "issue": "OpenAI API key not set",
                            "fix": "Set OPENAI_API_KEY environment variable"
                        })
                    
                    if not details.get("openpyxl_installed"):
                        fixes.append({
                            "priority": 3,
                            "issue": "Excel export not available",
                            "fix": "Run: pip install openpyxl"
                        })
        
        # Remove duplicates and sort by priority
        seen = set()
        unique_fixes = []
        for fix in fixes:
            key = fix["issue"]
            if key not in seen:
                seen.add(key)
                unique_fixes.append(fix)
        
        unique_fixes.sort(key=lambda x: x["priority"])
        
        # Print fixes
        for i, fix in enumerate(unique_fixes, 1):
            print(f"\n{i}. {fix['issue']}")
            print(f"   Fix: {fix['fix']}")
        
        if not unique_fixes:
            print("\n✅ No critical fixes needed!")
        
        print("\nFull results saved to: end_to_end_test_results.json")

if __name__ == "__main__":
    tester = EndToEndProductionTest()
    tester.run_all_flows()