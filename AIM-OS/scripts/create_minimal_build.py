#!/usr/bin/env python3
"""
Create Minimal Build Script

Creates a clean copy of AIM-OS containing only:
- Source code we wrote
- Documentation we wrote
- Essential configuration files
- Required data files

Excludes:
- node_modules/
- __pycache__/
- dist/ build artifacts
- Backup files
- Test artifacts
- Temporary files
- Large binary files
"""

import os
import shutil
import json
from pathlib import Path
from typing import Set, List, Tuple

# Base directory
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "aim-os-minimal"

# Patterns to exclude
EXCLUDE_PATTERNS = {
    # Dependencies
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "env",
    ".env",
    "ENV",
    
    # Build artifacts
    "dist",
    "build",
    ".next",
    "out",
    "coverage",
    "htmlcov",
    ".coverage",
    "*.egg-info",
    
    # IDE/Editor
    ".vscode",
    ".idea",
    ".cursor",
    "*.swp",
    "*.swo",
    "*~",
    
    # OS
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    
    # Logs
    "*.log",
    "logs",
    
    # Temporary
    ".tmp",
    "tmp",
    "temp",
    ".temp",
    
    # Backups
    "*.backup",
    "backups",
    "backup",
    
    # Database files (unless essential)
    "*.db-shm",
    "*.db-wal",
    
    # Test artifacts
    ".pytest_cache",
    "htmlcov",
    "coverage.xml",
    
    # Large binary/test data
    "codex",
    "codex_workspace",
    "snapshots",
    "test_mcp_memory",
    "test_mcp_configs",
    
    # Archive/legacy
    "archive",
    "legacy_docs",
    
    # OneDrive metadata
    "~$*",
    
    # Git
    ".git",
}

# File extensions to exclude
EXCLUDE_EXTENSIONS = {
    ".map",  # Source maps
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".exe",
    ".egg",
    ".whl",
}

# Directories to exclude completely
EXCLUDE_DIRECTORIES = {
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".next",
    "out",
    "htmlcov",
    "coverage",
    "logs",
    "backups",
    "backup",
    "codex",
    "codex_workspace",
    "snapshots",
    "test_mcp_memory",
    "test_mcp_configs",
    "archive",
    "legacy_docs",
    ".git",
    ".vscode",
    ".idea",
    ".cursor",
    "tmp",
    "temp",
    ".tmp",
    ".temp",
}

# Essential files to always include
ESSENTIAL_FILES = {
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    "package.json",
    "tsconfig.json",
    ".gitignore",
    "lucid_mcp_server.py",
    "LAUNCH_ELECTRON.bat",
    "LAUNCH_ELECTRON_DEV.bat",
}

# Essential directories to include
ESSENTIAL_DIRECTORIES = {
    "packages",
    "knowledge_architecture",
    "goals",
    "scripts",
    "cursor-addon",
    "daemon_rag_system",
}

def should_exclude(path: Path) -> bool:
    """Check if path should be excluded"""
    # Check if it's an excluded directory name
    if path.name in EXCLUDE_DIRECTORIES:
        return True
    
    # Check if it matches an exclude pattern
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    
    # Check extension
    if path.suffix in EXCLUDE_EXTENSIONS:
        return True
    
    # Check if it's a backup file
    if path.name.endswith(".backup"):
        return True
    
    return False

def should_include(path: Path) -> bool:
    """Check if path should be included"""
    # Always include essential files
    if path.name in ESSENTIAL_FILES:
        return True
    
    # Check if it's in an essential directory
    parts = path.parts
    for essential_dir in ESSENTIAL_DIRECTORIES:
        if essential_dir in parts:
            return True
    
    return False

def get_file_stats(path: Path) -> dict:
    """Get file statistics"""
    try:
        stat = path.stat()
        return {
            "size": stat.st_size,
            "modified": stat.st_mtime,
        }
    except Exception:
        return {"size": 0, "modified": 0}

def create_minimal_build():
    """Create minimal build"""
    print(f"Creating minimal build in: {OUTPUT_DIR}")
    
    # Remove existing output
    if OUTPUT_DIR.exists():
        print(f"Removing existing {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Track what we're copying
    copied_files: List[Tuple[str, int]] = []
    excluded_count = 0
    total_size = 0
    
    # Walk through source directory
    for root, dirs, files in os.walk(BASE_DIR):
        root_path = Path(root)
        
        # Skip output directory
        if OUTPUT_DIR in root_path.parents or OUTPUT_DIR == root_path:
            continue
        
        # Filter directories
        dirs[:] = [d for d in dirs if not should_exclude(root_path / d)]
        
        # Create relative path
        try:
            rel_path = root_path.relative_to(BASE_DIR)
        except ValueError:
            continue
        
        # Create output directory
        output_subdir = OUTPUT_DIR / rel_path
        output_subdir.mkdir(parents=True, exist_ok=True)
        
        # Copy files
        for file in files:
            file_path = root_path / file
            
            # Skip if excluded
            if should_exclude(file_path):
                excluded_count += 1
                continue
            
            # Include if essential or in essential directory
            if should_include(file_path) or rel_path.parts[0] in ESSENTIAL_DIRECTORIES:
                try:
                    output_file = output_subdir / file
                    shutil.copy2(file_path, output_file)
                    
                    file_size = get_file_stats(file_path)["size"]
                    copied_files.append((str(rel_path / file), file_size))
                    total_size += file_size
                except Exception as e:
                    print(f"Warning: Could not copy {file_path}: {e}")
    
    # Create manifest
    manifest = {
        "total_files": len(copied_files),
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "excluded_files": excluded_count,
        "files": sorted(copied_files, key=lambda x: x[0]),
    }
    
    manifest_path = OUTPUT_DIR / "MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    
    print("\n[SUCCESS] Minimal build created!")
    print(f"   Location: {OUTPUT_DIR}")
    print(f"   Files copied: {len(copied_files)}")
    print(f"   Files excluded: {excluded_count}")
    print(f"   Total size: {manifest['total_size_mb']} MB")
    print(f"   Manifest: {manifest_path}")
    
    return manifest

if __name__ == "__main__":
    create_minimal_build()

