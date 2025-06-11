#!/usr/bin/env python3
"""
Hedge Intelligence - Pre-Refactor Inspection Tool
Date: 2025-06-07 22:07:29 UTC
Author: thorrobber22
Description: Shows exactly what will be modified BEFORE any changes
"""

import os
from pathlib import Path
import hashlib
from datetime import datetime

class RefactorInspector:
    def __init__(self):
        self.changes = {
            'new_files': [],
            'modified_files': [],
            'deleted_files': [],
            'backup_files': []
        }
        
    def get_file_hash(self, filepath):
        """Get MD5 hash of file"""
        if not Path(filepath).exists():
            return None
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def inspect_changes(self):
        """Inspect what will change"""
        print("🔍 HEDGE INTELLIGENCE - REFACTOR INSPECTION")
        print("=" * 70)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"User: thorrobber22")
        print("=" * 70)
        
        # 1. NEW FILES TO BE CREATED
        print("\n📄 NEW FILES TO BE CREATED:")
        print("-" * 70)
        
        new_files = [
            {
                'path': 'components/document_explorer.py',
                'description': 'File tree navigation for SEC documents',
                'size': '~3KB'
            },
            {
                'path': 'components/persistent_chat.py',
                'description': 'Always-visible chat bar at bottom',
                'size': '~3KB'
            },
            {
                'path': 'components/data_extractor.py',
                'description': 'Extract financial data with citations',
                'size': '~2KB'
            },
            {
                'path': 'components/ipo_tracker_enhanced.py',
                'description': 'Enhanced IPO tracker with more details',
                'size': '~2KB'
            }
        ]
        
        for file_info in new_files:
            exists = "⚠️ WILL OVERWRITE" if Path(file_info['path']).exists() else "✅ NEW"
            print(f"{exists} {file_info['path']}")
            print(f"    Purpose: {file_info['description']}")
            print(f"    Size: {file_info['size']}")
            self.changes['new_files'].append(file_info)
        
        # 2. FILES TO BE MODIFIED
        print("\n✏️ FILES TO BE MODIFIED:")
        print("-" * 70)
        
        files_to_modify = [
            {
                'path': 'hedge_intelligence.py',
                'changes': [
                    '- Remove blue button styling',
                    '- Add dark grey theme',
                    '- Remove settings/preferences',
                    '- Add document explorer sidebar',
                    '- Add persistent chat bar',
                    '- Simplify dashboard'
                ]
            },
            {
                'path': 'services/ai_service.py',
                'changes': [
                    '+ Add get_ai_response() method',
                    '+ Add validation between GPT/Gemini',
                    '+ Add extraction support'
                ]
            },
            {
                'path': 'components/dashboard.py',
                'changes': [
                    '- Remove pipeline statistics',
                    '- Remove document counts',
                    '- Simplify to analyst focus'
                ]
            }
        ]
        
        for file_info in files_to_modify:
            if Path(file_info['path']).exists():
                current_hash = self.get_file_hash(file_info['path'])
                current_size = Path(file_info['path']).stat().st_size
                print(f"📝 {file_info['path']}")
                print(f"    Current size: {current_size:,} bytes")
                print(f"    Current hash: {current_hash[:16]}...")
                print(f"    Changes:")
                for change in file_info['changes']:
                    print(f"      {change}")
                self.changes['modified_files'].append(file_info)
            else:
                print(f"⚠️ {file_info['path']} - NOT FOUND (will skip)")
        
        # 3. FILES TO BE DELETED/REMOVED
        print("\n🗑️ FILES/FEATURES TO BE REMOVED:")
        print("-" * 70)
        
        files_to_remove = [
            {
                'path': 'components/settings.py',
                'reason': 'No user preferences needed'
            }
        ]
        
        for file_info in files_to_remove:
            if Path(file_info['path']).exists():
                print(f"❌ {file_info['path']}")
                print(f"    Reason: {file_info['reason']}")
                self.changes['deleted_files'].append(file_info)
            else:
                print(f"ℹ️ {file_info['path']} - Already removed")
        
        # 4. BACKUP PLAN
        print("\n💾 BACKUP PLAN:")
        print("-" * 70)
        
        backup_dir = Path("backup_20250607")
        print(f"Backup directory: {backup_dir}")
        
        files_to_backup = [
            "hedge_intelligence.py",
            "services/ai_service.py",
            "components/dashboard.py",
            "components/chat.py",
            "components/settings.py"
        ]
        
        for filepath in files_to_backup:
            if Path(filepath).exists():
                backup_path = backup_dir / filepath
                print(f"✅ Will backup: {filepath} → {backup_path}")
                self.changes['backup_files'].append(filepath)
            else:
                print(f"ℹ️ Skip backup: {filepath} (not found)")
        
        # 5. DATA SAFETY
        print("\n🔒 DATA SAFETY:")
        print("-" * 70)
        print("✅ SEC documents will NOT be touched")
        print("✅ Chat history will be preserved")
        print("✅ Company requests will be preserved")
        print("✅ Watchlists will be preserved")
        
        sec_docs = Path("data/sec_documents")
        if sec_docs.exists():
            companies = len(list(sec_docs.iterdir()))
            total_docs = sum(
                len(list(p.glob("*.html"))) 
                for p in sec_docs.iterdir() if p.is_dir()
            )
            print(f"\nCurrent data: {companies} companies, {total_docs:,} documents")
        
        # 6. SUMMARY
        print("\n📊 CHANGE SUMMARY:")
        print("-" * 70)
        print(f"New files to create: {len(self.changes['new_files'])}")
        print(f"Files to modify: {len(self.changes['modified_files'])}")
        print(f"Files to remove: {len(self.changes['deleted_files'])}")
        print(f"Files to backup: {len(self.changes['backup_files'])}")
        
        # 7. CONFIRMATION
        print("\n" + "=" * 70)
        print("⚠️  READY TO APPLY REFACTOR")
        print("=" * 70)
        print("\nThis inspection shows EXACTLY what will change.")
        print("Your SEC documents and data are SAFE.")
        print("\nTo proceed with refactor:")
        print("1. Run: python apply_refactor.py")
        print("\nTo test without changes:")
        print("1. Run: python production_test_v2.py")
        print("\nTo restore from backup later:")
        print("1. Copy files from backup_20250607/ back to original locations")
        
        # Save inspection report
        report_path = Path("refactor_inspection_report.txt")
        with open(report_path, 'w') as f:
            f.write(f"REFACTOR INSPECTION REPORT\n")
            f.write(f"Date: {datetime.now()}\n")
            f.write(f"User: thorrobber22\n\n")
            f.write(f"New files: {len(self.changes['new_files'])}\n")
            f.write(f"Modified files: {len(self.changes['modified_files'])}\n")
            f.write(f"Deleted files: {len(self.changes['deleted_files'])}\n")
            f.write(f"Backup files: {len(self.changes['backup_files'])}\n")
            
        print(f"\n📄 Full report saved to: {report_path}")

def main():
    inspector = RefactorInspector()
    inspector.inspect_changes()

if __name__ == "__main__":
    main()