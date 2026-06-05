"""Fail-closed audit for bounded Team Comms chains."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_agent_comms_audit_gate import AUDIT_RECEIPT_DIR, AUDIT_SCHEMA_ID, attach_audit_evidence_digest
from .ion_agent_comms_runs import build_agent_comms_runs_projection

TASK_RETURN_MACHINE_RECEIPTS_DIR = Path("ION/05_context/current/chatgpt_connector/task_return_machine_receipts")

DEFAULT_REQUIRED_ROLES = ("operator",)
DEFAULT_REQUIRED_EDGE_KINDS = ("root_message", "reply", "tracks_workpack", "produced_return", "synced_reply")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


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


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def _sha256(path: Path) -> str:
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


def _check(checks: list[dict[str, Any]], check_id: str, ok: bool, *, detail: str = "", evidence: Any = None) -> None:
    row: dict[str, Any] = {"check_id": check_id, "ok": bool(ok)}
    if detail:
        row["detail"] = detail
    if evidence not in (None, "", []):
        row["evidence"] = evidence
    checks.append(row)


def _find_run(root: Path, run_id: str, limit: int) -> tuple[dict[str, Any], dict[str, Any]]:
    projection = build_agent_comms_runs_projection(root, limit=limit)
    rows = _records(projection.get("runs"))
    if run_id:
        for row in rows:
            if _text(row.get("run_id")) == run_id:
                return row, projection
        return {}, projection
    for row in rows:
        if _text(row.get("status")) == "complete" and _text(row.get("operational_state")) == "response_observed":
            return row, projection
    return (rows[0] if rows else {}), projection


def _run_evidence_path(run: Mapping[str, Any]) -> str:
    graph = _record(run.get("graph"))
    for record in _records(graph.get("nodes")):
        if record.get("kind") == "run" and record.get("evidence_path"):
            return _text(record.get("evidence_path"))
    return ""


def _machine_receipts_by_return(root: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    receipt_dir = root / TASK_RETURN_MACHINE_RECEIPTS_DIR
    if not receipt_dir.exists():
        return rows
    for path in sorted(receipt_dir.glob("*.json")):
        payload = _read_json(path)
        target = _text(payload.get("task_return_packet_path"))
        if target:
            rows[target] = {"path": _rel(path, root), "packet": payload}
    return rows


def _worker_runs(root: Path, workpack_paths: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for workpack_path in workpack_paths:
        workpack = _read_json(root / workpack_path)
        for run_path in _list(workpack.get("codex_queue_runner_runs")):
            packet = _read_json(root / run_path)
            rows.append(
                {
                    "workpack_path": workpack_path,
                    "run_packet_path": run_path,
                    "status": packet.get("status"),
                    "pid": packet.get("pid"),
                    "returncode": packet.get("returncode"),
                    "completed_at": packet.get("completed_at"),
                    "failure_classification": packet.get("failure_classification"),
                }
            )
    return rows


def audit_agent_comms_chain(root: str | Path | None = None, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Audit a Team Comms run as real only when filesystem evidence closes."""

    shell_root = _root(root)
    data = dict(payload or {})
    run_id = _text(data.get("run_id"))
    strict_pristine = data.get("strict_pristine") is not False
    write_receipt = data.get("write_receipt") is not False
    limit = max(1, min(int(data.get("limit") or 100), 100))
    required_roles_input = _list(data.get("required_roles"))
    required_edge_kinds = set(_list(data.get("required_edge_kinds")) or DEFAULT_REQUIRED_EDGE_KINDS)
    min_workpacks_input = data.get("min_workpacks")

    run, projection = _find_run(shell_root, run_id, limit)
    checks: list[dict[str, Any]] = []
    findings: list[str] = []
    run_found = bool(run)
    _check(checks, "run_found", run_found, detail=run_id or "latest_complete_response_observed")
    if not run_found:
        findings.append("run_not_found")
        return {
            "schema_id": AUDIT_SCHEMA_ID,
            "ok": False,
            "audit_state": "FAIL",
            "generated_at": _now(),
            "run_id": run_id,
            "checks": checks,
            "findings": findings,
            "projection_run_count": projection.get("run_count"),
            **_no_authority(),
        }

    completion_state = _record(run.get("completion_state"))
    directive_state = _record(completion_state.get("directive_state"))
    followup_state = _record(completion_state.get("followup_decision"))
    policy_gate = _record(run.get("policy_gate"))
    graph = _record(run.get("graph"))
    work_items = _records(run.get("work_items"))
    roles = {str(node.get("role")) for node in _records(graph.get("nodes")) if node.get("role")}
    edge_kinds = {str(edge.get("kind")) for edge in _records(graph.get("edges")) if edge.get("kind")}
    run_path = _run_evidence_path(run)
    workpack_paths = [str(path) for path in _list(run.get("workpack_paths"))]
    latest_return_paths = [str(item.get("latest_return_packet_path")) for item in work_items if item.get("latest_return_packet_path")]
    receipts_by_return = _machine_receipts_by_return(shell_root)
    worker_runs = _worker_runs(shell_root, workpack_paths)
    if required_roles_input:
        required_roles = set(required_roles_input)
    else:
        required_roles = {
            _text(run.get("from_role"), "operator"),
            *[str(role) for role in _list(run.get("target_roles"))],
            *[str(item.get("agent_role_id")) for item in work_items if _text(item.get("agent_role_id"))],
        }
        required_roles = {role for role in required_roles if role}
        if not required_roles:
            required_roles = set(DEFAULT_REQUIRED_ROLES)
    try:
        min_workpacks = int(min_workpacks_input) if min_workpacks_input is not None else len(work_items)
    except (TypeError, ValueError):
        min_workpacks = len(work_items)
    min_workpacks = max(1, min_workpacks)

    _check(checks, "run_status_complete", _text(run.get("status")) == "complete", evidence=run.get("status"))
    _check(checks, "completion_state_complete", _text(completion_state.get("state")) == "complete", evidence=completion_state.get("state"))
    _check(checks, "operational_state_response_observed", _text(run.get("operational_state")) == "response_observed", evidence=run.get("operational_state"))
    _check(checks, "policy_gate_within_limits", policy_gate.get("ok") is True and policy_gate.get("state") == "within_limits", evidence=policy_gate)
    _check(checks, "required_roles_present", required_roles.issubset(roles), evidence=sorted(roles))
    _check(checks, "required_graph_edges_present", required_edge_kinds.issubset(edge_kinds), evidence=sorted(edge_kinds))
    _check(checks, "graph_not_truncated", graph.get("truncated") is False, evidence=graph.get("truncated"))
    _check(checks, "workpack_count_minimum", len(work_items) >= min_workpacks, evidence=len(work_items))
    _check(checks, "workpacks_all_returned", bool(work_items) and all(_text(item.get("latest_return_packet_path")) for item in work_items), evidence=latest_return_paths)
    _check(checks, "returns_all_accepted", bool(work_items) and all(int(item.get("accepted_return_count") or 0) >= 1 for item in work_items), evidence=[item.get("accepted_return_count") for item in work_items])
    _check(checks, "directive_pending_zero", int(directive_state.get("pending_directive_count") or 0) == 0, evidence=directive_state)
    directive_count = int(directive_state.get("directive_count") or 0)
    processed_directive_count = int(directive_state.get("processed_directive_count") or 0)
    _check(
        checks,
        "directive_processed_observed",
        directive_count == 0 or processed_directive_count >= directive_count,
        evidence={"directive_count": directive_count, "processed_directive_count": processed_directive_count},
    )
    _check(checks, "followup_no_followup_declared", followup_state.get("state") == "no_followup_declared", evidence=followup_state)

    receipt_rows: list[dict[str, Any]] = []
    for return_path in latest_return_paths:
        receipt = receipts_by_return.get(return_path, {})
        packet = _record(receipt.get("packet"))
        receipt_rows.append({"return_path": return_path, "receipt_path": receipt.get("path"), "accepted": packet.get("accepted_for_carrier_intake")})
    _check(
        checks,
        "machine_receipts_all_latest_returns",
        bool(latest_return_paths) and all(row.get("receipt_path") and row.get("accepted") is True for row in receipt_rows),
        evidence=receipt_rows,
    )

    if strict_pristine:
        accepted_worker_status = "RETURN_RECORDED_PROOF_ACCEPTED"
        _check(
            checks,
            "worker_runs_all_accepted",
            len(worker_runs) >= len(work_items) and all(row.get("status") == accepted_worker_status and row.get("returncode") == 0 for row in worker_runs),
            evidence=worker_runs,
        )

    for row in checks:
        if not row.get("ok"):
            findings.append(str(row.get("check_id")))

    ok = not findings
    receipt_path = ""
    result = {
        "schema_id": AUDIT_SCHEMA_ID,
        "ok": ok,
        "audit_state": "PASS" if ok else "FAIL",
        "generated_at": _now(),
        "run_id": run.get("run_id"),
        "run_path": run_path,
        "run_sha256": _sha256(shell_root / run_path) if run_path else "",
        "strict_pristine": strict_pristine,
        "checks": checks,
        "findings": findings,
        "metrics": {
            "workpack_count": run.get("workpack_count"),
            "task_return_count": run.get("task_return_count"),
            "accepted_return_count": run.get("accepted_return_count"),
            "agent_response_count": run.get("agent_response_count"),
            "graph_nodes": graph.get("node_count"),
            "graph_edges": graph.get("edge_count"),
            "directive_processed_count": directive_state.get("processed_directive_count"),
            "directive_pending_count": directive_state.get("pending_directive_count"),
        },
        "roles": sorted(roles),
        "edge_kinds": sorted(edge_kinds),
        "latest_return_paths": latest_return_paths,
        "machine_receipts": receipt_rows,
        "worker_runs": worker_runs,
        "chain_sequence": "task_dispatch -> accepted worker return(s) -> synced agent reply -> explicit directive processing when present -> terminal no_followup decision",
        "projection": {
            "run_count": projection.get("run_count"),
            "response_observed_count": projection.get("response_observed_count"),
            "policy_blocked_count": projection.get("policy_blocked_count"),
        },
        **_no_authority(),
    }
    result = attach_audit_evidence_digest(shell_root, result)
    if write_receipt:
        receipt = shell_root / AUDIT_RECEIPT_DIR / f"{_stamp()}_agent_comms_chain_audit.json"
        _write_json(receipt, result)
        receipt_path = _rel(receipt, shell_root)
        result["receipt_path"] = receipt_path
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit an ION Team Comms chain.")
    parser.add_argument("--ion-root", default=".", help="ION root or subpath")
    parser.add_argument("--run-id", default="", help="Run id to audit; defaults to latest complete response-observed run")
    parser.add_argument("--no-write", action="store_true", help="Do not write audit receipt")
    parser.add_argument("--allow-repaired", action="store_true", help="Do not require every linked worker run to be accepted")
    parser.add_argument("--json", action="store_true", help="Emit full JSON")
    args = parser.parse_args(argv)
    result = audit_agent_comms_chain(
        args.ion_root,
        {
            "run_id": args.run_id,
            "write_receipt": not args.no_write,
            "strict_pristine": not args.allow_repaired,
        },
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"AGENT_COMMS_CHAIN_AUDIT={result['audit_state']}")
        print(f"RUN_ID={result.get('run_id')}")
        print(f"RUN_SHA256={result.get('run_sha256')}")
        print(f"FINDINGS={'|'.join(result.get('findings') or [])}")
        if result.get("receipt_path"):
            print(f"RECEIPT={result.get('receipt_path')}")
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
