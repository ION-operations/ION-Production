from pathlib import Path


def test_agent_control_plane_ui_consumes_compact_home_projection_artifacts() -> None:
    ui_path = Path(__file__).resolve().parents[1] / "08_ui/joc_cockpit_shell/AgentControlPlanePanel.tsx"
    source = ui_path.read_text(encoding="utf-8")

    assert "agent_home_views" in source
    assert "scout_context_card" in source
    assert "self_improvement_loop" in source
    assert "CompactHomeProjectionCard" in source

    # Smoke guard: the UI should render compact projection artifacts, not poll raw logs.
    assert "messages.jsonl" not in source
    assert "ACTIVE_CARRIER_MESSAGE_QUEUE.json" not in source
    assert "ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json" not in source
