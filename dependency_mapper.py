"""
dependency_mapper.py - Visualize how components connect
Creates a detailed map of all dependencies
"""

import os
import ast
import json
from pathlib import Path
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt

class DependencyMapper:
    def __init__(self):
        self.base_path = Path(".")
        self.graph = nx.DiGraph()
        self.component_map = {}
        
    def map_all_dependencies(self):
        """Create complete dependency map"""
        print("MAPPING COMPONENT DEPENDENCIES...")
        print("-" * 60)
        
        # 1. Find all Python files
        python_files = list(self.base_path.rglob("*.py"))
        
        # 2. Build import map
        for file_path in python_files:
            if any(skip in str(file_path) for skip in ['venv', '__pycache__', '.git']):
                continue
                
            self.analyze_file_imports(file_path)
            
        # 3. Create visualization
        self.visualize_dependencies()
        
        # 4. Find critical paths
        self.find_critical_paths()
        
        # 5. Save dependency data
        self.save_dependency_data()
        
    def analyze_file_imports(self, file_path):
        """Analyze imports in a single file"""
        relative_path = str(file_path.relative_to(self.base_path))
        module_name = relative_path.replace(os.sep, '.').replace('.py', '')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        
            # Add to graph
            self.graph.add_node(module_name, file=relative_path)
            
            # Add edges for internal imports
            for imp in imports:
                if any(imp.startswith(prefix) for prefix in ['components', 'services', 'utils']):
                    self.graph.add_edge(module_name, imp)
                    
            self.component_map[module_name] = {
                'file': relative_path,
                'imports': imports,
                'external_deps': [i for i in imports if not any(
                    i.startswith(p) for p in ['components', 'services', 'utils']
                )]
            }
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
    def visualize_dependencies(self):
        """Create dependency visualization"""
        print("\nCreating dependency visualization...")
        
        # Group nodes by category
        categories = {
            'components': [],
            'services': [],
            'apps': [],
            'utils': [],
            'other': []
        }
        
        for node in self.graph.nodes():
            if node.startswith('components'):
                categories['components'].append(node)
            elif node.startswith('services'):
                categories['services'].append(node)
            elif 'app' in node:
                categories['apps'].append(node)
            elif node.startswith('utils'):
                categories['utils'].append(node)
            else:
                categories['other'].append(node)
                
        # Print category summary
        for category, nodes in categories.items():
            if nodes:
                print(f"\n{category.upper()}: {len(nodes)} components")
                in_degree = [(n, self.graph.in_degree(n)) for n in nodes]
                in_degree.sort(key=lambda x: x[1], reverse=True)
                
                print("  Most depended upon:")
                for node, degree in in_degree[:3]:
                    if degree > 0:
                        print(f"    - {node}: {degree} dependencies")
                        
    def find_critical_paths(self):
        """Identify critical dependency paths"""
        print("\nFINDING CRITICAL PATHS...")
        print("-" * 60)
        
        # Find cycles
        try:
            cycles = list(nx.simple_cycles(self.graph))
            if cycles:
                print(f"\n⚠️  Found {len(cycles)} circular dependencies!")
                for cycle in cycles[:3]:
                    print(f"  Cycle: {' -> '.join(cycle)} -> {cycle[0]}")
            else:
                print("\n✓ No circular dependencies found")
        except:
            print("\n✓ No circular dependencies found")
            
        # Find isolated components
        isolated = [n for n in self.graph.nodes() if 
                   self.graph.in_degree(n) == 0 and 
                   self.graph.out_degree(n) == 0]
        if isolated:
            print(f"\n📍 Found {len(isolated)} isolated components:")
            for comp in isolated[:5]:
                print(f"  - {comp}")
                
        # Find hubs (highly connected)
        hubs = [(n, self.graph.in_degree(n) + self.graph.out_degree(n)) 
                for n in self.graph.nodes()]
        hubs.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n🔗 Most connected components:")
        for node, connections in hubs[:5]:
            if connections > 0:
                print(f"  - {node}: {connections} connections")
                
    def save_dependency_data(self):
        """Save dependency analysis"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'total_components': len(self.graph.nodes()),
            'total_dependencies': len(self.graph.edges()),
            'components': self.component_map,
            'edges': list(self.graph.edges()),
            'isolated': [n for n in self.graph.nodes() if 
                        self.graph.in_degree(n) == 0 and 
                        self.graph.out_degree(n) == 0]
        }
        
        with open('dependency_analysis.json', 'w') as f:
            json.dump(output, f, indent=2)
            
        print(f"\n💾 Dependency data saved to dependency_analysis.json")

if __name__ == "__main__":
    mapper = DependencyMapper()
    mapper.map_all_dependencies()