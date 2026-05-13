#!/usr/bin/env python3
"""
Comprehensive codebase analysis tool.
Counts lines of code, files, and organizes by category.
Excludes third-party dependencies (node_modules, __pycache__, etc.).
"""

import os
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set

# Directories and patterns to exclude
EXCLUDE_DIRS = {
    'node_modules',
    '__pycache__',
    '.git',
    '.vscode',
    '.idea',
    'venv',
    'env',
    '.venv',
    'dist',
    'build',
    'coverage',
    '.pytest_cache',
    '*.egg-info',
    'cmc_service.egg-info',
    'data',  # CMC service data directory
    'quarantine',  # Codex quarantine
    'bench_data',  # Benchmark data
    'Documentation',  # Not our work - external documentation
    'Documentation_Consolidated',  # Not our work - external documentation
    'mcp_memory',  # Data storage
    'snapshots',  # Backup snapshots
    'backup',  # Backups
    'backups',  # Backups
    'archive',  # Archived content
    'codex',  # Data storage
    'codex_workspace',  # Data storage
    'test_mcp_memory',  # Test data
    'test_mcp_configs',  # Test configs
    'aim-os-minimal',  # Duplicate/minimal build
}

# File extensions to categorize
CODE_EXTENSIONS = {
    '.py': 'Python',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript React',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript React',
    '.java': 'Java',
    '.cpp': 'C++',
    '.c': 'C',
    '.cs': 'C#',
    '.go': 'Go',
    '.rs': 'Rust',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
}

DOC_EXTENSIONS = {
    '.md': 'Markdown',
    '.txt': 'Text',
    '.rst': 'reStructuredText',
    '.docx': 'Word',
}

CONFIG_EXTENSIONS = {
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.toml': 'TOML',
    '.xml': 'XML',
    '.ini': 'INI',
    '.cfg': 'Config',
    '.conf': 'Config',
    '.properties': 'Properties',
}

DATA_EXTENSIONS = {
    '.db': 'SQLite Database',
    '.sqlite': 'SQLite Database',
    '.csv': 'CSV',
    '.json': 'JSON Data',
}

BUILD_EXTENSIONS = {
    '.lock': 'Lock File',
    'package-lock.json': 'NPM Lock',
    'pnpm-lock.yaml': 'PNPM Lock',
    'yarn.lock': 'Yarn Lock',
}

OTHER_EXTENSIONS = {
    '.sh': 'Shell Script',
    '.bat': 'Batch Script',
    '.ps1': 'PowerShell',
    '.sql': 'SQL',
    '.acl': 'ACL',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.html': 'HTML',
    '.htm': 'HTML',
}

# Directory categories
DIRECTORY_CATEGORIES = {
    'packages': 'Core Packages (Production Code)',
    'knowledge_architecture': 'Knowledge Architecture (Documentation & Plans)',
    'scripts': 'Utility Scripts',
    'daemon_rag_system': 'Daemon RAG System',
    'coordination': 'Coordination Files',
    'goals': 'Goal Planning',
    'plans': 'Project Plans',
    'Testing': 'Test Artifacts & Documentation',
    'archive': 'Archived Files',
    'benchmarks': 'Benchmark Code',
    'bootloaders': 'Bootloader Configs',
    'codex': 'Codex System (CMC Integration)',
    'codex_workspace': 'Codex Workspace',
    'audit': 'Audit System',
    'audits': 'Audit Reports',
    'backups': 'Backups',
    'data': 'Data Files',
    'deploy': 'Deployment Configs',
    'deployment': 'Deployment Files',
    'docs': 'Documentation',
    'Documentation': 'Legacy Documentation',
    'evidence': 'Evidence Files',
    'examples': 'Example Code',
    'ideas': 'Ideas & Notes',
    'legacy_docs': 'Legacy Documentation',
    'logs': 'Log Files',
    'mcp_memory': 'MCP Memory Storage',
    'mcp-aether': 'MCP Aether Integration',
    'projects': 'Project Files',
    'reports': 'Reports',
    'runs': 'Run Artifacts',
    'schemas': 'Schema Definitions',
    'snapshots': 'Snapshots',
    'test_mcp_configs': 'MCP Test Configs',
    'test_mcp_memory': 'MCP Test Memory',
    'timeline_go appeals': 'Timeline Goals',
    'ui': 'UI Components',
    'active_work': 'Active Work',
    'analysis': 'Analysis Files',
    'achievements': 'Achievement Records',
}


def should_exclude(path: Path) -> bool:
    """Check if a path should be excluded from analysis."""
    parts = path.parts
    
    # Check for excluded directory names
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
        if part.startswith('.') and part != '.':
            return True
        if part.startswith('__') and part.endswith('__'):
            return True
    
    # Check for specific patterns
    if 'node_modules' in parts:
        return True
    if '__pycache__' in parts:
        return True
    if any(part.startswith('.') for part in parts[1:]):
        return True
    
    return False


def categorize_file(file_path: Path) -> Tuple[str, str]:
    """
    Categorize a file by extension.
    Returns (category, extension_type).
    """
    ext = file_path.suffix.lower()
    name = file_path.name.lower()
    
    # Check build files first
    if name in ['package-lock.json', 'pnpm-lock.yaml', 'yarn.lock']:
        return ('build', 'Lock File')
    if ext in BUILD_EXTENSIONS:
        return ('build', BUILD_EXTENSIONS[ext])
    
    # Check other categories
    if ext in CODE_EXTENSIONS:
        return ('code', CODE_EXTENSIONS[ext])
    if ext in DOC_EXTENSIONS:
        return ('docs', DOC_EXTENSIONS[ext])
    if ext in CONFIG_EXTENSIONS:
        return ('config', CONFIG_EXTENSIONS[ext])
    if ext in DATA_EXTENSIONS:
        return ('data', DATA_EXTENSIONS[ext])
    if ext in OTHER_EXTENSIONS:
        return ('other', OTHER_EXTENSIONS[ext])
    
    return ('unknown', ext or 'no extension')


def get_directory_category(path: Path) -> str:
    """Get the category for a directory path."""
    parts = path.parts
    
    # Check root-level directories
    if len(parts) > 0:
        root_dir = parts[0]
        if root_dir in DIRECTORY_CATEGORIES:
            return DIRECTORY_CATEGORIES[root_dir]
    
    # Check for specific patterns
    if 'knowledge_architecture' in parts:
        idx = parts.index('knowledge_architecture')
        subdir = parts[idx + 1] if idx + 1 < len(parts) else None
        if subdir == 'systems':
            if len(parts) > idx + 2:
                system_name = parts[idx + 2]
                return f'Knowledge Architecture - System: {system_name}'
        return 'Knowledge Architecture'
    
    if 'packages' in parts:
        idx = parts.index('packages')
        if len(parts) > idx + 1:
            package_name = parts[idx + 1]
            return f'Package: {package_name}'
        return 'Packages'
    
    return 'Other'


def count_lines(file_path: Path) -> int:
    """Count lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def analyze_codebase(root_dir: Path) -> Dict:
    """Analyze the entire codebase."""
    stats = {
        'total_files': 0,
        'total_lines': 0,
        'by_category': defaultdict(lambda: {'files': 0, 'lines': 0, 'extensions': defaultdict(lambda: {'files': 0, 'lines': 0})}),
        'by_directory': defaultdict(lambda: {'files': 0, 'lines': 0}),
        'by_file_type': defaultdict(lambda: {'files': 0, 'lines': 0}),
        'file_list': defaultdict(list),
    }
    
    print(f"Analyzing codebase in {root_dir}...")
    
    for root, dirs, files in os.walk(root_dir):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
        
        root_path = Path(root)
        
        for file in files:
            file_path = root_path / file
            
            # Skip excluded files
            if should_exclude(file_path):
                continue
            
            # Skip hidden files
            if file.startswith('.'):
                continue
            
            # Categorize file
            category, file_type = categorize_file(file_path)
            dir_category = get_directory_category(file_path.relative_to(root_dir))
            
            # Count lines
            lines = count_lines(file_path)
            
            # Update stats
            stats['total_files'] += 1
            stats['total_lines'] += lines
            
            stats['by_category'][category]['files'] += 1
            stats['by_category'][category]['lines'] += lines
            stats['by_category'][category]['extensions'][file_type]['files'] += 1
            stats['by_category'][category]['extensions'][file_type]['lines'] += lines
            
            stats['by_directory'][dir_category]['files'] += 1
            stats['by_directory'][dir_category]['lines'] += lines
            
            stats['by_file_type'][file_type]['files'] += 1
            stats['by_file_type'][file_type]['lines'] += lines
            
            # Store file info for detailed reporting
            stats['file_list'][category].append({
                'path': str(file_path.relative_to(root_dir)),
                'lines': lines,
                'type': file_type,
                'directory': dir_category,
            })
    
    return stats


def format_number(num: int) -> str:
    """Format number with commas."""
    return f"{num:,}"


def print_report(stats: Dict, output_file: str = None):
    """Print comprehensive report."""
    report_lines = []
    
    def add_line(text: str = ''):
        report_lines.append(text)
        try:
            print(text)
        except UnicodeEncodeError:
            # Fallback for Windows console encoding issues
            print(text.encode('ascii', 'replace').decode('ascii'))
    
    add_line("=" * 80)
    add_line("AIM-OS CODEBASE ANALYSIS REPORT")
    add_line("=" * 80)
    add_line()
    
    # Summary
    add_line("SUMMARY")
    add_line("-" * 80)
    add_line(f"Total Files: {format_number(stats['total_files'])}")
    add_line(f"Total Lines: {format_number(stats['total_lines'])}")
    add_line()
    
    # By Category
    add_line("BY CATEGORY")
    add_line("-" * 80)
    for category in sorted(stats['by_category'].keys()):
        cat_stats = stats['by_category'][category]
        files = cat_stats['files']
        lines = cat_stats['lines']
        percentage = (lines / stats['total_lines'] * 100) if stats['total_lines'] > 0 else 0
        add_line(f"{category.upper():<20} {format_number(files):>8} files | {format_number(lines):>12} lines ({percentage:>5.1f}%)")
        
        # Show top extensions in this category
        extensions = sorted(cat_stats['extensions'].items(), key=lambda x: x[1]['lines'], reverse=True)[:5]
        for ext_type, ext_stats in extensions:
            add_line(f"    - {ext_type:<18} {format_number(ext_stats['files']):>6} files | {format_number(ext_stats['lines']):>12} lines")
    add_line()
    
    # By Directory (Top 20)
    add_line("BY DIRECTORY (Top 20)")
    add_line("-" * 80)
    sorted_dirs = sorted(stats['by_directory'].items(), key=lambda x: x[1]['lines'], reverse=True)[:20]
    for dir_name, dir_stats in sorted_dirs:
        files = dir_stats['files']
        lines = dir_stats['lines']
        percentage = (lines / stats['total_lines'] * 100) if stats['total_lines'] > 0 else 0
        add_line(f"{dir_name:<50} {format_number(files):>6} files | {format_number(lines):>12} lines ({percentage:>5.1f}%)")
    add_line()
    
    # By File Type (Top 15)
    add_line("BY FILE TYPE (Top 15)")
    add_line("-" * 80)
    sorted_types = sorted(stats['by_file_type'].items(), key=lambda x: x[1]['lines'], reverse=True)[:15]
    for file_type, type_stats in sorted_types:
        files = type_stats['files']
        lines = type_stats['lines']
        percentage = (lines / stats['total_lines'] * 100) if stats['total_lines'] > 0 else 0
        add_line(f"{file_type:<30} {format_number(files):>6} files | {format_number(lines):>12} lines ({percentage:>5.1f}%)")
    add_line()
    
    # Detailed breakdown
    add_line("DETAILED BREAKDOWN")
    add_line("-" * 80)
    
    for category in ['code', 'docs', 'config', 'other', 'data', 'build']:
        if category not in stats['by_category']:
            continue
        
        cat_files = stats['file_list'][category]
        if not cat_files:
            continue
        
        add_line()
        add_line(f"{category.upper()} FILES:")
        
        # Group by directory
        by_dir = defaultdict(list)
        for file_info in cat_files:
            by_dir[file_info['directory']].append(file_info)
        
        # Show top directories
        sorted_dir_files = sorted(by_dir.items(), key=lambda x: sum(f['lines'] for f in x[1]), reverse=True)[:10]
        for dir_name, files in sorted_dir_files:
            total_lines = sum(f['lines'] for f in files)
            add_line(f"  {dir_name}: {len(files)} files, {format_number(total_lines)} lines")
    
    add_line()
    add_line("=" * 80)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        print(f"\nReport saved to {output_file}")
        
        # Also save JSON data
        json_file = output_file.replace('.txt', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, default=str)
        print(f"Data saved to {json_file}")


def main():
    """Main entry point."""
    root_dir = Path(__file__).parent.parent
    stats = analyze_codebase(root_dir)
    
    output_file = root_dir / 'CODEBASE_ANALYSIS_REPORT.txt'
    print_report(stats, str(output_file))


if __name__ == '__main__':
    main()

