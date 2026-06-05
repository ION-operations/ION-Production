"""Project/domain specialist context capsule generation.

The project canon dossier layer records what each project is. This module adds
the missing ION operating primitive: folder-bound specialist context capsules
and broker-shaped agent invocation packets for each domain and project family.
It prepares specialist work without pretending separate workers have already
run.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .ion_project_canon_dossier import (
    DOSSIER_INDEX,
    build_project_canon_dossiers,
)
from .ion_project_portfolio import (
    PORTFOLIO_DIR,
    PORTFOLIO_RECEIPTS_DIR,
    compact,
    read_json,
    slug,
    write_json,
)


SPECIALIST_DIR = PORTFOLIO_DIR / "specialists"
SPECIALIST_INDEX = SPECIALIST_DIR / "PROJECT_SPECIALIST_CONTEXT_INDEX.json"

INDEX_SCHEMA_ID = "ion.project_specialist_context_index.v1"
CAPSULE_SCHEMA_ID = "ion.project_specialist_context_capsule.v1"
PACKET_SCHEMA_ID = "ion.agent_invocation_packet.v1"
RECEIPT_SCHEMA_ID = "ion.project_specialist_context_receipt.v1"

DOMAIN_SPECIALIST_LANES = [
    {
        "lane_id": "domain_steward",
        "agent_role": "role.steward",
        "display_name": "Domain Steward",
        "objective": "Hold domain placement, project priority, gates, risks, and next-actions together.",
    },
    {
        "lane_id": "domain_context_cartographer",
        "agent_role": "role.context_cartographer",
        "display_name": "Domain Context Cartographer",
        "objective": "Maintain the domain capsule, context refs, docs, and project-to-chat binding map.",
    },
    {
        "lane_id": "domain_nemesis_reviewer",
        "agent_role": "role.nemesis",
        "display_name": "Domain Nemesis Reviewer",
        "objective": "Audit domain organization, duplicate collapse, missing docs, and false promotion claims.",
    },
]

PROJECT_SPECIALIST_LANES = [
    {
        "lane_id": "project_steward",
        "agent_role": "role.steward",
        "display_name": "Project Steward",
        "objective": "Keep the project family coherent: current source, lifecycle gates, risks, receipts, and next packet.",
    },
    {
        "lane_id": "project_context_cartographer",
        "agent_role": "role.context_cartographer",
        "display_name": "Project Context Cartographer",
        "objective": "Maintain the project capsule, context refs, session bindings, and required-read graph.",
    },
    {
        "lane_id": "project_mason_builder",
        "agent_role": "role.mason",
        "display_name": "Project Mason Builder",
        "objective": "Prepare bounded build/repair work from the current source only; never edit historical duplicate roots.",
    },
    {
        "lane_id": "project_diff_reviewer",
        "agent_role": "role.nemesis",
        "display_name": "Project Diff Reviewer",
        "objective": "Review every adjacent version diff before cleanup, promotion, or release decisions.",
    },
    {
        "lane_id": "project_docs_curator",
        "agent_role": "role.ionologist",
        "display_name": "Project Docs Curator",
        "objective": "Bind README, architecture, runbook, references, decisions, screenshots, and notes to the project/version.",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_project_specialist_contexts(
    root: str | Path = ".",
    *,
    mirror_to_organized: bool = True,
) -> dict[str, Any]:
    """Generate folder-bound specialist capsules and broker-shaped packets."""

    shell_root = Path(root).expanduser().resolve()
    dossier_index_path = shell_root / DOSSIER_INDEX
    dossier_index = read_json(dossier_index_path)
    if compact(dossier_index.get("schema_id")) != "ion.project_canon_dossier_index.v1":
        generated = build_project_canon_dossiers(shell_root, mirror_to_organized=mirror_to_organized)
        if generated.get("ok"):
            dossier_index = read_json(dossier_index_path)
    if compact(dossier_index.get("schema_id")) != "ion.project_canon_dossier_index.v1":
        return {
            "ok": False,
            "schema_id": INDEX_SCHEMA_ID,
            "status": "project_canon_dossier_index_missing",
            "dossier_index_path": dossier_index_path.as_posix(),
            "authority": _authority(),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        }

    generated_at = utc_now()
    output_root = shell_root / SPECIALIST_DIR
    output_root.mkdir(parents=True, exist_ok=True)
    materialized_root = compact(_mapping(dossier_index.get("organization_contract")).get("materialized_root"))

    domain_rows: list[dict[str, Any]] = []
    project_capsule_count = 0
    project_packet_count = 0
    mirrored_project_count = 0
    mirrored_domain_count = 0

    for domain in _mapping_list(dossier_index.get("domains")):
        domain_id = compact(domain.get("domain_id"), "domain")
        domain_slug = slug(domain_id, "domain")
        domain_dir = output_root / "domains" / domain_slug
        domain_dir.mkdir(parents=True, exist_ok=True)
        domain_capsule_path = domain_dir / "DOMAIN_SPECIALIST_CONTEXT_CAPSULE.json"
        domain_capsule_md_path = domain_dir / "DOMAIN_SPECIALIST_CONTEXT_CAPSULE.md"
        domain_packets_dir = domain_dir / "agent_packets"
        domain_packets_dir.mkdir(parents=True, exist_ok=True)
        domain_capsule = _domain_capsule(
            domain=domain,
            dossier_index=dossier_index,
            generated_at=generated_at,
            capsule_path=domain_capsule_path,
            capsule_md_path=domain_capsule_md_path,
            shell_root=shell_root,
        )
        write_json(domain_capsule_path, domain_capsule)
        domain_capsule_md_path.write_text(_domain_capsule_markdown(domain_capsule), encoding="utf-8")
        domain_packet_rows = _write_agent_packets(
            shell_root=shell_root,
            scope="domain",
            scope_id=domain_id,
            scope_label=compact(domain.get("label"), domain_id),
            lanes=DOMAIN_SPECIALIST_LANES,
            capsule=domain_capsule,
            packets_dir=domain_packets_dir,
            generated_at=generated_at,
        )
        domain_mirror = _mirror_domain_context(
            domain=domain,
            capsule=domain_capsule,
            markdown=_domain_capsule_markdown(domain_capsule),
            packet_rows=domain_packet_rows,
            materialized_root=materialized_root,
            enabled=mirror_to_organized,
        )
        if domain_mirror:
            mirrored_domain_count += 1

        project_rows: list[dict[str, Any]] = []
        for project in _mapping_list(domain.get("projects")):
            project_dossier = read_json(_record_path(shell_root, project, "project_dossier_path", "project_dossier_relpath"))
            family_id = compact(project.get("family_id"), "project")
            family_slug = slug(family_id, "project")
            project_dir = domain_dir / "projects" / family_slug
            project_packets_dir = project_dir / "agent_packets"
            project_packets_dir.mkdir(parents=True, exist_ok=True)
            project_capsule_path = project_dir / "PROJECT_SPECIALIST_CONTEXT_CAPSULE.json"
            project_capsule_md_path = project_dir / "PROJECT_SPECIALIST_CONTEXT_CAPSULE.md"
            project_capsule = _project_capsule(
                domain=domain,
                project=project,
                project_dossier=project_dossier,
                dossier_index=dossier_index,
                generated_at=generated_at,
                capsule_path=project_capsule_path,
                capsule_md_path=project_capsule_md_path,
                shell_root=shell_root,
            )
            write_json(project_capsule_path, project_capsule)
            project_capsule_md_path.write_text(_project_capsule_markdown(project_capsule), encoding="utf-8")
            packet_rows = _write_agent_packets(
                shell_root=shell_root,
                scope="project_family",
                scope_id=family_id,
                scope_label=compact(project.get("label"), family_id),
                lanes=PROJECT_SPECIALIST_LANES,
                capsule=project_capsule,
                packets_dir=project_packets_dir,
                generated_at=generated_at,
            )
            mirror = _mirror_project_context(
                project=project,
                project_dossier=project_dossier,
                capsule=project_capsule,
                markdown=_project_capsule_markdown(project_capsule),
                packet_rows=packet_rows,
                materialized_root=materialized_root,
                enabled=mirror_to_organized,
            )
            if mirror:
                mirrored_project_count += 1
            project_capsule_count += 1
            project_packet_count += len(packet_rows)
            project_rows.append(
                {
                    "family_id": family_id,
                    "label": compact(project.get("label"), family_id),
                    "domain_id": domain_id,
                    "specialist_capsule_path": project_capsule_path.as_posix(),
                    "specialist_capsule_relpath": _relpath(project_capsule_path, shell_root),
                    "specialist_capsule_markdown_path": project_capsule_md_path.as_posix(),
                    "specialist_capsule_markdown_relpath": _relpath(project_capsule_md_path, shell_root),
                    "agent_packet_count": len(packet_rows),
                    "agent_packets": packet_rows,
                    "organized_path": compact(project.get("organized_path")),
                    "mirror": mirror,
                }
            )

        domain_rows.append(
            {
                "domain_id": domain_id,
                "label": compact(domain.get("label"), domain_id),
                "specialist_capsule_path": domain_capsule_path.as_posix(),
                "specialist_capsule_relpath": _relpath(domain_capsule_path, shell_root),
                "specialist_capsule_markdown_path": domain_capsule_md_path.as_posix(),
                "specialist_capsule_markdown_relpath": _relpath(domain_capsule_md_path, shell_root),
                "agent_packet_count": len(domain_packet_rows),
                "agent_packets": domain_packet_rows,
                "project_specialist_capsules": project_rows,
                "mirror": domain_mirror,
            }
        )

    receipt_path = _write_receipt(
        shell_root=shell_root,
        generated_at=generated_at,
        domain_count=len(domain_rows),
        domain_packet_count=sum(_int(domain.get("agent_packet_count")) for domain in domain_rows),
        project_capsule_count=project_capsule_count,
        project_packet_count=project_packet_count,
        mirrored_domain_count=mirrored_domain_count,
        mirrored_project_count=mirrored_project_count,
    )
    index_path = shell_root / SPECIALIST_INDEX
    index = {
        "ok": True,
        "schema_id": INDEX_SCHEMA_ID,
        "generated_at": generated_at,
        "status": "project_specialist_contexts_ready",
        "dossier_index_path": dossier_index_path.as_posix(),
        "dossier_index_relpath": DOSSIER_INDEX.as_posix(),
        "specialist_root": output_root.as_posix(),
        "specialist_root_relpath": SPECIALIST_DIR.as_posix(),
        "index_path": index_path.as_posix(),
        "index_relpath": SPECIALIST_INDEX.as_posix(),
        "latest_receipt": {
            "path": receipt_path.as_posix(),
            "relpath": _relpath(receipt_path, shell_root),
            "created_at": generated_at,
        },
        "summary": {
            "domain_specialist_capsule_count": len(domain_rows),
            "domain_agent_packet_count": sum(_int(domain.get("agent_packet_count")) for domain in domain_rows),
            "project_specialist_capsule_count": project_capsule_count,
            "project_agent_packet_count": project_packet_count,
            "total_agent_packet_count": project_packet_count + sum(_int(domain.get("agent_packet_count")) for domain in domain_rows),
            "mirrored_domain_context_count": mirrored_domain_count,
            "mirrored_project_context_count": mirrored_project_count,
        },
        "specialist_contract": {
            "primitive": "one folder-bound specialist context capsule per domain and project family",
            "dispatch_posture": "agent invocation packets are prepared only; no worker is claimed spawned without broker/queue receipt",
            "project_folder_surface": ".ion/ION_CONTEXT_CAPSULE.yaml, .ion/AGENT.yaml, .ion/DOMAIN.yaml, .ion/RELATIONSHIPS.yaml, .ion/ACTIVE_CONTEXT_PACKAGE.md, .ion/SPECIALIST_AGENT_PACKETS.json",
            "carrier_feature_law": "CARRIER_FEATURES_MUST_MAP_TO_ION_OPS",
            "candidate_only": True,
        },
        "domains": domain_rows,
        "authority": _authority(),
        "non_claims": [
            "specialist capsules are candidate context packages, not accepted-state canon",
            "agent packets are prepared for bounded invocation and are not proof of worker execution",
            "no project specialist has production, live-execution, accepted-state, or secrets authority",
            "local writes require a future bounded workbench/agent packet with explicit approval and receipts",
        ],
    }
    write_json(index_path, index)
    (output_root / "README.md").write_text(_index_markdown(index), encoding="utf-8")
    return index


def _domain_capsule(
    *,
    domain: Mapping[str, Any],
    dossier_index: Mapping[str, Any],
    generated_at: str,
    capsule_path: Path,
    capsule_md_path: Path,
    shell_root: Path,
) -> dict[str, Any]:
    domain_id = compact(domain.get("domain_id"), "domain")
    label = compact(domain.get("label"), domain_id)
    context_refs = _compact_refs(
        [
            compact(domain.get("domain_dossier_relpath")),
            compact(domain.get("domain_dossier_markdown_relpath")),
            DOSSIER_INDEX.as_posix(),
        ]
    )
    return {
        "schema_id": CAPSULE_SCHEMA_ID,
        "generated_at": generated_at,
        "scope": "domain",
        "scope_id": domain_id,
        "label": label,
        "status": "domain_specialist_context_ready",
        "capsule_path": capsule_path.as_posix(),
        "capsule_relpath": _relpath(capsule_path, shell_root),
        "capsule_markdown_path": capsule_md_path.as_posix(),
        "capsule_markdown_relpath": _relpath(capsule_md_path, shell_root),
        "context_package": {
            "mode": "refs_and_inline_summary",
            "context_refs": context_refs,
            "required_reads": context_refs,
            "forbidden_reads": [".env", "secrets", "credentials"],
            "source_posture": "candidate",
            "inline_summary": (
                f"Domain specialist capsule for {label}. "
                f"Families: {_int(domain.get('family_count'))}; roots: {_int(domain.get('project_count'))}; "
                f"diffs: {_int(domain.get('diff_count'))}; docs: {_int(domain.get('doc_count'))}. "
                "Use the domain dossier as the domain operating board and route project-specific work to project capsules."
            ),
        },
        "domain_counts": {
            "families": _int(domain.get("family_count")),
            "project_roots": _int(domain.get("project_count")),
            "versions": _int(domain.get("version_count")),
            "diffs": _int(domain.get("diff_count")),
            "docs": _int(domain.get("doc_count")),
            "references": _int(domain.get("reference_count")),
        },
        "specialist_lanes": DOMAIN_SPECIALIST_LANES,
        "project_refs": [
            {
                "family_id": compact(project.get("family_id")),
                "label": compact(project.get("label")),
                "project_dossier_relpath": compact(project.get("project_dossier_relpath")),
                "organized_path": compact(project.get("organized_path")),
            }
            for project in _mapping_list(domain.get("projects"))
        ],
        "operating_rules": _operating_rules(),
        "authority": _authority(),
    }


def _project_capsule(
    *,
    domain: Mapping[str, Any],
    project: Mapping[str, Any],
    project_dossier: Mapping[str, Any],
    dossier_index: Mapping[str, Any],
    generated_at: str,
    capsule_path: Path,
    capsule_md_path: Path,
    shell_root: Path,
) -> dict[str, Any]:
    family_id = compact(project.get("family_id"), "project")
    label = compact(project.get("label"), family_id)
    identity = _mapping(project_dossier.get("identity"))
    counts = _mapping(project_dossier.get("counts"))
    source = _mapping(project_dossier.get("source_organization"))
    context_refs = _compact_refs(
        [
            compact(project.get("project_dossier_relpath")),
            compact(project.get("project_dossier_markdown_relpath")),
            compact(domain.get("domain_dossier_relpath")),
            DOSSIER_INDEX.as_posix(),
        ]
    )
    return {
        "schema_id": CAPSULE_SCHEMA_ID,
        "generated_at": generated_at,
        "scope": "project_family",
        "scope_id": family_id,
        "label": label,
        "status": "project_specialist_context_ready",
        "domain_id": compact(domain.get("domain_id")),
        "domain_label": compact(domain.get("label")),
        "capsule_path": capsule_path.as_posix(),
        "capsule_relpath": _relpath(capsule_path, shell_root),
        "capsule_markdown_path": capsule_md_path.as_posix(),
        "capsule_markdown_relpath": _relpath(capsule_md_path, shell_root),
        "context_package": {
            "mode": "refs_and_inline_summary",
            "context_refs": context_refs,
            "required_reads": context_refs,
            "forbidden_reads": [".env", "secrets", "credentials"],
            "source_posture": "candidate",
            "inline_summary": (
                f"Project specialist capsule for {label} in {compact(domain.get('label'))}. "
                f"Current source: {compact(source.get('current_source') or identity.get('current_path'), 'missing')}. "
                f"Versions: {_int(counts.get('version_count'))}; diffs: {_int(counts.get('diff_count'))}; "
                f"docs: {_int(counts.get('doc_count'))}; launchable: {_int(counts.get('launchable_count'))}. "
                "Operate from this project family capsule; historical roots are lineage witnesses, not edit targets."
            ),
        },
        "project_counts": {
            "project_roots": _int(counts.get("project_count")),
            "versions": _int(counts.get("version_count")),
            "branches": _int(counts.get("branch_count")),
            "diffs": _int(counts.get("diff_count")),
            "docs": _int(counts.get("doc_count")),
            "references": _int(counts.get("reference_count")),
            "launchable": _int(counts.get("launchable_count")),
        },
        "source_contract": {
            "current_source": compact(source.get("current_source") or identity.get("current_path")),
            "current_source_copy": compact(source.get("current_source_copy")),
            "organized_path": compact(source.get("organized_path") or project.get("organized_path")),
            "duplicate_policy": compact(source.get("duplicate_policy"), "historical full folders are lineage witnesses, not edit targets"),
            "write_policy": "no writes from this prepared capsule; future code work needs a bounded workbench/agent invocation receipt",
        },
        "specialist_lanes": PROJECT_SPECIALIST_LANES,
        "required_operating_surfaces": {
            "project_dossier": compact(project.get("project_dossier_relpath")),
            "project_dossier_markdown": compact(project.get("project_dossier_markdown_relpath")),
            "organized_project_folder": compact(project.get("organized_path")),
            "organized_context_package": f"{compact(project.get('organized_path'))}/.ion/ACTIVE_CONTEXT_PACKAGE.md" if compact(project.get("organized_path")) else "",
        },
        "chat_context_binding": {
            "status": "binding_pending",
            "next_action": "attach exact Codex/ChatGPT archive session IDs to this project capsule",
            "non_claim": "this capsule does not claim real chat attachment until archive binding proof exists",
        },
        "operating_rules": _operating_rules(),
        "authority": _authority(),
    }


def _write_agent_packets(
    *,
    shell_root: Path,
    scope: str,
    scope_id: str,
    scope_label: str,
    lanes: list[dict[str, str]],
    capsule: Mapping[str, Any],
    packets_dir: Path,
    generated_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lane in lanes:
        lane_id = compact(lane.get("lane_id"), "specialist")
        packet_path = packets_dir / f"{slug(lane_id, 'specialist')}.agent_invocation_packet.json"
        packet = _agent_packet(scope=scope, scope_id=scope_id, scope_label=scope_label, lane=lane, capsule=capsule, generated_at=generated_at)
        write_json(packet_path, packet)
        rows.append(
            {
                "lane_id": lane_id,
                "agent_role": compact(lane.get("agent_role")),
                "display_name": compact(lane.get("display_name")),
                "packet_path": packet_path.as_posix(),
                "packet_relpath": _relpath(packet_path, shell_root),
                "queued": False,
                "invocation_proof_status": "prepared_not_invoked",
            }
        )
    return rows


def _agent_packet(*, scope: str, scope_id: str, scope_label: str, lane: Mapping[str, Any], capsule: Mapping[str, Any], generated_at: str) -> dict[str, Any]:
    context = _mapping(capsule.get("context_package"))
    lane_id = compact(lane.get("lane_id"), "specialist")
    digest = hashlib.sha256(
        json.dumps(
            {
                "scope": scope,
                "scope_id": scope_id,
                "lane": lane_id,
                "capsule": capsule.get("capsule_relpath"),
                "generated_from": capsule.get("generated_at"),
            },
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()[:16]
    return {
        "schema_id": PACKET_SCHEMA_ID,
        "idempotency_key": f"project-specialist:{scope}:{slug(scope_id, 'scope')}:{lane_id}:{digest}",
        "created_by": "ion_project_specialist_context_builder",
        "agent_role": compact(lane.get("agent_role"), "role.context_cartographer"),
        "agent_display_name": compact(lane.get("display_name"), lane_id),
        "objective": (
            f"{compact(lane.get('objective'))} Scope: {scope} `{scope_label}`. "
            f"Use capsule `{compact(capsule.get('capsule_relpath'))}` and return proof-bearing findings only."
        ),
        "capsule_context": {
            "mode": "refs_and_inline_summary",
            "context_refs": _string_list(context.get("context_refs")),
            "inline_summary": compact(context.get("inline_summary")),
            "required_reads": _string_list(context.get("required_reads")),
            "forbidden_reads": _string_list(context.get("forbidden_reads")) or [".env", "secrets", "credentials"],
            "source_posture": "candidate",
        },
        "authority": {
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
            "local_write_authority": "none",
            "requires_operator_approval": False,
            "operator_approval_evidence": None,
            "allowed_paths": ["ION/05_context/current/project_portfolio/"],
            "forbidden_paths": [".env", "secrets", "credentials"],
            "hard_gates": [
                "access_credential",
                "broad_shell",
                "delete_file",
                "overwrite_protected_file",
                "production_deploy",
                "push_main",
            ],
        },
        "execution": {
            "backend": "codex_cli",
            "queue": False,
            "max_runtime_seconds": 900,
            "max_steps": 4,
            "stop_condition": "return proof packet, route question, or blocker",
        },
        "relay_policy": {
            "allow_relay_to_chatgpt": True,
            "allow_relay_to_operator": True,
            "ask_operator_on_authority_gap": True,
            "no_silent_authority_expansion": True,
        },
        "settlement": {
            "settlement_target": "project_specialist_context",
            "required_receipt_before_claiming_work": True,
        },
        "prepared_at": generated_at,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _mirror_domain_context(
    *,
    domain: Mapping[str, Any],
    capsule: Mapping[str, Any],
    markdown: str,
    packet_rows: list[Mapping[str, Any]],
    materialized_root: str,
    enabled: bool,
) -> dict[str, Any]:
    if not enabled or not materialized_root:
        return {}
    domain_folder = compact(domain.get("folder"))
    if not domain_folder:
        return {}
    target = Path(materialized_root).expanduser().resolve() / "domains" / domain_folder / ".ion"
    target.mkdir(parents=True, exist_ok=True)
    write_json(target / "DOMAIN_SPECIALIST_CONTEXT_CAPSULE.json", capsule)
    (target / "DOMAIN_SPECIALIST_CONTEXT_CAPSULE.md").write_text(markdown, encoding="utf-8")
    (target / "ION_CONTEXT_CAPSULE.yaml").write_text(_domain_context_yaml(domain, capsule), encoding="utf-8")
    write_json(target / "SPECIALIST_AGENT_PACKETS.json", {"packets": [dict(row) for row in packet_rows]})
    (target / "DOMAIN.yaml").write_text(_domain_yaml(domain, capsule), encoding="utf-8")
    return {"status": "mirrored_to_domain_folder", "path": target.as_posix()}


def _mirror_project_context(
    *,
    project: Mapping[str, Any],
    project_dossier: Mapping[str, Any],
    capsule: Mapping[str, Any],
    markdown: str,
    packet_rows: list[Mapping[str, Any]],
    materialized_root: str,
    enabled: bool,
) -> dict[str, Any]:
    organized_path = compact(project.get("organized_path"))
    if not enabled or not materialized_root or not organized_path:
        return {}
    try:
        materialized = Path(materialized_root).expanduser().resolve()
        organized = Path(organized_path).expanduser().resolve()
    except OSError:
        return {}
    if not _within(organized, materialized):
        return {}
    ion_dir = organized / ".ion"
    ion_dir.mkdir(parents=True, exist_ok=True)
    write_json(ion_dir / "PROJECT_SPECIALIST_CONTEXT_CAPSULE.json", capsule)
    (ion_dir / "PROJECT_SPECIALIST_CONTEXT_CAPSULE.md").write_text(markdown, encoding="utf-8")
    (ion_dir / "ACTIVE_CONTEXT_PACKAGE.md").write_text(markdown, encoding="utf-8")
    (ion_dir / "ION_CONTEXT_CAPSULE.yaml").write_text(_project_context_yaml(project, capsule), encoding="utf-8")
    write_json(ion_dir / "SPECIALIST_AGENT_PACKETS.json", {"packets": [dict(row) for row in packet_rows]})
    (ion_dir / "AGENT.yaml").write_text(_agent_yaml(project, capsule, packet_rows), encoding="utf-8")
    (ion_dir / "DOMAIN.yaml").write_text(_project_domain_yaml(project, capsule), encoding="utf-8")
    (ion_dir / "RELATIONSHIPS.yaml").write_text(_relationships_yaml(project, capsule, project_dossier), encoding="utf-8")
    return {"status": "mirrored_to_project_folder", "path": ion_dir.as_posix()}


def _domain_capsule_markdown(capsule: Mapping[str, Any]) -> str:
    counts = _mapping(capsule.get("domain_counts"))
    lines = [
        f"# {compact(capsule.get('label'), 'Domain')} Specialist Context Capsule",
        "",
        "Folder-bound specialist context for this project domain.",
        "",
        "## Scope",
        "",
        f"- scope: `{compact(capsule.get('scope'))}`",
        f"- scope_id: `{compact(capsule.get('scope_id'))}`",
        f"- families: `{_int(counts.get('families'))}`",
        f"- roots: `{_int(counts.get('project_roots'))}`",
        f"- versions: `{_int(counts.get('versions'))}`",
        f"- diffs: `{_int(counts.get('diffs'))}`",
        f"- docs / refs: `{_int(counts.get('docs'))}` / `{_int(counts.get('references'))}`",
        "",
        "## Specialist Lanes",
        "",
    ]
    for lane in _mapping_list(capsule.get("specialist_lanes")):
        lines.append(f"- {compact(lane.get('display_name'))} (`{compact(lane.get('agent_role'))}`): {compact(lane.get('objective'))}")
    lines.extend(["", "## Required Reads", ""])
    for ref in _string_list(_mapping(capsule.get("context_package")).get("required_reads")):
        lines.append(f"- `{ref}`")
    lines.extend(["", "## Project Capsules", ""])
    for project in _mapping_list(capsule.get("project_refs")):
        lines.append(f"- {compact(project.get('label'))}: `{compact(project.get('project_dossier_relpath'))}`")
    lines.extend(["", "## Authority", "", "Candidate context only. No production, live-execution, accepted-state, or secrets authority."])
    return "\n".join(lines) + "\n"


def _project_capsule_markdown(capsule: Mapping[str, Any]) -> str:
    counts = _mapping(capsule.get("project_counts"))
    source = _mapping(capsule.get("source_contract"))
    context = _mapping(capsule.get("context_package"))
    lines = [
        f"# {compact(capsule.get('label'), 'Project')} Specialist Context Capsule",
        "",
        "This is the folder-bound project specialist capsule. It is the default context package for specialist work on this project family.",
        "",
        "## Scope",
        "",
        f"- scope: `{compact(capsule.get('scope'))}`",
        f"- family_id: `{compact(capsule.get('scope_id'))}`",
        f"- domain: `{compact(capsule.get('domain_label'))}` / `{compact(capsule.get('domain_id'))}`",
        f"- roots: `{_int(counts.get('project_roots'))}`",
        f"- versions: `{_int(counts.get('versions'))}`",
        f"- diffs: `{_int(counts.get('diffs'))}`",
        f"- docs / refs: `{_int(counts.get('docs'))}` / `{_int(counts.get('references'))}`",
        f"- launchable: `{_int(counts.get('launchable'))}`",
        "",
        "## Source Contract",
        "",
        f"- current_source: `{compact(source.get('current_source'))}`",
        f"- current_source_copy: `{compact(source.get('current_source_copy'))}`",
        f"- organized_path: `{compact(source.get('organized_path'))}`",
        f"- duplicate_policy: {compact(source.get('duplicate_policy'))}",
        f"- write_policy: {compact(source.get('write_policy'))}",
        "",
        "## Specialist Agents",
        "",
    ]
    for lane in _mapping_list(capsule.get("specialist_lanes")):
        lines.append(f"- {compact(lane.get('display_name'))} (`{compact(lane.get('agent_role'))}`): {compact(lane.get('objective'))}")
    lines.extend(["", "## Required Reads", ""])
    for ref in _string_list(context.get("required_reads")):
        lines.append(f"- `{ref}`")
    lines.extend(
        [
            "",
            "## Chat And Context Binding",
            "",
            f"- status: `{compact(_mapping(capsule.get('chat_context_binding')).get('status'))}`",
            f"- next_action: {compact(_mapping(capsule.get('chat_context_binding')).get('next_action'))}",
            "",
            "## Operating Rules",
            "",
        ]
    )
    for rule in _string_list(capsule.get("operating_rules")):
        lines.append(f"- {rule}")
    lines.extend(["", "## Authority", "", "Candidate context only. No production, live-execution, accepted-state, or secrets authority."])
    return "\n".join(lines) + "\n"


def _index_markdown(index: Mapping[str, Any]) -> str:
    summary = _mapping(index.get("summary"))
    lines = [
        "# Project Specialist Context Index",
        "",
        "Prepared folder-bound specialist context capsules and agent invocation packets for every project domain and project family.",
        "",
        "## Summary",
        "",
        f"- domain capsules: {_int(summary.get('domain_specialist_capsule_count'))}",
        f"- project capsules: {_int(summary.get('project_specialist_capsule_count'))}",
        f"- domain agent packets: {_int(summary.get('domain_agent_packet_count'))}",
        f"- project agent packets: {_int(summary.get('project_agent_packet_count'))}",
        f"- mirrored project folders: {_int(summary.get('mirrored_project_context_count'))}",
        "",
        "## Contract",
        "",
        "- One folder-bound specialist capsule per domain and project family.",
        "- Agent packets are prepared, not invoked.",
        "- Actual specialist worker claims require broker/queue receipts.",
        "- Project folders carry `.ion/ACTIVE_CONTEXT_PACKAGE.md` as their default capsule.",
        "",
    ]
    for domain in _mapping_list(index.get("domains")):
        lines.append(f"- {compact(domain.get('label'))}: `{compact(domain.get('specialist_capsule_relpath'))}`")
    lines.extend(["", "Authority: candidate projection only."])
    return "\n".join(lines) + "\n"


def _agent_yaml(project: Mapping[str, Any], capsule: Mapping[str, Any], packet_rows: list[Mapping[str, Any]]) -> str:
    lines = [
        "schema_id: ion.project_folder_agent_descriptor.v1",
        f"family_id: {json.dumps(compact(project.get('family_id')))}",
        f"label: {json.dumps(compact(project.get('label')))}",
        f"domain_id: {json.dumps(compact(capsule.get('domain_id')))}",
        f"context_capsule: {json.dumps('PROJECT_SPECIALIST_CONTEXT_CAPSULE.md')}",
        f"active_context_package: {json.dumps('ACTIVE_CONTEXT_PACKAGE.md')}",
        "specialist_agents:",
    ]
    for row in packet_rows:
        lines.extend(
            [
                f"  - lane_id: {json.dumps(compact(row.get('lane_id')))}",
                f"    agent_role: {json.dumps(compact(row.get('agent_role')))}",
                f"    packet_relpath: {json.dumps(compact(row.get('packet_relpath')))}",
                "    invocation_proof_status: prepared_not_invoked",
            ]
        )
    lines.extend(
        [
            "authority:",
            "  candidate_projection: true",
            "  accepted_state_authority: false",
            "  production_authority: false",
            "  live_execution_authority: false",
            "  secrets_authority: false",
        ]
    )
    return "\n".join(lines) + "\n"


def _project_context_yaml(project: Mapping[str, Any], capsule: Mapping[str, Any]) -> str:
    context = _mapping(capsule.get("context_package"))
    lines = [
        "schema_id: ion.project_folder_context_capsule.v1",
        f"family_id: {json.dumps(compact(project.get('family_id')))}",
        f"label: {json.dumps(compact(project.get('label')))}",
        f"domain_id: {json.dumps(compact(capsule.get('domain_id')))}",
        "context_package:",
        "  mode: refs_and_inline_summary",
        "  required_reads:",
    ]
    for ref in _string_list(context.get("required_reads")):
        lines.append(f"    - {json.dumps(ref)}")
    lines.extend(
        [
            "  forbidden_reads:",
        ]
    )
    for ref in _string_list(context.get("forbidden_reads")):
        lines.append(f"    - {json.dumps(ref)}")
    lines.extend(
        [
            f"  inline_summary: {json.dumps(compact(context.get('inline_summary')))}",
            "authority:",
            "  candidate_projection: true",
            "  accepted_state_authority: false",
            "  production_authority: false",
            "  live_execution_authority: false",
            "  secrets_authority: false",
        ]
    )
    return "\n".join(lines) + "\n"


def _domain_context_yaml(domain: Mapping[str, Any], capsule: Mapping[str, Any]) -> str:
    context = _mapping(capsule.get("context_package"))
    lines = [
        "schema_id: ion.project_domain_context_capsule.v1",
        f"domain_id: {json.dumps(compact(domain.get('domain_id')))}",
        f"label: {json.dumps(compact(domain.get('label')))}",
        "context_package:",
        "  mode: refs_and_inline_summary",
        "  required_reads:",
    ]
    for ref in _string_list(context.get("required_reads")):
        lines.append(f"    - {json.dumps(ref)}")
    lines.extend(
        [
            f"  inline_summary: {json.dumps(compact(context.get('inline_summary')))}",
            "authority:",
            "  candidate_projection: true",
            "  accepted_state_authority: false",
            "  production_authority: false",
            "  live_execution_authority: false",
            "  secrets_authority: false",
        ]
    )
    return "\n".join(lines) + "\n"


def _domain_yaml(domain: Mapping[str, Any], capsule: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "schema_id: ion.project_domain_specialist_descriptor.v1",
            f"domain_id: {json.dumps(compact(domain.get('domain_id')))}",
            f"label: {json.dumps(compact(domain.get('label')))}",
            f"context_capsule: {json.dumps('DOMAIN_SPECIALIST_CONTEXT_CAPSULE.md')}",
            "authority:",
            "  candidate_projection: true",
            "  accepted_state_authority: false",
            "  production_authority: false",
            "  live_execution_authority: false",
            "  secrets_authority: false",
        ]
    ) + "\n"


def _project_domain_yaml(project: Mapping[str, Any], capsule: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "schema_id: ion.project_folder_domain_descriptor.v1",
            f"domain_id: {json.dumps(compact(capsule.get('domain_id')))}",
            f"domain_label: {json.dumps(compact(capsule.get('domain_label')))}",
            f"family_id: {json.dumps(compact(project.get('family_id')))}",
            f"project_label: {json.dumps(compact(project.get('label')))}",
        ]
    ) + "\n"


def _relationships_yaml(project: Mapping[str, Any], capsule: Mapping[str, Any], project_dossier: Mapping[str, Any]) -> str:
    required = _mapping(capsule.get("required_operating_surfaces"))
    return "\n".join(
        [
            "schema_id: ion.project_folder_relationships.v1",
            f"family_id: {json.dumps(compact(project.get('family_id')))}",
            "relationships:",
            f"  project_dossier: {json.dumps(compact(required.get('project_dossier')))}",
            f"  project_dossier_markdown: {json.dumps(compact(required.get('project_dossier_markdown')))}",
            f"  organized_project_folder: {json.dumps(compact(required.get('organized_project_folder')))}",
            f"  current_source: {json.dumps(compact(_mapping(project_dossier.get('source_organization')).get('current_source')))}",
            f"  current_source_copy: {json.dumps(compact(_mapping(project_dossier.get('source_organization')).get('current_source_copy')))}",
            "non_claims:",
            "  - agent packets are prepared_not_invoked",
            "  - chat binding remains binding_pending until archive proof exists",
        ]
    ) + "\n"


def _write_receipt(
    *,
    shell_root: Path,
    generated_at: str,
    domain_count: int,
    domain_packet_count: int,
    project_capsule_count: int,
    project_packet_count: int,
    mirrored_domain_count: int,
    mirrored_project_count: int,
) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = shell_root / PORTFOLIO_RECEIPTS_DIR / f"{stamp}_project_specialist_context_receipt.json"
    receipt = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "created_at": generated_at,
        "specialist_index_path": (shell_root / SPECIALIST_INDEX).as_posix(),
        "domain_specialist_capsule_count": domain_count,
        "domain_agent_packet_count": domain_packet_count,
        "project_specialist_capsule_count": project_capsule_count,
        "project_agent_packet_count": project_packet_count,
        "mirrored_domain_context_count": mirrored_domain_count,
        "mirrored_project_context_count": mirrored_project_count,
        "agent_invocation_status": "prepared_not_invoked",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
    write_json(path, receipt)
    return path


def _operating_rules() -> list[str]:
    return [
        "operate from the folder-bound capsule, not generic memory",
        "read the project/domain dossier before making claims",
        "current source is the work target; historical roots are lineage witnesses",
        "agent packets are prepared_not_invoked until broker/queue receipts exist",
        "no accepted-state, production, live-execution, or secrets authority",
        "write work requires a future bounded patch/workbench packet and receipt",
    ]


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
        values = [value]
    elif isinstance(value, (list, tuple)):
        values = value
    else:
        values = []
    return [compact(item) for item in values if compact(item)]


def _compact_refs(values: list[str]) -> list[str]:
    return [value for value in dict.fromkeys(compact(item) for item in values) if value]


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


def _record_path(shell_root: Path, row: Mapping[str, Any], path_key: str, relpath_key: str) -> Path:
    value = compact(row.get(path_key))
    if value:
        path = Path(value).expanduser()
        return path if path.is_absolute() else shell_root / path
    relvalue = compact(row.get(relpath_key))
    return shell_root / relvalue if relvalue else shell_root / "__missing_project_dossier__.json"


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate project specialist context capsules and prepared agent packets.")
    parser.add_argument("--root", default=".", help="ION active root")
    parser.add_argument("--no-mirror", action="store_true", help="Do not mirror .ion context packages into organized project folders")
    args = parser.parse_args(argv)
    result = build_project_specialist_contexts(args.root, mirror_to_organized=not args.no_mirror)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover - CLI helper
    raise SystemExit(main())
