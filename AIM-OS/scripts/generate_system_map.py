#!/usr/bin/env python3
"""
Generate Complete System File/Folder Map

Creates a comprehensive map of all files and folders in AIM-OS,
excluding only:
- node_modules
- __pycache__
- .git
- Temporary/build artifacts
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

# Base directory
BASE_DIR = Path(__file__).parent.parent
OUTPUT_FILE = BASE_DIR / "SYSTEM_MAP.json"
OUTPUT_TEXT = BASE_DIR / "SYSTEM_MAP.txt"

# Directories to skip
SKIP_DIRECTORIES = {
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".next",
    "out",
    "htmlcov",
    "coverage",
    ".coverage",
    ".vscode",
    ".idea",
    ".cursor",
}

def get_file_info(path: Path) -> dict:
    """Get file information"""
    try:
        stat = path.stat()
        return {
            "name": path.name,
            "path": str(path.relative_to(BASE_DIR)),
            "size_bytes": stat.st_size,
            "size_kb": round(stat.st_size / 1024, 2),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": path.suffix,
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
        }
    except Exception as e:
        return {
            "name": path.name,
            "path": str(path.relative_to(BASE_DIR)),
            "error": str(e),
        }

def generate_system_map():
    """Generate complete system map"""
    print(f"Generating system map...")
    
    system_map: Dict[str, List[dict]] = {}
    total_files = 0
    total_dirs = 0
    total_size = 0
    
    # Walk through directory
    for root, dirs, files in os.walk(BASE_DIR):
        root_path = Path(root)
        
        # Skip if in skip directory
        if any(skip in root_path.parts for skip in SKIP_DIRECTORIES):
            dirs[:] = []  # Don't traverse subdirectories
            continue
        
        # Get relative path
        try:
            rel_path = root_path.relative_to(BASE_DIR)
            rel_path_str = str(rel_path) if rel_path != Path(".") else "."
        except ValueError:
            continue
        
        # Filter directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRECTORIES]
        
        # Initialize directory entry
        if rel_path_str not in system_map:
            system_map[rel_path_str] = []
        
        # Add directories
        for dir_name in dirs:
            dir_path = root_path / dir_name
            dir_info = get_file_info(dir_path)
            dir_info["type"] = "directory"
            system_map[rel_path_str].append(dir_info)
            total_dirs += 1
        
        # Add files
        for file_name in files:
            file_path = root_path / file_name
            
            # Skip if in skip directory
            if any(skip in file_path.parts for skip in SKIP_DIRECTORIES):
                continue
            
            file_info = get_file_info(file_path)
            file_info["type"] = "file"
            system_map[rel_path_str].append(file_info)
            total_files += 1
            
            if "size_bytes" in file_info:
                total_size += file_info["size_bytes"]
    
    # Create summary
    summary = {
        "generated": datetime.now().isoformat(),
        "base_directory": str(BASE_DIR),
        "total_directories": total_dirs,
        "total_files": total_files,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "total_size_gb": round(total_size / (1024 * 1024 * 1024), 2),
        "directories_scanned": len(system_map),
        "excluded_directories": list(SKIP_DIRECTORIES),
    }
    
    # Combine summary and map
    full_map = {
        "summary": summary,
        "map": system_map,
    }
    
    # Write JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(full_map, f, indent=2)
    
    # Write text format
    with open(OUTPUT_TEXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("AIM-OS COMPLETE SYSTEM FILE/FOLDER MAP\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Generated: {summary['generated']}\n")
        f.write(f"Base Directory: {summary['base_directory']}\n\n")
        f.write(f"Summary:\n")
        f.write(f"  Total Directories: {summary['total_directories']}\n")
        f.write(f"  Total Files: {summary['total_files']}\n")
        f.write(f"  Total Size: {summary['total_size_mb']} MB ({summary['total_size_gb']} GB)\n")
        f.write(f"  Directories Scanned: {summary['directories_scanned']}\n\n")
        f.write(f"Excluded Directories: {', '.join(summary['excluded_directories'])}\n\n")
        f.write("=" * 80 + "\n\n")
        
        # Write directory tree
        for dir_path in sorted(system_map.keys()):
            if dir_path == ".":
                f.write("ROOT/\n")
            else:
                f.write(f"{dir_path}/\n")
            
            items = sorted(system_map[dir_path], key=lambda x: (x.get("type") == "directory", x["name"]))
            
            for item in items:
                item_type = "DIR" if item.get("type") == "directory" else "FILE"
                size_str = ""
                if "size_kb" in item:
                    size_str = f" ({item['size_kb']} KB)"
                f.write(f"  [{item_type}] {item['name']}{size_str}\n")
            
            f.write("\n")
    
    print("\n[SUCCESS] System map generated!")
    print(f"   JSON: {OUTPUT_FILE}")
    print(f"   Text: {OUTPUT_TEXT}")
    print(f"   Files: {total_files}")
    print(f"   Directories: {total_dirs}")
    print(f"   Total Size: {summary['total_size_mb']} MB ({summary['total_size_gb']} GB)")
    
    return full_map

if __name__ == "__main__":
    generate_system_map()

