"""ION README branch context helpers.

This module is intentionally small and side-effect free. It validates the local
shape of a branch context node without granting authority or mutating state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover - degraded environment
    yaml = None  # type: ignore[assignment]


BRANCH_NODE_SCHEMA_ID = "ion.branch_context_node.v0_1"
READY_VERDICT = "ION_BRANCH_CONTEXT_READY"
DEGRADED_VERDICT = "ION_BRANCH_CONTEXT_DEGRADED"
BLOCKED_VERDICT = "ION_BRANCH_CONTEXT_BLOCKED"

MATURITY_ORDER = [
    "B0_inert_folder",
    "B1_readme_entry",
    "B2_capsule_node",
    "B3_routed_branch",
    "B4_agentic_branch",
    "B5_evented_graph_branch",
    "B6_automation_ready_branch",
]

RESERVED_TAG_NAMESPACES = {
    "branch",
    "node",
    "route",
    "phase",
    "state",
    "authority",
    "proof",
    "artifact",
    "ui",
}


@dataclass
class BranchContextFinding:
    code: str
    severity: str
    message: str


@dataclass
class BranchContextReport:
    path: str
    maturity_level: str
    verdict: str
    ok: bool
    findings: list[BranchContextFinding] = field(default_factory=list)
    read_order: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    authority: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "maturity_level": self.maturity_level,
            "verdict": self.verdict,
            "ok": self.ok,
            "findings": [finding.__dict__ for finding in self.findings],
            "read_order": self.read_order,
            "tags": self.tags,
            "authority": self.authority,
        }


def normalize_ion_tag(tag: str) -> str:
    """Normalize one display tag into the conservative ION tag shape.

    Tags are navigation hints only. They never grant approval, receipt status,
    accepted state, production authority, or live execution authority.
    """

    text = str(tag).strip().lower().replace(" ", "-")
    text = "".join(ch for ch in text if ch.isalnum() or ch in {":", "_", "-"})
    if not text:
        return "state:untagged"
    if ":" in text:
        namespace, value = text.split(":", 1)
        namespace = namespace or "state"
        value = value or "untagged"
        return f"{namespace[:40]}:{value[:80]}"
    return text[:80]


def normalize_ion_tags(tags: list[str] | tuple[str, ...] | None) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for tag in tags or []:
        value = normalize_ion_tag(tag)
        if value not in seen:
            seen.add(value)
            normalized.append(value)
    return normalized


def _finding(code: str, severity: str, message: str) -> BranchContextFinding:
    return BranchContextFinding(code=code, severity=severity, message=message)


def _load_capsule(capsule_path: Path) -> tuple[dict[str, Any] | None, BranchContextFinding | None]:
    if yaml is None:
        return None, _finding(
            "yaml_unavailable",
            "blocker",
            "PyYAML is unavailable; cannot parse ION_CONTEXT_CAPSULE.yaml.",
        )
    try:
        data = yaml.safe_load(capsule_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exact parser error varies
        return None, _finding("capsule_parse_failed", "blocker", str(exc))
    if not isinstance(data, dict):
        return None, _finding("capsule_not_mapping", "blocker", "Capsule must parse as a YAML mapping.")
    return data, None


def classify_branch_context_node(path: Path | str) -> str:
    branch = Path(path)
    readme = branch / "README.md"
    capsule = branch / "ION_CONTEXT_CAPSULE.yaml"
    if readme.exists() and capsule.exists():
        return "B2_capsule_node"
    if readme.exists():
        return "B1_readme_entry"
    return "B0_inert_folder"


def validate_branch_context_node(path: Path | str) -> dict[str, Any]:
    """Validate local branch-node posture without following external edges."""

    branch = Path(path)
    findings: list[BranchContextFinding] = []
    readme = branch / "README.md"
    capsule = branch / "ION_CONTEXT_CAPSULE.yaml"
    maturity = classify_branch_context_node(branch)
    read_order: list[str] = []
    tags: list[str] = []
    authority: dict[str, Any] = {}

    if not readme.exists():
        findings.append(_finding("readme_missing", "warning", "README.md is missing."))
    else:
        readme_text = readme.read_text(encoding="utf-8", errors="replace")
        if "ION_CONTEXT_CAPSULE.yaml" not in readme_text:
            findings.append(
                _finding(
                    "readme_does_not_point_to_capsule",
                    "warning",
                    "README.md should point to ION_CONTEXT_CAPSULE.yaml.",
                )
            )
        if "Receipts" not in readme_text and "receipts" not in readme_text:
            findings.append(
                _finding(
                    "readme_receipt_surface_missing",
                    "warning",
                    "README.md should expose receipts/history or state-claim proof boundary.",
                )
            )

    capsule_data: dict[str, Any] | None = None
    if capsule.exists():
        capsule_data, parse_finding = _load_capsule(capsule)
        if parse_finding:
            findings.append(parse_finding)
        elif capsule_data:
            if capsule_data.get("schema_id") != BRANCH_NODE_SCHEMA_ID:
                findings.append(
                    _finding(
                        "capsule_schema_id_mismatch",
                        "blocker",
                        f"Expected schema_id {BRANCH_NODE_SCHEMA_ID}.",
                    )
                )
            claimed_maturity = capsule_data.get("maturity_level")
            if claimed_maturity in MATURITY_ORDER:
                maturity = str(claimed_maturity)
            else:
                findings.append(
                    _finding(
                        "capsule_maturity_invalid",
                        "blocker",
                        "maturity_level must use the README branch context maturity enum.",
                    )
                )
            read_order = [str(item) for item in capsule_data.get("read_order", [])]
            tags = normalize_ion_tags(capsule_data.get("tags", []))
            authority = dict(capsule_data.get("authority", {}) or {})
            for field in ("branch_id", "branch_label", "path", "purpose", "authority", "read_order"):
                if field not in capsule_data:
                    findings.append(_finding(f"capsule_missing_{field}", "blocker", f"Capsule missing {field}."))
            if authority.get("production_authority") is True:
                findings.append(
                    _finding(
                        "capsule_claims_production_authority",
                        "blocker",
                        "Branch capsule must not grant production authority by itself.",
                    )
                )
            if authority.get("live_execution_authority") is True:
                findings.append(
                    _finding(
                        "capsule_claims_live_execution_authority",
                        "blocker",
                        "Branch capsule must not grant live execution authority by itself.",
                    )
                )
            for tag in tags:
                namespace = tag.split(":", 1)[0] if ":" in tag else None
                if namespace and namespace not in RESERVED_TAG_NAMESPACES:
                    findings.append(
                        _finding(
                            "unknown_tag_namespace",
                            "info",
                            f"Tag namespace {namespace!r} is not reserved; treat as navigation only.",
                        )
                    )
    else:
        findings.append(_finding("capsule_missing", "warning", "ION_CONTEXT_CAPSULE.yaml is missing."))

    blocker = any(item.severity == "blocker" for item in findings)
    if blocker:
        verdict = BLOCKED_VERDICT
        ok = False
    elif findings:
        verdict = DEGRADED_VERDICT
        ok = maturity in {"B1_readme_entry", "B2_capsule_node", "B3_routed_branch"}
    else:
        verdict = READY_VERDICT
        ok = True

    return BranchContextReport(
        path=str(branch),
        maturity_level=maturity,
        verdict=verdict,
        ok=ok,
        findings=findings,
        read_order=read_order,
        tags=tags,
        authority=authority,
    ).to_dict()


def compile_branch_entry_packet(path: Path | str) -> dict[str, Any]:
    """Return a compact branch entry packet for front-door/carrier use."""

    report = validate_branch_context_node(path)
    return {
        "schema_id": "ion.branch_entry_packet.v0_1",
        "branch_path": report["path"],
        "verdict": report["verdict"],
        "maturity_level": report["maturity_level"],
        "read_order": report["read_order"],
        "tags": report["tags"],
        "authority": report["authority"],
        "safe_next": "inspect_read_order_then_emit_candidate_or_blocker",
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "findings": report["findings"],
    }
