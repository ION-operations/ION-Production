"""Project canon dossier generation.

This module turns the project portfolio manifest into durable domain/project
dossiers. The manifest remains the scan authority; these dossiers are the
operator and cockpit reading layer for domain pages, project tabs, lineage,
diffs, docs, chats, launch/preview, and next-actions.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .ion_project_portfolio import (
    CANONICAL_DOMAINS,
    PORTFOLIO_DIR,
    PORTFOLIO_MANIFEST,
    PORTFOLIO_RECEIPTS_DIR,
    compact,
    read_json,
    slug,
    write_json,
)


DOSSIER_DIR = PORTFOLIO_DIR / "dossiers"
DOSSIER_INDEX = DOSSIER_DIR / "PROJECT_CANON_DOSSIER_INDEX.json"

INDEX_SCHEMA_ID = "ion.project_canon_dossier_index.v1"
DOMAIN_SCHEMA_ID = "ion.project_domain_canon_dossier.v1"
PROJECT_SCHEMA_ID = "ion.project_family_canon_dossier.v1"
RECEIPT_SCHEMA_ID = "ion.project_canon_dossier_receipt.v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_project_canon_dossiers(
    root: str | Path = ".",
    *,
    mirror_to_organized: bool = True,
) -> dict[str, Any]:
    """Generate domain/project dossiers from the cached portfolio manifest."""

    shell_root = Path(root).expanduser().resolve()
    manifest_path = shell_root / PORTFOLIO_MANIFEST
    manifest = read_json(manifest_path)
    if compact(manifest.get("schema_id")) != "ion.project_portfolio.v1":
        return {
            "ok": False,
            "schema_id": INDEX_SCHEMA_ID,
            "status": "project_portfolio_manifest_missing",
            "manifest_path": manifest_path.as_posix(),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        }

    output_root = shell_root / DOSSIER_DIR
    output_root.mkdir(parents=True, exist_ok=True)
    families = _mapping_list(manifest.get("families"))
    domains = _domain_rows(manifest, families)
    families_by_domain = _families_by_domain(families)
    organizer = _mapping(manifest.get("organizer"))
    materialized_root = compact(organizer.get("materialized_root"))

    domain_index_rows: list[dict[str, Any]] = []
    project_dossier_count = 0
    mirrored_dossier_count = 0
    generated_at = utc_now()

    for domain in domains:
        domain_id = compact(domain.get("domain_id"), compact(domain.get("group_id"), "tools-generated-apps"))
        domain_dir = output_root / "domains" / slug(domain_id, "domain")
        projects_dir = domain_dir / "projects"
        projects_dir.mkdir(parents=True, exist_ok=True)
        domain_families = sorted(families_by_domain.get(domain_id, []), key=lambda item: compact(item.get("label")))
        project_rows: list[dict[str, Any]] = []

        for family in domain_families:
            family_slug = slug(family.get("family_id") or family.get("label"), "project")
            project_json_path = projects_dir / f"{family_slug}.json"
            project_md_path = projects_dir / f"{family_slug}.md"
            project_dossier = _project_dossier(
                manifest=manifest,
                domain=domain,
                family=family,
                generated_at=generated_at,
                project_json_path=project_json_path,
                project_md_path=project_md_path,
                shell_root=shell_root,
            )
            write_json(project_json_path, project_dossier)
            project_md_path.write_text(_project_markdown(project_dossier), encoding="utf-8")

            mirror_paths = _mirror_project_dossier(
                family=family,
                project_dossier=project_dossier,
                markdown=_project_markdown(project_dossier),
                materialized_root=materialized_root,
                enabled=mirror_to_organized,
            )
            if mirror_paths:
                mirrored_dossier_count += 1
                project_dossier["mirror"] = mirror_paths
                write_json(project_json_path, project_dossier)

            project_dossier_count += 1
            project_rows.append(
                {
                    "family_id": project_dossier["identity"]["family_id"],
                    "label": project_dossier["identity"]["label"],
                    "domain_id": domain_id,
                    "posture": project_dossier["operating_system"].get("posture", ""),
                    "readiness_score": project_dossier["operating_system"].get("readiness_score", 0),
                    "version_count": project_dossier["counts"]["version_count"],
                    "diff_count": project_dossier["counts"]["diff_count"],
                    "doc_count": project_dossier["counts"]["doc_count"],
                    "reference_count": project_dossier["counts"]["reference_count"],
                    "launchable_count": project_dossier["counts"]["launchable_count"],
                    "project_dossier_path": project_json_path.as_posix(),
                    "project_dossier_relpath": _relpath(project_json_path, shell_root),
                    "project_dossier_markdown_path": project_md_path.as_posix(),
                    "project_dossier_markdown_relpath": _relpath(project_md_path, shell_root),
                    "organized_path": compact(family.get("organized_path")),
                    "current_path": compact(family.get("current_path")),
                    "chat_binding_status": project_dossier["chat_attachment"]["status"],
                }
            )

        domain_json_path = domain_dir / "DOMAIN_DOSSIER.json"
        domain_md_path = domain_dir / "DOMAIN_DOSSIER.md"
        domain_dossier = _domain_dossier(
            manifest=manifest,
            domain=domain,
            project_rows=project_rows,
            generated_at=generated_at,
            domain_json_path=domain_json_path,
            domain_md_path=domain_md_path,
            shell_root=shell_root,
        )
        write_json(domain_json_path, domain_dossier)
        domain_md_path.write_text(_domain_markdown(domain_dossier), encoding="utf-8")

        domain_index_rows.append(
            {
                "domain_id": domain_id,
                "label": compact(domain.get("label"), domain_id),
                "folder": compact(domain.get("folder")),
                "posture": domain_dossier["operating_system"].get("posture", ""),
                "average_readiness_score": domain_dossier["operating_system"].get("average_readiness_score", 0),
                "family_count": len(project_rows),
                "project_count": _int(domain.get("project_count")),
                "version_count": _int(domain.get("version_count")),
                "diff_count": _int(domain.get("diff_count")),
                "doc_count": _int(domain.get("doc_count")),
                "reference_count": _int(domain.get("reference_count")),
                "launchable_count": _int(domain.get("launchable_count")),
                "domain_dossier_path": domain_json_path.as_posix(),
                "domain_dossier_relpath": _relpath(domain_json_path, shell_root),
                "domain_dossier_markdown_path": domain_md_path.as_posix(),
                "domain_dossier_markdown_relpath": _relpath(domain_md_path, shell_root),
                "projects": project_rows,
            }
        )

    index_path = shell_root / DOSSIER_INDEX
    receipt_path = _write_receipt(
        shell_root=shell_root,
        manifest_path=manifest_path,
        generated_at=generated_at,
        domain_count=len(domain_index_rows),
        project_dossier_count=project_dossier_count,
        mirrored_dossier_count=mirrored_dossier_count,
    )
    manifest_summary = _mapping(manifest.get("summary"))
    total_diff_count = sum(_int(domain.get("diff_count")) for domain in domain_index_rows)
    index = {
        "ok": True,
        "schema_id": INDEX_SCHEMA_ID,
        "generated_at": generated_at,
        "status": "project_canon_dossiers_ready",
        "source_manifest_path": manifest_path.as_posix(),
        "source_manifest_relpath": _relpath(manifest_path, shell_root),
        "source_manifest_generated_at": compact(manifest.get("generated_at")),
        "dossier_root": output_root.as_posix(),
        "dossier_root_relpath": _relpath(output_root, shell_root),
        "index_path": index_path.as_posix(),
        "index_relpath": DOSSIER_INDEX.as_posix(),
        "latest_receipt": {
            "path": receipt_path.as_posix(),
            "relpath": _relpath(receipt_path, shell_root),
            "created_at": generated_at,
        },
        "summary": {
            **manifest_summary,
            "domain_dossier_count": len(domain_index_rows),
            "project_dossier_count": project_dossier_count,
            "mirrored_project_dossier_count": mirrored_dossier_count,
            "project_diff_unit_count": total_diff_count,
            "diff_manifest_count": _int(manifest_summary.get("diff_manifest_count"), total_diff_count),
        },
        "cockpit_consumption": {
            "left_drawer": "load domains from this index; selecting a domain opens its domain page",
            "domain_page": "load domain_dossier_path for board, internal projects, docs, timeline, risks, and plans",
            "project_tabs": "load project_dossier_path for selected project detail tabs inside the active domain page",
            "preview_system": "bind launch_preview plus timeline/diffs to the selected project tab",
            "chat_system": "use chat_attachment.search_terms until the real project-to-chat index is available",
        },
        "organization_contract": {
            "copy_policy": compact(
                organizer.get("source_copy_policy"),
                "domain/project current source copy only; historical full folders become lineage pointers and diff manifests",
            ),
            "materialized_root": materialized_root,
            "historical_full_folder_policy": "do not copy historical roots as duplicate project folders; keep them as version path witnesses and adjacent diff units",
            "dossier_policy": "every domain and project family receives a human-readable markdown dossier plus JSON for cockpit consumption",
            "candidate_only": True,
        },
        "domains": domain_index_rows,
        "authority": _authority(),
        "non_claims": [
            "dossiers are generated from cached project portfolio data",
            "dossiers do not promote candidate organizer state to accepted state",
            "chat bindings are marked pending until a real archive/session index is attached",
            "launch and preview actions are represented as metadata only here",
        ],
    }
    write_json(index_path, index)
    (output_root / "README.md").write_text(_index_markdown(index), encoding="utf-8")
    return index


def _domain_rows(manifest: Mapping[str, Any], families: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = _mapping_list(manifest.get("canonical_domains"))
    if rows:
        return sorted(rows, key=lambda item: _int(item.get("sort_order")) or 99)
    by_domain = _families_by_domain(families)
    result: list[dict[str, Any]] = []
    for index, domain in enumerate(CANONICAL_DOMAINS, start=1):
        domain_id = compact(domain.get("domain_id"))
        domain_families = by_domain.get(domain_id, [])
        if not domain_families:
            continue
        result.append(
            {
                **domain,
                "group_id": domain_id,
                "sort_order": index,
                "family_count": len(domain_families),
                "project_count": sum(_int(family.get("project_count")) for family in domain_families),
                "version_count": sum(_int(family.get("version_count")) for family in domain_families),
                "diff_count": sum(_int(family.get("diff_count")) for family in domain_families),
                "doc_count": sum(_int(family.get("doc_count")) for family in domain_families),
                "reference_count": sum(_int(family.get("reference_count")) for family in domain_families),
                "launchable_count": sum(_int(family.get("launchable_count")) for family in domain_families),
                "operating_system": {},
                "families": [],
            }
        )
    return result


def _families_by_domain(families: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_domain: dict[str, list[dict[str, Any]]] = {}
    for family in families:
        domain_id = compact(family.get("domain_id") or family.get("group_id"), "tools-generated-apps")
        by_domain.setdefault(domain_id, []).append(family)
    return by_domain


def _project_dossier(
    *,
    manifest: Mapping[str, Any],
    domain: Mapping[str, Any],
    family: Mapping[str, Any],
    generated_at: str,
    project_json_path: Path,
    project_md_path: Path,
    shell_root: Path,
) -> dict[str, Any]:
    versions = _mapping_list(family.get("versions"))
    diffs = _mapping_list(family.get("diffs"))
    docs = _mapping(family.get("docs"))
    current = _mapping(family.get("current"))
    ops = _mapping(family.get("operating_system"))
    launch = _mapping(current.get("launch"))
    diff_rows = [_diff_dossier_row(diff) for diff in diffs]
    timeline_rows = [_version_timeline_row(version, index) for index, version in enumerate(versions, start=1)]
    family_id = compact(family.get("family_id"), "unknown")
    label = compact(family.get("label"), family_id)
    domain_id = compact(domain.get("domain_id") or family.get("domain_id"), "tools-generated-apps")
    organized_path = compact(family.get("organized_path"))
    source_copy_path = f"{organized_path}/source/current" if organized_path else ""

    return {
        "schema_id": PROJECT_SCHEMA_ID,
        "generated_at": generated_at,
        "status": "project_family_canon_dossier_ready",
        "identity": {
            "family_id": family_id,
            "label": label,
            "domain_id": domain_id,
            "domain_label": compact(domain.get("label") or family.get("domain_label"), domain_id),
            "source_ids": _string_list(family.get("source_ids")),
            "current_project_id": compact(family.get("current_project_id")),
            "current_path": compact(family.get("current_path")),
            "organized_path": organized_path,
            "dossier_path": project_json_path.as_posix(),
            "dossier_relpath": _relpath(project_json_path, shell_root),
            "dossier_markdown_path": project_md_path.as_posix(),
            "dossier_markdown_relpath": _relpath(project_md_path, shell_root),
        },
        "counts": {
            "project_count": _int(family.get("project_count")),
            "version_count": _int(family.get("version_count"), len(versions)),
            "branch_count": _int(family.get("branch_count")),
            "diff_count": _int(family.get("diff_count"), len(diffs)),
            "launchable_count": _int(family.get("launchable_count")),
            "doc_count": _int(family.get("doc_count") or docs.get("doc_count")),
            "reference_count": _int(family.get("reference_count") or docs.get("reference_count")),
            "workspace_dir_count": _int(family.get("workspace_dir_count")),
        },
        "source_organization": {
            "current_source": compact(family.get("current_path")),
            "current_source_copy": source_copy_path,
            "organized_path": organized_path,
            "lineage_status": compact(family.get("lineage_status")),
            "materialization_plan": compact(family.get("materialization_plan")),
            "source_copy_policy": compact(
                _mapping(manifest.get("organizer")).get("source_copy_policy"),
                "copy current source only; keep historical roots as lineage pointers and diff manifests",
            ),
            "duplicate_policy": "historical full folders are not copied as duplicate organized projects",
        },
        "timeline": {
            "status": "version_timeline_ready" if timeline_rows else "single_or_missing_version",
            "versions": timeline_rows,
            "current_version": next((row for row in timeline_rows if row.get("is_current")), timeline_rows[-1] if timeline_rows else {}),
        },
        "diff_evolution": {
            "status": "diffs_ready" if diff_rows else "single_root_or_diff_pending",
            "diff_count": len(diff_rows),
            "diffs": diff_rows,
        },
        "docs": {
            "status": compact(docs.get("status"), "docs_missing"),
            "doc_count": _int(docs.get("doc_count")),
            "reference_count": _int(docs.get("reference_count")),
            "coverage": _mapping(docs.get("coverage")),
            "primary_docs": _mapping_list(docs.get("primary_docs")),
            "docs": _mapping_list(docs.get("docs")),
            "references": _mapping_list(docs.get("references")),
            "target_docs": _mapping_list(docs.get("target_docs")),
        },
        "launch_preview": {
            "launchable": bool(current.get("launchable") or launch.get("launchable")),
            "status": compact(launch.get("status"), "not_launchable"),
            "framework": compact(launch.get("framework") or current.get("stack")),
            "project_path": compact(launch.get("project_path") or current.get("path")),
            "action_path": compact(launch.get("action_path")),
            "open_href": compact(launch.get("open_href") or launch.get("url")),
            "repair_policy": "repair-and-launch action remains explicit; this dossier records metadata only",
        },
        "chat_attachment": {
            "status": "binding_pending",
            "indexed_chat_count": 0,
            "search_terms": _chat_search_terms(domain, family),
            "next_action": "build project-to-chat attachment index from Codex/ChatGPT archive records and bind session IDs to family/version IDs",
            "non_claim": "no project chat is claimed attached by this dossier until a real archive/session index proves it",
        },
        "agent_workflows": _agent_workflows(family),
        "operating_system": ops,
        "quality_gates": _mapping_list(ops.get("quality_gates")),
        "risk_register": _mapping_list(ops.get("risk_register")),
        "next_actions": _mapping_list(ops.get("next_actions")),
        "future_plan": _future_plan(family, docs, diff_rows),
        "authority": _authority(),
    }


def _domain_dossier(
    *,
    manifest: Mapping[str, Any],
    domain: Mapping[str, Any],
    project_rows: list[dict[str, Any]],
    generated_at: str,
    domain_json_path: Path,
    domain_md_path: Path,
    shell_root: Path,
) -> dict[str, Any]:
    docs = _mapping(domain.get("docs"))
    ops = _mapping(domain.get("operating_system"))
    domain_id = compact(domain.get("domain_id") or domain.get("group_id"), "tools-generated-apps")
    return {
        "schema_id": DOMAIN_SCHEMA_ID,
        "generated_at": generated_at,
        "status": "project_domain_canon_dossier_ready",
        "domain": {
            "domain_id": domain_id,
            "label": compact(domain.get("label"), domain_id),
            "summary": compact(domain.get("summary")),
            "folder": compact(domain.get("folder")),
            "dossier_path": domain_json_path.as_posix(),
            "dossier_relpath": _relpath(domain_json_path, shell_root),
            "dossier_markdown_path": domain_md_path.as_posix(),
            "dossier_markdown_relpath": _relpath(domain_md_path, shell_root),
        },
        "counts": {
            "family_count": len(project_rows),
            "project_count": _int(domain.get("project_count")),
            "version_count": _int(domain.get("version_count")),
            "branch_count": _int(domain.get("branch_count")),
            "diff_count": _int(domain.get("diff_count")),
            "launchable_count": _int(domain.get("launchable_count")),
            "doc_count": _int(domain.get("doc_count")),
            "reference_count": _int(domain.get("reference_count")),
            "documented_family_count": _int(domain.get("documented_family_count")),
            "versioned_family_count": _int(domain.get("versioned_family_count")),
        },
        "projects": project_rows,
        "operating_system": ops,
        "board_columns": _mapping_list(ops.get("board_columns")),
        "top_risks": _mapping_list(ops.get("top_risks")),
        "maintenance_rhythm": _mapping_list(ops.get("maintenance_rhythm")),
        "docs": {
            "status": compact(docs.get("status"), "domain_docs_missing"),
            "doc_count": _int(docs.get("doc_count")),
            "reference_count": _int(docs.get("reference_count")),
            "recommended_sections": _string_list(docs.get("recommended_sections")),
            "top_docs": _mapping_list(docs.get("top_docs")),
            "references": _mapping_list(docs.get("references")),
            "target_docs": _mapping_list(docs.get("target_docs")),
        },
        "cockpit_workflow": {
            "entry": "left drawer domain selector",
            "domain_page": "internal project cards plus domain board, timeline, docs, diffs, chats, plans, and manage panes",
            "project_tabs": "clicking a project opens a project detail tab beside the domain tab",
            "critical_actions": ["open project tab", "preview/launch", "view diffs", "view docs", "attach chats", "record next action"],
        },
        "chat_attachment": {
            "status": "binding_pending",
            "next_action": "bind archived chats/sessions to domain and project family IDs",
            "search_terms": [compact(domain.get("label"), domain_id), domain_id],
        },
        "source_manifest": {
            "path": (shell_root / PORTFOLIO_MANIFEST).as_posix(),
            "relpath": PORTFOLIO_MANIFEST.as_posix(),
            "generated_at": compact(manifest.get("generated_at")),
        },
        "authority": _authority(),
    }


def _diff_dossier_row(diff: Mapping[str, Any]) -> dict[str, Any]:
    file_diff = _mapping(diff.get("file_diff"))
    return {
        "diff_id": compact(diff.get("diff_id")),
        "from_project_id": compact(diff.get("from_project_id")),
        "to_project_id": compact(diff.get("to_project_id")),
        "from_label": compact(diff.get("from_label")),
        "to_label": compact(diff.get("to_label")),
        "from_version": compact(diff.get("from_version")),
        "to_version": compact(diff.get("to_version")),
        "from_path": compact(diff.get("from_path")),
        "to_path": compact(diff.get("to_path")),
        "status": compact(diff.get("status")),
        "manifest_path": compact(diff.get("manifest_path")),
        "copy_policy": compact(diff.get("copy_policy")),
        "file_diff": file_diff,
        "change_explanation": _diff_explanation(diff, file_diff),
    }


def _diff_explanation(diff: Mapping[str, Any], file_diff: Mapping[str, Any]) -> str:
    status = compact(file_diff.get("status"), compact(diff.get("status"), "unknown"))
    from_label = compact(diff.get("from_label") or diff.get("from_version") or diff.get("from_project_id"), "previous version")
    to_label = compact(diff.get("to_label") or diff.get("to_version") or diff.get("to_project_id"), "next version")
    if status == "ready":
        added = _int(file_diff.get("added_count"))
        removed = _int(file_diff.get("removed_count"))
        changed = _int(file_diff.get("changed_count"))
        scope = _diff_scope(file_diff)
        return f"{from_label} to {to_label}: {changed} changed files, {added} added files, and {removed} removed files. Primary touched surface: {scope}."
    if status in {"not_available", "missing", "unreadable_zip"}:
        previous_status = compact(file_diff.get("previous_status"), "unknown")
        current_status = compact(file_diff.get("current_status"), "unknown")
        return f"{from_label} to {to_label}: lineage is registered, but source comparison is not available yet ({previous_status} -> {current_status}). Keep both paths as witnesses until the missing source is restored."
    if status == "not_materialized":
        return f"{from_label} to {to_label}: adjacent version pair is registered; materialize file-level diff before promotion or archive cleanup."
    return f"{from_label} to {to_label}: adjacent version pair is registered with diff status `{status}`."


def _diff_scope(file_diff: Mapping[str, Any]) -> str:
    samples = [
        *_string_list(file_diff.get("changed_sample"))[:12],
        *_string_list(file_diff.get("added_sample"))[:8],
        *_string_list(file_diff.get("removed_sample"))[:8],
    ]
    if not samples:
        return "no file samples recorded"
    buckets: dict[str, int] = {}
    for sample in samples:
        parts = [part for part in sample.split("/") if part]
        if len(parts) > 1:
            key = parts[0]
        elif "." in sample:
            key = sample.rsplit(".", 1)[-1]
        else:
            key = sample
        buckets[key] = buckets.get(key, 0) + 1
    ranked = sorted(buckets.items(), key=lambda item: (-item[1], item[0]))[:4]
    return ", ".join(f"{name} ({count})" for name, count in ranked)


def _version_timeline_row(version: Mapping[str, Any], index: int) -> dict[str, Any]:
    return {
        "sequence": index,
        "version_id": compact(version.get("version_id")),
        "project_id": compact(version.get("project_id")),
        "label": compact(version.get("display_label") or version.get("label"), f"Version {index}"),
        "version_token": compact(version.get("version_token")),
        "milestone_token": compact(version.get("milestone_token")),
        "date_token": compact(version.get("date_token")),
        "branch_id": compact(version.get("branch_id")),
        "branch_label": compact(version.get("branch_label")),
        "path": compact(version.get("path")),
        "stack": compact(version.get("stack")),
        "launchable": bool(version.get("launchable")),
        "is_current": bool(version.get("is_current")),
        "docs": {
            "doc_count": _int(_mapping(version.get("docs")).get("doc_count")),
            "status": compact(_mapping(version.get("docs")).get("status")),
        },
    }


def _future_plan(family: Mapping[str, Any], docs: Mapping[str, Any], diff_rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    ops = _mapping(family.get("operating_system"))
    actions = _mapping_list(ops.get("next_actions"))
    plan = [
        {
            "plan_id": "complete_docs_targets",
            "label": "Complete docs targets",
            "status": "ready" if _int(docs.get("doc_count")) else "needed",
            "detail": "Keep overview, architecture, runbook, references, decisions, and version notes attached to this project family.",
        },
        {
            "plan_id": "review_all_diff_units",
            "label": "Review all diff units",
            "status": "ready" if diff_rows else "single_root_or_needed",
            "detail": f"{len(diff_rows)} adjacent diff units are recorded for review and cleanup decisions.",
        },
        {
            "plan_id": "bind_project_chats",
            "label": "Bind project chats",
            "status": "needed",
            "detail": "Attach Codex/ChatGPT sessions to this domain/project/version after archive index generation.",
        },
        {
            "plan_id": "capture_preview_proof",
            "label": "Capture preview proof",
            "status": "needed",
            "detail": "Attach launch screenshots, runtime notes, and visual proof to the selected version.",
        },
    ]
    for action in actions[:4]:
        plan.append(
            {
                "plan_id": compact(action.get("action_id"), "next_action"),
                "label": compact(action.get("label"), "Next action"),
                "status": "candidate",
                "detail": compact(action.get("detail")),
            }
        )
    return plan


def _agent_workflows(family: Mapping[str, Any]) -> list[dict[str, Any]]:
    label = compact(family.get("label"), compact(family.get("family_id"), "project"))
    return [
        {
            "agent_lane": "domain_steward",
            "responsibility": "keep domain placement, current source, and lifecycle gates coherent",
            "trigger": f"{label} selected from domain page",
            "output": "domain/project status and next bounded action",
        },
        {
            "agent_lane": "developer_builder",
            "responsibility": "work from the current source path and avoid editing historical duplicate roots",
            "trigger": "project tab opens source or repair-and-launch action",
            "output": "bounded code change, tests, and launch status",
        },
        {
            "agent_lane": "diff_reviewer",
            "responsibility": "review every adjacent version diff before cleanup or promotion decisions",
            "trigger": "versioned family has diff units",
            "output": "diff explanation, risk, and version note",
        },
        {
            "agent_lane": "docs_curator",
            "responsibility": "bind README, architecture, runbook, references, decisions, screenshots, and notes to the exact project/version",
            "trigger": "docs gate is missing or stale",
            "output": "project docs health update",
        },
        {
            "agent_lane": "context_binder",
            "responsibility": "attach relevant Codex/ChatGPT sessions and context capsules to the project family",
            "trigger": "chat archive index becomes available",
            "output": "project-to-session binding map",
        },
    ]


def _chat_search_terms(domain: Mapping[str, Any], family: Mapping[str, Any]) -> list[str]:
    terms = [
        compact(domain.get("label")),
        compact(domain.get("domain_id")),
        compact(family.get("label")),
        compact(family.get("family_id")),
        compact(family.get("current_project_id")),
    ]
    current = _mapping(family.get("current"))
    terms.extend([compact(current.get("name")), compact(current.get("path"))])
    return [term for term in dict.fromkeys(terms) if term]


def _mirror_project_dossier(
    *,
    family: Mapping[str, Any],
    project_dossier: Mapping[str, Any],
    markdown: str,
    materialized_root: str,
    enabled: bool,
) -> dict[str, Any]:
    if not enabled or not materialized_root:
        return {}
    organized_path = compact(family.get("organized_path"))
    if not organized_path:
        return {}
    try:
        materialized = Path(materialized_root).expanduser().resolve()
        target = Path(organized_path).expanduser().resolve()
    except OSError:
        return {}
    if not _within(target, materialized):
        return {}
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / "CANON_DOSSIER.json"
    md_path = target / "CANON_DOSSIER.md"
    write_json(json_path, dict(project_dossier))
    md_path.write_text(markdown, encoding="utf-8")
    return {
        "status": "mirrored_to_organized_candidate",
        "json_path": json_path.as_posix(),
        "markdown_path": md_path.as_posix(),
    }


def _write_receipt(
    *,
    shell_root: Path,
    manifest_path: Path,
    generated_at: str,
    domain_count: int,
    project_dossier_count: int,
    mirrored_dossier_count: int,
) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    receipt_path = shell_root / PORTFOLIO_RECEIPTS_DIR / f"{stamp}_project_canon_dossier_receipt.json"
    receipt = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "created_at": generated_at,
        "manifest_path": manifest_path.as_posix(),
        "dossier_index_path": (shell_root / DOSSIER_INDEX).as_posix(),
        "domain_count": domain_count,
        "project_dossier_count": project_dossier_count,
        "mirrored_project_dossier_count": mirrored_dossier_count,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
    write_json(receipt_path, receipt)
    return receipt_path


def _index_markdown(index: Mapping[str, Any]) -> str:
    summary = _mapping(index.get("summary"))
    lines = [
        "# Project Canon Dossier Index",
        "",
        "Candidate generated reading layer for the Helixion Projects cockpit.",
        "",
        "## Summary",
        "",
        f"- domains: {_int(summary.get('domain_dossier_count'))}",
        f"- project families: {_int(summary.get('project_dossier_count'))}",
        f"- project roots: {_int(summary.get('project_root_count'))}",
        f"- versioned families: {_int(summary.get('versioned_family_count'))}",
        f"- diff manifests: {_int(summary.get('diff_manifest_count'))}",
        f"- docs discovered: {_int(summary.get('documentation_surface_count'))}",
        "",
        "## Cockpit Contract",
        "",
        "- Left drawer chooses domains.",
        "- Domain page shows internal projects and domain operating state.",
        "- Project clicks open project detail tabs within the same domain page.",
        "- Project tabs load version timeline, every diff unit, docs, launch/preview metadata, chats status, risks, and next actions.",
        "",
        "## Domains",
        "",
    ]
    for domain in _mapping_list(index.get("domains")):
        lines.append(
            f"- {compact(domain.get('label'))}: {_int(domain.get('family_count'))} families, "
            f"{_int(domain.get('diff_count'))} diffs, dossier `{compact(domain.get('domain_dossier_relpath'))}`"
        )
    lines.extend(["", "Authority: candidate projection only; no accepted-state, production, live-execution, or secrets authority."])
    return "\n".join(lines) + "\n"


def _domain_markdown(dossier: Mapping[str, Any]) -> str:
    domain = _mapping(dossier.get("domain"))
    counts = _mapping(dossier.get("counts"))
    ops = _mapping(dossier.get("operating_system"))
    lines = [
        f"# {compact(domain.get('label'), 'Project Domain')}",
        "",
        compact(domain.get("summary"), "No domain summary projected."),
        "",
        "## Canon State",
        "",
        f"- domain_id: `{compact(domain.get('domain_id'))}`",
        f"- posture: `{compact(ops.get('posture'), 'unknown')}`",
        f"- readiness: `{compact(ops.get('average_readiness_score'), '0')}`",
        f"- families: `{_int(counts.get('family_count'))}`",
        f"- roots: `{_int(counts.get('project_count'))}`",
        f"- versions: `{_int(counts.get('version_count'))}`",
        f"- diffs: `{_int(counts.get('diff_count'))}`",
        f"- docs / refs: `{_int(counts.get('doc_count'))}` / `{_int(counts.get('reference_count'))}`",
        "",
        "## Domain Workflow",
        "",
        "1. Choose this domain from the cockpit left drawer.",
        "2. Use the domain page to scan internal projects, board state, timeline, chats, diffs, docs, plans, and manage actions.",
        "3. Click a project to open its project-detail tab beside the domain tab.",
        "4. Keep launch/preview, diff history, docs, chats, and next action visible in the selected project tab.",
        "",
        "## Projects",
        "",
        "| Project | Posture | Score | Versions | Diffs | Docs | Launchable | Dossier |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for project in _mapping_list(dossier.get("projects")):
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(project.get("label")),
                    _cell(project.get("posture")),
                    str(_int(project.get("readiness_score"))),
                    str(_int(project.get("version_count"))),
                    str(_int(project.get("diff_count"))),
                    str(_int(project.get("doc_count"))),
                    str(_int(project.get("launchable_count"))),
                    f"`{_cell(project.get('project_dossier_markdown_relpath'))}`",
                ]
            )
            + " |"
        )
    lines.extend(["", "## Board", ""])
    for column in _mapping_list(dossier.get("board_columns")):
        lines.append(f"- {compact(column.get('label'), compact(column.get('column_id'), 'column'))}: {_int(column.get('count'))}")
    lines.extend(["", "## Risks", ""])
    risks = _mapping_list(dossier.get("top_risks"))
    if not risks:
        lines.append("- No top domain risks projected.")
    for risk in risks:
        lines.append(f"- {compact(risk.get('severity'), 'medium')}: {compact(risk.get('family_label'))} - {compact(risk.get('title'))}; {compact(risk.get('mitigation'))}")
    lines.extend(["", "## Agent Operating Loop", ""])
    for rhythm in _mapping_list(dossier.get("maintenance_rhythm")):
        lines.append(f"- {compact(rhythm.get('cadence'))}: {compact(rhythm.get('label'))} - {compact(rhythm.get('focus'))}")
    lines.extend(["", "## Authority", "", "Candidate projection only. No accepted-state, production, live-execution, or secrets authority."])
    return "\n".join(lines) + "\n"


def _project_markdown(dossier: Mapping[str, Any]) -> str:
    identity = _mapping(dossier.get("identity"))
    counts = _mapping(dossier.get("counts"))
    source = _mapping(dossier.get("source_organization"))
    timeline = _mapping(dossier.get("timeline"))
    diffs = _mapping(dossier.get("diff_evolution"))
    docs = _mapping(dossier.get("docs"))
    launch = _mapping(dossier.get("launch_preview"))
    chat = _mapping(dossier.get("chat_attachment"))
    ops = _mapping(dossier.get("operating_system"))
    lines = [
        f"# {compact(identity.get('label'), 'Project')} Canon Dossier",
        "",
        "Candidate project canon generated from the cached portfolio manifest.",
        "",
        "## Identity",
        "",
        f"- family_id: `{compact(identity.get('family_id'))}`",
        f"- domain: `{compact(identity.get('domain_label'))}` / `{compact(identity.get('domain_id'))}`",
        f"- posture: `{compact(ops.get('posture'), 'unknown')}`",
        f"- readiness: `{compact(ops.get('readiness_score'), '0')}`",
        f"- versions: `{_int(counts.get('version_count'))}`",
        f"- diffs: `{_int(counts.get('diff_count'))}`",
        f"- docs / refs: `{_int(counts.get('doc_count'))}` / `{_int(counts.get('reference_count'))}`",
        "",
        "## Source Organization",
        "",
        f"- current_source: `{compact(source.get('current_source'))}`",
        f"- current_source_copy: `{compact(source.get('current_source_copy'))}`",
        f"- organized_path: `{compact(source.get('organized_path'))}`",
        f"- lineage_status: `{compact(source.get('lineage_status'))}`",
        f"- policy: {compact(source.get('source_copy_policy'))}",
        f"- duplicate policy: {compact(source.get('duplicate_policy'))}",
        "",
        "## Timeline",
        "",
        "| Seq | Version | Branch | Current | Launch | Docs | Path |",
        "| ---: | --- | --- | --- | --- | ---: | --- |",
    ]
    for version in _mapping_list(timeline.get("versions")):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(_int(version.get("sequence"))),
                    _cell(version.get("label")),
                    _cell(version.get("branch_label")),
                    "yes" if version.get("is_current") else "",
                    "yes" if version.get("launchable") else "",
                    str(_int(_mapping(version.get("docs")).get("doc_count"))),
                    f"`{_cell(version.get('path'))}`",
                ]
            )
            + " |"
        )
    lines.extend(["", "## Diff Evolution", ""])
    diff_rows = _mapping_list(diffs.get("diffs"))
    if not diff_rows:
        lines.append("- No adjacent diff units projected; this is a single-root family or diff materialization is pending.")
    for diff in diff_rows:
        file_diff = _mapping(diff.get("file_diff"))
        lines.append(f"### {compact(diff.get('diff_id'), 'diff')}")
        lines.append("")
        lines.append(f"- from: `{compact(diff.get('from_label'))}` -> `{compact(diff.get('from_path'))}`")
        lines.append(f"- to: `{compact(diff.get('to_label'))}` -> `{compact(diff.get('to_path'))}`")
        lines.append(f"- status: `{compact(file_diff.get('status'), compact(diff.get('status')))}`")
        lines.append(f"- change explanation: {compact(diff.get('change_explanation'))}")
        if file_diff:
            lines.append(
                f"- counts: changed `{_int(file_diff.get('changed_count'))}`, added `{_int(file_diff.get('added_count'))}`, removed `{_int(file_diff.get('removed_count'))}`"
            )
            samples = _string_list(file_diff.get("changed_sample"))[:6] or _string_list(file_diff.get("added_sample"))[:6]
            if samples:
                lines.append(f"- sample files: {', '.join(f'`{sample}`' for sample in samples)}")
        lines.append("")
    lines.extend(["## Docs And References", ""])
    coverage = _mapping(docs.get("coverage"))
    lines.append(
        f"- coverage: readme `{bool(coverage.get('has_readme'))}`, architecture `{bool(coverage.get('has_architecture'))}`, runbook `{bool(coverage.get('has_runbook'))}`, references `{bool(coverage.get('has_references') or coverage.get('has_reference'))}`"
    )
    primary_docs = _mapping_list(docs.get("primary_docs"))
    if not primary_docs:
        lines.append("- No primary docs projected.")
    for doc in primary_docs[:16]:
        lines.append(f"- {compact(doc.get('kind'), 'doc')}: {compact(doc.get('title'), compact(doc.get('rel_path')))} - `{compact(doc.get('path'))}`")
    references = _mapping_list(docs.get("references"))
    if references:
        lines.extend(["", "References:"])
    for ref in references[:16]:
        lines.append(f"- {compact(ref.get('label'), compact(ref.get('type'), 'reference'))}: `{compact(ref.get('target'))}`")
    lines.extend(
        [
            "",
            "## Launch And Preview",
            "",
            f"- launchable: `{bool(launch.get('launchable'))}`",
            f"- status: `{compact(launch.get('status'))}`",
            f"- framework: `{compact(launch.get('framework'))}`",
            f"- project_path: `{compact(launch.get('project_path'))}`",
            f"- action_path: `{compact(launch.get('action_path'))}`",
            f"- preview href: `{compact(launch.get('open_href'))}`",
            "",
            "## Chats And Context Capsules",
            "",
            f"- chat binding status: `{compact(chat.get('status'))}`",
            f"- indexed chats: `{_int(chat.get('indexed_chat_count'))}`",
            f"- next action: {compact(chat.get('next_action'))}",
            f"- search terms: {', '.join(f'`{term}`' for term in _string_list(chat.get('search_terms'))[:12])}",
            "",
            "## Gates And Risks",
            "",
        ]
    )
    for gate in _mapping_list(dossier.get("quality_gates")):
        lines.append(f"- {compact(gate.get('label'))}: `{compact(gate.get('status'))}` - {compact(gate.get('evidence'))}")
    risks = _mapping_list(dossier.get("risk_register"))
    if risks:
        lines.extend(["", "Risks:"])
    for risk in risks:
        lines.append(f"- {compact(risk.get('severity'), 'medium')}: {compact(risk.get('title'))}; {compact(risk.get('mitigation'))}")
    lines.extend(["", "## Future Plan", ""])
    for plan in _mapping_list(dossier.get("future_plan")):
        lines.append(f"- {compact(plan.get('label'))}: `{compact(plan.get('status'))}` - {compact(plan.get('detail'))}")
    lines.extend(["", "## Agent Workflow", ""])
    for workflow in _mapping_list(dossier.get("agent_workflows")):
        lines.append(f"- {compact(workflow.get('agent_lane'))}: {compact(workflow.get('responsibility'))} Output: {compact(workflow.get('output'))}.")
    lines.extend(["", "## Authority", "", "Candidate projection only. No accepted-state, production, live-execution, or secrets authority."])
    return "\n".join(lines) + "\n"


def _authority() -> dict[str, bool]:
    return {
        "candidate_projection": True,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _mapping_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        values: Iterable[Any] = [value]
    elif isinstance(value, Iterable) and not isinstance(value, Mapping):
        values = value
    else:
        values = []
    return [compact(item) for item in values if compact(item)]


def _int(value: Any, fallback: int = 0) -> int:
    try:
        if value in (None, ""):
            return fallback
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _relpath(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _cell(value: Any) -> str:
    return compact(value).replace("|", "/").replace("\n", " ").replace("\r", " ")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate ION project canon dossiers from the portfolio manifest.")
    parser.add_argument("--root", default=".", help="ION active root")
    parser.add_argument("--no-mirror", action="store_true", help="Do not mirror project dossiers into the organized candidate folder")
    args = parser.parse_args(argv)
    result = build_project_canon_dossiers(args.root, mirror_to_organized=not args.no_mirror)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover - CLI helper
    raise SystemExit(main())
