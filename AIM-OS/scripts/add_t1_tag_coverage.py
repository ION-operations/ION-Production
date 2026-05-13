#!/usr/bin/env python3
"""Add NL tag coverage sections to T1 overview documents."""

from pathlib import Path
import re

SYSTEM_DATA = {
    "cmc": (331, 0.88),
    "hhni": (246, 0.87),
    "apoe": (421, 0.88),
    "seg": (89, 0.86),
    "sdfcvf": (178, 0.91),
    "cognitive_analysis": (178, 0.87),
    "timeline_context_system": (267, 0.88),
    "intuitive_intelligence_system": (93, 0.86),
}

def create_tag_coverage_section(total_tags: int, parity: float) -> str:
    """Create tag coverage section."""
    parity_label = "excellent" if parity >= 0.90 else ("very good" if parity >= 0.85 else "good")
    return f"""
## NL Tag Coverage

- **Total NL Tags:** {total_tags} tags
- **Quintet Parity:** P = {parity:.2f} ({parity_label})
- **Semantic Search:** All functions tagged
- **Tag Catalog:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md)

---

"""

def update_t1_file(t1_path: Path, system_key: str):
    """Add tag coverage to T1 file."""
    content = t1_path.read_text(encoding='utf-8')
    
    if "NL Tag Coverage" in content:
        print(f"[SKIP] {system_key} T1 already has tag coverage")
        return False
    
    total_tags, parity = SYSTEM_DATA[system_key]
    section = create_tag_coverage_section(total_tags, parity)
    
    # Find "## References" or "## Documentation" section and insert before it
    pattern = r'(\n## (?:References|Documentation)\n)'
    if re.search(pattern, content):
        updated = re.sub(pattern, section + r'\1', content, count=1)
        t1_path.write_text(updated, encoding='utf-8')
        print(f"[OK] {system_key} T1 updated")
        return True
    
    print(f"[WARN] {system_key} T1 - no Documentation section found")
    return False

def main():
    """Update all T1 files."""
    root = Path("C:/Users/bombe/OneDrive/Desktop/AIM-OS")
    
    updated = 0
    for system in SYSTEM_DATA.keys():
        t1_path = root / "knowledge_architecture" / "systems" / system / "T1_overview.md"
        
        if not t1_path.exists():
            print(f"[SKIP] {system} T1 not found")
            continue
        
        if update_t1_file(t1_path, system):
            updated += 1
    
    print(f"\n[DONE] Updated {updated}/8 T1 files")

if __name__ == "__main__":
    main()

