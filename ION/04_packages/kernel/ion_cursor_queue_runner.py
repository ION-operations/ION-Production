"""Bounded Cursor Agent CLI queue runner for ION carrier spawn rows.

This module is a local carrier adapter over the existing carrier turn packet and
role spawn plan. It does not create a second spawn system. The only executable
path is the fixed ``cursor-agent --print`` command for an already emitted spawn
row with a generated context package.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_carrier_onboard import resolve_shell_root_from_ion_root
from .ion_carrier_task_return import record_task_return

SCHEMA_ID = "ion.cursor_queue_runner.v1"
READY_VERDICT = "ION_CURSOR_QUEUE_RUNNER_READY"
BLOCKED_VERDICT = "ION_CURSOR_QUEUE_RUNNER_BLOCKED"
ACTIVE_TURN_PACKET_RELATIVE_PATH = Path("ION/05_context/current/ACTIVE_CARRIER_TURN_PACKET.json")
ACTIVE_SPAWN_PLAN_RELATIVE_PATH = Path("ION/05_context/current/ACTIVE_ROLE_SPAWN_PLAN.json")
CONNECTOR_DIR = Path("ION/05_context/current/cursor_connector")
RUNTIME_DIR = CONNECTOR_DIR / "runtime"
RUNS_DIR = CONNECTOR_DIR / "cursor_queue_runs"
RUNNER_STATE_PATH = RUNTIME_DIR / "cursor_queue_runner_state.json"
DEFAULT_CURSOR_BINARY = "cursor-agent"
DEFAULT_MODEL = os.environ.get("ION_CURSOR_MODEL", "composer-2.5-fast")
DEFAULT_MODE = os.environ.get("ION_CURSOR_AGENT_MODE", "")
DEFAULT_TIMEOUT_SECONDS = 3600
PROMPT_WRAPPER = (
    "You are a Cursor CLI carrier slot executing an ION generated context package.\n"
    "Do not act as the parent Cursor chat. Do not integrate as STEWARD.\n"
    "Your output MUST contain these three headings in gate-parseable plain format:\n"
    "1) ### CONTEXT PROOF first (one block per required file with path:, sha256:, line:, excerpt:).\n"
    "2) ### TEMPLATE ACTION PROOF with plain scalar lines only (NOT markdown bullets/bold):\n"
    "   template_id: <allowed template id>\n"
    "   action_id: <id>\n"
    "   result: <text>\n"
    "   touched_paths:\n"
    "   - <path>\n"
    "3) ### RESULT on its own heading with a short summary.\n"
    "Do not omit ### RESULT. Do not wrap template_id/action_id/result in ** or bullets.\n"
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _resolve_root(root: str | Path | None) -> Path:
    return resolve_shell_root_from_ion_root(root)


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _spawn_rows_from_turn(turn: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = turn.get("spawn_queue") or []
    return [row for row in rows if isinstance(row, Mapping)]


def _spawn_rows_from_plan(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in plan.get("role_spawn_plan") or []:
        if isinstance(row, Mapping) and row.get("spawn") is True:
            rows.append(
                {
                    "index": row.get("index"),
                    "role": row.get("role"),
                    "context_package_path": row.get("context_package_path"),
                    "context_load_receipt_path": row.get("context_load_receipt_path"),
                }
            )
    rows.sort(key=lambda item: int(item.get("index") or 0))
    return rows


def _human_gate_blockers(turn: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if turn.get("blocked_by_human_gate"):
        blockers.append("blocked_by_human_gate")
    for gate in turn.get("human_gates") or []:
        if isinstance(gate, Mapping) and gate.get("status") == "open":
            blockers.append(str(gate.get("id") or "open_human_gate"))
    return blockers


def _cursor_binary_ready(cursor_binary: str) -> tuple[bool, str | None]:
    path = shutil.which(cursor_binary)
    if not path:
        return False, f"cursor_binary_not_found:{cursor_binary}"
    return True, path


def _cursor_auth_status(cursor_binary: str) -> dict[str, Any]:
    command = [cursor_binary, "status", "--format", "json"]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "finding": "cursor_auth_status_failed", "error": str(exc)}
    stdout = (completed.stdout or "").strip()
    if completed.returncode != 0:
        return {
            "ok": False,
            "finding": "cursor_auth_status_nonzero",
            "returncode": completed.returncode,
            "stderr_tail": (completed.stderr or "")[-1000:],
        }
    try:
        payload = json.loads(stdout) if stdout.startswith("{") else {"raw": stdout}
    except json.JSONDecodeError:
        payload = {"raw": stdout}
    return {"ok": True, "status": payload}


def build_cursor_queue_runner_status(
    root: str | Path | None = None,
    *,
    cursor_binary: str = DEFAULT_CURSOR_BINARY,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    turn = _read_json(shell_root / ACTIVE_TURN_PACKET_RELATIVE_PATH) or {}
    plan = _read_json(shell_root / ACTIVE_SPAWN_PLAN_RELATIVE_PATH) or {}
    turn_rows = _spawn_rows_from_turn(turn)
    plan_rows = _spawn_rows_from_plan(plan)
    spawn_rows = turn_rows or plan_rows
    gate_blockers = _human_gate_blockers(turn)
    binary_ok, binary_path = _cursor_binary_ready(cursor_binary)
    auth = _cursor_auth_status(cursor_binary) if binary_ok else {"ok": False, "finding": "cursor_binary_missing"}

    blockers: list[str] = []
    if gate_blockers:
        blockers.extend(gate_blockers)
    if not binary_ok:
        blockers.append("cursor_binary_missing")
    if not auth.get("ok"):
        blockers.append("cursor_auth_unverified")

    state = _read_json(shell_root / RUNNER_STATE_PATH) or {}
    next_row = spawn_rows[0] if spawn_rows else None

    return {
        "schema_id": SCHEMA_ID,
        "verdict": READY_VERDICT if not blockers else BLOCKED_VERDICT,
        "generated_at": _now(),
        "turn_packet_path": ACTIVE_TURN_PACKET_RELATIVE_PATH.as_posix(),
        "spawn_plan_path": ACTIVE_SPAWN_PLAN_RELATIVE_PATH.as_posix(),
        "runner_state_path": RUNNER_STATE_PATH.as_posix(),
        "spawn_row_count": len(spawn_rows),
        "next_spawn_row": next_row,
        "blocked_by": blockers,
        "cursor_binary": cursor_binary,
        "cursor_binary_path": binary_path,
        "cursor_auth": auth,
        "default_model": DEFAULT_MODEL,
        "default_mode": DEFAULT_MODE,
        "latest_run": state.get("latest_run"),
        "production_authority": False,
        "live_execution_authority": False,
    }


def _select_spawn_row(
    rows: list[dict[str, Any]],
    *,
    role: str | None,
    index: int | None,
) -> dict[str, Any]:
    if not rows:
        raise ValueError("No spawn rows available")
    if role is None and index is None:
        return rows[0]
    matches = []
    for row in rows:
        role_ok = role is None or str(row.get("role", "")).lower() == role.lower()
        index_ok = index is None or int(row.get("index") or -1) == index
        if role_ok and index_ok:
            matches.append(row)
    if not matches:
        raise ValueError(f"No spawn row matched role={role!r} index={index!r}")
    if len(matches) > 1:
        raise ValueError(f"Ambiguous spawn row for role={role!r} index={index!r}")
    return matches[0]


def _safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:80] or "cursor_run"


def _build_cursor_command(
    *,
    cursor_binary: str,
    model: str,
    mode: str,
    force: bool,
) -> list[str]:
    command = [cursor_binary, "--print", "--output-format", "text", "--model", model]
    if mode:
        command.extend(["--mode", mode])
    if force:
        command.extend(["--force", "--trust"])
    return command


def process_cursor_queue_once(
    root: str | Path | None = None,
    *,
    role: str | None = None,
    index: int | None = None,
    cursor_binary: str = DEFAULT_CURSOR_BINARY,
    model: str | None = None,
    mode: str | None = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    force: bool = True,
    dry_run: bool = False,
    record_return: bool = True,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    status = build_cursor_queue_runner_status(shell_root, cursor_binary=cursor_binary)
    if status.get("verdict") != READY_VERDICT:
        return {
            **status,
            "ok": False,
            "result": "BLOCKED",
            "finding": "cursor_queue_runner_blocked",
        }

    turn = _read_json(shell_root / ACTIVE_TURN_PACKET_RELATIVE_PATH) or {}
    plan = _read_json(shell_root / ACTIVE_SPAWN_PLAN_RELATIVE_PATH) or {}
    rows = _spawn_rows_from_turn(turn) or _spawn_rows_from_plan(plan)
    row = _select_spawn_row(rows, role=role, index=index)

    package_rel = str(row.get("context_package_path") or "").strip()
    if not package_rel:
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": "BLOCKED",
            "finding": "missing_context_package_path",
            "spawn_row": row,
        }

    package_path = shell_root / package_rel
    if not package_path.is_file():
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": "BLOCKED",
            "finding": "context_package_missing",
            "context_package_path": package_rel,
            "spawn_row": row,
        }

    prompt = PROMPT_WRAPPER + "\n" + package_path.read_text(encoding="utf-8", errors="replace")
    chosen_model = model or DEFAULT_MODEL
    chosen_mode = mode if mode is not None else DEFAULT_MODE
    command = _build_cursor_command(
        cursor_binary=cursor_binary,
        model=chosen_model,
        mode=chosen_mode,
        force=force,
    )

    run_id = f"cursor_run_{_now().replace(':', '').replace('+00:00', 'Z')}_{_safe_slug(str(row.get('role')))}"
    run_dir = shell_root / RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = run_dir / "prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    run_packet: dict[str, Any] = {
        "schema_id": "ion.cursor_queue_run.v1",
        "run_id": run_id,
        "generated_at": _now(),
        "spawn_row": row,
        "context_package_path": package_rel,
        "prompt_path": _rel(shell_root, prompt_path),
        "command": command,
        "model": chosen_model,
        "mode": chosen_mode,
        "dry_run": dry_run,
        "production_authority": False,
        "live_execution_authority": False,
    }

    if dry_run:
        run_packet["result"] = "DRY_RUN"
        run_packet["ok"] = True
        _write_json(run_dir / "run.json", run_packet)
        _write_json(
            shell_root / RUNNER_STATE_PATH,
            {"schema_id": "ion.cursor_queue_runner_state.v1", "updated_at": _now(), "latest_run": run_packet},
        )
        return run_packet

    completed = subprocess.run(
        [*command, prompt],
        cwd=shell_root,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    output_path = run_dir / "output.md"
    output_text = completed.stdout or ""
    if completed.stderr:
        output_text += "\n\n--- stderr ---\n" + completed.stderr
    output_path.write_text(output_text, encoding="utf-8")

    run_packet.update(
        {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "output_path": _rel(shell_root, output_path),
            "stderr_tail": (completed.stderr or "")[-2000:],
        }
    )
    _write_json(run_dir / "run.json", run_packet)
    _write_json(
        shell_root / RUNNER_STATE_PATH,
        {"schema_id": "ion.cursor_queue_runner_state.v1", "updated_at": _now(), "latest_run": run_packet},
    )

    if record_return and completed.returncode == 0:
        try:
            intake = record_task_return(
                shell_root,
                role=str(row.get("role") or ""),
                index=int(row.get("index") or 0),
                task_output_path=_rel(shell_root, output_path),
            )
            run_packet["task_return_intake"] = intake
        except Exception as exc:  # noqa: BLE001 - surface intake failure on run packet
            run_packet["task_return_intake_error"] = str(exc)

    return run_packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ION bounded Cursor Agent CLI queue runner.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--process-once", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--role", default=None)
    parser.add_argument("--index", type=int, default=None)
    parser.add_argument("--cursor-binary", default=DEFAULT_CURSOR_BINARY)
    parser.add_argument("--model", default=None)
    parser.add_argument("--mode", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--no-record-return", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.process_once:
        result = process_cursor_queue_once(
            args.ion_root,
            role=args.role,
            index=args.index,
            cursor_binary=args.cursor_binary,
            model=args.model,
            mode=args.mode,
            timeout_seconds=args.timeout_seconds,
            dry_run=args.dry_run,
            record_return=not args.no_record_return,
        )
        ok = bool(result.get("ok"))
    else:
        result = build_cursor_queue_runner_status(args.ion_root, cursor_binary=args.cursor_binary)
        ok = result.get("verdict") == READY_VERDICT

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result.get("verdict") or result.get("result") or ("OK" if ok else "BLOCKED"))
        if result.get("finding"):
            print(f"- {result['finding']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
