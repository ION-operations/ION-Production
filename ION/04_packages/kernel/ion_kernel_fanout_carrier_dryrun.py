"""Carrier-facing dry-run entrypoint for bounded kernel fan-out scheduler checks.

This module is candidate/local only. It executes controlled no-op scenarios
through the true-parallel smoke harness and emits compact receipts without
mutating live queue state.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_kernel_fanout_true_parallel_smoke import (
    simulate_kernel_fanout_true_parallel_smoke,
)

SCHEMA_ID = "ion.kernel_fanout_carrier_dryrun_result.v1"
RUN_RECEIPT_SCHEMA_ID = "ion.kernel_fanout_carrier_dryrun_receipt.v1"
STATUS_SCHEMA_ID = "ion.kernel_fanout_carrier_dryrun_status.v1"
DEFAULT_OUTPUT_ROOT = Path("ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun")
DEFAULT_RESULT_FILENAME = "fanout_carrier_dryrun_result_20260514.json"
DEFAULT_ACCEPTED_RETURN_PATH = Path(
    "ION/05_context/current/chatgpt_connector/task_returns/2026-05-14T021628Z0000_task_return.json"
)
MAX_DRYRUN_CHILDREN = 2
MAX_DRYRUN_CHILD_TIMEOUT_SECONDS = 10
MAX_DRYRUN_PARENT_TIMEOUT_SECONDS = 10
QUEUE_PATHS = (
    "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
    "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_payload(payload: Mapping[str, Any]) -> str:
    material = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(material.encode("utf-8", errors="replace")).hexdigest()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid payload: {path}")
    return payload


def _queue_snapshot(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel in QUEUE_PATHS:
        path = root / rel
        exists = path.exists() and path.is_file()
        rows.append(
            {
                "path": rel,
                "exists": exists,
                "sha256": _sha256_file(path) if exists else None,
                "bytes": int(path.stat().st_size) if exists else None,
            }
        )
    return rows


def _project_rel(path: Path, *, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _resolve_from_root(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def _latest_result_path(output_root: Path) -> Path | None:
    exact = output_root / DEFAULT_RESULT_FILENAME
    if exact.exists():
        return exact
    candidates = sorted(output_root.glob("fanout_carrier_dryrun_result*.json"))
    return candidates[-1] if candidates else None


def _artifact_row(root: Path, path: Path, *, kind: str) -> dict[str, Any]:
    exists = path.exists() and path.is_file()
    return {
        "kind": kind,
        "path": _project_rel(path, root=root),
        "exists": exists,
        "sha256": _sha256_file(path) if exists else None,
    }


def _scenario_status_row(row: Mapping[str, Any]) -> dict[str, Any]:
    compact = row.get("compact_summary")
    compact_summary = compact if isinstance(compact, Mapping) else {}
    return {
        "scenario": str(row.get("scenario") or compact_summary.get("scenario") or ""),
        "plan_verdict": compact_summary.get("plan_verdict"),
        "settlement_verdict": compact_summary.get("settlement_verdict"),
    }


def _timeout_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    timeout_row = next((row for row in rows if row.get("scenario") == "forced_timeout"), None)
    compact = timeout_row.get("compact_summary") if isinstance(timeout_row, Mapping) else None
    compact_summary = compact if isinstance(compact, Mapping) else {}
    timeout_evidence = compact_summary.get("timeout_evidence")
    timeout_rows = timeout_evidence if isinstance(timeout_evidence, list) else []
    timeout_codes = sorted(
        {
            str(item.get("code"))
            for item in timeout_rows
            if isinstance(item, Mapping) and str(item.get("code") or "").strip()
        }
    )
    settlement = str(compact_summary.get("settlement_verdict") or "")
    return {
        "scenario": timeout_row.get("scenario") if isinstance(timeout_row, Mapping) else None,
        "settlement_verdict": compact_summary.get("settlement_verdict"),
        "blocked_children": compact_summary.get("blocked_children", []),
        "timeout_event_count": len(timeout_rows),
        "timeout_codes": timeout_codes,
        "fail_closed": bool(settlement == "SMOKE_BLOCKED" and timeout_rows),
    }


def _conflict_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    conflict_row = next((row for row in rows if row.get("scenario") == "forced_conflict"), None)
    compact = conflict_row.get("compact_summary") if isinstance(conflict_row, Mapping) else None
    compact_summary = compact if isinstance(compact, Mapping) else {}
    return {
        "scenario": conflict_row.get("scenario") if isinstance(conflict_row, Mapping) else None,
        "settlement_verdict": compact_summary.get("settlement_verdict"),
        "conflict_deferral_events": int(compact_summary.get("conflict_deferral_events") or 0),
        "conflict_deferred_children": compact_summary.get("conflict_deferred_children", []),
        "max_parallel_observed": compact_summary.get("max_parallel_observed"),
    }


def build_kernel_fanout_carrier_dryrun_status(
    root: str | Path | None = None,
    *,
    result_path: str | Path | None = None,
    accepted_return_path: str | Path | None = DEFAULT_ACCEPTED_RETURN_PATH,
) -> dict[str, Any]:
    shell_root = Path(root or ".").expanduser().resolve()
    output_root = shell_root / DEFAULT_OUTPUT_ROOT
    resolved_result_path = (
        _resolve_from_root(shell_root, result_path)
        if result_path is not None
        else _latest_result_path(output_root)
    )
    receipt_artifacts: list[dict[str, Any]] = []
    if accepted_return_path:
        receipt_artifacts.append(
            _artifact_row(
                shell_root,
                _resolve_from_root(shell_root, accepted_return_path),
                kind="accepted_carrier_dryrun_task_return",
            )
        )
    if resolved_result_path is None or not resolved_result_path.exists():
        return {
            "schema_id": STATUS_SCHEMA_ID,
            "generated_at": _now(),
            "status": "DRYRUN_RESULT_MISSING",
            "latest_dryrun_result_path": None,
            "latest_dryrun_result_sha256": None,
            "scenario_verdicts": [],
            "queue_mutation_detected": None,
            "timeout_fail_closed_summary": {
                "scenario": None,
                "settlement_verdict": None,
                "blocked_children": [],
                "timeout_event_count": 0,
                "timeout_codes": [],
                "fail_closed": False,
            },
            "conflict_lock_summary": {
                "scenario": None,
                "settlement_verdict": None,
                "conflict_deferral_events": 0,
                "conflict_deferred_children": [],
                "max_parallel_observed": None,
            },
            "receipt_artifacts": receipt_artifacts,
            "production_authority": False,
            "live_execution_authority": False,
            "mutates_active_state": False,
        }

    result = _read_json(resolved_result_path)
    receipt_artifacts.append(_artifact_row(shell_root, resolved_result_path, kind="latest_dryrun_result"))
    raw_rows = result.get("scenarios")
    rows = raw_rows if isinstance(raw_rows, list) else []
    scenario_verdicts = [_scenario_status_row(row) for row in rows if isinstance(row, Mapping)]
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        result_ref = row.get("result_path")
        if isinstance(result_ref, str) and result_ref.strip():
            receipt_artifacts.append(
                _artifact_row(shell_root, _resolve_from_root(shell_root, result_ref), kind="scenario_result")
            )
        parent_ref = row.get("parent_receipt_path")
        if isinstance(parent_ref, str) and parent_ref.strip():
            receipt_artifacts.append(
                _artifact_row(shell_root, _resolve_from_root(shell_root, parent_ref), kind="scenario_parent_receipt")
            )
    queue_integrity = result.get("queue_integrity")
    queue_data = queue_integrity if isinstance(queue_integrity, Mapping) else {}
    return {
        "schema_id": STATUS_SCHEMA_ID,
        "generated_at": _now(),
        "source_result_schema_id": result.get("schema_id"),
        "latest_dryrun_result_path": _project_rel(resolved_result_path, root=shell_root),
        "latest_dryrun_result_sha256": _sha256_file(resolved_result_path),
        "scenario_verdicts": scenario_verdicts,
        "queue_mutation_detected": bool(queue_data.get("queue_mutation_detected")),
        "timeout_fail_closed_summary": _timeout_summary(rows),
        "conflict_lock_summary": _conflict_summary(rows),
        "receipt_artifacts": receipt_artifacts,
        "production_authority": False,
        "live_execution_authority": False,
        "mutates_active_state": False,
    }


def _default_success_graph(*, artifact_root: str) -> dict[str, Any]:
    return {
        "parent_packet_id": "PCKT-ION-KERNEL-FANOUT-SCHEDULER-CARRIER-DRYRUN-SUCCESS-20260514",
        "request_id": "codex_req_kernel_fanout_carrier_dryrun_success_20260514",
        "max_parallel": 2,
        "artifact_root": artifact_root,
        "children": [
            {
                "child_id": "success_child_alpha",
                "objective": "Dry-run success child alpha.",
                "write_paths": [f"{artifact_root}/outputs/success_alpha.txt"],
                "heartbeat_seconds": 1,
            },
            {
                "child_id": "success_child_beta",
                "objective": "Dry-run success child beta.",
                "write_paths": [f"{artifact_root}/outputs/success_beta.txt"],
                "heartbeat_seconds": 1,
            },
        ],
    }


def _graph_from_fixture_payload(
    payload: Mapping[str, Any],
    *,
    artifact_root: str,
) -> dict[str, Any]:
    raw_children = payload.get("children")
    if not isinstance(raw_children, list):
        raise ValueError("fixture payload must include a children list")
    children: list[dict[str, Any]] = []
    for idx, raw in enumerate(raw_children):
        if not isinstance(raw, Mapping):
            continue
        child_id = str(raw.get("child_id") or f"fixture_child_{idx + 1}").strip()
        if not child_id:
            continue
        write_paths = raw.get("write_paths")
        if not isinstance(write_paths, list) or not write_paths:
            write_paths = [f"{artifact_root}/outputs/{child_id}.txt"]
        children.append(
            {
                "child_id": child_id,
                "objective": str(raw.get("objective") or f"Fixture child {idx + 1} dry-run."),
                "depends_on": [str(dep) for dep in raw.get("depends_on", [])],
                "write_paths": [str(path) for path in write_paths],
                "heartbeat_seconds": int(raw.get("heartbeat_seconds") or 1),
            }
        )
        if len(children) == MAX_DRYRUN_CHILDREN:
            break
    if len(children) < 2:
        raise ValueError("fixture payload must provide at least two child rows")
    return {
        "parent_packet_id": str(payload.get("parent_packet_id") or "PCKT-ION-KERNEL-FANOUT-SCHEDULER-CARRIER-DRYRUN-FIXTURE-20260514"),
        "request_id": str(payload.get("request_id") or "codex_req_kernel_fanout_carrier_dryrun_fixture_20260514"),
        "max_parallel": min(2, int(payload.get("max_parallel") or 2)),
        "artifact_root": artifact_root,
        "children": children,
    }


def _load_fixture_graph(path: Path, *, artifact_root: str) -> dict[str, Any]:
    payload = _read_json(path)
    return _graph_from_fixture_payload(payload, artifact_root=artifact_root)


def _assert_scenario_caps(graph: Mapping[str, Any], *, child_timeout_seconds: int, parent_timeout_seconds: int) -> None:
    children = graph.get("children")
    if not isinstance(children, list):
        raise ValueError("scenario graph must include children list")
    if len(children) > MAX_DRYRUN_CHILDREN:
        raise ValueError(f"scenario child count exceeds cap: {len(children)} > {MAX_DRYRUN_CHILDREN}")
    if child_timeout_seconds < 1 or child_timeout_seconds > MAX_DRYRUN_CHILD_TIMEOUT_SECONDS:
        raise ValueError(
            f"child_timeout_seconds must be within 1..{MAX_DRYRUN_CHILD_TIMEOUT_SECONDS}"
        )
    if parent_timeout_seconds < 1 or parent_timeout_seconds > MAX_DRYRUN_PARENT_TIMEOUT_SECONDS:
        raise ValueError(
            f"parent_timeout_seconds must be within 1..{MAX_DRYRUN_PARENT_TIMEOUT_SECONDS}"
        )


def _scenario_compact_summary(name: str, result: Mapping[str, Any]) -> dict[str, Any]:
    timeout_evidence = [
        finding
        for finding in result.get("blocked_findings", [])
        if isinstance(finding, Mapping) and str(finding.get("code")) in {"child_timeout", "parent_timeout"}
    ]
    deferrals = result.get("conflict_lock_observation", [])
    return {
        "scenario": name,
        "plan_verdict": result.get("plan_verdict"),
        "settlement_verdict": result.get("reducer_settlement_summary", {}).get("verdict"),
        "child_count": int(result.get("child_count") or 0),
        "max_parallel_observed": result.get("parallel_observation", {}).get("max_parallel_observed"),
        "overlap_seconds": result.get("parallel_observation", {}).get("overlap_seconds"),
        "blocked_children": result.get("reducer_settlement_summary", {}).get("blocked_children", []),
        "completed_children": result.get("reducer_settlement_summary", {}).get("completed_children", []),
        "conflict_deferred_children": result.get("reducer_settlement_summary", {}).get("conflict_deferred_children", []),
        "timeout_evidence": timeout_evidence,
        "conflict_deferral_events": sum(
            int(row.get("deferral_count") or 0) for row in deferrals if isinstance(row, Mapping)
        ),
    }


def _parent_lane_receipt(name: str, result: Mapping[str, Any], *, child_timeout_seconds: int, parent_timeout_seconds: int) -> dict[str, Any]:
    return {
        "schema_id": "ion.kernel_fanout_carrier_dryrun_parent_receipt.v1",
        "generated_at": _now(),
        "scenario": name,
        "run_id": result.get("run_id"),
        "request_id": result.get("request_id"),
        "child_timeout_seconds": child_timeout_seconds,
        "parent_timeout_seconds": parent_timeout_seconds,
        "production_authority": False,
        "live_execution_authority": False,
        "reducer_settlement_summary": result.get("reducer_settlement_summary", {}),
        "parallel_observation": result.get("parallel_observation", {}),
        "blocked_findings": result.get("blocked_findings", []),
        "child_receipt_paths": [
            {
                "child_id": row.get("child_id"),
                "lease_receipt_path": row.get("lease_receipt_path"),
                "heartbeat_receipt_path": row.get("heartbeat_receipt_path"),
                "worker_context_awareness_receipt_path": row.get("machine_signin_receipt_path"),
            }
            for row in result.get("children", [])
            if isinstance(row, Mapping)
        ],
    }


def run_kernel_fanout_carrier_dryrun(
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    fixture_graph: Mapping[str, Any] | None = None,
    accepted_signin_return: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path.cwd()
    output_root.mkdir(parents=True, exist_ok=True)

    queue_before = _queue_snapshot(root)
    base_artifact_root = "ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun/artifacts"
    success_graph = (
        _graph_from_fixture_payload(fixture_graph, artifact_root=f"{base_artifact_root}/success")
        if isinstance(fixture_graph, Mapping)
        else _default_success_graph(artifact_root=f"{base_artifact_root}/success")
    )
    success_graph["max_parallel"] = 2
    success_graph["children"] = list(success_graph.get("children", []))[:MAX_DRYRUN_CHILDREN]

    timeout_graph = copy.deepcopy(success_graph)
    timeout_graph["parent_packet_id"] = "PCKT-ION-KERNEL-FANOUT-SCHEDULER-CARRIER-DRYRUN-TIMEOUT-20260514"
    timeout_graph["request_id"] = "codex_req_kernel_fanout_carrier_dryrun_timeout_20260514"
    timeout_graph["artifact_root"] = f"{base_artifact_root}/forced_timeout"
    timeout_children: list[dict[str, Any]] = []
    for idx, child in enumerate(timeout_graph.get("children", [])):
        timeout_child = dict(child)
        timeout_child["child_id"] = f"timeout_child_{idx + 1}"
        timeout_child["depends_on"] = []
        timeout_child["write_paths"] = [f"{timeout_graph['artifact_root']}/outputs/timeout_{idx + 1}.txt"]
        timeout_children.append(timeout_child)
    timeout_graph["children"] = timeout_children

    conflict_graph = copy.deepcopy(success_graph)
    conflict_graph["parent_packet_id"] = "PCKT-ION-KERNEL-FANOUT-SCHEDULER-CARRIER-DRYRUN-CONFLICT-20260514"
    conflict_graph["request_id"] = "codex_req_kernel_fanout_carrier_dryrun_conflict_20260514"
    conflict_graph["artifact_root"] = f"{base_artifact_root}/forced_conflict"
    conflict_children: list[dict[str, Any]] = []
    conflict_path = f"{conflict_graph['artifact_root']}/outputs/conflict_shared.txt"
    for idx, child in enumerate(conflict_graph.get("children", [])):
        conflict_child = dict(child)
        conflict_child["child_id"] = f"conflict_child_{idx + 1}"
        conflict_child["depends_on"] = []
        conflict_child["write_paths"] = [conflict_path]
        conflict_children.append(conflict_child)
    conflict_graph["children"] = conflict_children

    scenarios = [
        {
            "name": "success",
            "graph": success_graph,
            "child_timeout_seconds": 4,
            "parent_timeout_seconds": 10,
            "durations": {
                str(success_graph["children"][0]["child_id"]): 1.2,
                str(success_graph["children"][1]["child_id"]): 1.0,
            },
            "expect_settlement_verdict": "SMOKE_READY",
        },
        {
            "name": "forced_timeout",
            "graph": timeout_graph,
            "child_timeout_seconds": 1,
            "parent_timeout_seconds": 10,
            "durations": {
                str(timeout_graph["children"][0]["child_id"]): 3.0,
                str(timeout_graph["children"][1]["child_id"]): 0.4,
            },
            "expect_settlement_verdict": "SMOKE_BLOCKED",
        },
        {
            "name": "forced_conflict",
            "graph": conflict_graph,
            "child_timeout_seconds": 4,
            "parent_timeout_seconds": 10,
            "durations": {
                str(conflict_graph["children"][0]["child_id"]): 1.1,
                str(conflict_graph["children"][1]["child_id"]): 0.6,
            },
            "expect_settlement_verdict": "SMOKE_READY",
        },
    ]

    scenario_rows: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for scenario in scenarios:
        name = str(scenario["name"])
        graph = dict(scenario["graph"])
        child_timeout_seconds = int(scenario["child_timeout_seconds"])
        parent_timeout_seconds = int(scenario["parent_timeout_seconds"])
        _assert_scenario_caps(
            graph,
            child_timeout_seconds=child_timeout_seconds,
            parent_timeout_seconds=parent_timeout_seconds,
        )

        scenario_dir = output_root / name
        result = simulate_kernel_fanout_true_parallel_smoke(
            graph,
            child_durations_seconds=scenario["durations"],
            child_timeout_seconds=child_timeout_seconds,
            parent_timeout_seconds=parent_timeout_seconds,
            heartbeat_interval_seconds=0.1,
            accepted_signin_return=accepted_signin_return,
            receipt_root_override=scenario_dir / "child_receipts",
        )
        result_path = scenario_dir / "result.json"
        _write_json(result_path, result)
        parent_receipt = _parent_lane_receipt(
            name,
            result,
            child_timeout_seconds=child_timeout_seconds,
            parent_timeout_seconds=parent_timeout_seconds,
        )
        parent_receipt_path = scenario_dir / "parent_receipt.json"
        _write_json(parent_receipt_path, parent_receipt)

        expected_verdict = str(scenario["expect_settlement_verdict"])
        actual_verdict = str(result.get("reducer_settlement_summary", {}).get("verdict"))
        if actual_verdict != expected_verdict:
            findings.append(
                {
                    "code": "unexpected_settlement_verdict",
                    "severity": "blocked",
                    "scenario": name,
                    "expected": expected_verdict,
                    "actual": actual_verdict,
                }
            )
        if name == "forced_timeout":
            timeout_findings = [
                row
                for row in result.get("blocked_findings", [])
                if isinstance(row, Mapping) and str(row.get("code")) == "child_timeout"
            ]
            if not timeout_findings:
                findings.append(
                    {
                        "code": "timeout_evidence_missing",
                        "severity": "blocked",
                        "scenario": name,
                    }
                )
        if name == "forced_conflict":
            deferrals = sum(
                int(row.get("deferral_count") or 0)
                for row in result.get("conflict_lock_observation", [])
                if isinstance(row, Mapping)
            )
            if deferrals <= 0:
                findings.append(
                    {
                        "code": "conflict_deferral_missing",
                        "severity": "blocked",
                        "scenario": name,
                    }
                )

        scenario_rows.append(
            {
                "scenario": name,
                "result_path": result_path.as_posix(),
                "parent_receipt_path": parent_receipt_path.as_posix(),
                "child_receipt_root": (scenario_dir / "child_receipts").as_posix(),
                "child_timeout_seconds": child_timeout_seconds,
                "parent_timeout_seconds": parent_timeout_seconds,
                "compact_summary": _scenario_compact_summary(name, result),
            }
        )

    queue_after = _queue_snapshot(root)
    before_map = {row["path"]: row for row in queue_before}
    queue_integrity = []
    queue_mutation_detected = False
    for after in queue_after:
        path = str(after["path"])
        before = before_map.get(path, {})
        unchanged = before.get("sha256") == after.get("sha256")
        if not unchanged:
            queue_mutation_detected = True
        queue_integrity.append(
            {
                "path": path,
                "before_sha256": before.get("sha256"),
                "after_sha256": after.get("sha256"),
                "unchanged": unchanged,
            }
        )

    if queue_mutation_detected:
        findings.append(
            {
                "code": "queue_mutation_detected",
                "severity": "blocked",
                "message": "live queue snapshots changed during dry-run harness",
            }
        )

    verdict = "CARRIER_DRYRUN_READY"
    if any(str(row.get("severity")) == "blocked" for row in findings):
        verdict = "CARRIER_DRYRUN_BLOCKED"

    result = {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": verdict,
        "production_authority": False,
        "live_execution_authority": False,
        "dry_run_only": True,
        "scenarios": scenario_rows,
        "queue_integrity": {
            "checked_paths": list(QUEUE_PATHS),
            "queue_mutation_detected": queue_mutation_detected,
            "rows": queue_integrity,
        },
        "child_caps": {
            "max_executable_children_per_scenario": MAX_DRYRUN_CHILDREN,
            "max_child_timeout_seconds": MAX_DRYRUN_CHILD_TIMEOUT_SECONDS,
            "max_parent_timeout_seconds": MAX_DRYRUN_PARENT_TIMEOUT_SECONDS,
        },
        "blocked_findings": findings,
    }
    result["result_sha256"] = _sha256_payload(result)
    return result


def run_default_carrier_dryrun(
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    fixture_json: Path | None = None,
    accepted_signin_return: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    fixture_graph = _load_fixture_graph(fixture_json, artifact_root="ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun/artifacts/success") if fixture_json else None
    result = run_kernel_fanout_carrier_dryrun(
        output_root=output_root,
        fixture_graph=fixture_graph,
        accepted_signin_return=accepted_signin_return,
    )
    output_path = output_root / DEFAULT_RESULT_FILENAME
    _write_json(output_path, result)
    return {
        "schema_id": RUN_RECEIPT_SCHEMA_ID,
        "result": result.get("verdict"),
        "output_path": output_path.as_posix(),
        "result_sha256": result.get("result_sha256"),
        "production_authority": False,
        "live_execution_authority": False,
        "queue_mutation_detected": result.get("queue_integrity", {}).get("queue_mutation_detected"),
        "scenario_summaries": [row.get("compact_summary", {}) for row in result.get("scenarios", [])],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run bounded kernel fanout carrier dry-run scenarios.")
    parser.add_argument("--output-root", help="Optional output root directory")
    parser.add_argument("--fixture-json", help="Optional fanout graph fixture JSON path")
    parser.add_argument("--accepted-signin-return", help="Optional accepted machine sign-in return JSON path")
    parser.add_argument("--output", help="Optional output path for receipt or result payload")
    parser.add_argument(
        "--emit-full-result",
        action="store_true",
        help="Emit full dry-run result JSON instead of compact run receipt",
    )
    args = parser.parse_args(argv)

    output_root = Path(args.output_root) if args.output_root else DEFAULT_OUTPUT_ROOT
    fixture_json = Path(args.fixture_json) if args.fixture_json else None
    accepted_signin_return = _read_json(Path(args.accepted_signin_return)) if args.accepted_signin_return else None

    if args.emit_full_result:
        fixture_graph = _load_fixture_graph(
            fixture_json,
            artifact_root="ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun/artifacts/success",
        ) if fixture_json else None
        payload = run_kernel_fanout_carrier_dryrun(
            output_root=output_root,
            fixture_graph=fixture_graph,
            accepted_signin_return=accepted_signin_return,
        )
    else:
        payload = run_default_carrier_dryrun(
            output_root=output_root,
            fixture_json=fixture_json,
            accepted_signin_return=accepted_signin_return,
        )

    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
