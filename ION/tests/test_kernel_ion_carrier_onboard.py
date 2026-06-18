from pathlib import Path

from kernel.ion_carrier_onboard import (
    CODEX_CLI_MODE,
    CODEX_CLI_TEMPLATE_PATH,
    CURSOR_CLI_MODE,
    CURSOR_CLI_TEMPLATE_PATH,
    GPT_SANDBOX_MODE,
    GPT_SANDBOX_TEMPLATE_PATH,
    build_active_work_packet,
)


def _repo_root() -> Path:
    root = Path.cwd()
    assert (root / "pyproject.toml").exists()
    assert (root / "ION/REPO_AUTHORITY.md").exists()
    return root


def test_gpt_sandbox_active_work_packet_uses_front_door_single_carrier_template():
    root = _repo_root()
    packet = build_active_work_packet(
        root,
        carrier="GPT_SANDBOX_CARRIER",
        objective="audit GPT sandbox front door route",
    )

    assert packet["active_template"] == GPT_SANDBOX_TEMPLATE_PATH
    assert packet["active_template_exists"] is True
    assert packet["mode"] == GPT_SANDBOX_MODE
    assert packet["role_phase_sequence"][0] == "PERSONA_INTERFACE_INGRESS"
    assert packet["role_phase_sequence"][1] == "RELAY"
    assert packet["role_phase_sequence"][-2] == "STEWARD_FINAL"
    assert packet["role_phase_sequence"][-1] == "PERSONA_INTERFACE_RESPONSE"
    assert packet["carrier_capabilities"]["can_use_mcp"] is False
    assert packet["carrier_capabilities"]["can_spawn_carrier_slots"] is False
    assert packet["production_authority"] is False
    assert packet["live_execution_authority"] is False


def test_codex_extension_active_work_packet_keeps_existing_cursor_workflow_template():
    root = _repo_root()
    packet = build_active_work_packet(
        root,
        carrier="codex_extension",
        objective="audit existing codex extension route",
    )

    assert packet["active_template"] == "ION/docs/cursor/ION_CURSOR_WORK_CYCLE_PACKET.md"
    assert packet["role_phase_sequence"][0] == "RELAY"
    assert "STEWARD" in packet["role_phase_sequence"]


def test_cursor_ide_active_work_packet_keeps_existing_cursor_workflow_template():
    root = _repo_root()
    packet = build_active_work_packet(
        root,
        carrier="cursor",
        objective="audit Cursor IDE carrier route",
    )

    assert packet["active_template"] == "ION/docs/cursor/ION_CURSOR_WORK_CYCLE_PACKET.md"
    assert packet["mode"] == "MANUAL_TEMPLATE_BOUND_WORKFLOW"
    assert packet["role_phase_sequence"][0] == "RELAY"


def test_cursor_cli_active_work_packet_uses_cursor_cli_execution_template():
    root = _repo_root()
    packet = build_active_work_packet(
        root,
        carrier="cursor_cli",
        objective="audit Cursor CLI route",
    )

    assert packet["active_template"] == CURSOR_CLI_TEMPLATE_PATH
    assert packet["active_template_exists"] is True
    assert packet["mode"] == CURSOR_CLI_MODE
    assert packet["role_phase_sequence"][0] == "RELAY"
    assert packet["production_authority"] is False
    assert packet["live_execution_authority"] is False


def test_codex_cli_active_work_packet_uses_codex_cli_profile_and_template():
    root = _repo_root()
    packet = build_active_work_packet(
        root,
        carrier="codex_cli",
        objective="audit Codex CLI route",
    )

    assert packet["active_template"] == CODEX_CLI_TEMPLATE_PATH
    assert packet["active_template_exists"] is True
    assert packet["mode"] == CODEX_CLI_MODE
    assert packet["role_phase_sequence"][0] == "PERSONA_INTERFACE_INGRESS"
    assert packet["role_phase_sequence"][1] == "RELAY"
    assert packet["role_phase_sequence"][-2] == "STEWARD_FINAL"
    assert packet["role_phase_sequence"][-1] == "PERSONA_INTERFACE_RESPONSE"
    assert packet["carrier_capabilities"]["can_edit_files"] is True
    assert packet["carrier_capabilities"]["can_run_shell_commands"] is True
    assert packet["carrier_capabilities"]["can_run_tests"] is True
    assert packet["carrier_capabilities"]["can_run_noninteractive_exec"] is True
    assert packet["carrier_capabilities"]["can_spawn_host_subagents"] is False
    assert packet["carrier_capabilities"]["can_use_mcp"] is False
    assert packet["production_authority"] is False
    assert packet["live_execution_authority"] is False
