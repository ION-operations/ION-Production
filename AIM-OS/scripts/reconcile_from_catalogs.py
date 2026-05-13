#!/usr/bin/env python3
"""
Reconcile tag counts from NL_TAG_CATALOG.md files (source of truth).

Bypasses CMC/registry imports to get reliable counts.
"""

from pathlib import Path
import json
import re

SYSTEMS = {
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

def extract_catalog_stats(catalog_path: Path) -> dict:
    """Extract tag statistics from a catalog file."""
    content = catalog_path.read_text(encoding='utf-8')
    
    stats = {
        "total_tags": 0,
        "files_tagged": 0,
        "by_type": {
            "NL_TAG": 0,
            "NL_TAG_INTENT": 0,
            "NL_TAG_CONNECT": 0,
            "NL_TAG_SPEC": 0
        }
    }
    
    # Extract from frontmatter or summary
    if match := re.search(r'total_tags:\s*(\d+)', content):
        stats["total_tags"] = int(match.group(1))
    
    if match := re.search(r'files_tagged:\s*(\d+)', content):
        stats["files_tagged"] = int(match.group(1))
    
    # Extract by type
    if match := re.search(r'primary_tags:\s*(\d+)', content):
        stats["by_type"]["NL_TAG"] = int(match.group(1))
    
    if match := re.search(r'intent_tags:\s*(\d+)', content):
        stats["by_type"]["NL_TAG_INTENT"] = int(match.group(1))
    
    if match := re.search(r'connect_tags:\s*(\d+)', content):
        stats["by_type"]["NL_TAG_CONNECT"] = int(match.group(1))
    
    if match := re.search(r'spec_tags:\s*(\d+)', content):
        stats["by_type"]["NL_TAG_SPEC"] = int(match.group(1))
    
    return stats

def main():
    """Generate reconciled totals from catalog files."""
    print("[RECONCILE] Analyzing NL_TAG_CATALOG.md files...", flush=True)
    
    root = Path("knowledge_architecture/systems")
    
    grand_totals = {
        "ALL": 0,
        "NL_TAG": 0,
        "NL_TAG_INTENT": 0,
        "NL_TAG_CONNECT": 0,
        "NL_TAG_SPEC": 0
    }
    
    files_total = 0
    systems_data = []
    
    for folder, display_name in SYSTEMS.items():
        catalog_path = root / folder / "NL_TAG_CATALOG.md"
        
        if not catalog_path.exists():
            print(f"  [WARN] {display_name}: No catalog found", flush=True)
            continue
        
        stats = extract_catalog_stats(catalog_path)
        
        systems_data.append({
            "system": display_name,
            "folder": folder,
            "files_tagged": stats["files_tagged"],
            "tags_total": stats["total_tags"],
            "by_type": stats["by_type"]
        })
        
        # Update grand totals
        grand_totals["ALL"] += stats["total_tags"]
        for tag_type, count in stats["by_type"].items():
            grand_totals[tag_type] += count
        
        files_total += stats["files_tagged"]
        
        print(f"  [OK] {display_name}: {stats['total_tags']} tags across {stats['files_tagged']} files", flush=True)
    
    # Build output
    output = {
        "session_id": "quintet_parity:2025-11-04",
        "generated": "2025-11-04T21:00:00Z",
        "source": "NL_TAG_CATALOG.md files (generated catalogs)",
        "method": "Extracted from catalog frontmatter and statistics",
        "grand_totals": grand_totals,
        "files_total": files_total,
        "systems": systems_data,
        "note": "These are the CANONICAL numbers. All documentation must match these exactly."
    }
    
    # Write to artifacts
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    
    output_path = artifacts_dir / "reconciled_totals.json"
    output_path.write_text(json.dumps(output, indent=2), encoding='utf-8')
    
    print(f"\n[OK] Wrote reconciled totals to: {output_path}", flush=True)
    print(f"\nGRAND TOTALS (SOURCE OF TRUTH):", flush=True)
    print(f"  Total Tags: {grand_totals['ALL']}")
    print(f"  Total Files: {files_total}")
    print(f"  By Type:")
    print(f"    NL_TAG: {grand_totals['NL_TAG']}")
    print(f"    NL_TAG_INTENT: {grand_totals['NL_TAG_INTENT']}")
    print(f"    NL_TAG_CONNECT: {grand_totals['NL_TAG_CONNECT']}")
    print(f"    NL_TAG_SPEC: {grand_totals['NL_TAG_SPEC']}")
    
    return output

if __name__ == "__main__":
    main()

