#!/usr/bin/env python3
"""Extract T-Level Content for ALL Partial Systems"""

import shutil
import sys
import io
import re
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def convert_l_to_t(system_dir: Path, l_level: str, t_level: str):
    """Convert L-level file to T-level with proper frontmatter."""
    l_file = system_dir / f"{l_level}_executive.md" if l_level == "L0" else \
             system_dir / f"{l_level}_overview.md" if l_level == "L1" else \
             system_dir / f"{l_level}_architecture.md" if l_level == "L2" else \
             system_dir / f"{l_level}_detailed.md" if l_level == "L3" else \
             system_dir / f"{l_level}_complete.md" if l_level == "L4" else None
    
    if not l_file or not l_file.exists():
        return False
    
    system_name = system_dir.name
    
    # Read L-level content
    l_content = l_file.read_text(encoding='utf-8')
    
    # Extract content (remove L-level frontmatter if present)
    if l_content.startswith('---'):
        content_parts = l_content.split('---', 2)
        if len(content_parts) >= 3:
            l_content_body = content_parts[2].strip()
        else:
            l_content_body = content_parts[1].strip() if len(content_parts) > 1 else l_content
    else:
        l_content_body = l_content.strip()
    
    # Create T-level frontmatter based on level
    if t_level == "T3":
        t_frontmatter = f"""---
id: "{system_name}_T3_detailed"
system: "{system_name}"
component: null
level: "T3"
type: "detailed"
title: "{system_name.upper()} Detailed Implementation Guide"
description: "10,000-word detailed implementation guide"
audience: "developers, implementers"
confidence_threshold: 0.60
token_cost: 10000
word_count: 10000
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T16:00:00Z"
author: "aether"
status: "complete"
tags: ["{system_name}", "core", "t0-t6", "transitional"]
dependencies: ["{system_name}_T2_architecture"]
related_docs: ["{system_name}_T4_complete", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

"""
    elif t_level == "T4":
        t_frontmatter = f"""---
id: "{system_name}_T4_complete"
system: "{system_name}"
component: null
level: "T4"
type: "complete"
title: "{system_name.upper()} Complete Specification"
description: "15,000+ word complete reference"
audience: "experts, maintainers"
confidence_threshold: 0.50
token_cost: 15000
word_count: 15000
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T16:00:00Z"
author: "aether"
status: "complete"
tags: ["{system_name}", "core", "t0-t6", "transitional"]
dependencies: ["{system_name}_T3_detailed"]
related_docs: ["system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

"""
    else:
        return False
    
    # Create T-level file
    t_file = system_dir / f"{t_level}_detailed.md" if t_level == "T3" else \
             system_dir / f"{t_level}_complete.md" if t_level == "T4" else None
    
    if not t_file:
        return False
    
    # Combine frontmatter and content
    t_content = t_frontmatter + "\n" + l_content_body
    
    # Write T-level file
    t_file.write_text(t_content, encoding='utf-8')
    return True

def extract_t_levels(system_name: str, convert_l3_t4: bool = True):
    """Extract T-level files for a system."""
    system_dir = Path(f"knowledge_architecture/systems/{system_name}")
    
    if not system_dir.exists():
        print(f"ERROR: System directory not found: {system_dir}")
        return
    
    print(f"\n=== {system_name.upper()} ===")
    
    # Copy T0-T2 from L0-L2 (if they contain T-level content)
    mappings = [
        ("L0_executive.md", "T0_executive.md"),
        ("L1_overview.md", "T1_overview.md"),
        ("L2_architecture.md", "T2_architecture.md"),
    ]
    
    for l_file, t_file in mappings:
        l_path = system_dir / l_file
        t_path = system_dir / t_file
        
        if l_path.exists():
            # Check if L file contains T-level content
            content = l_path.read_text(encoding='utf-8')
            if "TRANSITIONAL T-LEVEL DOCUMENT" in content or 'level: "T' in content:
                if not t_path.exists():
                    shutil.copy(l_path, t_path)
                    print(f"  [OK] Created {t_file}")
                else:
                    print(f"  [SKIP] {t_file} already exists")
            else:
                print(f"  [SKIP] {l_file} does not contain T-level content")
        else:
            print(f"  [SKIP] {l_file} not found")
    
    # Convert L3 to T3 and L4 to T4
    if convert_l3_t4:
        l3_path = system_dir / "L3_detailed.md"
        t3_path = system_dir / "T3_detailed.md"
        l4_path = system_dir / "L4_complete.md"
        t4_path = system_dir / "T4_complete.md"
        
        if l3_path.exists() and not t3_path.exists():
            if convert_l_to_t(system_dir, "L3", "T3"):
                print(f"  [OK] Created T3_detailed.md")
            else:
                print(f"  [ERROR] Failed to create T3_detailed.md")
        
        if l4_path.exists() and not t4_path.exists():
            if convert_l_to_t(system_dir, "L4", "T4"):
                print(f"  [OK] Created T4_complete.md")
            else:
                print(f"  [ERROR] Failed to create T4_complete.md")

# Core systems
core_systems = ["cmc", "hhni", "vif", "apoe", "seg", "sdfcvf", "cognitive_analysis"]

# Partial supporting systems
partial_systems = [
    "timeline_context_system",
    "cross_model_consciousness",
    "dual_prompt_architecture",
    "dynamic_onboarding",
    "mcp_integration",
    "autonomous_research_dream",
    "capability_awareness"
]

print("=== T-Level Content Extraction ===")
print(f"Processing {len(core_systems)} core systems + {len(partial_systems)} partial systems...\n")

# Process core systems (with L3→T3, L4→T4 conversion)
for system in core_systems:
    extract_t_levels(system, convert_l3_t4=True)

# Process partial systems (with L3→T3, L4→T4 conversion)
for system in partial_systems:
    extract_t_levels(system, convert_l3_t4=True)

print("\n[COMPLETE] Extraction complete for all partial systems!")

