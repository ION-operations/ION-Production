"""Cockpit actions for Team Comms audit receipts."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .ion_agent_comms_audit import audit_agent_comms_chain
from .ion_agent_comms_audit_gate import audit_gate_for_run
from .ion_agent_comms_runs import build_agent_comms_runs_projection

RUN_AUDIT_ACTION_SCHEMA_ID = "ion.agent_comms.run.audit_action.v1"


def _root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


def _record(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def _no_authority() -> dict[str, bool]:
    return {
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _run_projection(root: Path, run_id: str) -> dict[str, Any]:
    projection = build_agent_comms_runs_projection(root, limit=100)
    for row in list(projection.get("runs") or []):
        record = _record(row)
        if _text(record.get("run_id")) == run_id:
            return record
    return {}


def audit_agent_comms_run(root: str | Path | None, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    shell_root = _root(root)
    data = dict(payload or {})
    run_id = _text(data.get("run_id"))
    strict_pristine = data.get("strict_pristine") is not False
    write_receipt = data.get("write_receipt") is not False
    audit = audit_agent_comms_chain(
        shell_root,
        {
            "run_id": run_id,
            "strict_pristine": strict_pristine,
            "write_receipt": write_receipt,
        },
    )
    gate = audit_gate_for_run(shell_root, _text(audit.get("run_id"), run_id), run_path=_text(audit.get("run_path")))
    return {
        "schema_id": RUN_AUDIT_ACTION_SCHEMA_ID,
        "ok": bool(audit.get("ok")),
        "run_id": audit.get("run_id") or run_id,
        "audit": audit,
        "audit_gate": gate,
        "receipt_path": audit.get("receipt_path"),
        "finding": "audit_passed" if audit.get("ok") else "audit_failed",
        **_no_authority(),
    }


def maybe_audit_agent_comms_result(
    root: str | Path | None,
    payload: Mapping[str, Any] | None,
    result: Mapping[str, Any],
) -> dict[str, Any]:
    shell_root = _root(root)
    data = dict(payload or {})
    enriched = dict(result)
    run_id = _text(enriched.get("run_id") or data.get("run_id"))
    if data.get("auto_audit") is False:
        enriched["auto_audit"] = {"enabled": False, "state": "disabled", **_no_authority()}
        return enriched
    if not run_id or enriched.get("ok") is not True:
        enriched["auto_audit"] = {"enabled": True, "state": "skipped", "reason": "run_not_ready", **_no_authority()}
        return enriched
    run = _run_projection(shell_root, run_id)
    completion = _record(run.get("completion_state"))
    if completion.get("is_complete") is not True or _text(run.get("operational_state")) != "response_observed":
        enriched["audit_gate"] = audit_gate_for_run(shell_root, run_id, run_path=_text(run.get("run_path")))
        enriched["auto_audit"] = {
            "enabled": True,
            "state": "skipped",
            "reason": "run_not_complete",
            "completion_state": completion.get("state"),
            "operational_state": run.get("operational_state"),
            **_no_authority(),
        }
        return enriched
    action = audit_agent_comms_run(
        shell_root,
        {
            "run_id": run_id,
            "write_receipt": data.get("write_audit_receipt") is not False,
            "strict_pristine": data.get("strict_pristine") is not False,
        },
    )
    enriched["chain_audit"] = action.get("audit")
    enriched["audit_gate"] = action.get("audit_gate")
    enriched["auto_audit"] = {
        "enabled": True,
        "state": "receipt_written" if action.get("receipt_path") else "evaluated",
        "ok": action.get("ok"),
        "receipt_path": action.get("receipt_path"),
        "gate_state": _record(action.get("audit_gate")).get("state"),
        **_no_authority(),
    }
    return enriched
