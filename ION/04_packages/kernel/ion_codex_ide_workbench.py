"""Read-only Codex IDE workbench projection.

This module gives `/cockpit#ide` a first-class model instead of reusing the
Codex chat model implicitly. The model is a projection surface only: it may
describe context bindings, bridge artifacts, tabs, and safe capabilities, but it
does not grant file mutation, production, live execution, accepted-state, or
secrets authority.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .ion_cockpit_view_model import build_cockpit_surface_view_model, utc_now

SCHEMA_ID = "ion.codex_ide_workbench_model.v0_1"
CONTEXT_REGISTRY_SCHEMA_ID = "ion.codex_ide_context_registry.v0_1"
WORKSPACE_SESSION_SCHEMA_ID = "ion.codex_ide_workspace_session.v0_1"


def build_codex_ide_workbench_model(ion_root: str | Path = ".") -> dict[str, Any]:
    """Return the shell-compatible IDE surface model.

    The outer object intentionally remains an `ion.cockpit_surface_view_model`
    so the existing React shell can render it without a parallel app contract.
    The IDE-specific contract lives at `codex_ide_workbench`.
    """

    root = Path(ion_root).expanduser().resolve()
    model = dict(build_cockpit_surface_view_model(root, surface="codex"))
    ide_workbench = build_codex_ide_workbench_surface(root, runtime_model=model)
    runtime = _record(model.get("runtime"))
    top_bar = _record(model.get("top_bar"))
    registry = _record(ide_workbench.get("context_registry"))

    model.update(
        {
            "surface": "ide",
            "codex_ide_workbench": ide_workbench,
            "runtime": {
                **runtime,
                "version": "V0_1_CODEX_IDE_WORKBENCH_SURFACE",
                "ide_surface": True,
            },
            "top_bar": {
                **top_bar,
                "codex_ide_workbench_status": ide_workbench.get("status"),
                "codex_ide_context_binding_status": registry.get("status"),
                "codex_ide_context_system_count": registry.get("context_system_count", 0),
                "codex_ide_bridge_status": registry.get("bridge_status"),
            },
        }
    )
    return model


def build_codex_ide_workbench_surface(
    ion_root: str | Path = ".",
    *,
    runtime_model: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(ion_root).expanduser().resolve()
    model = _record(runtime_model)
    if not model:
        model = build_cockpit_surface_view_model(root, surface="codex")

    chat = _record(model.get("codex_capsule_chat"))
    cli = _record(model.get("codex_cli_workbench"))
    rollback = _record(model.get("codex_git_rollback"))
    current_worktree = _record(rollback.get("current_worktree"))
    diff_stats = _record(current_worktree.get("diff_stats"))
    file_edits = _records(current_worktree.get("file_edits"))
    context_surfaces = _records(_record(cli.get("context")).get("surfaces"))
    bridge_artifact = _read_latest_bridge_artifact(root, chat)
    context_registry = _build_context_registry(model, bridge_artifact=bridge_artifact)
    open_tabs = _build_open_tabs(bridge_artifact, file_edits=file_edits, context_surfaces=context_surfaces)
    selected_path = _text(
        _record(context_registry.get("latest_bridge")).get("selected_path")
        or _record(bridge_artifact.get("snapshot")).get("selected_path")
        or (open_tabs[0].get("path") if open_tabs else ""),
        "workspace",
    )

    return {
        "schema_id": SCHEMA_ID,
        "generated_at": utc_now(),
        "status": "ready",
        "root": root.as_posix(),
        "surface": "ide",
        "workspace_session": {
            "schema_id": WORKSPACE_SESSION_SCHEMA_ID,
            "session_id": "ide.current",
            "root": root.as_posix(),
            "active_chat_context_binding_id": context_registry.get("active_binding_id") or "",
            "active_bridge_id": _record(context_registry.get("latest_bridge")).get("bridge_id") or "",
            "active_branch_ids": _record(context_registry.get("latest_bridge")).get("branch_ids") or [],
            "selected_path": selected_path,
            "open_tabs": open_tabs,
            "preview_state_ref": "",
            "diagnostics_ref": "",
            "symbol_index_refs": [],
            "authority": _authority(),
        },
        "context_registry": context_registry,
        "editor": {
            "schema_id": "ion.codex_ide_editor_projection.v0_1",
            "engine": "projected_shell",
            "monaco_present": False,
            "editor_buffer_model_present": False,
            "open_tab_count": len(open_tabs),
            "selected_path": selected_path,
            "read_only_projection": True,
            "next_engine": "monaco_adapter_after_context_model",
        },
        "worktree": {
            "schema_id": "ion.codex_ide_worktree_projection.v0_1",
            "status": _text(current_worktree.get("status") or _record(rollback.get("summary")).get("status"), "projected"),
            "file_count": _int(diff_stats.get("file_count")) or len(file_edits),
            "insertions": _int(diff_stats.get("insertions")),
            "deletions": _int(diff_stats.get("deletions")),
            "file_edits": file_edits[:40],
            "authority": _authority(),
        },
        "capability_registry": _capability_registry(),
        "authority": _authority(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _build_context_registry(
    runtime_model: Mapping[str, Any],
    *,
    bridge_artifact: Mapping[str, Any],
) -> dict[str, Any]:
    chat = _record(runtime_model.get("codex_capsule_chat"))
    chat_context = _record(chat.get("chat_context"))
    bridge_surface = _record(chat.get("ide_context_bridge"))
    latest_bridge = _record(bridge_surface.get("latest_bridge"))
    bindings = _records(chat_context.get("bindings"))
    active_binding_id = _text(chat_context.get("active_binding_id"))
    active_binding = _record(chat_context.get("active_binding"))
    if not active_binding and active_binding_id:
        active_binding = next((binding for binding in bindings if binding.get("binding_id") == active_binding_id), {})
    binding_ids = [_text(binding.get("binding_id")) for binding in bindings if _text(binding.get("binding_id"))]
    duplicate_binding_ids = sorted({binding_id for binding_id in binding_ids if binding_ids.count(binding_id) > 1})

    bridge_count = _int(bridge_surface.get("bridge_count")) or len(_records(bridge_surface.get("bridges"))) or (1 if latest_bridge else 0)
    bridge_status = "mounted" if latest_bridge else "none_mounted"
    context_systems = _context_system_rows(runtime_model, active_binding_id=active_binding_id, bridge_artifact=bridge_artifact)
    warnings: list[dict[str, Any]] = []
    if not active_binding:
        warnings.append(
            {
                "warning_id": "ide.no_active_chat_context_binding",
                "severity": "warning",
                "message": "No active chat context binding is mounted for this IDE chat surface.",
                "authority_action": "create_or_select_context_binding_before_new_agent_work",
            }
        )
    if not latest_bridge:
        warnings.append(
            {
                "warning_id": "ide.no_context_bridge",
                "severity": "info",
                "message": "No IDE bridge artifact is mounted yet; send one IDE chat turn to create it.",
                "authority_action": "read_only_bridge_creation",
            }
        )
    if duplicate_binding_ids:
        warnings.append(
            {
                "warning_id": "ide.duplicate_context_binding_ids",
                "severity": "blocked",
                "message": "Duplicate chat context binding ids were projected.",
                "duplicate_binding_ids": duplicate_binding_ids,
                "authority_action": "context_identity_repair_required",
            }
        )

    return {
        "schema_id": CONTEXT_REGISTRY_SCHEMA_ID,
        "status": "active_binding_mounted" if active_binding else "no_active_binding",
        "active_binding_id": active_binding_id,
        "active_binding": active_binding or None,
        "binding_count": len(bindings),
        "bindings": [_compact_binding(binding, active_binding_id=active_binding_id) for binding in bindings[:80]],
        "binding_ids_unique": len(binding_ids) == len(set(binding_ids)),
        "duplicate_binding_ids": duplicate_binding_ids,
        "bridge_status": bridge_status,
        "bridge_count": bridge_count,
        "latest_bridge": latest_bridge or None,
        "latest_bridge_artifact_present": bool(bridge_artifact),
        "context_system_count": len(context_systems),
        "context_systems": context_systems,
        "warnings": warnings,
        "warning_count": len(warnings),
        "context_policy": {
            "context_drawer_is_canonical_surface": True,
            "chat_body_must_not_embed_context_browser": True,
            "capsule_mini_are_floor_not_chat_identity": True,
            "agent_context_binding_must_be_unique": True,
            "shared_parent_context_is_inherited_evidence_only": True,
            "ide_bridge_is_read_only_projection": True,
            "settlement_required_for_shared_context_update": True,
        },
        "authority": _authority(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _context_system_rows(
    runtime_model: Mapping[str, Any],
    *,
    active_binding_id: str,
    bridge_artifact: Mapping[str, Any],
) -> list[dict[str, Any]]:
    chat = _record(runtime_model.get("codex_capsule_chat"))
    chat_context = _record(chat.get("chat_context"))
    agent_control = _record(runtime_model.get("agent_control_plane"))
    graph = _record(runtime_model.get("context_package_graph"))
    packages = _records(_record(_record(runtime_model.get("docs_projects_packages")).get("context_packages")).get("packages"))
    rows: list[dict[str, Any]] = []

    for index, binding in enumerate(_records(chat_context.get("bindings"))):
        rows.append(_binding_context_row(binding, index=index, active_binding_id=active_binding_id))

    for index, fresh_chat in enumerate(_records(chat.get("fresh_agent_capsule_chats"))):
        binding = _record(fresh_chat.get("chat_context_binding"))
        row = _binding_context_row(binding, index=index, active_binding_id=active_binding_id)
        row.update(
            {
                "row_id": f"fresh_agent:{_text(fresh_chat.get('fresh_chat_id'), str(index))}",
                "context_kind": "fresh_agent_capsule_chat",
                "title": _text(fresh_chat.get("title") or row.get("title"), f"fresh agent {index + 1}"),
                "path": _text(fresh_chat.get("target_ref") or fresh_chat.get("target_path") or row.get("path")),
                "fresh_chat_id": _text(fresh_chat.get("fresh_chat_id")),
            }
        )
        rows.append(row)

    for index, agent in enumerate(_records(agent_control.get("agents"))):
        owner = _text(agent.get("agent_id") or agent.get("role_id") or agent.get("display_name"), f"agent-{index}")
        path = _text(agent.get("active_context_package") or agent.get("context_package_path") or agent.get("context_load_receipt_path") or agent.get("mount_receipt_path"))
        if not path and not _text(agent.get("context_system_status")):
            continue
        rows.append(
            {
                "schema_id": "ion.codex_ide_context_system_row.v0_1",
                "row_id": f"agent:{owner}:{index}",
                "context_kind": "agent_context_projection",
                "system_id": _text(agent.get("domain_id") or agent.get("registry_primary_domain"), "domain.pending"),
                "variant_id": _text(agent.get("role_id") or owner),
                "binding_id": "",
                "owner_agent_id": owner,
                "owner_chat_id": "",
                "title": _text(agent.get("display_name") or agent.get("role_id") or owner),
                "status": _text(agent.get("context_system_status") or agent.get("roster_status") or agent.get("status"), "projected"),
                "path": path,
                "active": False,
                "shared_parent": False,
                "materialization_state": "projected",
                "authority": _authority(),
            }
        )

    for index, branch in enumerate(_records(graph.get("branches"))):
        path = _text(branch.get("path") or branch.get("candidate_capsule_path") or branch.get("accepted_capsule_path"))
        rows.append(
            {
                "schema_id": "ion.codex_ide_context_system_row.v0_1",
                "row_id": f"context_branch:{path or index}",
                "context_kind": "context_package_branch",
                "system_id": _text(branch.get("package_type") or branch.get("classification"), "context_package"),
                "variant_id": _text(branch.get("maturity_level") or branch.get("promotion_readiness"), "projected"),
                "binding_id": "",
                "owner_agent_id": "",
                "owner_chat_id": "",
                "title": _short(path or f"context branch {index + 1}"),
                "status": _text(branch.get("promotion_readiness") or ("candidate_valid" if branch.get("candidate_valid") else ""), "projected"),
                "path": path,
                "active": False,
                "shared_parent": True,
                "materialization_state": "projected",
                "authority": _authority(),
            }
        )

    for index, package in enumerate(packages):
        package_id = _text(package.get("package_id") or package.get("label") or package.get("title"), f"package-{index}")
        rows.append(
            {
                "schema_id": "ion.codex_ide_context_system_row.v0_1",
                "row_id": f"context_package:{package_id}:{index}",
                "context_kind": "context_package_definition",
                "system_id": package_id,
                "variant_id": _text(package.get("context_type") or package.get("load_policy"), "package"),
                "binding_id": "",
                "owner_agent_id": "",
                "owner_chat_id": "",
                "title": package_id,
                "status": _text(package.get("load_policy") or package.get("status"), "available"),
                "path": " / ".join(_texts(package.get("path_refs"))) or _text(package.get("path") or package.get("source")),
                "active": False,
                "shared_parent": True,
                "materialization_state": "available",
                "authority": _authority(),
            }
        )

    snapshot = _record(bridge_artifact.get("snapshot"))
    for index, bridge_system in enumerate(_records(snapshot.get("context_systems"))):
        row_id = _text(bridge_system.get("id") or bridge_system.get("path") or bridge_system.get("title"), f"bridge-system-{index}")
        rows.append(
            {
                "schema_id": "ion.codex_ide_context_system_row.v0_1",
                "row_id": f"bridge:{row_id}:{index}",
                "context_kind": "ide_bridge_context_ref",
                "system_id": _text(bridge_system.get("kind") or bridge_system.get("source"), "bridge_context"),
                "variant_id": _text(bridge_system.get("status"), "bridge"),
                "binding_id": active_binding_id,
                "owner_agent_id": "",
                "owner_chat_id": active_binding_id,
                "title": _text(bridge_system.get("title") or row_id),
                "status": _text(bridge_system.get("status"), "bridged"),
                "path": _text(bridge_system.get("path")),
                "active": False,
                "shared_parent": True,
                "materialization_state": "bridged",
                "authority": _authority(),
            }
        )

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        key = _text(row.get("row_id")) or json.dumps(row, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped[:160]


def _binding_context_row(binding: Mapping[str, Any], *, index: int, active_binding_id: str) -> dict[str, Any]:
    binding_id = _text(binding.get("binding_id"), f"binding-{index}")
    agent_identity = _record(binding.get("agent_identity"))
    minimum = _record(binding.get("minimum_context"))
    ide_bridge = _record(binding.get("ide_context_bridge"))
    owner_agent_id = _text(agent_identity.get("agent_instance_id") or agent_identity.get("agent_true_name") or binding.get("role_id"))
    return {
        "schema_id": "ion.codex_ide_context_system_row.v0_1",
        "row_id": f"binding:{binding_id}",
        "context_kind": "chat_context_binding",
        "system_id": _text(binding.get("domain_id"), "domain.pending"),
        "variant_id": _text(binding.get("branch_id"), "branch.pending"),
        "binding_id": binding_id,
        "owner_agent_id": owner_agent_id,
        "owner_chat_id": _text(binding.get("source_turn_id")),
        "title": _text(binding.get("branch_title") or binding_id),
        "status": "active" if binding_id == active_binding_id else "available",
        "path": _text(minimum.get("capsule_ref") or binding.get("context_package_ref")),
        "active": binding_id == active_binding_id,
        "shared_parent": False,
        "materialization_state": "mounted" if binding_id == active_binding_id else "ready",
        "mounted_context_refs": _texts(binding.get("mounted_context_refs"))[:12],
        "branch_context_refs": _texts(binding.get("branch_context_refs"))[:12],
        "context_floor_refs": _texts(binding.get("context_floor_refs"))[:12],
        "ide_bridge_artifact_ref": _text(ide_bridge.get("artifact_ref")),
        "role_id": _text(binding.get("role_id")),
        "domain_id": _text(binding.get("domain_id")),
        "authority": _authority(),
    }


def _compact_binding(binding: Mapping[str, Any], *, active_binding_id: str) -> dict[str, Any]:
    agent_identity = _record(binding.get("agent_identity"))
    ide_bridge = _record(binding.get("ide_context_bridge"))
    binding_id = _text(binding.get("binding_id"))
    return {
        "binding_id": binding_id,
        "active": bool(binding_id and binding_id == active_binding_id),
        "context_version": _text(binding.get("context_version")),
        "lane_id": _text(binding.get("lane_id")),
        "source_turn_id": _text(binding.get("source_turn_id")),
        "domain_id": _text(binding.get("domain_id")),
        "role_id": _text(binding.get("role_id")),
        "branch_id": _text(binding.get("branch_id")),
        "branch_title": _text(binding.get("branch_title")),
        "owner_agent_id": _text(agent_identity.get("agent_instance_id")),
        "agent_true_name": _text(agent_identity.get("agent_true_name")),
        "mounted_context_ref_count": len(_texts(binding.get("mounted_context_refs"))),
        "branch_context_ref_count": len(_texts(binding.get("branch_context_refs"))),
        "ide_bridge_artifact_ref": _text(ide_bridge.get("artifact_ref")),
        "ide_context_branch_ids": _texts(binding.get("ide_context_branch_ids")),
        "authority": _authority(),
    }


def _read_latest_bridge_artifact(root: Path, chat: Mapping[str, Any]) -> dict[str, Any]:
    bridge_surface = _record(chat.get("ide_context_bridge"))
    latest_bridge = _record(bridge_surface.get("latest_bridge"))
    artifact_ref = _text(latest_bridge.get("artifact_ref"))
    if not artifact_ref:
        return {}
    artifact_path = (root / artifact_ref).resolve()
    try:
        artifact_path.relative_to(root)
    except ValueError:
        return {}
    try:
        if artifact_path.suffix != ".json" or not artifact_path.exists():
            return {}
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _build_open_tabs(
    bridge_artifact: Mapping[str, Any],
    *,
    file_edits: list[dict[str, Any]],
    context_surfaces: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    snapshot = _record(bridge_artifact.get("snapshot"))
    tabs = _records(snapshot.get("open_tabs"))
    if tabs:
        return [
            {
                "tab_id": _text(tab.get("id"), f"tab-{index}"),
                "path": _text(tab.get("path")),
                "label": _text(tab.get("label") or _short(tab.get("path")) or f"tab {index + 1}"),
                "kind": _text(tab.get("kind"), "source"),
                "status": _text(tab.get("status"), "projected"),
                "source": "ide_bridge_artifact",
                "readonly": True,
            }
            for index, tab in enumerate(tabs[:40])
        ]
    rows = [*file_edits[:20], *context_surfaces[:20]]
    return [
        {
            "tab_id": f"projected:{index}",
            "path": _text(row.get("path") or row.get("file_path") or row.get("relpath") or row.get("source")),
            "label": _text(row.get("label") or row.get("title") or _short(row.get("path") or row.get("file_path") or row.get("relpath") or row.get("source")) or f"source {index + 1}"),
            "kind": _text(row.get("kind") or row.get("type") or row.get("status"), "source"),
            "status": _text(row.get("status") or row.get("verdict"), "projected"),
            "source": "fallback_projection",
            "readonly": True,
        }
        for index, row in enumerate(rows)
    ]


def _capability_registry() -> dict[str, Any]:
    capabilities = [
        ("ide.inspect_context_binding", "Inspect active chat context binding", "context", "read_only", False),
        ("ide.inspect_bridge", "Inspect latest IDE bridge artifact", "context", "read_only", False),
        ("ide.open_projected_ref", "Open projected file or artifact ref", "ide", "read_only", False),
        ("ide.inspect_diff", "Inspect worktree diff projection", "git", "read_only", False),
        ("codex.ide_bridge_turn", "Mount IDE bridge on next Codex chat turn", "codex_cli", "candidate_write", True),
        ("codex.queue_work_packet", "Create bounded Codex work packet", "queue", "candidate_write", True),
        ("ide.patch_preview", "Produce patch preview from future editor buffer", "ide", "patch_preview", True),
    ]
    return {
        "schema_id": "ion.codex_ide_capability_registry.v0_1",
        "capability_count": len(capabilities),
        "capabilities": [
            {
                "capability_id": capability_id,
                "label": label,
                "family": family,
                "authority": authority,
                "mutates": mutates,
                "requires_confirmation": authority != "read_only",
                "idempotency_required": mutates,
            }
            for capability_id, label, family, authority, mutates in capabilities
        ],
        "authority": _authority(),
    }


def _authority() -> dict[str, bool]:
    return {
        "read_only_projection": True,
        "filesystem_mutation_authority": False,
        "can_mutate_context": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _record(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _records(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [dict(item) for item in value if isinstance(item, Mapping)]
    return []


def _texts(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_text(item) for item in value if _text(item)]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _short(value: Any) -> str:
    text = _text(value)
    if not text:
        return ""
    return text.rstrip("/").split("/")[-1] or text
