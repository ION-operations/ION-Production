#!/usr/bin/env python3
"""System Audit Script - T0-T6 Conversion Status"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

def check_system_conversion_status(system_dir: Path) -> Dict:
    """Check T0-T6 conversion status for a system."""
    system_name = system_dir.name
    
    # Check for T-level docs
    t0_exists = (system_dir / "T0_executive.md").exists()
    t1_exists = (system_dir / "T1_overview.md").exists()
    t2_exists = (system_dir / "T2_architecture.md").exists()
    t3_exists = (system_dir / "T3_detailed.md").exists()
    t4_exists = (system_dir / "T4_complete.md").exists()
    
    # Check for L-level docs
    l0_exists = (system_dir / "L0_executive.md").exists()
    l1_exists = (system_dir / "L1_overview.md").exists()
    l2_exists = (system_dir / "L2_architecture.md").exists()
    l3_exists = (system_dir / "L3_detailed.md").exists()
    l4_exists = (system_dir / "L4_complete.md").exists()
    
    # Determine status
    t_levels = sum([t0_exists, t1_exists, t2_exists, t3_exists, t4_exists])
    l_levels = sum([l0_exists, l1_exists, l2_exists, l3_exists, l4_exists])
    
    if t_levels == 5:
        status = "COMPLETE"
    elif t_levels > 0:
        status = "PARTIAL"
    elif l_levels > 0:
        status = "NOT_CONVERTED"
    else:
        status = "NO_DOCS"
    
    return {
        "system": system_name,
        "status": status,
        "t_levels": t_levels,
        "l_levels": l_levels,
        "t0": t0_exists,
        "t1": t1_exists,
        "t2": t2_exists,
        "t3": t3_exists,
        "t4": t4_exists,
        "l0": l0_exists,
        "l1": l1_exists,
        "l2": l2_exists,
        "l3": l3_exists,
        "l4": l4_exists,
    }

def main():
    """Main audit function."""
    systems_dir = Path("knowledge_architecture/systems")
    
    if not systems_dir.exists():
        print(f"ERROR: Systems directory not found: {systems_dir}")
        return
    
    results = []
    
    # Check each system
    for system_dir in sorted(systems_dir.iterdir()):
        if system_dir.is_dir():
            status = check_system_conversion_status(system_dir)
            results.append(status)
    
    # Sort results by status
    status_order = {"COMPLETE": 0, "PARTIAL": 1, "NOT_CONVERTED": 2, "NO_DOCS": 3}
    results.sort(key=lambda x: (status_order.get(x["status"], 99), x["system"]))
    
    import sys
    import io
    
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Print results
    print("# T0-T6 Conversion Status Audit\n")
    print(f"Total Systems: {len(results)}\n")
    
    # Group by status
    complete = [r for r in results if r["status"] == "COMPLETE"]
    partial = [r for r in results if r["status"] == "PARTIAL"]
    not_converted = [r for r in results if r["status"] == "NOT_CONVERTED"]
    no_docs = [r for r in results if r["status"] == "NO_DOCS"]
    
    print(f"## [COMPLETE] ({len(complete)} systems)")
    for r in complete:
        print(f"- {r['system']}")
    
    print(f"\n## [PARTIAL] ({len(partial)} systems)")
    for r in partial:
        print(f"- {r['system']} (T-levels: {r['t_levels']}/5)")
    
    print(f"\n## [NOT CONVERTED] ({len(not_converted)} systems)")
    for r in not_converted:
        print(f"- {r['system']} (L-levels: {r['l_levels']}/5)")
    
    if no_docs:
        print(f"\n## [NO DOCS] ({len(no_docs)} systems)")
        for r in no_docs:
            print(f"- {r['system']}")
    
    # Detailed breakdown
    print("\n## DETAILED BREAKDOWN\n")
    print("| System | Status | T0 | T1 | T2 | T3 | T4 | L0 | L1 | L2 | L3 | L4 |")
    print("|--------|--------|----|----|----|----|----|----|----|----|----|----|")
    for r in results:
        t0 = "YES" if r['t0'] else "NO"
        t1 = "YES" if r['t1'] else "NO"
        t2 = "YES" if r['t2'] else "NO"
        t3 = "YES" if r['t3'] else "NO"
        t4 = "YES" if r['t4'] else "NO"
        l0 = "YES" if r['l0'] else "NO"
        l1 = "YES" if r['l1'] else "NO"
        l2 = "YES" if r['l2'] else "NO"
        l3 = "YES" if r['l3'] else "NO"
        l4 = "YES" if r['l4'] else "NO"
        print(f"| {r['system']} | {r['status']} | {t0} | {t1} | {t2} | {t3} | {t4} | {l0} | {l1} | {l2} | {l3} | {l4} |")
    
    # Save to file
    output_file = Path("knowledge_architecture/AETHER_MEMORY/investigations/SYSTEM_AUDIT_RESULTS.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# T0-T6 Conversion Status Audit\n\n")
        f.write(f"**Date:** 2025-11-02\n")
        f.write(f"**Total Systems:** {len(results)}\n\n")
        
        f.write(f"## ✅ COMPLETE ({len(complete)} systems)\n")
        for r in complete:
            f.write(f"- {r['system']}\n")
        
        f.write(f"\n## ⏳ PARTIAL ({len(partial)} systems)\n")
        for r in partial:
            f.write(f"- {r['system']} (T-levels: {r['t_levels']}/5)\n")
        
        f.write(f"\n## ❌ NOT CONVERTED ({len(not_converted)} systems)\n")
        for r in not_converted:
            f.write(f"- {r['system']} (L-levels: {r['l_levels']}/5)\n")
        
        if no_docs:
            f.write(f"\n## ⚠️ NO DOCS ({len(no_docs)} systems)\n")
            for r in no_docs:
                f.write(f"- {r['system']}\n")
        
        f.write("\n## 📊 DETAILED BREAKDOWN\n\n")
        f.write("| System | Status | T0 | T1 | T2 | T3 | T4 | L0 | L1 | L2 | L3 | L4 |\n")
        f.write("|--------|--------|----|----|----|----|----|----|----|----|----|----|\n")
        for r in results:
            t0 = "✅" if r['t0'] else "❌"
            t1 = "✅" if r['t1'] else "❌"
            t2 = "✅" if r['t2'] else "❌"
            t3 = "✅" if r['t3'] else "❌"
            t4 = "✅" if r['t4'] else "❌"
            l0 = "✅" if r['l0'] else "❌"
            l1 = "✅" if r['l1'] else "❌"
            l2 = "✅" if r['l2'] else "❌"
            l3 = "✅" if r['l3'] else "❌"
            l4 = "✅" if r['l4'] else "❌"
            f.write(f"| {r['system']} | {r['status']} | {t0} | {t1} | {t2} | {t3} | {t4} | {l0} | {l1} | {l2} | {l3} | {l4} |\n")
    
    print(f"\n✅ Audit complete! Results saved to: {output_file}")
    print(f"\n📊 Summary:")
    print(f"  - Complete: {len(complete)}")
    print(f"  - Partial: {len(partial)}")
    print(f"  - Not Converted: {len(not_converted)}")
    print(f"  - No Docs: {len(no_docs)}")

if __name__ == "__main__":
    main()

