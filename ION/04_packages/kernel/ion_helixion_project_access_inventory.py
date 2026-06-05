"""Project portfolio to Helixion access-object inventory.

This candidate maps the existing project portfolio manifest into objects that
can be governed by the Helixion multi-user authorization evaluator. It keeps
virtual paths as the UI-facing address and redacts absolute local paths for
lower-trust ranks.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping
from urllib.parse import quote

from .ion_helixion_multi_user_identity import (
    AUTHORITY_FALSE,
    HelixionCapability,
    HelixionRankCeiling,
    HelixionSensitivityTier,
    normalize_rank,
    rank_ceiling_allows,
)


SCHEMA_ID = "ion.helixion_project_access_inventory.v0_1"
REDACTED_SCHEMA_ID = "ion.helixion_project_access_inventory.redacted.v0_1"
SURFACE_SCHEMA_ID = "ion.helixion_projects_surface.v0_1"
FAMILY_DETAIL_SCHEMA_ID = "ion.helixion_project_family_detail.v0_1"
DEFAULT_PORTFOLIO_MANIFEST = Path("ION/05_context/current/project_portfolio/PROJECT_PORTFOLIO_MANIFEST.json")
WORKBENCH_PROJECT_ROUTES = {
    "cosmos": "/projects/cosmos",
    "ion_dev": "/projects",
}
WORKBENCH_PROJECT_EMBEDS = {
    "cosmos": "/projects/cosmos/preview/",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _compact(value: Any, fallback: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    return fallback


def _as_int(value: Any, fallback: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value)
    return fallback


def _safe_text(value: Any, fallback: str = "") -> str:
    text = _compact(value, fallback)
    if not text:
        return fallback
    if text.startswith(("~", "file://")) or "/home/" in text or text.startswith("/"):
        return "redacted_local_ref"
    return text


def _slug(value: Any, fallback: str = "item") -> str:
    text = re.sub(r"[^a-z0-9]+", "-", _compact(value, fallback).lower()).strip("-")
    return text or fallback


def _hash_ref(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_compact(value).encode("utf-8")).hexdigest()


def _object_id(prefix: str, *parts: Any) -> str:
    seed = "|".join(_compact(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:24]}"


def _virtual_path(workspace_id: str, *parts: Any) -> str:
    safe_parts = [_slug(part) for part in parts if _compact(part)]
    return "ion://workspace/" + _slug(workspace_id, "workspace") + "/" + "/".join(safe_parts)


def _detail_href(family_id: str) -> str:
    return "/projects/family/" + quote(family_id, safe="")


def _safe_public_route(value: Any, fallback: str = "") -> str:
    route = _compact(value, fallback)
    if not route:
        return fallback
    if route.startswith("/") and not route.startswith("//") and "/home/" not in route and "file://" not in route:
        return route
    return fallback


def _load_project_portfolio_manifest(
    root: str | Path = ".",
    *,
    manifest_path: str | Path | None = None,
) -> tuple[Path, Mapping[str, Any]]:
    shell_root = Path(root).expanduser().resolve()
    path = Path(manifest_path) if manifest_path is not None else shell_root / DEFAULT_PORTFOLIO_MANIFEST
    if not path.is_absolute():
        path = shell_root / path
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, Mapping):
        raise ValueError("project portfolio manifest must be a JSON object")
    return path, manifest


def _object_row(
    *,
    object_id: str,
    object_type: str,
    workspace_id: str,
    label: str,
    sensitivity: HelixionSensitivityTier,
    virtual_path: str,
    parent_object_id: str | None = None,
    domain_id: str | None = None,
    family_id: str | None = None,
    project_id: str | None = None,
    version_id: str | None = None,
    canonical_ref: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_id": "ion.helixion_access_object.v0_1",
        "object_id": object_id,
        "object_type": object_type,
        "workspace_id": workspace_id,
        "parent_object_id": parent_object_id,
        "domain_id": domain_id,
        "family_id": family_id,
        "project_id": project_id,
        "version_id": version_id,
        "label": label,
        "sensitivity": str(sensitivity),
        "virtual_path": virtual_path,
        "canonical_ref": canonical_ref,
        "canonical_ref_sha256": _hash_ref(canonical_ref) if canonical_ref else "",
        "canonical_ref_redacted_by_default": bool(canonical_ref),
        "metadata": dict(metadata or {}),
        "authority": dict(AUTHORITY_FALSE),
    }


def _doc_objects(
    *,
    workspace_id: str,
    domain_id: str,
    family_id: str,
    version: Mapping[str, Any],
    parent_object_id: str,
    base_virtual_path: str,
    max_docs_per_version: int | None,
) -> list[dict[str, Any]]:
    docs = ((version.get("docs") or {}).get("docs") or []) if isinstance(version.get("docs"), Mapping) else []
    if max_docs_per_version is not None:
        docs = docs[:max_docs_per_version]
    rows: list[dict[str, Any]] = []
    for index, doc in enumerate(docs, start=1):
        if not isinstance(doc, Mapping):
            continue
        rel_path = _compact(doc.get("rel_path"), f"doc-{index}")
        canonical_ref = _compact(doc.get("path"))
        doc_id = _object_id("doc", workspace_id, family_id, version.get("version_id"), rel_path)
        rows.append(
            _object_row(
                object_id=doc_id,
                object_type="doc",
                workspace_id=workspace_id,
                label=_compact(doc.get("title"), rel_path),
                sensitivity=HelixionSensitivityTier.INTERNAL,
                virtual_path=f"{base_virtual_path}/docs/{_slug(rel_path, f'doc-{index}')}",
                parent_object_id=parent_object_id,
                domain_id=domain_id,
                family_id=family_id,
                project_id=_compact(version.get("project_id")),
                version_id=_compact(version.get("version_id")),
                canonical_ref=canonical_ref,
                metadata={
                    "rel_path": rel_path,
                    "kind": _compact(doc.get("kind"), "doc"),
                    "extension": _compact(doc.get("extension")),
                    "primary": bool(doc.get("primary")),
                    "reference": bool(doc.get("reference")),
                    "bytes": doc.get("bytes") if isinstance(doc.get("bytes"), int) else None,
                },
            )
        )
    return rows


def _diff_objects(
    *,
    workspace_id: str,
    domain_id: str,
    family: Mapping[str, Any],
    parent_object_id: str,
    base_virtual_path: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, diff in enumerate(family.get("diffs") or [], start=1):
        if not isinstance(diff, Mapping):
            continue
        diff_id = _compact(diff.get("diff_id"), f"diff-{index}")
        rows.append(
            _object_row(
                object_id=_object_id("diff", workspace_id, family.get("family_id"), diff_id),
                object_type="diff",
                workspace_id=workspace_id,
                label=diff_id,
                sensitivity=HelixionSensitivityTier.INTERNAL,
                virtual_path=f"{base_virtual_path}/diffs/{_slug(diff_id, f'diff-{index}')}",
                parent_object_id=parent_object_id,
                domain_id=domain_id,
                family_id=_compact(family.get("family_id")),
                canonical_ref=_compact(diff.get("manifest_path")),
                metadata={
                    "from_project_id": _compact(diff.get("from_project_id")),
                    "to_project_id": _compact(diff.get("to_project_id")),
                    "status": _compact(diff.get("status")),
                    "added_count": (((diff.get("file_diff") or {}).get("added_count")) if isinstance(diff.get("file_diff"), Mapping) else None),
                    "changed_count": (((diff.get("file_diff") or {}).get("changed_count")) if isinstance(diff.get("file_diff"), Mapping) else None),
                    "removed_count": (((diff.get("file_diff") or {}).get("removed_count")) if isinstance(diff.get("file_diff"), Mapping) else None),
                },
            )
        )
    return rows


def build_project_access_inventory(
    manifest: Mapping[str, Any],
    *,
    workspace_id: str = "wsp_local_operator",
    max_docs_per_version: int | None = None,
) -> dict[str, Any]:
    """Build access objects from a project portfolio manifest mapping."""

    objects: list[dict[str, Any]] = []
    file_roots: list[dict[str, Any]] = []
    domain_object_ids: dict[str, str] = {}

    for domain in manifest.get("canonical_domains") or []:
        if not isinstance(domain, Mapping):
            continue
        domain_id = _compact(domain.get("domain_id"), "unknown-domain")
        object_id = _object_id("domain", workspace_id, domain_id)
        domain_object_ids[domain_id] = object_id
        objects.append(
            _object_row(
                object_id=object_id,
                object_type="domain",
                workspace_id=workspace_id,
                label=_compact(domain.get("label"), domain_id),
                sensitivity=HelixionSensitivityTier.INTERNAL,
                virtual_path=_virtual_path(workspace_id, "domains", domain_id),
                domain_id=domain_id,
                metadata={
                    "summary": _compact(domain.get("summary")),
                    "project_count": domain.get("project_count"),
                    "version_count": domain.get("version_count"),
                    "family_count": domain.get("family_count"),
                    "launchable_count": domain.get("launchable_count"),
                    "doc_count": domain.get("doc_count"),
                    "diff_count": domain.get("diff_count"),
                },
            )
        )

    for family in manifest.get("families") or []:
        if not isinstance(family, Mapping):
            continue
        family_id = _compact(family.get("family_id"), "unknown-family")
        domain_id = _compact(family.get("domain_id"), "tools-generated-apps")
        domain_parent = domain_object_ids.get(domain_id) or _object_id("domain", workspace_id, domain_id)
        family_object_id = _object_id("family", workspace_id, family_id)
        family_virtual_path = _virtual_path(workspace_id, "domains", domain_id, "projects", family_id)
        objects.append(
            _object_row(
                object_id=family_object_id,
                object_type="project_family",
                workspace_id=workspace_id,
                label=_compact(family.get("label"), family_id),
                sensitivity=HelixionSensitivityTier.INTERNAL,
                virtual_path=family_virtual_path,
                parent_object_id=domain_parent,
                domain_id=domain_id,
                family_id=family_id,
                canonical_ref=_compact(family.get("current_path")),
                metadata={
                    "lineage_status": _compact(family.get("lineage_status")),
                    "project_count": family.get("project_count"),
                    "version_count": family.get("version_count"),
                    "branch_count": family.get("branch_count"),
                    "diff_count": family.get("diff_count"),
                    "doc_count": family.get("doc_count"),
                    "launchable_count": family.get("launchable_count"),
                    "source_ids": family.get("source_ids") if isinstance(family.get("source_ids"), list) else [],
                },
            )
        )
        objects.extend(
            _diff_objects(
                workspace_id=workspace_id,
                domain_id=domain_id,
                family=family,
                parent_object_id=family_object_id,
                base_virtual_path=family_virtual_path,
            )
        )
        for version in family.get("versions") or []:
            if not isinstance(version, Mapping):
                continue
            version_id = _compact(version.get("version_id"), "version")
            project_id = _compact(version.get("project_id"))
            version_object_id = _object_id("version", workspace_id, family_id, version_id, project_id)
            version_virtual_path = f"{family_virtual_path}/versions/{_slug(version_id, 'version')}"
            source_path = _compact(version.get("path"))
            objects.append(
                _object_row(
                    object_id=version_object_id,
                    object_type="project_version",
                    workspace_id=workspace_id,
                    label=_compact(version.get("display_label"), _compact(version.get("label"), version_id)),
                    sensitivity=HelixionSensitivityTier.INTERNAL,
                    virtual_path=version_virtual_path,
                    parent_object_id=family_object_id,
                    domain_id=domain_id,
                    family_id=family_id,
                    project_id=project_id,
                    version_id=version_id,
                    canonical_ref=source_path,
                    metadata={
                        "sequence_label": _compact(version.get("sequence_label")),
                        "version_token": _compact(version.get("version_token")),
                        "date_token": _compact(version.get("date_token")),
                        "branch_id": _compact(version.get("branch_id")),
                        "branch_label": _compact(version.get("branch_label")),
                        "stack": _compact(version.get("stack")),
                        "launchable": bool(version.get("launchable")),
                        "is_current": bool(version.get("is_current")),
                    },
                )
            )
            if source_path:
                file_root_id = _object_id("file_root", workspace_id, family_id, version_id, source_path)
                file_root = _object_row(
                    object_id=file_root_id,
                    object_type="file_root",
                    workspace_id=workspace_id,
                    label=f"{_compact(version.get('sequence_label'), version_id)} source root",
                    sensitivity=HelixionSensitivityTier.SOURCE,
                    virtual_path=f"{version_virtual_path}/source",
                    parent_object_id=version_object_id,
                    domain_id=domain_id,
                    family_id=family_id,
                    project_id=project_id,
                    version_id=version_id,
                    canonical_ref=source_path,
                    metadata={
                        "root_kind": "project_source_root",
                        "launchable": bool(version.get("launchable")),
                    },
                )
                objects.append(file_root)
                file_roots.append(file_root)
            if version.get("launchable"):
                launch = version.get("launch") if isinstance(version.get("launch"), Mapping) else {}
                objects.append(
                    _object_row(
                        object_id=_object_id("launch", workspace_id, family_id, version_id, project_id),
                        object_type="launch",
                        workspace_id=workspace_id,
                        label=f"Launch {_compact(version.get('display_label'), version_id)}",
                        sensitivity=HelixionSensitivityTier.LOCAL_CONTROL,
                        virtual_path=f"{version_virtual_path}/launch",
                        parent_object_id=version_object_id,
                        domain_id=domain_id,
                        family_id=family_id,
                        project_id=project_id,
                        version_id=version_id,
                        canonical_ref=source_path,
                        metadata={
                            "framework": _compact(launch.get("framework")),
                            "mode": _compact(launch.get("mode")),
                            "requires_local_machine": bool(launch.get("requires_local_machine", True)),
                            "managed_window_stops_server": bool(launch.get("managed_window_stops_server")),
                        },
                    )
                )
            objects.extend(
                _doc_objects(
                    workspace_id=workspace_id,
                    domain_id=domain_id,
                    family_id=family_id,
                    version=version,
                    parent_object_id=version_object_id,
                    base_virtual_path=version_virtual_path,
                    max_docs_per_version=max_docs_per_version,
                )
            )

    summary = {
        "domain_count": len([item for item in objects if item["object_type"] == "domain"]),
        "project_family_count": len([item for item in objects if item["object_type"] == "project_family"]),
        "version_count": len([item for item in objects if item["object_type"] == "project_version"]),
        "file_root_count": len(file_roots),
        "doc_count": len([item for item in objects if item["object_type"] == "doc"]),
        "diff_count": len([item for item in objects if item["object_type"] == "diff"]),
        "launch_count": len([item for item in objects if item["object_type"] == "launch"]),
        "object_count": len(objects),
    }
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _utc_now(),
        "workspace_id": workspace_id,
        "source_schema_id": _compact(manifest.get("schema_id")),
        "source_generated_at": _compact(manifest.get("generated_at")),
        "summary": summary,
        "objects": objects,
        "file_roots": file_roots,
        "virtual_path_contract": "UI and low-trust API surfaces use ion:// virtual paths; absolute canonical refs are redacted unless the rank can inspect local paths.",
        "authority": dict(AUTHORITY_FALSE),
    }


def build_project_access_inventory_from_file(
    root: str | Path = ".",
    *,
    manifest_path: str | Path | None = None,
    workspace_id: str = "wsp_local_operator",
    max_docs_per_version: int | None = None,
) -> dict[str, Any]:
    path, manifest = _load_project_portfolio_manifest(root, manifest_path=manifest_path)
    inventory = build_project_access_inventory(
        manifest,
        workspace_id=workspace_id,
        max_docs_per_version=max_docs_per_version,
    )
    inventory["source_manifest_path"] = path.as_posix()
    return inventory


def rank_can_view_sensitivity(rank: str | HelixionRankCeiling, sensitivity: str | HelixionSensitivityTier) -> bool:
    normalized_rank = normalize_rank(rank)
    normalized_sensitivity = HelixionSensitivityTier(str(sensitivity))
    if normalized_sensitivity == HelixionSensitivityTier.PUBLIC:
        return True
    if normalized_sensitivity == HelixionSensitivityTier.INTERNAL:
        return rank_ceiling_allows(normalized_rank, HelixionCapability.CURATED_DOC_READ)
    if normalized_sensitivity == HelixionSensitivityTier.SOURCE:
        return rank_ceiling_allows(normalized_rank, HelixionCapability.SOURCE_READ)
    if normalized_sensitivity == HelixionSensitivityTier.SENSITIVE_SOURCE:
        return rank_ceiling_allows(normalized_rank, HelixionCapability.SENSITIVE_SOURCE_REQUEST)
    if normalized_sensitivity == HelixionSensitivityTier.LOCAL_CONTROL:
        return rank_ceiling_allows(normalized_rank, HelixionCapability.PREVIEW_LAUNCH) or rank_ceiling_allows(
            normalized_rank,
            HelixionCapability.LOCAL_CONTROL_REQUEST,
        )
    return False


def rank_can_inspect_absolute_paths(rank: str | HelixionRankCeiling) -> bool:
    return normalize_rank(rank) in {
        HelixionRankCeiling.FOUNDER_ROOT_STEWARD,
        HelixionRankCeiling.STEWARD_ADMIN,
        HelixionRankCeiling.LEAD_ARCHITECT,
    }


def redact_project_access_inventory_for_rank(
    inventory: Mapping[str, Any],
    rank: str | HelixionRankCeiling,
) -> dict[str, Any]:
    normalized_rank = normalize_rank(rank)
    can_inspect_paths = rank_can_inspect_absolute_paths(normalized_rank)
    visible_objects: list[dict[str, Any]] = []
    hidden_count = 0
    for item in inventory.get("objects") or []:
        if not isinstance(item, Mapping):
            continue
        sensitivity = _compact(item.get("sensitivity"), HelixionSensitivityTier.INTERNAL.value)
        if not rank_can_view_sensitivity(normalized_rank, sensitivity):
            hidden_count += 1
            continue
        row = deepcopy(dict(item))
        if not can_inspect_paths and row.get("canonical_ref"):
            row["canonical_ref"] = None
            row["canonical_ref_redacted"] = True
        row["rank_visible"] = True
        visible_objects.append(row)
    file_roots = [item for item in visible_objects if item.get("object_type") == "file_root"]
    return {
        "schema_id": REDACTED_SCHEMA_ID,
        "workspace_id": inventory.get("workspace_id"),
        "rank_ceiling": str(normalized_rank),
        "path_inspection_allowed": can_inspect_paths,
        "object_count": len(visible_objects),
        "hidden_object_count": hidden_count,
        "summary": {
            "visible_domain_count": len([item for item in visible_objects if item.get("object_type") == "domain"]),
            "visible_project_family_count": len([item for item in visible_objects if item.get("object_type") == "project_family"]),
            "visible_version_count": len([item for item in visible_objects if item.get("object_type") == "project_version"]),
            "visible_file_root_count": len(file_roots),
            "visible_doc_count": len([item for item in visible_objects if item.get("object_type") == "doc"]),
            "visible_launch_count": len([item for item in visible_objects if item.get("object_type") == "launch"]),
        },
        "objects": visible_objects,
        "file_roots": file_roots,
        "authority": dict(AUTHORITY_FALSE),
    }


def project_access_inventory_summary(inventory: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "ion.helixion_project_access_inventory.summary.v0_1",
        "workspace_id": inventory.get("workspace_id"),
        "summary": dict(inventory.get("summary") if isinstance(inventory.get("summary"), Mapping) else {}),
        "virtual_path_contract": inventory.get("virtual_path_contract"),
        "authority": dict(AUTHORITY_FALSE),
    }


def _visible_object_counts(objects: Iterable[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in objects:
        value = _compact(item.get(key), "unknown")
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _safe_count_summary(value: Mapping[str, Any]) -> dict[str, int | bool]:
    keys = (
        "archive_project_count",
        "canonical_domain_count",
        "documentation_surface_count",
        "documented_family_count",
        "duplicate_cluster_count",
        "family_count",
        "group_count",
        "launchable_count",
        "legacy_copy_cluster_count",
        "materialized_present",
        "project_os_blocked_count",
        "project_os_ready_count",
        "project_os_watch_count",
        "project_root_count",
        "reference_count",
        "source_root_count",
        "versioned_family_count",
        "workspace_dir_count",
    )
    summary: dict[str, int | bool] = {}
    for key in keys:
        if key not in value:
            continue
        raw_value = value.get(key)
        summary[key] = raw_value if isinstance(raw_value, bool) else _as_int(raw_value)
    return summary


def _safe_sequence(items: Any, keys: tuple[str, ...], *, limit: int = 8) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not isinstance(items, list):
        return rows
    for item in items[:limit]:
        if not isinstance(item, Mapping):
            continue
        row: dict[str, Any] = {}
        for key in keys:
            raw_value = item.get(key)
            if isinstance(raw_value, (int, float, bool)):
                row[key] = raw_value
            else:
                row[key] = _safe_text(raw_value)
        rows.append(row)
    return rows


def _safe_operating_system(ops: Any, *, domain_level: bool = False) -> dict[str, Any]:
    if not isinstance(ops, Mapping):
        return {}
    if domain_level:
        return {
            "schema_id": _compact(ops.get("schema_id")),
            "posture": _compact(ops.get("posture")),
            "average_readiness_score": _as_int(ops.get("average_readiness_score")),
            "ready_count": _as_int(ops.get("ready_count")),
            "watch_count": _as_int(ops.get("watch_count")),
            "blocked_count": _as_int(ops.get("blocked_count")),
            "top_risks": _safe_sequence(
                ops.get("top_risks"),
                ("risk_id", "title", "severity", "mitigation", "family_id", "family_label"),
                limit=6,
            ),
            "board_columns": _safe_sequence(ops.get("board_columns"), ("column_id", "label", "count"), limit=8),
            "maintenance_rhythm": _safe_sequence(ops.get("maintenance_rhythm"), ("label", "cadence", "focus"), limit=6),
        }
    return {
        "schema_id": _compact(ops.get("schema_id")),
        "posture": _compact(ops.get("posture")),
        "readiness_score": _as_int(ops.get("readiness_score")),
        "summary": _safe_count_summary(ops.get("summary") if isinstance(ops.get("summary"), Mapping) else {}),
        "lifecycle": _safe_sequence(ops.get("lifecycle"), ("stage_id", "label", "objective", "status"), limit=8),
        "maintenance_lanes": _safe_sequence(
            ops.get("maintenance_lanes"),
            ("lane_id", "label", "objective", "status", "next_action"),
            limit=8,
        ),
        "next_actions": _safe_sequence(
            ops.get("next_actions"),
            ("action_id", "label", "lane", "priority", "detail"),
            limit=8,
        ),
        "quality_gates": _safe_sequence(ops.get("quality_gates"), ("gate_id", "label", "status", "evidence"), limit=8),
        "human_workflows": _safe_sequence(
            ops.get("human_workflows"),
            ("workflow_id", "label", "trigger", "cadence", "output"),
            limit=8,
        ),
        "operating_principles": [_safe_text(item) for item in (ops.get("operating_principles") or [])[:8] if _compact(item)],
        "risk_register": _safe_sequence(ops.get("risk_register"), ("risk_id", "title", "severity", "mitigation"), limit=8),
    }


def _safe_domain(domain: Mapping[str, Any]) -> dict[str, Any]:
    domain_id = _compact(domain.get("domain_id"), "unknown-domain")
    return {
        "domain_id": domain_id,
        "label": _compact(domain.get("label"), domain_id),
        "summary": _compact(domain.get("summary")),
        "sort_order": _as_int(domain.get("sort_order")),
        "project_count": _as_int(domain.get("project_count")),
        "family_count": _as_int(domain.get("family_count")),
        "version_count": _as_int(domain.get("version_count")),
        "versioned_family_count": _as_int(domain.get("versioned_family_count")),
        "branch_count": _as_int(domain.get("branch_count")),
        "diff_count": _as_int(domain.get("diff_count")),
        "doc_count": _as_int(domain.get("doc_count")),
        "reference_count": _as_int(domain.get("reference_count")),
        "launchable_count": _as_int(domain.get("launchable_count")),
        "operating_system": _safe_operating_system(domain.get("operating_system"), domain_level=True),
        "virtual_path": _virtual_path("wsp_local_operator", "domains", domain_id),
    }


def _safe_version(version: Mapping[str, Any], *, workspace_id: str, domain_id: str, family_id: str) -> dict[str, Any]:
    version_id = _compact(version.get("version_id"), "version")
    docs = version.get("docs") if isinstance(version.get("docs"), Mapping) else {}
    coverage = docs.get("coverage") if isinstance(docs.get("coverage"), Mapping) else {}
    launch = version.get("launch") if isinstance(version.get("launch"), Mapping) else {}
    return {
        "version_id": version_id,
        "project_id": _compact(version.get("project_id")),
        "display_label": _compact(version.get("display_label"), _compact(version.get("label"), version_id)),
        "sequence_label": _compact(version.get("sequence_label")),
        "version_token": _compact(version.get("version_token")),
        "date_token": _compact(version.get("date_token")),
        "milestone_token": _compact(version.get("milestone_token")),
        "branch_id": _compact(version.get("branch_id")),
        "branch_label": _compact(version.get("branch_label")),
        "stack": _compact(version.get("stack")),
        "launchable": bool(version.get("launchable")),
        "is_current": bool(version.get("is_current")),
        "launch_status": _compact(launch.get("status")),
        "launch_mode": _compact(launch.get("mode")),
        "docs": {
            "status": _compact(docs.get("status")),
            "doc_count": _as_int(docs.get("doc_count")),
            "reference_count": _as_int(docs.get("reference_count")),
            "coverage": {
                "has_readme": bool(coverage.get("has_readme")),
                "has_architecture": bool(coverage.get("has_architecture")),
                "has_runbook": bool(coverage.get("has_runbook")),
                "has_reference": bool(coverage.get("has_reference")),
            },
        },
        "virtual_path": f"{_virtual_path(workspace_id, 'domains', domain_id, 'projects', family_id)}/versions/{_slug(version_id, 'version')}",
    }


def _family_score(family: Mapping[str, Any]) -> int:
    ops = family.get("operating_system") if isinstance(family.get("operating_system"), Mapping) else {}
    posture_bonus = {"ready": 40, "watch": 20, "blocked": 0}.get(_compact(ops.get("posture")), 10)
    return (
        posture_bonus
        + _as_int(ops.get("readiness_score"))
        + (_as_int(family.get("launchable_count")) * 8)
        + (_as_int(family.get("version_count")) * 3)
        + _as_int(family.get("doc_count"))
    )


def _safe_family(family: Mapping[str, Any], *, workspace_id: str, max_versions_per_family: int) -> dict[str, Any]:
    family_id = _compact(family.get("family_id"), "unknown-family")
    domain_id = _compact(family.get("domain_id"), "tools-generated-apps")
    versions = [item for item in (family.get("versions") or []) if isinstance(item, Mapping)]
    current_version = next((item for item in versions if item.get("is_current")), versions[-1] if versions else {})
    safe_versions = [
        _safe_version(version, workspace_id=workspace_id, domain_id=domain_id, family_id=family_id)
        for version in versions[:max_versions_per_family]
    ]
    if current_version and all(item["version_id"] != _compact(current_version.get("version_id")) for item in safe_versions):
        safe_versions.insert(0, _safe_version(current_version, workspace_id=workspace_id, domain_id=domain_id, family_id=family_id))
    docs = family.get("docs") if isinstance(family.get("docs"), Mapping) else {}
    return {
        "family_id": family_id,
        "label": _compact(family.get("label"), family_id),
        "domain_id": domain_id,
        "domain_label": _compact(family.get("domain_label")),
        "group_id": _compact(family.get("group_id")),
        "lineage_status": _compact(family.get("lineage_status")),
        "project_count": _as_int(family.get("project_count")),
        "version_count": _as_int(family.get("version_count")),
        "branch_count": _as_int(family.get("branch_count")),
        "workspace_dir_count": _as_int(family.get("workspace_dir_count")),
        "diff_count": _as_int(family.get("diff_count")),
        "doc_count": _as_int(family.get("doc_count")),
        "reference_count": _as_int(family.get("reference_count")),
        "launchable_count": _as_int(family.get("launchable_count")),
        "source_ids": [str(item) for item in family.get("source_ids", []) if _compact(item)],
        "docs": {
            "status": _compact(docs.get("status")),
            "doc_count": _as_int(docs.get("doc_count")),
            "reference_count": _as_int(docs.get("reference_count")),
            "recommended_sections": [str(item) for item in (docs.get("recommended_sections") or [])[:10] if _compact(item)],
        },
        "operating_system": _safe_operating_system(family.get("operating_system")),
        "current": _safe_version(current_version, workspace_id=workspace_id, domain_id=domain_id, family_id=family_id)
        if isinstance(current_version, Mapping) and current_version
        else {},
        "versions": safe_versions[:max_versions_per_family],
        "virtual_path": _virtual_path(workspace_id, "domains", domain_id, "projects", family_id),
        "detail_href": _detail_href(family_id),
    }


def _safe_doc_items(docs: Any, *, limit: int = 12) -> list[dict[str, Any]]:
    if not isinstance(docs, Mapping):
        return []
    rows: list[dict[str, Any]] = []
    for index, doc in enumerate(docs.get("docs") or [], start=1):
        if not isinstance(doc, Mapping):
            continue
        rel_path = _safe_text(doc.get("rel_path"), f"doc-{index}")
        rows.append(
            {
                "title": _safe_text(doc.get("title"), rel_path),
                "rel_path": rel_path,
                "kind": _safe_text(doc.get("kind"), "doc"),
                "extension": _safe_text(doc.get("extension")),
                "primary": bool(doc.get("primary")),
                "reference": bool(doc.get("reference")),
                "bytes": _as_int(doc.get("bytes")),
            }
        )
        if len(rows) >= limit:
            break
    return rows


def _safe_version_detail(version: Mapping[str, Any], *, workspace_id: str, domain_id: str, family_id: str) -> dict[str, Any]:
    row = _safe_version(version, workspace_id=workspace_id, domain_id=domain_id, family_id=family_id)
    docs = version.get("docs") if isinstance(version.get("docs"), Mapping) else {}
    launch = version.get("launch") if isinstance(version.get("launch"), Mapping) else {}
    row["docs"]["items"] = _safe_doc_items(docs)
    row["launch"] = {
        "status": _safe_text(launch.get("status")),
        "framework": _safe_text(launch.get("framework")),
        "mode": _safe_text(launch.get("mode")),
        "requires_local_machine": bool(launch.get("requires_local_machine", True)) if launch else False,
        "managed_window_stops_server": bool(launch.get("managed_window_stops_server")) if launch else False,
    }
    return row


def _safe_file_sample(items: Any, *, limit: int = 12) -> list[str]:
    if not isinstance(items, list):
        return []
    rows: list[str] = []
    for item in items:
        text = _safe_text(item)
        if text and text != "redacted_local_ref":
            rows.append(text)
        if len(rows) >= limit:
            break
    return rows


def _safe_diff(
    diff: Mapping[str, Any],
    *,
    workspace_id: str,
    domain_id: str,
    family_id: str,
    project_to_version: Mapping[str, str],
    index: int,
) -> dict[str, Any]:
    diff_id = _compact(diff.get("diff_id"), f"diff-{index}")
    file_diff = diff.get("file_diff") if isinstance(diff.get("file_diff"), Mapping) else {}
    from_project_id = _safe_text(diff.get("from_project_id"))
    to_project_id = _safe_text(diff.get("to_project_id"))
    return {
        "diff_id": diff_id,
        "status": _safe_text(diff.get("status"), _safe_text(file_diff.get("status"), "candidate_diff_manifest")),
        "from_project_id": from_project_id,
        "to_project_id": to_project_id,
        "from_label": _safe_text(diff.get("from_label")),
        "to_label": _safe_text(diff.get("to_label")),
        "from_version": _safe_text(diff.get("from_version"), project_to_version.get(from_project_id, "")),
        "to_version": _safe_text(diff.get("to_version"), project_to_version.get(to_project_id, "")),
        "from_branch": _safe_text(diff.get("from_branch")),
        "to_branch": _safe_text(diff.get("to_branch")),
        "added_count": _as_int(file_diff.get("added_count")),
        "changed_count": _as_int(file_diff.get("changed_count")),
        "removed_count": _as_int(file_diff.get("removed_count")),
        "current_file_count": _as_int(file_diff.get("current_file_count")),
        "previous_file_count": _as_int(file_diff.get("previous_file_count")),
        "truncated": bool(file_diff.get("truncated")),
        "added_sample": _safe_file_sample(file_diff.get("added_sample")),
        "changed_sample": _safe_file_sample(file_diff.get("changed_sample")),
        "removed_sample": _safe_file_sample(file_diff.get("removed_sample")),
        "copy_policy": _safe_text(diff.get("copy_policy")),
        "virtual_path": f"{_virtual_path(workspace_id, 'domains', domain_id, 'projects', family_id)}/diffs/{_slug(diff_id, f'diff-{index}')}",
    }


def _find_family(manifest: Mapping[str, Any], family_id: str) -> Mapping[str, Any] | None:
    for family in manifest.get("families") or []:
        if isinstance(family, Mapping) and _compact(family.get("family_id")) == family_id:
            return family
    return None


def _safe_workbench_summary(workbench_summary: Any) -> dict[str, Any]:
    if not isinstance(workbench_summary, Mapping) or not workbench_summary.get("ok"):
        return {}
    project = workbench_summary.get("project") if isinstance(workbench_summary.get("project"), Mapping) else {}
    preview = workbench_summary.get("preview") if isinstance(workbench_summary.get("preview"), Mapping) else {}
    history_counts = workbench_summary.get("history_counts") if isinstance(workbench_summary.get("history_counts"), Mapping) else {}
    action = (
        workbench_summary.get("next_recommended_safe_action")
        if isinstance(workbench_summary.get("next_recommended_safe_action"), Mapping)
        else {}
    )
    return {
        "schema_id": _safe_text(workbench_summary.get("schema_id")),
        "project_id": _safe_text(workbench_summary.get("project_id")),
        "label": _safe_text(project.get("label")),
        "preview_status": _safe_text(preview.get("status"), _safe_text(workbench_summary.get("session", {}).get("preview_status") if isinstance(workbench_summary.get("session"), Mapping) else "")),
        "preview_public_path": _safe_public_route(project.get("preview_public_path")),
        "history_counts": {
            "patch_receipt_count": _as_int(history_counts.get("patch_receipt_count")),
            "browser_capture_count": _as_int(history_counts.get("browser_capture_count")),
            "rollback_candidate_count": _as_int(history_counts.get("rollback_candidate_count")),
        },
        "next_recommended_safe_action": {
            "action_id": _safe_text(action.get("action_id")),
            "label": _safe_text(action.get("label")),
            "reason": _safe_text(action.get("reason")),
        },
        "public_preview_allowed": bool(workbench_summary.get("public_preview_allowed")),
        "mutations_require_cockpit_auth": bool(workbench_summary.get("mutations_require_cockpit_auth", True)),
        "write_confirmation_required": bool(workbench_summary.get("write_confirmation_required", True)),
    }


def _preview_capability_for_family(
    family: Mapping[str, Any],
    *,
    workbench_project_id: str = "",
    workbench_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    safe_workbench = _safe_workbench_summary(workbench_summary)
    if workbench_project_id:
        preview_href = _safe_public_route(
            safe_workbench.get("preview_public_path"),
            WORKBENCH_PROJECT_ROUTES.get(workbench_project_id, "/projects"),
        )
        return {
            "capability": "embedded_workbench",
            "label": "Registered workbench preview",
            "state": "ready" if safe_workbench else "registered",
            "workbench_project_id": workbench_project_id,
            "preview_href": preview_href,
            "embed_src": _safe_public_route(WORKBENCH_PROJECT_EMBEDS.get(workbench_project_id)),
            "launchable": _as_int(family.get("launchable_count")) > 0,
            "requires_auth_for_mutation": True,
            "action_href": "/cockpit/projects/launch/start",
            "summary": "Live preview is embedded when a registered workbench route exists; patch, build, launch, capture, and rollback mutations remain cockpit-auth gated.",
        }
    if _as_int(family.get("launchable_count")) > 0:
        return {
            "capability": "managed_launch",
            "label": "Managed launch candidate",
            "state": "auth_gated",
            "workbench_project_id": "",
            "preview_href": "/cockpit#projects",
            "embed_src": "",
            "launchable": True,
            "requires_auth_for_mutation": True,
            "action_href": "/cockpit/projects/launch/start",
            "summary": "This family has launch metadata; starting, stopping, diagnostics, and screenshots stay behind cockpit authentication.",
        }
    return {
        "capability": "catalog_only",
        "label": "Catalog and canon only",
        "state": "read_only",
        "workbench_project_id": "",
        "preview_href": "",
        "embed_src": "",
        "launchable": False,
        "requires_auth_for_mutation": True,
        "action_href": "",
        "summary": "This family is organized for identity, docs, lineage, and planning until a launch or workbench path is attached.",
    }


def _proof_ladder(
    family: Mapping[str, Any],
    *,
    version_count: int,
    diff_count: int,
    doc_count: int,
    workbench_summary: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    safe_workbench = _safe_workbench_summary(workbench_summary)
    history_counts = safe_workbench.get("history_counts") if isinstance(safe_workbench.get("history_counts"), Mapping) else {}
    browser_capture_count = _as_int(history_counts.get("browser_capture_count"))
    rollback_candidate_count = _as_int(history_counts.get("rollback_candidate_count"))
    launchable_count = _as_int(family.get("launchable_count"))

    def row(proof_id: str, label: str, status: str, evidence: str) -> dict[str, Any]:
        return {
            "proof_id": proof_id,
            "label": label,
            "status": status,
            "evidence": evidence,
        }

    return [
        row(
            "source_canon",
            "Source canon",
            "pass" if _compact(family.get("lineage_status")) else "watch",
            _safe_text(family.get("lineage_status"), "family registered"),
        ),
        row(
            "version_lineage",
            "Version lineage",
            "pass" if version_count > 1 and diff_count > 0 else "watch",
            f"{version_count} versions / {diff_count} diffs",
        ),
        row(
            "docs_bound",
            "Docs bound",
            "pass" if doc_count > 0 else "watch",
            f"{doc_count} docs",
        ),
        row(
            "preview_launch",
            "Preview or launch",
            "pass" if launchable_count > 0 or safe_workbench else "watch",
            "workbench registered" if safe_workbench else f"{launchable_count} launchable versions",
        ),
        row(
            "visual_capture",
            "Visual capture",
            "pass" if browser_capture_count > 0 else "watch",
            f"{browser_capture_count} browser captures",
        ),
        row(
            "rollback_lane",
            "Rollback lane",
            "pass" if rollback_candidate_count > 0 else "watch",
            f"{rollback_candidate_count} rollback candidates",
        ),
    ]


def _audience_lenses(family: Mapping[str, Any], preview_capability: Mapping[str, Any]) -> list[dict[str, Any]]:
    label = _compact(family.get("label"), _compact(family.get("family_id"), "Project family"))
    return [
        {
            "lens_id": "vibe_coder",
            "label": "Vibe coder",
            "wants": "what it is, whether it launches, how it looks, and what to touch next",
            "surface": f"{label}: {_safe_text(preview_capability.get('label'))}",
        },
        {
            "lens_id": "developer",
            "label": "Developer",
            "wants": "versions, diffs, docs, stack, launch metadata, proof, and rollback posture",
            "surface": f"{_as_int(family.get('version_count'))} versions / {_as_int(family.get('diff_count'))} diffs / {_as_int(family.get('doc_count'))} docs",
        },
        {
            "lens_id": "ion_agents",
            "label": "ION agents",
            "wants": "context capsule continuity, authority boundary, proof ladder, future packets, and safe next actions",
            "surface": "candidate/projected state only; cockpit auth gates all mutation lanes",
        },
    ]


def _future_lanes(family: Mapping[str, Any]) -> list[dict[str, Any]]:
    ops = family.get("operating_system") if isinstance(family.get("operating_system"), Mapping) else {}
    rows: list[dict[str, Any]] = []
    for lane in ops.get("maintenance_lanes") or []:
        if not isinstance(lane, Mapping):
            continue
        rows.append(
            {
                "lane_id": _safe_text(lane.get("lane_id"), f"lane-{len(rows) + 1}"),
                "label": _safe_text(lane.get("label"), "Maintenance Lane"),
                "objective": _safe_text(lane.get("objective")),
                "status": _safe_text(lane.get("status"), "watch"),
                "next_action": _safe_text(lane.get("next_action")),
            }
        )
        if len(rows) >= 8:
            break
    if rows:
        return rows
    return [
        {
            "lane_id": "stabilize",
            "label": "Stabilize",
            "objective": "Keep the current source, launch posture, and docs attached to this family.",
            "status": "watch",
            "next_action": "capture proof or attach a workbench route",
        },
        {
            "lane_id": "canonize",
            "label": "Canonize",
            "objective": "Keep versions, diffs, context capsules, and future plans visible from this page.",
            "status": "ready",
            "next_action": "review lineage and future goals",
        },
    ]


def build_helixion_project_family_detail_model(
    manifest: Mapping[str, Any],
    family_id: str,
    *,
    workspace_id: str = "wsp_local_operator",
    rank: str | HelixionRankCeiling = HelixionRankCeiling.VIEWER_CLIENT,
    max_versions: int = 24,
    max_diffs: int = 24,
    workbench_project_id: str = "",
    workbench_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a redacted family detail model for the Helixion Projects surface."""

    family = _find_family(manifest, family_id)
    if family is None:
        raise KeyError(f"unknown project family: {family_id}")
    domain_id = _compact(family.get("domain_id"), "tools-generated-apps")
    versions = [item for item in (family.get("versions") or []) if isinstance(item, Mapping)]
    current_version = next((item for item in versions if item.get("is_current")), versions[-1] if versions else {})
    safe_versions = [
        _safe_version_detail(version, workspace_id=workspace_id, domain_id=domain_id, family_id=family_id)
        for version in versions[: max(1, max_versions)]
    ]
    if current_version and all(item["version_id"] != _compact(current_version.get("version_id")) for item in safe_versions):
        safe_versions.insert(0, _safe_version_detail(current_version, workspace_id=workspace_id, domain_id=domain_id, family_id=family_id))
    project_to_version = {
        _compact(version.get("project_id")): _compact(version.get("version_id"))
        for version in versions
        if _compact(version.get("project_id"))
    }
    safe_diffs = [
        _safe_diff(
            diff,
            workspace_id=workspace_id,
            domain_id=domain_id,
            family_id=family_id,
            project_to_version=project_to_version,
            index=index,
        )
        for index, diff in enumerate((family.get("diffs") or [])[: max(1, max_diffs)], start=1)
        if isinstance(diff, Mapping)
    ]
    preview_capability = _preview_capability_for_family(
        family,
        workbench_project_id=workbench_project_id,
        workbench_summary=workbench_summary,
    )
    safe_family = _safe_family(family, workspace_id=workspace_id, max_versions_per_family=min(max_versions, 8))
    safe_family["versions"] = safe_versions[: max(1, max_versions)]
    safe_family["current"] = (
        _safe_version_detail(current_version, workspace_id=workspace_id, domain_id=domain_id, family_id=family_id)
        if isinstance(current_version, Mapping) and current_version
        else {}
    )
    safe_workbench = _safe_workbench_summary(workbench_summary)
    proof_ladder = _proof_ladder(
        family,
        version_count=len(versions),
        diff_count=len(safe_diffs),
        doc_count=_as_int(family.get("doc_count")),
        workbench_summary=workbench_summary,
    )
    return {
        "schema_id": FAMILY_DETAIL_SCHEMA_ID,
        "generated_at": _utc_now(),
        "workspace_id": workspace_id,
        "rank_ceiling": str(normalize_rank(rank)),
        "source_schema_id": _compact(manifest.get("schema_id")),
        "source_generated_at": _compact(manifest.get("generated_at")),
        "family": safe_family,
        "versions": safe_versions[: max(1, max_versions)],
        "diffs": safe_diffs,
        "docs_health": safe_family.get("docs", {}),
        "operating_system": safe_family.get("operating_system", {}),
        "preview_capability": preview_capability,
        "workbench_summary": safe_workbench,
        "proof_ladder": proof_ladder,
        "proof_summary": {
            "pass_count": len([item for item in proof_ladder if item.get("status") == "pass"]),
            "watch_count": len([item for item in proof_ladder if item.get("status") != "pass"]),
        },
        "audience_lenses": _audience_lenses(family, preview_capability),
        "context_capsule_lane": {
            "schema_id": "ion.project_context_capsule_lane.v0_1",
            "label": "Context Capsule Lane",
            "contract": "Family identity, version lineage, diffs, docs, proof, and future plans are preserved as a recoverable project-management capsule.",
            "handoff_targets": ["project_curator", "build_runner", "proof_reviewer", "context_librarian", "operator_steward"],
            "authority": dict(AUTHORITY_FALSE),
        },
        "future_plan_lanes": _future_lanes(family),
        "project_canon_contract": {
            "address_space": "ion://workspace virtual paths",
            "local_path_policy": "absolute local refs remain redacted from this family detail",
            "preview_rule": "preview is visible when registered; launch, patch, capture, stop, and rollback mutations require cockpit auth",
            "authority": dict(AUTHORITY_FALSE),
        },
        "authority": dict(AUTHORITY_FALSE),
    }


def _same_path(left: Any, right: Path) -> bool:
    text = _compact(left)
    if not text or text.startswith(("ion://", "file://")):
        return False
    try:
        return Path(text).expanduser().resolve() == right
    except Exception:
        return False


def _infer_workbench_project_for_family(root: Path, family: Mapping[str, Any]) -> str:
    try:
        from .ion_project_workbench import project_specs
    except Exception:
        return ""
    try:
        specs = project_specs(root)
    except Exception:
        return ""
    candidate_paths = [_compact(family.get("current_path"))]
    for version in family.get("versions") or []:
        if isinstance(version, Mapping):
            candidate_paths.append(_compact(version.get("path")))
    for project_id, spec in specs.items():
        if project_id not in WORKBENCH_PROJECT_ROUTES:
            continue
        if project_id == "ion_dev":
            if any(_same_path(path, spec.root) for path in candidate_paths):
                return project_id
            continue
        if any(_same_path(path, spec.root) for path in candidate_paths):
            return project_id
    return ""


def build_helixion_project_family_detail_model_from_file(
    root: str | Path = ".",
    family_id: str = "",
    *,
    manifest_path: str | Path | None = None,
    workspace_id: str = "wsp_local_operator",
    rank: str | HelixionRankCeiling = HelixionRankCeiling.VIEWER_CLIENT,
    max_versions: int = 24,
    max_diffs: int = 24,
) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    path, manifest = _load_project_portfolio_manifest(shell_root, manifest_path=manifest_path)
    family = _find_family(manifest, family_id)
    if family is None:
        raise KeyError(f"unknown project family: {family_id}")
    workbench_project_id = _infer_workbench_project_for_family(shell_root, family)
    workbench_summary: Mapping[str, Any] | None = None
    if workbench_project_id:
        try:
            from .ion_project_workbench import build_project_workbench_timeline

            workbench_summary = build_project_workbench_timeline(
                shell_root,
                project_id=workbench_project_id,
                probe_preview=False,
                max_items=6,
            )
        except Exception:
            workbench_summary = None
    model = build_helixion_project_family_detail_model(
        manifest,
        family_id,
        workspace_id=workspace_id,
        rank=rank,
        max_versions=max_versions,
        max_diffs=max_diffs,
        workbench_project_id=workbench_project_id,
        workbench_summary=workbench_summary,
    )
    model["source_manifest"] = {
        "virtual_path": _virtual_path(workspace_id, "context", "project-portfolio", "manifest"),
        "canonical_ref_sha256": _hash_ref(path.as_posix()),
        "canonical_ref_redacted": True,
    }
    return model


def build_helixion_projects_surface_model(
    manifest: Mapping[str, Any],
    *,
    workspace_id: str = "wsp_local_operator",
    rank: str | HelixionRankCeiling = HelixionRankCeiling.VIEWER_CLIENT,
    max_docs_per_version: int | None = 2,
    max_domains: int = 12,
    max_families: int = 24,
    max_versions_per_family: int = 4,
) -> dict[str, Any]:
    """Build the redacted UI canon for Helixion's project system."""

    inventory = build_project_access_inventory(
        manifest,
        workspace_id=workspace_id,
        max_docs_per_version=max_docs_per_version,
    )
    redacted_inventory = redact_project_access_inventory_for_rank(inventory, rank)
    visible_objects = [item for item in redacted_inventory.get("objects") or [] if isinstance(item, Mapping)]
    domains = [_safe_domain(item) for item in (manifest.get("canonical_domains") or []) if isinstance(item, Mapping)]
    domains = sorted(domains, key=lambda item: (item.get("sort_order") or 999, item.get("label") or ""))[:max_domains]
    families = [item for item in (manifest.get("families") or []) if isinstance(item, Mapping)]
    featured = sorted(families, key=_family_score, reverse=True)[:max_families]

    return {
        "schema_id": SURFACE_SCHEMA_ID,
        "generated_at": _utc_now(),
        "workspace_id": workspace_id,
        "rank_ceiling": str(normalize_rank(rank)),
        "source_schema_id": _compact(manifest.get("schema_id")),
        "source_generated_at": _compact(manifest.get("generated_at")),
        "portfolio_summary": _safe_count_summary(manifest.get("summary") if isinstance(manifest.get("summary"), Mapping) else {}),
        "access_summary": {
            "path_inspection_allowed": bool(redacted_inventory.get("path_inspection_allowed")),
            "visible_object_count": _as_int(redacted_inventory.get("object_count")),
            "hidden_object_count": _as_int(redacted_inventory.get("hidden_object_count")),
            "visible_by_type": _visible_object_counts(visible_objects, "object_type"),
            "visible_by_sensitivity": _visible_object_counts(visible_objects, "sensitivity"),
        },
        "canonical_domains": domains,
        "featured_families": [
            _safe_family(family, workspace_id=workspace_id, max_versions_per_family=max_versions_per_family) for family in featured
        ],
        "project_canon_contract": {
            "address_space": "ion://workspace virtual paths",
            "local_path_policy": "absolute local refs remain redacted from viewer surfaces",
            "organization_rule": "domains own families; families own versions, docs, diffs, launch proof, risks, and future actions",
            "management_rule": "project state is visibility/candidate-state unless a separate proof-bearing authority gate promotes it",
            "authority": dict(AUTHORITY_FALSE),
        },
        "agent_operating_model": [
            {
                "role_id": "project_curator",
                "label": "Project Curator",
                "responsibility": "domain placement, family identity, source canon, duplicate reduction, and lineage shape",
            },
            {
                "role_id": "build_runner",
                "label": "Build Runner",
                "responsibility": "managed local launches, dependency repair posture, diagnostics, stop controls, and runtime notes",
            },
            {
                "role_id": "proof_reviewer",
                "label": "Proof Reviewer",
                "responsibility": "screenshots, runtime proof, quality gates, visual regressions, and evidence labels",
            },
            {
                "role_id": "context_librarian",
                "label": "Context Librarian",
                "responsibility": "context capsules, handoff packets, docs coverage, receipts, and recoverable continuity",
            },
            {
                "role_id": "operator_steward",
                "label": "Operator Steward",
                "responsibility": "review decisions, quarantine/promote intent, future goals, and authority boundaries",
            },
        ],
        "timeline_axes": [
            {"axis_id": "version_lineage", "label": "Version lineage", "unit": "family version plus adjacent diff"},
            {"axis_id": "build_proof", "label": "Build proof", "unit": "launch, capture, diagnostic, and stop receipt"},
            {"axis_id": "context_capsule", "label": "Context capsule", "unit": "capsule, mini, status, handoff, and next packet"},
            {"axis_id": "docs_canon", "label": "Docs canon", "unit": "overview, architecture, runbook, references, decisions"},
            {"axis_id": "future_plan", "label": "Future plan", "unit": "goal, risk, next action, milestone, and review cadence"},
        ],
        "future_plan_lanes": [
            {
                "lane_id": "intake",
                "label": "Intake",
                "goal": "discover roots, classify domains, and preserve source authority without promoting copies blindly",
            },
            {
                "lane_id": "stabilize",
                "label": "Stabilize",
                "goal": "select current source, repair launch path, and mark legacy folders as lineage or archive evidence",
            },
            {
                "lane_id": "verify",
                "label": "Verify",
                "goal": "bind screenshots, runtime proof, docs, receipts, and operator observations to exact versions",
            },
            {
                "lane_id": "canonize",
                "label": "Canonize",
                "goal": "make project identity, goals, plans, context, and management state visible from one surface",
            },
            {
                "lane_id": "maintain",
                "label": "Maintain",
                "goal": "keep recurring triage, lineage review, release review, and reference hygiene attached to each family",
            },
        ],
        "authority": dict(AUTHORITY_FALSE),
    }


def build_helixion_projects_surface_model_from_file(
    root: str | Path = ".",
    *,
    manifest_path: str | Path | None = None,
    workspace_id: str = "wsp_local_operator",
    rank: str | HelixionRankCeiling = HelixionRankCeiling.VIEWER_CLIENT,
    max_docs_per_version: int | None = 2,
    max_domains: int = 12,
    max_families: int = 24,
    max_versions_per_family: int = 4,
) -> dict[str, Any]:
    path, manifest = _load_project_portfolio_manifest(root, manifest_path=manifest_path)
    model = build_helixion_projects_surface_model(
        manifest,
        workspace_id=workspace_id,
        rank=rank,
        max_docs_per_version=max_docs_per_version,
        max_domains=max_domains,
        max_families=max_families,
        max_versions_per_family=max_versions_per_family,
    )
    model["source_manifest"] = {
        "virtual_path": _virtual_path(workspace_id, "context", "project-portfolio", "manifest"),
        "canonical_ref_sha256": _hash_ref(path.as_posix()),
        "canonical_ref_redacted": True,
    }
    return model
