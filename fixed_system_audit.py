#!/usr/bin/env python3
"""
Hedge Intelligence - Fixed System Audit
Date: 2025-06-09 01:59:44 UTC
Purpose: Fixed audit to handle empty folders and investigate document quality
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
import subprocess

class FixedSystemAudit:
    def __init__(self):
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'user': 'thorrobber22',
            'findings': {
                'documents': {},
                'admin_panel': {},
                'scrapers': {},
                'user_features': {},
                'data_flow': {},
                'sample_content': {}
            }
        }
    
    def audit_documents(self):
        """Audit all SEC documents with better error handling"""
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
                
                if not files:  # Handle empty directories
                    print(f"\n{company_dir.name}: ⚠️  EMPTY DIRECTORY")
                    self.report['findings']['documents'][company_dir.name] = {
                        'total_files': 0,
                        'status': 'EMPTY'
                    }
                    continue
                
                valid_count = 0
                junk_count = 0
                sample_content = []
                
                # Check ALL files for better accuracy
                for i, file_path in enumerate(files):
                    try:
                        file_size = file_path.stat().st_size
                        
                        # Quick size check first
                        if file_size < 1000:
                            junk_count += 1
                            if i < 2:  # Save sample
                                sample_content.append({
                                    'file': file_path.name,
                                    'size': file_size,
                                    'issue': 'Too small'
                                })
                            continue
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # More detailed checks
                        has_sec_markers = any([
                            'SECURITIES AND EXCHANGE COMMISSION' in content.upper(),
                            'CENTRAL INDEX KEY:' in content.upper(),
                            'CONFORMED SUBMISSION TYPE:' in content.upper(),
                            'FILED AS OF DATE:' in content.upper()
                        ])
                        
                        is_search_page = any([
                            'companysearch' in file_path.name.lower(),
                            '<title>EDGAR Search Results</title>' in content,
                            'No matching Ticker Symbol' in content,
                            'No matches found for' in content
                        ])
                        
                        # Save sample of first few files
                        if i < 2:
                            preview = content[:500].replace('\n', ' ')
                            sample_content.append({
                                'file': file_path.name,
                                'size': file_size,
                                'has_sec_markers': has_sec_markers,
                                'is_search_page': is_search_page,
                                'preview': preview[:200] + '...'
                            })
                        
                        if is_search_page or not has_sec_markers:
                            junk_count += 1
                        else:
                            valid_count += 1
                            
                    except Exception as e:
                        junk_count += 1
                        if i < 2:
                            sample_content.append({
                                'file': file_path.name,
                                'error': str(e)
                            })
                
                # Calculate percentages
                junk_percentage = (junk_count / len(files)) * 100 if files else 0
                
                if junk_percentage > 30:
                    problem_companies.append(company_dir.name)
                
                self.report['findings']['documents'][company_dir.name] = {
                    'total_files': len(files),
                    'valid_files': valid_count,
                    'junk_files': junk_count,
                    'junk_percentage': f"{junk_percentage:.0f}%",
                    'samples': sample_content[:2]  # First 2 samples
                }
                
                total_files += len(files)
                total_valid += valid_count
                
                print(f"\n{company_dir.name}:")
                print(f"  Total files: {len(files)}")
                print(f"  Valid SEC documents: {valid_count}")
                print(f"  Junk/Search pages: {junk_count} ({junk_percentage:.0f}%)")
                
                # Show sample
                if sample_content and junk_count > 0:
                    print(f"  Sample issue: {sample_content[0].get('issue', 'Check preview')}")
        
        print(f"\n📊 SUMMARY:")
        print(f"  Total files across all companies: {total_files}")
        print(f"  Valid SEC documents: {total_valid}")
        print(f"  Problem companies (>30% junk): {', '.join(problem_companies) if problem_companies else 'None'}")
        
        self.report['findings']['documents']['summary'] = {
            'total_files': total_files,
            'total_valid': total_valid,
            'problem_companies': problem_companies
        }
        
        # If all documents are junk, investigate deeper
        if total_valid == 0:
            print("\n⚠️  WARNING: No valid documents found! Investigating...")
            self.investigate_document_issue()
    
    def investigate_document_issue(self):
        """Deeper investigation when all docs appear to be junk"""
        print("\n🔍 DEEP INVESTIGATION:")
        
        # Check a specific file we know should exist
        test_files = [
            Path("data/sec_documents/CRCL/companysearch.html"),
            Path("data/sec_documents/CRCL/000175454624001010.html"),
            Path("data/sec_documents/FMFC/000181849324000324.html")
        ]
        
        for test_file in test_files:
            if test_file.exists():
                print(f"\n📄 Examining: {test_file}")
                
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                print(f"  Size: {len(content):,} bytes")
                print(f"  First 300 chars: {content[:300]}")
                
                # Check what kind of content it is
                if '<html' in content.lower():
                    print("  Type: HTML document")
                    
                    # Look for title
                    import re
                    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                    if title_match:
                        print(f"  Title: {title_match.group(1)}")
                    
                    # Check for SEC content
                    if 'companysearch' in test_file.name:
                        print("  ⚠️  This is a search results page, not a filing!")
                    elif 'SECURITIES AND EXCHANGE COMMISSION' in content.upper():
                        print("  ✅ Contains SEC header - likely valid!")
                    else:
                        print("  ❌ Missing SEC markers - might be download error")
                
                self.report['findings']['sample_content'][str(test_file)] = {
                    'size': len(content),
                    'preview': content[:500]
                }
                
                break
    
    def audit_admin_panel(self):
        """Check admin panel setup"""
        print("\n" + "="*70)
        print("👨‍💼 ADMIN PANEL AUDIT")
        print("="*70)
        
        # Check both possible admin panel files
        admin_files = {
            'main_browser': Path('admin/admin_final_browser.py'),
            'main_panel': Path('admin/admin_panel.py'),
            'scraper_sec': Path('scrapers/sec/sec_compliant_scraper.py'),
            'scraper_edgar': Path('admin/edgar_scraper.py'),
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
            print(f"\n📝 Company requests: {len(requests)}")
            for req in requests[:3]:  # Show first 3
                print(f"  - {req.get('company', 'Unknown')} ({req.get('status', 'pending')})")
    
    def audit_scrapers(self):
        """Check all scraper locations"""
        print("\n" + "="*70)
        print("🕷️ SCRAPER AUDIT")
        print("="*70)
        
        # Check all possible scraper locations
        scrapers = [
            Path('scrapers/sec/sec_compliant_scraper.py'),
            Path('scrapers/sec_compliant_scraper.py'),
            Path('scrapers/iposcoop_scraper.py'),
            Path('scrapers/edgar_scraper.py'),
            Path('admin/edgar_scraper.py'),
            Path('admin/sec_api_client.py'),
            Path('admin/sec_compliant_scraper.py')
        ]
        
        found_scrapers = []
        
        for scraper in scrapers:
            if scraper.exists():
                print(f"✓ Found: {scraper}")
                found_scrapers.append(str(scraper))
                
                # Check for key functions
                try:
                    with open(scraper, 'r') as f:
                        content = f.read()
                    
                    # Look for important functions
                    has_download = 'download' in content.lower()
                    has_progress = 'progress' in content.lower()
                    has_rate_limit = any(word in content.lower() for word in ['rate', 'sleep', 'delay'])
                    
                    if has_download:
                        print(f"  ✓ Has download functionality")
                    if has_progress:
                        print(f"  ✓ Has progress tracking")
                    if has_rate_limit:
                        print(f"  ✓ Has rate limiting")
                        
                except Exception as e:
                    print(f"  ⚠️  Error reading: {e}")
        
        if not found_scrapers:
            print("❌ NO SCRAPERS FOUND!")
        
        self.report['findings']['scrapers']['found'] = found_scrapers
    
    def save_report(self):
        """Save complete audit report"""
        report_path = Path('system_audit_report_fixed.json')
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
        
        print(f"\n📄 Full report saved: {report_path}")
        
        # Critical issues summary
        print("\n" + "="*70)
        print("🚨 CRITICAL ISSUES:")
        print("="*70)
        
        # Check if we have ANY valid documents
        total_valid = self.report['findings']['documents']['summary']['total_valid']
        if total_valid == 0:
            print("\n1. ❌ NO VALID DOCUMENTS FOUND")
            print("   All files appear to be search results or corrupted")
            print("   Need to re-download from SEC using admin panel")
        
        # Check scraper location
        found_scrapers = self.report['findings']['scrapers'].get('found', [])
        if not any('sec_compliant_scraper' in s for s in found_scrapers):
            print("\n2. ❌ SEC SCRAPER NOT IN EXPECTED LOCATION")
            print("   Admin panel expects: scrapers/sec/sec_compliant_scraper.py")
            print("   Found scrapers at:", found_scrapers)
        
        print("\n" + "="*70)
        print("📋 RECOMMENDED ACTIONS:")
        print("="*70)
        print("1. DELETE all current documents (they're all junk)")
        print("2. FIX scraper location issue")
        print("3. RE-DOWNLOAD companies through admin panel")
        print("4. THEN test user features")

def main():
    print("🔍 HEDGE INTELLIGENCE - FIXED SYSTEM AUDIT")
    print("="*70)
    
    auditor = FixedSystemAudit()
    
    # Run all audits
    auditor.audit_documents()
    auditor.audit_admin_panel()
    auditor.audit_scrapers()
    
    # Save report
    auditor.save_report()

if __name__ == "__main__":
    main()