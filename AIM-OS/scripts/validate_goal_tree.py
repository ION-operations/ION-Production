#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Goal Tree Validation Script

Validates GOAL_TREE.yaml structure, completeness, and connections.

Checks:
1. All systems in packages/ have goals (or documented exception)
2. All goals reference existing systems/artifacts
3. All objectives have complete metadata
4. No duplicate OBJ IDs
5. All KRs have quantified targets
6. Dependencies are valid

Usage:
    python scripts/validate_goal_tree.py
    python scripts/validate_goal_tree.py --detailed

Output:
    goals/GOAL_TREE_VALIDATION_REPORT.md
"""

import yaml
import sys
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime


class GoalTreeValidator:
    """Validate GOAL_TREE.yaml structure and completeness"""
    
    def __init__(self, goal_tree_path: str = "goals/GOAL_TREE.yaml"):
        self.goal_tree_path = Path(goal_tree_path)
        self.goal_tree = self.load_goal_tree()
        self.issues = []
        self.warnings = []
        self.stats = {}
    
    def load_goal_tree(self) -> dict:
        """Load and parse GOAL_TREE.yaml"""
        try:
            with open(self.goal_tree_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[ERROR] Could not load GOAL_TREE.yaml: {e}")
            sys.exit(1)
    
    def validate_all(self) -> bool:
        """Run all validation checks"""
        print("[*] Validating GOAL_TREE.yaml...\n")
        
        self.check_metadata_completeness()
        self.check_duplicate_ids()
        self.check_quantified_targets()
        self.check_systems_have_goals()
        self.check_goals_have_systems()
        self.check_dependencies_valid()
        self.collect_statistics()
        
        return len(self.issues) == 0
    
    def check_metadata_completeness(self):
        """Check all objectives have required metadata"""
        print("[*] Checking metadata completeness...")
        
        required_fields = [
            "id", "name", "description", "owner", "priority_tier",
            "target_date", "key_results", "status", "completion_percentage"
        ]
        
        for obj in self.goal_tree.get("objectives", []):
            obj_id = obj.get("id", "UNKNOWN")
            
            for field in required_fields:
                if field not in obj:
                    self.issues.append(f"{obj_id} missing required field: {field}")
            
            # Check key_results structure
            if "key_results" in obj:
                for kr in obj["key_results"]:
                    if "id" not in kr:
                        self.issues.append(f"{obj_id} has KR without id")
                    if "metric" not in kr:
                        self.issues.append(f"{obj_id} has KR without metric")
                    if "target" not in kr:
                        self.issues.append(f"{obj_id} has KR without target")
        
        if not self.issues:
            print("[OK] All objectives have complete metadata\n")
        else:
            print(f"[WARN] Found {len(self.issues)} metadata issues\n")
    
    def check_duplicate_ids(self):
        """Check for duplicate OBJ IDs"""
        print("[*] Checking for duplicate IDs...")
        
        ids_seen = set()
        for obj in self.goal_tree.get("objectives", []):
            obj_id = obj.get("id")
            if obj_id in ids_seen:
                self.issues.append(f"Duplicate ID found: {obj_id}")
            ids_seen.add(obj_id)
        
        if len(ids_seen) == len(self.goal_tree.get("objectives", [])):
            print(f"[OK] All {len(ids_seen)} objective IDs are unique\n")
        else:
            print(f"[ERROR] Duplicate IDs found\n")
    
    def check_quantified_targets(self):
        """Check all KRs have quantified targets"""
        print("[*] Checking quantified targets...")
        
        total_krs = 0
        quantified = 0
        
        for obj in self.goal_tree.get("objectives", []):
            obj_id = obj.get("id")
            for kr in obj.get("key_results", []):
                total_krs += 1
                target = kr.get("target", "")
                
                # Check if target has numbers or clear quantification
                if any(char.isdigit() for char in str(target)) or "100%" in str(target):
                    quantified += 1
                else:
                    self.warnings.append(f"{obj_id} {kr.get('id')}: Target not quantified: '{target}'")
        
        print(f"[OK] {quantified}/{total_krs} KRs have quantified targets ({quantified/total_krs*100:.1f}%)\n")
        self.stats["total_krs"] = total_krs
        self.stats["quantified_krs"] = quantified
    
    def check_systems_have_goals(self):
        """Check all substantial systems in packages/ have goals"""
        print("[*] Checking systems have goals...")
        
        packages_dir = Path("packages")
        if not packages_dir.exists():
            self.warnings.append("packages/ directory not found")
            return
        
        orphaned_systems = []
        
        for pkg in packages_dir.iterdir():
            if not pkg.is_dir() or pkg.name.startswith("_"):
                continue
            
            # Count LOC (rough estimate from .py files)
            py_files = list(pkg.rglob("*.py"))
            if len(py_files) == 0:
                continue  # Not a Python package
            
            # Check if mentioned in goal tree
            pkg_mentioned = self.is_system_in_goals(pkg.name)
            
            if not pkg_mentioned:
                orphaned_systems.append(pkg.name)
        
        if orphaned_systems:
            self.warnings.append(f"Systems without clear goals: {', '.join(orphaned_systems)}")
            print(f"[WARN] {len(orphaned_systems)} systems may need goals\n")
        else:
            print(f"[OK] All systems connected to goals\n")
        
        self.stats["orphaned_systems"] = len(orphaned_systems)
    
    def is_system_in_goals(self, system_name: str) -> bool:
        """Check if system mentioned anywhere in goal tree"""
        goal_tree_str = str(self.goal_tree).lower()
        return system_name.lower() in goal_tree_str
    
    def check_goals_have_systems(self):
        """Check all goals reference existing artifacts"""
        print("[*] Checking goals have systems...")
        
        goals_without_systems = []
        
        for obj in self.goal_tree.get("objectives", []):
            obj_id = obj.get("id")
            artifacts = obj.get("artifacts", [])
            
            if not artifacts:
                self.warnings.append(f"{obj_id} has no artifacts listed")
                continue
            
            # Check if at least one artifact exists
            has_existing = False
            for artifact in artifacts:
                # Clean artifact path (remove descriptions)
                artifact_path = artifact.split("(")[0].strip()
                if Path(artifact_path).exists():
                    has_existing = True
                    break
            
            if not has_existing:
                goals_without_systems.append(obj_id)
        
        if goals_without_systems:
            self.warnings.append(f"Goals with no existing artifacts: {', '.join(goals_without_systems)}")
            print(f"[WARN] {len(goals_without_systems)} goals may need artifact updates\n")
        else:
            print(f"[OK] All goals have existing artifacts\n")
        
        self.stats["goals_without_systems"] = len(goals_without_systems)
    
    def check_dependencies_valid(self):
        """Check dependencies between goals are valid"""
        print("[*] Checking dependencies...")
        
        obj_ids = {obj.get("id") for obj in self.goal_tree.get("objectives", [])}
        invalid_deps = []
        
        for obj in self.goal_tree.get("objectives", []):
            obj_id = obj.get("id")
            depends_on = obj.get("depends_on", [])
            
            if isinstance(depends_on, list):
                for dep in depends_on:
                    # Extract OBJ-XX from string like "OBJ-12 (protocols)"
                    dep_id = dep.split("(")[0].strip().split()[0]
                    if dep_id.startswith("OBJ-") and dep_id not in obj_ids:
                        invalid_deps.append(f"{obj_id} depends on non-existent {dep_id}")
        
        if invalid_deps:
            self.issues.extend(invalid_deps)
            print(f"[ERROR] {len(invalid_deps)} invalid dependencies\n")
        else:
            print(f"[OK] All dependencies valid\n")
    
    def collect_statistics(self):
        """Collect statistics about goal tree"""
        objectives = self.goal_tree.get("objectives", [])
        
        self.stats["total_objectives"] = len(objectives)
        self.stats["tier_s"] = len([o for o in objectives if "S -" in o.get("priority_tier", "")])
        self.stats["tier_a"] = len([o for o in objectives if "A -" in o.get("priority_tier", "")])
        self.stats["tier_b"] = len([o for o in objectives if "B -" in o.get("priority_tier", "")])
        self.stats["tier_c"] = len([o for o in objectives if "C -" in o.get("priority_tier", "")])
        
        self.stats["in_progress"] = len([o for o in objectives if o.get("status") == "in_progress"])
        self.stats["completed"] = len([o for o in objectives if o.get("status") == "completed"])
        self.stats["planning"] = len([o for o in objectives if o.get("status") == "planning"])
        self.stats["paused"] = len([o for o in objectives if o.get("status") == "paused"])
        
        # Average completion
        completions = [o.get("completion_percentage", 0) for o in objectives]
        self.stats["avg_completion"] = sum(completions) / len(completions) if completions else 0
    
    def generate_report(self):
        """Generate validation report"""
        report_path = Path("goals/GOAL_TREE_VALIDATION_REPORT.md")
        
        report = f"""# Goal Tree Validation Report
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**Validator:** Aether (Automated)  
**Goal Tree Version:** {self.goal_tree.get('version', 'unknown')}  

---

## 📊 SUMMARY

**Total Objectives:** {self.stats['total_objectives']}  
**Critical Issues:** {len(self.issues)}  
**Warnings:** {len(self.warnings)}  
**Overall Status:** {"✅ PASS" if len(self.issues) == 0 else "❌ FAIL"}

---

## 📈 STATISTICS

**By Tier:**
- TIER S (Ship-Critical): {self.stats['tier_s']}
- TIER A (High): {self.stats['tier_a']}
- TIER B (Medium): {self.stats['tier_b']}
- TIER C (Future): {self.stats['tier_c']}

**By Status:**
- In Progress: {self.stats['in_progress']}
- Completed: {self.stats['completed']}
- Planning: {self.stats['planning']}
- Paused: {self.stats['paused']}

**Completion:**
- Average: {self.stats['avg_completion']:.1f}%
- Quantified KRs: {self.stats.get('quantified_krs', 0)}/{self.stats.get('total_krs', 0)}

**Orphans:**
- Systems without goals: {self.stats.get('orphaned_systems', 0)}
- Goals without systems: {self.stats.get('goals_without_systems', 0)}

---

## ❌ CRITICAL ISSUES ({len(self.issues)})

"""
        
        if self.issues:
            for i, issue in enumerate(self.issues, 1):
                report += f"{i}. {issue}\n"
        else:
            report += "None! ✅\n"
        
        report += f"\n---\n\n## ⚠️ WARNINGS ({len(self.warnings)})\n\n"
        
        if self.warnings:
            for i, warning in enumerate(self.warnings, 1):
                report += f"{i}. {warning}\n"
        else:
            report += "None! ✅\n"
        
        report += "\n---\n\n**Validation Complete:** "
        report += "✅ PASS - All checks passed!" if len(self.issues) == 0 else "❌ FAIL - Issues found"
        
        report_path.write_text(report, encoding='utf-8')
        print(f"[*] Report written to: {report_path}")
        
        return report
    
    def print_summary(self):
        """Print summary to console"""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(f"[*] Objectives: {self.stats['total_objectives']}")
        print(f"[ERROR] Critical Issues: {len(self.issues)}")
        print(f"[WARN] Warnings: {len(self.warnings)}")
        print(f"[*] Average Completion: {self.stats['avg_completion']:.1f}%")
        print("="*60)
        
        if len(self.issues) == 0:
            print("\n[OK] VALIDATION PASSED - Goal tree is healthy!")
            return True
        else:
            print("\n[ERROR] VALIDATION FAILED - Issues need attention")
            print("\nSee goals/GOAL_TREE_VALIDATION_REPORT.md for details")
            return False


def main():
    """Main validation flow"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate GOAL_TREE.yaml")
    parser.add_argument("--detailed", action="store_true", help="Run detailed validation")
    args = parser.parse_args()
    
    validator = GoalTreeValidator()
    
    # Run validation
    passed = validator.validate_all()
    
    # Generate report
    validator.generate_report()
    
    # Print summary
    validator.print_summary()
    
    # Exit code
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

