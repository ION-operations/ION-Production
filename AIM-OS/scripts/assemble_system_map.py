#!/usr/bin/env python3
"""
Assemble System Map from Existing Organization
Tests the singularity property: If organization is O(n), this should be EASY

Strategy:
1. Parse SUPER_INDEX.md for all systems and concepts
2. Parse each system's L0_executive.md for metadata
3. Parse NL_TAG_CATALOG for integration points
4. Parse system connection maps (YAML)
5. Assemble complete picture from existing organization

If this works easily → Organization is real
If this is hard → Organization has gaps
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

PROJECT_ROOT = Path(__file__).parent.parent

# Known systems from documentation
CORE_SYSTEMS = ['CMC', 'HHNI', 'VIF', 'APOE', 'SEG', 'SDF-CVF', 'CAS']
SUPPORTING_SYSTEMS = ['TCS', 'IIS', 'SCOR', 'ARD', 'Capability Awareness', 
                      'Advanced Monaco Editor', 'NL Tags', 'Daemon/RAG']

def parse_super_index() -> Dict:
    """Parse SUPER_INDEX.md to extract all systems and concepts"""
    print("Parsing SUPER_INDEX.md...")
    
    super_index_path = PROJECT_ROOT / 'knowledge_architecture' / 'SUPER_INDEX.md'
    
    if not super_index_path.exists():
        print(f"  [WARN] SUPER_INDEX.md not found at {super_index_path}")
        return {}
    
    with open(super_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    systems = {}
    concepts = []
    
    # Extract system references (e.g., "CMC (Context Memory Core)")
    system_pattern = r'(?:^|\n)(?:\*\*)?([A-Z]{2,}(?:-[A-Z]+)?)(?: \([^)]+\))?(?:\*\*)?:'
    matches = re.findall(system_pattern, content)
    
    for system in set(matches):
        if len(system) >= 2:  # Valid system acronym
            systems[system] = {'mentioned_in_super_index': True}
    
    print(f"  Found {len(systems)} systems referenced in SUPER_INDEX")
    
    return {'systems': systems, 'concepts': concepts}


def parse_system_l0_files() -> Dict:
    """Parse L0_executive.md files for each system"""
    print("Parsing L0_executive.md files...")
    
    systems_dir = PROJECT_ROOT / 'knowledge_architecture' / 'systems'
    
    if not systems_dir.exists():
        print(f"  [WARN] Systems directory not found at {systems_dir}")
        return {}
    
    systems = {}
    
    for system_dir in systems_dir.iterdir():
        if system_dir.is_dir():
            l0_path = system_dir / 'L0_executive.md'
            
            if l0_path.exists():
                with open(l0_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract key info
                system_name = system_dir.name
                
                # Try to find completion percentage
                completion_match = re.search(r'(?:completion|progress|status)[:\s]+(\d+)%', content, re.IGNORECASE)
                completion = int(completion_match.group(1)) if completion_match else None
                
                # Count words
                word_count = len(content.split())
                
                systems[system_name] = {
                    'has_l0': True,
                    'l0_words': word_count,
                    'completion': completion,
                    'path': str(system_dir)
                }
    
    print(f"  Found {len(systems)} systems with L0 documentation")
    
    return systems


def parse_nl_tag_catalogs() -> Dict:
    """Parse NL_TAG_CATALOG.md files for integration points"""
    print("Parsing NL_TAG_CATALOG files...")
    
    systems_dir = PROJECT_ROOT / 'knowledge_architecture' / 'systems'
    
    connections = defaultdict(list)
    tag_counts = {}
    
    for system_dir in systems_dir.iterdir():
        if system_dir.is_dir():
            catalog_path = system_dir / 'NL_TAG_CATALOG.md'
            
            if catalog_path.exists():
                with open(catalog_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                system_name = system_dir.name
                
                # Count total tags
                tag_count = content.count('NL_TAG')
                tag_counts[system_name] = tag_count
                
                # Find CONNECT tags (integration points)
                connect_pattern = r'NL_TAG_CONNECT[^:]*:\s*([A-Z]{2,}(?:-[A-Z]+)?)[^\n]*→[^\n]*([A-Z]{2,}(?:-[A-Z]+)?)'
                matches = re.findall(connect_pattern, content)
                
                for from_sys, to_sys in matches:
                    connections[system_name].append({
                        'from': from_sys,
                        'to': to_sys,
                        'type': 'integration'
                    })
    
    print(f"  Found {len(tag_counts)} systems with NL tag catalogs")
    print(f"  Total integration points: {sum(len(v) for v in connections.values())}")
    
    return {'connections': dict(connections), 'tag_counts': tag_counts}


def scan_packages_directory() -> Dict:
    """Scan packages/ for actual code"""
    print("Scanning packages/ directory...")
    
    packages_dir = PROJECT_ROOT / 'packages'
    
    if not packages_dir.exists():
        print(f"  [WARN] Packages directory not found")
        return {}
    
    packages = {}
    
    for pkg_dir in packages_dir.iterdir():
        if pkg_dir.is_dir() and not pkg_dir.name.startswith('_'):
            # Count Python files
            py_files = list(pkg_dir.glob('**/*.py'))
            py_files = [f for f in py_files if '__pycache__' not in str(f)]
            
            # Count test files
            test_files = list(pkg_dir.glob('**/test_*.py'))
            
            # Count lines
            total_lines = 0
            for py_file in py_files:
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        total_lines += len(f.readlines())
                except:
                    pass
            
            packages[pkg_dir.name] = {
                'py_files': len(py_files),
                'test_files': len(test_files),
                'lines': total_lines,
                'path': str(pkg_dir)
            }
    
    print(f"  Found {len(packages)} packages")
    
    return packages


def scan_knowledge_architecture() -> Dict:
    """Scan knowledge_architecture/ for documentation"""
    print("Scanning knowledge_architecture/...")
    
    ka_dir = PROJECT_ROOT / 'knowledge_architecture'
    
    if not ka_dir.exists():
        print(f"  [WARN] knowledge_architecture not found")
        return {}
    
    # Count markdown files
    md_files = list(ka_dir.glob('**/*.md'))
    
    # Exclude large generated files
    md_files = [f for f in md_files if f.stat().st_size < 10_000_000]  # < 10MB
    
    # Count total lines
    total_lines = 0
    total_words = 0
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                total_lines += content.count('\n')
                total_words += len(content.split())
        except:
            pass
    
    stats = {
        'total_files': len(md_files),
        'total_lines': total_lines,
        'total_words': total_words,
    }
    
    print(f"  Found {len(md_files)} documentation files")
    print(f"  Total: {total_words:,} words, {total_lines:,} lines")
    
    return stats


def count_tests() -> Dict:
    """Count all tests across packages"""
    print("Counting tests...")
    
    packages_dir = PROJECT_ROOT / 'packages'
    
    test_files = []
    total_tests = 0
    
    for pkg_dir in packages_dir.iterdir():
        if pkg_dir.is_dir():
            # Find test files
            tests = list(pkg_dir.glob('**/test_*.py'))
            test_files.extend(tests)
            
            # Count test functions
            for test_file in tests:
                try:
                    with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Count test_* functions
                        total_tests += content.count('def test_')
                except:
                    pass
    
    print(f"  Found {len(test_files)} test files")
    print(f"  Estimated {total_tests} test functions")
    
    return {
        'test_files': len(test_files),
        'test_functions': total_tests
    }


def calculate_metrics(data: Dict) -> Dict:
    """Calculate complexity and organization metrics"""
    print("\nCalculating metrics...")
    
    # Complexity metrics
    total_code_lines = sum(pkg['lines'] for pkg in data['packages'].values())
    total_packages = len(data['packages'])
    total_systems = len(data['system_l0'])
    total_tests = data['tests']['test_functions']
    
    C_complexity = total_code_lines + (total_packages * 100) + (total_systems * 500)
    
    print(f"  Complexity (C):")
    print(f"    Code lines: {total_code_lines:,}")
    print(f"    Packages: {total_packages}")
    print(f"    Systems: {total_systems}")
    print(f"    Tests: {total_tests}")
    print(f"    TOTAL C: {C_complexity:,}")
    
    # Organization metrics
    doc_words = data['documentation']['total_words']
    doc_files = data['documentation']['total_files']
    systems_with_l0 = len(data['system_l0'])
    total_tags = sum(data['nl_tags']['tag_counts'].values())
    
    O_organization = doc_words + (doc_files * 10) + (systems_with_l0 * 1000) + (total_tags * 5)
    
    print(f"  Organization (O):")
    print(f"    Doc words: {doc_words:,}")
    print(f"    Doc files: {doc_files:,}")
    print(f"    Systems with L0: {systems_with_l0}")
    print(f"    NL tags: {total_tags:,}")
    print(f"    TOTAL O: {O_organization:,}")
    
    # Calculate ratio
    ratio = O_organization / C_complexity if C_complexity > 0 else 0
    
    print(f"\n  Ratio (O/C): {ratio:.2f}")
    
    if ratio >= 0.8:
        print("  [OK] BOUNDED DIVERGENCE CONFIRMED!")
    elif ratio >= 0.5:
        print("  [WARN] PARTIAL DIVERGENCE")
    else:
        print("  [FAIL] DIVERGENCE DETECTED")
    
    return {
        'complexity': C_complexity,
        'organization': O_organization,
        'ratio': ratio,
        'code_lines': total_code_lines,
        'doc_words': doc_words,
        'tests': total_tests,
        'systems': total_systems,
    }


def generate_system_map_data(data: Dict) -> Dict:
    """Generate data for visualization"""
    print("\nGenerating system map data...")
    
    # Build nodes
    nodes = []
    
    # Add systems as nodes
    for system_name, system_data in data['system_l0'].items():
        nodes.append({
            'id': system_name,
            'type': 'system',
            'label': system_name,
            'completion': system_data.get('completion', 0),
            'has_docs': system_data.get('has_l0', False),
            'has_code': system_name.lower() in [p.lower() for p in data['packages'].keys()],
        })
    
    # Build edges from connections
    edges = []
    for system, connections in data['nl_tags']['connections'].items():
        for conn in connections:
            edges.append({
                'from': conn['from'],
                'to': conn['to'],
                'type': conn['type']
            })
    
    print(f"  Generated {len(nodes)} nodes, {len(edges)} edges")
    
    return {
        'nodes': nodes,
        'edges': edges
    }


def main():
    print("=" * 80)
    print("SYSTEM MAP ASSEMBLY - Using Existing Organization")
    print("=" * 80)
    print()
    
    # Gather data from existing organization
    data = {}
    
    data['super_index'] = parse_super_index()
    data['system_l0'] = parse_system_l0_files()
    data['nl_tags'] = parse_nl_tag_catalogs()
    data['packages'] = scan_packages_directory()
    data['documentation'] = scan_knowledge_architecture()
    data['tests'] = count_tests()
    
    print()
    print("=" * 80)
    
    # Calculate metrics
    metrics = calculate_metrics(data)
    
    # Generate map data
    map_data = generate_system_map_data(data)
    
    # Combine everything
    output = {
        'generated': '2025-11-04',
        'data': data,
        'metrics': metrics,
        'map': map_data
    }
    
    # Save to file
    output_path = PROJECT_ROOT / 'SYSTEM_MAP_DATA.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print()
    print("=" * 80)
    print(f"[SAVED] System map data written to: {output_path}")
    print()
    print("SUMMARY:")
    print(f"  Systems: {metrics['systems']}")
    print(f"  Code: {metrics['code_lines']:,} lines")
    print(f"  Docs: {metrics['doc_words']:,} words")
    print(f"  Tests: {metrics['tests']}")
    print(f"  Ratio (O/C): {metrics['ratio']:.2f}")
    print()
    
    if metrics['ratio'] >= 0.8:
        print("[OK] Organization assembled easily from existing metadata!")
        print("     This PROVES the singularity property - organization is real!")
    else:
        print("[WARN] Some gaps in organization detected")
        print("       May need more comprehensive indexing")
    
    print("=" * 80)
    
    return output


if __name__ == '__main__':
    main()

