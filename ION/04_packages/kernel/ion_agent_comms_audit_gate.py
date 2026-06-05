"""Receipt-backed cleanliness gate for Team Comms run audits."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .ion_agent_comms import AGENT_COMMS_ROOT

AUDIT_SCHEMA_ID = "ion.agent_comms.chain_audit.v1"
AUDIT_GATE_SCHEMA_ID = "ion.agent_comms.audit_gate.v1"
AUDIT_RECEIPT_DIR = AGENT_COMMS_ROOT / "audits"


def _root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _record(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _records(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item)]
    return []


def _text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _repo_path(root: Path, rel_path: str) -> Path | None:
    path = Path(rel_path)
    if not rel_path or path.is_absolute() or ".." in path.parts:
        return None
    return root / path


def _sha256(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _no_authority() -> dict[str, bool]:
    return {
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def audit_evidence_files(audit: Mapping[str, Any]) -> list[str]:
    """Return the evidence paths that must stay unchanged for an audit receipt to remain fresh."""

    paths: list[str] = []
    for candidate in [
        _text(audit.get("run_path")),
        *_list(audit.get("latest_return_paths")),
    ]:
        if candidate:
            paths.append(candidate)
    for row in _records(audit.get("machine_receipts")):
        receipt_path = _text(row.get("receipt_path"))
        if receipt_path:
            paths.append(receipt_path)
    for row in _records(audit.get("worker_runs")):
        for key in ("workpack_path", "run_packet_path"):
            value = _text(row.get(key))
            if value:
                paths.append(value)
    return sorted(dict.fromkeys(paths))


def audit_evidence_digest(root: str | Path | None, audit: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _root(root)
    files: list[dict[str, Any]] = []
    for rel_path in audit_evidence_files(audit):
        path = _repo_path(shell_root, rel_path)
        exists = bool(path and path.exists())
        files.append(
            {
                "path": rel_path,
                "exists": exists,
                "sha256": _sha256(path) if exists else "",
            }
        )
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema_id": "ion.agent_comms.audit_evidence_digest.v1",
        "evidence_sha256": hashlib.sha256(canonical).hexdigest(),
        "evidence_files": files,
        "evidence_file_count": len(files),
        **_no_authority(),
    }


def attach_audit_evidence_digest(root: str | Path | None, audit: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(audit)
    digest = audit_evidence_digest(root, result)
    result["evidence_sha256"] = digest["evidence_sha256"]
    result["evidence_file_count"] = digest["evidence_file_count"]
    result["evidence_files"] = digest["evidence_files"]
    return result


def latest_audit_receipts(root: str | Path | None, run_id: str) -> list[dict[str, Any]]:
    shell_root = _root(root)
    rows: list[dict[str, Any]] = []
    receipt_dir = shell_root / AUDIT_RECEIPT_DIR
    if not receipt_dir.exists():
        return rows
    for path in sorted(receipt_dir.glob("*.json")):
        packet = _read_json(path)
        if packet.get("schema_id") != AUDIT_SCHEMA_ID:
            continue
        if _text(packet.get("run_id")) != run_id:
            continue
        rows.append({"path": _rel(path, shell_root), "packet": packet})
    rows.sort(key=lambda item: (_text(_record(item.get("packet")).get("generated_at")), _text(item.get("path"))), reverse=True)
    return rows


def audit_gate_for_run(root: str | Path | None, run_id: str, *, run_path: str = "") -> dict[str, Any]:
    shell_root = _root(root)
    run_id = _text(run_id)
    current_run_path = run_path
    if not run_id:
        return {
            "schema_id": AUDIT_GATE_SCHEMA_ID,
            "clean": False,
            "state": "run_id_required",
            "receipt_required": True,
            "stale_reasons": ["run_id_required"],
            **_no_authority(),
        }
    receipts = latest_audit_receipts(shell_root, run_id)
    if not receipts:
        return {
            "schema_id": AUDIT_GATE_SCHEMA_ID,
            "run_id": run_id,
            "clean": False,
            "state": "audit_missing",
            "receipt_required": True,
            "stale_reasons": ["audit_receipt_missing"],
            "latest_audit_path": "",
            **_no_authority(),
        }
    latest = receipts[0]
    audit = _record(latest.get("packet"))
    current_run_path = current_run_path or _text(audit.get("run_path"))
    current_run_sha256 = _sha256(_repo_path(shell_root, current_run_path))
    current_digest = audit_evidence_digest(shell_root, audit)
    recorded_evidence_sha256 = _text(audit.get("evidence_sha256"))
    stale_reasons: list[str] = []
    if audit.get("ok") is not True or _text(audit.get("audit_state")) != "PASS":
        stale_reasons.append("latest_audit_not_pass")
    if _text(audit.get("run_sha256")) != current_run_sha256:
        stale_reasons.append("run_sha256_mismatch")
    if not recorded_evidence_sha256:
        stale_reasons.append("evidence_sha256_missing")
    elif recorded_evidence_sha256 != _text(current_digest.get("evidence_sha256")):
        stale_reasons.append("evidence_sha256_mismatch")
    if stale_reasons:
        state = "audit_failed" if "latest_audit_not_pass" in stale_reasons else "audit_stale"
    else:
        state = "clean"
    return {
        "schema_id": AUDIT_GATE_SCHEMA_ID,
        "run_id": run_id,
        "clean": state == "clean",
        "state": state,
        "receipt_required": True,
        "latest_audit_path": latest.get("path"),
        "latest_audit_generated_at": audit.get("generated_at"),
        "latest_audit_state": audit.get("audit_state"),
        "latest_audit_ok": audit.get("ok"),
        "findings": list(audit.get("findings") or []),
        "run_path": current_run_path,
        "run_sha256": audit.get("run_sha256"),
        "current_run_sha256": current_run_sha256,
        "evidence_sha256": recorded_evidence_sha256,
        "current_evidence_sha256": current_digest.get("evidence_sha256"),
        "evidence_file_count": current_digest.get("evidence_file_count"),
        "stale_reasons": stale_reasons,
        **_no_authority(),
    }
