#!/usr/bin/env python3
"""
Add MCP tool integration sections to all agent onboarding files.

This script adds:
1. MCP context restoration section to NAVIGATION.md
2. MCP enhancement section to CONTEXT.md
"""

import os
import re
from pathlib import Path

# Agent information: (agent_name, system_name, query_terms)
AGENTS = [
    ("atlas", "CMC", "atlas agent identity context CMC memory storage"),
    ("sev", "HHNI", "sev agent identity context HHNI retrieval"),
    ("veritas", "VIF", "veritas agent identity context VIF verification"),
    ("nexus", "APOE", "nexus agent identity context APOE orchestration"),
    ("sage", "SEG", "sage agent identity context SEG knowledge synthesis"),
    ("meta", "CAS", "meta agent identity context CAS cognitive analysis"),
    ("chronos", "TCS", "chronos agent identity context TCS timeline"),
    ("lexicon", "UI", "lexicon agent identity context UI interface"),
    ("codex", "Chat", "codex agent identity context chat conversation"),
    ("solo", "Integration", "solo agent identity context integration"),
    ("prism", "IIS", "prism agent identity context IIS intuition"),
    ("sentinel", "SDF-CVF", "sentinel agent identity context SDF-CVF quality"),
    ("nova", "Developer", "nova agent identity context developer code"),
    ("echo", "User Advocate", "echo agent identity context user advocate"),
]

BASE_DIR = Path(__file__).parent.parent
AGENTS_DIR = BASE_DIR / "agents"


def add_mcp_section_to_navigation(agent_name: str, system_name: str, query_terms: str) -> bool:
    """Add MCP context restoration section to NAVIGATION.md"""
    nav_file = AGENTS_DIR / agent_name / "NAVIGATION.md"
    
    if not nav_file.exists():
        print(f"WARNING: {agent_name}/NAVIGATION.md not found")
        return False
    
    content = nav_file.read_text(encoding='utf-8')
    
    # Check if MCP section already exists
    if "I need to restore my context (session start)" in content:
        print(f"OK: {agent_name}/NAVIGATION.md already has MCP section")
        return True
    
    # Find the insertion point (after "SITUATION-BASED NAVIGATION" and before first "I need to")
    pattern = r'(## 🎯 \*\*SITUATION-BASED NAVIGATION\*\*\n\n)### \*\*"I need to'
    
    mcp_section = f'''### **"I need to restore my context (session start)"**

**Static Files (Always Available):**
1. Read [README.md](./README.md) - Your identity
2. Read [CONTEXT.md](./CONTEXT.md) - Your context
3. Read [NAVIGATION.md](./NAVIGATION.md) - Navigation guide
4. Read [MISSIONS.md](./MISSIONS.md) - Past missions

**MCP Tools (When Available):**
```python
# 1. Restore timeline context
timeline = mcp_lucid-mcp_get_timeline_entries(limit=10)

# 2. Restore memory context
memory = mcp_lucid-mcp_retrieve_memory(
    query="{query_terms}",
    limit=5,
    tags={{"agent": "{agent_name}", "type": "onboarding"}}
)

# 3. Restore goal context
goals = mcp_lucid-mcp_query_goal_timeline(status="in_progress")

# 4. Record session start
mcp_lucid-mcp_add_timeline_entry(
    prompt_id=f"session_start_{{timestamp}}",
    user_input="Session initialization - {agent_name.title()}",
    context_state={{"agent": "{agent_name}", "phase": "onboarding"}}
)
```

**If MCP Not Available:**
- Continue with static files only
- All functionality still works
- Navigation links still functional

**Reference:** See [ONBOARDING_CONSOLIDATION_PROTOCOL.md](../../ONBOARDING_CONSOLIDATION_PROTOCOL.md) for complete hybrid onboarding protocol

---

### **"I need to'''
    
    replacement = r'\1' + mcp_section
    
    new_content = re.sub(pattern, replacement, content, count=1)
    
    if new_content == content:
        print(f"WARNING: {agent_name}/NAVIGATION.md: Could not find insertion point")
        return False
    
    nav_file.write_text(new_content, encoding='utf-8')
    print(f"OK: Updated {agent_name}/NAVIGATION.md")
    return True


def add_mcp_section_to_context(agent_name: str, system_name: str, query_terms: str) -> bool:
    """Add MCP enhancement section to CONTEXT.md"""
    context_file = AGENTS_DIR / agent_name / "CONTEXT.md"
    
    if not context_file.exists():
        print(f"WARNING: {agent_name}/CONTEXT.md not found")
        return False
    
    content = context_file.read_text(encoding='utf-8')
    
    # Check if MCP section already exists
    if "CONTEXT RESTORATION (MCP-Enhanced)" in content:
        print(f"OK: {agent_name}/CONTEXT.md already has MCP section")
        return True
    
    # Find the insertion point (before "EVOLUTION" section)
    pattern = r'(## 🔄 \*\*EVOLUTION\*\*)'
    
    mcp_section = f'''## 🔄 **CONTEXT RESTORATION (MCP-Enhanced)**

**Static Context (From This File):**
- Timeline (historical, from file)
- Keywords (static, from file)
- Important things (static, from file)
- Relationships (static, from file)

**Dynamic Context (From MCP Tools):**
- Recent timeline entries (`get_timeline_entries`) - Recent work and context
- Relevant memories (`retrieve_memory`) - Related insights from memory
- Active goals (`query_goal_timeline`) - Current goals and progress

**Hybrid Approach:**
- Static context = Base layer (always available)
- MCP context = Enhancement layer (when available)
- Combined = Complete context

**MCP Tools to Use:**
- `get_timeline_entries` - Restore recent timeline (use instead of `get_timeline_summary` due to bug)
- `retrieve_memory` - Restore relevant insights (query: "{query_terms}")
- `query_goal_timeline` - Restore active goals (status: "in_progress")
- `add_timeline_entry` - Record session start and context
- `store_memory` - Store onboarding context for future sessions

**Reference:** See [MCP_TOOLS_ONBOARDING_MAPPING.md](../../MCP_TOOLS_ONBOARDING_MAPPING.md) for complete MCP tool mapping

---

\\1'''
    
    new_content = re.sub(pattern, mcp_section, content, count=1)
    
    if new_content == content:
        print(f"WARNING: {agent_name}/CONTEXT.md: Could not find insertion point")
        return False
    
    context_file.write_text(new_content, encoding='utf-8')
    print(f"OK: Updated {agent_name}/CONTEXT.md")
    return True


def main():
    """Update all agent files with MCP integration"""
    import sys
    import io
    
    # Fix encoding for Windows console
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("Adding MCP integration to all agent onboarding files...\n")
    
    nav_success = 0
    context_success = 0
    
    for agent_name, system_name, query_terms in AGENTS:
        print(f"\nProcessing {agent_name.title()} ({system_name})...")
        
        if add_mcp_section_to_navigation(agent_name, system_name, query_terms):
            nav_success += 1
        
        if add_mcp_section_to_context(agent_name, system_name, query_terms):
            context_success += 1
    
    print(f"\nComplete!")
    print(f"   NAVIGATION.md: {nav_success}/{len(AGENTS)} updated")
    print(f"   CONTEXT.md: {context_success}/{len(AGENTS)} updated")


if __name__ == "__main__":
    main()

