#!/usr/bin/env python3
"""
NL Tag Coverage Auditor

Audits NL tag coverage across all core AIM-OS systems.
Reports on coverage percentages, tag types found, and gaps.

Usage:
    python scripts/audit_nl_tag_coverage.py --all
    python scripts/audit_nl_tag_coverage.py --system cmc
    python scripts/audit_nl_tag_coverage.py --report
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from packages.nl_tags import NLTagParser, NLTagRegistry
except ImportError:
    print("ERROR: packages.nl_tags not found. Ensure nl_tags package is installed.")
    sys.exit(1)

@dataclass
class TagCoverageResult:
    """Tag coverage result for a system"""
    system_name: str
    total_files: int
    total_functions: int  # Estimated from code
    total_tags: int
    tag_types: Dict[str, int]  # Count by tag type
    coverage_percentage: float
    files_with_tags: int
    files_without_tags: int
    sample_tags: List[str]  # Sample of found tags

class NLTagCoverageAuditor:
    """Audits NL tag coverage across core systems"""
    
    CORE_SYSTEMS = [
        'cmc_service',
        'hhni',
        'vif',
        'sdfcvf',
        'apoe',
        # Note: CAS, TCS, IIS may not have packages yet
    ]
    
    def __init__(self):
        self.parser = NLTagParser()
        self.packages_dir = project_root / "packages"
        
    def audit_system(self, system_name: str) -> TagCoverageResult:
        """Audit single system"""
        print(f"Auditing {system_name}...")
        
        system_path = self.packages_dir / system_name
        if not system_path.exists():
            print(f"  WARNING: {system_path} not found")
            return TagCoverageResult(
                system_name=system_name,
                total_files=0,
                total_functions=0,
                total_tags=0,
                tag_types={},
                coverage_percentage=0.0,
                files_with_tags=0,
                files_without_tags=0,
                sample_tags=[]
            )
        
        # Find all Python files
        py_files = list(system_path.glob("**/*.py"))
        py_files = [f for f in py_files if "__pycache__" not in str(f)]
        
        total_tags = 0
        tag_types = {}
        files_with_tags = 0
        files_without_tags = 0
        all_tags = []
        
        # Parse each file
        for py_file in py_files:
            try:
                tags = self.parser.parse_file(str(py_file))
                
                if tags:
                    files_with_tags += 1
                    for tag in tags:
                        total_tags += 1
                        all_tags.append(tag.tag_text)
                        
                        # Identify tag type
                        tag_type = self._identify_tag_type(tag.tag_text)
                        tag_types[tag_type] = tag_types.get(tag_type, 0) + 1
                else:
                    files_without_tags += 1
                    
            except Exception as e:
                print(f"    Error parsing {py_file.name}: {e}")
                files_without_tags += 1
        
        # Estimate total functions (rough count from "def " occurrences)
        total_functions = self._estimate_function_count(py_files)
        
        # Calculate coverage
        coverage_percentage = (total_tags / total_functions * 100) if total_functions > 0 else 0.0
        
        # Sample tags (first 5)
        sample_tags = all_tags[:5]
        
        result = TagCoverageResult(
            system_name=system_name,
            total_files=len(py_files),
            total_functions=total_functions,
            total_tags=total_tags,
            tag_types=tag_types,
            coverage_percentage=coverage_percentage,
            files_with_tags=files_with_tags,
            files_without_tags=files_without_tags,
            sample_tags=sample_tags
        )
        
        return result
    
    def _identify_tag_type(self, tag_text: str) -> str:
        """Identify tag type from text"""
        if "NL_TAG_CONNECT:" in tag_text or "CONNECT:" in tag_text:
            return "CONNECT"
        elif "NL_TAG_INTENT:" in tag_text or "INTENT:" in tag_text:
            return "INTENT"
        elif "NL_TAG_SPEC:" in tag_text or "SPEC:" in tag_text:
            return "SPEC"
        elif "NL_TAG:" in tag_text:
            return "STRUCTURED"
        else:
            return "SIMPLE"
    
    def _estimate_function_count(self, py_files: List[Path]) -> int:
        """Estimate total function count"""
        total_functions = 0
        
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                # Count "def " occurrences
                function_count = content.count("\ndef ") + content.count("\n    def ") + content.count("\n        def ")
                total_functions += function_count
            except Exception as e:
                continue
        
        return total_functions
    
    def audit_all_systems(self) -> List[TagCoverageResult]:
        """Audit all core systems"""
        results = []
        
        for system in self.CORE_SYSTEMS:
            result = self.audit_system(system)
            results.append(result)
        
        return results

def print_coverage_result(result: TagCoverageResult):
    """Print coverage result"""
    print("\n" + "="*80)
    print(f"System: {result.system_name}")
    print("="*80)
    print(f"Total Files: {result.total_files}")
    print(f"Total Functions (estimated): {result.total_functions}")
    print(f"Total Tags: {result.total_tags}")
    print(f"Coverage: {result.coverage_percentage:.1f}%")
    print(f"Files with Tags: {result.files_with_tags}")
    print(f"Files without Tags: {result.files_without_tags}")
    print()
    
    if result.tag_types:
        print("Tag Types Found:")
        for tag_type, count in sorted(result.tag_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tag_type}: {count}")
        print()
    
    if result.sample_tags:
        print("Sample Tags:")
        for tag in result.sample_tags:
            # Truncate long tags
            tag_preview = tag[:80] + "..." if len(tag) > 80 else tag
            print(f"  - {tag_preview}")
    
    print("="*80)

def generate_report(results: List[TagCoverageResult]):
    """Generate comprehensive audit report"""
    report_path = project_root / "knowledge_architecture" / "validation" / "NL_TAG_COVERAGE_AUDIT_REPORT.md"
    
    # Calculate totals
    total_files = sum(r.total_files for r in results)
    total_functions = sum(r.total_functions for r in results)
    total_tags = sum(r.total_tags for r in results)
    overall_coverage = (total_tags / total_functions * 100) if total_functions > 0 else 0.0
    
    # Generate report
    report = f"""# NL Tag Coverage Audit Report

**Date:** 2025-11-03  
**Systems Audited:** {len(results)}  
**Status:** {'✅ GOOD COVERAGE' if overall_coverage >= 50 else '⚠️ LOW COVERAGE'}

---

## Summary

**Overall Coverage:** {total_tags} tags / {total_functions} functions = {overall_coverage:.1f}%

**Total Files:** {total_files}  
**Total Functions:** {total_functions}  
**Total Tags:** {total_tags}

---

## System-by-System Results

"""
    
    for result in results:
        status_emoji = "✅" if result.coverage_percentage >= 50 else "⚠️"
        report += f"\n### {status_emoji} {result.system_name}\n\n"
        report += f"**Coverage:** {result.coverage_percentage:.1f}% ({result.total_tags} / {result.total_functions})\n"
        report += f"**Files:** {result.total_files} total, {result.files_with_tags} with tags, {result.files_without_tags} without\n\n"
        
        if result.tag_types:
            report += "**Tag Types:**\n"
            for tag_type, count in sorted(result.tag_types.items(), key=lambda x: x[1], reverse=True):
                report += f"- {tag_type}: {count}\n"
            report += "\n"
    
    report += "\n---\n\n**Next Steps:** Implement SDF-CVF quintet parity to enforce tag coverage and alignment.\n"
    
    # Write report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    
    print(f"\nAudit report generated: {report_path}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Audit NL tag coverage across core systems")
    parser.add_argument("--system", help="System name to audit")
    parser.add_argument("--all", action="store_true", help="Audit all core systems")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive report")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    
    args = parser.parse_args()
    
    auditor = NLTagCoverageAuditor()
    
    if args.system:
        result = auditor.audit_system(args.system)
        if args.json:
            print(json.dumps(asdict(result), indent=2))
        else:
            print_coverage_result(result)
    elif args.all or args.report:
        results = auditor.audit_all_systems()
        
        if args.json:
            print(json.dumps([asdict(r) for r in results], indent=2))
        elif args.report:
            for result in results:
                print_coverage_result(result)
            generate_report(results)
        else:
            for result in results:
                print_coverage_result(result)
    else:
        print("ERROR: Must specify --system, --all, or --report")
        sys.exit(1)

if __name__ == "__main__":
    main()

