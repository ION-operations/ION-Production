from __future__ import annotations

import json
from pathlib import Path

from kernel.ion_codex_operational_posture import (
    BLOCKED_STATE,
    OPERATIONAL_POSTURE_SECTION,
    PARTIAL_STATE,
    READY_STATE,
    build_codex_operational_posture,
    evaluate_operational_posture_proof,
    ion_operational_posture_required,
    main,
    render_operational_posture_block,
    write_current_operational_posture,
)


def _seed_ready_root(tmp_path: Path) -> Path:
    root = tmp_path / "ion-root"
    required_paths = [
        "pyproject.toml",
        "ION/REPO_AUTHORITY.md",
        "ION/02_architecture/ION_MOUNT_CONTRACT.md",
        "ION/02_architecture/CODEX_CLI_CARRIER_PROTOCOL.md",
        "ION/03_registry/codex_cli_carrier_profile.yaml",
        "ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md",
        "ION/05_context/current/codex_solo/CAPSULE.md",
        "ION/05_context/current/codex_solo/MINI.md",
        "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
        "ION/05_context/current/codex_solo/STATUS.json",
        "ION/04_packages/kernel/ion_codex_carrier_sync.py",
        "ION/04_packages/kernel/ion_carrier_mount_receipt.py",
        "ION/03_registry/agent_context_system_registry.yaml",
        "ION/05_context/current/agent_context_systems/AGENT_CONTEXT_SYSTEMS_INDEX.md",
        "ION/03_registry/boots/PERSONA_INTERFACE.boot.md",
        "ION/05_context/current/agent_context_systems/PERSONA_INTERFACE.context_system.md",
        "ION/07_templates/bindings/PERSONA_INTERFACE__USER_RESPONSE.md",
        "ION/03_registry/boots/RELAY.boot.md",
        "ION/05_context/current/agent_context_systems/RELAY.context_system.md",
        "ION/07_templates/bindings/RELAY__HANDOFF.md",
        "ION/03_registry/boots/STEWARD.boot.md",
        "ION/05_context/current/agent_context_systems/STEWARD.context_system.md",
        "ION/07_templates/bindings/STEWARD__TASK.md",
        "ION/03_registry/boots/VIZIER.boot.md",
        "ION/05_context/current/agent_context_systems/VIZIER.context_system.md",
        "ION/03_registry/boots/MASON.boot.md",
        "ION/05_context/current/agent_context_systems/MASON.context_system.md",
        "ION/07_templates/bindings/MASON__CODE.md",
        "ION/03_registry/boots/NEMESIS.boot.md",
        "ION/05_context/current/agent_context_systems/NEMESIS.context_system.md",
        "ION/03_registry/boots/VICE.boot.md",
        "ION/05_context/current/agent_context_systems/VICE.context_system.md",
        "ION/03_registry/boots/SCRIBE.boot.md",
        "ION/05_context/current/agent_context_systems/SCRIBE.context_system.md",
        "ION/07_templates/carriers/SINGLE_CARRIER_SEQUENTIAL_PACKET.md",
        ".codex/hooks/ion_session_start_context.py",
        ".codex/hooks/ion_user_prompt_submit.py",
        ".codex/hooks/ion_precompact.py",
        ".codex/hooks/ion_postcompact.py",
        ".codex/hooks/ion_stop.py",
        "ION/05_context/current/codex_skills_v0/MANIFEST.json",
        "ION/05_context/current/codex_skills_v0/skills/ion-orchestration/SKILL.md",
        "ION/05_context/current/codex_skills_v0/skills/ion-hook-engineer/SKILL.md",
        "ION/05_context/current/codex_skills_v0/skills/ion-context-scout/SKILL.md",
        "ION/05_context/current/codex_skills_v0/skills/ion-memory-curator/SKILL.md",
        "ION/05_context/current/codex_skills_v0/skills/ion-workbench/SKILL.md",
        "ION/05_context/current/codex_skills_v0/skills/ion-operator-artifact-hygiene/SKILL.md",
    ]
    for rel_path in required_paths:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        text = f"{rel_path}\n"
        if rel_path == "ION/03_registry/codex_cli_carrier_profile.yaml":
            text = "carrier_id: CODEX_CLI_CARRIER\ncan_spawn_host_subagents: false\n"
        path.write_text(text, encoding="utf-8")
    (root / "ION/05_context/current/ACTIVE_ROLE_SPAWN_PLAN.json").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/05_context/current/ACTIVE_ROLE_SPAWN_PLAN.json").write_text(
        json.dumps({"active_spawn_count": 0, "carrier": "codex_cli", "created_at": "2026-05-16T00:00:00Z"})
        + "\n",
        encoding="utf-8",
    )
    return root


def _seed_installed_skill_root(tmp_path: Path, skill_ids: list[str] | None = None) -> Path:
    root = tmp_path / "codex-skills"
    for skill_id in skill_ids or [
        "ion-orchestration",
        "ion-context-scout",
        "ion-memory-curator",
        "ion-workbench",
        "ion-hook-engineer",
        "ion-operator-artifact-hygiene",
    ]:
        path = root / skill_id / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\nname: {skill_id}\n---\n", encoding="utf-8")
    return root


def test_operational_posture_ready_for_full_local_codex_setup(tmp_path: Path) -> None:
    root = _seed_ready_root(tmp_path)
    installed_skill_root = _seed_installed_skill_root(tmp_path)

    posture = build_codex_operational_posture(root, installed_skill_root=installed_skill_root)

    assert posture["schema_id"] == "ion.codex_operational_posture.v0_1"
    assert posture["ion_operational_state"] == READY_STATE
    assert posture["carrier"]["carrier_mode"] == "single_carrier_sequential_role_phases"
    assert posture["carrier"]["can_spawn_host_subagents_profile"] is False
    assert posture["role_phase_contract"]["mode"] == "single_carrier_sequential"
    assert "PERSONA_INTERFACE_INGRESS" in posture["role_phase_contract"]["role_phase_sequence"]
    assert posture["context_system_posture"]["fallback_only"].startswith("Mini/Capsule")
    assert posture["skills"]["required_ref_count"] == 7
    assert posture["skills"]["native_codex_skill_installation"]["status"] == "complete"
    assert posture["warnings"] == []


def test_operational_posture_partial_when_role_refs_missing(tmp_path: Path) -> None:
    root = _seed_ready_root(tmp_path)
    installed_skill_root = _seed_installed_skill_root(tmp_path)
    (root / "ION/03_registry/boots/MASON.boot.md").unlink()

    posture = build_codex_operational_posture(root, installed_skill_root=installed_skill_root)

    assert posture["ion_operational_state"] == PARTIAL_STATE
    assert "role_context_refs_missing" in posture["blockers"]
    assert "ION/03_registry/boots/MASON.boot.md" in posture["role_phase_contract"]["missing_required_refs"]


def test_operational_posture_blocked_when_mount_guard_blocked(tmp_path: Path) -> None:
    posture = build_codex_operational_posture(tmp_path)

    assert posture["ion_operational_state"] == BLOCKED_STATE
    assert "mount_guard_not_ready" in posture["blockers"]


def test_render_operational_posture_block_makes_fallback_and_subagents_visible(tmp_path: Path) -> None:
    posture = build_codex_operational_posture(
        _seed_ready_root(tmp_path),
        installed_skill_root=_seed_installed_skill_root(tmp_path),
    )

    block = render_operational_posture_block(posture)

    assert "ION Codex Operational Posture v0.1" in block
    assert f"ion_operational_state: {READY_STATE}" in block
    assert "single_carrier_sequential_role_phases" in block
    assert "skills: repo=7/7 native_installed=6/6 active=ion-orchestration" in block
    assert "external workers are optional carrier slots, not required for ION mount" in block
    assert "Mini/Capsule are fallback witnesses only" in block


def test_operational_posture_warns_when_repo_skills_are_not_native_installed(tmp_path: Path) -> None:
    root = _seed_ready_root(tmp_path)
    installed_skill_root = _seed_installed_skill_root(tmp_path, ["ion-orchestration"])

    posture = build_codex_operational_posture(root, installed_skill_root=installed_skill_root)

    assert posture["ion_operational_state"] == READY_STATE
    assert "codex_native_skills_not_globally_installed" in posture["warnings"]
    native = posture["skills"]["native_codex_skill_installation"]
    assert native["status"] == "partial"
    assert native["installed_skill_ids"] == ["ion-orchestration"]
    assert "ion-hook-engineer" in native["missing_skill_ids"]


def test_write_current_operational_posture_writes_snapshot(tmp_path: Path) -> None:
    root = _seed_ready_root(tmp_path)
    posture = build_codex_operational_posture(root, installed_skill_root=_seed_installed_skill_root(tmp_path))

    result = write_current_operational_posture(root, posture)

    assert result["ok"] is True
    written = json.loads((root / result["path"]).read_text(encoding="utf-8"))
    assert written["ion_operational_state"] == READY_STATE


def test_cli_status_can_write_current_snapshot(tmp_path: Path, capsys) -> None:
    root = _seed_ready_root(tmp_path)

    assert main(["--ion-root", str(root), "status", "--json", "--write-current"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["posture"]["ion_operational_state"] == READY_STATE
    assert payload["write_current"]["path"].endswith("CURRENT_ION_CODEX_OPERATIONAL_POSTURE.json")


def test_operational_posture_proof_accepts_explicit_ready_state() -> None:
    output = f"""{OPERATIONAL_POSTURE_SECTION}
ion_operational_state: ION_CODEX_OPERATIONAL_READY
mount_truth_state: CODEX_CARRIER_LOCAL_MOUNT_READY
role_phase_sequence: PERSONA_INTERFACE_INGRESS -> RELAY -> STEWARD
context_fallback: Mini/Capsule are fallback witnesses only.
non_claims: no accepted-state claim
"""

    result = evaluate_operational_posture_proof(output)

    assert result["accepted"] is True


def test_operational_posture_proof_accepts_markdown_code_wrapped_values() -> None:
    output = f"""{OPERATIONAL_POSTURE_SECTION}
ion_operational_state: `ION_CODEX_OPERATIONAL_READY`
mount_truth_state: `CODEX_CARRIER_LOCAL_MOUNT_READY`
role_phase_sequence: `PERSONA_INTERFACE_INGRESS -> RELAY -> STEWARD`
context_fallback: `Mini/Capsule are fallback witnesses only.`
non_claims: `no accepted-state claim`
"""

    result = evaluate_operational_posture_proof(output)

    assert result["accepted"] is True


def test_operational_posture_proof_rejects_missing_section() -> None:
    result = evaluate_operational_posture_proof("### CONTEXT PROOF\nread something\n")

    assert result["accepted"] is False
    assert f"missing_required_section:{OPERATIONAL_POSTURE_SECTION}" in result["findings"]


def test_operational_posture_required_for_red_alert_and_mount_work() -> None:
    assert ion_operational_posture_required({"work_class": "red_alert"}) is True
    assert ion_operational_posture_required({"objective": "repair branch_gateway_mount parity"}) is True
    assert ion_operational_posture_required({"objective": "small docs typo"}) is False
