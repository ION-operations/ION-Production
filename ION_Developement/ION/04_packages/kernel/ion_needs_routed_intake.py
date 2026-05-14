"""Needs_Routed intake classifier and bounded archive lane.

This module classifies operator-dropped candidate packets without applying
patches, mutating active queues, staging Git paths, or claiming accepted state.
Confirmed write mode writes receipts/indexes and only moves artifacts that were
placed under Needs_Routed/drop/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_carrier_onboard import resolve_shell_root_from_ion_root

SCHEMA_ID = "ion.needs_routed_intake.v1"
READY_VERDICT = "ION_NEEDS_ROUTED_INTAKE_READY"
WRITTEN_VERDICT = "ION_NEEDS_ROUTED_INTAKE_WRITTEN"
BLOCKED_VERDICT = "ION_NEEDS_ROUTED_INTAKE_BLOCKED"
WRITE_CONFIRMATION = "ION_NEEDS_ROUTED_INTAKE_WRITE_CONFIRMED"

DEFAULT_NEEDS_ROUTED_NAME = "Needs_Routed"
SYSTEM_DIRS = {"drop", "intake", "routed", "history", "blocked", "receipts", "indexes"}
SOURCE_LANE_DIRS = {"diffs", "workpackets"}
MARKER_FILES = {".gitkeep"}
ROOT_CONTROL_FILES = {"README.md"}
TEXT_SUFFIXES = {".diff", ".patch", ".md", ".txt", ".yaml", ".yml", ".json", ".toml"}
PATCH_SUFFIXES = {".diff", ".patch"}
ZIP_SUFFIXES = {".zip"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
SECRET_NAME_PATTERNS = (
    ".env",
    "secret",
    "token",
    "credential",
    "credentials",
    "private_key",
    "client_secret",
    "service_role",
    "api_key",
    "vault",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_slug(value: str, *, limit: int = 120) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return (slug or "needs_routed_item")[:limit]


def _read_text_hint(path: Path) -> str:
    if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:65536]
    except OSError:
        return ""


def _workspace_root(shell_root: Path, workspace_root: str | Path | None) -> Path:
    return Path(workspace_root).expanduser().resolve() if workspace_root else shell_root.parent


def resolve_needs_routed_root(
    ion_root: str | Path | None = None,
    *,
    workspace_root: str | Path | None = None,
    needs_root: str | Path | None = None,
) -> Path:
    if needs_root:
        return Path(needs_root).expanduser().resolve()
    shell_root = resolve_shell_root_from_ion_root(ion_root)
    return _workspace_root(shell_root, workspace_root) / DEFAULT_NEEDS_ROUTED_NAME


def _repo_or_abs(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def _path_sha256(path: Path) -> str | None:
    if path.is_file():
        digest = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    if path.is_dir():
        digest = hashlib.sha256()
        for child in sorted(p for p in path.rglob("*") if p.is_file()):
            try:
                rel = child.relative_to(path).as_posix()
            except ValueError:
                rel = child.name
            digest.update(rel.encode("utf-8", errors="replace"))
            digest.update(b"\0")
            child_hash = _path_sha256(child)
            if child_hash:
                digest.update(child_hash.encode("ascii"))
            digest.update(b"\0")
        return digest.hexdigest()
    return None


def _path_size(path: Path) -> int | None:
    try:
        if path.is_file():
            return path.stat().st_size
        if path.is_dir():
            return sum(child.stat().st_size for child in path.rglob("*") if child.is_file())
    except OSError:
        return None
    return None


def _artifact_kind(path: Path) -> str:
    if path.is_dir():
        return "directory_bundle"
    suffix = path.suffix.lower()
    if suffix in PATCH_SUFFIXES:
        return "patch"
    if suffix in ZIP_SUFFIXES:
        return "bundle_zip"
    if suffix in {".yaml", ".yml"}:
        return "yaml_packet"
    if suffix == ".json":
        return "json_receipt_or_manifest"
    if suffix == ".md":
        return "markdown_workpacket"
    if suffix in IMAGE_SUFFIXES:
        return "visual_evidence"
    return "unknown_artifact"


def _secret_risk(path: Path) -> bool:
    lowered = path.as_posix().lower()
    if path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}:
        return True
    return any(pattern in lowered for pattern in SECRET_NAME_PATTERNS)


def _route_for(path: Path, *, kind: str, text_hint: str, duplicate: bool) -> tuple[str, float, list[str]]:
    name = path.name
    haystack = f"{name}\n{text_hint[:4096]}".upper()
    reasons: list[str] = [f"artifact_kind:{kind}"]

    if _secret_risk(path):
        return "secret_or_private_blocked", 1.0, [*reasons, "secret_or_private_path_marker"]
    if duplicate:
        return "duplicate_or_superseded", 0.95, [*reasons, "duplicate_sha256_in_scan"]
    if kind == "patch":
        if any(token in haystack for token in ("CUSTOM_GPT", "FRONT_DOOR", "PERSONA", "GPT_BUILDER")):
            return "custom_gpt_package_review", 0.9, [*reasons, "patch_mentions_custom_gpt_lane"]
        return "apply_candidate_patch", 0.86, [*reasons, "patch_or_diff_suffix"]
    if any(token in haystack for token in ("CUSTOM_GPT", "GPT_BUILDER", "FRONT_DOOR_CARRIER", "V4_7", "V4_6")):
        return "custom_gpt_package_review", 0.88, [*reasons, "name_or_text_matches_custom_gpt_lane"]
    if any(token in haystack for token in ("CONTEXT_PACKAGE", "CONTEXT CAPSULE", "ION_CONTEXT_CAPSULE", "CONTINUITY", "TRANSFER")):
        return "context_package_ingest", 0.84, [*reasons, "name_or_text_matches_context_package_lane"]
    if any(token in haystack for token in ("WORKPACKET", "PCKT-", "PACKET", "CODEX_WORKPACK")):
        return "queue_codex_workpacket", 0.82, [*reasons, "name_or_text_matches_workpacket_lane"]
    if any(token in haystack for token in ("RECEIPT", "REPORT", "VALIDATION", "EVIDENCE")):
        return "source_lane_archive", 0.72, [*reasons, "name_or_text_matches_evidence_lane"]
    if any(token in haystack for token in ("RUNTIME", "LEDGER", "QUEUE_STATE", "LOG")):
        return "runtime_evidence_archive", 0.72, [*reasons, "name_or_text_matches_runtime_evidence"]
    if kind in {"bundle_zip", "directory_bundle"}:
        return "owner_review_required", 0.55, [*reasons, "opaque_bundle_requires_owner_review"]
    return "owner_review_required", 0.5, [*reasons, "no_confident_route_match"]


def _queue_proposal(route_class: str, item_id: str, original_path: str) -> dict[str, Any] | None:
    if route_class not in {
        "apply_candidate_patch",
        "queue_codex_workpacket",
        "custom_gpt_package_review",
        "context_package_ingest",
    }:
        return None
    return {
        "proposal_only": True,
        "queue_mutation_performed": False,
        "packet_id": f"PCKT-ION-NEEDS-ROUTED-{item_id.upper()}",
        "work_class": route_class,
        "source_artifact_path": original_path,
        "objective": (
            "Review and route this Needs_Routed artifact under ION candidate-state "
            "boundaries. Do not apply, stage, commit, push, or mutate active queues "
            "without a later explicit packet."
        ),
    }


def _children(directory: Path, *, root_scope: bool = False) -> list[Path]:
    if not directory.exists():
        return []
    children = []
    for child in directory.iterdir():
        if child.name in MARKER_FILES:
            continue
        if root_scope and child.name in ROOT_CONTROL_FILES:
            continue
        children.append(child)
    return sorted(children)


def _scan_entries(needs_root: Path, scan_scope: str) -> tuple[list[Path], str, list[str]]:
    warnings: list[str] = []
    drop_root = needs_root / "drop"
    if scan_scope == "drop":
        return _children(drop_root), "drop", warnings

    if scan_scope == "root":
        entries = [
            child
            for child in _children(needs_root, root_scope=True)
            if child.name not in SYSTEM_DIRS and child.name not in SOURCE_LANE_DIRS
        ]
        return sorted(entries), "root", warnings

    drop_entries = _children(drop_root)
    if drop_entries:
        return drop_entries, "drop", warnings

    entries = [
        child
        for child in _children(needs_root, root_scope=True)
        if child.name not in SYSTEM_DIRS and child.name not in SOURCE_LANE_DIRS
    ]
    warnings.append("drop_empty_scanning_top_level_legacy_backlog_read_only")
    return sorted(entries), "root", warnings


def _item_id(path: Path, digest: str | None) -> str:
    seed = digest[:12] if digest else _safe_slug(path.name, limit=24)
    return f"needs_{seed}_{_safe_slug(path.stem or path.name, limit=48).lower()}"


def build_needs_routed_intake(
    ion_root: str | Path | None = None,
    *,
    workspace_root: str | Path | None = None,
    needs_root: str | Path | None = None,
    scan_scope: str = "auto",
) -> dict[str, Any]:
    root = resolve_needs_routed_root(ion_root, workspace_root=workspace_root, needs_root=needs_root)
    entries, effective_scope, warnings = _scan_entries(root, scan_scope)
    seen_hashes: set[str] = set()
    items: list[dict[str, Any]] = []
    for path in entries:
        digest = _path_sha256(path)
        duplicate = bool(digest and digest in seen_hashes)
        if digest:
            seen_hashes.add(digest)
        kind = _artifact_kind(path)
        text_hint = _read_text_hint(path)
        route_class, confidence, reasons = _route_for(path, kind=kind, text_hint=text_hint, duplicate=duplicate)
        rel = _repo_or_abs(path, root.parent)
        status = "candidate_unmoved"
        if route_class == "secret_or_private_blocked":
            status = "blocked_pending_operator_review"
        item = {
            "item_id": _item_id(path, digest),
            "original_path": rel,
            "sha256": digest,
            "size_bytes": _path_size(path),
            "artifact_kind": kind,
            "route_class": route_class,
            "confidence": confidence,
            "status": status,
            "reasons": reasons,
            "target_path": None,
            "moved_to": None,
            "queue_proposal": _queue_proposal(route_class, _item_id(path, digest), rel),
            "source_scope": effective_scope,
        }
        items.append(item)

    summary = _summary(items)
    blocked_findings = [
        f"{item['original_path']}:secret_or_private_blocked"
        for item in items
        if item["route_class"] == "secret_or_private_blocked"
    ]
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": READY_VERDICT,
        "ok": True,
        "posture": "sandbox-candidate",
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "needs_routed_root": root.as_posix(),
        "scan_scope": effective_scope,
        "write_performed": False,
        "file_moves_performed": False,
        "queue_mutation_performed": False,
        "receipt_path": None,
        "index_path": None,
        "items": items,
        "summary": summary,
        "blocked_findings": blocked_findings,
        "warning_findings": warnings,
    }


def _summary(items: list[Mapping[str, Any]]) -> dict[str, Any]:
    by_route: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    by_status: dict[str, int] = {}
    queue_proposal_count = 0
    for item in items:
        route = str(item.get("route_class", "unknown"))
        kind = str(item.get("artifact_kind", "unknown"))
        status = str(item.get("status", "unknown"))
        by_route[route] = by_route.get(route, 0) + 1
        by_kind[kind] = by_kind.get(kind, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
        if item.get("queue_proposal"):
            queue_proposal_count += 1
    return {
        "item_count": len(items),
        "route_class_counts": by_route,
        "artifact_kind_counts": by_kind,
        "status_counts": by_status,
        "queue_proposal_count": queue_proposal_count,
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _target_for(root: Path, item: Mapping[str, Any], original_path: Path, stamp: str) -> Path | None:
    try:
        original_path.relative_to(root / "drop")
    except ValueError:
        return None
    route = str(item.get("route_class", "owner_review_required"))
    lane = "blocked" if route == "secret_or_private_blocked" else "history"
    date_part = stamp[:8]
    target_dir = root / lane / date_part / route
    target_name = _safe_slug(original_path.name)
    target = target_dir / target_name
    if not target.exists():
        return target
    suffix = str(item.get("sha256") or "duplicate")[:10]
    return target_dir / f"{Path(target_name).stem}_{suffix}{Path(target_name).suffix}"


def write_needs_routed_intake(
    ion_root: str | Path | None = None,
    *,
    workspace_root: str | Path | None = None,
    needs_root: str | Path | None = None,
    scan_scope: str = "auto",
    confirmation: str | None = None,
) -> dict[str, Any]:
    if confirmation != WRITE_CONFIRMATION:
        result = build_needs_routed_intake(
            ion_root,
            workspace_root=workspace_root,
            needs_root=needs_root,
            scan_scope=scan_scope,
        )
        result.update(
            {
                "verdict": BLOCKED_VERDICT,
                "ok": False,
                "blocked_findings": [
                    *result.get("blocked_findings", []),
                    "write_confirmation_required",
                ],
            }
        )
        return result

    root = resolve_needs_routed_root(ion_root, workspace_root=workspace_root, needs_root=needs_root)
    for dirname in (*SYSTEM_DIRS, *SOURCE_LANE_DIRS):
        (root / dirname).mkdir(parents=True, exist_ok=True)

    result = build_needs_routed_intake(
        ion_root,
        workspace_root=workspace_root,
        needs_root=root,
        scan_scope=scan_scope,
    )
    stamp = _timestamp()
    moves_performed = False
    updated_items: list[dict[str, Any]] = []
    for item in result["items"]:
        item = dict(item)
        original = root.parent / str(item["original_path"])
        target = _target_for(root, item, original, stamp)
        if target is None:
            item["status"] = "review_only_not_moved"
            item["reasons"] = [*item.get("reasons", []), "legacy_or_source_lane_backlog_not_moved_by_default"]
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(original.as_posix(), target.as_posix())
            item["target_path"] = _repo_or_abs(target, root.parent)
            item["moved_to"] = item["target_path"]
            item["status"] = "blocked_moved_for_review" if item["route_class"] == "secret_or_private_blocked" else "ingested_moved_to_history"
            moves_performed = True
        updated_items.append(item)

    result["items"] = updated_items
    result["summary"] = _summary(updated_items)
    result["verdict"] = WRITTEN_VERDICT
    result["write_performed"] = True
    result["file_moves_performed"] = moves_performed
    result["generated_at"] = _now()

    receipt_path = root / "receipts" / f"needs_routed_intake_{stamp}.json"
    index_path = root / "indexes" / "NEEDS_ROUTED_INDEX.json"
    result["receipt_path"] = _repo_or_abs(receipt_path, root.parent)
    result["index_path"] = _repo_or_abs(index_path, root.parent)
    _write_json(receipt_path, result)
    _write_json(index_path, result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify and optionally archive Needs_Routed artifacts.")
    parser.add_argument("--ion-root", default=None)
    parser.add_argument("--workspace-root", default=None)
    parser.add_argument("--needs-root", default=None)
    parser.add_argument("--scan-scope", choices=("auto", "drop", "root"), default="auto")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--confirmation", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.write:
        result = write_needs_routed_intake(
            args.ion_root,
            workspace_root=args.workspace_root,
            needs_root=args.needs_root,
            scan_scope=args.scan_scope,
            confirmation=args.confirmation,
        )
    else:
        result = build_needs_routed_intake(
            args.ion_root,
            workspace_root=args.workspace_root,
            needs_root=args.needs_root,
            scan_scope=args.scan_scope,
        )

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["verdict"])
        print(json.dumps(result["summary"], indent=2, sort_keys=True))
        if result.get("receipt_path"):
            print(f"receipt: {result['receipt_path']}")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
