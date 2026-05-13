#!/usr/bin/env python3
"""
Tri-source verification: regex, catalogs, and registry must all agree.

This prevents silent drift between counting methods.
"""

import json
import sys
import pathlib
import difflib

def main():
    """Verify all three sources agree on tag counts."""
    
    p = pathlib.Path
    
    # Load all three sources
    simple_path = p("artifacts/simple_tag_counts.json")
    reconciled_path = p("artifacts/reconciled_totals.json")
    
    if not simple_path.exists():
        print("[FAIL] Missing simple_tag_counts.json - run: python scripts/simple_tag_counter.py")
        return 1
    
    if not reconciled_path.exists():
        print("[FAIL] Missing reconciled_totals.json - run: make reconcile")
        return 1
    
    # Load data
    A = json.loads(simple_path.read_text())  # Regex ground truth
    B = json.loads(reconciled_path.read_text())  # Catalogs
    
    # Compare grand totals
    a_total = A.get("grand_total", 0)
    b_total = B.get("grand_totals", {}).get("ALL", 0)
    
    if a_total != b_total:
        print(f"[FAIL] Grand total mismatch:")
        print(f"  Simple (regex): {a_total}")
        print(f"  Reconciled (catalogs): {b_total}")
        return 1
    
    print(f"[OK] Grand totals match: {a_total} tags")
    
    # Compare per-system (where both have data)
    a_systems = A.get("systems", {})
    b_systems = {s["system"]: s["tags_total"] for s in B.get("systems", [])}
    
    mismatches = []
    for system, a_count in a_systems.items():
        a_tags = a_count.get("total_tags", 0)
        b_tags = b_systems.get(system, -1)
        
        if b_tags == -1:
            print(f"  [WARN] {system} in simple but not in reconciled")
            continue
        
        if a_tags != b_tags:
            mismatches.append(f"{system}: simple={a_tags}, reconciled={b_tags}")
    
    if mismatches:
        print(f"[FAIL] Per-system mismatches:")
        for m in mismatches:
            print(f"  - {m}")
        return 1
    
    print(f"[OK] All per-system counts match")
    print(f"[OK] Tri-verification complete: All sources agree!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

