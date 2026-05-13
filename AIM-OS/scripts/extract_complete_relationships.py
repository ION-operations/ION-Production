#!/usr/bin/env python3
"""
Complete Relationship Extractor - Extract ALL relationships in AIM-OS

Extracts:
- System → System (architecture dependencies)
- Doc → Doc (L0-L6 hierarchy, cross-references)
- Code → Code (imports, function calls)
- Doc → Code (describes implementation)
- Test → Code (validates implementation)
- Index → Everything (SUPER_INDEX, catalogs)
- Tag → Code (NL tag annotations)
- Quintet groupings (code+test+doc+spec+tag)

This builds the complete relationship database for visualization.
"""

import json
import re
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).parent.parent

class RelationshipExtractor:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.node_ids = set()
        
    def add_node(self, node_id: str, node_data: dict):
        """Add node if not exists"""
        if node_id not in self.node_ids:
            self.nodes.append({'id': node_id, **node_data})
            self.node_ids.add(node_id)
    
    def add_edge(self, from_id: str, to_id: str, edge_data: dict):
        """Add edge"""
        self.edges.append({
            'from': from_id,
            'to': to_id,
            **edge_data
        })
    
    def extract_system_relationships(self):
        """Parse cross_system_connections.yaml for system dependencies"""
        print("Extracting system relationships...")
        
        yaml_path = PROJECT_ROOT / 'knowledge_architecture' / 'NAVIGATION' / 'cross_system_connections.yaml'
        
        if not yaml_path.exists():
            print(f"  [WARN] cross_system_connections.yaml not found")
            return
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            # YAML file has multiple documents, load all
            docs = list(yaml.safe_load_all(f))
        
        # Find the document with 'systems' key
        systems = None
        for doc in docs:
            if doc and 'systems' in doc:
                systems = doc['systems']
                break
        
        if not systems:
            print("  [WARN] No systems found in YAML")
            return
        
        for system_id, system_data in systems.items():
            # Add system node
            self.add_node(f"system:{system_id}", {
                'type': 'system',
                'name': system_data.get('name', system_id),
                'status': system_data.get('status', 'unknown'),
                'layer': self._determine_layer(system_id),
            })
            
            # Add dependency edges
            depends_on = system_data.get('depends_on', [])
            for dep in depends_on:
                if isinstance(dep, dict):
                    dep_id = list(dep.keys())[0]
                else:
                    dep_id = dep
                
                self.add_edge(f"system:{system_id}", f"system:{dep_id}", {
                    'type': 'depends_on',
                    'strength': 'critical',
                    'zoom_levels': [0, 1, 2]
                })
            
            # Add provides_to edges
            provides_to = system_data.get('provides_to', [])
            for provider in provides_to:
                if isinstance(provider, dict):
                    provider_id = list(provider.keys())[0]
                else:
                    provider_id = provider
                
                self.add_edge(f"system:{system_id}", f"system:{provider_id}", {
                    'type': 'provides_to',
                    'strength': 'strong',
                    'zoom_levels': [0, 1, 2]
                })
        
        print(f"  Found {len([n for n in self.nodes if n['type']=='system'])} systems")
    
    def extract_doc_hierarchy(self):
        """Extract L0→L1→L2→L3→L4→L5→L6 chains for each system"""
        print("Extracting documentation hierarchy...")
        
        systems_dir = PROJECT_ROOT / 'knowledge_architecture' / 'systems'
        
        if not systems_dir.exists():
            return
        
        doc_count = 0
        
        for system_dir in systems_dir.iterdir():
            if not system_dir.is_dir():
                continue
            
            system_id = system_dir.name
            
            # Find all L/T level docs
            levels = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6',
                     'T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6']
            
            doc_files = {}
            for level in levels:
                for suffix in ['_executive.md', '_overview.md', '_architecture.md', 
                              '_detailed.md', '_complete.md', '_academic.md', '_spec.md']:
                    doc_path = system_dir / f"{level}{suffix}"
                    if doc_path.exists():
                        doc_files[level] = doc_path
                        break
            
            # Add doc nodes and hierarchy edges
            prev_level = None
            for level in ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
                if level in doc_files:
                    doc_path = doc_files[level]
                    node_id = f"doc:{system_id}:{level}"
                    
                    # Count words
                    try:
                        with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            words = len(content.split())
                    except:
                        words = 0
                    
                    self.add_node(node_id, {
                        'type': 'doc',
                        'system': system_id,
                        'level': level,
                        'path': str(doc_path.relative_to(PROJECT_ROOT)),
                        'words': words,
                        'zoom_levels': [1, 2, 3, 4]
                    })
                    
                    doc_count += 1
                    
                    # Add hierarchy edge (L0→L1→L2...)
                    if prev_level:
                        self.add_edge(f"doc:{system_id}:{prev_level}", node_id, {
                            'type': 'expands_to',
                            'relationship': 'documentation_hierarchy',
                            'zoom_levels': [2, 3, 4]
                        })
                    
                    # Link to system
                    self.add_edge(f"system:{system_id}", node_id, {
                        'type': 'has_documentation',
                        'relationship': 'documented_by',
                        'zoom_levels': [1, 2, 3]
                    })
                    
                    prev_level = level
        
        print(f"  Found {doc_count} documentation files")
    
    def extract_code_packages(self):
        """Extract all packages and code files"""
        print("Extracting code packages...")
        
        packages_dir = PROJECT_ROOT / 'packages'
        
        if not packages_dir.exists():
            return
        
        code_count = 0
        
        for pkg_dir in packages_dir.iterdir():
            if not pkg_dir.is_dir() or pkg_dir.name.startswith('_'):
                continue
            
            pkg_id = pkg_dir.name
            
            # Determine system mapping
            system = self._map_package_to_system(pkg_id)
            
            # Add package node
            self.add_node(f"package:{pkg_id}", {
                'type': 'package',
                'name': pkg_id,
                'system': system,
                'path': str(pkg_dir.relative_to(PROJECT_ROOT)),
                'zoom_levels': [1, 2, 3]
            })
            
            # Link package to system
            if system:
                self.add_edge(f"system:{system}", f"package:{pkg_id}", {
                    'type': 'implemented_by',
                    'relationship': 'package_implements_system',
                    'zoom_levels': [1, 2]
                })
            
            # Find all Python files (non-test)
            py_files = [f for f in pkg_dir.rglob('*.py') 
                       if '__pycache__' not in str(f) and not f.name.startswith('test_')]
            
            for py_file in py_files:
                code_id = f"code:{py_file.relative_to(PROJECT_ROOT)}"
                
                # Count LOC
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
                except:
                    loc = 0
                
                self.add_node(code_id, {
                    'type': 'code',
                    'language': 'python',
                    'package': pkg_id,
                    'system': system,
                    'path': str(py_file.relative_to(PROJECT_ROOT)),
                    'loc': loc,
                    'zoom_levels': [2, 3, 4]
                })
                
                # Link to package
                self.add_edge(f"package:{pkg_id}", code_id, {
                    'type': 'contains',
                    'relationship': 'package_contains_file',
                    'zoom_levels': [2, 3]
                })
                
                code_count += 1
        
        print(f"  Found {code_count} code files")
    
    def extract_test_relationships(self):
        """Extract test files and link to code"""
        print("Extracting test relationships...")
        
        packages_dir = PROJECT_ROOT / 'packages'
        
        if not packages_dir.exists():
            return
        
        test_count = 0
        
        for pkg_dir in packages_dir.iterdir():
            if not pkg_dir.is_dir():
                continue
            
            # Find test files
            test_files = list(pkg_dir.rglob('test_*.py'))
            
            for test_file in test_files:
                test_id = f"test:{test_file.relative_to(PROJECT_ROOT)}"
                
                # Count tests
                try:
                    with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        test_funcs = content.count('def test_')
                except:
                    test_funcs = 0
                
                self.add_node(test_id, {
                    'type': 'test',
                    'language': 'python',
                    'path': str(test_file.relative_to(PROJECT_ROOT)),
                    'test_count': test_funcs,
                    'zoom_levels': [2, 3, 4]
                })
                
                # Try to find corresponding code file
                # test_witness.py → witness.py
                code_name = test_file.name.replace('test_', '')
                potential_code = test_file.parent.parent / code_name
                
                if potential_code.exists():
                    code_id = f"code:{potential_code.relative_to(PROJECT_ROOT)}"
                    self.add_edge(test_id, code_id, {
                        'type': 'tests',
                        'relationship': 'validates',
                        'zoom_levels': [2, 3, 4]
                    })
                
                test_count += 1
        
        print(f"  Found {test_count} test files")
    
    def extract_code_imports(self):
        """Extract import relationships between code files"""
        print("Extracting code imports...")
        
        # This could be MANY relationships - be selective
        # Only track cross-package imports (not internal)
        
        packages_dir = PROJECT_ROOT / 'packages'
        if not packages_dir.exists():
            return
        
        import_count = 0
        
        for pkg_dir in packages_dir.iterdir():
            if not pkg_dir.is_dir():
                continue
            
            py_files = [f for f in pkg_dir.rglob('*.py') if '__pycache__' not in str(f)]
            
            for py_file in py_files:
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Find imports from other packages
                    # from packages.cmc_service import X
                    # from cmc_service import X
                    imports = re.findall(r'from\s+(?:packages\.)?(\w+)', content)
                    
                    for imp in set(imports):
                        # Check if this is another package
                        if imp != pkg_dir.name and (packages_dir / imp).exists():
                            from_id = f"code:{py_file.relative_to(PROJECT_ROOT)}"
                            to_id = f"package:{imp}"
                            
                            self.add_edge(from_id, to_id, {
                                'type': 'imports_from',
                                'relationship': 'code_dependency',
                                'zoom_levels': [3, 4]
                            })
                            
                            import_count += 1
                
                except Exception as e:
                    pass
        
        print(f"  Found {import_count} import relationships")
    
    def extract_super_index_relationships(self):
        """Parse SUPER_INDEX.md to show how it connects everything"""
        print("Extracting SUPER_INDEX relationships...")
        
        super_index_path = PROJECT_ROOT / 'knowledge_architecture' / 'SUPER_INDEX.md'
        
        if not super_index_path.exists():
            return
        
        # Add SUPER_INDEX as special node
        self.add_node("index:SUPER_INDEX", {
            'type': 'index',
            'name': 'SUPER_INDEX',
            'path': str(super_index_path.relative_to(PROJECT_ROOT)),
            'zoom_levels': [0, 1, 2, 3, 4]
        })
        
        with open(super_index_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find all concept entries
        # Pattern: **ConceptName:**
        concepts = re.findall(r'\*\*([A-Z][A-Za-z\s]+(?:\([A-Z]+\))?)\:\*\*', content)
        
        connection_count = 0
        
        for concept in set(concepts):
            concept_id = f"concept:{concept}"
            
            self.add_node(concept_id, {
                'type': 'concept',
                'name': concept,
                'zoom_levels': [4, 5]
            })
            
            # Connect SUPER_INDEX to concept
            self.add_edge("index:SUPER_INDEX", concept_id, {
                'type': 'indexes',
                'relationship': 'maps_concept',
                'zoom_levels': [3, 4, 5]
            })
            
            connection_count += 1
        
        print(f"  SUPER_INDEX indexes {connection_count} concepts")
    
    def extract_nl_tag_catalogs(self):
        """Extract NL tag catalogs and their coverage"""
        print("Extracting NL tag relationships...")
        
        systems_dir = PROJECT_ROOT / 'knowledge_architecture' / 'systems'
        
        if not systems_dir.exists():
            return
        
        tag_count = 0
        
        for system_dir in systems_dir.iterdir():
            if not system_dir.is_dir():
                continue
            
            catalog_path = system_dir / 'NL_TAG_CATALOG.md'
            
            if catalog_path.exists():
                system_id = system_dir.name
                
                # Add catalog as index node
                catalog_id = f"index:NL_TAG_CATALOG:{system_id}"
                
                self.add_node(catalog_id, {
                    'type': 'index',
                    'name': f'{system_id} NL Tag Catalog',
                    'system': system_id,
                    'path': str(catalog_path.relative_to(PROJECT_ROOT)),
                    'zoom_levels': [2, 3, 4]
                })
                
                # Link to system
                self.add_edge(f"system:{system_id}", catalog_id, {
                    'type': 'has_catalog',
                    'relationship': 'cataloged_by',
                    'zoom_levels': [2, 3]
                })
                
                # Parse catalog for tags
                with open(catalog_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Find all tag IDs (e.g., VIF-WITNESS-001)
                tags = re.findall(r'\*\*([A-Z]+-[A-Z]+-\d+)\*\*', content)
                
                for tag in set(tags):
                    tag_id = f"tag:{tag}"
                    
                    self.add_node(tag_id, {
                        'type': 'nl_tag',
                        'tag_id': tag,
                        'system': system_id,
                        'zoom_levels': [4, 5]
                    })
                    
                    # Link catalog to tag
                    self.add_edge(catalog_id, tag_id, {
                        'type': 'catalogs',
                        'relationship': 'contains_tag',
                        'zoom_levels': [4, 5]
                    })
                    
                    tag_count += 1
        
        print(f"  Found {tag_count} NL tags")
    
    def extract_quintet_groupings(self):
        """For each code file, find its test/doc/spec/tag (quintet)"""
        print("Extracting quintet groupings...")
        
        packages_dir = PROJECT_ROOT / 'packages'
        
        if not packages_dir.exists():
            return
        
        quintet_count = 0
        
        for pkg_dir in packages_dir.iterdir():
            if not pkg_dir.is_dir():
                continue
            
            py_files = [f for f in pkg_dir.rglob('*.py') 
                       if '__pycache__' not in str(f) and not f.name.startswith('test_')]
            
            for py_file in py_files:
                code_id = f"code:{py_file.relative_to(PROJECT_ROOT)}"
                
                # Create quintet group node
                quintet_id = f"quintet:{py_file.stem}"
                
                elements = []
                
                # Check for test
                test_file = py_file.parent / f"tests/test_{py_file.name}"
                if not test_file.exists():
                    test_file = py_file.parent / f"test_{py_file.name}"
                
                if test_file.exists():
                    test_id = f"test:{test_file.relative_to(PROJECT_ROOT)}"
                    elements.append(('test', test_id))
                
                # Check for doc (in system/L3)
                # This is approximate - would need better heuristic
                
                # Check for NL tags in file
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        has_tags = 'NL_TAG' in content
                except:
                    has_tags = False
                
                if has_tags:
                    elements.append(('tags', 'present'))
                
                # Calculate parity (simplified)
                parity = len(elements) / 5.0  # code + test + doc + spec + tags = 5
                
                if len(elements) >= 2:  # At least code + one other element
                    self.add_node(quintet_id, {
                        'type': 'quintet',
                        'code_file': str(py_file.relative_to(PROJECT_ROOT)),
                        'elements': elements,
                        'parity': parity,
                        'zoom_levels': [3, 4]
                    })
                    
                    # Link quintet to code
                    self.add_edge(quintet_id, code_id, {
                        'type': 'groups',
                        'relationship': 'quintet_contains',
                        'zoom_levels': [3, 4]
                    })
                    
                    quintet_count += 1
        
        print(f"  Found {quintet_count} quintet groupings")
    
    def _determine_layer(self, system_id: str) -> int:
        """Determine which layer a system belongs to"""
        system_lower = system_id.lower()
        
        if system_lower in ['cmc', 'seg']:
            return 1
        elif system_lower in ['hhni', 'vif', 'sdfcvf', 'sdf-cvf', 'sdf_cvf']:
            return 2
        elif system_lower in ['apoe']:
            return 3
        elif system_lower in ['cas', 'cognitive_analysis', 'tcs', 'timeline_context_system', 
                              'iis', 'intuitive_intelligence_system']:
            return 4
        elif 'icip' in system_lower or 'monaco' in system_lower or 'mobile' in system_lower:
            return 6
        else:
            return 5  # Infrastructure
    
    def _map_package_to_system(self, pkg_name: str) -> str:
        """Map package name to system"""
        pkg_lower = pkg_name.lower()
        
        mapping = {
            'cmc': 'CMC', 'cmc_service': 'CMC',
            'hhni': 'HHNI',
            'vif': 'VIF',
            'apoe': 'APOE', 'apoe_runner': 'APOE',
            'seg': 'SEG',
            'sdfcvf': 'SDF-CVF',
            'cas': 'CAS', 'cognitive_analysis': 'CAS',
            'timeline_context_system': 'TCS',
            'intuitive_intelligence_system': 'IIS',
            'scor': 'SCOR',
            'autonomous_research_dream': 'ARD',
        }
        
        return mapping.get(pkg_lower, None)
    
    def generate_statistics(self) -> dict:
        """Generate statistics about the graph"""
        stats = {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'by_node_type': defaultdict(int),
            'by_edge_type': defaultdict(int),
            'by_layer': defaultdict(int),
        }
        
        for node in self.nodes:
            stats['by_node_type'][node['type']] += 1
            if 'layer' in node:
                stats['by_layer'][node['layer']] += 1
        
        for edge in self.edges:
            stats['by_edge_type'][edge['type']] += 1
        
        return dict(stats)
    
    def save(self, output_path: str):
        """Save complete relationship database"""
        output = {
            'generated': '2025-11-04',
            'nodes': self.nodes,
            'edges': self.edges,
            'statistics': self.generate_statistics()
        }
        
        path = PROJECT_ROOT / output_path
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        
        return path


def main():
    print("=" * 80)
    print("COMPLETE RELATIONSHIP EXTRACTION")
    print("=" * 80)
    print()
    
    extractor = RelationshipExtractor()
    
    # Extract all relationship types
    extractor.extract_system_relationships()
    extractor.extract_doc_hierarchy()
    extractor.extract_code_packages()
    extractor.extract_test_relationships()
    extractor.extract_code_imports()
    extractor.extract_super_index_relationships()
    extractor.extract_nl_tag_catalogs()
    extractor.extract_quintet_groupings()
    
    # Generate statistics
    stats = extractor.generate_statistics()
    
    print()
    print("=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total nodes: {stats['total_nodes']:,}")
    print(f"Total edges: {stats['total_edges']:,}")
    print()
    print("Nodes by type:")
    for node_type, count in sorted(stats['by_node_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {node_type:>15s}: {count:>6,}")
    print()
    print("Edges by type:")
    for edge_type, count in sorted(stats['by_edge_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {edge_type:>20s}: {count:>6,}")
    print()
    
    # Save
    output_path = extractor.save('COMPLETE_RELATIONSHIPS.json')
    
    print("=" * 80)
    print(f"[SAVED] Complete relationship database: {output_path}")
    print()
    print(f"Ready for visualization generation!")
    print("Next: python scripts/generate_d3_visualization.py")
    print("=" * 80)


if __name__ == '__main__':
    main()

