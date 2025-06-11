#!/usr/bin/env python3
"""
Hedge Intelligence - Final Production Test
Date: 2025-06-09 00:29:36 UTC
Author: thorrobber22
Description: Complete production readiness test
"""

import subprocess
import sys
import time
import json
import traceback
from pathlib import Path
from datetime import datetime
import asyncio
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
                details = details[8:]  # Remove WARNING: prefix
                
        except Exception as e:
            status = 'FAIL'
            details = f"Exception: {str(e)}"
            traceback.print_exc()
            
        duration = time.time() - start_time
        
        # Log result
        test_result = {
            'category': category,
            'name': name,
            'status': status,
            'details': details,
            'duration': duration
        }
        
        self.results['tests'].append(test_result)
        
        # Update summary
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
            'streamlit',
            'pandas',
            'openai',
            'google.generativeai',
            'bs4',
            'dotenv',
            'requests'
        ]
        
        for dep in critical_deps:
            def check_dep(d=dep):
                try:
                    __import__(d)
                    return True, f"{d} installed"
                except ImportError:
                    return False, f"{d} not installed"
                    
            self.run_test('Dependencies', dep, check_dep)
            
    def test_sec_documents(self):
        """Test 3: SEC Document Access"""
        print("\n📄 Testing SEC Documents")
        print("-"*60)
        
        def check_documents():
            doc_path = Path('data/sec_documents')
            if not doc_path.exists():
                return False, "SEC documents directory missing"
                
            companies = list(doc_path.iterdir())
            if not companies:
                return False, "No companies found"
                
            total_files = sum(
                len(list(c.glob('*.html'))) 
                for c in companies if c.is_dir()
            )
            
            return True, f"{len(companies)} companies, {total_files} documents"
            
        self.run_test('Data', 'SEC Documents', check_documents)
        
    def test_api_configuration(self):
        """Test 4: API Configuration"""
        print("\n🔑 Testing API Configuration")
        print("-"*60)
        
        def check_openai():
            if not Path('.env').exists():
                return False, ".env file missing"
                
            with open('.env', 'r') as f:
                content = f.read()
                
            if 'OPENAI_API_KEY=' in content:
                if 'your_openai_api_key' not in content:
                    return True, "OpenAI API key configured"
                else:
                    return True, "WARNING:OpenAI API key is placeholder"
            return False, "OpenAI API key missing"
            
        def check_google():
            with open('.env', 'r') as f:
                content = f.read()
                
            if 'GOOGLE_API_KEY=' in content:
                if 'your_google_api_key' not in content:
                    return True, "Google API key configured"
                else:
                    return True, "WARNING:Google API key is placeholder"
            return False, "Google API key missing"
            
        self.run_test('API', 'OpenAI Configuration', check_openai)
        self.run_test('API', 'Google Configuration', check_google)
        
    def test_streamlit_app(self):
        """Test 5: Streamlit App Structure"""
        print("\n🎯 Testing Streamlit App")
        print("-"*60)
        
        def check_app_structure():
            with open('hedge_intelligence.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
            required = [
                'import streamlit',
                'st.set_page_config',
                'apply_dark_theme',
                'DocumentExplorer',
                'PersistentChat'
            ]
            
            missing = [r for r in required if r not in content]
            
            if missing:
                return False, f"Missing: {', '.join(missing)}"
                
            # Check for blue styling
            if '#007bff' in content.lower() or 'blue' in content.lower():
                return True, "WARNING:Blue styling detected"
                
            return True, "All components present, no blue styling"
            
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
                
                if isinstance(docs, list) and all(isinstance(d, str) for d in docs):
                    return True, f"Service working - {len(companies)} companies"
                else:
                    return False, "Document service returns wrong type"
                    
            except Exception as e:
                return False, str(e)
                
        def test_ai_service():
            try:
                from services.ai_service import AIService
                ai = AIService()
                
                # Check for required method
                if hasattr(ai, 'get_ai_response'):
                    return True, "AI service has required methods"
                else:
                    return True, "WARNING:get_ai_response method missing"
                    
            except Exception as e:
                return False, str(e)
                
        self.run_test('Services', 'Document Service', test_document_service)
        self.run_test('Services', 'AI Service', test_ai_service)
        
    def test_performance(self):
        """Test 7: Performance Metrics"""
        print("\n⚡ Testing Performance")
        print("-"*60)
        
        def check_memory():
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb < 300:
                return True, f"Memory usage: {memory_mb:.1f} MB"
            else:
                return True, f"WARNING:High memory: {memory_mb:.1f} MB"
                
        def check_startup_time():
            start = time.time()
            
            # Import main modules
            try:
                import streamlit
                from services.document_service import DocumentService
                from services.ai_service import AIService
                
                duration = time.time() - start
                
                if duration < 3.0:
                    return True, f"Startup time: {duration:.2f}s"
                else:
                    return True, f"WARNING:Slow startup: {duration:.2f}s"
                    
            except Exception as e:
                return False, str(e)
                
        self.run_test('Performance', 'Memory Usage', check_memory)
        self.run_test('Performance', 'Startup Time', check_startup_time)
        
    def generate_report(self):
        """Generate final report"""
        print("\n" + "="*70)
        print("📊 PRODUCTION TEST REPORT")
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
            print("Minor issues detected. Review failures above.")
        else:
            print("\n❌ NOT READY")
            print("Multiple critical failures. Fix issues before launch.")
            
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
        self.test_performance()
        
        self.generate_report()

def main():
    # First generate context
    print("Step 1: Generating full context...")
    os.system("python generate_full_context.py")
    
    print("\n" + "="*70)
    print("\nStep 2: Running production test...")
    
    # Run production test
    tester = ProductionTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main()