"""Codex Carrier Sync Layer for ION.

This module maps Codex-native lifecycle features back into normal ION
operations.  Hooks call this shared adapter rather than carrying their own ION
logic.  The v0.1 posture is observation and preservation only: it writes local
candidate receipts and baton pointers, but it does not accept state, mutate
Capsule/HOT_CONTEXT, enforce broad tool governance, or grant live authority.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_workspace_paths import resolve_repo_root

SCHEMA_ID = "ion.codex_carrier_sync.v0_1"
RECEIPT_SCHEMA_ID = "ion.codex_carrier_sync_hook_receipt.v0_1"
READY_VERDICT = "ION_CODEX_CARRIER_SYNC_READY"
BLOCKED_VERDICT = "ION_CODEX_CARRIER_SYNC_BLOCKED"

ACTIVE_ROOT = resolve_repo_root(Path(__file__))
PARENT_ROOT = ACTIVE_ROOT.parent
HOOK_ROOT = Path("ION/05_context/current/codex_cli/hooks")
RUNTIME_HOOK_ROOT = HOOK_ROOT / "runtime"
STATE_DIR = RUNTIME_HOOK_ROOT / "_state"
CODEX_SOLO_DIR = Path("ION/05_context/current/codex_solo")
MINI_PATH = CODEX_SOLO_DIR / "MINI.md"
STATUS_PATH = CODEX_SOLO_DIR / "STATUS.json"
AGENT_MOUNT_ROOT = Path("ION/05_context/current/codex_agent_mounts")
PORTABLE_CONTEXT_DIR = ".ion"
PORTABLE_CONTEXT_MANIFEST = "ION_CONTEXT_CAPSULE.yaml"
PORTABLE_ACTIVE_CONTEXT_PACKAGE = "ACTIVE_CONTEXT_PACKAGE.md"

ION_OPERATION_SET: tuple[str, ...] = (
    "context_load",
    "situation_route",
    "bounded_execution",
    "receipt_preservation",
    "domain_capsule_update",
    "drift_repair",
    "next_packet_compile",
)

HOOK_OPERATION_MAP: dict[str, tuple[str, ...]] = {
    "UserPromptSubmit": ("context_load", "situation_route", "receipt_preservation"),
    "PreCompact": ("receipt_preservation", "drift_repair", "next_packet_compile"),
    "PostCompact": ("drift_repair", "receipt_preservation"),
    "Stop": ("receipt_preservation", "next_packet_compile"),
}

AUTHORITY_FALSE: dict[str, bool] = {
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
}

CONTINUE_OUTPUT: dict[str, Any] = {"continue": True, "suppressOutput": True}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return _now().replace("-", "").replace(":", "").replace("+00:00", "Z")


def _slug(value: Any, *, fallback: str = "item", limit: int = 96) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip()).strip("._-")
    return (text or fallback)[:limit]


def _clean_line(value: Any, *, limit: int = 220) -> str:
    text = re.sub(r"\s+", " ", "" if value is None else str(value)).strip()
    return text[:limit]


def _read_text(path: Path, *, fallback: str = "") -> str:
    if not path.exists() or not path.is_file():
        return fallback
    return path.read_text(encoding="utf-8", errors="replace")


def _read_json(path: Path) -> Any | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
    except ValueError:
        return False
    return True


def _repo_rel(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def _folder_local_context_root(cwd: Path, root_path: Path) -> Path | None:
    for candidate in (cwd, *cwd.parents):
        if not _is_relative_to(candidate, root_path):
            return None
        if candidate == root_path:
            return None
        if (candidate / PORTABLE_CONTEXT_DIR / PORTABLE_CONTEXT_MANIFEST).is_file():
            return candidate
    return None


def resolve_context_scope(payload: Mapping[str, Any], shell_root: str | Path) -> dict[str, Any]:
    root_path = Path(shell_root).expanduser().resolve()
    cwd = Path(str(payload.get("cwd") or root_path)).expanduser().resolve()
    mount_root = root_path / AGENT_MOUNT_ROOT
    base = {
        "schema_id": "ion.codex_carrier_context_scope.v0_1",
        "cwd": cwd.as_posix(),
        "active_root": root_path.as_posix(),
        "shared_codex_solo_boot_context_loaded": False,
        "shared_codex_solo_is_working_capsule": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
    if _is_relative_to(cwd, mount_root):
        rel = cwd.relative_to(mount_root)
        if rel.parts:
            mount_path = mount_root / rel.parts[0]
            manifest = mount_path / "ION_AGENT_MOUNT_MANIFEST.json"
            capsule = mount_path / ".ion" / "ION_CONTEXT_CAPSULE.yaml"
            active_package = mount_path / ".ion" / "ACTIVE_CONTEXT_PACKAGE.md"
            if manifest.is_file() or capsule.is_file():
                return {
                    **base,
                    "classification": "codex_agent_mount",
                    "working_capsule_source": "folder_local_ion_context_capsule",
                    "mount_path": _repo_rel(root_path, mount_path),
                    "manifest_path": _repo_rel(root_path, manifest),
                    "portable_context_manifest_path": _repo_rel(root_path, capsule),
                    "portable_active_context_package_md_path": _repo_rel(root_path, active_package),
                }
    context_root = _folder_local_context_root(cwd, root_path)
    if context_root is not None:
        capsule = context_root / PORTABLE_CONTEXT_DIR / PORTABLE_CONTEXT_MANIFEST
        active_package = context_root / PORTABLE_CONTEXT_DIR / PORTABLE_ACTIVE_CONTEXT_PACKAGE
        return {
            **base,
            "classification": "folder_local_context_capsule",
            "working_capsule_source": "folder_local_ion_context_capsule",
            "context_root_path": _repo_rel(root_path, context_root),
            "portable_context_manifest_path": _repo_rel(root_path, capsule),
            "portable_active_context_package_md_path": _repo_rel(root_path, active_package),
            "agents_md_path": _repo_rel(root_path, context_root / "AGENTS.md"),
            "codex_config_path": _repo_rel(root_path, context_root / ".codex" / "config.toml"),
            "context_identity_path": _repo_rel(root_path, context_root / PORTABLE_CONTEXT_DIR / "CONTEXT_IDENTITY.json"),
        }
    return {
        **base,
        "classification": "root_shared_fallback_only",
        "working_capsule_source": None,
        "required_action": "select_folder_local_context_capsule_or_agent_mount_before_material_domain_work",
        "blocked_as_working_capsule": "ION/05_context/current/codex_solo",
    }


def resolve_active_root(cwd: str | Path | None = None, root: str | Path | None = None) -> tuple[Path, list[str]]:
    """Resolve the active ION root while accepting parent-root Codex launches."""

    findings: list[str] = []
    if root is not None:
        candidate = Path(root).expanduser().resolve()
    else:
        candidate = Path(cwd or ".").expanduser().resolve()

    probes = [candidate, *candidate.parents]
    for path in probes:
        if (path / "pyproject.toml").is_file() and (path / "ION" / "REPO_AUTHORITY.md").is_file():
            return path, findings

    if _is_relative_to(candidate, PARENT_ROOT) and (ACTIVE_ROOT / "pyproject.toml").is_file():
        findings.append("resolved_from_parent_workspace")
        return ACTIVE_ROOT, findings

    findings.append(f"cwd_outside_active_ion_root:{candidate}")
    return ACTIVE_ROOT, findings


def _payload_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    keys = [
        "hook_event_name",
        "session_id",
        "turn_id",
        "cwd",
        "model",
        "permission_mode",
        "trigger",
        "tool_name",
        "tool_use_id",
        "transcript_path",
    ]
    summary = {key: payload.get(key) for key in keys if key in payload}
    if "prompt" in payload:
        summary["prompt_excerpt"] = _clean_line(payload.get("prompt"), limit=260)
    if "last_assistant_message" in payload:
        summary["last_assistant_message_excerpt"] = _clean_line(payload.get("last_assistant_message"), limit=260)
    return summary


def _mini_field(mini: str, name: str) -> str | None:
    prefix = f"{name}:"
    for line in mini.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def resolve_active_objective(
    root: str | Path | None = None,
    *,
    context_scope: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    shell_root, findings = resolve_active_root(root=root or ACTIVE_ROOT)
    if context_scope and context_scope.get("classification") == "codex_agent_mount":
        manifest_path = context_scope.get("manifest_path")
        manifest: dict[str, Any] = {}
        if isinstance(manifest_path, str) and manifest_path:
            manifest_payload = _read_json(shell_root / manifest_path)
            manifest = manifest_payload if isinstance(manifest_payload, dict) else {}
        return {
            "classification": "codex_agent_mount",
            "working_capsule_source": context_scope.get("working_capsule_source"),
            "shared_codex_solo_objective_loaded": False,
            "active_template": "FOLDER_LOCAL_AGENT_CONTEXT_PACKAGE",
            "mount_path": context_scope.get("mount_path"),
            "manifest_path": context_scope.get("manifest_path"),
            "portable_context_manifest_path": context_scope.get("portable_context_manifest_path"),
            "portable_active_context_package_md_path": context_scope.get("portable_active_context_package_md_path"),
            "agent_role_id": manifest.get("agent_role_id"),
            "agent_display_name": manifest.get("agent_display_name"),
            "domain_id": manifest.get("domain_id"),
            "findings": findings,
        }
    if context_scope and context_scope.get("classification") == "folder_local_context_capsule":
        identity_path = context_scope.get("context_identity_path")
        identity: dict[str, Any] = {}
        if isinstance(identity_path, str) and identity_path:
            identity_payload = _read_json(shell_root / identity_path)
            identity = identity_payload if isinstance(identity_payload, dict) else {}
        return {
            "classification": "folder_local_context_capsule",
            "working_capsule_source": context_scope.get("working_capsule_source"),
            "shared_codex_solo_objective_loaded": False,
            "active_template": identity.get("active_template") or "FOLDER_LOCAL_CONTEXT_PACKAGE",
            "context_root_path": context_scope.get("context_root_path"),
            "portable_context_manifest_path": context_scope.get("portable_context_manifest_path"),
            "portable_active_context_package_md_path": context_scope.get("portable_active_context_package_md_path"),
            "context_id": identity.get("context_id"),
            "domain_id": identity.get("domain_id"),
            "focus": identity.get("focus"),
            "findings": findings,
        }
    if context_scope:
        return {
            "classification": "root_shared_fallback_only",
            "shared_codex_solo_objective_loaded": False,
            "required_action": "select_folder_local_context_capsule_or_agent_mount_before_material_domain_work",
            "findings": findings,
        }
    mini = _read_text(shell_root / MINI_PATH)
    status = _read_json(shell_root / STATUS_PATH) or {}
    recent_rows = status.get("capsule", {}).get("recent_rows", []) if isinstance(status, dict) else []
    latest_row = recent_rows[-1] if recent_rows else None
    objective = {
        "mission": _mini_field(mini, "MISSION"),
        "phase": _mini_field(mini, "PHASE"),
        "last_receipt": _mini_field(mini, "LAST_RECEIPT"),
        "blocker": _mini_field(mini, "BLOCKER"),
        "next_action": _mini_field(mini, "NEXT"),
        "active_template": _mini_field(mini, "ACTIVE_TEMPLATE"),
        "latest_capsule_row": latest_row,
        "findings": findings,
    }
    return {key: value for key, value in objective.items() if value not in (None, [], {})}


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def suggest_skill_or_domain(prompt: str, root: str | Path | None = None) -> dict[str, Any]:
    text = prompt.lower()
    proceed = bool(re.search(r"\b(proceed|continue|carry on|go ahead|resume|next step|keep going)\b", text))
    ion_operation_frustration = _contains_any(
        text,
        (
            "why aren't you",
            "why arent you",
            "operate as ion",
            "operating as ion",
            "constantly tell you to mount",
            "tell you to mount",
            "mount it",
            "ion can only work",
            "ion is not working",
            "no built ion integration",
            "no persona",
            "no relay",
            "no steward",
            "100% failure",
        ),
    )
    suggestion = {
        "intent_class": "general_ion_work",
        "proceed_continue_detected": proceed,
        "suggested_skill": "ion-orchestration",
        "suggested_domain": "codex_carrier_sync",
        "candidate_packet": "PCKT-ION-CODEX-CARRIER-SYNC-LAYER-V0_1",
        "confidence": "medium",
        "reason": "default_codex_carrier_sync_route",
    }
    if proceed:
        suggestion.update({
            "intent_class": "continue_active_objective",
            "confidence": "high",
            "reason": "prompt_contains_continue_or_proceed_signal",
        })
    if ion_operation_frustration:
        suggestion.update({
            "intent_class": "carrier_operation_failure_repair",
            "suggested_domain": "codex_carrier_sync",
            "candidate_packet": "PCKT-ION-CODEX-OPERATE-NOT-EXPLAIN-GUARD-V0_1",
            "confidence": "high",
            "reason": "prompt_reports_operator_having_to_remind_carrier_to_mount_or_operate",
        })
    if _contains_any(text, ("ion", "mount", "hook", "codex", "carrier", "config.toml", "mcp", "subagent", "skill", "precompact", "postcompact")):
        suggestion.update({
            "suggested_domain": "codex_carrier_sync",
            "candidate_packet": suggestion.get("candidate_packet") or "PCKT-ION-CODEX-CARRIER-SYNC-LAYER-V0_1",
            "confidence": "high",
            "reason": suggestion.get("reason") if ion_operation_frustration else "prompt_mentions_ion_or_codex_carrier_feature_surface",
        })
    if _contains_any(text, ("helixion", "joc", "wisdomnet")):
        suggestion.update({
            "suggested_domain": "helixion_joc_rebuild",
            "candidate_packet": "HELIXION_JOC_ORCHESTRATION_CONTEXT_PACKAGE",
            "confidence": "high",
            "reason": "prompt_mentions_helixion_joc_or_wisdomnet",
        })
    if _contains_any(text, ("gpt builder", "action schema", "gpt action", "gateway")):
        suggestion.update({
            "suggested_domain": "ion_gpt_action_gateway",
            "candidate_packet": "GPT_ACTION_SCHEMA_RELEASE_OR_VALIDATION_PACKET",
            "confidence": "high",
            "reason": "prompt_mentions_gpt_action_gateway_surface",
        })
    if _contains_any(text, ("review", "audit", "find issues")):
        suggestion.update({
            "intent_class": "review_or_audit",
            "candidate_packet": "CODEX_REVIEW_OR_AUDIT_WORK_UNIT",
            "confidence": "medium",
            "reason": "prompt_mentions_review_or_audit",
        })
    return suggestion


def build_response_contract(
    route: Mapping[str, Any],
    mount_guard: Mapping[str, Any],
    operational_posture: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the chat-facing contract that turns mount proof into action."""

    mount_ready = mount_guard.get("mount_truth_state") == "CODEX_CARRIER_LOCAL_MOUNT_READY"
    operational_ready = operational_posture.get("ion_operational_state") == "ION_CODEX_OPERATIONAL_READY"
    operate_now = bool(mount_ready and operational_ready)
    return {
        "schema_id": "ion.codex_response_contract.v0_1",
        "status": "OPERATE_AS_ION_NOW" if operate_now else "BLOCK_OR_RECEIPT_ONLY_UNTIL_MOUNT_READY",
        "operator_remount_required": False if operate_now else True,
        "must_not_ask_operator_to_remount_when_ready": operate_now,
        "must_not_stop_at_mount_explanation": operate_now,
        "must_take_bounded_next_step": operate_now,
        "persona_fronted_response_required": operate_now,
        "visible_role_surface_required": False,
        "internal_role_trace_visible_by_default": False,
        "audit_trace_available_on_request": True,
        "visible_role_markers": [
            "PERSONA_INTERFACE_RESPONSE",
            "RELAY",
            "STEWARD",
            "MASON",
            "SCRIBE",
        ],
        "role_phase_mode": "single_carrier_sequential",
        "intent_class": route.get("intent_class"),
        "suggested_domain": route.get("suggested_domain"),
        "candidate_packet": route.get("candidate_packet"),
        "external_workers": (
            "optional carrier slots; not required for ION mount; use only when generated spawn rows "
            "or explicit invocation proof exist"
        ),
        "operator_visible_rule": (
            "If mount is ready, answer through Persona Interface by default and act through "
            "the current internal role phases without making the operator manage them. Do not "
            "ask the operator to remind, mount, or verify ION first."
        ),
        "visible_role_rule": (
            "For normal substantive ION turns, return only the Persona Interface response. "
            "Keep Relay, Steward, Mason, Scribe, and other role-phase trace internal unless "
            "the operator asks for audit/proof/debug detail."
        ),
        "failure_condition": (
            "Explaining that ION can operate without performing the next bounded action, "
            "or leaking internal role machinery into the default Persona-facing answer, is carrier drift."
        ),
    }


def _git_status_paths(shell_root: Path) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=shell_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception as exc:
        return {"ok": False, "error": _clean_line(exc), "paths": []}
    paths: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2].strip() or line[:2]
        path = line[3:].strip() if len(line) > 3 else line.strip()
        paths.append({"status": status, "path": path})
    return {"ok": result.returncode == 0, "returncode": result.returncode, "paths": paths[:200], "path_count": len(paths)}


def _receipt_dir(event_name: str) -> Path:
    return RUNTIME_HOOK_ROOT / event_name.lower()


def write_candidate_hook_receipt(
    event_name: str,
    payload: Mapping[str, Any],
    *,
    root: str | Path | None = None,
    operation_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    shell_root, findings = resolve_active_root(cwd=payload.get("cwd"), root=root)
    session_id = _slug(payload.get("session_id"), fallback="session")
    turn_id = _slug(payload.get("turn_id"), fallback="turn")
    receipt_id = f"{_stamp()}_{_slug(event_name, fallback='hook')}_{session_id}_{turn_id}"
    rel_path = _receipt_dir(event_name) / f"{receipt_id}.json"
    receipt = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "receipt_id": receipt_id,
        "created_at": _now(),
        "event_name": event_name,
        "active_root": str(shell_root),
        "ion_operation_targets": list(HOOK_OPERATION_MAP.get(event_name, ("receipt_preservation",))),
        "carrier_feature_map_law": "CARRIER_FEATURES_MUST_MAP_TO_ION_OPS",
        "payload_summary": _payload_summary(payload),
        "operation_payload": dict(operation_payload or {}),
        "findings": findings,
        "candidate_state_only": True,
        **AUTHORITY_FALSE,
    }
    _write_json(shell_root / rel_path, receipt)
    receipt["path"] = rel_path.as_posix()
    return receipt


def _state_ref_path(session_id: Any, turn_id: Any, event_name: str) -> Path:
    session = _slug(session_id, fallback="session", limit=64)
    turn = _slug(turn_id, fallback="turn", limit=64)
    return STATE_DIR / f"{session}_{turn}_{event_name.lower()}.json"


def _write_state_ref(shell_root: Path, payload: Mapping[str, Any], event_name: str, receipt: Mapping[str, Any]) -> None:
    ref = {
        "schema_id": "ion.codex_carrier_sync_hook_state_ref.v0_1",
        "created_at": _now(),
        "event_name": event_name,
        "session_id": payload.get("session_id"),
        "turn_id": payload.get("turn_id"),
        "receipt_path": receipt.get("path"),
        "candidate_state_only": True,
        **AUTHORITY_FALSE,
    }
    _write_json(shell_root / _state_ref_path(payload.get("session_id"), payload.get("turn_id"), event_name), ref)


def _read_state_ref(shell_root: Path, payload: Mapping[str, Any], event_name: str) -> dict[str, Any] | None:
    value = _read_json(shell_root / _state_ref_path(payload.get("session_id"), payload.get("turn_id"), event_name))
    return value if isinstance(value, dict) else None


def _additional_context(event_name: str, receipt: Mapping[str, Any], operation_payload: Mapping[str, Any]) -> str:
    objective = operation_payload.get("active_objective") if isinstance(operation_payload, Mapping) else None
    route = operation_payload.get("route") if isinstance(operation_payload, Mapping) else None
    context_scope = operation_payload.get("context_scope") if isinstance(operation_payload, Mapping) else None
    mount_guard = operation_payload.get("mount_guard") if isinstance(operation_payload, Mapping) else None
    operational_posture = operation_payload.get("operational_posture") if isinstance(operation_payload, Mapping) else None
    response_contract = operation_payload.get("response_contract") if isinstance(operation_payload, Mapping) else None
    lines = [
        "ION Codex Carrier Sync v0.1",
        "law: CARRIER_FEATURES_MUST_MAP_TO_ION_OPS",
        f"event: {event_name}",
        f"ops: {', '.join(receipt.get('ion_operation_targets', []))}",
        f"candidate_receipt: {receipt.get('path')}",
        "authority: candidate only; no accepted state, production, live execution, or secrets authority.",
    ]
    if isinstance(mount_guard, Mapping):
        try:
            from kernel.ion_codex_mount_guard import render_mount_guard_block

            lines.extend(["", render_mount_guard_block(mount_guard)])
        except Exception:
            lines.append("mount_guard: unavailable")
    if isinstance(operational_posture, Mapping):
        try:
            from kernel.ion_codex_operational_posture import render_operational_posture_block

            lines.extend(["", render_operational_posture_block(operational_posture)])
        except Exception:
            lines.append("operational_posture: unavailable")
    if isinstance(route, Mapping):
        lines.extend([
            f"intent_class: {route.get('intent_class')}",
            f"suggested_domain: {route.get('suggested_domain')}",
            f"suggested_skill: {route.get('suggested_skill')}",
            f"candidate_packet: {route.get('candidate_packet')}",
            f"proceed_continue_detected: {route.get('proceed_continue_detected')}",
        ])
    if isinstance(context_scope, Mapping):
        lines.extend([
            "",
            "ION Codex Context Scope v0.1",
            f"classification: {context_scope.get('classification')}",
            f"working_capsule_source: {context_scope.get('working_capsule_source')}",
            f"shared_codex_solo_boot_context_loaded: {context_scope.get('shared_codex_solo_boot_context_loaded')}",
            f"shared_codex_solo_is_working_capsule: {context_scope.get('shared_codex_solo_is_working_capsule')}",
        ])
        if context_scope.get("mount_path"):
            lines.append(f"mount_path: {context_scope.get('mount_path')}")
        if context_scope.get("context_root_path"):
            lines.append(f"context_root_path: {context_scope.get('context_root_path')}")
        if context_scope.get("required_action"):
            lines.append(f"required_action: {context_scope.get('required_action')}")
    if isinstance(response_contract, Mapping):
        lines.extend([
            "",
            "ION Codex Response Contract v0.1",
            f"status: {response_contract.get('status')}",
            f"operator_remount_required: {response_contract.get('operator_remount_required')}",
            f"must_not_ask_operator_to_remount_when_ready: {response_contract.get('must_not_ask_operator_to_remount_when_ready')}",
            f"must_not_stop_at_mount_explanation: {response_contract.get('must_not_stop_at_mount_explanation')}",
            f"must_take_bounded_next_step: {response_contract.get('must_take_bounded_next_step')}",
            f"persona_fronted_response_required: {response_contract.get('persona_fronted_response_required')}",
            f"visible_role_surface_required: {response_contract.get('visible_role_surface_required')}",
            f"internal_role_trace_visible_by_default: {response_contract.get('internal_role_trace_visible_by_default')}",
            f"audit_trace_available_on_request: {response_contract.get('audit_trace_available_on_request')}",
            f"visible_role_markers: {', '.join(response_contract.get('visible_role_markers') or [])}",
            f"operator_visible_rule: {response_contract.get('operator_visible_rule')}",
            f"visible_role_rule: {response_contract.get('visible_role_rule')}",
            f"failure_condition: {response_contract.get('failure_condition')}",
        ])
    if isinstance(objective, Mapping):
        for key in (
            "classification",
            "shared_codex_solo_objective_loaded",
            "working_capsule_source",
            "mount_path",
            "context_root_path",
            "context_id",
            "agent_role_id",
            "agent_display_name",
            "domain_id",
            "focus",
        ):
            if key in objective and objective[key] not in (None, "", [], {}):
                lines.append(f"active_{key}: {_clean_line(objective[key], limit=180)}")
        for key in ("mission", "phase", "last_receipt", "blocker", "next_action", "active_template"):
            if objective.get(key):
                lines.append(f"active_{key}: {_clean_line(objective[key], limit=180)}")
    return "\n".join(lines)


def classify_prompt_submit(payload: Mapping[str, Any], root: str | Path | None = None) -> dict[str, Any]:
    shell_root, findings = resolve_active_root(cwd=payload.get("cwd"), root=root)
    prompt = str(payload.get("prompt") or "")
    mount_guard, mount_guard_write = _mount_guard_snapshot(shell_root)
    operational_posture, operational_posture_write = _operational_posture_snapshot(shell_root)
    route = suggest_skill_or_domain(prompt, shell_root)
    context_scope = resolve_context_scope(payload, shell_root)
    operation = {
        "route": route,
        "context_scope": context_scope,
        "active_objective": resolve_active_objective(shell_root, context_scope=context_scope),
        "mount_guard": mount_guard,
        "mount_guard_write": mount_guard_write,
        "operational_posture": operational_posture,
        "operational_posture_write": operational_posture_write,
        "response_contract": build_response_contract(route, mount_guard, operational_posture),
        "root_findings": findings,
    }
    receipt = write_candidate_hook_receipt("UserPromptSubmit", payload, root=shell_root, operation_payload=operation)
    output = {
        **CONTINUE_OUTPUT,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": _additional_context("UserPromptSubmit", receipt, operation),
        },
    }
    if findings and any(item.startswith("cwd_outside") for item in findings):
        output["systemMessage"] = "ION carrier sync resolved active root with visible warning; verify cwd before material work."
    return output


def _mount_guard_snapshot(shell_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    from kernel.ion_codex_mount_guard import build_codex_mount_status, write_current_mount_status

    mount_guard = build_codex_mount_status(shell_root)
    return mount_guard, write_current_mount_status(shell_root, mount_guard)


def _operational_posture_snapshot(shell_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    from kernel.ion_codex_operational_posture import build_codex_operational_posture, write_current_operational_posture

    posture = build_codex_operational_posture(shell_root)
    return posture, write_current_operational_posture(shell_root, posture)


def checkpoint_precompact(payload: Mapping[str, Any], root: str | Path | None = None) -> dict[str, Any]:
    shell_root, findings = resolve_active_root(cwd=payload.get("cwd"), root=root)
    mount_guard, mount_guard_write = _mount_guard_snapshot(shell_root)
    operational_posture, operational_posture_write = _operational_posture_snapshot(shell_root)
    context_scope = resolve_context_scope(payload, shell_root)
    operation = {
        "checkpoint_kind": "precompact_context_baton",
        "trigger": payload.get("trigger"),
        "context_scope": context_scope,
        "active_objective": resolve_active_objective(shell_root, context_scope=context_scope),
        "mount_guard": mount_guard,
        "mount_guard_write": mount_guard_write,
        "operational_posture": operational_posture,
        "operational_posture_write": operational_posture_write,
        "dirty_paths_snapshot": _git_status_paths(shell_root),
        "root_findings": findings,
    }
    receipt = write_candidate_hook_receipt("PreCompact", payload, root=shell_root, operation_payload=operation)
    _write_state_ref(shell_root, payload, "PreCompact", receipt)
    output = dict(CONTINUE_OUTPUT)
    if findings and any(item.startswith("cwd_outside") for item in findings):
        output["systemMessage"] = "ION PreCompact checkpoint used visible active-root resolution warning."
    return output


def verify_postcompact(payload: Mapping[str, Any], root: str | Path | None = None) -> dict[str, Any]:
    shell_root, findings = resolve_active_root(cwd=payload.get("cwd"), root=root)
    checkpoint = _read_state_ref(shell_root, payload, "PreCompact")
    mount_guard, mount_guard_write = _mount_guard_snapshot(shell_root)
    operational_posture, operational_posture_write = _operational_posture_snapshot(shell_root)
    operation = {
        "verification_kind": "postcompact_checkpoint_survival",
        "trigger": payload.get("trigger"),
        "precompact_checkpoint_found": checkpoint is not None,
        "precompact_checkpoint_ref": checkpoint,
        "mount_guard": mount_guard,
        "mount_guard_write": mount_guard_write,
        "operational_posture": operational_posture,
        "operational_posture_write": operational_posture_write,
        "root_findings": findings,
    }
    receipt = write_candidate_hook_receipt("PostCompact", payload, root=shell_root, operation_payload=operation)
    _write_state_ref(shell_root, payload, "PostCompact", receipt)
    output = dict(CONTINUE_OUTPUT)
    if checkpoint is None:
        output["systemMessage"] = "ION PostCompact did not find a matching PreCompact checkpoint; continuity receipt was still recorded."
    return output


def record_stop_receipt(payload: Mapping[str, Any], root: str | Path | None = None) -> dict[str, Any]:
    shell_root, findings = resolve_active_root(cwd=payload.get("cwd"), root=root)
    mount_guard, mount_guard_write = _mount_guard_snapshot(shell_root)
    operational_posture, operational_posture_write = _operational_posture_snapshot(shell_root)
    context_scope = resolve_context_scope(payload, shell_root)
    operation = {
        "receipt_kind": "turn_stop_handoff",
        "context_scope": context_scope,
        "active_objective": resolve_active_objective(shell_root, context_scope=context_scope),
        "mount_guard": mount_guard,
        "mount_guard_write": mount_guard_write,
        "operational_posture": operational_posture,
        "operational_posture_write": operational_posture_write,
        "dirty_paths_snapshot": _git_status_paths(shell_root),
        "last_assistant_message_excerpt": _clean_line(payload.get("last_assistant_message"), limit=500),
        "next_baton": {
            "recommended_next_action": "Resume from latest Codex Carrier Sync Stop receipt, then Capsule/Mini if broader continuity is needed.",
            "candidate_state_only": True,
        },
        "root_findings": findings,
    }
    receipt = write_candidate_hook_receipt("Stop", payload, root=shell_root, operation_payload=operation)
    _write_state_ref(shell_root, payload, "Stop", receipt)
    output = dict(CONTINUE_OUTPUT)
    if findings and any(item.startswith("cwd_outside") for item in findings):
        output["systemMessage"] = "ION Stop receipt used visible active-root resolution warning."
    return output


def handle_hook_event(event_name: str, payload: Mapping[str, Any], root: str | Path | None = None) -> dict[str, Any]:
    try:
        if event_name == "UserPromptSubmit":
            return classify_prompt_submit(payload, root=root)
        if event_name == "PreCompact":
            return checkpoint_precompact(payload, root=root)
        if event_name == "PostCompact":
            return verify_postcompact(payload, root=root)
        if event_name == "Stop":
            return record_stop_receipt(payload, root=root)
        receipt = write_candidate_hook_receipt(event_name, payload, root=root)
        return {**CONTINUE_OUTPUT, "systemMessage": f"ION carrier sync recorded unsupported hook event {event_name}: {receipt['path']}"}
    except Exception as exc:  # pragma: no cover - live hook must fail visible
        return {
            "continue": True,
            "suppressOutput": False,
            "systemMessage": f"ION_CARRIER_NOT_OPERATIONAL: carrier sync hook error: {_clean_line(exc, limit=300)}",
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": (
                    "ION_CARRIER_NOT_OPERATIONAL\n"
                    "mount_truth_state: HOOK_ERROR_BLOCKED\n"
                    "required_action: inspect hook receipt/state before serious ION work"
                ),
            },
        }


def build_carrier_sync_status(root: str | Path | None = None) -> dict[str, Any]:
    shell_root, findings = resolve_active_root(root=root or ACTIVE_ROOT)
    from kernel.ion_codex_mount_guard import build_codex_mount_status
    from kernel.ion_codex_operational_posture import build_codex_operational_posture

    mount_guard = build_codex_mount_status(shell_root)
    operational_posture = build_codex_operational_posture(shell_root)
    return {
        "schema_id": SCHEMA_ID,
        "verdict": READY_VERDICT if not any(item.startswith("cwd_outside") for item in findings) else BLOCKED_VERDICT,
        "ok": not any(item.startswith("cwd_outside") for item in findings),
        "active_root": str(shell_root),
        "mount_guard": mount_guard,
        "operational_posture": operational_posture,
        "hook_runtime_root": HOOK_ROOT.as_posix(),
        "operation_set": list(ION_OPERATION_SET),
        "hook_operation_map": {key: list(value) for key, value in HOOK_OPERATION_MAP.items()},
        "policy": {
            "capsule_hot_context_auto_mutation": False,
            "broad_pretooluse_governance": False,
            "permission_request_policy": False,
            "candidate_receipts_only": True,
        },
        "findings": findings,
        **AUTHORITY_FALSE,
    }


def _read_stdin_json() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ION Codex Carrier Sync adapter")
    parser.add_argument("--ion-root", default=str(ACTIVE_ROOT), help="Active ION shell root")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="Print carrier sync status")
    status.add_argument("--json", action="store_true")

    hook = sub.add_parser("hook", help="Handle one Codex hook payload from stdin")
    hook.add_argument("--event", required=True, choices=sorted(HOOK_OPERATION_MAP))
    hook.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "status":
        payload = build_carrier_sync_status(args.ion_root)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"{payload['verdict']} active_root={payload['active_root']}")
        return 0 if payload.get("ok") else 2
    if args.command == "hook":
        output = handle_hook_event(args.event, _read_stdin_json(), root=args.ion_root)
        print(json.dumps(output, sort_keys=True))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
