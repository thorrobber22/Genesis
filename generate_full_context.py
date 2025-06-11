#!/usr/bin/env python3
"""
Hedge Intelligence - Full Context Generator
Date: 2025-06-09 00:29:36 UTC
Author: thorrobber22
Description: Generates complete context dump of entire codebase
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
import ast
import re

class ContextGenerator:
    def __init__(self):
        self.context = {
            'timestamp': datetime.now().isoformat(),
            'user': 'thorrobber22',
            'project': 'Hedge Intelligence',
            'description': 'SEC Document Analysis Platform with AI',
            'file_structure': {},
            'code_analysis': {},
            'data_summary': {},
            'dependencies': {},
            'configuration': {}
        }
        
    def generate_full_context(self):
        """Generate complete context dump"""
        print("🔍 HEDGE INTELLIGENCE - FULL CONTEXT GENERATOR")
        print("="*70)
        
        # 1. Map file structure
        self.map_file_structure()
        
        # 2. Analyze key files
        self.analyze_key_files()
        
        # 3. Summarize data
        self.summarize_data()
        
        # 4. Check dependencies
        self.check_dependencies()
        
        # 5. Extract configuration
        self.extract_configuration()
        
        # 6. Generate markdown report
        self.generate_markdown_report()
        
        # 7. Save context
        self.save_context()
        
    def map_file_structure(self):
        """Map complete file structure"""
        print("\n📁 Mapping file structure...")
        
        def get_tree(path, prefix="", max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return {}
                
            tree = {}
            path = Path(path)
            
            if path.is_file():
                size = path.stat().st_size
                tree = {
                    'type': 'file',
                    'size': size,
                    'extension': path.suffix
                }
            elif path.is_dir():
                children = {}
                try:
                    for item in sorted(path.iterdir()):
                        if item.name.startswith('.') or item.name == '__pycache__':
                            continue
                        children[item.name] = get_tree(item, prefix + "  ", max_depth, current_depth + 1)
                except PermissionError:
                    pass
                    
                tree = {
                    'type': 'directory',
                    'children': children
                }
                
            return tree
        
        self.context['file_structure'] = get_tree('.', max_depth=4)
        print("✅ File structure mapped")
        
    def analyze_key_files(self):
        """Analyze key Python files"""
        print("\n📝 Analyzing key files...")
        
        key_files = [
            'hedge_intelligence.py',
            'services/ai_service.py',
            'services/document_service.py',
            'components/document_explorer.py',
            'components/persistent_chat.py',
            'components/data_extractor.py',
            'components/ipo_tracker_enhanced.py'
        ]
        
        for filepath in key_files:
            if Path(filepath).exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                analysis = {
                    'lines': len(content.splitlines()),
                    'characters': len(content),
                    'functions': [],
                    'classes': [],
                    'imports': []
                }
                
                # Extract functions and classes
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            analysis['functions'].append(node.name)
                        elif isinstance(node, ast.ClassDef):
                            analysis['classes'].append(node.name)
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                analysis['imports'].append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            analysis['imports'].append(f"{node.module}")
                except:
                    pass
                    
                self.context['code_analysis'][filepath] = analysis
                print(f"✅ Analyzed {filepath}")
                
    def summarize_data(self):
        """Summarize data directories"""
        print("\n📊 Summarizing data...")
        
        data_dir = Path('data')
        if data_dir.exists():
            # SEC Documents
            sec_path = data_dir / 'sec_documents'
            if sec_path.exists():
                companies = {}
                total_files = 0
                
                for company_dir in sec_path.iterdir():
                    if company_dir.is_dir():
                        files = list(company_dir.glob('*.html'))
                        companies[company_dir.name] = {
                            'count': len(files),
                            'types': self.categorize_filings(files)
                        }
                        total_files += len(files)
                        
                self.context['data_summary']['sec_documents'] = {
                    'total_companies': len(companies),
                    'total_files': total_files,
                    'companies': companies
                }
                
            # Other data directories
            for subdir in data_dir.iterdir():
                if subdir.is_dir() and subdir.name != 'sec_documents':
                    file_count = len(list(subdir.glob('*')))
                    self.context['data_summary'][subdir.name] = {
                        'file_count': file_count
                    }
                    
        print("✅ Data summarized")
        
    def categorize_filings(self, files):
        """Categorize SEC filings by type"""
        categories = {
            '10-K': 0,
            '10-Q': 0,
            '8-K': 0,
            'S-1': 0,
            'Other': 0
        }
        
        for file in files:
            name = file.name.upper()
            if '10-K' in name or '10K' in name:
                categories['10-K'] += 1
            elif '10-Q' in name or '10Q' in name:
                categories['10-Q'] += 1
            elif '8-K' in name or '8K' in name:
                categories['8-K'] += 1
            elif 'S-1' in name or 'S1' in name:
                categories['S-1'] += 1
            else:
                categories['Other'] += 1
                
        return categories
        
    def check_dependencies(self):
        """Check installed dependencies"""
        print("\n📦 Checking dependencies...")
        
        if Path('requirements.txt').exists():
            with open('requirements.txt', 'r') as f:
                requirements = f.read().splitlines()
                
            self.context['dependencies']['requirements'] = requirements
            
        # Check what's actually installed
        import pkg_resources
        installed = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        self.context['dependencies']['installed'] = installed
        
        print("✅ Dependencies checked")
        
    def extract_configuration(self):
        """Extract configuration from .env"""
        print("\n⚙️ Extracting configuration...")
        
        if Path('.env').exists():
            with open('.env', 'r') as f:
                env_content = f.read()
                
            # Extract keys (not values for security)
            keys = []
            for line in env_content.splitlines():
                if '=' in line and not line.startswith('#'):
                    key = line.split('=')[0].strip()
                    keys.append(key)
                    
            self.context['configuration']['env_keys'] = keys
            
        print("✅ Configuration extracted")
        
    def generate_markdown_report(self):
        """Generate markdown report"""
        print("\n📄 Generating report...")
        
        report = f"""# HEDGE INTELLIGENCE - FULL CONTEXT DUMP
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*  
*User: thorrobber22*

## 🎯 PROJECT OVERVIEW

**Name:** Hedge Intelligence  
**Purpose:** SEC Document Analysis Platform with AI Chat  
**Core Features:**
- Document Explorer (file tree navigation)
- AI Chat with citations
- Automatic data extraction
- IPO tracking
- Professional grey theme

## 📁 FILE STRUCTURE

### Key Files:
"""
        
        # Add key files
        for filepath, analysis in self.context['code_analysis'].items():
            report += f"\n**{filepath}**\n"
            report += f"- Lines: {analysis['lines']}\n"
            report += f"- Classes: {', '.join(analysis['classes']) if analysis['classes'] else 'None'}\n"
            report += f"- Functions: {len(analysis['functions'])}\n"
            
        # Add data summary
        report += "\n## 📊 DATA SUMMARY\n\n"
        
        if 'sec_documents' in self.context['data_summary']:
            sec_data = self.context['data_summary']['sec_documents']
            report += f"**SEC Documents:**\n"
            report += f"- Total Companies: {sec_data['total_companies']}\n"
            report += f"- Total Files: {sec_data['total_files']}\n\n"
            
            report += "**Companies:**\n"
            for company, data in list(sec_data['companies'].items())[:5]:
                report += f"- {company}: {data['count']} files\n"
                
        # Add dependencies
        report += "\n## 📦 DEPENDENCIES\n\n"
        if 'requirements' in self.context['dependencies']:
            report += "**Required:**\n"
            for req in self.context['dependencies']['requirements']:
                report += f"- {req}\n"
                
        # Save report
        with open('context_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
            
        print("✅ Report generated: context_report.md")
        
    def save_context(self):
        """Save full context as JSON"""
        with open('full_context.json', 'w', encoding='utf-8') as f:
            json.dump(self.context, f, indent=2)
            
        print("✅ Full context saved: full_context.json")

def main():
    generator = ContextGenerator()
    generator.generate_full_context()
    
    print("\n" + "="*70)
    print("✅ CONTEXT GENERATION COMPLETE!")
    print("="*70)
    print("\nGenerated files:")
    print("1. full_context.json - Complete data structure")
    print("2. context_report.md - Readable summary")

if __name__ == "__main__":
    main()