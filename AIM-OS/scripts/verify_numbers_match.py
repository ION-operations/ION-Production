#!/usr/bin/env python3
"""
Verify all documentation numbers match artifacts/reconciled_totals.json.

Returns exit code 1 if any divergence found.
"""

from pathlib import Path
import json
import re
import sys

def main():
    """Verify documentation matches canonical numbers."""
    
    # Load canonical numbers
    reconciled = json.loads(Path("artifacts/reconciled_totals.json").read_text())
    
    print("[VERIFY] Checking documentation against reconciled_totals.json...")
    
    errors = []
    
    # Check each system's T1 file
    for sys_data in reconciled["systems"]:
        folder = sys_data["folder"]
        correct_count = sys_data["tags_total"]
        display_name = sys_data["system"]
        
        t1_path = Path(f"knowledge_architecture/systems/{folder}/T1_overview.md")
        
        if not t1_path.exists():
            continue
        
        content = t1_path.read_text(encoding='utf-8')
        
        # Find "**Total NL Tags:** NNN"
        if match := re.search(r'\*\*Total NL Tags:\*\*\s*(\d+)', content):
            found_count = int(match.group(1))
            if found_count != correct_count:
                errors.append(f"{display_name} T1: has {found_count}, should be {correct_count}")
        else:
            errors.append(f"{display_name} T1: No tag count found")
    
    # Check grand total in final report
    final_report = Path("knowledge_architecture/AETHER_MEMORY/DOCUMENTATION_WORK_COMPLETE_FINAL.md")
    if final_report.exists():
        content = final_report.read_text(encoding='utf-8')
        
        # Find "**Total Tags:** NNN"
        if match := re.search(r'\*\*Total Tags:\*\*\s*(\d+)', content):
            found_total = int(match.group(1))
            correct_total = reconciled["grand_totals"]["ALL"]
            if found_total != correct_total:
                errors.append(f"Final report: has {found_total}, should be {correct_total}")
    
    if errors:
        print("\n[FAIL] Number mismatches found:")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print("[OK] All numbers match source of truth!")
        return 0

if __name__ == "__main__":
    sys.exit(main())

