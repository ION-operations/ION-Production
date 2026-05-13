#!/usr/bin/env python3
"""
Build SEV reports monolith with navigable index for AI consumption.
Output: REPORTS_MONOLITH_INDEX_YYYY-MM-DD.md
"""
import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

REPORTS_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = REPORTS_DIR / f"REPORTS_MONOLITH_INDEX_{datetime.now().strftime('%Y-%m-%d')}.md"

# Exclude the monolith itself and scripts
EXCLUDE = {"README.md", "scripts"}


def sanitize_anchor(name: str) -> str:
    """Create valid markdown anchor from filename."""
    base = Path(name).stem
    return re.sub(r"[^\w\-]", "_", base).lower()


def categorize(filename: str) -> str:
    """Assign file to logical category for index grouping."""
    name = filename.upper()
    if name.startswith("CONSOLIDATION_FINDINGS_BOARD"):
        return "Findings Boards"
    if name.startswith("AIMOS_PROJECT_SURFACE") or name.startswith("AIMOS_4_AXIS") or name.startswith("AIMOS_CONSOLIDATION_GAP"):
        return "Core Registers (WP01)"
    if name.startswith("AIMOS_CONTROL_SURFACE") or name.startswith("AIMOS_AGENT_CONTINUITY") or name.startswith("AIMOS_CANON_PRECEDENCE"):
        return "Control & Continuity (WP04)"
    if name.startswith("AIMOS_EXTERNAL_TRUTH") or name.startswith("AIMOS_OPERATOR_DEPENDENCY") or name.startswith("AIMOS_CONSOLIDATION_COMPLETION"):
        return "External & Completion Gates (WP05)"
    if name.startswith("AIMOS_CORE_SYSTEM_LIVE") or name.startswith("AIMOS_RUNTIME_DEGRADED") or name.startswith("AIMOS_VERIFICATION_METHOD"):
        return "Runtime Verification (WP03)"
    if name.startswith("AIMOS_STALE_CANON") or name.startswith("AIMOS_UI_HABITAT") or name.startswith("AIMOS_BRANCH_EXTERNAL"):
        return "Stale Canon & Overlap (WP02)"
    if name.startswith("AIMOS_JOC_CLUSTER"):
        return "JOC Cluster Comparative"
    if name.startswith("AIMOS_GENOME_"):
        return "Genome Surface Comparative"
    if name.startswith("AIMOS_ECHO_FORGE_CLUSTER"):
        return "Echo Forge Cluster"
    if name.startswith("AIMOS_HOST_ADAPTER_CLUSTER"):
        return "Host Adapter Cluster"
    if name.startswith("AIMOS_TRANSPORT_EXECUTION_CLUSTER"):
        return "Transport Execution Cluster"
    if name.startswith("AIMOS_CORE_RUNTIME_SPINE"):
        return "Core Runtime Spine"
    if "PROFILE_MATRIX" in name or "COMPARISON" in name or "BEST_AT_MAP" in name:
        # Extract family/cluster from name for grouping
        if "PROCEED" in name:
            return "Proceed/Recovery Family"
        if "RESTORE" in name:
            return "Restore Family"
        if "CONTROL" in name or "COMMS" in name or "DOCTRINE" in name:
            return "Control/Comms Surfaces"
        if "CONTINUITY" in name or "STATUS" in name or "RUNTIME_TRUTH" in name:
            return "Continuity & Status Surfaces"
        if "AUTHORITY" in name or "PRECEDENCE" in name or "FORCE_STRUCTURE" in name:
            return "Authority & Precedence"
        if "ACTIVATION" in name or "EXECUTION" in name or "DEPENDENCY" in name:
            return "Activation & Execution"
        if "CORROBORATION" in name or "OPERATIONAL_PROOF" in name:
            return "Corroboration & Proof"
        if "TEMPORAL" in name or "CURRENTNESS" in name:
            return "Temporal & Provenance"
        return "Other Comparative Surfaces"
    if name.startswith("COMPOSER_"):
        return "COMPOSER Reports"
    if name.startswith("FORGE_"):
        return "FORGE Reports"
    if name.startswith("OPUS_CAPSULE"):
        return "OPUS Candidate Register"
    if name.startswith("EXTERNAL_SURFACE") or name.startswith("WORK_PACKAGE_01_LOCAL"):
        return "Supporting Evidence"
    if name.startswith("RUNTIME_TRUTH_MAP"):
        return "Runtime Truth"
    if name.startswith("PALISADE") or name.startswith("RELAY") or name.startswith("WAVE01"):
        return "Legacy / Verification"
    return "Other"


def build_index(files_by_category: dict) -> str:
    """Build the navigable index section."""
    lines = [
        "# AIM-OS SEV Reports Monolith — Master Index",
        "",
        "> Single-file consolidation of `.agent/sev/reports/` for AI navigation.",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## How to Navigate",
        "",
        "- **Search**: Use Ctrl+F / Cmd+F to find terms across all reports.",
        "- **Jump**: Click any link below or search for `## FILE:` to reach a specific report.",
        "- **Categories**: Reports are grouped by consolidation work package and topic.",
        "",
        "---",
        "",
        "## Index by Category",
        "",
    ]

    for category in sorted(files_by_category.keys()):
        files = files_by_category[category]
        lines.append(f"### {category}")
        lines.append("")
        for fname in sorted(files):
            anchor = sanitize_anchor(fname)
            lines.append(f"- [{fname}](#file-{anchor})")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Full Content")
    lines.append("")
    return "\n".join(lines)


def main():
    files = []
    for f in REPORTS_DIR.iterdir():
        if f.is_file() and f.suffix == ".md" and f.name not in EXCLUDE:
            if not f.name.startswith("REPORTS_MONOLITH"):
                files.append(f.name)

    files_by_category = defaultdict(list)
    for f in sorted(files):
        files_by_category[categorize(f)].append(f)

    # Build output
    output_parts = [build_index(files_by_category)]

    for category in sorted(files_by_category.keys()):
        for fname in sorted(files_by_category[category]):
            path = REPORTS_DIR / fname
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                content = f"*[Error reading file: {e}]*"
            anchor = sanitize_anchor(fname)
            output_parts.append(f"\n\n---\n\n## FILE: {fname}\n\n<!-- anchor: #file-{anchor} -->\n\n{content}\n")

    full_content = "".join(output_parts)

    # Write
    OUTPUT_FILE.write_text(full_content, encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")
    print(f"  Files: {len(files)}")
    print(f"  Size: {len(full_content) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
