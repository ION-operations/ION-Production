#!/usr/bin/env python3
"""
Fix all tag numbers in T-level docs to match reconciled_totals.json (source of truth).

This ensures all documentation matches reality exactly.
"""

from pathlib import Path
import json
import re

# Load reconciled totals (SOURCE OF TRUTH)
reconciled = json.loads(Path("artifacts/reconciled_totals.json").read_text())

# Build lookup
CORRECT_NUMBERS = {}
for sys_data in reconciled["systems"]:
    folder = sys_data["folder"]
    CORRECT_NUMBERS[folder] = sys_data["tags_total"]

print("CORRECT NUMBERS (from reconciled_totals.json):")
for folder, count in CORRECT_NUMBERS.items():
    print(f"  {folder}: {count} tags")

# System folder to display name
FOLDER_TO_NAME = {
    "vif": "VIF",
    "cmc": "CMC",
    "hhni": "HHNI",
    "apoe": "APOE",
    "seg": "SEG",
    "sdfcvf": "SDF-CVF",
    "cognitive_analysis": "CAS",
    "timeline_context_system": "TCS",
    "intuitive_intelligence_system": "IIS"
}

def fix_t1_file(t1_path: Path, system_folder: str):
    """Fix T1 tag count."""
    content = t1_path.read_text(encoding='utf-8')
    correct_count = CORRECT_NUMBERS[system_folder]
    
    # Pattern: "**Total NL Tags:** NNN tags"
    pattern = r'(\*\*Total NL Tags:\*\*\s*)\d+(\s*tags)'
    replacement = f'\\g<1>{correct_count}\\g<2>'
    
    updated = re.sub(pattern, replacement, content)
    
    if updated != content:
        t1_path.write_text(updated, encoding='utf-8')
        return True
    return False

def fix_t2_file(t2_path: Path, system_folder: str):
    """Fix T2 tag counts."""
    content = t2_path.read_text(encoding='utf-8')
    correct_count = CORRECT_NUMBERS[system_folder]
    
    # Pattern 1: "**Total tags:** NNN NL tags"
    pattern1 = r'(\*\*Total tags:\*\*\s*)\d+(\s*NL tags|\s*across)'
    replacement1 = f'\\g<1>{correct_count}\\g<2>'
    
    updated = re.sub(pattern1, replacement1, content)
    
    if updated != content:
        t2_path.write_text(updated, encoding='utf-8')
        return True
    return False

def fix_t3_file(t3_path: Path, system_folder: str):
    """Fix T3 catalog reference."""
    content = t3_path.read_text(encoding='utf-8')
    correct_count = CORRECT_NUMBERS[system_folder]
    
    # Pattern: "[NL_TAG_CATALOG.md](NL_TAG_CATALOG.md) (NNN tags)"
    pattern = r'(\[NL_TAG_CATALOG\.md\]\(NL_TAG_CATALOG\.md\)\s*\()\d+(\s*tags\))'
    replacement = f'\\g<1>{correct_count}\\g<2>'
    
    updated = re.sub(pattern, replacement, content)
    
    if updated != content:
        t3_path.write_text(updated, encoding='utf-8')
        return True
    return False

def main():
    """Fix all T-level docs with correct numbers."""
    root = Path("knowledge_architecture/systems")
    
    fixed_files = []
    
    for folder in CORRECT_NUMBERS.keys():
        system_dir = root / folder
        display_name = FOLDER_TO_NAME.get(folder, folder.upper())
        
        # Fix T1
        t1_path = system_dir / "T1_overview.md"
        if t1_path.exists():
            if fix_t1_file(t1_path, folder):
                fixed_files.append(str(t1_path))
                print(f"  [FIXED] {display_name} T1 -> {CORRECT_NUMBERS[folder]} tags", flush=True)
        
        # Fix T2
        t2_path = system_dir / "T2_architecture.md"
        if t2_path.exists():
            if fix_t2_file(t2_path, folder):
                fixed_files.append(str(t2_path))
                print(f"  [FIXED] {display_name} T2 -> {CORRECT_NUMBERS[folder]} tags", flush=True)
        
        # Fix T3
        t3_path = system_dir / "T3_detailed.md"
        if t3_path.exists():
            if fix_t3_file(t3_path, folder):
                fixed_files.append(str(t3_path))
                print(f"  [FIXED] {display_name} T3 -> {CORRECT_NUMBERS[folder]} tags", flush=True)
    
    print(f"\n[DONE] Fixed {len(fixed_files)} files with correct numbers")
    print(f"\nFiles updated: {len(fixed_files)}")
    
    # Write list for git add
    if fixed_files:
        Path("artifacts/fixed_files.txt").write_text("\n".join(fixed_files), encoding='utf-8')

if __name__ == "__main__":
    main()

