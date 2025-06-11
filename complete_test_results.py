#!/usr/bin/env python3
"""
Complete the test results display and production test suite
Date: 2025-06-09 17:35:36 UTC
"""

def show_results(self):
    """Show test results"""
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)
    
    passed = sum(1 for v in self.test_results.values() if v == 'PASS')
    total = len(self.test_results)
    failed = sum(1 for v in self.test_results.values() if v == 'FAIL')
    warnings = sum(1 for v in self.test_results.values() if v == 'WARNING')
    
    # Calculate percentage
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    # Show summary
    print(f"\nSUMMARY:")
    print(f"Total Tests: {total}")
    print(f"✅ Passed:   {passed} ({pass_rate:.1f}%)")
    print(f"⚠️  Warnings: {warnings}")
    print(f"❌ Failed:   {failed}")
    
    # Show detailed results
    print("\nDETAILED RESULTS:")
    print("-" * 80)
    
    # Group by category
    categories = {
        'Admin Features': [],
        'User Features': [],
        'Data & Documents': [],
        'Integration': []
    }
    
    # Categorize tests
    for test_name, result in self.test_results.items():
        if any(x in test_name for x in ['ipo', 'cik', 'sec', 'admin', 'request']):
            categories['Admin Features'].append((test_name, result))
        elif any(x in test_name for x in ['document', 'chat', 'search', 'dashboard', 'download']):
            categories['User Features'].append((test_name, result))
        elif any(x in test_name for x in ['data', 'files', 'api']):
            categories['Data & Documents'].append((test_name, result))
        else:
            categories['Integration'].append((test_name, result))
    
    # Display by category
    for category, tests in categories.items():
        if tests:
            print(f"\n{category}:")
            for test_name, result in tests:
                icon = "✅" if result == "PASS" else "⚠️ " if result == "WARNING" else "❌"
                print(f"  {icon} {test_name}: {result}")
    
    # Show critical failures
    failures = [(k, v) for k, v in self.test_results.items() if v == 'FAIL']
    if failures:
        print("\n" + "="*80)
        print("CRITICAL FAILURES (Must Fix):")
        print("="*80)
        for test_name, _ in failures:
            print(f"❌ {test_name}")
            if test_name in self.failure_details:
                print(f"   Details: {self.failure_details[test_name]}")
    
    # Show recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    
    if pass_rate >= 90:
        print("✅ PRODUCTION READY!")
        print("   Your application is ready for production deployment.")
        print("   Consider fixing any warnings for optimal performance.")
    elif pass_rate >= 70:
        print("⚠️  MOSTLY READY")
        print("   Fix critical failures before production deployment.")
        print("   The application will work but may have issues.")
    else:
        print("❌ NOT READY")
        print("   Too many failures. Fix critical issues first.")
    
    # Generate fix script if needed
    if failed > 0:
        self.generate_fix_script(failures)
    
    # Save results
    self.save_results()
    
    return pass_rate

def generate_fix_script(self, failures):
    """Generate script to fix failures"""
    print("\n" + "="*80)
    print("GENERATING FIX SCRIPT")
    print("="*80)
    
    fix_commands = []
    
    for test_name, _ in failures:
        if 'ipo_scraper' in test_name:
            fix_commands.append({
                'issue': 'IPO Scraper not working',
                'fix': 'python -c "from scrapers.ipo_scraper import scrape_ipos; scrape_ipos()"'
            })
        elif 'document' in test_name:
            fix_commands.append({
                'issue': 'Document issues',
                'fix': 'python admin/admin_panel.py  # Download more documents'
            })
        elif 'api' in test_name:
            fix_commands.append({
                'issue': 'API configuration',
                'fix': 'Check .env file for API keys'
            })
    
    # Create fix script
    fix_script = '''#!/usr/bin/env python3
"""
Auto-generated fix script
Generated: {timestamp}
"""

import subprocess
import sys
from pathlib import Path

fixes = {fixes}

print("HEDGE INTELLIGENCE - AUTOMATED FIX")
print("="*60)

for fix in fixes:
    print(f"\\nFixing: {{fix['issue']}}")
    print(f"Command: {{fix['fix']}}")
    
    try:
        if fix['fix'].startswith('python'):
            subprocess.run(fix['fix'], shell=True, check=True)
            print("✅ Fixed")
        else:
            print(f"⚠️  Manual action required: {{fix['fix']}}")
    except Exception as e:
        print(f"❌ Failed: {{e}}")

print("\\n✅ Fix script completed!")
'''.format(
        timestamp=datetime.now().isoformat(),
        fixes=fix_commands
    )
    
    with open('fix_issues.py', 'w') as f:
        f.write(fix_script)
    
    print(f"✅ Fix script saved to: fix_issues.py")
    print("   Run: python fix_issues.py")

def save_results(self):
    """Save test results to file"""
    results_data = {
        'timestamp': datetime.now().isoformat(),
        'user': 'thorrobber22',
        'results': self.test_results,
        'stats': {
            'total': len(self.test_results),
            'passed': sum(1 for v in self.test_results.values() if v == 'PASS'),
            'failed': sum(1 for v in self.test_results.values() if v == 'FAIL'),
            'warnings': sum(1 for v in self.test_results.values() if v == 'WARNING')
        },
        'details': self.failure_details
    }
    
    results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")