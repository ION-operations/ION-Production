#!/usr/bin/env python3
"""
Generate Master File Index - Complete hierarchical map of project structure

Categorizes everything clearly:
- CORE: Real code and documentation (what matters)
- GENERATED: Dependencies, build artifacts, caches
- DATA: Databases, logs, semantic nodes
- ARCHIVE: Backups, historical versions
"""

import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent

# File categorization rules
GENERATED_PATTERNS = [
    '__pycache__', 'node_modules', '.pyc', '.pyo',
    'dist', 'build', '.egg-info', 'htmlcov',
    '.pytest_cache', '.mypy_cache', '.map', '.min.js'
]

DATA_PATTERNS = [
    '.db', '.sqlite', '.log', '.jsonl', 'data/',
    'codex/', 'mcp_memory/', 'snapshots/', 'logs/'
]

ARCHIVE_PATTERNS = [
    'archive/', 'backup/', 'historical_versions/',
    'aim-os-minimal', '.git'
]

def categorize_path(path: Path) -> str:
    """Categorize a file/folder"""
    path_str = str(path).lower()
    
    # Check archive first
    if any(p in path_str for p in ARCHIVE_PATTERNS):
        return 'ARCHIVE'
    
    # Check generated
    if any(p in path_str for p in GENERATED_PATTERNS):
        return 'GENERATED'
    
    # Check data
    if any(p in path_str for p in DATA_PATTERNS):
        return 'DATA'
    
    # Everything else is core
    return 'CORE'

def get_file_info(path: Path) -> dict:
    """Get file metadata"""
    try:
        stat = path.stat()
        size = stat.st_size
        
        # Count lines for text files
        lines = 0
        if path.suffix in ['.py', '.ts', '.tsx', '.js', '.jsx', '.md', '.txt', '.yaml', '.yml', '.json']:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
            except:
                pass
        
        return {
            'size': size,
            'lines': lines,
            'type': path.suffix or 'DIR'
        }
    except:
        return {'size': 0, 'lines': 0, 'type': 'ERROR'}

def build_tree(root_path: Path, max_depth: int = 4, current_depth: int = 0) -> dict:
    """Build hierarchical tree structure"""
    
    if current_depth >= max_depth:
        return None
    
    tree = {
        'name': root_path.name or str(root_path),
        'path': str(root_path.relative_to(PROJECT_ROOT)),
        'is_dir': root_path.is_dir(),
        'category': categorize_path(root_path),
        'children': [],
        'stats': {'files': 0, 'dirs': 0, 'size': 0, 'lines': 0}
    }
    
    if root_path.is_dir():
        try:
            children = []
            for item in sorted(root_path.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
                child_tree = build_tree(item, max_depth, current_depth + 1)
                if child_tree:
                    children.append(child_tree)
                    # Aggregate stats
                    tree['stats']['files'] += child_tree['stats']['files']
                    tree['stats']['dirs'] += child_tree['stats']['dirs']
                    tree['stats']['size'] += child_tree['stats']['size']
                    tree['stats']['lines'] += child_tree['stats']['lines']
            
            tree['children'] = children
            tree['stats']['dirs'] += 1
        except PermissionError:
            pass
    else:
        info = get_file_info(root_path)
        tree['stats']['files'] = 1
        tree['stats']['size'] = info['size']
        tree['stats']['lines'] = info['lines']
        tree['file_type'] = info['type']
    
    return tree

def format_size(size: int) -> str:
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}TB"

def print_tree(tree: dict, indent: int = 0, show_category: bool = True, file=None):
    """Print tree structure with proper formatting"""
    
    # Indentation
    prefix = "  " * indent
    
    # Icon
    if tree['is_dir']:
        icon = "[DIR]" if tree['category'] == 'CORE' else \
               "[DATA]" if tree['category'] == 'DATA' else \
               "[GEN]" if tree['category'] == 'GENERATED' else \
               "[ARC]"
    else:
        icon = "[FILE]"
    
    # Name and stats
    name = tree['name']
    stats = tree['stats']
    
    if tree['is_dir']:
        info = f"({stats['files']:,} files, {stats['dirs']:,} dirs, {format_size(stats['size'])}"
        if stats['lines'] > 0:
            info += f", {stats['lines']:,} lines"
        info += ")"
    else:
        info = f"({format_size(stats['size'])}"
        if stats['lines'] > 0:
            info += f", {stats['lines']:,} lines"
        info += ")"
    
    # Category tag
    category_tag = f" [{tree['category']}]" if show_category and indent < 2 else ""
    
    line = f"{prefix}{icon} {name} {info}{category_tag}\n"
    file.write(line)
    
    # Print children (limit depth)
    if tree['is_dir'] and tree['children'] and indent < 3:
        for child in tree['children']:
            print_tree(child, indent + 1, show_category, file)

def generate_category_summary(tree: dict) -> dict:
    """Generate summary by category"""
    categories = defaultdict(lambda: {'files': 0, 'dirs': 0, 'size': 0, 'lines': 0})
    
    def traverse(node):
        cat = node['category']
        if node['is_dir']:
            categories[cat]['dirs'] += 1
            for child in node['children']:
                traverse(child)
        else:
            categories[cat]['files'] += 1
            categories[cat]['size'] += node['stats']['size']
            categories[cat]['lines'] += node['stats']['lines']
    
    traverse(tree)
    return dict(categories)

def main():
    print("=" * 80)
    print("MASTER FILE INDEX GENERATOR")
    print("=" * 80)
    print()
    print("Building hierarchical tree...")
    
    # Build tree
    tree = build_tree(PROJECT_ROOT, max_depth=4)
    
    # Generate category summary
    categories = generate_category_summary(tree)
    
    print(f"[OK] Complete")
    print()
    
    # Write to file
    output_path = PROJECT_ROOT / 'MASTER_FILE_INDEX.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# AIM-OS Master File Index\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("---\n\n")
        
        # Category Summary
        f.write("## 📊 Summary by Category\n\n")
        
        for category in ['CORE', 'DATA', 'GENERATED', 'ARCHIVE']:
            if category in categories:
                stats = categories[category]
                f.write(f"### {category}\n")
                f.write(f"- Files: {stats['files']:,}\n")
                f.write(f"- Directories: {stats['dirs']:,}\n")
                f.write(f"- Total Size: {format_size(stats['size'])}\n")
                if stats['lines'] > 0:
                    f.write(f"- Total Lines: {stats['lines']:,}\n")
                f.write("\n")
        
        f.write("---\n\n")
        
        # Full tree
        f.write("## 🗂️ Complete File Hierarchy\n\n")
        f.write("**Legend:**\n")
        f.write("- 📁 CORE - Real code and documentation (what matters)\n")
        f.write("- 🗂️ DATA - Databases, logs, semantic nodes\n")
        f.write("- 📦 GENERATED - Dependencies, build artifacts, caches\n")
        f.write("- 📚 ARCHIVE - Backups, historical versions\n")
        f.write("\n---\n\n")
        
        print_tree(tree, file=f)
    
    print(f"[SAVED] Master index written to: {output_path}")
    print()
    
    # Print summary to console
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for category in ['CORE', 'DATA', 'GENERATED', 'ARCHIVE']:
        if category in categories:
            stats = categories[category]
            print(f"\n{category}:")
            print(f"  Files:       {stats['files']:>10,}")
            print(f"  Directories: {stats['dirs']:>10,}")
            print(f"  Size:        {format_size(stats['size']):>10}")
            if stats['lines'] > 0:
                print(f"  Lines:       {stats['lines']:>10,}")
    
    print()
    print("=" * 80)
    print(f"\n[OK] Complete index written to: {output_path}")
    print()

if __name__ == '__main__':
    main()

