"""Bounded ION automation control-plane.

This module turns common ION/capsule maintenance steps into explicit kernel
actions that the cockpit can run without relying on ad-hoc AI instruction.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_agent_control_plane import build_agent_control_plane_projection
from .ion_agent_comms_directory import build_agent_communication_directory, materialize_agent_communication_directory
from .ion_agent_comms_directives import build_agent_comms_directive_pickup_projection, process_agent_comms_directives
from .ion_context_starter_capsule import (
    build_context_starter_capsule_projection,
    materialize_context_starter_capsule,
)
from .ion_codex_agent_mount import PORTABLE_PACKAGE_ROOT, export_portable_agent_domain_package, materialize_codex_agent_mount
from .ion_domain_weaver import (
    DOMAIN_WEAVER_DOGFOOD_CONTEXT_CAPSULE_PATH,
    DOMAIN_WEAVER_PROMOTION_GATE_PATH,
    DOMAIN_WEAVER_PROJECTION_PATH,
    DOMAIN_WEAVER_PROMOTION_REVIEW_PATH,
    DOMAIN_WEAVER_STEWARD_READY_REVIEW_PATH,
    materialize_domain_weaver_dogfood_context_capsule,
    materialize_domain_weaver_promotion_gate,
    materialize_domain_weaver_projection,
    materialize_domain_weaver_promotion_review,
    materialize_domain_weaver_steward_ready_review,
)

SCHEMA_ID = "ion.automation_control_plane.v0_1"
ACTION_SCHEMA_ID = "ion.automation_action_result.v0_1"
CONFIRMATION = "ION_BOUNDED_WRITE_CONFIRMED"
RECEIPT_DIR = Path("ION/05_context/current/automation_kernel/receipts")

ACTION_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "action_id": "starter_capsule.verify",
        "label": "Verify Context Starter",
        "group": "starter_capsule",
        "mode": "read",
        "description": "Check the clean OPERATOR_FINAL context starter for required files.",
        "requires_confirmation": False,
        "writes_generated_artifacts": False,
    },
    {
        "action_id": "starter_capsule.materialize",
        "label": "Materialize Context Starter",
        "group": "starter_capsule",
        "mode": "bounded_write",
        "description": "Create or refresh the clean OPERATOR_FINAL context starter for new folders.",
        "requires_confirmation": True,
        "writes_generated_artifacts": True,
    },
    {
        "action_id": "agent_mounts.materialize_all",
        "label": "Materialize Agent Mounts",
        "group": "agent_mounts",
        "mode": "bounded_write",
        "description": "Regenerate Codex-native mount folders for every registered projected agent.",
        "requires_confirmation": True,
        "writes_generated_artifacts": True,
    },
    {
        "action_id": "portable_packages.regenerate_lean",
        "label": "Regenerate Lean Packages",
        "group": "portable_packages",
        "mode": "bounded_write",
        "description": "Remove generated portable package exports and regenerate them with directory source refs as manifest-only.",
        "requires_confirmation": True,
        "writes_generated_artifacts": True,
    },
    {
        "action_id": "agent_comms.directory_materialize",
        "label": "Materialize Comms Directory",
        "group": "agent_comms",
        "mode": "bounded_write",
        "description": "Write the shared agent communication directory used by agent capsules and automation guardrails.",
        "requires_confirmation": True,
        "writes_generated_artifacts": True,
    },
    {
        "action_id": "domain_weaver.materialize_projection",
        "label": "Materialize Domain Weaver",
        "group": "domain_weaver",
        "mode": "bounded_write",
        "description": "Write the current domain-agent weave projection for capsules, mounts, cockpit, and comms routing.",
        "requires_confirmation": True,
        "writes_generated_artifacts": True,
    },
    {
        "action_id": "domain_weaver.materialize_promotion_review",
        "label": "Materialize Promotion Review",
        "group": "domain_weaver",
        "mode": "bounded_write",
        "description": "Write candidate-domain promotion review packets and draft registry records without mutating active registry truth.",
        "requires_confirmation": True,
        "writes_generated_artifacts": True,
    },
    {
        "action_id": "domain_weaver.materialize_promotion_gate",
        "label": "Materialize Promotion Gate",
        "group": "domain_weaver",
        "mode": "bounded_write",
        "description": "Write candidate-domain promotion gate validation without mutating active registry truth.",
        "requires_confirmation": True,
        "writes_generated_artifacts": True,
    },
    {
        "action_id": "domain_weaver.materialize_dogfood_context_capsule",
        "label": "Materialize Dogfood Capsule",
        "group": "domain_weaver",
        "mode": "bounded_write",
        "description": "Write a bounded Domain Weaver dogfood context capsule and exactly one candidate next packet.",
        "requires_confirmation": True,
        "writes_generated_artifacts": True,
    },
    {
        "action_id": "domain_weaver.materialize_steward_ready_review",
        "label": "Materialize Ready Review",
        "group": "domain_weaver",
        "mode": "bounded_write",
        "description": "Write candidate Steward settlement review for the current Domain Weaver ready state.",
        "requires_confirmation": True,
        "writes_generated_artifacts": True,
    },
    {
        "action_id": "agent_comms.process_directives",
        "label": "Process Agent Directives",
        "group": "agent_comms",
        "mode": "automation_pickup",
        "description": "Pick up explicit agent-authored ion-agent-comms code blocks and route them through spawn templates.",
        "requires_confirmation": False,
        "writes_generated_artifacts": True,
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _resolve_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


def _tree_stats(path: Path) -> dict[str, int]:
    if not path.exists():
        return {"files": 0, "bytes": 0}
    files = 0
    bytes_total = 0
    for item in path.rglob("*"):
        if item.is_file():
            files += 1
            bytes_total += item.stat().st_size
    return {"files": files, "bytes": bytes_total}


def _receipt(root: Path, action_id: str, result: Mapping[str, Any]) -> str:
    receipt_dir = root / RECEIPT_DIR
    receipt_dir.mkdir(parents=True, exist_ok=True)
    safe = action_id.replace(".", "_").replace("/", "_")
    path = receipt_dir / f"{_stamp()}_{safe}.json"
    path.write_text(json.dumps(dict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path.relative_to(root).as_posix()


def _recent_receipts(root: Path, limit: int = 20) -> list[dict[str, Any]]:
    receipt_dir = root / RECEIPT_DIR
    rows = []
    for path in sorted(receipt_dir.glob("*.json"), reverse=True)[:limit] if receipt_dir.exists() else []:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "action_id": payload.get("action_id") or path.stem,
                "ok": bool(payload.get("ok")),
                "created_at": payload.get("created_at"),
                "summary": payload.get("summary") or payload.get("finding"),
            }
        )
    return rows


def _action(action_id: str) -> dict[str, Any] | None:
    return next((dict(action) for action in ACTION_DEFINITIONS if action["action_id"] == action_id), None)


def build_automation_control_plane(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    starter = build_context_starter_capsule_projection(shell_root)
    agent_model = build_agent_control_plane_projection(shell_root)
    comms_directory = build_agent_communication_directory(
        shell_root,
        agents=list(agent_model.get("agents") or []),
        domains=list(agent_model.get("domains") or []),
    )
    directive_pickup = build_agent_comms_directive_pickup_projection(shell_root)
    package_root = shell_root / PORTABLE_PACKAGE_ROOT
    package_latest = list(package_root.glob("*/LATEST.json")) if package_root.exists() else []
    domain_weaver = agent_model.get("domain_weaver") if isinstance(agent_model.get("domain_weaver"), Mapping) else {}
    domain_weaver_projection = shell_root / DOMAIN_WEAVER_PROJECTION_PATH
    domain_weaver_promotion_review = shell_root / DOMAIN_WEAVER_PROMOTION_REVIEW_PATH
    domain_weaver_promotion_gate = shell_root / DOMAIN_WEAVER_PROMOTION_GATE_PATH
    domain_weaver_dogfood_capsule = shell_root / DOMAIN_WEAVER_DOGFOOD_CONTEXT_CAPSULE_PATH
    domain_weaver_steward_ready_review = shell_root / DOMAIN_WEAVER_STEWARD_READY_REVIEW_PATH
    promotion_review = domain_weaver.get("promotion_review") if isinstance(domain_weaver.get("promotion_review"), Mapping) else {}
    promotion_gate = domain_weaver.get("promotion_gate") if isinstance(domain_weaver.get("promotion_gate"), Mapping) else {}
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": "ION_AUTOMATION_CONTROL_PLANE_READY",
        "summary": {
            "action_count": len(ACTION_DEFINITIONS),
            "starter_ready": bool(starter.get("ready")),
            "portable_package_count": len(package_latest),
            "portable_package_files": _tree_stats(package_root)["files"],
            "available_agent_comms_count": comms_directory.get("available_agent_count", 0),
            "automation_prompt_limit": comms_directory.get("automation_comms_policy", {}).get("limits", {}).get("default_prompt_limit"),
            "agent_comms_directive_pickup": True,
            "directive_processed_count": directive_pickup.get("processed_count", 0),
            "directive_pickup_receipt_count": directive_pickup.get("receipt_count", 0),
            "domain_weaver_gap_count": domain_weaver.get("summary", {}).get("gap_count", 0)
            if isinstance(domain_weaver.get("summary"), Mapping)
            else 0,
            "domain_weaver_projection_exists": domain_weaver_projection.is_file(),
            "domain_weaver_promotion_review_exists": domain_weaver_promotion_review.is_file(),
            "domain_weaver_promotion_ready_count": promotion_review.get("summary", {}).get("ready_for_registry_draft_count", 0)
            if isinstance(promotion_review.get("summary"), Mapping)
            else 0,
            "domain_weaver_promotion_gate_exists": domain_weaver_promotion_gate.is_file(),
            "domain_weaver_promotion_gate_clean_count": promotion_gate.get("summary", {}).get("clean_count", 0)
            if isinstance(promotion_gate.get("summary"), Mapping)
            else 0,
            "domain_weaver_dogfood_capsule_exists": domain_weaver_dogfood_capsule.is_file(),
            "domain_weaver_steward_ready_review_exists": domain_weaver_steward_ready_review.is_file(),
        },
        "actions": list(ACTION_DEFINITIONS),
        "starter_capsule": starter,
        "agent_comms": comms_directory,
        "agent_comms_directive_pickup": directive_pickup,
        "portable_packages": {
            "root": PORTABLE_PACKAGE_ROOT.as_posix(),
            "latest_count": len(package_latest),
            "tree_stats": _tree_stats(package_root),
            "directory_snapshot_policy": "disabled_by_default",
        },
        "domain_weaver": {
            "projection_path": DOMAIN_WEAVER_PROJECTION_PATH.as_posix(),
            "projection_exists": domain_weaver_projection.is_file(),
            "promotion_review_path": DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix(),
            "promotion_review_exists": domain_weaver_promotion_review.is_file(),
            "promotion_gate_path": DOMAIN_WEAVER_PROMOTION_GATE_PATH.as_posix(),
            "promotion_gate_exists": domain_weaver_promotion_gate.is_file(),
            "dogfood_context_capsule_path": DOMAIN_WEAVER_DOGFOOD_CONTEXT_CAPSULE_PATH.as_posix(),
            "dogfood_context_capsule_exists": domain_weaver_dogfood_capsule.is_file(),
            "steward_ready_review_path": DOMAIN_WEAVER_STEWARD_READY_REVIEW_PATH.as_posix(),
            "steward_ready_review_exists": domain_weaver_steward_ready_review.is_file(),
            "projection": domain_weaver,
        },
        "recent_receipts": _recent_receipts(shell_root),
        "confirmation_token": CONFIRMATION,
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    }


def _require_confirmation(action: Mapping[str, Any], payload: Mapping[str, Any]) -> str | None:
    if not action.get("requires_confirmation"):
        return None
    if str(payload.get("confirmation") or "") != CONFIRMATION:
        return "confirmation_required"
    return None


def _materialize_all_agent_mounts(root: Path) -> dict[str, Any]:
    model = build_agent_control_plane_projection(root)
    domains = {str(domain.get("domain_id") or ""): domain for domain in model.get("domains") or [] if isinstance(domain, Mapping)}
    communication_directory = build_agent_communication_directory(
        root,
        agents=list(model.get("agents") or []),
        domains=list(model.get("domains") or []),
    )
    directory_result = materialize_agent_communication_directory(
        root,
        agents=list(model.get("agents") or []),
        domains=list(model.get("domains") or []),
    )
    mounts = []
    for agent in model.get("agents") or []:
        if not isinstance(agent, Mapping):
            continue
        mount = agent.get("native_codex_mount") if isinstance(agent.get("native_codex_mount"), Mapping) else {}
        domain_id = str(mount.get("domain_id") or agent.get("registry_primary_domain") or "")
        mounts.append(materialize_codex_agent_mount(root, agent, domains.get(domain_id), communication_directory=communication_directory))
    return {
        "materialized_count": len(mounts),
        "mount_paths": [mount.get("mount_path") for mount in mounts],
        "communication_directory": directory_result,
    }


def _regenerate_lean_portable_packages(root: Path) -> dict[str, Any]:
    model = build_agent_control_plane_projection(root)
    domains = {str(domain.get("domain_id") or ""): domain for domain in model.get("domains") or [] if isinstance(domain, Mapping)}
    communication_directory = build_agent_communication_directory(
        root,
        agents=list(model.get("agents") or []),
        domains=list(model.get("domains") or []),
    )
    directory_result = materialize_agent_communication_directory(
        root,
        agents=list(model.get("agents") or []),
        domains=list(model.get("domains") or []),
    )
    package_root = root / PORTABLE_PACKAGE_ROOT
    before = _tree_stats(package_root)
    removed = []
    if package_root.exists():
        removed = sorted(path.relative_to(root).as_posix() for path in package_root.glob("*"))
        shutil.rmtree(package_root)
    packages = []
    for agent in model.get("agents") or []:
        if not isinstance(agent, Mapping):
            continue
        mount = agent.get("native_codex_mount") if isinstance(agent.get("native_codex_mount"), Mapping) else {}
        domain_id = str(mount.get("domain_id") or agent.get("registry_primary_domain") or "")
        packages.append(export_portable_agent_domain_package(root, agent, domains.get(domain_id), communication_directory=communication_directory))
    return {
        "before": before,
        "after": _tree_stats(package_root),
        "removed_package_dirs": removed,
        "regenerated_package_count": len(packages),
        "communication_directory": directory_result,
        "directory_snapshot_policy": "disabled_by_default",
    }


def execute_automation_action(root: str | Path | None, payload: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    action_id = str(payload.get("action_id") or "").strip()
    action = _action(action_id)
    if not action:
        return {"schema_id": ACTION_SCHEMA_ID, "ok": False, "finding": "unknown_action", "action_id": action_id}
    confirmation_error = _require_confirmation(action, payload)
    if confirmation_error:
        return {"schema_id": ACTION_SCHEMA_ID, "ok": False, "finding": confirmation_error, "action_id": action_id}
    try:
        if action_id == "starter_capsule.verify":
            data = build_context_starter_capsule_projection(shell_root)
            summary = "Context starter verified."
        elif action_id == "starter_capsule.materialize":
            data = materialize_context_starter_capsule(shell_root)
            summary = "Context starter materialized."
        elif action_id == "agent_mounts.materialize_all":
            data = _materialize_all_agent_mounts(shell_root)
            summary = f"Materialized {data['materialized_count']} agent mounts."
        elif action_id == "portable_packages.regenerate_lean":
            data = _regenerate_lean_portable_packages(shell_root)
            summary = f"Regenerated {data['regenerated_package_count']} lean portable packages."
        elif action_id == "agent_comms.directory_materialize":
            model = build_agent_control_plane_projection(shell_root)
            data = materialize_agent_communication_directory(
                shell_root,
                agents=list(model.get("agents") or []),
                domains=list(model.get("domains") or []),
            )
            summary = f"Materialized agent comms directory for {data['available_agent_count']} available agents."
        elif action_id == "domain_weaver.materialize_projection":
            model = build_agent_control_plane_projection(shell_root)
            data = materialize_domain_weaver_projection(shell_root, model.get("domain_weaver"))
            summary = f"Materialized Domain Weaver projection with {data.get('summary', {}).get('gap_count', 0)} gaps."
        elif action_id == "domain_weaver.materialize_promotion_review":
            model = build_agent_control_plane_projection(shell_root)
            data = materialize_domain_weaver_promotion_review(shell_root, model.get("domain_weaver"))
            summary = (
                "Materialized Domain Weaver promotion review with "
                f"{data.get('candidate_draft_count', 0)} candidate registry drafts."
            )
        elif action_id == "domain_weaver.materialize_promotion_gate":
            model = build_agent_control_plane_projection(shell_root)
            data = materialize_domain_weaver_promotion_gate(
                shell_root,
                review=(model.get("domain_weaver") or {}).get("promotion_review")
                if isinstance(model.get("domain_weaver"), Mapping)
                else None,
                projection=model.get("domain_weaver"),
            )
            summary = (
                "Materialized Domain Weaver promotion gate with "
                f"{data.get('clean_count', 0)} clean candidates and {data.get('blocked_count', 0)} blocked candidates."
            )
        elif action_id == "domain_weaver.materialize_dogfood_context_capsule":
            model = build_agent_control_plane_projection(shell_root)
            data = materialize_domain_weaver_dogfood_context_capsule(shell_root, model.get("domain_weaver"))
            summary = (
                "Materialized Domain Weaver dogfood context capsule with next packet "
                f"{data.get('selected_packet_id', '')}."
            )
        elif action_id == "domain_weaver.materialize_steward_ready_review":
            model = build_agent_control_plane_projection(shell_root)
            data = materialize_domain_weaver_steward_ready_review(shell_root, model.get("domain_weaver"))
            summary = f"Materialized Domain Weaver Steward ready review: {data.get('decision', '')}."
        elif action_id == "agent_comms.process_directives":
            data = process_agent_comms_directives(shell_root, payload)
            summary = f"Processed {data['processed_directive_count']} agent comms directives."
        else:
            return {"schema_id": ACTION_SCHEMA_ID, "ok": False, "finding": "unimplemented_action", "action_id": action_id}
        result: dict[str, Any] = {
            "schema_id": ACTION_SCHEMA_ID,
            "ok": True,
            "created_at": _now(),
            "action_id": action_id,
            "action": action,
            "summary": summary,
            "result": data,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        }
    except Exception as exc:
        result = {
            "schema_id": ACTION_SCHEMA_ID,
            "ok": False,
            "created_at": _now(),
            "action_id": action_id,
            "finding": "automation_failed",
            "error": exc.__class__.__name__,
        }
    result["receipt_path"] = _receipt(shell_root, action_id, result)
    return result
