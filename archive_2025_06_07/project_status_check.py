#!/usr/bin/env python3
"""
Check current project status and what needs to be added
Date: 2025-06-06 17:08:24 UTC
Author: thorrobber22
"""

from pathlib import Path
import json
import ast

def check_file_structure():
    """Check which files exist and their basic structure"""
    print("=" * 60)
    print("HEDGE INTELLIGENCE - PROJECT STATUS CHECK")
    print("=" * 60)
    
    # Expected vs Actual structure
    expected_files = {
        # Core Admin Files
        'admin.py': {'status': '?', 'has_multi_upload': False, 'has_doc_viewer': False},
        'admin_streamlined.py': {'status': '?', 'type': 'admin'},
        'admin_fixed.py': {'status': '?', 'type': 'admin'},
        'admin_real_data.py': {'status': '?', 'type': 'admin'},
        
        # Core Processing
        'process_and_index.py': {'status': '?', 'has_doc_detection': False},
        'core/document_processor.py': {'status': '?', 'type': 'new_needed'},
        'core/vector_store.py': {'status': '?', 'type': 'new_needed'},
        'core/chat_engine.py': {'status': '?', 'has_multi_doc': False},
        'core/report_generator.py': {'status': '?', 'type': 'new_needed'},
        
        # Scrapers
        'scrapers/ipo_scraper.py': {'status': '?', 'is_async': False},
        'scrapers/ipo_scraper_fixed.py': {'status': '?', 'type': 'scraper'},
        
        # Background Services
        'background/scheduler.py': {'status': '?', 'has_categorization': False},
        'background/update_service.py': {'status': '?', 'type': 'new_needed'},
        
        # Main App
        'app.py': {'status': '?', 'has_doc_viewer': False},
        'streamlit_app.py': {'status': '?', 'type': 'app'},
        
        # UI Components
        'ui/components/data_cards.py': {'status': '?', 'has_doc_counts': False},
        'ui/components/chat_interface.py': {'status': '?', 'has_sources': False},
    }
    
    # Check each file
    for filepath, info in expected_files.items():
        path = Path(filepath)
        if path.exists():
            info['status'] = '✅ EXISTS'
            
            # Check file contents for specific features
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for specific implementations
                if 'admin' in filepath:
                    if 'accept_multiple_files=True' in content:
                        info['has_multi_upload'] = True
                    if 'download' in content.lower() or 'viewer' in content.lower():
                        info['has_doc_viewer'] = True
                        
                elif filepath == 'process_and_index.py':
                    if 'detect_document_type' in content or 'document_type' in content:
                        info['has_doc_detection'] = True
                        
                elif 'chat_engine' in filepath:
                    if 'document_type' in content or 'multi_doc' in content:
                        info['has_multi_doc'] = True
                        
                elif 'scheduler' in filepath:
                    if 'UPCOMING' in content and 'TODAY' in content:
                        info['has_categorization'] = True
                        
                elif 'ipo_scraper.py' in filepath:
                    if 'async def' in content:
                        info['is_async'] = True
                        
                elif 'data_cards' in filepath:
                    if 'document' in content.lower():
                        info['has_doc_counts'] = True
                        
                elif 'chat_interface' in filepath:
                    if 'source' in content.lower():
                        info['has_sources'] = True
                        
            except Exception as e:
                info['error'] = str(e)
        else:
            info['status'] = '❌ MISSING'
    
    return expected_files

def check_data_structure():
    """Check data directory structure"""
    print("\n📁 DATA STRUCTURE:")
    print("-" * 40)
    
    data_dirs = {
        'data/': '?',
        'data/documents/': '?',
        'data/processed/': '?',
        'data/ipo_pipeline/': '?',
        'data/sec_documents/': '?',
        'vector_store/': '?',
    }
    
    for dir_path in data_dirs:
        path = Path(dir_path)
        if path.exists():
            file_count = len(list(path.glob('**/*'))) if path.is_dir() else 0
            data_dirs[dir_path] = f'✅ ({file_count} files)'
        else:
            data_dirs[dir_path] = '❌ Missing'
    
    return data_dirs

def analyze_current_state():
    """Analyze what we have vs what we need"""
    files = check_file_structure()
    data = check_data_structure()
    
    # Print file status
    print("\n📄 FILE STATUS:")
    print("-" * 40)
    
    for filepath, info in files.items():
        print(f"{filepath:35} {info['status']}")
        
        # Print sub-features
        for key, value in info.items():
            if key not in ['status', 'type', 'error'] and value:
                print(f"  └─ {key}: {'✅' if value else '❌'}")
    
    # Print data structure
    print("\n📁 DATA STRUCTURE:")
    print("-" * 40)
    
    for dir_path, status in data.items():
        print(f"{dir_path:35} {status}")
    
    # Determine current phase
    print("\n📊 PHASE ANALYSIS:")
    print("-" * 40)
    
    # Check Phase 3 progress
    phase3_complete = {
        '3.1 Admin Panel': False,
        '3.2 Document Processing': False,
        '3.3 Vector Search': False,
        '3.4 Chat Engine': False,
    }
    
    # Check specifics
    if any('admin' in f and files[f]['status'] == '✅ EXISTS' for f in files):
        if any(files[f].get('has_multi_upload') for f in files if 'admin' in f):
            phase3_complete['3.1 Admin Panel'] = True
    
    if files.get('core/document_processor.py', {}).get('status') == '✅ EXISTS':
        phase3_complete['3.2 Document Processing'] = True
    elif files.get('process_and_index.py', {}).get('has_doc_detection'):
        phase3_complete['3.2 Document Processing'] = 'Partial'
    
    if files.get('core/vector_store.py', {}).get('status') == '✅ EXISTS':
        phase3_complete['3.3 Vector Search'] = True
    
    if files.get('core/chat_engine.py', {}).get('has_multi_doc'):
        phase3_complete['3.4 Chat Engine'] = True
    
    for phase, status in phase3_complete.items():
        symbol = '✅' if status == True else '⚠️' if status == 'Partial' else '❌'
        print(f"{phase:30} {symbol} {status if isinstance(status, str) else ''}")
    
    # What needs to be done
    print("\n🎯 NEXT STEPS:")
    print("-" * 40)
    
    next_steps = []
    
    # Based on missing files
    if files.get('core/document_processor.py', {}).get('status') == '❌ MISSING':
        next_steps.append("Create core/document_processor.py for document type detection")
    
    if files.get('core/vector_store.py', {}).get('status') == '❌ MISSING':
        next_steps.append("Create core/vector_store.py for ChromaDB integration")
    
    if not files.get('core/chat_engine.py', {}).get('has_multi_doc'):
        next_steps.append("Update chat engine for multi-document search")
    
    if files.get('core/report_generator.py', {}).get('status') == '❌ MISSING':
        next_steps.append("Create report generator for PDF exports")
    
    # Based on features
    admin_has_features = any(files[f].get('has_multi_upload') and files[f].get('has_doc_viewer') 
                           for f in files if 'admin' in f)
    if not admin_has_features:
        next_steps.append("Add multi-file upload and document viewer to admin")
    
    for i, step in enumerate(next_steps, 1):
        print(f"{i}. {step}")
    
    # Summary
    print("\n📈 SUMMARY:")
    print("-" * 40)
    print(f"Phase 3.1 (Admin): {'✅ Complete' if phase3_complete['3.1 Admin Panel'] else '🔄 In Progress'}")
    print(f"Phase 3.2 (Processing): {'✅ Complete' if phase3_complete['3.2 Document Processing'] == True else '🔄 Needs Work'}")
    print(f"Phase 3.3 (Vector): {'✅ Complete' if phase3_complete['3.3 Vector Search'] else '❌ Not Started'}")
    print(f"Phase 3.4 (Chat): {'✅ Complete' if phase3_complete['3.4 Chat Engine'] else '🔄 Needs Update'}")
    
    return files, data, phase3_complete

if __name__ == "__main__":
    files, data, phase_status = analyze_current_state()
    
    # Create a quick glimpse script if needed
    print("\n💡 To inspect specific files, run:")
    print("python glimpse_file.py <filepath>")