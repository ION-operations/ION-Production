#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T→L Cutover Readiness Check and Self-Automation Script
Comprehensive checkup and validation before cutover execution.
Usage: python scripts/cutover/checkup_and_validate.py
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

# Systems expected to have T0-T6 documentation
EXPECTED_SYSTEMS = [
    "cmc",
    "hhni",
    "vif",
    "apoe",
    "seg",
    "sdfcvf",
    "cognitive_analysis",
    "cross_model_consciousness",
    "timeline_context_system",
    "dual_prompt_architecture",
    "capability_awareness",
    "dynamic_onboarding",
    "advanced_monaco_editor",
    "autonomous_research_dream",
    "mcp_integration",
]

# Expected T-level files per system
EXPECTED_T_FILES = ["T0_executive.md", "T1_overview.md", "T2_architecture.md", "T3_detailed.md"]
OPTIONAL_T_FILES = ["T4_complete.md", "T6_complete.md"]

# Files that need reference updates
REFERENCE_FILES = [
    "knowledge_architecture/SUPER_INDEX.md",
    "knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md",
    "plans/EPIC_STANDARDS_TRACKING.md",
]

class CutoverReadinessCheck:
    """Comprehensive cutover readiness validation."""
    
    def __init__(self):
        self.systems_dir = Path("knowledge_architecture/systems")
        self.issues = []
        self.warnings = []
        self.successes = []
        self.system_status = defaultdict(dict)
        
    def check_t_level_files(self):
        """Check existence and completeness of T-level files."""
        print("\n🔍 Checking T-level files...")
        print("=" * 60)
        
        total_t_files = 0
        missing_systems = []
        
        for system in EXPECTED_SYSTEMS:
            system_dir = self.systems_dir / system
            if not system_dir.exists():
                missing_systems.append(system)
                self.issues.append(f"System directory not found: {system}")
                continue
            
            system_t_files = []
            for t_file in EXPECTED_T_FILES + OPTIONAL_T_FILES:
                t_path = system_dir / t_file
                if t_path.exists():
                    system_t_files.append(t_file)
                    total_t_files += 1
            
            # Check completeness
            expected_count = len(EXPECTED_T_FILES)
            found_count = sum(1 for f in EXPECTED_T_FILES if f in system_t_files)
            
            status = "complete" if found_count >= expected_count else "incomplete"
            self.system_status[system] = {
                "t_files": system_t_files,
                "status": status,
                "found": found_count,
                "expected": expected_count
            }
            
            if status == "complete":
                self.successes.append(f"✅ {system}: {found_count}/{expected_count} T-level files found")
            else:
                self.warnings.append(f"⚠️  {system}: Only {found_count}/{expected_count} T-level files found")
        
        print(f"\n📊 Summary:")
        print(f"   Total T-level files found: {total_t_files}")
        print(f"   Systems checked: {len(EXPECTED_SYSTEMS)}")
        print(f"   Systems complete: {sum(1 for s in self.system_status.values() if s['status'] == 'complete')}")
        
        if missing_systems:
            print(f"\n❌ Missing systems: {', '.join(missing_systems)}")
        
        return total_t_files > 0
    
    def check_l_level_files(self):
        """Check for existing L-level files that will be backed up."""
        print("\n🔍 Checking existing L-level files...")
        print("=" * 60)
        
        total_l_files = 0
        
        for system in EXPECTED_SYSTEMS:
            system_dir = self.systems_dir / system
            if not system_dir.exists():
                continue
            
            l_files = list(system_dir.glob("L*.md"))
            total_l_files += len(l_files)
            
            if l_files:
                self.warnings.append(f"⚠️  {system}: {len(l_files)} existing L-level files will be backed up")
        
        print(f"\n📊 Summary:")
        print(f"   Total existing L-level files: {total_l_files}")
        print(f"   These will be backed up to legacy_docs/ before cutover")
        
        return True
    
    def check_reference_files(self):
        """Check that reference files exist and can be updated."""
        print("\n🔍 Checking reference files...")
        print("=" * 60)
        
        missing_refs = []
        t_refs_found = defaultdict(int)
        
        for ref_file in REFERENCE_FILES:
            ref_path = Path(ref_file)
            if not ref_path.exists():
                missing_refs.append(ref_file)
                self.issues.append(f"Reference file not found: {ref_file}")
                continue
            
            # Check for T-level references
            content = ref_path.read_text(encoding="utf-8")
            t_refs = len(re.findall(r"T[0-6]_", content, re.IGNORECASE))
            t_refs_found[ref_file] = t_refs
            
            if t_refs > 0:
                self.warnings.append(f"⚠️  {ref_file}: {t_refs} T-level references found (will be updated)")
            else:
                self.successes.append(f"✅ {ref_file}: No T-level references found")
        
        # Check system maps
        system_maps = list(self.systems_dir.rglob("system.map.lucid.json5"))
        t_refs_in_maps = 0
        
        for map_file in system_maps:
            content = map_file.read_text(encoding="utf-8")
            t_refs = len(re.findall(r"T[0-6]_", content, re.IGNORECASE))
            if t_refs > 0:
                t_refs_in_maps += t_refs
                self.warnings.append(f"⚠️  {map_file}: {t_refs} T-level references found")
        
        print(f"\n📊 Summary:")
        print(f"   Reference files checked: {len(REFERENCE_FILES)}")
        print(f"   System maps checked: {len(system_maps)}")
        print(f"   Total T-level references found: {sum(t_refs_found.values()) + t_refs_in_maps}")
        
        if missing_refs:
            print(f"\n❌ Missing reference files: {', '.join(missing_refs)}")
            return False
        
        return True
    
    def check_scripts(self):
        """Check that all automation scripts exist."""
        print("\n🔍 Checking automation scripts...")
        print("=" * 60)
        
        scripts_dir = Path("scripts/cutover")
        required_scripts = [
            "backup_legacy.sh",
            "rename_t2l.sh",
            "update_references.py",
            "remove_banners.py",
            "validate_cutover.sh",
            "execute_cutover.sh",
        ]
        
        missing_scripts = []
        
        for script in required_scripts:
            script_path = scripts_dir / script
            if script_path.exists():
                self.successes.append(f"✅ {script}: Found")
            else:
                missing_scripts.append(script)
                self.issues.append(f"Script not found: {script}")
        
        print(f"\n📊 Summary:")
        print(f"   Scripts checked: {len(required_scripts)}")
        print(f"   Scripts found: {len(required_scripts) - len(missing_scripts)}")
        
        if missing_scripts:
            print(f"\n❌ Missing scripts: {', '.join(missing_scripts)}")
            return False
        
        return True
    
    def check_gate_results(self):
        """Check that gate results exist for all systems."""
        print("\n🔍 Checking gate results...")
        print("=" * 60)
        
        gate_results_dir = Path("coordination/epic_standards_overhaul/artifacts/gate_checks")
        
        if not gate_results_dir.exists():
            self.warnings.append(f"⚠️  Gate results directory not found: {gate_results_dir}")
            return True
        
        expected_gates = [
            "CMC_T0_T6_GATE_RESULTS.md",
            "HHNI_T0_T6_GATE_RESULTS.md",
            "VIF_T0_T6_GATE_RESULTS.md",
            "APOE_T0_T6_GATE_RESULTS.md",
            "SEG_T0_T6_GATE_RESULTS.md",
            "SDFCVF_T0_T6_GATE_RESULTS.md",
            "CAS_T0_T6_GATE_RESULTS.md",
            "TCS_T0_T6_GATE_RESULTS.md",
            "XMC_T0_T6_GATE_RESULTS.md",
            "DPA_T0_T6_GATE_RESULTS.md",
            "CAF_T0_T6_GATE_RESULTS.md",
            "DOS_T0_T6_GATE_RESULTS.md",
            "AME_T0_T6_GATE_RESULTS.md",
            "ARD_T0_T6_GATE_RESULTS.md",
        ]
        
        found_gates = []
        missing_gates = []
        
        for gate_file in expected_gates:
            gate_path = gate_results_dir / gate_file
            if gate_path.exists():
                found_gates.append(gate_file)
                self.successes.append(f"✅ {gate_file}: Found")
            else:
                missing_gates.append(gate_file)
                self.warnings.append(f"⚠️  {gate_file}: Not found")
        
        print(f"\n📊 Summary:")
        print(f"   Gate results checked: {len(expected_gates)}")
        print(f"   Gate results found: {len(found_gates)}")
        
        if missing_gates:
            print(f"\n⚠️  Missing gate results: {len(missing_gates)}")
        
        return True
    
    def generate_report(self):
        """Generate comprehensive readiness report."""
        print("\n" + "=" * 60)
        print("📋 CUTOVER READINESS REPORT")
        print("=" * 60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n✅ SUCCESSES:")
        if self.successes:
            for success in self.successes[:20]:  # Limit display
                print(f"   {success}")
            if len(self.successes) > 20:
                print(f"   ... and {len(self.successes) - 20} more")
        else:
            print("   None")
        
        print("\n⚠️  WARNINGS:")
        if self.warnings:
            for warning in self.warnings[:20]:  # Limit display
                print(f"   {warning}")
            if len(self.warnings) > 20:
                print(f"   ... and {len(self.warnings) - 20} more")
        else:
            print("   None")
        
        print("\n❌ ISSUES:")
        if self.issues:
            for issue in self.issues:
                print(f"   {issue}")
        else:
            print("   None")
        
        print("\n" + "=" * 60)
        
        # Overall readiness
        is_ready = len(self.issues) == 0
        
        if is_ready:
            print("✅ READY FOR CUTOVER")
            print("\nAll checks passed. You can proceed with cutover execution.")
        else:
            print("❌ NOT READY FOR CUTOVER")
            print(f"\n{len(self.issues)} critical issues must be resolved before cutover.")
        
        print("=" * 60)
        
        return is_ready
    
    def run_all_checks(self):
        """Run all readiness checks."""
        print("🚀 Starting T→L Cutover Readiness Check")
        print("=" * 60)
        
        checks = [
            ("T-level files", self.check_t_level_files),
            ("L-level files", self.check_l_level_files),
            ("Reference files", self.check_reference_files),
            ("Automation scripts", self.check_scripts),
            ("Gate results", self.check_gate_results),
        ]
        
        results = {}
        for name, check_func in checks:
            try:
                results[name] = check_func()
            except Exception as e:
                self.issues.append(f"Error in {name} check: {str(e)}")
                results[name] = False
        
        return self.generate_report()

def main():
    """Main execution."""
    checker = CutoverReadinessCheck()
    is_ready = checker.run_all_checks()
    
    # Exit code: 0 = ready, 1 = not ready
    exit(0 if is_ready else 1)

if __name__ == "__main__":
    main()

