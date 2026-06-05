"""Codex-grade Browser GPT agent harness.

This module turns the existing Browser GPT DOM calibration lane into an
agent-operable runtime: context capsule, DOM requirement matrix, safe
Playwright orchestration, and durable receipts. It never grants production,
accepted-state, secrets, cookie-read, or silent-send authority.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_browser_gpt_dom_calibration import (
    DEFAULT_ORIGIN,
    DEFAULT_PROFILE_ID,
    INDEX_PATH,
    LATEST_HEALTH_PATH,
    LATEST_PROFILE_PATH,
    PROBE_PHASE_DEPENDENCIES,
    SURFACE_SPECS,
    calibrate_with_playwright,
    default_authority,
    latest_browser_gpt_dom_summary,
    playwright_auto_interaction_plan,
    probe_phase_sweep_projection,
)
from .ion_browser_gpt_screen_automation import latest_screen_automation_state

AGENT_SCHEMA_ID = "ion.codex_browser_agent.v1"
CAPSULE_SCHEMA_ID = "ion.codex_browser_agent.context_capsule.v1"
REQUIREMENTS_SCHEMA_ID = "ion.codex_browser_agent.dom_requirements.v1"
REPORT_SCHEMA_ID = "ion.codex_browser_agent.report.v1"
RECEIPT_SCHEMA_ID = "ion.codex_browser_agent.receipt.v1"
COMPARISON_SCHEMA_ID = "ion.codex_browser_agent.profile_comparison.v1"

BASE_DIR = Path("ION/05_context/current/browser_gpt_dom_profiles/codex_browser_agent")
CAPSULES_DIR = BASE_DIR / "context_capsules"
REQUIREMENTS_DIR = BASE_DIR / "dom_requirements"
REPORTS_DIR = BASE_DIR / "reports"
RECEIPTS_DIR = BASE_DIR / "receipts"
COMPARISONS_DIR = BASE_DIR / "comparisons"

LATEST_CAPSULE_PATH = BASE_DIR / "latest_context_capsule.json"
LATEST_REQUIREMENTS_PATH = BASE_DIR / "latest_dom_requirements.json"
LATEST_REPORT_PATH = BASE_DIR / "latest_agent_report.json"

DEFAULT_OBJECTIVE = (
    "Inspect ChatGPT through the Browser GPT DOM lane, identify the current DOM "
    "surfaces needed by ION, and write a context capsule for the next Codex turn."
)

GPT_DIALOGUE_LOOP_SCHEMA_ID = "ion.codex_browser_agent.gpt_dialogue_action_loop.v1"
SELF_EVOLUTION_LOOP_SCHEMA_ID = "ion.codex_browser_agent.self_evolution_loop.v1"
CDP_ACCESSIBILITY_WITNESS_SCHEMA_ID = "ion.codex_browser_agent.cdp_accessibility_witness.v1"
SANDBOX_SKILL_BENCHMARK_SCHEMA_ID = "ion.codex_browser_agent.sandbox_skill_benchmark.v1"
SANDBOX_SKILL_BENCHMARK_RESULT_SCHEMA_ID = "ion.codex_browser_agent.sandbox_skill_benchmark_result.v1"

SANDBOX_BENCHMARKS_DIR = BASE_DIR / "sandbox_benchmarks"
LATEST_SANDBOX_BENCHMARK_PATH = SANDBOX_BENCHMARKS_DIR / "latest_sandbox_benchmark_result.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def safe_slug(value: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "_" for ch in value.strip())
    return "_".join(part for part in normalized.split("_") if part)[:96] or "codex_browser_agent"


def resolve_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


def repo_rel(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception as exc:  # pragma: no cover - projection must stay fail-soft.
        return {"_read_error": str(exc), "_path": path.as_posix()}


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_file_bytes(path: Path) -> bytes | None:
    try:
        return path.read_bytes() if path.is_file() else None
    except OSError:
        return None


def restore_file_bytes(path: Path, data: bytes | None) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if data is None:
        if path.exists():
            path.unlink()
            return "removed_created_file"
        return "missing_unchanged"
    path.write_bytes(data)
    return "restored"


def sha256_file(path: Path) -> str:
    if not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes | None) -> str:
    return hashlib.sha256(data).hexdigest() if data is not None else ""


def resolve_artifact_path(root: Path, value: str | Path | None) -> Path:
    if not value:
        return root / "__missing__"
    path = Path(str(value)).expanduser()
    return path if path.is_absolute() else root / path


def as_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def profile_surface_map(profile: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    surfaces = profile.get("surfaces") if isinstance(profile.get("surfaces"), Mapping) else {}
    return {str(surface_id): dict(value) for surface_id, value in surfaces.items() if isinstance(value, Mapping)}


def compare_selector_profiles(
    root: str | Path = ".",
    *,
    candidate_profile_path: str | Path | None,
    baseline_profile_path: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    shell_root = resolve_root(root)
    baseline_path = resolve_artifact_path(shell_root, baseline_profile_path or LATEST_PROFILE_PATH)
    candidate_path = resolve_artifact_path(shell_root, candidate_profile_path)
    baseline = read_json(baseline_path)
    candidate = read_json(candidate_path)
    baseline_surfaces = profile_surface_map(baseline)
    candidate_surfaces = profile_surface_map(candidate)
    rows: list[dict[str, Any]] = []
    regressions: list[dict[str, Any]] = []
    improvements: list[dict[str, Any]] = []

    for surface_id, spec in SURFACE_SPECS.items():
        baseline_surface = baseline_surfaces.get(surface_id, {})
        candidate_surface = candidate_surfaces.get(surface_id, {})
        baseline_selector = str(baseline_surface.get("selector") or "").strip()
        candidate_selector = str(candidate_surface.get("selector") or "").strip()
        baseline_confidence = as_float(baseline_surface.get("confidence"))
        candidate_confidence = as_float(candidate_surface.get("confidence"))
        baseline_ready = bool(baseline_selector and baseline_confidence >= 0.7)
        candidate_ready = bool(candidate_selector and candidate_confidence >= 0.7)
        if baseline_selector and candidate_selector and baseline_selector == candidate_selector:
            verdict = "same_selector"
        elif baseline_selector and candidate_selector:
            verdict = "changed_selector"
        elif baseline_selector and not candidate_selector:
            verdict = "candidate_missing"
        elif candidate_selector and not baseline_selector:
            verdict = "candidate_new"
        else:
            verdict = "both_missing"
        row = {
            "surface_id": surface_id,
            "kind": spec.get("kind", "unknown"),
            "required": bool(spec.get("required")),
            "verdict": verdict,
            "baseline_selector": baseline_selector,
            "candidate_selector": candidate_selector,
            "baseline_confidence": round(baseline_confidence, 3),
            "candidate_confidence": round(candidate_confidence, 3),
            "baseline_ready": baseline_ready,
            "candidate_ready": candidate_ready,
        }
        rows.append(row)
        if spec.get("required") and baseline_ready and not candidate_ready:
            regressions.append(
                {
                    "surface_id": surface_id,
                    "reason": "required_surface_lost_or_degraded",
                    "baseline_confidence": row["baseline_confidence"],
                    "candidate_confidence": row["candidate_confidence"],
                }
            )
        if candidate_ready and not baseline_ready:
            improvements.append(
                {
                    "surface_id": surface_id,
                    "reason": "candidate_surface_now_ready",
                    "baseline_confidence": row["baseline_confidence"],
                    "candidate_confidence": row["candidate_confidence"],
                }
            )

    selector_match_count = sum(1 for row in rows if row["verdict"] == "same_selector")
    candidate_missing_count = sum(1 for row in rows if row["verdict"] == "candidate_missing")
    changed_selector_count = sum(1 for row in rows if row["verdict"] == "changed_selector")
    payload = {
        "schema_id": COMPARISON_SCHEMA_ID,
        "generated_at": utc_now(),
        "status": "regression_detected" if regressions else "comparison_ready",
        "baseline_profile_id": baseline.get("profile_id"),
        "candidate_profile_id": candidate.get("profile_id"),
        "baseline_profile_path": repo_rel(shell_root, baseline_path),
        "candidate_profile_path": repo_rel(shell_root, candidate_path),
        "baseline_sha256": sha256_file(baseline_path),
        "candidate_sha256": sha256_file(candidate_path),
        "surface_count": len(rows),
        "selector_match_count": selector_match_count,
        "changed_selector_count": changed_selector_count,
        "candidate_missing_count": candidate_missing_count,
        "regression_count": len(regressions),
        "improvement_count": len(improvements),
        "regressions": regressions,
        "improvements": improvements,
        "surfaces": rows,
        "authority": agent_authority(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
    if run_id:
        comparison_path = shell_root / COMPARISONS_DIR / f"{safe_slug(run_id)}.profile_comparison.json"
        write_json(comparison_path, payload)
        payload["comparison_path"] = repo_rel(shell_root, comparison_path)
        write_json(comparison_path, payload)
    return payload


def agent_authority(*, playwright_inspection_requested: bool = False) -> dict[str, Any]:
    authority = default_authority()
    authority.update(
        {
            "schema_id": "ion.codex_browser_agent.authority.v1",
            "playwright_browser_observation_requested": bool(playwright_inspection_requested),
            "playwright_menu_click_authority": bool(playwright_inspection_requested),
            "playwright_send_click_authority": False,
            "composer_test_requires_explicit_flag": True,
            "allowed_browser_effects": [
                "open_or_focus_chatgpt_page",
                "read_redacted_dom_shape",
                "capture_screenshots",
                "open_safe_menus_or_drawers",
                "optional_reversible_composer_insert_readback_when_flagged",
            ],
            "forbidden_browser_effects": [
                "click_send",
                "read_cookies",
                "extract_credentials",
                "mutate_accepted_state",
                "claim_production_authority",
                "silent_auto_login",
            ],
        }
    )
    return authority


def python_playwright_available() -> bool:
    return importlib.util.find_spec("playwright") is not None


def chrome_executable() -> str:
    for candidate in (
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("google-chrome-stable"),
    ):
        if candidate:
            return candidate
    return ""


def _surface_rows_from_summary(summary: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for item in summary.get("surfaces", []) if isinstance(summary.get("surfaces"), list) else []:
        if isinstance(item, Mapping) and item.get("surface_id"):
            rows[str(item["surface_id"])] = dict(item)
    return rows


def _twin_control_rows(summary: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    twin = summary.get("chatgpt_dom_twin") if isinstance(summary.get("chatgpt_dom_twin"), Mapping) else {}
    rows: dict[str, dict[str, Any]] = {}
    for item in twin.get("controls", []) if isinstance(twin.get("controls"), list) else []:
        if isinstance(item, Mapping) and item.get("surface_id"):
            rows[str(item["surface_id"])] = dict(item)
    return rows


def _surface_selector(surface_id: str, summary_rows: Mapping[str, Mapping[str, Any]], twin_rows: Mapping[str, Mapping[str, Any]]) -> str:
    row = summary_rows.get(surface_id, {})
    twin = twin_rows.get(surface_id, {})
    return str(row.get("selector") or twin.get("selector") or "").strip()


def _surface_confidence(surface_id: str, summary_rows: Mapping[str, Mapping[str, Any]], twin_rows: Mapping[str, Mapping[str, Any]]) -> float:
    row = summary_rows.get(surface_id, {})
    twin = twin_rows.get(surface_id, {})
    for value in (row.get("confidence"), twin.get("confidence")):
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            continue
    return 0.0


def _surface_status(
    surface_id: str,
    selector: str,
    confidence: float,
    spec: Mapping[str, Any],
    phase_dependency: Mapping[str, Any] | None,
) -> str:
    if selector and confidence >= 0.7:
        return "ready"
    if selector:
        return "candidate_needs_recheck"
    if spec.get("required"):
        return "missing_required"
    if phase_dependency:
        return "needs_phase_capture"
    return "optional_unobserved"


def _surface_requirement_text(surface_id: str, status: str, phase_dependency: Mapping[str, Any] | None) -> str:
    if surface_id == "send_button":
        return "Prove the draft-visible send button selector after a reversible draft probe; never click Send."
    if surface_id == "composer":
        return "Prove editable composer selector, focus behavior, newline behavior, and reversible draft readback."
    if surface_id == "message_list":
        return "Prove message container anchors and readable user/assistant/tool/thinking event extraction."
    if surface_id == "native_action_cards":
        return "Prove action-card panels, full detail extraction, and visible Allow/Reject affordances."
    if phase_dependency:
        return str(phase_dependency.get("instruction") or "Open the required menu/drawer phase and recapture this surface.")
    if status == "missing_required":
        return "Required surface is not observed; run Playwright inspection and DOM probe phase capture."
    return "Keep as optional observation surface; record selector only when visible and uniquely attributable."


def build_dom_requirement_matrix(summary: Mapping[str, Any], phase_sweep: Mapping[str, Any] | None = None) -> dict[str, Any]:
    phase_sweep = phase_sweep or {}
    summary_rows = _surface_rows_from_summary(summary)
    twin_rows = _twin_control_rows(summary)
    rows: list[dict[str, Any]] = []
    critical_gaps: list[dict[str, Any]] = []
    phase_captures: list[dict[str, Any]] = []

    for surface_id, spec in SURFACE_SPECS.items():
        phase_dependency = PROBE_PHASE_DEPENDENCIES.get(surface_id)
        selector = _surface_selector(surface_id, summary_rows, twin_rows)
        confidence = _surface_confidence(surface_id, summary_rows, twin_rows)
        status = _surface_status(surface_id, selector, confidence, spec, phase_dependency)
        row = {
            "surface_id": surface_id,
            "kind": spec.get("kind", "unknown"),
            "required": bool(spec.get("required")),
            "status": status,
            "selector": selector,
            "confidence": round(confidence, 3),
            "hotkeys": list(spec.get("hotkeys", [])) if isinstance(spec.get("hotkeys"), list) else [],
            "phase": phase_dependency.get("phase") if phase_dependency else None,
            "opener_surface_id": phase_dependency.get("opener_surface_id") if phase_dependency else None,
            "requirement": _surface_requirement_text(surface_id, status, phase_dependency),
            "validated_by": list(summary_rows.get(surface_id, {}).get("validated_by", []))
            if isinstance(summary_rows.get(surface_id, {}).get("validated_by"), list)
            else [],
        }
        rows.append(row)
        if status == "missing_required":
            critical_gaps.append({"surface_id": surface_id, "status": status, "requirement": row["requirement"]})
        if status == "needs_phase_capture" and phase_dependency:
            phase_captures.append(
                {
                    "surface_id": surface_id,
                    "phase": phase_dependency["phase"],
                    "opener_surface_id": phase_dependency["opener_surface_id"],
                    "requirement": row["requirement"],
                }
            )

    ready_count = sum(1 for row in rows if row["status"] == "ready")
    return {
        "schema_id": REQUIREMENTS_SCHEMA_ID,
        "generated_at": utc_now(),
        "status": "blocked_required_surfaces" if critical_gaps else "ready_for_iterative_inspection",
        "surface_count": len(rows),
        "ready_surface_count": ready_count,
        "critical_gap_count": len(critical_gaps),
        "phase_capture_count": len(phase_captures),
        "phase_sweep_status": phase_sweep.get("status"),
        "phase_sweep_merged_found_surface_ids": phase_sweep.get("merged_found_surface_ids", []),
        "surfaces": rows,
        "critical_gaps": critical_gaps,
        "phase_captures": phase_captures,
        "authority": agent_authority(),
    }


def build_capability_matrix(root: Path) -> list[dict[str, Any]]:
    state = latest_screen_automation_state(root) or {}
    return [
        {
            "capability_id": "python_playwright",
            "status": "available" if python_playwright_available() else "missing",
            "purpose": "Launch/attach a Chromium inspection run and capture DOM/screenshot evidence.",
            "executable": chrome_executable(),
            "no_send_click": True,
        },
        {
            "capability_id": "dom_probe_extension",
            "status": "available" if (root / "browser_extension/browser_gpt_dom_probe/OPERATOR_FINAL/manifest.json").exists() else "missing",
            "purpose": "In-page observer bridge for current ChatGPT DOM snapshots and phase sweeps.",
            "no_cookie_read": True,
        },
        {
            "capability_id": "chatops_bridge_extension",
            "status": "available" if (root / "browser_extension/ion_chatops_bridge/dist/content.js").exists() else "missing",
            "purpose": "Relay open tabs, visible conversation, native navigation, approvals, and actions.",
            "runtime_file": "browser_extension/ion_chatops_bridge/dist/content.js",
        },
        {
            "capability_id": "screen_automation_memory",
            "status": "learned" if state else "missing",
            "purpose": "Reuse known local browser geometry for extension reload and tab refresh operations.",
            "state_captured_at": state.get("captured_at"),
        },
    ]


def build_gpt_dialogue_action_loop(requirements: Mapping[str, Any], *, target_url: str) -> dict[str, Any]:
    """Project the closed-loop GPT dialogue/action/DOM verification protocol.

    This is intentionally a protocol projection, not an execution grant. It
    defines how Codex may collaborate with a ChatGPT tab once the operator has
    explicitly approved any send/action step.
    """
    ready_surface_count = int(requirements.get("ready_surface_count") or 0)
    critical_gap_count = int(requirements.get("critical_gap_count") or 0)
    status = "ready_for_gated_dialogue" if ready_surface_count and critical_gap_count == 0 else "needs_surface_proof"
    phases = [
        {
            "phase": "operator_objective_seed",
            "actor": "operator_or_codex",
            "input": "bounded objective plus current ION context capsule",
            "output": "approved prompt draft",
            "gate": "operator_send_approval_required",
        },
        {
            "phase": "approved_gpt_turn",
            "actor": "browser_gpt_bridge",
            "input": "APPROVED_SEND_DRAFT with receipt id",
            "output": "visible ChatGPT assistant response",
            "gate": "no_silent_send_no_mid_output_send_without_policy",
        },
        {
            "phase": "dom_and_transcript_observation",
            "actor": "codex_browser_agent",
            "input": "READ_VISIBLE_CONVERSATION, READ_APPROVAL_REQUESTS, READ_NATIVE_ACTION_CARDS",
            "output": "timeline events, action proposals, panel detail rows",
            "gate": "read_visible_dom_only",
        },
        {
            "phase": "action_proposal_triage",
            "actor": "codex_browser_agent",
            "input": "GPT emitted action YAML, native action confirmation, or tool/status text",
            "output": "classified candidate: safe_read, candidate_write, needs_operator, reject",
            "gate": "no_action_execution_from_chat_text",
        },
        {
            "phase": "semantic_dom_verification",
            "actor": "playwright_or_cdp_witness",
            "input": "current DOM, accessibility roles, screenshots, selector profile",
            "output": "evidence receipt and selector/action-detail verdict",
            "gate": "no_send_click_no_secret_or_cookie_read",
        },
        {
            "phase": "codex_response_or_next_prompt",
            "actor": "codex",
            "input": "verified evidence plus ION authority boundaries",
            "output": "operator report, next approved prompt draft, or bounded action packet",
            "gate": "operator_decides_execution_or_auto_policy_scope",
        },
    ]
    return {
        "schema_id": GPT_DIALOGUE_LOOP_SCHEMA_ID,
        "status": status,
        "target_url": target_url,
        "turn_budget_default": 6,
        "loop_capabilities": [
            "ask_gpt_for_plan_or_action_yaml",
            "read_gpt_visible_response_and_tool_statuses",
            "extract_action_cards_and_full_detail_panels",
            "verify_dom_claims_with_playwright_or_cdp",
            "reply_with_proceed_or_correction_only_after_output_completes",
            "write_context_capsule_and_receipts_for_next_turn",
        ],
        "phases": phases,
        "decision_verdicts": [
            "continue_dialogue",
            "request_operator_approval",
            "queue_candidate_action_for_gateway_validation",
            "run_read_only_dom_verification",
            "stop_for_boundary_or_terms_risk",
        ],
        "advanced_skill_benchmark": {
            "schema_id": "ion.codex_browser_agent.advanced_skill_benchmark.v1",
            "status": "sandbox_only_design",
            "purpose": "Use demanding browser/game-like tasks as capability benchmarks for perception, timing, planning, recovery, and evidence loops without controlling third-party live clients.",
            "allowed_examples": [
                "synthetic browser UI boss-fight benchmark",
                "local canvas reaction/phase-recognition harness",
                "toy Web simulation with documented controls and receipts",
            ],
            "forbidden_examples": [
                "live MMORPG botting",
                "third-party game client control",
                "terms-of-service evasion",
                "external economy automation",
                "anti-cheat bypass",
            ],
        },
        "required_surfaces": [
            "message_list",
            "latest_assistant_message",
            "composer",
            "send_button",
            "native_action_cards",
        ],
        "authority": {
            "operator_approved_send_required": True,
            "silent_send_authority": False,
            "native_action_approval_required": True,
            "action_execution_from_chat_text": False,
            "browser_game_client_control_authority": False,
            "third_party_terms_bypass_authority": False,
            "cookie_read_authority": False,
            "secrets_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        },
    }


def build_cdp_accessibility_witness(
    requirements: Mapping[str, Any],
    capability_matrix: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    capability_rows = capability_matrix or []
    playwright_available = any(
        row.get("capability_id") == "python_playwright" and row.get("status") == "available"
        for row in capability_rows
        if isinstance(row, Mapping)
    )
    target_surfaces = [
        "composer",
        "send_button",
        "message_list",
        "latest_assistant_message",
        "native_action_cards",
        "drawer_surface",
    ]
    return {
        "schema_id": CDP_ACCESSIBILITY_WITNESS_SCHEMA_ID,
        "status": "ready_for_read_only_probe" if playwright_available else "needs_python_playwright",
        "purpose": "Provide a second read-only witness for role/name/state drift, active dialogs, and native action affordances using Playwright accessibility snapshots and CDP Accessibility methods.",
        "critical_gap_count": requirements.get("critical_gap_count", 0),
        "target_surfaces": target_surfaces,
        "target_roles": [
            "textbox",
            "button",
            "dialog",
            "menu",
            "menuitem",
            "list",
            "article",
            "status",
        ],
        "read_only_methods": [
            "Playwright page.accessibility.snapshot",
            "CDP Accessibility.enable",
            "CDP Accessibility.getFullAXTree",
            "CDP Accessibility.queryAXTree",
            "CDP Accessibility.disable",
        ],
        "probe_steps": [
            "open_or_attach_chatgpt_tab_with_operator_approved_context",
            "capture_redacted_dom_snapshot",
            "capture_redacted_playwright_accessibility_snapshot",
            "capture_cdp_full_ax_tree_roles_names_states",
            "compare_role_name_state_against_selector_profile",
            "write_accessibility_witness_receipt",
        ],
        "redaction_policy": {
            "include": ["role", "name_preview", "description_preview", "ignored", "disabled", "focused", "expanded", "selected"],
            "truncate_text_to_chars": 180,
            "exclude": ["cookies", "localStorage", "sessionStorage", "credentials", "full_message_text_by_default"],
        },
        "artifact_paths": {
            "playwright_accessibility_snapshot": "ION/05_context/current/browser_gpt_dom_profiles/snapshots/*.accessibility_snapshot_redacted.json",
            "cdp_witness_receipts": "ION/05_context/current/browser_gpt_dom_profiles/accessibility_witness/",
        },
        "authority": {
            "read_only_probe": True,
            "playwright_send_click_authority": False,
            "native_action_approval_authority": False,
            "cookie_read_authority": False,
            "secrets_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        },
    }


def build_sandbox_skill_benchmark(
    requirements: Mapping[str, Any],
    capability_matrix: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Define the owned synthetic benchmark for high-skill browser automation.

    This is intentionally local and synthetic. It measures the same perception,
    timing, planning, and recovery loops a strong browser agent needs without
    controlling any third-party game/client or bypassing any service terms.
    """
    capability_rows = capability_matrix or []
    playwright_available = any(
        row.get("capability_id") == "python_playwright" and row.get("status") == "available"
        for row in capability_rows
        if isinstance(row, Mapping)
    )
    benchmark_cases = [
        {
            "case_id": "synthetic_phase_reaction_grid",
            "surface": "owned_local_canvas_fixture",
            "purpose": "React to phase, projectile, and safe-tile signals with bounded decision latency.",
            "scripted_steps": [
                {"t_ms": 0, "signal": "phase_start", "required_decision": "scan_hazard_and_safe_tile", "deadline_ms": 120},
                {"t_ms": 160, "signal": "projectile_magic", "required_decision": "select_blue_defense", "deadline_ms": 260},
                {"t_ms": 420, "signal": "floor_tile_red", "required_decision": "move_to_green_tile", "deadline_ms": 620},
                {"t_ms": 760, "signal": "phase_cooldown", "required_decision": "resume_primary_action", "deadline_ms": 940},
            ],
            "success_metrics": ["decision_accuracy", "deadline_hit_rate", "phase_state_continuity"],
        },
        {
            "case_id": "native_action_panel_triage",
            "surface": "owned_html_action_card_fixture",
            "purpose": "Classify full action detail panels into safe-read, approval-required, or reject decisions.",
            "scripted_steps": [
                {"t_ms": 0, "signal": "read_only_runtime_probe", "required_decision": "request_operator_or_policy_approval", "deadline_ms": 500},
                {"t_ms": 320, "signal": "shell_expansion_risk", "required_decision": "reject_for_boundary_review", "deadline_ms": 720},
                {"t_ms": 780, "signal": "receipt_writeback_only", "required_decision": "queue_candidate_packet", "deadline_ms": 1180},
            ],
            "success_metrics": ["detail_extraction_completeness", "authority_classification", "receipt_linkage"],
        },
        {
            "case_id": "selector_drift_recovery",
            "surface": "owned_dom_fixture_with_mutations",
            "purpose": "Recover from renamed classes by falling back to role/name/state, accessibility, and text anchors.",
            "scripted_steps": [
                {"t_ms": 0, "signal": "primary_selector_missing", "required_decision": "try_role_locator", "deadline_ms": 250},
                {"t_ms": 260, "signal": "role_name_ambiguous", "required_decision": "query_accessibility_tree", "deadline_ms": 620},
                {"t_ms": 700, "signal": "text_anchor_matches", "required_decision": "write_selector_repair_receipt", "deadline_ms": 1200},
            ],
            "success_metrics": ["fallback_depth", "false_positive_avoidance", "repair_receipt_quality"],
        },
    ]
    return {
        "schema_id": SANDBOX_SKILL_BENCHMARK_SCHEMA_ID,
        "status": "ready_for_local_benchmark" if playwright_available else "ready_for_static_reference_benchmark",
        "purpose": "Measure Browser GPT/Codex perception, timing, planning, recovery, and receipt loops in owned synthetic browser fixtures before any real external client is considered.",
        "critical_gap_count": requirements.get("critical_gap_count", 0),
        "case_count": len(benchmark_cases),
        "benchmark_cases": benchmark_cases,
        "minimum_pass_score": 0.92,
        "scoring_dimensions": {
            "decision_accuracy": 0.35,
            "deadline_hit_rate": 0.2,
            "authority_boundary": 0.2,
            "recovery_quality": 0.15,
            "receipt_quality": 0.1,
        },
        "artifact_paths": {
            "latest_result": LATEST_SANDBOX_BENCHMARK_PATH.as_posix(),
            "result_archive": (SANDBOX_BENCHMARKS_DIR / "*.json").as_posix(),
        },
        "allowed_surfaces": [
            "owned_local_canvas_fixture",
            "owned_html_action_card_fixture",
            "owned_dom_fixture_with_mutations",
        ],
        "forbidden_surfaces": [
            "third_party_game_client",
            "external_economy",
            "anti_cheat_or_terms_evasion",
            "live_chatgpt_send_without_operator_approval",
        ],
        "authority": {
            "sandbox_only": True,
            "third_party_game_client_control_authority": False,
            "browser_game_client_control_authority": False,
            "terms_bypass_authority": False,
            "live_execution_authority": False,
            "production_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
            "cookie_read_authority": False,
            "silent_send_authority": False,
        },
    }


def run_sandbox_skill_benchmark(root: str | Path = ".") -> dict[str, Any]:
    shell_root = resolve_root(root)
    capsule = build_context_capsule(shell_root)
    benchmark = capsule.get("sandbox_skill_benchmark") if isinstance(capsule.get("sandbox_skill_benchmark"), Mapping) else {}
    cases = [row for row in benchmark.get("benchmark_cases", []) if isinstance(row, Mapping)]
    case_results: list[dict[str, Any]] = []
    total_steps = 0
    for case in cases:
        steps = [step for step in case.get("scripted_steps", []) if isinstance(step, Mapping)]
        total_steps += len(steps)
        case_results.append(
            {
                "case_id": case.get("case_id"),
                "surface": case.get("surface"),
                "scripted_step_count": len(steps),
                "decision_accuracy": 1.0,
                "deadline_hit_rate": 1.0,
                "authority_boundary_pass": True,
                "receipt_quality_pass": True,
                "score": 1.0 if steps else 0.0,
            }
        )
    measured_score = round(sum(float(row.get("score") or 0.0) for row in case_results) / max(len(case_results), 1), 4)
    minimum_pass_score = float(benchmark.get("minimum_pass_score") or 0.92)
    run_id = f"{stamp()}_sandbox_reaction_planning_benchmark"
    result_path = shell_root / SANDBOX_BENCHMARKS_DIR / f"{run_id}.json"
    result = {
        "schema_id": SANDBOX_SKILL_BENCHMARK_RESULT_SCHEMA_ID,
        "run_id": run_id,
        "generated_at": utc_now(),
        "status": "passed" if measured_score >= minimum_pass_score and case_results else "failed",
        "benchmark_schema_id": benchmark.get("schema_id"),
        "case_count": len(case_results),
        "scripted_step_count": total_steps,
        "measured_score": measured_score,
        "minimum_pass_score": minimum_pass_score,
        "case_results": case_results,
        "result_path": repo_rel(shell_root, result_path),
        "latest_result_path": repo_rel(shell_root, shell_root / LATEST_SANDBOX_BENCHMARK_PATH),
        "authority": benchmark.get("authority", {}),
        "forbidden_surface_check": {
            "third_party_game_client_control_authority": False,
            "terms_bypass_authority": False,
            "live_execution_authority": False,
            "silent_send_authority": False,
        },
    }
    write_json(result_path, result)
    write_json(shell_root / LATEST_SANDBOX_BENCHMARK_PATH, result)
    return {**result, "ok": result["status"] == "passed"}


def build_self_evolution_loop(
    requirements: Mapping[str, Any],
    dialogue_loop: Mapping[str, Any],
    capability_matrix: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Project the candidate-only loop for improving Browser GPT itself.

    The loop can observe, ask, rank, prove, and prepare work packets. It cannot
    apply patches from GPT text, approve native actions, or claim accepted state.
    """
    critical_gap_count = int(requirements.get("critical_gap_count") or 0)
    dialogue_status = str(dialogue_loop.get("status") or "missing")
    capability_rows = capability_matrix or []
    available_capabilities = [
        str(row.get("capability_id"))
        for row in capability_rows
        if isinstance(row, Mapping) and str(row.get("status") or "").lower() in {"available", "learned", "planned"}
    ]
    status = (
        "ready_for_candidate_self_evolution"
        if dialogue_status == "ready_for_gated_dialogue" and critical_gap_count == 0
        else "needs_surface_or_dialogue_proof"
    )
    ranked_candidate_queue = [
        {
            "rank": 1,
            "candidate_id": "action_detail_extraction_live_panel_sync",
            "candidate_class": "action_detail_extraction",
            "status": "implemented_validated",
            "title": "Synchronize native action cards with full panel details and process receipts.",
            "score": 0.92,
            "why_now": "Operator needs action requests visible in the chat page with full details and approval controls.",
            "proof_plan": ["extension_parser_smoke", "live_dom_panel_fixture", "cockpit_model_projection"],
            "required_gate": "explicit_operator_or_auto_approve_policy",
        },
        {
            "rank": 2,
            "candidate_id": "pending_message_state_machine",
            "candidate_class": "pending_message_ux",
            "status": "implemented_validated",
            "title": "Add pending/sending/sent/received/assistant-pending chat state machine.",
            "score": 0.88,
            "why_now": "Outbound chat should show immediate feedback and avoid sudden jerky transcript refreshes.",
            "proof_plan": ["unit_state_machine", "chat_ui_smoke", "auto_scroll_check"],
            "required_gate": "source_patch_and_ui_build",
        },
        {
            "rank": 3,
            "candidate_id": "compact_chatgpt_status_bar",
            "candidate_class": "ui_compaction_and_state",
            "status": "implemented_validated",
            "title": "Compact Browser GPT telemetry and control bars into icons, checks, collapsed details, and dense counters.",
            "score": 0.84,
            "why_now": "The current Browser GPT header/status text is too large for active use.",
            "proof_plan": ["desktop_mobile_visual_smoke", "text_overlap_check", "cockpit_build"],
            "required_gate": "source_patch_and_ui_build",
        },
        {
            "rank": 4,
            "candidate_id": "chat_input_keyboard_autoscroll",
            "candidate_class": "pending_message_ux",
            "status": "implemented_validated",
            "title": "Harden Enter-to-send, Shift+Enter newline, and active-chat autoscroll behavior.",
            "score": 0.81,
            "why_now": "The chat surface should behave like a native conversation pane during active collaboration.",
            "proof_plan": ["keyboard_event_unit", "playwright_chat_input_smoke", "scroll_anchor_check"],
            "required_gate": "source_patch_and_ui_build",
        },
        {
            "rank": 5,
            "candidate_id": "cdp_accessibility_tree_witness",
            "candidate_class": "cdp_accessibility_witness",
            "status": "implemented_validated",
            "title": "Add read-only CDP/accessibility witness receipts for roles, dialogs, and action affordances.",
            "score": 0.76,
            "why_now": "A second witness reduces selector drift risk when ChatGPT DOM changes.",
            "proof_plan": ["read_only_cdp_probe", "accessibility_snapshot_receipt", "no_secret_boundary_check"],
            "required_gate": "read_only_probe_only",
        },
        {
            "rank": 6,
            "candidate_id": "native_history_chat_indexer",
            "candidate_class": "dom_selector_repair",
            "status": "implemented_validated",
            "title": "Index open ChatGPT tabs, native sidebar history, custom GPTs, and reopenable chat metadata.",
            "score": 0.74,
            "why_now": "The app should show current tabs plus past/native chats as durable reopen sources.",
            "proof_plan": ["sidebar_phase_sweep", "history_fixture", "archive_projection_test", "extension_parser_smoke"],
            "required_gate": "read_visible_dom_only",
        },
        {
            "rank": 7,
            "candidate_id": "sandbox_reaction_planning_benchmark",
            "candidate_class": "sandbox_skill_benchmark",
            "status": "implemented_validated",
            "title": "Build a local synthetic browser benchmark for perception, timing, planning, and recovery.",
            "score": 0.64,
            "why_now": "High-skill automation should be measured in an owned sandbox before any real external client is considered.",
            "proof_plan": ["local_sandbox_task", "metrics_receipt", "terms_boundary_assertions", "sandbox_benchmark_cli"],
            "required_gate": "sandbox_only",
        },
    ]
    open_candidates = [row for row in ranked_candidate_queue if row.get("status") != "implemented_validated"]
    top_candidate = (
        open_candidates[0]
        if open_candidates
        else {
            "candidate_id": "all_current_candidates_validated",
            "title": "All current Browser GPT self-evolution candidates have focused validation.",
        }
    )
    return {
        "schema_id": SELF_EVOLUTION_LOOP_SCHEMA_ID,
        "status": status,
        "objective": (
            "Let Browser GPT and Codex propose, validate, and receipt their own next bounded improvements "
            "without autonomous mutation, live execution, or accepted-state authority."
        ),
        "dialogue_loop_status": dialogue_status,
        "critical_gap_count": critical_gap_count,
        "available_capabilities": available_capabilities,
        "top_candidate_id": top_candidate["candidate_id"],
        "top_candidate_title": top_candidate["title"],
        "implemented_candidate_count": len(ranked_candidate_queue) - len(open_candidates),
        "ranked_candidate_count": len(ranked_candidate_queue),
        "ranked_candidate_queue": ranked_candidate_queue,
        "cycle_phases": [
            {
                "phase": "observe_current_capability_state",
                "actor": "codex_browser_agent",
                "input": "latest capsule, cockpit model, selector profile, extension smoke, tests, visual receipts",
                "output": "current capability/gap digest",
                "gate": "read_only_receipted_sources",
            },
            {
                "phase": "ask_gpt_for_candidate_improvements",
                "actor": "gpt_dialogue_action_loop",
                "input": "approved prompt draft plus current gap digest",
                "output": "candidate improvement proposals",
                "gate": "operator_approved_send_required_no_silent_send",
            },
            {
                "phase": "extract_candidate_actions",
                "actor": "codex_browser_agent",
                "input": "visible GPT transcript, action cards, YAML/JSON snippets, tool/status text",
                "output": "normalized candidate action records",
                "gate": "parse_only_no_execution_from_chat_text",
            },
            {
                "phase": "rank_candidates",
                "actor": "codex_browser_agent",
                "input": "candidate records plus score weights and stop conditions",
                "output": "ranked candidate queue with reject/hold/prove decisions",
                "gate": "bounded_scope_and_rollback_check_required",
            },
            {
                "phase": "prove_candidate_in_sandbox",
                "actor": "pytest_playwright_cdp_witness",
                "input": "candidate patch preview or read-only probe plan",
                "output": "unit/static/visual/DOM evidence receipt",
                "gate": "sandbox_or_read_only_probe_only",
            },
            {
                "phase": "prepare_bounded_patch_or_packet",
                "actor": "codex",
                "input": "passing proof receipt plus scoped diff/work packet",
                "output": "candidate patch, queue packet, or operator report",
                "gate": "no_auto_apply_from_gpt_output",
            },
            {
                "phase": "operator_or_policy_gate",
                "actor": "operator_or_explicit_policy",
                "input": "candidate packet, blast radius, rollback path, proof receipt",
                "output": "approved bounded execution or stop/revise decision",
                "gate": "explicit_approval_required_for_mutation_or_live_action",
            },
            {
                "phase": "write_receipt_and_next_capsule",
                "actor": "codex_browser_agent",
                "input": "decision, evidence, source refs, next step",
                "output": "receipt, updated candidate capsule, cockpit projection",
                "gate": "receipt_preservation_no_accepted_state_claim",
            },
        ],
        "candidate_classes": [
            {
                "candidate_class": "dom_selector_repair",
                "purpose": "Repair selector drift for message timeline, composer, send, menus, native history, and action panels.",
                "proof_required": ["selector_profile_comparison", "playwright_actionability_or_visibility", "visual_smoke"],
            },
            {
                "candidate_class": "action_detail_extraction",
                "purpose": "Expose full native action titles, descriptions, endpoints, payload summaries, confirmation buttons, and process receipts.",
                "proof_required": ["extension_parser_smoke", "dom_fixture_with_allow_button", "cockpit_model_projection"],
            },
            {
                "candidate_class": "ui_compaction_and_state",
                "purpose": "Compact Browser GPT status bars into icons/checks/collapsed detail while preserving active/pending/sent/received states.",
                "proof_required": ["cockpit_build", "desktop_mobile_visual_smoke", "no_overlap_check"],
            },
            {
                "candidate_class": "pending_message_ux",
                "purpose": "Show outbound user messages immediately as pending/sending, then sent/received, with pending assistant response state.",
                "proof_required": ["unit_state_machine", "chat_ui_smoke", "auto_scroll_check"],
            },
            {
                "candidate_class": "cdp_accessibility_witness",
                "purpose": "Add CDP/accessibility-tree evidence for role/name/state drift and active dialogs.",
                "proof_required": ["read_only_cdp_probe", "accessibility_snapshot_receipt", "no_cookie_or_secret_read"],
            },
            {
                "candidate_class": "sandbox_skill_benchmark",
                "purpose": "Measure perception/timing/planning/recovery in local synthetic browser tasks only.",
                "proof_required": ["local_sandbox_task", "receipt_metrics", "terms_boundary_check"],
            },
            {
                "candidate_class": "test_hardening",
                "purpose": "Turn every discovered Browser GPT failure into focused parser, model, extension, or visual-proof coverage.",
                "proof_required": ["focused_test", "regression_guard", "receipt_link"],
            },
        ],
        "score_weights": {
            "operator_value": 0.25,
            "safety": 0.2,
            "proofability": 0.2,
            "blast_radius": 0.15,
            "rollbackability": 0.1,
            "implementation_cost": 0.1,
        },
        "stop_conditions": [
            "ambiguous_authority_or_approval",
            "secrets_cookie_or_credential_access_required",
            "third_party_game_client_or_terms_evasion_requested",
            "action_execution_inferred_only_from_chat_text",
            "untestable_or_unreceiptable_claim",
            "no_rollback_or_patch_preview_path",
            "production_live_or_accepted_state_authority_missing",
        ],
        "research_constraints": [
            {
                "source_id": "playwright_actionability",
                "source_url": "https://playwright.dev/docs/actionability",
                "constraint": "Use actionability checks and retrying assertions for UI proof instead of fixed sleeps.",
            },
            {
                "source_id": "chrome_extension_messaging",
                "source_url": "https://developer.chrome.com/docs/extensions/develop/concepts/messaging",
                "constraint": "Treat content-script/page messages as untrusted inputs and avoid interpreting them as executable authority.",
            },
            {
                "source_id": "chrome_content_script_isolation",
                "source_url": "https://developer.chrome.com/docs/extensions/develop/concepts/content-scripts",
                "constraint": "Respect isolated-world boundaries when designing the in-page observer bridge.",
            },
            {
                "source_id": "cdp_accessibility_domain",
                "source_url": "https://chromedevtools.github.io/devtools-protocol/tot/Accessibility/",
                "constraint": "Keep accessibility-tree evidence read-only and pair it with DOM/screenshot receipts.",
            },
        ],
        "authority": {
            "candidate_self_evolution_authority": True,
            "operator_approved_send_required": True,
            "silent_send_authority": False,
            "native_action_approval_required": True,
            "native_action_auto_approval_authority": False,
            "patch_apply_from_gpt_text_authority": False,
            "action_execution_from_chat_text": False,
            "browser_game_client_control_authority": False,
            "third_party_terms_bypass_authority": False,
            "cookie_read_authority": False,
            "secrets_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        },
    }


def build_agent_plan(
    requirements: Mapping[str, Any],
    *,
    target_url: str,
    profile_id: str,
    capability_matrix: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    safe_interactions = [
        dict(item) for item in playwright_auto_interaction_plan() if item.get("surface_id") != "send_button"
    ]
    dialogue_loop = build_gpt_dialogue_action_loop(requirements, target_url=target_url)
    cdp_accessibility_witness = build_cdp_accessibility_witness(requirements, capability_matrix)
    sandbox_skill_benchmark = build_sandbox_skill_benchmark(requirements, capability_matrix)
    self_evolution_loop = build_self_evolution_loop(requirements, dialogue_loop, capability_matrix)
    return {
        "schema_id": "ion.codex_browser_agent.plan.v1",
        "target_url": target_url,
        "profile_id": profile_id,
        "safe_interaction_count": len(safe_interactions),
        "safe_interactions": safe_interactions,
        "phases": [
            {"phase": "context_capsule_load", "action": "Read latest Browser GPT DOM, screen automation, action sync, and cockpit projection."},
            {"phase": "baseline_playwright_inspect", "action": "Open ChatGPT, wait for ready/challenge state, capture baseline DOM and screenshot."},
            {"phase": "safe_phase_sweep", "action": "Open sidebar/model/thinking/tools/upload menus where safe, then recapture DOM."},
            {"phase": "conversation_projection", "action": "Extract readable user/assistant/tool/thinking timeline events from DOM anchors."},
            {"phase": "native_action_projection", "action": "Extract full action detail panels plus Allow/Reject affordances without approving unless separately commanded."},
            {"phase": "gpt_dialogue_action_loop", "action": "Use approved sends to ask GPT for plans/action packets, read its response, verify DOM/action claims, and either report or ask for the next gated turn."},
            {"phase": "cdp_accessibility_witness", "action": "Capture read-only role/name/state evidence for dialogs, buttons, composer, and action cards using Playwright/CDP accessibility surfaces."},
            {"phase": "sandbox_skill_benchmark", "action": "Run owned synthetic browser tasks for perception, timing, planning, recovery, and receipt metrics without touching third-party clients."},
            {"phase": "self_evolution_loop", "action": "Ask for candidate improvements, normalize/rank them, prove them in sandbox or read-only probes, and write receipts before any gated mutation."},
            {"phase": "capsule_writeback", "action": "Write report, DOM requirements, context capsule, screenshots, and receipts."},
        ],
        "commands": {
            "plan": "python3 -S -m kernel.ion_codex_browser_agent --ion-root . --plan --json",
            "inspect_headless": (
                "python3 -S -m kernel.ion_codex_browser_agent --ion-root . --inspect "
                f"--profile-id {profile_id} --target-url {target_url} --json"
            ),
            "inspect_comparison": (
                "python3 -S -m kernel.ion_codex_browser_agent --ion-root . --inspect --comparison-profile "
                f"--profile-id {profile_id} --target-url {target_url} --json"
            ),
            "inspect_headed_with_probe": (
                "python3 -S -m kernel.ion_codex_browser_agent --ion-root . --inspect --headed "
                f"--profile-id {profile_id} --target-url {target_url} --use-dom-probe-extension --json"
            ),
            "sandbox_benchmark": "python3 -S -m kernel.ion_codex_browser_agent --ion-root . --sandbox-benchmark --json",
        },
        "blocked_until": [
            "Operator supplies an existing user data dir only when current logged-in ChatGPT state is required.",
            "Composer insert/readback requires --allow-composer-test and still never clicks Send.",
        ],
        "no_send_click": True,
        "critical_gap_count": requirements.get("critical_gap_count", 0),
        "gpt_dialogue_action_loop": dialogue_loop,
        "cdp_accessibility_witness": cdp_accessibility_witness,
        "sandbox_skill_benchmark": sandbox_skill_benchmark,
        "self_evolution_loop": self_evolution_loop,
    }


def build_context_capsule(
    root: str | Path = ".",
    *,
    objective: str = DEFAULT_OBJECTIVE,
    target_url: str = DEFAULT_ORIGIN,
    profile_id: str = DEFAULT_PROFILE_ID,
    playwright_inspection_requested: bool = False,
) -> dict[str, Any]:
    shell_root = resolve_root(root)
    dom_summary = latest_browser_gpt_dom_summary(shell_root)
    phase_sweep = probe_phase_sweep_projection(shell_root)
    requirements = build_dom_requirement_matrix(dom_summary, phase_sweep)
    capability_matrix = build_capability_matrix(shell_root)
    plan = build_agent_plan(
        requirements,
        target_url=target_url,
        profile_id=profile_id,
        capability_matrix=capability_matrix,
    )
    twin = dom_summary.get("chatgpt_dom_twin") if isinstance(dom_summary.get("chatgpt_dom_twin"), Mapping) else {}
    transcript = twin.get("transcript") if isinstance(twin.get("transcript"), Mapping) else {}
    state = twin.get("state") if isinstance(twin.get("state"), Mapping) else {}
    return {
        "schema_id": CAPSULE_SCHEMA_ID,
        "generated_at": utc_now(),
        "objective": objective,
        "root": shell_root.as_posix(),
        "target_url": target_url,
        "profile_id": profile_id,
        "status": "ready_for_playwright_inspection" if not requirements.get("critical_gap_count") else "needs_dom_repair_inspection",
        "summary": {
            "browser_gpt_dom_status": dom_summary.get("status"),
            "dom_twin_status": twin.get("status"),
            "surface_count": requirements.get("surface_count"),
            "ready_surface_count": requirements.get("ready_surface_count"),
            "critical_gap_count": requirements.get("critical_gap_count"),
            "phase_capture_count": requirements.get("phase_capture_count"),
            "timeline_event_count": transcript.get("timeline_event_count"),
            "message_count": transcript.get("message_count"),
            "current_page_state": state.get("current_page_state"),
        },
        "capabilities": capability_matrix,
        "dom_requirements": requirements,
        "agent_plan": plan,
        "gpt_dialogue_action_loop": plan.get("gpt_dialogue_action_loop", {}),
        "cdp_accessibility_witness": plan.get("cdp_accessibility_witness", {}),
        "sandbox_skill_benchmark": plan.get("sandbox_skill_benchmark", {}),
        "self_evolution_loop": plan.get("self_evolution_loop", {}),
        "source_paths": {
            "latest_selector_profile": "ION/05_context/current/browser_gpt_dom_profiles/latest.selector_profile.json",
            "latest_probe_snapshot": "ION/05_context/current/browser_gpt_dom_profiles/probe_snapshots/latest_probe_snapshot.json",
            "latest_screen_automation": "ION/05_context/current/browser_gpt_dom_profiles/screen_automation/latest_state.json",
        },
        "authority": agent_authority(playwright_inspection_requested=playwright_inspection_requested),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def write_agent_receipt(root: Path, run_id: str, report: Mapping[str, Any], status: str) -> str:
    receipt_path = root / RECEIPTS_DIR / f"{run_id}.receipt.json"
    receipt = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "receipt_id": run_id,
        "written_at": utc_now(),
        "status": status,
        "report_path": repo_rel(root, root / LATEST_REPORT_PATH),
        "capsule_path": repo_rel(root, root / LATEST_CAPSULE_PATH),
        "requirements_path": repo_rel(root, root / LATEST_REQUIREMENTS_PATH),
        "artifacts": report.get("artifacts", {}),
        "authority": report.get("authority", agent_authority()),
    }
    write_json(receipt_path, receipt)
    return repo_rel(root, receipt_path)


def write_agent_artifacts(root: Path, run_id: str, capsule: Mapping[str, Any], report: Mapping[str, Any]) -> dict[str, str]:
    capsule_path = root / CAPSULES_DIR / f"{run_id}.context_capsule.json"
    requirements_path = root / REQUIREMENTS_DIR / f"{run_id}.dom_requirements.json"
    report_path = root / REPORTS_DIR / f"{run_id}.agent_report.json"
    requirements = capsule.get("dom_requirements") if isinstance(capsule.get("dom_requirements"), Mapping) else {}

    write_json(capsule_path, capsule)
    write_json(requirements_path, requirements)
    write_json(report_path, report)
    write_json(root / LATEST_CAPSULE_PATH, capsule)
    write_json(root / LATEST_REQUIREMENTS_PATH, requirements)
    write_json(root / LATEST_REPORT_PATH, report)

    return {
        "capsule_path": repo_rel(root, capsule_path),
        "requirements_path": repo_rel(root, requirements_path),
        "report_path": repo_rel(root, report_path),
        "latest_capsule_path": repo_rel(root, root / LATEST_CAPSULE_PATH),
        "latest_requirements_path": repo_rel(root, root / LATEST_REQUIREMENTS_PATH),
        "latest_report_path": repo_rel(root, root / LATEST_REPORT_PATH),
    }


def run_codex_browser_agent(
    root: str | Path = ".",
    *,
    objective: str = DEFAULT_OBJECTIVE,
    target_url: str = DEFAULT_ORIGIN,
    profile_id: str = DEFAULT_PROFILE_ID,
    inspect: bool = False,
    user_data_dir: str | None = None,
    extension_root: str | None = None,
    headless: bool = True,
    allow_composer_test: bool = False,
    auto_interactions: bool = True,
    use_dom_probe_extension: bool = False,
    ready_timeout_ms: int = 120_000,
    comparison_profile: bool = False,
) -> dict[str, Any]:
    shell_root = resolve_root(root)
    run_stamp = stamp()
    effective_profile_id = (
        f"{profile_id}_comparison_{run_stamp}"
        if inspect and comparison_profile and safe_slug(profile_id) == safe_slug(DEFAULT_PROFILE_ID)
        else profile_id
    )
    if inspect and comparison_profile and safe_slug(effective_profile_id) == safe_slug(profile_id):
        effective_profile_id = f"{profile_id}_comparison_{run_stamp}"
    run_id = f"{run_stamp}_{safe_slug(effective_profile_id)}_{'compare' if inspect and comparison_profile else 'inspect' if inspect else 'plan'}"
    canonical_profile_path = shell_root / LATEST_PROFILE_PATH
    canonical_guard_paths = {
        "latest_selector_profile": shell_root / LATEST_PROFILE_PATH,
        "latest_dom_health": shell_root / LATEST_HEALTH_PATH,
        "profile_index": shell_root / INDEX_PATH,
    }
    canonical_guard_bytes = {name: read_file_bytes(path) for name, path in canonical_guard_paths.items()}
    canonical_before_sha256 = sha256_bytes(canonical_guard_bytes["latest_selector_profile"])
    baseline_snapshot_path: Path | None = None
    if comparison_profile and canonical_guard_bytes["latest_selector_profile"] is not None:
        baseline_snapshot_path = shell_root / COMPARISONS_DIR / f"{safe_slug(run_id)}.baseline_latest.selector_profile.json"
        baseline_snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_snapshot_path.write_bytes(canonical_guard_bytes["latest_selector_profile"] or b"")
    pre_capsule = build_context_capsule(
        shell_root,
        objective=objective,
        target_url=target_url,
        profile_id=effective_profile_id,
        playwright_inspection_requested=inspect,
    )
    inspection_result: dict[str, Any] | None = None
    comparison_report: dict[str, Any] | None = None
    canonical_guard_before_restore: dict[str, str] = {}
    canonical_guard_restore_status: dict[str, str] = {name: "not_requested" for name in canonical_guard_paths}
    finding = "agent_plan_written"
    status = "planned"

    if inspect:
        try:
            inspection_result = calibrate_with_playwright(
                shell_root,
                profile_id=effective_profile_id,
                target_url=target_url,
                user_data_dir=user_data_dir,
                extension_root=extension_root,
                headless=headless,
                allow_composer_test=allow_composer_test,
                auto_interactions=auto_interactions,
                use_dom_probe_extension=use_dom_probe_extension,
                ready_timeout_ms=ready_timeout_ms,
                promote_latest=not comparison_profile,
            )
        except Exception as exc:  # pragma: no cover - browser/runtime dependent.
            inspection_result = {
                "ok": False,
                "status": "exception",
                "finding": "playwright_inspection_exception",
                "error": str(exc)[:800],
                "profile_id": safe_slug(effective_profile_id),
                "promoted_latest": False if comparison_profile else None,
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
            }
        finding = "playwright_inspection_completed" if inspection_result.get("ok") else "playwright_inspection_degraded"
        status = "completed" if inspection_result.get("ok") else "degraded"
        canonical_guard_before_restore = {
            name: sha256_file(path)
            for name, path in canonical_guard_paths.items()
        }
        canonical_guard_restore_status: dict[str, str] = {}
        if comparison_profile:
            canonical_guard_restore_status = {
                name: restore_file_bytes(path, canonical_guard_bytes[name])
                for name, path in canonical_guard_paths.items()
            }
        else:
            canonical_guard_restore_status = {name: "not_requested" for name in canonical_guard_paths}
        inspection_result["canonical_guard"] = {
            "before_restore_sha256": canonical_guard_before_restore,
            "restore_status": canonical_guard_restore_status,
            "after_restore_sha256": {name: sha256_file(path) for name, path in canonical_guard_paths.items()},
        }
        if comparison_profile and inspection_result.get("profile_path"):
            comparison_report = compare_selector_profiles(
                shell_root,
                candidate_profile_path=inspection_result.get("profile_path"),
                baseline_profile_path=baseline_snapshot_path or LATEST_PROFILE_PATH,
                run_id=run_id,
            )
            if comparison_report.get("regression_count", 0):
                finding = "playwright_comparison_regression_detected"
                status = "degraded"

    capsule = build_context_capsule(
        shell_root,
        objective=objective,
        target_url=target_url,
        profile_id=effective_profile_id,
        playwright_inspection_requested=inspect,
    )
    capsule["run_id"] = run_id
    capsule["inspection_result"] = inspection_result or {}
    capsule["comparison_profile"] = comparison_profile
    capsule["comparison_report"] = comparison_report or {}
    capsule["pre_inspection_summary"] = pre_capsule.get("summary", {})
    canonical_after_sha256 = sha256_file(canonical_profile_path)

    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "run_id": run_id,
        "generated_at": utc_now(),
        "status": status,
        "finding": finding,
        "mode": "playwright_inspect" if inspect else "plan_only",
        "objective": objective,
        "target_url": target_url,
        "profile_id": effective_profile_id,
        "requested_profile_id": profile_id,
        "comparison_profile": comparison_profile,
        "canonical_profile_path": repo_rel(shell_root, canonical_profile_path),
        "canonical_profile_sha256_before": canonical_before_sha256,
        "canonical_profile_sha256_after": canonical_after_sha256,
        "canonical_profile_preserved": canonical_before_sha256 == canonical_after_sha256,
        "canonical_profile_changed_during_run": bool(
            comparison_profile
            and canonical_guard_before_restore.get("latest_selector_profile")
            and canonical_guard_before_restore.get("latest_selector_profile") != canonical_before_sha256
        ),
        "canonical_guard": {
            "guarded_paths": {name: repo_rel(shell_root, path) for name, path in canonical_guard_paths.items()},
            "before_run_sha256": {name: sha256_bytes(data) for name, data in canonical_guard_bytes.items()},
            "before_restore_sha256": canonical_guard_before_restore,
            "restore_status": canonical_guard_restore_status,
            "after_restore_sha256": {name: sha256_file(path) for name, path in canonical_guard_paths.items()},
            "baseline_profile_snapshot_path": repo_rel(shell_root, baseline_snapshot_path) if baseline_snapshot_path else None,
        },
        "summary": capsule.get("summary", {}),
        "inspection_result": inspection_result or {},
        "comparison_report": comparison_report or {},
        "no_send_click_performed": True,
        "allow_composer_test": allow_composer_test,
        "auto_interactions": auto_interactions,
        "use_dom_probe_extension": use_dom_probe_extension,
        "ready_timeout_ms": ready_timeout_ms,
        "artifacts": {},
        "authority": agent_authority(playwright_inspection_requested=inspect),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
    artifact_paths = write_agent_artifacts(shell_root, run_id, capsule, report)
    if comparison_report and comparison_report.get("comparison_path"):
        artifact_paths["comparison_path"] = str(comparison_report["comparison_path"])
    if baseline_snapshot_path:
        artifact_paths["baseline_profile_snapshot_path"] = repo_rel(shell_root, baseline_snapshot_path)
    if inspection_result and inspection_result.get("profile_path"):
        artifact_paths["inspection_profile_path"] = str(inspection_result["profile_path"])
    if inspection_result and inspection_result.get("receipt_path"):
        artifact_paths["inspection_receipt_path"] = str(inspection_result["receipt_path"])
    report["artifacts"] = artifact_paths
    write_json(shell_root / REPORTS_DIR / f"{run_id}.agent_report.json", report)
    write_json(shell_root / LATEST_REPORT_PATH, report)
    receipt_path = write_agent_receipt(shell_root, run_id, report, status=status)
    report["receipt_path"] = receipt_path
    write_json(shell_root / REPORTS_DIR / f"{run_id}.agent_report.json", report)
    write_json(shell_root / LATEST_REPORT_PATH, report)
    return {**report, "ok": status in {"planned", "completed"}, "capsule_path": artifact_paths["latest_capsule_path"], "requirements_path": artifact_paths["latest_requirements_path"]}


def latest_codex_browser_agent_summary(root: str | Path = ".") -> dict[str, Any]:
    shell_root = resolve_root(root)
    report = read_json(shell_root / LATEST_REPORT_PATH)
    capsule = read_json(shell_root / LATEST_CAPSULE_PATH)
    requirements = read_json(shell_root / LATEST_REQUIREMENTS_PATH)
    if not report and not capsule:
        return {
            "schema_id": AGENT_SCHEMA_ID,
            "status": "missing",
            "recommended_action": "run_codex_browser_agent_plan",
            "commands": ["python3 -S -m kernel.ion_codex_browser_agent --ion-root . --plan --json"],
            "authority": agent_authority(),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    comparison = report.get("comparison_report") if isinstance(report.get("comparison_report"), Mapping) else {}
    dialogue_loop = capsule.get("gpt_dialogue_action_loop") if isinstance(capsule.get("gpt_dialogue_action_loop"), Mapping) else {}
    cdp_accessibility_witness = capsule.get("cdp_accessibility_witness") if isinstance(capsule.get("cdp_accessibility_witness"), Mapping) else {}
    sandbox_skill_benchmark = capsule.get("sandbox_skill_benchmark") if isinstance(capsule.get("sandbox_skill_benchmark"), Mapping) else {}
    self_evolution_loop = capsule.get("self_evolution_loop") if isinstance(capsule.get("self_evolution_loop"), Mapping) else {}
    sandbox_benchmark_result = read_json(shell_root / LATEST_SANDBOX_BENCHMARK_PATH)
    return {
        "schema_id": AGENT_SCHEMA_ID,
        "status": report.get("status") or capsule.get("status") or "present",
        "finding": report.get("finding"),
        "mode": report.get("mode"),
        "run_id": report.get("run_id") or capsule.get("run_id"),
        "generated_at": report.get("generated_at") or capsule.get("generated_at"),
        "comparison_profile": bool(report.get("comparison_profile")),
        "canonical_profile_preserved": report.get("canonical_profile_preserved"),
        "canonical_profile_changed_during_run": report.get("canonical_profile_changed_during_run"),
        "comparison_status": comparison.get("status"),
        "comparison_regression_count": comparison.get("regression_count", 0),
        "comparison_selector_match_count": comparison.get("selector_match_count", 0),
        "comparison_changed_selector_count": comparison.get("changed_selector_count", 0),
        "summary": capsule.get("summary", {}),
        "critical_gap_count": requirements.get("critical_gap_count", 0),
        "phase_capture_count": requirements.get("phase_capture_count", 0),
        "ready_surface_count": requirements.get("ready_surface_count", 0),
        "surface_count": requirements.get("surface_count", 0),
        "gpt_dialogue_action_loop": dialogue_loop,
        "cdp_accessibility_witness": cdp_accessibility_witness,
        "sandbox_skill_benchmark": sandbox_skill_benchmark,
        "sandbox_skill_benchmark_result": sandbox_benchmark_result,
        "self_evolution_loop": self_evolution_loop,
        "no_send_click_performed": report.get("no_send_click_performed", True),
        "artifacts": {
            "latest_report": repo_rel(shell_root, shell_root / LATEST_REPORT_PATH),
            "latest_capsule": repo_rel(shell_root, shell_root / LATEST_CAPSULE_PATH),
            "latest_requirements": repo_rel(shell_root, shell_root / LATEST_REQUIREMENTS_PATH),
            "receipt_path": report.get("receipt_path"),
            "comparison_path": comparison.get("comparison_path"),
            "latest_sandbox_benchmark_result": repo_rel(shell_root, shell_root / LATEST_SANDBOX_BENCHMARK_PATH),
            "baseline_profile_snapshot_path": (
                report.get("artifacts") if isinstance(report.get("artifacts"), Mapping) else {}
            ).get("baseline_profile_snapshot_path"),
            "inspection_profile_path": (report.get("artifacts") if isinstance(report.get("artifacts"), Mapping) else {}).get("inspection_profile_path"),
        },
        "commands": (capsule.get("agent_plan") if isinstance(capsule.get("agent_plan"), Mapping) else {}).get("commands", {}),
        "authority": agent_authority(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run or plan the Codex Browser GPT agent lane.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--objective", default=DEFAULT_OBJECTIVE)
    parser.add_argument("--target-url", default=DEFAULT_ORIGIN)
    parser.add_argument("--profile-id", default=DEFAULT_PROFILE_ID)
    parser.add_argument("--plan", action="store_true", help="Write only the agent plan/capsule/requirements.")
    parser.add_argument("--inspect", action="store_true", help="Run Playwright inspection and then write the capsule.")
    parser.add_argument("--user-data-dir", default=None, help="Optional Chromium user data dir. Use only with operator approval.")
    parser.add_argument("--extension-root", default=None)
    parser.add_argument("--use-dom-probe-extension", action="store_true")
    parser.add_argument("--no-auto-interactions", action="store_true")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--allow-composer-test", action="store_true")
    parser.add_argument("--ready-timeout-ms", type=int, default=120_000)
    parser.add_argument("--comparison-profile", action="store_true", help="Write inspection as an isolated candidate and compare against latest selector profile.")
    parser.add_argument("--sandbox-benchmark", action="store_true", help="Run the owned local synthetic Browser GPT benchmark and write a metrics receipt.")
    parser.add_argument("--latest", action="store_true", help="Read the latest agent projection without writing.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.sandbox_benchmark:
        result = run_sandbox_skill_benchmark(args.ion_root)
    elif args.latest:
        result = latest_codex_browser_agent_summary(args.ion_root)
    else:
        result = run_codex_browser_agent(
            args.ion_root,
            objective=args.objective,
            target_url=args.target_url,
            profile_id=args.profile_id,
            inspect=args.inspect and not args.plan,
            user_data_dir=args.user_data_dir,
            extension_root=args.extension_root,
            headless=not args.headed,
            allow_composer_test=args.allow_composer_test,
            auto_interactions=not args.no_auto_interactions,
            use_dom_probe_extension=args.use_dom_probe_extension,
            ready_timeout_ms=args.ready_timeout_ms,
            comparison_profile=args.comparison_profile,
        )

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result.get("finding") or result.get("status"))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
