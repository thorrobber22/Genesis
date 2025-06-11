#!/usr/bin/env python3
"""
Simple Project Audit - No Unicode Issues
Date: 2025-06-07 12:17:20 UTC
Author: thorrobber22
"""

import os
import json
from pathlib import Path
from datetime import datetime

def audit_project():
    """Simple project audit without unicode"""
    print("HEDGE INTELLIGENCE PROJECT AUDIT")
    print("="*60)
    
    audit_data = {
        'timestamp': datetime.now().isoformat(),
        'project_root': os.getcwd(),
        'files': {},
        'statistics': {
            'total_files': 0,
            'python_files': [],
            'key_directories': {}
        },
        'sec_documents': {}
    }
    
    # Key files to check
    key_files = [
        'admin_final_browser.py',
        'hedge_intelligence_ui.py',
        'requirements.txt',
        'data/pipeline_data.json'
    ]
    
    # Walk through project
    for root, dirs, files in os.walk('.'):
        # Skip venv and cache
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git']]
        
        for file in files:
            filepath = Path(root) / file
            rel_path = os.path.relpath(filepath, '.').replace('\\', '/')
            
            # Skip certain files
            if filepath.suffix.lower() in ['.jpg', '.png', '.pdf', '.pyc']:
                continue
                
            try:
                stat = filepath.stat()
                audit_data['files'][rel_path] = {
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
                
                audit_data['statistics']['total_files'] += 1
                
                # Track Python files
                if filepath.suffix == '.py':
                    audit_data['statistics']['python_files'].append(rel_path)
                    
            except Exception as e:
                audit_data['files'][rel_path] = {'error': str(e)}
    
    # Check key directories
    dirs_to_check = [
        'scrapers/sec',
        'data/sec_documents',
        'processors',
        'data'
    ]
    
    for dir_path in dirs_to_check:
        p = Path(dir_path)
        if p.exists():
            files = list(p.rglob('*.*'))
            audit_data['statistics']['key_directories'][dir_path] = {
                'exists': True,
                'file_count': len(files)
            }
        else:
            audit_data['statistics']['key_directories'][dir_path] = {
                'exists': False
            }
    
    # Analyze SEC documents
    sec_dir = Path('data/sec_documents')
    if sec_dir.exists():
        for company_dir in sec_dir.iterdir():
            if company_dir.is_dir():
                files = list(company_dir.glob('*.*'))
                total_size = sum(f.stat().st_size for f in files if f.exists())
                
                file_types = {}
                for f in files:
                    ext = f.suffix.lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
                
                audit_data['sec_documents'][company_dir.name] = {
                    'total_files': len(files),
                    'total_size_mb': total_size / 1024 / 1024,
                    'file_types': file_types
                }
    
    # Load pipeline data
    pipeline_file = Path('data/pipeline_data.json')
    if pipeline_file.exists():
        try:
            with open(pipeline_file, 'r', encoding='utf-8') as f:
                pipeline_data = json.load(f)
                audit_data['pipeline_status'] = {
                    'pending': len(pipeline_data.get('pending', [])),
                    'active': len(pipeline_data.get('active', [])),
                    'completed': len(pipeline_data.get('completed', []))
                }
        except:
            audit_data['pipeline_status'] = 'error_reading'
    
    # Print summary
    print(f"\nPROJECT SUMMARY:")
    print(f"Total Files: {audit_data['statistics']['total_files']}")
    print(f"Python Files: {len(audit_data['statistics']['python_files'])}")
    print(f"\nSEC DOCUMENTS:")
    print(f"Companies: {len(audit_data['sec_documents'])}")
    
    total_docs = 0
    for company, info in audit_data['sec_documents'].items():
        print(f"  {company}: {info['total_files']} files ({info['total_size_mb']:.1f} MB)")
        total_docs += info['total_files']
    
    print(f"Total Documents: {total_docs}")
    
    # Save audit
    with open('project_audit.json', 'w', encoding='utf-8') as f:
        json.dump(audit_data, f, indent=2)
    
    print(f"\nAudit saved to: project_audit.json")
    
    # Create simple text summary
    summary = []
    summary.append("HEDGE INTELLIGENCE PROJECT STRUCTURE")
    summary.append("="*60)
    summary.append(f"Generated: {datetime.now()}")
    summary.append("")
    summary.append("KEY PYTHON FILES:")
    
    important_files = [
        'admin_final_browser.py',
        'hedge_intelligence_ui.py',
        'scrapers/sec/sec_compliant_scraper.py',
        'scrapers/sec/pipeline_manager.py',
        'processors/document_processor.py'
    ]
    
    for file in important_files:
        if file in audit_data['files']:
            info = audit_data['files'][file]
            if 'size' in info:
                summary.append(f"  [OK] {file} ({info['size']/1024:.1f} KB)")
            else:
                summary.append(f"  [ERROR] {file}")
        else:
            summary.append(f"  [MISSING] {file}")
    
    summary.append("")
    summary.append("DIRECTORIES:")
    for dir_path, info in audit_data['statistics']['key_directories'].items():
        if info['exists']:
            summary.append(f"  [OK] {dir_path} ({info['file_count']} files)")
        else:
            summary.append(f"  [MISSING] {dir_path}")
    
    with open('project_summary.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary))
    
    print("Summary saved to: project_summary.txt")
    
    return audit_data

if __name__ == "__main__":
    audit_project()