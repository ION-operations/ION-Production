#!/usr/bin/env python3
"""Comprehensive Project Analysis Script"""
import os
from collections import defaultdict
from pathlib import Path

def analyze_project():
    """Analyze the AIM-OS project structure"""
    exclude_dirs = {'node_modules', '.git', '__pycache__', '.pytest_cache', 'dist', 'build', '.venv', 'venv'}
    exclude_patterns = {'package-lock.json', 'yarn.lock', 'poetry.lock', '.pyc'}
    
    stats = {
        'code': {'files': 0, 'lines': 0, 'extensions': defaultdict(lambda: {'files': 0, 'lines': 0})},
        'docs': {'files': 0, 'lines': 0, 'extensions': defaultdict(lambda: {'files': 0, 'lines': 0})},
        'data': {'files': 0, 'lines': 0, 'extensions': defaultdict(lambda: {'files': 0, 'lines': 0})},
        'folders': {'total': 0, 'key_folders': defaultdict(int)}
    }
    
    code_extensions = {'.py', '.ts', '.tsx', '.js', '.jsx'}
    doc_extensions = {'.md', '.yaml', '.yml', '.txt'}
    data_extensions = {'.json'}
    
    key_folders = {
        'packages', 'knowledge_architecture', 'Documentation', 
        'goals', 'analysis', 'scripts', 'tests'
    }
    
    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        if any(excluded in root for excluded in exclude_dirs):
            continue
            
        # Count folder
        stats['folders']['total'] += 1
        for key_folder in key_folders:
            if key_folder in root:
                stats['folders']['key_folders'][key_folder] += 1
        
        for file in files:
            # Skip excluded files
            if any(pattern in file for pattern in exclude_patterns):
                continue
                
            file_path = os.path.join(root, file)
            ext = Path(file).suffix.lower()
            
            # Count lines
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
            except:
                lines = 0
            
            # Categorize file
            if ext in code_extensions:
                stats['code']['files'] += 1
                stats['code']['lines'] += lines
                stats['code']['extensions'][ext]['files'] += 1
                stats['code']['extensions'][ext]['lines'] += lines
            elif ext in doc_extensions:
                stats['docs']['files'] += 1
                stats['docs']['lines'] += lines
                stats['docs']['extensions'][ext]['files'] += 1
                stats['docs']['extensions'][ext]['lines'] += lines
            elif ext in data_extensions:
                stats['data']['files'] += 1
                stats['data']['lines'] += lines
                stats['data']['extensions'][ext]['files'] += 1
                stats['data']['extensions'][ext]['lines'] += lines
    
    return stats

def print_report(stats):
    """Print formatted report"""
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 80)
    print("AIM-OS PROJECT ANALYSIS")
    print("=" * 80)
    
    print("\nOVERVIEW:")
    total_files = stats['code']['files'] + stats['docs']['files'] + stats['data']['files']
    total_lines = stats['code']['lines'] + stats['docs']['lines'] + stats['data']['lines']
    print(f"  Total Files: {total_files:,}")
    print(f"  Total Lines: {total_lines:,}")
    print(f"  Total Folders: {stats['folders']['total']:,}")
    
    print("\nCODE ANALYSIS:")
    print(f"  Code Files: {stats['code']['files']:,}")
    print(f"  Code Lines: {stats['code']['lines']:,}")
    print("  By Extension:")
    for ext, data in sorted(stats['code']['extensions'].items()):
        print(f"    {ext}: {data['files']:,} files, {data['lines']:,} lines")
    
    print("\nDOCUMENTATION ANALYSIS:")
    print(f"  Doc Files: {stats['docs']['files']:,}")
    print(f"  Doc Lines: {stats['docs']['lines']:,}")
    print("  By Extension:")
    for ext, data in sorted(stats['docs']['extensions'].items()):
        print(f"    {ext}: {data['files']:,} files, {data['lines']:,} lines")
    
    print("\nDATA ANALYSIS:")
    print(f"  Data Files: {stats['data']['files']:,}")
    print(f"  Data Lines: {stats['data']['lines']:,}")
    print("  By Extension:")
    for ext, data in sorted(stats['data']['extensions'].items()):
        print(f"    {ext}: {data['files']:,} files, {data['lines']:,} lines")
    
    print("\nKEY FOLDERS:")
    for folder, count in sorted(stats['folders']['key_folders'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {folder}/: {count:,} folders")
    
    print("\n" + "=" * 80)
    
    # Ratio analysis
    print("\nRATIOS:")
    print(f"  Code:Documentation = 1:{stats['docs']['lines']/stats['code']['lines']:.2f}")
    print(f"  Code Percentage: {stats['code']['lines']/total_lines*100:.1f}%")
    print(f"  Documentation Percentage: {stats['docs']['lines']/total_lines*100:.1f}%")
    
    print("\n" + "=" * 80)
    print("Analysis Complete!")
    print("=" * 80)

if __name__ == '__main__':
    stats = analyze_project()
    print_report(stats)
