#!/usr/bin/env python3
"""
Remove transitional banners and update frontmatter from T-level docs.
Usage: python scripts/cutover/remove_banners.py
"""

import re
from pathlib import Path

# Banner patterns (order matters)
BANNER_PATTERNS = [
    r"<!---\s*TRANSITIONAL T-LEVEL DOCUMENT.*?--->",
    r"---\s*\n\*\*TRANSITIONAL.*?\n---",
    r"<!--\s*TRANSITIONAL.*?-->",
]

def update_file(file_path: Path):
    """Remove banners and update frontmatter."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        
        # Remove banners
        for pattern in BANNER_PATTERNS:
            content = re.sub(pattern, "", content, flags=re.DOTALL | re.IGNORECASE)
        
        # Update frontmatter level field (T0 → L0, etc.)
        content = re.sub(r"level:\s*T(\d)", r"level: L\1", content)
        
        # Update frontmatter status field
        content = re.sub(r"status:\s*draft", "status: complete", content, flags=re.IGNORECASE)
        content = re.sub(r"status:\s*transitional", "status: complete", content, flags=re.IGNORECASE)
        
        # Update headers if they reference T-level
        content = re.sub(r"# T(\d)", r"# L\1", content)
        
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
    systems_dir = Path("knowledge_architecture/systems")
    updated_count = 0
    
    if not systems_dir.exists():
        print(f"❌ Systems directory not found: {systems_dir}")
        return
    
    print("🔄 Removing transitional banners and updating frontmatter...")
    print()
    
    # Update all L-level files (renamed from T-level)
    for system_dir in sorted(systems_dir.iterdir()):
        if system_dir.is_dir():
            for level_file in ["L0_executive.md", "L1_overview.md", "L2_architecture.md", "L3_detailed.md", "L4_complete.md", "L6_complete.md"]:
                file_path = system_dir / level_file
                if file_path.exists():
                    if update_file(file_path):
                        updated_count += 1
    
    print()
    if updated_count > 0:
        print(f"✅ Updated {updated_count} files")
    else:
        print("ℹ️  No files required updates")

if __name__ == "__main__":
    main()

