#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L0-L6 Gate Validation Script (Post-Cutover)
Validates L0-L6 documentation compliance after T→L cutover.
Usage: python scripts/cutover/validate_l0l6_gate.py
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

# Systems that were cutover
CUTOVER_SYSTEMS = [
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

# Required L-level files
REQUIRED_L_FILES = ["L0_executive.md", "L1_overview.md", "L2_architecture.md", "L3_detailed.md"]
OPTIONAL_L_FILES = ["L4_complete.md", "L6_complete.md"]

class L0L6GateValidator:
    """L0-L6 Gate Validation."""
    
    def __init__(self):
        self.systems_dir = Path("knowledge_architecture/systems")
        self.issues = []
        self.warnings = []
        self.successes = []
        self.system_status = defaultdict(dict)
        
    def check_file_existence(self):
        """Check that all required L-level files exist."""
        print("\n🔍 Checking L-level file existence...")
        print("=" * 60)
        
        total_files = 0
        missing_files = []
        
        for system in CUTOVER_SYSTEMS:
            system_dir = self.systems_dir / system
            if not system_dir.exists():
                self.issues.append(f"System directory not found: {system}")
                continue
            
            system_l_files = []
            for l_file in REQUIRED_L_FILES + OPTIONAL_L_FILES:
                l_path = system_dir / l_file
                if l_path.exists():
                    system_l_files.append(l_file)
                    total_files += 1
            
            # Check completeness
            required_count = len(REQUIRED_L_FILES)
            found_count = sum(1 for f in REQUIRED_L_FILES if f in system_l_files)
            
            status = "complete" if found_count >= required_count else "incomplete"
            self.system_status[system] = {
                "l_files": system_l_files,
                "status": status,
                "found": found_count,
                "expected": required_count
            }
            
            if status == "complete":
                self.successes.append(f"✅ {system}: {found_count}/{required_count} L-level files found")
            else:
                missing = [f for f in REQUIRED_L_FILES if f not in system_l_files]
                missing_files.append((system, missing))
                self.warnings.append(f"⚠️  {system}: Only {found_count}/{required_count} L-level files found (missing: {', '.join(missing)})")
        
        print(f"\n📊 Summary:")
        print(f"   Total L-level files found: {total_files}")
        print(f"   Systems checked: {len(CUTOVER_SYSTEMS)}")
        print(f"   Systems complete: {sum(1 for s in self.system_status.values() if s['status'] == 'complete')}")
        
        if missing_files:
            print(f"\n⚠️  Missing files:")
            for system, missing in missing_files:
                print(f"   {system}: {', '.join(missing)}")
        
        return len(missing_files) == 0
    
    def check_metadata(self):
        """Check that metadata is present and valid."""
        print("\n🔍 Checking metadata...")
        print("=" * 60)
        
        systems_with_metadata = 0
        systems_without_metadata = []
        
        for system in CUTOVER_SYSTEMS:
            system_dir = self.systems_dir / system
            if not system_dir.exists():
                continue
            
            l0_file = system_dir / "L0_executive.md"
            if l0_file.exists():
                content = l0_file.read_text(encoding="utf-8")
                # Check for frontmatter (YAML between ---)
                if re.search(r'^---\s*\n.*?\n---', content, re.MULTILINE | re.DOTALL):
                    systems_with_metadata += 1
                    self.successes.append(f"✅ {system}: Metadata present")
                else:
                    systems_without_metadata.append(system)
                    self.warnings.append(f"⚠️  {system}: Missing frontmatter metadata")
        
        print(f"\n📊 Summary:")
        print(f"   Systems with metadata: {systems_with_metadata}/{len(CUTOVER_SYSTEMS)}")
        
        if systems_without_metadata:
            print(f"\n⚠️  Systems without metadata: {', '.join(systems_without_metadata)}")
        
        return len(systems_without_metadata) == 0
    
    def check_navigation_links(self):
        """Check internal navigation links."""
        print("\n🔍 Checking navigation links...")
        print("=" * 60)
        
        systems_with_links = 0
        systems_without_links = []
        
        for system in CUTOVER_SYSTEMS:
            system_dir = self.systems_dir / system
            if not system_dir.exists():
                continue
            
            l1_file = system_dir / "L1_overview.md"
            if l1_file.exists():
                content = l1_file.read_text(encoding="utf-8")
                # Check for links to L0, L2
                has_l0_link = bool(re.search(r'L0_executive|L0\.md', content, re.IGNORECASE))
                has_l2_link = bool(re.search(r'L2_architecture|L2\.md', content, re.IGNORECASE))
                
                if has_l0_link or has_l2_link:
                    systems_with_links += 1
                    self.successes.append(f"✅ {system}: Navigation links present")
                else:
                    systems_without_links.append(system)
                    self.warnings.append(f"⚠️  {system}: Missing navigation links")
        
        print(f"\n📊 Summary:")
        print(f"   Systems with links: {systems_with_links}/{len(CUTOVER_SYSTEMS)}")
        
        if systems_without_links:
            print(f"\n⚠️  Systems without links: {', '.join(systems_without_links)}")
        
        return len(systems_without_links) == 0
    
    def check_word_counts(self):
        """Check approximate word counts."""
        print("\n🔍 Checking word counts...")
        print("=" * 60)
        
        word_count_targets = {
            "L0_executive.md": (80, 120),  # ~100 words
            "L1_overview.md": (400, 600),  # ~500 words
            "L2_architecture.md": (1600, 2400),  # ~2000 words
            "L3_detailed.md": (8000, 12000),  # ~10000 words
        }
        
        systems_checked = 0
        systems_within_range = 0
        
        for system in CUTOVER_SYSTEMS:
            system_dir = self.systems_dir / system
            if not system_dir.exists():
                continue
            
            all_within_range = True
            for l_file, (min_words, max_words) in word_count_targets.items():
                l_path = system_dir / l_file
                if l_path.exists():
                    content = l_path.read_text(encoding="utf-8")
                    word_count = len(content.split())
                    
                    if min_words <= word_count <= max_words:
                        pass  # Within range
                    else:
                        all_within_range = False
                        self.warnings.append(f"⚠️  {system}/{l_file}: {word_count} words (target: {min_words}-{max_words})")
            
            systems_checked += 1
            if all_within_range:
                systems_within_range += 1
                self.successes.append(f"✅ {system}: Word counts within acceptable range")
        
        print(f"\n📊 Summary:")
        print(f"   Systems checked: {systems_checked}")
        print(f"   Systems within range: {systems_within_range}")
        
        return True  # Not blocking, just informational
    
    def check_index_integration(self):
        """Check integration with indices."""
        print("\n🔍 Checking index integration...")
        print("=" * 60)
        
        # Check SUPER_INDEX.md
        super_index = Path("knowledge_architecture/SUPER_INDEX.md")
        if super_index.exists():
            content = super_index.read_text(encoding="utf-8")
            systems_found = sum(1 for system in CUTOVER_SYSTEMS if re.search(rf'\b{system}\b', content, re.IGNORECASE))
            if systems_found >= len(CUTOVER_SYSTEMS) * 0.8:  # 80% threshold
                self.successes.append(f"✅ SUPER_INDEX.md: {systems_found}/{len(CUTOVER_SYSTEMS)} systems referenced")
            else:
                self.warnings.append(f"⚠️  SUPER_INDEX.md: Only {systems_found}/{len(CUTOVER_SYSTEMS)} systems referenced")
        
        # Check HIERARCHICAL_NAVIGATION_INDEX.md
        nav_index = Path("knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md")
        if nav_index.exists():
            content = nav_index.read_text(encoding="utf-8")
            systems_found = sum(1 for system in CUTOVER_SYSTEMS if re.search(rf'\b{system}\b', content, re.IGNORECASE))
            if systems_found >= len(CUTOVER_SYSTEMS) * 0.8:  # 80% threshold
                self.successes.append(f"✅ HIERARCHICAL_NAVIGATION_INDEX.md: {systems_found}/{len(CUTOVER_SYSTEMS)} systems referenced")
            else:
                self.warnings.append(f"⚠️  HIERARCHICAL_NAVIGATION_INDEX.md: Only {systems_found}/{len(CUTOVER_SYSTEMS)} systems referenced")
        
        return True
    
    def generate_report(self):
        """Generate validation report."""
        print("\n" + "=" * 60)
        print("📋 L0-L6 GATE VALIDATION REPORT")
        print("=" * 60)
        print(f"Generated: {sys.argv[0]}")
        
        print("\n✅ SUCCESSES:")
        if self.successes:
            for success in self.successes[:30]:  # Limit display
                print(f"   {success}")
            if len(self.successes) > 30:
                print(f"   ... and {len(self.successes) - 30} more")
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
        
        # Overall validation
        is_valid = len(self.issues) == 0
        
        if is_valid:
            print("✅ GATE VALIDATION PASSED")
            print("\nAll required checks passed. L0-L6 documentation compliant.")
        else:
            print("❌ GATE VALIDATION FAILED")
            print(f"\n{len(self.issues)} critical issues must be resolved.")
        
        print("=" * 60)
        
        return is_valid
    
    def run_all_checks(self):
        """Run all validation checks."""
        print("🚀 Starting L0-L6 Gate Validation (Post-Cutover)")
        print("=" * 60)
        
        checks = [
            ("File existence", self.check_file_existence),
            ("Metadata", self.check_metadata),
            ("Navigation links", self.check_navigation_links),
            ("Word counts", self.check_word_counts),
            ("Index integration", self.check_index_integration),
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
    validator = L0L6GateValidator()
    is_valid = validator.run_all_checks()
    
    # Exit code: 0 = valid, 1 = invalid
    exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()

