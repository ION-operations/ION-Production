"""True-name binding helpers for Worker Shift and Presence.

This candidate module binds action-bound worker true names to explicit context
packages and path scopes. It validates path and lease claims, but grants no
production, live execution, secret, deployment, or accepted-state authority.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


SCHEMA_ID = "ion.true_name_binding.v0_1"
PARSED_SCHEMA_ID = "ion.true_name_binding.parsed_true_name.v0_1"
VALIDATION_SCHEMA_ID = "ion.true_name_binding.path_validation.v0_1"
LEASE_VALIDATION_SCHEMA_ID = "ion.true_name_binding.lease_validation.v0_1"

TRUE_NAME_BINDING_ROOT = Path("ION/05_context/current/worker_shift/true_name_bindings")

AUTHORITY_FALSE: dict[str, bool] = {
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "deploy_authority": False,
}

ACTIVE_BINDING_STATES = {"ACTIVE", "BOUND"}
INACTIVE_BINDING_STATES = {"SIGNED_OFF", "EXPIRED", "SETTLED", "SUPERSEDED", "RELEASED", "FAILED"}
LEASE_MODES = {"read", "write", "exclusive_write"}

TRUE_NAME_RE = re.compile(
    r"^(?P<carrier>[a-z][a-z0-9]*)_(?P<lane>[a-z])(?P<sequence>[0-9]+)_(?P<mission>[a-z0-9]+(?:_[a-z0-9]+)*)$"
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _slug(value: Any, *, fallback: str = "item", limit: int = 96) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip()).strip("._-")
    return (slug or fallback)[:limit]


def _clean_path(value: str | Path) -> str:
    text = str(value).replace("\\", "/").strip()
    text = re.sub(r"/+", "/", text)
    return text.strip("./") or "."


def _paths(paths: Iterable[str | Path] | None) -> list[str]:
    return sorted({_clean_path(path) for path in (paths or [])})


def _list(values: Iterable[Any] | None) -> list[str]:
    return sorted({str(value).strip() for value in (values or []) if str(value).strip()})


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _read_json(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _resolve_root(root: str | Path | None = None) -> Path:
    return Path(root or ".").expanduser().resolve(strict=False)


def _rel(path: Path | str, root: Path) -> str:
    candidate = Path(path)
    try:
        return candidate.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return candidate.as_posix()


def infer_domain(mission_movement: str) -> str:
    """Infer the default domain from a mission movement name."""

    movement = mission_movement.lower()
    if "vault" in movement or "secret" in movement:
        return "security.vault"
    if "wave" in movement:
        return "context.wave"
    if "worker_shift" in movement or "presence" in movement:
        return "worker_shift.presence"
    if "status" in movement or "truth" in movement:
        return "status.truth"
    if "action" in movement or "gateway" in movement:
        return "action.gateway"
    return f"mission.{movement}"


def infer_path_domain(path: str | Path) -> str | None:
    """Infer a coarse domain from a path string without reading the path."""

    clean = _clean_path(path)
    if clean.startswith("ION_VAULT_LOCAL") or clean.startswith("env/") or clean.startswith(".env") or "/env/" in clean:
        return "security.vault"
    if clean in {"env.supabase.local", "env.supabase.local.example"}:
        return "security.vault"
    if "ion_security_boundary.py" in clean or "/security" in clean or clean.startswith("ION/05_context/current/security"):
        return "security.vault"
    if clean.startswith("ION/05_context/current/worker_shift"):
        return "worker_shift.presence"
    if "wave" in clean.lower():
        return "context.wave"
    if clean.startswith("ION/02_architecture"):
        return "architecture"
    return None


def parse_true_name(true_name: str) -> dict[str, Any]:
    """Parse a true name such as codex_a2_vault_move."""

    match = TRUE_NAME_RE.match(true_name)
    if not match:
        raise ValueError(f"invalid true name:{true_name}")
    mission = match.group("mission")
    return {
        "schema_id": PARSED_SCHEMA_ID,
        "true_name": true_name,
        "carrier": match.group("carrier"),
        "lane": match.group("lane").upper(),
        "sequence": int(match.group("sequence")),
        "mission_movement": mission,
        "inferred_domain": infer_domain(mission),
        "authority": dict(AUTHORITY_FALSE),
    }


def bind_true_name(
    true_name: str,
    *,
    folder_domains: Iterable[str] | None = None,
    context_package_ids: Iterable[str] | None = None,
    allowed_path_scopes: Iterable[str | Path] | None = None,
    expected_receipts: Iterable[str | Path] | None = None,
    binding_id: str | None = None,
    status: str | None = None,
    expires_at: str | None = None,
    supersedes: str | None = None,
    root: str | Path | None = None,
    now: str | None = None,
    write: bool = False,
) -> dict[str, Any]:
    """Create an action-bound true-name binding and optionally persist it."""

    shell_root = _resolve_root(root)
    timestamp = now or _now()
    parsed = parse_true_name(true_name)
    domains = _list(folder_domains)
    package_ids = _list(context_package_ids)
    scopes = _paths(allowed_path_scopes)
    receipts = _paths(expected_receipts)
    incomplete: list[str] = []
    if not package_ids:
        incomplete.append("MISSING_CONTEXT_PACKAGE")
    if not scopes:
        incomplete.append("MISSING_ALLOWED_PATH_SCOPE")
    if not domains:
        incomplete.append("MISSING_FOLDER_DOMAIN")
    elif parsed["inferred_domain"] not in domains:
        incomplete.append("INFERRED_DOMAIN_NOT_ASSIGNED")
    binding_status = status or ("INCOMPLETE" if incomplete else "ACTIVE")
    binding = {
        "schema_id": SCHEMA_ID,
        "binding_id": binding_id or f"tnb:{_slug(true_name)}",
        "true_name": true_name,
        "parsed_true_name": parsed,
        "folder_domains": domains,
        "context_package_ids": package_ids,
        "allowed_path_scopes": scopes,
        "expected_receipts": receipts,
        "binding_status": binding_status,
        "binding_ready": binding_status in ACTIVE_BINDING_STATES and not incomplete,
        "incomplete_reasons": incomplete,
        "created_at": timestamp,
        "expires_at": expires_at,
        "supersedes": supersedes,
        "identity_law": {
            "action_bound_identity_not_persona": True,
            "expires_settles_or_is_superseded": True,
            "does_not_grant_authority": True,
        },
        "authority": dict(AUTHORITY_FALSE),
    }
    if write:
        path = shell_root / TRUE_NAME_BINDING_ROOT / f"{_slug(true_name)}.json"
        _write_json(path, binding)
        binding["binding_path"] = _rel(path, shell_root)
    return binding


def load_true_name_binding(true_name: str, *, root: str | Path | None = None) -> dict[str, Any] | None:
    """Load a persisted true-name binding from the candidate context holder."""

    shell_root = _resolve_root(root)
    payload = _read_json(shell_root / TRUE_NAME_BINDING_ROOT / f"{_slug(true_name)}.json")
    return payload if isinstance(payload, dict) else None


def _scope_allows_path(scope: str, path: str) -> bool:
    clean_scope = _clean_path(scope)
    clean_path = _clean_path(path)
    if any(mark in clean_scope for mark in "*?["):
        return fnmatch.fnmatch(clean_path, clean_scope)
    return clean_path == clean_scope or clean_path.startswith(f"{clean_scope}/")


def _active_shift_for_true_name(board: Mapping[str, Any], true_name: str) -> Mapping[str, Any] | None:
    for shift in board.get("active_shifts", []):
        if not isinstance(shift, Mapping):
            continue
        if shift.get("worker_id") != true_name:
            continue
        if shift.get("status") in {"ACTIVE", "SIGNED_ON", "HEARTBEAT"}:
            return shift
    return None


def validate_path_claim(
    binding: Mapping[str, Any],
    paths: Iterable[str | Path],
    *,
    require_ready: bool = True,
) -> dict[str, Any]:
    """Validate that claimed paths are inside an active true-name binding."""

    claimed_paths = _paths(paths)
    scopes = [str(scope) for scope in binding.get("allowed_path_scopes", [])]
    domains = set(str(domain) for domain in binding.get("folder_domains", []))
    status = str(binding.get("binding_status") or "")
    ready = bool(binding.get("binding_ready"))
    rejections: list[dict[str, Any]] = []
    accepted: list[str] = []

    if status in INACTIVE_BINDING_STATES or status not in ACTIVE_BINDING_STATES | {"INCOMPLETE"}:
        rejections.append({"reason": "TRUE_NAME_BINDING_NOT_ACTIVE", "binding_status": status})
    if require_ready and not ready:
        rejections.append(
            {
                "reason": "TRUE_NAME_BINDING_INCOMPLETE",
                "incomplete_reasons": list(binding.get("incomplete_reasons", [])),
            }
        )

    for path in claimed_paths:
        matching_scopes = [scope for scope in scopes if _scope_allows_path(scope, path)]
        path_domain = infer_path_domain(path)
        path_rejections: list[str] = []
        if not matching_scopes:
            path_rejections.append("PATH_OUTSIDE_TRUE_NAME_BINDING")
        if path_domain and path_domain not in domains:
            path_rejections.append("DOMAIN_PATH_MISMATCH")
        if path_rejections:
            rejections.append(
                {
                    "path": path,
                    "path_domain": path_domain,
                    "reasons": path_rejections,
                    "allowed_path_scopes": scopes,
                    "folder_domains": sorted(domains),
                }
            )
        else:
            accepted.append(path)

    return {
        "schema_id": VALIDATION_SCHEMA_ID,
        "true_name": binding.get("true_name"),
        "ok": not rejections,
        "decision": "ACCEPT" if not rejections else "REJECT",
        "accepted_paths": accepted,
        "rejections": rejections,
        "authority": dict(AUTHORITY_FALSE),
    }


def validate_lease_claim(
    binding: Mapping[str, Any],
    *,
    lease_id: str,
    paths: Iterable[str | Path],
    mode: str,
    board: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a Worker Shift lease claim against a true-name binding."""

    if mode not in LEASE_MODES:
        raise ValueError(f"unsupported lease mode:{mode}")
    true_name = str(binding.get("true_name") or "")
    path_validation = validate_path_claim(binding, paths)
    rejections = list(path_validation["rejections"])
    if board is not None and _active_shift_for_true_name(board, true_name) is None:
        rejections.append({"reason": "TRUE_NAME_HAS_NO_ACTIVE_SIGN_ON", "true_name": true_name})
    return {
        "schema_id": LEASE_VALIDATION_SCHEMA_ID,
        "true_name": true_name,
        "lease": {
            "lease_id": lease_id,
            "worker_id": true_name,
            "mode": mode,
            "paths": _paths(paths),
        },
        "ok": not rejections,
        "decision": "ACCEPT" if not rejections else "REJECT",
        "path_validation": path_validation,
        "rejections": rejections,
        "authority": dict(AUTHORITY_FALSE),
    }


def claim_bound_work_lease(
    binding: Mapping[str, Any],
    *,
    root: str | Path | None = None,
    lease_id: str,
    paths: Iterable[str | Path],
    mode: str,
    board: Mapping[str, Any] | None = None,
    objective: str | None = None,
    packet_id: str | None = None,
    branch_id: str | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Validate and then claim a Worker Shift lease through the presence helper."""

    validation = validate_lease_claim(binding, lease_id=lease_id, paths=paths, mode=mode, board=board)
    if not validation["ok"]:
        return {
            "ok": False,
            "result": "TRUE_NAME_BINDING_REJECTED",
            "validation": validation,
            "authority": dict(AUTHORITY_FALSE),
        }
    from .ion_worker_shift_presence import claim_work_lease

    lease = claim_work_lease(
        validation["true_name"],
        lease_id,
        validation["lease"]["paths"],
        mode,
        root=root,
        objective=objective,
        packet_id=packet_id,
        branch_id=branch_id,
        now=now,
    )
    return {
        "ok": lease["receipt"]["result"] == "ACTIVE",
        "result": lease["receipt"]["result"],
        "validation": validation,
        "lease_claim": lease,
        "authority": dict(AUTHORITY_FALSE),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ION true-name binding helper")
    parser.add_argument("--root", default=".", help="ION active root")
    sub = parser.add_subparsers(dest="command", required=True)

    parse_cmd = sub.add_parser("parse")
    parse_cmd.add_argument("true_name")

    bind_cmd = sub.add_parser("bind")
    bind_cmd.add_argument("true_name")
    bind_cmd.add_argument("--domain", action="append", default=[])
    bind_cmd.add_argument("--context-package-id", action="append", default=[])
    bind_cmd.add_argument("--path-scope", action="append", default=[])
    bind_cmd.add_argument("--expected-receipt", action="append", default=[])
    bind_cmd.add_argument("--write", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "parse":
        result = parse_true_name(args.true_name)
    else:
        result = bind_true_name(
            args.true_name,
            folder_domains=args.domain,
            context_package_ids=args.context_package_id,
            allowed_path_scopes=args.path_scope,
            expected_receipts=args.expected_receipt,
            root=args.root,
            write=args.write,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
