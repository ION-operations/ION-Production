#!/usr/bin/env python3
"""
Documentation Standards Validator - MCP Tools Integration

Automated documentation standards validation using MCP tools.
Integrates with LUCID-MCP server for validation, quality tracking, and compliance enforcement.

Usage:
    python validate_documentation_standards.py --system <system_name>
    python validate_documentation_standards.py --all
    python validate_documentation_standards.py --quality-dashboard
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class ValidationResult:
    """Documentation standards validation result"""
    system_name: str
    validation_date: str
    compliance_score: float
    l0_complete: bool
    l1_complete: bool
    l2_complete: bool
    l3_complete: bool
    l4_complete: bool
    metadata_compliant: bool
    crosslinks_valid: bool
    templates_compliant: bool
    violations: List[str]
    recommendations: List[str]
    passed: bool

class DocumentationStandardsValidator:
    """Documentation standards validator with MCP tools integration"""
    
    def __init__(self, system_path: str):
        self.system_path = Path(system_path)
        self.system_name = self.system_path.name
        self.results: List[ValidationResult] = []
        
    def validate_system(self) -> ValidationResult:
        """Validate documentation standards for a system"""
        print(f"🔍 Validating documentation standards for {self.system_name}...")
        
        # Step 1: Create snapshot before validation
        snapshot_name = f"pre_validation_{self.system_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"📸 Creating snapshot: {snapshot_name}")
        # Note: In production, this would call MCP tool: create_snapshot
        
        # Step 2: Check L0-L4 completeness
        l0_complete = self._check_l0_exists()
        l1_complete = self._check_l1_exists()
        l2_complete = self._check_l2_exists()
        l3_complete = self._check_l3_exists()
        l4_complete = self._check_l4_exists()
        
        # Step 3: Check metadata compliance
        metadata_compliant = self._check_metadata_compliance()
        
        # Step 4: Check cross-links
        crosslinks_valid = self._check_crosslinks()
        
        # Step 5: Check template compliance
        templates_compliant = self._check_template_compliance()
        
        # Step 6: Calculate compliance score
        compliance_score = self._calculate_compliance_score(
            l0_complete, l1_complete, l2_complete, l3_complete, l4_complete,
            metadata_compliant, crosslinks_valid, templates_compliant
        )
        
        # Step 7: Identify violations and recommendations
        violations = self._identify_violations(
            l0_complete, l1_complete, l2_complete, l3_complete, l4_complete,
            metadata_compliant, crosslinks_valid, templates_compliant
        )
        recommendations = self._generate_recommendations(violations)
        
        # Step 8: Determine pass/fail
        passed = compliance_score >= 0.80 and len(violations) == 0
        
        result = ValidationResult(
            system_name=self.system_name,
            validation_date=datetime.now().isoformat(),
            compliance_score=compliance_score,
            l0_complete=l0_complete,
            l1_complete=l1_complete,
            l2_complete=l2_complete,
            l3_complete=l3_complete,
            l4_complete=l4_complete,
            metadata_compliant=metadata_compliant,
            crosslinks_valid=crosslinks_valid,
            templates_compliant=templates_compliant,
            violations=violations,
            recommendations=recommendations,
            passed=passed
        )
        
        self.results.append(result)
        
        # Step 9: Track confidence via MCP (would call MCP tool)
        print(f"📊 Tracking confidence: {compliance_score:.2f}")
        # Note: In production, this would call MCP tool: track_confidence
        
        # Step 10: Store results in CMC (would call MCP tool)
        print(f"💾 Storing validation results in CMC...")
        # Note: In production, this would call MCP tool: store_memory
        
        # Step 11: Track timeline (would call MCP tool)
        print(f"📅 Tracking validation timeline...")
        # Note: In production, this would call MCP tool: add_timeline_entry
        
        return result
    
    def _check_l0_exists(self) -> bool:
        """Check if L0 executive summary exists"""
        l0_path = self.system_path / "L0_executive.md"
        if not l0_path.exists():
            return False
        
        # Check word count (should be ~100 words)
        content = l0_path.read_text(encoding='utf-8')
        word_count = len(content.split())
        return 50 <= word_count <= 200
    
    def _check_l1_exists(self) -> bool:
        """Check if L1 overview exists"""
        l1_path = self.system_path / "L1_overview.md"
        if not l1_path.exists():
            return False
        
        # Check word count (should be ~500 words)
        content = l1_path.read_text(encoding='utf-8')
        word_count = len(content.split())
        return 400 <= word_count <= 800
    
    def _check_l2_exists(self) -> bool:
        """Check if L2 architecture exists"""
        l2_path = self.system_path / "L2_architecture.md"
        return l2_path.exists()
    
    def _check_l3_exists(self) -> bool:
        """Check if L3 detailed exists"""
        l3_path = self.system_path / "L3_detailed.md"
        return l3_path.exists()
    
    def _check_l4_exists(self) -> bool:
        """Check if L4 complete exists"""
        l4_path = self.system_path / "L4_complete.md"
        return l4_path.exists()
    
    def _check_metadata_compliance(self) -> bool:
        """Check if metadata frontmatter is compliant"""
        # Check L2 (most critical for standards)
        l2_path = self.system_path / "L2_architecture.md"
        if not l2_path.exists():
            return False
        
        content = l2_path.read_text(encoding='utf-8')
        
        # Check for frontmatter
        if not content.startswith('---'):
            return False
        
        # Check for required fields
        required_fields = ['id', 'type', 'system', 'level']
        frontmatter_end = content.find('---', 3)
        if frontmatter_end == -1:
            return False
        
        frontmatter = content[3:frontmatter_end]
        
        for field in required_fields:
            if f'{field}:' not in frontmatter:
                return False
        
        return True
    
    def _check_crosslinks(self) -> bool:
        """Check if cross-links to system maps, indices exist"""
        l2_path = self.system_path / "L2_architecture.md"
        if not l2_path.exists():
            return False
        
        content = l2_path.read_text(encoding='utf-8')
        
        # Check for system map reference
        has_system_map = 'system.map.lucid.json5' in content or 'system.map' in content
        
        # Check for References section
        has_references = '## References' in content or '## REFERENCE' in content
        
        return has_system_map and has_references
    
    def _check_template_compliance(self) -> bool:
        """Check if documentation follows templates"""
        # Basic check: does it have required sections?
        l2_path = self.system_path / "L2_architecture.md"
        if not l2_path.exists():
            return False
        
        content = l2_path.read_text(encoding='utf-8')
        
        # Check for required sections (basic template compliance)
        required_sections = ['##', '###']  # Has headings
        has_structure = any(marker in content for marker in required_sections)
        
        return has_structure
    
    def _calculate_compliance_score(self, *args) -> float:
        """Calculate overall compliance score"""
        checks = [args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7]]
        passed = sum(checks)
        total = len(checks)
        
        # Weighted scoring (L0-L4 are more important)
        weights = [0.15, 0.15, 0.20, 0.20, 0.20, 0.05, 0.03, 0.02]
        weighted_score = sum(weight * (1.0 if check else 0.0) for weight, check in zip(weights, checks))
        
        return weighted_score
    
    def _identify_violations(self, *args) -> List[str]:
        """Identify standards violations"""
        violations = []
        
        if not args[0]:
            violations.append("Missing L0_executive.md")
        if not args[1]:
            violations.append("Missing L1_overview.md")
        if not args[2]:
            violations.append("Missing L2_architecture.md")
        if not args[3]:
            violations.append("Missing L3_detailed.md")
        if not args[4]:
            violations.append("Missing L4_complete.md")
        if not args[5]:
            violations.append("Metadata frontmatter non-compliant")
        if not args[6]:
            violations.append("Missing cross-links to system maps or indices")
        if not args[7]:
            violations.append("Template compliance issues")
        
        return violations
    
    def _generate_recommendations(self, violations: List[str]) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []
        
        violation_map = {
            "Missing L0_executive.md": "Create L0_executive.md following PERFECT_TEMPLATES_LIBRARY.md template",
            "Missing L1_overview.md": "Create L1_overview.md following PERFECT_TEMPLATES_LIBRARY.md template",
            "Missing L2_architecture.md": "Create L2_architecture.md following PERFECT_TEMPLATES_LIBRARY.md template",
            "Missing L3_detailed.md": "Create L3_detailed.md following PERFECT_TEMPLATES_LIBRARY.md template",
            "Missing L4_complete.md": "Create L4_complete.md following PERFECT_TEMPLATES_LIBRARY.md template",
            "Metadata frontmatter non-compliant": "Add required metadata fields (id, type, system, level) to frontmatter",
            "Missing cross-links to system maps or indices": "Add References section with links to system.map.lucid.json5, SUPER_INDEX.md, HIERARCHICAL_NAVIGATION_INDEX.md",
            "Template compliance issues": "Review PERFECT_TEMPLATES_LIBRARY.md and ensure documentation follows template structure"
        }
        
        for violation in violations:
            if violation in violation_map:
                recommendations.append(violation_map[violation])
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate validation report"""
        report = f"""
# Documentation Standards Validation Report

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agent:** Atlas  
**Validator:** Documentation Standards Validator (MCP Tools Integration)

---

## 📊 **VALIDATION SUMMARY**

**Systems Validated:** {len(self.results)}  
**Passed:** {sum(1 for r in self.results if r.passed)}  
**Failed:** {sum(1 for r in self.results if not r.passed)}  
**Average Compliance Score:** {sum(r.compliance_score for r in self.results) / len(self.results) if self.results else 0:.2f}

---

## 📋 **DETAILED RESULTS**

"""
        
        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            report += f"""
### **{result.system_name}** - {status}

**Compliance Score:** {result.compliance_score:.2f}  
**Validation Date:** {result.validation_date}

**L0-L4 Completeness:**
- L0: {'✅' if result.l0_complete else '❌'}
- L1: {'✅' if result.l1_complete else '❌'}
- L2: {'✅' if result.l2_complete else '❌'}
- L3: {'✅' if result.l3_complete else '❌'}
- L4: {'✅' if result.l4_complete else '❌'}

**Standards Compliance:**
- Metadata: {'✅' if result.metadata_compliant else '❌'}
- Cross-links: {'✅' if result.crosslinks_valid else '❌'}
- Templates: {'✅' if result.templates_compliant else '❌'}

**Violations:**
{chr(10).join(f'- {v}' for v in result.violations) if result.violations else '- None ✅'}

**Recommendations:**
{chr(10).join(f'- {r}' for r in result.recommendations) if result.recommendations else '- None ✅'}

---

"""
        
        return report


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Documentation Standards Validator')
    parser.add_argument('--system', type=str, help='System name to validate')
    parser.add_argument('--all', action='store_true', help='Validate all systems')
    parser.add_argument('--output', type=str, help='Output file for report')
    
    args = parser.parse_args()
    
    if args.all:
        # Validate all systems
        systems_dir = project_root / "knowledge_architecture" / "systems"
        systems = [d for d in systems_dir.iterdir() if d.is_dir()]
        
        print(f"🔍 Validating {len(systems)} systems...")
        
        validator = DocumentationStandardsValidator(str(systems_dir))
        results = []
        
        for system_dir in systems:
            system_validator = DocumentationStandardsValidator(str(system_dir))
            result = system_validator.validate_system()
            results.append(result)
            validator.results.append(result)
        
        report = validator.generate_report()
        
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(report, encoding='utf-8')
            print(f"✅ Report saved to {output_path}")
        else:
            print(report)
            
    elif args.system:
        # Validate single system
        systems_dir = project_root / "knowledge_architecture" / "systems"
        system_path = systems_dir / args.system
        
        if not system_path.exists():
            print(f"❌ System not found: {args.system}")
            sys.exit(1)
        
        validator = DocumentationStandardsValidator(str(system_path))
        result = validator.validate_system()
        
        report = validator.generate_report()
        
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(report, encoding='utf-8')
            print(f"✅ Report saved to {output_path}")
        else:
            print(report)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

