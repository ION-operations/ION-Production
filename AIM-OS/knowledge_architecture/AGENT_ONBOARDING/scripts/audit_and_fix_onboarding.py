#!/usr/bin/env python3
"""
Comprehensive audit and fix script for agent onboarding files.
Fixes common issues and enhances content quality.
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).parent.parent
AGENTS_DIR = BASE_DIR / "agents"
AGENT_DOCS_DIR = BASE_DIR.parent.parent / "ide_orchestration" / "prototypes" / "dac" / "docs" / "agents"
SYSTEMS_DIR = BASE_DIR.parent / "systems"
CONSOLIDATION_DOCS = BASE_DIR.parent.parent / "ide_orchestration" / "prototypes" / "dac" / "docs"

# Agent to system mapping
AGENT_TO_SYSTEM = {
    'atlas': 'cmc',
    'sev': 'hhni',
    'veritas': 'vif',
    'nexus': 'apoe',
    'sage': 'seg',
    'meta': 'cognitive_analysis',
    'chronos': 'timeline_context_system',
    'prism': 'intuitive_intelligence_system',
    'sentinel': 'sdfcvf'
}

# System display names
SYSTEM_DISPLAY_NAMES = {
    'cmc': 'CMC',
    'hhni': 'HHNI',
    'vif': 'VIF',
    'apoe': 'APOE',
    'seg': 'SEG',
    'cognitive_analysis': 'CAS',
    'timeline_context_system': 'TCS',
    'intuitive_intelligence_system': 'IIS',
    'sdfcvf': 'SDF-CVF'
}

def find_agent_identity_file(agent_id: str) -> Optional[str]:
    """Find agent identity file."""
    agent_docs_path = AGENT_DOCS_DIR / agent_id
    if not agent_docs_path.exists():
        return None
    
    # Look for identity files
    patterns = [
        f'AGENT_{agent_id.upper()}_IDENTITY.md',
        f'AGENT_{agent_id.capitalize()}_IDENTITY.md',
        f'{agent_id.capitalize()}_IDENTITY.md',
        f'{agent_id.upper()}_IDENTITY.md'
    ]
    
    for pattern in patterns:
        for file_path in agent_docs_path.glob(pattern):
            return str(file_path.relative_to(AGENT_DOCS_DIR))
    
    return None

def find_verification_report(agent_id: str) -> Optional[str]:
    """Find Phase 4 verification report."""
    agent_docs_path = AGENT_DOCS_DIR / agent_id
    if not agent_docs_path.exists():
        return None
    
    # Look for verification reports
    patterns = [
        f'*PHASE4*VERIFICATION*.md',
        f'*VERIFICATION*REPORT*.md',
        f'{agent_id.upper()}_PHASE4*.md',
        f'{agent_id.capitalize()}_PHASE4*.md'
    ]
    
    for pattern in patterns:
        for file_path in agent_docs_path.glob(pattern):
            return str(file_path.relative_to(AGENT_DOCS_DIR))
    
    return None

def get_system_keywords(system_name: str) -> List[str]:
    """Extract keywords from system documentation."""
    system_dir = SYSTEMS_DIR / system_name
    if not system_dir.exists():
        return []
    
    keywords = []
    
    # Read T0 or T1 for keywords
    for doc_file in ['T0_executive.md', 'T1_overview.md', 'T2_architecture.md']:
        doc_path = system_dir / doc_file
        if doc_path.exists():
            content = doc_path.read_text(encoding='utf-8')
            # Extract key terms (capitalized words, technical terms)
            # This is a simple extraction - could be enhanced
            matches = re.findall(r'\b([A-Z][A-Z0-9]+)\b', content)
            keywords.extend(matches[:10])  # Limit to 10
    
    return list(set(keywords))[:5]  # Return unique, limit to 5

def fix_readme(agent_id: str, system_name: str):
    """Fix README.md for agent."""
    readme_path = AGENTS_DIR / agent_id / "README.md"
    if not readme_path.exists():
        return
    
    content = readme_path.read_text(encoding='utf-8')
    original_content = content
    
    # Fix agent identity link
    identity_file = find_agent_identity_file(agent_id)
    if identity_file:
        # Update identity file reference
        pattern = r'(\[Agent Identity\]\([^)]+\))'
        replacement = f"[Agent Identity](../../../ide_orchestration/prototypes/dac/docs/agents/{agent_id}/{identity_file})"
        content = re.sub(pattern, replacement, content)
    else:
        # Remove or comment out identity link if not found
        pattern = r'- \[Agent Identity\]\([^)]+\)'
        content = re.sub(pattern, f'- [Agent Identity](../../../ide_orchestration/prototypes/dac/docs/agents/{agent_id}/) - *Not yet created*', content)
    
    # Fix system display name
    system_display = SYSTEM_DISPLAY_NAMES.get(system_name, system_name.upper())
    content = re.sub(r'\*\*Core System:\*\* ([^(]+) \(([^)]+)\)', 
                     f'**Core System:** {system_display} ({system_display})', content)
    
    if content != original_content:
        readme_path.write_text(content, encoding='utf-8')
        print(f"Fixed {readme_path}")

def enhance_context(agent_id: str, system_name: str):
    """Enhance CONTEXT.md with system-specific keywords."""
    context_path = AGENTS_DIR / agent_id / "CONTEXT.md"
    if not context_path.exists():
        return
    
    content = context_path.read_text(encoding='utf-8')
    original_content = content
    
    # Get system keywords
    keywords = get_system_keywords(system_name)
    
    # Enhance keywords section
    if keywords and "### **Core Concepts:**" in content:
        # Find keywords section and enhance
        keyword_section = "### **Core Concepts:**\n"
        for keyword in keywords:
            keyword_section += f"- **{keyword}:** {keyword} concept and relevance\n"
        
        # Replace existing keywords section
        pattern = r'### \*\*Core Concepts:\*\*\n(?:- \*\*[^\*]+\*\*: [^\n]+\n)+'
        if re.search(pattern, content):
            content = re.sub(pattern, keyword_section.rstrip() + '\n', content)
        else:
            # Insert after "## 🔑 **KEYWORDS**"
            if "## 🔑 **KEYWORDS**" in content:
                insert_pos = content.find("## 🔑 **KEYWORDS**") + len("## 🔑 **KEYWORDS**")
                content = content[:insert_pos] + "\n\n" + keyword_section + content[insert_pos:]
    
    if content != original_content:
        context_path.write_text(content, encoding='utf-8')
        print(f"Enhanced {context_path}")

def fix_navigation(agent_id: str, system_name: str):
    """Fix NAVIGATION.md with correct system paths."""
    nav_path = AGENTS_DIR / agent_id / "NAVIGATION.md"
    if not nav_path.exists():
        return
    
    content = nav_path.read_text(encoding='utf-8')
    original_content = content
    
    # Fix system documentation paths
    system_display = SYSTEM_DISPLAY_NAMES.get(system_name, system_name.upper())
    content = re.sub(r'\[([^\]]+)\]\(../../systems/\{system\}/', 
                     f'[\\1](../../systems/{system_name}/', content)
    content = re.sub(r'\{System\}', system_display, content)
    content = re.sub(r'\{system\}', system_name, content)
    content = re.sub(r'\{system_name\}', system_display, content)
    
    # Fix integration map anchor
    integration_anchors = {
        'cmc': '#1-cmc-context-memory-core---foundation',
        'hhni': '#2-hhni-hierarchical-hypergraph-neural-index---retrieval',
        'vif': '#3-vif-verifiable-intelligence-framework---verification',
        'apoe': '#5-apoe-ai-powered-orchestration-engine---orchestration',
        'seg': '#6-seg-semantic-episodic-graphs---knowledge',
        'cognitive_analysis': '#6-cas-cognitive-analysis-system---analysis',
        'timeline_context_system': '#7-tcs-timeline-context-system---timeline',
        'intuitive_intelligence_system': '#enhancement-system-integrations',
        'sdfcvf': '#sdf-cvf-atomic-evolution-framework---quality'
    }
    
    anchor = integration_anchors.get(system_name, '')
    if anchor:
        pattern = r'(\[Master Integration Map\]\([^)]+\))([^#]*)'
        replacement = f"\\1{anchor}"
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        nav_path.write_text(content, encoding='utf-8')
        print(f"Fixed {nav_path}")

def fix_missions(agent_id: str):
    """Fix MISSIONS.md with correct verification report links."""
    missions_path = AGENTS_DIR / agent_id / "MISSIONS.md"
    if not missions_path.exists():
        return
    
    content = missions_path.read_text(encoding='utf-8')
    original_content = content
    
    # Fix verification report link
    verification_report = find_verification_report(agent_id)
    if verification_report:
        pattern = r'(\[Phase 4 Verification Report\]\([^)]+\))'
        replacement = f"[Phase 4 Verification Report](../../../ide_orchestration/prototypes/dac/docs/agents/{agent_id}/{verification_report})"
        content = re.sub(pattern, replacement, content)
    else:
        # Remove or comment out if not found
        pattern = r'- \[Phase 4 Verification Report\]\([^)]+\)'
        content = re.sub(pattern, f'- [Phase 4 Verification Report](../../../ide_orchestration/prototypes/dac/docs/agents/{agent_id}/) - *Not yet created*', content)
    
    if content != original_content:
        missions_path.write_text(content, encoding='utf-8')
        print(f"Fixed {missions_path}")

def main():
    """Main audit and fix function."""
    print("Auditing and fixing agent onboarding files...\n")
    
    for agent_id, system_name in AGENT_TO_SYSTEM.items():
        agent_dir = AGENTS_DIR / agent_id
        if not agent_dir.exists():
            continue
        
        print(f"Processing {agent_id} ({system_name})...")
        fix_readme(agent_id, system_name)
        enhance_context(agent_id, system_name)
        fix_navigation(agent_id, system_name)
        fix_missions(agent_id)
        print()
    
    print("Audit and fix complete!")

if __name__ == "__main__":
    main()

