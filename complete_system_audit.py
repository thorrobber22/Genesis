#!/usr/bin/env python3
"""
Hedge Intelligence - Complete System Audit
Date: 2025-06-09 01:53:18 UTC
Purpose: Audit entire system before making any changes
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
import subprocess

class CompleteSystemAudit:
    def __init__(self):
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'user': 'thorrobber22',
            'findings': {
                'documents': {},
                'admin_panel': {},
                'scrapers': {},
                'user_features': {},
                'data_flow': {}
            }
        }
    
    def audit_documents(self):
        """Audit all SEC documents"""
        print("\n" + "="*70)
        print("📁 DOCUMENT AUDIT")
        print("="*70)
        
        sec_path = Path("data/sec_documents")
        total_files = 0
        total_valid = 0
        problem_companies = []
        
        for company_dir in sec_path.iterdir():
            if company_dir.is_dir():
                files = list(company_dir.glob("*.html"))
                valid_count = 0
                junk_count = 0
                
                # Sample check - look at first 5 files
                for i, file_path in enumerate(files[:5]):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Check for junk indicators
                        is_junk = any([
                            'companysearch' in file_path.name.lower(),
                            len(content) < 5000,
                            'search results' in content.lower(),
                            'no matches found' in content.lower(),
                            'CENTRAL INDEX KEY' not in content.upper()
                        ])
                        
                        if is_junk:
                            junk_count += 1
                        else:
                            valid_count += 1
                            
                    except Exception as e:
                        junk_count += 1
                
                # Extrapolate based on sample
                estimated_junk = int((junk_count / min(5, len(files))) * len(files))
                estimated_valid = len(files) - estimated_junk
                
                if estimated_junk > len(files) * 0.3:  # More than 30% junk
                    problem_companies.append(company_dir.name)
                
                self.report['findings']['documents'][company_dir.name] = {
                    'total_files': len(files),
                    'estimated_valid': estimated_valid,
                    'estimated_junk': estimated_junk,
                    'sample_junk_rate': f"{(junk_count/min(5, len(files))*100):.0f}%"
                }
                
                total_files += len(files)
                total_valid += estimated_valid
                
                print(f"\n{company_dir.name}:")
                print(f"  Total files: {len(files)}")
                print(f"  Estimated valid: {estimated_valid}")
                print(f"  Estimated junk: {estimated_junk}")
        
        print(f"\n📊 SUMMARY:")
        print(f"  Total files across all companies: {total_files}")
        print(f"  Estimated valid documents: {total_valid}")
        print(f"  Problem companies (>30% junk): {problem_companies}")
        
        self.report['findings']['documents']['summary'] = {
            'total_files': total_files,
            'total_valid': total_valid,
            'problem_companies': problem_companies
        }
    
    def audit_admin_panel(self):
        """Check admin panel setup"""
        print("\n" + "="*70)
        print("👨‍💼 ADMIN PANEL AUDIT")
        print("="*70)
        
        admin_files = {
            'main': Path('admin/admin_final_browser.py'),
            'scraper': Path('scrapers/sec/sec_compliant_scraper.py'),
            'requests': Path('data/company_requests.json'),
            'ipo_cache': Path('data/cache/ipo_calendar.json')
        }
        
        for name, path in admin_files.items():
            if path.exists():
                size = path.stat().st_size
                print(f"✓ {name}: {path} ({size:,} bytes)")
                self.report['findings']['admin_panel'][name] = {
                    'exists': True,
                    'path': str(path),
                    'size': size
                }
            else:
                print(f"✗ {name}: {path} NOT FOUND")
                self.report['findings']['admin_panel'][name] = {
                    'exists': False,
                    'path': str(path)
                }
        
        # Check for company requests
        if admin_files['requests'].exists():
            with open(admin_files['requests'], 'r') as f:
                requests = json.load(f)
            print(f"\n📝 Pending requests: {len(requests)}")
            for req in requests[:3]:  # Show first 3
                print(f"  - {req.get('company', 'Unknown')} ({req.get('status', 'pending')})")
    
    def audit_scrapers(self):
        """Check scraper configurations"""
        print("\n" + "="*70)
        print("🕷️ SCRAPER AUDIT")
        print("="*70)
        
        scrapers = [
            Path('scrapers/sec/sec_compliant_scraper.py'),
            Path('scrapers/iposcoop_scraper.py'),
            Path('admin/edgar_scraper.py'),
            Path('admin/sec_api_client.py')
        ]
        
        for scraper in scrapers:
            if scraper.exists():
                print(f"✓ {scraper}")
                
                # Check for key functions
                with open(scraper, 'r') as f:
                    content = f.read()
                
                has_progress = 'progress' in content.lower()
                has_rate_limit = 'rate' in content.lower() or 'sleep' in content.lower()
                
                print(f"  - Progress tracking: {'Yes' if has_progress else 'No'}")
                print(f"  - Rate limiting: {'Yes' if has_rate_limit else 'No'}")
            else:
                print(f"✗ {scraper} NOT FOUND")
    
    def audit_user_features(self):
        """Check if user-facing features have required components"""
        print("\n" + "="*70)
        print("🎯 USER FEATURE AUDIT")
        print("="*70)
        
        features = {
            'Document Explorer': [
                'components/document_explorer.py',
                'services/document_service.py'
            ],
            'AI Chat': [
                'components/chat.py',
                'components/persistent_chat.py',
                'services/ai_service.py'
            ],
            'Data Extraction': [
                'components/data_extractor.py',
                'core/document_processor.py'
            ],
            'IPO Tracker': [
                'components/ipo_tracker_enhanced.py',
                'scrapers/iposcoop_scraper.py'
            ],
            'Watchlist': [
                'components/watchlist.py',
                'services/watchlist_service.py'
            ]
        }
        
        for feature, required_files in features.items():
            print(f"\n{feature}:")
            all_exist = True
            
            for file_path in required_files:
                path = Path(file_path)
                if path.exists():
                    print(f"  ✓ {file_path}")
                else:
                    print(f"  ✗ {file_path} MISSING")
                    all_exist = False
            
            self.report['findings']['user_features'][feature] = {
                'ready': all_exist,
                'files': required_files
            }
    
    def audit_data_flow(self):
        """Trace the data flow from admin to user"""
        print("\n" + "="*70)
        print("🔄 DATA FLOW AUDIT")
        print("="*70)
        
        print("\n1. Company Request Flow:")
        print("   User → company_requests.json → Admin Panel → SEC Scraper → sec_documents/")
        
        # Check each step
        steps = {
            'Request file': Path('data/company_requests.json').exists(),
            'Admin panel': Path('admin/admin_final_browser.py').exists(),
            'SEC scraper': Path('scrapers/sec/sec_compliant_scraper.py').exists(),
            'Document storage': Path('data/sec_documents').exists()
        }
        
        for step, exists in steps.items():
            print(f"   {'✓' if exists else '✗'} {step}")
        
        print("\n2. IPO Data Flow:")
        print("   IPOScoop → iposcoop_scraper.py → ipo_calendar.json → IPO Tracker")
        
        ipo_steps = {
            'IPO scraper': Path('scrapers/iposcoop_scraper.py').exists(),
            'IPO cache': Path('data/cache/ipo_calendar.json').exists(),
            'IPO tracker': Path('components/ipo_tracker_enhanced.py').exists()
        }
        
        for step, exists in ipo_steps.items():
            print(f"   {'✓' if exists else '✗'} {step}")
    
    def save_report(self):
        """Save complete audit report"""
        report_path = Path('system_audit_report.json')
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
        
        print(f"\n📄 Full report saved: {report_path}")
        
        # Summary
        print("\n" + "="*70)
        print("🎯 CRITICAL ISSUES TO FIX:")
        print("="*70)
        
        # Document issues
        problem_companies = self.report['findings']['documents']['summary']['problem_companies']
        if problem_companies:
            print(f"\n1. Document Quality:")
            print(f"   - {len(problem_companies)} companies have >30% junk files")
            print(f"   - Affected: {', '.join(problem_companies)}")
        
        # Missing components
        print(f"\n2. Missing Components:")
        for feature, data in self.report['findings']['user_features'].items():
            if not data['ready']:
                print(f"   - {feature} is incomplete")
        
        # Admin integration
        if not self.report['findings']['admin_panel'].get('scraper', {}).get('exists'):
            print(f"\n3. Admin Integration:")
            print(f"   - SEC scraper not found at expected location")

def main():
    print("🔍 HEDGE INTELLIGENCE - COMPLETE SYSTEM AUDIT")
    print("="*70)
    
    auditor = CompleteSystemAudit()
    
    # Run all audits
    auditor.audit_documents()
    auditor.audit_admin_panel()
    auditor.audit_scrapers()
    auditor.audit_user_features()
    auditor.audit_data_flow()
    
    # Save report
    auditor.save_report()
    
    print("\n✅ AUDIT COMPLETE! Check system_audit_report.json for details.")
    
    # Ask what to do next
    print("\n📋 RECOMMENDED NEXT STEPS:")
    print("1. Clean junk documents (high priority)")
    print("2. Fix missing components")
    print("3. Test admin → user data flow")
    print("4. Update theme to Apple style")
    
    response = input("\nProceed with document cleanup? (y/n): ")
    if response.lower() == 'y':
        print("\nRun: python document_cleanup.py")

if __name__ == "__main__":
    main()