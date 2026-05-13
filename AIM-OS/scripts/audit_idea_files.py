#!/usr/bin/env python3
"""
Idea Files Audit Script
Audits all idea files and generates comprehensive report
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import json

def extract_file_type(filename: str) -> str:
    """Extract file type from filename pattern"""
    upper_parts = re.findall(r'([A-Z]+(?:_[A-Z]+)*)', filename)
    if upper_parts:
        return upper_parts[0]
    return "OTHER"

def extract_role_from_path(filepath: str) -> str:
    """Extract role from file path"""
    parts = filepath.split(os.sep)
    if 'ideas' in parts:
        idx = parts.index('ideas')
        if idx + 1 < len(parts):
            role = parts[idx + 1]
            if role not in ['core_insights', 'cursor_integration', 'discussions', 'templates', 'ui_innovations']:
                return role
    return "shared"

def extract_system_references(content: str) -> List[str]:
    """Extract system references from content"""
    systems = ['CMC', 'HHNI', 'VIF', 'APOE', 'SEG', 'SDF-CVF', 'CAS', 'TCS', 'IIS', 'SCOR', 'MCP', 'LUCID']
    found = []
    for system in systems:
        if system in content or system.lower() in content.lower():
            found.append(system)
    return found

def audit_idea_files() -> Dict:
    """Audit all idea files"""
    ideas_dir = Path('ideas')
    files_data = []
    
    for filepath in ideas_dir.rglob('*.md'):
        rel_path = str(filepath.relative_to(ideas_dir))
        filename = filepath.name
        
        # Read file content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"[Error reading file: {e}]"
        
        # Extract metadata
        file_type = extract_file_type(filename)
        role = extract_role_from_path(rel_path)
        systems = extract_system_references(content)
        
        # Check for existing frontmatter
        has_frontmatter = content.startswith('---')
        
        files_data.append({
            'path': rel_path,
            'filename': filename,
            'type': file_type,
            'role': role,
            'systems': systems,
            'has_frontmatter': has_frontmatter,
            'size': len(content),
            'lines': len(content.split('\n'))
        })
    
    return {
        'total_files': len(files_data),
        'files': files_data,
        'by_type': {},
        'by_role': {},
        'by_system': {},
        'with_frontmatter': sum(1 for f in files_data if f['has_frontmatter']),
        'without_frontmatter': sum(1 for f in files_data if not f['has_frontmatter'])
    }

if __name__ == '__main__':
    audit_result = audit_idea_files()
    
    # Generate statistics
    by_type = {}
    by_role = {}
    by_system = {}
    
    for file_data in audit_result['files']:
        # Count by type
        file_type = file_data['type']
        by_type[file_type] = by_type.get(file_type, 0) + 1
        
        # Count by role
        role = file_data['role']
        by_role[role] = by_role.get(role, 0) + 1
        
        # Count by system
        for system in file_data['systems']:
            by_system[system] = by_system.get(system, 0) + 1
    
    audit_result['by_type'] = dict(sorted(by_type.items(), key=lambda x: x[1], reverse=True))
    audit_result['by_role'] = dict(sorted(by_role.items(), key=lambda x: x[1], reverse=True))
    audit_result['by_system'] = dict(sorted(by_system.items(), key=lambda x: x[1], reverse=True))
    
    # Print summary
    print(f"Total idea files: {audit_result['total_files']}")
    print(f"Files with frontmatter: {audit_result['with_frontmatter']}")
    print(f"Files without frontmatter: {audit_result['without_frontmatter']}")
    print(f"\nBy type: {audit_result['by_type']}")
    print(f"\nBy role: {audit_result['by_role']}")
    print(f"\nBy system: {audit_result['by_system']}")
    
    # Save detailed report
    report_path = Path('knowledge_architecture/AETHER_MEMORY/investigations/IDEA_FILES_AUDIT_RESULTS.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(audit_result, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed report saved to: {report_path}")

