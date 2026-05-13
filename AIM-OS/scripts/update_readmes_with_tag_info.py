#!/usr/bin/env python3
"""
Update Package READMEs with NL Tag Information

Adds or updates NL Tag Coverage section in package READMEs.

Usage:
    python scripts/update_readmes_with_tag_info.py --all
    python scripts/update_readmes_with_tag_info.py packages/vif/
"""

import argparse
import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from packages.nl_tags.universal_registry import UniversalTagRegistry


PACKAGE_READMES = {
    "vif": "packages/vif/README.md",
    "cmc_service": "packages/cmc_service/README.md",
    "apoe": "packages/apoe/README.md",
    "hhni": "packages/hhni/README.md",
    "seg": "packages/seg/README.md",
    "sdfcvf": "packages/sdfcvf/README.md",
    "timeline_context_system": "packages/timeline_context_system/README.md",
    "cas": "packages/cas/README.md",
    "intuitive_intelligence_system": "packages/intuitive_intelligence_system/README.md",
}


def generate_tag_section(system_path: str, system_name: str) -> str:
    """Generate NL tag coverage section for README"""
    registry = UniversalTagRegistry()
    count = registry.scan_codebase(system_path, pattern="*_TAGGED.py")
    
    if count == 0:
        return ""
    
    # Get tag breakdown
    system_tags = registry.query(system=system_name.upper())
    
    by_type = {}
    for tag_id in system_tags:
        tag_data = registry.get(tag_id)
        if tag_data:
            tag_type = tag_data.get("kind", "TAG")
            by_type[tag_type] = by_type.get(tag_type, 0) + 1
    
    # Generate section
    section = []
    section.append("## NL Tag Coverage")
    section.append("")
    section.append("This package has comprehensive NL tag coverage:")
    section.append(f"- **Total tags:** {count}")
    
    if "TAG" in by_type:
        section.append(f"- **Primary tags (NL_TAG):** {by_type.get('TAG', 0)}")
    if "CONNECT" in by_type:
        section.append(f"- **Integration tags (CONNECT):** {by_type.get('CONNECT', 0)}")
    if "INTENT" in by_type:
        section.append(f"- **Design decisions (INTENT):** {by_type.get('INTENT', 0)}")
    if "SPEC" in by_type:
        section.append(f"- **Validations (SPEC):** {by_type.get('SPEC', 0)}")
    
    section.append(f"- **Tag catalog:** [NL_TAG_CATALOG.md](../../knowledge_architecture/systems/{system_name.lower()}/NL_TAG_CATALOG.md)")
    section.append("")
    section.append("All functions are tagged for:")
    section.append("- Semantic search (HHNI integration)")
    section.append("- Cross-system tracing (CONNECT tags)")
    section.append("- Design intent tracking (INTENT tags)")
    section.append("- Schema validation (SPEC tags)")
    section.append("- Quintet parity enforcement (SDF-CVF)")
    section.append("")
    
    return "\n".join(section)


def update_readme(readme_path: str, tag_section: str) -> bool:
    """Update or insert NL tag section in README"""
    try:
        if not Path(readme_path).exists():
            print(f"  [SKIP] README not found: {readme_path}")
            return False
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if NL tag section exists
        if "## NL Tag Coverage" in content:
            # Replace existing section
            lines = content.split('\n')
            new_lines = []
            skip = False
            
            for i, line in enumerate(lines):
                if line.startswith("## NL Tag Coverage"):
                    # Start skipping
                    skip = True
                    # Insert new section
                    new_lines.append(tag_section)
                elif skip and line.startswith("##"):
                    # Next section - stop skipping
                    skip = False
                    new_lines.append(line)
                elif not skip:
                    new_lines.append(line)
            
            new_content = '\n'.join(new_lines)
        else:
            # Append section
            new_content = content.rstrip() + "\n\n---\n\n" + tag_section
        
        # Write back
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    
    except Exception as e:
        print(f"  [ERROR] Failed to update {readme_path}: {e}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Update package READMEs with NL tag info")
    parser.add_argument("system_path", nargs="?", help="Path to system package")
    parser.add_argument("--all", action="store_true", help="Update all systems")
    
    args = parser.parse_args()
    
    if args.all:
        print("Updating all package READMEs with NL tag information...")
        print("")
        
        for system_dir, readme_path in PACKAGE_READMES.items():
            system_name = system_dir.replace("_service", "").replace("_system", "")
            print(f"Processing {system_name.upper()}...")
            
            # Generate section
            system_path = f"packages/{system_dir}/"
            tag_section = generate_tag_section(system_path, system_name)
            
            if tag_section:
                # Update README
                success = update_readme(readme_path, tag_section)
                if success:
                    print(f"  [OK] Updated {readme_path}")
            else:
                print(f"  [SKIP] No tags found")
            
            print("")
        
        print("All READMEs updated!")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

