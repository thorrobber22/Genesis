#!/usr/bin/env python3
"""
Project Audit Script - Captures complete project state
Date: 2025-06-07 12:04:14 UTC
Author: thorrobber22
"""

import os
import json
from pathlib import Path
from datetime import datetime
import hashlib

def get_file_info(filepath):
    """Get detailed file information"""
    try:
        stat = filepath.stat()
        with open(filepath, 'rb') as f:
            content = f.read()
            file_hash = hashlib.md5(content).hexdigest()
        
        return {
            'path': str(filepath),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'hash': file_hash,
            'lines': len(content.decode('utf-8', errors='ignore').splitlines()) if filepath.suffix in ['.py', '.txt', '.json'] else None
        }
    except Exception as e:
        return {
            'path': str(filepath),
            'error': str(e)
        }

def analyze_python_file(filepath):
    """Extract key information from Python files"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract classes
        classes = []
        for line in content.splitlines():
            if line.strip().startswith('class '):
                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                classes.append(class_name)
        
        # Extract main functions
        functions = []
        for line in content.splitlines():
            if line.strip().startswith('def ') and not line.strip().startswith('def _'):
                func_name = line.split('def ')[1].split('(')[0].strip()
                if func_name not in ['__init__', '__str__', '__repr__']:
                    functions.append(func_name)
        
        # Check for async
        is_async = 'async def' in content or 'asyncio' in content
        
        # Check imports
        imports = {
            'streamlit': 'streamlit' in content,
            'openai': 'openai' in content,
            'chromadb': 'chromadb' in content,
            'aiohttp': 'aiohttp' in content,
            'beautifulsoup': 'BeautifulSoup' in content or 'bs4' in content
        }
        
        return {
            'classes': classes,
            'functions': functions[:10],  # First 10 functions
            'is_async': is_async,
            'imports': imports,
            'docstring': content.split('"""')[1] if '"""' in content else None
        }
    except:
        return None

def audit_project():
    """Complete project audit"""
    print("🔍 HEDGE INTELLIGENCE PROJECT AUDIT")
    print("="*60)
    
    audit_data = {
        'timestamp': datetime.now().isoformat(),
        'project_root': os.getcwd(),
        'structure': {},
        'statistics': {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'python_files': []
        },
        'data_analysis': {
            'sec_documents': {},
            'pipeline_status': None
        },
        'key_files': {}
    }
    
    # Define key files to analyze
    key_files = [
        'admin_final_browser.py',
        'hedge_intelligence_ui.py',
        'scrapers/sec/sec_compliant_scraper.py',
        'scrapers/sec/pipeline_manager.py',
        'processors/document_processor.py',
        'data/pipeline_data.json'
    ]
    
    # Walk through project
    for root, dirs, files in os.walk('.'):
        # Skip venv and cache
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
        
        rel_root = os.path.relpath(root, '.')
        
        for file in files:
            filepath = Path(root) / file
            rel_path = os.path.relpath(filepath, '.')
            
            # Skip large binary files
            if filepath.suffix.lower() in ['.jpg', '.png', '.pdf', '.exe', '.dll']:
                continue
                
            # Get file info
            file_info = get_file_info(filepath)
            
            # Update statistics
            audit_data['statistics']['total_files'] += 1
            if 'size' in file_info:
                audit_data['statistics']['total_size'] += file_info['size']
            
            # Count file types
            ext = filepath.suffix.lower()
            if ext:
                audit_data['statistics']['file_types'][ext] = audit_data['statistics']['file_types'].get(ext, 0) + 1
            
            # Analyze Python files
            if ext == '.py':
                py_analysis = analyze_python_file(filepath)
                if py_analysis:
                    file_info['analysis'] = py_analysis
                    audit_data['statistics']['python_files'].append({
                        'path': rel_path,
                        'classes': py_analysis['classes'],
                        'functions': py_analysis['functions'][:5]  # First 5 functions
                    })
            
            # Store in structure
            parts = rel_path.split(os.sep)
            current = audit_data['structure']
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = file_info
            
            # Analyze key files
            if rel_path.replace('\\', '/') in key_files:
                audit_data['key_files'][rel_path] = file_info
    
    # Analyze SEC documents
    sec_dir = Path('data/sec_documents')
    if sec_dir.exists():
        for company_dir in sec_dir.iterdir():
            if company_dir.is_dir():
                files = list(company_dir.glob('*.*'))
                doc_types = {}
                for f in files:
                    ext = f.suffix.lower()
                    doc_types[ext] = doc_types.get(ext, 0) + 1
                
                audit_data['data_analysis']['sec_documents'][company_dir.name] = {
                    'total_files': len(files),
                    'total_size_mb': sum(f.stat().st_size for f in files) / 1024 / 1024,
                    'file_types': doc_types
                }
    
    # Load pipeline data
    pipeline_file = Path('data/pipeline_data.json')
    if pipeline_file.exists():
        with open(pipeline_file, 'r') as f:
            pipeline_data = json.load(f)
            audit_data['data_analysis']['pipeline_status'] = {
                'pending': len(pipeline_data.get('pending', [])),
                'active': len(pipeline_data.get('active', [])),
                'completed': len(pipeline_data.get('completed', [])),
                'companies': [ipo['ticker'] for ipo in pipeline_data.get('active', [])]
            }
    
    # Print summary
    print(f"\n📊 PROJECT SUMMARY")
    print(f"Total Files: {audit_data['statistics']['total_files']}")
    print(f"Total Size: {audit_data['statistics']['total_size'] / 1024 / 1024:.1f} MB")
    print(f"Python Files: {len(audit_data['statistics']['python_files'])}")
    
    print(f"\n📁 SEC DOCUMENTS")
    total_docs = sum(info['total_files'] for info in audit_data['data_analysis']['sec_documents'].values())
    total_size = sum(info['total_size_mb'] for info in audit_data['data_analysis']['sec_documents'].values())
    print(f"Companies: {len(audit_data['data_analysis']['sec_documents'])}")
    print(f"Total Documents: {total_docs}")
    print(f"Total Size: {total_size:.1f} MB")
    
    # Save audit
    output_file = 'project_audit.json'
    with open(output_file, 'w') as f:
        json.dump(audit_data, f, indent=2)
    
    print(f"\n✅ Audit saved to: {output_file}")
    
    # Create a readable summary
    summary = []
    summary.append("HEDGE INTELLIGENCE PROJECT AUDIT SUMMARY")
    summary.append("="*60)
    summary.append(f"Generated: {datetime.now().isoformat()}")
    summary.append(f"Project Root: {os.getcwd()}")
    summary.append("")
    
    summary.append("KEY FILES STATUS:")
    for filepath, info in audit_data['key_files'].items():
        if 'error' not in info:
            summary.append(f"✅ {filepath} ({info['size']/1024:.1f} KB)")
            if 'analysis' in info and info['analysis']:
                if info['analysis']['classes']:
                    summary.append(f"   Classes: {', '.join(info['analysis']['classes'])}")
        else:
            summary.append(f"❌ {filepath} - {info['error']}")
    
    summary.append("")
    summary.append("PYTHON FILES:")
    for py_file in audit_data['statistics']['python_files'][:10]:
        summary.append(f"• {py_file['path']}")
        if py_file['classes']:
            summary.append(f"  Classes: {', '.join(py_file['classes'])}")
        if py_file['functions']:
            summary.append(f"  Functions: {', '.join(py_file['functions'])}")
    
    summary_text = '\n'.join(summary)
    
    with open('project_audit_summary.txt', 'w') as f:
        f.write(summary_text)
    
    print(f"✅ Summary saved to: project_audit_summary.txt")
    
    return audit_data

if __name__ == "__main__":
    audit_project()