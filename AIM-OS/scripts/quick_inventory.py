#!/usr/bin/env python3
"""
Quick File Inventory - Fast version without git operations
Collects essential metrics to prove singularity property

Usage:
    python scripts/quick_inventory.py
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Ignore patterns
IGNORE_PATTERNS = [
    '__pycache__', 'node_modules', '.git', 'htmlcov', 
    '.pytest_cache', '.mypy_cache', 'dist', 'build',
    '.egg-info', 'aim-os-minimal'  # Skip duplicates
]

# System keywords
SYSTEMS = {
    'CMC': ['cmc', 'memory_store', 'bitemporal'],
    'HHNI': ['hhni', 'index', 'retrieval'],
    'VIF': ['vif', 'confidence', 'witness'],
    'APOE': ['apoe', 'orchestration', 'acl'],
    'SEG': ['seg', 'knowledge', 'graph'],
    'SDF-CVF': ['sdfcvf', 'quartet', 'parity'],
    'CAS': ['cognitive_analysis', 'cas'],
    'TCS': ['timeline_context', 'tcs'],
    'IIS': ['intuitive_intelligence', 'iis'],
    'SCOR': ['scor', 'safety'],
    'ARD': ['autonomous_research_dream', 'ard'],
}

def should_ignore(path: Path) -> bool:
    """Check if should ignore"""
    path_str = str(path)
    return any(pattern in path_str for pattern in IGNORE_PATTERNS)

def classify_system(path: Path) -> str:
    """Determine system"""
    path_lower = str(path).lower()
    for system, keywords in SYSTEMS.items():
        if any(kw in path_lower for kw in keywords):
            return system
    return 'infrastructure'

def classify_role(path: Path) -> str:
    """Classify role"""
    p = str(path).lower()
    if 'packages/cmc' in p or 'packages/hhni' in p or 'packages/vif' in p or \
       'packages/apoe' in p or 'packages/seg' in p or 'packages/sdfcvf' in p:
        return 'core'
    if 'packages/' in p:
        return 'supporting'
    if 'knowledge_architecture' in p or 'coordination' in p:
        return 'infrastructure'
    if 'archive' in p or 'backup' in p:
        return 'archive'
    if '.db' in p or '.log' in p or 'data/' in p:
        return 'data'
    return 'other'

def classify_type(path: Path) -> str:
    """Classify file type"""
    ext = path.suffix.lower()
    if ext == '.py':
        return 'code_python'
    if ext in ['.ts', '.tsx', '.js', '.jsx']:
        return 'code_typescript'
    if ext == '.md':
        return 'doc_markdown'
    if ext in ['.json', '.yaml', '.yml']:
        return 'config'
    if ext in ['.db', '.sqlite']:
        return 'database'
    return 'other'

def count_lines_fast(path: Path) -> tuple:
    """Fast line counting"""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        total = len(lines)
        blank = sum(1 for line in lines if not line.strip())
        
        # Quick comment detection for Python
        comments = 0
        if path.suffix == '.py':
            comments = sum(1 for line in lines if line.strip().startswith('#'))
        
        code = total - blank - comments
        return (total, code, comments, blank)
    except:
        return (0, 0, 0, 0)

def scan_fast():
    """Fast scan of entire project"""
    print("QUICK INVENTORY - Fast Metrics Collection")
    print("=" * 80)
    
    files = []
    stats = defaultdict(lambda: {
        'files': 0, 'lines_total': 0, 'lines_code': 0, 
        'lines_comments': 0, 'lines_blank': 0, 'size': 0
    })
    
    count = 0
    for path in PROJECT_ROOT.rglob('*'):
        if path.is_file() and not should_ignore(path):
            count += 1
            if count % 500 == 0:
                print(f"  Processed {count} files...")
            
            # Get metrics
            system = classify_system(path)
            role = classify_role(path)
            ftype = classify_type(path)
            total, code, comments, blank = count_lines_fast(path)
            size = path.stat().st_size
            
            # Aggregate
            for category, value in [('system', system), ('role', role), ('type', ftype)]:
                stats[f"{category}_{value}"]['files'] += 1
                stats[f"{category}_{value}"]['lines_total'] += total
                stats[f"{category}_{value}"]['lines_code'] += code
                stats[f"{category}_{value}"]['lines_comments'] += comments
                stats[f"{category}_{value}"]['lines_blank'] += blank
                stats[f"{category}_{value}"]['size'] += size
            
            # Overall totals
            stats['_total']['files'] += 1
            stats['_total']['lines_total'] += total
            stats['_total']['lines_code'] += code
            stats['_total']['lines_comments'] += comments
            stats['_total']['lines_blank'] += blank
            stats['_total']['size'] += size
    
    print(f"\n[OK] Scanned {count} files\n")
    
    # Print results
    print("=" * 80)
    print("OVERALL TOTALS")
    print("=" * 80)
    t = stats['_total']
    print(f"Files:          {t['files']:>10,}")
    print(f"Total lines:    {t['lines_total']:>10,}")
    print(f"  Code:         {t['lines_code']:>10,} ({t['lines_code']/t['lines_total']*100:>5.1f}%)")
    print(f"  Comments:     {t['lines_comments']:>10,} ({t['lines_comments']/t['lines_total']*100:>5.1f}%)")
    print(f"  Blank:        {t['lines_blank']:>10,} ({t['lines_blank']/t['lines_total']*100:>5.1f}%)")
    print(f"Total size:     {t['size']:>10,} bytes ({t['size']/1024/1024:>6.1f} MB)")
    print()
    
    # By system
    print("=" * 80)
    print("BY SYSTEM")
    print("=" * 80)
    systems = [(k.replace('system_', ''), v) for k, v in stats.items() if k.startswith('system_')]
    systems.sort(key=lambda x: x[1]['lines_code'], reverse=True)
    for system, data in systems:
        if data['lines_code'] > 0:
            print(f"{system:>15s}: {data['files']:>4,} files, {data['lines_code']:>7,} LOC")
    print()
    
    # By role
    print("=" * 80)
    print("BY ROLE")
    print("=" * 80)
    roles = [(k.replace('role_', ''), v) for k, v in stats.items() if k.startswith('role_')]
    roles.sort(key=lambda x: x[1]['lines_total'], reverse=True)
    for role, data in roles:
        print(f"{role:>15s}: {data['files']:>4,} files, {data['lines_total']:>8,} lines")
    print()
    
    # By type
    print("=" * 80)
    print("BY TYPE")
    print("=" * 80)
    types = [(k.replace('type_', ''), v) for k, v in stats.items() if k.startswith('type_')]
    types.sort(key=lambda x: x[1]['lines_total'], reverse=True)
    for ftype, data in types[:10]:  # Top 10
        print(f"{ftype:>20s}: {data['files']:>4,} files, {data['lines_total']:>8,} lines")
    print()
    
    # Complexity calculation
    print("=" * 80)
    print("SINGULARITY PROPERTY ANALYSIS")
    print("=" * 80)
    
    # Complexity metrics
    C_code = t['lines_code'] + t['files']
    C_complexity = C_code  # Simplified
    
    # Organization metrics (from what we know)
    doc_lines = sum(v['lines_total'] for k, v in stats.items() if 'doc_markdown' in k)
    O_docs = doc_lines
    O_organization = O_docs  # Simplified
    
    print(f"Complexity (C):     {C_complexity:>10,}")
    print(f"  Code LOC:         {t['lines_code']:>10,}")
    print(f"  Files:            {t['files']:>10,}")
    print()
    print(f"Organization (O):   {O_organization:>10,}")
    print(f"  Doc lines:        {doc_lines:>10,}")
    print()
    
    # Ratio
    ratio = O_organization / C_complexity if C_complexity > 0 else 0
    print(f"Ratio (O/C):        {ratio:>10.2f}")
    print()
    
    if ratio >= 0.8:
        print("[OK] BOUNDED DIVERGENCE CONFIRMED!")
        print("   Organization scaling WITH complexity")
    elif ratio >= 0.5:
        print("[WARN] PARTIAL DIVERGENCE")
        print("   Organization growing but lagging slightly")
    else:
        print("[FAIL] DIVERGENCE DETECTED")
        print("   Organization not keeping pace")
    
    print("=" * 80)
    
    # Save JSON
    output = {
        'generated': datetime.now().isoformat(),
        'totals': dict(stats['_total']),
        'by_system': {k.replace('system_', ''): v for k, v in stats.items() if k.startswith('system_')},
        'by_role': {k.replace('role_', ''): v for k, v in stats.items() if k.startswith('role_')},
        'by_type': {k.replace('type_', ''): v for k, v in stats.items() if k.startswith('type_')},
        'complexity': C_complexity,
        'organization': O_organization,
        'ratio': ratio,
    }
    
    out_path = PROJECT_ROOT / 'QUICK_METRICS.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n[SAVED] Output written to: {out_path}")
    print()

if __name__ == '__main__':
    scan_fast()

