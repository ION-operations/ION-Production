#!/usr/bin/env python3
"""
Comprehensive File Inventory Script
Collects complete metadata about every file in AIM-OS project
Part of Singularity Property validation - proving O(organization) = O(complexity)

Usage:
    python scripts/comprehensive_inventory.py [--output FILE]
"""

import os
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Ignore patterns - exclude data, dependencies, backups, etc.
IGNORE_PATTERNS = [
    '__pycache__',
    'node_modules',
    '.git',
    'htmlcov',
    '.pytest_cache',
    '.mypy_cache',
    '*.pyc',
    '*.pyo',
    '*.egg-info',
    'dist',
    'build',
    # Data directories
    'data/',
    'mcp_memory/',
    'snapshots/',
    'codex/',
    # Dependencies
    'dependencies/',
    'vendor/',
    'lib/',
    # Backups
    'backup/',
    'backups/',
    '.backup/',
    'archive/',
    'archives/',
    'historical_versions/',
    # Build artifacts
    '.next/',
    '.nuxt/',
    '.cache/',
    'coverage/',
    '.coverage',
    # IDE/Editor
    '.vscode/',
    '.idea/',
    '.cursor/',
    # OS
    '.DS_Store',
    'Thumbs.db',
    # Temporary
    'tmp/',
    'temp/',
    '.tmp/',
    '.temp/',
]

# System classification keywords
SYSTEM_KEYWORDS = {
    'CMC': ['cmc', 'memory_store', 'bitemporal', 'atom'],
    'HHNI': ['hhni', 'index', 'retrieval', 'dvns'],
    'VIF': ['vif', 'confidence', 'witness', 'calibration'],
    'APOE': ['apoe', 'orchestration', 'acl', 'execution'],
    'SEG': ['seg', 'knowledge', 'graph', 'synthesis'],
    'SDF-CVF': ['sdfcvf', 'quartet', 'parity', 'quality'],
    'CAS': ['cognitive_analysis', 'cas', 'meta_cognitive'],
    'TCS': ['timeline_context', 'tcs'],
    'IIS': ['intuitive_intelligence', 'iis'],
    'SCOR': ['scor', 'safety', 'reliability'],
    'ARD': ['autonomous_research_dream', 'ard'],
}

# File type classifications
FILE_TYPES = {
    # Code
    '.py': 'code_python',
    '.ts': 'code_typescript',
    '.tsx': 'code_typescript_react',
    '.js': 'code_javascript',
    '.jsx': 'code_javascript_react',
    '.rs': 'code_rust',
    '.go': 'code_go',
    '.cpp': 'code_cpp',
    '.c': 'code_c',
    '.h': 'code_header',
    
    # Documentation
    '.md': 'doc_markdown',
    '.txt': 'doc_text',
    '.rst': 'doc_restructured',
    '.pdf': 'doc_pdf',
    '.docx': 'doc_word',
    
    # Configuration
    '.json': 'config_json',
    '.yaml': 'config_yaml',
    '.yml': 'config_yaml',
    '.toml': 'config_toml',
    '.ini': 'config_ini',
    '.env': 'config_env',
    
    # Data
    '.db': 'data_database',
    '.sqlite': 'data_database',
    '.log': 'data_log',
    '.jsonl': 'data_jsonlines',
    '.csv': 'data_csv',
    
    # Build/Package
    '.lock': 'build_lock',
    'package.json': 'build_package',
    'requirements.txt': 'build_requirements',
    'Dockerfile': 'build_docker',
    '.sh': 'build_script',
    '.bat': 'build_script',
    '.ps1': 'build_script',
}


def should_ignore(path: Path) -> bool:
    """Check if path should be ignored"""
    path_str = str(path)
    for pattern in IGNORE_PATTERNS:
        if pattern in path_str:
            return True
    return False


def classify_file_type(path: Path) -> str:
    """Classify file by extension"""
    suffix = path.suffix.lower()
    name = path.name.lower()
    
    # Check special names
    for special_name, file_type in FILE_TYPES.items():
        if '.' not in special_name and name == special_name:
            return file_type
    
    # Check extension
    return FILE_TYPES.get(suffix, 'unknown')


def classify_system(path: Path) -> Optional[str]:
    """Determine which system a file belongs to"""
    path_str = str(path).lower()
    
    # Check each system's keywords
    for system, keywords in SYSTEM_KEYWORDS.items():
        for keyword in keywords:
            if keyword in path_str:
                return system
    
    return None


def classify_role(path: Path) -> str:
    """Classify file role (core, supporting, infrastructure, etc.)"""
    path_str = str(path).lower()
    
    # Core systems
    if 'packages/cmc' in path_str or 'packages/hhni' in path_str or \
       'packages/vif' in path_str or 'packages/apoe' in path_str or \
       'packages/seg' in path_str or 'packages/sdfcvf' in path_str:
        return 'core'
    
    # Supporting systems
    if 'packages/' in path_str:
        return 'supporting'
    
    # Infrastructure
    if 'knowledge_architecture' in path_str or 'coordination' in path_str or \
       'scripts' in path_str or '.cursor' in path_str:
        return 'infrastructure'
    
    # Data
    if 'codex' in path_str or 'mcp_memory' in path_str or 'snapshots' in path_str or \
       '.db' in path_str or '.log' in path_str:
        return 'data'
    
    # Archive
    if 'archive' in path_str or 'backup' in path_str or 'historical_versions' in path_str:
        return 'archive'
    
    # Experimental
    if 'ideas' in path_str or 'testing' in path_str or 'experiment' in path_str:
        return 'experimental'
    
    return 'unassigned'


def count_lines(path: Path) -> Tuple[int, int, int, int]:
    """Count lines: total, code, comments, blank
    Returns: (total, code, comments, blank)
    """
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        total = len(lines)
        blank = sum(1 for line in lines if not line.strip())
        
        # Detect comments based on file type
        suffix = path.suffix.lower()
        comment_count = 0
        
        if suffix in ['.py']:
            # Python: # and """..."""
            in_multiline = False
            for line in lines:
                stripped = line.strip()
                if '"""' in stripped or "'''" in stripped:
                    in_multiline = not in_multiline
                    comment_count += 1
                elif in_multiline or stripped.startswith('#'):
                    comment_count += 1
        
        elif suffix in ['.ts', '.tsx', '.js', '.jsx']:
            # JavaScript/TypeScript: // and /*...*/
            in_multiline = False
            for line in lines:
                stripped = line.strip()
                if '/*' in stripped:
                    in_multiline = True
                if in_multiline:
                    comment_count += 1
                elif stripped.startswith('//'):
                    comment_count += 1
                if '*/' in stripped:
                    in_multiline = False
        
        elif suffix == '.md':
            # Markdown: all lines are "documentation"
            code_count = 0
            comment_count = 0
        
        code = total - blank - comment_count
        
        return (total, max(0, code), comment_count, blank)
    
    except Exception as e:
        return (0, 0, 0, 0)


def extract_nl_tags(path: Path) -> int:
    """Count NL_TAG occurrences in file"""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return content.count('# NL_TAG')
    except:
        return 0


def extract_dependencies(path: Path) -> List[str]:
    """Extract dependencies (imports, requires, etc.)"""
    deps = []
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        suffix = path.suffix.lower()
        
        if suffix == '.py':
            # Python imports
            imports = re.findall(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE)
            deps.extend(imports)
        
        elif suffix in ['.ts', '.tsx', '.js', '.jsx']:
            # TypeScript/JavaScript imports
            imports = re.findall(r'from\s+["\']([^"\']+)["\']', content)
            deps.extend(imports)
    
    except:
        pass
    
    return list(set(deps))  # Unique


def get_git_info(path: Path) -> Dict:
    """Get git information for file"""
    try:
        # Get creation date (first commit)
        result = subprocess.run(
            ['git', 'log', '--follow', '--format=%ai', '--', str(path)],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        dates = result.stdout.strip().split('\n')
        created = dates[-1] if dates and dates[-1] else None
        
        # Get last modification date
        modified = dates[0] if dates and dates[0] else None
        
        # Count commits
        result = subprocess.run(
            ['git', 'log', '--oneline', '--follow', '--', str(path)],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        commit_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        return {
            'created': created,
            'last_modified': modified,
            'commit_count': commit_count
        }
    except:
        return {
            'created': None,
            'last_modified': None,
            'commit_count': 0
        }


def scan_file(path: Path) -> Dict:
    """Collect all metadata for a single file"""
    rel_path = path.relative_to(PROJECT_ROOT)
    
    # Basic info
    info = {
        'path': str(rel_path),
        'name': path.name,
        'extension': path.suffix,
        'size_bytes': path.stat().st_size if path.exists() else 0,
    }
    
    # Classification
    info['type'] = classify_file_type(path)
    info['system'] = classify_system(path)
    info['role'] = classify_role(path)
    
    # Line counts
    total, code, comments, blank = count_lines(path)
    info['lines_total'] = total
    info['lines_code'] = code
    info['lines_comments'] = comments
    info['lines_blank'] = blank
    
    # Additional metadata
    info['nl_tags'] = extract_nl_tags(path)
    info['dependencies'] = extract_dependencies(path)
    
    # Git info
    info['git'] = get_git_info(path)
    
    return info


def scan_directory(root: Path) -> List[Dict]:
    """Recursively scan directory and collect all file metadata"""
    files = []
    total_files = 0
    
    print(f"Scanning {root}...")
    
    for path in root.rglob('*'):
        if path.is_file() and not should_ignore(path):
            total_files += 1
            if total_files % 100 == 0:
                print(f"  Processed {total_files} files...")
            
            try:
                file_info = scan_file(path)
                files.append(file_info)
            except Exception as e:
                print(f"  Error processing {path}: {e}")
    
    print(f"Completed scan: {total_files} files processed")
    return files


def calculate_totals(files: List[Dict]) -> Dict:
    """Calculate aggregate totals"""
    totals = {
        'total_files': len(files),
        'total_size_bytes': sum(f['size_bytes'] for f in files),
        'total_lines': sum(f['lines_total'] for f in files),
        'total_lines_code': sum(f['lines_code'] for f in files),
        'total_lines_comments': sum(f['lines_comments'] for f in files),
        'total_lines_blank': sum(f['lines_blank'] for f in files),
        'total_nl_tags': sum(f['nl_tags'] for f in files),
    }
    
    return totals


def calculate_by_category(files: List[Dict], category: str) -> Dict:
    """Calculate metrics grouped by category (system, role, type)"""
    grouped = defaultdict(lambda: {
        'files': 0,
        'size_bytes': 0,
        'lines_total': 0,
        'lines_code': 0,
        'lines_comments': 0,
        'lines_blank': 0,
        'nl_tags': 0,
    })
    
    for f in files:
        key = f.get(category, 'unknown')
        if key:
            grouped[key]['files'] += 1
            grouped[key]['size_bytes'] += f['size_bytes']
            grouped[key]['lines_total'] += f['lines_total']
            grouped[key]['lines_code'] += f['lines_code']
            grouped[key]['lines_comments'] += f['lines_comments']
            grouped[key]['lines_blank'] += f['lines_blank']
            grouped[key]['nl_tags'] += f['nl_tags']
    
    return dict(grouped)


def generate_inventory(output_file: str = 'COMPREHENSIVE_FILE_INVENTORY.json'):
    """Main function to generate complete inventory"""
    print("=" * 80)
    print("AIM-OS COMPREHENSIVE FILE INVENTORY")
    print("=" * 80)
    print()
    
    # Scan all files
    print("Phase 1: Scanning files...")
    files = scan_directory(PROJECT_ROOT)
    print(f"✓ Found {len(files)} files")
    print()
    
    # Calculate totals
    print("Phase 2: Calculating totals...")
    totals = calculate_totals(files)
    print(f"✓ Total lines: {totals['total_lines']:,}")
    print(f"  - Code: {totals['total_lines_code']:,}")
    print(f"  - Comments: {totals['total_lines_comments']:,}")
    print(f"  - Blank: {totals['total_lines_blank']:,}")
    print(f"✓ Total size: {totals['total_size_bytes']:,} bytes ({totals['total_size_bytes']/1024/1024:.1f} MB)")
    print(f"✓ NL tags: {totals['total_nl_tags']:,}")
    print()
    
    # Calculate by categories
    print("Phase 3: Grouping by categories...")
    by_system = calculate_by_category(files, 'system')
    by_role = calculate_by_category(files, 'role')
    by_type = calculate_by_category(files, 'type')
    print(f"✓ Systems: {len(by_system)}")
    print(f"✓ Roles: {len(by_role)}")
    print(f"✓ Types: {len(by_type)}")
    print()
    
    # Build output structure
    output = {
        'generated': datetime.now().isoformat(),
        'project_root': str(PROJECT_ROOT),
        'totals': totals,
        'by_system': by_system,
        'by_role': by_role,
        'by_type': by_type,
        'files': files,
    }
    
    # Write to file
    print(f"Phase 4: Writing to {output_file}...")
    output_path = PROJECT_ROOT / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"✓ Written to {output_path}")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files scanned: {len(files):,}")
    print(f"Total lines: {totals['total_lines']:,}")
    print(f"  Code: {totals['total_lines_code']:,} ({totals['total_lines_code']/totals['total_lines']*100:.1f}%)")
    print(f"  Docs: {totals['total_lines_comments']:,} ({totals['total_lines_comments']/totals['total_lines']*100:.1f}%)")
    print()
    print("Top 5 systems by LOC:")
    sorted_systems = sorted(by_system.items(), key=lambda x: x[1]['lines_code'], reverse=True)
    for i, (system, metrics) in enumerate(sorted_systems[:5], 1):
        if system and system != 'None':
            print(f"  {i}. {system}: {metrics['lines_code']:,} lines")
    print()
    print("By role:")
    for role, metrics in sorted(by_role.items(), key=lambda x: x[1]['lines_total'], reverse=True):
        print(f"  {role}: {metrics['files']:,} files, {metrics['lines_total']:,} lines")
    print()
    print(f"Output written to: {output_path}")
    print("=" * 80)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate comprehensive file inventory')
    parser.add_argument('--output', default='COMPREHENSIVE_FILE_INVENTORY.json',
                       help='Output JSON file path')
    
    args = parser.parse_args()
    generate_inventory(args.output)

