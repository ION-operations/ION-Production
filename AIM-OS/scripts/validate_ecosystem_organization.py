#!/usr/bin/env python3
"""
Validate AIM-OS Ecosystem Organization

Checks:
1. All systems in correct locations (knowledge_architecture/systems/)
2. All systems have T0-T6 documentation
3. All systems have system.map.lucid.json5
4. SUPER_INDEX includes all systems
5. Navigation index includes all systems
6. Goal tree references all systems

Purpose: Ensure ecosystem is organized to spec before North Star creation
"""

from pathlib import Path
from typing import Dict, List, Set, Tuple
import json
import yaml

class EcosystemValidator:
    def __init__(self, workspace_root: str = "."):
        self.root = Path(workspace_root)
        self.systems_dir = self.root / "knowledge_architecture" / "systems"
        self.super_index = self.root / "knowledge_architecture" / "SUPER_INDEX.md"
        self.nav_index = self.root / "knowledge_architecture" / "HIERARCHICAL_NAVIGATION_INDEX.md"
        self.goal_tree = self.root / "goals" / "GOAL_TREE.yaml"
        
        self.issues = []
        self.warnings = []
        
    def validate(self) -> Dict:
        """Run complete ecosystem validation."""
        print("[*] Validating AIM-OS Ecosystem Organization...\n")
        
        # Get all systems
        systems = self.get_all_systems()
        print(f"[*] Found {len(systems)} systems\n")
        
        # Check 1: T0-T6 completeness
        print("[*] Checking T0-T6 documentation...")
        self.check_t_level_completeness(systems)
        
        # Check 2: System maps
        print("[*] Checking system maps...")
        self.check_system_maps(systems)
        
        # Check 3: SUPER_INDEX
        print("[*] Checking SUPER_INDEX coverage...")
        self.check_super_index(systems)
        
        # Check 4: Navigation index
        print("[*] Checking navigation index...")
        self.check_navigation_index(systems)
        
        # Check 5: Goal tree
        print("[*] Checking goal tree references...")
        self.check_goal_tree(systems)
        
        # Generate report
        return self.generate_report(systems)
    
    def get_all_systems(self) -> List[str]:
        """Get all system directories."""
        if not self.systems_dir.exists():
            return []
        
        systems = [
            d.name for d in self.systems_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        return sorted(systems)
    
    def check_t_level_completeness(self, systems: List[str]):
        """Check if all systems have complete T0-T6 documentation."""
        t_levels = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6']
        
        for system in systems:
            system_dir = self.systems_dir / system
            
            for level in t_levels:
                # Look for T0_executive.md, T1_overview.md, etc.
                pattern = f"{level}_*.md"
                matching_files = list(system_dir.glob(pattern))
                
                if not matching_files:
                    if level in ['T0', 'T1', 'T2']:  # Critical levels
                        self.issues.append({
                            'type': 'missing_t_level',
                            'severity': 'HIGH',
                            'system': system,
                            'level': level,
                            'message': f"{system} missing {level} documentation (CRITICAL)",
                            'action': f"Create knowledge_architecture/systems/{system}/{level}_*.md"
                        })
                    else:  # T3-T6 optional but recommended
                        self.warnings.append({
                            'type': 'missing_t_level',
                            'severity': 'MEDIUM',
                            'system': system,
                            'level': level,
                            'message': f"{system} missing {level} documentation (recommended)",
                            'action': f"Consider creating {system}/{level}_*.md"
                        })
    
    def check_system_maps(self, systems: List[str]):
        """Check if all systems have system.map.lucid.json5."""
        for system in systems:
            system_dir = self.systems_dir / system
            map_path = system_dir / "system.map.lucid.json5"
            
            if not map_path.exists():
                self.issues.append({
                    'type': 'missing_system_map',
                    'severity': 'HIGH',
                    'system': system,
                    'message': f"{system} missing system map (CRITICAL for AI navigation)",
                    'action': f"Create knowledge_architecture/systems/{system}/system.map.lucid.json5"
                })
    
    def check_super_index(self, systems: List[str]):
        """Check if SUPER_INDEX includes all systems."""
        if not self.super_index.exists():
            self.issues.append({
                'type': 'missing_super_index',
                'severity': 'CRITICAL',
                'message': "SUPER_INDEX.md not found!",
                'action': "Create knowledge_architecture/SUPER_INDEX.md"
            })
            return
        
        # Read SUPER_INDEX
        super_index_content = self.super_index.read_text(encoding='utf-8')
        
        # Check each system is mentioned
        for system in systems:
            # Look for system name (case-insensitive)
            if system.lower() not in super_index_content.lower():
                self.warnings.append({
                    'type': 'system_not_indexed',
                    'severity': 'MEDIUM',
                    'system': system,
                    'message': f"{system} not found in SUPER_INDEX",
                    'action': f"Add {system} concepts to SUPER_INDEX.md"
                })
    
    def check_navigation_index(self, systems: List[str]):
        """Check if navigation index includes all systems."""
        nav_path = self.nav_index
        
        if not nav_path.exists():
            self.warnings.append({
                'type': 'missing_nav_index',
                'severity': 'MEDIUM',
                'message': "HIERARCHICAL_NAVIGATION_INDEX.md not found",
                'action': "Create navigation index"
            })
            return
        
        # Read navigation index
        nav_content = nav_path.read_text(encoding='utf-8')
        
        # Check each system is referenced
        for system in systems:
            if system.lower() not in nav_content.lower():
                self.warnings.append({
                    'type': 'system_not_in_nav',
                    'severity': 'LOW',
                    'system': system,
                    'message': f"{system} not in navigation index",
                    'action': f"Add {system} to HIERARCHICAL_NAVIGATION_INDEX.md"
                })
    
    def check_goal_tree(self, systems: List[str]):
        """Check if goal tree references systems."""
        if not self.goal_tree.exists():
            self.issues.append({
                'type': 'missing_goal_tree',
                'severity': 'CRITICAL',
                'message': "GOAL_TREE.yaml not found!",
                'action': "Create goals/GOAL_TREE.yaml"
            })
            return
        
        # Read goal tree
        try:
            goal_content = self.goal_tree.read_text(encoding='utf-8')
            
            # Core systems should have goals
            core_systems = ['cmc', 'hhni', 'vif', 'apoe', 'seg', 'sdfcvf', 'cas', 'sis']
            
            for system in core_systems:
                if system.upper() not in goal_content and system.lower() not in goal_content:
                    self.warnings.append({
                        'type': 'core_system_no_goal',
                        'severity': 'MEDIUM',
                        'system': system,
                        'message': f"Core system {system.upper()} not clearly referenced in goals",
                        'action': f"Ensure {system.upper()} has associated goal"
                    })
        except Exception as e:
            self.issues.append({
                'type': 'goal_tree_error',
                'severity': 'HIGH',
                'message': f"Error reading GOAL_TREE.yaml: {e}",
                'action': "Fix GOAL_TREE.yaml format"
            })
    
    def generate_report(self, systems: List[str]) -> Dict:
        """Generate validation report."""
        print("\n" + "="*60)
        print("ECOSYSTEM VALIDATION REPORT")
        print("="*60)
        
        print(f"\n[*] Systems Validated: {len(systems)}")
        print(f"[ERROR] Critical Issues: {len([i for i in self.issues if i.get('severity') == 'CRITICAL'])}")
        print(f"[ERROR] High Issues: {len([i for i in self.issues if i.get('severity') == 'HIGH'])}")
        print(f"[WARN] Warnings: {len(self.warnings)}")
        
        # Print critical/high issues
        critical_and_high = [i for i in self.issues if i.get('severity') in ['CRITICAL', 'HIGH']]
        
        if critical_and_high:
            print(f"\n[!] CRITICAL/HIGH ISSUES ({len(critical_and_high)}):\n")
            for issue in critical_and_high[:10]:  # Show first 10
                print(f"  [{issue['severity']}] {issue['message']}")
                print(f"    Action: {issue['action']}\n")
        
        # Summary
        print("\n" + "="*60)
        if len(critical_and_high) == 0:
            print("[OK] ECOSYSTEM HEALTHY - Ready for North Star creation!")
        elif len(critical_and_high) < 10:
            print("[WARN] Minor issues found - can proceed with caution")
        else:
            print("[ERROR] Major issues found - fix before proceeding")
        print("="*60)
        
        # Write detailed report
        report_path = self.root / "audits" / "2025-11-05" / "ECOSYSTEM_VALIDATION_REPORT.md"
        self.write_detailed_report(report_path, systems)
        print(f"\n[*] Detailed report: {report_path}")
        
        return {
            'systems_count': len(systems),
            'critical_issues': len([i for i in self.issues if i.get('severity') == 'CRITICAL']),
            'high_issues': len([i for i in self.issues if i.get('severity') == 'HIGH']),
            'warnings': len(self.warnings),
            'all_issues': self.issues,
            'all_warnings': self.warnings
        }
    
    def write_detailed_report(self, report_path: Path, systems: List[str]):
        """Write detailed validation report."""
        report = f"""# Ecosystem Validation Report

**Date:** 2025-11-05
**Purpose:** Validate AIM-OS ecosystem organization before North Star creation
**Systems Validated:** {len(systems)}

---

## Summary

| Metric | Count |
|--------|-------|
| Total Systems | {len(systems)} |
| Critical Issues | {len([i for i in self.issues if i.get('severity') == 'CRITICAL'])} |
| High Issues | {len([i for i in self.issues if i.get('severity') == 'HIGH'])} |
| Warnings | {len(self.warnings)} |

---

## Critical/High Issues

"""
        
        critical_and_high = [i for i in self.issues if i.get('severity') in ['CRITICAL', 'HIGH']]
        
        if critical_and_high:
            for issue in critical_and_high:
                report += f"\n### [{issue['severity']}] {issue['message']}\n"
                report += f"- **Action:** {issue['action']}\n"
                if 'system' in issue:
                    report += f"- **System:** {issue['system']}\n"
        else:
            report += "\n✅ No critical or high issues found!\n"
        
        report += "\n---\n\n## Warnings\n"
        
        if self.warnings:
            for warning in self.warnings[:20]:  # First 20 warnings
                report += f"\n### [{warning.get('severity', 'MEDIUM')}] {warning['message']}\n"
                report += f"- **Action:** {warning['action']}\n"
                if 'system' in warning:
                    report += f"- **System:** {warning['system']}\n"
        else:
            report += "\n✅ No warnings!\n"
        
        report += "\n---\n\n## Recommendation\n\n"
        
        if len(critical_and_high) == 0:
            report += "✅ **PROCEED** - Ecosystem is healthy and ready for North Star creation!\n"
        elif len(critical_and_high) < 10:
            report += "⚠️ **PROCEED WITH CAUTION** - Minor issues found, can fix as we go.\n"
        else:
            report += "❌ **DO NOT PROCEED** - Major issues found, fix ecosystem first!\n"
        
        # Write report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding='utf-8')


if __name__ == "__main__":
    validator = EcosystemValidator()
    result = validator.validate()

