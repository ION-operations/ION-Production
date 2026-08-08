"""Record and proof-gate CLI task returns for the ION carrier loop.

V84 gave the parent Cursor chat a lawful spawn queue. V85 closes the other half
of the loop: every spawned Task return must be captured, checked against the
role's generated context-load receipt, recorded in an active return ledger, and
forwarded to Steward only after the context proof passes.

This module does not perform live carrier automation. It gives the carrier a
deterministic file-backed intake transaction for returns already received from
CLI workers. Prompt-spawn overrides are isolated from the unrelated active
carrier turn, ledger, and Steward queue.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_carrier_continue import ACTIVE_TURN_PACKET_RELATIVE_PATH
from .ion_carrier_onboard import resolve_shell_root_from_ion_root
from .ion_context_proof_gate import evaluate_context_proof_return_files
from .ion_cycle_runner import ACTIVE_SPAWN_PLAN_RELATIVE_PATH
from .ion_gate_registry import demote_evaluation_to_witness
from .ion_template_action_gate import evaluate_template_action_proof_file
from .ion_carrier_spawn_execution_gate import upsert_spawn_execution_proof_receipt

ACTIVE_TASK_RETURN_LEDGER_RELATIVE_PATH = Path("ION/05_context/current/ACTIVE_CARRIER_TASK_RETURN_LEDGER.json")
ACTIVE_STEWARD_INTEGRATION_QUEUE_RELATIVE_PATH = Path("ION/05_context/current/ACTIVE_STEWARD_INTEGRATION_QUEUE.json")
TASK_RETURN_CAPTURES_RELATIVE_DIR = Path("ION/05_context/current/task_returns")


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_slug(value: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:80] or "task_return"


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _spawn_context_package_is_read_only(
    shell_root: Path, row: Mapping[str, Any]
) -> bool:
    relative = Path(str(row.get("context_package_path") or ""))
    if relative.is_absolute() or ".." in relative.parts:
        return False
    package = (shell_root / relative).resolve()
    try:
        package.relative_to(shell_root.resolve())
    except ValueError:
        return False
    if not package.is_file() or package.is_symlink():
        return False
    text = package.read_text(encoding="utf-8", errors="replace").lower()
    return "read-only audit: do not write a return artifact" in text


def _load_plan(shell_root: Path) -> dict[str, Any]:
    plan_path = shell_root / ACTIVE_SPAWN_PLAN_RELATIVE_PATH
    plan = _read_json(plan_path)
    if plan is None:
        raise FileNotFoundError(f"Missing active spawn plan: {ACTIVE_SPAWN_PLAN_RELATIVE_PATH}")
    return plan


def _spawn_rows(plan: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = plan.get("role_spawn_plan", [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, Mapping) and row.get("spawn") is True]


def load_prompt_spawn_row_from_run_bundle(
    shell_root: Path,
    execution_bundle_root: str,
) -> dict[str, Any]:
    """Load an isolated prompt-spawn spawn row from a run bundle directory."""

    bundle_rel = str(execution_bundle_root or "").strip()
    if not bundle_rel:
        raise ValueError("prompt-spawn execution_bundle_root is required")
    bundle_path = Path(bundle_rel)
    if bundle_path.is_absolute() or ".." in bundle_path.parts:
        raise ValueError("prompt-spawn execution_bundle_root must be a safe root-relative path")
    run_dir = (shell_root / bundle_path).resolve()
    try:
        run_dir.relative_to(shell_root.resolve())
    except ValueError as exc:
        raise ValueError("prompt-spawn execution_bundle_root must stay under shell root") from exc
    if not run_dir.is_dir():
        raise FileNotFoundError(f"Missing prompt-spawn run bundle: {bundle_rel}")

    admission_path = run_dir / "spawn_admission.json"
    if not admission_path.is_file():
        raise FileNotFoundError(
            f"Missing prompt-spawn admission artifact: {_safe_relative(admission_path, shell_root)}"
        )
    admission = _read_json(admission_path) or {}
    if admission.get("carrier_invocation_admitted") is not True:
        raise ValueError("prompt-spawn spawn_admission.json does not admit carrier invocation")

    spawn_row_path = run_dir / "spawn_row.json"
    if not spawn_row_path.is_file():
        raise FileNotFoundError(
            f"Missing prompt-spawn spawn row artifact: {_safe_relative(spawn_row_path, shell_root)}"
        )
    row = _read_json(spawn_row_path)
    if not isinstance(row, dict):
        raise ValueError("prompt-spawn spawn_row.json must be a JSON object")

    normalized_bundle = _safe_relative(run_dir, shell_root)
    row = dict(row)
    row["execution_bundle_root"] = normalized_bundle
    row["run_id"] = str(row.get("run_id") or run_dir.name).strip() or run_dir.name
    if not str(row.get("carrier_id") or "").strip():
        row["carrier_id"] = str(admission.get("carrier_id") or "").strip() or None
    for path_key in ("context_package_path", "context_load_receipt_path"):
        member = Path(str(row.get(path_key) or ""))
        if member.is_absolute() or ".." in member.parts:
            raise ValueError(f"prompt-spawn {path_key} must be a safe root-relative path")
        if member.parent.as_posix() != normalized_bundle:
            row[path_key] = f"{normalized_bundle}/{member.name}"
    return row


def default_prompt_spawn_task_output_relative(
    shell_root: Path,
    execution_bundle_root: str,
) -> str:
    """Return the default worker output path for a prompt-spawn run bundle."""

    bundle_rel = str(execution_bundle_root or "").strip()
    bundle_path = shell_root / bundle_rel
    for name in ("output.md", "worker_output.md"):
        candidate = bundle_path / name
        if candidate.is_file():
            return _safe_relative(candidate, shell_root)
    run_json = bundle_path / "run.json"
    if run_json.is_file():
        run = _read_json(run_json) or {}
        output_rel = str(run.get("output_path") or "").strip()
        if output_rel and (shell_root / output_rel).is_file():
            return output_rel
    raise FileNotFoundError(
        f"No prompt-spawn worker output found under {bundle_rel} (expected output.md or run.json output_path)"
    )


def record_prompt_spawn_run_task_return(
    root: str | Path | None = None,
    *,
    execution_bundle_root: str,
    task_output_path: str | Path | None = None,
    task_output_text: str | None = None,
    enqueue_steward_integration: bool = True,
) -> dict[str, Any]:
    """Record one prompt-spawn-lane return without matching ACTIVE_ROLE_SPAWN_PLAN."""

    shell_root = resolve_shell_root_from_ion_root(root)
    row = load_prompt_spawn_row_from_run_bundle(shell_root, execution_bundle_root)
    resolved_output = task_output_path
    if resolved_output is None and task_output_text is None:
        resolved_output = default_prompt_spawn_task_output_relative(shell_root, row["execution_bundle_root"])
    return record_task_return(
        shell_root,
        role=str(row.get("role") or "domain_worker"),
        index=int(row.get("index") or 0),
        task_output_path=resolved_output,
        task_output_text=task_output_text,
        spawn_row_override=row,
        enqueue_steward_integration=enqueue_steward_integration,
    )


def _select_spawn_row(plan: Mapping[str, Any], *, role: str | None, index: int | None) -> Mapping[str, Any]:
    rows = _spawn_rows(plan)
    matches: list[Mapping[str, Any]] = []
    for row in rows:
        role_matches = role is None or str(row.get("role", "")).lower() == role.lower()
        index_matches = index is None or int(row.get("index", -1)) == index
        if role_matches and index_matches:
            matches.append(row)
    if not matches:
        label = f"role={role!r} index={index!r}"
        raise ValueError(f"No spawned role row matched {label}")
    if len(matches) > 1:
        label = f"role={role!r} index={index!r}"
        raise ValueError(f"Ambiguous spawned role row for {label}; provide both --role and --index")
    return matches[0]


def _read_or_capture_task_output(
    shell_root: Path,
    *,
    row: Mapping[str, Any],
    task_output_path: str | Path | None,
    task_output_text: str | None,
) -> tuple[str, Path, str]:
    if task_output_path:
        source = Path(task_output_path)
        if not source.is_absolute():
            source = shell_root / source
        text = source.read_text(encoding="utf-8", errors="replace")
        return text, source, _safe_relative(source, shell_root)

    if task_output_text is None:
        raise ValueError("Either task_output_path or task_output_text is required")

    capture_dir = shell_root / TASK_RETURN_CAPTURES_RELATIVE_DIR
    capture_dir.mkdir(parents=True, exist_ok=True)
    role = _safe_slug(str(row.get("role", "unknown")))
    index = int(row.get("index", 0))
    capture = capture_dir / f"{_iso_now().replace(':', '').replace('+', 'Z')}_{index:02d}_{role}_task_return.md"
    capture.write_text(task_output_text, encoding="utf-8")
    return task_output_text, capture, _safe_relative(capture, shell_root)


def _new_ledger(plan: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "ion.carrier_task_return_ledger.v1",
        "created_at": _iso_now(),
        "updated_at": _iso_now(),
        "active_spawn_plan_path": str(ACTIVE_SPAWN_PLAN_RELATIVE_PATH),
        "execution_bundle_root": plan.get("execution_bundle_root"),
        "records": [],
        "production_authority": False,
        "live_execution_authority": False,
    }


def _new_steward_queue(plan: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "ion.steward_integration_queue.v1",
        "created_at": _iso_now(),
        "updated_at": _iso_now(),
        "active_spawn_plan_path": str(ACTIVE_SPAWN_PLAN_RELATIVE_PATH),
        "execution_bundle_root": plan.get("execution_bundle_root"),
        "items": [],
        "production_authority": False,
        "live_execution_authority": False,
    }


def initialize_task_return_state(root: str | Path | None = None) -> dict[str, Any]:
    """Create empty V85 return ledger and Steward queue for the active spawn plan."""

    shell_root = resolve_shell_root_from_ion_root(root)
    plan = _load_plan(shell_root)

    ledger = _new_ledger(plan)
    queue = _new_steward_queue(plan)

    _write_json(shell_root / ACTIVE_TASK_RETURN_LEDGER_RELATIVE_PATH, ledger)
    _write_json(shell_root / ACTIVE_STEWARD_INTEGRATION_QUEUE_RELATIVE_PATH, queue)

    turn_path = shell_root / ACTIVE_TURN_PACKET_RELATIVE_PATH
    turn = _read_json(turn_path)
    if turn is not None:
        turn["task_return_ledger_path"] = str(ACTIVE_TASK_RETURN_LEDGER_RELATIVE_PATH)
        turn["steward_integration_queue_path"] = str(ACTIVE_STEWARD_INTEGRATION_QUEUE_RELATIVE_PATH)
        turn["return_intake_state"] = {
            "schema_id": "ion.carrier_return_intake_state.v1",
            "status": "WAITING_FOR_TASK_RETURNS",
            "accepted_count": 0,
            "rejected_count": 0,
            "pending_count": len(turn.get("spawn_queue", [])) if isinstance(turn.get("spawn_queue"), list) else 0,
            "required_action": "Record each Cursor Task worker output with kernel.ion_carrier_task_return before Steward integration.",
        }
        existing_actions = list(turn.get("carrier_next_actions", []))
        intake_action = "For each Task return, save/capture the full output and run kernel.ion_carrier_task_return against the row's receipt before integration."
        if intake_action not in existing_actions:
            existing_actions.insert(6, intake_action)
        turn["carrier_next_actions"] = existing_actions
        _write_json(turn_path, turn)

    return {
        "schema_id": "ion.carrier_task_return_state_init.v1",
        "verdict": "ION_TASK_RETURN_STATE_READY",
        "active_task_return_ledger_path": str(ACTIVE_TASK_RETURN_LEDGER_RELATIVE_PATH),
        "active_steward_integration_queue_path": str(ACTIVE_STEWARD_INTEGRATION_QUEUE_RELATIVE_PATH),
        "execution_bundle_root": plan.get("execution_bundle_root"),
        "production_authority": False,
        "live_execution_authority": False,
    }


def record_task_return(
    root: str | Path | None = None,
    *,
    role: str | None = None,
    index: int | None = None,
    task_output_path: str | Path | None = None,
    task_output_text: str | None = None,
    spawn_row_override: Mapping[str, Any] | None = None,
    enqueue_steward_integration: bool = True,
) -> dict[str, Any]:
    """Evaluate and record one CLI task return for a spawned role row."""

    shell_root = resolve_shell_root_from_ion_root(root)
    isolated_prompt_spawn = spawn_row_override is not None
    if isolated_prompt_spawn:
        row = dict(spawn_row_override)
        required_identity = ("execution_bundle_root", "run_id", "carrier_id")
        missing_identity = [key for key in required_identity if not str(row.get(key) or "").strip()]
        if missing_identity:
            raise ValueError(
                "Prompt-spawn row lacks isolated execution identity: "
                + ", ".join(missing_identity)
            )
        execution_bundle_root = str(row["execution_bundle_root"])
        bundle_path = Path(execution_bundle_root)
        if bundle_path.is_absolute() or ".." in bundle_path.parts:
            raise ValueError("Prompt-spawn execution_bundle_root must be a safe root-relative path")
        if bundle_path.name != str(row["run_id"]):
            raise ValueError("Prompt-spawn run_id must match execution_bundle_root basename")
        for path_key in ("context_package_path", "context_load_receipt_path"):
            member = Path(str(row.get(path_key) or ""))
            if member.is_absolute() or ".." in member.parts or member.parent != bundle_path:
                raise ValueError(
                    f"Prompt-spawn {path_key} must be a direct member of execution_bundle_root"
                )
        plan = {
            "schema_id": "ion.prompt_spawn_execution_plan.v1",
            "execution_bundle_root": execution_bundle_root,
            "role_spawn_plan": [{**row, "spawn": True}],
            "active_spawn_plan_path": None,
            "active_turn_packet_path": None,
        }
    else:
        plan = _load_plan(shell_root)
        row = _select_spawn_row(plan, role=role, index=index)

    receipt_rel = row.get("context_load_receipt_path")
    if not isinstance(receipt_rel, str) or not receipt_rel:
        raise ValueError(f"Spawn row lacks context_load_receipt_path: {row.get('role')}#{row.get('index')}")

    receipt_path = shell_root / receipt_rel
    if not receipt_path.exists():
        raise FileNotFoundError(f"Missing context-load receipt: {receipt_rel}")

    task_text, captured_path, captured_rel = _read_or_capture_task_output(
        shell_root,
        row=row,
        task_output_path=task_output_path,
        task_output_text=task_output_text,
    )

    raw_context_evaluation = evaluate_context_proof_return_files(
        receipt_path=receipt_path,
        task_output_path=captured_path,
    )
    read_only_return = _spawn_context_package_is_read_only(shell_root, row)
    raw_template_action_evaluation = evaluate_template_action_proof_file(
        captured_path,
        read_only=read_only_return,
    )
    raw_context_accepted = bool(raw_context_evaluation.get("accepted"))
    raw_template_action_accepted = bool(raw_template_action_evaluation.get("accepted"))
    context_evaluation = demote_evaluation_to_witness(
        shell_root,
        gate_id="gate.context_proof_return",
        evaluation=raw_context_evaluation,
    )
    template_action_evaluation = demote_evaluation_to_witness(
        shell_root,
        gate_id="gate.template_action_proof",
        evaluation=raw_template_action_evaluation,
    )
    if not raw_context_accepted:
        context_evaluation["accepted"] = False
        context_evaluation["integration_decision"] = "REJECT_RETURN_AND_RERUN_TASK"
    if not raw_template_action_accepted:
        template_action_evaluation["accepted"] = False
        template_action_evaluation["integration_decision"] = "REJECT_RETURN_AND_RERUN_OR_REPAIR"
    findings = [
        *(f"context_proof:{finding}" for finding in context_evaluation.get("findings", [])),
        *(f"template_action:{finding}" for finding in template_action_evaluation.get("findings", [])),
    ]
    accepted = (
        raw_context_accepted
        and raw_template_action_accepted
        and bool(context_evaluation.get("accepted"))
        and bool(template_action_evaluation.get("accepted"))
    )
    evaluation = {
        "schema_id": "ion.carrier_task_return_combined_evaluation.v1",
        "accepted": accepted,
        "findings": findings,
        "context_proof": context_evaluation,
        "template_action": template_action_evaluation,
        "raw_context_proof_accepted": raw_context_accepted,
        "raw_template_action_accepted": raw_template_action_accepted,
        "read_only_return": read_only_return,
        "integration_decision": "ALLOW_STEWARD_REVIEW" if accepted else "REJECT_RETURN_AND_RERUN_TASK",
        "production_authority": False,
        "live_execution_authority": False,
    }

    turn = _read_json(shell_root / ACTIVE_TURN_PACKET_RELATIVE_PATH) or {}
    carrier = str(row.get("carrier_id") or turn.get("carrier") or "unknown")

    record = {
        "schema_id": "ion.carrier_task_return_record.v1",
        "created_at": _iso_now(),
        "role": row.get("role"),
        "index": row.get("index"),
        "carrier_slot": row.get("carrier_slot"),
        "carrier_id": row.get("carrier_id"),
        "run_id": row.get("run_id"),
        "intent_id": row.get("intent_id"),
        "execution_bundle_root": plan.get("execution_bundle_root"),
        "context_package_path": row.get("context_package_path"),
        "context_load_receipt_path": receipt_rel,
        "task_output_path": captured_rel,
        "task_output_sha256": _sha256_text(task_text) if not task_output_path else _sha256_file(captured_path),
        "accepted": accepted,
        "findings": findings,
        "integration_decision": evaluation.get("integration_decision"),
        "required_paths_count": len(context_evaluation.get("required_paths", [])),
        "missing_paths_count": len(context_evaluation.get("missing_paths", [])),
        "template_id": template_action_evaluation.get("template_id"),
        "action_id": template_action_evaluation.get("action_id"),
        "touched_paths": list(template_action_evaluation.get("touched_paths", [])),
        "production_authority": False,
        "live_execution_authority": False,
    }
    record["spawn_execution_proof_path"] = upsert_spawn_execution_proof_receipt(
        shell_root,
        plan=plan,
        row=row,
        carrier=carrier,
        task_return_path=captured_rel,
        task_output_sha256=record["task_output_sha256"],
        accepted=accepted,
        intake_result={
            "status": "accepted" if accepted else "rejected",
            "context_proof_accepted": raw_context_accepted,
            "template_action_accepted": raw_template_action_accepted,
            "integration_decision": evaluation.get("integration_decision"),
            "findings": findings,
        },
    )

    if isolated_prompt_spawn:
        task_return_rel = f"{execution_bundle_root}/task_return.json"
        record["task_return_record_path"] = task_return_rel
        isolated_result = {
            "schema_id": "ion.carrier_task_return_result.v1",
            "verdict": "ION_TASK_RETURN_ACCEPTED_FOR_REVIEW" if accepted else "ION_TASK_RETURN_REJECTED_RERUN_REQUIRED",
            "accepted": accepted,
            "record": record,
            "evaluation": evaluation,
            "state_scope": "isolated_prompt_spawn_run",
            "active_carrier_state_mutated": False,
            "active_task_return_ledger_path": None,
            "active_steward_integration_queue_path": None,
            "steward_integration_requested": bool(enqueue_steward_integration),
            "steward_integration_enqueued": False,
            "production_authority": False,
            "live_execution_authority": False,
        }
        task_return_path = shell_root / task_return_rel
        if task_return_path.is_symlink():
            raise ValueError("Prompt-spawn task_return.json may not be a symlink")
        _write_json(task_return_path, isolated_result)
        return {
            **isolated_result,
            "task_return_path": task_return_rel,
            "task_return_sha256": _sha256_file(task_return_path),
        }

    ledger_path = shell_root / ACTIVE_TASK_RETURN_LEDGER_RELATIVE_PATH
    ledger = _read_json(ledger_path) or _new_ledger(plan)
    records = [item for item in ledger.get("records", []) if isinstance(item, Mapping)]
    records.append(record)
    ledger["records"] = records
    ledger["updated_at"] = _iso_now()
    ledger["execution_bundle_root"] = plan.get("execution_bundle_root")
    _write_json(ledger_path, ledger)

    queue_path = shell_root / ACTIVE_STEWARD_INTEGRATION_QUEUE_RELATIVE_PATH
    queue = _read_json(queue_path) or _new_steward_queue(plan)
    items = [item for item in queue.get("items", []) if isinstance(item, Mapping)]
    if accepted and enqueue_steward_integration:
        items.append({
            "schema_id": "ion.steward_integration_queue_item.v1",
            "created_at": record["created_at"],
            "status": "PENDING_STEWARD_INTEGRATION",
            "role": row.get("role"),
            "index": row.get("index"),
            "task_output_path": captured_rel,
            "task_output_sha256": record["task_output_sha256"],
            "context_package_path": row.get("context_package_path"),
            "context_load_receipt_path": receipt_rel,
            "template_id": record.get("template_id"),
            "action_id": record.get("action_id"),
            "touched_paths": record.get("touched_paths", []),
            "integration_instruction": "STEWARD may review and integrate this return because the context-proof and template-action gates accepted it.",
        })
    queue["items"] = items
    queue["updated_at"] = _iso_now()
    queue["execution_bundle_root"] = plan.get("execution_bundle_root")
    _write_json(queue_path, queue)

    _update_turn_intake_state(shell_root=shell_root, plan=plan, ledger=ledger, queue=queue)

    return {
        "schema_id": "ion.carrier_task_return_result.v1",
        "verdict": "ION_TASK_RETURN_ACCEPTED_FOR_STEWARD" if accepted else "ION_TASK_RETURN_REJECTED_RERUN_REQUIRED",
        "accepted": accepted,
        "record": record,
        "evaluation": evaluation,
        "state_scope": "active_carrier_turn",
        "active_carrier_state_mutated": True,
        "active_task_return_ledger_path": str(ACTIVE_TASK_RETURN_LEDGER_RELATIVE_PATH),
        "active_steward_integration_queue_path": str(ACTIVE_STEWARD_INTEGRATION_QUEUE_RELATIVE_PATH),
        "steward_integration_requested": bool(enqueue_steward_integration),
        "steward_integration_enqueued": bool(accepted and enqueue_steward_integration),
        "production_authority": False,
        "live_execution_authority": False,
    }


def _update_turn_intake_state(
    *,
    shell_root: Path,
    plan: Mapping[str, Any],
    ledger: Mapping[str, Any],
    queue: Mapping[str, Any],
) -> None:
    turn_path = shell_root / ACTIVE_TURN_PACKET_RELATIVE_PATH
    turn = _read_json(turn_path)
    if turn is None:
        return

    spawn_keys = {(str(row.get("role")), int(row.get("index", 0))) for row in _spawn_rows(plan)}
    latest_by_key: dict[tuple[str, int], Mapping[str, Any]] = {}
    for record in ledger.get("records", []):
        if not isinstance(record, Mapping):
            continue
        key = (str(record.get("role")), int(record.get("index", 0)))
        latest_by_key[key] = record

    accepted = sum(1 for key in spawn_keys if latest_by_key.get(key, {}).get("accepted") is True)
    rejected = sum(1 for key in spawn_keys if key in latest_by_key and latest_by_key[key].get("accepted") is not True)
    pending = max(0, len(spawn_keys) - accepted - rejected)

    queue_items = queue.get("items", [])
    queue_count = len(queue_items) if isinstance(queue_items, list) else 0

    turn["task_return_ledger_path"] = str(ACTIVE_TASK_RETURN_LEDGER_RELATIVE_PATH)
    turn["steward_integration_queue_path"] = str(ACTIVE_STEWARD_INTEGRATION_QUEUE_RELATIVE_PATH)
    turn["return_intake_state"] = {
        "schema_id": "ion.carrier_return_intake_state.v1",
        "status": "ALL_ACCEPTED_READY_FOR_STEWARD" if pending == 0 and rejected == 0 and accepted == len(spawn_keys) else "WAITING_OR_REJECTED_TASK_RETURNS",
        "accepted_count": accepted,
        "rejected_count": rejected,
        "pending_count": pending,
        "steward_queue_count": queue_count,
        "required_action": "Integrate accepted queue items with STEWARD; rerun rejected roles; do not ask the operator to choose agents.",
    }
    _write_json(turn_path, turn)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record and proof-gate one ION Cursor Task return.")
    parser.add_argument("--ion-root", default=None)
    parser.add_argument("--role", default=None)
    parser.add_argument("--index", type=int, default=None)
    parser.add_argument("--task-output", default=None, help="Path to captured Task output markdown/text.")
    parser.add_argument("--task-output-text", default=None, help="Literal Task output text; captured to ION/05_context/current/task_returns/.")
    parser.add_argument(
        "--prompt-spawn-run",
        default=None,
        help=(
            "Root-relative prompt-spawn execution bundle containing spawn_admission.json, "
            "spawn_row.json, and output.md (or run.json output_path)."
        ),
    )
    parser.add_argument("--init", action="store_true", help="Initialize the active return ledger and Steward integration queue only.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.init:
        result = initialize_task_return_state(args.ion_root)
    elif args.prompt_spawn_run:
        result = record_prompt_spawn_run_task_return(
            args.ion_root,
            execution_bundle_root=args.prompt_spawn_run,
            task_output_path=args.task_output,
            task_output_text=args.task_output_text,
        )
    else:
        result = record_task_return(
            args.ion_root,
            role=args.role,
            index=args.index,
            task_output_path=args.task_output,
            task_output_text=args.task_output_text,
        )

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["verdict"])
        if "record" in result:
            for finding in result["record"].get("findings", []):
                print(f"- {finding}")

    return 0 if result.get("accepted", True) or args.init else 1


if __name__ == "__main__":
    raise SystemExit(main())
