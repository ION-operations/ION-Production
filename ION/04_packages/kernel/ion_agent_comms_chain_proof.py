"""Step-by-step proof harness for bounded Team Comms chains."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_agent_comms import AGENT_COMMS_ROOT
from .ion_agent_comms_audit import audit_agent_comms_chain
from .ion_agent_comms_audit_gate import audit_gate_for_run
from .ion_agent_comms_runs import build_agent_comms_runs_projection

CHAIN_PROOF_SCHEMA_ID = "ion.agent_comms.chain_proof.v1"
CHAIN_PROOF_RECEIPT_DIR = AGENT_COMMS_ROOT / "chain_proofs"
TASK_RETURN_MACHINE_RECEIPTS_DIR = Path("ION/05_context/current/chatgpt_connector/task_return_machine_receipts")

FOLLOWUP_TERMINAL_STATES = {"followup_directive_observed", "no_followup_declared", "blocked_declared"}


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


def _no_authority() -> dict[str, bool]:
    return {
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _find_run(root: Path, run_id: str, limit: int) -> tuple[dict[str, Any], dict[str, Any]]:
    projection = build_agent_comms_runs_projection(root, limit=limit)
    rows = _records(projection.get("runs"))
    if run_id:
        for row in rows:
            if _text(row.get("run_id")) == run_id:
                return row, projection
        return {}, projection
    for row in rows:
        if _text(row.get("operational_state")) == "response_observed":
            return row, projection
    return (rows[0] if rows else {}), projection


def _run_evidence_path(run: Mapping[str, Any]) -> str:
    run_path = _text(run.get("run_path"))
    if run_path:
        return run_path
    for node in _records(_record(run.get("graph")).get("nodes")):
        if node.get("kind") == "run" and node.get("evidence_path"):
            return _text(node.get("evidence_path"))
    return ""


def _machine_receipts_by_return(root: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    receipt_dir = root / TASK_RETURN_MACHINE_RECEIPTS_DIR
    if not receipt_dir.exists():
        return rows
    for path in sorted(receipt_dir.glob("*.json")):
        packet = _read_json(path)
        return_path = _text(packet.get("task_return_packet_path"))
        if return_path:
            rows[return_path] = {"path": _rel(path, root), "packet": packet}
    return rows


def _worker_run_rows(root: Path, workpack_paths: list[str]) -> list[dict[str, Any]]:
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
                    "returncode": packet.get("returncode"),
                    "pid": packet.get("pid"),
                    "completed_at": packet.get("completed_at"),
                    "exists": bool(packet),
                }
            )
    return rows


def _link(
    links: list[dict[str, Any]],
    link_id: str,
    ok: bool,
    *,
    state: str = "",
    required: bool = True,
    evidence_refs: list[str] | None = None,
    detail: Mapping[str, Any] | None = None,
) -> None:
    row: dict[str, Any] = {
        "link_id": link_id,
        "ok": bool(ok),
        "required": bool(required),
        "state": state or ("observed" if ok else "missing"),
    }
    refs = [ref for ref in list(evidence_refs or []) if ref]
    if refs:
        row["evidence_refs"] = refs
    if detail:
        row["detail"] = dict(detail)
    links.append(row)


def prove_agent_comms_chain(root: str | Path | None = None, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return explicit proof links for a real Team Comms run.

    This harness does not invent messages or receipts. It reads the current run,
    durable Team Comms messages, workpack paths, worker evidence, return packets,
    synced replies, directive state, and audit gate state.
    """

    shell_root = _root(root)
    data = dict(payload or {})
    run_id = _text(data.get("run_id"))
    limit = max(1, min(int(data.get("limit") or 100), 100))
    require_directive = data.get("require_directive") is not False
    require_machine_receipts = data.get("require_machine_receipts") is not False
    require_clean_audit = data.get("require_clean_audit") is True
    try:
        min_agents = max(1, int(data.get("min_agents") or 2))
    except (TypeError, ValueError):
        min_agents = 2
    write_receipt = data.get("write_receipt") is True

    run, projection = _find_run(shell_root, run_id, limit)
    links: list[dict[str, Any]] = []
    generated_at = _now()
    if not run:
        _link(links, "run_observed", False, evidence_refs=[run_id], detail={"projection_run_count": projection.get("run_count")})
        result = {
            "schema_id": CHAIN_PROOF_SCHEMA_ID,
            "ok": False,
            "proof_state": "blocked_at_run_observed",
            "generated_at": generated_at,
            "run_id": run_id,
            "run_path": "",
            "first_missing_link": "run_observed",
            "missing_links": ["run_observed"],
            "links": links,
            "projection": {"run_count": projection.get("run_count")},
            "chain_sequence": "message -> directive -> workpack -> worker -> task_return -> synced_reply -> followup_decision",
            **_no_authority(),
        }
        if write_receipt:
            receipt = shell_root / CHAIN_PROOF_RECEIPT_DIR / f"{_stamp()}_agent_comms_chain_proof.json"
            _write_json(receipt, result)
            result["receipt_path"] = _rel(receipt, shell_root)
        return result

    run_id = _text(run.get("run_id"))
    run_path = _run_evidence_path(run)
    completion_state = _record(run.get("completion_state"))
    directive_state = _record(completion_state.get("directive_state"))
    followup_state = _record(completion_state.get("followup_decision")) or _record(run.get("followup_decision"))
    policy_gate = _record(run.get("policy_gate"))
    graph = _record(run.get("graph"))
    graph_edges = _records(graph.get("edges"))
    graph_nodes = _records(graph.get("nodes"))
    work_items = _records(run.get("work_items"))
    workpack_paths = _list(run.get("workpack_paths"))
    latest_return_paths = [str(item.get("latest_return_packet_path")) for item in work_items if item.get("latest_return_packet_path")]
    return_message_ids = _record(run.get("return_message_ids"))
    worker_runtime = _record(run.get("worker_runtime"))
    worker_runs = _worker_run_rows(shell_root, workpack_paths)
    receipts_by_return = _machine_receipts_by_return(shell_root)
    receipt_rows = [
        {
            "return_path": return_path,
            "receipt_path": _record(receipts_by_return.get(return_path)).get("path"),
            "accepted": _record(_record(receipts_by_return.get(return_path)).get("packet")).get("accepted_for_carrier_intake"),
        }
        for return_path in latest_return_paths
    ]
    roles = {
        str(node.get("role"))
        for node in graph_nodes
        if _text(node.get("role")) and _text(node.get("role")) != "operator"
    }
    roles.update(str(item.get("agent_role_id")) for item in work_items if _text(item.get("agent_role_id")))
    roles = {role for role in roles if role}
    edge_kinds = {str(edge.get("kind")) for edge in graph_edges if edge.get("kind")}
    synced_reply_edges = [edge for edge in graph_edges if edge.get("kind") == "synced_reply"]
    directive_count = int(directive_state.get("directive_count") or 0)
    processed_directive_count = int(directive_state.get("processed_directive_count") or 0)
    pending_directive_count = int(directive_state.get("pending_directive_count") or 0)
    worker_count = int(worker_runtime.get("worker_count") or 0)
    worker_evidence_count = worker_count + len(worker_runs)
    task_return_count = int(run.get("task_return_count") or 0)
    agent_response_count = int(run.get("agent_response_count") or 0)
    followup_decision_state = _text(followup_state.get("state"), "missing")

    _link(links, "run_observed", True, state=_text(run.get("status"), "observed"), evidence_refs=[run_path])
    _link(
        links,
        "message_sent",
        bool(_list(run.get("root_message_ids")) or int(run.get("message_count") or 0) > 0),
        evidence_refs=_list(run.get("message_paths"))[:6],
        detail={"root_message_ids": _list(run.get("root_message_ids")), "thread_ids": _list(run.get("thread_ids"))},
    )
    _link(
        links,
        "multi_agent_handoff",
        len(roles) >= min_agents,
        state=f"{len(roles)}/{min_agents}_agents",
        evidence_refs=workpack_paths[:8],
        detail={"roles": sorted(roles), "min_agents": min_agents},
    )
    _link(
        links,
        "directive_observed",
        directive_count > 0 or not require_directive,
        required=require_directive,
        state="observed" if directive_count > 0 else "not_required",
        detail={"directive_count": directive_count, "pending_directive_count": pending_directive_count},
    )
    _link(
        links,
        "directive_processed",
        (directive_count == 0 and not require_directive) or (directive_count > 0 and processed_directive_count >= directive_count and pending_directive_count == 0),
        required=require_directive,
        state="processed" if processed_directive_count else ("not_required" if not require_directive else "missing"),
        detail={
            "directive_count": directive_count,
            "processed_directive_count": processed_directive_count,
            "pending_directive_count": pending_directive_count,
        },
    )
    _link(links, "workpack_created", bool(work_items or workpack_paths), evidence_refs=workpack_paths[:8], detail={"workpack_count": len(work_items)})
    _link(
        links,
        "worker_started",
        worker_evidence_count > 0,
        state="observed" if worker_evidence_count else "missing",
        evidence_refs=[str(row.get("run_packet_path")) for row in worker_runs if row.get("run_packet_path")][:8],
        detail={"runtime_worker_count": worker_count, "queue_worker_run_count": len(worker_runs), "latest_worker": worker_runtime.get("latest_worker")},
    )
    _link(
        links,
        "task_return_observed",
        task_return_count > 0 and bool(latest_return_paths),
        evidence_refs=latest_return_paths[:8],
        detail={"task_return_count": task_return_count, "accepted_return_count": run.get("accepted_return_count")},
    )
    _link(
        links,
        "machine_receipts_observed",
        bool(latest_return_paths) and all(row.get("receipt_path") and row.get("accepted") is True for row in receipt_rows),
        required=require_machine_receipts,
        evidence_refs=[str(row.get("receipt_path")) for row in receipt_rows if row.get("receipt_path")][:8],
        detail={"receipt_rows": receipt_rows},
    )
    _link(
        links,
        "synced_reply_observed",
        bool(synced_reply_edges or return_message_ids) and agent_response_count > 0,
        evidence_refs=list(_record(run.get("return_message_paths")).values())[:8],
        detail={"synced_reply_edge_count": len(synced_reply_edges), "return_message_count": len(return_message_ids), "agent_response_count": agent_response_count},
    )
    _link(
        links,
        "followup_decision_observed",
        followup_decision_state in FOLLOWUP_TERMINAL_STATES,
        state=followup_decision_state,
        detail={"followup_decision": followup_state},
    )
    _link(
        links,
        "policy_limits_enforced",
        policy_gate.get("ok") is True and _text(policy_gate.get("state")) == "within_limits",
        state=_text(policy_gate.get("state"), "missing"),
        detail={"blocked_limits": list(policy_gate.get("blocked_limits") or [])},
    )

    audit = audit_agent_comms_chain(
        shell_root,
        {
            "run_id": run_id,
            "write_receipt": False,
            "strict_pristine": data.get("strict_pristine") is not False,
            "limit": limit,
        },
    )
    audit_gate = audit_gate_for_run(shell_root, run_id, run_path=run_path)
    _link(
        links,
        "clean_audit_receipt",
        audit_gate.get("clean") is True,
        required=require_clean_audit,
        state=_text(audit_gate.get("state"), "audit_missing"),
        evidence_refs=[_text(audit_gate.get("latest_audit_path"))],
        detail={"audit_state": audit.get("audit_state"), "audit_findings": list(audit.get("findings") or [])},
    )

    missing_links = [str(link.get("link_id")) for link in links if link.get("required") is True and link.get("ok") is not True]
    first_missing_link = missing_links[0] if missing_links else ""
    result = {
        "schema_id": CHAIN_PROOF_SCHEMA_ID,
        "ok": not missing_links,
        "proof_state": "chain_proved" if not missing_links else f"blocked_at_{first_missing_link}",
        "generated_at": generated_at,
        "run_id": run_id,
        "run_path": run_path,
        "first_missing_link": first_missing_link,
        "missing_links": missing_links,
        "links": links,
        "metrics": {
            "agent_role_count": len(roles),
            "directive_count": directive_count,
            "processed_directive_count": processed_directive_count,
            "pending_directive_count": pending_directive_count,
            "workpack_count": len(work_items),
            "worker_evidence_count": worker_evidence_count,
            "task_return_count": task_return_count,
            "machine_receipt_count": sum(1 for row in receipt_rows if row.get("receipt_path")),
            "synced_reply_count": len(synced_reply_edges) or len(return_message_ids),
            "agent_response_count": agent_response_count,
            "graph_node_count": graph.get("node_count"),
            "graph_edge_count": graph.get("edge_count"),
        },
        "roles": sorted(roles),
        "edge_kinds": sorted(edge_kinds),
        "latest_return_paths": latest_return_paths,
        "worker_runs": worker_runs,
        "machine_receipts": receipt_rows,
        "followup_decision_state": followup_decision_state,
        "audit_state": audit.get("audit_state"),
        "audit_ok": audit.get("ok"),
        "audit_findings": list(audit.get("findings") or []),
        "audit_gate": audit_gate,
        "projection": {
            "run_count": projection.get("run_count"),
            "response_observed_count": projection.get("response_observed_count"),
            "active_worker_count": projection.get("active_worker_count"),
        },
        "chain_sequence": "message -> directive -> workpack -> worker -> task_return -> machine_receipt -> synced_reply -> followup_decision -> policy_gate",
        "policy": "Chain proof only reads filesystem artifacts and automation receipts. It does not create agent replies, decide routing, or grant production/live/accepted-state/secrets authority.",
        **_no_authority(),
    }
    if write_receipt:
        receipt = shell_root / CHAIN_PROOF_RECEIPT_DIR / f"{_stamp()}_agent_comms_chain_proof.json"
        _write_json(receipt, result)
        result["receipt_path"] = _rel(receipt, shell_root)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prove each link of an ION Team Comms chain.")
    parser.add_argument("--ion-root", default=".", help="ION root or subpath")
    parser.add_argument("--run-id", default="", help="Run id to prove; defaults to latest response-observed run")
    parser.add_argument("--write-receipt", action="store_true", help="Write a chain proof receipt")
    parser.add_argument("--allow-no-directive", action="store_true", help="Do not require an agent-authored directive link")
    parser.add_argument("--allow-missing-machine-receipts", action="store_true", help="Do not fail when machine receipts are missing")
    parser.add_argument("--require-clean-audit", action="store_true", help="Require a fresh clean audit receipt")
    parser.add_argument("--min-agents", type=int, default=2, help="Minimum non-operator agent roles required")
    parser.add_argument("--json", action="store_true", help="Emit full JSON")
    args = parser.parse_args(argv)
    result = prove_agent_comms_chain(
        args.ion_root,
        {
            "run_id": args.run_id,
            "write_receipt": args.write_receipt,
            "require_directive": not args.allow_no_directive,
            "require_machine_receipts": not args.allow_missing_machine_receipts,
            "require_clean_audit": args.require_clean_audit,
            "min_agents": args.min_agents,
        },
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"AGENT_COMMS_CHAIN_PROOF={result['proof_state']}")
        print(f"RUN_ID={result.get('run_id')}")
        print(f"FIRST_MISSING_LINK={result.get('first_missing_link')}")
        print(f"MISSING_LINKS={'|'.join(result.get('missing_links') or [])}")
        if result.get("receipt_path"):
            print(f"RECEIPT={result.get('receipt_path')}")
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
