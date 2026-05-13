#!/usr/bin/env python3
"""Simple T-Level Extraction Script - Copy T-level content from L-level files"""

import shutil
import sys
import io
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_t_levels(system_name: str):
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
    
    # Check for L3 and L4 (need conversion)
    l3_path = system_dir / "L3_detailed.md"
    t3_path = system_dir / "T3_detailed.md"
    l4_path = system_dir / "L4_complete.md"
    t4_path = system_dir / "T4_complete.md"
    
    if l3_path.exists() and not t3_path.exists():
        print(f"  [TODO] Need to convert L3_detailed.md → T3_detailed.md")
    
    if l4_path.exists() and not t4_path.exists():
        print(f"  [TODO] Need to convert L4_complete.md → T4_complete.md")

# Core systems
core_systems = ["cmc", "hhni", "vif", "apoe", "seg", "sdfcvf", "cognitive_analysis"]

print("=== T-Level Content Extraction ===")
print(f"Processing {len(core_systems)} core systems...\n")

for system in core_systems:
    extract_t_levels(system)

print("\n[COMPLETE] Extraction complete!")

