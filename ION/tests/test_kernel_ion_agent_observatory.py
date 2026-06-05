import json
from pathlib import Path

import pytest
import yaml

from kernel.ion_action_mcp_branch_leaders import action_branch_describe, action_branch_invoke
from kernel.ion_agent_observatory import CONFIRMATION_TOKEN, invoke_agent_observatory_route

SESSION_ID = "019e8b2b-c770-71d3-b2d8-e4c1c14eba0b"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


@pytest.fixture()
def observatory_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "ION_Developement"
    (root / "ION/03_registry").mkdir(parents=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("candidate test authority\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname='ion-test'\n", encoding="utf-8")
    registry_src = Path.cwd() / "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml"
    registry_dst = root / "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml"
    registry_dst.write_text(registry_src.read_text(encoding="utf-8"), encoding="utf-8")
    workspace_registry = {
        "schema_id": "ion.workspace_root_registry.v1_candidate",
        "default_root_id": "active_ion_control",
        "roots": [
            {
                "root_id": "active_ion_control",
                "label": "Active ION control root",
                "absolute_path": str(root),
                "root_class": "active_ion_control_root",
                "allowed_operations": ["read", "search", "profile", "spawn_agent"],
                "forbidden_operations": ["run_shell", "git_push", "deletion", "secrets", "accepted_state", "production"],
                "requires_operator_confirmation": True,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
                "accepted_state_authority": False,
                "accepted_state_claim": False,
                "git_push_authority": False,
                "deletion_authority": False,
                "max_bytes": 64000,
                "max_files": 100,
                "path_exclusions": [".git", ".env"],
                "proof_requirements": ["root_id", "cwd", "authority_flags"],
            },
            {
                "root_id": "codex_peer_worker_sandbox_root",
                "label": "Codex peer worker sandbox",
                "absolute_path": str(root / "ION/05_context/current/codex_peer_worker_sandboxes"),
                "root_class": "sandbox_root",
                "allowed_operations": ["read", "search", "profile", "spawn_agent", "write_candidate", "run_tests", "run_shell"],
                "forbidden_operations": ["git_push", "deletion", "secrets", "accepted_state", "production"],
                "requires_operator_confirmation": True,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
                "accepted_state_authority": False,
                "accepted_state_claim": False,
                "git_push_authority": False,
                "deletion_authority": False,
                "max_bytes": 64000,
                "max_files": 100,
                "path_exclusions": [".git", ".env"],
                "proof_requirements": ["root_id", "sandbox_path"],
            },
        ],
    }
    (root / "ION/03_registry/ion_workspace_root_registry.yaml").write_text(yaml.safe_dump(workspace_registry), encoding="utf-8")
    _write_json(root / "ION/05_context/current/codex_solo/STATUS.json", {"phase": "domain_weaver_test", "blocker": "materialization blocked until exact-active proof"})
    (root / "ION/05_context/current/codex_solo/HOT_CONTEXT.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/05_context/current/codex_solo/HOT_CONTEXT.md").write_text("Domain Weaver HOT context exact-active binding blocked.\n", encoding="utf-8")
    _write_json(root / "ION/05_context/current/domain_weaver/live_carrier_binding/ACTIVE_INVOKABLE_BINDING_PROOF_ROWS.candidate.json", {"summary": {"exact_active_binding_count": 0, "missing_exact_active_binding_count": 6, "materialization_ready": False, "topology_materialization_allowed": False}})
    _write_json(root / "ION/05_context/current/domain_weaver/live_carrier_binding/EXACT_ACTIVE_SPECIALIST_BINDING_RESULT.latest.json", {"created_at": "2026-06-03T01:00:00+00:00", "next_packet": "focused proof repair"})
    _write_json(root / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json", {"generated_at": "2026-06-03T01:05:00+00:00", "active_run": {"run_id": "run-domain-weaver", "request_id": "req-domain-weaver", "objective": "Domain Weaver exact-active proof"}})
    _write_json(root / "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json", {"request_count": 1, "requests": [{"request_id": "req-domain-weaver", "status": "QUEUED_FOR_CODEX_CARRIER", "objective": "Domain Weaver exact-active proof", "created_at": "2026-06-03T01:00:00+00:00"}]})
    _write_json(root / "ION/05_context/current/chatgpt_connector/work_lanes/INDEX.json", {"schema_id": "ion.codex_work_lane_index.v0_1", "queued_request_count": 1, "needs_triage_count": 0, "lane_counts": {"audit_lane": 1}})
    _write_json(root / "ION/05_context/current/chatgpt_connector/task_returns/domain_weaver_return.json", {"created_at": "2026-06-03T01:10:00+00:00", "status": "RETURN_RECORDED_PROOF_ACCEPTED", "summary": "candidate worker return only"})
    live_dir = root / "ION/05_context/current/chatgpt_connector/codex_live_sessions" / SESSION_ID
    _write_json(live_dir / "session.json", {"session_id": SESSION_ID, "role_id": "lead_codex_domain_weaver_build_manager", "display_name": "Lead Codex Domain Weaver Build Manager", "domain_id": "domain.domain_weaver", "objective": "Manage Domain Weaver", "status": "active", "updated_at": "2026-06-03T01:12:00+00:00", "current_packet_id": "packet-test"})
    _write_json(root / "ION/05_context/current/chatgpt_connector/codex_live_sessions/INDEX.json", {"sessions": {SESSION_ID: {"session_id": SESSION_ID, "role_id": "lead_codex_domain_weaver_build_manager", "display_name": "Lead Codex Domain Weaver Build Manager", "domain_id": "domain.domain_weaver", "status": "active", "updated_at": "2026-06-03T01:12:00+00:00", "session_path": f"ION/05_context/current/chatgpt_connector/codex_live_sessions/{SESSION_ID}/session.json"}}})
    (live_dir / "inbox.jsonl").write_text(json.dumps({"message": "hello"}) + "\n", encoding="utf-8")
    (live_dir / "outbox.jsonl").write_text(json.dumps({"message": "reply"}) + "\n", encoding="utf-8")
    _write_json(root / "ION/05_context/current/gemini_ion_sandboxes/sandbox-a/result.json", {"created_at": "2026-06-03T01:11:00+00:00", "result": "sandbox candidate diff"})
    (root / "ION/08_ui/joc_cockpit_shell/dist").mkdir(parents=True, exist_ok=True)
    (root / "ION/08_ui/joc_cockpit_shell/dist/index.html").write_text("<div>cockpit</div>", encoding="utf-8")
    (root / "ION/08_ui/joc_cockpit_shell/AgentControlPlanePanel.tsx").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/08_ui/joc_cockpit_shell/AgentControlPlanePanel.tsx").write_text("export const panel = 'agents';\n", encoding="utf-8")
    (root / "ION/08_ui/joc_cockpit_shell/CodexWorkbenchShell.tsx").write_text("export const workbench = 'codex';\n", encoding="utf-8")
    (root / "ION/04_packages/kernel").mkdir(parents=True, exist_ok=True)
    (root / "ION/04_packages/kernel/ion_chatgpt_browser_mcp_http_preview.py").write_text("# endpoint fixture\n", encoding="utf-8")
    home = tmp_path / "home"
    session_file = home / ".codex/sessions/2026/06/02" / f"rollout-2026-06-02T21-49-22-{SESSION_ID}.jsonl"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_lines = [
        {"type": "session_meta", "timestamp": "2026-06-03T01:00:00+00:00", "payload": {"id": SESSION_ID, "cwd": str(root), "originator": "codex_cli", "model_provider": "openai"}},
        {"type": "response_item", "timestamp": "2026-06-03T01:01:00+00:00", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Domain Weaver status?"}]}},
        {"type": "response_item", "timestamp": "2026-06-03T01:02:00+00:00", "payload": {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "Nemesis returned next_packet_allowed; first seam kernel.ion_domain_weaver_io; no materialization."}]}},
    ]
    session_file.write_text("\n".join(json.dumps(line) for line in session_lines) + "\n", encoding="utf-8")
    monkeypatch.setenv("CODEX_HOME", str(home / ".codex"))
    monkeypatch.setenv("ION_AGENT_OBSERVATORY_SKIP_SERVICE_STATUS", "1")
    return root


def test_agent_observatory_overview_normalizes_sources_and_authority_false(observatory_root: Path):
    result = invoke_agent_observatory_route(observatory_root, route_id="agent_observatory_overview", args={"include_completed": True, "limit": 30})

    assert result["ok"] is True
    kinds = {row["agent_kind"] for row in result["agents"]}
    assert {"codex_saved_session", "codex_live_session", "codex_queue_worker", "domain_weaver_worker", "gemini_sandbox", "multi_root_spawn_packet", "cockpit_surface"} <= kinds
    for row in result["agents"]:
        assert row["authority"]["accepted_state_claim"] is False
        assert row["authority"]["production_authority"] is False
        assert row["authority"]["secrets_authority"] is False


def test_agent_observatory_missing_sources_do_not_crash(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = tmp_path / "root"
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("authority\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname='empty'\n", encoding="utf-8")
    (root / "ION/03_registry").mkdir(parents=True, exist_ok=True)
    (root / "ION/03_registry/ion_workspace_root_registry.yaml").write_text("roots: []\n", encoding="utf-8")
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "missing_codex"))
    monkeypatch.setenv("ION_AGENT_OBSERVATORY_SKIP_SERVICE_STATUS", "1")

    result = invoke_agent_observatory_route(root, route_id="agent_observatory_overview", args={"limit": 20})

    assert result["ok"] is True
    assert any(row["agent_kind"] == "source_unavailable" for row in result["agents"])


def test_agent_observatory_action_affordances_for_saved_session(observatory_root: Path):
    result = invoke_agent_observatory_route(observatory_root, route_id="agent_observatory_action_affordances", args={"session_id": SESSION_ID})

    assert result["ok"] is True
    routes = {action.get("route_id"): action for action in result["actions"]}
    action_ids = {action.get("action_id"): action for action in result["actions"]}
    assert "session_summary" in routes
    assert "session_transcript_slice" in routes
    assert "session_resume_send_preview" in routes
    assert action_ids["resume_send_preview_read_only"]["args"]["sandbox_mode"] == "read-only"
    assert action_ids["resume_send_preview_workspace_write"]["args"]["sandbox_mode"] == "workspace-write"
    assert action_ids["resume_send_read_only"]["requires_confirmation"] is True
    assert action_ids["resume_send_workspace_write"]["args"]["sandbox_mode"] == "workspace-write"
    assert action_ids["resume_send_workspace_write"]["requires_confirmation"] is True


def test_agent_observatory_action_affordances_for_queue_run(observatory_root: Path):
    result = invoke_agent_observatory_route(observatory_root, route_id="agent_observatory_action_affordances", args={"agent_ref": "codex_queue:current"})

    assert result["ok"] is True
    routes = {action.get("route_id") for action in result["actions"]}
    assert "status_summary" in routes
    assert "agent_observatory_latest_tail" in routes
    assert result["accepted_state_claim"] is False


def test_agent_observatory_domain_weaver_preserves_materialization_blocker(observatory_root: Path):
    result = invoke_agent_observatory_route(observatory_root, route_id="agent_observatory_domain_weaver_status", args={})

    assert result["ok"] is True
    assert result["exact_active_binding_count"] == 0
    assert result["missing_exact_active_binding_count"] == 6
    assert result["materialization_ready"] is False
    assert result["topology_materialization_allowed"] is False


def test_agent_observatory_cockpit_status_supabase_unavailable_cleanly(observatory_root: Path):
    result = invoke_agent_observatory_route(observatory_root, route_id="agent_observatory_cockpit_status", args={})

    assert result["ok"] is True
    assert result["supabase_availability"]["available"] is False
    assert result["accepted_state_claim"] is False


def test_agent_observatory_snapshot_requires_confirmation_and_idempotency(observatory_root: Path):
    no_gate = invoke_agent_observatory_route(observatory_root, route_id="agent_observatory_snapshot", args={})
    assert no_gate["ok"] is False
    assert no_gate["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"

    no_confirm = invoke_agent_observatory_route(observatory_root, route_id="agent_observatory_snapshot", args={"idempotency_key": "snap-test"})
    assert no_confirm["ok"] is False
    assert no_confirm["refusal_class"] == "CONFIRMATION_REQUIRED"

    written = invoke_agent_observatory_route(observatory_root, route_id="agent_observatory_snapshot", args={"idempotency_key": "snap-test", "confirmation": CONFIRMATION_TOKEN, "snapshot_name": "AGENT_OBSERVATORY_TEST.candidate.json"})
    assert written["ok"] is True
    replay = invoke_agent_observatory_route(observatory_root, route_id="agent_observatory_snapshot", args={"idempotency_key": "snap-test", "confirmation": CONFIRMATION_TOKEN, "snapshot_name": "AGENT_OBSERVATORY_TEST.candidate.json"})
    assert replay["idempotent_replay"] is True


def test_agent_observatory_rejects_unsafe_identifiers(observatory_root: Path):
    result = invoke_agent_observatory_route(observatory_root, route_id="agent_observatory_agent_detail", args={"session_id": "../bad"})

    assert result["ok"] is False
    assert result["refusal_class"] == "SCHEMA_INVALID"


def test_agent_observatory_branch_routes_visible_and_invokable(observatory_root: Path):
    described = action_branch_describe(observatory_root, branch_id="agent_observatory", depth="full")
    assert described["ok"] is True
    routes = {route["route_id"] for route in described["branch"]["routes"]}
    assert "agent_observatory_overview" in routes
    assert "agent_observatory_snapshot" in routes

    result = action_branch_invoke(observatory_root, branch_id="agent_observatory", route_id="agent_observatory_overview", args={"include_completed": True, "limit": 20}, expected_route_schema_version="v0")
    assert result["ok"] is True
    assert result["delegated_result"]["ok"] is True
    assert any(row["session_id"] == SESSION_ID for row in result["delegated_result"]["agents"])
