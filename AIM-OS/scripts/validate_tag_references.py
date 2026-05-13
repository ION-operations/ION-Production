#!/usr/bin/env python3
"""
Validate Tag References in Documentation

Scans all documentation files for tag references (e.g., `VIF-WITNESS-001`)
and validates they exist in the universal tag registry.

Usage:
    python scripts/validate_tag_references.py knowledge_architecture/
    python scripts/validate_tag_references.py knowledge_architecture/systems/vif/
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from packages.nl_tags.universal_registry import UniversalTagRegistry


def find_tag_references(file_path: str) -> List[Tuple[int, str]]:
    """Find all tag references in a file
    
    Returns list of (line_number, tag_id) tuples
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        references = []
        
        # Pattern: `TAG-ID` or [TAG-ID] or (TAG-ID) or just TAG-ID in backticks
        # Format: SYSTEM-CATEGORY-NNN or SYSTEM-CATEGORYNAME-NNN
        pattern = r'`?([A-Z]+(?:CVF)?-[A-Z]+-\d+)`?'
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            matches = re.findall(pattern, line)
            for tag_id in matches:
                references.append((i, tag_id))
        
        return references
    
    except Exception as e:
        return []


def validate_references(
    doc_path: str,
    references: List[Tuple[int, str]],
    registry: UniversalTagRegistry
) -> List[Tuple[int, str, str]]:
    """Validate tag references exist
    
    Returns list of (line_number, tag_id, error_message) for broken refs
    """
    broken = []
    
    for line_num, tag_id in references:
        tag_data = registry.get(tag_id)
        
        if not tag_data:
            # Tag doesn't exist in registry
            # Could be ADR reference or schema file (allowed)
            if tag_id.startswith("ADR-") or tag_id.endswith("-TBD"):
                continue  # ADRs and TBD placeholders are OK
            
            broken.append((line_num, tag_id, "Tag not found in registry"))
    
    return broken


def scan_directory(dir_path: str, registry: UniversalTagRegistry) -> Dict[str, List]:
    """Scan directory for markdown files and validate tag references"""
    results = {}
    
    dir_path_obj = Path(dir_path)
    
    # Find all markdown files
    md_files = list(dir_path_obj.glob("**/*.md"))
    
    print(f"Scanning {len(md_files)} markdown files in {dir_path}...")
    print("")
    
    for md_file in md_files:
        # Skip READMEs (they reference many systems)
        # Skip catalogs (they list all tags)
        if md_file.name == "README.md" or "CATALOG" in md_file.name:
            continue
        
        references = find_tag_references(str(md_file))
        
        if references:
            broken = validate_references(str(md_file), references, registry)
            
            if broken:
                results[str(md_file)] = broken
    
    return results


def generate_report(broken_refs: Dict[str, List]) -> str:
    """Generate validation report"""
    if not broken_refs:
        return "All tag references validated successfully! No broken references found."
    
    report = []
    report.append("Tag Reference Validation Report")
    report.append("=" * 60)
    report.append("")
    report.append(f"Found broken tag references in {len(broken_refs)} files:")
    report.append("")
    
    for file_path, broken in sorted(broken_refs.items()):
        report.append(f"File: {file_path}")
        report.append(f"  Broken references: {len(broken)}")
        
        for line_num, tag_id, error in broken:
            report.append(f"    Line {line_num}: {tag_id} - {error}")
        
        report.append("")
    
    report.append("=" * 60)
    report.append(f"Total files with issues: {len(broken_refs)}")
    report.append(f"Total broken references: {sum(len(refs) for refs in broken_refs.values())}")
    report.append("")
    report.append("Fix by:")
    report.append("1. Verify tag exists in tag catalogs")
    report.append("2. Update documentation with correct tag ID")
    report.append("3. Or add tag to code if missing")
    
    return "\n".join(report)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Validate tag references in documentation")
    parser.add_argument("directory", help="Directory to scan (e.g., knowledge_architecture/)")
    parser.add_argument("-o", "--output", help="Output report file")
    
    args = parser.parse_args()
    
    print("Validating tag references...")
    print("")
    
    # Build universal registry (scan all tagged files)
    print("Loading universal tag registry...")
    registry = UniversalTagRegistry()
    
    # Scan all systems
    for system_dir in ["vif", "cmc_service", "apoe", "hhni", "seg", "sdfcvf", 
                       "timeline_context_system", "cas", "intuitive_intelligence_system"]:
        system_path = f"packages/{system_dir}/"
        if Path(system_path).exists():
            count = registry.scan_codebase(system_path, pattern="*_TAGGED.py")
            if count > 0:
                print(f"  Loaded {count} tags from {system_dir}")
    
    print(f"")
    print(f"Total tags in registry: {registry.count()}")
    print("")
    
    # Scan documentation
    broken_refs = scan_directory(args.directory, registry)
    
    # Generate report
    report = generate_report(broken_refs)
    
    # Print report
    print("")
    print(report)
    
    # Save report if output specified
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"")
        print(f"[OK] Report saved to: {args.output}")


if __name__ == "__main__":
    main()

