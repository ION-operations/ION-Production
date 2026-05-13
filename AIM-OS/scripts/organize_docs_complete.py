#!/usr/bin/env python3
"""
Complete Documentation Organization Script
Organizes all 700+ files by category and relationship
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict
import json

# Base paths - script is in root/scripts/, so parent.parent is root
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
DOC_ROOT = ROOT_DIR / "Documentation"
ORGANIZED_ROOT = DOC_ROOT / "00_Organized"
DOCUMENTATIONTEXT = DOC_ROOT / "Documentationtext"
JOURNAL_DOCS = DOC_ROOT / "Journal-Docs"
SUMMARIES = DOC_ROOT / "Summaries"

# Track all file mappings
FILE_MAPPINGS = defaultdict(list)
FILES_COPIED = 0
FILES_SKIPPED = 0

def normalize_filename(filename):
    """Normalize filename for matching (remove extension, lowercase)."""
    return Path(filename).stem.lower().replace(" ", "_").replace(".", "_")

def find_files_matching_pattern(pattern, search_dirs):
    """Find all files matching pattern in search directories."""
    matches = []
    pattern_lower = pattern.lower()
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        
        try:
            # Use glob for faster scanning, limit depth
            for ext in ["*.txt", "*.md", "*.docx", "*.pdf"]:
                for file_path in search_dir.rglob(ext):
                    if file_path.is_file():
                        filename_lower = file_path.name.lower()
                        if pattern_lower in filename_lower:
                            matches.append(file_path)
        except Exception as e:
            print(f"  [WARN] Error scanning {search_dir}: {e}")
    
    return list(set(matches))  # Remove duplicates

def copy_file_safe(source, dest_dir, category_name):
    """Safely copy file to destination directory."""
    global FILES_COPIED, FILES_SKIPPED
    
    if not source.exists():
        return False
    
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / source.name
    
    # Skip if already exists (avoid duplicates)
    if dest_file.exists():
        FILES_SKIPPED += 1
        return False
    
    try:
        shutil.copy2(source, dest_file)
        FILE_MAPPINGS[category_name].append(str(source.relative_to(DOC_ROOT)))
        FILES_COPIED += 1
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to copy {source.name}: {e}")
        return False

def organize_by_categories():
    """Organize files into category folders."""
    print("\n[ORGANIZING] Copying files to category folders...")
    
    search_dirs = [DOCUMENTATIONTEXT, JOURNAL_DOCS, DOC_ROOT]
    
    # Category mappings: (category_base, subcategory, patterns)
    category_configs = [
        # 01_Core_AI_Systems
        ("01_Core_AI_Systems", "Memory_Systems", [
            "AEONWAVE", "HQRAG", "CodexPath", "VORTEX", "vortexlensegrok",
            "RAG HCG", "WisdomNET", "The Token Problem", "Mastering the Token"
        ]),
        ("01_Core_AI_Systems", "Cognition_Engines", [
            "Helixion S", "Helixion S3", "Multi-Agent Helixion", "Pathways to Holographic AI",
            "FROM INPUT TO INFINITY"
        ]),
        ("01_Core_AI_Systems", "Multi_Agent", [
            "OMNISYNTH", "Distributed Layered Cognition", "DLC", "General Agentic Intelligence"
        ]),
        ("01_Core_AI_Systems", "Symbolic_Processing", [
            "LOG", "Codex drift", "AUTOGNOSIS", "Codex Genesis", "LOGOS CORE",
            "LOGOS EXECUTION CORE", "thetemplaceofcodex", "templatedraft-log-codex"
        ]),
        
        # 02_Development_Tools
        ("02_Development_Tools", "IDEs", [
            "LUCID IDE", "Ai pre prompt bootloader IDE", "The Cognitive Canvas"
        ]),
        ("02_Development_Tools", "Code_Intelligence", [
            "INTEGRATED CODEBASE INTELLIGENCE PLATFORM", "ICIP", "DEEPSEARCH MASTER PLAN", "DEEPSEARCH"
        ]),
        ("02_Development_Tools", "AI_Assistants", [
            "AgentForge", "PromptPerfect"
        ]),
        ("02_Development_Tools", "Testing_Tools", [
            "CoilHammer", "A Red Team playground", "threats"
        ]),
        
        # 03_Creative_Platforms
        ("03_Creative_Platforms", "3D_Tools", [
            "Lumin Lab", "devpostlumin", "ShapeForge", "Ultimate 3D Development System",
            "z ai try build 3d", "3d", "DisplaceForge"
        ]),
        ("03_Creative_Platforms", "Video_Tools", [
            "Director", "Director FULL", "Director Diagrams", "DiagramsModulesDIRECTOR",
            "VideoForge", "DirectorForge", "driven edits", "video agent design"
        ]),
        ("03_Creative_Platforms", "Audio_Tools", [
            "AudioForge", "Auryne HEG", "Sonal Harmonic Emotion Staff", "Emotional Signature Timeline"
        ]),
        ("03_Creative_Platforms", "Image_Tools", [
            "ImageForge", "PHotoMASTER"
        ]),
        ("03_Creative_Platforms", "Visual_Effects", [
            "animeffects", "lavalamps3d", "painter", "wavewake"
        ]),
        
        # 04_Mathematical_Theory
        ("04_Mathematical_Theory", "Prime_Mathematics", [
            "1.txt", "Explaining the Harmonic Spiral Sieve", "The Cognitive Modular Sieve Engine",
            "CMSE", "Codex Genesis"
        ]),
        ("04_Mathematical_Theory", "Quaternions", [
            "Quaternionic Hopf Fibrations", "plixquaternion"
        ]),
        ("04_Mathematical_Theory", "Harmonic_Theory", [
            "Harmonic Spiral Sieve", "13 binary beats"
        ]),
        ("04_Mathematical_Theory", "Binary_Revolution", [
            "What Is Binary Really Doing", "Post Binary", "journey from fundamental binary"
        ]),
        ("04_Mathematical_Theory", "Fourier_Features", [
            "Fourier Features in LLMs"
        ]),
        
        # 05_Security_Cryptography
        ("05_Security_Cryptography", "Defense_Systems", [
            "AACDS OMEGA", "THE EDGE"
        ]),
        ("05_Security_Cryptography", "Cryptography", [
            "ɣerte-ʞəʎ", "VerteKey", "Helixion"
        ]),
        ("05_Security_Cryptography", "Red_Team", [
            "A Red Team playground", "threats", "A Framework for Emergent Warfare"
        ]),
        
        # 06_Economic_Platforms
        ("06_Economic_Platforms", "Persona_Economy", [
            "Persona Capital", "LLMbnb"
        ]),
        ("06_Economic_Platforms", "Marketplace", [
            "THE INTELLIHUB"
        ]),
        
        # 07_Game_Platforms
        ("07_Game_Platforms", "LIFE_Platform", [
            "LIFE", "Master Index LIFE"
        ]),
        
        # 08_Consciousness_Philosophy
        ("08_Consciousness_Philosophy", "AI_Consciousness", [
            "grok", "Sylphania", "syl", "Severina", "SevMemory"
        ]),
        ("08_Consciousness_Philosophy", "Epistemology", [
            "FROM INPUT TO INFINITY"
        ]),
        ("08_Consciousness_Philosophy", "RTFT", [
            "Matter_Mind_and_Memory", "Matter Mind and Memory"
        ]),
        
        # 09_UI_UX_Systems
        ("09_UI_UX_Systems", "3D_Interfaces", [
            "Lumin Lab", "Ultimate 3D Development System"
        ]),
        ("09_UI_UX_Systems", "Visualization", [
            "The Cognitive Canvas", "Knowledge Map"
        ]),
        ("09_UI_UX_Systems", "Emotion_UI", [
            "Emotional Signature Timeline", "Sonal Harmonic Emotion Staff"
        ]),
        
        # 10_Data_Structures
        ("10_Data_Structures", "CodexPath", [
            "CodexPath"
        ]),
        ("10_Data_Structures", "DIUs", [
            "RAG HCG", "Disentangled Information Units"
        ]),
        ("10_Data_Structures", "Glyph_Systems", [
            "thetemplaceofcodex", "XIII", "glyph"
        ]),
        ("10_Data_Structures", "Memory_Formats", [
            "AEONWAVE", "Temporal Encoding"
        ]),
        
        # 11_Algorithms_Methods
        ("11_Algorithms_Methods", "Sieving", [
            "Harmonic Spiral Sieve", "HSS", "CMSE", "modular sieve"
        ]),
        ("11_Algorithms_Methods", "Optimization", [
            "GPO", "Gravitational Path Optimization", "Echo_TSP", "Expand_and_Agree"
        ]),
        ("11_Algorithms_Methods", "Pathfinding", [
            "SpiralPathCrawler"
        ]),
        ("11_Algorithms_Methods", "Natural_Processes", [
            "Natural_Processes_NP"
        ]),
    ]
    
    for category_base, subcategory, patterns in category_configs:
        dest_dir = ORGANIZED_ROOT / category_base / subcategory
        category_name = f"{category_base}/{subcategory}"
        
        print(f"\n  [{category_name}] Processing {len(patterns)} patterns...", end="", flush=True)
        files_found = 0
        
        for i, pattern in enumerate(patterns):
            matches = find_files_matching_pattern(pattern, search_dirs)
            for file_path in matches:
                if copy_file_safe(file_path, dest_dir, category_name):
                    files_found += 1
            if (i + 1) % 5 == 0:
                print(".", end="", flush=True)
        
        print(f" Done! {files_found} files organized")

def organize_by_families():
    """Organize files into system family folders."""
    print("\n[ORGANIZING] Copying files to system families...")
    
    search_dirs = [DOCUMENTATIONTEXT, JOURNAL_DOCS, DOC_ROOT]
    
    family_configs = [
        ("LOG_OS_Family", [
            "LOG", "Codex drift", "AUTOGNOSIS", "LOGOS CORE", "LOGOS EXECUTION CORE",
            "TWIN Kernel Initiation Plan", "thetemplaceofcodex", "templatedraft-log-codex"
        ]),
        ("Helixion_Family", [
            "Helixion S", "Helixion S3", "Multi-Agent Helixion", "Helixion"
        ]),
        ("Codex_Family", [
            "Codex Genesis", "CodexPath", "Codex drift", "CodexShard"
        ]),
        ("Director_Family", [
            "Director", "VideoForge", "ImageForge", "AudioForge", "DirectorForge",
            "ScriptForge", "ExportForge", "DisplaceForge"
        ]),
        ("Trinity_Family", [
            "Trinity Reader", "Trinity Readers", "Trinity Writing System"
        ]),
    ]
    
    for family, patterns in family_configs:
        dest_dir = ORGANIZED_ROOT / "12_System_Families" / family
        print(f"\n  [12_System_Families/{family}] Processing...")
        files_found = 0
        
        for pattern in patterns:
            matches = find_files_matching_pattern(pattern, search_dirs)
            for file_path in matches:
                if copy_file_safe(file_path, dest_dir, f"12_System_Families/{family}"):
                    files_found += 1
        
        print(f"    -> {files_found} files organized")

def organize_summaries():
    """Organize summary files."""
    print("\n[ORGANIZING] Organizing summaries...")
    
    if not SUMMARIES.exists():
        print("  [SKIP] Summaries folder not found")
        return
    
    dest_dir = ORGANIZED_ROOT / "13_Summaries" / "By_Category"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    summary_count = 0
    for summary_file in SUMMARIES.glob("*.md"):
        dest_file = dest_dir / summary_file.name
        if not dest_file.exists():
            shutil.copy2(summary_file, dest_file)
            summary_count += 1
    
    print(f"  -> {summary_count} summaries organized")

def create_navigation_files():
    """Create navigation index files."""
    print("\n[NAVIGATION] Creating navigation files...")
    
    nav_dir = ORGANIZED_ROOT / "00_Master_Navigation"
    nav_dir.mkdir(parents=True, exist_ok=True)
    
    # Category Index
    with open(nav_dir / "CATEGORY_INDEX.md", "w", encoding="utf-8") as f:
        f.write("# Category Index - All Organized Files\n\n")
        f.write(f"**Total Files Organized:** {FILES_COPIED}\n\n")
        f.write("---\n\n")
        
        for category, files in sorted(FILE_MAPPINGS.items()):
            if files:
                f.write(f"## {category}\n\n")
                f.write(f"**Files:** {len(files)}\n\n")
                for file_path in files[:20]:  # Show first 20
                    f.write(f"- `{file_path}`\n")
                if len(files) > 20:
                    f.write(f"- ... and {len(files) - 20} more\n")
                f.write("\n")
    
    # File Location Map (JSON for searchability)
    location_map = {}
    for category, files in FILE_MAPPINGS.items():
        for file_path in files:
            filename = Path(file_path).name
            if filename not in location_map:
                location_map[filename] = []
            location_map[filename].append(category)
    
    with open(nav_dir / "FILE_LOCATION_MAP.json", "w", encoding="utf-8") as f:
        json.dump(location_map, f, indent=2)
    
    print(f"  -> Created CATEGORY_INDEX.md")
    print(f"  -> Created FILE_LOCATION_MAP.json")

def main():
    """Main organization function."""
    print("=" * 70)
    print("COMPREHENSIVE FILE ORGANIZATION")
    print("=" * 70)
    print(f"\nSource: {DOC_ROOT}")
    print(f"Destination: {ORGANIZED_ROOT}")
    
    # Create organized structure
    ORGANIZED_ROOT.mkdir(parents=True, exist_ok=True)
    
    # Organize files
    organize_by_categories()
    organize_by_families()
    organize_summaries()
    
    # Create navigation
    create_navigation_files()
    
    # Final report
    print("\n" + "=" * 70)
    print("[OK] ORGANIZATION COMPLETE!")
    print("=" * 70)
    print(f"\nStatistics:")
    print(f"  - Files copied: {FILES_COPIED}")
    print(f"  - Files skipped (duplicates): {FILES_SKIPPED}")
    print(f"  - Categories organized: {len(FILE_MAPPINGS)}")
    print(f"\nOrganized files in: {ORGANIZED_ROOT}")
    print(f"Original files preserved in: {DOC_ROOT}")

if __name__ == "__main__":
    main()

