#!/usr/bin/env python3
"""
Add implementation tag maps to T3 detailed documentation files.

This script systematically adds tag map sections to all T3 detailed docs
that are missing them, using catalog data for accuracy.
"""

from pathlib import Path
import re

# System tag metrics from catalogs
SYSTEM_TAG_METRICS = {
    "cmc": {"total": 331, "coverage_public": 89, "coverage_internal": 71, "parity": 0.88},
    "hhni": {"total": 246, "coverage_public": 86, "coverage_internal": 68, "parity": 0.87},
    "apoe": {"total": 421, "coverage_public": 90, "coverage_internal": 74, "parity": 0.88},
    "seg": {"total": 89, "coverage_public": 82, "coverage_internal": 65, "parity": 0.86},
    "sdfcvf": {"total": 178, "coverage_public": 88, "coverage_internal": 70, "parity": 0.91},
    "cognitive_analysis": {"total": 178, "coverage_public": 85, "coverage_internal": 68, "parity": 0.87},
    "timeline_context_system": {"total": 267, "coverage_public": 87, "coverage_internal": 69, "parity": 0.88},
    "intuitive_intelligence_system": {"total": 93, "coverage_public": 84, "coverage_internal": 67, "parity": 0.86},
}

# Tag categories for each system
SYSTEM_TAG_CATEGORIES = {
    "cmc": [
        "CMC-ATOM: Atom storage, retrieval, CRUD operations",
        "CMC-SNAPSHOT: Snapshot creation, restoration, time-travel",
        "CMC-BITEMPORAL: Temporal indexing, valid/transaction times",
        "CMC-COMPRESS: Compression strategies, optimization",
        "CMC-PIPELINE: Processing pipelines, transformations",
        "CMC-QUERY: Query operations, retrieval patterns"
    ],
    "hhni": [
        "HHNI-INDEX: Hierarchical indexing, DVNS physics",
        "HHNI-EMBED: Semantic embeddings, similarity",
        "HHNI-RETRIEVAL: Context assembly, ranking",
        "HHNI-PHYSICS: DVNS physics simulation",
        "HHNI-BUDGET: Cost tracking, optimization"
    ],
    "apoe": [
        "APOE-PLAN: Plan creation, orchestration",
        "APOE-GATE: Execution gates, confidence routing",
        "APOE-EXEC: Task processing, parallelization",
        "APOE-ACL: Access control, security",
        "APOE-BUDGET: Cost pooling, optimization"
    ],
    "seg": [
        "SEG-GRAPH: Graph construction, knowledge synthesis",
        "SEG-WITNESS: Provenance tracking, lineage",
        "SEG-QUERY: Knowledge retrieval, traversal"
    ],
    "sdfcvf": [
        "SDFCVF-QUARTET: Quartet parity enforcement",
        "SDFCVF-QUINTET: Quintet parity with NL tags",
        "SDFCVF-GATE: Quality gates, enforcement",
        "SDFCVF-BLAST: Blast radius calculation"
    ],
    "cognitive_analysis": [
        "CAS-DRIFT: Drift detection, cognitive monitoring",
        "CAS-ATTENTION: Attention tracking, focus analysis",
        "CAS-CATEGORY: Categorization accuracy",
        "CAS-FAILURE: Failure mode detection"
    ],
    "timeline_context_system": [
        "TCS-TIMELINE: Timeline entry tracking",
        "TCS-GOAL: Goal timeline management",
        "TCS-JOURNAL: Consciousness journaling",
        "TCS-DUMP: Context dumping, preservation",
        "TCS-DUAL: Dual-prompt architecture"
    ],
    "intuitive_intelligence_system": [
        "IIS-INTUITION: Intuition computation",
        "IIS-EMOTIONAL: Emotional salience",
        "IIS-META: Meta-intuition tracking",
        "IIS-CCS: CCS integration"
    ]
}

def create_tag_map_section(system_key: str) -> str:
    """Create implementation tag map section for a system."""
    metrics = SYSTEM_TAG_METRICS[system_key]
    categories = SYSTEM_TAG_CATEGORIES[system_key]
    
    section = f"""---

## 📋 Implementation Tag Map

All referenced code is tagged for semantic search and quintet parity validation.

**Tag Categories:**
"""
    
    for category in categories:
        section += f"- **{category}**\n"
    
    section += f"""
**Complete index:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md) ({metrics['total']} tags)

**Tag Navigation:**
- Use tag IDs to locate exact code locations
- CONNECT tags show cross-system integration points
- INTENT tags explain design rationale
- SPEC tags document validation rules

---
"""
    
    return section

def update_t3_file(t3_path: Path, system_key: str):
    """Add tag map section to T3 file if missing."""
    content = t3_path.read_text(encoding='utf-8')
    
    # Check if already has tag map
    if "Implementation Tag Map" in content:
        print(f"[SKIP] {system_key} T3 already has tag map")
        return False
    
    # Find insertion point (after Prerequisites or Audience section)
    tag_map = create_tag_map_section(system_key)
    
    # Try multiple insertion patterns
    patterns = [
        (r'(## Prerequisites\n\n.*?\n\n)', r'\1' + tag_map),
        (r'(## Audience\n\n.*?\n\n)', r'\1' + tag_map),
        (r'(## Purpose\n\n.*?\n\n)', r'\1' + tag_map),
    ]
    
    for pattern, replacement in patterns:
        if re.search(pattern, content, re.DOTALL):
            updated_content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
            t3_path.write_text(updated_content, encoding='utf-8')
            print(f"[OK] {system_key} T3 updated with tag map", flush=True)
            return True
    
    print(f"[WARN] {system_key} T3 - couldn't find insertion point", flush=True)
    return False

def main():
    """Update all T3 files with tag maps."""
    root = Path("C:/Users/bombe/OneDrive/Desktop/AIM-OS")
    
    systems = ["cmc", "hhni", "apoe", "seg", "sdfcvf", 
               "cognitive_analysis", "timeline_context_system", 
               "intuitive_intelligence_system"]
    
    updated = 0
    for system in systems:
        t3_path = root / "knowledge_architecture" / "systems" / system / "T3_detailed.md"
        
        if not t3_path.exists():
            print(f"[SKIP] {system} T3 not found")
            continue
        
        if update_t3_file(t3_path, system):
            updated += 1
    
    print(f"\n[DONE] Updated {updated}/{len(systems)} T3 files")

if __name__ == "__main__":
    main()

