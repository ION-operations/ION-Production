#!/usr/bin/env python3
"""
Verify all links in agent onboarding files.
Checks for broken links and missing files.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

BASE_DIR = Path(__file__).parent.parent
AGENTS_DIR = BASE_DIR / "agents"
# Find workspace root by going up from BASE_DIR until we find the root marker
# BASE_DIR is knowledge_architecture/AGENT_ONBOARDING
# Workspace root is the directory containing knowledge_architecture/
WORKSPACE_ROOT = BASE_DIR.parent.parent  # knowledge_architecture/AGENT_ONBOARDING -> knowledge_architecture -> workspace root

def extract_links(content: str, file_path: Path) -> List[Tuple[str, str, int]]:
    """Extract all markdown links from content."""
    links = []
    # Pattern: [text](path) or [text](path#anchor)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    for match in re.finditer(pattern, content):
        link_text = match.group(1)
        link_path = match.group(2)
        line_num = content[:match.start()].count('\n') + 1
        links.append((link_text, link_path, line_num))
    return links

def resolve_link(link_path: str, from_file: Path) -> Path:
    """Resolve relative link path to absolute path from workspace root."""
    # Remove anchor if present
    if '#' in link_path:
        link_path = link_path.split('#')[0]
    
    # Skip external URLs
    if link_path.startswith('http://') or link_path.startswith('https://'):
        return None
    
    # Resolve relative to file location
    if link_path.startswith('/'):
        # Absolute from workspace root
        return WORKSPACE_ROOT / link_path[1:]
    else:
        # Relative to file - resolve from file's directory
        # From: knowledge_architecture/AGENT_ONBOARDING/agents/{agent}/README.md
        # Link: ../../../systems/cmc/T0_executive.md
        # Resolve: workspace_root/systems/cmc/T0_executive.md
        
        # Count ../ in link_path
        if link_path.startswith('../'):
            # Count how many levels up
            parts = link_path.split('/')
            up_count = sum(1 for p in parts if p == '..')
            # Remove ../ parts
            remaining_path = '/'.join([p for p in parts if p != '..'])
            
            # From file location, go up up_count levels, then append remaining_path
            # File is at: knowledge_architecture/AGENT_ONBOARDING/agents/{agent}/README.md
            # up_count=3 means: go up 3 levels from README.md -> agents -> AGENT_ONBOARDING -> knowledge_architecture -> workspace_root
            # Then append remaining_path
            
            current = from_file.parent
            for _ in range(up_count):
                current = current.parent
            
            resolved = current / remaining_path
            return resolved.resolve()
        else:
            # Relative to file directory
            resolved = (from_file.parent / link_path).resolve()
            return resolved

def verify_file_exists(file_path: Path) -> bool:
    """Verify file exists."""
    if file_path is None:
        return False
    return file_path.exists() and file_path.is_file()

def verify_onboarding_file(file_path: Path) -> List[Dict[str, any]]:
    """Verify all links in an onboarding file."""
    issues = []
    content = file_path.read_text(encoding='utf-8')
    links = extract_links(content, file_path)
    
    for link_text, link_path, line_num in links:
        resolved_path = resolve_link(link_path, file_path)
        if resolved_path and not verify_file_exists(resolved_path):
            issues.append({
                'file': str(file_path.relative_to(BASE_DIR)),
                'line': line_num,
                'link_text': link_text,
                'link_path': link_path,
                'resolved_path': str(resolved_path),
                'issue': 'File not found'
            })
    
    return issues

def main():
    """Main verification function."""
    all_issues = []
    
    # Verify all agent onboarding files
    for agent_dir in AGENTS_DIR.iterdir():
        if not agent_dir.is_dir():
            continue
        
        for file_name in ['README.md', 'CONTEXT.md', 'NAVIGATION.md', 'MISSIONS.md']:
            file_path = agent_dir / file_name
            if file_path.exists():
                issues = verify_onboarding_file(file_path)
                all_issues.extend(issues)
    
    # Report results
    if all_issues:
        print(f"Found {len(all_issues)} broken links:\n")
        for issue in all_issues:
            print(f"  {issue['file']}:{issue['line']}")
            print(f"    Link: [{issue['link_text']}]({issue['link_path']})")
            print(f"    Resolved: {issue['resolved_path']}")
            print(f"    Issue: {issue['issue']}\n")
        return 1
    else:
        print("All links verified successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main())

