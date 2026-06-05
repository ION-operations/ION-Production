"""Project Cockpit managed candidate-state lane.

This module keeps the cockpit's project, mission, blocker, question, and
timeline state in a narrow local ledger. It is intentionally not accepted ION
state: writes are candidate cockpit state plus receipts only.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

from .ion_project_launcher import PROJECT_LOCAL_LAUNCH_CONFIRMATION, build_project_launcher_status
from .ion_project_canon_dossier import DOSSIER_INDEX
from .ion_project_specialist_context import SPECIALIST_INDEX
from .ion_project_portfolio import (
    PORTFOLIO_MANIFEST,
    build_project_portfolio_model,
    default_application_dev_root,
    default_cosmos_project_root,
    default_cosmos_workspace_root,
    default_materialized_root,
)


CURRENT = Path("ION/05_context/current")
PROJECT_COCKPIT_DIR = CURRENT / "project_cockpit"
PROJECT_COCKPIT_LEDGER = PROJECT_COCKPIT_DIR / "PROJECT_COCKPIT_LEDGER.json"
PROJECT_COCKPIT_RECEIPTS_DIR = PROJECT_COCKPIT_DIR / "receipts"
PROJECT_COCKPIT_WRITE_CONFIRMATION = "ION_PROJECT_COCKPIT_WRITE_CONFIRMED"
DEFAULT_APPLICATION_DEV_LAUNCHER_URL = "http://127.0.0.1:5199"

SCHEMA_ID = "ion.project_cockpit_ledger.v1"
PROJECTION_SCHEMA_ID = "ion.project_cockpit_projection.v1"
RECEIPT_SCHEMA_ID = "ion.project_cockpit_action_receipt.v1"
DEFAULT_PROJECT_ID = "ion_vnext"

_SAFE_ID_RE = re.compile(r"[^a-z0-9]+")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def compact(value: Any, fallback: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    return fallback


def listify(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if value is None:
        return []
    return [value]


def string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        raw = [item.strip() for item in value.split(",")]
    else:
        raw = [compact(item) for item in listify(value)]
    return [item for item in raw if item]


def read_json(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception as exc:  # pragma: no cover - defensive projection
        return {"_read_error": exc.__class__.__name__, "_path": path.as_posix()}


def load_project_cockpit_ledger(root: str | Path = ".") -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    payload = read_json(shell_root / PROJECT_COCKPIT_LEDGER)
    ledger = _default_ledger()
    if payload:
        for key in ("schema_id", "created_at", "updated_at"):
            if payload.get(key):
                ledger[key] = payload[key]
        for key in ("projects", "missions", "blockers", "questions", "timeline_events"):
            ledger[key] = [item for item in listify(payload.get(key)) if isinstance(item, Mapping)]
    return ledger


def _project_portfolio_for_cockpit(shell_root: Path) -> tuple[dict[str, Any], str]:
    manifest = read_json(shell_root / PORTFOLIO_MANIFEST)
    if manifest.get("schema_id") == "ion.project_portfolio.v1":
        portfolio = dict(manifest)
        portfolio.setdefault("status", "project_portfolio_ready")
        portfolio["load_mode"] = "cached_manifest"
        return _compact_project_portfolio_for_cockpit(portfolio), "cached_manifest"
    portfolio = build_project_portfolio_model(shell_root)
    if isinstance(portfolio, Mapping):
        model = dict(portfolio)
        model["load_mode"] = "fresh_scan"
        return _compact_project_portfolio_for_cockpit(model), "fresh_scan"
    return {}, "missing"


def _pick_mapping(item: Mapping[str, Any], keys: list[str]) -> dict[str, Any]:
    return {key: item[key] for key in keys if key in item and item[key] not in (None, "", [], {})}


def _compact_docs(docs: Any) -> dict[str, Any]:
    if not isinstance(docs, Mapping):
        return {}
    result = _pick_mapping(
        docs,
        [
            "doc_count",
            "reference_count",
            "documented_family_count",
            "coverage",
            "recommended_sections",
            "top_docs",
            "primary_docs",
            "docs",
            "references",
            "target_docs",
        ],
    )
    for key, limit in (
        ("top_docs", 10),
        ("primary_docs", 8),
        ("docs", 8),
        ("references", 8),
        ("target_docs", 8),
    ):
        result[key] = [_compact_doc_row(row) for row in listify(result.get(key))[:limit] if isinstance(row, Mapping)]
    if not result.get("top_docs"):
        result.pop("top_docs", None)
    if not result.get("primary_docs"):
        result.pop("primary_docs", None)
    if not result.get("docs"):
        result.pop("docs", None)
    if not result.get("references"):
        result.pop("references", None)
    if not result.get("target_docs"):
        result.pop("target_docs", None)
    return result


def _compact_doc_row(row: Mapping[str, Any]) -> dict[str, Any]:
    result = _pick_mapping(
        row,
        [
            "kind",
            "primary",
            "title",
            "label",
            "type",
            "detail",
            "path",
            "rel_path",
            "target",
            "status",
            "excerpt",
        ],
    )
    excerpt = result.get("excerpt")
    if isinstance(excerpt, str) and len(excerpt) > 260:
        result["excerpt"] = excerpt[:257].rstrip() + "..."
    return result


def _compact_launch(launch: Any) -> dict[str, Any]:
    if not isinstance(launch, Mapping):
        return {}
    return _pick_mapping(
        launch,
        [
            "launchable",
            "status",
            "framework",
            "project_path",
            "project_id",
            "version_id",
            "label",
            "action_path",
            "install_repair_on_launch",
            "managed_window_stops_server",
            "open_href",
            "url",
        ],
    )


def _compact_project_row(project: Any) -> dict[str, Any]:
    if not isinstance(project, Mapping):
        return {}
    result = _pick_mapping(
        project,
        [
            "project_id",
            "source_id",
            "source_label",
            "family_id",
            "group_id",
            "domain_id",
            "domain_label",
            "family_label",
            "label",
            "name",
            "package_version",
            "version_token",
            "date_token",
            "milestone_token",
            "branch_id",
            "branch_label",
            "path",
            "source_root",
            "rel_path",
            "markers",
            "stack",
            "launchable",
            "scripts",
            "load",
            "has_git",
            "status",
        ],
    )
    launch = _compact_launch(project.get("launch"))
    if launch:
        result["launch"] = launch
    return result


def _compact_version(version: Any) -> dict[str, Any]:
    if not isinstance(version, Mapping):
        return {}
    result = _pick_mapping(
        version,
        [
            "version_id",
            "project_id",
            "label",
            "display_label",
            "sequence_label",
            "version_token",
            "date_token",
            "milestone_token",
            "branch_id",
            "branch_label",
            "path",
            "stack",
            "launchable",
            "is_current",
            "load",
        ],
    )
    launch = _compact_launch(version.get("launch"))
    if launch:
        result["launch"] = launch
    docs = _compact_docs(version.get("docs"))
    if docs:
        result["docs"] = docs
    return result


def _compact_diff(diff: Any) -> dict[str, Any]:
    if not isinstance(diff, Mapping):
        return {}
    result = _pick_mapping(
        diff,
        [
            "diff_id",
            "from_project_id",
            "to_project_id",
            "from_path",
            "to_path",
            "from_version",
            "to_version",
            "from_label",
            "to_label",
            "from_branch",
            "to_branch",
            "status",
            "copy_policy",
            "manifest_path",
        ],
    )
    file_diff = diff.get("file_diff")
    if isinstance(file_diff, Mapping):
        compact_file_diff = _pick_mapping(
            file_diff,
            [
                "status",
                "added_count",
                "removed_count",
                "changed_count",
                "previous_file_count",
                "current_file_count",
                "truncated",
            ],
        )
        for key in ("added_sample", "removed_sample", "changed_sample"):
            compact_file_diff[key] = string_list(file_diff.get(key))[:18]
            if not compact_file_diff[key]:
                compact_file_diff.pop(key, None)
        result["file_diff"] = compact_file_diff
    return result


def _compact_family(family: Any) -> dict[str, Any]:
    if not isinstance(family, Mapping):
        return {}
    result = _pick_mapping(
        family,
        [
            "family_id",
            "group_id",
            "domain_id",
            "domain_label",
            "label",
            "source_ids",
            "workspace_dir_count",
            "project_count",
            "version_count",
            "branch_count",
            "diff_count",
            "launchable_count",
            "doc_count",
            "reference_count",
            "current_project_id",
            "current_path",
            "organized_path",
            "lineage_status",
            "materialization_plan",
            "operating_system",
        ],
    )
    current = _compact_project_row(family.get("current"))
    if current:
        result["current"] = current
    result["versions"] = [_compact_version(version) for version in listify(family.get("versions")) if isinstance(version, Mapping)]
    result["branches"] = [
        _pick_mapping(branch, ["branch_id", "label", "version_count", "launchable_count"])
        for branch in listify(family.get("branches"))
        if isinstance(branch, Mapping)
    ]
    result["diffs"] = [_compact_diff(diff) for diff in listify(family.get("diffs")) if isinstance(diff, Mapping)]
    docs = _compact_docs(family.get("docs"))
    if docs:
        result["docs"] = docs
    return result


def _compact_domain(domain: Any) -> dict[str, Any]:
    if not isinstance(domain, Mapping):
        return {}
    result = _pick_mapping(
        domain,
        [
            "domain_id",
            "group_id",
            "label",
            "summary",
            "folder",
            "sort_order",
            "family_count",
            "project_count",
            "version_count",
            "branch_count",
            "diff_count",
            "launchable_count",
            "doc_count",
            "reference_count",
            "documented_family_count",
            "operating_system",
            "versioned_family_count",
        ],
    )
    result["families"] = [
        _pick_mapping(
            family,
            [
                "family_id",
                "label",
                "version_count",
                "branch_count",
                "diff_count",
                "project_count",
                "launchable_count",
                "doc_count",
                "reference_count",
                "ops_posture",
                "ops_score",
                "current_path",
            ],
        )
        for family in listify(domain.get("families"))
        if isinstance(family, Mapping)
    ]
    docs = _compact_docs(domain.get("docs"))
    if docs:
        result["docs"] = docs
    return result


def _compact_project_portfolio_for_cockpit(portfolio: Mapping[str, Any]) -> dict[str, Any]:
    result = _pick_mapping(
        portfolio,
        [
            "schema_id",
            "generated_at",
            "status",
            "load_mode",
            "source_roots",
            "source_present",
            "organizer",
            "summary",
            "groups",
            "recommendations",
        ],
    )
    result["canonical_domains"] = [_compact_domain(domain) for domain in listify(portfolio.get("canonical_domains")) if isinstance(domain, Mapping)]
    result["families"] = [_compact_family(family) for family in listify(portfolio.get("families")) if isinstance(family, Mapping)]
    result["projects"] = [_compact_project_row(project) for project in listify(portfolio.get("projects")) if isinstance(project, Mapping)]
    result["duplicate_clusters"] = [
        {
            **_pick_mapping(cluster, ["cluster_id", "family_id", "label", "count", "recommendation"]),
            "paths": string_list(cluster.get("paths"))[:12],
        }
        for cluster in listify(portfolio.get("duplicate_clusters"))
        if isinstance(cluster, Mapping)
    ]
    return result


def _portfolio_organization_state(shell_root: Path, portfolio: Mapping[str, Any], load_mode: str) -> dict[str, Any]:
    summary = portfolio.get("summary") if isinstance(portfolio.get("summary"), Mapping) else {}
    organizer = portfolio.get("organizer") if isinstance(portfolio.get("organizer"), Mapping) else {}
    latest_receipt = organizer.get("latest_materialization_receipt") if isinstance(organizer.get("latest_materialization_receipt"), Mapping) else {}
    materialized_root = compact(organizer.get("materialized_root"), default_materialized_root(shell_root).as_posix())
    materialized_present = bool(
        organizer.get("materialized_present")
        or summary.get("materialized_present")
        or (materialized_root and Path(materialized_root).exists())
    )
    diff_manifest_count = 0
    for family in listify(portfolio.get("families")):
        if isinstance(family, Mapping):
            diff_manifest_count += int(family.get("diff_count") or len(listify(family.get("diffs"))))
    dossier_index_path = shell_root / DOSSIER_INDEX
    dossier_index = read_json(dossier_index_path)
    dossier_summary = dossier_index.get("summary") if isinstance(dossier_index.get("summary"), Mapping) else {}
    specialist_index_path = shell_root / SPECIALIST_INDEX
    specialist_index = read_json(specialist_index_path)
    specialist_summary = specialist_index.get("summary") if isinstance(specialist_index.get("summary"), Mapping) else {}
    return {
        "status": "materialized" if materialized_present else ("manifest_ready" if portfolio else "missing"),
        "load_mode": load_mode,
        "candidate_only": True,
        "materialized_present": materialized_present,
        "materialized_root": materialized_root,
        "manifest_path": (shell_root / PORTFOLIO_MANIFEST).as_posix(),
        "latest_receipt": dict(latest_receipt) if isinstance(latest_receipt, Mapping) else {},
        "source_copy_policy": compact(
            organizer.get("source_copy_policy"),
            "domain/project current source copy only; historical folders stay as lineage pointers and diff manifests",
        ),
        "layout": compact(
            organizer.get("layout"),
            "domains/<domain>/<project>/source/current plus lineage, notes, and screenshots",
        ),
        "copy_count": latest_receipt.get("copy_count", 0) if isinstance(latest_receipt, Mapping) else 0,
        "family_count": summary.get("family_count", 0),
        "project_root_count": summary.get("project_root_count", 0),
        "duplicate_cluster_count": summary.get("duplicate_cluster_count", 0),
        "legacy_copy_cluster_count": summary.get("legacy_copy_cluster_count", 0),
        "versioned_family_count": summary.get("versioned_family_count", 0),
        "diff_manifest_count": diff_manifest_count,
        "canon_dossiers": {
            "status": compact(dossier_index.get("status"), "missing") if dossier_index else "missing",
            "index_path": dossier_index_path.as_posix(),
            "index_relpath": DOSSIER_INDEX.as_posix(),
            "generated_at": compact(dossier_index.get("generated_at")) if dossier_index else "",
            "domain_dossier_count": dossier_summary.get("domain_dossier_count", 0),
            "project_dossier_count": dossier_summary.get("project_dossier_count", 0),
            "mirrored_project_dossier_count": dossier_summary.get("mirrored_project_dossier_count", 0),
        },
        "project_specialists": {
            "status": compact(specialist_index.get("status"), "missing") if specialist_index else "missing",
            "index_path": specialist_index_path.as_posix(),
            "index_relpath": SPECIALIST_INDEX.as_posix(),
            "generated_at": compact(specialist_index.get("generated_at")) if specialist_index else "",
            "domain_specialist_capsule_count": specialist_summary.get("domain_specialist_capsule_count", 0),
            "project_specialist_capsule_count": specialist_summary.get("project_specialist_capsule_count", 0),
            "domain_agent_packet_count": specialist_summary.get("domain_agent_packet_count", 0),
            "project_agent_packet_count": specialist_summary.get("project_agent_packet_count", 0),
            "total_agent_packet_count": specialist_summary.get("total_agent_packet_count", 0),
            "mirrored_domain_context_count": specialist_summary.get("mirrored_domain_context_count", 0),
            "mirrored_project_context_count": specialist_summary.get("mirrored_project_context_count", 0),
            "agent_invocation_status": "prepared_not_invoked" if specialist_index else "missing",
        },
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def build_project_cockpit_model(
    root: str | Path,
    *,
    vnext: Mapping[str, Any] | None = None,
    runtime_timeline: list[dict[str, Any]] | None = None,
    lane_timeline: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    vnext = vnext or {}
    ledger = load_project_cockpit_ledger(shell_root)
    managed_projects = [dict(item) for item in listify(ledger.get("projects")) if isinstance(item, Mapping)]
    managed_missions = [dict(item) for item in listify(ledger.get("missions")) if isinstance(item, Mapping)]
    managed_blockers = [_normalize_record(dict(item), "blocker") for item in listify(ledger.get("blockers")) if isinstance(item, Mapping)]
    managed_questions = [_normalize_record(dict(item), "question") for item in listify(ledger.get("questions")) if isinstance(item, Mapping)]
    projects = _project_rows(managed_projects, vnext, shell_root)
    missions = _mission_rows(managed_missions, vnext)
    derived_blockers = _derived_vnext_blockers(vnext)
    blockers = sorted(
        [*derived_blockers, *managed_blockers],
        key=lambda item: (_status_rank(item.get("status")), _severity_rank(item.get("severity")), compact(item.get("created_at")), compact(item.get("blocker_id"))),
    )
    questions = sorted(
        managed_questions,
        key=lambda item: (_status_rank(item.get("status")), _priority_rank(item.get("priority")), compact(item.get("created_at")), compact(item.get("question_id"))),
    )
    receipt_events, latest_receipts = _project_cockpit_receipt_events(shell_root)
    project_portfolio, portfolio_load_mode = _project_portfolio_for_cockpit(shell_root)
    organization_state = _portfolio_organization_state(shell_root, project_portfolio, portfolio_load_mode)
    launcher_status = build_project_launcher_status(shell_root)
    timeline = _project_timeline(
        ledger=ledger,
        vnext=vnext,
        blockers=blockers,
        questions=questions,
        receipt_events=receipt_events,
        runtime_timeline=runtime_timeline or [],
        lane_timeline=lane_timeline or {},
    )
    return {
        "schema_id": PROJECTION_SCHEMA_ID,
        "generated_at": utc_now(),
        "status": "project_cockpit_ready",
        "selected_project_id": DEFAULT_PROJECT_ID,
        "source_paths": {
            "ledger": PROJECT_COCKPIT_LEDGER.as_posix(),
            "receipts": PROJECT_COCKPIT_RECEIPTS_DIR.as_posix(),
            "vnext_projection": "vnext_mission_control",
            "application_dev_root": _application_dev_root(shell_root).as_posix(),
            "application_dev_launcher": _application_dev_launcher_url() + "/",
            "cosmos_workspace_root": default_cosmos_workspace_root(shell_root).as_posix(),
            "cosmos_root": _cosmos_root(shell_root).as_posix(),
            "project_portfolio_manifest": (shell_root / "ION/05_context/current/project_portfolio/PROJECT_PORTFOLIO_MANIFEST.json").as_posix(),
            "project_portfolio_materialized_root": default_materialized_root(shell_root).as_posix(),
            "project_canon_dossier_index": (shell_root / DOSSIER_INDEX).as_posix(),
            "project_specialist_context_index": (shell_root / SPECIALIST_INDEX).as_posix(),
        },
        "source_present": {
            "ledger": (shell_root / PROJECT_COCKPIT_LEDGER).exists(),
            "receipts": (shell_root / PROJECT_COCKPIT_RECEIPTS_DIR).exists(),
            "vnext_projection": bool(vnext),
            "application_dev_root": _application_dev_root(shell_root).exists(),
            "cosmos_workspace_root": default_cosmos_workspace_root(shell_root).exists(),
            "cosmos_root": _cosmos_root(shell_root).exists(),
            "project_portfolio_manifest": (shell_root / "ION/05_context/current/project_portfolio/PROJECT_PORTFOLIO_MANIFEST.json").exists(),
            "project_portfolio_materialized_root": default_materialized_root(shell_root).exists(),
            "project_canon_dossier_index": (shell_root / DOSSIER_INDEX).exists(),
            "project_specialist_context_index": (shell_root / SPECIALIST_INDEX).exists(),
        },
        "projects": projects,
        "missions": missions,
        "blockers": blockers,
        "questions": questions,
        "timeline_events": timeline,
        "latest_receipts": latest_receipts,
        "portfolio": project_portfolio,
        "portfolio_load_mode": portfolio_load_mode,
        "organization_state": organization_state,
        "launcher": launcher_status,
        "summary": {
            "project_count": len(projects),
            "mission_count": len(missions),
            "blocker_count": len(blockers),
            "open_blocker_count": len([item for item in blockers if _is_open_status(item.get("status"))]),
            "derived_blocker_count": len(derived_blockers),
            "managed_blocker_count": len(managed_blockers),
            "question_count": len(questions),
            "open_question_count": len([item for item in questions if _is_open_status(item.get("status"))]),
            "blocking_question_count": len([item for item in questions if item.get("blocking")]),
            "timeline_event_count": len(timeline),
            "portfolio_project_root_count": project_portfolio.get("summary", {}).get("project_root_count", 0)
            if isinstance(project_portfolio.get("summary"), Mapping)
            else 0,
            "portfolio_family_count": project_portfolio.get("summary", {}).get("family_count", 0)
            if isinstance(project_portfolio.get("summary"), Mapping)
            else 0,
            "portfolio_duplicate_cluster_count": project_portfolio.get("summary", {}).get("duplicate_cluster_count", 0)
            if isinstance(project_portfolio.get("summary"), Mapping)
            else 0,
            "portfolio_versioned_family_count": organization_state.get("versioned_family_count", 0),
            "portfolio_diff_manifest_count": organization_state.get("diff_manifest_count", 0),
            "portfolio_copy_count": organization_state.get("copy_count", 0),
            "portfolio_load_mode": portfolio_load_mode,
        },
        "authority": {
            "candidate_state_write_authority": True,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
            "supabase_mutation_authority": False,
            "codex_queue_dispatch_authority": False,
        },
        "write_confirmation": PROJECT_COCKPIT_WRITE_CONFIRMATION,
        "local_launch_confirmation": PROJECT_LOCAL_LAUNCH_CONFIRMATION,
        "non_claims": [
            "project cockpit ledger is candidate cockpit state",
            "derived vNext blockers close only when source vNext proof gates close",
            "UI actions do not dispatch Codex work",
            "UI actions do not grant accepted-state, production, live-execution, secrets, or Supabase authority",
        ],
    }


def apply_project_cockpit_action(
    root: str | Path,
    *,
    record_type: str,
    action: str,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    if compact(payload.get("confirmation")) != PROJECT_COCKPIT_WRITE_CONFIRMATION:
        return {
            "ok": False,
            "finding": "confirmation_required",
            "required_confirmation": PROJECT_COCKPIT_WRITE_CONFIRMATION,
            "production_authority": False,
            "live_execution_authority": False,
        }
    if record_type not in {"blocker", "question"}:
        return {"ok": False, "finding": "unsupported_record_type", "record_type": record_type}
    if action not in {"create", "update", "resolve"}:
        return {"ok": False, "finding": "unsupported_action", "action": action}

    ledger = load_project_cockpit_ledger(shell_root)
    collection_key = "blockers" if record_type == "blocker" else "questions"
    records = [dict(item) for item in listify(ledger.get(collection_key)) if isinstance(item, Mapping)]
    now = utc_now()
    actor = compact(payload.get("actor"), "operator")

    before: dict[str, Any] | None = None
    after: dict[str, Any]
    if action == "create":
        after = _create_record(record_type, payload, created_at=now, actor=actor)
        if any(_record_id(item, record_type) == _record_id(after, record_type) for item in records):
            return {"ok": False, "finding": "record_already_exists", "record_id": _record_id(after, record_type)}
        records.append(after)
    else:
        requested_id = compact(payload.get(f"{record_type}_id") or payload.get("record_id") or payload.get("id"))
        if not requested_id:
            return {"ok": False, "finding": "record_id_required", "record_type": record_type}
        index = next((idx for idx, item in enumerate(records) if _record_id(item, record_type) == requested_id), -1)
        if index < 0:
            return {"ok": False, "finding": "record_not_found", "record_id": requested_id}
        before = dict(records[index])
        after = _update_record(record_type, before, payload, action=action, updated_at=now, actor=actor)
        records[index] = after

    ledger[collection_key] = records
    ledger["updated_at"] = now
    ledger.setdefault("timeline_events", [])
    event = _ledger_event(record_type, action, after, created_at=now, actor=actor)
    ledger["timeline_events"] = [*listify(ledger.get("timeline_events")), event]
    _write_json(shell_root / PROJECT_COCKPIT_LEDGER, ledger)
    receipt = _write_receipt(
        shell_root,
        {
            "schema_id": RECEIPT_SCHEMA_ID,
            "receipt_id": _receipt_id(record_type, action, after, now),
            "created_at": now,
            "actor": actor,
            "action": action,
            "record_type": record_type,
            "record_id": _record_id(after, record_type),
            "before": before,
            "after": after,
            "timeline_event": event,
            "evidence_refs": string_list(payload.get("evidence_refs")),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
            "supabase_mutation_authority": False,
            "codex_queue_dispatch_authority": False,
        },
    )
    return {
        "ok": True,
        "schema_id": "ion.project_cockpit_action_result.v1",
        "action": action,
        "record_type": record_type,
        "record": after,
        "receipt": receipt,
        "ledger_path": PROJECT_COCKPIT_LEDGER.as_posix(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _default_ledger() -> dict[str, Any]:
    now = utc_now()
    return {
        "schema_id": SCHEMA_ID,
        "created_at": now,
        "updated_at": now,
        "projects": [],
        "missions": [],
        "blockers": [],
        "questions": [],
        "timeline_events": [],
        "authority": {
            "candidate_state_only": True,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    }


def _project_rows(managed_projects: list[dict[str, Any]], vnext: Mapping[str, Any], root: Path) -> list[dict[str, Any]]:
    by_id = {
        **_default_project_rows(root),
    }
    by_id[DEFAULT_PROJECT_ID] = {
        **by_id.get(DEFAULT_PROJECT_ID, {}),
        "project_id": DEFAULT_PROJECT_ID,
        "label": "ION vNext",
        "status": compact(vnext.get("status"), "projected"),
        "summary": compact(vnext.get("mission"), "Clean local-first ION operating layer."),
        "kind": "ion_vnext_rebuild",
        "current_packet": ((vnext.get("current_packet") or {}).get("token") if isinstance(vnext.get("current_packet"), Mapping) else None),
        "source": "derived_vnext_projection",
        "route_hint": "project_cockpit:vnext",
        "route_href": "#projects:vnext",
        "evidence_refs": ["ION_VNEXT/01_canon/WORKSPACE_CANON.yaml", "ION_VNEXT/07_work"],
    }
    for project in managed_projects:
        project_id = compact(project.get("project_id"), DEFAULT_PROJECT_ID)
        by_id[project_id] = {**by_id.get(project_id, {}), **project, "project_id": project_id}
    return sorted(by_id.values(), key=lambda item: (0 if item.get("project_id") == "application_dev" else 1, compact(item.get("label"))))


def _default_project_rows(root: Path) -> dict[str, dict[str, Any]]:
    app_dev_root = _application_dev_root(root)
    cosmos_root = _cosmos_root(root)
    app_counts = _application_dev_counts(app_dev_root)
    launcher_url = _application_dev_launcher_url()
    return {
        "application_dev": {
            "project_id": "application_dev",
            "label": "Application Dev Apps",
            "status": "workspace_ready" if app_dev_root.exists() else "missing",
            "summary": "Local Application_Dev catalog and one-click install-and-launch hub for generated apps.",
            "kind": "application_dev_launcher",
            "path": app_dev_root.as_posix(),
            "exists": app_dev_root.exists(),
            "source": "local_application_dev_workspace",
            "route_hint": "external_local_launcher",
            "route_href": "/projects/application-dev",
            "launcher_url": launcher_url + "/",
            "app_catalog_url": "/projects/application-dev/apps.json",
            "package_root_count": app_counts["package_root_count"],
            "launchable_count": app_counts["launchable_count"],
            "family_count": app_counts["family_count"],
            "evidence_refs": [app_dev_root.as_posix(), "tools/appdev-launcher.mjs"],
        },
        "cosmos": {
            "project_id": "cosmos",
            "label": "Cosmos Water World",
            "status": "registered" if cosmos_root.exists() else "missing",
            "summary": "Helixion project workbench lane with preview, browser capture, patch preview, and rollback receipts.",
            "kind": "helixion_project_workbench",
            "path": cosmos_root.as_posix(),
            "exists": cosmos_root.exists(),
            "source": "project_workbench_registry",
            "route_hint": "project_workbench",
            "route_href": "/projects/cosmos",
            "preview_href": "/projects/cosmos/preview/",
            "evidence_refs": [cosmos_root.as_posix(), "ION/04_packages/kernel/ion_project_workbench.py"],
        },
        "ion_development": {
            "project_id": "ion_development",
            "label": "ION Development",
            "status": "active",
            "summary": "Active local ION root, cockpit, carrier, package, and runtime surfaces.",
            "kind": "active_ion_root",
            "source": "current_shell_root",
            "route_hint": "cockpit",
            "route_href": "#mission",
            "evidence_refs": ["ION/REPO_AUTHORITY.md", "ION/05_context/current/codex_solo/CAPSULE.md"],
        },
    }


def _application_dev_root(root: str | Path | None = None) -> Path:
    return default_application_dev_root(root)


def _application_dev_launcher_url() -> str:
    return (os.environ.get("ION_APPLICATION_DEV_LAUNCHER_URL") or DEFAULT_APPLICATION_DEV_LAUNCHER_URL).rstrip("/")


def _cosmos_root(root: str | Path | None = None) -> Path:
    return default_cosmos_project_root(root)


def _application_dev_counts(root: Path) -> dict[str, int]:
    if not root.exists():
        return {"package_root_count": 0, "launchable_count": 0, "family_count": 0}
    ignored = {".git", ".cache", ".next", ".turbo", "build", "coverage", "dist", "node_modules", "out"}
    package_roots: list[Path] = []
    families: set[str] = set()
    launchable = 0
    try:
        for package_json in root.rglob("package.json"):
            if any(part in ignored for part in package_json.relative_to(root).parts):
                continue
            package_roots.append(package_json.parent)
            rel_parts = package_json.parent.relative_to(root).parts
            if rel_parts:
                families.add(rel_parts[0])
            payload = read_json(package_json)
            scripts = payload.get("scripts") if isinstance(payload.get("scripts"), Mapping) else {}
            if (package_json.parent / "index.html").exists() or any(compact(scripts.get(key)) for key in ("dev", "start")):
                launchable += 1
    except Exception:  # pragma: no cover - defensive projection
        return {"package_root_count": len(package_roots), "launchable_count": launchable, "family_count": len(families)}
    return {"package_root_count": len(package_roots), "launchable_count": launchable, "family_count": len(families)}


def _mission_rows(managed_missions: list[dict[str, Any]], vnext: Mapping[str, Any]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for family in listify(vnext.get("mission_families")):
        if not isinstance(family, Mapping):
            continue
        mission_id = compact(family.get("family_id"), "mission")
        by_id[mission_id] = {
            "mission_id": mission_id,
            "project_id": DEFAULT_PROJECT_ID,
            "label": compact(family.get("label"), mission_id),
            "summary": compact(family.get("description"), "Mission family projected from vNext evidence."),
            "status": compact(family.get("status"), "mapped"),
            "mission_type": "vnext_family",
            "packet_count": family.get("packet_count", 0),
            "epoch_count": family.get("epoch_count", 0),
            "protocol_count": family.get("protocol_count", 0),
            "context_package_count": family.get("context_package_count", 0),
            "evidence_refs": string_list(family.get("evidence_paths")),
            "source": "derived_vnext_mission_family",
        }
    for mission in managed_missions:
        mission_id = compact(mission.get("mission_id"), _id_from_text("mission", mission.get("label") or mission.get("summary") or "mission"))
        by_id[mission_id] = {**by_id.get(mission_id, {}), **mission, "mission_id": mission_id, "project_id": compact(mission.get("project_id"), DEFAULT_PROJECT_ID)}
    return sorted(by_id.values(), key=lambda item: compact(item.get("label")))


def _derived_vnext_blockers(vnext: Mapping[str, Any]) -> list[dict[str, Any]]:
    latest_packet = vnext.get("current_packet") if isinstance(vnext.get("current_packet"), Mapping) else {}
    latest_evidence = compact(latest_packet.get("result_path") or latest_packet.get("packet_path"), "ION_VNEXT/07_work")
    blockers: list[dict[str, Any]] = []
    for gate in listify(vnext.get("gates")):
        if not isinstance(gate, Mapping):
            continue
        gate_id = compact(gate.get("gate_id"), "unknown_gate")
        status = compact(gate.get("status"), "open")
        blockers.append(
            {
                "blocker_id": f"derived_vnext_gate_{_slug(gate_id)}",
                "project_id": DEFAULT_PROJECT_ID,
                "mission_ids": [],
                "title": gate_id.replace("_", " "),
                "detail": "Derived from the vNext proof-gate projection. Close it by closing the source vNext gate through a proof-gated packet.",
                "severity": _severity_for_gate(gate_id, status),
                "status": status,
                "source": "derived_vnext_gate",
                "derived": True,
                "latest_packet": compact(gate.get("latest_packet") or latest_packet.get("token"), ""),
                "blocks": [gate_id],
                "unlock_condition": _unlock_condition_for_gate(gate_id),
                "required_next_action": compact(latest_packet.get("next_route_condition"), "Create or complete the bounded proof packet that removes this gate."),
                "evidence_refs": [latest_evidence],
                "created_at": compact(latest_packet.get("created_at"), ""),
            }
        )
    return blockers


def _project_timeline(
    *,
    ledger: Mapping[str, Any],
    vnext: Mapping[str, Any],
    blockers: list[dict[str, Any]],
    questions: list[dict[str, Any]],
    receipt_events: list[dict[str, Any]],
    runtime_timeline: list[dict[str, Any]],
    lane_timeline: Mapping[str, Any],
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for packet in listify(vnext.get("packets")):
        if not isinstance(packet, Mapping):
            continue
        events.append(
            {
                "event_id": f"packet_{compact(packet.get('sequence_id'), compact(packet.get('token'), 'packet'))}",
                "project_id": DEFAULT_PROJECT_ID,
                "event_type": "packet",
                "status": compact(packet.get("status"), "unknown"),
                "occurred_at": compact(packet.get("created_at"), ""),
                "title": compact(packet.get("title") or packet.get("token"), "vNext packet"),
                "detail": compact(packet.get("verdict") or packet.get("packet_id"), ""),
                "evidence_refs": string_list(packet.get("result_path") or packet.get("packet_path")),
                "source": "vnext_projection",
            }
        )
    for blocker in blockers:
        if blocker.get("derived") and not _is_open_status(blocker.get("status")):
            continue
        events.append(
            {
                "event_id": f"blocker_{compact(blocker.get('blocker_id'))}",
                "project_id": compact(blocker.get("project_id"), DEFAULT_PROJECT_ID),
                "event_type": "blocker",
                "status": compact(blocker.get("status"), "open"),
                "occurred_at": compact(blocker.get("updated_at") or blocker.get("created_at"), ""),
                "title": compact(blocker.get("title"), "blocker"),
                "detail": compact(blocker.get("required_next_action") or blocker.get("unlock_condition"), ""),
                "evidence_refs": string_list(blocker.get("evidence_refs")),
                "source": compact(blocker.get("source"), "project_cockpit"),
            }
        )
    for question in questions:
        events.append(
            {
                "event_id": f"question_{compact(question.get('question_id'))}",
                "project_id": compact(question.get("project_id"), DEFAULT_PROJECT_ID),
                "event_type": "question",
                "status": compact(question.get("status"), "open"),
                "occurred_at": compact(question.get("updated_at") or question.get("created_at"), ""),
                "title": compact(question.get("question_text"), "open question"),
                "detail": compact(question.get("context") or question.get("resolution"), ""),
                "evidence_refs": string_list(question.get("evidence_refs")),
                "source": "project_cockpit_ledger",
            }
        )
    for event in listify(ledger.get("timeline_events")):
        if isinstance(event, Mapping):
            events.append({**dict(event), "source": compact(event.get("source"), "project_cockpit_ledger")})
    events.extend(receipt_events)
    for event in runtime_timeline[:20]:
        events.append(
            {
                "event_id": f"runtime_{compact(event.get('source'), 'event')}_{compact(event.get('event_type'), 'event')}_{compact(event.get('time'), '')}",
                "project_id": DEFAULT_PROJECT_ID,
                "event_type": "runtime",
                "status": compact(event.get("status"), "unknown"),
                "occurred_at": compact(event.get("time"), ""),
                "title": compact(event.get("source"), "runtime event"),
                "detail": compact(event.get("detail") or event.get("path"), ""),
                "evidence_refs": string_list(event.get("path")),
                "source": "cockpit_runtime_timeline",
            }
        )
    for event in listify(lane_timeline.get("events"))[:40]:
        if not isinstance(event, Mapping):
            continue
        events.append(
            {
                "event_id": f"lane_{compact(event.get('id'), 'event')}",
                "project_id": DEFAULT_PROJECT_ID,
                "event_type": "lane",
                "status": compact(event.get("status"), "unknown"),
                "occurred_at": compact(event.get("timestamp"), ""),
                "title": f"{compact(event.get('requested_lane'), 'unknown')} -> {compact(event.get('effective_lane'), 'unknown')}",
                "detail": compact(event.get("lane_change_reason") or event.get("receipt_id") or event.get("source_path"), ""),
                "evidence_refs": string_list(event.get("source_path")),
                "source": "lane_timeline",
            }
        )
    unique: dict[str, dict[str, Any]] = {}
    for event in events:
        event_id = compact(event.get("event_id"), _id_from_text("event", event.get("title") or event.get("detail") or "event"))
        unique[event_id] = {**event, "event_id": event_id}
    return sorted(unique.values(), key=lambda item: (compact(item.get("occurred_at")), compact(item.get("event_id"))), reverse=True)[:220]


def _create_record(record_type: str, payload: Mapping[str, Any], *, created_at: str, actor: str) -> dict[str, Any]:
    if record_type == "blocker":
        title = compact(payload.get("title"))
        if not title:
            raise ValueError("blocker title is required")
        return _normalize_record(
            {
                "blocker_id": compact(payload.get("blocker_id"), _id_from_text("blocker", f"{created_at} {title}")),
                "project_id": compact(payload.get("project_id"), DEFAULT_PROJECT_ID),
                "mission_ids": string_list(payload.get("mission_ids")),
                "title": title,
                "detail": compact(payload.get("detail")),
                "severity": compact(payload.get("severity"), "medium"),
                "status": compact(payload.get("status"), "open"),
                "blocks": string_list(payload.get("blocks")),
                "unlock_condition": compact(payload.get("unlock_condition")),
                "required_next_action": compact(payload.get("required_next_action")),
                "owner_route": compact(payload.get("owner_route"), "codex_cli"),
                "evidence_refs": string_list(payload.get("evidence_refs")),
                "created_by": actor,
                "created_at": created_at,
                "updated_at": created_at,
                "source": "project_cockpit_managed",
                "derived": False,
            },
            record_type,
        )
    question_text = compact(payload.get("question_text") or payload.get("title"))
    if not question_text:
        raise ValueError("question_text is required")
    return _normalize_record(
        {
            "question_id": compact(payload.get("question_id"), _id_from_text("question", f"{created_at} {question_text}")),
            "project_id": compact(payload.get("project_id"), DEFAULT_PROJECT_ID),
            "mission_ids": string_list(payload.get("mission_ids")),
            "question_text": question_text,
            "needed_from": compact(payload.get("needed_from"), "ION_OPERATOR_OR_STEWARD"),
            "priority": compact(payload.get("priority"), "P2_NORMAL"),
            "status": compact(payload.get("status"), "open"),
            "context": compact(payload.get("context")),
            "blocking": string_list(payload.get("blocking")),
            "evidence_refs": string_list(payload.get("evidence_refs")),
            "created_by": actor,
            "created_at": created_at,
            "updated_at": created_at,
            "source": "project_cockpit_managed",
        },
        record_type,
    )


def _update_record(record_type: str, before: dict[str, Any], payload: Mapping[str, Any], *, action: str, updated_at: str, actor: str) -> dict[str, Any]:
    after = dict(before)
    editable = {
        "blocker": ("title", "detail", "severity", "status", "mission_ids", "blocks", "unlock_condition", "required_next_action", "owner_route", "evidence_refs"),
        "question": ("question_text", "needed_from", "priority", "status", "context", "blocking", "evidence_refs"),
    }[record_type]
    for key in editable:
        if key not in payload:
            continue
        after[key] = string_list(payload.get(key)) if key in {"mission_ids", "blocks", "evidence_refs", "blocking"} else compact(payload.get(key), compact(after.get(key)))
    if action == "resolve":
        after["status"] = compact(payload.get("status"), "resolved")
        after["resolved_by"] = actor
        after["resolved_at"] = updated_at
        after["resolution"] = compact(payload.get("resolution"), "Resolved from Project Cockpit.")
        after["resolution_evidence"] = string_list(payload.get("resolution_evidence") or payload.get("evidence_refs"))
    after["updated_by"] = actor
    after["updated_at"] = updated_at
    return _normalize_record(after, record_type)


def _normalize_record(record: dict[str, Any], record_type: str) -> dict[str, Any]:
    record["project_id"] = compact(record.get("project_id"), DEFAULT_PROJECT_ID)
    record["mission_ids"] = string_list(record.get("mission_ids"))
    record["evidence_refs"] = string_list(record.get("evidence_refs"))
    if record_type == "blocker":
        record["blocker_id"] = compact(record.get("blocker_id"), _id_from_text("blocker", record.get("title") or "blocker"))
        record["status"] = compact(record.get("status"), "open").lower()
        record["severity"] = compact(record.get("severity"), "medium").lower()
        record["blocks"] = string_list(record.get("blocks"))
        record["derived"] = bool(record.get("derived"))
    else:
        record["question_id"] = compact(record.get("question_id"), _id_from_text("question", record.get("question_text") or "question"))
        record["status"] = compact(record.get("status"), "open").lower()
        record["priority"] = compact(record.get("priority"), "P2_NORMAL")
        record["blocking"] = string_list(record.get("blocking"))
    return record


def _ledger_event(record_type: str, action: str, record: Mapping[str, Any], *, created_at: str, actor: str) -> dict[str, Any]:
    return {
        "event_id": _id_from_text("event", f"{created_at} {record_type} {action} {_record_id(record, record_type)}"),
        "project_id": compact(record.get("project_id"), DEFAULT_PROJECT_ID),
        "event_type": f"{record_type}_{action}",
        "status": compact(record.get("status"), "recorded"),
        "occurred_at": created_at,
        "title": compact(record.get("title") or record.get("question_text"), _record_id(record, record_type)),
        "detail": compact(record.get("resolution") or record.get("required_next_action") or record.get("context"), ""),
        "actor": actor,
        "evidence_refs": string_list(record.get("evidence_refs")),
        "source": "project_cockpit_ledger",
    }


def _project_cockpit_receipt_events(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    receipt_dir = root / PROJECT_COCKPIT_RECEIPTS_DIR
    for path in sorted(receipt_dir.glob("*.json"), reverse=True)[:80] if receipt_dir.exists() else []:
        payload = read_json(path)
        if not payload:
            continue
        rel = path.relative_to(root).as_posix()
        receipt = {
            "receipt_id": payload.get("receipt_id"),
            "created_at": payload.get("created_at"),
            "action": payload.get("action"),
            "record_type": payload.get("record_type"),
            "record_id": payload.get("record_id"),
            "path": rel,
        }
        receipts.append(receipt)
        events.append(
            {
                "event_id": f"receipt_{compact(payload.get('receipt_id'), path.stem)}",
                "project_id": DEFAULT_PROJECT_ID,
                "event_type": "receipt",
                "status": "recorded",
                "occurred_at": compact(payload.get("created_at"), ""),
                "title": f"{compact(payload.get('record_type'), 'record')} {compact(payload.get('action'), 'action')}",
                "detail": compact(payload.get("record_id"), ""),
                "evidence_refs": [rel],
                "source": "project_cockpit_receipts",
            }
        )
    return events, receipts


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_receipt(root: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    receipt_id = compact(payload.get("receipt_id"), _id_from_text("receipt", utc_now()))
    path = root / PROJECT_COCKPIT_RECEIPTS_DIR / f"{receipt_id}.json"
    _write_json(path, payload)
    return {**payload, "path": path.relative_to(root).as_posix()}


def _receipt_id(record_type: str, action: str, record: Mapping[str, Any], created_at: str) -> str:
    return _id_from_text("project_cockpit_receipt", f"{created_at} {record_type} {action} {_record_id(record, record_type)}")


def _record_id(record: Mapping[str, Any], record_type: str) -> str:
    return compact(record.get("blocker_id" if record_type == "blocker" else "question_id"), "")


def _id_from_text(prefix: str, text: Any) -> str:
    return f"{prefix}_{_slug(compact(text, prefix))}"


def _slug(text: str) -> str:
    return _SAFE_ID_RE.sub("_", text.lower()).strip("_")[:96] or "item"


def _status_rank(value: Any) -> int:
    status = compact(value, "open").lower()
    if status in {"open", "blocked", "critical"}:
        return 0
    if status in {"assigned", "in_progress", "watch"}:
        return 1
    if status in {"resolved", "closed", "complete"}:
        return 3
    return 2


def _severity_rank(value: Any) -> int:
    severity = compact(value, "medium").lower()
    return {"critical": 0, "high": 1, "medium": 2, "normal": 2, "low": 3, "watch": 3}.get(severity, 2)


def _priority_rank(value: Any) -> int:
    priority = compact(value, "P2_NORMAL")
    return {"P0_BLOCKING": 0, "P1_HIGH": 1, "P2_NORMAL": 2, "P3_LOW": 3}.get(priority, 2)


def _is_open_status(value: Any) -> bool:
    return compact(value, "open").lower() not in {"closed", "resolved", "complete"}


def _severity_for_gate(gate_id: str, status: str) -> str:
    if compact(status).lower() in {"closed", "resolved", "complete"}:
        return "low"
    lowered = gate_id.lower()
    if "production" in lowered or "authority" in lowered or "approval" in lowered:
        return "high"
    if "supabase" in lowered or "live" in lowered:
        return "medium"
    return "normal"


def _unlock_condition_for_gate(gate_id: str) -> str:
    lowered = gate_id.lower()
    if "release_bundle" in lowered:
        return "Produce and validate the release bundle candidate through a proof-gated packet."
    if "rollback" in lowered:
        return "Produce and validate rollback package evidence through a proof-gated packet."
    if "approval" in lowered:
        return "Record the correct operator/steward decision artifact without inferring approval from chat presence."
    if "production" in lowered or "authority" in lowered:
        return "Create a separate proof-gated production authority transition packet and keep authority false until accepted."
    if "supabase" in lowered:
        return "Run or explicitly defer the Supabase mirror smoke through a safe non-authoritative proof packet."
    if "mcp" in lowered:
        return "Run the MCP listener smoke through the bounded local proof lane."
    return "Close the source gate through a bounded packet with evidence, validation, receipt, and non-claims."
