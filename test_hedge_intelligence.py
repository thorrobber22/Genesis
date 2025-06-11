#!/usr/bin/env python3
"""
Hedge Intelligence - Production Test V3
Date: 2025-06-07 22:26:32 UTC
Author: thorrobber22
Description: Complete test of the hedge intelligence platform
"""

import subprocess
import sys
import time
import json
import traceback
from pathlib import Path
from datetime import datetime
import importlib.util
import requests
import pandas as pd

class HedgeIntelligenceTest:
    def __init__(self):
        self.test_results = []
        self.critical_errors = []
        self.warnings = []
        self.test_start = time.time()
        
    def log_test(self, component, test_name, status, details="", duration=0):
        """Log test result with timing"""
        result = {
            'component': component,
            'test': test_name,
            'status': status,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        # Status symbols
        symbols = {
            'PASS': '✅',
            'FAIL': '❌',
            'WARN': '⚠️',
            'INFO': 'ℹ️',
            'SKIP': '⏭️'
        }
        
        symbol = symbols.get(status, '❓')
        print(f"{symbol} [{component}] {test_name}: {status}")
        if details:
            print(f"   → {details}")
        if duration > 0:
            print(f"   ⏱️  {duration:.2f}s")
            
        if status == 'FAIL':
            self.critical_errors.append(f"{component}: {test_name}")
        elif status == 'WARN':
            self.warnings.append(f"{component}: {test_name}")
    
    def test_python_version(self):
        """Test 1: Python Version"""
        start = time.time()
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.log_test("Environment", "Python Version", "PASS", 
                         f"Python {version.major}.{version.minor}.{version.micro}",
                         time.time() - start)
        else:
            self.log_test("Environment", "Python Version", "FAIL",
                         f"Python {version.major}.{version.minor} (need 3.8+)",
                         time.time() - start)
    
    def test_dependencies(self):
        """Test 2: Required Dependencies"""
        print("\n" + "="*60)
        print("📦 Testing Dependencies")
        print("="*60)
        
        dependencies = [
            ("streamlit", "1.28.0", "UI Framework"),
            ("pandas", None, "Data Analysis"),
            ("openai", None, "GPT API"),
            ("google-generativeai", None, "Gemini API"),
            ("beautifulsoup4", None, "HTML Parsing"),
            ("requests", None, "HTTP Client"),
            ("python-dotenv", None, "Environment"),
            ("yfinance", None, "Market Data")
        ]
        
        for package, min_version, description in dependencies:
            start = time.time()
            try:
                module = importlib.import_module(package.replace("-", "_"))
                version = getattr(module, "__version__", "unknown")
                self.log_test("Dependencies", package, "PASS", 
                             f"v{version} - {description}",
                             time.time() - start)
            except ImportError:
                self.log_test("Dependencies", package, "FAIL",
                             f"Not installed - {description}",
                             time.time() - start)
    
    def test_file_structure(self):
        """Test 3: Project File Structure"""
        print("\n" + "="*60)
        print("📁 Testing File Structure")
        print("="*60)
        
        required_files = {
            # Core files
            "hedge_intelligence.py": "Main application",
            ".env": "Environment variables",
            "requirements.txt": "Dependencies",
            
            # Services
            "services/ai_service.py": "AI integration",
            "services/document_service.py": "Document handling",
            "services/watchlist_service.py": "Watchlist management",
            "services/sec_scraper.py": "SEC data fetcher",
            
            # Components
            "components/chat.py": "Chat interface",
            "components/dashboard.py": "Main dashboard",
            "components/document_viewer.py": "Document display",
            "components/ipo_tracker.py": "IPO tracking",
            
            # Utils
            "utils/doc_processor.py": "Document processing",
            "utils/helpers.py": "Helper functions",
            
            # Scrapers
            "scrapers/iposcoop_scraper.py": "IPO data scraper",
            "scrapers/cik_resolver.py": "Company CIK lookup"
        }
        
        for filepath, description in required_files.items():
            start = time.time()
            path = Path(filepath)
            
            if path.exists():
                size = path.stat().st_size
                self.log_test("Files", filepath, "PASS",
                             f"{size:,} bytes - {description}",
                             time.time() - start)
            else:
                if filepath == ".env":
                    self.log_test("Files", filepath, "WARN",
                                 f"Missing - {description}",
                                 time.time() - start)
                else:
                    self.log_test("Files", filepath, "FAIL",
                                 f"Not found - {description}",
                                 time.time() - start)
    
    def test_data_directories(self):
        """Test 4: Data Directories"""
        print("\n" + "="*60)
        print("📂 Testing Data Directories")
        print("="*60)
        
        data_dirs = {
            "data": "Root data directory",
            "data/sec_documents": "SEC filings storage",
            "data/watchlists": "User watchlists",
            "data/chat_history": "Chat conversations",
            "data/ipo_pipeline": "IPO tracking data",
            "data/company_requests": "Company addition requests"
        }
        
        for dir_path, description in data_dirs.items():
            start = time.time()
            path = Path(dir_path)
            
            if path.exists() and path.is_dir():
                # Count contents
                if "sec_documents" in dir_path and path.exists():
                    companies = len(list(path.iterdir()))
                    total_files = sum(len(list(p.glob("*"))) for p in path.iterdir() if p.is_dir())
                    self.log_test("Directories", dir_path, "PASS",
                                 f"{companies} companies, {total_files} files - {description}",
                                 time.time() - start)
                else:
                    file_count = len(list(path.glob("*")))
                    self.log_test("Directories", dir_path, "PASS",
                                 f"{file_count} items - {description}",
                                 time.time() - start)
            else:
                self.log_test("Directories", dir_path, "WARN",
                             f"Missing - {description}",
                             time.time() - start)
    
    def test_sec_documents(self):
        """Test 5: SEC Document Analysis"""
        print("\n" + "="*60)
        print("📄 Testing SEC Documents")
        print("="*60)
        
        sec_path = Path("data/sec_documents")
        if not sec_path.exists():
            self.log_test("SEC Docs", "Directory", "FAIL", "No SEC documents directory")
            return
            
        companies = list(sec_path.iterdir())
        if not companies:
            self.log_test("SEC Docs", "Companies", "WARN", "No companies found")
            return
            
        # Test sample company
        test_company = companies[0]
        self.log_test("SEC Docs", "Companies Found", "PASS", 
                     f"{len(companies)} companies available")
        
        # Check document types
        doc_types = {
            "10-K": 0,
            "10-Q": 0,
            "8-K": 0,
            "S-1": 0,
            "Other": 0
        }
        
        for company_dir in companies[:3]:  # Check first 3 companies
            for doc in company_dir.glob("*.html"):
                doc_name = doc.name.upper()
                if "10-K" in doc_name:
                    doc_types["10-K"] += 1
                elif "10-Q" in doc_name:
                    doc_types["10-Q"] += 1
                elif "8-K" in doc_name:
                    doc_types["8-K"] += 1
                elif "S-1" in doc_name:
                    doc_types["S-1"] += 1
                else:
                    doc_types["Other"] += 1
        
        for doc_type, count in doc_types.items():
            if count > 0:
                self.log_test("SEC Docs", f"{doc_type} Forms", "PASS", f"{count} found")
    
    def test_api_configuration(self):
        """Test 6: API Configuration"""
        print("\n" + "="*60)
        print("🔑 Testing API Configuration")
        print("="*60)
        
        env_path = Path(".env")
        if not env_path.exists():
            self.log_test("APIs", "Environment File", "FAIL", ".env file missing")
            return
            
        # Read environment variables
        with open(env_path, 'r') as f:
            env_content = f.read()
            
        # Check for API keys (don't log actual values)
        api_keys = {
            "OPENAI_API_KEY": "OpenAI GPT access",
            "GOOGLE_API_KEY": "Google Gemini access",
            "BING_API_KEY": "Bing search (optional)"
        }
        
        for key, description in api_keys.items():
            if key in env_content and f"{key}=" in env_content:
                # Check if it has a value (not just KEY=)
                if f"{key}=your_" not in env_content and f"{key}=''" not in env_content:
                    self.log_test("APIs", key, "PASS", f"Configured - {description}")
                else:
                    self.log_test("APIs", key, "WARN", f"Placeholder value - {description}")
            else:
                if "BING" in key:
                    self.log_test("APIs", key, "INFO", f"Not configured - {description}")
                else:
                    self.log_test("APIs", key, "FAIL", f"Missing - {description}")
    
    def test_streamlit_app(self):
        """Test 7: Streamlit App Structure"""
        print("\n" + "="*60)
        print("🎯 Testing Streamlit App")
        print("="*60)
        
        start = time.time()
        
        # Check if hedge_intelligence.py has proper structure
        if not Path("hedge_intelligence.py").exists():
            self.log_test("Streamlit", "Main App", "FAIL", "hedge_intelligence.py not found")
            return
            
        with open("hedge_intelligence.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for essential Streamlit components
        checks = {
            "import streamlit": "Streamlit import",
            "st.set_page_config": "Page configuration",
            "def main()": "Main function",
            "if __name__": "Entry point"
        }
        
        for pattern, description in checks.items():
            if pattern in content:
                self.log_test("Streamlit", description, "PASS", "Found in main app")
            else:
                self.log_test("Streamlit", description, "FAIL", "Missing from main app")
                
        # Check for navigation
        if "selectbox" in content or "sidebar" in content:
            self.log_test("Streamlit", "Navigation", "PASS", "Navigation components found")
        else:
            self.log_test("Streamlit", "Navigation", "WARN", "No navigation found")
            
        duration = time.time() - start
        self.log_test("Streamlit", "App Structure", "PASS", 
                     f"Analysis complete", duration)
    
    def test_services_integration(self):
        """Test 8: Service Integration"""
        print("\n" + "="*60)
        print("🔌 Testing Service Integration")
        print("="*60)
        
        # Test AI Service
        try:
            from services.ai_service import AIService
            ai = AIService()
            self.log_test("Services", "AI Service", "PASS", "Initialized successfully")
            
            # Check methods
            if hasattr(ai, 'process_query'):
                self.log_test("Services", "AI process_query", "PASS", "Method available")
            else:
                self.log_test("Services", "AI process_query", "WARN", "Method missing")
                
        except Exception as e:
            self.log_test("Services", "AI Service", "FAIL", str(e))
            
        # Test Document Service
        try:
            from services.document_service import DocumentService
            doc = DocumentService()
            self.log_test("Services", "Document Service", "PASS", "Initialized successfully")
            
            # Check if can list companies
            companies = doc.get_companies()
            if companies:
                self.log_test("Services", "Document Access", "PASS", 
                             f"{len(companies)} companies accessible")
            else:
                self.log_test("Services", "Document Access", "WARN", "No companies found")
                
        except Exception as e:
            self.log_test("Services", "Document Service", "FAIL", str(e))
    
    def test_sample_workflow(self):
        """Test 9: Sample Workflow"""
        print("\n" + "="*60)
        print("🔄 Testing Sample Workflow")
        print("="*60)
        
        try:
            # 1. Load a document
            from services.document_service import DocumentService
            doc_service = DocumentService()
            
            companies = doc_service.get_companies()
            if not companies:
                self.log_test("Workflow", "Load Companies", "FAIL", "No companies available")
                return
                
            self.log_test("Workflow", "Load Companies", "PASS", 
                         f"Found {len(companies)} companies")
            
            # 2. Get documents for first company
            first_company = companies[0]
            docs = doc_service.get_company_documents(first_company)
            
            if docs:
                self.log_test("Workflow", "Load Documents", "PASS",
                             f"Found {len(docs)} documents for {first_company}")
                
                # 3. Load first document
                if docs:
                    first_doc = docs[0]
                    content = doc_service.get_document_content(first_company, first_doc)
                    if content:
                        self.log_test("Workflow", "Read Document", "PASS",
                                     f"Loaded {len(content):,} characters")
                    else:
                        self.log_test("Workflow", "Read Document", "FAIL",
                                     "Could not read document")
            else:
                self.log_test("Workflow", "Load Documents", "FAIL",
                             f"No documents for {first_company}")
                
        except Exception as e:
            self.log_test("Workflow", "Sample Workflow", "FAIL", str(e))
            traceback.print_exc()
    
    def test_performance(self):
        """Test 10: Performance Metrics"""
        print("\n" + "="*60)
        print("⚡ Testing Performance")
        print("="*60)
        
        # Test document loading speed
        start = time.time()
        try:
            from services.document_service import DocumentService
            doc_service = DocumentService()
            companies = doc_service.get_companies()
            
            load_time = time.time() - start
            if load_time < 1.0:
                self.log_test("Performance", "Company List Load", "PASS",
                             f"Loaded in {load_time:.3f}s")
            else:
                self.log_test("Performance", "Company List Load", "WARN",
                             f"Slow load: {load_time:.3f}s")
                
        except Exception as e:
            self.log_test("Performance", "Company List Load", "FAIL", str(e))
            
        # Test memory usage
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb < 500:
            self.log_test("Performance", "Memory Usage", "PASS",
                         f"{memory_mb:.1f} MB")
        else:
            self.log_test("Performance", "Memory Usage", "WARN",
                         f"High usage: {memory_mb:.1f} MB")
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*70)
        print("📊 HEDGE INTELLIGENCE TEST REPORT")
        print("="*70)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"User: thorrobber22")
        print(f"Total Duration: {time.time() - self.test_start:.2f}s")
        print("="*70)
        
        # Count results by status
        status_counts = {}
        for result in self.test_results:
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            
        # Summary table
        print("\n📈 Test Summary:")
        print("-"*40)
        print(f"{'Status':<10} {'Count':<10} {'Percentage':<10}")
        print("-"*40)
        
        total_tests = len(self.test_results)
        for status, count in sorted(status_counts.items()):
            percentage = (count / total_tests) * 100
            print(f"{status:<10} {count:<10} {percentage:.1f}%")
            
        print("-"*40)
        print(f"{'TOTAL':<10} {total_tests:<10} 100.0%")
        
        # Critical errors
        if self.critical_errors:
            print("\n❌ Critical Errors:")
            for error in self.critical_errors:
                print(f"  - {error}")
                
        # Warnings
        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
                
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'user': 'thorrobber22',
            'duration': time.time() - self.test_start,
            'summary': status_counts,
            'critical_errors': self.critical_errors,
            'warnings': self.warnings,
            'detailed_results': self.test_results
        }
        
        report_path = Path("test_report_v3.json")
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        # Final verdict
        if not self.critical_errors:
            print("\n✅ ALL TESTS PASSED!")
            print("Hedge Intelligence is ready to launch.")
            print("\nRun: streamlit run hedge_intelligence.py")
        elif len(self.critical_errors) <= 2:
            print("\n⚠️  MINOR ISSUES DETECTED")
            print("The platform should work with limited functionality.")
            print("Review critical errors above.")
        else:
            print("\n❌ MULTIPLE FAILURES DETECTED")
            print("Please fix critical errors before launching.")
            
    def run_all_tests(self):
        """Execute complete test suite"""
        print("🚀 HEDGE INTELLIGENCE - PRODUCTION TEST V3")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"User: thorrobber22")
        print("="*70)
        
        # Run test suite
        self.test_python_version()
        self.test_dependencies()
        self.test_file_structure()
        self.test_data_directories()
        self.test_sec_documents()
        self.test_api_configuration()
        self.test_streamlit_app()
        self.test_services_integration()
        self.test_sample_workflow()
        self.test_performance()
        
        # Generate report
        self.generate_report()

def main():
    """Run production test"""
    # Check if psutil is available for performance testing
    try:
        import psutil
    except ImportError:
        print("Installing psutil for performance testing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        
    tester = HedgeIntelligenceTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main()