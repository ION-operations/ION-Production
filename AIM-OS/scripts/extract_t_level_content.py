#!/usr/bin/env python3
"""T-Level Content Extraction Script"""

import re
from pathlib import Path
from typing import Dict, Optional

def extract_t_level_content(file_path: Path) -> Optional[Dict]:
    """Extract T-level content from L-level file."""
    if not file_path.exists():
        return None
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Check for T-level banner
        has_banner = "TRANSITIONAL T-LEVEL DOCUMENT" in content
        
        # Extract metadata
        metadata_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not metadata_match:
            return None
        
        metadata = metadata_match.group(1)
        
        # Check for T-level in metadata
        t_level_match = re.search(r'level:\s*["\']T(\d)', metadata)
        if not t_level_match and not has_banner:
            return None
        
        t_level = t_level_match.group(1) if t_level_match else None
        
        # Extract content after metadata
        content_after_metadata = content.split('---', 2)[2] if '---' in content else content
        content_after_metadata = content_after_metadata.strip()
        
        return {
            "level": f"T{t_level}" if t_level else None,
            "metadata": metadata,
            "content": content_after_metadata,
            "has_banner": has_banner,
            "full_content": content
        }
    except Exception as e:
        return {"error": str(e)}

def create_t_level_file(system_dir: Path, level: str, t_content: Dict):
    """Create T-level file from extracted content."""
    t_file = system_dir / f"{level}_executive.md" if level == "T0" else \
             system_dir / f"{level}_overview.md" if level == "T1" else \
             system_dir / f"{level}_architecture.md" if level == "T2" else \
             system_dir / f"{level}_detailed.md" if level == "T3" else \
             system_dir / f"{level}_complete.md" if level == "T4" else None
    
    if not t_file:
        return False
    
    # If file already exists, check if it's different
    if t_file.exists():
        existing = t_file.read_text(encoding='utf-8')
        if existing == t_content["full_content"]:
            return True  # Already exists with same content
    
    # Create T-level file
    t_file.write_text(t_content["full_content"], encoding='utf-8')
    return True

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
    
    # Create T-level frontmatter
    t_frontmatter = f"""---
id: "{system_name}_{t_level}_executive"
system: "{system_name}"
component: null
level: "{t_level}"
type: "executive"
title: "{system_name.upper()} Executive Summary"
description: "100-word executive summary of {system_name.upper()}"
audience: "executives, quick reference"
confidence_threshold: 0.80
token_cost: 100
word_count: 100
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T16:00:00Z"
author: "aether"
status: "complete"
tags: ["{system_name}", "core", "t0-t6", "transitional"]
dependencies: []
related_docs: ["{system_name}_{t_level.replace('T0', 'T1')}_overview", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.
"""
    
    # Adjust frontmatter based on level
    if t_level == "T1":
        t_frontmatter = t_frontmatter.replace('executive', 'overview').replace('100-word', '500-word').replace('100', '500').replace('0.80', '0.75')
    elif t_level == "T2":
        t_frontmatter = t_frontmatter.replace('executive', 'architecture').replace('100-word', '2,000-word').replace('100', '2000').replace('0.80', '0.70')
    elif t_level == "T3":
        t_frontmatter = t_frontmatter.replace('executive', 'detailed').replace('100-word', '10,000-word').replace('100', '10000').replace('0.80', '0.60')
    elif t_level == "T4":
        t_frontmatter = t_frontmatter.replace('executive', 'complete').replace('100-word', '15,000+ word').replace('100', '15000').replace('0.80', '0.50')
    
    # Extract content (remove L-level frontmatter if present)
    if l_content.startswith('---'):
        content_parts = l_content.split('---', 2)
        if len(content_parts) >= 3:
            l_content = content_parts[2].strip()
        else:
            l_content = content_parts[1].strip() if len(content_parts) > 1 else l_content
    
    # Create T-level file
    t_file = system_dir / f"{t_level}_executive.md" if t_level == "T0" else \
             system_dir / f"{t_level}_overview.md" if t_level == "T1" else \
             system_dir / f"{t_level}_architecture.md" if t_level == "T2" else \
             system_dir / f"{t_level}_detailed.md" if t_level == "T3" else \
             system_dir / f"{t_level}_complete.md" if t_level == "T4" else None
    
    if not t_file:
        return False
    
    # Combine frontmatter and content
    t_content = t_frontmatter + "\n\n" + l_content
    
    # Write T-level file
    t_file.write_text(t_content, encoding='utf-8')
    return True

def extract_system(system_name: str):
    """Extract T-level content for a system."""
    system_dir = Path(f"knowledge_architecture/systems/{system_name}")
    
    if not system_dir.exists():
        print(f"ERROR: System directory not found: {system_dir}")
        return
    
    print(f"\n=== Extracting T-level content for {system_name} ===")
    
    # Extract T0-T2 from L0-L2 files
    l0_t0 = extract_t_level_content(system_dir / "L0_executive.md")
    l1_t1 = extract_t_level_content(system_dir / "L1_overview.md")
    l2_t2 = extract_t_level_content(system_dir / "L2_architecture.md")
    
    # Create T0-T2 files
    if l0_t0 and l0_t0.get("has_t_level"):
def main():
    """Main extraction function."""
    import sys
    import io
    
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Core systems first
    core_systems = ["cmc", "hhni", "vif", "apoe", "seg", "sdfcvf", "cognitive_analysis"]
    
    print("=== T-Level Content Extraction ===")
    print(f"Extracting T-level content for {len(core_systems)} core systems...\n")
    
    for system in core_systems:
        extract_system(system)
    
    print("\n[COMPLETE] Extraction complete for core systems!")

def main():
    """Main extraction function."""
    # Core systems first
    core_systems = ["cmc", "hhni", "vif", "apoe", "seg", "sdfcvf", "cognitive_analysis"]
    
    print("=== T-Level Content Extraction ===")
    print(f"Extracting T-level content for {len(core_systems)} core systems...\n")
    
    for system in core_systems:
        extract_system(system)
    
    print("\n✅ Extraction complete for core systems!")

if __name__ == "__main__":
    main()

