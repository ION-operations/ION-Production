"""Scope-native ION cockpit projection and HTML renderer.

This is a candidate evolution surface that unifies objective spine, scope graph,
Team Comms operational graph, kernel scheduler projection, progress lanes, gates,
context stack, proof, change ledger, and timeline.

It is read-only: no production, live execution, or accepted-state authority.
"""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Mapping

SCHEMA_ID = "ion.scope_cockpit_projection.v1"
HTML_SCHEMA_ID = "ion.scope_cockpit_html.v1"


def _shell_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "ION/05_context").exists():
            return path
        if (path / "05_context").exists() and (path / "REPO_AUTHORITY.md").exists():
            return path.parent
    return candidate


def _e(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    if value is None:
        return []
    return [value]


def _load_agent_count(root: Path) -> int:
    path = root / "ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return 0
    try:
        return int(payload.get("agent_count") or len(payload.get("agents") or []))
    except Exception:
        return 0


def _progress_lane(label: str, value: int, basis: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "label": label,
        "value": max(0, min(100, int(value))),
        "basis": dict(basis),
    }


def _scope_stack(selected_thread_id: str) -> list[dict[str, Any]]:
    return [
        {
            "scope_id": "northstar.ion",
            "scope_type": "NORTHSTAR",
            "title": "ION Long Horizon Operating Room",
            "parent_scope_id": "",
            "indent": 0,
            "summary": "Sovereign intent, current phase, cross-domain routing, accepted-state map.",
        },
        {
            "scope_id": "domain.agent_communication_systems",
            "scope_type": "DOMAIN",
            "title": "Agent Communication Systems",
            "parent_scope_id": "northstar.ion",
            "indent": 1,
            "summary": "Visible agent communication substrate, room contracts, directive pickup, chain proof.",
        },
        {
            "scope_id": "project.team_comms_vnext",
            "scope_type": "PROJECT",
            "title": "Team Comms vNext",
            "parent_scope_id": "domain.agent_communication_systems",
            "indent": 2,
            "summary": "Turn agent Discord into an ION-native operational graph.",
        },
        {
            "scope_id": "mission.team_comms.operational_graph_projection",
            "scope_type": "MISSION",
            "title": "Operational Graph Projection",
            "parent_scope_id": "project.team_comms_vnext",
            "indent": 3,
            "summary": "Unify messages, agents, domains, context, scheduler, workpacks, returns, receipts, and lifecycle.",
        },
        {
            "scope_id": f"thread.{selected_thread_id}",
            "scope_type": "THREAD",
            "title": "Selected Team Comms Workroom",
            "parent_scope_id": "mission.team_comms.operational_graph_projection",
            "indent": 4,
            "summary": selected_thread_id,
        },
    ]


def _objective_spine(scheduler_projection: Mapping[str, Any], operational_graph: Mapping[str, Any]) -> dict[str, Any]:
    candidates = int(scheduler_projection.get("candidate_count") or 0)
    blocking = int(scheduler_projection.get("blocking_factor_count") or 0)
    proof_state = str((operational_graph.get("proof_projection") or {}).get("proof_state") or "CANDIDATE")
    plan_value = 46
    schedule_value = 22 if candidates else 8
    proof_value = 35 if proof_state not in {"CANDIDATE_RETURN", "CANDIDATE"} else 12
    accepted_value = 0
    return {
        "schema_id": "ion.scope_objective_spine.v1",
        "objective": {
            "statement": "Make Team Comms an ION-native operational graph.",
            "why_now": "The current substrate has durable comms and receipts, but the UI needs explicit objective, scheduler, context, proof, and accepted-state meaning.",
            "northstar_alignment": "Turn long-horizon human intent into accepted state through domain-aware agents, shaped context, bounded work, visible scheduling, and proof.",
        },
        "success_shape": {
            "success_type": "HYBRID",
            "definition": "Every Team Comms thread can be viewed as objective → route → context → scheduler → work → proof → accepted-state impact.",
            "criteria": [
                {"criterion_id": "route_ribbon", "label": "Route ribbon visible", "state": "PARTIAL"},
                {"criterion_id": "thread_lifecycle", "label": "Thread lifecycle visible", "state": "PARTIAL"},
                {"criterion_id": "scheduler_projection", "label": "Kernel scheduler projection integrated", "state": "ACTIVE"},
                {"criterion_id": "context_stack", "label": "Context stack visible", "state": "PARTIAL"},
                {"criterion_id": "accepted_state_boundary", "label": "Candidate vs accepted state visible", "state": "PLANNED"},
            ],
        },
        "completion_mode": {
            "mode": "HYBRID",
            "finite_end_condition": "Projection accepted into cockpit with proof.",
            "recurring_responsibility": "Domain continues stewardship and drift watch.",
        },
        "current_phase": {
            "phase_id": "phase.scheduler_projection",
            "label": "Kernel Scheduler Projection",
            "state": "ACTIVE",
            "summary": "Expose what can move, what is blocked, what is in flight, and what future candidates exist without turning the cockpit into the scheduler.",
        },
        "progress_lanes": [
            _progress_lane("Plan", plan_value, {"phases_complete": 2, "phases_total": 8}),
            _progress_lane("Schedule", schedule_value, {"candidate_count": candidates, "blocking_factor_count": blocking}),
            _progress_lane("Proof", proof_value, {"thread_proof_state": proof_state}),
            _progress_lane("Accepted State", accepted_value, {"accepted_state_receipts": 0}),
        ],
        "trajectory": {
            "status": "ACTIVE",
            "trajectory": "ADVANCING_WITH_SCOPE_EXPANSION",
            "confidence": "MEDIUM_HIGH",
            "summary": "Conceptual shape is clear; implementation remains candidate until proof and acceptance.",
        },
        "next_lawful_move": {
            "move_type": "CREATE_WORKPACK",
            "label": "Build operational graph projection compiler",
            "why": "Scope, scheduler, and thread graph requirements are now explicit enough for a first implementation slice.",
            "requires_acceptance_gate": True,
        },
    }


def _phase_plan() -> dict[str, Any]:
    return {
        "schema_id": "ion.scope_phase_plan.v1",
        "version": 3,
        "current_phase_id": "phase.scheduler_projection",
        "original_phase_count": 5,
        "current_phase_count": 8,
        "phases": [
            {"phase_id": "phase.problem_framing", "label": "Problem Framing", "state": "COMPLETE", "original": True},
            {"phase_id": "phase.scope_ontology", "label": "Scope Ontology", "state": "COMPLETE", "original": True},
            {"phase_id": "phase.scheduler_projection", "label": "Kernel Scheduler Projection", "state": "ACTIVE", "original": False, "added_after_start": True},
            {"phase_id": "phase.operational_graph_schema", "label": "Operational Graph Schema", "state": "PLANNED", "original": True},
            {"phase_id": "phase.thread_lifecycle", "label": "Thread Lifecycle", "state": "PLANNED", "original": False, "added_after_start": True},
            {"phase_id": "phase.ui_prototype", "label": "UI Prototype", "state": "PARTIAL", "original": True},
            {"phase_id": "phase.implementation", "label": "Implementation", "state": "PLANNED", "original": True},
            {"phase_id": "phase.acceptance", "label": "Proof + Acceptance", "state": "PLANNED", "original": True},
        ],
    }


def _gates() -> list[dict[str, Any]]:
    return [
        {
            "gate_id": "gate.scheduler_projection_review",
            "label": "Scheduler Projection Review",
            "gate_type": "SCHEDULER",
            "state": "OPEN",
            "required": True,
            "summary": "Confirm UI distinguishes phase, scheduler, execution, proof, and accepted-state timelines.",
        },
        {
            "gate_id": "gate.implementation_proof",
            "label": "Implementation Proof",
            "gate_type": "IMPLEMENTATION",
            "state": "PENDING",
            "required": True,
            "summary": "Projection compiler must emit deterministic UI-safe JSON and pass smoke validation.",
        },
        {
            "gate_id": "gate.visual_proof",
            "label": "Visual Proof",
            "gate_type": "VISUAL_PROOF",
            "state": "PENDING",
            "required": True,
            "summary": "Cockpit view must be visually verified after implementation.",
        },
        {
            "gate_id": "gate.accepted_state_receipt",
            "label": "Accepted-State Receipt",
            "gate_type": "ACCEPTANCE",
            "state": "PENDING",
            "required": True,
            "summary": "Candidate output does not become durable product state without accepted-state receipt.",
        },
    ]


def _change_ledger() -> list[dict[str, Any]]:
    return [
        {
            "change_id": "change.added_scheduler_projection_phase",
            "change_type": "PHASE_ADDED",
            "summary": "Added Kernel Scheduler Projection as an explicit phase.",
            "reason": "The cockpit must show what should move next, what is blocked, and what is in flight.",
            "impact": "Reduces confusion between mission phase, scheduler state, execution, proof, and accepted state.",
        },
        {
            "change_id": "change.split_progress_lanes",
            "change_type": "SUCCESS_SHAPE_CHANGED",
            "summary": "Split progress into Plan / Schedule / Proof / Accepted State lanes.",
            "reason": "A single progress percent would misrepresent candidate work as accepted state.",
            "impact": "Progress is more honest and inspectable.",
        },
    ]


def _timeline_events(operational_graph: Mapping[str, Any], scheduler_projection: Mapping[str, Any]) -> list[dict[str, Any]]:
    events = [
        {"lane": "OBJECTIVE", "label": "Objective framed", "summary": "Team Comms vNext needs scope-aware objective/progress/proof semantics."},
        {"lane": "OBJECTIVE", "label": "Scheduler phase added", "summary": "Kernel scheduler projection became a first-class cockpit lane."},
    ]
    selected = scheduler_projection.get("selected_candidate") if isinstance(scheduler_projection.get("selected_candidate"), Mapping) else None
    if selected:
        events.append(
            {
                "lane": "SCHEDULER",
                "label": str(selected.get("candidate_title") or "Scheduler candidate selected"),
                "summary": f"{selected.get('scheduler_state')} / {selected.get('commitment')} / {selected.get('selected_carrier')}",
            }
        )
    for message in _as_list(operational_graph.get("messages"))[:6]:
        if isinstance(message, Mapping):
            events.append(
                {
                    "lane": "EXECUTION",
                    "label": f"{message.get('from_role')} / {message.get('message_kind')}",
                    "summary": str(message.get("summary") or "")[:180],
                }
            )
    proof = operational_graph.get("proof_projection") if isinstance(operational_graph.get("proof_projection"), Mapping) else {}
    events.append({"lane": "PROOF", "label": str(proof.get("proof_state") or "Proof pending"), "summary": f"{proof.get('proof_ref_count', 0)} proof refs"})
    events.append({"lane": "ACCEPTED_STATE", "label": "Acceptance pending", "summary": "No accepted-state receipt is attached to this projection."})
    return events


def build_scope_cockpit_model(
    root: str | Path | None = None,
    *,
    thread_id: str | None = None,
) -> dict[str, Any]:
    shell_root = _shell_root(root)
    from .ion_agent_comms import build_agent_comms_projection
    from .ion_agent_comms_operational_graph import build_agent_comms_thread_operational_graph
    from .ion_scope_scheduler_projection import build_scope_scheduler_projection

    operational_graph = build_agent_comms_thread_operational_graph(shell_root, thread_id=thread_id)
    selected_thread_id = str(operational_graph.get("thread_id") or thread_id or "")
    scheduler_projection = build_scope_scheduler_projection(
        shell_root,
        scope_type="MISSION",
        scope_ref="mission.team_comms.operational_graph_projection",
        fallback_to_global=True,
    )
    try:
        comms_projection = build_agent_comms_projection(shell_root, limit=80)
    except Exception as exc:
        comms_projection = {"ok": False, "finding": "agent_comms_projection_failed", "error": exc.__class__.__name__}

    timeline_events = _timeline_events(operational_graph, scheduler_projection)
    proof_projection = operational_graph.get("proof_projection")
    context_matryoshka = operational_graph.get("context_segments")
    objective_spine = _objective_spine(scheduler_projection, operational_graph)
    phase_plan = _phase_plan()
    return {
        "schema_id": SCHEMA_ID,
        "ok": True,
        "selected_scope_id": "mission.team_comms.operational_graph_projection",
        "selected_thread_id": selected_thread_id,
        "shell_root": str(shell_root),
        "summary": {
            "agent_count": _load_agent_count(shell_root),
            "thread_count": (comms_projection.get("summary") or {}).get("thread_count", 0) if isinstance(comms_projection.get("summary"), Mapping) else 0,
            "scheduler_candidate_count": scheduler_projection.get("candidate_count", 0),
            "proof_state": (operational_graph.get("proof_projection") or {}).get("proof_state") if isinstance(operational_graph.get("proof_projection"), Mapping) else "",
        },
        "scope_stack": _scope_stack(selected_thread_id),
        "objective_spine": objective_spine,
        "phase_rail": objective_spine.get("current_phase") if isinstance(objective_spine.get("current_phase"), Mapping) else {},
        "progress_lanes": objective_spine.get("progress_lanes") if isinstance(objective_spine.get("progress_lanes"), list) else [],
        "phase_plan": phase_plan,
        "gates": _gates(),
        "change_ledger": _change_ledger(),
        "scheduler_projection": scheduler_projection,
        "thread_operational_graph": operational_graph,
        "agent_comms_projection_summary": comms_projection.get("summary", {}),
        "context_matryoshka": context_matryoshka if isinstance(context_matryoshka, list) else [],
        "proof_projection": proof_projection if isinstance(proof_projection, Mapping) else {},
        "timeline": timeline_events,
        "timeline_events": timeline_events,
        "policy": [
            "Scope cockpit is a projection; it does not mutate scheduler, comms, execution, or accepted state.",
            "Messages, scheduler candidates, and returns remain candidate until proof and acceptance gates settle them.",
        ],
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _pill(text: Any, tone: str = "") -> str:
    return f'<span class="pill {tone}">{_e(text)}</span>'


def _progress_bar(row: Mapping[str, Any]) -> str:
    value = max(0, min(100, int(row.get("value") or 0)))
    return (
        '<div class="progress-row">'
        f'<div><b>{_e(row.get("label"))}</b><span>{value}%</span></div>'
        f'<div class="bar"><i style="width:{value}%"></i></div>'
        f'<code>{_e(json.dumps(row.get("basis") or {}, sort_keys=True))}</code>'
        '</div>'
    )


def _render_scope_stack(scopes: list[Mapping[str, Any]], selected_id: str) -> str:
    cards = []
    for scope in scopes:
        indent = int(scope.get("indent") or 0)
        active = " active" if scope.get("scope_id") == selected_id else ""
        cards.append(
            f'<article class="scope-card indent-{indent}{active}">'
            f'<div class="scope-kind">{_e(scope.get("scope_type"))}</div>'
            f'<b>{_e(scope.get("title"))}</b>'
            f'<p>{_e(scope.get("summary"))}</p>'
            '</article>'
        )
    return "".join(cards)


def _render_phase_plan(phase_plan: Mapping[str, Any]) -> str:
    html_parts = []
    for phase in _as_list(phase_plan.get("phases")):
        if not isinstance(phase, Mapping):
            continue
        state = str(phase.get("state") or "PLANNED").lower()
        inserted = " inserted" if phase.get("added_after_start") else ""
        html_parts.append(
            f'<div class="phase {state}{inserted}">'
            f'<span>{_e(phase.get("label"))}</span>'
            f'<b>{_e(phase.get("state"))}</b>'
            '</div>'
        )
    return '<div class="phase-rail">' + "".join(html_parts) + "</div>"


def _render_scheduler(model: Mapping[str, Any]) -> str:
    scheduler = model.get("scheduler_projection") if isinstance(model.get("scheduler_projection"), Mapping) else {}
    summary = scheduler.get("summary") if isinstance(scheduler.get("summary"), Mapping) else {}
    selected = scheduler.get("selected_candidate") if isinstance(scheduler.get("selected_candidate"), Mapping) else None
    chips = "".join(_pill(f"{key}: {value}", "green" if key in {"ready", "in_flight"} and value else "amber" if value else "") for key, value in summary.items() if value)
    if not chips:
        chips = _pill("no active scheduler candidates", "amber")
    selected_html = ""
    if selected:
        selected_html = (
            '<div class="candidate selected">'
            f'<div class="eyebrow">selected candidate</div>'
            f'<h3>{_e(selected.get("candidate_title"))}</h3>'
            f'<p>{_e(selected.get("candidate_summary"))}</p>'
            f'<div class="chips">{_pill(selected.get("scheduler_state"), "green")}{_pill(selected.get("commitment"), "cyan")}{_pill(selected.get("selected_carrier"), "blue")}</div>'
            f'<p class="muted">{_e(selected.get("reason"))}</p>'
            '</div>'
        )
    candidates = []
    for row in _as_list(scheduler.get("candidates"))[:8]:
        if isinstance(row, Mapping):
            candidates.append(
                '<div class="candidate">'
                f'<b>{_e(row.get("candidate_title"))}</b>'
                f'<span>{_e(row.get("scheduler_state"))} / {_e(row.get("commitment"))} / {_e(row.get("selected_carrier"))}</span>'
                '</div>'
            )
    return (
        '<section class="panel">'
        '<header><b>Kernel Scheduler Projection</b><span>motion layer</span></header>'
        '<div class="chips">' + chips + '</div>'
        f'{selected_html}'
        '<div class="candidate-list">' + "".join(candidates) + '</div>'
        '</section>'
    )


def _render_thread_graph(model: Mapping[str, Any]) -> str:
    graph = model.get("thread_operational_graph") if isinstance(model.get("thread_operational_graph"), Mapping) else {}
    messages = [m for m in _as_list(graph.get("messages")) if isinstance(m, Mapping)]
    lifecycle = graph.get("thread_lifecycle") if isinstance(graph.get("thread_lifecycle"), Mapping) else {}
    followup = graph.get("followup_contract") if isinstance(graph.get("followup_contract"), Mapping) else {}
    context_segments = [c for c in _as_list(graph.get("context_segments")) if isinstance(c, Mapping)]
    message_html = "".join(
        '<article class="message">'
        f'<div><b>{_e(message.get("from_role"))}</b><span>{_e(message.get("created_at"))}</span></div>'
        f'<p>{_e(message.get("summary"))}</p>'
        f'<footer>{_pill(message.get("message_kind"), "cyan")}</footer>'
        '</article>'
        for message in messages
    )
    context_html = "".join(
        '<div class="context-layer">'
        f'<b>{_e(segment.get("label"))}</b><p>{_e(segment.get("summary"))}</p><span>{_e(segment.get("state"))}</span>'
        '</div>'
        for segment in context_segments
    )
    return (
        '<section class="grid two">'
        '<div class="panel"><header><b>Thread Workroom</b><span>agent comms</span></header>'
        f'<div class="chips">{_pill("Lifecycle: " + str(lifecycle.get("state") or "unknown"), "green")}{_pill("Follow-up: " + str(followup.get("state") or "unknown"), "cyan")}</div>'
        f'{message_html or "<p class=muted>No selected messages.</p>"}'
        '</div>'
        '<div class="panel"><header><b>Context Matryoshka</b><span>safe projection</span></header>'
        f'{context_html}'
        '</div>'
        '</section>'
    )


def _render_gates_and_changes(model: Mapping[str, Any]) -> str:
    gates = [g for g in _as_list(model.get("gates")) if isinstance(g, Mapping)]
    changes = [c for c in _as_list(model.get("change_ledger")) if isinstance(c, Mapping)]
    gates_html = "".join(
        '<div class="gate">'
        f'<b>{_e(gate.get("label"))}</b><span>{_e(gate.get("state"))}</span><p>{_e(gate.get("summary"))}</p>'
        '</div>'
        for gate in gates
    )
    change_html = "".join(
        '<div class="change">'
        f'<b>{_e(change.get("summary"))}</b><span>{_e(change.get("change_type"))}</span><p>{_e(change.get("reason"))}</p>'
        '</div>'
        for change in changes
    )
    return (
        '<section class="grid two">'
        '<div class="panel"><header><b>Expected Gates</b><span>proof path</span></header>' + gates_html + '</div>'
        '<div class="panel"><header><b>Change Ledger</b><span>expectation history</span></header>' + change_html + '</div>'
        '</section>'
    )


def _render_timeline(model: Mapping[str, Any]) -> str:
    events = [event for event in _as_list(model.get("timeline_events")) if isinstance(event, Mapping)]
    return (
        '<section class="panel"><header><b>Four-Lane Timeline</b><span>objective / scheduler / execution / proof / accepted state</span></header>'
        + "".join(
            '<div class="event">'
            f'<span>{_e(event.get("lane"))}</span><b>{_e(event.get("label"))}</b><p>{_e(event.get("summary"))}</p>'
            '</div>'
            for event in events
        )
        + '</section>'
    )


def render_scope_cockpit_html(model: Mapping[str, Any]) -> str:
    objective = (model.get("objective_spine") or {}).get("objective") if isinstance(model.get("objective_spine"), Mapping) else {}
    objective_spine = model.get("objective_spine") if isinstance(model.get("objective_spine"), Mapping) else {}
    progress_lanes = [row for row in _as_list(objective_spine.get("progress_lanes")) if isinstance(row, Mapping)]
    selected_scope = str(model.get("selected_scope_id") or "")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ION Scope Cockpit</title>
<style>
:root {{
  --bg:#050706; --panel:#0a0f0c; --panel2:#0f1712; --line:#1f3029; --line2:#2d4c40;
  --text:#d8e6dd; --muted:#7b8b82; --green:#00ff75; --cyan:#2df7ff; --amber:#f8c646; --blue:#7aa7ff; --red:#ff4e6d;
  --mono:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace;
}}
*{{box-sizing:border-box}} body{{margin:0;background:radial-gradient(circle at 20% 0,rgba(0,255,117,.12),transparent 32vw),var(--bg);color:var(--text);font-family:var(--mono);}}
.app{{height:100vh;display:grid;grid-template-columns:320px 1fr 360px;grid-template-rows:42px 1fr 34px;}}
.top{{grid-column:1/4;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:10px;padding:0 12px;background:#070a08}}
.top b{{color:var(--green);letter-spacing:.12em}} .top span{{color:var(--muted);font-size:11px}}
.left{{border-right:1px solid var(--line);overflow:auto;padding:10px;background:rgba(5,7,6,.75)}} .main{{overflow:auto;padding:12px}} .right{{border-left:1px solid var(--line);overflow:auto;padding:10px;background:rgba(5,7,6,.75)}}
.scope-card{{border:1px solid var(--line);padding:9px;margin-bottom:7px;background:rgba(10,15,12,.82)}} .scope-card.active{{border-color:var(--green);box-shadow:inset 3px 0 0 var(--green)}} .scope-card b{{display:block;color:#f0fff4;font-size:11px;margin-top:4px}} .scope-card p{{margin:5px 0 0;color:var(--muted);font-size:9px;line-height:1.4}} .scope-kind{{font-size:9px;color:var(--green);letter-spacing:.1em}} .indent-1{{margin-left:14px}} .indent-2{{margin-left:28px}} .indent-3{{margin-left:42px}} .indent-4{{margin-left:56px}}
.hero{{border:1px solid var(--line);background:linear-gradient(180deg,rgba(0,255,117,.06),rgba(0,0,0,.15));padding:14px;margin-bottom:12px}} h1{{margin:0;color:#f0fff4;font-size:20px;letter-spacing:.07em;text-transform:uppercase}} .hero p{{color:var(--muted);line-height:1.5;font-size:12px;max-width:1100px}}
.pill{{display:inline-block;border:1px solid var(--line2);padding:3px 7px;margin:2px;color:var(--muted);font-size:9px;text-transform:uppercase}} .pill.green{{color:var(--green);border-color:rgba(0,255,117,.45)}} .pill.cyan{{color:var(--cyan);border-color:rgba(45,247,255,.45)}} .pill.amber{{color:var(--amber);border-color:rgba(248,198,70,.45)}} .pill.blue{{color:var(--blue);border-color:rgba(122,167,255,.45)}}
.grid.two{{display:grid;grid-template-columns:1fr 1fr;gap:12px}} .panel{{border:1px solid var(--line);background:rgba(10,15,12,.84);padding:10px;margin-bottom:12px}} .panel header{{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);margin:-10px -10px 10px;padding:9px 10px;background:rgba(255,255,255,.02)}} .panel header b{{font-size:11px;color:#f0fff4;text-transform:uppercase}} .panel header span{{font-size:9px;color:var(--muted);text-transform:uppercase}}
.phase-rail{{display:flex;gap:6px;overflow:auto;margin:10px 0 12px}} .phase{{min-width:130px;border:1px solid var(--line);padding:7px;background:#08100c}} .phase.complete{{border-color:rgba(0,255,117,.45)}} .phase.active{{border-color:rgba(45,247,255,.65)}} .phase.inserted{{border-style:dashed}} .phase span{{display:block;color:#eafbf0;font-size:10px}} .phase b{{display:block;color:var(--muted);font-size:8px;margin-top:5px}}
.progress-row{{border:1px solid var(--line);padding:8px;margin-bottom:7px;background:rgba(0,0,0,.16)}} .progress-row>div:first-child{{display:flex;justify-content:space-between}} .progress-row b{{color:#effff4;font-size:10px}} .progress-row span{{color:var(--green);font-size:10px}} .bar{{height:7px;border:1px solid var(--line2);margin:6px 0;background:#050806}} .bar i{{display:block;height:100%;background:linear-gradient(90deg,var(--green),var(--cyan))}} code{{display:block;color:var(--muted);font-size:8px;white-space:pre-wrap;overflow-wrap:anywhere}}
.candidate,.message,.gate,.change,.event,.context-layer{{border:1px solid var(--line);background:rgba(0,0,0,.18);padding:8px;margin-bottom:7px}} .candidate h3{{margin:4px 0;color:#f0fff4;font-size:13px}} .candidate b,.message b,.gate b,.change b,.event b,.context-layer b{{color:#effff4;font-size:10px}} .candidate span,.message span,.gate span,.change span,.event span,.context-layer span{{color:var(--muted);font-size:8px;text-transform:uppercase}} .candidate p,.message p,.gate p,.change p,.event p,.context-layer p{{color:var(--muted);font-size:10px;line-height:1.45;margin:6px 0}}
.chips{{margin-bottom:8px}} .muted{{color:var(--muted)!important}} .bottom{{grid-column:1/4;border-top:1px solid var(--line);display:flex;align-items:center;gap:12px;padding:0 10px;color:var(--muted);font-size:9px;text-transform:uppercase}} .bottom b{{color:var(--green)}}
@media(max-width:1200px){{.app{{grid-template-columns:280px 1fr}}.right{{display:none}}.top,.bottom{{grid-column:1/3}}.grid.two{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="app" data-schema="{_e(HTML_SCHEMA_ID)}">
<header class="top"><b>ION SCOPE COCKPIT</b><span>objective + scheduler + comms + proof projection</span>{_pill('read-only','green')}{_pill('no accepted-state authority','amber')}</header>
<aside class="left">
  <h3 style="margin:0 0 10px;color:#f0fff4;font-size:12px;text-transform:uppercase">Scope Stack</h3>
  {_render_scope_stack([s for s in _as_list(model.get("scope_stack")) if isinstance(s, Mapping)], selected_scope)}
</aside>
<main class="main">
  <section class="hero">
    <h1>{_e(objective.get("statement"))}</h1>
    <p>{_e(objective.get("why_now"))}</p>
    <div>{_pill('phase: ' + str((objective_spine.get('current_phase') or {}).get('label') or ''), 'cyan')}{_pill('trajectory: ' + str((objective_spine.get('trajectory') or {}).get('trajectory') or ''), 'green')}</div>
  </section>
  <section class="panel"><header><b>Phase Rail</b><span>original + inserted phases</span></header>{_render_phase_plan(model.get("phase_plan") if isinstance(model.get("phase_plan"), Mapping) else {})}</section>
  <section class="grid two"><div class="panel"><header><b>Progress Lanes</b><span>plan / schedule / proof / accepted state</span></header>{"".join(_progress_bar(row) for row in progress_lanes)}</div>{_render_scheduler(model)}</section>
  {_render_thread_graph(model)}
  {_render_gates_and_changes(model)}
  {_render_timeline(model)}
</main>
<aside class="right">
  <section class="panel"><header><b>Why This Exists</b><span>inspector</span></header>
    <p class="muted">{_e(objective.get("northstar_alignment"))}</p>
    <div class="chips">{_pill('production: false')}{_pill('live execution: false')}{_pill('accepted state: false')}</div>
  </section>
  <section class="panel"><header><b>Next Lawful Move</b><span>scheduler-informed</span></header>
    <h3 style="margin:0;color:#f0fff4">{_e((objective_spine.get('next_lawful_move') or {}).get('label'))}</h3>
    <p class="muted">{_e((objective_spine.get('next_lawful_move') or {}).get('why'))}</p>
  </section>
  <section class="panel"><header><b>Raw Model</b><span>debug</span></header><code>{_e(json.dumps(model, indent=2, sort_keys=True)[:10000])}</code></section>
</aside>
<footer class="bottom"><span><b>projection</b> read-only</span><span><b>scheduler</b> motion layer</span><span><b>proof</b> not accepted state</span></footer>
</div>
</body>
</html>"""
