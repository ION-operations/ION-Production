#!/usr/bin/env python3
"""
Comprehensive AppExamples Organization Script
Organizes all apps by priority and category
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict

# Base paths
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
APPEXAMPLES_ROOT = ROOT_DIR / "Documentation" / "appexamples"
ORGANIZED_ROOT = APPEXAMPLES_ROOT / "00_Organized"

# App mappings: (source_name, dest_category, dest_subcategory)
APP_MAPPINGS = [
    # CRITICAL
    ("CURSOR_NL_VALIDATION_EXTENSION", "01_CRITICAL_AIMOS", "Cursor_Extensions"),
    ("Lucid_IDE", "01_CRITICAL_AIMOS", "IDE_Platforms"),
    
    # HIGH PRIORITY
    ("LUMIN_V1_30_CLEAN", "02_HIGH_PRIORITY", "3D_Platforms"),
    ("appbuilder", "02_HIGH_PRIORITY", "Multi_Agent_Platforms"),  # WisdomNET
    ("browserai", "02_HIGH_PRIORITY", "Browser_Extensions"),
    
    # MEDIUM PRIORITY
    ("amazinguiediter", "03_MEDIUM_PRIORITY", "AI_Tools"),
    ("LUNAR", "03_MEDIUM_PRIORITY", "Development_Tools"),
    ("MeshyVault", "03_MEDIUM_PRIORITY", "AI_Tools"),
    ("InfiniTREE", "03_MEDIUM_PRIORITY", "Visualization"),
    
    # APPLICATION EXAMPLES
    ("UI for image edit", "04_APPLICATION_EXAMPLES", "Image_Editing"),
    ("lava-lamp-studio", "04_APPLICATION_EXAMPLES", "Creative_Tools"),
    ("cool2d3dtexture", "04_APPLICATION_EXAMPLES", "Creative_Tools"),
    ("organizer", "04_APPLICATION_EXAMPLES", "Organization"),
    ("doc", "04_APPLICATION_EXAMPLES", "Organization"),
    ("wisdomtree", "04_APPLICATION_EXAMPLES", "Visualization"),
    ("wisdomnet", "04_APPLICATION_EXAMPLES", "Visualization"),
    ("Cloud Ai", "04_APPLICATION_EXAMPLES", "Cloud_Apps"),
    ("Cloud Ai App", "04_APPLICATION_EXAMPLES", "Cloud_Apps"),
]

FILES_COPIED = 0
FILES_SKIPPED = 0
APPS_ORGANIZED = 0

def copy_app_safe(source_dir, dest_dir, app_name):
    """Safely copy app directory to destination."""
    global FILES_COPIED, FILES_SKIPPED, APPS_ORGANIZED
    
    if not source_dir.exists():
        print(f"  [WARN] Source not found: {source_dir}")
        return False
    
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy entire directory
    try:
        if dest_dir.exists():
            # Check if already copied (compare sizes)
            source_size = sum(f.stat().st_size for f in source_dir.rglob('*') if f.is_file())
            dest_size = sum(f.stat().st_size for f in dest_dir.rglob('*') if f.is_file())
            
            if source_size == dest_size and source_size > 0:
                FILES_SKIPPED += 1
                print(f"  [SKIP] Already organized: {app_name}")
                return False
        
        # Copy directory
        shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
        
        # Count files copied
        files_in_app = sum(1 for f in source_dir.rglob('*') if f.is_file())
        FILES_COPIED += files_in_app
        APPS_ORGANIZED += 1
        
        print(f"  [OK] Organized: {app_name} ({files_in_app} files)")
        return True
        
    except Exception as e:
        print(f"  [ERROR] Failed to copy {app_name}: {e}")
        return False

def organize_apps():
    """Organize all apps by priority and category."""
    print("\n[ORGANIZING] Copying apps to organized structure...")
    
    for source_name, category, subcategory in APP_MAPPINGS:
        source_dir = APPEXAMPLES_ROOT / source_name
        dest_dir = ORGANIZED_ROOT / category / subcategory / source_name
        
        print(f"\n  [{category}/{subcategory}] {source_name}...", end="", flush=True)
        
        if copy_app_safe(source_dir, dest_dir, source_name):
            print(" Done!")
        else:
            print(" Skipped or failed")

def create_summary():
    """Create organization summary."""
    summary_path = ORGANIZED_ROOT / "ORGANIZATION_SUMMARY.md"
    
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# AppExamples Organization Summary\n\n")
        f.write(f"**Date:** 2025-11-12\n")
        f.write(f"**Status:** Complete\n\n")
        f.write("---\n\n")
        f.write(f"## Statistics\n\n")
        f.write(f"- **Apps Organized:** {APPS_ORGANIZED}\n")
        f.write(f"- **Files Copied:** {FILES_COPIED}\n")
        f.write(f"- **Files Skipped:** {FILES_SKIPPED}\n")
        f.write(f"- **Total Apps:** {len(APP_MAPPINGS)}\n\n")
        f.write("---\n\n")
        f.write("## Organization Structure\n\n")
        f.write("Apps organized by priority and category:\n\n")
        f.write("- **01_CRITICAL_AIMOS** - Direct AIM-OS integration apps\n")
        f.write("- **02_HIGH_PRIORITY** - High-value patterns for AIM-OS\n")
        f.write("- **03_MEDIUM_PRIORITY** - Useful patterns when needed\n")
        f.write("- **04_APPLICATION_EXAMPLES** - Reference implementations\n\n")
        f.write("---\n\n")
        f.write("*Organization Complete!* 💙\n")
    
    print(f"\n[OK] Created organization summary: {summary_path}")

def main():
    """Main organization function."""
    print("=" * 70)
    print("APPEXAMPLES COMPREHENSIVE ORGANIZATION")
    print("=" * 70)
    
    print(f"Source: {APPEXAMPLES_ROOT}")
    print(f"Destination: {ORGANIZED_ROOT}")
    
    organize_apps()
    create_summary()
    
    print("\n" + "=" * 70)
    print("[OK] ORGANIZATION COMPLETE")
    print("=" * 70)
    print(f"\nResults:")
    print(f"  - Apps organized: {APPS_ORGANIZED}")
    print(f"  - Files copied: {FILES_COPIED}")
    print(f"  - Files skipped: {FILES_SKIPPED}")
    print(f"  - Organized apps in: {ORGANIZED_ROOT}")
    print(f"  - Navigation hub: {ORGANIZED_ROOT / '00_Master_Navigation'}")
    print("\nNext steps:")
    print(f"  1. Review organized structure in '{ORGANIZED_ROOT}'")
    print(f"  2. Use navigation files in '{ORGANIZED_ROOT / '00_Master_Navigation'}'")

if __name__ == "__main__":
    main()

