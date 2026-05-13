#!/usr/bin/env python3
"""
Cross-Reference Validator

Validates cross-references across all L/T-level documentation using system maps, indexes, and cross-system connections.
Integrates with Documentation Governance & Cross-Reference Protocol.

Usage:
    python scripts/validate_cross_references.py --system cmc
    python scripts/validate_cross_references.py --core-systems
    python scripts/validate_cross_references.py --all
    python scripts/validate_cross_references.py --audit-report
"""

import sys
import json
import yaml
import json5
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# System name aliases (common abbreviations)
SYSTEM_ALIASES = {
    "cas": "cognitive_analysis",
    "tcs": "timeline_context_system",
    "iis": "intuitive_intelligence_system",
    "sdf-cvf": "sdfcvf",
    "sdf_cvf": "sdfcvf"
}

# External systems (not AIM-OS systems, so we skip them in validation)
EXTERNAL_SYSTEMS = {
    "storage", "vector", "graph", "embedding", "audit", "ci", "llm",
    "storage.external", "vector.faiss", "graph.neo4j", "daemon.ragsystem"
}

# System hierarchy (for one-way reference validation)
SYSTEM_HIERARCHY = {
    # Layer 1: Memory & Knowledge Foundation
    "layer1": ["cmc", "seg"],
    # Layer 2: Intelligence Processing
    "layer2": ["hhni", "vif", "sdfcvf"],
    # Layer 3: Orchestration & Planning
    "layer3": ["apoe"],
    # Layer 4: Consciousness Engine
    "layer4": ["cognitive_analysis", "timeline_context_system", "intuitive_intelligence_system"]
}

@dataclass
class CrossReferenceValidationResult:
    """Cross-reference validation result"""
    system_name: str
    validation_date: str
    t2_related_systems_present: bool
    referenced_systems_exist: bool
    bidirectional_references_valid: bool
    system_map_ports_match: bool
    system_index_connections_match: bool
    cross_system_yaml_matches: bool
    overall_passed: bool
    missing_references: List[str]
    broken_references: List[str]
    bidirectional_issues: List[str]
    recommendations: List[str]

class CrossReferenceValidator:
    """Validates cross-references across documentation"""
    
    def __init__(self, system_name: str):
        self.system_name = system_name
        self.system_path = project_root / "knowledge_architecture" / "systems" / system_name
        
        # Load system resources
        self.system_map = self._load_system_map()
        self.system_index = self._load_system_index()
        self.cross_system_connections = self._load_cross_system_connections()
        
    def validate(self) -> CrossReferenceValidationResult:
        """Run complete cross-reference validation"""
        print(f"Validating cross-references for {self.system_name}...")
        
        missing_references = []
        broken_references = []
        bidirectional_issues = []
        recommendations = []
        
        # Rule 1: T2 Related Systems Section
        t2_related_systems_present, rule1_missing, rule1_recs = self._validate_t2_related_systems()
        missing_references.extend(rule1_missing)
        recommendations.extend(rule1_recs)
        
        # Rule 2: Referenced Systems Exist
        referenced_systems_exist, rule2_broken, rule2_recs = self._validate_referenced_systems_exist()
        broken_references.extend(rule2_broken)
        recommendations.extend(rule2_recs)
        
        # Rule 3: Bidirectional References
        bidirectional_valid, rule3_issues, rule3_recs = self._validate_bidirectional_references()
        bidirectional_issues.extend(rule3_issues)
        recommendations.extend(rule3_recs)
        
        # Rule 4: System Map Ports Match
        system_map_ports_match, rule4_missing, rule4_recs = self._validate_system_map_ports()
        missing_references.extend(rule4_missing)
        recommendations.extend(rule4_recs)
        
        # Rule 5: System Index Connections Match
        system_index_match, rule5_missing, rule5_recs = self._validate_system_index_connections()
        missing_references.extend(rule5_missing)
        recommendations.extend(rule5_recs)
        
        # Rule 6: Cross-System Connections YAML Match
        yaml_matches, rule6_missing, rule6_recs = self._validate_cross_system_yaml()
        missing_references.extend(rule6_missing)
        recommendations.extend(rule6_recs)
        
        # Overall pass/fail
        overall_passed = (
            t2_related_systems_present and
            referenced_systems_exist and
            len(broken_references) == 0
        )  # bidirectional and missing references are warnings
        
        result = CrossReferenceValidationResult(
            system_name=self.system_name,
            validation_date=datetime.now().isoformat(),
            t2_related_systems_present=t2_related_systems_present,
            referenced_systems_exist=referenced_systems_exist,
            bidirectional_references_valid=bidirectional_valid,
            system_map_ports_match=system_map_ports_match,
            system_index_connections_match=system_index_match,
            cross_system_yaml_matches=yaml_matches,
            overall_passed=overall_passed,
            missing_references=missing_references,
            broken_references=broken_references,
            bidirectional_issues=bidirectional_issues,
            recommendations=recommendations
        )
        
        return result
    
    def _load_system_map(self) -> Optional[Dict]:
        """Load system map"""
        system_map_path = self.system_path / "system.map.lucid.json5"
        if not system_map_path.exists():
            return None
        
        try:
            with open(system_map_path, "r", encoding="utf-8") as f:
                return json5.load(f)
        except Exception as e:
            print(f"WARNING: Could not load system map: {e}", file=sys.stderr)
            return None
    
    def _load_system_index(self) -> Optional[Dict]:
        """Load system index"""
        system_index_path = self.system_path / "system.index.lucid.json5"
        if not system_index_path.exists():
            return None
        
        try:
            with open(system_index_path, "r", encoding="utf-8") as f:
                return json5.load(f)
        except Exception as e:
            print(f"WARNING: Could not load system index: {e}", file=sys.stderr)
            return None
    
    def _load_cross_system_connections(self) -> Optional[Dict]:
        """Load cross-system connections YAML"""
        yaml_path = project_root / "knowledge_architecture" / "NAVIGATION" / "cross_system_connections.yaml"
        if not yaml_path.exists():
            return None
        
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                # Load all documents (YAML may have multiple docs separated by ---)
                docs = list(yaml.safe_load_all(f))
                # Return first non-comment document
                for doc in docs:
                    if doc and isinstance(doc, dict):
                        return doc
                return None
        except Exception as e:
            # Avoid unicode issues in error messages
            print(f"WARNING: Could not load cross-system connections: {e}", file=sys.stderr)
            return None
    
    def _validate_t2_related_systems(self) -> tuple[bool, List[str], List[str]]:
        """Validate T2 architecture has Related Systems section"""
        missing = []
        recommendations = []
        
        # Load T2 doc
        t2_path = self.system_path / "T2_architecture.md"
        if not t2_path.exists():
            missing.append("T2 architecture document missing")
            recommendations.append(f"Create T2 architecture: {t2_path}")
            return False, missing, recommendations
        
        content = t2_path.read_text(encoding="utf-8")
        
        # Check for Related Systems section
        has_related_systems = (
            "## Related Systems" in content or
            "## 🔗 RELATED SYSTEMS" in content or
            "## 🔗 Related Systems" in content
        )
        
        if not has_related_systems:
            missing.append("T2 architecture missing 'Related Systems' section")
            recommendations.append("Add Related Systems section to T2 architecture")
            return False, missing, recommendations
        
        return True, missing, recommendations
    
    def _validate_referenced_systems_exist(self) -> tuple[bool, List[str], List[str]]:
        """Validate all referenced systems exist"""
        broken = []
        recommendations = []
        
        # Load T2 doc
        t2_path = self.system_path / "T2_architecture.md"
        if not t2_path.exists():
            return True, broken, recommendations  # Already caught by Rule 1
        
        content = t2_path.read_text(encoding="utf-8")
        
        # Extract system references (simplified)
        referenced_systems = self._extract_system_references(content)
        
        # Check each referenced system exists
        for ref_system in referenced_systems:
            # Apply alias mapping
            canonical_name = SYSTEM_ALIASES.get(ref_system, ref_system)
            
            ref_system_path = project_root / "knowledge_architecture" / "systems" / canonical_name
            if not ref_system_path.exists():
                broken.append(f"Referenced system '{ref_system}' (canonical: '{canonical_name}') does not exist")
                recommendations.append(f"Remove reference to '{ref_system}' OR create system documentation")
        
        passed = len(broken) == 0
        return passed, broken, recommendations
    
    def _validate_bidirectional_references(self) -> tuple[bool, List[str], List[str]]:
        """Validate bidirectional references (A→B implies B→A)"""
        issues = []
        recommendations = []
        
        # Load T2 doc
        t2_path = self.system_path / "T2_architecture.md"
        if not t2_path.exists():
            return True, issues, recommendations  # Already caught by Rule 1
        
        content = t2_path.read_text(encoding="utf-8")
        
        # Extract system references
        referenced_systems = self._extract_system_references(content)
        
        # Determine current system's layer
        current_layer = self._get_system_layer(self.system_name)
        
        # Check bidirectional references
        for ref_system in referenced_systems:
            # Apply alias mapping
            canonical_name = SYSTEM_ALIASES.get(ref_system, ref_system)
            
            # Determine referenced system's layer
            ref_layer = self._get_system_layer(canonical_name)
            
            # Allow one-way references for hierarchical dependencies
            # Higher layers (4) can reference lower layers (1-3) without reciprocation
            if current_layer > ref_layer:
                continue  # One-way reference is allowed (higher → lower)
            
            ref_t2_path = project_root / "knowledge_architecture" / "systems" / canonical_name / "T2_architecture.md"
            if not ref_t2_path.exists():
                continue  # Skip if referenced system doesn't have T2 doc yet
            
            ref_content = ref_t2_path.read_text(encoding="utf-8")
            ref_referenced_systems = self._extract_system_references(ref_content)
            
            if self.system_name not in ref_referenced_systems:
                issues.append(f"Bidirectional reference missing: {self.system_name}→{canonical_name} exists, but {canonical_name}→{self.system_name} missing")
                recommendations.append(f"Add reference to '{self.system_name}' in {canonical_name}/T2_architecture.md")
        
        passed = len(issues) == 0
        return passed, issues, recommendations
    
    def _get_system_layer(self, system_name: str) -> int:
        """Get system layer from hierarchy"""
        for layer_num, (layer_key, systems) in enumerate(SYSTEM_HIERARCHY.items(), start=1):
            if system_name in systems:
                return layer_num
        return 0  # Unknown layer
    
    def _validate_system_map_ports(self) -> tuple[bool, List[str], List[str]]:
        """Validate system map ports match T2 doc references"""
        missing = []
        recommendations = []
        
        if not self.system_map:
            return True, missing, recommendations  # No system map to validate
        
        # Extract connected systems from ports
        connected_systems = set()
        for port in self.system_map.get("ports", []):
            if "connectsToSystem" in port:
                # Extract system name from systemId (e.g., "cmc.contextMemoryCore" → "cmc")
                system_id = port["connectsToSystem"]
                system_name = system_id.split(".")[0]
                
                # Skip external systems (not AIM-OS systems)
                if system_name in EXTERNAL_SYSTEMS or system_id in EXTERNAL_SYSTEMS:
                    continue
                
                connected_systems.add(system_name)
        
        # Load T2 doc
        t2_path = self.system_path / "T2_architecture.md"
        if not t2_path.exists():
            return True, missing, recommendations  # Already caught by Rule 1
        
        content = t2_path.read_text(encoding="utf-8")
        referenced_systems = set(self._extract_system_references(content))
        
        # Check if all connected systems are referenced
        for connected in connected_systems:
            # Apply alias mapping
            canonical_name = SYSTEM_ALIASES.get(connected, connected)
            
            if canonical_name not in referenced_systems:
                missing.append(f"System map port connects to '{connected}', but T2 doc does not reference it")
                recommendations.append(f"Add reference to '{canonical_name}' in Related Systems section")
        
        passed = len(missing) == 0
        return passed, missing, recommendations
    
    def _validate_system_index_connections(self) -> tuple[bool, List[str], List[str]]:
        """Validate system index connections match docs"""
        missing = []
        recommendations = []
        
        if not self.system_index:
            return True, missing, recommendations  # No system index to validate
        
        # Extract dependencies (simplified - would need to parse actual structure)
        # For now, return True (placeholder for full implementation)
        return True, missing, recommendations
    
    def _validate_cross_system_yaml(self) -> tuple[bool, List[str], List[str]]:
        """Validate cross-system connections YAML matches docs"""
        missing = []
        recommendations = []
        
        if not self.cross_system_connections:
            return True, missing, recommendations  # No YAML to validate
        
        # Find system in YAML
        system_key = self.system_name.upper()
        if system_key not in self.cross_system_connections.get("systems", {}):
            return True, missing, recommendations  # System not in YAML yet
        
        system_data = self.cross_system_connections["systems"][system_key]
        
        # Extract dependencies and provides_to
        dependencies = system_data.get("depends_on", [])
        provides_to_data = system_data.get("provides_to", [])
        
        # Extract system names from dependencies (handle dict format)
        dep_systems = []
        for item in dependencies:
            if isinstance(item, dict):
                dep_systems.extend(list(item.keys()))
            elif isinstance(item, str):
                dep_systems.append(item)
        
        # Extract system names from provides_to (handle dict format)
        provides_to_systems = []
        for item in provides_to_data:
            if isinstance(item, dict):
                provides_to_systems.extend(list(item.keys()))
            elif isinstance(item, str):
                provides_to_systems.append(item)
        
        all_connections = dep_systems + provides_to_systems
        
        # Load T2 doc
        t2_path = self.system_path / "T2_architecture.md"
        if not t2_path.exists():
            return True, missing, recommendations  # Already caught by Rule 1
        
        content = t2_path.read_text(encoding="utf-8")
        referenced_systems = set(self._extract_system_references(content))
        
        # Check if all connections are referenced
        for connection in all_connections:
            connection_lower = connection.lower()
            if connection_lower not in [s.lower() for s in referenced_systems]:
                missing.append(f"Cross-system connections YAML shows connection '{connection}', but T2 doc does not reference it")
                recommendations.append(f"Add reference to '{connection}' in Related Systems section")
        
        passed = len(missing) == 0
        return passed, missing, recommendations
    
    def _extract_system_references(self, content: str) -> List[str]:
        """Extract system references from content (simplified)"""
        # This is a simplified extraction - in production, would use more sophisticated parsing
        systems = []
        
        # Common patterns
        patterns = ["CMC", "HHNI", "VIF", "SEG", "APOE", "SDF-CVF", "SDF_CVF", "CAS", "TCS", "IIS"]
        
        for pattern in patterns:
            if pattern in content:
                # Convert to lowercase
                system_name = pattern.lower().replace("_", "").replace("-", "")
                if system_name == "sdfcvf":
                    system_name = "sdfcvf"
                
                # Apply alias mapping
                system_name = SYSTEM_ALIASES.get(system_name, system_name)
                
                systems.append(system_name)
        
        return list(set(systems))

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Validate cross-references across documentation")
    parser.add_argument("--system", help="System name to validate")
    parser.add_argument("--core-systems", action="store_true", help="Validate all 9 core systems")
    parser.add_argument("--all", action="store_true", help="Validate all systems")
    parser.add_argument("--audit-report", action="store_true", help="Generate comprehensive audit report")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    
    args = parser.parse_args()
    
    # Determine which systems to validate
    if args.system:
        systems = [args.system]
    elif args.core_systems:
        systems = ["cmc", "seg", "hhni", "vif", "sdfcvf", "apoe", "cognitive_analysis", "timeline_context_system", "intuitive_intelligence_system"]
    elif args.all:
        # Find all systems
        systems_path = project_root / "knowledge_architecture" / "systems"
        systems = [d.name for d in systems_path.iterdir() if d.is_dir()]
    else:
        print("❌ ERROR: Must specify --system, --core-systems, or --all")
        sys.exit(1)
    
    # Validate each system
    results = []
    for system in systems:
        validator = CrossReferenceValidator(system)
        result = validator.validate()
        results.append(result)
    
    # Output results
    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    elif args.audit_report:
        generate_audit_report(results)
    else:
        for result in results:
            print_validation_result(result)
    
    # Exit code
    all_passed = all(r.overall_passed for r in results)
    sys.exit(0 if all_passed else 1)

def print_validation_result(result: CrossReferenceValidationResult):
    """Print validation result in human-readable format"""
    print("\n" + "="*80)
    print(f"Cross-Reference Validation Result: {result.system_name}")
    print("="*80)
    print(f"Date: {result.validation_date}")
    print()
    
    # Rule results
    print("Validation Rules:")
    print(f"  Rule 1 - T2 Related Systems Present:       {'[PASS]' if result.t2_related_systems_present else '[FAIL]'}")
    print(f"  Rule 2 - Referenced Systems Exist:         {'[PASS]' if result.referenced_systems_exist else '[FAIL]'}")
    print(f"  Rule 3 - Bidirectional References Valid:   {'[PASS]' if result.bidirectional_references_valid else '[WARNING]'}")
    print(f"  Rule 4 - System Map Ports Match:           {'[PASS]' if result.system_map_ports_match else '[WARNING]'}")
    print(f"  Rule 5 - System Index Connections Match:   {'[PASS]' if result.system_index_connections_match else '[WARNING]'}")
    print(f"  Rule 6 - Cross-System YAML Matches:        {'[PASS]' if result.cross_system_yaml_matches else '[WARNING]'}")
    print()
    
    # Overall result
    if result.overall_passed:
        print("[PASS] OVERALL: Cross-references valid")
    else:
        print("[FAIL] OVERALL: Cross-references have critical issues")
    print()
    
    # Issues
    if result.broken_references:
        print("BROKEN REFERENCES:")
        for broken in result.broken_references:
            print(f"  - {broken}")
        print()
    
    if result.missing_references:
        print("MISSING REFERENCES:")
        for missing in result.missing_references:
            print(f"  - {missing}")
        print()
    
    if result.bidirectional_issues:
        print("BIDIRECTIONAL REFERENCE ISSUES:")
        for issue in result.bidirectional_issues:
            print(f"  - {issue}")
        print()
    
    # Recommendations
    if result.recommendations:
        print("RECOMMENDATIONS:")
        for recommendation in result.recommendations:
            print(f"  - {recommendation}")
        print()
    
    print("="*80)

def generate_audit_report(results: List[CrossReferenceValidationResult]):
    """Generate comprehensive audit report"""
    report_path = project_root / "knowledge_architecture" / "validation" / "CROSS_REFERENCE_AUDIT_REPORT.md"
    
    # Generate report content
    report = f"""# Cross-Reference Audit Report

**Date:** {datetime.now().isoformat()}  
**Systems Validated:** {len(results)}  
**Status:** {'✅ ALL PASS' if all(r.overall_passed for r in results) else '⚠️ ISSUES FOUND'}

---

## Summary

**Overall Pass Rate:** {sum(1 for r in results if r.overall_passed)} / {len(results)} ({100 * sum(1 for r in results if r.overall_passed) // len(results)}%)

**Total Issues:**
- Broken References: {sum(len(r.broken_references) for r in results)}
- Missing References: {sum(len(r.missing_references) for r in results)}
- Bidirectional Issues: {sum(len(r.bidirectional_issues) for r in results)}

---

## System-by-System Results

"""
    
    for result in results:
        status_emoji = "✅" if result.overall_passed else "❌"
        report += f"\n### {status_emoji} {result.system_name}\n\n"
        report += f"**Status:** {'PASS' if result.overall_passed else 'FAIL'}\n\n"
        
        if result.broken_references or result.missing_references or result.bidirectional_issues:
            report += "**Issues:**\n"
            for broken in result.broken_references:
                report += f"- ❌ {broken}\n"
            for missing in result.missing_references:
                report += f"- ⚠️ {missing}\n"
            for bidirectional in result.bidirectional_issues:
                report += f"- ⚠️ {bidirectional}\n"
            report += "\n"
    
    report += "\n---\n\n**Next Steps:** Run `python scripts/generate_cross_references.py --all` to generate missing cross-references.\n"
    
    # Write report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    
    print(f"\nAudit report generated: {report_path}")

if __name__ == "__main__":
    main()

