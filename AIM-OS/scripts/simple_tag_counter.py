#!/usr/bin/env python3
"""
Simple, reliable tag counter - parses files directly.

Bypasses UniversalTagRegistry to get accurate counts.
"""

from pathlib import Path
import re
import json

TAG_PATTERN = r'#\s*NL_TAG(?:_(\w+))?\s*:\s*([A-Z]+-[A-Z0-9]+-\d+)\s*\|'

def count_tags_in_file(file_path: Path) -> int:
    """Count NL tags in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        matches = re.findall(TAG_PATTERN, content)
        return len(matches)
    except:
        return 0

def count_tags_in_system(system_path: str) -> dict:
    """Count all tags in a system."""
    base = Path(system_path)
    
    total = 0
    files_with_tags = 0
    
    for py_file in base.rglob("*.py"):
        # Skip test files and __pycache__
        if '__pycache__' in str(py_file) or 'venv' in str(py_file):
            continue
        
        count = count_tags_in_file(py_file)
        if count > 0:
            total += count
            files_with_tags += 1
            print(f"  {py_file.name}: {count} tags", flush=True)
    
    return {
        "total_tags": total,
        "files_tagged": files_with_tags
    }

def main():
    """Count tags for all core systems."""
    systems = {
        "vif": "VIF",
        "cmc_service": "CMC",
        "hhni": "HHNI",
        "apoe": "APOE",
        "seg": "SEG",
        "sdfcvf": "SDF-CVF",
        "cas": "CAS",
        "timeline_context_system": "TCS",
        "intuitive_intelligence_system": "IIS"
    }
    
    results = {}
    grand_total = 0
    grand_files = 0
    
    for folder, name in systems.items():
        print(f"\n{name} ({folder}):")
        path = f"packages/{folder}"
        
        if not Path(path).exists():
            print(f"  [SKIP] Path not found")
            continue
        
        stats = count_tags_in_system(path)
        results[name] = stats
        
        grand_total += stats["total_tags"]
        grand_files += stats["files_tagged"]
        
        print(f"  TOTAL: {stats['total_tags']} tags across {stats['files_tagged']} files")
    
    print(f"\n========================================")
    print(f"GRAND TOTAL: {grand_total} tags")
    print(f"FILES TOTAL: {grand_files} files")
    print(f"========================================")
    
    # Save results
    output = {
        "grand_total": grand_total,
        "grand_files": grand_files,
        "systems": results
    }
    
    Path("artifacts/simple_tag_counts.json").write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(f"\n[OK] Saved to artifacts/simple_tag_counts.json")

if __name__ == "__main__":
    main()

