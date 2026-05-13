#!/usr/bin/env python3
"""
Daemon/RAG System - Standards Compliance Audit Script

Audits daemon system against all 34 documentation standards.

Author: Solo
Date: 2025-10-30
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Add daemon_rag_system to path
sys.path.insert(0, str(Path(__file__).parent.parent / "daemon_rag_system"))

@dataclass
class ComplianceResult:
    """Result of a compliance check"""
    standard_name: str
    category: str
    compliant: bool
    issues: List[str]
    recommendations: List[str]
    severity: str  # "critical", "high", "medium", "low"

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# Define all 34 standards
STANDARDS = {
    "Phase 1: Foundational Standards (6)": [
        ("L0-L6 Documentation", "foundational"),
        ("System Maps", "foundational"),
        ("System Indexes", "foundational"),
        ("Metadata", "foundational"),
        ("Validation Framework", "foundational"),
        ("Templates Library", "foundational"),
    ],
    "Phase 2: Consciousness & Memory (6)": [
        ("Thought Journals", "consciousness"),
        ("Decision Logs", "consciousness"),
        ("Learning Logs", "consciousness"),
        ("Active Context", "consciousness"),
        ("Session Continuity", "consciousness"),
        ("Questions for Braden", "consciousness"),
    ],
    "Phase 3: Planning & Goals (5)": [
        ("Goal Tree", "planning"),
        ("KPI Metrics", "planning"),
        ("Task Dependency Map", "planning"),
        ("Project Plans", "planning"),
        ("System Hierarchy", "planning"),
    ],
    "Phase 4: Supporting Standards (17)": [
        # Timeline & History (3)
        ("Timeline Context Entries", "timeline"),
        ("Build Timeline", "timeline"),
        ("Build Ledger", "timeline"),
        # Coordination & Communication (3)
        ("Coordination Files", "coordination"),
        ("Status Reports", "coordination"),
        ("Goal Dashboard", "coordination"),
        # Navigation & Indexing (2)
        ("SUPER_INDEX", "navigation"),
        ("Hierarchical Navigation Index", "navigation"),
        # Error & Quality (3)
        ("Error Intelligence", "quality"),
        ("Test Documentation", "quality"),
        ("Quality Metrics", "quality"),
        # Research & Ideas (2)
        ("Research Documentation", "research"),
        ("Ideas & Concepts", "research"),
        # Audit & Analysis (2)
        ("Audit Reports", "audit"),
        ("Analysis Documentation", "audit"),
        # Architecture (2)
        ("Architecture Documentation", "architecture"),
        ("Component Documentation", "architecture"),
    ],
}

def check_l0_l6_compliance(daemon_path: Path) -> ComplianceResult:
    """Check L0-L6 documentation compliance"""
    issues = []
    recommendations = []
    
    # Check if L0-L4 docs exist (relative to project root)
    project_root = daemon_path.parent
    doc_path = project_root / "knowledge_architecture" / "systems" / "daemon_rag_system"
    l0_exists = (doc_path / "L0_executive.md").exists()
    l1_exists = (doc_path / "L1_overview.md").exists()
    l2_exists = (doc_path / "L2_architecture.md").exists()
    l3_exists = (doc_path / "L3_detailed.md").exists()
    l4_exists = (doc_path / "L4_complete.md").exists()
    
    if not all([l0_exists, l1_exists, l2_exists, l3_exists, l4_exists]):
        missing = []
        if not l0_exists: missing.append("L0")
        if not l1_exists: missing.append("L1")
        if not l2_exists: missing.append("L2")
        if not l3_exists: missing.append("L3")
        if not l4_exists: missing.append("L4")
        issues.append(f"Missing L0-L4 documentation files: {', '.join(missing)}")
        recommendations.append("Create complete L0-L4 documentation suite")
    
    # Check word counts (approximate) - only if files exist
    if l3_exists:
        try:
            l3_content = (doc_path / "L3_detailed.md").read_text(encoding='utf-8')
            l3_words = len(l3_content.split())
            if l3_words < 8000:
                issues.append(f"L3 documentation below target (current: {l3_words}, target: 8000-12000)")
                recommendations.append("Expand L3 documentation to meet word count targets")
        except Exception as e:
            issues.append(f"Could not read L3 file: {e}")
    
    compliant = len(issues) == 0
    severity = Severity.CRITICAL if not compliant else Severity.LOW
    
    return ComplianceResult(
        standard_name="L0-L6 Documentation",
        category="foundational",
        compliant=compliant,
        issues=issues,
        recommendations=recommendations,
        severity=severity.value
    )

def check_metadata_compliance(daemon_path: Path) -> ComplianceResult:
    """Check metadata standards compliance"""
    issues = []
    recommendations = []
    
    # Check for metadata in main files
    main_file = daemon_path / "daemon_rag_system.py"
    if main_file.exists():
        content = main_file.read_text(encoding='utf-8')
        has_metadata = any(keyword in content.lower() for keyword in [
            "system_id", "classification", "status", "last_updated", "owner"
        ])
        
        if not has_metadata:
            issues.append("Missing metadata header in main file")
            recommendations.append("Add metadata header to daemon_rag_system.py")
    
    compliant = len(issues) == 0
    severity = Severity.MEDIUM if not compliant else Severity.LOW
    
    return ComplianceResult(
        standard_name="Metadata",
        category="foundational",
        compliant=compliant,
        issues=issues,
        recommendations=recommendations,
        severity=severity.value
    )

def check_test_documentation_compliance(daemon_path: Path) -> ComplianceResult:
    """Check test documentation compliance"""
    issues = []
    recommendations = []
    
    test_file = daemon_path / "test_daemon_rag_system.py"
    if not test_file.exists():
        issues.append("Test file not found")
        recommendations.append("Create comprehensive test suite")
    else:
        # Check test coverage
        content = test_file.read_text(encoding='utf-8')
        test_count = content.count("def test_")
        
        if test_count < 10:
            issues.append(f"Low test coverage (current: {test_count} tests)")
            recommendations.append("Expand test suite to cover all subsystems")
    
    compliant = len(issues) == 0
    severity = Severity.HIGH if not compliant else Severity.LOW
    
    return ComplianceResult(
        standard_name="Test Documentation",
        category="quality",
        compliant=compliant,
        issues=issues,
        recommendations=recommendations,
        severity=severity.value
    )

def check_ah_protocol_compliance(daemon_path: Path) -> ComplianceResult:
    """Check A-H Protocol compliance"""
    issues = []
    recommendations = []
    
    ah_path = daemon_path / "ah_protocol"
    if not ah_path.exists():
        issues.append("A-H Protocol directory not found")
        recommendations.append("Create A-H Protocol implementation")
    else:
        # Check for all 8 steps
        required_files = [
            "intent_capture.py",
            "hypothesis_formation.py",
            "context_mapping.py",
            "deep_expansion_layer.py",
            "context_mesh_maps.py",
            "confidence_gated_controls.py",
            "implementation.py",
            "audit_memory_continuity.py"
        ]
        
        missing_files = [f for f in required_files if not (ah_path / f).exists()]
        if missing_files:
            issues.append(f"Missing A-H Protocol files: {', '.join(missing_files)}")
            recommendations.append("Complete A-H Protocol implementation")
        
        # Check integration
        main_file = daemon_path / "daemon_rag_system.py"
        if main_file.exists():
            content = main_file.read_text(encoding='utf-8')
            if "ah_protocol" not in content.lower():
                issues.append("A-H Protocol not integrated into main system")
                recommendations.append("Integrate A-H Protocol workflow into daemon")
    
    compliant = len(issues) == 0
    severity = Severity.CRITICAL if not compliant else Severity.LOW
    
    return ComplianceResult(
        standard_name="A-H Protocol",
        category="architecture",
        compliant=compliant,
        issues=issues,
        recommendations=recommendations,
        severity=severity.value
    )

def check_system_maps_compliance(daemon_path: Path) -> ComplianceResult:
    """Check System Maps compliance"""
    issues = []
    recommendations = []
    
    project_root = daemon_path.parent
    ka_path = project_root / "knowledge_architecture"
    
    # Check for Atlas system maps
    atlas_files = [
        "ATLAS_MERMAID_EPIC.md",
        "ATLAS_MERMAID_COMPLETE_BRANCHED.md",
        "ATLAS_MERMAID_ULTRA_COMPLEX.md",
        "atlas.index.lucid.json5"
    ]
    
    missing_atlas = []
    for atlas_file in atlas_files:
        atlas_path = ka_path / atlas_file
        if not atlas_path.exists():
            missing_atlas.append(atlas_file)
    
    if missing_atlas:
        issues.append(f"Missing Atlas system map files: {', '.join(missing_atlas)}")
        recommendations.append("Create complete Atlas system maps")
    
    # Check daemon-specific system map
    daemon_doc_path = ka_path / "systems" / "daemon_rag_system"
    daemon_map_exists = (daemon_doc_path / "system.map.lucid.json5").exists() or \
                       (daemon_doc_path / "SYSTEM_MAP.md").exists()
    
    if not daemon_map_exists:
        issues.append("Daemon system map not found")
        recommendations.append("Create daemon system map (system.map.lucid.json5 or SYSTEM_MAP.md)")
    
    compliant = len(issues) == 0
    severity = Severity.MEDIUM if not compliant else Severity.LOW
    
    return ComplianceResult(
        standard_name="System Maps",
        category="foundational",
        compliant=compliant,
        issues=issues,
        recommendations=recommendations,
        severity=severity.value
    )

def check_system_indexes_compliance(daemon_path: Path) -> ComplianceResult:
    """Check System Indexes compliance"""
    issues = []
    recommendations = []
    
    project_root = daemon_path.parent
    ka_path = project_root / "knowledge_architecture"
    
    # Check for Hierarchical Navigation Index
    hierarchical_index = ka_path / "HIERARCHICAL_NAVIGATION_INDEX.md"
    if not hierarchical_index.exists():
        issues.append("Hierarchical Navigation Index not found")
        recommendations.append("Create HIERARCHICAL_NAVIGATION_INDEX.md")
    else:
        # Check if daemon is included in index
        try:
            content = hierarchical_index.read_text(encoding='utf-8')
            if "daemon" not in content.lower() and "daemon_rag_system" not in content.lower():
                issues.append("Daemon system not referenced in Hierarchical Navigation Index")
                recommendations.append("Add daemon system to HIERARCHICAL_NAVIGATION_INDEX.md")
        except Exception as e:
            issues.append(f"Could not read Hierarchical Navigation Index: {e}")
    
    # Check for SUPER_INDEX
    super_index = ka_path / "SUPER_INDEX.md"
    if not super_index.exists():
        issues.append("SUPER_INDEX.md not found")
        recommendations.append("Create SUPER_INDEX.md")
    else:
        # Check if daemon is included
        try:
            content = super_index.read_text(encoding='utf-8')
            if "daemon" not in content.lower() and "daemon_rag_system" not in content.lower():
                issues.append("Daemon system not referenced in SUPER_INDEX")
                recommendations.append("Add daemon system to SUPER_INDEX.md")
        except Exception as e:
            issues.append(f"Could not read SUPER_INDEX: {e}")
    
    compliant = len(issues) == 0
    severity = Severity.MEDIUM if not compliant else Severity.LOW
    
    return ComplianceResult(
        standard_name="System Indexes",
        category="foundational",
        compliant=compliant,
        issues=issues,
        recommendations=recommendations,
        severity=severity.value
    )

def check_validation_framework_compliance(daemon_path: Path) -> ComplianceResult:
    """Check Validation Framework compliance"""
    issues = []
    recommendations = []
    
    project_root = daemon_path.parent
    ka_path = project_root / "knowledge_architecture"
    
    # Check for Validation Framework standard
    validation_framework = ka_path / "PERFECT_VALIDATION_FRAMEWORK.md"
    if not validation_framework.exists():
        issues.append("Validation Framework standard not found")
        recommendations.append("Create PERFECT_VALIDATION_FRAMEWORK.md")
    
    # Check for validation directory
    validation_dir = ka_path / "validation"
    if not validation_dir.exists():
        issues.append("Validation directory not found")
        recommendations.append("Create knowledge_architecture/validation/ directory")
    
    # Check for daemon-specific validation
    daemon_doc_path = ka_path / "systems" / "daemon_rag_system"
    daemon_validation = validation_dir / "daemon_rag_system.validation.md" if validation_dir.exists() else None
    
    if daemon_validation and not daemon_validation.exists():
        issues.append("Daemon validation checklist not found")
        recommendations.append("Create daemon_rag_system.validation.md")
    
    # Check if audit script uses validation framework
    audit_script = daemon_path / "audit_standards_compliance.py"
    if audit_script.exists():
        try:
            content = audit_script.read_text(encoding='utf-8')
            # Check if script references validation framework concepts
            has_validation_concepts = any(keyword in content.lower() for keyword in [
                "validation", "validate", "compliant", "compliance"
            ])
            if not has_validation_concepts:
                issues.append("Audit script does not reference validation framework")
                recommendations.append("Integrate validation framework into audit script")
        except Exception as e:
            issues.append(f"Could not read audit script: {e}")
    
    compliant = len(issues) == 0
    severity = Severity.MEDIUM if not compliant else Severity.LOW
    
    return ComplianceResult(
        standard_name="Validation Framework",
        category="foundational",
        compliant=compliant,
        issues=issues,
        recommendations=recommendations,
        severity=severity.value
    )

def check_templates_library_compliance(daemon_path: Path) -> ComplianceResult:
    """Check Templates Library compliance"""
    issues = []
    recommendations = []
    
    project_root = daemon_path.parent
    ka_path = project_root / "knowledge_architecture"
    
    # Check for Templates Library standard
    templates_library = ka_path / "PERFECT_TEMPLATES_LIBRARY.md"
    if not templates_library.exists():
        issues.append("Templates Library standard not found")
        recommendations.append("Create PERFECT_TEMPLATES_LIBRARY.md")
    
    # Check for templates directory
    templates_dir = ka_path / "templates" or ka_path / "timeline_templates"
    templates_found = False
    
    if (ka_path / "templates").exists():
        templates_found = True
        templates_dir = ka_path / "templates"
    elif (ka_path / "timeline_templates").exists():
        templates_found = True
        templates_dir = ka_path / "timeline_templates"
    
    if not templates_found:
        issues.append("Templates directory not found")
        recommendations.append("Create knowledge_architecture/templates/ directory")
    
    # Check for daemon-specific templates
    if templates_found:
        daemon_templates = list(templates_dir.glob("*daemon*")) + list(templates_dir.glob("*rag*"))
        if not daemon_templates:
            issues.append("Daemon-specific templates not found")
            recommendations.append("Create daemon templates in templates directory")
    
    compliant = len(issues) == 0
    severity = Severity.MEDIUM if not compliant else Severity.LOW
    
    return ComplianceResult(
        standard_name="Templates Library",
        category="foundational",
        compliant=compliant,
        issues=issues,
        recommendations=recommendations,
        severity=severity.value
    )

def check_standards_compliance(daemon_path: Path) -> List[ComplianceResult]:
    """Run all compliance checks"""
    results = []
    
    # Key checks
    results.append(check_l0_l6_compliance(daemon_path))
    results.append(check_metadata_compliance(daemon_path))
    results.append(check_test_documentation_compliance(daemon_path))
    results.append(check_ah_protocol_compliance(daemon_path))
    
    # Foundational standards (Phase 1)
    results.append(check_system_maps_compliance(daemon_path))
    results.append(check_system_indexes_compliance(daemon_path))
    results.append(check_validation_framework_compliance(daemon_path))
    results.append(check_templates_library_compliance(daemon_path))
    
    # TODO: Add checks for remaining standards
    # For now, mark others as "not checked"
    for phase_name, standards in STANDARDS.items():
        for standard_name, category in standards:
            if not any(r.standard_name == standard_name for r in results):
                results.append(ComplianceResult(
                    standard_name=standard_name,
                    category=category,
                    compliant=False,
                    issues=["Not yet audited"],
                    recommendations=["Run compliance audit"],
                    severity="medium"
                ))
    
    return results

def generate_compliance_report(results: List[ComplianceResult]) -> str:
    """Generate compliance report"""
    report = []
    report.append("=" * 70)
    report.append("DAEMON/RAG SYSTEM - STANDARDS COMPLIANCE AUDIT REPORT")
    report.append("=" * 70)
    report.append("")
    
    # Summary
    total = len(results)
    compliant = sum(1 for r in results if r.compliant)
    non_compliant = total - compliant
    
    report.append(f"**Summary:**")
    report.append(f"- Total Standards: {total}")
    report.append(f"- Compliant: {compliant} ({compliant/total*100:.1f}%)")
    report.append(f"- Non-Compliant: {non_compliant} ({non_compliant/total*100:.1f}%)")
    report.append("")
    
    # By severity
    critical = [r for r in results if r.severity == "critical" and not r.compliant]
    high = [r for r in results if r.severity == "high" and not r.compliant]
    medium = [r for r in results if r.severity == "medium" and not r.compliant]
    low = [r for r in results if r.severity == "low" and not r.compliant]
    
    report.append(f"**By Severity:**")
    report.append(f"- Critical Issues: {len(critical)}")
    report.append(f"- High Issues: {len(high)}")
    report.append(f"- Medium Issues: {len(medium)}")
    report.append(f"- Low Issues: {len(low)}")
    report.append("")
    
    # Detailed results
    report.append("=" * 70)
    report.append("DETAILED COMPLIANCE RESULTS")
    report.append("=" * 70)
    report.append("")
    
    for result in results:
        status = "✅ COMPLIANT" if result.compliant else "❌ NON-COMPLIANT"
        report.append(f"**{result.standard_name}** ({result.category}) - {status}")
        report.append(f"Severity: {result.severity.upper()}")
        
        if result.issues:
            report.append(f"Issues:")
            for issue in result.issues:
                report.append(f"  - {issue}")
        
        if result.recommendations:
            report.append(f"Recommendations:")
            for rec in result.recommendations:
                report.append(f"  - {rec}")
        
        report.append("")
    
    return "\n".join(report)

def main():
    """Main function"""
    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    daemon_path = Path(__file__).parent.parent / "daemon_rag_system"
    
    if not daemon_path.exists():
        print(f"Error: Daemon path not found: {daemon_path}")
        return 1
    
    print("Running standards compliance audit...")
    results = check_standards_compliance(daemon_path)
    
    report = generate_compliance_report(results)
    print(report)
    
    # Save report
    report_path = daemon_path / "STANDARDS_COMPLIANCE_AUDIT.md"
    report_path.write_text(report, encoding='utf-8')
    print(f"\nReport saved to: {report_path}")
    
    # Return exit code based on critical issues
    critical_issues = [r for r in results if r.severity == "critical" and not r.compliant]
    return 1 if critical_issues else 0

if __name__ == "__main__":
    sys.exit(main())

