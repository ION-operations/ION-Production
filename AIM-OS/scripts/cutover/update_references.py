#!/usr/bin/env python3
"""
Update all references from T-level to L-level across codebase.
Usage: python scripts/cutover/update_references.py
"""

import re
import os
from pathlib import Path

# Files to update
TARGET_FILES = [
    "knowledge_architecture/SUPER_INDEX.md",
    "knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md",
    "plans/EPIC_STANDARDS_TRACKING.md",
]

# Replacement patterns (order matters - more specific first)
REPLACEMENTS = [
    # File references
    (r"T0_executive\.md", "L0_executive.md"),
    (r"T1_overview\.md", "L1_overview.md"),
    (r"T2_architecture\.md", "L2_architecture.md"),
    (r"T3_detailed\.md", "L3_detailed.md"),
    (r"T4_complete\.md", "L4_complete.md"),
    (r"T6_complete\.md", "L6_complete.md"),
    # Anchor references
    (r"#t0-executive", "#l0-executive"),
    (r"#t1-overview", "#l1-overview"),
    (r"#t2-architecture", "#l2-architecture"),
    (r"#t3-detailed", "#l3-detailed"),
    # Path references
    (r"/T0_executive", "/L0_executive"),
    (r"/T1_overview", "/L1_overview"),
    (r"/T2_architecture", "/L2_architecture"),
    (r"/T3_detailed", "/L3_detailed"),
]

def update_file(file_path: Path):
    """Update references in a single file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        
        for pattern, replacement in REPLACEMENTS:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            print(f"✅ Updated {file_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Main execution."""
    updated_count = 0
    
    print("🔄 Updating references from T-level to L-level...")
    print()
    
    # Update target files
    for target_file in TARGET_FILES:
        file_path = Path(target_file)
        if file_path.exists():
            if update_file(file_path):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {target_file}")
    
    # Update system map files
    systems_dir = Path("knowledge_architecture/systems")
    if systems_dir.exists():
        for map_file in systems_dir.rglob("system.map.lucid.json5"):
            if update_file(map_file):
                updated_count += 1
    
    print()
    if updated_count > 0:
        print(f"✅ Updated {updated_count} files")
    else:
        print("ℹ️  No files required updates")

if __name__ == "__main__":
    main()

