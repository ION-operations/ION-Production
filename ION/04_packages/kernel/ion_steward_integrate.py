"""ION deterministic Steward integration boundary.

V101 introduced the template/action gate for individual worker outputs. V107
adds a queue-consume path so accepted carrier returns can move from
PENDING_STEWARD_INTEGRATION to explicit integrated/rejected state with receipts.
"""
from __future__ import annotations
import argparse, contextlib, fcntl, hashlib, json, os, subprocess, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence
from .ion_template_action_gate import evaluate_template_action_proof

QUEUE_REL = Path("ION/05_context/current/ACTIVE_STEWARD_INTEGRATION_QUEUE.json")
TURN_PACKET_REL = Path("ION/05_context/current/ACTIVE_CARRIER_TURN_PACKET.json")
RECEIPT_ROOT_REL = Path("ION/05_context/current/steward_integrations")
BRIDGE_RECEIPT_REL = Path(
    "ION/05_context/current/cursor_connector/runtime/"
    "prompt_spawn_steward_candidate_active_queue_bridge_receipt.json"
)
SPAWN_PROOFS_REL = Path("ION/05_context/current/spawn_execution_proofs")
AUTHORITY_CONSUMPTION_ROOT_REL = RECEIPT_ROOT_REL / "accepted_state_authority_token_consumptions"
INTEGRATION_LOCK_REL = RECEIPT_ROOT_REL / ".steward_exact_subset.lock"
SUBSET_RESULT_SCHEMA = "ion.steward_exact_run_subset_integration_result.v2"
SUBSET_RECEIPT_SCHEMA_V1 = "ion.steward_exact_run_subset_integration_receipt.v1"
SUBSET_RECEIPT_SCHEMA_V2 = "ion.steward_exact_run_subset_integration_receipt.v2"
AUTHORITY_TOKEN_SCHEMA = "ion.accepted_state_authority_token.v1"
AUTHORITY_CONSUMPTION_SCHEMA = "ion.accepted_state_authority_token_consumption_receipt.v1"
RANK5_FROZEN_RUN_IDS = frozenset(
    {
        "prompt_spawn_2026-07-21T205341+0000_domain_worker_nmixya29",
        "prompt_spawn_2026-07-21T205549+0000_domain_worker_o35x_v5o",
    }
)

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _root(path: str | Path) -> Path:
    p = Path(path).expanduser().resolve()
    return p.parent if p.name == "ION" else p

def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def _read_queue(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_id": "ion.steward_integration_queue.v1", "items": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data.get("items"), list):
            data["items"] = []
        return data
    except Exception:
        return {"schema_id": "ion.steward_integration_queue.v1", "items": [], "findings": ["previous_queue_unreadable"]}

def _safe_slug(value: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:80] or "item"

def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()

def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

TOUCHED_PATHS_RECONCILIATION_SCHEMA = "ion.touched_paths_reconciliation.v1"
TOUCHED_PATHS_RECONCILIATION_SCHEMA_V2 = "ion.touched_paths_reconciliation.v2"
MAX_RECONCILIATION_GATE_FINDINGS = 50
MAX_RECONCILIATION_FULL_LIST_ARTIFACT_BYTES = 1_048_576
DEFAULT_RECONCILIATION_SURFACE_EXCLUDE_PREFIXES: tuple[str, ...] = (
    "ION/05_context/current/cursor_connector/prompt_spawn_runs/",
    "ION/05_context/current/steward_integrations/",
    "ION/05_context/current/spawn_execution_proofs/",
    "ION/05_context/current/task_returns/",
)

def _normalize_repo_rel_path(path: str) -> str:
    text = str(path or "").strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text

def _git_repo_root(shell: Path) -> Path | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=shell,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None
    if completed.returncode != 0:
        return None
    top = completed.stdout.strip()
    return Path(top).resolve() if top else None

def _parse_porcelain_path(line: str) -> str | None:
    if len(line) < 4:
        return None
    path_part = line[3:].strip()
    if path_part.startswith('"') and path_part.endswith('"'):
        path_part = path_part[1:-1]
    if " -> " in path_part:
        path_part = path_part.split(" -> ", 1)[1].strip().strip('"')
    normalized = _normalize_repo_rel_path(path_part)
    return normalized or None

def _git_porcelain_dirty_paths(shell: Path, *, scope_to_shell_cwd: bool = False) -> tuple[set[str], list[str]]:
    """Return repo-relative dirty paths from git status --porcelain=v1."""
    findings: list[str] = []
    git_root = _git_repo_root(shell)
    if git_root is None:
        return set(), ["touched_paths_reconciliation:git_unavailable"]
    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z"],
            cwd=git_root,
            check=False,
            capture_output=True,
            timeout=10,
        )
    except Exception as exc:
        return set(), [f"touched_paths_reconciliation:git_status_failed:{exc!s}"[:200]]
    if completed.returncode != 0:
        return set(), ["touched_paths_reconciliation:git_status_nonzero"]
    raw = completed.stdout
    dirty: set[str] = set()
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        try:
            line = entry.decode("utf-8", errors="replace")
        except Exception:
            continue
        if line.startswith("##"):
            continue
        parsed = _parse_porcelain_path(line)
        if not parsed:
            continue
        try:
            rel = Path(parsed)
            if not rel.is_absolute():
                dirty.add(_normalize_repo_rel_path(parsed))
            else:
                dirty.add(_normalize_repo_rel_path(str(rel.resolve().relative_to(git_root))))
        except ValueError:
            dirty.add(_normalize_repo_rel_path(parsed))
    if scope_to_shell_cwd:
        try:
            shell_rel = shell.resolve().relative_to(git_root)
            prefix = "" if str(shell_rel) == "." else f"{shell_rel.as_posix()}/"
        except ValueError:
            prefix = ""
        if prefix:
            scoped = {path for path in dirty if path == prefix.rstrip("/") or path.startswith(prefix)}
            if not scoped and dirty:
                findings.append("touched_paths_reconciliation:shell_outside_git_dirty_scope")
            dirty = scoped
    return dirty, findings

def _reconciliation_directory_roots(claimed: set[str]) -> set[str]:
    roots: set[str] = set()
    for path in claimed:
        norm = _normalize_repo_rel_path(path)
        if not norm:
            continue
        if "/" in norm:
            roots.add(norm.rsplit("/", 1)[0])
        else:
            roots.add(norm)
    return roots

def _path_in_reconciliation_scope(path: str, roots: set[str]) -> bool:
    norm = _normalize_repo_rel_path(path)
    if not roots:
        return False
    for root in roots:
        if norm == root or norm.startswith(f"{root}/"):
            return True
    return False

def _default_reconciliation_surface_excludes() -> set[str]:
    return {_normalize_repo_rel_path(item) for item in DEFAULT_RECONCILIATION_SURFACE_EXCLUDE_PREFIXES}

def _is_reconciliation_excluded_surface(path: str, excluded: set[str]) -> bool:
    norm = _normalize_repo_rel_path(path)
    for exc in excluded:
        exc_norm = _normalize_repo_rel_path(exc)
        if not exc_norm:
            continue
        if norm == exc_norm:
            return True
        prefix = exc_norm if exc_norm.endswith("/") else f"{exc_norm}/"
        if norm.startswith(prefix):
            return True
    return False

def _scope_dirty_paths_for_reconciliation(
    dirty: set[str],
    *,
    roots: set[str],
    excluded: set[str],
) -> set[str]:
    """Return dirty paths eligible for undeclared-write comparison."""
    surface_excludes = _default_reconciliation_surface_excludes() | excluded
    scoped: set[str] = set()
    for path in dirty:
        if _is_reconciliation_excluded_surface(path, surface_excludes):
            continue
        if roots and _path_in_reconciliation_scope(path, roots):
            scoped.add(path)
    return scoped

def _cap_reconciliation_findings_for_gate(
    reconciliation: Mapping[str, Any],
    *,
    shell: Path,
    artifact_rel: Path | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Bound gate-level findings; optionally persist full undeclared list to a side artifact."""
    payload = dict(reconciliation)
    undeclared_full = list(payload.get("undeclared_writes_full") or payload.get("undeclared_writes") or [])
    unchanged = list(payload.get("claimed_but_unchanged") or [])
    git_findings = [
        item
        for item in (payload.get("findings") or [])
        if isinstance(item, str) and not item.startswith("touched_paths_reconciliation:undeclared_write:")
        and not item.startswith("touched_paths_reconciliation:claimed_but_unchanged:")
    ]
    total_undeclared = len(undeclared_full)
    sample = undeclared_full[:MAX_RECONCILIATION_GATE_FINDINGS]
    truncated = total_undeclared > MAX_RECONCILIATION_GATE_FINDINGS
    artifact_path: str | None = None
    if undeclared_full:
        full_bytes = json.dumps(undeclared_full, separators=(",", ":")).encode("utf-8")
        if len(full_bytes) <= MAX_RECONCILIATION_FULL_LIST_ARTIFACT_BYTES and artifact_rel is not None:
            artifact_abs = shell / artifact_rel
            artifact_abs.parent.mkdir(parents=True, exist_ok=True)
            artifact_abs.write_text(json.dumps(undeclared_full, indent=2) + "\n", encoding="utf-8")
            artifact_path = str(artifact_rel)
    payload["schema_id"] = TOUCHED_PATHS_RECONCILIATION_SCHEMA_V2
    payload["undeclared_writes_total_count"] = total_undeclared
    payload["undeclared_writes"] = sample
    payload["undeclared_writes_truncated"] = truncated
    if artifact_path:
        payload["undeclared_writes_full_artifact_path"] = artifact_path
    payload.pop("undeclared_writes_full", None)
    gate_findings = list(git_findings)
    if truncated:
        gate_findings.append(
            f"touched_paths_reconciliation:undeclared_writes_total:{total_undeclared}:sampled:{len(sample)}"
        )
    for path in sample:
        gate_findings.append(f"touched_paths_reconciliation:undeclared_write:{path}")
    for path in unchanged:
        gate_findings.append(f"touched_paths_reconciliation:claimed_but_unchanged:{path}")
    if len(gate_findings) > MAX_RECONCILIATION_GATE_FINDINGS + len(unchanged) + 1:
        gate_findings = gate_findings[: MAX_RECONCILIATION_GATE_FINDINGS + len(unchanged) + 1]
    payload["findings"] = gate_findings
    return payload, gate_findings

def reconcile_claimed_touched_paths(
    *,
    ion_root: str | Path,
    claimed_paths: Sequence[str],
    exclude_paths: Sequence[str] | None = None,
    reconciliation_roots: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Compare worker-claimed touched_paths to git porcelain dirty paths (fail-open on git miss)."""
    shell = _root(ion_root)
    claimed_raw = [str(item).strip() for item in claimed_paths if str(item).strip()]
    read_only_none = claimed_raw == ["none"] or not claimed_raw
    claimed = set()
    if not read_only_none:
        claimed = {_normalize_repo_rel_path(item) for item in claimed_raw if item.lower() != "none"}
    excluded = {_normalize_repo_rel_path(item) for item in (exclude_paths or []) if str(item).strip()}
    dirty_all, git_findings = _git_porcelain_dirty_paths(shell, scope_to_shell_cwd=False)
    extra_roots = {_normalize_repo_rel_path(item) for item in (reconciliation_roots or []) if str(item).strip()}
    roots = _reconciliation_directory_roots(claimed) | extra_roots
    scoped_dirty = _scope_dirty_paths_for_reconciliation(dirty_all, roots=roots, excluded=excluded)
    scoped_dirty -= excluded
    findings = list(git_findings)
    undeclared: list[str] = []
    unchanged: list[str] = []
    if scoped_dirty or claimed:
        if read_only_none:
            undeclared = sorted(path for path in scoped_dirty if path not in excluded)
        else:
            undeclared = sorted(path for path in scoped_dirty if path not in claimed)
            unchanged = sorted(path for path in claimed if path not in dirty_all)
    for path in undeclared:
        findings.append(f"touched_paths_reconciliation:undeclared_write:{path}")
    for path in unchanged:
        findings.append(f"touched_paths_reconciliation:claimed_but_unchanged:{path}")
    return {
        "schema_id": TOUCHED_PATHS_RECONCILIATION_SCHEMA,
        "claimed_paths": sorted(claimed) if claimed else (["none"] if read_only_none else []),
        "reconciliation_roots": sorted(roots),
        "observed_dirty_paths": sorted(scoped_dirty),
        "observed_dirty_paths_total_in_repo": len(dirty_all),
        "undeclared_writes_full": undeclared,
        "undeclared_writes": undeclared,
        "claimed_but_unchanged": unchanged,
        "findings": findings,
        "reconciliation_ok": not undeclared and not unchanged and not git_findings,
        "git_observed": "git_unavailable" not in "".join(git_findings),
        "default_surface_excludes": sorted(_default_reconciliation_surface_excludes()),
    }

def _gate_with_touched_paths_reconciliation(
    *,
    ion_root: str | Path,
    gate: Mapping[str, Any],
    exclude_paths: Sequence[str] | None = None,
    reconciliation_artifact_rel: Path | None = None,
) -> dict[str, Any]:
    merged = dict(gate)
    if not merged.get("accepted"):
        return merged
    shell = _root(ion_root)
    reconciliation_raw = reconcile_claimed_touched_paths(
        ion_root=ion_root,
        claimed_paths=list(merged.get("touched_paths") or []),
        exclude_paths=exclude_paths,
    )
    reconciliation, gate_reconciliation_findings = _cap_reconciliation_findings_for_gate(
        reconciliation_raw,
        shell=shell,
        artifact_rel=reconciliation_artifact_rel,
    )
    merged["touched_paths_reconciliation"] = reconciliation
    base_findings = [
        item
        for item in (merged.get("findings") or [])
        if isinstance(item, str) and not str(item).startswith("touched_paths_reconciliation:")
    ]
    merged["findings"] = base_findings + gate_reconciliation_findings
    merged["claimed_touched_paths"] = list(merged.get("touched_paths") or [])
    return merged

def _canonical_item_bytes(item: Mapping[str, Any]) -> bytes:
    return json.dumps(item, sort_keys=True, separators=(",", ":")).encode("utf-8")

def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")

def _queue_item_run_id(item: Mapping[str, Any]) -> str:
    return str(item.get("run_id") or item.get("prompt_spawn_run_id") or "").strip()

def _is_sha256(value: str) -> bool:
    normalized = str(value or "").strip().lower()
    return len(normalized) == 64 and all(char in "0123456789abcdef" for char in normalized)

def _canonical_target_set_sha256(integrate_run_ids: Sequence[str]) -> str:
    canonical = json.dumps(sorted(integrate_run_ids), separators=(",", ":"), ensure_ascii=True)
    return _sha256_text(canonical)

def _subset_v2_receipt_name(target_set_sha256: str) -> str:
    return f"steward_integrate_subset_v2_{target_set_sha256[:16]}.json"

def _resolve_under_root(shell: Path, value: str | Path) -> Path | None:
    candidate = Path(value)
    resolved = (candidate if candidate.is_absolute() else shell / candidate).expanduser().resolve()
    try:
        resolved.relative_to(shell)
    except ValueError:
        return None
    return resolved

def _mapping_value(payload: Mapping[str, Any], key: str) -> Any:
    if key in payload:
        return payload.get(key)
    for container_name in ("review", "review_binding", "proof_anchors", "integration_contract"):
        container = payload.get(container_name)
        if isinstance(container, Mapping) and key in container:
            return container.get(key)
    return None

def _normalized_output_map(value: Any) -> dict[str, str] | None:
    if not isinstance(value, Mapping):
        return None
    normalized = {str(key).strip(): str(item).strip().lower() for key, item in value.items()}
    if not normalized or any(not key or not _is_sha256(item) for key, item in normalized.items()):
        return None
    return normalized

def _subset_receipt_name(integrate_run_ids: Sequence[str]) -> str:
    frozen = set(integrate_run_ids)
    if frozen == RANK5_FROZEN_RUN_IDS:
        return "steward_integrate_subset_rank5_20260721.json"
    digest = hashlib.sha256("|".join(sorted(integrate_run_ids)).encode("utf-8")).hexdigest()[:12]
    return f"steward_integrate_subset_{digest}.json"

def _per_run_receipt_name(run_id: str) -> str:
    return f"steward_integrate_{_safe_slug(run_id)}.json"

def _fail_subset(findings: list[str], **extra: Any) -> dict[str, Any]:
    result = {
        "schema_id": SUBSET_RESULT_SCHEMA,
        "accepted": False,
        "processed_count": 0,
        "accepted_count": 0,
        "rejected_count": 0,
        "findings": findings,
        "verdict": "ION_STEWARD_EXACT_RUN_SUBSET_VALIDATION_FAILED",
        "write_performed": False,
        "dry_run": extra.pop("dry_run", False),
        "production_authority": False,
        "live_execution_authority": False,
    }
    result.update(extra)
    return result

def _find_disposition_receipt(shell: Path, expected_sha256: str) -> tuple[Path, dict[str, Any]] | None:
    normalized = str(expected_sha256 or "").strip().lower()
    runs_roots = [
        shell / "ION/05_context/current/cursor_connector/prompt_spawn_runs",
        shell / "ION/05_context/current/claude_connector/claude_prompt_spawn_runs",
        shell / "ION/05_context/current/codex_connector/codex_prompt_spawn_runs",
    ]
    for runs_root in runs_roots:
        if not runs_root.is_dir():
            continue
        for receipt_path in sorted(runs_root.glob("*/steward_candidate_disposition_receipt.json")):
            if _sha256_file(receipt_path) == normalized:
                return receipt_path, json.loads(receipt_path.read_text(encoding="utf-8"))
    return None

def _verify_steward_spawn_proof(
    shell: Path,
    *,
    review_run_id: str,
    review_run_output_sha256: str,
) -> tuple[dict[str, Any] | None, str | None]:
    proofs_root = shell / SPAWN_PROOFS_REL
    if not proofs_root.is_dir():
        return None, "spawn_execution_proofs_missing"
    normalized = review_run_output_sha256.strip().lower()
    matches: list[dict[str, Any]] = []
    for proof_path in sorted(proofs_root.glob("**/*_spawn_execution_proof.candidate.json")):
        try:
            proof = json.loads(proof_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        proof_run_id = str(
            proof.get("run_id")
            or proof.get("prompt_spawn_run_id")
            or proof.get("provider_run_id")
            or ""
        ).strip()
        if proof_run_id != review_run_id:
            continue
        if str(proof.get("task_output_sha256") or "").strip().lower() != normalized:
            continue
        intake = proof.get("intake_result") if isinstance(proof.get("intake_result"), Mapping) else {}
        request = proof.get("request") if isinstance(proof.get("request"), Mapping) else {}
        role_values = {
            str(value).strip()
            for value in (
                proof.get("role_id"),
                proof.get("role"),
                proof.get("requested_role"),
                request.get("role_id"),
                request.get("role"),
                intake.get("role_id"),
            )
            if value is not None
        }
        if "role.steward" not in role_values:
            continue
        if proof.get("intake_attempted") is not True or str(intake.get("status") or "").lower() != "accepted":
            continue
        matches.append(
            {
                "path": str(proof_path.relative_to(shell)),
                "sha256": _sha256_file(proof_path),
                "payload": proof,
            }
        )
    if not matches:
        return None, "exact_role_steward_spawn_intake_proof_not_accepted"
    unique_anchors = {(item["path"], item["sha256"]) for item in matches}
    if len(unique_anchors) != 1:
        return None, "ambiguous_role_steward_spawn_intake_proof"
    return matches[0], None

def _validate_review_receipt_binding(
    *,
    payload: Mapping[str, Any],
    label: str,
    run_ids: Sequence[str],
    output_by_run: Mapping[str, str],
) -> tuple[dict[str, str] | None, list[str]]:
    findings: list[str] = []
    review_run_id = str(_mapping_value(payload, "review_run_id") or "").strip()
    review_output_sha256 = str(_mapping_value(payload, "review_run_output_sha256") or "").strip().lower()
    target_run_ids = _mapping_value(payload, "target_run_ids")
    receipt_output_map = _normalized_output_map(_mapping_value(payload, "output_sha256_by_run_id"))
    if not review_run_id:
        findings.append(f"{label}_review_run_id_missing")
    if not _is_sha256(review_output_sha256):
        findings.append(f"{label}_review_run_output_sha256_invalid")
    if not isinstance(target_run_ids, list) or set(str(item).strip() for item in target_run_ids) != set(run_ids):
        findings.append(f"{label}_target_run_ids_mismatch")
    if receipt_output_map != dict(output_by_run):
        findings.append(f"{label}_output_sha256_by_run_id_mismatch")
    if findings:
        return None, findings
    return {
        "review_run_id": review_run_id,
        "review_run_output_sha256": review_output_sha256,
    }, []

def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)

def _validate_authority_token(
    *,
    shell: Path,
    token_path_value: str | Path,
    token_sha256: str,
    run_ids: Sequence[str],
    target_set_sha256: str,
    output_by_run: Mapping[str, str],
    proof_anchors: Mapping[str, Any],
) -> tuple[dict[str, Any] | None, Path | None, Path | None, list[str]]:
    findings: list[str] = []
    normalized_token_sha256 = str(token_sha256 or "").strip().lower()
    if not _is_sha256(normalized_token_sha256):
        return None, None, None, ["accepted_state_authority_token_sha256_invalid"]
    token_path = _resolve_under_root(shell, token_path_value)
    if token_path is None:
        return None, None, None, ["accepted_state_authority_token_path_outside_active_root"]
    if not token_path.is_file():
        return None, None, None, ["accepted_state_authority_token_missing"]
    if _sha256_file(token_path) != normalized_token_sha256:
        return None, None, None, ["accepted_state_authority_token_sha256_mismatch"]
    try:
        token = json.loads(token_path.read_text(encoding="utf-8"))
    except Exception:
        return None, None, None, ["accepted_state_authority_token_unreadable"]
    if not isinstance(token, Mapping):
        return None, None, None, ["accepted_state_authority_token_not_object"]
    token = dict(token)
    if token.get("schema_id") != AUTHORITY_TOKEN_SCHEMA:
        findings.append("accepted_state_authority_token_schema_mismatch")
    if token.get("single_use") is not True:
        findings.append("accepted_state_authority_token_not_single_use")
    if str(token.get("issuer_role_id") or "").strip() != "role.steward":
        findings.append("accepted_state_authority_token_issuer_role_mismatch")
    token_targets = token.get("target_run_ids")
    if not isinstance(token_targets, list) or set(str(item).strip() for item in token_targets) != set(run_ids):
        findings.append("accepted_state_authority_token_target_run_ids_mismatch")
    if token.get("target_count") != len(run_ids):
        findings.append("accepted_state_authority_token_target_count_mismatch")
    if str(token.get("target_set_sha256") or "").strip().lower() != target_set_sha256:
        findings.append("accepted_state_authority_token_target_set_sha256_mismatch")
    if _normalized_output_map(token.get("output_sha256_by_run_id")) != dict(output_by_run):
        findings.append("accepted_state_authority_token_output_sha256_by_run_id_mismatch")
    constraints = token.get("constraints") if isinstance(token.get("constraints"), Mapping) else {}
    if constraints.get("accepted_state_authority") is not True:
        findings.append("accepted_state_authority_token_constraint_missing")
    if constraints.get("accepted_state_scope") != "exact_queue_targets_only":
        findings.append("accepted_state_authority_token_scope_mismatch")
    for authority_name in (
        "product_authority",
        "production_authority",
        "live_execution_authority",
        "external_execution_authority",
        "secrets_authority",
        "relay_authority",
    ):
        if constraints.get(authority_name) is not False or token.get(authority_name) is True:
            findings.append(f"accepted_state_authority_token_{authority_name}_must_be_false")
    expires_at = _parse_timestamp(token.get("expires_at"))
    if expires_at is None:
        findings.append("accepted_state_authority_token_expiry_invalid")
    elif expires_at <= datetime.now(timezone.utc):
        findings.append("accepted_state_authority_token_expired")
    issued_at = _parse_timestamp(token.get("issued_at"))
    if issued_at is None:
        findings.append("accepted_state_authority_token_issued_at_invalid")
    elif issued_at > datetime.now(timezone.utc):
        findings.append("accepted_state_authority_token_not_yet_valid")
    token_anchors = token.get("proof_anchors") if isinstance(token.get("proof_anchors"), Mapping) else {}
    for anchor_name in (
        "review_run_id",
        "review_run_output_sha256",
        "disposition_receipt_sha256",
        "bridge_receipt_sha256",
        "spawn_proof_path",
        "spawn_proof_sha256",
    ):
        expected = proof_anchors.get(anchor_name)
        actual = token_anchors.get(anchor_name)
        if isinstance(expected, str) and anchor_name.endswith("sha256"):
            actual = str(actual or "").strip().lower()
        if actual != expected:
            findings.append(f"accepted_state_authority_token_{anchor_name}_mismatch")
    binding_path_value = token.get("authority_binding_path")
    binding_sha256 = str(token.get("authority_binding_sha256") or "").strip().lower()
    binding_path = _resolve_under_root(shell, binding_path_value) if isinstance(binding_path_value, str) else None
    if binding_path is None or not binding_path.is_file():
        findings.append("accepted_state_authority_binding_missing")
    elif not _is_sha256(binding_sha256) or _sha256_file(binding_path) != binding_sha256:
        findings.append("accepted_state_authority_binding_sha256_mismatch")
    else:
        try:
            binding = json.loads(binding_path.read_text(encoding="utf-8"))
        except Exception:
            binding = None
        if not isinstance(binding, Mapping):
            findings.append("accepted_state_authority_binding_unreadable")
        else:
            binding_authority = binding.get("authority") if isinstance(binding.get("authority"), Mapping) else {}
            binding_role = str(binding.get("role_id") or binding.get("issuer_role_id") or "").strip()
            binding_grant = binding.get("accepted_state_authority")
            if binding_grant is None:
                binding_grant = binding_authority.get("accepted_state_authority")
            if binding_role != "role.steward" or binding_grant is not True:
                findings.append("accepted_state_authority_binding_role_or_grant_mismatch")
    consumption_rel = AUTHORITY_CONSUMPTION_ROOT_REL / f"{normalized_token_sha256}.json"
    consumption_path = shell / consumption_rel
    if consumption_path.exists():
        findings.append("accepted_state_authority_token_already_consumed")
    if findings:
        return None, token_path, consumption_path, findings
    return token, token_path, consumption_path, []

@contextlib.contextmanager
def _integration_lock(shell: Path):
    lock_path = shell / INTEGRATION_LOCK_REL
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

def _atomic_write_json_batch(entries: Sequence[tuple[Path, Mapping[str, Any]]]) -> None:
    staged: list[tuple[Path, Path]] = []
    originals: dict[Path, bytes | None] = {}
    replaced: list[Path] = []
    try:
        for path, value in entries:
            path.parent.mkdir(parents=True, exist_ok=True)
            originals[path] = path.read_bytes() if path.exists() else None
            descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
            temporary_path = Path(temporary_name)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(_canonical_json_bytes(value))
                handle.flush()
                os.fsync(handle.fileno())
            staged.append((temporary_path, path))
        for temporary_path, path in staged:
            os.replace(temporary_path, path)
            replaced.append(path)
        for directory in {path.parent for _, path in staged}:
            descriptor = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
    except Exception:
        for path in reversed(replaced):
            original = originals[path]
            if original is None:
                path.unlink(missing_ok=True)
                continue
            descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.rollback.", dir=path.parent)
            temporary_path = Path(temporary_name)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(original)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, path)
        raise
    finally:
        for temporary_path, _path in staged:
            temporary_path.unlink(missing_ok=True)

def _integrate_queue_item(
    *,
    shell: Path,
    item: dict[str, Any],
    ordinal: int,
    created_at: str,
) -> tuple[dict[str, Any], dict[str, Any], str, bool]:
    task_output_path = item.get("task_output_path")
    task_path = shell / task_output_path if isinstance(task_output_path, str) else None
    receipt_id = _queue_receipt_id(item, ordinal)
    receipt_rel = RECEIPT_ROOT_REL / _per_run_receipt_name(str(item.get("run_id") or receipt_id))

    if not task_path or not task_path.exists():
        gate = {
            "schema_id": "ion.template_action_gate_result.v1",
            "accepted": False,
            "findings": ["missing_task_output_for_steward_integration"],
            "integration_decision": "REJECT_RETURN_AND_RERUN_OR_REPAIR",
            "production_authority": False,
            "live_external_execution_authority": False,
        }
        worker_output = ""
    else:
        worker_output = task_path.read_text(encoding="utf-8", errors="replace")
        gate = evaluate_template_action_proof(worker_output=worker_output)

    accepted = bool(gate.get("accepted"))
    decision = "INTEGRATED_AS_ACCEPTED_STATE_DELTA" if accepted else "REJECTED_BY_TEMPLATE_ACTION_GATE"
    receipt = {
        "schema_id": "ion.steward_queue_integration_receipt.v1",
        "receipt_id": receipt_id,
        "created_at": created_at,
        "source": "active_steward_integration_queue_exact_run_subset",
        "accepted": accepted,
        "decision": decision,
        "role": item.get("role"),
        "index": item.get("index"),
        "run_id": item.get("run_id"),
        "task_output_path": task_output_path,
        "task_output_sha256": hashlib.sha256(worker_output.encode("utf-8")).hexdigest() if worker_output else None,
        "gate": gate,
        "worker_output_preview": worker_output[:1600],
        "production_authority": False,
        "external_execution_authority": False,
    }
    mutable = dict(item)
    mutable["status"] = "STEWARD_INTEGRATED" if accepted else "STEWARD_INTEGRATION_REJECTED"
    mutable["steward_integrated_at"] = created_at
    mutable["steward_receipt_id"] = receipt_id
    mutable["steward_receipt_path"] = str(receipt_rel)
    mutable["steward_decision"] = decision
    mutable["steward_gate_findings"] = list(gate.get("findings", []))
    mutable["accepted"] = accepted
    return mutable, receipt, str(receipt_rel), accepted

def steward_integrate_exact_run_subset(
    *,
    ion_root: str | Path,
    integrate_run_ids: Sequence[str],
    output_sha256: Sequence[str],
    disposition_receipt_sha256: str,
    bridge_receipt_sha256: str,
    steward_return_sha256: str | None = None,
    bridge_receipt_path: str | None = None,
    accepted_state_authority_token_path: str | Path | None = None,
    accepted_state_authority_token_sha256: str | None = None,
    write: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Fail-closed subset steward integration for explicit run_id targets."""
    shell = _root(ion_root)
    created_at = _now()
    run_ids = [str(value).strip() for value in integrate_run_ids]
    output_hashes = [str(value).strip().lower() for value in output_sha256]
    disposition_hash = str(disposition_receipt_sha256 or "").strip().lower()
    bridge_hash = str(bridge_receipt_sha256 or "").strip().lower()
    deprecated_steward_hash = str(steward_return_sha256 or "").strip().lower()

    if dry_run and write:
        return _fail_subset(["dry_run_and_write_mutually_exclusive"], dry_run=True)
    if not run_ids:
        return _fail_subset(["integrate_run_ids_must_be_nonempty"], target_run_ids=run_ids, dry_run=dry_run)
    if len(output_hashes) != len(run_ids):
        return _fail_subset(["output_sha256_count_must_equal_target_count"], target_run_ids=run_ids, dry_run=dry_run)
    if len(set(run_ids)) != len(run_ids):
        return _fail_subset(["duplicate_integrate_run_id"], target_run_ids=run_ids, dry_run=dry_run)
    if any(not run_id for run_id in run_ids):
        return _fail_subset(["empty_integrate_run_id"], target_run_ids=run_ids, dry_run=dry_run)
    if any(not _is_sha256(value) for value in output_hashes):
        return _fail_subset(["invalid_output_sha256"], target_run_ids=run_ids, dry_run=dry_run)

    output_by_run = dict(zip(run_ids, output_hashes, strict=True))
    target_count = len(run_ids)
    target_set_sha256 = _canonical_target_set_sha256(run_ids)
    bridge_path = _resolve_under_root(shell, bridge_receipt_path or BRIDGE_RECEIPT_REL)
    if bridge_path is None:
        return _fail_subset(["bridge_receipt_path_outside_active_root"], target_run_ids=run_ids, dry_run=dry_run)
    if not bridge_path.exists():
        return _fail_subset(["bridge_receipt_missing"], target_run_ids=run_ids, dry_run=dry_run)
    live_bridge_hash = _sha256_file(bridge_path)
    if live_bridge_hash != bridge_hash:
        return _fail_subset(
            ["bridge_receipt_sha256_mismatch"],
            target_run_ids=run_ids,
            live_bridge_receipt_sha256=live_bridge_hash,
            dry_run=dry_run,
        )
    try:
        bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
    except Exception:
        return _fail_subset(["bridge_receipt_unreadable"], target_run_ids=run_ids, dry_run=dry_run)
    bridge_disposition = str(bridge.get("disposition_receipt_sha256") or "").strip().lower()
    if bridge_disposition != disposition_hash:
        return _fail_subset(
            ["disposition_receipt_sha256_bridge_drift"],
            target_run_ids=run_ids,
            dry_run=dry_run,
        )
    disposition = _find_disposition_receipt(shell, disposition_hash)
    if disposition is None:
        return _fail_subset(["disposition_receipt_missing"], target_run_ids=run_ids, dry_run=dry_run)
    disposition_path, disposition_payload = disposition
    if _sha256_file(disposition_path) != disposition_hash:
        return _fail_subset(["disposition_receipt_sha256_mismatch"], target_run_ids=run_ids, dry_run=dry_run)

    disposition_review, disposition_findings = _validate_review_receipt_binding(
        payload=disposition_payload,
        label="disposition_receipt",
        run_ids=run_ids,
        output_by_run=output_by_run,
    )
    bridge_review, bridge_findings = _validate_review_receipt_binding(
        payload=bridge,
        label="bridge_receipt",
        run_ids=run_ids,
        output_by_run=output_by_run,
    )
    if disposition_findings or bridge_findings:
        return _fail_subset(
            disposition_findings + bridge_findings,
            target_run_ids=run_ids,
            target_count=target_count,
            target_set_sha256=target_set_sha256,
            dry_run=dry_run,
        )
    assert disposition_review is not None and bridge_review is not None
    if disposition_review != bridge_review:
        return _fail_subset(
            ["disposition_bridge_review_identity_mismatch"],
            target_run_ids=run_ids,
            target_count=target_count,
            target_set_sha256=target_set_sha256,
            dry_run=dry_run,
        )
    review_run_id = disposition_review["review_run_id"]
    review_run_output_sha256 = disposition_review["review_run_output_sha256"]
    if deprecated_steward_hash and deprecated_steward_hash != review_run_output_sha256:
        return _fail_subset(
            ["deprecated_steward_return_sha256_review_output_mismatch"],
            target_run_ids=run_ids,
            dry_run=dry_run,
        )
    spawn_proof, spawn_finding = _verify_steward_spawn_proof(
        shell,
        review_run_id=review_run_id,
        review_run_output_sha256=review_run_output_sha256,
    )
    if spawn_proof is None:
        return _fail_subset([spawn_finding or "steward_spawn_proof_not_accepted"], target_run_ids=run_ids, dry_run=dry_run)

    queue_path = shell / QUEUE_REL
    if not queue_path.is_file():
        return _fail_subset(["steward_integration_queue_missing"], target_run_ids=run_ids, dry_run=dry_run)
    try:
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
    except Exception:
        return _fail_subset(["steward_integration_queue_unreadable"], target_run_ids=run_ids, dry_run=dry_run)
    if not isinstance(queue, Mapping) or not isinstance(queue.get("items"), list):
        return _fail_subset(["steward_integration_queue_schema_invalid"], target_run_ids=run_ids, dry_run=dry_run)
    queue = dict(queue)
    queue_source_sha256 = _sha256_file(queue_path)
    items = [dict(item) for item in queue.get("items", []) if isinstance(item, Mapping)]
    non_target_snapshots = {
        index: _canonical_item_bytes(item)
        for index, item in enumerate(items)
        if _queue_item_run_id(item) not in set(run_ids)
    }

    target_indexes: dict[str, int] = {}
    for index, item in enumerate(items):
        run_id = _queue_item_run_id(item)
        if run_id in set(run_ids):
            if run_id in target_indexes:
                return _fail_subset(["duplicate_target_run_id_in_queue"], target_run_ids=run_ids, dry_run=dry_run)
            target_indexes[run_id] = index
    missing_targets = [run_id for run_id in run_ids if run_id not in target_indexes]
    if missing_targets:
        return _fail_subset(
            ["missing_target_run_id_in_queue"],
            target_run_ids=run_ids,
            missing_run_ids=missing_targets,
            dry_run=dry_run,
        )

    target_items: dict[str, dict[str, Any]] = {}
    for run_id in run_ids:
        item = items[target_indexes[run_id]]
        expected_hash = output_by_run[run_id]
        actual_hash = str(item.get("task_output_sha256") or "").strip().lower()
        if actual_hash != expected_hash:
            return _fail_subset(
                ["target_task_output_sha256_mismatch"],
                target_run_ids=run_ids,
                run_id=run_id,
                expected_sha256=expected_hash,
                actual_sha256=actual_hash,
                dry_run=dry_run,
            )
        task_output_path = item.get("task_output_path")
        task_path = _resolve_under_root(shell, task_output_path) if isinstance(task_output_path, str) else None
        if not task_path or not task_path.exists():
            return _fail_subset(["target_task_output_missing"], target_run_ids=run_ids, run_id=run_id, dry_run=dry_run)
        if _sha256_file(task_path) != expected_hash:
            return _fail_subset(
                ["target_task_output_file_sha256_mismatch"],
                target_run_ids=run_ids,
                run_id=run_id,
                dry_run=dry_run,
            )
        target_items[run_id] = item

    legacy_subset_receipt_rel = RECEIPT_ROOT_REL / _subset_receipt_name(run_ids)
    subset_receipt_rel = RECEIPT_ROOT_REL / _subset_v2_receipt_name(target_set_sha256)
    try:
        existing_legacy_subset = _read_json(shell / legacy_subset_receipt_rel)
        existing_subset = _read_json(shell / subset_receipt_rel)
    except Exception:
        return _fail_subset(["existing_subset_receipt_unreadable"], target_run_ids=run_ids, dry_run=dry_run)
    all_integrated = all(item.get("status") == "STEWARD_INTEGRATED" for item in target_items.values())
    any_integrated = any(item.get("status") == "STEWARD_INTEGRATED" for item in target_items.values())

    proof_anchors = {
        "disposition_receipt_sha256": disposition_hash,
        "bridge_receipt_sha256": bridge_hash,
        "review_run_id": review_run_id,
        "review_run_output_sha256": review_run_output_sha256,
        "spawn_proof_path": spawn_proof["path"],
        "spawn_proof_sha256": spawn_proof["sha256"],
        "steward_return_sha256": deprecated_steward_hash or None,
        "output_sha256_by_run_id": output_by_run,
    }
    legacy_proof_anchors = {
        "disposition_receipt_sha256": disposition_hash,
        "bridge_receipt_sha256": bridge_hash,
        "steward_return_sha256": deprecated_steward_hash,
        "output_sha256_by_run_id": output_by_run,
    }

    if existing_subset and isinstance(existing_subset, Mapping):
        prior_targets = existing_subset.get("target_run_ids")
        if isinstance(prior_targets, list) and set(prior_targets) != set(run_ids):
            return _fail_subset(
                ["idempotent_subset_receipt_target_set_mismatch"],
                target_run_ids=run_ids,
                dry_run=dry_run,
            )
        prior_anchors = existing_subset.get("proof_anchors")
        if isinstance(prior_anchors, Mapping) and dict(prior_anchors) != proof_anchors:
            return _fail_subset(["idempotent_subset_receipt_anchor_drift"], target_run_ids=run_ids, dry_run=dry_run)

    if all_integrated and existing_subset:
        pending_count = sum(1 for item in items if item.get("status") == "PENDING_STEWARD_INTEGRATION")
        return {
            "schema_id": SUBSET_RESULT_SCHEMA,
            "accepted": True,
            "processed_count": 0,
            "accepted_count": target_count,
            "rejected_count": 0,
            "pending_count": pending_count,
            "idempotent_replay": True,
            "target_run_ids": run_ids,
            "target_count": target_count,
            "target_set_sha256": target_set_sha256,
            "proof_anchors": proof_anchors,
            "subset_receipt_path": str(subset_receipt_rel),
            "queue_path": str(QUEUE_REL),
            "verdict": "ION_STEWARD_EXACT_RUN_SUBSET_ALREADY_INTEGRATED",
            "write_performed": False,
            "dry_run": dry_run,
            "production_authority": False,
            "live_execution_authority": False,
        }
    if all_integrated and existing_legacy_subset:
        prior_targets = existing_legacy_subset.get("target_run_ids")
        prior_anchors = existing_legacy_subset.get("proof_anchors")
        if (
            isinstance(prior_targets, list)
            and set(prior_targets) == set(run_ids)
            and isinstance(prior_anchors, Mapping)
            and dict(prior_anchors) == legacy_proof_anchors
        ):
            pending_count = sum(1 for item in items if item.get("status") == "PENDING_STEWARD_INTEGRATION")
            return {
                "schema_id": "ion.steward_exact_run_subset_integration_result.v1",
                "accepted": True,
                "processed_count": 0,
                "accepted_count": target_count,
                "rejected_count": 0,
                "pending_count": pending_count,
                "idempotent_replay": True,
                "target_run_ids": run_ids,
                "target_count": target_count,
                "target_set_sha256": target_set_sha256,
                "proof_anchors": legacy_proof_anchors,
                "subset_receipt_path": str(legacy_subset_receipt_rel),
                "queue_path": str(QUEUE_REL),
                "verdict": "ION_STEWARD_EXACT_RUN_SUBSET_ALREADY_INTEGRATED",
                "write_performed": False,
                "dry_run": dry_run,
                "production_authority": False,
                "live_execution_authority": False,
            }
    if all_integrated:
        return _fail_subset(["integrated_targets_missing_matching_immutable_receipt"], target_run_ids=run_ids, dry_run=dry_run)

    if any_integrated and not all_integrated:
        return _fail_subset(["partial_target_integration_state"], target_run_ids=run_ids, dry_run=dry_run)

    for run_id, item in target_items.items():
        if item.get("status") != "PENDING_STEWARD_INTEGRATION":
            return _fail_subset(
                ["target_status_not_pending"],
                target_run_ids=run_ids,
                run_id=run_id,
                status=item.get("status"),
                dry_run=dry_run,
            )

    receipts: list[dict[str, Any]] = []
    accepted_count = 0
    rejected_count = 0
    updated_items = [dict(item) for item in items]

    for ordinal, run_id in enumerate(run_ids, start=1):
        index = target_indexes[run_id]
        integrated_item, receipt, receipt_rel, accepted = _integrate_queue_item(
            shell=shell,
            item=updated_items[index],
            ordinal=index + 1,
            created_at=created_at,
        )
        updated_items[index] = integrated_item
        receipts.append({"receipt": receipt, "receipt_path": receipt_rel, "run_id": run_id})
        if accepted:
            accepted_count += 1
        else:
            rejected_count += 1

    if accepted_count != target_count:
        return _fail_subset(
            ["accepted_count_not_equal_target_count"],
            target_run_ids=run_ids,
            target_count=target_count,
            accepted_count=accepted_count,
            rejected_count=rejected_count,
            dry_run=dry_run,
        )

    for index, snapshot in non_target_snapshots.items():
        if _canonical_item_bytes(updated_items[index]) != snapshot:
            return _fail_subset(["non_target_queue_item_mutated"], target_run_ids=run_ids, dry_run=dry_run)

    pending_count = sum(1 for item in updated_items if item.get("status") == "PENDING_STEWARD_INTEGRATION")
    authority_token: dict[str, Any] | None = None
    authority_token_path: Path | None = None
    consumption_path: Path | None = None
    token_args_supplied = accepted_state_authority_token_path is not None or accepted_state_authority_token_sha256 is not None
    if write and not token_args_supplied:
        return _fail_subset(
            ["accepted_state_authority_token_required_for_new_write"],
            target_run_ids=run_ids,
            target_count=target_count,
            target_set_sha256=target_set_sha256,
            dry_run=dry_run,
        )
    if token_args_supplied:
        if accepted_state_authority_token_path is None or accepted_state_authority_token_sha256 is None:
            return _fail_subset(["accepted_state_authority_token_path_and_sha256_required_together"], target_run_ids=run_ids, dry_run=dry_run)
        authority_token, authority_token_path, consumption_path, token_findings = _validate_authority_token(
            shell=shell,
            token_path_value=accepted_state_authority_token_path,
            token_sha256=accepted_state_authority_token_sha256,
            run_ids=run_ids,
            target_set_sha256=target_set_sha256,
            output_by_run=output_by_run,
            proof_anchors=proof_anchors,
        )
        if token_findings:
            return _fail_subset(
                token_findings,
                target_run_ids=run_ids,
                target_count=target_count,
                target_set_sha256=target_set_sha256,
                dry_run=dry_run,
            )
    token_hash = str(accepted_state_authority_token_sha256 or "").strip().lower() or None
    transaction_id = _sha256_text(
        json.dumps(
            {
                "target_set_sha256": target_set_sha256,
                "disposition_receipt_sha256": disposition_hash,
                "bridge_receipt_sha256": bridge_hash,
                "review_run_id": review_run_id,
                "review_run_output_sha256": review_run_output_sha256,
                "authority_token_sha256": token_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    for entry in receipts:
        run_id = entry["run_id"]
        receipt_rel = RECEIPT_ROOT_REL / (
            f"steward_integrate_v2_{_safe_slug(run_id)}_{transaction_id[:16]}.json"
        )
        entry["receipt_path"] = str(receipt_rel)
        entry["receipt"]["schema_id"] = "ion.steward_queue_integration_receipt.v2"
        entry["receipt"]["receipt_id"] = receipt_rel.stem
        entry["receipt"]["transaction_id"] = transaction_id
        entry["receipt"]["target_set_sha256"] = target_set_sha256
        entry["receipt"]["proof_anchors"] = proof_anchors
        entry["receipt"]["accepted_state_authority_token_sha256"] = token_hash
        index = target_indexes[run_id]
        updated_items[index]["steward_receipt_id"] = receipt_rel.stem
        updated_items[index]["steward_receipt_path"] = str(receipt_rel)
        updated_items[index]["steward_integration_transaction_id"] = transaction_id
        updated_items[index]["accepted_state_authority_token_sha256"] = token_hash
    subset_receipt = {
        "schema_id": SUBSET_RECEIPT_SCHEMA_V2,
        "created_at": created_at,
        "transaction_id": transaction_id,
        "target_run_ids": run_ids,
        "target_count": target_count,
        "target_set_sha256": target_set_sha256,
        "proof_anchors": proof_anchors,
        "accepted_state_authority_token_path": (
            str(authority_token_path.relative_to(shell)) if authority_token_path is not None else None
        ),
        "accepted_state_authority_token_sha256": token_hash,
        "processed_count": target_count,
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "per_run_receipt_paths": [entry["receipt_path"] for entry in receipts],
        "bridge_receipt_path": str(bridge_path.relative_to(shell)),
        "disposition_receipt_path": str(disposition_path.relative_to(shell)),
        "steward_return_sha256": deprecated_steward_hash or None,
        "product_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "external_execution_authority": False,
        "secrets_authority": False,
        "relay_authority": False,
    }

    if write and not dry_run:
        assert authority_token is not None
        assert authority_token_path is not None
        assert consumption_path is not None
        consumption_receipt = {
            "schema_id": AUTHORITY_CONSUMPTION_SCHEMA,
            "created_at": created_at,
            "transaction_id": transaction_id,
            "token_id": authority_token.get("token_id"),
            "accepted_state_authority_token_path": str(authority_token_path.relative_to(shell)),
            "accepted_state_authority_token_sha256": token_hash,
            "authority_binding_path": authority_token.get("authority_binding_path"),
            "authority_binding_sha256": authority_token.get("authority_binding_sha256"),
            "issuer_role_id": "role.steward",
            "single_use": True,
            "consumed": True,
            "target_run_ids": run_ids,
            "target_count": target_count,
            "target_set_sha256": target_set_sha256,
            "proof_anchors": proof_anchors,
            "subset_receipt_path": str(subset_receipt_rel),
            "product_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "external_execution_authority": False,
            "secrets_authority": False,
            "relay_authority": False,
        }
        queue["items"] = updated_items
        queue["last_updated_at"] = created_at
        queue["last_queue_integration_at"] = created_at
        queue["last_steward_integration_transaction_id"] = transaction_id
        queue["steward_integration_counts"] = {
            "schema_id": "ion.steward_integration_counts.v2",
            "accepted": sum(1 for item in updated_items if item.get("status") == "STEWARD_INTEGRATED"),
            "rejected": sum(1 for item in updated_items if item.get("status") == "STEWARD_INTEGRATION_REJECTED"),
            "pending": pending_count,
            "skipped_existing": len(items) - target_count,
            "subset_integration": True,
            "target_count": target_count,
            "target_set_sha256": target_set_sha256,
        }
        queue["last_receipt_path"] = str(subset_receipt_rel)
        immutable_entries = [
            *((shell / entry["receipt_path"], entry["receipt"]) for entry in receipts),
            (shell / subset_receipt_rel, subset_receipt),
            (consumption_path, consumption_receipt),
        ]
        with _integration_lock(shell):
            if _sha256_file(queue_path) != queue_source_sha256:
                return _fail_subset(["steward_integration_queue_changed_before_commit"], target_run_ids=run_ids, dry_run=dry_run)
            if _sha256_file(bridge_path) != bridge_hash or _sha256_file(disposition_path) != disposition_hash:
                return _fail_subset(["review_receipt_anchor_changed_before_commit"], target_run_ids=run_ids, dry_run=dry_run)
            spawn_proof_path = shell / str(spawn_proof["path"])
            if _sha256_file(spawn_proof_path) != spawn_proof["sha256"]:
                return _fail_subset(["spawn_proof_anchor_changed_before_commit"], target_run_ids=run_ids, dry_run=dry_run)
            if _sha256_file(authority_token_path) != token_hash:
                return _fail_subset(["accepted_state_authority_token_changed_before_commit"], target_run_ids=run_ids, dry_run=dry_run)
            if consumption_path.exists():
                return _fail_subset(["accepted_state_authority_token_already_consumed"], target_run_ids=run_ids, dry_run=dry_run)
            if any(path.exists() for path, _value in immutable_entries):
                return _fail_subset(["immutable_v2_integration_receipt_already_exists"], target_run_ids=run_ids, dry_run=dry_run)
            try:
                _atomic_write_json_batch([*immutable_entries, (queue_path, queue)])
            except Exception as exc:
                return _fail_subset(
                    ["atomic_steward_integration_commit_failed"],
                    target_run_ids=run_ids,
                    error_class=type(exc).__name__,
                    dry_run=dry_run,
                )

    return {
        "schema_id": SUBSET_RESULT_SCHEMA,
        "accepted": True,
        "processed_count": target_count,
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "pending_count": pending_count,
        "idempotent_replay": False,
        "target_run_ids": run_ids,
        "target_count": target_count,
        "target_set_sha256": target_set_sha256,
        "proof_anchors": proof_anchors,
        "accepted_state_authority_token_sha256": token_hash,
        "receipts": receipts,
        "subset_receipt_path": str(subset_receipt_rel),
        "queue_path": str(QUEUE_REL),
        "verdict": "ION_STEWARD_EXACT_RUN_SUBSET_INTEGRATION_COMPLETE",
        "write_performed": bool(write and not dry_run),
        "dry_run": dry_run,
        "product_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "external_execution_authority": False,
        "secrets_authority": False,
        "relay_authority": False,
    }

def steward_integrate_return(*, ion_root: str | Path, worker_output: str, source: str = "local_autonomous_loop", cycle_id: str = "manual", step_index: int = 1, write: bool = False) -> dict[str, Any]:
    shell = _root(ion_root)
    created_at = _now()
    receipt_id = f"{cycle_id}_step_{step_index:02d}_steward_integration"
    receipt_rel = RECEIPT_ROOT_REL / f"{receipt_id}.json"
    gate = _gate_with_touched_paths_reconciliation(
        ion_root=shell,
        gate=evaluate_template_action_proof(worker_output=worker_output),
        exclude_paths=[str(receipt_rel), str(QUEUE_REL)],
        reconciliation_artifact_rel=RECEIPT_ROOT_REL / f"{receipt_id}_undeclared_writes.json",
    )
    accepted = bool(gate["accepted"])
    receipt = {
        "schema_id": "ion.steward_integration_receipt.v1",
        "receipt_id": receipt_id,
        "created_at": created_at,
        "source": source,
        "cycle_id": cycle_id,
        "step_index": step_index,
        "accepted": accepted,
        "decision": "READ_ONLY_TEMPLATE_ACTION_GATE_ACCEPTED" if accepted else "REJECTED_BY_TEMPLATE_ACTION_GATE",
        "gate": gate,
        "worker_output_sha256": hashlib.sha256(worker_output.encode("utf-8")).hexdigest(),
        "worker_output_preview": worker_output[:1600],
        "production_authority": False,
        "external_execution_authority": False,
    }
    queue_path = shell / QUEUE_REL
    queue = _read_queue(queue_path)
    queue["last_updated_at"] = created_at
    queue["last_receipt_path"] = str(receipt_rel)
    queue["items"].append({
        "receipt_id": receipt_id,
        "created_at": created_at,
        "cycle_id": cycle_id,
        "step_index": step_index,
        "accepted": accepted,
        "decision": receipt["decision"],
        "receipt_path": str(receipt_rel),
        "template_id": gate.get("template_id"),
        "action_id": gate.get("action_id"),
        "touched_paths": gate.get("touched_paths", []),
    })
    if write:
        _write_json(shell / receipt_rel, receipt)
        _write_json(queue_path, queue)
    return {"schema_id": "ion.steward_integration_result.v1", "accepted": accepted, "receipt": receipt, "receipt_path": str(receipt_rel), "queue_path": str(QUEUE_REL), "write_performed": write}

def steward_integrate_return_file(*, ion_root: str | Path, worker_output_path: str | Path, source: str = "local_autonomous_loop", cycle_id: str = "manual", step_index: int = 1, write: bool = False) -> dict[str, Any]:
    return steward_integrate_return(ion_root=ion_root, worker_output=Path(worker_output_path).read_text(encoding="utf-8", errors="replace"), source=source, cycle_id=cycle_id, step_index=step_index, write=write)

def _queue_receipt_id(item: Mapping[str, Any], ordinal: int) -> str:
    role = _safe_slug(str(item.get("role", "unknown")))
    index = int(item.get("index", ordinal))
    source = str(item.get("task_output_sha256") or item.get("task_output_path") or item.get("created_at") or ordinal)
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]
    return f"queue_{index:02d}_{role}_{digest}_steward_integration"

def _update_turn_packet_after_queue_integration(shell: Path, *, accepted_count: int, rejected_count: int, pending_count: int) -> None:
    turn = _read_json(shell / TURN_PACKET_REL)
    if turn is None:
        return
    turn["steward_integration_state"] = {
        "schema_id": "ion.steward_integration_state.v1",
        "status": "STEWARD_INTEGRATION_COMPLETE" if pending_count == 0 and rejected_count == 0 else "STEWARD_INTEGRATION_REVIEW_REQUIRED",
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "pending_count": pending_count,
        "required_action": "Continue or queue new work after Steward integration is complete." if pending_count == 0 and rejected_count == 0 else "Review rejected or pending Steward integration items.",
    }
    intake = turn.get("return_intake_state")
    if isinstance(intake, dict):
        intake["steward_queue_count"] = pending_count
        if pending_count == 0 and rejected_count == 0:
            intake["status"] = "STEWARD_INTEGRATION_COMPLETE"
            intake["required_action"] = "Continue or queue new work; accepted returns have Steward integration receipts."
        turn["return_intake_state"] = intake
    _write_json(shell / TURN_PACKET_REL, turn)

def steward_integrate_pending_queue(*, ion_root: str | Path, write: bool = False) -> dict[str, Any]:
    """Consume pending Steward queue items with template/action receipts."""
    shell = _root(ion_root)
    created_at = _now()
    queue_path = shell / QUEUE_REL
    queue = _read_queue(queue_path)
    items = [item for item in queue.get("items", []) if isinstance(item, Mapping)]

    updated_items: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    accepted_count = 0
    rejected_count = 0
    skipped_count = 0

    for ordinal, item in enumerate(items, start=1):
        mutable = dict(item)
        if mutable.get("status") != "PENDING_STEWARD_INTEGRATION":
            updated_items.append(mutable)
            skipped_count += 1
            continue

        task_output_path = mutable.get("task_output_path")
        task_path = shell / task_output_path if isinstance(task_output_path, str) else None
        receipt_id = _queue_receipt_id(mutable, ordinal)
        receipt_rel = RECEIPT_ROOT_REL / f"{receipt_id}.json"

        if not task_path or not task_path.exists():
            gate = {
                "schema_id": "ion.template_action_gate_result.v1",
                "accepted": False,
                "findings": ["missing_task_output_for_steward_integration"],
                "integration_decision": "REJECT_RETURN_AND_RERUN_OR_REPAIR",
                "production_authority": False,
                "live_external_execution_authority": False,
            }
            worker_output = ""
        else:
            worker_output = task_path.read_text(encoding="utf-8", errors="replace")
            gate = _gate_with_touched_paths_reconciliation(
                ion_root=shell,
                gate=evaluate_template_action_proof(worker_output=worker_output),
                exclude_paths=[str(receipt_rel), str(QUEUE_REL)],
                reconciliation_artifact_rel=RECEIPT_ROOT_REL / f"{receipt_id}_undeclared_writes.json",
            )

        accepted = bool(gate.get("accepted"))
        decision = "INTEGRATED_AS_ACCEPTED_STATE_DELTA" if accepted else "REJECTED_BY_TEMPLATE_ACTION_GATE"
        receipt = {
            "schema_id": "ion.steward_queue_integration_receipt.v1",
            "receipt_id": receipt_id,
            "created_at": created_at,
            "source": "active_steward_integration_queue",
            "accepted": accepted,
            "decision": decision,
            "role": mutable.get("role"),
            "index": mutable.get("index"),
            "task_output_path": task_output_path,
            "task_output_sha256": hashlib.sha256(worker_output.encode("utf-8")).hexdigest() if worker_output else None,
            "gate": gate,
            "worker_output_preview": worker_output[:1600],
            "production_authority": False,
            "external_execution_authority": False,
        }
        receipts.append({"receipt": receipt, "receipt_path": str(receipt_rel)})

        mutable["status"] = "STEWARD_INTEGRATED" if accepted else "STEWARD_INTEGRATION_REJECTED"
        mutable["steward_integrated_at"] = created_at
        mutable["steward_receipt_id"] = receipt_id
        mutable["steward_receipt_path"] = str(receipt_rel)
        mutable["steward_decision"] = decision
        mutable["steward_gate_findings"] = list(gate.get("findings", []))
        mutable["accepted"] = accepted
        updated_items.append(mutable)
        if accepted:
            accepted_count += 1
        else:
            rejected_count += 1

    pending_count = sum(1 for item in updated_items if item.get("status") == "PENDING_STEWARD_INTEGRATION")
    queue["items"] = updated_items
    queue["last_updated_at"] = created_at
    queue["last_queue_integration_at"] = created_at
    queue["steward_integration_counts"] = {
        "schema_id": "ion.steward_integration_counts.v1",
        "accepted": accepted_count,
        "rejected": rejected_count,
        "pending": pending_count,
        "skipped_existing": skipped_count,
    }
    if receipts:
        queue["last_receipt_path"] = receipts[-1]["receipt_path"]

    if write:
        for item in receipts:
            _write_json(shell / item["receipt_path"], item["receipt"])
        _write_json(queue_path, queue)
        _update_turn_packet_after_queue_integration(
            shell,
            accepted_count=accepted_count,
            rejected_count=rejected_count,
            pending_count=pending_count,
        )

    result = {
        "schema_id": "ion.steward_queue_integration_result.v1",
        "accepted": pending_count == 0 and rejected_count == 0,
        "processed_count": accepted_count + rejected_count,
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "pending_count": pending_count,
        "skipped_existing_count": skipped_count,
        "receipts": receipts,
        "queue_path": str(QUEUE_REL),
        "write_performed": write,
        "production_authority": False,
        "live_execution_authority": False,
    }
    result["verdict"] = "ION_STEWARD_QUEUE_INTEGRATION_COMPLETE" if result["accepted"] else "ION_STEWARD_QUEUE_INTEGRATION_REVIEW_REQUIRED"
    return result

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Integrate an accepted ION worker return through Steward.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--worker-output", default=None)
    parser.add_argument("--cycle-id", default="manual")
    parser.add_argument("--step-index", type=int, default=1)
    parser.add_argument("--integrate-queue", action="store_true")
    parser.add_argument("--integrate-run-ids", action="append", default=None)
    parser.add_argument("--output-sha256", action="append", default=None)
    parser.add_argument("--disposition-receipt-sha256", default=None)
    parser.add_argument("--bridge-receipt-sha256", default=None)
    parser.add_argument("--steward-return-sha256", default=None)
    parser.add_argument("--bridge-receipt-path", default=None)
    parser.add_argument("--accepted-state-authority-token-path", default=None)
    parser.add_argument("--accepted-state-authority-token-sha256", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    subset_requested = any(
        value is not None
        for value in (
            args.integrate_run_ids,
            args.output_sha256,
            args.disposition_receipt_sha256,
            args.bridge_receipt_sha256,
            args.steward_return_sha256,
            args.accepted_state_authority_token_path,
            args.accepted_state_authority_token_sha256,
        )
    )
    if subset_requested:
        missing = [
            name
            for name, value in (
                ("--integrate-run-ids", args.integrate_run_ids),
                ("--output-sha256", args.output_sha256),
                ("--disposition-receipt-sha256", args.disposition_receipt_sha256),
                ("--bridge-receipt-sha256", args.bridge_receipt_sha256),
            )
            if not value
        ]
        if missing:
            parser.error(f"exact-run subset integration requires: {', '.join(missing)}")
        if args.integrate_queue:
            parser.error("--integrate-run-ids cannot be combined with --integrate-queue")
        result = steward_integrate_exact_run_subset(
            ion_root=args.ion_root,
            integrate_run_ids=list(args.integrate_run_ids or []),
            output_sha256=list(args.output_sha256 or []),
            disposition_receipt_sha256=str(args.disposition_receipt_sha256),
            bridge_receipt_sha256=str(args.bridge_receipt_sha256),
            steward_return_sha256=str(args.steward_return_sha256),
            bridge_receipt_path=args.bridge_receipt_path,
            accepted_state_authority_token_path=args.accepted_state_authority_token_path,
            accepted_state_authority_token_sha256=args.accepted_state_authority_token_sha256,
            write=args.write,
            dry_run=args.dry_run,
        )
    elif args.integrate_queue:
        result = steward_integrate_pending_queue(ion_root=args.ion_root, write=args.write)
    else:
        if not args.worker_output:
            parser.error("--worker-output is required unless --integrate-queue or subset flags are used")
        result = steward_integrate_return_file(ion_root=args.ion_root, worker_output_path=args.worker_output, cycle_id=args.cycle_id, step_index=args.step_index, write=args.write)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result.get("verdict") or ("ION_STEWARD_INTEGRATION_ACCEPTED" if result["accepted"] else "ION_STEWARD_INTEGRATION_REJECTED"))
    return 0 if result["accepted"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
