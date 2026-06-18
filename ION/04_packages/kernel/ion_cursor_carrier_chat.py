"""Cursor CLI carrier cockpit chat model and turn execution for ION.

Bounded local adapter over the existing carrier turn packet, cursor queue runner,
and proof gates. Does not grant production or live execution authority.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .ion_carrier_onboard import resolve_shell_root_from_ion_root
from .ion_context_proof_gate import evaluate_context_proof_return_files
from .ion_template_action_gate import evaluate_template_action_proof_file

SCHEMA_ID = "ion.cursor_carrier_chat_model.v1"
STATE_SCHEMA_ID = "ion.cursor_carrier_chat_state.v1"
CURRENT = Path("ION/05_context/current")
STATE_DIR = CURRENT / "cursor_carrier_chat"
STATE_PATH = STATE_DIR / "state.json"
MODEL_PATH = STATE_DIR / "model.json"
ACTIVE_TURN_PACKET_RELATIVE_PATH = Path("ION/05_context/current/ACTIVE_CARRIER_TURN_PACKET.json")
ACTIVE_SPAWN_PLAN_RELATIVE_PATH = Path("ION/05_context/current/ACTIVE_ROLE_SPAWN_PLAN.json")
CARRIER_CONTROL_PROOF_RECEIPT_RELATIVE_PATH = Path(
    "ION/05_context/current/ACTIVE_CARRIER_CONTROL_PROOF_RECEIPT.json"
)
RUNS_DIR = Path("ION/05_context/current/cursor_connector/cursor_queue_runs")
DEFAULT_CURSOR_MODEL = "composer-2.5-fast"
RECENT_RUNS_LIMIT = 20


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_root(root: str | Path | None) -> Path:
    return resolve_shell_root_from_ion_root(root)


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _spawn_rows_from_turn(turn: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in turn.get("spawn_queue") or []:
        if not isinstance(row, Mapping):
            continue
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


def _spawn_row_for_role_index(
    shell_root: Path,
    *,
    role: str,
    index: int,
) -> dict[str, Any] | None:
    turn = _read_json(shell_root / ACTIVE_TURN_PACKET_RELATIVE_PATH) or {}
    rows = _spawn_rows_from_turn(turn)
    for row in rows:
        if str(row.get("role") or "").lower() == role.lower() and int(row.get("index") or -1) == index:
            return row
    plan = _read_json(shell_root / ACTIVE_SPAWN_PLAN_RELATIVE_PATH) or {}
    for row in plan.get("role_spawn_plan") or []:
        if not isinstance(row, Mapping) or row.get("spawn") is not True:
            continue
        if str(row.get("role") or "").lower() == role.lower() and int(row.get("index") or -1) == index:
            return {
                "index": row.get("index"),
                "role": row.get("role"),
                "context_package_path": row.get("context_package_path"),
                "context_load_receipt_path": row.get("context_load_receipt_path"),
            }
    return None


def _discover_recent_runs(shell_root: Path, *, limit: int = RECENT_RUNS_LIMIT) -> list[dict[str, Any]]:
    runs_root = shell_root / RUNS_DIR
    if not runs_root.is_dir():
        return []
    entries: list[dict[str, Any]] = []
    for run_dir in runs_root.iterdir():
        if not run_dir.is_dir():
            continue
        output_path = run_dir / "output.md"
        entries.append(
            {
                "run_dir": run_dir.name,
                "output_path": _rel(shell_root, output_path) if output_path.is_file() else None,
                "output_present": output_path.is_file(),
                "mtime": output_path.stat().st_mtime if output_path.is_file() else run_dir.stat().st_mtime,
            }
        )
    entries.sort(key=lambda item: float(item.get("mtime") or 0), reverse=True)
    for item in entries:
        item.pop("mtime", None)
    return entries[:limit]


def _carrier_control_proof_summary(shell_root: Path) -> dict[str, Any] | None:
    receipt = _read_json(shell_root / CARRIER_CONTROL_PROOF_RECEIPT_RELATIVE_PATH)
    if not receipt:
        return None
    return {
        "accepted": receipt.get("accepted"),
        "integration_decision": receipt.get("integration_decision"),
        "receipt_path": CARRIER_CONTROL_PROOF_RECEIPT_RELATIVE_PATH.as_posix(),
    }


def load_cursor_carrier_chat_state(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    state = _read_json(shell_root / STATE_PATH) or {"schema_id": STATE_SCHEMA_ID, "turns": []}
    state.setdefault("turns", [])
    state.setdefault("production_authority", False)
    state.setdefault("live_execution_authority", False)
    return state


def save_cursor_carrier_chat_state(root: str | Path | None, state: Mapping[str, Any]) -> None:
    shell_root = _resolve_root(root)
    payload = dict(state)
    payload["schema_id"] = STATE_SCHEMA_ID
    payload["updated_at"] = _now()
    payload["production_authority"] = False
    payload["live_execution_authority"] = False
    _write_json(shell_root / STATE_PATH, payload)


def build_cursor_carrier_chat_model(root: str | Path | None = None, *, write: bool = False) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    turn = _read_json(shell_root / ACTIVE_TURN_PACKET_RELATIVE_PATH) or {}
    state = load_cursor_carrier_chat_state(shell_root)
    model = {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "state_path": STATE_PATH.as_posix(),
        "model_path": MODEL_PATH.as_posix(),
        "spawn_queue": _spawn_rows_from_turn(turn),
        "recent_runs": _discover_recent_runs(shell_root),
        "turns": list(state.get("turns") or [])[-40:],
        "carrier_control_proof": _carrier_control_proof_summary(shell_root),
        "production_authority": False,
        "live_execution_authority": False,
    }
    if write:
        _write_json(shell_root / MODEL_PATH, model)
    return model


def _extract_gate_results(
    runner_payload: Mapping[str, Any],
    *,
    shell_root: Path,
    output_path: Path,
    receipt_path: Path | None,
) -> tuple[bool, bool, list[str], dict[str, Any] | None, dict[str, Any] | None]:
    intake = runner_payload.get("task_return_intake")
    if isinstance(intake, Mapping):
        evaluation = intake.get("evaluation")
        if isinstance(evaluation, Mapping):
            context_eval = evaluation.get("context_proof")
            template_eval = evaluation.get("template_action")
            if isinstance(context_eval, Mapping) and isinstance(template_eval, Mapping):
                context_accepted = bool(context_eval.get("accepted"))
                template_accepted = bool(template_eval.get("accepted"))
                findings = list(evaluation.get("findings") or [])
                return context_accepted, template_accepted, findings, context_eval, template_eval

    if not output_path.is_file():
        return False, False, ["missing_output_path"], None, None
    if receipt_path is None or not receipt_path.is_file():
        template_eval = evaluate_template_action_proof_file(output_path)
        return False, bool(template_eval.get("accepted")), ["missing_context_load_receipt"], None, template_eval

    context_eval = evaluate_context_proof_return_files(
        receipt_path=receipt_path,
        task_output_path=output_path,
    )
    template_eval = evaluate_template_action_proof_file(output_path)
    context_accepted = bool(context_eval.get("accepted"))
    template_accepted = bool(template_eval.get("accepted"))
    findings = [
        *(f"context_proof:{finding}" for finding in context_eval.get("findings", [])),
        *(f"template_action:{finding}" for finding in template_eval.get("findings", [])),
    ]
    return context_accepted, template_accepted, findings, context_eval, template_eval


def _newest_output_path(shell_root: Path) -> Path | None:
    recent = _discover_recent_runs(shell_root, limit=1)
    if not recent:
        return None
    output_rel = recent[0].get("output_path")
    if not isinstance(output_rel, str) or not output_rel:
        return None
    path = shell_root / output_rel
    return path if path.is_file() else None


def run_cursor_carrier_chat_turn(
    root: str | Path | None,
    *,
    operator_message: str,
    role: str,
    index: int,
    model: str | None = None,
    record_return: bool = False,
    _runner: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    command = [
        sys.executable,
        "-m",
        "kernel.ion_cursor_queue_runner",
        "--ion-root",
        ".",
        "--process-once",
        "--role",
        role,
        "--index",
        str(index),
        "--json",
    ]
    if not record_return:
        command.append("--no-record-return")

    env = os.environ.copy()
    env["PYTHONPATH"] = "ION/04_packages"
    env["ION_CURSOR_MODEL"] = model or DEFAULT_CURSOR_MODEL

    completed = _runner(
        command,
        cwd=shell_root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    stdout = (completed.stdout or "").strip()
    runner_payload: dict[str, Any] = {}
    if stdout:
        try:
            runner_payload = json.loads(stdout)
        except json.JSONDecodeError:
            runner_payload = {"ok": False, "finding": "runner_json_parse_failed", "stdout_tail": stdout[-2000:]}

    output_rel = str(runner_payload.get("output_path") or "").strip()
    output_path = shell_root / output_rel if output_rel else None
    if output_path is None or not output_path.is_file():
        newest = _newest_output_path(shell_root)
        output_path = newest
        if output_path is not None:
            output_rel = _rel(shell_root, output_path)

    spawn_row = _spawn_row_for_role_index(shell_root, role=role, index=index) or {}
    receipt_rel = str(spawn_row.get("context_load_receipt_path") or "").strip()
    receipt_path = shell_root / receipt_rel if receipt_rel else None

    context_accepted = False
    template_accepted = False
    findings: list[str] = []
    if output_path is not None:
        context_accepted, template_accepted, findings, _, _ = _extract_gate_results(
            runner_payload,
            shell_root=shell_root,
            output_path=output_path,
            receipt_path=receipt_path,
        )
    elif runner_payload.get("finding"):
        findings.append(str(runner_payload.get("finding")))

    return {
        "operator_message": operator_message,
        "role": role,
        "index": index,
        "output_path": output_rel,
        "context_proof_accepted": context_accepted,
        "template_action_accepted": template_accepted,
        "both_accepted": context_accepted and template_accepted,
        "findings": findings,
        "runner_returncode": completed.returncode,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _html_text(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _cursor_spawn_queue_rows(spawn_queue: list[dict[str, Any]]) -> str:
    if not spawn_queue:
        return '<tr><td colspan="4">No spawn queue rows.</td></tr>'
    return "".join(
        "<tr>"
        f"<td>{_html_text(row.get('index') or 'none')}</td>"
        f"<td>{_html_text(row.get('role') or 'none')}</td>"
        f"<td><code>{_html_text(row.get('context_package_path') or 'none')}</code></td>"
        f"<td><code>{_html_text(row.get('context_load_receipt_path') or 'none')}</code></td>"
        "</tr>"
        for row in spawn_queue
    )


def _cursor_spawn_select_options(spawn_queue: list[dict[str, Any]]) -> str:
    if not spawn_queue:
        return '<option value="">(no spawn rows)</option>'
    return "".join(
        f'<option value="{_html_text(f"{row.get("role") or ""}:{row.get("index") or 0}")}">'
        f'{_html_text(f"{row.get("role") or "unknown"} @ {row.get("index") or 0}")}</option>'
        for row in spawn_queue
    )


def _cursor_recent_run_rows(recent_runs: list[dict[str, Any]]) -> str:
    if not recent_runs:
        return '<tr><td colspan="2">No recent cursor queue runs.</td></tr>'
    return "".join(
        "<tr>"
        f"<td><code>{_html_text(row.get('run_dir') or 'none')}</code></td>"
        f"<td>{_cursor_proof_badge('present' if row.get('output_present') else 'missing')}</td>"
        "</tr>"
        for row in recent_runs
    )


def _cursor_proof_badge(value: Any) -> str:
    raw = str(value if value is not None else "unknown")
    lower = raw.lower()
    if lower in {"true", "pass", "accepted", "present"}:
        kind = "ok"
    elif lower in {"false", "fail", "rejected", "missing", "blocked"}:
        kind = "bad"
    else:
        kind = "neutral"
    return f'<span class="badge badge-{kind}">{_html_text(raw)}</span>'


def _cursor_turn_cards(turns: list[dict[str, Any]]) -> str:
    if not turns:
        return '<p class="meta">No recorded turns yet.</p>'
    cards: list[str] = []
    for turn in turns:
        if not isinstance(turn, Mapping):
            continue
        turn_result = turn.get("turn_result") if isinstance(turn.get("turn_result"), Mapping) else {}
        both = turn_result.get("both_accepted")
        pass_fail = "PASS" if both is True else "FAIL" if both is False else "UNKNOWN"
        badge_kind = "ok" if both is True else "bad" if both is False else "neutral"
        findings = turn_result.get("findings") or []
        findings_html = ""
        if isinstance(findings, list) and findings:
            findings_html = (
                "<ul>"
                + "".join(f"<li><code>{_html_text(item)}</code></li>" for item in findings)
                + "</ul>"
            )
        cards.append(
            '<article class="turn-card">'
            f'<div class="turn-head"><span class="badge badge-{badge_kind}">{_html_text(pass_fail)}</span>'
            f'<span class="meta">{_html_text(turn.get("created_at") or "unknown")}</span></div>'
            f'<p><strong>operator:</strong> {_html_text(turn.get("operator_message") or "")}</p>'
            f'<p class="meta">context_proof: {_cursor_proof_badge(turn_result.get("context_proof_accepted"))} '
            f"template_action: {_cursor_proof_badge(turn_result.get('template_action_accepted'))}</p>"
            f"{findings_html}"
            "</article>"
        )
    return "".join(cards)


def _cursor_carrier_proof_label(proof: Mapping[str, Any] | None) -> str:
    if not proof:
        return "no carrier-control receipt"
    return str(proof.get("integration_decision") or "unknown")


def render_cursor_carrier_console_html(root: str | Path | None = None, *, auth_token: str | None = None) -> str:
    """Render the Cursor CLI carrier context-proof console (SSR + polling)."""

    from .ion_chatgpt_browser_mcp_http_preview import (  # noqa: PLC0415
        HELIXION_SITE_CSS,
        render_helixion_site_bar,
    )

    model = build_cursor_carrier_chat_model(root)
    spawn_queue = [row for row in model.get("spawn_queue", []) if isinstance(row, dict)]
    recent_runs = [row for row in model.get("recent_runs", []) if isinstance(row, dict)]
    turns = [row for row in model.get("turns", []) if isinstance(row, dict)]
    proof = model.get("carrier_control_proof") if isinstance(model.get("carrier_control_proof"), Mapping) else None
    proof_label = _cursor_carrier_proof_label(proof)
    proof_kind = "ok" if proof and proof.get("accepted") is True else "neutral"
    if proof and proof.get("accepted") is False:
        proof_kind = "bad"
    model_endpoint = "/cockpit/cursor/model.json"
    turn_endpoint = "/cockpit/cursor/turn"
    _ = auth_token
    safe_model = json.dumps(model)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>ION Cursor CLI Carrier</title>
  <style>
    {HELIXION_SITE_CSS}
    :root {{
      color-scheme: dark;
      --bg: #0d1013;
      --panel: #161d22;
      --line: #31404a;
      --text: #e8eef3;
      --muted: #9eb1be;
      --ok: #46d7a4;
      --warn: #f7b955;
      --bad: #ef6b77;
      --accent: #53a5ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      line-height: 1.4;
    }}
    main {{ max-width: 1280px; margin: 0 auto; padding: 24px 18px 38px; }}
    header {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 16px; align-items: start; border-bottom: 1px solid var(--line); padding-bottom: 14px; margin-bottom: 12px; }}
    h1 {{ margin: 0 0 5px; font-size: clamp(22px, 4.2vw, 42px); line-height: 1.05; font-family: "JetBrains Mono", "IBM Plex Sans", monospace; }}
    h2 {{ margin: 0 0 10px; font-size: 16px; font-family: "JetBrains Mono", "IBM Plex Sans", monospace; }}
    p {{ color: var(--muted); margin: 0 0 8px; }}
    code {{ background: #0a0e11; border: 1px solid #26323a; border-radius: 3px; color: #b9d7ff; padding: 1px 4px; overflow-wrap: anywhere; }}
    .status-badge {{ display: inline-flex; gap: 8px; align-items: center; border: 1px solid var(--line); padding: 7px 10px; border-radius: 3px; font-size: 12px; text-transform: uppercase; }}
    .status-dot {{ width: 9px; height: 9px; border-radius: 999px; }}
    .status-ok .status-dot {{ background: var(--ok); box-shadow: 0 0 12px rgba(70, 215, 164, 0.4); }}
    .status-bad .status-dot {{ background: var(--bad); box-shadow: 0 0 12px rgba(239, 107, 119, 0.4); }}
    .status-neutral .status-dot {{ background: #8da0ae; }}
    .grid {{ display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 10px; }}
    .card {{ background: linear-gradient(180deg, #182027 0%, #141b20 100%); border: 1px solid var(--line); border-radius: 4px; padding: 12px; min-height: 100%; }}
    .span-12 {{ grid-column: span 12; }}
    .span-6 {{ grid-column: span 6; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    th, td {{ border-bottom: 1px solid #2b3841; padding: 6px 5px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 700; text-transform: uppercase; font-size: 11px; }}
    .badge {{ display: inline-flex; border: 1px solid var(--line); border-radius: 999px; padding: 1px 8px; font-size: 11px; white-space: nowrap; }}
    .badge-ok {{ color: var(--ok); border-color: rgba(70, 215, 164, 0.5); }}
    .badge-bad {{ color: var(--bad); border-color: rgba(239, 107, 119, 0.6); }}
    .badge-neutral {{ color: var(--muted); }}
    .composer {{ display: grid; gap: 10px; }}
    .composer textarea, .composer input, .composer select {{
      width: 100%;
      background: #10161b;
      color: var(--text);
      border: 1px solid #34424c;
      border-radius: 3px;
      padding: 8px;
      font: inherit;
      font-size: 13px;
    }}
    .composer textarea {{ min-height: 110px; resize: vertical; }}
    .composer button {{
      justify-self: start;
      border: 1px solid #485864;
      background: #172027;
      color: var(--text);
      border-radius: 3px;
      padding: 8px 12px;
      cursor: pointer;
      font-weight: 700;
      text-transform: uppercase;
      font-size: 11px;
    }}
    .composer button:disabled {{ opacity: 0.55; cursor: not-allowed; }}
    .meta {{ font-size: 11px; color: var(--muted); }}
    .turn-card {{ border: 1px solid #2b3841; border-radius: 4px; padding: 10px; margin-bottom: 8px; background: #10161b; }}
    .turn-head {{ display: flex; justify-content: space-between; gap: 8px; margin-bottom: 6px; }}
    .turn-card ul {{ margin: 6px 0 0; padding-left: 18px; }}
    @media (max-width: 840px) {{
      header {{ grid-template-columns: 1fr; }}
      .grid {{ grid-template-columns: 1fr; }}
      .span-12, .span-6 {{ grid-column: span 1; }}
    }}
  </style>
</head>
<body data-endpoint="{_html_text(model_endpoint)}" data-turn-endpoint="{_html_text(turn_endpoint)}">
  {render_helixion_site_bar("cursor", auth_token=auth_token)}
  <main>
    <header>
      <div>
        <h1>Cursor CLI Carrier — Context Proof Console</h1>
        <p>Bounded local proof console over carrier spawn queue, cursor queue runs, and context/template gates.</p>
        <p class="meta">model: <code>{_html_text(model.get('schema_id') or 'unknown')}</code> | generated: <code id="generated-at">{_html_text(model.get("generated_at") or "none")}</code></p>
      </div>
      <div class="status-badge status-{proof_kind}" id="proof-badge"><span class="status-dot"></span><span id="proof-label">{_html_text(proof_label)}</span></div>
    </header>

    <section class="grid" aria-label="cursor carrier console">
      <article class="card span-12">
        <h2>Active Spawn Queue</h2>
        <table>
          <thead><tr><th>index</th><th>role</th><th>context package</th><th>context load receipt</th></tr></thead>
          <tbody id="spawn-queue">{_cursor_spawn_queue_rows(spawn_queue)}</tbody>
        </table>
      </article>

      <article class="card span-12">
        <h2>Turn Composer</h2>
        <form id="turn-form" class="composer">
          <label for="spawn-select">role / index</label>
          <select id="spawn-select" name="spawn">{_cursor_spawn_select_options(spawn_queue)}</select>
          <label for="operator-message">operator message</label>
          <textarea id="operator-message" name="operator_message" placeholder="Bounded operator message for this cursor-agent turn"></textarea>
          <label for="model-input">model (optional)</label>
          <input id="model-input" name="model" type="text" placeholder="composer-2.5-fast">
          <button id="turn-submit" type="submit">Run cursor-agent turn</button>
        </form>
      </article>

      <article class="card span-6">
        <h2>Recent Runs</h2>
        <table>
          <thead><tr><th>run_dir</th><th>output</th></tr></thead>
          <tbody id="recent-runs">{_cursor_recent_run_rows(recent_runs)}</tbody>
        </table>
      </article>

      <article class="card span-6">
        <h2>Turns Log</h2>
        <div id="turns-log">{_cursor_turn_cards(turns)}</div>
      </article>
    </section>
  </main>
  <script id="initial-model" type="application/json">{safe_model}</script>
  <script>
    const endpoint = document.body.dataset.endpoint;
    const turnEndpoint = document.body.dataset.turnEndpoint;
    const proofBadge = document.getElementById("proof-badge");
    const proofLabel = document.getElementById("proof-label");
    const generatedAt = document.getElementById("generated-at");
    const spawnQueueBody = document.getElementById("spawn-queue");
    const spawnSelect = document.getElementById("spawn-select");
    const recentRunsBody = document.getElementById("recent-runs");
    const turnsLog = document.getElementById("turns-log");
    const turnForm = document.getElementById("turn-form");
    const turnSubmit = document.getElementById("turn-submit");
    const operatorMessage = document.getElementById("operator-message");
    const modelInput = document.getElementById("model-input");

    function text(value) {{
      return value === undefined || value === null || value === "" ? "" : String(value);
    }}

    function esc(value) {{
      return text(value).replace(/[&<>"']/g, (ch) => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[ch]));
    }}

    function badge(value) {{
      const raw = text(value) || "unknown";
      const lower = raw.toLowerCase();
      let kind = "neutral";
      if (lower.includes("accept") || lower.includes("pass") || lower === "true" || lower === "present") kind = "ok";
      if (lower.includes("fail") || lower.includes("reject") || lower === "false" || lower === "missing" || lower.includes("block")) kind = "bad";
      return `<span class="badge badge-${{kind}}">${{esc(raw)}}</span>`;
    }}

    function renderSpawnQueue(rows) {{
      if (!Array.isArray(rows) || rows.length === 0) {{
        spawnQueueBody.innerHTML = '<tr><td colspan="4">No spawn queue rows.</td></tr>';
        spawnSelect.innerHTML = '<option value="">(no spawn rows)</option>';
        return;
      }}
      spawnQueueBody.innerHTML = rows.map((row) => `
        <tr>
          <td>${{esc(row.index)}}</td>
          <td>${{esc(row.role)}}</td>
          <td><code>${{esc(row.context_package_path || "none")}}</code></td>
          <td><code>${{esc(row.context_load_receipt_path || "none")}}</code></td>
        </tr>
      `).join("");
      const current = spawnSelect.value;
      spawnSelect.innerHTML = rows.map((row) => {{
        const value = `${{text(row.role)}}:${{text(row.index)}}`;
        const label = `${{text(row.role || "unknown")}} @ ${{text(row.index || 0)}}`;
        return `<option value="${{esc(value)}}">${{esc(label)}}</option>`;
      }}).join("");
      if (current) spawnSelect.value = current;
    }}

    function renderRecentRuns(rows) {{
      if (!Array.isArray(rows) || rows.length === 0) {{
        recentRunsBody.innerHTML = '<tr><td colspan="2">No recent cursor queue runs.</td></tr>';
        return;
      }}
      recentRunsBody.innerHTML = rows.map((row) => `
        <tr>
          <td><code>${{esc(row.run_dir || "none")}}</code></td>
          <td>${{badge(row.output_present ? "present" : "missing")}}</td>
        </tr>
      `).join("");
    }}

    function renderTurns(rows) {{
      if (!Array.isArray(rows) || rows.length === 0) {{
        turnsLog.innerHTML = '<p class="meta">No recorded turns yet.</p>';
        return;
      }}
      turnsLog.innerHTML = rows.map((turn) => {{
        const result = turn.turn_result || {{}};
        const both = result.both_accepted;
        const passFail = both === true ? "PASS" : both === false ? "FAIL" : "UNKNOWN";
        const passKind = both === true ? "ok" : both === false ? "bad" : "neutral";
        const findings = Array.isArray(result.findings) ? result.findings : [];
        const findingsHtml = findings.length
          ? `<ul>${{findings.map((item) => `<li><code>${{esc(item)}}</code></li>`).join("")}}</ul>`
          : "";
        return `
          <article class="turn-card">
            <div class="turn-head"><span class="badge badge-${{passKind}}">${{esc(passFail)}}</span><span class="meta">${{esc(turn.created_at || "unknown")}}</span></div>
            <p><strong>operator:</strong> ${{esc(turn.operator_message || "")}}</p>
            <p class="meta">context_proof: ${{badge(result.context_proof_accepted)}} template_action: ${{badge(result.template_action_accepted)}}</p>
            ${{findingsHtml}}
          </article>
        `;
      }}).join("");
    }}

    function renderProof(proof) {{
      let label = "no carrier-control receipt";
      let kind = "neutral";
      if (proof && typeof proof === "object") {{
        label = text(proof.integration_decision || "unknown");
        if (proof.accepted === true) kind = "ok";
        if (proof.accepted === false) kind = "bad";
      }}
      proofBadge.className = `status-badge status-${{kind}}`;
      proofLabel.textContent = label;
    }}

    function render(model) {{
      if (!model || typeof model !== "object") return;
      if (generatedAt) generatedAt.textContent = text(model.generated_at || "none");
      renderProof(model.carrier_control_proof || null);
      renderSpawnQueue(model.spawn_queue || []);
      renderRecentRuns(model.recent_runs || []);
      renderTurns(model.turns || []);
    }}

    async function poll() {{
      try {{
        const response = await fetch(endpoint, {{cache: "no-store", headers: {{"accept": "application/json"}}}});
        if (!response.ok) return;
        render(await response.json());
      }} catch (_error) {{}}
    }}

    turnForm.addEventListener("submit", async (event) => {{
      event.preventDefault();
      const selected = text(spawnSelect.value);
      if (!selected || !selected.includes(":")) return;
      const splitAt = selected.lastIndexOf(":");
      const role = selected.slice(0, splitAt);
      const index = Number(selected.slice(splitAt + 1));
      const payload = {{
        operator_message: text(operatorMessage.value),
        role,
        index,
      }};
      const modelValue = text(modelInput.value);
      if (modelValue) payload.model = modelValue;
      turnSubmit.disabled = true;
      try {{
        const response = await fetch(turnEndpoint, {{
          method: "POST",
          headers: {{"content-type": "application/json", "accept": "application/json"}},
          body: JSON.stringify(payload),
        }});
        if (response.ok) {{
          await poll();
        }}
      }} catch (_error) {{
      }} finally {{
        turnSubmit.disabled = false;
      }}
    }});

    const initialModel = JSON.parse(document.getElementById("initial-model").textContent || "{{}}");
    render(initialModel);
    setInterval(poll, 5000);
    poll();
  </script>
</body>
</html>
"""


def record_cursor_chat_turn(
    root: str | Path | None,
    *,
    operator_message: str,
    assistant_text: str,
    turn_result: dict[str, Any] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    state = load_cursor_carrier_chat_state(shell_root)
    turn = {
        "created_at": _now(),
        "operator_message": operator_message,
        "assistant_text": assistant_text,
        "turn_result": turn_result,
        **extra,
    }
    state.setdefault("turns", []).append(turn)
    save_cursor_carrier_chat_state(shell_root, state)
    return {"ok": True, "turn": turn, "turn_count": len(state["turns"])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ION Cursor CLI carrier cockpit chat model.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--build-model", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.build_model:
        model = build_cursor_carrier_chat_model(args.ion_root, write=True)
        if args.json:
            print(json.dumps(model, indent=2, sort_keys=True))
        else:
            print(model.get("schema_id", SCHEMA_ID))
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
