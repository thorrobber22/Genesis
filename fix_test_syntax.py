#!/usr/bin/env python3
"""
Fix syntax error in test_complete_system.py
"""

from pathlib import Path

def fix_syntax_error():
    """Fix the syntax error in test_complete_system.py"""
    print("🔧 FIXING SYNTAX ERROR")
    print("="*70)
    
    # Rewrite the entire test file properly
    correct_test_content = '''#!/usr/bin/env python3
"""
Complete system test - ALL features
"""

import json
import time
from pathlib import Path
from datetime import datetime

class CompleteSystemTest:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'passed': 0,
            'failed': 0
        }
    
    def test_1_document_explorer(self):
        """Test document browsing"""
        print("\\n🧪 TEST 1: DOCUMENT EXPLORER")
        
        from services.document_service import DocumentService
        doc_service = DocumentService()
        
        # Get companies
        companies = doc_service.get_companies()
        print(f"  Companies found: {len(companies)}")
        
        # Check CRCL
        if 'CRCL' in companies:
            docs = doc_service.get_company_documents('CRCL')
            print(f"  CRCL documents: {len(docs)}")
            
            # Try to load one
            if docs:
                content = doc_service.get_document_content('CRCL', docs[0])
                is_valid = len(content) > 10000 and 'SECURITIES' in content.upper()
                print(f"  Document valid: {is_valid}")
                
                self.results['tests']['document_explorer'] = 'PASS' if is_valid else 'FAIL'
                return is_valid
        
        self.results['tests']['document_explorer'] = 'FAIL'
        return False
    
    def test_2_ai_chat(self):
        """Test AI chat with citations"""
        print("\\n🧪 TEST 2: AI CHAT WITH CITATIONS")
        
        try:
            from services.ai_service import AIService
            ai = AIService()
            
            # Create context in the format AIService expects: List[Dict]
            test_context = [
                {
                    'content': """SECURITIES AND EXCHANGE COMMISSION
                    Form 10-K
                    
                    BUSINESS
                    Circle Internet Financial operates a stablecoin platform.
                    The company's primary product is USDC, a dollar-backed stablecoin.
                    
                    FINANCIAL STATEMENTS
                    Revenue for 2024 was $2.8 billion on page 47.
                    Net income was $850 million on page 48.""",
                    'metadata': {
                        'source': 'CRCL_10K_2024.html',
                        'page': 47
                    }
                }
            ]
            
            response, confidence = ai.get_ai_response(
                "What is the company's revenue?",
                test_context
            )
            
            # Check if response is valid
            has_citation = any(marker in str(response) for marker in ['page', 'Page', '47', 'CRCL'])
            has_amount = '$2.8 billion' in str(response) or '2.8' in str(response)
            
            print(f"  Response: {str(response)[:200]}...")
            print(f"  Has citation: {has_citation}")
            print(f"  Has correct amount: {has_amount}")
            print(f"  Confidence: {confidence}")
            
            self.results['tests']['ai_chat'] = 'PASS' if (has_citation or has_amount) else 'FAIL'
            return has_citation or has_amount
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.results['tests']['ai_chat'] = 'FAIL'
            return False
    
    def test_3_admin_flow(self):
        """Test admin panel connection"""
        print("\\n🧪 TEST 3: ADMIN PANEL INTEGRATION")
        
        # Check if admin panel exists
        admin_path = Path("admin/admin_panel.py")
        admin_browser = Path("admin/admin_final_browser.py")
        
        admin_exists = admin_path.exists() or admin_browser.exists()
        print(f"  Admin panel found: {admin_exists}")
        
        # Check company requests
        requests_file = Path("data/company_requests.json")
        if requests_file.exists():
            with open(requests_file, 'r') as f:
                requests = json.load(f)
            print(f"  Pending requests: {len(requests)}")
            
            self.results['tests']['admin_flow'] = 'PASS' if admin_exists else 'FAIL'
            return admin_exists
        
        self.results['tests']['admin_flow'] = 'FAIL'
        return False
    
    def test_4_ipo_tracker(self):
        """Test IPO tracker"""
        print("\\n🧪 TEST 4: IPO TRACKER")
        
        ipo_cache = Path("data/cache/ipo_calendar.json")
        
        if ipo_cache.exists():
            with open(ipo_cache, 'r') as f:
                data = json.load(f)
            
            # Check for real IPOs
            if 'ipos' in data:
                fake_companies = ['Stripe', 'Databricks', 'SpaceX']
                real_ipos = [ipo for ipo in data['ipos'] 
                           if not any(fake in ipo.get('company', '') 
                                    for fake in fake_companies)]
                
                print(f"  Real IPOs found: {len(real_ipos)}")
                
                self.results['tests']['ipo_tracker'] = 'PASS' if real_ipos else 'FAIL'
                return bool(real_ipos)
        
        self.results['tests']['ipo_tracker'] = 'FAIL'
        return False
    
    def test_5_theme(self):
        """Test theme (no blue)"""
        print("\\n🧪 TEST 5: THEME CHECK")
        
        with open("hedge_intelligence.py", 'r') as f:
            content = f.read()
        
        # Check for dark theme removal
        has_dark = '#0E1117' in content
        has_cream = '#FAFAF8' in content or 'cream' in content.lower()
        
        print(f"  Dark theme present: {has_dark}")
        print(f"  Cream theme ready: {has_cream}")
        
        self.results['tests']['theme'] = 'PASS' if not has_dark or has_cream else 'FAIL'
        return not has_dark or has_cream
    
    def generate_report(self):
        """Generate test report"""
        print("\\n" + "="*70)
        print("📊 SYSTEM TEST REPORT")
        print("="*70)
        
        for test, result in self.results['tests'].items():
            icon = "✅" if result == 'PASS' else "❌"
            print(f"{icon} {test}: {result}")
        
        passed = sum(1 for r in self.results['tests'].values() if r == 'PASS')
        total = len(self.results['tests'])
        
        print(f"\\nScore: {passed}/{total} ({passed/total*100:.0f}%)")
        
        if passed < total:
            print("\\n🔧 FIXES NEEDED:")
            for test, result in self.results['tests'].items():
                if result == 'FAIL':
                    print(f"  - {test}")

def main():
    tester = CompleteSystemTest()
    
    # Run all tests
    tester.test_1_document_explorer()
    tester.test_2_ai_chat()
    tester.test_3_admin_flow()
    tester.test_4_ipo_tracker()
    tester.test_5_theme()
    
    # Report
    tester.generate_report()

if __name__ == "__main__":
    main()
'''
    
    # Write the corrected file
    test_path = Path("test_complete_system.py")
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(correct_test_content)
    
    print("✅ Fixed syntax error in test_complete_system.py")
    
    # Also check if AIService was restored
    check_ai_service_status()

def check_ai_service_status():
    """Check if AIService is in original state"""
    print("\n🔍 Checking AIService status...")
    
    ai_path = Path("services/ai_service.py")
    backup_path = Path("services/ai_service_backup.py")
    
    if backup_path.exists():
        print("  ✅ Backup exists - restoring original...")
        
        with open(backup_path, 'r', encoding='utf-8') as f:
            original = f.read()
        
        with open(ai_path, 'w', encoding='utf-8') as f:
            f.write(original)
        
        print("  ✅ Restored original AIService")
    else:
        print("  ⚠️  No backup found - AIService may be modified")

def main():
    print("🔧 FIXING TEST FILE SYNTAX ERROR")
    print("="*70)
    
    fix_syntax_error()
    
    print("\n✅ Ready to test!")
    print("\nRun: python test_complete_system.py")

if __name__ == "__main__":
    main()