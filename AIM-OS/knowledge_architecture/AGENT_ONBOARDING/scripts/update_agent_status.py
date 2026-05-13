#!/usr/bin/env python3
"""
Update agent onboarding status from system documentation.
Automatically updates completion percentages and integration status.
"""

import sys
import re
from pathlib import Path
from typing import Dict, Optional

BASE_DIR = Path(__file__).parent.parent
AGENTS_DIR = BASE_DIR / "agents"
SYSTEMS_DIR = BASE_DIR.parent / "systems"

# System to agent mapping
SYSTEM_TO_AGENT = {
    'cmc': 'atlas',
    'hhni': 'sev',
    'vif': 'veritas',
    'apoe': 'nexus',
    'seg': 'sage',
    'cognitive_analysis': 'meta',
    'timeline_context_system': 'chronos',
    'intuitive_intelligence_system': 'prism',
    'sdfcvf': 'sentinel'
}

def get_system_status(system_name: str) -> Dict[str, Optional[str]]:
    """Get system status from system documentation."""
    system_dir = SYSTEMS_DIR / system_name
    if not system_dir.exists():
        return {'completion': None, 'status': None}
    
    # Try to read T0 or T1 for status
    for doc_file in ['T0_executive.md', 'T1_overview.md']:
        doc_path = system_dir / doc_file
        if doc_path.exists():
            content = doc_path.read_text(encoding='utf-8')
            # Look for status patterns
            status_match = re.search(r'Status[:\s]+([^\n]+)', content, re.IGNORECASE)
            completion_match = re.search(r'(\d+)%', content)
            
            status = status_match.group(1).strip() if status_match else None
            completion = completion_match.group(1) + '%' if completion_match else None
            
            return {'completion': completion, 'status': status}
    
    return {'completion': None, 'status': None}

def update_readme_status(agent_id: str, system_status: Dict[str, Optional[str]]):
    """Update README.md with system status."""
    readme_path = AGENTS_DIR / agent_id / "README.md"
    if not readme_path.exists():
        return
    
    content = readme_path.read_text(encoding='utf-8')
    
    # Update completion percentage
    if system_status['completion']:
        pattern = r'(\*\*{System} Completion:\*\* )([^\n]+)'
        replacement = f"\\1{system_status['completion']}"
        content = re.sub(pattern, replacement, content)
    
    # Update status
    if system_status['status']:
        pattern = r'(\*\*Status:\*\* )([^\n]+)'
        replacement = f"\\1{system_status['status']}"
        content = re.sub(pattern, replacement, content)
    
    readme_path.write_text(content, encoding='utf-8')
    print(f"Updated {readme_path}")

def main():
    """Main update function."""
    for system_name, agent_id in SYSTEM_TO_AGENT.items():
        agent_dir = AGENTS_DIR / agent_id
        if not agent_dir.exists():
            continue
        
        system_status = get_system_status(system_name)
        update_readme_status(agent_id, system_status)
    
    print("Agent status update complete!")

if __name__ == "__main__":
    main()

