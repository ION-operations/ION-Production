#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T→L Cutover Execution Script (Windows Compatible)
Executes the complete T→L cutover process.
Usage: python scripts/cutover/execute_cutover.py
"""

import os
import sys
import shutil
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

SYSTEMS = [
    "cmc",
    "hhni",
    "vif",
    "apoe",
    "seg",
    "sdfcvf",
    "cognitive_analysis",
    "cross_model_consciousness",
    "timeline_context_system",
    "dual_prompt_architecture",
    "capability_awareness",
    "dynamic_onboarding",
    "advanced_monaco_editor",
    "autonomous_research_dream",
    "mcp_integration",  # Added: MCP Integration system
]

def backup_legacy():
    """Step 1: Backup L-level documents."""
    print("\n📦 Step 1: Backing up L-level documents...")
    print("=" * 60)
    
    systems_dir = Path("knowledge_architecture/systems")
    legacy_dir = Path("legacy_docs")
    
    backed_up = 0
    
    for system in SYSTEMS:
        system_dir = systems_dir / system
        if not system_dir.exists():
            continue
        
        legacy_system_dir = legacy_dir / system
        legacy_system_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy L-level files
        l_files = list(system_dir.glob("L*.md"))
        if l_files:
            for l_file in l_files:
                dest = legacy_system_dir / l_file.name
                shutil.copy2(l_file, dest)
                backed_up += 1
        
        if l_files:
            print(f"✅ Backed up {len(l_files)} files from {system}")
    
    print(f"\n✅ Backup complete: {backed_up} files backed up")
    return backed_up > 0

def rename_t2l():
    """Step 2: Rename T-level files to L-level."""
    print("\n🔄 Step 2: Renaming T→L for all systems...")
    print("=" * 60)
    
    systems_dir = Path("knowledge_architecture/systems")
    renamed_total = 0
    
    rename_map = {
        "T0_executive.md": "L0_executive.md",
        "T1_overview.md": "L1_overview.md",
        "T2_architecture.md": "L2_architecture.md",
        "T3_detailed.md": "L3_detailed.md",
        "T4_complete.md": "L4_complete.md",
        "T6_complete.md": "L6_complete.md",
    }
    
    for system in SYSTEMS:
        system_dir = systems_dir / system
        if not system_dir.exists():
            continue
        
        renamed_count = 0
        for old_name, new_name in rename_map.items():
            old_path = system_dir / old_name
            new_path = system_dir / new_name
            
            if old_path.exists():
                # If new file exists, remove it first (backup already done)
                if new_path.exists():
                    new_path.unlink()
                
                old_path.rename(new_path)
                renamed_count += 1
                renamed_total += 1
        
        if renamed_count > 0:
            print(f"✅ Renamed {renamed_count} files for {system}")
    
    print(f"\n✅ Rename complete: {renamed_total} files renamed")
    return renamed_total > 0

def update_references():
    """Step 3: Update references."""
    print("\n🔄 Step 3: Updating references...")
    print("=" * 60)
    
    # Import the update_references script
    sys.path.insert(0, str(Path(__file__).parent))
    from update_references import main as update_main
    
    update_main()

def remove_banners():
    """Step 4: Remove banners."""
    print("\n🔄 Step 4: Removing transitional banners...")
    print("=" * 60)
    
    # Import the remove_banners script
    sys.path.insert(0, str(Path(__file__).parent))
    from remove_banners import main as remove_main
    
    remove_main()

def validate_cutover():
    """Step 5: Validate cutover."""
    print("\n🔍 Step 5: Validating cutover...")
    print("=" * 60)
    
    # Run validation check - only check for actual T-level files (T0-T6)
    remaining_t = [
        f for f in Path("knowledge_architecture/systems").rglob("T*.md")
        if f.name.startswith(("T0_executive", "T1_overview", "T2_architecture", "T3_detailed", "T4_complete", "T6_complete"))
    ]
    
    if remaining_t:
        print(f"❌ Found {len(remaining_t)} remaining T-level files:")
        for f in remaining_t[:10]:  # Show first 10
            print(f"   {f}")
        if len(remaining_t) > 10:
            print(f"   ... and {len(remaining_t) - 10} more")
        return False
    else:
        print("✅ No remaining T-level files found")
    
    l_files = list(Path("knowledge_architecture/systems").rglob("L*.md"))
    print(f"✅ Found {len(l_files)} L-level files")
    
    return True

def main():
    """Main execution."""
    print("🚀 T→L Cutover Execution")
    print("=" * 60)
    print(f"Started: {sys.argv[0]}")
    print()
    
    try:
        # Step 1: Backup
        if not backup_legacy():
            print("⚠️  Warning: No L-level files found to backup")
        
        # Step 2: Rename
        if not rename_t2l():
            print("❌ Error: No T-level files found to rename")
            return 1
        
        # Step 3: Update references
        update_references()
        
        # Step 4: Remove banners
        remove_banners()
        
        # Step 5: Validate
        if not validate_cutover():
            print("\n❌ Cutover validation failed")
            return 1
        
        print("\n" + "=" * 60)
        print("✅ Cutover execution complete!")
        print()
        print("Next steps:")
        print("1. Run L0-L6 gate validation")
        print("2. Update tracking files")
        print("3. Document completion")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during cutover: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

