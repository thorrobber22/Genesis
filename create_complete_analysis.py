#!/usr/bin/env python3
"""
Complete analysis of all Hedge Intelligence components
"""

from pathlib import Path
import re
import json
import ast

class HedgeIntelligenceAnalyzer:
    def __init__(self):
        self.root = Path(".")
        self.components = {}
        self.imports = {}
        self.functions = {}
        self.session_states = {}
        self.data_structures = {}
        
    def analyze_all(self):
        """Run complete analysis"""
        print("HEDGE INTELLIGENCE - COMPLETE SYSTEM ANALYSIS")
        print("="*80)
        
        # 1. Component Analysis
        self.analyze_components()
        
        # 2. Main App Analysis
        self.analyze_main_app()
        
        # 3. Service Analysis
        self.analyze_services()
        
        # 4. Data Structure Analysis
        self.analyze_data_structures()
        
        # 5. Session State Analysis
        self.analyze_session_state()
        
        # 6. Import Dependency Analysis
        self.analyze_imports()
        
        # 7. Function Flow Analysis
        self.analyze_function_flows()
        
        # 8. Error Handling Analysis
        self.analyze_error_handling()
        
        # Generate report
        self.generate_report()
    
    def analyze_components(self):
        """Analyze all components"""
        print("\n1. COMPONENT ANALYSIS")
        print("-"*80)
        
        components_dir = self.root / "components"
        if components_dir.exists():
            for comp_file in components_dir.glob("*.py"):
                if comp_file.stem == "__init__":
                    continue
                    
                print(f"\n  Analyzing: {comp_file.name}")
                self.components[comp_file.stem] = self.analyze_file(comp_file)
                
    def analyze_main_app(self):
        """Analyze main application file"""
        print("\n2. MAIN APP ANALYSIS")
        print("-"*80)
        
        main_app = self.root / "hedge_intelligence.py"
        if main_app.exists():
            print(f"\n  Analyzing: hedge_intelligence.py")
            self.components['main'] = self.analyze_file(main_app)
            
    def analyze_services(self):
        """Analyze all services"""
        print("\n3. SERVICE ANALYSIS")
        print("-"*80)
        
        services_dir = self.root / "services"
        if services_dir.exists():
            for service_file in services_dir.glob("*.py"):
                if service_file.stem == "__init__":
                    continue
                    
                print(f"\n  Analyzing: {service_file.name}")
                self.components[f"service_{service_file.stem}"] = self.analyze_file(service_file)
    
    def analyze_file(self, filepath):
        """Analyze a single Python file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'path': str(filepath),
            'imports': self.extract_imports(content),
            'classes': self.extract_classes(content),
            'functions': self.extract_functions(content),
            'session_states': self.extract_session_states(content),
            'streamlit_components': self.extract_streamlit_components(content),
            'error_handling': self.extract_error_handling(content)
        }
        
        # Show summary
        print(f"    - Imports: {len(analysis['imports'])}")
        print(f"    - Classes: {len(analysis['classes'])}")
        print(f"    - Functions: {len(analysis['functions'])}")
        print(f"    - Session States: {len(analysis['session_states'])}")
        print(f"    - Streamlit Components: {len(analysis['streamlit_components'])}")
        print(f"    - Try/Except Blocks: {len(analysis['error_handling'])}")
        
        return analysis
    
    def extract_imports(self, content):
        """Extract all imports"""
        imports = []
        
        # Standard imports
        import_pattern = re.findall(r'^import\s+(\S+)(?:\s+as\s+(\S+))?', content, re.MULTILINE)
        imports.extend([(imp[0], imp[1] if imp[1] else imp[0]) for imp in import_pattern])
        
        # From imports
        from_pattern = re.findall(r'^from\s+(\S+)\s+import\s+(.+)$', content, re.MULTILINE)
        for module, items in from_pattern:
            items_list = [item.strip() for item in items.split(',')]
            imports.extend([(module, item.split(' as ')[0].strip()) for item in items_list])
        
        return imports
    
    def extract_classes(self, content):
        """Extract class definitions"""
        classes = []
        class_pattern = re.findall(r'^class\s+(\w+)(?:\(([^)]+)\))?\s*:', content, re.MULTILINE)
        
        for cls_name, parent in class_pattern:
            # Find methods in class
            class_block = re.search(rf'class\s+{cls_name}.*?(?=\nclass|\Z)', content, re.DOTALL)
            methods = []
            if class_block:
                methods = re.findall(r'def\s+(\w+)\s*\(', class_block.group(0))
            
            classes.append({
                'name': cls_name,
                'parent': parent.strip() if parent else None,
                'methods': methods
            })
        
        return classes
    
    def extract_functions(self, content):
        """Extract function definitions"""
        functions = []
        func_pattern = re.findall(r'^def\s+(\w+)\s*\(([^)]*)\)\s*(?:->([^:]+))?\s*:', content, re.MULTILINE)
        
        for func_name, params, return_type in func_pattern:
            # Extract docstring
            func_block = re.search(rf'def\s+{func_name}.*?"""(.*?)"""', content, re.DOTALL)
            docstring = func_block.group(1).strip() if func_block else ""
            
            functions.append({
                'name': func_name,
                'params': params.strip(),
                'return_type': return_type.strip() if return_type else None,
                'docstring': docstring
            })
        
        return functions
    
    def extract_session_states(self, content):
        """Extract session state usage"""
        session_states = set()
        
        # Pattern for st.session_state access
        patterns = [
            r'st\.session_state\[[\'"](.*?)[\'"]\]',
            r'st\.session_state\.([\w]+)',
            r'if\s+[\'"](.*?)[\'"]\s+in\s+st\.session_state',
            r'st\.session_state\.get\([\'"](.*?)[\'"]\)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            session_states.update(matches)
        
        return list(session_states)
    
    def extract_streamlit_components(self, content):
        """Extract Streamlit component usage"""
        components = []
        
        # Common Streamlit components
        st_components = [
            'title', 'header', 'subheader', 'text', 'markdown', 'caption',
            'button', 'text_input', 'text_area', 'selectbox', 'multiselect',
            'slider', 'checkbox', 'radio', 'number_input', 'date_input',
            'time_input', 'file_uploader', 'color_picker', 'form', 'form_submit_button',
            'columns', 'container', 'expander', 'sidebar', 'empty', 'placeholder',
            'info', 'warning', 'error', 'success', 'exception', 'spinner',
            'progress', 'balloons', 'snow', 'dataframe', 'table', 'metric',
            'json', 'code', 'latex', 'write', 'image', 'audio', 'video'
        ]
        
        for comp in st_components:
            pattern = rf'st\.{comp}\s*\('
            if re.search(pattern, content):
                count = len(re.findall(pattern, content))
                components.append({'name': comp, 'count': count})
        
        return components
    
    def extract_error_handling(self, content):
        """Extract error handling blocks"""
        error_blocks = []
        
        # Find try/except blocks
        try_pattern = re.findall(r'try\s*:(.*?)except(?:\s+(\w+))?\s*(?:as\s+(\w+))?\s*:', content, re.DOTALL)
        
        for try_block, exception_type, exception_var in try_pattern:
            error_blocks.append({
                'exception_type': exception_type if exception_type else 'Exception',
                'variable': exception_var if exception_var else None,
                'has_else': 'else:' in try_block,
                'has_finally': 'finally:' in try_block
            })
        
        return error_blocks
    
    def analyze_data_structures(self):
        """Analyze JSON data structures"""
        print("\n4. DATA STRUCTURE ANALYSIS")
        print("-"*80)
        
        data_dir = self.root / "data"
        if data_dir.exists():
            for json_file in data_dir.glob("*.json"):
                print(f"\n  Analyzing: {json_file.name}")
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.data_structures[json_file.stem] = {
                        'type': type(data).__name__,
                        'size': len(data) if isinstance(data, (list, dict)) else 1,
                        'structure': self.analyze_json_structure(data)
                    }
                    
                    print(f"    - Type: {type(data).__name__}")
                    print(f"    - Size: {len(data) if isinstance(data, (list, dict)) else 1}")
                    
                except Exception as e:
                    print(f"    - Error: {e}")
    
    def analyze_json_structure(self, data, level=0, max_level=3):
        """Analyze JSON structure recursively"""
        if level > max_level:
            return "..."
        
        if isinstance(data, dict):
            return {k: self.analyze_json_structure(v, level+1, max_level) 
                    for k, v in list(data.items())[:5]}  # Sample first 5
        elif isinstance(data, list) and data:
            return [self.analyze_json_structure(data[0], level+1, max_level)]
        else:
            return type(data).__name__
    
    def analyze_session_state(self):
        """Compile all session state usage"""
        print("\n5. SESSION STATE COMPILATION")
        print("-"*80)
        
        all_states = set()
        for comp_name, comp_data in self.components.items():
            all_states.update(comp_data.get('session_states', []))
        
        print(f"\n  Total unique session states: {len(all_states)}")
        for state in sorted(all_states):
            print(f"    - {state}")
        
        self.session_states = all_states
    
    def analyze_imports(self):
        """Analyze import dependencies"""
        print("\n6. IMPORT DEPENDENCY ANALYSIS")
        print("-"*80)
        
        # Build import graph
        import_graph = {}
        for comp_name, comp_data in self.components.items():
            imports = comp_data.get('imports', [])
            import_graph[comp_name] = [imp[0] for imp in imports]
        
        # Find circular dependencies
        print("\n  Checking for circular dependencies...")
        circular = self.find_circular_dependencies(import_graph)
        if circular:
            print("    ⚠️  Circular dependencies found:")
            for cycle in circular:
                print(f"      {' -> '.join(cycle)}")
        else:
            print("    ✅ No circular dependencies found")
        
        self.imports = import_graph
    
    def find_circular_dependencies(self, graph):
        """Find circular import dependencies"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                elif neighbor not in visited and neighbor in graph:
                    dfs(neighbor, path[:])
            
            rec_stack.remove(node)
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def analyze_function_flows(self):
        """Analyze how functions call each other"""
        print("\n7. FUNCTION FLOW ANALYSIS")
        print("-"*80)
        
        # Key function flows
        key_flows = {
            'document_selection': [],
            'chat_interaction': [],
            'navigation': []
        }
        
        # Analyze main app for flows
        main_comp = self.components.get('main', {})
        main_funcs = main_comp.get('functions', [])
        
        print("\n  Main application functions:")
        for func in main_funcs:
            print(f"    - {func['name']}()")
            if func['docstring']:
                print(f"      {func['docstring'][:60]}...")
    
    def analyze_error_handling(self):
        """Compile error handling analysis"""
        print("\n8. ERROR HANDLING ANALYSIS")
        print("-"*80)
        
        total_try_except = 0
        components_with_errors = []
        
        for comp_name, comp_data in self.components.items():
            error_blocks = comp_data.get('error_handling', [])
            if error_blocks:
                total_try_except += len(error_blocks)
                components_with_errors.append({
                    'name': comp_name,
                    'count': len(error_blocks),
                    'types': list(set(e['exception_type'] for e in error_blocks))
                })
        
        print(f"\n  Total try/except blocks: {total_try_except}")
        print("\n  Components with error handling:")
        for comp in components_with_errors:
            print(f"    - {comp['name']}: {comp['count']} blocks")
            print(f"      Exception types: {', '.join(comp['types'])}")
    
    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "="*80)
        print("ANALYSIS SUMMARY")
        print("="*80)
        
        # Save to file
        report = {
            'components': self.components,
            'session_states': list(self.session_states),
            'data_structures': self.data_structures,
            'imports': self.imports
        }
        
        with open('hedge_intelligence_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print("\n✅ Complete analysis saved to: hedge_intelligence_analysis.json")
        
        # Key findings
        print("\nKEY FINDINGS:")
        print("-"*40)
        print(f"1. Total components analyzed: {len(self.components)}")
        print(f"2. Total session states: {len(self.session_states)}")
        print(f"3. Total data structures: {len(self.data_structures)}")
        print(f"4. Components with error handling: {len([c for c in self.components.values() if c.get('error_handling')])}")

if __name__ == "__main__":
    analyzer = HedgeIntelligenceAnalyzer()
    analyzer.analyze_all()