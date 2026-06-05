"""ION operational posture for Codex CLI chat.

This is the chat-facing contract above the lower-level mount guard.  It answers:
is ION operational here, what role-phase mode is lawful, whether optional
external worker processes are active/proven, and whether Mini/Capsule are only
fallback witnesses.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from kernel.ion_codex_mount_guard import (
    READY_STATE as MOUNT_READY_STATE,
    build_codex_mount_status,
)


SCHEMA_ID = "ion.codex_operational_posture.v0_1"
PROOF_SCHEMA_ID = "ion.codex_operational_posture_proof.v0_1"
READY_STATE = "ION_CODEX_OPERATIONAL_READY"
PARTIAL_STATE = "ION_CODEX_OPERATIONAL_PARTIAL"
BLOCKED_STATE = "ION_CODEX_OPERATIONAL_BLOCKED"
OPERATIONAL_POSTURE_SECTION = "### ION OPERATIONAL POSTURE"
DEFAULT_CURRENT_STATUS_PATH = (
    "ION/05_context/current/codex_cli/operational_posture/CURRENT_ION_CODEX_OPERATIONAL_POSTURE.json"
)

ROLE_PHASE_SEQUENCE: tuple[str, ...] = (
    "PERSONA_INTERFACE_INGRESS",
    "RELAY",
    "STEWARD",
    "VIZIER",
    "MASON",
    "NEMESIS_OR_VICE_REVIEW",
    "SCRIBE",
    "STEWARD_FINAL",
    "PERSONA_INTERFACE_RESPONSE",
)

ROLE_REQUIRED_REFS: tuple[tuple[str, str], ...] = (
    ("ION/03_registry/agent_context_system_registry.yaml", "agent_context_system_registry"),
    ("ION/05_context/current/agent_context_systems/AGENT_CONTEXT_SYSTEMS_INDEX.md", "agent_context_system_index"),
    ("ION/03_registry/boots/PERSONA_INTERFACE.boot.md", "persona_interface_boot"),
    ("ION/05_context/current/agent_context_systems/PERSONA_INTERFACE.context_system.md", "persona_interface_context_system"),
    ("ION/07_templates/bindings/PERSONA_INTERFACE__USER_RESPONSE.md", "persona_interface_return_template"),
    ("ION/03_registry/boots/RELAY.boot.md", "relay_boot"),
    ("ION/05_context/current/agent_context_systems/RELAY.context_system.md", "relay_context_system"),
    ("ION/07_templates/bindings/RELAY__HANDOFF.md", "relay_handoff_template"),
    ("ION/03_registry/boots/STEWARD.boot.md", "steward_boot"),
    ("ION/05_context/current/agent_context_systems/STEWARD.context_system.md", "steward_context_system"),
    ("ION/07_templates/bindings/STEWARD__TASK.md", "steward_task_template"),
    ("ION/03_registry/boots/VIZIER.boot.md", "vizier_boot"),
    ("ION/05_context/current/agent_context_systems/VIZIER.context_system.md", "vizier_context_system"),
    ("ION/03_registry/boots/MASON.boot.md", "mason_boot"),
    ("ION/05_context/current/agent_context_systems/MASON.context_system.md", "mason_context_system"),
    ("ION/07_templates/bindings/MASON__CODE.md", "mason_code_template"),
    ("ION/03_registry/boots/NEMESIS.boot.md", "nemesis_boot"),
    ("ION/05_context/current/agent_context_systems/NEMESIS.context_system.md", "nemesis_context_system"),
    ("ION/03_registry/boots/VICE.boot.md", "vice_boot"),
    ("ION/05_context/current/agent_context_systems/VICE.context_system.md", "vice_context_system"),
    ("ION/03_registry/boots/SCRIBE.boot.md", "scribe_boot"),
    ("ION/05_context/current/agent_context_systems/SCRIBE.context_system.md", "scribe_context_system"),
    ("ION/07_templates/carriers/SINGLE_CARRIER_SEQUENTIAL_PACKET.md", "single_carrier_role_phase_template"),
)

HOOK_REFS: tuple[tuple[str, str], ...] = (
    (".codex/hooks/ion_session_start_context.py", "session_start_hook"),
    (".codex/hooks/ion_user_prompt_submit.py", "user_prompt_submit_hook"),
    (".codex/hooks/ion_precompact.py", "precompact_hook"),
    (".codex/hooks/ion_postcompact.py", "postcompact_hook"),
    (".codex/hooks/ion_stop.py", "stop_hook"),
)

SKILL_REFS: tuple[tuple[str, str], ...] = (
    ("ION/05_context/current/codex_skills_v0/MANIFEST.json", "repo_codex_skills_manifest"),
    ("ION/05_context/current/codex_skills_v0/skills/ion-orchestration/SKILL.md", "repo_ion_orchestration_skill"),
    ("ION/05_context/current/codex_skills_v0/skills/ion-hook-engineer/SKILL.md", "repo_ion_hook_engineer_skill"),
    ("ION/05_context/current/codex_skills_v0/skills/ion-context-scout/SKILL.md", "repo_ion_context_scout_skill"),
    ("ION/05_context/current/codex_skills_v0/skills/ion-memory-curator/SKILL.md", "repo_ion_memory_curator_skill"),
    ("ION/05_context/current/codex_skills_v0/skills/ion-workbench/SKILL.md", "repo_ion_workbench_skill"),
    (
        "ION/05_context/current/codex_skills_v0/skills/ion-operator-artifact-hygiene/SKILL.md",
        "repo_ion_operator_artifact_hygiene_skill",
    ),
)

CODEX_NATIVE_SKILL_IDS: tuple[str, ...] = (
    "ion-orchestration",
    "ion-context-scout",
    "ion-memory-curator",
    "ion-workbench",
    "ion-hook-engineer",
    "ion-operator-artifact-hygiene",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _read_json(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _ref(root: Path, rel_path: str, purpose: str) -> dict[str, Any]:
    path = root / rel_path
    return {
        "path": rel_path,
        "purpose": purpose,
        "exists": path.is_file(),
    }


def _refs(root: Path, refs: Sequence[tuple[str, str]]) -> list[dict[str, Any]]:
    return [_ref(root, rel_path, purpose) for rel_path, purpose in refs]


def _missing(refs: Sequence[Mapping[str, Any]]) -> list[str]:
    return [str(ref["path"]) for ref in refs if not ref.get("exists")]


def _codex_native_skill_install_status(installed_skill_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(installed_skill_root).expanduser() if installed_skill_root is not None else Path.home() / ".codex" / "skills"
    refs = [
        {
            "skill_id": skill_id,
            "path": (root / skill_id / "SKILL.md").as_posix(),
            "exists": (root / skill_id / "SKILL.md").is_file(),
        }
        for skill_id in CODEX_NATIVE_SKILL_IDS
    ]
    installed = [str(ref["skill_id"]) for ref in refs if ref.get("exists")]
    missing = [str(ref["skill_id"]) for ref in refs if not ref.get("exists")]
    if not installed:
        status = "none_installed"
    elif missing:
        status = "partial"
    else:
        status = "complete"
    return {
        "skill_root": root.as_posix(),
        "status": status,
        "installed_skill_ids": installed,
        "missing_skill_ids": missing,
        "installed_count": len(installed),
        "expected_count": len(CODEX_NATIVE_SKILL_IDS),
        "refs": refs,
        "note": "Repo-local codex_skills_v0 drafts are not automatically native Codex skills until installed under this root.",
    }


def _profile_bool(profile_text: str, key: str) -> bool | None:
    prefix = f"{key}:"
    for line in profile_text.splitlines():
        if line.strip().startswith(prefix):
            value = line.split(":", 1)[1].strip().lower()
            if value in {"true", "yes"}:
                return True
            if value in {"false", "no"}:
                return False
    return None


def _active_spawn_plan_status(root: Path) -> dict[str, Any]:
    path = root / "ION/05_context/current/ACTIVE_ROLE_SPAWN_PLAN.json"
    payload = _read_json(path)
    if not isinstance(payload, dict):
        return {
            "path": "ION/05_context/current/ACTIVE_ROLE_SPAWN_PLAN.json",
            "exists": path.is_file(),
            "active_spawn_count": None,
            "generated_spawn_rows_available": False,
            "status": "missing_or_invalid",
        }
    active_count = int(payload.get("active_spawn_count") or 0)
    return {
        "path": "ION/05_context/current/ACTIVE_ROLE_SPAWN_PLAN.json",
        "exists": True,
        "created_at": payload.get("created_at"),
        "carrier": payload.get("carrier"),
        "objective": payload.get("objective"),
        "active_spawn_count": active_count,
        "completed_role_count": payload.get("completed_role_count"),
        "generated_spawn_rows_available": active_count > 0,
        "status": "spawn_rows_available" if active_count > 0 else "no_active_spawn_rows",
    }


def build_codex_operational_posture(
    root: str | Path,
    *,
    installed_skill_root: str | Path | None = None,
) -> dict[str, Any]:
    root_path = Path(root).expanduser().resolve()
    mount = build_codex_mount_status(root_path)
    role_refs = _refs(root_path, ROLE_REQUIRED_REFS)
    hook_refs = _refs(root_path, HOOK_REFS)
    skill_refs = _refs(root_path, SKILL_REFS)
    role_missing = _missing(role_refs)
    hook_missing = _missing(hook_refs)
    skill_missing = _missing(skill_refs)
    profile_text = _read_text(root_path / "ION/03_registry/codex_cli_carrier_profile.yaml")
    can_spawn_host_subagents = _profile_bool(profile_text, "can_spawn_host_subagents")
    spawn_plan = _active_spawn_plan_status(root_path)
    native_skill_install = _codex_native_skill_install_status(installed_skill_root)

    blockers: list[str] = []
    warnings: list[str] = []
    if mount.get("mount_truth_state") != MOUNT_READY_STATE:
        blockers.append("mount_guard_not_ready")
    if role_missing:
        blockers.append("role_context_refs_missing")
    if hook_missing:
        blockers.append("codex_hooks_missing")
    if skill_missing:
        warnings.append("repo_codex_skill_refs_missing")
    if native_skill_install["missing_skill_ids"]:
        warnings.append("codex_native_skills_not_globally_installed")
    if "mount_guard_not_ready" in blockers:
        state = BLOCKED_STATE
        carrier_mode = "fallback_context_only_or_blocked"
    elif blockers:
        state = PARTIAL_STATE
        carrier_mode = "partial_ion_operation_receipt_only_for_role_claims"
    else:
        state = READY_STATE
        carrier_mode = "single_carrier_sequential_role_phases"

    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "active_root": root_path.as_posix(),
        "ion_operational_state": state,
        "ok": state == READY_STATE,
        "mount_guard": mount,
        "carrier": {
            "carrier_id": "CODEX_CLI_CARRIER",
            "carrier_mode": carrier_mode,
            "ion_carrier_mount": "mounted_ion_codex_carrier",
            "can_spawn_host_subagents_profile": can_spawn_host_subagents,
            "subagent_policy": (
                "external workers are optional carrier slots, not required for ION mount; "
                "use generated spawn rows or explicit invocation proof when separate "
                "worker processes are needed"
            ),
        },
        "role_phase_contract": {
            "mode": "single_carrier_sequential" if state == READY_STATE else "not_fully_available",
            "role_phase_sequence": list(ROLE_PHASE_SEQUENCE),
            "authority_claim": "role phases are bounded ION operating lenses, not ungated final authority",
            "required_refs_present": len(role_refs) - len(role_missing),
            "required_ref_count": len(role_refs),
            "missing_required_refs": role_missing,
        },
        "hooks": {
            "required_refs_present": len(hook_refs) - len(hook_missing),
            "required_ref_count": len(hook_refs),
            "missing_required_refs": hook_missing,
        },
        "skills": {
            "active_skill": "ion-orchestration",
            "repo_skill_manifest_status": "candidate",
            "required_refs_present": len(skill_refs) - len(skill_missing),
            "required_ref_count": len(skill_refs),
            "missing_required_refs": skill_missing,
            "native_codex_skill_installation": native_skill_install,
        },
        "spawn_plan": spawn_plan,
        "context_system_posture": {
            "primary_context_authority": "agent_context_systems_and_task_packages",
            "fallback_only": "Mini/Capsule are standing witnesses and fallback context, not primary live onboarding",
            "fallback_visible_when": "ion_operational_state is not ION_CODEX_OPERATIONAL_READY",
        },
        "source_order": [
            "operator",
            "repo_authority_and_mount_contract",
            "codex_operational_posture",
            "agent_context_system_registry",
            "role_phase_templates",
            "active_work_packet_and_spawn_plan_when_current",
            "codex_solo_capsule_as_witness",
            "receipts_and_tests",
            "memory_or_recall_last",
        ],
        "warnings": warnings,
        "blockers": blockers,
        "past_attempt_failure_causes": [
            "hooks were advisory and did not render a full operational state",
            "Mini/Capsule were treated as enough context instead of fallback witnesses",
            "role names were sometimes used without role-phase/package proof",
            "external worker capability was implied even though Codex profile does not prove spawned workers",
            "stale ACTIVE_ROLE_SPAWN_PLAN data could be mistaken for current execution authority",
            "task returns were not yet required to carry mount/operational posture proof",
            "repo-local skill drafts could be mistaken for natively installed Codex skills",
        ],
        "claims": [
            "ION Codex carrier mounted for this repo",
        ],
        "non_claims": [
            "STEWARD/RELAY/PERSONA authority requires role-phase proof",
            "no external worker process claim without spawn proof",
            "no production authority",
            "no live execution authority",
            "no accepted-state claim",
            "no secrets authority",
        ],
    }


def render_operational_posture_block(posture: Mapping[str, Any]) -> str:
    carrier = posture.get("carrier") or {}
    role = posture.get("role_phase_contract") or {}
    hooks = posture.get("hooks") or {}
    skills = posture.get("skills") or {}
    spawn = posture.get("spawn_plan") or {}
    warnings = posture.get("warnings") or []
    blockers = posture.get("blockers") or []
    phases = role.get("role_phase_sequence") or []
    return "\n".join(
        [
            "ION Codex Operational Posture v0.1",
            f"ion_operational_state: {posture.get('ion_operational_state')}",
            f"carrier_mode: {carrier.get('carrier_mode')}",
            f"role_phase_mode: {role.get('mode')}",
            f"role_phase_sequence: {' -> '.join(phases)}",
            f"role_refs: {role.get('required_refs_present')}/{role.get('required_ref_count')}",
            f"hooks: {hooks.get('required_refs_present')}/{hooks.get('required_ref_count')}",
            (
                "skills: "
                f"repo={skills.get('required_refs_present')}/{skills.get('required_ref_count')} "
                f"native_installed={((skills.get('native_codex_skill_installation') or {}).get('installed_count'))}/"
                f"{((skills.get('native_codex_skill_installation') or {}).get('expected_count'))} "
                f"active={skills.get('active_skill')}"
            ),
            f"subagent_policy: {carrier.get('subagent_policy')}",
            f"spawn_plan: {spawn.get('status')} active_spawn_count={spawn.get('active_spawn_count')}",
            "context_fallback: Mini/Capsule are fallback witnesses only; operational state must say when fallback is active.",
            f"warnings: {', '.join(warnings) if warnings else 'none'}",
            f"blockers: {', '.join(blockers) if blockers else 'none'}",
        ]
    )


def ion_operational_posture_required(payload: Mapping[str, Any]) -> bool:
    """Return true when a work request must prove ION operational posture."""

    explicit = payload.get("ion_operational_posture_required")
    if explicit is not None:
        return bool(explicit)
    signal = " ".join(
        str(payload.get(key) or "")
        for key in (
            "work_class",
            "workload_class",
            "risk_level",
            "route_family",
            "request_kind",
            "objective",
        )
    ).lower()
    return any(
        marker in signal
        for marker in (
            "red_alert",
            "settlement",
            "branch_gateway_mount",
            "carrier_mount",
            "codex_carrier",
            "operator_release_packaging",
            "gpt_builder",
        )
    )


def evaluate_operational_posture_proof(
    worker_output: str,
    *,
    expected_operational_state: str = READY_STATE,
    expected_mount_state: str = MOUNT_READY_STATE,
) -> dict[str, Any]:
    """Validate that a task return explicitly states current ION/Codex posture."""

    findings: list[str] = []
    text = str(worker_output or "")
    lower = text.lower()
    def field_value(name: str) -> str:
        match = re.search(rf"(?im)^\s*{re.escape(name)}\s*:\s*(.+?)\s*$", text)
        if not match:
            return ""
        return match.group(1).strip().strip("`*_\"'")

    if OPERATIONAL_POSTURE_SECTION.lower() not in lower:
        findings.append(f"missing_required_section:{OPERATIONAL_POSTURE_SECTION}")
    if field_value("ion_operational_state") != expected_operational_state:
        findings.append(f"missing_or_wrong_ion_operational_state:{expected_operational_state}")
    if field_value("mount_truth_state") != expected_mount_state:
        findings.append(f"missing_or_wrong_mount_truth_state:{expected_mount_state}")
    if "role_phase_sequence:" not in lower:
        findings.append("missing_required_field:role_phase_sequence")
    if "context_fallback:" not in lower:
        findings.append("missing_required_field:context_fallback")
    if "no accepted-state claim" not in lower and "no_accepted_state_claim" not in lower:
        findings.append("missing_non_claim:no_accepted_state_claim")
    return {
        "schema_id": PROOF_SCHEMA_ID,
        "accepted": not findings,
        "expected_operational_state": expected_operational_state,
        "expected_mount_state": expected_mount_state,
        "findings": findings,
    }


def write_current_operational_posture(
    root: str | Path,
    posture: Mapping[str, Any],
    *,
    output_path: str | Path = DEFAULT_CURRENT_STATUS_PATH,
) -> dict[str, Any]:
    root_path = Path(root).expanduser().resolve()
    path = root_path / output_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(posture), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "ok": bool(posture.get("ok")),
        "path": _rel(path, root_path),
        "ion_operational_state": posture.get("ion_operational_state"),
    }


def _status_command(args: argparse.Namespace) -> dict[str, Any]:
    posture = build_codex_operational_posture(args.ion_root)
    payload: dict[str, Any] = {"posture": posture, "block": render_operational_posture_block(posture)}
    if args.write_current:
        payload["write_current"] = write_current_operational_posture(args.ion_root, posture)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ION Codex operational posture")
    parser.add_argument("--ion-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)
    status = sub.add_parser("status")
    status.add_argument("--json", action="store_true")
    status.add_argument("--write-current", action="store_true")
    status.set_defaults(func=_status_command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = args.func(args)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload["block"])
    return 0 if payload["posture"].get("ion_operational_state") != BLOCKED_STATE else 2


if __name__ == "__main__":
    raise SystemExit(main())
