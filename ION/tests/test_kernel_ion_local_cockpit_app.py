import json
import shutil
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import urllib.error
import urllib.request
import subprocess

from kernel.ion_cockpit_view_model import build_cockpit_surface_view_model
from kernel.ion_dual_codex_chat import WRITE_CONFIRMATION_TOKEN
from kernel.ion_project_cockpit import PROJECT_COCKPIT_WRITE_CONFIRMATION
from kernel.ion_local_cockpit_app import (
    REACT_CSP,
    build_cockpit_health,
    build_cockpit_html,
    build_react_cockpit_html,
    make_handler,
    resolve_react_static_asset,
)


LOCAL_ARCHIVE_SESSION_ID = "cccccccc-dddd-eeee-ffff-111111111111"


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def seed_codex_home(root: Path) -> Path:
    codex_home = root / "codex-home"
    write_jsonl(codex_home / "session_index.jsonl", [{"id": LOCAL_ARCHIVE_SESSION_ID, "thread_name": "Local archive"}])
    write_jsonl(codex_home / "history.jsonl", [{"session_id": LOCAL_ARCHIVE_SESSION_ID, "text": "local archive smoke"}])
    write_jsonl(
        codex_home / f"sessions/2026/05/23/rollout-{LOCAL_ARCHIVE_SESSION_ID}.jsonl",
        [
            {"type": "session_meta", "timestamp": "2026-05-23T12:00:00+00:00", "payload": {"id": LOCAL_ARCHIVE_SESSION_ID}},
            {"type": "event_msg", "timestamp": "2026-05-23T12:01:00+00:00", "payload": {"type": "user_message", "message": "local archive smoke"}},
        ],
    )
    return codex_home


def seed_branch_action_root(root: Path) -> None:
    registry_source = Path.cwd() / "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml"
    registry_target = root / "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml"
    registry_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(registry_source, registry_target)
    (root / "ION/03_registry/boots").mkdir(parents=True, exist_ok=True)
    (root / "ION/04_packages/kernel").mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-cockpit-branch-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# Test Authority\n\nPurpose: local cockpit action branch smoke.\n", encoding="utf-8")


def test_local_cockpit_health_is_guarded_candidate_state_only(tmp_path: Path):
    result = build_cockpit_health(tmp_path)

    assert result["schema_id"] == "ion.local_cockpit_app.v1"
    assert result["verdict"] == "ION_LOCAL_COCKPIT_APP_READY"
    assert result["visibility_only"] is False
    assert result["guarded_candidate_state_write_authority"] is True
    assert result["project_cockpit_write_confirmation"] == PROJECT_COCKPIT_WRITE_CONFIRMATION
    assert result["accepted_state_authority"] is False
    assert result["production_authority"] is False
    assert result["live_execution_authority"] is False


def test_local_cockpit_html_renders_codex_and_service_state():
    model = {
        "runtime": {"status": "ready", "shell_root": "/tmp/ion", "blocked": False},
        "top_bar": {"objective": "cockpit smoke", "gate_count": 0, "steward_queue_count": 0, "operator_queue_pending": 0},
        "local_services": {
            "status": "ready",
            "services": [
                {
                    "unit_name": "ion-cockpit-app.service",
                    "status": "ready",
                    "health_url": "http://127.0.0.1:8788/health",
                    "findings": [],
                }
            ],
        },
        "chatgpt_browser_mcp": {
            "transport_state": "TUNNEL_RUNNING_VERIFIED",
            "active_connector_url": "https://ion.helixion.net/mcp",
            "codex_queue_runner": {
                "verdict": "ION_CODEX_QUEUE_RUNNER_READY",
                "queued_request_count": 0,
                "active_process_running": False,
                "next_request_path": None,
                "reconciliation": {"write": False},
            },
            "agent_invocation_broker": {"verdict": "ION_AGENT_INVOCATION_BROKER_READY"},
        },
        "queues": {"human_gates": [], "steward_integration": []},
        "timeline": [{"source": "work", "event_type": "packet", "status": "ready", "detail": "visible"}],
        "receipts": [{"name": "receipt.json", "path": "ION/receipt.json", "authority_class": "WITNESS"}],
        "source_paths": {"work": "ION/05_context/current/ACTIVE_WORK_PACKET.json"},
    }

    html = build_cockpit_html(json.loads(json.dumps(model)))

    assert "ION LOCAL COCKPIT" in html
    assert "cockpit smoke" in html
    assert "ION_CODEX_QUEUE_RUNNER_READY" in html
    assert "ion-cockpit-app.service" in html
    assert "Reconciliation write" in html


def test_local_cockpit_react_bundle_helpers_are_local_only(tmp_path: Path):
    dist = tmp_path / "ION/08_ui/joc_cockpit_shell/dist"
    asset = dist / "assets/app.js"
    asset.parent.mkdir(parents=True)
    (dist / "index.html").write_text("<main id=\"root\"></main>", encoding="utf-8")
    asset.write_text("console.log('ion')", encoding="utf-8")

    assert build_react_cockpit_html(tmp_path) == "<main id=\"root\"></main>"
    assert resolve_react_static_asset(tmp_path, "/joc-static/assets/app.js") == asset.resolve()
    assert resolve_react_static_asset(tmp_path, "/joc-static/../secret") is None


def test_react_cockpit_csp_allows_cloudflare_insights_beacon_without_inline_scripts():
    assert "script-src 'self' https://static.cloudflareinsights.com" in REACT_CSP
    assert "connect-src 'self' https://cloudflareinsights.com" in REACT_CSP
    assert "script-src 'unsafe-inline'" not in REACT_CSP
    assert "frame-ancestors 'none'" in REACT_CSP


def test_cockpit_weave_surface_uses_materialized_domain_weaver_projection(tmp_path: Path):
    projection_path = tmp_path / "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    projection_path.parent.mkdir(parents=True)
    projection_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.projection.v0_1_candidate",
                "weave_status": "ready_for_reproof",
                "summary": {
                    "current_capability_class": "approval_governed_visual_proof_live_hydration_operator_rejection_blocked",
                    "usable_domain_count": 7,
                    "active_domain_count": 5,
                    "candidate_domain_count": 2,
                    "candidate_covered_domain_count": 6,
                    "covered_domain_count": 5,
                    "gap_count": 3,
                    "edge_count": 11,
                },
                "domains": [{"domain_id": "ui_development", "status": "candidate"}],
                "agents": [{"role_id": "visual_proof_auditor", "status": "bound"}],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    model = build_cockpit_surface_view_model(tmp_path, surface="weave")

    assert model["surface"] == "weave"
    assert model["codex_capsule_chat"]["verdict"] == "deferred"
    assert model["agent_control_plane"]["summary"]["domain_weaver_gap_count"] == 3
    assert model["agent_control_plane"]["domain_weaver"]["summary"]["current_capability_class"] == (
        "approval_governed_visual_proof_live_hydration_operator_rejection_blocked"
    )
    assert model["agent_control_plane"]["diagnostics"]["full_agent_control_plane_deferred"] is True


def test_local_cockpit_serves_weave_surface_endpoint(monkeypatch, tmp_path: Path):
    captured = {}

    def fake_surface_model(root: Path, *, surface: str):
        captured["root"] = root
        captured["surface"] = surface
        return {"schema_id": "ion.cockpit_surface_view_model.v1", "surface": surface}

    monkeypatch.setattr("kernel.ion_local_cockpit_app.build_cockpit_surface_view_model", fake_surface_model)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{server.server_address[1]}/cockpit/weave/model.json", timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["surface"] == "weave"
        assert captured["surface"] == "weave"
        assert captured["root"] == tmp_path
    finally:
        server.shutdown()


def test_local_cockpit_action_branch_invoke_endpoint_profiles_large_artifact(tmp_path: Path):
    seed_branch_action_root(tmp_path)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_address[1]}/cockpit/action-branch/invoke",
            data=json.dumps(
                {
                    "branch_id": "large_artifact_intelligence",
                    "route_id": "large_file_profile",
                    "args": {"path": "ION/REPO_AUTHORITY.md"},
                    "expected_route_schema_version": "v0",
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))

        delegated = payload["delegated_result"]
        assert payload["ok"] is True
        assert payload["branch_id"] == "large_artifact_intelligence"
        assert payload["route_id"] == "large_file_profile"
        assert payload["mutates_active_state"] is False
        assert delegated["content_returned"] == "metadata_only"
        assert delegated["path"] == "ION/REPO_AUTHORITY.md"
        assert delegated["production_authority"] is False
        assert delegated["live_execution_authority"] is False
        assert delegated["accepted_state_claim"] is False
    finally:
        server.shutdown()


def test_local_cockpit_records_project_blocker_candidate_receipt(tmp_path: Path):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_address[1]}/cockpit/projects/blocker/create",
            data=json.dumps(
                {
                    "confirmation": PROJECT_COCKPIT_WRITE_CONFIRMATION,
                    "title": "Local app blocker smoke",
                    "detail": "Candidate project cockpit blocker write.",
                    "severity": "medium",
                    "required_next_action": "Verify receipt path.",
                    "evidence_refs": "ION/tests/test_kernel_ion_local_cockpit_app.py",
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["ok"] is True
        assert payload["record_type"] == "blocker"
        assert payload["record"]["title"] == "Local app blocker smoke"
        assert payload["accepted_state_authority"] is False
        assert (tmp_path / payload["ledger_path"]).exists()
        assert (tmp_path / payload["receipt"]["path"]).exists()

        resolve_request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_address[1]}/cockpit/projects/blocker/resolve",
            data=json.dumps(
                {
                    "confirmation": PROJECT_COCKPIT_WRITE_CONFIRMATION,
                    "record_id": payload["record"]["blocker_id"],
                    "resolution": "Receipt write verified.",
                    "evidence_refs": payload["receipt"]["path"],
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(resolve_request, timeout=5) as response:
            resolve_payload = json.loads(response.read().decode("utf-8"))
        assert resolve_payload["ok"] is True
        assert resolve_payload["record"]["status"] == "resolved"
    finally:
        server.shutdown()


def test_local_cockpit_domain_weaver_action_endpoint_routes_to_action_helper(tmp_path: Path, monkeypatch):
    calls: list[dict] = []

    def fake_domain_weaver_action(root: Path, payload: dict):
        calls.append({"root": Path(root), "payload": dict(payload)})
        return {
            "schema_id": "ion.domain_weaver.operator_action_result.v0_1",
            "ok": True,
            "action": payload.get("action"),
            "receipt_paths": ["ION/05_context/current/domain_weaver/receipts/test.json"],
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        }

    monkeypatch.setattr("kernel.ion_local_cockpit_app.execute_domain_weaver_action", fake_domain_weaver_action)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_address[1]}/cockpit/domain-weaver/action",
            data=json.dumps(
                {
                    "action": "refresh_queue_governor",
                    "confirmation": WRITE_CONFIRMATION_TOKEN,
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["ok"] is True
        assert payload["action"] == "refresh_queue_governor"
        assert payload["accepted_state_authority"] is False
        assert calls == [
            {
                "root": tmp_path,
                "payload": {"action": "refresh_queue_governor", "confirmation": WRITE_CONFIRMATION_TOKEN},
            }
        ]
    finally:
        server.shutdown()


def test_local_cockpit_agent_start_endpoint_uses_direct_codex_broker(tmp_path: Path, monkeypatch):
    captured = {}

    def fake_invoke_agent(_root, **kwargs):
        captured.update(kwargs)
        return {
            "ok": True,
            "result": "BACKEND_CODEX_STARTED",
            "invocation_path": "ION/05_context/current/chatgpt_connector/agent_invocations/test.json",
            "production_authority": False,
            "live_execution_authority": False,
        }

    monkeypatch.setattr("kernel.ion_local_cockpit_app.invoke_agent", fake_invoke_agent)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_address[1]}/cockpit/agents/start",
            data=json.dumps({"agent": "role.mason", "domain_id": "domain.construction_routing_integration", "objective": "direct codex endpoint smoke"}).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["ok"] is True
        assert captured["agent"] == "role.mason"
        assert captured["objective"] == "direct codex endpoint smoke"
        assert captured["mode"] == "direct_codex"
        assert captured["queue"] is True
        assert captured["start"] is True
        assert captured["domain_id"] == "domain.construction_routing_integration"
        assert captured["use_codex_mount"] is True
        assert captured["target_root_id"] == "active_ion_control"
        assert captured["movement_class"] == "ION_KERNEL_CONTROL_MOVEMENT"
    finally:
        server.shutdown()


def test_local_cockpit_agent_relay_endpoints_route_to_broker(tmp_path: Path, monkeypatch):
    captured: dict[str, dict] = {}

    def fake_create_relay(_root, payload):
        captured["create"] = dict(payload)
        return {"ok": True, "relay_id": "relay-smoke", "production_authority": False, "live_execution_authority": False}

    def fake_respond_relay(_root, payload):
        captured["respond"] = dict(payload)
        return {"ok": True, "relay_id": payload["relay_id"], "status": "QUEUED", "production_authority": False, "live_execution_authority": False}

    def fake_settle(_root, payload):
        captured["settle"] = dict(payload)
        return {"ok": True, "status": "TERMINAL_ACCEPTED", "production_authority": False, "live_execution_authority": False}

    monkeypatch.setattr("kernel.ion_local_cockpit_app.create_agent_relay_message", fake_create_relay)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.respond_agent_relay", fake_respond_relay)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.settle_agent_invocation", fake_settle)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_address[1]}"
        for endpoint, payload in [
            ("/cockpit/agents/relay/create", {"invocation_id": "agent-1", "to": "role.ionologist", "question": "relay smoke"}),
            ("/cockpit/agents/relay/respond", {"relay_id": "relay-smoke", "answered_by": "role.ionologist", "response": "answer smoke"}),
            ("/cockpit/agents/settle", {"invocation_id": "agent-1", "terminal_state": "accepted", "evidence_refs": ["receipt.json"]}),
        ]:
            request = urllib.request.Request(
                f"{base}{endpoint}",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=5) as response:
                result = json.loads(response.read().decode("utf-8"))
            assert result["ok"] is True

        assert captured["create"]["to"] == "role.ionologist"
        assert captured["respond"]["answered_by"] == "role.ionologist"
        assert captured["settle"]["terminal_state"] == "accepted"
    finally:
        server.shutdown()


def test_local_cockpit_agent_comms_endpoints_route_to_comms_substrate(tmp_path: Path, monkeypatch):
    captured: dict[str, dict] = {}

    def fake_send(_root, payload):
        captured["send"] = dict(payload)
        return {"ok": True, "message_id": "msg-smoke", "thread_id": "thread-smoke", "production_authority": False, "live_execution_authority": False}

    def fake_ack(_root, payload):
        captured["ack"] = dict(payload)
        return {"ok": True, "message_id": payload["message_id"], "status": "acknowledged", "production_authority": False, "live_execution_authority": False}

    def fake_list(_root, **kwargs):
        captured["list"] = dict(kwargs)
        return {"ok": True, "threads": [], "production_authority": False, "live_execution_authority": False}

    def fake_thread(_root, thread_id, **kwargs):
        captured["thread"] = {"thread_id": thread_id, **kwargs}
        return {"ok": True, "thread": {"thread_id": thread_id}, "messages": [], "production_authority": False, "live_execution_authority": False}

    def fake_branch(_root, payload):
        captured["branch"] = dict(payload)
        return {"ok": True, "new_thread_id": "thread-branch", "source_message_id": payload["source_message_id"], "production_authority": False, "live_execution_authority": False}

    def fake_run_start(_root, payload):
        captured["run_start"] = dict(payload)
        return {"ok": True, "run_id": "run-smoke", "thread_ids": ["thread-smoke"], "production_authority": False, "live_execution_authority": False}

    def fake_run_pickup(_root, payload):
        captured["run_pickup"] = dict(payload)
        return {"ok": True, "run_id": payload["run_id"], "processed_directive_count": 1, "production_authority": False, "live_execution_authority": False}

    def fake_run_worker(_root, payload):
        captured["run_worker"] = dict(payload)
        return {
            "ok": True,
            "run_id": payload["run_id"],
            "workpack_path": payload["workpack_path"],
            "worker_started": True,
            "request_specific_worker_start": True,
            "production_authority": False,
            "live_execution_authority": False,
        }

    def fake_run_continue(_root, payload):
        captured["run_continue"] = dict(payload)
        return {"ok": True, "run_id": payload["run_id"], "worker_start_count": 1, "production_authority": False, "live_execution_authority": False}

    def fake_run_audit(_root, payload):
        captured["run_audit"] = dict(payload)
        return {"ok": True, "run_id": payload["run_id"], "audit_gate": {"state": "clean", "clean": True}, "production_authority": False, "live_execution_authority": False}

    def fake_dispatch_route(_root, payload):
        captured["dispatch_route"] = dict(payload)
        return {"ok": True, "dispatch_id": "dispatch-smoke", "run_id": "run-smoke", "production_authority": False, "live_execution_authority": False}

    def fake_dispatch_tick(_root, payload):
        captured["dispatch_tick"] = dict(payload)
        return {"ok": True, "run_id": payload["run_id"], "production_authority": False, "live_execution_authority": False}

    def fake_dispatch_pause(_root, payload):
        captured["dispatch_pause"] = dict(payload)
        return {"ok": True, "state": {"paused": payload["paused"]}, "production_authority": False, "live_execution_authority": False}

    def fake_dispatch_runner(_root, payload):
        captured["dispatch_runner"] = dict(payload)
        return {"ok": True, "tick_count": payload.get("max_ticks", 1), "production_authority": False, "live_execution_authority": False}

    monkeypatch.setattr("kernel.ion_local_cockpit_app.send_agent_message", fake_send)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.ack_agent_message", fake_ack)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.list_agent_threads", fake_list)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.read_agent_thread", fake_thread)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.create_agent_message_branch", fake_branch)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.start_agent_comms_run", fake_run_start)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.pickup_agent_comms_run", fake_run_pickup)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.continue_agent_comms_run", fake_run_continue)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.start_agent_comms_run_worker", fake_run_worker)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.audit_agent_comms_run", fake_run_audit)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.route_steward_dispatcher", fake_dispatch_route)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.tick_steward_dispatcher", fake_dispatch_tick)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.run_steward_dispatcher_runner", fake_dispatch_runner)
    monkeypatch.setattr("kernel.ion_local_cockpit_app.pause_steward_dispatcher", fake_dispatch_pause)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_address[1]}"
        for endpoint, payload in [
            ("/cockpit/agents/comms/send", {"from_role": "operator", "to_roles": ["role.steward"], "body": "message smoke"}),
            ("/cockpit/agents/comms/ack", {"message_id": "msg-smoke", "ack_by": "role.steward"}),
            ("/cockpit/agents/comms/list", {"role_id": "role.steward", "channel_id": "team"}),
            ("/cockpit/agents/comms/thread", {"thread_id": "thread-smoke", "role_id": "role.steward"}),
            ("/cockpit/agents/comms/branch", {"source_message_id": "msg-smoke"}),
            ("/cockpit/agents/comms/run/start", {"objective": "run smoke", "body": "start run"}),
            ("/cockpit/agents/comms/run/pickup", {"run_id": "run-smoke"}),
            ("/cockpit/agents/comms/run/continue", {"run_id": "run-smoke"}),
            ("/cockpit/agents/comms/run/start-worker", {"run_id": "run-smoke", "workpack_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/run-smoke.json"}),
            ("/cockpit/agents/comms/run/audit", {"run_id": "run-smoke"}),
            ("/cockpit/agents/dispatcher/route", {"objective": "dispatch smoke", "body": "@steward route"}),
            ("/cockpit/agents/dispatcher/tick", {"run_id": "run-smoke"}),
            ("/cockpit/agents/dispatcher/runner", {"run_id": "run-smoke", "max_ticks": 2}),
            ("/cockpit/agents/dispatcher/pause", {"paused": True}),
        ]:
            request = urllib.request.Request(
                f"{base}{endpoint}",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=5) as response:
                result = json.loads(response.read().decode("utf-8"))
            assert result["ok"] is True

        assert captured["send"]["body"] == "message smoke"
        assert captured["ack"]["ack_by"] == "role.steward"
        assert captured["list"]["role_id"] == "role.steward"
        assert captured["thread"]["thread_id"] == "thread-smoke"
        assert captured["branch"]["source_message_id"] == "msg-smoke"
        assert captured["run_start"]["objective"] == "run smoke"
        assert captured["run_pickup"]["run_id"] == "run-smoke"
        assert captured["run_continue"]["run_id"] == "run-smoke"
        assert captured["run_worker"]["workpack_path"].endswith("run-smoke.json")
        assert captured["run_audit"]["run_id"] == "run-smoke"
        assert captured["dispatch_route"]["objective"] == "dispatch smoke"
        assert captured["dispatch_tick"]["run_id"] == "run-smoke"
        assert captured["dispatch_pause"]["paused"] is True
    finally:
        server.shutdown()


def test_local_cockpit_agent_spawn_template_endpoint_routes_to_template_layer(tmp_path: Path, monkeypatch):
    captured: dict[str, dict] = {}

    def fake_spawn(_root, payload):
        captured["spawn"] = dict(payload)
        return {
            "ok": True,
            "schema_id": "ion.agent_spawn_template.result.v1",
            "template_id": payload["template_id"],
            "dispatch_mode": payload["dispatch_mode"],
            "spawn_status": "WORKPACK_PREPARED",
            "production_authority": False,
            "live_execution_authority": False,
        }

    monkeypatch.setattr("kernel.ion_local_cockpit_app.execute_agent_spawn_template", fake_spawn)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_address[1]}/cockpit/agents/spawn-template",
            data=json.dumps(
                {
                    "template_id": "agent_workpack_decision",
                    "dispatch_mode": "prepare_workpack",
                    "agent": "role.mason",
                    "domain_id": "domain.construction_routing_integration",
                    "objective": "spawn template smoke",
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["ok"] is True
        assert captured["spawn"]["template_id"] == "agent_workpack_decision"
        assert captured["spawn"]["dispatch_mode"] == "prepare_workpack"
        assert captured["spawn"]["agent"] == "role.mason"
    finally:
        server.shutdown()


def test_local_cockpit_serves_application_dev_bridge_and_catalog_proxy(monkeypatch, tmp_path: Path):
    class CatalogHandler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if self.path != "/apps.json":
                self.send_response(404)
                self.end_headers()
                return
            body = json.dumps({"summary": {"count": 1, "launchable": 1}, "apps": [{"slug": "demo"}]}).encode("utf-8")
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            return

    catalog_server = ThreadingHTTPServer(("127.0.0.1", 0), CatalogHandler)
    catalog_thread = Thread(target=catalog_server.serve_forever, daemon=True)
    catalog_thread.start()
    monkeypatch.setenv("ION_APPLICATION_DEV_LAUNCHER_URL", f"http://127.0.0.1:{catalog_server.server_address[1]}")

    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_address[1]}"
        with urllib.request.urlopen(f"{base}/projects/application-dev", timeout=5) as response:
            html = response.read().decode("utf-8")
        assert "Application Dev Apps" in html
        assert "/projects/application-dev/apps.json" in html

        with urllib.request.urlopen(f"{base}/projects/application-dev/apps.json", timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert payload["summary"]["count"] == 1
        assert payload["apps"][0]["slug"] == "demo"
    finally:
        server.shutdown()
        catalog_server.shutdown()


def test_local_cockpit_serves_codex_archive_endpoint(monkeypatch, tmp_path: Path):
    codex_home = seed_codex_home(tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_address[1]}/cockpit/chat/archive.json?session_id={LOCAL_ARCHIVE_SESSION_ID}"
        with urllib.request.urlopen(url, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert payload["schema_id"] == "ion.codex_conversation_archive.v1"
        assert payload["sessions"][0]["session_id"] == LOCAL_ARCHIVE_SESSION_ID
        assert payload["selected_session_excerpt"]["found"] is True
        assert payload["raw_transcript_exported"] is False

        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_address[1]}/cockpit/chat/archive/attach",
            data=json.dumps({"session_id": LOCAL_ARCHIVE_SESSION_ID, "confirmation": WRITE_CONFIRMATION_TOKEN}).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            attach_payload = json.loads(response.read().decode("utf-8"))
        assert attach_payload["ok"] is True
        assert attach_payload["attachment"]["session_id"] == LOCAL_ARCHIVE_SESSION_ID
        assert attach_payload["packet"]["codex_resume"]["command"] == ["codex", "resume", LOCAL_ARCHIVE_SESSION_ID]
        branch_request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_address[1]}/cockpit/chat/branch",
            data=json.dumps({
                "confirmation": WRITE_CONFIRMATION_TOKEN,
                "parent_kind": "archive_session",
                "parent_session_id": LOCAL_ARCHIVE_SESSION_ID,
                "title": "Local branch",
                "objective": "Branch the local archive smoke.",
            }).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(branch_request, timeout=5) as response:
            branch_payload = json.loads(response.read().decode("utf-8"))
        assert branch_payload["ok"] is True
        assert branch_payload["branch"]["codex_fork"]["command_text"] == f"codex fork {LOCAL_ARCHIVE_SESSION_ID}"
        assert branch_payload["branch"]["codex_fork"]["cockpit_spawned_process"] is False
    finally:
        server.shutdown()


def test_local_cockpit_serves_codex_rollback_diff_endpoint(tmp_path: Path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "ion@example.test"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "ION Test"], cwd=tmp_path, check=True, capture_output=True, text=True)
    target = tmp_path / "app.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "app.py"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True, text=True)
    target.write_text("VALUE = 2\n", encoding="utf-8")

    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_address[1]}"
        capture_request = urllib.request.Request(
            f"{base}/cockpit/chat/git/rollback/capture",
            data=json.dumps({"confirmation": WRITE_CONFIRMATION_TOKEN, "label": "local route"}).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(capture_request, timeout=5) as response:
            capture_payload = json.loads(response.read().decode("utf-8"))
        assert capture_payload["ok"] is True

        with urllib.request.urlopen(f"{base}/cockpit/chat/diffs.json", timeout=5) as response:
            model = json.loads(response.read().decode("utf-8"))
        assert model["schema_id"] == "ion.codex_git_rollback.v1"
        assert model["summary"]["checkpoint_count"] == 1
        assert model["summary"]["current_file_count"] >= 1
        assert "app.py" in model["current_worktree"]["diff_stats"]["files"]
        assert model["checkpoints"][0]["rollback_supported"] is True
    finally:
        server.shutdown()


def test_local_cockpit_chat_turn_uses_raw_codex_cli_flag(monkeypatch, tmp_path: Path):
    _seed_root = seed_codex_home(tmp_path)
    monkeypatch.setenv("CODEX_HOME", _seed_root.as_posix())
    captured: dict[str, object] = {}

    def fake_record_chat_turn(_root, **kwargs):
        captured.update(kwargs)
        return {
            "ok": True,
            "assistant_turn": {
                "author": "codex_cli",
                "message": f"Raw Codex CLI reply: {kwargs.get('message')}",
                "response_mode": "raw_codex_cli",
                "response_carrier": None,
                "wrapper_prompt_used": False,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    monkeypatch.setattr("kernel.ion_local_cockpit_app.record_chat_turn", fake_record_chat_turn)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_address[1]}/cockpit/chat/turn",
            data=json.dumps({
                "lane_id": "codex_general",
                "message": "hello from cockpit",
                "author": "operator",
                "execution_mode": "respond_only",
                "client_id": "pending_chat_turn_test",
                "target_session_id": "019e8b2b-c770-71d3-b2d8-e4c1c14eba0b",
                "codex_session_transport": "app_server",
                "ide_context_bridge": {
                    "source": "codex_ide_workbench",
                    "active_view": "diffs",
                    "selected_path": "ION/08_ui/joc_cockpit_shell/CodexIdeWorkbenchPanel.tsx",
                },
            }).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["ok"] is True
        assert captured["raw_codex_cli_enabled"] is True
        assert captured["client_id"] == "pending_chat_turn_test"
        assert captured["target_session_id"] == "019e8b2b-c770-71d3-b2d8-e4c1c14eba0b"
        assert captured["codex_session_transport"] == "app_server"
        assert captured["ide_context_bridge"]["active_view"] == "diffs"
        assert captured["ide_context_bridge"]["selected_path"] == "ION/08_ui/joc_cockpit_shell/CodexIdeWorkbenchPanel.tsx"
        assert "response_carrier_enabled" not in captured
        assert payload["assistant_turn"]["author"] == "codex_cli"
        assert payload["assistant_turn"]["response_mode"] == "raw_codex_cli"
        assert payload["assistant_turn"]["message"] == "Raw Codex CLI reply: hello from cockpit"
    finally:
        server.shutdown()


def test_local_cockpit_serves_same_port_system_diagnostics(tmp_path: Path):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{server.server_address[1]}/cockpit/system/model.json", timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["schema_id"] == "ion.system_diagnostics.v1"
        assert payload["authority"]["production_authority"] is False
        assert payload["authority"]["live_execution_authority"] is False
        assert "summary" in payload
        assert "dev_servers" in payload
        assert "data_quality" in payload
        assert "cleanup_candidates" in payload
    finally:
        server.shutdown()


def test_local_cockpit_system_diagnostics_rejects_unsupported_action(tmp_path: Path):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_address[1]}/cockpit/system/preview_action",
            data=json.dumps({"action": {"action_type": "delete_everything"}}).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(request, timeout=8)
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))
        else:  # pragma: no cover - endpoint should reject unsupported mutation shape
            raise AssertionError("unsupported action unexpectedly accepted")

        assert payload["ok"] is False
        assert "unsupported action type" in payload["error"]
    finally:
        server.shutdown()
