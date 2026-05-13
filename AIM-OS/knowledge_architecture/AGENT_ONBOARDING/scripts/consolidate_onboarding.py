#!/usr/bin/env python3
"""
Consolidate agent onboarding updates.
Checks for new agent work and updates onboarding files.
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict

BASE_DIR = Path(__file__).parent.parent
AGENTS_DIR = BASE_DIR / "agents"
AGENT_DOCS_DIR = BASE_DIR.parent.parent / "ide_orchestration" / "prototypes" / "dac" / "docs" / "agents"

def find_new_agent_work(agent_id: str) -> List[Dict[str, str]]:
    """Find new agent work from agent documentation folder."""
    agent_docs_path = AGENT_DOCS_DIR / agent_id
    if not agent_docs_path.exists():
        return []
    
    new_work = []
    for doc_file in agent_docs_path.glob("*.md"):
        # Skip onboarding files
        if doc_file.name in ['README.md', 'CONTEXT.md', 'NAVIGATION.md', 'MISSIONS.md']:
            continue
        
        # Check if already referenced in MISSIONS.md
        missions_path = AGENTS_DIR / agent_id / "MISSIONS.md"
        if missions_path.exists():
            missions_content = missions_path.read_text(encoding='utf-8')
            if doc_file.name in missions_content:
                continue
        
        # Get file modification time
        mtime = datetime.fromtimestamp(doc_file.stat().st_mtime)
        
        new_work.append({
            'file': doc_file.name,
            'path': str(doc_file.relative_to(AGENT_DOCS_DIR)),
            'modified': mtime.strftime('%Y-%m-%d')
        })
    
    return new_work

def update_missions(agent_id: str, new_work: List[Dict[str, str]]):
    """Update MISSIONS.md with new work."""
    missions_path = AGENTS_DIR / agent_id / "MISSIONS.md"
    if not missions_path.exists():
        return
    
    content = missions_path.read_text(encoding='utf-8')
    
    # Find missions section
    if new_work:
        # Add new mission entries
        mission_entries = []
        for work in new_work:
            entry = f"""
### **Mission: {work['file']} ({work['modified']})**

**Purpose:** {work['file']}

**Deliverables:**
- [{work['file']}](../../../ide_orchestration/prototypes/dac/docs/agents/{agent_id}/{work['file']}) - {work['file']}

**Status:** ✅ Complete
"""
            mission_entries.append(entry)
        
        # Insert before "## 💡 **LESSONS LEARNED**" section
        if "## 💡 **LESSONS LEARNED**" in content:
            insert_pos = content.find("## 💡 **LESSONS LEARNED**")
            new_content = content[:insert_pos] + "\n".join(mission_entries) + "\n\n" + content[insert_pos:]
            missions_path.write_text(new_content, encoding='utf-8')
            print(f"Updated {missions_path} with {len(new_work)} new missions")

def main():
    """Main consolidation function."""
    for agent_dir in AGENTS_DIR.iterdir():
        if not agent_dir.is_dir():
            continue
        
        agent_id = agent_dir.name
        new_work = find_new_agent_work(agent_id)
        
        if new_work:
            print(f"Found {len(new_work)} new work items for {agent_id}")
            update_missions(agent_id, new_work)

if __name__ == "__main__":
    main()

