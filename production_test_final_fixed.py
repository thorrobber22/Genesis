#!/usr/bin/env python3
"""
Hedge Intelligence - Final Production Test (Fixed)
Date: 2025-06-09 00:38:42 UTC
Author: thorrobber22
Description: Complete production readiness test with os import fixed
"""

import subprocess
import sys
import os  # THIS WAS MISSING!
import time
import json
import traceback
from pathlib import Path
from datetime import datetime
import psutil

class ProductionTest:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'user': 'thorrobber22',
            'tests': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
        
    def run_test(self, category, name, test_func):
        """Run a single test"""
        start_time = time.time()
        
        try:
            result, details = test_func()
            status = 'PASS' if result else 'FAIL'
            
            if result and details.startswith('WARNING:'):
                status = 'WARN'
                details = details[8:]
                
        except Exception as e:
            status = 'FAIL'
            details = f"Exception: {str(e)}"
            traceback.print_exc()
            
        duration = time.time() - start_time
        
        test_result = {
            'category': category,
            'name': name,
            'status': status,
            'details': details,
            'duration': duration
        }
        
        self.results['tests'].append(test_result)
        self.results['summary']['total'] += 1
        
        if status == 'PASS':
            self.results['summary']['passed'] += 1
            print(f"✅ [{category}] {name}: PASSED ({duration:.2f}s)")
        elif status == 'WARN':
            self.results['summary']['warnings'] += 1
            print(f"⚠️  [{category}] {name}: WARNING - {details}")
        else:
            self.results['summary']['failed'] += 1
            print(f"❌ [{category}] {name}: FAILED - {details}")
            
    def test_core_files(self):
        """Test 1: Core Files Exist"""
        print("\n📁 Testing Core Files")
        print("-"*60)
        
        core_files = {
            'hedge_intelligence.py': 'Main application',
            'services/ai_service.py': 'AI integration',
            'services/document_service.py': 'Document handling',
            'components/document_explorer.py': 'File explorer',
            'components/persistent_chat.py': 'Chat interface',
            'components/data_extractor.py': 'Data extraction',
            'components/ipo_tracker_enhanced.py': 'IPO tracker',
            'data/sec_documents': 'SEC documents directory'
        }
        
        for filepath, description in core_files.items():
            self.run_test('Files', filepath, 
                lambda p=filepath: (Path(p).exists(), description))
                
    def test_dependencies(self):
        """Test 2: Python Dependencies"""
        print("\n📦 Testing Dependencies")
        print("-"*60)
        
        critical_deps = [
            ('streamlit', 'streamlit'),
            ('pandas', 'pandas'),
            ('openai', 'openai'),
            ('google.generativeai', 'google-generativeai'),
            ('bs4', 'beautifulsoup4'),
            ('dotenv', 'python-dotenv'),
            ('requests', 'requests')
        ]
        
        for import_name, package_name in critical_deps:
            def check_dep(imp=import_name, pkg=package_name):
                try:
                    __import__(imp)
                    return True, f"{pkg} installed"
                except ImportError:
                    return False, f"{pkg} not installed"
                    
            self.run_test('Dependencies', package_name, check_dep)
            
    def test_sec_documents(self):
        """Test 3: SEC Document Access"""
        print("\n📄 Testing SEC Documents")
        print("-"*60)
        
        def check_documents():
            doc_path = Path('data/sec_documents')
            if not doc_path.exists():
                return False, "SEC documents directory missing"
                
            companies = [d for d in doc_path.iterdir() if d.is_dir()]
            if not companies:
                return False, "No companies found"
                
            # Count documents properly
            total_files = 0
            company_details = []
            
            for company in companies[:3]:  # Check first 3
                files = list(company.glob('*.html'))
                total_files += len(files)
                company_details.append(f"{company.name}({len(files)})")
                
            details = f"{len(companies)} companies: {', '.join(company_details)}..."
            return True, details
            
        self.run_test('Data', 'SEC Documents', check_documents)
        
        # Test document categorization
        def check_filing_types():
            doc_path = Path('data/sec_documents')
            if not doc_path.exists():
                return False, "No documents to check"
                
            filing_types = {'10-K': 0, '10-Q': 0, '8-K': 0, 'S-1': 0}
            
            for company in doc_path.iterdir():
                if company.is_dir():
                    for doc in company.glob('*.html'):
                        name = doc.name.upper()
                        if '10-K' in name or '10K' in name:
                            filing_types['10-K'] += 1
                        elif '10-Q' in name or '10Q' in name:
                            filing_types['10-Q'] += 1
                        elif '8-K' in name or '8K' in name:
                            filing_types['8-K'] += 1
                        elif 'S-1' in name or 'S1' in name:
                            filing_types['S-1'] += 1
                            
            summary = ', '.join([f"{k}:{v}" for k,v in filing_types.items() if v > 0])
            return True, f"Filing types: {summary}"
            
        self.run_test('Data', 'Filing Types', check_filing_types)
        
    def test_api_configuration(self):
        """Test 4: API Configuration"""
        print("\n🔑 Testing API Configuration")
        print("-"*60)
        
        def check_env_file():
            if not Path('.env').exists():
                return False, ".env file missing"
            return True, ".env file exists"
            
        self.run_test('Config', 'Environment File', check_env_file)
        
        def check_api_keys():
            if not Path('.env').exists():
                return False, "No .env file"
                
            with open('.env', 'r') as f:
                content = f.read()
                
            keys_status = []
            
            # Check OpenAI
            if 'OPENAI_API_KEY=' in content:
                if 'your_openai_api_key' not in content and 'sk-' in content:
                    keys_status.append("OpenAI:✓")
                else:
                    keys_status.append("OpenAI:placeholder")
            else:
                keys_status.append("OpenAI:missing")
                
            # Check Google
            if 'GOOGLE_API_KEY=' in content:
                if 'your_google_api_key' not in content:
                    keys_status.append("Google:✓")
                else:
                    keys_status.append("Google:placeholder")
            else:
                keys_status.append("Google:missing")
                
            return True, f"WARNING:{', '.join(keys_status)}"
            
        self.run_test('Config', 'API Keys', check_api_keys)
        
    def test_streamlit_app(self):
        """Test 5: Streamlit App Structure"""
        print("\n🎯 Testing Streamlit App")
        print("-"*60)
        
        def check_app_structure():
            with open('hedge_intelligence.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
            checks = {
                'import streamlit': 'Streamlit import',
                'DocumentExplorer': 'Document Explorer component',
                'PersistentChat': 'Persistent Chat component',
                'apply_dark_theme': 'Dark theme function',
                'st.set_page_config': 'Page config'
            }
            
            missing = []
            for pattern, desc in checks.items():
                if pattern not in content:
                    missing.append(desc)
                    
            if missing:
                return False, f"Missing: {', '.join(missing)}"
                
            # Check NO BLUE
            if '#007bff' in content.lower() or 'color: blue' in content.lower():
                return True, "WARNING:Blue styling detected - should be grey!"
                
            return True, "All components present, grey theme"
            
        self.run_test('App', 'Streamlit Structure', check_app_structure)
        
    def test_services(self):
        """Test 6: Service Integration"""
        print("\n🔌 Testing Services")
        print("-"*60)
        
        def test_document_service():
            try:
                from services.document_service import DocumentService
                ds = DocumentService()
                companies = ds.get_companies()
                
                if not companies:
                    return True, "WARNING:No companies found"
                    
                # Test getting documents
                docs = ds.get_company_documents(companies[0])
                
                # Check if returns strings (not dicts)
                if isinstance(docs, list) and len(docs) > 0:
                    if isinstance(docs[0], str):
                        return True, f"Working correctly - {len(companies)} companies"
                    else:
                        return False, "Returns dicts instead of strings - needs fix"
                else:
                    return True, "WARNING:No documents found"
                    
            except Exception as e:
                return False, str(e)
                
        def test_ai_service():
            try:
                from services.ai_service import AIService
                ai = AIService()
                
                # Check for required method
                if hasattr(ai, 'get_ai_response'):
                    return True, "Has get_ai_response method"
                elif hasattr(ai, 'process_query'):
                    return True, "WARNING:Has process_query but not get_ai_response"
                else:
                    return False, "Missing required AI methods"
                    
            except Exception as e:
                return False, str(e)
                
        self.run_test('Services', 'Document Service', test_document_service)
        self.run_test('Services', 'AI Service', test_ai_service)
        
    def test_new_components(self):
        """Test 7: New Refactored Components"""
        print("\n🆕 Testing New Components")
        print("-"*60)
        
        components = [
            ('components.document_explorer', 'DocumentExplorer', 'Document Explorer'),
            ('components.persistent_chat', 'PersistentChat', 'Persistent Chat'),
            ('components.data_extractor', 'DataExtractor', 'Data Extractor'),
            ('components.ipo_tracker_enhanced', 'IPOTrackerEnhanced', 'IPO Tracker')
        ]
        
        for module_name, class_name, description in components:
            def test_component(mod=module_name, cls=class_name, desc=description):
                try:
                    module = __import__(mod, fromlist=[cls])
                    if hasattr(module, cls):
                        # Try to instantiate
                        instance = getattr(module, cls)()
                        return True, f"{desc} works"
                    else:
                        return False, f"{cls} not found in module"
                except Exception as e:
                    return False, f"Error: {str(e)}"
                    
            self.run_test('Components', description, test_component)
            
    def test_performance(self):
        """Test 8: Performance Metrics"""
        print("\n⚡ Testing Performance")
        print("-"*60)
        
        def check_memory():
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb < 300:
                return True, f"Memory usage: {memory_mb:.1f} MB - Good"
            elif memory_mb < 500:
                return True, f"WARNING:Memory usage: {memory_mb:.1f} MB - High"
            else:
                return False, f"Memory usage: {memory_mb:.1f} MB - Too high"
                
        self.run_test('Performance', 'Memory Usage', check_memory)
        
    def generate_report(self):
        """Generate final report"""
        print("\n" + "="*70)
        print("📊 PRODUCTION TEST REPORT - HEDGE INTELLIGENCE")
        print("="*70)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"User: thorrobber22")
        print("="*70)
        
        summary = self.results['summary']
        print(f"\nTotal Tests: {summary['total']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⚠️  Warnings: {summary['warnings']}")
        
        # Success rate
        success_rate = (summary['passed'] / summary['total']) * 100 if summary['total'] > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        # Critical failures
        failures = [t for t in self.results['tests'] if t['status'] == 'FAIL']
        if failures:
            print("\n❌ CRITICAL FAILURES:")
            for fail in failures:
                print(f"  - [{fail['category']}] {fail['name']}: {fail['details']}")
                
        # Warnings
        warnings = [t for t in self.results['tests'] if t['status'] == 'WARN']
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warn in warnings:
                print(f"  - [{warn['category']}] {warn['name']}: {warn['details']}")
                
        # Save report
        with open('production_test_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
            
        print(f"\n📄 Detailed report saved: production_test_report.json")
        
        # Final verdict
        if summary['failed'] == 0:
            print("\n🎉 PRODUCTION READY!")
            print("All critical tests passed. Ready to launch:")
            print("  streamlit run hedge_intelligence.py")
        elif summary['failed'] <= 2:
            print("\n⚠️  MOSTLY READY")
            print("Minor issues detected. Fix remaining issues:")
            print("  1. Run: python final_fix.py")
            print("  2. Update GOOGLE_API_KEY in .env")
            print("  3. Then: streamlit run hedge_intelligence.py")
        else:
            print("\n❌ NOT READY")
            print("Multiple critical failures. Run fixes:")
            print("  python quick_fix_all.py")
            
    def run_all_tests(self):
        """Execute complete test suite"""
        print("🚀 HEDGE INTELLIGENCE - PRODUCTION TEST")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"User: thorrobber22")
        print("="*70)
        
        self.test_core_files()
        self.test_dependencies()
        self.test_sec_documents()
        self.test_api_configuration()
        self.test_streamlit_app()
        self.test_services()
        self.test_new_components()
        self.test_performance()
        
        self.generate_report()

def main():
    # Run production test directly
    tester = ProductionTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main()