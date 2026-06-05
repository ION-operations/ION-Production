"""Bounded Action/MCP branch leader registry and route invocation helpers.

This module gives Custom GPT Actions and MCP carriers a stable branch-leader
surface over declared ION owner tools. It does not expose arbitrary shell,
arbitrary Python function calls, dynamic imports, or credential access.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

_YAML_IMPORT_ERROR: Exception | None = None
try:
    import yaml  # type: ignore[import-untyped]
except Exception as exc:  # pragma: no cover - exercised in python -S worker lanes
    yaml = None  # type: ignore[assignment]
    _YAML_IMPORT_ERROR = exc

from .ion_carrier_onboard import resolve_shell_root_from_ion_root
from .ion_branch_context_materialization import (
    RECEIPTS_PATH as BRANCH_CONTEXT_RECEIPTS_PATH,
    build_candidate_branch_capsule,
    build_materialization_receipt,
    classify_branch_context,
    write_materialization_receipt,
)

SCHEMA_ID = "ion.action_mcp_branch_leaders.v0"
REGISTRY_RELATIVE_PATH = Path("ION/03_registry/ion_action_mcp_branch_leader_registry.yaml")
CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"
DEFAULT_BRANCH_LIST_LIMIT = 100
FINAL_OPERATOR_KIT_PREFIX = "ION_GPT_FINAL_OPERATOR_UPLOAD_KIT_"
FINAL_OPERATOR_KIT_KNOWLEDGE_DIR = "02_UPLOAD_EVERY_FILE_IN_THIS_FOLDER_TO_GPT_KNOWLEDGE"
WORKER_SHIFT_ROUTE_IDS = {
    "status_summary",
    "active_workers",
    "stale_workers",
    "active_leases",
    "coordination_state",
    "parallel_plan_preview",
}
LATEST_CONTEXT_ROUTE_IDS = {
    "mount_status",
    "latest_handoff",
    "current_context_pack",
    "recent_receipts",
    "next_allowed_routes",
    "package_freshness",
}
LATEST_CONTEXT_NON_CLAIMS = {
    "accepted_state_claim": False,
    "production_authority": False,
    "live_execution_authority": False,
    "gpt_builder_updated": False,
    "git_pushed": False,
    "deployed": False,
    "service_restarted": False,
    "action_mount_equivalent": False,
}
LATEST_CONTEXT_PROOF_OBLIGATIONS = [
    "Read local bootloader main instructions, root manifest, and markdown mount/index files before Branch Gateway calls.",
    "Declare mount truth state before serious ION work.",
    "Verify referenced receipt paths and hashes before relying on handoff claims.",
    "Treat candidate receipts and package rebuilds as candidate-only unless settlement proof says accepted.",
    "Use next_allowed_routes before any write/runtime/accepted-state route.",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_root(root: str | Path | None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return resolve_shell_root_from_ion_root(root)


def _blocked(
    operation: str,
    finding: str,
    *,
    refusal_class: str = "SCHEMA_INVALID",
    data: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "operation": operation,
        "ok": False,
        "finding": finding,
        "refusal_class": refusal_class,
        "production_authority": False,
        "live_execution_authority": False,
    }
    if data:
        payload.update(dict(data))
    return payload


def _ok(operation: str, data: Mapping[str, Any], **extra: Any) -> dict[str, Any]:
    payload = {
        "schema_id": SCHEMA_ID,
        "operation": operation,
        "ok": True,
        "generated_at": _now(),
        "production_authority": False,
        "live_execution_authority": False,
    }
    payload.update(dict(data))
    payload.update(extra)
    return payload


def _clean_lease_path_value(value: Any) -> str:
    return re.sub(r"/+", "/", str(value or "").strip().replace("\\", "/")).strip("/")


def _clean_string_list(values: list[Any]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if text and text not in seen:
            cleaned.append(text)
            seen.add(text)
    return cleaned


def _route_lease_gate(route: Mapping[str, Any]) -> dict[str, Any]:
    gate = route.get("lease_gate")
    return dict(gate) if isinstance(gate, Mapping) else {}


def _route_safe_idempotency_key(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{text[:80]}_{digest}"


def _route_required_lease_mode(route: Mapping[str, Any]) -> str:
    if bool(route.get("edit_lease_required")):
        return "exclusive_write"
    if bool(route.get("artifact_lease_required")):
        return "artifact"
    gate = _route_lease_gate(route)
    required = str(gate.get("required_lease_type") or gate.get("lease_type") or "").strip()
    if required in {"exclusive_write", "exclusive-write", "write", "edit"}:
        return "exclusive_write"
    if required == "artifact":
        return "artifact"
    return ""


def _route_agent_id_required(route: Mapping[str, Any]) -> bool:
    return bool(route.get("agent_id_required")) or bool(_route_required_lease_mode(route))


def _route_lease_id_required(route: Mapping[str, Any]) -> bool:
    return bool(route.get("lease_id_required")) or bool(_route_required_lease_mode(route))


def _route_lease_gate_is_dynamic(gate: Mapping[str, Any]) -> bool:
    derivation = str(gate.get("target_derivation") or gate.get("target_source") or "").strip()
    return bool(gate.get("dynamic_target")) or derivation in {"dynamic", "handler_dynamic", "handler"}


def _route_lease_gate_target_derivation(gate: Mapping[str, Any]) -> str:
    derivation = str(gate.get("target_derivation") or gate.get("target_source") or "").strip()
    if derivation:
        return derivation
    if bool(gate.get("dynamic_target")):
        return "handler_dynamic"
    if str(gate.get("target_path") or "").strip():
        return "declarative_target_path"
    if str(gate.get("target_path_template") or "").strip():
        return "declarative_target_path_template"
    if str(gate.get("target_argument") or "").strip():
        return "argument_target"
    return "route_args"


def _public_route_lease_gate_model(route: Mapping[str, Any]) -> dict[str, Any]:
    gate = _route_lease_gate(route)
    required_mode = _route_required_lease_mode(route)
    write_intent_required = bool(route.get("write_intent_lease_required"))
    if not gate and not required_mode and not write_intent_required:
        return {}

    dynamic_target = bool(gate) and _route_lease_gate_is_dynamic(gate)
    if write_intent_required:
        gate_kind = "write_intent_lease"
        required_lease_type = "write_intent"
        lease_id_field = "write_intent_lease_id"
        target_derivation = "route_args_or_write_intent_payload"
        central_active_validation = True
    else:
        gate_kind = (
            "edit_lease"
            if required_mode == "exclusive_write"
            else "artifact_lease"
            if required_mode == "artifact"
            else "lease_gate"
        )
        required_lease_type = required_mode or str(gate.get("required_lease_type") or gate.get("lease_type") or "").strip()
        lease_id_field = "lease_id"
        target_derivation = _route_lease_gate_target_derivation(gate) if gate else "route_args"
        central_active_validation = bool(required_mode) and not dynamic_target

    model: dict[str, Any] = {
        "schema_id": "ion.branch_route_lease_gate_public.v0_1",
        "gate_kind": gate_kind,
        "required_lease_type": required_lease_type,
        "actor_proof_required": bool(route.get("agent_id_required")) or _route_agent_id_required(route) or write_intent_required,
        "lease_id_required": _route_lease_id_required(route) if not write_intent_required else True,
        "lease_id_field": lease_id_field,
        "target_derivation": target_derivation,
        "central_gate_actor_lease_proof_required": bool(required_lease_type) or write_intent_required,
        "central_active_lease_validation": central_active_validation,
        "handler_dynamic_target_gate_deferred": dynamic_target,
        "handler_fail_closed_required": dynamic_target,
        "central_enforcement": (
            "actor_and_lease_proof_required_target_validation_deferred_to_handler"
            if dynamic_target
            else "active_lease_validated_before_delegation"
            if central_active_validation
            else "actor_proof_only"
        ),
    }
    if gate:
        model["lease_gate"] = dict(gate)
    return model


def _handler_dynamic_target_gate_deferred_metadata(
    *,
    branch_id: str,
    route_id: str,
    route: Mapping[str, Any],
    route_args: Mapping[str, Any],
) -> dict[str, Any]:
    gate = _route_lease_gate(route)
    if not gate or not _route_lease_gate_is_dynamic(gate):
        return {}
    agent_id = str(route_args.get("agent_id") or route_args.get("worker_id") or "").strip()
    lease_id = str(route_args.get("lease_id") or "").strip()
    return {
        "handler_dynamic_target_gate_deferred": {
            "deferred": True,
            "branch_id": branch_id,
            "route_id": route_id,
            "required_lease_type": _route_required_lease_mode(route),
            "required_fields": ["agent_id", "lease_id"],
            "provided_agent_id": bool(agent_id),
            "provided_lease_id": bool(lease_id),
            "target_derivation": _route_lease_gate_target_derivation(gate),
            "central_active_lease_validation": False,
            "handler_fail_closed_required": True,
            "reason": "lease_target_derivation_is_handler_dynamic",
        }
    }


def _public_required_mutation_fields(route: Mapping[str, Any]) -> list[str]:
    existing = route.get("required_mutation_fields")
    if isinstance(existing, list):
        return [str(field) for field in existing]
    if not _route_lease_gate(route):
        return []
    fields: list[str] = []
    if route.get("idempotency_required"):
        fields.append("idempotency_key")
    if route.get("confirmation_required"):
        fields.append("confirmation")
    if _route_agent_id_required(route):
        fields.append("agent_id")
    if route.get("write_intent_lease_required"):
        fields.append("write_intent_lease_id")
    elif _route_lease_id_required(route):
        fields.append("lease_id")
    return fields


def _route_lease_path_candidates(root: Path, value: Any) -> list[str]:
    raw = str(value or "").strip()
    if not raw:
        return []
    cleaned = _clean_lease_path_value(raw)
    candidates = [candidate for candidate in (raw, cleaned) if candidate]
    path = Path(raw)
    if not path.is_absolute():
        path = root / raw
    resolved = path.resolve(strict=False)
    candidates.append(resolved.as_posix())
    try:
        candidates.append(resolved.relative_to(root).as_posix())
    except ValueError:
        pass
    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        text = _clean_lease_path_value(candidate)
        if text and text not in seen:
            deduped.append(text)
            seen.add(text)
    return deduped


def _route_lease_target_row(root: Path, value: Any) -> dict[str, Any]:
    candidates = _route_lease_path_candidates(root, value)
    return {
        "target_path": candidates[0] if candidates else str(value or ""),
        "lease_path_candidates": candidates,
    }


def _append_route_lease_target_values(root: Path, targets: list[dict[str, Any]], value: Any) -> None:
    if isinstance(value, list):
        for item in value:
            if isinstance(item, Mapping):
                nested_value = item.get("target_path") or item.get("path")
                if str(nested_value or "").strip():
                    targets.append(_route_lease_target_row(root, nested_value))
            elif str(item or "").strip():
                targets.append(_route_lease_target_row(root, item))
        return
    if isinstance(value, Mapping):
        nested_value = value.get("target_path") or value.get("path")
        if str(nested_value or "").strip():
            targets.append(_route_lease_target_row(root, nested_value))
        return
    if isinstance(value, (str, Path)) and str(value or "").strip():
        targets.append(_route_lease_target_row(root, value))


def _render_route_lease_target_template(template: str, route_args: Mapping[str, Any]) -> tuple[str, str | None]:
    missing: list[str] = []

    def replace(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        if key == "safe_idempotency_key":
            value = _route_safe_idempotency_key(route_args.get("idempotency_key"))
        else:
            raw = route_args.get(key)
            if key == "agent_id" and raw in (None, ""):
                raw = route_args.get("worker_id")
            value = str(raw or "").strip()
            if key.endswith("_id") or key in {"root_id"}:
                value = _clean_lease_path_value(value)
        if not value:
            missing.append(key)
        return value

    rendered = re.sub(r"\{([^{}]+)\}", replace, template)
    if missing:
        return "", "lease_target_template_arg_required"
    return rendered, None


def _append_route_lease_gate_targets(
    root: Path,
    targets: list[dict[str, Any]],
    gate: Mapping[str, Any],
    route_args: Mapping[str, Any],
) -> str | None:
    target_path = str(gate.get("target_path") or "").strip()
    if target_path:
        _append_route_lease_target_values(root, targets, target_path)
    target_template = str(gate.get("target_path_template") or "").strip()
    if target_template:
        rendered, finding = _render_route_lease_target_template(target_template, route_args)
        if finding:
            return finding
        _append_route_lease_target_values(root, targets, rendered)
    target_argument = str(gate.get("target_argument") or "").strip()
    if target_argument:
        value = route_args.get(target_argument)
        if value in (None, "", []):
            return "lease_target_argument_required"
        _append_route_lease_target_values(root, targets, value)
    return None


def _route_write_intent_lease_id(route_args: Mapping[str, Any]) -> str:
    for key in (
        "write_intent_lease_id",
        "write_intent_lease",
        "write_lease_id",
        "lease_id",
    ):
        raw = route_args.get(key)
        if isinstance(raw, Mapping):
            continue
        value = str(raw or "").strip()
        if value:
            return value
    for key in ("write_intent", "write_intent_lease"):
        nested = route_args.get(key)
        if not isinstance(nested, Mapping):
            continue
        for nested_key in ("write_intent_lease_id", "lease_id", "id"):
            value = str(nested.get(nested_key) or "").strip()
            if value:
                return value
    return ""


def _upload_session_target_path(root: Path, upload_id: str) -> str:
    if not re.fullmatch(r"upload_[0-9TZ-]+_[a-z0-9_]+", upload_id):
        return ""
    path = root / "ION/05_context/current/chatgpt_connector/artifact_uploads" / f"{upload_id}.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return ""
    return str(payload.get("target_path") or "").strip() if isinstance(payload, Mapping) else ""


def _derive_route_lease_targets(root: Path, route: Mapping[str, Any], route_args: Mapping[str, Any]) -> tuple[list[dict[str, Any]], str | None]:
    targets: list[dict[str, Any]] = []
    gate = _route_lease_gate(route)
    if gate:
        gate_finding = _append_route_lease_gate_targets(root, targets, gate, route_args)
        if gate_finding:
            return [], gate_finding
    for key in ("write_intent_required_target_roots", "required_write_intent_target_paths"):
        raw_required = route.get(key)
        if isinstance(raw_required, list):
            _append_route_lease_target_values(root, targets, raw_required)
    for key in ("target_paths", "paths", "write_set", "target_write_paths", "write_paths"):
        _append_route_lease_target_values(root, targets, route_args.get(key))
    for key in ("target_path", "path"):
        _append_route_lease_target_values(root, targets, route_args.get(key))
    write_intent = route_args.get("write_intent")
    if isinstance(write_intent, Mapping):
        for key in ("target_paths", "paths", "write_set", "target_write_paths", "write_paths"):
            _append_route_lease_target_values(root, targets, write_intent.get(key))
        for key in ("target_path", "path"):
            _append_route_lease_target_values(root, targets, write_intent.get(key))
    operations = route_args.get("operations")
    if isinstance(operations, list):
        project_id = str(route_args.get("project_id") or "").strip()
        project_spec = None
        if project_id:
            try:
                from .ion_project_workbench import resolve_project

                project_spec, _ = resolve_project(root, project_id)
            except Exception:
                project_spec = None
        for operation in operations:
            if not isinstance(operation, Mapping):
                return [], "lease_target_operation_invalid"
            value = str(operation.get("target_path") or operation.get("path") or "").strip()
            if not value:
                return [], "lease_target_operation_path_required"
            if project_spec is not None:
                candidates = [value, f"project_workbench/{project_id}/{value}"]
                target = (project_spec.root / value).resolve(strict=False)
                candidates.append(target.as_posix())
                try:
                    candidates.append(target.relative_to(root).as_posix())
                except ValueError:
                    pass
                targets.append(
                    {
                        "target_path": value,
                        "lease_path_candidates": _clean_string_list(candidates),
                    }
                )
            else:
                targets.append(_route_lease_target_row(root, value))
    upload_id = str(route_args.get("upload_id") or "").strip()
    if upload_id:
        target_path = _upload_session_target_path(root, upload_id)
        if target_path:
            targets.append(_route_lease_target_row(root, target_path))
    artifact_name = str(route_args.get("artifact_name") or "").strip()
    if not targets and artifact_name:
        targets.append(
            _route_lease_target_row(
                root,
                f"ION/05_context/current/chatgpt_connector/artifacts/{artifact_name}",
            )
        )
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for target in targets:
        key = "|".join(target.get("lease_path_candidates") or [str(target.get("target_path") or "")])
        if key and key not in seen:
            deduped.append(target)
            seen.add(key)
    if not deduped:
        return [], "lease_target_not_derivable"
    return deduped, None


def _enforce_route_write_intent_lease_gate(
    *,
    shell_root: Path,
    branch_id: str,
    route_id: str,
    route: Mapping[str, Any],
    route_args: Mapping[str, Any],
) -> dict[str, Any] | None:
    if not bool(route.get("write_intent_lease_required")):
        return None
    agent_id = str(route_args.get("agent_id") or route_args.get("worker_id") or "").strip()
    lease_id = _route_write_intent_lease_id(route_args)
    base = {
        "branch_id": branch_id,
        "route_id": route_id,
        "required_lease_type": "write_intent",
        "required_fields": ["agent_id", "write_intent_lease_id"],
        "provided_agent_id": bool(agent_id),
        "provided_write_intent_lease_id": bool(lease_id),
        "write_intent_mutation_context": branch_id,
        "lease_gate_public": _public_route_lease_gate_model(route),
    }
    if not agent_id or not lease_id:
        return _blocked(
            "ionActionBranchInvoke",
            "write_intent_lease_required",
            refusal_class="LEASE_REQUIRED",
            data=base,
        )
    target_files, finding = _derive_route_lease_targets(shell_root, route, route_args)
    if finding:
        return _blocked(
            "ionActionBranchInvoke",
            finding,
            refusal_class="LEASE_TARGET_NOT_DERIVABLE",
            data={**base, "target_files": target_files},
        )
    from .ion_worker_shift_presence import require_active_write_intent_lease

    gate = require_active_write_intent_lease(
        shell_root,
        agent_id=agent_id,
        lease_id=lease_id,
        target_files=target_files,
        target_route_id=route_id,
        mutation_context=branch_id,
        idempotency_key=str(route_args.get("idempotency_key") or "").strip() or None,
    )
    if not gate.get("ok"):
        return _blocked(
            "ionActionBranchInvoke",
            str(gate.get("finding") or "write_intent_lease_required"),
            refusal_class="LEASE_REQUIRED",
            data={**base, **gate, "target_files": target_files},
        )
    return None


def _enforce_route_lease_gate(
    *,
    shell_root: Path,
    branch_id: str,
    route_id: str,
    route: Mapping[str, Any],
    route_args: Mapping[str, Any],
) -> dict[str, Any] | None:
    required_mode = _route_required_lease_mode(route)
    if not required_mode:
        return None
    agent_id = str(route_args.get("agent_id") or route_args.get("worker_id") or "").strip()
    lease_id = str(route_args.get("lease_id") or "").strip()
    gate = _route_lease_gate(route)
    base = {
        "branch_id": branch_id,
        "route_id": route_id,
        "required_lease_type": required_mode,
        "required_fields": ["agent_id", "lease_id"],
        "provided_agent_id": bool(agent_id),
        "provided_lease_id": bool(lease_id),
        "lease_gate_public": _public_route_lease_gate_model(route),
    }
    if gate:
        base["lease_gate"] = dict(gate)
    if not agent_id or not lease_id:
        return _blocked(
            "ionActionBranchInvoke",
            f"{required_mode}_lease_required",
            refusal_class="LEASE_REQUIRED",
            data=base,
        )
    if gate and _route_lease_gate_is_dynamic(gate):
        return None
    target_files, finding = _derive_route_lease_targets(shell_root, route, route_args)
    if finding:
        return _blocked(
            "ionActionBranchInvoke",
            finding,
            refusal_class="LEASE_TARGET_NOT_DERIVABLE",
            data={**base, "target_files": target_files},
        )
    from .ion_worker_shift_presence import require_active_edit_lease

    gate = require_active_edit_lease(
        shell_root,
        agent_id=agent_id,
        lease_id=lease_id,
        target_files=target_files,
        required_mode=required_mode,
    )
    if not gate.get("ok"):
        return _blocked(
            "ionActionBranchInvoke",
            f"{required_mode}_lease_required",
            refusal_class="LEASE_REQUIRED",
            data={**base, **gate, "target_files": target_files},
        )
    return None


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _repo_rel(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root).as_posix()
    except ValueError:
        # Tolerate the reversed-argument shape used by bounded sandbox helpers:
        # _repo_rel(root, child) should still render child relative to root.
        try:
            return root.resolve(strict=False).relative_to(path).as_posix()
        except ValueError:
            return path.as_posix()


def _workspace_root(root: Path) -> Path:
    return root.parent if root.name == "ION_Developement" else root


def _display_path(path: Path, root: Path) -> str:
    workspace = _workspace_root(root)
    try:
        return path.resolve(strict=False).relative_to(workspace).as_posix()
    except ValueError:
        return _repo_rel(path, root)


def _resolve_workspace_path(root: Path, value: str | Path) -> Path:
    raw = Path(str(value))
    if raw.is_absolute():
        return raw
    if raw.parts and raw.parts[0] == "ION_GPT":
        return (_workspace_root(root) / raw).resolve(strict=False)
    return (root / raw).resolve(strict=False)


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_object(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return dict(value) if isinstance(value, Mapping) else None


def _text_excerpt(path: Path, *, max_chars: int = 700) -> str | None:
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    return text[:max(0, max_chars)]


def _file_ref(root: Path, path: Path, *, include_excerpt: bool = False, max_excerpt_chars: int = 700) -> dict[str, Any]:
    ref: dict[str, Any] = {
        "path": _display_path(path, root),
        "exists": path.is_file(),
    }
    if path.is_file():
        ref["size_bytes"] = path.stat().st_size
        ref["sha256"] = _sha256_file(path)
        if include_excerpt:
            ref["excerpt"] = _text_excerpt(path, max_chars=max_excerpt_chars)
    return ref


def _latest_context_upload_root(root: Path) -> Path:
    workspace_candidate = _workspace_root(root) / "ION_GPT/02_PACKAGES_TO_UPLOAD"
    if workspace_candidate.exists():
        return workspace_candidate
    return root / "ION_GPT/02_PACKAGES_TO_UPLOAD"


def _upload_set_timestamp(path: Path) -> str | None:
    prefix = "ION_GPT_UPLOAD_SET_"
    return path.name[len(prefix) :] if path.name.startswith(prefix) else None


def _latest_upload_set(root: Path) -> Path | None:
    upload_root = _latest_context_upload_root(root)
    if not upload_root.is_dir():
        return None
    candidates = [
        item
        for item in upload_root.iterdir()
        if item.is_dir() and item.name.startswith("ION_GPT_UPLOAD_SET_")
    ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: (_upload_set_timestamp(item) or "", item.stat().st_mtime), reverse=True)[0]


def _final_operator_kit_timestamp(path: Path) -> str | None:
    return path.name[len(FINAL_OPERATOR_KIT_PREFIX) :] if path.name.startswith(FINAL_OPERATOR_KIT_PREFIX) else None


def _latest_final_operator_kit(root: Path) -> Path | None:
    upload_root = _latest_context_upload_root(root)
    if not upload_root.is_dir():
        return None
    candidates = [
        item
        for item in upload_root.iterdir()
        if item.is_dir() and item.name.startswith(FINAL_OPERATOR_KIT_PREFIX)
    ]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda item: (_final_operator_kit_timestamp(item) or "", item.stat().st_mtime),
        reverse=True,
    )[0]


def _final_operator_manifest_path(kit: Path) -> Path:
    return kit / FINAL_OPERATOR_KIT_KNOWLEDGE_DIR / "00_ROOT_MANIFEST.json"


def _latest_upload_manifest(root: Path) -> tuple[Path | None, dict[str, Any] | None]:
    final_kit = _latest_final_operator_kit(root)
    if final_kit:
        manifest_path = _final_operator_manifest_path(final_kit)
        return manifest_path, _json_object(manifest_path)
    upload_set = _latest_upload_set(root)
    if not upload_set:
        return None, None
    manifest_path = upload_set / "ION_GPT_UPLOAD_MANIFEST.json"
    return manifest_path, _json_object(manifest_path)


def _latest_context_mount_state(root: Path, manifest: Mapping[str, Any] | None) -> str:
    if manifest:
        return str(manifest.get("mount_truth_state_for_rebuild") or "FULL_LOCAL_SANDBOX_MOUNT")
    if (root / "ION/05_context/current/codex_solo/CAPSULE.md").is_file():
        return "LOCAL_SANDBOX_PARTIAL_MOUNT"
    return "UNMOUNTED_ROLEPLAY_BLOCKED"


def _latest_handoff_files(root: Path, *, limit: int = 5) -> list[Path]:
    history = root / "ION/05_context/current/codex_solo/history"
    if not history.is_dir():
        return []
    candidates = [item for item in history.glob("codex_solo_post_*.json") if item.is_file()]
    return sorted(candidates, key=lambda item: (item.stat().st_mtime, item.name), reverse=True)[: max(1, limit)]


def _receipt_files(root: Path, *, limit: int = 10) -> list[Path]:
    current = root / "ION/05_context/current"
    patterns = [
        "codex_solo/history/codex_solo_post_*.json",
        "context_settlement/accepted/*.json",
        "context_settlement/inbox/*.json",
        "chatgpt_connector/codex_queue_runs/*/context_receipt.json",
        "chatgpt_connector/codex_queue_runs/*/worker_context_awareness_receipt.json",
        "action_gateway/runtime/*receipt*.json",
    ]
    candidates: list[Path] = []
    if current.is_dir():
        for pattern in patterns:
            candidates.extend(item for item in current.glob(pattern) if item.is_file())
    unique = {path.resolve(strict=False): path for path in candidates}
    return sorted(unique.values(), key=lambda item: (item.stat().st_mtime, item.name), reverse=True)[: max(1, limit)]


def _latest_context_required_reads(root: Path, upload_set: Path | None) -> list[Path]:
    final_kit = _latest_final_operator_kit(root)
    if final_kit:
        knowledge_root = final_kit / FINAL_OPERATOR_KIT_KNOWLEDGE_DIR
        return [
            root / "ION/REPO_AUTHORITY.md",
            root / "ION/02_architecture/ION_MOUNT_CONTRACT.md",
            root / "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
            root / "ION/05_context/current/codex_solo/MINI.md",
            root / "ION/05_context/current/codex_solo/CAPSULE.md",
            root / "ION/05_context/current/codex_solo/STATUS.json",
            final_kit / "00_READ_ME_FIRST_DO_THIS_ONLY.md",
            final_kit / "01_PASTE_THIS_IN_GPT_BUILDER_INSTRUCTIONS.md",
            knowledge_root / "00_ROOT_MANIFEST.json",
            knowledge_root / "01_START_HERE_MOUNT_ORDER.md",
            knowledge_root / "04_ACTIONS_MCP_AND_BRANCH_GATEWAY.md",
            knowledge_root / "05_RECEIPTS_ACCEPTED_STATE_AND_SETTLEMENT.md",
            knowledge_root / "09_OPERATOR_APPROVALS_AND_RED_ALERT.md",
            root / "ION/04_packages/kernel/ion_action_mcp_branch_leaders.py",
            root / REGISTRY_RELATIVE_PATH,
        ]

    upload_root = upload_set or (_latest_context_upload_root(root) / "ION_GPT_UPLOAD_SET_UNKNOWN")
    markdown_root = _latest_context_upload_root(root) / "UPLOAD_THESE_MARKDOWN"
    return [
        root / "ION/REPO_AUTHORITY.md",
        root / "ION/02_architecture/ION_MOUNT_CONTRACT.md",
        root / "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
        root / "ION/05_context/current/codex_solo/MINI.md",
        root / "ION/05_context/current/codex_solo/CAPSULE.md",
        root / "ION/05_context/current/codex_solo/STATUS.json",
        upload_root / "ION_GPT_UPLOAD_MANIFEST.json",
        upload_root / "ION_CODEX_TASK_RETURN.md",
        markdown_root / "01_START_HERE_MOUNT_ORDER.md",
        markdown_root / "04_ACTIONS_MCP_AND_BRANCH_GATEWAY.md",
        markdown_root / "05_RECEIPTS_ACCEPTED_STATE_AND_SETTLEMENT.md",
        markdown_root / "09_OPERATOR_INTERFACE_AND_APPROVALS.md",
        markdown_root / "10_RED_ALERT_FALLBACK_AND_FAILURE_MODES.md",
        root / "ION/04_packages/kernel/ion_action_mcp_branch_leaders.py",
        root / REGISTRY_RELATIVE_PATH,
    ]


def _route_templates() -> list[dict[str, Any]]:
    return [
        {
            "operation": "ionActionBranchInvoke",
            "branch_id": "latest_context",
            "route_id": route_id,
            "expected_route_schema_version": "v0",
            "args": {},
        }
        for route_id in [
            "mount_status",
            "latest_handoff",
            "current_context_pack",
            "recent_receipts",
            "next_allowed_routes",
            "package_freshness",
        ]
    ]


def _latest_context_base(root: Path, route_id: str, *, manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "ok": True,
        "schema_id": "ion.latest_context_branch.v0_1",
        "branch_id": "latest_context",
        "route_id": route_id,
        "mount_truth_state": _latest_context_mount_state(root, manifest),
        "source_posture": "repo_observed_candidate_context_handoff",
        "action_mount_equivalent": False,
        "action_mount_equivalent_reason": (
            "Branch Gateway latest_context v0.1 returns proof-bearing read views, "
            "but does not yet enforce all mount-parity refusal barriers."
        ),
        "authority": {
            "route_authority_class": "read-only",
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
        "non_claims": dict(LATEST_CONTEXT_NON_CLAIMS),
        "mutates_active_state": False,
    }


def _redact_gemini_cli_broker_text(text: str) -> str:
    if not text:
        return text
    redacted = text
    redacted = re.sub(r"AIza[0-9A-Za-z_-]{20,}", "AIza***REDACTED***", redacted)
    redacted = re.sub(r"ya29\\.[0-9A-Za-z_.-]+", "ya29.***REDACTED***", redacted)
    redacted = re.sub(
        r"(?i)(GEMINI_API_KEY|GOOGLE_API_KEY|GOOGLE_APPLICATION_CREDENTIALS)\\s*[=:]\\s*[^\\s,;]+",
        r"\\1=***REDACTED***",
        redacted,
    )
    return redacted



GEMINI_ION_SANDBOX_ROOT_REL = Path("ION/05_context/current/gemini_ion_sandboxes")
GEMINI_ION_SANDBOX_DEFAULT_INCLUDE_ROOTS = [
    "ION/04_packages/kernel",
    "ION/tests",
    "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml",
    "ION/05_context/current/domain_weaver/swarm_evolution/POST_FISSION_OBSERVATION_FANIN_SETTLEMENT_AND_EXACT_BINDING_MATERIALIZATION_STOP.candidate.json",
]
GEMINI_ION_SANDBOX_EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
    "codex_queue_runs",
    "archive_attachments",
}


def _gemini_ion_sandbox_authority() -> dict[str, bool]:
    return {
        "sandbox_write_authority": True,
        "sandbox_shell_authority": True,
        "sandbox_test_authority": True,
        "active_repo_write_authority": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "git_push_authority": False,
        "deletion_authority_outside_sandbox": False,
    }


def _gemini_ion_sandbox_safe_id(value: Any) -> str:
    sandbox_id = str(value or f"gemini-ion-sandbox-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}").strip()
    if not sandbox_id or not re.match(r"^[A-Za-z0-9_.:-]+$", sandbox_id):
        raise ValueError("unsafe_sandbox_id")
    return sandbox_id


def _gemini_ion_sandbox_paths(root: Path, sandbox_id: str) -> dict[str, Path]:
    base = root / GEMINI_ION_SANDBOX_ROOT_REL / sandbox_id
    return {
        "base": base,
        "workspace": base / "workspace",
        "results": base / "results",
        "receipts": base / "receipts",
        "manifest": base / "sandbox_manifest.json",
    }


def _gemini_ion_sandbox_roots(values: Any) -> list[str]:
    raw = values if isinstance(values, list) and values else GEMINI_ION_SANDBOX_DEFAULT_INCLUDE_ROOTS
    roots: list[str] = []
    for item in raw:
        text = str(item).strip().strip("/")
        if not text:
            continue
        if text == ".." or text.startswith("../") or "/../" in text:
            raise ValueError("unsafe_include_root")
        if not (text == "ION" or text.startswith("ION/")):
            raise ValueError("include_root_outside_ion")
        roots.append(text)
    return roots


def _gemini_ion_sandbox_iter_files(path: Path):
    if path.is_file():
        yield path
        return
    for child in sorted(path.rglob("*")):
        if child.is_dir():
            continue
        if set(child.relative_to(path).parts) & GEMINI_ION_SANDBOX_EXCLUDE_DIRS:
            continue
        yield child


def _gemini_ion_sandbox_find_binary() -> str | None:
    candidates = [
        shutil.which("gemini"),
        str(Path.home() / ".npm-global/bin/gemini"),
        "/usr/local/bin/gemini",
        "/opt/homebrew/bin/gemini",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def _gemini_ion_sandbox_env_posture() -> dict[str, Any]:
    keys = [
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_LOCATION",
        "GOOGLE_GENAI_USE_VERTEXAI",
        "GOOGLE_APPLICATION_CREDENTIALS",
    ]
    return {f"{key}_present": bool(os.getenv(key)) for key in keys} | {"redaction": "presence_only_no_values_recorded"}


def _gemini_ion_sandbox_plan(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    sandbox_id = _gemini_ion_sandbox_safe_id(args.get("sandbox_id"))
    paths = _gemini_ion_sandbox_paths(root, sandbox_id)
    return {
        "ok": True,
        "schema_id": "ion.gemini_ion_sandbox.plan.v1_candidate",
        "sandbox_id": sandbox_id,
        "sandbox_path": _repo_rel(root, paths["base"]),
        "workspace_path": _repo_rel(root, paths["workspace"]),
        "include_roots": _gemini_ion_sandbox_roots(args.get("include_roots")),
        "max_files": int(args.get("max_files") or 5000),
        "max_bytes": int(args.get("max_bytes") or 100_000_000),
        "would_materialize": False,
        "authority": _gemini_ion_sandbox_authority(),
    }


def _gemini_ion_sandbox_materialize(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    sandbox_id = _gemini_ion_sandbox_safe_id(args.get("sandbox_id"))
    include_roots = _gemini_ion_sandbox_roots(args.get("include_roots"))
    max_files = int(args.get("max_files") or 5000)
    max_bytes = int(args.get("max_bytes") or 100_000_000)
    overwrite = bool(args.get("overwrite"))
    paths = _gemini_ion_sandbox_paths(root, sandbox_id)
    base = paths["base"]
    workspace = paths["workspace"]
    if base.exists() and not overwrite:
        return {
            "ok": False,
            "finding": "sandbox_exists",
            "sandbox_id": sandbox_id,
            "sandbox_path": _repo_rel(root, base),
            "requires_overwrite": True,
            "authority": _gemini_ion_sandbox_authority(),
        }
    if base.exists() and overwrite:
        shutil.rmtree(base)
    workspace.mkdir(parents=True, exist_ok=True)
    copied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    total_bytes = 0
    for include_root in include_roots:
        source = root / include_root
        if not source.exists():
            skipped.append({"path": include_root, "reason": "missing"})
            continue
        for src in _gemini_ion_sandbox_iter_files(source):
            if len(copied) >= max_files:
                skipped.append({"path": include_root, "reason": "max_files_reached"})
                break
            size = src.stat().st_size
            if total_bytes + size > max_bytes:
                skipped.append({"path": _repo_rel(root, src), "reason": "max_bytes_reached", "size_bytes": size})
                continue
            dst = workspace / _repo_rel(root, src)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            total_bytes += size
            copied.append({
                "path": _repo_rel(root, src),
                "sandbox_path": _repo_rel(root, dst),
                "size_bytes": size,
                "sha256": _sha256_file(dst),
            })
    manifest = {
        "schema_id": "ion.gemini_ion_sandbox.manifest.v1_candidate",
        "created_at": _now(),
        "sandbox_id": sandbox_id,
        "sandbox_path": _repo_rel(root, base),
        "workspace_path": _repo_rel(root, workspace),
        "include_roots": include_roots,
        "copied_file_count": len(copied),
        "copied_bytes": total_bytes,
        "copied_files": copied,
        "skipped": skipped,
        "authority": _gemini_ion_sandbox_authority(),
        "non_claims": [
            "This sandbox is candidate-only.",
            "Gemini may write only inside the sandbox workspace.",
            "No active ION state is accepted from this sandbox without later proof settlement.",
        ],
    }
    paths["manifest"].parent.mkdir(parents=True, exist_ok=True)
    paths["manifest"].write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = {
        "schema_id": "ion.gemini_ion_sandbox.materialize_receipt.v1_candidate",
        "created_at": _now(),
        "ok": True,
        "sandbox_id": sandbox_id,
        "manifest_path": _repo_rel(root, paths["manifest"]),
        "manifest_sha256": _sha256_file(paths["manifest"]),
        "authority": _gemini_ion_sandbox_authority(),
    }
    receipt_path = paths["receipts"] / "materialize_receipt.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "schema_id": "ion.gemini_ion_sandbox.materialize_result.v1_candidate",
        "sandbox_id": sandbox_id,
        "sandbox_path": _repo_rel(root, base),
        "workspace_path": _repo_rel(root, workspace),
        "manifest_path": _repo_rel(root, paths["manifest"]),
        "manifest_sha256": _sha256_file(paths["manifest"]),
        "receipt_path": _repo_rel(root, receipt_path),
        "copied_file_count": len(copied),
        "copied_bytes": total_bytes,
        "skipped_count": len(skipped),
        "authority": _gemini_ion_sandbox_authority(),
    }


def _gemini_ion_sandbox_status(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    base = root / GEMINI_ION_SANDBOX_ROOT_REL
    sandboxes: list[dict[str, Any]] = []
    if base.exists():
        for child in sorted(base.iterdir()):
            if child.is_dir():
                manifest = child / "sandbox_manifest.json"
                sandboxes.append({
                    "sandbox_id": child.name,
                    "path": _repo_rel(root, child),
                    "manifest_exists": manifest.exists(),
                    "manifest_sha256": _sha256_file(manifest),
                })
    return {
        "ok": True,
        "schema_id": "ion.gemini_ion_sandbox.status.v1_candidate",
        "sandbox_root": _repo_rel(root, base),
        "sandbox_count": len(sandboxes),
        "sandboxes": sandboxes,
        "authority": _gemini_ion_sandbox_authority(),
    }


def _gemini_ion_sandbox_result(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    sandbox_id = _gemini_ion_sandbox_safe_id(args.get("sandbox_id"))
    name = str(args.get("name") or "gemini_run_probe_result.json")
    if "/" in name or ".." in name or not name.endswith(".json"):
        return {"ok": False, "finding": "unsafe_result_name", "name": name}
    target = _gemini_ion_sandbox_paths(root, sandbox_id)["results"] / name
    if not target.exists():
        return {"ok": False, "finding": "result_missing", "path": _repo_rel(root, target)}
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        payload = {"raw_text": target.read_text(encoding="utf-8", errors="replace")}
    return {
        "ok": True,
        "schema_id": "ion.gemini_ion_sandbox.result_read.v1_candidate",
        "sandbox_id": sandbox_id,
        "path": _repo_rel(root, target),
        "sha256": _sha256_file(target),
        "result": payload,
        "authority": _gemini_ion_sandbox_authority(),
    }


def _gemini_ion_sandbox_run_probe(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    sandbox_id = _gemini_ion_sandbox_safe_id(args.get("sandbox_id"))
    paths = _gemini_ion_sandbox_paths(root, sandbox_id)
    workspace = paths["workspace"]
    if not workspace.exists():
        return {"ok": False, "finding": "sandbox_workspace_missing", "sandbox_id": sandbox_id}
    gemini = _gemini_ion_sandbox_find_binary()
    if not gemini:
        return {"ok": False, "finding": "gemini_binary_missing", "env_posture": _gemini_ion_sandbox_env_posture()}
    timeout = int(args.get("timeout") or 300)
    prompt = str(args.get("prompt") or (
        "You are inside a disposable ION sandbox. Inspect the copied files and write a concise "
        "candidate report to GEMINI_SANDBOX_REPORT.md. Do not access secrets, do not push git, "
        "and do not claim accepted state."
    ))
    use_cli_sandbox = bool(args.get("cli_sandbox", False))
    argv = [gemini, "--skip-trust", "--approval-mode", "yolo"]
    if use_cli_sandbox:
        argv.append("--sandbox")
    argv.extend(["--prompt", prompt])
    if args.get("model"):
        argv.extend(["--model", str(args.get("model"))])
    completed = subprocess.run(
        argv,
        cwd=str(workspace),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=max(timeout, 30),
        check=False,
    )
    result = {
        "schema_id": "ion.gemini_ion_sandbox.run_probe_result.v1_candidate",
        "created_at": _now(),
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "sandbox_id": sandbox_id,
        "workspace_path": _repo_rel(root, workspace),
        "argv_shape": ["gemini", *(["--sandbox"] if use_cli_sandbox else []), "--prompt", "<redacted_prompt>", *(["--model", str(args.get("model"))] if args.get("model") else [])],
        "stdout_tail": _redact_gemini_cli_broker_text((completed.stdout or "")[-8000:]),
        "stderr_tail": _redact_gemini_cli_broker_text((completed.stderr or "")[-8000:]),
        "env_posture": _gemini_ion_sandbox_env_posture(),
        "authority": _gemini_ion_sandbox_authority(),
        "non_claims": [
            "Gemini output is candidate-only.",
            "Any files changed are inside the sandbox workspace.",
            "No active repo mutation is accepted by this result.",
        ],
    }
    result_path = paths["results"] / "gemini_run_probe_result.json"
    receipt_path = paths["receipts"] / "gemini_run_probe_receipt.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema_id": "ion.gemini_ion_sandbox.run_probe_receipt.v1_candidate",
        "created_at": _now(),
        "ok": result["ok"],
        "sandbox_id": sandbox_id,
        "result_path": _repo_rel(root, result_path),
        "result_sha256": _sha256_file(result_path),
        "authority": _gemini_ion_sandbox_authority(),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "ok": result["ok"],
        "schema_id": "ion.gemini_ion_sandbox.run_probe_summary.v1_candidate",
        "sandbox_id": sandbox_id,
        "result_path": _repo_rel(root, result_path),
        "result_sha256": _sha256_file(result_path),
        "receipt_path": _repo_rel(root, receipt_path),
        "returncode": completed.returncode,
        "authority": _gemini_ion_sandbox_authority(),
    }


def _invoke_gemini_cli_broker_route(
    root: Path,
    *,
    route_id: str,
    args: Mapping[str, Any],
) -> dict[str, Any]:
    """Invoke the dAimon-local Gemini CLI broker through fixed command shapes only."""
    broker = root / "dAimon/gemini_cli/scripts/gemini_cli_action_broker_v2.py"
    if not broker.exists():
        return {
            "ok": False,
            "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
            "finding": "gemini_cli_action_broker_missing",
            "broker_path": str(broker.relative_to(root) if broker.is_relative_to(root) else broker),
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        }

    route_alias = str(args.get("broker_command") or route_id)
    argv: list[str] = [sys.executable, str(broker)]
    timeout = int(args.get("timeout") or 120)
    mutates_state = False

    if route_alias in {"sandbox_plan", "gemini_ion_sandbox_plan"}:
        return _gemini_ion_sandbox_plan(root, args)
    if route_alias in {"sandbox_materialize", "gemini_ion_sandbox_materialize"}:
        return _gemini_ion_sandbox_materialize(root, args)
    if route_alias in {"sandbox_status", "gemini_ion_sandbox_status"}:
        return _gemini_ion_sandbox_status(root, args)
    if route_alias in {"sandbox_run_probe", "gemini_ion_sandbox_run_probe"}:
        return _gemini_ion_sandbox_run_probe(root, args)
    if route_alias in {"sandbox_result", "gemini_ion_sandbox_result"}:
        return _gemini_ion_sandbox_result(root, args)

    if route_alias in {"broker_status", "action_broker_status_live", "status"}:
        argv.append("status")
        if bool(args.get("write")):
            argv.append("--write")
            mutates_state = True
    elif route_alias in {"broker_result", "result"}:
        argv.append("result")
        name = str(args.get("name") or "20260527_gemini_readiness_summary.json")
        if "/" in name or ".." in name or not name.endswith(".json"):
            return {
                "ok": False,
                "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                "finding": "unsafe_result_name",
                "name": name,
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        argv.extend(["--name", name])
    elif route_alias in {"broker_readiness", "readiness", "run-readiness"}:
        argv.append("run-readiness")
        argv.extend(["--timeout", str(timeout)])
        if bool(args.get("run_handoff")):
            if args.get("confirmation") != "ION_BOUNDED_WRITE_CONFIRMED":
                return {
                    "ok": False,
                    "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                    "finding": "run_handoff_requires_confirmation",
                    "required_confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
                    "accepted_state_claim": False,
                    "production_authority": False,
                    "live_execution_authority": False,
                    "secrets_authority": False,
                }
            argv.append("--run-handoff")
        mutates_state = True
    elif route_alias in {"broker_eval", "eval", "run-eval"}:
        eval_runner = root / "dAimon/gemini_cli/scripts/run_flash_lane_eval.py"
        if not eval_runner.exists():
            return {
                "ok": False,
                "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                "finding": "gemini_flash_lane_eval_runner_missing",
                "runner_path": "dAimon/gemini_cli/scripts/run_flash_lane_eval.py",
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        argv = [sys.executable, str(eval_runner), "--timeout", str(timeout)]
        mutates_state = True
    elif route_alias in {"broker_eval_strict", "eval_strict", "run-eval-strict"}:
        eval_runner = root / "dAimon/gemini_cli/scripts/run_flash_lane_eval_strict.py"
        if not eval_runner.exists():
            return {
                "ok": False,
                "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                "finding": "gemini_flash_lane_strict_eval_runner_missing",
                "runner_path": "dAimon/gemini_cli/scripts/run_flash_lane_eval_strict.py",
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        argv = [sys.executable, str(eval_runner), "--timeout", str(timeout)]
        mutates_state = True
    elif route_alias in {"broker_eval_policy", "eval_policy", "run-eval-policy"}:
        eval_runner = root / "dAimon/gemini_cli/scripts/run_flash_lane_eval_policy_grounded.py"
        if not eval_runner.exists():
            return {
                "ok": False,
                "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                "finding": "gemini_flash_lane_policy_eval_runner_missing",
                "runner_path": "dAimon/gemini_cli/scripts/run_flash_lane_eval_policy_grounded.py",
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        argv = [sys.executable, str(eval_runner), "--timeout", str(timeout)]
        mutates_state = True
    elif route_alias in {"boundary_selftest", "classifier_selftest", "run-boundary-selftest"}:
        classifier = root / "dAimon/gemini_cli/scripts/daimon_boundary_classifier_v2.py"
        if not classifier.exists():
            return {
                "ok": False,
                "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                "finding": "daimon_boundary_classifier_missing",
                "classifier_path": "dAimon/gemini_cli/scripts/daimon_boundary_classifier.py",
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        argv = [sys.executable, str(classifier), "--selftest"]
        mutates_state = True
    elif route_alias in {"broker_eval_classifier_loop", "eval_classifier_loop", "classifier_loop_eval", "run-classifier-loop-eval"}:
        eval_runner = root / "dAimon/gemini_cli/scripts/run_flash_lane_eval_classifier_loop_v2.py"
        if not eval_runner.exists():
            return {
                "ok": False,
                "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                "finding": "gemini_classifier_loop_eval_runner_missing",
                "runner_path": "dAimon/gemini_cli/scripts/run_flash_lane_eval_classifier_loop.py",
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        argv = [sys.executable, str(eval_runner), "--timeout", str(timeout)]
        mutates_state = True
    elif route_alias in {"boundary_integrate", "classifier_integrate", "apply-boundary-integration"}:
        integrator = root / "dAimon/gemini_cli/scripts/apply_boundary_classifier_integration.py"
        if not integrator.exists():
            return {
                "ok": False,
                "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                "finding": "daimon_boundary_integration_runner_missing",
                "runner_path": "dAimon/gemini_cli/scripts/apply_boundary_classifier_integration.py",
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        argv = [sys.executable, str(integrator), "--apply" if bool(args.get("apply")) else "--dry-run"]
        mutates_state = bool(args.get("apply"))
    elif route_alias in {"boundary_verify", "classifier_verify", "verify-boundary-integration"}:
        verifier = root / "dAimon/gemini_cli/scripts/verify_boundary_classifier_integration.py"
        if not verifier.exists():
            return {
                "ok": False,
                "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                "finding": "daimon_boundary_integration_verifier_missing",
                "runner_path": "dAimon/gemini_cli/scripts/verify_boundary_classifier_integration.py",
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        argv = [sys.executable, str(verifier)]
        mutates_state = True
    elif route_alias in {"boundary_core_fix", "classifier_core_fix", "fix-boundary-classifier-core"}:
        fixer = root / "dAimon/gemini_cli/scripts/apply_boundary_classifier_core_fix.py"
        if not fixer.exists():
            return {
                "ok": False,
                "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                "finding": "daimon_boundary_core_fix_runner_missing",
                "runner_path": "dAimon/gemini_cli/scripts/apply_boundary_classifier_core_fix.py",
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        argv = [sys.executable, str(fixer)]
        mutates_state = True
    elif route_alias in {"broker_run_packet", "run_packet", "run-packet"}:
        packet_runner = root / "dAimon/gemini_cli/scripts/gemini_cli_run_packet.py"
        if not packet_runner.exists():
            return {
                "ok": False,
                "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                "finding": "gemini_run_packet_runner_missing",
                "runner_path": "dAimon/gemini_cli/scripts/gemini_cli_run_packet.py",
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        argv = [sys.executable, str(packet_runner), "--timeout", str(timeout)]
        packet_id = str(args.get("packet_id") or "").strip()
        packet_path = str(args.get("packet_path") or args.get("path") or "").strip()
        expected_sha256 = str(args.get("expected_sha256") or "").strip()
        model = str(args.get("model") or "").strip()
        if not packet_id and not packet_path:
            return {
                "ok": False,
                "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                "finding": "packet_id_or_packet_path_required",
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        if packet_id:
            argv.extend(["--packet-id", packet_id])
        if packet_path:
            argv.extend(["--packet-path", packet_path])
        if expected_sha256:
            argv.extend(["--expected-sha256", expected_sha256])
        if model:
            argv.extend(["--model", model])
        mutates_state = True
    elif route_alias in {"domain_weave_controller_mvp", "controller_mvp", "run-domain-weave-controller-mvp", "domain_weave_controller_mvp_v2", "controller_mvp_v2", "run-domain-weave-controller-mvp-v2", "domain_weave_controller_mvp_v3", "controller_mvp_v3", "run-domain-weave-controller-mvp-v3", "domain_weave_controller_mvp_v4", "controller_mvp_v4", "run-domain-weave-controller-mvp-v4", "domain_weave_controller_mvp_v5", "controller_mvp_v5", "run-domain-weave-controller-mvp-v5", "domain_weave_controller_mvp_v6", "controller_mvp_v6", "run-domain-weave-controller-mvp-v6"}:
        if route_alias in {"domain_weave_controller_mvp_v6", "controller_mvp_v6", "run-domain-weave-controller-mvp-v6"}:
            controller_name = "domain_weave_controller_mvp_v6.py"
        elif route_alias in {"domain_weave_controller_mvp_v5", "controller_mvp_v5", "run-domain-weave-controller-mvp-v5"}:
            controller_name = "domain_weave_controller_mvp_v5.py"
        elif route_alias in {"domain_weave_controller_mvp_v4", "controller_mvp_v4", "run-domain-weave-controller-mvp-v4"}:
            controller_name = "domain_weave_controller_mvp_v4.py"
        elif route_alias in {"domain_weave_controller_mvp_v3", "controller_mvp_v3", "run-domain-weave-controller-mvp-v3"}:
            controller_name = "domain_weave_controller_mvp_v3.py"
        elif route_alias in {"domain_weave_controller_mvp_v2", "controller_mvp_v2", "run-domain-weave-controller-mvp-v2"}:
            controller_name = "domain_weave_controller_mvp_v2.py"
        else:
            controller_name = "domain_weave_controller_mvp.py"
        controller = root / f"dAimon/gemini_cli/scripts/{controller_name}"
        if not controller.exists():
            return {
                "ok": False,
                "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                "finding": "domain_weave_controller_mvp_missing",
                "runner_path": "dAimon/gemini_cli/scripts/domain_weave_controller_mvp.py",
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        target_root = str(args.get("target_root") or "dAimon/gemini_cli").strip()
        run_id = str(args.get("run_id") or "").strip()
        max_depth = str(args.get("max_depth") or 3)
        max_files = str(args.get("max_files") or 800)
        argv = [
            sys.executable,
            str(controller),
            "--dry-run",
            "--target-root",
            target_root,
            "--max-depth",
            max_depth,
            "--max-files",
            max_files,
            "--timeout",
            str(timeout),
        ]
        if run_id:
            argv.extend(["--run-id", run_id])
        action = args.get("action")
        if action:
            argv.extend(["--action", str(action)])
        touched = args.get("touched")
        if touched:
            touched_values = touched if isinstance(touched, list) else [touched]
            for touched_path in touched_values:
                argv.extend(["--touched", str(touched_path)])
        provider_ownership_overlay = args.get("provider_ownership_overlay")
        if provider_ownership_overlay:
            argv.extend(["--provider-ownership-overlay", str(provider_ownership_overlay)])
        provider_reflex_overlay = args.get("provider_reflex_overlay")
        if provider_reflex_overlay:
            argv.extend(["--provider-reflex-overlay", str(provider_reflex_overlay)])
        mutates_state = True
    elif route_alias in {"broker_enqueue", "enqueue"}:
        argv.append("enqueue")
        packet_id = str(args.get("packet_id") or "").strip()
        objective = str(args.get("objective") or "").strip()
        if not packet_id or not objective:
            return {
                "ok": False,
                "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
                "finding": "packet_id_and_objective_required",
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        argv.extend(["--packet-id", packet_id, "--objective", objective])
        if args.get("domain_id"):
            argv.extend(["--domain-id", str(args.get("domain_id"))])
        if args.get("agent_role_id"):
            argv.extend(["--agent-role-id", str(args.get("agent_role_id"))])
        for ref in args.get("context_refs") or []:
            argv.extend(["--context-ref", str(ref)])
        if bool(args.get("overwrite")):
            argv.append("--overwrite")
        mutates_state = True
    else:
        return {
            "ok": False,
            "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
            "finding": "unsupported_gemini_broker_route",
            "route_id": route_id,
            "broker_command": route_alias,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        }

    broker_env = dict(os.environ)
    broker_env.setdefault("ION_GEMINI_VAULT_ENV", str(root / "ION_VAULT_LOCAL/env/google_ai_studio.env"))
    completed = subprocess.run(
        argv,
        cwd=str(root),
        env=broker_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=max(timeout + 60, 120),
        check=False,
    )
    stdout = _redact_gemini_cli_broker_text(completed.stdout or "")
    stderr = _redact_gemini_cli_broker_text(completed.stderr or "")
    parsed_stdout: Any = None
    try:
        parsed_stdout = json.loads(stdout) if stdout.strip() else None
    except json.JSONDecodeError:
        parsed_stdout = None

    return {
        "ok": completed.returncode == 0,
        "schema_id": "ion.gemini_cli.branch_broker_result.v1_candidate",
        "broker_path": "dAimon/gemini_cli/scripts/gemini_cli_action_broker.py",
        "route_id": route_id,
        "broker_command": route_alias,
        "argv_shape": [Path(argv[0]).name, "dAimon/gemini_cli/scripts/gemini_cli_action_broker.py", *argv[2:]],
        "returncode": completed.returncode,
        "stdout_json": parsed_stdout,
        "stdout_tail": stdout[-4000:],
        "stderr_tail": stderr[-3000:],
        "mutates_state": mutates_state,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _invoke_browser_queue_local_status_route(
    root: Path,
    *,
    route_id: str,
    args: Mapping[str, Any],
) -> dict[str, Any]:
    """Read-only local browser queue/status proof surface."""
    runner = root / "ION/05_context/current/chatgpt_connector/scripts/browser_queue_local_status.py"
    if not runner.exists():
        return {
            "ok": False,
            "schema_id": "ion.browser_queue.local_status.branch_result.v1_candidate",
            "finding": "browser_queue_local_status_runner_missing",
            "runner_path": "ION/05_context/current/chatgpt_connector/scripts/browser_queue_local_status.py",
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        }
    argv = [sys.executable, str(runner)]
    query = args.get("query")
    request_path = args.get("request_path") or args.get("path")
    invocation_id = args.get("invocation_id")
    if isinstance(query, str) and query.strip():
        argv.extend(["--query", query.strip()])
    if isinstance(request_path, str) and request_path.strip():
        argv.extend(["--request-path", request_path.strip()])
    if isinstance(invocation_id, str) and invocation_id.strip():
        argv.extend(["--invocation-id", invocation_id.strip()])
    timeout = int(args.get("timeout") or 60)
    completed = subprocess.run(
        argv,
        cwd=str(root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=max(timeout, 30),
        check=False,
    )
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    parsed_stdout: Any = None
    try:
        parsed_stdout = json.loads(stdout) if stdout.strip() else None
    except json.JSONDecodeError:
        parsed_stdout = None
    return {
        "ok": completed.returncode == 0,
        "schema_id": "ion.browser_queue.local_status.branch_result.v1_candidate",
        "runner_path": "ION/05_context/current/chatgpt_connector/scripts/browser_queue_local_status.py",
        "route_id": route_id,
        "argv_shape": [Path(argv[0]).name, "ION/05_context/current/chatgpt_connector/scripts/browser_queue_local_status.py", "<bounded-read-only-args>"],
        "returncode": completed.returncode,
        "stdout_json": parsed_stdout,
        "stdout_tail": stdout[-5000:],
        "stderr_tail": stderr[-3000:],
        "mutates_state": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "browser_send_authority": False,
        "enqueue_authority": False,
    }


def _invoke_native_ide_control_route(
    root: Path,
    *,
    route_id: str,
    args: Mapping[str, Any],
) -> dict[str, Any]:
    """Invoke the Sev native IDE control lane through fixed command shapes only."""
    runner = root / "ION/05_context/current/chatgpt_connector/scripts/native_ide_control_lane_v7.py"
    if not runner.exists():
        return {
            "ok": False,
            "schema_id": "ion.native_ide.branch_result.v1_candidate",
            "finding": "native_ide_control_runner_missing",
            "runner_path": "ION/05_context/current/chatgpt_connector/scripts/native_ide_control_lane.py",
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        }

    route_alias = str(args.get("native_ide_command") or args.get("broker_command") or route_id)
    command_map = {
        "native_ide_sign_in": "sign-in",
        "sign_in": "sign-in",
        "session_sign_in": "sign-in",
        "native_ide_status": "dist-status",
        "status": "dist-status",
        "native_ide_legacy_status": "status",
        "legacy_status": "status",
        "native_ide_patch_dry_run": "patch-dist-overlay-dry-run",
        "patch_overlay_dry_run": "patch-dist-overlay-dry-run",
        "patch-dist-overlay-dry-run": "patch-dist-overlay-dry-run",
        "native_ide_patch_apply": "patch-dist-overlay-apply",
        "patch_overlay_apply": "patch-dist-overlay-apply",
        "patch-dist-overlay-apply": "patch-dist-overlay-apply",
        "native_ide_smoke_source": "smoke-dist-overlay",
        "smoke_overlay_source": "smoke-dist-overlay",
        "native_ide_extension_smoke": "smoke-dist-overlay",
        "run_extension_smoke": "smoke-dist-overlay",
        "smoke-dist-overlay": "smoke-dist-overlay",
        "native_ide_telemetry_dry_run": "patch-telemetry-dry-run",
        "patch_overlay_telemetry_dry_run": "patch-telemetry-dry-run",
        "native_ide_telemetry_apply": "patch-telemetry-apply",
        "patch_overlay_telemetry_apply": "patch-telemetry-apply",
        "native_ide_telemetry_smoke_source": "smoke-telemetry-source",
        "smoke_overlay_telemetry_source": "smoke-telemetry-source",
        "native_ide_latest_telemetry_receipt": "latest-telemetry-receipt",
        "latest_overlay_telemetry_receipt": "latest-telemetry-receipt",
        "native_ide_dist_overlay_dry_run": "patch-dist-overlay-dry-run",
        "patch_dist_overlay_dry_run": "patch-dist-overlay-dry-run",
        "native_ide_dist_overlay_apply": "patch-dist-overlay-apply",
        "patch_dist_overlay_apply": "patch-dist-overlay-apply",
        "native_ide_dist_overlay_smoke": "smoke-dist-overlay",
        "smoke_dist_overlay": "smoke-dist-overlay",
        "native_ide_dist_overlay_status": "dist-status",
        "dist_overlay_status": "dist-status",
        "native_ide_dist_status": "dist-status",
        "dist_status": "dist-status",
        "dist-status": "dist-status",
        "native_ide_overlay_queue_occlusion_dry_run": "patch-overlay-queue-occlusion-dry-run",
        "patch_overlay_queue_occlusion_dry_run": "patch-overlay-queue-occlusion-dry-run",
        "native_ide_overlay_queue_occlusion_apply": "patch-overlay-queue-occlusion-apply",
        "patch_overlay_queue_occlusion_apply": "patch-overlay-queue-occlusion-apply",
        "native_ide_overlay_queue_occlusion_smoke": "smoke-overlay-queue-occlusion",
        "smoke_overlay_queue_occlusion": "smoke-overlay-queue-occlusion",
        "native_ide_overlay_standard_click_fix_dry_run": "patch-overlay-standard-click-fix-dry-run",
        "patch_overlay_standard_click_fix_dry_run": "patch-overlay-standard-click-fix-dry-run",
        "native_ide_overlay_standard_click_fix_apply": "patch-overlay-standard-click-fix-apply",
        "patch_overlay_standard_click_fix_apply": "patch-overlay-standard-click-fix-apply",
        "native_ide_overlay_standard_click_fix_smoke": "smoke-overlay-standard-click-fix",
        "smoke_overlay_standard_click_fix": "smoke-overlay-standard-click-fix",
        "native_ide_operator_panel_dry_run": "patch-operator-panel-dry-run",
        "patch_operator_panel_dry_run": "patch-operator-panel-dry-run",
        "native_ide_operator_panel_apply": "patch-operator-panel-apply",
        "patch_operator_panel_apply": "patch-operator-panel-apply",
        "native_ide_operator_panel_smoke": "smoke-operator-panel",
        "smoke_operator_panel": "smoke-operator-panel",
    }
    subcommand = command_map.get(route_alias)
    if not subcommand:
        return {
            "ok": False,
            "schema_id": "ion.native_ide.branch_result.v1_candidate",
            "finding": "unsupported_native_ide_command",
            "route_id": route_id,
            "native_ide_command": route_alias,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        }
    if subcommand == "patch-overlay-apply" and args.get("confirmation") != "ION_BOUNDED_WRITE_CONFIRMED":
        return {
            "ok": False,
            "schema_id": "ion.native_ide.branch_result.v1_candidate",
            "finding": "native_ide_patch_apply_requires_confirmation",
            "required_confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        }

    timeout = int(args.get("timeout") or 90)
    argv = [sys.executable, str(runner), subcommand]
    completed = subprocess.run(
        argv,
        cwd=str(root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=max(timeout, 60),
        check=False,
    )
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    parsed_stdout: Any = None
    try:
        parsed_stdout = json.loads(stdout) if stdout.strip() else None
    except json.JSONDecodeError:
        parsed_stdout = None
    return {
        "ok": completed.returncode == 0,
        "schema_id": "ion.native_ide.branch_result.v1_candidate",
        "runner_path": "ION/05_context/current/chatgpt_connector/scripts/native_ide_control_lane.py",
        "route_id": route_id,
        "native_ide_command": route_alias,
        "argv_shape": [Path(argv[0]).name, "ION/05_context/current/chatgpt_connector/scripts/native_ide_control_lane.py", subcommand],
        "returncode": completed.returncode,
        "stdout_json": parsed_stdout,
        "stdout_tail": stdout[-4000:],
        "stderr_tail": stderr[-3000:],
        "mutates_state": subcommand not in {"status", "dist-status"},
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "arbitrary_shell_authority": False,
    }


def _invoke_latest_context_route(
    root: str | Path | None,
    *,
    route_id: str,
    args: Mapping[str, Any],
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    manifest_path, manifest = _latest_upload_manifest(shell_root)
    final_kit = _latest_final_operator_kit(shell_root)
    upload_set = final_kit or (manifest_path.parent if manifest_path else _latest_upload_set(shell_root))
    handoffs = _latest_handoff_files(shell_root, limit=5)
    latest_handoff_path = handoffs[0] if handoffs else None
    latest_handoff = _json_object(latest_handoff_path) if latest_handoff_path else None
    manifest_ref = _file_ref(shell_root, manifest_path, include_excerpt=False) if manifest_path else None
    upload_timestamp = (
        _final_operator_kit_timestamp(upload_set)
        or _upload_set_timestamp(upload_set)
        if upload_set
        else None
    )
    package_kind = "final_operator_upload_kit" if final_kit else "legacy_upload_set"
    base = _latest_context_base(shell_root, route_id, manifest=manifest)

    if route_id == "mount_status":
        first_zip = None
        if manifest:
            for entry in manifest.get("knowledge_entries") or manifest.get("upload_entries", []):
                if isinstance(entry, Mapping) and entry.get("kind") == "zip_context_package":
                    first_zip = dict(entry)
                    break
        markdown_count = None
        zip_count = None
        if manifest:
            entries = manifest.get("knowledge_entries") or manifest.get("upload_entries") or []
            if isinstance(entries, list):
                markdown_count = sum(1 for entry in entries if isinstance(entry, Mapping) and entry.get("kind") == "knowledge_markdown")
                zip_count = sum(1 for entry in entries if isinstance(entry, Mapping) and entry.get("kind") == "zip_context_package")
        base.update(
            {
                "local_package": {
                    "package_kind": package_kind,
                    "package_folder": _display_path(upload_set, shell_root) if upload_set else None,
                    "package_timestamp": upload_timestamp,
                    "manifest": manifest_ref,
                    "manifest_source_posture": manifest.get("source_posture") if manifest else None,
                    "main_instruction_chars": manifest.get("main_instruction_chars") if manifest else None,
                    "markdown_knowledge_file_count": (
                        manifest.get("markdown_knowledge_file_count") if manifest and manifest.get("markdown_knowledge_file_count") is not None else markdown_count
                    ),
                    "zip_context_package_count": (
                        manifest.get("zip_context_package_count") if manifest and manifest.get("zip_context_package_count") is not None else zip_count
                    ),
                    "knowledge_file_count": manifest.get("knowledge_file_count") if manifest else None,
                    "first_zip": first_zip,
                },
                "latest_available_handoff": {
                    "handoff_id": latest_handoff_path.stem if latest_handoff_path else None,
                    "path": _display_path(latest_handoff_path, shell_root) if latest_handoff_path else None,
                    "created_at": latest_handoff.get("created_at") if latest_handoff else None,
                    "operator_packet": latest_handoff.get("operator_packet") if latest_handoff else None,
                    "sha256": _sha256_file(latest_handoff_path) if latest_handoff_path else None,
                },
                "freshness_status": {
                    "local_package": "current_candidate" if manifest else "missing_or_unproven",
                    "installed_gpt_package": "unknown_without_fresh_gpt_or_operator_proof",
                    "branch_gateway": "not_action_mount_equivalent",
                },
            }
        )
        return base

    if route_id == "latest_handoff":
        mini_path = shell_root / "ION/05_context/current/codex_solo/MINI.md"
        status_path = shell_root / "ION/05_context/current/codex_solo/STATUS.json"
        status = _json_object(status_path) or {}
        base.update(
            {
                "active_objective": {
                    "source": "latest_handoff_and_codex_solo_status",
                    "latest_operator_packet": latest_handoff.get("operator_packet") if latest_handoff else None,
                    "mini_excerpt": _text_excerpt(mini_path, max_chars=900),
                    "status_capsule_ok": (status.get("capsule") or {}).get("ok") if isinstance(status.get("capsule"), Mapping) else None,
                },
                "last_available_handoff": _file_ref(shell_root, latest_handoff_path, include_excerpt=True, max_excerpt_chars=900) if latest_handoff_path else None,
                "last_available_handoff_summary": {
                    "created_at": latest_handoff.get("created_at") if latest_handoff else None,
                    "posture": latest_handoff.get("posture") if latest_handoff else None,
                    "summary": latest_handoff.get("summary") if latest_handoff else None,
                    "artifacts": latest_handoff.get("artifacts") if latest_handoff else None,
                    "non_claims": latest_handoff.get("non_claims") if latest_handoff else None,
                },
                "current_blockers": [
                    "Branch Gateway latest_context is not ACTION_MOUNT_EQUIVALENT.",
                    "GPT Builder installed package freshness remains unknown unless the fresh GPT reports its mounted manifest hash/timestamp.",
                ],
                "next_recommended_packet": "Fresh GPT smoke: local bootloader mount, then latest_context mount_status/latest_handoff/current_context_pack, then next_allowed_routes.",
                "receipt_refs": [_file_ref(shell_root, item) for item in _receipt_files(shell_root, limit=5)],
            }
        )
        return base

    if route_id == "current_context_pack":
        required_reads = [_file_ref(shell_root, item, include_excerpt=item.suffix in {".md", ".json"}, max_excerpt_chars=650) for item in _latest_context_required_reads(shell_root, upload_set)]
        missing = [item["path"] for item in required_reads if not item.get("exists")]
        base.update(
            {
                "required_reads": required_reads,
                "context_refs": {
                    "root_manifest": manifest_ref,
                    "latest_handoff": _file_ref(shell_root, latest_handoff_path) if latest_handoff_path else None,
                    "latest_receipts": [_file_ref(shell_root, item) for item in _receipt_files(shell_root, limit=6)],
                },
                "proof_obligations": list(LATEST_CONTEXT_PROOF_OBLIGATIONS),
                "route_templates": _route_templates(),
                "stale_or_missing_context_warnings": missing,
                "refusal_barrier": "If any required read needed for the objective is missing, respond LOCAL_SANDBOX_PARTIAL_MOUNT or UNMOUNTED_ROLEPLAY_BLOCKED instead of improvising.",
            }
        )
        return base

    if route_id == "recent_receipts":
        receipt_refs = []
        for item in _receipt_files(shell_root, limit=int(args.get("limit") or 10)):
            status = "accepted" if "context_settlement/accepted" in item.as_posix() else "candidate_or_evidence"
            receipt_ref = _file_ref(shell_root, item)
            receipt_ref["settlement_status"] = status
            receipt_refs.append(receipt_ref)
        base.update(
            {
                "latest_relevant_receipts": receipt_refs,
                "settlement_posture": "accepted only for refs explicitly under context_settlement/accepted; all other receipt refs are candidate/evidence until settled.",
                "receipt_count": len(receipt_refs),
            }
        )
        return base

    if route_id == "next_allowed_routes":
        read_routes = [
            {
                "branch_id": "latest_context",
                "route_id": item,
                "route_authority_class": "read-only",
                "required_approval_phrase": None,
                "allowed_now": True,
            }
            for item in sorted(LATEST_CONTEXT_ROUTE_IDS)
        ]
        planned_write_routes = [
            {
                "branch_id": "latest_context",
                "route_id": "record_handoff",
                "route_authority_class": "bounded write",
                "required_approval_phrase": CONFIRMATION_TOKEN,
                "idempotency_required": True,
                "implemented": False,
            },
            {
                "branch_id": "latest_context",
                "route_id": "settle_handoff",
                "route_authority_class": "accepted-state",
                "required_approval_phrase": CONFIRMATION_TOKEN,
                "idempotency_required": True,
                "implemented": False,
            },
        ]
        base.update(
            {
                "allowed_next_routes": read_routes,
                "planned_gated_routes_not_implemented_v0_1": planned_write_routes,
                "blockers_before_mutation_routes": [
                    "Define receipt schema and settlement authority lane for latest_context writes.",
                    "Require explicit confirmation, idempotency key, proof refs, and refusal on missing required context.",
                    "Do not claim accepted state unless settlement proof is present and route authority allows it.",
                ],
                "route_templates": _route_templates(),
            }
        )
        return base

    if route_id == "package_freshness":
        installed_timestamp = str(args.get("installed_package_timestamp") or "").strip() or None
        latest_timestamp = upload_timestamp
        installed_status = "unknown"
        if installed_timestamp and latest_timestamp:
            installed_status = "current" if installed_timestamp == latest_timestamp else "stale"
        base.update(
            {
                "current_gpt_upload_package_timestamp": installed_timestamp,
                "latest_rebuilt_package_timestamp": latest_timestamp,
                "installed_package_status": installed_status,
                "local_rebuilt_package": {
                    "package_kind": package_kind,
                    "package_folder": _display_path(upload_set, shell_root) if upload_set else None,
                    "manifest": manifest_ref,
                    "manifest_generated_at_utc": manifest.get("generated_at_utc") if manifest else None,
                    "source_posture": manifest.get("source_posture") if manifest else None,
                },
                "proof_needed_to_prove_freshness": [
                    "Fresh GPT reports mounted 00_ROOT_MANIFEST.json sha256 and generated_at_utc.",
                    "Operator compares reported manifest sha256 to local latest_context.package_freshness manifest sha256.",
                    "If hashes/timestamps differ, treat GPT package as stale until re-uploaded.",
                ],
                "proving_routes": [
                    "latest_context.mount_status",
                    "latest_context.package_freshness",
                    "latest_context.current_context_pack",
                ],
            }
        )
        return base

    return _blocked(
        "latestContextInvoke",
        "route_not_supported_by_latest_context_handler",
        refusal_class="BRANCH_ROUTE_NOT_FOUND",
        data={"route_id": route_id, "known_route_ids": sorted(LATEST_CONTEXT_ROUTE_IDS)},
    )


def _resolve_repo_path(root: str | Path | None, value: str | Path | None) -> tuple[Path | None, dict[str, Any] | None]:
    shell_root = _resolve_root(root)
    raw = str(value or "").strip()
    if not raw:
        return None, _blocked("resolveBranchPath", "path_required")
    candidate = Path(raw).expanduser()
    resolved = candidate.resolve(strict=False) if candidate.is_absolute() else (shell_root / candidate).resolve(strict=False)
    if not _is_relative_to(resolved, shell_root):
        return None, _blocked(
            "resolveBranchPath",
            "path_outside_repo_root",
            refusal_class="PATH_NOT_ALLOWED",
            data={"path": raw, "repo_root": shell_root.as_posix()},
        )
    return resolved, None


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "write"}


def _write_requested(args: Mapping[str, Any]) -> bool:
    return any(_truthy(args.get(key)) for key in ("write", "write_receipt", "write_candidate_capsule"))


def _yaml_subset_scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "":
        return ""
    if value == "{}":
        return {}
    if value == "[]":
        return []
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_yaml_subset_scalar(part.strip()) for part in inner.split(",")]
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def _yaml_subset_rows(text: str) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        rows.append((indent, line.strip()))
    return rows


def _yaml_subset_block(rows: list[tuple[int, str]], index: int, parent_indent: int, style: str) -> tuple[str, int]:
    parts: list[str] = []
    while index < len(rows):
        indent, stripped = rows[index]
        if indent <= parent_indent:
            break
        parts.append(stripped)
        index += 1
    return ("\n".join(parts) if style == "|" else " ".join(parts)).strip(), index


def _parse_yaml_subset_node(rows: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(rows):
        return {}, index
    is_list = rows[index][0] == indent and rows[index][1].startswith("- ")
    if is_list:
        items: list[Any] = []
        while index < len(rows):
            row_indent, stripped = rows[index]
            if row_indent < indent:
                break
            if row_indent != indent or not stripped.startswith("- "):
                break
            item_text = stripped[2:].strip()
            index += 1
            if not item_text:
                if index < len(rows) and rows[index][0] > row_indent:
                    item, index = _parse_yaml_subset_node(rows, index, rows[index][0])
                else:
                    item = None
                items.append(item)
                continue
            if ":" in item_text and not item_text.startswith(("'", '"')):
                key, raw_value = item_text.split(":", 1)
                item_dict: dict[str, Any] = {}
                key = key.strip()
                raw_value = raw_value.strip()
                if raw_value in {">", "|"}:
                    item_dict[key], index = _yaml_subset_block(rows, index, row_indent, raw_value)
                elif raw_value:
                    item_dict[key] = _yaml_subset_scalar(raw_value)
                elif index < len(rows) and rows[index][0] > row_indent:
                    item_dict[key], index = _parse_yaml_subset_node(rows, index, rows[index][0])
                else:
                    item_dict[key] = None
                if index < len(rows) and rows[index][0] > row_indent:
                    extra, index = _parse_yaml_subset_node(rows, index, rows[index][0])
                    if isinstance(extra, Mapping):
                        item_dict.update(dict(extra))
                items.append(item_dict)
            else:
                items.append(_yaml_subset_scalar(item_text))
        return items, index

    mapping: dict[str, Any] = {}
    while index < len(rows):
        row_indent, stripped = rows[index]
        if row_indent < indent:
            break
        if row_indent != indent:
            break
        if stripped.startswith("- "):
            break
        if ":" not in stripped:
            index += 1
            continue
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        index += 1
        if raw_value in {">", "|"}:
            mapping[key], index = _yaml_subset_block(rows, index, row_indent, raw_value)
        elif raw_value:
            mapping[key] = _yaml_subset_scalar(raw_value)
        elif index < len(rows) and rows[index][0] > row_indent:
            mapping[key], index = _parse_yaml_subset_node(rows, index, rows[index][0])
        else:
            mapping[key] = None
    return mapping, index


def _load_yaml_mapping(text: str) -> dict[str, Any]:
    if yaml is not None:
        loaded = yaml.safe_load(text)
    else:
        loaded, _ = _parse_yaml_subset_node(_yaml_subset_rows(text), 0, 0)
    if not isinstance(loaded, dict):
        raise ValueError("YAML registry must parse to an object")
    return loaded


def load_branch_leader_registry(root: str | Path | None = None) -> dict[str, Any]:
    """Load and validate the branch leader registry."""

    shell_root = _resolve_root(root)
    registry_path = shell_root / REGISTRY_RELATIVE_PATH
    if not registry_path.exists():
        raise FileNotFoundError(f"missing branch leader registry: {REGISTRY_RELATIVE_PATH.as_posix()}")
    loaded = _load_yaml_mapping(registry_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("branch leader registry must parse to an object")
    branches = loaded.get("branches")
    if not isinstance(branches, list):
        raise ValueError("branch leader registry requires branches list")

    seen_branches: set[str] = set()
    for branch in branches:
        if not isinstance(branch, Mapping):
            raise ValueError("branch entries must be objects")
        branch_id = str(branch.get("branch_id") or "").strip()
        if not branch_id:
            raise ValueError("branch entry missing branch_id")
        if branch_id in seen_branches:
            raise ValueError(f"duplicate branch_id: {branch_id}")
        seen_branches.add(branch_id)
        seen_routes: set[str] = set()
        for route in branch.get("routes") or []:
            if not isinstance(route, Mapping):
                raise ValueError(f"route entries must be objects in branch {branch_id}")
            route_id = str(route.get("route_id") or "").strip()
            if not route_id:
                raise ValueError(f"route entry missing route_id in branch {branch_id}")
            if route_id in seen_routes:
                raise ValueError(f"duplicate route_id: {branch_id}/{route_id}")
            seen_routes.add(route_id)
    return loaded


def _branch_index(registry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(branch.get("branch_id")): branch
        for branch in registry.get("branches", [])
        if isinstance(branch, Mapping) and branch.get("branch_id")
    }


def _route_index(branch: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(route.get("route_id")): route
        for route in branch.get("routes", [])
        if isinstance(route, Mapping) and route.get("route_id")
    }


def validate_branch_route(
    root: str | Path | None,
    branch_id: str,
    route_id: str | None = None,
) -> tuple[Mapping[str, Any] | None, Mapping[str, Any] | None, dict[str, Any] | None]:
    """Return branch/route or a blocked payload for unknown ids."""

    registry = load_branch_leader_registry(root)
    branch = _branch_index(registry).get(str(branch_id or "").strip())
    if not branch:
        return None, None, _blocked(
            "validate",
            "branch_not_found",
            refusal_class="BRANCH_ROUTE_NOT_FOUND",
            data={"branch_id": branch_id, "known_branch_ids": sorted(_branch_index(registry))},
        )
    if route_id is None:
        return branch, None, None
    route = _route_index(branch).get(str(route_id or "").strip())
    if not route:
        return branch, None, _blocked(
            "validate",
            "route_not_found",
            refusal_class="BRANCH_ROUTE_NOT_FOUND",
            data={"branch_id": branch_id, "route_id": route_id, "known_route_ids": sorted(_route_index(branch))},
        )
    return branch, route, None


def _resolve_invoke_target(
    root: str | Path | None,
    *,
    branch_id: str,
    route_id: str,
) -> tuple[str, str, dict[str, Any] | None]:
    """Resolve invoke target with a bounded worker-shift fallback.

    A legacy caller can accidentally route worker_shift read calls through the
    lazy branch_context lane. When a worker_shift read route id is requested via
    branch_context, resolve to worker_shift explicitly instead of falling into
    lazy branch route handlers.
    """

    requested_branch_id = str(branch_id or "").strip()
    requested_route_id = str(route_id or "").strip()
    if requested_branch_id != "branch_context" or requested_route_id not in WORKER_SHIFT_ROUTE_IDS:
        return requested_branch_id, requested_route_id, None

    registry = load_branch_leader_registry(root)
    worker_shift_branch = _branch_index(registry).get("worker_shift")
    if not worker_shift_branch:
        return requested_branch_id, requested_route_id, None
    if requested_route_id not in _route_index(worker_shift_branch):
        return requested_branch_id, requested_route_id, None

    return (
        "worker_shift",
        requested_route_id,
        {
            "resolver_fallback": "worker_shift_route_from_branch_context",
            "requested_branch_id": requested_branch_id,
            "resolved_branch_id": "worker_shift",
        },
    )


def _public_route(
    route: Mapping[str, Any],
    *,
    include_schema: bool = True,
    branch_invocable: bool = True,
) -> dict[str, Any]:
    owner_tool = route.get("mcp_tool") or ("ion_branch_leader_gateway" if route.get("local_handler") else None)
    payload = {
        "route_id": route.get("route_id"),
        "title": route.get("title"),
        "summary": route.get("summary"),
        "mutates_state": bool(route.get("mutates_state")),
        "conditional_write": bool(route.get("conditional_write")),
        "route_schema_version": route.get("route_schema_version") or "v0",
        "confirmation_required": route.get("confirmation_required") or False,
        "idempotency_required": bool(route.get("idempotency_required")),
        "approval_required": bool(route.get("approval_required")),
        "invocable": bool(branch_invocable) and route.get("invocable", True) is not False and bool(owner_tool),
        "owner_tool": owner_tool,
    }
    if include_schema and isinstance(route.get("args_schema"), Mapping):
        payload["args_schema"] = dict(route["args_schema"])
    if isinstance(route.get("default_args"), Mapping):
        payload["default_args"] = dict(route["default_args"])
    if isinstance(route.get("route_enforcement"), Mapping):
        payload["route_enforcement"] = dict(route["route_enforcement"])
    if isinstance(route.get("compact_response_guidance"), Mapping):
        payload["compact_response_guidance"] = dict(route["compact_response_guidance"])
    if isinstance(route.get("oversize_recovery"), Mapping):
        payload["oversize_recovery"] = dict(route["oversize_recovery"])
    if isinstance(route.get("proof_requirements"), list):
        payload["proof_requirements"] = list(route["proof_requirements"])
    if isinstance(route.get("write_intent_required_target_roots"), list):
        payload["write_intent_required_target_roots"] = [
            str(item)
            for item in route["write_intent_required_target_roots"]
            if str(item or "").strip()
        ]
    if isinstance(route.get("required_write_intent_target_paths"), list):
        payload["required_write_intent_target_paths"] = [
            str(item)
            for item in route["required_write_intent_target_paths"]
            if str(item or "").strip()
        ]
    lease_gate = _route_lease_gate(route)
    if lease_gate:
        payload["lease_gate"] = lease_gate
    lease_gate_public = _public_route_lease_gate_model(route)
    if lease_gate_public:
        payload["lease_gate_public"] = lease_gate_public
    derived_flags = {
        "edit_lease_required": _route_required_lease_mode(route) == "exclusive_write",
        "artifact_lease_required": _route_required_lease_mode(route) == "artifact",
        "agent_id_required": _route_agent_id_required(route),
        "lease_id_required": _route_lease_id_required(route),
        "write_intent_lease_required": bool(route.get("write_intent_lease_required")),
        "write_intent_lease_id_required": bool(route.get("write_intent_lease_id_required")),
    }
    for key in (
        "edit_lease_required",
        "artifact_lease_required",
        "agent_id_required",
        "lease_id_required",
        "write_intent_lease_required",
        "write_intent_lease_id_required",
    ):
        if key in route or derived_flags[key]:
            payload[key] = derived_flags[key]
    required_mutation_fields = _public_required_mutation_fields(route)
    if required_mutation_fields:
        payload["required_mutation_fields"] = required_mutation_fields
    if isinstance(route.get("high_stakes_call_shape_template"), Mapping):
        payload["high_stakes_call_shape_template"] = dict(route["high_stakes_call_shape_template"])
    return payload


def _lazy_branch_summary(root: str | Path | None, path: str | Path, *, depth: str | None = None) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    target, blocked = _resolve_repo_path(shell_root, path)
    if blocked:
        return {
            "ok": False,
            "blocker": blocked.get("finding"),
            "refusal_class": blocked.get("refusal_class"),
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
        }
    assert target is not None
    classification = classify_branch_context(target, root=shell_root)
    inspection = classification.get("inspection") if isinstance(classification.get("inspection"), Mapping) else {}
    parent_context = classification.get("parent_context") if isinstance(classification.get("parent_context"), Mapping) else {}
    blocker = None
    if classification.get("decision") in {"not_branch", "blocked"}:
        blocker = classification.get("next_action") or inspection.get("ignore_reason") or classification.get("classification")

    suggested_next_calls = [
        {
            "operation": "ionActionBranchInvoke",
            "branch_id": "branch_context",
            "route_id": "inherit_parent_context",
            "expected_route_schema_version": "v0",
            "args": {"path": classification.get("path"), "write": False},
        }
    ]
    if classification.get("candidate_available"):
        suggested_next_calls.append(
            {
                "operation": "ionActionBranchInvoke",
                "branch_id": "branch_context",
                "route_id": "materialize_candidate_context",
                "expected_route_schema_version": "v0",
                "args": {"path": classification.get("path"), "write": False},
                "write_requires": {
                    "write": True,
                    "confirmation": CONFIRMATION_TOKEN,
                    "idempotency_key": "required",
                },
            }
        )

    payload: dict[str, Any] = {
        "ok": True,
        "schema_id": "ion.branch_leader_lazy_context_summary.v0_1",
        "branch_id": str(classification.get("path") or "").replace("/", "_").strip("_") or "root",
        "branch_path": classification.get("path"),
        "maturity_level": classification.get("maturity_level"),
        "classification": classification.get("classification"),
        "decision": classification.get("decision"),
        "parent_context": parent_context,
        "local_context_files": inspection.get("local_context_files") or [],
        "local_files_inspected": inspection.get("local_files_inspected") or [],
        "candidate_available": bool(classification.get("candidate_available")),
        "suggested_next_calls": suggested_next_calls,
        "allowed_operations": [
            "describe_without_write",
            "inherit_parent_context",
            "materialize_candidate_context_with_explicit_confirmation",
        ],
        "receipts_path": BRANCH_CONTEXT_RECEIPTS_PATH,
        "blocker": blocker,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "candidate_state_only": True,
    }
    if (depth or "summary") in {"full", "candidate"} and classification.get("candidate_available"):
        payload["candidate_capsule"] = build_candidate_branch_capsule(
            target,
            classification.get("parent_context") if isinstance(classification.get("parent_context"), Mapping) else None,
            inspection,
            root=shell_root,
        )
    return payload


def action_branch_list(root: str | Path | None = None, *, limit: int = DEFAULT_BRANCH_LIST_LIMIT) -> dict[str, Any]:
    registry = load_branch_leader_registry(root)
    branches = []
    for branch in registry.get("branches", [])[: max(1, min(limit, DEFAULT_BRANCH_LIST_LIMIT))]:
        if not isinstance(branch, Mapping):
            continue
        routes = [route for route in branch.get("routes", []) if isinstance(route, Mapping)]
        branch_payload = {
            "branch_id": branch.get("branch_id"),
            "title": branch.get("title"),
            "family": branch.get("family"),
            "maturity": branch.get("maturity"),
            "path": branch.get("path"),
            "lazy_context_enabled": bool(branch.get("lazy_context_enabled")),
            "authority_summary": branch.get("authority_summary"),
            "route_count": len(routes),
            "read_route_count": sum(1 for route in routes if not route.get("mutates_state")),
            "mutation_route_count": sum(1 for route in routes if route.get("mutates_state")),
            "suggested_next_calls": branch.get("suggested_next_calls") or [],
        }
        if isinstance(branch.get("oversize_recovery"), Mapping):
            branch_payload["oversize_recovery"] = dict(branch["oversize_recovery"])
        if isinstance(branch.get("compact_response_guidance"), Mapping):
            branch_payload["compact_response_guidance"] = dict(branch["compact_response_guidance"])
        if "action_mount_equivalent" in branch:
            branch_payload["action_mount_equivalent"] = bool(branch.get("action_mount_equivalent"))
        branches.append(branch_payload)
    return _ok(
        "ionActionBranchList",
        {
            "registry_path": REGISTRY_RELATIVE_PATH.as_posix(),
            "registry_schema_id": registry.get("schema_id"),
            "registry_status": registry.get("status"),
            "branch_count": len(branches),
            "branches": branches,
        },
    )


def action_branch_describe(
    root: str | Path | None,
    *,
    branch_id: str | None = None,
    path: str | None = None,
    path_or_branch_id: str | None = None,
    depth: str | None = None,
    profile: str | None = None,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    registry = load_branch_leader_registry(shell_root)
    branches = _branch_index(registry)
    target = str(path_or_branch_id or branch_id or path or "").strip()
    branch = branches.get(str(branch_id or path_or_branch_id or "").strip())
    if not branch and not path and target in branches:
        branch = branches[target]
    if not branch and target:
        lazy = _lazy_branch_summary(shell_root, target, depth=depth)
        if not lazy.get("ok"):
            return _blocked(
                "ionActionBranchDescribe",
                str(lazy.get("blocker") or "branch_or_path_not_found"),
                refusal_class=str(lazy.get("refusal_class") or "BRANCH_ROUTE_NOT_FOUND"),
                data={"path_or_branch_id": target},
            )
        branch_context = branches.get("branch_context", {})
        return _ok(
            "ionActionBranchDescribe",
            {
                "branch": {
                    "branch_id": lazy.get("branch_id"),
                    "title": f"Lazy Branch Context: {lazy.get('branch_path')}",
                    "family": "branch_context_materialization",
                    "maturity": lazy.get("maturity_level"),
                    "authority_summary": "Candidate/local branch context description only; no writes from describe.",
                    "context_refs": lazy.get("local_context_files") or [],
                    "suggested_next_calls": lazy.get("suggested_next_calls") or [],
                    "profile": profile or "default",
                    "depth": depth or "summary",
                    "routes": [
                        _public_route(route, include_schema=True)
                        for route in _route_index(branch_context).values()
                    ],
                },
                "branch_context": lazy,
                "next_call_shape": {
                    "operation": "ionActionBranchInvoke",
                    "required": ["branch_id", "route_id", "expected_route_schema_version"],
                    "mutation_fields": ["idempotency_key", "confirmation", "approval"],
                },
            },
        )
    if not branch:
        return _blocked("ionActionBranchDescribe", "branch_id_or_path_required")

    include_schema = (depth or "summary") not in {"brief", "list"}
    branch_invocable = branch.get("invocable", True) is not False
    routes = [
        _public_route(route, include_schema=include_schema, branch_invocable=branch_invocable)
        for route in branch.get("routes", [])
        if isinstance(route, Mapping)
    ]
    branch_path = str(path or branch.get("path") or "").strip()
    lazy_context = _lazy_branch_summary(shell_root, branch_path, depth=depth) if branch_path else {
        "ok": False,
        "blocker": "no_branch_path_bound_in_registry",
        "candidate_available": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }
    branch_payload = {
        "branch_id": branch.get("branch_id"),
        "title": branch.get("title"),
        "family": branch.get("family"),
        "maturity": branch.get("maturity"),
        "path": branch.get("path"),
        "authority_summary": branch.get("authority_summary"),
        "context_refs": branch.get("context_refs") or [],
        "suggested_next_calls": branch.get("suggested_next_calls") or [],
        "invocable": branch_invocable,
        "profile": profile or "default",
        "depth": depth or "summary",
        "routes": routes,
    }
    if isinstance(branch.get("oversize_recovery"), Mapping):
        branch_payload["oversize_recovery"] = dict(branch["oversize_recovery"])
    if isinstance(branch.get("compact_response_guidance"), Mapping):
        branch_payload["compact_response_guidance"] = dict(branch["compact_response_guidance"])
    if "action_mount_equivalent" in branch:
        branch_payload["action_mount_equivalent"] = bool(branch.get("action_mount_equivalent"))
    return _ok(
        "ionActionBranchDescribe",
        {
            "branch": branch_payload,
            "branch_context": lazy_context,
            "next_call_shape": {
                "operation": "ionActionBranchInvoke",
                "required": ["branch_id", "route_id", "expected_route_schema_version"],
                "mutation_fields": ["idempotency_key", "confirmation", "approval"],
            },
        },
    )


def _validate_args_schema(route: Mapping[str, Any], args: Mapping[str, Any]) -> str | None:
    schema = route.get("args_schema") if isinstance(route.get("args_schema"), Mapping) else {}
    required = schema.get("required") if isinstance(schema, Mapping) else None
    if isinstance(required, list):
        for key in required:
            key_name = str(key)
            if key_name == "write_intent_lease_id" and _route_write_intent_lease_id(args):
                continue
            if key_name not in args or args.get(key_name) in (None, ""):
                return f"missing_required_arg:{key}"
    return None


def _merge_route_args(route: Mapping[str, Any], args: Mapping[str, Any] | None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    if isinstance(route.get("default_args"), Mapping):
        merged.update(dict(route["default_args"]))
    if args:
        merged.update(dict(args))
    return merged


def _enforce_route_mutation_envelope(
    *,
    branch_id: str,
    route_id: str,
    route: Mapping[str, Any],
    route_args: Mapping[str, Any],
    approval: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    route_write_invocation = bool(route.get("mutates_state")) or (
        bool(route.get("conditional_write")) and _write_requested(route_args)
    )
    if not route_write_invocation:
        return None

    base = {"branch_id": branch_id, "route_id": route_id}
    if route.get("idempotency_required") and not str(route_args.get("idempotency_key") or "").strip():
        return _blocked(
            "ionActionBranchInvoke",
            "idempotency_key_required",
            refusal_class="IDEMPOTENCY_KEY_REQUIRED",
            data=base,
        )
    required_confirmation = str(route.get("confirmation_required") or "")
    if required_confirmation and str(route_args.get("confirmation") or "") != required_confirmation:
        return _blocked(
            "ionActionBranchInvoke",
            "confirmation_required",
            refusal_class="CONFIRMATION_REQUIRED",
            data={**base, "required_confirmation": required_confirmation},
        )
    if route.get("approval_required") and not approval:
        return _blocked(
            "ionActionBranchInvoke",
            "approval_required",
            refusal_class="OPERATOR_APPROVAL_REQUIRED",
            data=base,
        )
    if _route_agent_id_required(route):
        agent_id = str(route_args.get("agent_id") or route_args.get("worker_id") or "").strip()
        if not agent_id:
            return _blocked(
                "ionActionBranchInvoke",
                "actor_proof_required",
                refusal_class="ACTOR_PROOF_REQUIRED",
                data={**base, "required_fields": ["agent_id"], "provided_agent_id": False},
            )
    required_mutation_fields = route.get("required_mutation_fields")
    if isinstance(required_mutation_fields, list):
        missing_fields: list[str] = []
        for field in required_mutation_fields:
            field_name = str(field or "").strip()
            if not field_name or field_name in {"idempotency_key", "confirmation"}:
                continue
            value = route_args.get(field_name)
            if field_name == "agent_id":
                value = route_args.get("agent_id") or route_args.get("worker_id")
            if field_name == "write_intent_lease_id":
                value = _route_write_intent_lease_id(route_args)
            if value in (None, "", []):
                missing_fields.append(field_name)
        if missing_fields:
            return _blocked(
                "ionActionBranchInvoke",
                "mutation_proof_required",
                refusal_class="MUTATION_PROOF_REQUIRED",
                data={**base, "required_fields": missing_fields},
            )
    return None


def _write_candidate_capsule(path: Path, payload: Mapping[str, Any]) -> Path:
    target_dir = path if path.is_dir() or not path.suffix else path.parent
    target = target_dir / "ION_CONTEXT_CAPSULE.candidate.yaml"
    if target.exists():
        raise FileExistsError(target.as_posix())
    target.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def _lease_path_overlap(left: str, right: str) -> bool:
    left_clean = str(left or "").replace("\\", "/").rstrip("/")
    right_clean = str(right or "").replace("\\", "/").rstrip("/")
    return (
        left_clean == right_clean
        or left_clean.startswith(f"{right_clean}/")
        or right_clean.startswith(f"{left_clean}/")
    )


def _carrier_overlap_risk(
    *,
    board: Mapping[str, Any],
    stale_worker_count: int,
) -> dict[str, Any]:
    active_shifts = [
        shift for shift in board.get("active_shifts", []) if isinstance(shift, Mapping)
    ]
    active_leases = [
        lease
        for lease in board.get("active_leases", [])
        if isinstance(lease, Mapping) and str(lease.get("status") or "ACTIVE") in {"ACTIVE", "CLAIMED"}
    ]
    carrier_counts: dict[str, int] = {}
    for shift in active_shifts:
        identity = shift.get("identity") if isinstance(shift.get("identity"), Mapping) else {}
        carrier_type = str(identity.get("carrier_type") or str(shift.get("worker_id") or "").split(":", 1)[0] or "unknown")
        carrier_counts[carrier_type] = carrier_counts.get(carrier_type, 0) + 1

    overlap_pairs: list[dict[str, Any]] = []
    for index, left in enumerate(active_leases):
        left_paths = [str(path) for path in left.get("paths", [])]
        for right in active_leases[index + 1 :]:
            if left.get("worker_id") == right.get("worker_id"):
                continue
            right_paths = [str(path) for path in right.get("paths", [])]
            overlaps = [
                {"left_path": left_path, "right_path": right_path}
                for left_path in left_paths
                for right_path in right_paths
                if _lease_path_overlap(left_path, right_path)
            ]
            if overlaps:
                overlap_pairs.append(
                    {
                        "left_lease_id": left.get("lease_id"),
                        "right_lease_id": right.get("lease_id"),
                        "left_worker_id": left.get("worker_id"),
                        "right_worker_id": right.get("worker_id"),
                        "overlaps": overlaps,
                    }
                )

    exclusive_write_count = sum(1 for lease in active_leases if str(lease.get("lease_type") or "") == "exclusive_write")
    risk_flags: list[str] = []
    if len(carrier_counts) > 1:
        risk_flags.append("multi_carrier_active")
    if overlap_pairs:
        risk_flags.append("overlapping_active_leases")
    if stale_worker_count > 0:
        risk_flags.append("stale_workers_present")
    if exclusive_write_count > 0:
        risk_flags.append("exclusive_write_leases_present")

    risk_level = "none"
    if overlap_pairs and exclusive_write_count > 0:
        risk_level = "high"
    elif overlap_pairs or len(carrier_counts) > 1 or stale_worker_count > 0:
        risk_level = "medium"
    elif len(active_shifts) > 1 or len(active_leases) > 0:
        risk_level = "low"

    return {
        "risk_level": risk_level,
        "risk_flags": risk_flags,
        "active_carriers": [
            {"carrier_type": carrier_type, "worker_count": count}
            for carrier_type, count in sorted(carrier_counts.items())
        ],
        "lease_overlap_pair_count": len(overlap_pairs),
        "lease_overlap_pairs": overlap_pairs,
        "exclusive_write_lease_count": exclusive_write_count,
    }


def _queue_coordination_state(root: Path, *, active_worker_count: int, stale_worker_count: int) -> dict[str, Any]:
    queue_path = root / "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json"
    if not queue_path.is_file():
        return {
            "queue_path": _repo_rel(queue_path, root),
            "queue_observed": False,
            "queue_status": "missing_queue_file",
            "active_worker_count": active_worker_count,
            "stale_worker_count": stale_worker_count,
            "pressure_hint": "unknown",
        }

    try:
        queue_payload = json.loads(queue_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "queue_path": _repo_rel(queue_path, root),
            "queue_observed": False,
            "queue_status": f"queue_parse_error:{exc.__class__.__name__}",
            "active_worker_count": active_worker_count,
            "stale_worker_count": stale_worker_count,
            "pressure_hint": "unknown",
        }
    if not isinstance(queue_payload, Mapping):
        return {
            "queue_path": _repo_rel(queue_path, root),
            "queue_observed": False,
            "queue_status": "queue_payload_not_mapping",
            "active_worker_count": active_worker_count,
            "stale_worker_count": stale_worker_count,
            "pressure_hint": "unknown",
        }

    requests = [item for item in queue_payload.get("requests", []) if isinstance(item, Mapping)]
    status_counts: dict[str, int] = {}
    for request in requests:
        status = str(request.get("status") or "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1
    request_count = int(queue_payload.get("request_count") or len(requests))
    queued_like = sum(count for status, count in status_counts.items() if status.startswith("QUEUED"))
    in_flight = sum(
        count
        for status, count in status_counts.items()
        if status.startswith("CLAIMED") or status.startswith("RUNNING") or status.startswith("PROCESSING")
    )

    if request_count > 0 and active_worker_count == 0:
        pressure_hint = "queue_backlog_without_active_workers"
    elif stale_worker_count > 0 and (queued_like > 0 or in_flight > 0):
        pressure_hint = "queue_work_with_stale_workers"
    elif queued_like > max(active_worker_count, 1):
        pressure_hint = "queue_backlog_above_active_workers"
    elif queued_like > 0 or in_flight > 0:
        pressure_hint = "queue_work_present"
    else:
        pressure_hint = "idle_or_balanced"

    return {
        "queue_path": _repo_rel(queue_path, root),
        "queue_observed": True,
        "queue_status": "ok",
        "request_count": request_count,
        "duplicate_group_count": int(queue_payload.get("duplicate_group_count") or 0),
        "status_counts": status_counts,
        "queued_like_count": queued_like,
        "in_flight_count": in_flight,
        "active_worker_count": active_worker_count,
        "stale_worker_count": stale_worker_count,
        "pressure_hint": pressure_hint,
    }


def _codex_queue_pid_running(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _codex_queue_active_worker_projection(root: Path) -> dict[str, Any]:
    state_path = root / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state: Mapping[str, Any] = {}
    if state_path.is_file():
        try:
            loaded = json.loads(state_path.read_text(encoding="utf-8"))
            if isinstance(loaded, Mapping):
                state = loaded
        except Exception:
            state = {}
    entries: list[Mapping[str, Any]] = []
    active_runs = state.get("active_runs")
    if isinstance(active_runs, Mapping):
        entries.extend([value for value in active_runs.values() if isinstance(value, Mapping)])
    elif isinstance(active_runs, list):
        entries.extend([value for value in active_runs if isinstance(value, Mapping)])
    active_run = state.get("active_run")
    if isinstance(active_run, Mapping):
        key = str(active_run.get("run_id") or active_run.get("run_packet_path") or active_run.get("request_path") or "")
        if key and not any(str(row.get("run_id") or row.get("run_packet_path") or row.get("request_path") or "") == key for row in entries):
            entries.append(active_run)
    workers: list[dict[str, Any]] = []
    for entry in entries:
        try:
            pid = int(entry.get("pid")) if entry.get("pid") else None
        except (TypeError, ValueError):
            pid = None
        if not _codex_queue_pid_running(pid):
            continue
        run_rel = str(entry.get("run_packet_path") or "").strip()
        run_status = None
        request_id = entry.get("request_id")
        if run_rel:
            run_path = root / run_rel
            if run_path.is_file():
                try:
                    run = json.loads(run_path.read_text(encoding="utf-8"))
                    if isinstance(run, Mapping):
                        run_status = run.get("status")
                        request_id = request_id or run.get("request_id")
                except Exception:
                    run_status = None
        run_id = str(entry.get("run_id") or run_rel or entry.get("request_path") or "codex_queue_worker")
        workers.append(
            {
                "worker_id": f"codex_queue:{run_id}",
                "display_callsign": f"Codex Queue / {entry.get('lane_id') or 'unknown_lane'}",
                "status": run_status or "CODEX_QUEUE_ACTIVE",
                "source": "codex_queue_runner_state",
                "run_id": entry.get("run_id"),
                "pid": pid,
                "run_packet_path": run_rel or None,
                "request_path": entry.get("request_path"),
                "request_id": request_id,
                "lane_id": entry.get("lane_id"),
                "last_heartbeat_at": entry.get("started_at"),
            }
        )
    return {
        "schema_id": "ion.worker_shift_codex_queue_active_worker_projection.v0_1",
        "state_path": _repo_rel(state_path, root),
        "active_worker_count": len(workers),
        "workers": workers,
        "mutates_active_state": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _reconciled_worker_shift_summary(summary: Mapping[str, Any], codex_projection: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(summary)
    board_workers = [worker for worker in result.get("workers", []) if isinstance(worker, Mapping)]
    codex_workers = [worker for worker in codex_projection.get("workers", []) if isinstance(worker, Mapping)]
    board_count = int(result.get("active_worker_count") or len(board_workers))
    result["board_active_worker_count"] = board_count
    result["codex_queue_active_worker_count"] = int(codex_projection.get("active_worker_count") or len(codex_workers))
    result["active_worker_count"] = board_count + result["codex_queue_active_worker_count"]
    result["workers"] = [*board_workers, *codex_workers]
    active_by_status = dict(result.get("active_by_status") if isinstance(result.get("active_by_status"), Mapping) else {})
    if codex_workers:
        active_by_status["CODEX_QUEUE_ACTIVE"] = active_by_status.get("CODEX_QUEUE_ACTIVE", 0) + len(codex_workers)
    result["active_by_status"] = active_by_status
    result["reconciliation_source"] = "worker_shift_board_plus_codex_queue_runner_state"
    result["mutates_active_state"] = False
    return result


def _invoke_worker_shift_route(
    root: str | Path | None,
    *,
    route_id: str,
    args: Mapping[str, Any],
) -> dict[str, Any]:
    from .ion_worker_shift_presence import (
        classify_stale_workers,
        heartbeat_edit_lease,
        load_shift_board,
        release_edit_lease,
        request_edit_lease,
        request_handoff,
        request_operator_override,
        summarize_shift_board,
    )
    from .ion_codex_queue_runner import build_codex_parallel_plan_preview

    shell_root = _resolve_root(root)
    if route_id == "request_edit_lease":
        return _ok("workerShiftRequestEditLease", request_edit_lease(shell_root, args), mutates_active_state=True)
    if route_id == "heartbeat_edit_lease":
        return _ok("workerShiftHeartbeatEditLease", heartbeat_edit_lease(shell_root, args), mutates_active_state=True)
    if route_id == "release_edit_lease":
        return _ok("workerShiftReleaseEditLease", release_edit_lease(shell_root, args), mutates_active_state=True)
    if route_id == "request_handoff":
        return _ok("workerShiftRequestHandoff", request_handoff(shell_root, args), mutates_active_state=True)
    if route_id == "request_operator_override":
        return _ok("workerShiftRequestOperatorOverride", request_operator_override(shell_root, args), mutates_active_state=True)
    if route_id == "parallel_plan_preview":
        preview = build_codex_parallel_plan_preview(shell_root, args)
        return _ok("workerShiftParallelPlanPreview", {**preview, "worker_shift_route": True})

    stale_after = max(1, int(args.get("stale_after_minutes") or 45))
    expired_after = max(stale_after + 1, int(args.get("expired_after_minutes") or 120))
    board = load_shift_board(shell_root)
    stale = classify_stale_workers(
        root=shell_root,
        board=board,
        stale_after_minutes=stale_after,
        expired_after_minutes=expired_after,
        write=False,
    )
    board_summary = summarize_shift_board(root=shell_root, board=board)
    codex_queue_reconciliation = _codex_queue_active_worker_projection(shell_root)
    summary = _reconciled_worker_shift_summary(board_summary, codex_queue_reconciliation)
    overlap_risk = _carrier_overlap_risk(board=board, stale_worker_count=len(stale.get("stale_workers", [])))
    queue_state = _queue_coordination_state(
        shell_root,
        active_worker_count=int(summary.get("active_worker_count") or 0),
        stale_worker_count=int(summary.get("stale_worker_count") or 0),
    )

    if route_id == "status_summary":
        return _ok(
            "workerShiftStatusSummary",
            {
                "worker_shift_summary": summary,
                "stale_classification": stale,
                "carrier_overlap_risk": overlap_risk,
                "queue_coordination_state": queue_state,
                "codex_queue_reconciliation": codex_queue_reconciliation,
                "mutates_active_state": False,
            },
        )
    if route_id == "active_workers":
        return _ok(
            "workerShiftActiveWorkers",
            {
                "workers": summary.get("workers", []),
                "active_worker_count": summary.get("active_worker_count", 0),
                "mutates_active_state": False,
            },
        )
    if route_id == "stale_workers":
        return _ok(
            "workerShiftStaleWorkers",
            {
                "stale_workers": stale.get("stale_workers", []),
                "stale_worker_count": len(stale.get("stale_workers", [])),
                "stale_after_minutes": stale_after,
                "expired_after_minutes": expired_after,
                "mutates_active_state": False,
            },
        )
    if route_id == "active_leases":
        return _ok(
            "workerShiftActiveLeases",
            {
                "active_leases": summary.get("active_leases", []),
                "active_lease_count": summary.get("active_lease_count", 0),
                "carrier_overlap_risk": overlap_risk,
                "mutates_active_state": False,
            },
        )
    if route_id == "coordination_state":
        return _ok(
            "workerShiftCoordinationState",
            {
                "worker_shift_summary": summary,
                "queue_coordination_state": queue_state,
                "carrier_overlap_risk": overlap_risk,
                "codex_queue_reconciliation": codex_queue_reconciliation,
                "mutates_active_state": False,
            },
        )

    return _blocked(
        "workerShiftInvoke",
        "route_not_supported_by_worker_shift_handler",
        refusal_class="BRANCH_ROUTE_NOT_FOUND",
        data={"route_id": route_id},
    )



DESKTOP_RESCUE_EXCLUDE_PATTERNS = [
    "ion_custom_gpt_action_gateway",
    "ion-action-gateway",
    "cloudflared",
    "systemd",
    "dbus-daemon",
    "ssh",
]
DESKTOP_RESCUE_GROUP_PATTERNS = {
    "codex_gemini": ["codex", "gemini"],
    "browser_webgpu": ["chrome", "chromium", "brave", "electron", "webgpu"],
    "terminal_agents": ["codex", "gemini", "node", "npm"],
    "gnome_shell": ["gnome-shell"],
}


def _desktop_rescue_ps_rows(limit: int = 80) -> list[dict[str, Any]]:
    argv = ["ps", "-eo", "pid=,ppid=,stat=,pcpu=,pmem=,comm=,args=", "--sort=-pcpu"]
    completed = subprocess.run(argv, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=False)
    rows: list[dict[str, Any]] = []
    if completed.returncode != 0:
        return rows
    for raw in (completed.stdout or "").splitlines()[: max(1, limit)]:
        parts = raw.strip().split(None, 6)
        if len(parts) < 7:
            continue
        pid_s, ppid_s, stat, pcpu_s, pmem_s, comm, args = parts
        try:
            pid = int(pid_s)
            ppid = int(ppid_s)
            pcpu = float(pcpu_s)
            pmem = float(pmem_s)
        except ValueError:
            continue
        rows.append({"pid": pid, "ppid": ppid, "stat": stat, "pcpu": pcpu, "pmem": pmem, "comm": comm, "args": args[:500]})
    return rows


def _desktop_rescue_candidate_rows(rows: list[Mapping[str, Any]], target_group: str) -> list[dict[str, Any]]:
    patterns = DESKTOP_RESCUE_GROUP_PATTERNS.get(target_group, DESKTOP_RESCUE_GROUP_PATTERNS["codex_gemini"])
    candidates: list[dict[str, Any]] = []
    own_pid = os.getpid()
    for row in rows:
        text = f"{row.get('comm') or ''} {row.get('args') or ''}".lower()
        if int(row.get("pid") or 0) in {0, 1, own_pid}:
            continue
        if any(exclude.lower() in text for exclude in DESKTOP_RESCUE_EXCLUDE_PATTERNS):
            continue
        if not any(pattern.lower() in text for pattern in patterns):
            continue
        candidates.append(dict(row))
    return candidates


def _desktop_rescue_write_receipt(root: Path, name: str, payload: Mapping[str, Any]) -> str:
    receipt_dir = root / "ION/05_context/current/desktop_rescue/receipts"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    path = receipt_dir / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{name}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return _repo_rel(path, root)


def _invoke_desktop_rescue_route(
    root: str | Path | None,
    *,
    route_id: str,
    args: Mapping[str, Any],
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    limit = max(10, min(300, int(args.get("limit") or 80)))
    target_group = str(args.get("target_group") or "codex_gemini")
    rows = _desktop_rescue_ps_rows(limit=limit)
    candidates = _desktop_rescue_candidate_rows(rows, target_group)
    base = {
        "schema_id": "ion.desktop_rescue.branch_result.v1_candidate",
        "generated_at": _now(),
        "target_group": target_group,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
        "secrets_authority": False,
        "active_repo_write_authority": False,
    }
    if route_id == "status":
        high_cpu = [row for row in rows if float(row.get("pcpu") or 0.0) >= float(args.get("cpu_threshold") or 25.0)]
        return _ok(
            "desktopRescueStatus",
            {
                **base,
                "ok": True,
                "process_count_sampled": len(rows),
                "candidate_count": len(candidates),
                "candidates": candidates[:50],
                "high_cpu_rows": high_cpu[:30],
                "actions_taken": [],
                "safe_next_routes": ["desktop_rescue.kill_preview", "desktop_rescue.kill_apply"],
                "mutates_active_state": False,
            },
        )
    if route_id == "kill_preview":
        return _ok(
            "desktopRescueKillPreview",
            {
                **base,
                "ok": True,
                "would_signal": "TERM",
                "would_kill_count": len(candidates),
                "candidates": candidates[:50],
                "mutates_active_state": False,
                "warning": "Preview only. kill_apply requires confirmation and idempotency.",
            },
        )
    if route_id == "kill_apply":
        max_kill = max(1, min(50, int(args.get("max_kill_count") or 20)))
        selected = candidates[:max_kill]
        actions: list[dict[str, Any]] = []
        for row in selected:
            pid = int(row.get("pid") or 0)
            try:
                os.kill(pid, 15)
                actions.append({"pid": pid, "signal": "TERM", "ok": True, "comm": row.get("comm"), "args": row.get("args")})
            except ProcessLookupError:
                actions.append({"pid": pid, "signal": "TERM", "ok": True, "finding": "already_exited", "comm": row.get("comm")})
            except PermissionError as exc:
                actions.append({"pid": pid, "signal": "TERM", "ok": False, "finding": "permission_denied", "error": str(exc), "comm": row.get("comm")})
            except OSError as exc:
                actions.append({"pid": pid, "signal": "TERM", "ok": False, "finding": "os_error", "error": str(exc), "comm": row.get("comm")})
        payload = {
            **base,
            "ok": all(bool(action.get("ok")) for action in actions) if actions else True,
            "actions_taken": actions,
            "killed_count": sum(1 for action in actions if action.get("ok")),
            "candidate_count_before": len(candidates),
            "mutates_active_state": True,
            "non_claims": [
                "This route only targeted user-space process names in the selected target group.",
                "This route did not kill ion-action-gateway, cloudflared, systemd, or display manager processes by design.",
                "This route did not reboot, push git, access secrets, or accept state.",
            ],
        }
        payload["receipt_path"] = _desktop_rescue_write_receipt(shell_root, "kill_apply", payload)
        return _ok("desktopRescueKillApply", payload)
    return _blocked(
        "desktopRescueInvoke",
        "route_not_supported_by_desktop_rescue_handler",
        refusal_class="BRANCH_ROUTE_NOT_FOUND",
        data={"route_id": route_id},
    )


def _invoke_lazy_branch_route(
    root: str | Path | None,
    *,
    route_id: str,
    args: Mapping[str, Any],
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    target, blocked = _resolve_repo_path(shell_root, args.get("path") or args.get("branch_path"))
    if blocked:
        return blocked
    assert target is not None
    write = _write_requested(args)
    classification = classify_branch_context(target, root=shell_root, materialize=write)

    if route_id == "describe_path":
        return _ok(
            "lazyBranchDescribePath",
            {
                "branch_context": _lazy_branch_summary(shell_root, target, depth=str(args.get("depth") or "summary")),
                "mutates_active_state": False,
            },
        )

    if route_id == "inherit_parent_context":
        receipt = build_materialization_receipt(
            target,
            classification=classification,
            decision=str(classification.get("decision") or "inherited"),
            next_carrier_instructions=[
                "Use parent context for this branch until real work requires candidate local context."
            ],
            root=shell_root,
        )
        written = write_materialization_receipt(receipt, root=shell_root, write=write)
        return _ok(
            "lazyBranchInheritParentContext",
            {
                "branch_context": _lazy_branch_summary(shell_root, target),
                "materialization_receipt": written,
                "mutates_active_state": bool(written.get("wrote")),
            },
        )

    if route_id == "materialize_candidate_context":
        if not classification.get("candidate_available"):
            return _blocked(
                "lazyBranchMaterializeCandidateContext",
                "candidate_context_not_available",
                refusal_class="BRANCH_CONTEXT_NOT_MATERIALIZABLE",
                data={
                    "branch_path": classification.get("path"),
                    "classification": classification.get("classification"),
                    "decision": classification.get("decision"),
                    "blocker": classification.get("next_action"),
                },
            )
        candidate = build_candidate_branch_capsule(
            target,
            classification.get("parent_context") if isinstance(classification.get("parent_context"), Mapping) else None,
            classification.get("inspection") if isinstance(classification.get("inspection"), Mapping) else None,
            root=shell_root,
        )
        if not write:
            return _ok(
                "lazyBranchMaterializeCandidateContext",
                {
                    "branch_context": _lazy_branch_summary(shell_root, target, depth="candidate"),
                    "candidate_capsule": candidate,
                    "wrote_candidate_capsule": False,
                    "mutates_active_state": False,
                },
            )
        try:
            candidate_path = _write_candidate_capsule(target, candidate)
        except FileExistsError as exc:
            return _blocked(
                "lazyBranchMaterializeCandidateContext",
                "candidate_capsule_already_exists",
                refusal_class="BRANCH_CONTEXT_NOT_MATERIALIZABLE",
                data={"path": exc.args[0]},
            )
        receipt = build_materialization_receipt(
            target,
            classification=classification,
            decision="created",
            touched_paths=[candidate_path],
            created_files=[candidate_path],
            next_carrier_instructions=[
                "Treat ION_CONTEXT_CAPSULE.candidate.yaml as candidate-only until reviewed or accepted."
            ],
            root=shell_root,
        )
        written = write_materialization_receipt(receipt, root=shell_root, write=True)
        return _ok(
            "lazyBranchMaterializeCandidateContext",
            {
                "branch_context": _lazy_branch_summary(shell_root, target, depth="candidate"),
                "candidate_capsule_path": _repo_rel(candidate_path, shell_root),
                "materialization_receipt": written,
                "wrote_candidate_capsule": True,
                "mutates_active_state": True,
            },
        )

    return _blocked(
        "lazyBranchInvoke",
        "route_not_supported_by_lazy_branch_handler",
        refusal_class="BRANCH_ROUTE_NOT_FOUND",
        data={"route_id": route_id},
    )


def action_branch_invoke(
    root: str | Path | None,
    *,
    branch_id: str,
    route_id: str,
    args: Mapping[str, Any] | None = None,
    idempotency_key: str | None = None,
    confirmation: str | None = None,
    approval: Mapping[str, Any] | None = None,
    expected_route_schema_version: str | None = None,
) -> dict[str, Any]:
    resolved_branch_id, resolved_route_id, resolution = _resolve_invoke_target(
        root,
        branch_id=branch_id,
        route_id=route_id,
    )
    branch, route, blocked = validate_branch_route(root, resolved_branch_id, resolved_route_id)
    if blocked:
        return blocked
    assert branch is not None and route is not None

    if branch.get("invocable", True) is False:
        return _blocked(
            "ionActionBranchInvoke",
            "branch_not_invocable_in_current_operating_model",
            refusal_class="BRANCH_NOT_INVOCABLE",
            data={"branch_id": resolved_branch_id, "route_id": resolved_route_id},
        )
    expected = str(expected_route_schema_version or "").strip()
    actual_version = str(route.get("route_schema_version") or "v0")
    if expected and expected != actual_version:
        return _blocked(
            "ionActionBranchInvoke",
            "route_schema_version_mismatch",
            data={"branch_id": resolved_branch_id, "route_id": resolved_route_id, "expected": expected, "actual": actual_version},
        )

    route_args = _merge_route_args(route, args)
    if idempotency_key:
        route_args.setdefault("idempotency_key", idempotency_key)
    if confirmation:
        route_args.setdefault("confirmation", confirmation)

    if route.get("invocable", True) is False or not (route.get("mcp_tool") or route.get("local_handler")):
        envelope_blocked = _enforce_route_mutation_envelope(
            branch_id=resolved_branch_id,
            route_id=resolved_route_id,
            route=route,
            route_args=route_args,
            approval=approval,
        )
        if envelope_blocked:
            return envelope_blocked
        return _blocked(
            "ionActionBranchInvoke",
            "route_not_invocable_in_v0",
            refusal_class="ROUTE_NOT_INVOCABLE",
            data={"branch_id": resolved_branch_id, "route_id": resolved_route_id},
        )

    route_write_invocation = bool(route.get("mutates_state")) or (
        bool(route.get("conditional_write")) and _write_requested(route_args)
    )
    route_preserves_delegated_read_blocker = (
        not route_write_invocation
        and resolved_branch_id == "project_workbench"
        and resolved_route_id in {"file_read", "file_slice_read"}
    )
    route_fail_closes_delegated_blocker = not route_preserves_delegated_read_blocker
    envelope_blocked = _enforce_route_mutation_envelope(
        branch_id=resolved_branch_id,
        route_id=resolved_route_id,
        route=route,
        route_args=route_args,
        approval=approval,
    )
    if envelope_blocked:
        return envelope_blocked

    arg_finding = _validate_args_schema(route, route_args)
    if arg_finding:
        return _blocked(
            "ionActionBranchInvoke",
            arg_finding,
            data={"branch_id": resolved_branch_id, "route_id": resolved_route_id},
        )

    lease_blocked = _enforce_route_lease_gate(
        shell_root=_resolve_root(root),
        branch_id=resolved_branch_id,
        route_id=resolved_route_id,
        route=route,
        route_args=route_args,
    )
    if lease_blocked:
        return lease_blocked

    write_intent_lease_blocked = _enforce_route_write_intent_lease_gate(
        shell_root=_resolve_root(root),
        branch_id=resolved_branch_id,
        route_id=resolved_route_id,
        route=route,
        route_args=route_args,
    )
    if write_intent_lease_blocked:
        return write_intent_lease_blocked
    route_lease_gate_public = _public_route_lease_gate_model(route)
    dynamic_lease_gate_deferred = _handler_dynamic_target_gate_deferred_metadata(
        branch_id=resolved_branch_id,
        route_id=resolved_route_id,
        route=route,
        route_args=route_args,
    )

    if route.get("local_handler"):
        local_handler = str(route.get("local_handler") or "")
        if local_handler == "lazy_branch_context":
            delegated = _invoke_lazy_branch_route(root, route_id=resolved_route_id, args=route_args)
        elif local_handler == "worker_shift_presence":
            delegated = _invoke_worker_shift_route(root, route_id=resolved_route_id, args=route_args)
        elif local_handler == "runtime_services":
            from .ion_runtime_service_control import invoke_runtime_service_route

            delegated = invoke_runtime_service_route(root, route_id=resolved_route_id, args=route_args)
        elif local_handler == "latest_context":
            delegated = _invoke_latest_context_route(root, route_id=resolved_route_id, args=route_args)
        elif local_handler == "gemini_cli_broker":
            delegated = _invoke_gemini_cli_broker_route(root, route_id=resolved_route_id, args=route_args)
        elif local_handler == "native_ide_control":
            delegated = _invoke_native_ide_control_route(root, route_id=resolved_route_id, args=route_args)
        elif local_handler == "browser_queue_local_status":
            delegated = _invoke_browser_queue_local_status_route(root, route_id=resolved_route_id, args=route_args)
        elif local_handler == "chatgpt_browser_operating_card":
            from .ion_chatgpt_browser_operating_card import build_operating_card

            delegated = build_operating_card(root, route_args)
        elif local_handler == "codex_live_session_bridge":
            from .ion_codex_live_session_bridge import invoke_codex_live_session_bridge_route

            delegated = invoke_codex_live_session_bridge_route(root, route_id=resolved_route_id, args=route_args)
        elif local_handler == "codex_session_store":
            from .ion_codex_session_store_bridge import invoke_codex_session_store_route

            delegated = invoke_codex_session_store_route(root, route_id=resolved_route_id, args=route_args)
        elif local_handler == "codex_app_server":
            from .ion_codex_app_server_bridge import invoke_codex_app_server_route

            delegated = invoke_codex_app_server_route(root, route_id=resolved_route_id, args=route_args)
        elif local_handler == "agent_observatory":
            from .ion_agent_observatory import invoke_agent_observatory_route

            delegated = invoke_agent_observatory_route(root, route_id=resolved_route_id, args=route_args)
        elif local_handler == "multi_root_workspace":
            from .ion_multi_root_workspace import invoke_multi_root_workspace_route

            delegated = invoke_multi_root_workspace_route(root, route_id=resolved_route_id, args=route_args)
        elif local_handler == "desktop_rescue":
            delegated = _invoke_desktop_rescue_route(root, route_id=resolved_route_id, args=route_args)
        else:
            return _blocked(
                "ionActionBranchInvoke",
                "unsupported_local_handler",
                refusal_class="BRANCH_ROUTE_NOT_FOUND",
                data={"branch_id": resolved_branch_id, "route_id": resolved_route_id, "local_handler": local_handler},
            )
        payload = {
            "branch_id": resolved_branch_id,
            "branch_title": branch.get("title"),
            "route_id": resolved_route_id,
            "route_title": route.get("title"),
            "route_schema_version": actual_version,
            "owner_tool": "ion_branch_leader_gateway",
            "delegated_result": delegated,
            "mutates_active_state": bool(delegated.get("mutates_active_state"))
            or bool(delegated.get("mutates_state"))
            or bool(
                isinstance(delegated.get("materialization_receipt"), Mapping)
                and delegated["materialization_receipt"].get("wrote")
            ),
        }
        if route_lease_gate_public:
            payload["lease_gate_public"] = route_lease_gate_public
        if dynamic_lease_gate_deferred:
            payload.update(dynamic_lease_gate_deferred)
        if resolution:
            payload["resolver"] = dict(resolution)
        if delegated.get("ok") is False and route_fail_closes_delegated_blocker:
            delegated_public = {
                key: value
                for key, value in delegated.items()
                if key
                not in {
                    "schema_id",
                    "operation",
                    "ok",
                    "finding",
                    "refusal_class",
                    "production_authority",
                    "live_execution_authority",
                }
            }
            payload.update(delegated_public)
            return _blocked(
                "ionActionBranchInvoke",
                str(delegated.get("finding") or "delegated_route_blocked"),
                refusal_class=str(delegated.get("refusal_class") or "DELEGATED_ROUTE_BLOCKED"),
                data=payload,
            )
        return _ok(
            "ionActionBranchInvoke",
            payload,
        )

    from .ion_chatgpt_browser_mcp_connector_contract import call_chatgpt_connector_tool

    owner_tool = str(route["mcp_tool"])
    delegated = call_chatgpt_connector_tool(root, owner_tool, route_args)
    payload = {
        "branch_id": resolved_branch_id,
        "branch_title": branch.get("title"),
        "route_id": resolved_route_id,
        "route_title": route.get("title"),
        "route_schema_version": actual_version,
        "owner_tool": owner_tool,
        "delegated_result": delegated,
        "mutates_active_state": bool(delegated.get("mutates_active_state")) if isinstance(delegated, Mapping) else bool(route.get("mutates_state")),
    }
    if route_lease_gate_public:
        payload["lease_gate_public"] = route_lease_gate_public
    if dynamic_lease_gate_deferred:
        payload.update(dynamic_lease_gate_deferred)
    if resolution:
        payload["resolver"] = dict(resolution)
    if isinstance(delegated, Mapping) and delegated.get("ok") is False and route_fail_closes_delegated_blocker:
        delegated_public = {
            key: value
            for key, value in delegated.items()
            if key
            not in {
                "schema_id",
                "operation",
                "ok",
                "finding",
                "refusal_class",
                "production_authority",
                "live_execution_authority",
            }
        }
        payload.update(delegated_public)
        return _blocked(
            "ionActionBranchInvoke",
            str(delegated.get("finding") or "delegated_mcp_tool_blocked"),
            refusal_class=str(delegated.get("refusal_class") or "DELEGATED_MCP_TOOL_BLOCKED"),
            data=payload,
        )
    return _ok(
        "ionActionBranchInvoke",
        payload,
    )


def action_branch_receipts(
    root: str | Path | None,
    *,
    branch_id: str,
    route_id: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    branch, route, blocked = validate_branch_route(root, branch_id, route_id)
    if blocked:
        return blocked
    query_parts = [branch_id]
    if route_id:
        query_parts.append(route_id)
    query = " ".join(query_parts)
    from .ion_chatgpt_browser_mcp_connector_contract import call_chatgpt_connector_tool

    delegated = call_chatgpt_connector_tool(root, "ion_receipt_search", {"query": query, "limit": max(1, min(int(limit), 50))})
    return _ok(
        "ionActionBranchReceipts",
        {
            "branch_id": branch_id,
            "route_id": route_id,
            "route_title": route.get("title") if route else None,
            "delegated_result": delegated,
        },
    )


def _load_json_arg(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON input must be an object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ION Action/MCP branch leader helper.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--branch-id", default=None)
    parser.add_argument("--describe", default=None)
    parser.add_argument("--invoke", action="store_true")
    parser.add_argument("--receipts", default=None)
    parser.add_argument("--route-id", default=None)
    parser.add_argument("--args-json", default=None)
    parser.add_argument("--idempotency-key", default=None)
    parser.add_argument("--confirmation", default=None)
    parser.add_argument("--expected-route-schema-version", default=None)
    args = parser.parse_args(argv)

    if args.describe:
        result = action_branch_describe(args.ion_root, branch_id=args.describe)
    elif args.invoke:
        result = action_branch_invoke(
            args.ion_root,
            branch_id=str(args.branch_id or ""),
            route_id=str(args.route_id or ""),
            args=_load_json_arg(args.args_json),
            idempotency_key=args.idempotency_key,
            confirmation=args.confirmation,
            expected_route_schema_version=args.expected_route_schema_version,
        )
    elif args.receipts:
        result = action_branch_receipts(args.ion_root, branch_id=args.receipts, route_id=args.route_id)
    else:
        result = action_branch_list(args.ion_root)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") is not False else 1


if __name__ == "__main__":
    raise SystemExit(main())
