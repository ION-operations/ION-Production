#!/usr/bin/env python3
"""
Reconcile quintet session numbers from Universal Registry.

This script generates the SINGLE SOURCE OF TRUTH for all tag counts,
preventing human errors and drift.
"""

from pathlib import Path
import json
import sys

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.nl_tags.universal_registry import UniversalTagRegistry
from packages.cmc_service.api import MemoryStore

SYSTEM_KEY_ORDER = ["vif", "cmc", "apoe", "hhni", "seg", "sdfcvf", "cas", "timeline_context_system", "intuitive_intelligence_system"]

# System name mappings (folder → display name)
SYSTEM_DISPLAY_NAMES = {
    "vif": "VIF",
    "cmc_service": "CMC",
    "apoe": "APOE",
    "hhni": "HHNI",
    "seg": "SEG",
    "sdfcvf": "SDF-CVF",
    "cas": "CAS",
    "timeline_context_system": "TCS",
    "intuitive_intelligence_system": "IIS"
}

def main():
    """Generate reconciled totals from Universal Registry."""
    print("Reconciling quintet session numbers from source of truth...")
    
    # Initialize registry with CMC
    cmc = MemoryStore('mcp_memory/cmc.db')
    reg = UniversalTagRegistry(cmc)
    
    # Scan all packages
    print("Scanning codebase...")
    reg.scan_codebase('packages')
    
    # Get raw tags
    all_tags = list(reg.tags.values())
    
    # Count by system and type
    totals = {
        "ALL": 0,
        "NL_TAG": 0,
        "NL_TAG_INTENT": 0,
        "NL_TAG_CONNECT": 0,
        "NL_TAG_SPEC": 0
    }
    
    per_system = {}
    files_per_system = {}
    
    for tag in all_tags:
        system = tag.get("system", "UNSPEC")
        tag_type = tag.get("type", "NL_TAG")
        file_path = tag.get("file", "")
        
        # Initialize system if needed
        if system not in per_system:
            per_system[system] = {
                "ALL": 0,
                "NL_TAG": 0,
                "NL_TAG_INTENT": 0,
                "NL_TAG_CONNECT": 0,
                "NL_TAG_SPEC": 0
            }
            files_per_system[system] = set()
        
        # Count tags
        per_system[system]["ALL"] += 1
        per_system[system][tag_type] += 1
        totals["ALL"] += 1
        totals[tag_type] += 1
        
        # Track files
        if file_path:
            files_per_system[system].add(file_path)
    
    # Count unique files total
    all_files = set()
    for files in files_per_system.values():
        all_files.update(files)
    
    # Build output structure
    systems_data = []
    for system in SYSTEM_KEY_ORDER:
        if system in per_system:
            display_name = SYSTEM_DISPLAY_NAMES.get(system, system.upper())
            systems_data.append({
                "system": display_name,
                "folder": system,
                "files_tagged": len(files_per_system.get(system, set())),
                "tags_total": per_system[system]["ALL"],
                "by_type": {
                    "NL_TAG": per_system[system]["NL_TAG"],
                    "NL_TAG_INTENT": per_system[system]["NL_TAG_INTENT"],
                    "NL_TAG_CONNECT": per_system[system]["NL_TAG_CONNECT"],
                    "NL_TAG_SPEC": per_system[system]["NL_TAG_SPEC"]
                }
            })
    
    output = {
        "session_id": "quintet_parity:2025-11-04",
        "generated": "2025-11-04T21:00:00Z",
        "source": "UniversalTagRegistry (packages/nl_tags/universal_registry.py)",
        "grand_totals": totals,
        "files_total": len(all_files),
        "systems": systems_data
    }
    
    # Write to artifacts
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    
    output_path = artifacts_dir / "reconciled_totals.json"
    output_path.write_text(json.dumps(output, indent=2), encoding='utf-8')
    
    print(f"\n✅ Wrote reconciled totals to: {output_path}")
    print(f"\nGRAND TOTALS (SOURCE OF TRUTH):")
    print(f"  Total Tags: {totals['ALL']}")
    print(f"  Total Files: {len(all_files)}")
    print(f"\nPER SYSTEM:")
    for sys_data in systems_data:
        print(f"  {sys_data['system']}: {sys_data['tags_total']} tags across {sys_data['files_tagged']} files")
    
    return output

if __name__ == "__main__":
    main()

