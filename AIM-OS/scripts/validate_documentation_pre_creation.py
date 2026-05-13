#!/usr/bin/env python3
"""
Documentation Pre-Creation Validator

Validates documentation before creation to prevent orphaned docs and ensure system alignment.
Integrates with Documentation Governance & Cross-Reference Protocol.

Usage:
    python scripts/validate_documentation_pre_creation.py \
      --doc-type idea \
      --location "ideas/architects/claude-sonnet/SEED_new_idea.md" \
      --systems "cmc,hhni" \
      --frontmatter "frontmatter.yaml"
    
    python scripts/validate_documentation_pre_creation.py \
      --doc-type analysis \
      --location "analysis/cross_system/NEW_ANALYSIS.md" \
      --standalone "Meta-analysis across all systems"
"""

import sys
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class PreCreationValidationResult:
    """Pre-creation validation result"""
    doc_type: str
    location: str
    validation_date: str
    system_alignment_passed: bool
    template_compliance_passed: bool
    location_standards_passed: bool
    cross_reference_prep_passed: bool
    overall_passed: bool
    violations: List[str]
    warnings: List[str]
    recommendations: List[str]
    auto_fixes: List[str]

class PreCreationValidator:
    """Validates documentation before creation"""
    
    def __init__(self, doc_type: str, location: str, systems: Optional[List[str]] = None, 
                 standalone_reason: Optional[str] = None, frontmatter: Optional[Dict] = None):
        self.doc_type = doc_type
        self.location = Path(location)
        self.systems = systems or []
        self.standalone_reason = standalone_reason
        self.frontmatter = frontmatter or {}
        
        # Load system hierarchy
        self.system_hierarchy = self._load_system_hierarchy()
        
        # Load templates
        self.templates = self._load_templates()
        
    def validate(self) -> PreCreationValidationResult:
        """Run complete pre-creation validation"""
        print(f"🔍 Validating pre-creation for {self.location}...")
        
        violations = []
        warnings = []
        recommendations = []
        auto_fixes = []
        
        # Gate 1: System Alignment
        system_alignment_passed, sys_violations, sys_warnings = self._validate_system_alignment()
        violations.extend(sys_violations)
        warnings.extend(sys_warnings)
        
        # Gate 2: Template Compliance
        template_compliance_passed, tmpl_violations, tmpl_recommendations = self._validate_template_compliance()
        violations.extend(tmpl_violations)
        recommendations.extend(tmpl_recommendations)
        
        # Gate 3: Location Standards
        location_standards_passed, loc_violations, loc_auto_fixes = self._validate_location_standards()
        violations.extend(loc_violations)
        auto_fixes.extend(loc_auto_fixes)
        
        # Gate 4: Cross-Reference Preparation
        cross_ref_prep_passed, ref_warnings, ref_recommendations = self._validate_cross_reference_prep()
        warnings.extend(ref_warnings)
        recommendations.extend(ref_recommendations)
        
        # Overall pass/fail
        overall_passed = (
            system_alignment_passed and
            template_compliance_passed and
            location_standards_passed
        )  # cross_ref_prep can have warnings, not failures
        
        result = PreCreationValidationResult(
            doc_type=self.doc_type,
            location=str(self.location),
            validation_date=datetime.now().isoformat(),
            system_alignment_passed=system_alignment_passed,
            template_compliance_passed=template_compliance_passed,
            location_standards_passed=location_standards_passed,
            cross_reference_prep_passed=cross_ref_prep_passed,
            overall_passed=overall_passed,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            auto_fixes=auto_fixes
        )
        
        return result
    
    def _validate_system_alignment(self) -> tuple[bool, List[str], List[str]]:
        """Validate system alignment"""
        violations = []
        warnings = []
        
        # Check if systems provided OR standalone reason
        has_systems = len(self.systems) > 0
        has_standalone = self.standalone_reason is not None and len(self.standalone_reason) > 0
        
        if not has_systems and not has_standalone:
            violations.append("CRITICAL: Must reference at least one system OR provide standalone reason")
            return False, violations, warnings
        
        # If systems provided, validate they exist
        if has_systems:
            for system in self.systems:
                if not self._system_exists(system):
                    violations.append(f"CRITICAL: System '{system}' does not exist in SYSTEM_HIERARCHY.md")
            
            if violations:
                return False, violations, warnings
        
        # If standalone, check reason is meaningful
        if has_standalone and len(self.standalone_reason) < 20:
            warnings.append("WARNING: Standalone reason is very short, consider being more specific")
        
        return True, violations, warnings
    
    def _validate_template_compliance(self) -> tuple[bool, List[str], List[str]]:
        """Validate template compliance"""
        violations = []
        recommendations = []
        
        # Check if template exists for doc type
        template = self.templates.get(self.doc_type)
        if not template:
            violations.append(f"CRITICAL: No template exists for doc type '{self.doc_type}'")
            recommendations.append(f"Available doc types: {', '.join(self.templates.keys())}")
            return False, violations, recommendations
        
        # Check required frontmatter fields
        required_fields = template.get("required_fields", [])
        for field in required_fields:
            if field not in self.frontmatter:
                violations.append(f"CRITICAL: Missing required frontmatter field '{field}'")
        
        if violations:
            recommendations.append(f"See template: knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md")
            return False, violations, recommendations
        
        return True, violations, recommendations
    
    def _validate_location_standards(self) -> tuple[bool, List[str], List[str]]:
        """Validate location and naming standards"""
        violations = []
        auto_fixes = []
        
        # Get expected location pattern based on doc type
        expected_pattern = self._get_expected_location_pattern(self.doc_type)
        
        # Check if location matches pattern
        if not self._location_matches_pattern(self.location, expected_pattern):
            violations.append(f"CRITICAL: Location does not match expected pattern: {expected_pattern}")
            
            # Suggest auto-fix
            suggested_location = self._suggest_location(self.doc_type, self.location)
            auto_fixes.append(f"Suggested location: {suggested_location}")
            
            return False, violations, auto_fixes
        
        # Check naming conventions
        if not self._naming_follows_conventions(self.location, self.doc_type):
            violations.append(f"CRITICAL: Naming does not follow conventions for doc type '{self.doc_type}'")
            
            # Suggest auto-fix
            suggested_name = self._suggest_naming(self.doc_type, self.location)
            auto_fixes.append(f"Suggested naming: {suggested_name}")
            
            return False, violations, auto_fixes
        
        return True, violations, auto_fixes
    
    def _validate_cross_reference_prep(self) -> tuple[bool, List[str], List[str]]:
        """Validate cross-reference preparation"""
        warnings = []
        recommendations = []
        
        # Check if related systems identified
        if not self.systems and not self.standalone_reason:
            warnings.append("WARNING: No related systems identified")
            recommendations.append("Identify related systems from system maps/indexes")
        
        # Check if related docs identified
        if "related_docs" not in self.frontmatter or len(self.frontmatter.get("related_docs", [])) == 0:
            warnings.append("WARNING: No related docs identified")
            recommendations.append("Identify related docs for cross-referencing")
        
        # Always pass (warnings only, not failures)
        return True, warnings, recommendations
    
    def _load_system_hierarchy(self) -> Dict:
        """Load system hierarchy"""
        hierarchy_path = project_root / "knowledge_architecture" / "SYSTEM_HIERARCHY.md"
        if not hierarchy_path.exists():
            return {}
        
        # Parse system hierarchy for system list
        content = hierarchy_path.read_text(encoding="utf-8")
        
        # Extract systems (simple parsing)
        systems = set()
        for line in content.split("\n"):
            if line.strip().startswith("- **") and "**" in line[5:]:
                system_name = line.split("**")[1].strip()
                if "(" in system_name:
                    system_name = system_name.split("(")[0].strip()
                systems.add(system_name.lower())
        
        return {"systems": list(systems)}
    
    def _load_templates(self) -> Dict:
        """Load available templates"""
        # Simplified template loading (in production, would parse PERFECT_TEMPLATES_LIBRARY.md)
        return {
            "idea": {"required_fields": ["id", "systems", "tags", "created", "author", "status"]},
            "analysis": {"required_fields": ["id", "systems", "tags", "created", "author", "status", "methodology"]},
            "coordination": {"required_fields": ["id", "tags", "created", "author", "status"]},
            "system_doc": {"required_fields": ["id", "system", "level", "type", "title", "description", "audience", "created", "author", "status"]},
            "protocol": {"required_fields": ["id", "system", "level", "type", "title", "description", "created", "author", "status"]}
        }
    
    def _system_exists(self, system: str) -> bool:
        """Check if system exists in hierarchy"""
        return system.lower() in [s.lower() for s in self.system_hierarchy.get("systems", [])]
    
    def _get_expected_location_pattern(self, doc_type: str) -> str:
        """Get expected location pattern for doc type"""
        patterns = {
            "idea": "ideas/{category}/{agent}/{TYPE}_{name}.md",
            "system_doc": "knowledge_architecture/systems/{system}/T{0-6}_{type}.md",
            "protocol": "knowledge_architecture/AETHER_MEMORY/protocols/T{0-6}_{name}.md",
            "coordination": "coordination/{YYYY-MM-DD}_{topic}.md",
            "analysis": "analysis/{category}/{name}.md"
        }
        return patterns.get(doc_type, "unknown")
    
    def _location_matches_pattern(self, location: Path, pattern: str) -> bool:
        """Check if location matches expected pattern"""
        # Simplified pattern matching (in production, would use regex)
        location_str = str(location)
        
        if "ideas/" in pattern:
            return location_str.startswith("ideas/")
        elif "knowledge_architecture/systems/" in pattern:
            return location_str.startswith("knowledge_architecture/systems/")
        elif "coordination/" in pattern:
            return location_str.startswith("coordination/")
        elif "analysis/" in pattern:
            return location_str.startswith("analysis/")
        
        return True  # Default to pass for unknown patterns
    
    def _naming_follows_conventions(self, location: Path, doc_type: str) -> bool:
        """Check if naming follows conventions"""
        # Simplified naming check (in production, would use regex)
        filename = location.name
        
        if doc_type == "system_doc":
            # Should be T{0-6}_{type}.md
            return filename.startswith("T") and filename.endswith(".md")
        elif doc_type == "idea":
            # Should be {TYPE}_{description}.md
            return "_" in filename and filename.endswith(".md")
        elif doc_type == "coordination":
            # Should be {YYYY-MM-DD}_{topic}.md
            return len(filename.split("-")) >= 3
        
        return True  # Default to pass for unknown types
    
    def _suggest_location(self, doc_type: str, current_location: Path) -> str:
        """Suggest correct location"""
        if doc_type == "idea":
            return f"ideas/architects/claude-sonnet/{current_location.name}"
        elif doc_type == "system_doc":
            return f"knowledge_architecture/systems/{{system}}/{current_location.name}"
        elif doc_type == "coordination":
            return f"coordination/{datetime.now().strftime('%Y-%m-%d')}_{current_location.stem}.md"
        
        return str(current_location)
    
    def _suggest_naming(self, doc_type: str, current_location: Path) -> str:
        """Suggest correct naming"""
        if doc_type == "system_doc":
            return "T0_executive.md (or T1_overview.md, T2_architecture.md, etc.)"
        elif doc_type == "idea":
            return "SEED_description.md (or BLUEPRINT_name.md, VALIDATION_name.md, etc.)"
        elif doc_type == "coordination":
            return f"{datetime.now().strftime('%Y-%m-%d')}_topic.md"
        
        return current_location.name

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Validate documentation before creation")
    parser.add_argument("--doc-type", required=True, help="Document type (idea, analysis, coordination, system_doc, protocol)")
    parser.add_argument("--location", required=True, help="Proposed location for the document")
    parser.add_argument("--systems", help="Comma-separated list of related systems")
    parser.add_argument("--standalone", help="Standalone reason (if not related to any system)")
    parser.add_argument("--frontmatter", help="Path to frontmatter YAML file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    
    args = parser.parse_args()
    
    # Parse systems
    systems = args.systems.split(",") if args.systems else []
    
    # Load frontmatter if provided
    frontmatter = {}
    if args.frontmatter:
        frontmatter_path = Path(args.frontmatter)
        if frontmatter_path.exists():
            with open(frontmatter_path, "r", encoding="utf-8") as f:
                frontmatter = yaml.safe_load(f)
    
    # Create validator
    validator = PreCreationValidator(
        doc_type=args.doc_type,
        location=args.location,
        systems=systems,
        standalone_reason=args.standalone,
        frontmatter=frontmatter
    )
    
    # Run validation
    result = validator.validate()
    
    # Output result
    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print_validation_result(result)
    
    # Exit code
    sys.exit(0 if result.overall_passed else 1)

def print_validation_result(result: PreCreationValidationResult):
    """Print validation result in human-readable format"""
    print("\n" + "="*80)
    print(f"📋 Pre-Creation Validation Result")
    print("="*80)
    print(f"Doc Type: {result.doc_type}")
    print(f"Location: {result.location}")
    print(f"Date: {result.validation_date}")
    print()
    
    # Gate results
    print("🚪 Validation Gates:")
    print(f"  Gate 1 - System Alignment:        {'✅ PASS' if result.system_alignment_passed else '❌ FAIL'}")
    print(f"  Gate 2 - Template Compliance:     {'✅ PASS' if result.template_compliance_passed else '❌ FAIL'}")
    print(f"  Gate 3 - Location Standards:      {'✅ PASS' if result.location_standards_passed else '❌ FAIL'}")
    print(f"  Gate 4 - Cross-Reference Prep:    {'✅ PASS' if result.cross_reference_prep_passed else '⚠️ WARNING'}")
    print()
    
    # Overall result
    if result.overall_passed:
        print("✅ OVERALL: PASS - Safe to create documentation")
    else:
        print("❌ OVERALL: FAIL - Do not create documentation until violations fixed")
    print()
    
    # Violations
    if result.violations:
        print("❌ VIOLATIONS:")
        for violation in result.violations:
            print(f"  - {violation}")
        print()
    
    # Warnings
    if result.warnings:
        print("⚠️ WARNINGS:")
        for warning in result.warnings:
            print(f"  - {warning}")
        print()
    
    # Recommendations
    if result.recommendations:
        print("💡 RECOMMENDATIONS:")
        for recommendation in result.recommendations:
            print(f"  - {recommendation}")
        print()
    
    # Auto-fixes
    if result.auto_fixes:
        print("🔧 AUTO-FIXES AVAILABLE:")
        for auto_fix in result.auto_fixes:
            print(f"  - {auto_fix}")
        print()
    
    print("="*80)

if __name__ == "__main__":
    main()

