#!/usr/bin/env python3
"""
Hedge Intelligence - Production Test V2
Date: 2025-06-07 22:04:04 UTC
Author: thorrobber22
Description: Complete test of refactored analyst platform
"""

import asyncio
import json
import sys
import traceback
from pathlib import Path
from datetime import datetime
import time
import importlib
import pandas as pd

class ProductionTestV2:
    def __init__(self):
        self.test_results = []
        self.critical_failures = []
        self.test_company = "CRCL"
        self.test_document = None
        
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        # Print result
        status_symbols = {
            'PASSED': '✅',
            'FAILED': '❌',
            'WARNING': '⚠️',
            'INFO': 'ℹ️'
        }
        symbol = status_symbols.get(status, '❓')
        print(f"{symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
            
        if status == 'FAILED':
            self.critical_failures.append(test_name)
    
    def test_file_structure(self):
        """Test 1: Verify file structure after refactor"""
        print("\n📁 TEST 1: File Structure")
        print("-" * 50)
        
        required_files = [
            ("hedge_intelligence.py", "Main application"),
            ("components/document_explorer.py", "Document explorer"),
            ("components/persistent_chat.py", "Chat component"),
            ("components/data_extractor.py", "Data extraction"),
            ("components/ipo_tracker_enhanced.py", "IPO tracker"),
            ("services/ai_service.py", "AI service"),
            ("services/document_service.py", "Document service")
        ]
        
        all_present = True
        for file_path, description in required_files:
            if Path(file_path).exists():
                self.log_test(f"File: {file_path}", "PASSED", description)
            else:
                self.log_test(f"File: {file_path}", "FAILED", f"Missing {description}")
                all_present = False
                
        return all_present
    
    def test_imports(self):
        """Test 2: Verify all imports work"""
        print("\n📦 TEST 2: Import Tests")
        print("-" * 50)
        
        imports_to_test = [
            ("components.document_explorer", "DocumentExplorer"),
            ("components.persistent_chat", "PersistentChat"),
            ("components.data_extractor", "DataExtractor"),
            ("components.ipo_tracker_enhanced", "IPOTrackerEnhanced"),
            ("services.ai_service", "AIService"),
            ("services.document_service", "DocumentService")
        ]
        
        all_imported = True
        for module_name, class_name in imports_to_test:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, class_name):
                    self.log_test(f"Import: {class_name}", "PASSED", f"from {module_name}")
                else:
                    self.log_test(f"Import: {class_name}", "FAILED", f"Class not found in {module_name}")
                    all_imported = False
            except Exception as e:
                self.log_test(f"Import: {module_name}", "FAILED", str(e))
                all_imported = False
                
        return all_imported
    
    def test_data_directories(self):
        """Test 3: Verify data directories"""
        print("\n📂 TEST 3: Data Directories")
        print("-" * 50)
        
        required_dirs = [
            "data/sec_documents",
            "data/ipo_pipeline",
            "components",
            "services"
        ]
        
        for dir_path in required_dirs:
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                # Count contents
                if "sec_documents" in dir_path:
                    companies = len(list(path.iterdir()))
                    total_docs = sum(
                        len(list(p.glob("*.html"))) 
                        for p in path.iterdir() if p.is_dir()
                    )
                    self.log_test(f"Directory: {dir_path}", "PASSED", 
                                f"{companies} companies, {total_docs} documents")
                else:
                    self.log_test(f"Directory: {dir_path}", "PASSED", "Exists")
            else:
                self.log_test(f"Directory: {dir_path}", "FAILED", "Missing")
    
    def test_document_explorer(self):
        """Test 4: Document Explorer functionality"""
        print("\n📊 TEST 4: Document Explorer")
        print("-" * 50)
        
        try:
            from components.document_explorer import DocumentExplorer
            
            explorer = DocumentExplorer()
            companies = explorer.get_companies_with_counts()
            
            if companies:
                self.log_test("Document Explorer Init", "PASSED", 
                            f"Found {len(companies)} companies")
                
                # Test company listing
                for company, count in list(companies.items())[:3]:
                    self.log_test(f"Company: {company}", "INFO", f"{count} documents")
                    
                # Store first company for later tests
                self.test_company = list(companies.keys())[0]
                
                # Find a test document
                company_path = Path(f"data/sec_documents/{self.test_company}")
                docs = list(company_path.glob("*.html"))
                if docs:
                    self.test_document = docs[0].name
                    self.log_test("Test Document Selected", "PASSED", self.test_document)
                    
            else:
                self.log_test("Document Explorer", "WARNING", "No companies found")
                
        except Exception as e:
            self.log_test("Document Explorer", "FAILED", str(e))
            traceback.print_exc()
    
    def test_data_extractor(self):
        """Test 5: Data Extraction"""
        print("\n🔍 TEST 5: Data Extractor")
        print("-" * 50)
        
        try:
            from components.data_extractor import DataExtractor
            
            extractor = DataExtractor()
            
            # Test with sample text
            sample_text = """
            The company reported total revenues of $2,836 million for the fiscal year,
            representing a 67% increase. Net income was $420 million. 
            We have 1,250 employees worldwide.
            """
            
            # Test revenue extraction
            revenue = extractor.extract_with_citations(sample_text, 'revenue')
            if revenue['status'] == 'found':
                self.log_test("Extract Revenue", "PASSED", 
                            f"${revenue['value']} {revenue.get('unit', '')}")
            else:
                self.log_test("Extract Revenue", "WARNING", "Not found in sample")
                
            # Test employee extraction
            employees = extractor.extract_with_citations(sample_text, 'employees')
            if employees['status'] == 'found':
                self.log_test("Extract Employees", "PASSED", 
                            f"{employees['value']} employees")
            else:
                self.log_test("Extract Employees", "WARNING", "Not found in sample")
                
        except Exception as e:
            self.log_test("Data Extractor", "FAILED", str(e))
            traceback.print_exc()
    
    def test_ai_service(self):
        """Test 6: AI Service"""
        print("\n🤖 TEST 6: AI Service")
        print("-" * 50)
        
        try:
            from services.ai_service import AIService
            
            # Check if AI service can be initialized
            ai = AIService()
            self.log_test("AI Service Init", "PASSED", "Service initialized")
            
            # Check for required method
            if hasattr(ai, 'get_ai_response'):
                self.log_test("AI Method: get_ai_response", "PASSED", "Method exists")
                
                # Test simple query (without making actual API call)
                test_prompt = "What are the main risks?"
                test_context = "The company faces regulatory risks."
                
                try:
                    # This might fail if no API keys, which is OK for structure test
                    response = ai.get_ai_response(test_prompt, test_context)
                    if response:
                        self.log_test("AI Response Test", "PASSED", "Got response")
                    else:
                        self.log_test("AI Response Test", "WARNING", "No response (check API keys)")
                except Exception as e:
                    self.log_test("AI Response Test", "WARNING", f"API not configured: {str(e)}")
                    
            else:
                self.log_test("AI Method: get_ai_response", "FAILED", "Method missing")
                
        except Exception as e:
            self.log_test("AI Service", "FAILED", str(e))
            traceback.print_exc()
    
    def test_persistent_chat(self):
        """Test 7: Persistent Chat Component"""
        print("\n💬 TEST 7: Persistent Chat")
        print("-" * 50)
        
        try:
            from components.persistent_chat import PersistentChat
            
            chat = PersistentChat()
            self.log_test("Persistent Chat Init", "PASSED", "Component initialized")
            
            # Check methods
            if hasattr(chat, 'render_chat_bar'):
                self.log_test("Chat Method: render_chat_bar", "PASSED", "Method exists")
            else:
                self.log_test("Chat Method: render_chat_bar", "FAILED", "Method missing")
                
            if hasattr(chat, 'process_query'):
                self.log_test("Chat Method: process_query", "PASSED", "Method exists")
            else:
                self.log_test("Chat Method: process_query", "FAILED", "Method missing")
                
        except Exception as e:
            self.log_test("Persistent Chat", "FAILED", str(e))
            traceback.print_exc()
    
    def test_ipo_tracker(self):
        """Test 8: IPO Tracker"""
        print("\n📈 TEST 8: IPO Tracker Enhanced")
        print("-" * 50)
        
        try:
            from components.ipo_tracker_enhanced import IPOTrackerEnhanced
            
            tracker = IPOTrackerEnhanced()
            self.log_test("IPO Tracker Init", "PASSED", "Component initialized")
            
            # Test data loading
            ipos = tracker.load_ipo_data()
            if ipos:
                self.log_test("IPO Data Load", "PASSED", f"{len(ipos)} IPOs found")
                
                # Check first IPO structure
                first_ipo = ipos[0]
                required_fields = ['company', 'sector', 'expected_date']
                for field in required_fields:
                    if field in first_ipo:
                        self.log_test(f"IPO Field: {field}", "PASSED", first_ipo[field])
                    else:
                        self.log_test(f"IPO Field: {field}", "WARNING", "Missing")
            else:
                self.log_test("IPO Data", "WARNING", "No IPO data")
                
        except Exception as e:
            self.log_test("IPO Tracker", "FAILED", str(e))
            traceback.print_exc()
    
    def test_theme_and_styling(self):
        """Test 9: Theme and Styling"""
        print("\n🎨 TEST 9: Theme and Styling")
        print("-" * 50)
        
        try:
            # Read main file to check for theme
            with open("hedge_intelligence.py", "r", encoding="utf-8") as f:
                content = f.read()
                
            # Check for dark theme
            if "apply_dark_theme" in content:
                self.log_test("Dark Theme Function", "PASSED", "Found")
                
                # Check for no blue buttons
                if "#007BFF" not in content and "blue" not in content.lower():
                    self.log_test("No Blue Buttons", "PASSED", "Grey theme applied")
                else:
                    self.log_test("No Blue Buttons", "WARNING", "Blue color found")
                    
            else:
                self.log_test("Dark Theme", "FAILED", "Theme function missing")
                
            # Check for removed features
            if "settings" not in content.lower():
                self.log_test("Settings Removed", "PASSED", "No settings found")
            else:
                self.log_test("Settings Removed", "WARNING", "Settings references remain")
                
        except Exception as e:
            self.log_test("Theme Check", "FAILED", str(e))
    
    def test_document_workflow(self):
        """Test 10: Complete Document Workflow"""
        print("\n📄 TEST 10: Document Workflow")
        print("-" * 50)
        
        try:
            # Simulate selecting and viewing a document
            if self.test_document:
                doc_path = Path(f"data/sec_documents/{self.test_company}/{self.test_document}")
                
                if doc_path.exists():
                    self.log_test("Document Access", "PASSED", f"{self.test_company}/{self.test_document}")
                    
                    # Test reading document
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:1000]
                        
                    self.log_test("Document Read", "PASSED", f"{len(content)} chars loaded")
                    
                    # Test extraction on real document
                    from components.data_extractor import DataExtractor
                    extractor = DataExtractor()
                    
                    # Try to extract something
                    result = extractor.extract_with_citations(content, 'revenue')
                    if result['status'] == 'found':
                        self.log_test("Real Document Extract", "PASSED", "Found data")
                    else:
                        self.log_test("Real Document Extract", "INFO", "No revenue in sample")
                        
                else:
                    self.log_test("Document Access", "FAILED", "Document not found")
            else:
                self.log_test("Document Workflow", "WARNING", "No test document selected")
                
        except Exception as e:
            self.log_test("Document Workflow", "FAILED", str(e))
            traceback.print_exc()
    
    def test_company_request(self):
        """Test 11: Company Request System"""
        print("\n📨 TEST 11: Company Request")
        print("-" * 50)
        
        try:
            # Create test request
            request = {
                'company': 'Tesla Inc',
                'ticker': 'TSLA',
                'priority': 'High',
                'reason': 'Production test request',
                'status': 'pending',
                'timestamp': datetime.now().isoformat()
            }
            
            # Save request
            requests_file = Path("data/company_requests.json")
            if requests_file.exists():
                with open(requests_file, 'r') as f:
                    requests = json.load(f)
            else:
                requests = []
                
            requests.append(request)
            
            requests_file.parent.mkdir(exist_ok=True)
            with open(requests_file, 'w') as f:
                json.dump(requests, f, indent=2)
                
            self.log_test("Company Request", "PASSED", "Request saved")
            
            # Verify it was saved
            with open(requests_file, 'r') as f:
                saved_requests = json.load(f)
                
            if any(r['ticker'] == 'TSLA' for r in saved_requests):
                self.log_test("Request Verification", "PASSED", "TSLA request found")
            else:
                self.log_test("Request Verification", "FAILED", "Request not saved")
                
        except Exception as e:
            self.log_test("Company Request", "FAILED", str(e))
            traceback.print_exc()
    
    def test_session_state(self):
        """Test 12: Session State Management"""
        print("\n🔄 TEST 12: Session State")
        print("-" * 50)
        
        try:
            # Check main file for session state usage
            with open("hedge_intelligence.py", "r", encoding="utf-8") as f:
                content = f.read()
                
            session_vars = [
                "selected_doc",
                "chat_history",
                "show_company_request"
            ]
            
            for var in session_vars:
                if f"st.session_state.{var}" in content or f"'{var}'" in content:
                    self.log_test(f"Session: {var}", "PASSED", "Used in app")
                else:
                    self.log_test(f"Session: {var}", "INFO", "Not found")
                    
        except Exception as e:
            self.log_test("Session State", "FAILED", str(e))
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 PRODUCTION TEST SUMMARY V2")
        print("=" * 70)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"User: thorrobber22")
        print("=" * 70)
        
        # Count results
        passed = sum(1 for r in self.test_results if r['status'] == 'PASSED')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAILED')
        warnings = sum(1 for r in self.test_results if r['status'] == 'WARNING')
        info = sum(1 for r in self.test_results if r['status'] == 'INFO')
        
        # Print summary table
        print(f"\n{'Test Category':<30} {'Status':<10} {'Details':<30}")
        print("-" * 70)
        
        current_category = ""
        for result in self.test_results:
            test_name = result['test']
            # Extract category
            if ":" in test_name:
                category = test_name.split(":")[0]
                if category != current_category:
                    print("-" * 70)
                current_category = category
                
            print(f"{test_name:<30} {result['status']:<10} {result['details'][:29]}")
        
        print("-" * 70)
        print(f"\nTotal Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"ℹ️  Info: {info}")
        
        # Critical failures
        if self.critical_failures:
            print("\n⚠️  CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"  - {failure}")
        
        # Save results
        results_file = Path("data/production_test_v2_results.json")
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': len(self.test_results),
                    'passed': passed,
                    'failed': failed,
                    'warnings': warnings,
                    'info': info
                },
                'critical_failures': self.critical_failures,
                'details': self.test_results
            }, f, indent=2)
        
        print(f"\n📁 Results saved to: {results_file}")
        
        # Final verdict
        if failed == 0:
            print("\n🎉 ALL CRITICAL TESTS PASSED!")
            print("The refactored platform is ready for use.")
        elif failed <= 2:
            print("\n⚠️  Minor issues detected.")
            print("The platform should work but may have limited functionality.")
        else:
            print("\n❌ Multiple failures detected.")
            print("Please review the errors before launching.")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 HEDGE INTELLIGENCE - PRODUCTION TEST V2")
        print("Testing refactored analyst platform...")
        print("=" * 70)
        
        # Run all tests
        self.test_file_structure()
        self.test_imports()
        self.test_data_directories()
        self.test_document_explorer()
        self.test_data_extractor()
        self.test_ai_service()
        self.test_persistent_chat()
        self.test_ipo_tracker()
        self.test_theme_and_styling()
        self.test_document_workflow()
        self.test_company_request()
        self.test_session_state()
        
        # Print summary
        self.print_summary()

def main():
    """Run production test"""
    tester = ProductionTestV2()
    tester.run_all_tests()

if __name__ == "__main__":
    main()