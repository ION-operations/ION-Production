from pathlib import Path

from kernel.ion_codex_carrier_domain import (
    DOMAIN_READY_VERDICT,
    WRITE_CONFIRMATION_TOKEN,
    REQUIRED_SURFACES,
    build_codex_agent_registry,
    build_codex_carrier_cockpit_snapshot,
    build_codex_carrier_domain_registry,
    build_codex_carrier_event_ledger,
    build_codex_session_registry,
    initialize_codex_carrier_domain,
    main,
    register_codex_carrier_session,
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
    return root


def test_codex_carrier_domain_status_ready_on_seeded_root(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)

    result = build_codex_carrier_domain_registry(root)

    assert result["schema_id"] == "ion.codex_carrier_domain.v1"
    assert result["verdict"] == DOMAIN_READY_VERDICT
    assert result["ok"] is True
    assert result["production_authority"] is False
    assert result["live_execution_authority"] is False
    assert result["secrets_authority"] is False
    assert "ion.codex.carrier.status" in result["mcp_read_only_tools"]
    assert "ion.codex.carrier.events" in result["mcp_read_only_tools"]
    assert "ion.codex.raw_context.status" in result["mcp_read_only_tools"]
    assert result["memory_policy"]["raw_context_sync_lane"] == "manifest_only_by_default"


def test_codex_carrier_domain_init_writes_control_plane_surfaces(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)

    result = initialize_codex_carrier_domain(root)

    assert result["verdict"] == DOMAIN_READY_VERDICT
    for rel in result["written_paths"]:
        assert (root / rel).exists()
    sessions = build_codex_session_registry(root)
    assert sessions["session_count"] == 0
    agents = build_codex_agent_registry(root)
    assert agents["agent_count"] >= 10
    events = build_codex_carrier_event_ledger(root)
    assert events["event_count"] == 0
    cockpit = build_codex_carrier_cockpit_snapshot(root)
    assert cockpit["domain_registry"]["verdict"] == DOMAIN_READY_VERDICT
    assert cockpit["context_truth_panel"]["shared_context_write_allowed"] is False
    assert cockpit["context_truth_panel"]["raw_context_committed_by_default"] is False
    assert cockpit["raw_context_sync_lane"]["ok"] is True
    assert cockpit["event_ledger"]["event_count"] == 0


def test_register_codex_session_creates_session_record_and_branch_capsule(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    initialize_codex_carrier_domain(root)

    session = register_codex_carrier_session(
        root,
        agent_tag="codex_local_ion_mason",
        current_packet="PCKT-UNIT-CODEX-CARRIER-001",
        session_label="unit branch capsule registration",
    )

    assert session["accepted_state_authority"] is False
    assert session["settlement_required"] is True
    assert (root / session["path"]).exists()
    assert (root / session["ion_branch_capsule"] / "CAPSULE.md").exists()
    assert (root / session["ion_branch_capsule"] / "CODEX_SESSION.json").exists()
    assert (root / session["ion_branch_capsule"] / "STATUS.json").exists()
    assert (root / session["ion_branch_capsule"] / "RAW_CONTEXT_MANIFEST.json").exists()
    assert session["raw_context_manifest"]["snapshot_content_committed"] is False
    registry = build_codex_session_registry(root)
    assert registry["session_count"] == 1
    assert registry["raw_context_manifest_count"] == 1
    events = build_codex_carrier_event_ledger(root)
    assert events["event_count"] >= 2
    assert "codex.session.registered" in events["event_types"]
    cockpit = build_codex_carrier_cockpit_snapshot(root)
    assert cockpit["session_registry"]["active_session_count"] == 1
    assert cockpit["event_ledger"]["event_count"] >= 2
    assert any(edge["kind"] == "binds_branch_capsule" for edge in cockpit["agent_graph"]["edges"])
    assert any(edge["kind"] == "has_raw_context_manifest" for edge in cockpit["agent_graph"]["edges"])


def test_codex_carrier_cli_accepts_ion_root_before_or_after_subcommand(tmp_path: Path, capsys) -> None:
    root = _minimal_shell_root(tmp_path)

    assert main(["--ion-root", str(root), "status", "--json"]) == 0
    first = capsys.readouterr().out
    assert DOMAIN_READY_VERDICT in first

    assert main(["status", "--ion-root", str(root), "--json"]) == 0
    second = capsys.readouterr().out
    assert DOMAIN_READY_VERDICT in second

    initialize_codex_carrier_domain(root)
    assert main(["events", "--ion-root", str(root), "--json"]) == 0
    third = capsys.readouterr().out
    assert "ion.codex_carrier_event_ledger.v1" in third


def test_codex_carrier_init_cli_requires_confirmation(tmp_path: Path, capsys) -> None:
    root = _minimal_shell_root(tmp_path)

    assert main(["init", "--ion-root", str(root), "--confirmation", "WRONG", "--json"]) == 3
    refused = capsys.readouterr().out
    assert "CONFIRMATION_REQUIRED" in refused

    assert main(["init", "--ion-root", str(root), "--confirmation", WRITE_CONFIRMATION_TOKEN, "--json"]) == 0
    accepted = capsys.readouterr().out
    assert DOMAIN_READY_VERDICT in accepted


def test_mcp_codex_carrier_tools_are_read_only_projections(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    initialize_codex_carrier_domain(root)
    bridge = IonMcpLocalBridge(root / "ION", tmp_path / "bridge-state")

    status = bridge.call_tool("ion.codex.carrier.status", {})
    cockpit = bridge.call_tool("ion.codex.carrier.cockpit", {})
    events = bridge.call_tool("ion.codex.carrier.events", {})
    raw_context = bridge.call_tool("ion.codex.raw_context.status", {})

    for result in (status, cockpit, events, raw_context):
        assert result.status == IonMcpToolStatus.OK
        assert result.execution_resolution == IonMcpExecutionResolution.READ_ONLY
        assert result.kernel_truth_mutated is False
        assert result.live_execution_authorized is False
        assert result.payload["production_authority"] is False
        assert result.payload["live_execution_authority"] is False
