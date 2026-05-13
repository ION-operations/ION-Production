from pathlib import Path

from kernel.ion_codex_carrier_domain import REQUIRED_SURFACES
from kernel.ion_codex_carrier_os import (
    READY_VERDICT,
    WRITE_CONFIRMATION_TOKEN,
    build_codex_carrier_os_source_map,
    initialize_codex_carrier_os,
    main,
)
from kernel.ion_mcp_local_bridge import IonMcpExecutionResolution, IonMcpLocalBridge, IonMcpToolStatus


def _seed_required_surface(root: Path, rel: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# seeded test surface\n{rel}\n", encoding="utf-8")


def _minimal_shell_root(tmp_path: Path) -> Path:
    root = tmp_path / "ion-shell"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    for rel in REQUIRED_SURFACES.values():
        _seed_required_surface(root, rel)
    _seed_required_surface(root, "ION/02_architecture/CODEX_CARRIER_OS_RUNTIME_PROTOCOL.md")
    return root


def test_codex_carrier_os_initializes_source_map_slash_commands_and_mirror_policy(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)

    result = initialize_codex_carrier_os(root)

    assert result["verdict"] == READY_VERDICT
    assert result["ok"] is True
    assert (root / "ION/05_context/current/codex_carrier/CODEX_CARRIER_OS_SOURCE_MAP.json").exists()
    assert (root / "ION/05_context/current/codex_carrier/CODEX_SLASH_COMMAND_REGISTRY.json").exists()
    assert (root / "ION/05_context/current/codex_carrier/CODEX_CONTEXT_MIRROR_POLICY.json").exists()
    assert result["context_mirror_policy"]["live_repo_runs_from_drive"] is False
    assert result["event"]["event_id"].startswith("evt_")

    source = build_codex_carrier_os_source_map(root)
    assert source["verdict"] == READY_VERDICT
    assert source["context_mirror_policy"]["drive_is_active_working_tree"] is False
    assert source["runtime_event_bus"]["event_count"] >= 1
    assert source["raw_context_sync_lane"]["raw_content_exported"] is False
    assert source["drive_runtime_authority"] is False


def test_codex_carrier_os_cli_requires_confirmation(tmp_path: Path, capsys) -> None:
    root = _minimal_shell_root(tmp_path)

    assert main(["init", "--ion-root", str(root), "--confirmation", "WRONG", "--json"]) == 3
    refused = capsys.readouterr().out
    assert "CONFIRMATION_REQUIRED" in refused

    assert main(["init", "--ion-root", str(root), "--confirmation", WRITE_CONFIRMATION_TOKEN, "--json"]) == 0
    accepted = capsys.readouterr().out
    assert READY_VERDICT in accepted


def test_mcp_codex_carrier_os_tool_is_read_only_projection(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    initialize_codex_carrier_os(root)
    bridge = IonMcpLocalBridge(root / "ION", tmp_path / "bridge-state")

    result = bridge.call_tool("ion.codex.carrier.os", {})

    assert result.status == IonMcpToolStatus.OK
    assert result.execution_resolution == IonMcpExecutionResolution.READ_ONLY
    assert result.kernel_truth_mutated is False
    assert result.live_execution_authorized is False
    assert result.payload["schema_id"] == "ion.codex_carrier_os_source_map.v1"
    assert result.payload["drive_runtime_authority"] is False
