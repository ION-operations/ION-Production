"""Codex CLI resume adapter for ION candidate continuity.

This adapter binds a native Codex CLI session id to ION worker true-name,
rank, context, status, cwd/root, leases, and receipt evidence. It never invokes
``codex resume``; it only produces manifests, lawful-resume decisions, bounded
prompts, and JSON-serializable receipts.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .ion_true_name_binding import parse_true_name


SCHEMA_ID = "ion.codex_cli_resume_adapter.v0_1"
MANIFEST_SCHEMA_ID = "ion.codex_cli_resume_manifest.v0_1"
DECISION_SCHEMA_ID = "ion.codex_cli_resume_decision.v0_1"
RECEIPT_SCHEMA_ID = "ion.codex_cli_resume_receipt.v0_1"
FORK_ROUTE_SCHEMA_ID = "ion.codex_cli_resume_fork_side_route.v0_1"
TRANSCRIPT_CLASSIFICATION_SCHEMA_ID = "ion.codex_cli_transcript_classification.v0_1"

SESSION_ROOT = Path("ION/05_context/current/codex_cli/sessions")

AUTHORITY_FALSE: dict[str, bool] = {
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "deploy_authority": False,
    "github_push_authority": False,
}

READY_STATUS_VERDICTS = {
    "ION_STATUS_READY",
    "ION_STATUS_PARTIAL",
    "ION_STATUS_SINGLE_CARRIER_READY",
    "ION_CODEX_SOLO_CONTEXT_READY",
}

INACTIVE_TRUE_NAME_STATES = {
    "EXPIRED",
    "SIGNED_OFF",
    "SETTLED",
    "SUPERSEDED",
    "RELEASED",
    "FAILED",
}

RANK_SIGNATURE_FIELDS = (
    "rank_id",
    "context_level",
    "domain_scope",
    "mutation_class",
    "settlement_power",
)

WRITE_RESUME_MODES = {"write", "exclusive_write", "candidate_patch", "mutation"}
WRITE_LEASE_MODES = {"write", "exclusive_write"}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp(now: str | None = None) -> str:
    return (now or _now()).replace("-", "").replace(":", "").replace("+00:00", "Z")


def _slug(value: Any, *, fallback: str = "item", limit: int = 96) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip()).strip("._-")
    return (slug or fallback)[:limit]


def _resolve_root(root: str | Path | None = None) -> Path:
    return Path(root or ".").expanduser().resolve(strict=False)


def _clean_path(value: str | Path) -> str:
    text = str(value).replace("\\", "/").strip()
    text = re.sub(r"/+", "/", text)
    return text.strip("./") or "."


def _paths(paths: Iterable[str | Path] | None) -> list[str]:
    return sorted({_clean_path(path) for path in (paths or [])})


def _rel(path: Path | str, root: Path) -> str:
    candidate = Path(path)
    try:
        return candidate.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return candidate.as_posix()


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


def _sha256_text(value: Any) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


def _path_forbidden(path: str | Path) -> str | None:
    clean = _clean_path(path)
    name = Path(clean).name
    if clean.startswith("ION_VAULT_LOCAL") or "/ION_VAULT_LOCAL/" in clean:
        return "VAULT_PATH_FORBIDDEN"
    if clean == ".env" or name.startswith(".env"):
        return "ENV_PATH_FORBIDDEN"
    return None


def _file_hash_entry(root: Path, path: str | Path) -> dict[str, Any]:
    clean = _clean_path(path)
    forbidden = _path_forbidden(clean)
    if forbidden:
        raise ValueError(f"{forbidden}:{clean}")
    target = root / clean
    entry: dict[str, Any] = {
        "path": clean,
        "exists": target.is_file(),
    }
    if target.is_file():
        entry["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    else:
        entry["sha256"] = None
    return entry


def _context_hashes(root: Path, context_package_refs: Iterable[str | Path] | None) -> list[dict[str, Any]]:
    return [_file_hash_entry(root, path) for path in _paths(context_package_refs)]


def _hash_set(entries: Iterable[Mapping[str, Any]]) -> str:
    stable = [
        {"path": item.get("path"), "exists": item.get("exists"), "sha256": item.get("sha256")}
        for item in entries
    ]
    return hashlib.sha256(json.dumps(stable, sort_keys=True).encode("utf-8")).hexdigest()


def _normalize_authority(authority: Mapping[str, Any] | None = None) -> dict[str, bool]:
    result = dict(AUTHORITY_FALSE)
    if authority:
        for key in result:
            if key in authority:
                result[key] = bool(authority[key])
    return result


def _normalize_rank_vector(rank: Mapping[str, Any] | str) -> dict[str, Any]:
    if isinstance(rank, str):
        payload: dict[str, Any] = {"rank_id": rank}
    else:
        payload = dict(rank)
    context_level = str(payload.get("context_level") or "")
    if not payload.get("rank_id") and context_level.startswith("R"):
        payload["rank_id"] = context_level
    payload.setdefault("authority", dict(AUTHORITY_FALSE))
    payload["authority"] = _normalize_authority(payload.get("authority"))
    return payload


def _rank_signature(rank: Mapping[str, Any]) -> dict[str, Any]:
    normalized = _normalize_rank_vector(rank)
    return {field: normalized.get(field) for field in RANK_SIGNATURE_FIELDS if normalized.get(field) is not None}


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value)
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _is_expired(expires_at: Any, *, now: str | None = None) -> bool:
    parsed = _parse_time(expires_at)
    current = _parse_time(now) or datetime.now(timezone.utc)
    return parsed is not None and parsed <= current


def _status_is_blocked(verdict: Any) -> bool:
    text = str(verdict or "").strip().upper()
    if not text:
        return True
    if "BLOCKED" in text or "DEGRADED" in text:
        return True
    return text not in READY_STATUS_VERDICTS


def _path_overlap(left: str, right: str) -> bool:
    left_clean = _clean_path(left).rstrip("/")
    right_clean = _clean_path(right).rstrip("/")
    return (
        left_clean == right_clean
        or left_clean.startswith(f"{right_clean}/")
        or right_clean.startswith(f"{left_clean}/")
    )


def _active_lease_covers_path(
    leases: Iterable[Mapping[str, Any]],
    *,
    worker_true_name: str,
    required_path: str,
    requested_mode: str,
) -> bool:
    needs_write = requested_mode in WRITE_RESUME_MODES
    for lease in leases:
        if lease.get("status") not in (None, "ACTIVE", "CLAIMED"):
            continue
        if lease.get("worker_id") != worker_true_name:
            continue
        mode = str(lease.get("mode") or lease.get("lease_type") or "")
        if needs_write and mode not in WRITE_LEASE_MODES:
            continue
        if not needs_write and mode not in WRITE_LEASE_MODES | {"read"}:
            continue
        if any(_path_overlap(required_path, str(path)) for path in lease.get("paths", [])):
            return True
    return False


def _missing_required_leases(
    *,
    worker_true_name: str,
    required_paths: Iterable[str],
    leases: Iterable[Mapping[str, Any]],
    requested_mode: str,
) -> list[str]:
    if requested_mode not in WRITE_RESUME_MODES:
        return []
    return [
        path
        for path in _paths(required_paths)
        if not _active_lease_covers_path(
            leases,
            worker_true_name=worker_true_name,
            required_path=path,
            requested_mode=requested_mode,
        )
    ]


def classify_transcript_ref(transcript_ref: str | Path | None) -> dict[str, Any]:
    """Classify a Codex transcript as witness evidence, never state."""

    return {
        "schema_id": TRANSCRIPT_CLASSIFICATION_SCHEMA_ID,
        "transcript_ref": _clean_path(transcript_ref) if transcript_ref else None,
        "classification": "transcript_witness_not_state",
        "state_authority": False,
        "accepted_state_claim": False,
        "policy": "native_codex_transcript_can_inform_resume_but_cannot_replace_ion_manifest_or_receipts",
        "authority": dict(AUTHORITY_FALSE),
    }


def _root_identity(root: Path, cwd: str | Path, ion_root: str | Path) -> dict[str, Any]:
    cwd_text = str(Path(cwd).expanduser().resolve(strict=False))
    ion_root_text = str(Path(ion_root).expanduser().resolve(strict=False))
    file_hashes: list[dict[str, Any]] = []
    for ref in ("pyproject.toml", "ION/REPO_AUTHORITY.md"):
        file_hashes.append(_file_hash_entry(root, ref))
    return {
        "cwd": cwd_text,
        "ion_root": ion_root_text,
        "cwd_sha256": _sha256_text(cwd_text),
        "ion_root_sha256": _sha256_text(ion_root_text),
        "file_hashes": file_hashes,
        "file_hash_set_sha256": _hash_set(file_hashes),
    }


def register_codex_session_manifest(
    *,
    codex_session_id: str,
    worker_true_name: str,
    rank_vector: Mapping[str, Any] | str,
    context_package_refs: Iterable[str | Path],
    status_verdict: str,
    cwd: str | Path,
    ion_root: str | Path,
    leases: Iterable[Mapping[str, Any]] | None = None,
    required_lease_paths: Iterable[str | Path] | None = None,
    transcript_ref: str | Path | None = None,
    true_name_binding: Mapping[str, Any] | None = None,
    true_name_expires_at: str | None = None,
    require_explicit_session_id: bool = True,
    allow_context_hash_drift: bool = False,
    cli_capability_observed: Mapping[str, Any] | None = None,
    manifest_id: str | None = None,
    root: str | Path | None = None,
    now: str | None = None,
    write: bool = False,
) -> dict[str, Any]:
    """Create and optionally persist a Codex resume manifest."""

    shell_root = _resolve_root(root)
    timestamp = now or _now()
    normalized_rank = _normalize_rank_vector(rank_vector)
    context_hashes = _context_hashes(shell_root, context_package_refs)
    lease_payload = [dict(lease) for lease in (leases or [])]
    inferred_required_paths = required_lease_paths
    if inferred_required_paths is None:
        inferred_required_paths = [
            path
            for lease in lease_payload
            for path in lease.get("paths", [])
            if path
        ]
    binding = dict(
        true_name_binding
        or {
            "binding_status": "ACTIVE",
            "binding_ready": True,
            "expires_at": true_name_expires_at,
        }
    )
    binding.setdefault("true_name", worker_true_name)
    binding.setdefault("expires_at", true_name_expires_at)
    manifest = {
        "schema_id": MANIFEST_SCHEMA_ID,
        "manifest_id": manifest_id or f"codex_resume_manifest:{_slug(codex_session_id)}",
        "created_at": timestamp,
        "carrier": "codex_cli",
        "codex_session_id": str(codex_session_id),
        "worker_true_name": worker_true_name,
        "true_name_binding": binding,
        "rank_vector": normalized_rank,
        "rank_signature": _rank_signature(normalized_rank),
        "status": {
            "verdict": status_verdict,
            "blocked": _status_is_blocked(status_verdict),
        },
        "root_identity": _root_identity(shell_root, cwd, ion_root),
        "context_packages": {
            "refs": _paths(context_package_refs),
            "hashes": context_hashes,
            "hash_set_sha256": _hash_set(context_hashes),
        },
        "leases": lease_payload,
        "required_lease_paths": _paths(inferred_required_paths),
        "transcript": classify_transcript_ref(transcript_ref),
        "resume_policy": {
            "require_explicit_session_id": bool(require_explicit_session_id),
            "blind_last_resume_allowed": not bool(require_explicit_session_id),
            "allow_context_hash_drift": bool(allow_context_hash_drift),
            "actual_resume_execution_allowed": False,
        },
        "cli_capability_observed": dict(cli_capability_observed or {}),
        "authority": dict(AUTHORITY_FALSE),
    }
    if write:
        manifest_path = shell_root / SESSION_ROOT / _slug(codex_session_id) / "manifest.json"
        _write_json(manifest_path, manifest)
        manifest["manifest_path"] = _rel(manifest_path, shell_root)
    return manifest


def load_codex_session_manifest(
    codex_session_id: str,
    *,
    root: str | Path | None = None,
) -> dict[str, Any] | None:
    """Load a persisted Codex resume manifest by native session id."""

    shell_root = _resolve_root(root)
    payload = _read_json(shell_root / SESSION_ROOT / _slug(codex_session_id) / "manifest.json")
    return payload if isinstance(payload, dict) else None


def build_bounded_resume_prompt(manifest: Mapping[str, Any]) -> str:
    """Render a bounded prompt to send after a separately approved resume."""

    context_refs = manifest.get("context_packages", {}).get("refs", [])
    lease_ids = [str(lease.get("lease_id")) for lease in manifest.get("leases", []) if lease.get("lease_id")]
    lines = [
        "# ION Codex CLI Resume Packet",
        "",
        f"codex_session_id: {manifest.get('codex_session_id')}",
        f"worker_true_name: {manifest.get('worker_true_name')}",
        "carrier: codex_cli",
        "resume_scope: bounded_candidate_continuity",
        "production_authority: false",
        "live_execution_authority: false",
        "accepted_state_claim: false",
        "secrets_authority: false",
        "",
        "Resume posture:",
        "- Treat the native Codex transcript as witness evidence only.",
        "- Use this manifest, Worker Shift leases, rank vector, status verdict, and context hashes as the ION resume gate.",
        "- Do not claim accepted state, production authority, live execution authority, deployment authority, push authority, or secret access.",
        "",
        "Root identity:",
        f"- cwd: {manifest.get('root_identity', {}).get('cwd')}",
        f"- ion_root: {manifest.get('root_identity', {}).get('ion_root')}",
        "",
        "Context packages:",
        *[f"- {ref}" for ref in context_refs],
        "",
        "Active lease evidence:",
        *[f"- {lease_id}" for lease_id in lease_ids],
    ]
    return "\n".join(lines).rstrip() + "\n"


def evaluate_resume_lawfulness(
    manifest: Mapping[str, Any],
    *,
    requested_session_id: str | None = None,
    use_last: bool = False,
    worker_true_name: str | None = None,
    current_rank_vector: Mapping[str, Any] | str | None = None,
    current_status_verdict: str | None = None,
    current_cwd: str | Path | None = None,
    current_ion_root: str | Path | None = None,
    current_context_package_refs: Iterable[str | Path] | None = None,
    current_leases: Iterable[Mapping[str, Any]] | None = None,
    requested_mode: str = "read",
    requested_authority: Mapping[str, Any] | None = None,
    allow_context_hash_drift: bool = False,
    root: str | Path | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Evaluate whether a Codex CLI resume is lawful under the manifest."""

    shell_root = _resolve_root(root)
    timestamp = now or _now()
    rejections: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    manifest_session_id = str(manifest.get("codex_session_id") or "")
    expected_true_name = str(manifest.get("worker_true_name") or "")
    policy = manifest.get("resume_policy", {}) if isinstance(manifest.get("resume_policy"), Mapping) else {}
    require_explicit = bool(policy.get("require_explicit_session_id", True))

    if use_last and require_explicit and not requested_session_id:
        rejections.append({"reason": "BLIND_LAST_RESUME_BLOCKED", "policy": "explicit_session_id_required"})
    if require_explicit and not requested_session_id:
        rejections.append({"reason": "EXPLICIT_SESSION_ID_REQUIRED"})
    if requested_session_id and str(requested_session_id) != manifest_session_id:
        rejections.append(
            {
                "reason": "SESSION_ID_MISMATCH",
                "requested_session_id": str(requested_session_id),
                "manifest_session_id": manifest_session_id,
            }
        )
    if worker_true_name and worker_true_name != expected_true_name:
        rejections.append(
            {
                "reason": "WORKER_TRUE_NAME_MISMATCH",
                "requested_true_name": worker_true_name,
                "manifest_true_name": expected_true_name,
            }
        )

    binding = manifest.get("true_name_binding", {}) if isinstance(manifest.get("true_name_binding"), Mapping) else {}
    binding_status = str(binding.get("binding_status") or "")
    if binding_status in INACTIVE_TRUE_NAME_STATES:
        rejections.append({"reason": "TRUE_NAME_NOT_ACTIVE", "binding_status": binding_status})
    if _is_expired(binding.get("expires_at"), now=timestamp):
        rejections.append({"reason": "TRUE_NAME_EXPIRED", "expires_at": binding.get("expires_at")})

    expected_rank = manifest.get("rank_signature", _rank_signature(manifest.get("rank_vector", {})))
    actual_rank = _rank_signature(current_rank_vector or manifest.get("rank_vector", {}))
    if actual_rank != expected_rank:
        rejections.append({"reason": "RANK_DRIFT", "expected": expected_rank, "actual": actual_rank})

    status_verdict = current_status_verdict or manifest.get("status", {}).get("verdict")
    if _status_is_blocked(status_verdict):
        rejections.append({"reason": "STATUS_BLOCKED", "status_verdict": status_verdict})

    root_identity = manifest.get("root_identity", {}) if isinstance(manifest.get("root_identity"), Mapping) else {}
    if current_cwd is not None:
        current_cwd_text = str(Path(current_cwd).expanduser().resolve(strict=False))
        if current_cwd_text != root_identity.get("cwd"):
            rejections.append(
                {"reason": "CWD_ROOT_MISMATCH", "expected": root_identity.get("cwd"), "actual": current_cwd_text}
            )
    if current_ion_root is not None:
        current_ion_root_text = str(Path(current_ion_root).expanduser().resolve(strict=False))
        if current_ion_root_text != root_identity.get("ion_root"):
            rejections.append(
                {
                    "reason": "ION_ROOT_MISMATCH",
                    "expected": root_identity.get("ion_root"),
                    "actual": current_ion_root_text,
                }
            )

    context_refs = (
        _paths(current_context_package_refs)
        if current_context_package_refs is not None
        else list(manifest.get("context_packages", {}).get("refs", []))
    )
    current_hashes = _context_hashes(shell_root, context_refs)
    expected_hashes = list(manifest.get("context_packages", {}).get("hashes", []))
    current_hash_set = _hash_set(current_hashes)
    expected_hash_set = str(manifest.get("context_packages", {}).get("hash_set_sha256") or _hash_set(expected_hashes))
    drift_allowed = bool(allow_context_hash_drift or policy.get("allow_context_hash_drift"))
    if current_hash_set != expected_hash_set:
        drift = {
            "reason": "CONTEXT_HASH_DRIFT",
            "expected_hash_set_sha256": expected_hash_set,
            "actual_hash_set_sha256": current_hash_set,
            "expected_hashes": expected_hashes,
            "actual_hashes": current_hashes,
        }
        if drift_allowed:
            warnings.append({**drift, "approved": True})
        else:
            rejections.append(drift)

    lease_payload = [dict(lease) for lease in (current_leases if current_leases is not None else manifest.get("leases", []))]
    missing_leases = _missing_required_leases(
        worker_true_name=expected_true_name,
        required_paths=manifest.get("required_lease_paths", []),
        leases=lease_payload,
        requested_mode=requested_mode,
    )
    if missing_leases:
        rejections.append(
            {
                "reason": "REQUIRED_WRITE_LEASE_MISSING",
                "missing_paths": missing_leases,
                "requested_mode": requested_mode,
            }
        )

    requested = _normalize_authority(requested_authority)
    if requested["production_authority"] or requested["live_execution_authority"]:
        rejections.append(
            {
                "reason": "RESUME_CANNOT_GRANT_PRODUCTION_OR_LIVE_AUTHORITY",
                "requested_authority": requested,
            }
        )

    ok = not rejections
    decision = {
        "schema_id": DECISION_SCHEMA_ID,
        "created_at": timestamp,
        "codex_session_id": manifest_session_id,
        "worker_true_name": expected_true_name,
        "requested": {
            "session_id": requested_session_id,
            "use_last": bool(use_last),
            "requested_mode": requested_mode,
            "requested_authority": requested,
        },
        "decision": "ALLOW_RESUME" if ok else "BLOCK_RESUME",
        "ok": ok,
        "resume_lawful": ok,
        "rejections": rejections,
        "warnings": warnings,
        "bounded_resume_prompt": build_bounded_resume_prompt(manifest) if ok else None,
        "actual_resume_executed": False,
        "authority": dict(AUTHORITY_FALSE),
    }
    json.dumps(decision, sort_keys=True)
    return decision


def make_resume_receipt(
    manifest: Mapping[str, Any],
    decision: Mapping[str, Any],
    *,
    root: str | Path | None = None,
    now: str | None = None,
    write: bool = False,
) -> dict[str, Any]:
    """Create and optionally persist a resume decision receipt."""

    shell_root = _resolve_root(root)
    timestamp = now or _now()
    receipt = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "created_at": timestamp,
        "receipt_type": "codex_cli_resume_decision",
        "codex_session_id": manifest.get("codex_session_id"),
        "worker_true_name": manifest.get("worker_true_name"),
        "manifest_id": manifest.get("manifest_id"),
        "manifest_path": manifest.get("manifest_path"),
        "decision": dict(decision),
        "actual_resume_executed": False,
        "authority": dict(AUTHORITY_FALSE),
    }
    if write:
        receipt_path = (
            shell_root
            / SESSION_ROOT
            / _slug(manifest.get("codex_session_id"))
            / f"resume_decision_{_stamp(timestamp)}.json"
        )
        _write_json(receipt_path, receipt)
        receipt["receipt_path"] = _rel(receipt_path, shell_root)
    json.dumps(receipt, sort_keys=True)
    return receipt


def create_fork_side_route(
    manifest: Mapping[str, Any],
    *,
    movement: str = "codex_resume_adapter_fork",
    now: str | None = None,
) -> dict[str, Any]:
    """Create a candidate child true name for fork/side-route work."""

    timestamp = now or _now()
    parent_true_name = str(manifest.get("worker_true_name") or "")
    parsed = parse_true_name(parent_true_name)
    child_true_name = (
        f"{parsed['carrier']}_{str(parsed['lane']).lower()}{int(parsed['sequence']) + 1}_{_slug(movement).lower()}"
    )
    route = {
        "schema_id": FORK_ROUTE_SCHEMA_ID,
        "created_at": timestamp,
        "parent_true_name": parent_true_name,
        "candidate_child_true_name": child_true_name,
        "codex_session_id": manifest.get("codex_session_id"),
        "route_type": "fork_side_route_candidate",
        "accepted_state_claim": False,
        "settlement_power": "recommend_only",
        "authority": dict(AUTHORITY_FALSE),
    }
    json.dumps(route, sort_keys=True)
    return route


__all__ = [
    "AUTHORITY_FALSE",
    "DECISION_SCHEMA_ID",
    "FORK_ROUTE_SCHEMA_ID",
    "MANIFEST_SCHEMA_ID",
    "RECEIPT_SCHEMA_ID",
    "SCHEMA_ID",
    "SESSION_ROOT",
    "TRANSCRIPT_CLASSIFICATION_SCHEMA_ID",
    "build_bounded_resume_prompt",
    "classify_transcript_ref",
    "create_fork_side_route",
    "evaluate_resume_lawfulness",
    "load_codex_session_manifest",
    "make_resume_receipt",
    "register_codex_session_manifest",
]
