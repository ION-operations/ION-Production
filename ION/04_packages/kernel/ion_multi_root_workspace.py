from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


SCHEMA_ID = "ion.multi_root_workspace.v1_candidate"
REGISTRY_RELATIVE_PATH = Path("ION/03_registry/ion_workspace_root_registry.yaml")
RECEIPT_RELATIVE_ROOT = Path("ION/05_context/current/workspace_roots")
CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"
MAX_BYTES_DEFAULT = 64_000
MAX_FILES_DEFAULT = 200
MAX_LINE_COUNT_DEFAULT = 120

SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,96}$")
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{12,}"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[^\s\"']{6,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-.]{12,}"),
]
FORBIDDEN_COMMANDS = {"bash", "sh", "zsh", "fish", "sudo", "su", "rm", "rmdir", "mv", "git", "curl", "wget", "ssh", "scp"}
ALLOWED_OPERATIONS = {"read", "search", "profile", "spawn_agent", "write_candidate", "run_tests", "run_shell"}

AUTHORITY_FALSE = {
    "accepted_state_claim": False,
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "git_push_authority": False,
    "deletion_authority": False,
}

NON_CLAIMS = [
    "Registered roots are an allowlist, not arbitrary filesystem authority.",
    "Root-scoped reads/searches are bounded and redact secret-looking content.",
    "Spawn routes write candidate packets/receipts only; they do not prove direct live agent control.",
    "No accepted-state, production, secrets, git push, deletion, or materialization authority is granted.",
]

MUTATION_ACTOR_PROOF_FIELDS = ["agent_id", "actor_root_id"]
MUTATION_LEASE_PROOF_FIELDS = ["lease_id"]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_id(value: Any, *, field: str = "id") -> str:
    text = str(value or "").strip()
    if not SAFE_ID_RE.fullmatch(text):
        raise ValueError(f"unsafe_{field}")
    return text


def _safe_idempotency_key(value: Any) -> str:
    text = _safe_id(value, field="idempotency_key")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{text[:80]}_{digest}"


def _redact(value: Any, *, limit: int = 4000) -> str:
    text = str(value or "")
    if len(text) > limit:
        text = text[:limit] + "...[truncated]"
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("***REDACTED***", text)
    return text


def _repo_rel(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def _base(route_id: str, *, ok: bool = True, finding: str | None = None, refusal_class: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": ok,
        "schema_id": SCHEMA_ID,
        "route_id": route_id,
        "generated_at": _now(),
        "mutates_active_state": False,
        **AUTHORITY_FALSE,
        "authority": dict(AUTHORITY_FALSE),
        "non_claims": list(NON_CLAIMS),
    }
    if finding:
        payload["finding"] = finding
    if refusal_class:
        payload["refusal_class"] = refusal_class
    return payload


def _blocked(route_id: str, finding: str, *, refusal_class: str = "SCHEMA_INVALID", data: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = _base(route_id, ok=False, finding=finding, refusal_class=refusal_class)
    if data:
        payload.update(dict(data))
    return payload


def _read_yaml_or_json(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text) or {}
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("registry_not_object")
    return data


def _write_yaml_or_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is not None:
        text = yaml.safe_dump(dict(payload), sort_keys=False)
    else:
        text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def _registry_path(root: Path) -> Path:
    return root / REGISTRY_RELATIVE_PATH


def _load_registry(root: Path) -> tuple[Path, dict[str, Any]]:
    path = _registry_path(root)
    if not path.is_file():
        raise FileNotFoundError("workspace_root_registry_missing")
    registry = _read_yaml_or_json(path)
    roots = registry.get("roots")
    if not isinstance(roots, list):
        raise ValueError("workspace_root_registry_roots_missing")
    return path, registry


def _root_entries(registry: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [dict(item) for item in registry.get("roots", []) if isinstance(item, Mapping)]


def _registered_root(root: Path, root_id: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    registry_path, registry = _load_registry(root)
    safe_root_id = _safe_id(root_id, field="root_id")
    for entry in _root_entries(registry):
        if entry.get("root_id") == safe_root_id:
            absolute_path = Path(str(entry.get("absolute_path") or "")).expanduser().resolve(strict=False)
            entry["absolute_path"] = absolute_path.as_posix()
            return registry_path, registry, entry
    raise KeyError("unregistered_root")


def _path_exclusions(entry: Mapping[str, Any]) -> list[str]:
    raw = entry.get("path_exclusions") or []
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if str(item).strip()]


def _is_excluded(relative: Path, exclusions: Sequence[str]) -> str | None:
    rel = relative.as_posix()
    parts = set(relative.parts)
    for pattern in exclusions:
        clean = pattern.strip()
        if not clean:
            continue
        if clean in parts or rel == clean or rel.startswith(clean.rstrip("/") + "/"):
            return clean
        if clean.startswith("**/") and clean[3:] in parts:
            return clean
    return None


def _resolve_under_root(entry: Mapping[str, Any], value: Any, *, default_to_root: bool = False) -> tuple[Path, Path]:
    base = Path(str(entry.get("absolute_path") or "")).expanduser().resolve(strict=False)
    raw = str(value or "").strip()
    if not raw and default_to_root:
        candidate = base
    elif not raw:
        raise ValueError("path_required")
    else:
        path = Path(raw).expanduser()
        candidate = path.resolve(strict=False) if path.is_absolute() else (base / path).resolve(strict=False)
    try:
        relative = candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError("path_outside_registered_root") from exc
    excluded = _is_excluded(relative, _path_exclusions(entry))
    if excluded:
        raise ValueError("path_excluded_by_root_policy")
    return candidate, relative


def _operation_allowed(entry: Mapping[str, Any], operation: str) -> bool:
    allowed = {str(item) for item in entry.get("allowed_operations", []) if str(item)}
    forbidden = {str(item) for item in entry.get("forbidden_operations", []) if str(item)}
    return operation in allowed and operation not in forbidden


def _operation_or_block(route_id: str, entry: Mapping[str, Any], operation: str) -> dict[str, Any] | None:
    if _operation_allowed(entry, operation):
        return None
    return _blocked(
        route_id,
        "operation_not_allowed_for_root",
        refusal_class="ROOT_OPERATION_NOT_ALLOWED",
        data={
            "root_id": entry.get("root_id"),
            "operation": operation,
            "allowed_operations": entry.get("allowed_operations", []),
            "forbidden_operations": entry.get("forbidden_operations", []),
        },
    )


def _require_gate(route_id: str, args: Mapping[str, Any]) -> dict[str, Any] | None:
    if not str(args.get("idempotency_key") or "").strip():
        return _blocked(route_id, "idempotency_key_required", refusal_class="IDEMPOTENCY_KEY_REQUIRED")
    if str(args.get("confirmation") or "") != CONFIRMATION_TOKEN:
        return _blocked(route_id, "confirmation_required", refusal_class="CONFIRMATION_REQUIRED", data={"required_confirmation": CONFIRMATION_TOKEN})
    return None


def _actor_id(args: Mapping[str, Any]) -> str:
    return str(args.get("agent_id") or args.get("worker_id") or "").strip()


def _root_scoped_actor_proof(
    route_id: str,
    root: Path,
    args: Mapping[str, Any],
    *,
    target_root_id: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    agent_id = _actor_id(args)
    actor_root_id = str(args.get("actor_root_id") or "").strip()
    base = {
        "route_id": route_id,
        "target_root_id": target_root_id,
        "required_fields": list(MUTATION_ACTOR_PROOF_FIELDS),
        "provided_agent_id": bool(agent_id),
        "provided_actor_root_id": bool(actor_root_id),
    }
    if not agent_id or not actor_root_id:
        return None, _blocked(
            route_id,
            "root_scoped_actor_proof_required",
            refusal_class="ACTOR_PROOF_REQUIRED",
            data=base,
        )
    try:
        _, _, actor_entry = _registered_root(root, actor_root_id)
    except KeyError:
        return None, _blocked(
            route_id,
            "actor_root_not_registered",
            refusal_class="ACTOR_ROOT_NOT_REGISTERED",
            data={**base, "actor_root_id": actor_root_id},
        )
    except ValueError as exc:
        return None, _blocked(
            route_id,
            str(exc),
            refusal_class="ACTOR_ROOT_NOT_ALLOWED",
            data={**base, "actor_root_id": actor_root_id},
        )
    return {
        "agent_id": agent_id,
        "actor_root_id": actor_root_id,
        "actor_root_registered": True,
        "actor_root_class": actor_entry.get("root_class"),
        "target_root_id": target_root_id,
        **AUTHORITY_FALSE,
    }, None


def _public_lease_gate(gate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": gate.get("schema_id"),
        "ok": bool(gate.get("ok")),
        "required_lease_type": gate.get("required_lease_type"),
        "agent_id": gate.get("agent_id"),
        "lease_id": gate.get("lease_id"),
        "covered_target_count": gate.get("covered_target_count"),
        "lease_paths": gate.get("lease_paths", []),
        "lease_freshness": gate.get("lease_freshness"),
        "identity_binding_status": gate.get("identity_binding_status"),
        "authority": dict(AUTHORITY_FALSE),
    }


def _mutation_proof_requirements(
    *,
    required_lease_type: str,
    target_root_id: str,
    target_paths: Sequence[str] | None = None,
    target_scope: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "required_fields": list(MUTATION_ACTOR_PROOF_FIELDS + MUTATION_LEASE_PROOF_FIELDS),
        "worker_id_alias_accepted": True,
        "target_root_id": target_root_id,
        "required_lease_type": required_lease_type,
        "lease_validation": "require_active_edit_lease",
    }
    if target_paths:
        payload["lease_target_paths"] = list(target_paths)
    if target_scope:
        payload["lease_target_scope"] = target_scope
    return payload


def _require_mutation_proof(
    route_id: str,
    root: Path,
    args: Mapping[str, Any],
    *,
    target_root_id: str,
    target_paths: Sequence[str],
    required_lease_type: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    actor_proof, blocked = _root_scoped_actor_proof(route_id, root, args, target_root_id=target_root_id)
    if blocked:
        return blocked, None
    targets = [str(item).replace("\\", "/").strip() for item in target_paths if str(item or "").strip()]
    lease_id = str(args.get("lease_id") or "").strip()
    base = {
        "route_id": route_id,
        "target_root_id": target_root_id,
        "required_lease_type": required_lease_type,
        "required_fields": list(MUTATION_ACTOR_PROOF_FIELDS + MUTATION_LEASE_PROOF_FIELDS),
        "provided_agent_id": bool(actor_proof and actor_proof.get("agent_id")),
        "provided_actor_root_id": bool(actor_proof and actor_proof.get("actor_root_id")),
        "provided_lease_id": bool(lease_id),
        "lease_target_paths": targets,
    }
    if not lease_id:
        return _blocked(
            route_id,
            f"{required_lease_type}_lease_required",
            refusal_class="LEASE_REQUIRED",
            data=base,
        ), None
    if not targets:
        return _blocked(
            route_id,
            "lease_target_not_derivable",
            refusal_class="LEASE_TARGET_NOT_DERIVABLE",
            data=base,
        ), None

    from .ion_worker_shift_presence import require_active_edit_lease

    gate = require_active_edit_lease(
        root,
        agent_id=str(actor_proof["agent_id"]),
        lease_id=lease_id,
        target_files=targets,
        required_mode=required_lease_type,
    )
    if not gate.get("ok"):
        return _blocked(
            route_id,
            f"{required_lease_type}_lease_required",
            refusal_class="LEASE_REQUIRED",
            data={**base, **gate},
        ), None
    target_proof = {
        "target_root_id": target_root_id,
        "lease_target_paths": targets,
        "required_lease_type": required_lease_type,
        "target_paths_derived_by_route": True,
    }
    return None, {
        "proof_requirements_met": True,
        "actor_proof": actor_proof,
        "target_proof": target_proof,
        "lease_proof": _public_lease_gate(gate),
    }


def _public_root(entry: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(str(entry.get("absolute_path") or "")).expanduser().resolve(strict=False)
    return {
        "root_id": entry.get("root_id"),
        "label": entry.get("label"),
        "absolute_path": path.as_posix(),
        "root_class": entry.get("root_class"),
        "allowed_operations": entry.get("allowed_operations", []),
        "forbidden_operations": entry.get("forbidden_operations", []),
        "requires_operator_confirmation": bool(entry.get("requires_operator_confirmation", True)),
        **AUTHORITY_FALSE,
        "max_bytes": int(entry.get("max_bytes") or MAX_BYTES_DEFAULT),
        "max_files": int(entry.get("max_files") or MAX_FILES_DEFAULT),
        "path_exclusions": _path_exclusions(entry),
        "proof_requirements": entry.get("proof_requirements", []),
        "path_exists": path.exists(),
        "is_dir": path.is_dir(),
    }


def _root_registry(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    registry_path, registry = _load_registry(root)
    roots = [_public_root(entry) for entry in _root_entries(registry)]
    payload = _base("root_registry")
    payload.update(
        {
            "registry_path": _repo_rel(root, registry_path),
            "root_count": len(roots),
            "roots": roots[: max(1, min(int(args.get("limit") or 50), 100))],
            "default_root_id": registry.get("default_root_id"),
        }
    )
    return payload


def _root_status(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    root_id = str(args.get("root_id") or "").strip()
    if root_id:
        try:
            _, _, entry = _registered_root(root, root_id)
        except KeyError:
            return _blocked("root_status", "unregistered_root", refusal_class="ROOT_NOT_REGISTERED", data={"root_id": root_id})
        payload = _base("root_status")
        payload.update({"root": _public_root(entry)})
        return payload
    return _root_registry(root, args)


def _register_record_from_args(args: Mapping[str, Any]) -> dict[str, Any]:
    root_id = _safe_id(args.get("root_id"), field="root_id")
    absolute_path = Path(str(args.get("absolute_path") or "")).expanduser().resolve(strict=False)
    allowed = [str(item) for item in args.get("allowed_operations", []) if str(item) in ALLOWED_OPERATIONS]
    forbidden = [str(item) for item in args.get("forbidden_operations", []) if str(item) in ALLOWED_OPERATIONS]
    return {
        "root_id": root_id,
        "label": str(args.get("label") or root_id),
        "absolute_path": absolute_path.as_posix(),
        "root_class": str(args.get("root_class") or "external_project_root"),
        "allowed_operations": allowed or ["read", "search", "profile"],
        "forbidden_operations": forbidden,
        "requires_operator_confirmation": True,
        **AUTHORITY_FALSE,
        "max_bytes": max(1024, min(int(args.get("max_bytes") or MAX_BYTES_DEFAULT), 1_000_000)),
        "max_files": max(1, min(int(args.get("max_files") or MAX_FILES_DEFAULT), 5000)),
        "path_exclusions": list(args.get("path_exclusions") or [".git", ".env", "node_modules", ".venv", "__pycache__"]),
        "proof_requirements": list(args.get("proof_requirements") or ["root_id", "actor_root_id", "agent_id", "lease_id", "authority_flags", "non_claims"]),
    }


def _root_register_preview(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    record = _register_record_from_args(args)
    payload = _base("root_register_preview")
    payload.update(
        {
            "would_register": True,
            "record": record,
            "path_exists": Path(record["absolute_path"]).exists(),
            "registry_path": _repo_rel(root, _registry_path(root)),
            "mutation_proof_requirements": _mutation_proof_requirements(
                required_lease_type="exclusive_write",
                target_root_id=str(record["root_id"]),
                target_paths=[REGISTRY_RELATIVE_PATH.as_posix()],
            ),
        }
    )
    return payload


def _write_receipt(root: Path, folder: str, name: str, payload: Mapping[str, Any]) -> str:
    path = root / RECEIPT_RELATIVE_ROOT / folder / f"{_timestamp()}_{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return _repo_rel(root, path)


def _root_register(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    gated = _require_gate("root_register", args)
    if gated:
        return gated
    record = _register_record_from_args(args)
    proof_blocked, mutation_proof = _require_mutation_proof(
        "root_register",
        root,
        args,
        target_root_id=str(record["root_id"]),
        target_paths=[REGISTRY_RELATIVE_PATH.as_posix()],
        required_lease_type="exclusive_write",
    )
    if proof_blocked:
        return proof_blocked
    registry_path, registry = _load_registry(root)
    idem = _safe_idempotency_key(args.get("idempotency_key"))
    receipt_path = root / RECEIPT_RELATIVE_ROOT / "root_register_runs" / record["root_id"] / idem / "root_register_receipt.json"
    if receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        payload = _base("root_register")
        payload.update({"idempotent_replay": True, "receipt_path": _repo_rel(root, receipt_path), "receipt": receipt})
        return payload
    roots = _root_entries(registry)
    replaced = False
    for index, item in enumerate(roots):
        if item.get("root_id") == record["root_id"]:
            roots[index] = record
            replaced = True
            break
    if not replaced:
        roots.append(record)
    registry["roots"] = roots
    _write_yaml_or_json(registry_path, registry)
    receipt = {
        "schema_id": "ion.multi_root_workspace.root_register_receipt.v1_candidate",
        "created_at": _now(),
        "idempotency_key": args.get("idempotency_key"),
        "registered_root": record,
        "replaced_existing": replaced,
        "mutation_proof": mutation_proof,
        **AUTHORITY_FALSE,
        "non_claims": list(NON_CLAIMS),
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload = _base("root_register")
    payload.update({"registered_root": record, "replaced_existing": replaced, "receipt_path": _repo_rel(root, receipt_path), "mutation_proof": mutation_proof, "mutates_active_state": True})
    return payload


def _root_discovery_preview(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    registry_path, registry = _load_registry(root)
    registered_ids = {entry.get("root_id") for entry in _root_entries(registry)}
    candidates = [
        {"root_id": "active_ion_control", "absolute_path": "/home/sev/ION - Production/ION_Developement"},
        {"root_id": "ion_workspace_parent", "absolute_path": "/home/sev/ION - Production"},
        {"root_id": "codex_session_store", "absolute_path": "/home/sev/.codex/sessions"},
        {"root_id": "gemini_ion_sandbox_root", "absolute_path": "/home/sev/ION - Production/ION_Developement/ION/05_context/current/gemini_ion_sandboxes"},
    ]
    for item in candidates:
        path = Path(item["absolute_path"]).expanduser().resolve(strict=False)
        item["path_exists"] = path.exists()
        item["registered"] = item["root_id"] in registered_ids
    payload = _base("root_discovery_preview")
    payload.update({"registry_path": _repo_rel(root, registry_path), "candidate_count": len(candidates), "candidates": candidates, "would_scan_filesystem": False})
    return payload


def _file_profile(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "root_file_profile"
    try:
        _, _, entry = _registered_root(root, str(args.get("root_id") or ""))
        blocked = _operation_or_block(route_id, entry, "profile") or _operation_or_block(route_id, entry, "read")
        if blocked and not _operation_allowed(entry, "profile"):
            return blocked
        target, relative = _resolve_under_root(entry, args.get("path"), default_to_root=True)
    except KeyError:
        return _blocked(route_id, "unregistered_root", refusal_class="ROOT_NOT_REGISTERED", data={"root_id": args.get("root_id")})
    except ValueError as exc:
        return _blocked(route_id, str(exc), refusal_class="PATH_NOT_ALLOWED")
    stat = target.stat() if target.exists() else None
    sample_bytes = b""
    if target.is_file() and stat:
        max_bytes = min(int(entry.get("max_bytes") or MAX_BYTES_DEFAULT), int(args.get("max_bytes") or MAX_BYTES_DEFAULT))
        sample_bytes = target.read_bytes()[:max_bytes]
    payload = _base(route_id)
    payload.update(
        {
            "root": _public_root(entry),
            "root_id": entry.get("root_id"),
            "path": relative.as_posix(),
            "absolute_path": target.as_posix(),
            "exists": target.exists(),
            "is_file": target.is_file(),
            "is_dir": target.is_dir(),
            "size_bytes": stat.st_size if stat else None,
            "sampled_bytes": len(sample_bytes),
            "sha256_sample": hashlib.sha256(sample_bytes).hexdigest() if sample_bytes else None,
            "line_count_sample": sample_bytes.decode("utf-8", errors="replace").count("\n") if sample_bytes else None,
        }
    )
    return payload


def _file_slice(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "root_file_slice"
    try:
        _, _, entry = _registered_root(root, str(args.get("root_id") or ""))
        blocked = _operation_or_block(route_id, entry, "read")
        if blocked:
            return blocked
        target, relative = _resolve_under_root(entry, args.get("path"))
    except KeyError:
        return _blocked(route_id, "unregistered_root", refusal_class="ROOT_NOT_REGISTERED", data={"root_id": args.get("root_id")})
    except ValueError as exc:
        return _blocked(route_id, str(exc), refusal_class="PATH_NOT_ALLOWED")
    if not target.is_file():
        return _blocked(route_id, "file_not_found", refusal_class="PATH_NOT_ALLOWED", data={"path": relative.as_posix()})
    max_bytes = min(int(entry.get("max_bytes") or MAX_BYTES_DEFAULT), max(1, min(int(args.get("max_bytes") or MAX_BYTES_DEFAULT), 250_000)))
    start_line = max(1, int(args.get("start_line") or args.get("start") or 1))
    line_count = max(1, min(int(args.get("line_count") or MAX_LINE_COUNT_DEFAULT), 500))
    records = []
    used = 0
    with target.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            if line_no < start_line:
                continue
            if len(records) >= line_count or used >= max_bytes:
                break
            text = _redact(line.rstrip("\n"), limit=max_bytes)
            used += len(text.encode("utf-8", errors="replace"))
            records.append({"line_no": line_no, "text": text})
    payload = _base(route_id)
    payload.update({"root_id": entry.get("root_id"), "path": relative.as_posix(), "absolute_path": target.as_posix(), "records": records, "returned_line_count": len(records), "returned_bytes_approx": used, "bounded": True})
    return payload


def _iter_search_files(entry: Mapping[str, Any], base: Path, max_files: int) -> list[Path]:
    files: list[Path] = []
    exclusions = _path_exclusions(entry)
    for current, dirs, names in os.walk(base):
        current_path = Path(current)
        try:
            current_rel = current_path.relative_to(base)
        except ValueError:
            continue
        dirs[:] = [name for name in dirs if not _is_excluded(current_rel / name, exclusions)]
        for name in names:
            path = current_path / name
            try:
                relative = path.relative_to(base)
            except ValueError:
                continue
            if _is_excluded(relative, exclusions):
                continue
            files.append(path)
            if len(files) >= max_files:
                return files
    return files


def _root_search(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "root_search"
    query = str(args.get("query") or "").strip()
    if not query:
        return _blocked(route_id, "query_required")
    try:
        _, _, entry = _registered_root(root, str(args.get("root_id") or ""))
        blocked = _operation_or_block(route_id, entry, "search")
        if blocked:
            return blocked
        base, relative_base = _resolve_under_root(entry, args.get("path"), default_to_root=True)
    except KeyError:
        return _blocked(route_id, "unregistered_root", refusal_class="ROOT_NOT_REGISTERED", data={"root_id": args.get("root_id")})
    except ValueError as exc:
        return _blocked(route_id, str(exc), refusal_class="PATH_NOT_ALLOWED")
    max_files = max(1, min(int(args.get("max_files") or entry.get("max_files") or MAX_FILES_DEFAULT), int(entry.get("max_files") or MAX_FILES_DEFAULT), 1000))
    max_matches = max(1, min(int(args.get("max_matches") or 25), 100))
    max_bytes = max(1024, min(int(args.get("max_bytes") or entry.get("max_bytes") or MAX_BYTES_DEFAULT), int(entry.get("max_bytes") or MAX_BYTES_DEFAULT), 250_000))
    candidates = [base] if base.is_file() else _iter_search_files(entry, base, max_files)
    matches = []
    searched = 0
    for path in candidates:
        if len(matches) >= max_matches:
            break
        if not path.is_file():
            continue
        searched += 1
        try:
            text = path.read_bytes()[:max_bytes].decode("utf-8", errors="replace")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if query.lower() in line.lower():
                matches.append({"path": path.relative_to(Path(str(entry["absolute_path"]))).as_posix(), "line_no": line_no, "excerpt": _redact(line, limit=800)})
                if len(matches) >= max_matches:
                    break
    payload = _base(route_id)
    payload.update({"root_id": entry.get("root_id"), "path": relative_base.as_posix(), "query": _redact(query, limit=200), "searched_file_count": searched, "match_count": len(matches), "matches": matches, "bounded": True})
    return payload


def _spawn_packet(root: Path, args: Mapping[str, Any], entry: Mapping[str, Any], cwd: Path, cwd_rel: Path) -> dict[str, Any]:
    return {
        "schema_id": "ion.multi_root_workspace.agent_spawn_packet.v1_candidate",
        "created_at": _now(),
        "root_id": entry.get("root_id"),
        "root_class": entry.get("root_class"),
        "root_absolute_path": entry.get("absolute_path"),
        "cwd": cwd.as_posix(),
        "cwd_relative_path": cwd_rel.as_posix(),
        "objective": _redact(args.get("objective"), limit=8000),
        "agent_role": _redact(args.get("agent_role"), limit=500),
        "agent_carrier": str(args.get("agent_carrier") or "codex"),
        "model": str(args.get("model") or "gpt-5.5"),
        "effort": str(args.get("effort") or "high"),
        "allowed_paths": list(args.get("allowed_paths") or [cwd_rel.as_posix()]),
        "forbidden_paths": list(args.get("forbidden_paths") or entry.get("path_exclusions") or []),
        "max_runtime_seconds": max(1, min(int(args.get("max_runtime") or args.get("max_runtime_seconds") or 900), 7200)),
        "proof_required": list(args.get("proof_required") or ["root_id", "cwd", "touched_paths", "authority_flags", "return_contract"]),
        "return_contract": args.get("return_contract") or {
            "required_sections": ["CONTEXT_PROOF", "ROOT_AUTHORITY_PROOF", "WORK_RESULT", "NON_CLAIMS"],
            "must_include_root_id": True,
            "must_include_cwd": True,
        },
        "requested_authority_flags": args.get("authority_flags") or dict(AUTHORITY_FALSE),
        "mutation_proof_requirements": _mutation_proof_requirements(
            required_lease_type="exclusive_write",
            target_root_id=str(entry.get("root_id") or ""),
            target_scope="ION/05_context/current/workspace_roots/spawn_runs/{root_id}/{safe_idempotency_key}",
        ),
        **AUTHORITY_FALSE,
        "non_claims": list(NON_CLAIMS),
    }


def _root_agent_spawn_preview(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "root_agent_spawn_preview"
    try:
        _, _, entry = _registered_root(root, str(args.get("root_id") or ""))
        blocked = _operation_or_block(route_id, entry, "spawn_agent")
        if blocked:
            return blocked
        cwd, cwd_rel = _resolve_under_root(entry, args.get("cwd"), default_to_root=True)
    except KeyError:
        return _blocked(route_id, "unregistered_root", refusal_class="ROOT_NOT_REGISTERED", data={"root_id": args.get("root_id")})
    except ValueError as exc:
        return _blocked(route_id, str(exc), refusal_class="PATH_NOT_ALLOWED")
    packet = _spawn_packet(root, args, entry, cwd, cwd_rel)
    payload = _base(route_id)
    payload.update({"root_id": entry.get("root_id"), "cwd": cwd.as_posix(), "cwd_proof": {"cwd_under_registered_root": True, "cwd_relative_path": cwd_rel.as_posix()}, "requires_confirmation_for_spawn": True, "would_write_spawn_packet": True, "would_start_process": False, "mutation_proof_requirements": packet["mutation_proof_requirements"], "spawn_packet_preview": packet})
    return payload


def _root_agent_spawn(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "root_agent_spawn"
    gated = _require_gate(route_id, args)
    if gated:
        return gated
    preview = _root_agent_spawn_preview(root, args)
    if not preview.get("ok"):
        return preview
    entry = preview["spawn_packet_preview"]
    root_id = str(entry["root_id"])
    idem = _safe_idempotency_key(args.get("idempotency_key"))
    run_dir = root / RECEIPT_RELATIVE_ROOT / "spawn_runs" / root_id / idem
    packet_path = run_dir / "spawn_packet.json"
    task_return_path = run_dir / "task_return_stub.json"
    receipt_path = run_dir / "root_agent_spawn_receipt.json"
    proof_blocked, mutation_proof = _require_mutation_proof(
        route_id,
        root,
        args,
        target_root_id=root_id,
        target_paths=[_repo_rel(root, run_dir)],
        required_lease_type="exclusive_write",
    )
    if proof_blocked:
        return proof_blocked
    if receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        payload = _base(route_id)
        payload.update({"idempotent_replay": True, "receipt_path": _repo_rel(root, receipt_path), "receipt": receipt})
        return payload
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    task_return_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    entry["mutation_proof"] = mutation_proof
    packet_path.write_text(json.dumps(entry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    task_stub = {
        "schema_id": "ion.multi_root_workspace.task_return_stub.v1_candidate",
        "created_at": _now(),
        "root_id": root_id,
        "status": "PENDING_AGENT_NOT_STARTED_BY_MULTI_ROOT_WORKSPACE_ROUTE",
        "spawn_packet_path": _repo_rel(root, packet_path),
        **AUTHORITY_FALSE,
        "non_claims": list(NON_CLAIMS),
    }
    task_return_path.write_text(json.dumps(task_stub, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = {
        "schema_id": "ion.multi_root_workspace.root_agent_spawn_receipt.v1_candidate",
        "created_at": _now(),
        "idempotency_key": args.get("idempotency_key"),
        "root_id": root_id,
        "cwd": entry["cwd"],
        "cwd_proof": preview["cwd_proof"],
        "spawn_packet_path": _repo_rel(root, packet_path),
        "task_return_path": _repo_rel(root, task_return_path),
        "actual_process_started": False,
        "mutation_proof": mutation_proof,
        **AUTHORITY_FALSE,
        "non_claims": list(NON_CLAIMS),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload = _base(route_id)
    payload.update({"root_id": root_id, "cwd": entry["cwd"], "spawn_packet_path": _repo_rel(root, packet_path), "receipt_path": _repo_rel(root, receipt_path), "task_return_path": _repo_rel(root, task_return_path), "actual_process_started": False, "mutation_proof": mutation_proof, "mutates_active_state": True})
    return payload


def _command_preview(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "root_command_preview"
    try:
        _, _, entry = _registered_root(root, str(args.get("root_id") or ""))
        blocked = _operation_or_block(route_id, entry, "run_shell")
        if blocked:
            return blocked
        cwd, cwd_rel = _resolve_under_root(entry, args.get("cwd"), default_to_root=True)
    except KeyError:
        return _blocked(route_id, "unregistered_root", refusal_class="ROOT_NOT_REGISTERED", data={"root_id": args.get("root_id")})
    except ValueError as exc:
        return _blocked(route_id, str(exc), refusal_class="PATH_NOT_ALLOWED")
    command_argv = [str(item) for item in args.get("command_argv", [])]
    if not command_argv:
        return _blocked(route_id, "command_argv_required")
    executable = Path(command_argv[0]).name
    if executable in FORBIDDEN_COMMANDS:
        return _blocked(route_id, "command_executable_not_allowed", refusal_class="COMMAND_NOT_ALLOWED", data={"executable": executable})
    payload = _base(route_id)
    payload.update({"root_id": entry.get("root_id"), "cwd": cwd.as_posix(), "cwd_relative_path": cwd_rel.as_posix(), "command_argv": [_redact(item, limit=1000) for item in command_argv], "would_run": True, "requires_confirmation": True, "bounded_timeout_seconds": max(1, min(int(args.get("timeout_seconds") or 30), 300)), "mutation_proof_requirements": _mutation_proof_requirements(required_lease_type="exclusive_write", target_root_id=str(entry.get("root_id") or ""), target_paths=[cwd.as_posix()])})
    return payload


def _command_run(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "root_command_run"
    gated = _require_gate(route_id, args)
    if gated:
        return gated
    preview = _command_preview(root, args)
    if not preview.get("ok"):
        return preview
    _, _, entry = _registered_root(root, str(args.get("root_id") or ""))
    if str(entry.get("root_class")) != "sandbox_root":
        return _blocked(route_id, "command_run_only_enabled_for_sandbox_root", refusal_class="ROOT_OPERATION_NOT_ALLOWED", data={"root_id": entry.get("root_id"), "root_class": entry.get("root_class")})
    proof_blocked, mutation_proof = _require_mutation_proof(
        route_id,
        root,
        args,
        target_root_id=str(entry.get("root_id") or ""),
        target_paths=[str(preview["cwd"])],
        required_lease_type="exclusive_write",
    )
    if proof_blocked:
        return proof_blocked
    command_argv = [str(item) for item in args.get("command_argv", [])]
    timeout_seconds = int(preview["bounded_timeout_seconds"])
    idem = _safe_idempotency_key(args.get("idempotency_key"))
    receipt_file = root / RECEIPT_RELATIVE_ROOT / "command_runs" / str(entry.get("root_id")) / idem / "command_run_receipt.json"
    if receipt_file.is_file():
        receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
        payload = _base(route_id)
        payload.update({"idempotent_replay": True, "receipt_path": _repo_rel(root, receipt_file), "receipt": receipt})
        return payload
    completed = subprocess.run(command_argv, cwd=str(preview["cwd"]), text=True, capture_output=True, timeout=timeout_seconds)
    receipt = {
        "schema_id": "ion.multi_root_workspace.command_run_receipt.v1_candidate",
        "created_at": _now(),
        "root_id": entry.get("root_id"),
        "cwd": preview["cwd"],
        "command_argv_redacted": preview["command_argv"],
        "returncode": completed.returncode,
        "stdout_excerpt": _redact(completed.stdout, limit=4000),
        "stderr_excerpt": _redact(completed.stderr, limit=4000),
        "timeout_seconds": timeout_seconds,
        "bounded_local_command_executed": True,
        "mutation_proof": mutation_proof,
        **AUTHORITY_FALSE,
        "non_claims": list(NON_CLAIMS),
    }
    receipt_file.parent.mkdir(parents=True, exist_ok=True)
    receipt_file.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload = _base(route_id, ok=completed.returncode == 0)
    payload.update({"root_id": entry.get("root_id"), "cwd": preview["cwd"], "returncode": completed.returncode, "receipt_path": _repo_rel(root, receipt_file), "mutation_proof": mutation_proof, "mutates_active_state": True})
    return payload


def _root_receipts(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    root_id = str(args.get("root_id") or "").strip()
    limit = max(1, min(int(args.get("limit") or 20), 100))
    base = root / RECEIPT_RELATIVE_ROOT
    receipts = []
    if base.is_dir():
        for path in sorted(base.rglob("*.json"), key=lambda item: (item.stat().st_mtime, item.as_posix()), reverse=True):
            if len(receipts) >= limit:
                break
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                data = {}
            if root_id and data.get("root_id") != root_id:
                continue
            receipts.append({"path": _repo_rel(root, path), "schema_id": data.get("schema_id"), "created_at": data.get("created_at"), "root_id": data.get("root_id"), "cwd": data.get("cwd")})
    payload = _base("root_receipts")
    payload.update({"receipt_count": len(receipts), "receipts": receipts, "root_id": root_id or None})
    return payload


def invoke_multi_root_workspace_route(
    root: str | Path | None,
    *,
    route_id: str,
    args: Mapping[str, Any],
) -> dict[str, Any]:
    shell_root = Path(root or Path.cwd()).expanduser().resolve(strict=False)
    try:
        if route_id == "root_registry":
            return _root_registry(shell_root, args)
        if route_id == "root_status":
            return _root_status(shell_root, args)
        if route_id == "root_register_preview":
            return _root_register_preview(shell_root, args)
        if route_id == "root_register":
            return _root_register(shell_root, args)
        if route_id == "root_discovery_preview":
            return _root_discovery_preview(shell_root, args)
        if route_id == "root_file_profile":
            return _file_profile(shell_root, args)
        if route_id == "root_file_slice":
            return _file_slice(shell_root, args)
        if route_id == "root_search":
            return _root_search(shell_root, args)
        if route_id == "root_agent_spawn_preview":
            return _root_agent_spawn_preview(shell_root, args)
        if route_id == "root_agent_spawn":
            return _root_agent_spawn(shell_root, args)
        if route_id == "root_command_preview":
            return _command_preview(shell_root, args)
        if route_id == "root_command_run":
            return _command_run(shell_root, args)
        if route_id == "root_receipts":
            return _root_receipts(shell_root, args)
    except FileNotFoundError as exc:
        return _blocked(route_id, str(exc), refusal_class="ROOT_REGISTRY_NOT_FOUND")
    except ValueError as exc:
        return _blocked(route_id, str(exc), refusal_class="SCHEMA_INVALID")
    return _blocked(route_id, "route_not_supported_by_multi_root_workspace", refusal_class="BRANCH_ROUTE_NOT_FOUND", data={"route_id": route_id})
