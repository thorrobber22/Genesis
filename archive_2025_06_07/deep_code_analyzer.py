#!/usr/bin/env python3
"""
Deep Code Analyzer - Understands every file's purpose and potential
Date: 2025-06-07 12:29:30 UTC
Author: thorrobber22
Goal: Find reusable components for the main user-facing app
"""

import os
import ast
import json
from pathlib import Path
from datetime import datetime
import re

class DeepCodeAnalyzer:
    def __init__(self):
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'goal': 'Find components to leverage for chat-based SEC research app',
            'reusable_components': {},
            'ui_components': {},
            'data_processors': {},
            'api_integrations': {},
            'chat_components': {},
            'document_handlers': {},
            'full_file_analysis': {}
        }
        
    def analyze_python_file(self, filepath):
        """Deep analysis of Python file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            analysis = {
                'filepath': str(filepath),
                'size': len(content),
                'relevance_score': 0,
                'potential_use': [],
                'key_features': [],
                'imports': self.extract_imports(content),
                'classes': {},
                'functions': {},
                'ui_elements': [],
                'data_handling': [],
                'api_calls': []
            }
            
            # Parse AST
            try:
                tree = ast.parse(content)
                
                # Extract classes with methods
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_info = {
                            'methods': [],
                            'docstring': ast.get_docstring(node),
                            'inherits': [base.id for base in node.bases if hasattr(base, 'id')]
                        }
                        
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                class_info['methods'].append({
                                    'name': item.name,
                                    'args': [arg.arg for arg in item.args.args],
                                    'is_async': isinstance(item, ast.AsyncFunctionDef)
                                })
                        
                        analysis['classes'][node.name] = class_info
                    
                    elif isinstance(node, ast.FunctionDef):
                        if node.col_offset == 0:  # Top-level function
                            analysis['functions'][node.name] = {
                                'args': [arg.arg for arg in node.args.args],
                                'is_async': isinstance(node, ast.AsyncFunctionDef),
                                'docstring': ast.get_docstring(node)
                            }
            except:
                pass
            
            # Detect UI components (Streamlit)
            if 'streamlit' in content:
                analysis['relevance_score'] += 30
                analysis['potential_use'].append('UI_FRAMEWORK')
                
                # Find streamlit components
                ui_patterns = [
                    (r'st\.chat_input', 'chat_input'),
                    (r'st\.chat_message', 'chat_message'),
                    (r'st\.sidebar', 'sidebar'),
                    (r'st\.container', 'container'),
                    (r'st\.columns', 'layout'),
                    (r'st\.button', 'interaction'),
                    (r'st\.text_input', 'input'),
                    (r'st\.markdown', 'display')
                ]
                
                for pattern, component in ui_patterns:
                    if re.search(pattern, content):
                        analysis['ui_elements'].append(component)
            
            # Detect chat/conversation components
            chat_keywords = ['chat', 'message', 'conversation', 'response', 'query', 'prompt']
            for keyword in chat_keywords:
                if keyword in content.lower():
                    analysis['relevance_score'] += 10
                    analysis['potential_use'].append(f'CHAT_{keyword.upper()}')
            
            # Detect document processing
            if any(x in content for x in ['BeautifulSoup', 'PyPDF', 'extract_text', 'parse_document']):
                analysis['relevance_score'] += 25
                analysis['potential_use'].append('DOCUMENT_PROCESSING')
                analysis['data_handling'].append('document_parsing')
            
            # Detect SEC/financial data handling
            if any(x in content.lower() for x in ['sec', 'filing', 'edgar', 'cik', '10-k', '10-q', 's-1']):
                analysis['relevance_score'] += 40
                analysis['potential_use'].append('SEC_DATA_HANDLING')
                analysis['data_handling'].append('sec_filings')
            
            # Detect AI/ML components
            if any(x in content for x in ['openai', 'chromadb', 'embedding', 'vector', 'GPT', 'gemini']):
                analysis['relevance_score'] += 35
                analysis['potential_use'].append('AI_INTEGRATION')
                
                if 'chromadb' in content:
                    analysis['key_features'].append('vector_database')
                if 'openai' in content or 'gemini' in content:
                    analysis['key_features'].append('llm_integration')
            
            # Detect API patterns
            if 'aiohttp' in content or 'requests' in content or 'async def' in content:
                analysis['relevance_score'] += 15
                analysis['potential_use'].append('API_CLIENT')
                analysis['api_calls'] = self.find_api_endpoints(content)
            
            # Special handling for key files
            filename = filepath.name
            if 'scraper' in filename.lower():
                analysis['key_features'].append('data_collection')
            if 'admin' in filename.lower():
                analysis['key_features'].append('management_interface')
            if 'processor' in filename.lower():
                analysis['key_features'].append('data_processing')
            if 'ui' in filename.lower() or 'interface' in filename.lower():
                analysis['key_features'].append('user_interface')
                analysis['relevance_score'] += 20
            
            return analysis
            
        except Exception as e:
            return {'filepath': str(filepath), 'error': str(e)}
    
    def extract_imports(self, content):
        """Extract all imports from file"""
        imports = []
        import_pattern = r'(?:from\s+(\S+)\s+)?import\s+(.+)'
        
        for match in re.finditer(import_pattern, content):
            module = match.group(1) or ''
            items = match.group(2)
            imports.append({
                'module': module,
                'items': [item.strip() for item in items.split(',')]
            })
        
        return imports
    
    def find_api_endpoints(self, content):
        """Find API endpoints in code"""
        endpoints = []
        
        # URL patterns
        url_pattern = r'["\']https?://[^"\']+["\']'
        for match in re.finditer(url_pattern, content):
            endpoints.append(match.group().strip('"\''))
        
        return endpoints
    
    def categorize_file(self, analysis):
        """Categorize file based on analysis"""
        filepath = analysis['filepath']
        
        # High relevance for user-facing app
        if analysis['relevance_score'] >= 30:
            if 'UI_FRAMEWORK' in analysis['potential_use']:
                self.analysis_results['ui_components'][filepath] = {
                    'score': analysis['relevance_score'],
                    'ui_elements': analysis['ui_elements'],
                    'potential': 'Can be adapted for main chat interface'
                }
            
            if 'CHAT_' in str(analysis['potential_use']):
                self.analysis_results['chat_components'][filepath] = {
                    'score': analysis['relevance_score'],
                    'features': analysis['key_features'],
                    'potential': 'Chat functionality to reuse'
                }
            
            if 'DOCUMENT_PROCESSING' in analysis['potential_use']:
                self.analysis_results['document_handlers'][filepath] = {
                    'score': analysis['relevance_score'],
                    'capabilities': analysis['data_handling'],
                    'potential': 'Document parsing for viewer'
                }
            
            if 'AI_INTEGRATION' in analysis['potential_use']:
                self.analysis_results['data_processors'][filepath] = {
                    'score': analysis['relevance_score'],
                    'ai_features': analysis['key_features'],
                    'potential': 'AI/RAG functionality'
                }
            
            if 'SEC_DATA_HANDLING' in analysis['potential_use']:
                self.analysis_results['reusable_components'][filepath] = {
                    'score': analysis['relevance_score'],
                    'sec_features': analysis['data_handling'],
                    'classes': list(analysis['classes'].keys()),
                    'potential': 'SEC data expertise to leverage'
                }
    
    def analyze_project(self):
        """Analyze entire project"""
        print("🔍 DEEP CODE ANALYSIS FOR CHAT-BASED SEC APP")
        print("="*60)
        
        # Focus directories
        focus_dirs = [
            '.',
            'scrapers',
            'scrapers/sec',
            'processors',
            'utils'
        ]
        
        total_files = 0
        high_relevance_files = 0
        
        for focus_dir in focus_dirs:
            if not Path(focus_dir).exists():
                continue
                
            for root, dirs, files in os.walk(focus_dir):
                # Skip venv and cache
                dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'data']]
                
                for file in files:
                    if file.endswith('.py'):
                        filepath = Path(root) / file
                        total_files += 1
                        
                        print(f"Analyzing: {filepath}")
                        analysis = self.analyze_python_file(filepath)
                        
                        if 'error' not in analysis:
                            self.analysis_results['full_file_analysis'][str(filepath)] = analysis
                            self.categorize_file(analysis)
                            
                            if analysis['relevance_score'] >= 30:
                                high_relevance_files += 1
                                print(f"  ⭐ HIGH RELEVANCE: Score {analysis['relevance_score']}")
                                print(f"     Uses: {', '.join(analysis['potential_use'])}")
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Print summary
        print(f"\n📊 ANALYSIS COMPLETE")
        print(f"Total Python files analyzed: {total_files}")
        print(f"High relevance files: {high_relevance_files}")
        print(f"\n🎯 COMPONENTS TO LEVERAGE:")
        
        print(f"\n1. UI Components ({len(self.analysis_results['ui_components'])} files)")
        for filepath, info in list(self.analysis_results['ui_components'].items())[:3]:
            print(f"   • {Path(filepath).name}: {info['potential']}")
        
        print(f"\n2. Document Handlers ({len(self.analysis_results['document_handlers'])} files)")
        for filepath, info in list(self.analysis_results['document_handlers'].items())[:3]:
            print(f"   • {Path(filepath).name}: {info['potential']}")
        
        print(f"\n3. AI/Data Processors ({len(self.analysis_results['data_processors'])} files)")
        for filepath, info in list(self.analysis_results['data_processors'].items())[:3]:
            print(f"   • {Path(filepath).name}: {info['potential']}")
        
        # Save results
        with open('deep_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        print(f"\n✅ Full analysis saved to: deep_analysis_results.json")
        
        # Create actionable summary
        self.create_action_plan()
    
    def generate_recommendations(self):
        """Generate specific recommendations"""
        self.analysis_results['recommendations'] = {
            'immediate_reuse': [],
            'adapt_for_chat': [],
            'data_pipeline': [],
            'ui_inspiration': []
        }
        
        # Find best components
        for filepath, analysis in self.analysis_results['full_file_analysis'].items():
            if analysis.get('relevance_score', 0) >= 40:
                recommendation = {
                    'file': filepath,
                    'reason': analysis['potential_use'],
                    'classes_to_use': list(analysis.get('classes', {}).keys()),
                    'functions_to_use': list(analysis.get('functions', {}).keys())[:5]
                }
                
                if 'SEC_DATA_HANDLING' in analysis['potential_use']:
                    self.analysis_results['recommendations']['immediate_reuse'].append(recommendation)
                elif 'UI_FRAMEWORK' in analysis['potential_use']:
                    self.analysis_results['recommendations']['ui_inspiration'].append(recommendation)
                elif 'AI_INTEGRATION' in analysis['potential_use']:
                    self.analysis_results['recommendations']['data_pipeline'].append(recommendation)
    
    def create_action_plan(self):
        """Create actionable plan"""
        plan = []
        plan.append("🎯 ACTION PLAN FOR CHAT-BASED SEC APP")
        plan.append("="*60)
        plan.append("\nBUILD ORDER:")
        plan.append("\n1. LEVERAGE EXISTING COMPONENTS:")
        
        # List top files to reuse
        top_files = sorted(
            [(f, a) for f, a in self.analysis_results['full_file_analysis'].items()],
            key=lambda x: x[1].get('relevance_score', 0),
            reverse=True
        )[:10]
        
        for filepath, analysis in top_files:
            if analysis.get('relevance_score', 0) >= 30:
                plan.append(f"\n   📄 {Path(filepath).name} (Score: {analysis['relevance_score']})")
                plan.append(f"      Purpose: {', '.join(analysis.get('potential_use', []))}")
                if analysis.get('classes'):
                    plan.append(f"      Classes: {', '.join(list(analysis['classes'].keys())[:3])}")
                if analysis.get('key_features'):
                    plan.append(f"      Features: {', '.join(analysis['key_features'])}")
        
        plan.append("\n2. NEXT STEPS:")
        plan.append("   • Use document processor structure for ChromaDB integration")
        plan.append("   • Adapt UI components for clean chat interface")
        plan.append("   • Leverage SEC scraper classes for data retrieval")
        plan.append("   • Implement dual AI validation using existing patterns")
        
        with open('action_plan.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(plan))
        
        print("\n✅ Action plan saved to: action_plan.txt")

if __name__ == "__main__":
    analyzer = DeepCodeAnalyzer()
    analyzer.analyze_project()