#!/usr/bin/env python3
"""
Comprehensive File Organization Script
Organizes all documentation files by category and relationship
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set

# Base paths
DOC_ROOT = Path(__file__).parent.parent / "Documentation"
ORGANIZED_ROOT = DOC_ROOT / "00_Organized"
DOCUMENTATIONTEXT = DOC_ROOT / "Documentationtext"
JOURNAL_DOCS = DOC_ROOT / "Journal-Docs"
SUMMARIES = DOC_ROOT / "Summaries"

# Category mappings (file patterns → category folders)
CATEGORY_MAPPINGS = {
    # 01_Core_AI_Systems
    "Memory_Systems": [
        "AEONWAVE", "HQRAG", "CMC", "HHNI", "CodexPath", "VORTEX", "vortexlensegrok",
        "RAG HCG", "WisdomNET", "The Token Problem", "Mastering the Token"
    ],
    "Cognition_Engines": [
        "Helixion S", "Helixion S3", "Multi-Agent Helixion", "Pathways to Holographic AI",
        "FROM INPUT TO INFINITY"
    ],
    "Multi_Agent": [
        "OMNISYNTH", "Distributed Layered Cognition", "DLC", "General Agentic Intelligence",
        "Multi-Agent Helixion"
    ],
    "Symbolic_Processing": [
        "LOG", "Codex drift", "AUTOGNOSIS", "Codex Genesis", "LOGOS CORE",
        "LOGOS EXECUTION CORE", "thetemplaceofcodex", "templatedraft-log-codex"
    ],
    
    # 02_Development_Tools
    "IDEs": [
        "LUCID IDE", "Ai pre prompt bootloader IDE", "The Cognitive Canvas"
    ],
    "Code_Intelligence": [
        "INTEGRATED CODEBASE INTELLIGENCE PLATFORM", "ICIP", "DEEPSEARCH MASTER PLAN", "DEEPSEARCH"
    ],
    "AI_Assistants": [
        "AgentForge", "PromptPerfect"
    ],
    "Testing_Tools": [
        "CoilHammer", "A Red Team playground", "threats"
    ],
    
    # 03_Creative_Platforms
    "3D_Tools": [
        "Lumin Lab", "devpostlumin", "ShapeForge", "Ultimate 3D Development System",
        "z ai try build 3d", "3d", "DisplaceForge"
    ],
    "Video_Tools": [
        "Director", "Director FULL", "Director Diagrams", "DiagramsModulesDIRECTOR",
        "VideoForge", "DirectorForge", "driven edits", "video agent design"
    ],
    "Audio_Tools": [
        "AudioForge", "Auryne HEG", "Sonal Harmonic Emotion Staff", "Emotional Signature Timeline"
    ],
    "Image_Tools": [
        "ImageForge", "PHotoMASTER"
    ],
    "Visual_Effects": [
        "animeffects", "lavalamps3d", "painter", "wavewake"
    ],
    
    # 04_Mathematical_Theory
    "Prime_Mathematics": [
        "1.txt", "Explaining the Harmonic Spiral Sieve", "The Cognitive Modular Sieve Engine",
        "CMSE", "Codex Genesis"
    ],
    "Quaternions": [
        "Quaternionic Hopf Fibrations", "plixquaternion"
    ],
    "Harmonic_Theory": [
        "Harmonic Spiral Sieve", "13 binary beats", "Codex Genesis"
    ],
    "Binary_Revolution": [
        "What Is Binary Really Doing", "Post Binary", "journey from fundamental binary"
    ],
    "Fourier_Features": [
        "Fourier Features in LLMs"
    ],
    
    # 05_Security_Cryptography
    "Defense_Systems": [
        "AACDS OMEGA", "THE EDGE"
    ],
    "Cryptography": [
        "ɣerte-ʞəʎ", "VerteKey", "Helixion"
    ],
    "Authentication": [
        "NameCore", "EIDYN", "Dual-Name"
    ],
    "Red_Team": [
        "A Red Team playground", "threats", "A Framework for Emergent Warfare"
    ],
    
    # 06_Economic_Platforms
    "Persona_Economy": [
        "Persona Capital", "LLMbnb"
    ],
    "Marketplace": [
        "THE INTELLIHUB"
    ],
    
    # 07_Game_Platforms
    "LIFE_Platform": [
        "LIFE", "Master Index LIFE"
    ],
    "FSMC": [
        "FSMC", "Faction State Memory Core"
    ],
    "MOSL": [
        "MOSL", "Multiplayer Ops Synchro Layer"
    ],
    "Game_Systems": [
        "GCT", "SWE", "DRTS", "StorySync", "World War Clock"
    ],
    
    # 08_Consciousness_Philosophy
    "AI_Consciousness": [
        "grok", "Sylphania", "syl", "Severina", "SevMemory"
    ],
    "Epistemology": [
        "FROM INPUT TO INFINITY"
    ],
    "RTFT": [
        "Matter_Mind_and_Memory", "Matter Mind and Memory"
    ],
    
    # 09_UI_UX_Systems
    "3D_Interfaces": [
        "Lumin Lab", "Ultimate 3D Development System"
    ],
    "Visualization": [
        "The Cognitive Canvas", "Knowledge Map"
    ],
    "Emotion_UI": [
        "Emotional Signature Timeline", "Sonal Harmonic Emotion Staff"
    ],
    "Terminal_Systems": [
        "DRTS", "RitualShell"
    ],
    
    # 10_Data_Structures
    "CodexPath": [
        "CodexPath"
    ],
    "DIUs": [
        "RAG HCG", "Disentangled Information Units"
    ],
    "Glyph_Systems": [
        "thetemplaceofcodex", "XIII", "glyph"
    ],
    "Memory_Formats": [
        "AEONWAVE", "Temporal Encoding"
    ],
    
    # 11_Algorithms_Methods
    "Sieving": [
        "Harmonic Spiral Sieve", "HSS", "CMSE", "modular sieve"
    ],
    "Optimization": [
        "GPO", "Gravitational Path Optimization", "Echo_TSP", "Expand_and_Agree"
    ],
    "Pathfinding": [
        "SpiralPathCrawler"
    ],
    "Natural_Processes": [
        "Natural_Processes_NP"
    ],
}

# System family mappings
FAMILY_MAPPINGS = {
    "LOG_OS_Family": [
        "LOG", "Codex drift", "AUTOGNOSIS", "LOGOS CORE", "LOGOS EXECUTION CORE",
        "TWIN Kernel Initiation Plan", "thetemplaceofcodex", "templatedraft-log-codex"
    ],
    "Helixion_Family": [
        "Helixion S", "Helixion S3", "Multi-Agent Helixion", "Helixion"
    ],
    "Codex_Family": [
        "Codex Genesis", "CodexPath", "Codex drift", "CodexShard"
    ],
    "Director_Family": [
        "Director", "VideoForge", "ImageForge", "AudioForge", "DirectorForge",
        "ScriptForge", "ExportForge", "DisplaceForge"
    ],
    "Trinity_Family": [
        "Trinity Reader", "Trinity Readers", "Trinity Writing System"
    ],
}

def find_files_matching_pattern(pattern: str, search_dirs: List[Path]) -> List[Path]:
    """Find all files matching pattern in search directories."""
    matches = []
    pattern_lower = pattern.lower()
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
            
        for file_path in search_dir.rglob("*"):
            if file_path.is_file():
                filename_lower = file_path.name.lower()
                if pattern_lower in filename_lower:
                    matches.append(file_path)
    
    return matches

def organize_files():
    """Main organization function."""
    print("=" * 70)
    print("COMPREHENSIVE FILE ORGANIZATION")
    print("=" * 70)
    
    # Create organized structure
    print("\n[1/5] Creating folder structure...")
    create_folder_structure()
    
    # Map files to categories
    print("\n[2/5] Mapping files to categories...")
    file_mappings = map_files_to_categories()
    
    # Copy files to category folders
    print("\n[3/5] Copying files to category folders...")
    copy_files_to_categories(file_mappings)
    
    # Copy files to family folders
    print("\n[4/5] Copying files to system families...")
    copy_files_to_families(file_mappings)
    
    # Create navigation files
    print("\n[5/5] Creating navigation files...")
    create_navigation_files(file_mappings)
    
    print("\n" + "=" * 70)
    print("[OK] ORGANIZATION COMPLETE!")
    print("=" * 70)
    print(f"\nOrganized files in: {ORGANIZED_ROOT}")
    print(f"Original files preserved in: {DOC_ROOT}")

def create_folder_structure():
    """Create all category and family folders."""
    base_categories = [
        "01_Core_AI_Systems", "02_Development_Tools", "03_Creative_Platforms",
        "04_Mathematical_Theory", "05_Security_Cryptography", "06_Economic_Platforms",
        "07_Game_Platforms", "08_Consciousness_Philosophy", "09_UI_UX_Systems",
        "10_Data_Structures", "11_Algorithms_Methods", "12_System_Families",
        "13_Summaries", "99_Archive"
    ]
    
    for category in base_categories:
        category_path = ORGANIZED_ROOT / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        # Create subcategories
        if category in CATEGORY_MAPPINGS:
            for subcat in CATEGORY_MAPPINGS.keys():
                subcat_path = category_path / subcat
                subcat_path.mkdir(parents=True, exist_ok=True)
    
    # Create system family folders
    families_path = ORGANIZED_ROOT / "12_System_Families"
    for family in FAMILY_MAPPINGS.keys():
        (families_path / family).mkdir(parents=True, exist_ok=True)

def map_files_to_categories() -> Dict[str, List[Path]]:
    """Map files to their categories."""
    mappings: Dict[str, List[Path]] = {}
    search_dirs = [DOCUMENTATIONTEXT, JOURNAL_DOCS, DOC_ROOT]
    
    for category, patterns in CATEGORY_MAPPINGS.items():
        mappings[category] = []
        for pattern in patterns:
            matches = find_files_matching_pattern(pattern, search_dirs)
            mappings[category].extend(matches)
    
    return mappings

def copy_files_to_categories(file_mappings: Dict[str, List[Path]]):
    """Copy files to their category folders."""
    # Determine category base from subcategory name
    category_base_map = {
        "Memory_Systems": "01_Core_AI_Systems",
        "Cognition_Engines": "01_Core_AI_Systems",
        "Multi_Agent": "01_Core_AI_Systems",
        "Symbolic_Processing": "01_Core_AI_Systems",
        "IDEs": "02_Development_Tools",
        "Code_Intelligence": "02_Development_Tools",
        "AI_Assistants": "02_Development_Tools",
        "Testing_Tools": "02_Development_Tools",
        # ... (add all mappings)
    }
    
    for subcategory, files in file_mappings.items():
        if not files:
            continue
        
        # Find base category
        base_category = None
        for base, subs in [
            ("01_Core_AI_Systems", ["Memory_Systems", "Cognition_Engines", "Multi_Agent", "Symbolic_Processing"]),
            ("02_Development_Tools", ["IDEs", "Code_Intelligence", "AI_Assistants", "Testing_Tools"]),
            ("03_Creative_Platforms", ["3D_Tools", "Video_Tools", "Audio_Tools", "Image_Tools", "Visual_Effects"]),
            ("04_Mathematical_Theory", ["Prime_Mathematics", "Quaternions", "Harmonic_Theory", "Binary_Revolution", "Fourier_Features"]),
            ("05_Security_Cryptography", ["Defense_Systems", "Cryptography", "Authentication", "Red_Team"]),
            ("06_Economic_Platforms", ["Persona_Economy", "Marketplace"]),
            ("07_Game_Platforms", ["LIFE_Platform", "FSMC", "MOSL", "Game_Systems"]),
            ("08_Consciousness_Philosophy", ["AI_Consciousness", "Epistemology", "RTFT"]),
            ("09_UI_UX_Systems", ["3D_Interfaces", "Visualization", "Emotion_UI", "Terminal_Systems"]),
            ("10_Data_Structures", ["CodexPath", "DIUs", "Glyph_Systems", "Memory_Formats"]),
            ("11_Algorithms_Methods", ["Sieving", "Optimization", "Pathfinding", "Natural_Processes"]),
        ]:
            if subcategory in subs:
                base_category = base
                break
        
        if not base_category:
            continue
        
        dest_dir = ORGANIZED_ROOT / base_category / subcategory
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in files:
            if file_path.exists():
                dest_file = dest_dir / file_path.name
                if not dest_file.exists():
                    shutil.copy2(file_path, dest_file)
                    print(f"  Copied: {file_path.name} → {base_category}/{subcategory}/")

def copy_files_to_families(file_mappings: Dict[str, List[Path]]):
    """Copy files to system family folders."""
    families_path = ORGANIZED_ROOT / "12_System_Families"
    search_dirs = [DOCUMENTATIONTEXT, JOURNAL_DOCS, DOC_ROOT]
    
    for family, patterns in FAMILY_MAPPINGS.items():
        family_dir = families_path / family
        family_dir.mkdir(parents=True, exist_ok=True)
        
        for pattern in patterns:
            matches = find_files_matching_pattern(pattern, search_dirs)
            for file_path in matches:
                if file_path.exists():
                    dest_file = family_dir / file_path.name
                    if not dest_file.exists():
                        shutil.copy2(file_path, dest_file)
                        print(f"  Copied: {file_path.name} → 12_System_Families/{family}/")

def create_navigation_files(file_mappings: Dict[str, List[Path]]):
    """Create navigation index files."""
    nav_dir = ORGANIZED_ROOT / "00_Master_Navigation"
    nav_dir.mkdir(parents=True, exist_ok=True)
    
    # Create category index
    with open(nav_dir / "CATEGORY_INDEX.md", "w", encoding="utf-8") as f:
        f.write("# Category Index\n\n")
        for category, files in sorted(file_mappings.items()):
            if files:
                f.write(f"## {category}\n")
                f.write(f"**Files:** {len(files)}\n\n")
                for file_path in files[:10]:  # Show first 10
                    f.write(f"- {file_path.name}\n")
                if len(files) > 10:
                    f.write(f"- ... and {len(files) - 10} more\n")
                f.write("\n")

if __name__ == "__main__":
    organize_files()

