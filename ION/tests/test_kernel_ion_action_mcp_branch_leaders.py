import base64
import hashlib
import json
import os
import zipfile
from pathlib import Path

import yaml

from kernel.ion_action_mcp_branch_leaders import (
    REGISTRY_RELATIVE_PATH,
    action_branch_describe,
    action_branch_invoke,
    action_branch_list,
    action_branch_receipts,
    load_branch_leader_registry,
)
from kernel import ion_action_mcp_branch_leaders as branch_leaders
from kernel import ion_chatgpt_browser_mcp_connector_contract as connector_contract
from kernel import ion_codex_session_store_bridge as codex_session_store_bridge
from kernel import ion_runtime_service_control as runtime_services
from kernel.ion_chatgpt_browser_mcp_connector_contract import (
    BOUNDED_QUEUE_RECEIPT_TOOLS,
    STATUS_READ_TOOLS,
    call_chatgpt_connector_tool,
)
from kernel.ion_chatgpt_browser_mcp_http_preview import handle_mcp_jsonrpc
from kernel.ion_worker_shift_presence import claim_work_lease, load_shift_board, write_signon_receipt


def test_branch_leader_registry_loads_initial_branches():
    registry = load_branch_leader_registry(Path.cwd())
    branch_ids = {branch["branch_id"] for branch in registry["branches"]}

    assert registry["schema_id"] == "ion.action_mcp_branch_leader_registry.v0"
    assert {
        "branch_context",
        "gateway_core",
        "project_workbench",
        "codex_queue",
        "runtime_services",
        "worker_shift",
        "agent_swarm",
        "browser_queue",
        "supabase_cockpit",
        "context_graph",
        "receipts",
        "latest_context",
        "multi_root_workspace",
    }.issubset(branch_ids)


def test_branch_leader_registry_fallback_loads_without_pyyaml(monkeypatch):
    monkeypatch.setattr(branch_leaders, "yaml", None)

    registry = load_branch_leader_registry(Path.cwd())
    branch = next(item for item in registry["branches"] if item["branch_id"] == "codex_queue")
    routes = {route["route_id"]: route for route in branch["routes"]}

    assert routes["worker_trace"]["mcp_tool"] == "ion_codex_worker_trace"
    assert routes["worker_trace"]["mutates_state"] is False


def test_branch_list_and_describe_return_route_capsules():
    listed = action_branch_list(Path.cwd())
    described = action_branch_describe(Path.cwd(), branch_id="project_workbench", depth="full")

    assert listed["ok"] is True
    assert listed["branch_count"] >= 10
    assert any(branch["branch_id"] == "project_workbench" for branch in listed["branches"])
    assert any(branch["branch_id"] == "branch_context" for branch in listed["branches"])
    assert described["ok"] is True
    assert described["branch"]["branch_id"] == "project_workbench"
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert routes["context_capsule"]["owner_tool"] == "ion_project_context_capsule"
    assert routes["patch_apply"]["mutates_state"] is True
    assert routes["patch_apply"]["idempotency_required"] is True
    assert routes["patch_apply"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert routes["patch_apply"]["edit_lease_required"] is True
    assert routes["patch_apply"]["agent_id_required"] is True
    assert routes["patch_apply"]["lease_id_required"] is True
    assert routes["patch_apply"]["required_mutation_fields"] == [
        "idempotency_key",
        "confirmation",
        "agent_id",
        "lease_id",
    ]
    assert routes["patch_apply"]["lease_gate_public"]["gate_kind"] == "edit_lease"
    assert routes["patch_apply"]["lease_gate_public"]["central_active_lease_validation"] is True
    assert routes["patch_apply"]["lease_gate_public"]["handler_dynamic_target_gate_deferred"] is False
    assert routes["patch_apply"]["args_schema"]["required"] == [
        "project_id",
        "operations",
        "idempotency_key",
        "confirmation",
        "agent_id",
        "lease_id",
    ]
    assert routes["patch_apply"]["args_schema"]["properties"]["agent_id"]["type"] == "string"
    assert routes["patch_apply"]["args_schema"]["properties"]["lease_id"]["type"] == "string"
    assert described["branch_context"]["candidate_available"] is False

    repo_ingest = action_branch_describe(Path.cwd(), branch_id="repo_ingest", depth="full")
    repo_routes = {route["route_id"]: route for route in repo_ingest["branch"]["routes"]}
    assert repo_routes["apply_patch"]["edit_lease_required"] is True
    assert repo_routes["apply_patch"]["agent_id_required"] is True
    assert repo_routes["apply_patch"]["lease_id_required"] is True
    assert {"confirmation", "agent_id", "lease_id"}.issubset(
        set(repo_routes["apply_patch"]["args_schema"]["required"])
    )
    assert repo_routes["apply_create"]["artifact_lease_required"] is True
    assert repo_routes["apply_create"]["agent_id_required"] is True
    assert repo_routes["apply_create"]["lease_id_required"] is True
    assert repo_routes["apply_create"]["idempotency_required"] is True
    assert {"confirmation", "idempotency_key", "agent_id", "lease_id"}.issubset(
        set(repo_routes["apply_create"]["args_schema"]["required"])
    )
    assert repo_routes["artifact_upload_init"]["artifact_lease_required"] is True
    assert repo_routes["artifact_upload_init"]["agent_id_required"] is True
    assert repo_routes["artifact_upload_init"]["lease_id_required"] is True
    assert repo_routes["artifact_upload_init"]["idempotency_required"] is True
    assert {"confirmation", "idempotency_key", "agent_id", "lease_id"}.issubset(
        set(repo_routes["artifact_upload_init"]["args_schema"]["required"])
    )
    assert repo_routes["artifact_upload_chunk"]["artifact_lease_required"] is True
    assert repo_routes["artifact_upload_chunk"]["agent_id_required"] is True
    assert repo_routes["artifact_upload_chunk"]["lease_id_required"] is True
    assert repo_routes["artifact_upload_chunk"]["idempotency_required"] is True
    assert {"confirmation", "idempotency_key", "agent_id", "lease_id"}.issubset(
        set(repo_routes["artifact_upload_chunk"]["args_schema"]["required"])
    )
    assert repo_routes["artifact_upload_commit"]["artifact_lease_required"] is True
    assert repo_routes["artifact_upload_commit"]["agent_id_required"] is True
    assert repo_routes["artifact_upload_commit"]["lease_id_required"] is True
    assert repo_routes["artifact_upload_commit"]["idempotency_required"] is True
    assert {"confirmation", "idempotency_key", "agent_id", "lease_id"}.issubset(
        set(repo_routes["artifact_upload_commit"]["args_schema"]["required"])
    )

    browser_queue = action_branch_describe(Path.cwd(), branch_id="browser_queue", depth="full")
    browser_routes = {route["route_id"]: route for route in browser_queue["branch"]["routes"]}
    enqueue = browser_routes["enqueue"]
    receipts = browser_routes["receipts"]
    assert receipts["mutates_state"] is False
    assert receipts["idempotency_required"] is False
    assert receipts["confirmation_required"] is False
    assert "agent_id_required" not in receipts
    assert enqueue["mutates_state"] is True
    assert enqueue["invocable"] is False
    assert enqueue["idempotency_required"] is True
    assert enqueue["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert enqueue["agent_id_required"] is True
    assert enqueue["required_mutation_fields"] == [
        "idempotency_key",
        "confirmation",
        "agent_id",
    ]
    assert enqueue["args_schema"]["required"] == [
        "idempotency_key",
        "confirmation",
        "agent_id",
    ]

    codex_queue = action_branch_describe(Path.cwd(), branch_id="codex_queue", depth="full")
    codex_routes = {route["route_id"]: route for route in codex_queue["branch"]["routes"]}
    for route_id in ("request_work_packet", "process_once", "runner_reconcile", "supersede_duplicates"):
        route = codex_routes[route_id]
        assert route["mutates_state"] is True
        assert route["idempotency_required"] is True
        assert route["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
        assert route["agent_id_required"] is True
        assert route["write_intent_lease_required"] is True
        assert route["write_intent_lease_id_required"] is True
        assert route["lease_gate_public"]["gate_kind"] == "write_intent_lease"
        assert route["lease_gate_public"]["required_lease_type"] == "write_intent"
        assert route["lease_gate_public"]["lease_id_field"] == "write_intent_lease_id"
        assert route["lease_gate_public"]["central_active_lease_validation"] is True
        assert route["required_mutation_fields"] == [
            "idempotency_key",
            "confirmation",
            "agent_id",
            "write_intent_lease_id",
        ]
        assert {"agent_id", "write_intent_lease_id"}.issubset(set(route["args_schema"]["required"]))
    assert codex_routes["queue_status"]["mutates_state"] is False
    assert "agent_id_required" not in codex_routes["queue_status"]
    bridge_preview = codex_routes["transient_usage_limit_bridge_preview"]
    bridge_create = codex_routes["transient_usage_limit_bridge_create"]
    assert bridge_preview["mutates_state"] is False
    assert bridge_preview["owner_tool"] == "ion_branch_leader_gateway"
    assert bridge_preview["args_schema"]["required"] == ["run_packet_path"]
    assert bridge_create["mutates_state"] is True
    assert bridge_create["owner_tool"] == "ion_branch_leader_gateway"
    assert bridge_create["confirmation_required"] == "ION_CODEX_CARRIER_SESSION_BRIDGE_CONFIRMED"
    assert bridge_create["idempotency_required"] is True
    assert bridge_create["agent_id_required"] is True
    assert bridge_create["write_intent_lease_required"] is True
    assert bridge_create["write_intent_lease_id_required"] is True
    assert bridge_create["required_mutation_fields"] == [
        "idempotency_key",
        "confirmation",
        "agent_id",
        "write_intent_lease_id",
    ]
    assert {"run_packet_path", "agent_id", "write_intent_lease_id"}.issubset(set(bridge_create["args_schema"]["required"]))

    native_ide = action_branch_describe(Path.cwd(), branch_id="chatgpt_browser_carrier_context", depth="full")
    native_routes = {route["route_id"]: route for route in native_ide["branch"]["routes"]}
    native_apply = native_routes["native_ide_patch_apply"]
    assert native_routes["native_ide_status"]["mutates_state"] is False
    assert "agent_id_required" not in native_routes["native_ide_status"]
    assert native_apply["edit_lease_required"] is True
    assert native_apply["agent_id_required"] is True
    assert native_apply["lease_id_required"] is True
    assert native_apply["required_mutation_fields"] == [
        "idempotency_key",
        "confirmation",
        "agent_id",
        "lease_id",
        "target_paths",
    ]
    assert {"agent_id", "lease_id", "target_paths"}.issubset(set(native_apply["args_schema"]["required"]))


def test_browser_queue_enqueue_requires_mutation_actor_proof_before_noninvocable():
    no_idempotency = action_branch_invoke(
        Path.cwd(),
        branch_id="browser_queue",
        route_id="enqueue",
        args={"agent_id": "agent-browser-queue"},
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        Path.cwd(),
        branch_id="browser_queue",
        route_id="enqueue",
        args={"agent_id": "agent-browser-queue"},
        idempotency_key="browser-queue-enqueue-proof",
        expected_route_schema_version="v0",
    )
    no_actor = action_branch_invoke(
        Path.cwd(),
        branch_id="browser_queue",
        route_id="enqueue",
        idempotency_key="browser-queue-enqueue-proof",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    fully_proved_but_not_invocable = action_branch_invoke(
        Path.cwd(),
        branch_id="browser_queue",
        route_id="enqueue",
        args={"agent_id": "agent-browser-queue"},
        idempotency_key="browser-queue-enqueue-proof",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"
    assert no_actor["ok"] is False
    assert no_actor["refusal_class"] == "ACTOR_PROOF_REQUIRED"
    assert fully_proved_but_not_invocable["ok"] is False
    assert fully_proved_but_not_invocable["refusal_class"] == "ROUTE_NOT_INVOCABLE"


def test_codex_queue_request_work_packet_route_exposes_high_stakes_call_shape():
    described = action_branch_describe(Path.cwd(), branch_id="codex_queue", depth="full")

    assert described["ok"] is True
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    route = routes["request_work_packet"]
    enforcement = route["route_enforcement"]
    template = route["high_stakes_call_shape_template"]

    assert enforcement["high_stakes_requires_structured_route_metadata"] is True
    assert "codex_model_override.selected_model" in enforcement["required_fields_for_high_stakes"]
    assert enforcement["required_model_override"]["selected_model"] == "gpt-5.5"
    assert template["idempotency_key"] == "pckt-<stable-packet-id>"
    assert template["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert template["requested_model"] == "gpt-5.5"
    assert "agent_id" in enforcement["required_fields_for_high_stakes"]
    assert "write_intent_lease_id" in enforcement["required_fields_for_high_stakes"]
    assert template["agent_id"] == "<bound-worker-or-lead-agent-id>"
    assert template["write_intent_lease_id"] == "<worker-shift-write-intent-lease-id>"


def test_codex_queue_mutations_require_actor_and_write_intent_before_delegation():
    no_idempotency = action_branch_invoke(
        Path.cwd(),
        branch_id="codex_queue",
        route_id="request_work_packet",
        args={
            "objective": "bounded queue gate smoke",
            "agent_id": "agent-codex-queue",
            "write_intent_lease_id": "write-intent-codex-queue",
        },
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        Path.cwd(),
        branch_id="codex_queue",
        route_id="request_work_packet",
        args={
            "objective": "bounded queue gate smoke",
            "agent_id": "agent-codex-queue",
            "write_intent_lease_id": "write-intent-codex-queue",
        },
        idempotency_key="codex-queue-mutation-gate",
        expected_route_schema_version="v0",
    )
    no_actor = action_branch_invoke(
        Path.cwd(),
        branch_id="codex_queue",
        route_id="request_work_packet",
        args={
            "objective": "bounded queue gate smoke",
            "write_intent_lease_id": "write-intent-codex-queue",
        },
        idempotency_key="codex-queue-mutation-gate",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    no_write_intent = action_branch_invoke(
        Path.cwd(),
        branch_id="codex_queue",
        route_id="request_work_packet",
        args={
            "objective": "bounded queue gate smoke",
            "agent_id": "agent-codex-queue",
        },
        idempotency_key="codex-queue-mutation-gate",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"
    assert no_actor["ok"] is False
    assert no_actor["refusal_class"] == "ACTOR_PROOF_REQUIRED"
    assert no_write_intent["ok"] is False
    assert no_write_intent["refusal_class"] == "MUTATION_PROOF_REQUIRED"
    assert no_write_intent["required_fields"] == ["write_intent_lease_id"]


def _seed_codex_queue_write_intent_lease(
    root: Path,
    *,
    agent_id: str,
    lease_id: str,
    target_paths: list[str],
    route_id: str = "request_work_packet",
    mutation_context: str = "codex_queue",
    idempotency_key: str = "codex-queue-write-intent-gate",
) -> None:
    from datetime import datetime, timezone

    timestamp = datetime.now(timezone.utc).isoformat()
    board_path = root / "ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json"
    board_path.parent.mkdir(parents=True, exist_ok=True)
    board_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.worker_shift_board.v0_1",
                "updated_at": timestamp,
                "authority": {
                    "accepted_state_authority": False,
                    "production_authority": False,
                    "live_execution_authority": False,
                    "secrets_authority": False,
                },
                "active_shifts": [],
                "active_leases": [
                    {
                        "lease_id": lease_id,
                        "agent_id": agent_id,
                        "worker_id": agent_id,
                        "declared_true_name": agent_id,
                        "identity_binding_status": "BOUND_TRUE_NAME",
                        "worker_id_source": "declared_true_name",
                        "unbound_worker_id": False,
                        "mode": "write",
                        "lease_type": "write",
                        "lease_class": "write_intent_lease",
                        "write_intent_required": True,
                        "root_scope": "active_root",
                        "active_root": str(root),
                        "target_route_id": route_id,
                        "mutation_context": mutation_context,
                        "idempotency_key": idempotency_key,
                        "confirmation": "ION_WRITE_INTENT_CONFIRMED",
                        "operation_class": "active_write_mutation",
                        "paths": target_paths,
                        "raw_paths": target_paths,
                        "resolved_paths": [
                            (root / target_path).resolve(strict=False).as_posix()
                            for target_path in target_paths
                        ],
                        "claimed_at": timestamp,
                        "last_heartbeat_at": timestamp,
                        "updated_at": timestamp,
                        "status": "ACTIVE",
                    }
                ],
                "stale_workers": [],
                "recent_signoffs": [],
                "recent_receipts": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _seed_exclusive_active_context_refresh_lease(
    root: Path,
    *,
    agent_id: str,
    lease_id: str,
    target_paths: list[str],
) -> None:
    from datetime import datetime, timezone

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    board_path = root / "ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json"
    board_path.parent.mkdir(parents=True, exist_ok=True)
    board_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.worker_shift_board.v0_1",
                "updated_at": timestamp,
                "authority": {
                    "accepted_state_authority": False,
                    "production_authority": False,
                    "live_execution_authority": False,
                    "secrets_authority": False,
                },
                "active_shifts": [],
                "active_leases": [
                    {
                        "lease_id": lease_id,
                        "agent_id": agent_id,
                        "worker_id": agent_id,
                        "declared_true_name": agent_id,
                        "identity_binding_status": "BOUND_TRUE_NAME",
                        "worker_id_source": "declared_true_name",
                        "unbound_worker_id": False,
                        "mode": "exclusive_write",
                        "lease_type": "exclusive_write",
                        "lease_class": "active_context_refresh_lease",
                        "root_scope": "active_root",
                        "active_root": str(root),
                        "paths": target_paths,
                        "raw_paths": target_paths,
                        "resolved_paths": [
                            (root / target_path).resolve(strict=False).as_posix()
                            for target_path in target_paths
                        ],
                        "claimed_at": timestamp,
                        "last_heartbeat_at": timestamp,
                        "updated_at": timestamp,
                        "status": "ACTIVE",
                    }
                ],
                "stale_workers": [],
                "recent_signoffs": [],
                "recent_receipts": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def test_codex_queue_write_intent_gate_fails_closed_without_active_lease(monkeypatch):
    calls: list[tuple[object, str, dict]] = []

    def fake_connector(root, owner_tool, route_args):
        calls.append((root, owner_tool, dict(route_args)))
        return {"ok": True}

    monkeypatch.setattr(connector_contract, "call_chatgpt_connector_tool", fake_connector)

    result = action_branch_invoke(
        Path.cwd(),
        branch_id="codex_queue",
        route_id="request_work_packet",
        args={
            "objective": "bounded queue gate smoke",
            "agent_id": "agent-codex-queue",
            "write_intent_lease_id": "write-intent-codex-queue",
        },
        idempotency_key="codex-queue-write-intent-no-targets",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert result["ok"] is False
    assert result["refusal_class"] == "LEASE_REQUIRED"
    assert result["finding"] == "active_edit_lease_not_found"
    assert calls == []


def test_codex_queue_write_intent_gate_checks_route_context_before_delegation(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    agent_id = "codex_cli:branch-gateway:20260604:001"
    lease_id = "lease-codex-queue-wrong-context"
    idempotency_key = "codex-queue-write-intent-wrong-context"
    target_paths = [
        "ION/05_context/current/agent_comms",
        "ION/05_context/current/runtime_services/receipts",
    ]
    _seed_codex_queue_write_intent_lease(
        root,
        agent_id=agent_id,
        lease_id=lease_id,
        target_paths=target_paths,
        mutation_context="browser_queue",
        idempotency_key=idempotency_key,
    )
    calls: list[tuple[object, str, dict]] = []

    def fake_connector(root_arg, owner_tool, route_args):
        calls.append((root_arg, owner_tool, dict(route_args)))
        return {"ok": True}

    monkeypatch.setattr(connector_contract, "call_chatgpt_connector_tool", fake_connector)

    result = action_branch_invoke(
        root,
        branch_id="codex_queue",
        route_id="request_work_packet",
        args={
            "objective": "bounded queue gate smoke",
            "agent_id": agent_id,
            "write_intent_lease_id": lease_id,
            "target_paths": target_paths,
        },
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert result["ok"] is False
    assert result["refusal_class"] == "LEASE_REQUIRED"
    assert result["finding"] == "active_write_intent_lease_invalid"
    assert "lease_mutating_context_mismatch" in result["blockers"]
    assert calls == []


def test_domain_weaver_comms_write_intent_gate_requires_declared_target_roots(tmp_path: Path) -> None:
    root = _branch_gateway_root(tmp_path)
    agent_id = "codex_cli:domain-weaver-comms-target-root"
    lease_id = "lease-domain-weaver-comms-missing-receipts"
    idempotency_key = "domain-weaver-comms-missing-required-target-root"
    target_paths = ["ION/05_context/current/agent_comms"]
    _seed_codex_queue_write_intent_lease(
        root,
        agent_id=agent_id,
        lease_id=lease_id,
        target_paths=target_paths,
        route_id="comms_send",
        mutation_context="domain_weaver_agents",
        idempotency_key=idempotency_key,
    )

    result = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_send",
        args={
            "body": "This must not delegate because the receipt target root is absent from the lease.",
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": idempotency_key,
            "agent_id": agent_id,
            "write_intent_lease_id": lease_id,
            "write_intent": {"target_paths": target_paths},
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key=idempotency_key,
        expected_route_schema_version="v0",
    )

    assert result["ok"] is False
    assert result["refusal_class"] == "LEASE_REQUIRED"
    assert result["finding"] == "active_edit_lease_invalid"
    assert "lease_missing_target_coverage" in result["blockers"]
    missing = result["edit_lease_gate"]["missing_targets"]
    assert any(
        "ION/05_context/current/runtime_services/receipts" in candidates
        for row in missing
        for candidates in row["lease_path_candidates"]
    )
    assert not (root / "ION/05_context/current/runtime_services/receipts").exists()


def test_codex_queue_write_intent_gate_accepts_worker_shift_lease_before_delegation(
    tmp_path: Path,
    monkeypatch,
):
    root = _branch_gateway_root(tmp_path)
    agent_id = "codex_cli:branch-gateway:20260604:002"
    lease_id = "lease-codex-queue-valid-write-intent"
    idempotency_key = "codex-queue-write-intent-valid"
    target_paths = [
        "ION/05_context/current/agent_comms",
        "ION/05_context/current/runtime_services/receipts",
    ]
    _seed_codex_queue_write_intent_lease(
        root,
        agent_id=agent_id,
        lease_id=lease_id,
        target_paths=target_paths,
        idempotency_key=idempotency_key,
    )
    calls: list[tuple[object, str, dict]] = []

    def fake_connector(root_arg, owner_tool, route_args):
        calls.append((root_arg, owner_tool, dict(route_args)))
        return {"ok": True, "mutates_active_state": False, "fake_delegation": True}

    monkeypatch.setattr(connector_contract, "call_chatgpt_connector_tool", fake_connector)

    result = action_branch_invoke(
        root,
        branch_id="codex_queue",
        route_id="request_work_packet",
        args={
            "objective": "bounded queue gate smoke",
            "agent_id": agent_id,
            "write_intent": {
                "lease_id": lease_id,
                "target_paths": target_paths,
            },
        },
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["owner_tool"] == "ion_request_codex_work_packet"
    assert result["delegated_result"]["fake_delegation"] is True
    assert calls == [
        (
            root,
            "ion_request_codex_work_packet",
            {
                "objective": "bounded queue gate smoke",
                "agent_id": agent_id,
                "write_intent": {
                    "lease_id": lease_id,
                    "target_paths": target_paths,
                },
                "idempotency_key": idempotency_key,
                "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            },
        )
    ]


def test_gemini_branch_is_legacy_non_invocable_for_codex_only_domain_weaver():
    described = action_branch_describe(Path.cwd(), branch_id="gemini_cli_carrier_context", depth="full")
    invoked = action_branch_invoke(
        Path.cwd(),
        branch_id="gemini_cli_carrier_context",
        route_id="capsule",
        expected_route_schema_version="v0",
    )

    assert described["ok"] is True
    assert described["branch"]["invocable"] is False
    assert all(route["invocable"] is False for route in described["branch"]["routes"])
    assert invoked["ok"] is False
    assert invoked["refusal_class"] == "BRANCH_NOT_INVOCABLE"


def test_latest_context_branch_describe_exposes_mount_routes():
    described = action_branch_describe(Path.cwd(), branch_id="latest_context", depth="full")

    assert described["ok"] is True
    assert described["branch"]["branch_id"] == "latest_context"
    assert described["branch"]["family"] == "context_handoff_mount"
    assert described["branch"]["action_mount_equivalent"] is False
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert {
        "mount_status",
        "latest_handoff",
        "current_context_pack",
        "recent_receipts",
        "next_allowed_routes",
        "package_freshness",
    } <= set(routes)
    assert all(routes[route_id]["owner_tool"] == "ion_branch_leader_gateway" for route_id in routes)
    assert all(routes[route_id]["mutates_state"] is False for route_id in routes)
    assert all(routes[route_id]["confirmation_required"] is False for route_id in routes)


def test_latest_context_branch_read_routes_include_mount_proof_and_non_claims():
    for route_id in [
        "mount_status",
        "latest_handoff",
        "current_context_pack",
        "recent_receipts",
        "next_allowed_routes",
        "package_freshness",
    ]:
        args = {"limit": 3} if route_id == "recent_receipts" else {}
        result = action_branch_invoke(
            Path.cwd(),
            branch_id="latest_context",
            route_id=route_id,
            args=args,
            expected_route_schema_version="v0",
        )

        assert result["ok"] is True
        assert result["owner_tool"] == "ion_branch_leader_gateway"
        assert result["mutates_active_state"] is False
        delegated = result["delegated_result"]
        assert delegated["ok"] is True
        assert delegated["schema_id"] == "ion.latest_context_branch.v0_1"
        assert delegated["mount_truth_state"] in {
            "FULL_LOCAL_SANDBOX_MOUNT",
            "FULL_LOCAL_SANDBOX_MOUNT_CANDIDATE_PACKAGE_VALIDATED",
            "LOCAL_SANDBOX_PARTIAL_MOUNT",
            "UNMOUNTED_ROLEPLAY_BLOCKED",
        }
        assert delegated["source_posture"] == "repo_observed_candidate_context_handoff"
        assert delegated["action_mount_equivalent"] is False
        assert delegated["non_claims"]["accepted_state_claim"] is False
        assert delegated["non_claims"]["production_authority"] is False
        assert delegated["mutates_active_state"] is False


def test_latest_context_current_context_pack_includes_required_reads_and_route_templates():
    result = action_branch_invoke(
        Path.cwd(),
        branch_id="latest_context",
        route_id="current_context_pack",
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    delegated = result["delegated_result"]
    required_read_paths = {item["path"] for item in delegated["required_reads"]}
    assert "ION_Developement/ION/REPO_AUTHORITY.md" in required_read_paths or "ION/REPO_AUTHORITY.md" in required_read_paths
    assert any(path.endswith("00_ROOT_MANIFEST.json") for path in required_read_paths)
    assert any(path.endswith("09_OPERATOR_APPROVALS_AND_RED_ALERT.md") for path in required_read_paths)
    assert not any(path.endswith("10_RED_ALERT_FALLBACK_AND_FAILURE_MODES.md") for path in required_read_paths)
    assert {template["route_id"] for template in delegated["route_templates"]} == {
        "mount_status",
        "latest_handoff",
        "current_context_pack",
        "recent_receipts",
        "next_allowed_routes",
        "package_freshness",
    }
    assert delegated["action_mount_equivalent"] is False


def test_latest_context_prefers_collapsed_final_operator_kit():
    result = action_branch_invoke(
        Path.cwd(),
        branch_id="latest_context",
        route_id="mount_status",
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    local_package = result["delegated_result"]["local_package"]
    assert local_package["package_kind"] == "final_operator_upload_kit"
    assert "ION_GPT_FINAL_OPERATOR_UPLOAD_KIT_" in local_package["package_folder"]
    assert local_package["manifest"]["path"].endswith(
        "02_UPLOAD_EVERY_FILE_IN_THIS_FOLDER_TO_GPT_KNOWLEDGE/00_ROOT_MANIFEST.json"
    )
    assert local_package["knowledge_file_count"] == 20
    assert local_package["markdown_knowledge_file_count"] == 9
    assert local_package["zip_context_package_count"] == 10


def test_worker_shift_branch_describe_and_routes_are_read_only():
    described = action_branch_describe(Path.cwd(), branch_id="worker_shift", depth="full")

    assert described["ok"] is True
    assert described["branch"]["branch_id"] == "worker_shift"
    assert (
        "ION/05_context/current/context_settlement/accepted/SETTLEMENT_RECEIPT_CODEX_RUN_FAMILY_ACCEPTED_REPLAY_20260515T194247Z.json"
        in described["branch"]["context_refs"]
    )
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert {"status_summary", "active_workers", "stale_workers", "active_leases", "coordination_state"} <= set(routes)
    read_only_route_ids = {"status_summary", "active_workers", "stale_workers", "active_leases", "coordination_state"}
    assert all(routes[route_id]["mutates_state"] is False for route_id in read_only_route_ids)
    assert all(routes[route_id]["idempotency_required"] is False for route_id in read_only_route_ids)
    assert all(routes[route_id]["confirmation_required"] is False for route_id in read_only_route_ids)
    assert routes["request_edit_lease"]["mutates_state"] is True
    assert routes["request_edit_lease"]["idempotency_required"] is True
    assert routes["request_edit_lease"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"


def test_chatgpt_browser_operating_card_route_is_read_only_and_conservative(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    domain_projection = root / "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    domain_projection.parent.mkdir(parents=True, exist_ok=True)
    domain_projection.write_text(
        json.dumps(
            {
                "weave_status": "candidate_coverage_ready",
                "domain_count": 20,
                "agent_count": 20,
                "edge_count": 227,
                "queue_request_count": 569,
                "gap_count": 0,
                "live_return_complete": True,
                "full_domain_weaver_ready": False,
                "self_evolution_ready": False,
                "ui_development_ready": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    claim_work_lease(
        root=root,
        worker_id="codex_cli:unbound-card-worker",
        lease_id="lease-operating-card-orphan",
        paths=["ION/04_packages/kernel/ion_action_mcp_branch_leaders.py"],
        mode="exclusive_write",
        objective="operating card blocker fixture",
        allow_worker_id_mismatch=True,
    )

    described = action_branch_describe(root, branch_id="chatgpt_browser_carrier_context", depth="full")
    result = action_branch_invoke(
        root,
        branch_id="chatgpt_browser_carrier_context",
        route_id="operating_card",
        expected_route_schema_version="v0",
    )

    assert described["ok"] is True
    assert "operating_card" in {route["route_id"] for route in described["branch"]["routes"]}
    assert result["ok"] is True
    assert result["mutates_active_state"] is False
    delegated = result["delegated_result"]
    assert delegated["ok"] is True
    assert delegated["mutates_active_state"] is False
    assert delegated["authority"]["accepted_state_claim"] is False
    assert delegated["authority"]["production_authority"] is False
    assert delegated["authority"]["live_execution_authority"] is False
    assert delegated["authority"]["secrets_authority"] is False
    assert delegated["worker_shift"]["active_lease_count"] == 1
    assert delegated["worker_shift"]["readiness_blocked_by_unbound_leases"] is True
    assert delegated["domain_weaver"]["weave_status"] == "candidate_coverage_ready"
    assert delegated["domain_weaver"]["full_domain_weaver_ready"] is False
    assert delegated["domain_weaver"]["self_evolution_ready"] is False
    assert delegated["domain_weaver"]["ui_development_ready"] is False
    assert delegated["contact_modes"]["direct_resume_send"].startswith("workspace_write_preview")


def test_runtime_services_branch_describe_exposes_gated_routes():
    described = action_branch_describe(Path.cwd(), branch_id="runtime_services", depth="full")

    assert described["ok"] is True
    assert described["branch"]["branch_id"] == "runtime_services"
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert {"service_status", "service_reload_plan", "restart_service", "retest_service", "reload_and_retest"} <= set(routes)
    assert routes["service_status"]["mutates_state"] is False
    assert routes["service_reload_plan"]["mutates_state"] is False
    assert routes["retest_service"]["mutates_state"] is False
    assert routes["restart_service"]["mutates_state"] is True
    assert routes["restart_service"]["idempotency_required"] is True
    assert routes["restart_service"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert routes["reload_and_retest"]["mutates_state"] is True
    assert routes["reload_and_retest"]["idempotency_required"] is True


def test_runtime_services_status_and_reload_plan_are_read_only(monkeypatch):
    monkeypatch.setattr(runtime_services.subprocess, "run", _fake_runtime_services_run)
    result = action_branch_invoke(
        Path.cwd(),
        branch_id="runtime_services",
        route_id="service_status",
        args={"service_id": "mcp_preview"},
        expected_route_schema_version="v0",
    )
    plan = action_branch_invoke(
        Path.cwd(),
        branch_id="runtime_services",
        route_id="service_reload_plan",
        args={"service_id": "mcp_preview"},
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["owner_tool"] == "ion_branch_leader_gateway"
    assert result["mutates_active_state"] is False
    assert result["delegated_result"]["services"][0]["unit"]["unit_identity_proof"]["unit_matches_allowlist"] is True
    assert plan["ok"] is True
    assert plan["mutates_active_state"] is False
    assert plan["delegated_result"]["would_restart"] is True
    assert plan["delegated_result"]["restart_command_shape"] == ["systemctl", "--user", "restart", "ion-mcp-preview.service"]


def test_runtime_services_rejects_arbitrary_service_id():
    result = action_branch_invoke(
        Path.cwd(),
        branch_id="runtime_services",
        route_id="service_reload_plan",
        args={"service_id": "ssh.service"},
        expected_route_schema_version="v0",
    )

    assert result["ok"] is False
    assert result["refusal_class"] == "SERVICE_ID_NOT_ALLOWED"
    assert "ssh.service" not in result["allowed_service_ids"]


def test_runtime_services_mutation_requires_idempotency_and_confirmation():
    no_idempotency = action_branch_invoke(
        Path.cwd(),
        branch_id="runtime_services",
        route_id="restart_service",
        args={"service_id": "mcp_preview"},
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        Path.cwd(),
        branch_id="runtime_services",
        route_id="restart_service",
        args={"service_id": "mcp_preview"},
        idempotency_key="runtime-test",
        expected_route_schema_version="v0",
    )

    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"


def test_runtime_services_reload_and_retest_records_receipts(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    monkeypatch.setattr(runtime_services.subprocess, "run", _fake_runtime_services_run)
    monkeypatch.setattr(runtime_services.urllib.request, "urlopen", _fake_runtime_services_urlopen)

    result = action_branch_invoke(
        root,
        branch_id="runtime_services",
        route_id="reload_and_retest",
        args={"service_id": "mcp_preview"},
        idempotency_key="runtime-services-test",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["mutates_active_state"] is True
    delegated = result["delegated_result"]
    assert delegated["restart_result"]["post_receipt_path"].startswith("ION/05_context/current/runtime_services/receipts/")
    assert delegated["retest_result"]["status"]["health"]["status"] == "ready"
    assert (root / delegated["restart_result"]["pre_receipt_path"]).is_file()
    assert (root / delegated["restart_result"]["post_receipt_path"]).is_file()
    assert (root / delegated["combined_receipt_path"]).is_file()


def test_runtime_services_action_gateway_self_restart_is_deferred(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    monkeypatch.setattr(runtime_services.subprocess, "run", _fake_runtime_services_run)

    result = action_branch_invoke(
        root,
        branch_id="runtime_services",
        route_id="restart_service",
        args={"service_id": "action_gateway"},
        idempotency_key="action-gateway-self-restart-test",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert result["ok"] is False
    assert result["refusal_class"] == "SELF_RESTART_DEFERRED"
    assert "MCP 8765" in result["recovery_route"]
    assert (root / result["pre_receipt_path"]).is_file()
    assert (root / result["post_receipt_path"]).is_file()


def test_runtime_services_focused_test_plan_is_allowlisted_and_read_only():
    result = action_branch_invoke(
        Path.cwd(),
        branch_id="runtime_services",
        route_id="focused_test_plan",
        args={"suite_id": "native_ide_v4_alias_regression"},
        expected_route_schema_version="v0",
    )
    blocked = action_branch_invoke(
        Path.cwd(),
        branch_id="runtime_services",
        route_id="focused_test_plan",
        args={"suite_id": "native_ide_v4_alias_regression", "test_ids": ["ION/tests/unbounded.py::test_nope"]},
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["mutates_active_state"] is False
    delegated = result["delegated_result"]
    assert delegated["ok"] is True
    assert delegated["mutates_active_state"] is False
    assert delegated["arbitrary_shell_authority"] is False
    assert delegated["arbitrary_test_authority"] is False
    assert delegated["command_shape"][:3] == ["python3", "-m", "pytest"]
    assert "test_native_ide_overlay_routes_target_v4_dist_commands" in " ".join(delegated["test_ids"])
    assert blocked["ok"] is False
    assert blocked["delegated_result"]["refusal_class"] == "TEST_ID_NOT_ALLOWED"


def test_runtime_services_focused_test_run_requires_confirmation_and_writes_receipt(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    monkeypatch.setattr(runtime_services.subprocess, "run", _fake_runtime_services_run)

    no_confirmation = action_branch_invoke(
        root,
        branch_id="runtime_services",
        route_id="focused_test_run",
        args={"suite_id": "native_ide_v4_alias_regression"},
        idempotency_key="focused-test-run-test",
        expected_route_schema_version="v0",
    )
    result = action_branch_invoke(
        root,
        branch_id="runtime_services",
        route_id="focused_test_run",
        args={"suite_id": "native_ide_v4_alias_regression"},
        idempotency_key="focused-test-run-test",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"
    assert result["ok"] is True
    assert result["mutates_active_state"] is True
    delegated = result["delegated_result"]
    assert delegated["ok"] is True
    assert delegated["finding"] == "tests_passed"
    assert delegated["returncode"] == 0
    assert delegated["arbitrary_shell_authority"] is False
    assert (root / delegated["receipt_path"]).is_file()


def test_chatgpt_native_validation_manifest_and_receipts_are_read_only(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    monkeypatch.setattr(runtime_services.subprocess, "run", _fake_runtime_services_run)

    run = action_branch_invoke(
        root,
        branch_id="chatgpt_native_validation",
        route_id="focused_test_run",
        args={"suite_id": "native_ide_v4_alias_regression"},
        idempotency_key="chatgpt-native-validation-receipt-test",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert run["ok"] is True
    receipt_path = run["delegated_result"]["receipt_path"]
    assert (root / receipt_path).is_file()

    older_failure = root / "ION/05_context/current/runtime_services/test_run_receipts/20200101T000000Z_focused_test_run_native_ide_v4_alias_regression_old-failure.json"
    older_failure.parent.mkdir(parents=True, exist_ok=True)
    older_failure.write_text(
        json.dumps(
            {
                "schema_id": "ion.runtime_focused_test_run_receipt.v0_1",
                "created_at": "2020-01-01T00:00:00+00:00",
                "suite_id": "native_ide_v4_alias_regression",
                "idempotency_key": "old-failure",
                "payload": {
                    "ok": False,
                    "finding": "tests_failed",
                    "returncode": 1,
                    "test_ids": ["ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_native_ide_status_defaults_to_dist_status"],
                },
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_claim": False,
                "secrets_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    os.utime(older_failure, (1, 1))

    manifest = action_branch_invoke(
        root,
        branch_id="chatgpt_native_validation",
        route_id="suite_manifest",
        args={"include_receipts": True, "receipt_limit": 2, "status_history_limit": 5, "stale_after_seconds": 2592000},
        expected_route_schema_version="v0",
    )
    receipts = action_branch_invoke(
        root,
        branch_id="chatgpt_native_validation",
        route_id="receipts",
        args={"suite_id": "native_ide_v4_alias_regression", "limit": 2},
        expected_route_schema_version="v0",
    )

    assert manifest["ok"] is True
    assert manifest["mutates_active_state"] is False
    manifest_result = manifest["delegated_result"]
    assert manifest_result["ok"] is True
    assert manifest_result["mutates_active_state"] is False
    assert manifest_result["arbitrary_shell_authority"] is False
    assert manifest_result["arbitrary_test_authority"] is False
    assert manifest_result["stale_after_seconds"] == 2592000
    native_suite = next(item for item in manifest_result["suites"] if item["suite_id"] == "native_ide_v4_alias_regression")
    assert native_suite["recent_receipts"][0]["path"] == receipt_path
    assert native_suite["recent_receipts"][0]["ok"] is True
    latest_status = native_suite["latest_status"]
    assert manifest_result["latest_status_by_suite"]["native_ide_v4_alias_regression"] == latest_status
    assert latest_status["latest"]["path"] == receipt_path
    assert latest_status["latest_ok"] is True
    assert latest_status["latest_finding"] == "tests_passed"
    assert latest_status["last_passed_at"] is not None
    assert latest_status["last_failed_at"] == "2020-01-01T00:00:00+00:00"
    assert latest_status["has_superseded_failures"] is True
    assert latest_status["superseded_failure_count"] >= 1
    assert latest_status["is_stale"] is False
    assert receipts["ok"] is True
    assert receipts["mutates_active_state"] is False
    receipt_result = receipts["delegated_result"]
    assert receipt_result["match_count"] >= 1
    assert receipt_result["matches"][0]["path"] == receipt_path
    assert receipt_result["matches"][0]["production_authority"] is False
    assert receipt_result["matches"][0]["live_execution_authority"] is False
    assert receipt_result["matches"][0]["accepted_state_claim"] is False
    assert receipt_result["matches"][0]["secrets_authority"] is False


def test_runtime_services_freshness_probe_reports_registry_handler_parity(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    monkeypatch.setattr(runtime_services.subprocess, "run", _fake_runtime_services_run)
    monkeypatch.setattr(runtime_services.urllib.request, "urlopen", _fake_runtime_services_urlopen)

    result = action_branch_invoke(
        root,
        branch_id="runtime_services",
        route_id="runtime_freshness_probe",
        args={"service_id": "mcp_preview", "branch_ids": ["runtime_services", "chatgpt_native_validation"]},
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["mutates_active_state"] is False
    delegated = result["delegated_result"]
    assert delegated["ok"] is True
    assert delegated["mutates_active_state"] is False
    assert delegated["verdict"] == "fresh_enough"
    assert delegated["stale_mismatch_detected"] is False
    assert delegated["missing_from_handler"] == {}
    assert len(delegated["source_sha256"]) == 64
    assert "runtime_freshness_probe" in delegated["handler_supported_route_ids"]
    assert "runtime_freshness_probe" in delegated["registry_route_ids_by_branch"]["runtime_services"]
    assert "suite_manifest" in delegated["registry_route_ids_by_branch"]["chatgpt_native_validation"]
    assert delegated["service_status"]["service_id"] == "mcp_preview"
    assert delegated["service_status"]["unit"]["unit_identity_proof"]["unit_matches_allowlist"] is True
    assert delegated["production_authority"] is False
    assert delegated["live_execution_authority"] is False
    assert delegated["accepted_state_claim"] is False
    assert delegated["secrets_authority"] is False


def test_worker_shift_branch_invoke_status_summary_includes_overlap_and_queue_state(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    _seed_worker_shift_state(root)

    result = action_branch_invoke(
        root,
        branch_id="worker_shift",
        route_id="status_summary",
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["owner_tool"] == "ion_branch_leader_gateway"
    assert result["mutates_active_state"] is False
    delegated = result["delegated_result"]
    assert delegated["ok"] is True
    assert delegated["carrier_overlap_risk"]["risk_level"] in {"medium", "high"}
    assert delegated["queue_coordination_state"]["queue_observed"] is True
    assert delegated["queue_coordination_state"]["status_counts"]["QUEUED_FOR_CODEX_CARRIER"] == 2
    assert delegated["queue_coordination_state"]["status_counts"]["CLAIMED_BY_CODEX_QUEUE_RUNNER"] == 1


def test_worker_shift_status_summary_reconciles_active_codex_queue_workers(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    state_path = root / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    run_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/active_codex/run.json"
    request_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/active_codex.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    (root / run_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / request_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / run_rel).write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "run_id": "active_codex",
                "request_id": "codex_req_active",
                "status": "CODEX_CLI_RUNNING",
                "pid": os.getpid(),
                "run_packet_path": run_rel,
                "request_path": request_rel,
                "lane_id": "audit_lane",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / request_rel).write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_active",
                "status": "CLAIMED_BY_CODEX_QUEUE_RUNNER",
                "objective": "Active Codex queue worker",
                "lane_id": "audit_lane",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": "active_codex",
                    "pid": os.getpid(),
                    "run_packet_path": run_rel,
                    "request_path": request_rel,
                    "lane_id": "audit_lane",
                    "started_at": "2026-06-02T12:00:00+00:00",
                },
                "active_runs": {
                    "active_codex": {
                        "run_id": "active_codex",
                        "pid": os.getpid(),
                        "run_packet_path": run_rel,
                        "request_path": request_rel,
                        "lane_id": "audit_lane",
                        "started_at": "2026-06-02T12:00:00+00:00",
                    }
                },
                "latest_run": run_rel,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = action_branch_invoke(
        root,
        branch_id="worker_shift",
        route_id="status_summary",
        expected_route_schema_version="v0",
    )

    delegated = result["delegated_result"]
    summary = delegated["worker_shift_summary"]
    assert result["ok"] is True
    assert result["mutates_active_state"] is False
    assert summary["board_active_worker_count"] == 0
    assert summary["codex_queue_active_worker_count"] == 1
    assert summary["active_worker_count"] == 1
    assert delegated["codex_queue_reconciliation"]["workers"][0]["run_packet_path"] == run_rel
    assert delegated["queue_coordination_state"]["active_worker_count"] == 1


def test_worker_shift_branch_invoke_active_workers_route_returns_read_view(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    _seed_worker_shift_state(root)

    result = action_branch_invoke(
        root,
        branch_id="worker_shift",
        route_id="active_workers",
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["owner_tool"] == "ion_branch_leader_gateway"
    assert result["mutates_active_state"] is False
    delegated = result["delegated_result"]
    assert delegated["ok"] is True
    assert delegated["mutates_active_state"] is False
    assert delegated["active_worker_count"] >= 1
    assert isinstance(delegated["workers"], list)


def test_worker_shift_branch_invoke_coordination_state_route_returns_read_view(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    _seed_worker_shift_state(root)

    result = action_branch_invoke(
        root,
        branch_id="worker_shift",
        route_id="coordination_state",
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["owner_tool"] == "ion_branch_leader_gateway"
    assert result["mutates_active_state"] is False
    delegated = result["delegated_result"]
    assert delegated["ok"] is True
    assert delegated["mutates_active_state"] is False
    assert delegated["queue_coordination_state"]["queue_observed"] is True
    assert delegated["carrier_overlap_risk"]["risk_level"] in {"medium", "high"}


def test_worker_shift_route_ids_resolve_from_branch_context_invoke_lane(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    _seed_worker_shift_state(root)

    result = action_branch_invoke(
        root,
        branch_id="branch_context",
        route_id="status_summary",
        args={"path": "ION/04_packages/kernel"},
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["branch_id"] == "worker_shift"
    assert result["owner_tool"] == "ion_branch_leader_gateway"
    assert result["mutates_active_state"] is False
    assert result["resolver"]["resolver_fallback"] == "worker_shift_route_from_branch_context"
    assert result["resolver"]["requested_branch_id"] == "branch_context"
    assert result["resolver"]["resolved_branch_id"] == "worker_shift"


def test_worker_shift_operator_override_settlement_returns_through_branch_gateway(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    lease_claim = claim_work_lease(
        root=root,
        worker_id="codex_cli:unbound-orphan",
        lease_id="lease-branch-orphan",
        paths=["ION/04_packages/kernel/ion_action_mcp_branch_leaders.py"],
        mode="exclusive_write",
        objective="branch gateway orphan settlement regression",
        allow_worker_id_mismatch=True,
    )

    result = action_branch_invoke(
        root,
        branch_id="worker_shift",
        route_id="request_operator_override",
        args={
            "override_id": "override-branch-orphan",
            "actor_id": "operator:branch-test",
            "operator_id": "operator:branch-test",
            "lease_id": "lease-branch-orphan",
            "target_paths": ["ION/04_packages/kernel/ion_action_mcp_branch_leaders.py"],
            "root_scope": str(root),
            "reason": "operator-approved test orphan settlement",
            "blocked_finding": "ORPHAN_ACTIVE_EXCLUSIVE_WRITE_BLOCKED",
            "operator_proof_marker": "ION_OPERATOR_OVERRIDE_REQUESTED",
            "evidence": {"override_action": "release_orphan_unbound_lease"},
            "receipt_evidence": [lease_claim["receipt_path"]],
            "idempotency_key": "override-branch-orphan",
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
        },
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["mutates_active_state"] is True
    delegated = result["delegated_result"]
    assert delegated["override_granted"] is True
    assert delegated["settlement_result"] == "ORPHAN_ACTIVE_LEASE_RELEASED_BY_OPERATOR_OVERRIDE"
    assert load_shift_board(root)["active_leases"] == []


def test_branch_describe_path_uses_lazy_context_without_writing(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    branch = root / "ION/04_packages/kernel/demo_lazy_branch"
    branch.mkdir(parents=True)
    (branch / "worker.py").write_text("VALUE = 1\n", encoding="utf-8")

    described = action_branch_describe(root, path_or_branch_id="ION/04_packages/kernel/demo_lazy_branch", depth="candidate")

    assert described["ok"] is True
    assert described["branch"]["family"] == "branch_context_materialization"
    assert described["branch_context"]["classification"] == "materializable_branch"
    assert described["branch_context"]["maturity_level"] == "level_1_inherited"
    assert described["branch_context"]["candidate_available"] is True
    assert "candidate_capsule" in described["branch_context"]
    assert not (branch / "ION_CONTEXT_CAPSULE.candidate.yaml").exists()


def test_branch_describe_ignored_path_returns_not_branch_blocker(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    ignored = root / "node_modules/pkg"
    ignored.mkdir(parents=True)

    described = action_branch_describe(root, path_or_branch_id="node_modules/pkg")

    assert described["ok"] is True
    assert described["branch_context"]["classification"] == "ignored_path"
    assert described["branch_context"]["decision"] == "not_branch"
    assert described["branch_context"]["blocker"] == "do_not_materialize_this_path"
    assert described["branch_context"]["candidate_available"] is False


def test_branch_invoke_rejects_unknown_branch_and_route():
    missing_branch = action_branch_invoke(
        Path.cwd(),
        branch_id="missing",
        route_id="health",
        expected_route_schema_version="v0",
    )
    missing_route = action_branch_invoke(
        Path.cwd(),
        branch_id="gateway_core",
        route_id="missing",
        expected_route_schema_version="v0",
    )

    assert missing_branch["ok"] is False
    assert missing_branch["refusal_class"] == "BRANCH_ROUTE_NOT_FOUND"
    assert missing_route["ok"] is False
    assert missing_route["refusal_class"] == "BRANCH_ROUTE_NOT_FOUND"


def test_branch_invoke_read_only_route_delegates_to_owner_tool():
    result = action_branch_invoke(
        Path.cwd(),
        branch_id="gateway_core",
        route_id="health",
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["owner_tool"] == "ion_status"
    assert result["mutates_active_state"] is False
    assert result["delegated_result"]["ok"] is True
    assert result["delegated_result"]["data"]["schema_id"] == "ion.status.v1"


def test_branch_invoke_mutation_route_requires_idempotency_and_confirmation():
    no_idempotency = action_branch_invoke(
        Path.cwd(),
        branch_id="project_workbench",
        route_id="patch_apply",
        args={"project_id": "cosmos", "operations": [], "agent_id": "agent-test", "lease_id": "lease-test"},
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        Path.cwd(),
        branch_id="project_workbench",
        route_id="patch_apply",
        args={"project_id": "cosmos", "operations": [], "agent_id": "agent-test", "lease_id": "lease-test"},
        idempotency_key="test-key",
        expected_route_schema_version="v0",
    )

    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"


def test_branch_context_materialize_route_is_dry_run_then_confirmation_gated(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    branch = root / "ION/04_packages/kernel/demo_materialize"
    branch.mkdir(parents=True)
    (branch / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")

    dry_run = action_branch_invoke(
        root,
        branch_id="branch_context",
        route_id="materialize_candidate_context",
        args={"path": "ION/04_packages/kernel/demo_materialize"},
        expected_route_schema_version="v0",
    )
    no_idempotency = action_branch_invoke(
        root,
        branch_id="branch_context",
        route_id="materialize_candidate_context",
        args={"path": "ION/04_packages/kernel/demo_materialize", "write": True},
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        root,
        branch_id="branch_context",
        route_id="materialize_candidate_context",
        args={"path": "ION/04_packages/kernel/demo_materialize", "write": True},
        idempotency_key="lazy-test",
        expected_route_schema_version="v0",
    )

    assert dry_run["ok"] is True
    assert dry_run["mutates_active_state"] is False
    assert dry_run["delegated_result"]["wrote_candidate_capsule"] is False
    assert not (branch / "ION_CONTEXT_CAPSULE.candidate.yaml").exists()
    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"

    written = action_branch_invoke(
        root,
        branch_id="branch_context",
        route_id="materialize_candidate_context",
        args={"path": "ION/04_packages/kernel/demo_materialize", "write": True},
        idempotency_key="lazy-test-write",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert written["ok"] is True
    assert written["mutates_active_state"] is True
    assert (branch / "ION_CONTEXT_CAPSULE.candidate.yaml").is_file()
    receipt_path = root / written["delegated_result"]["materialization_receipt"]["receipt_path"]
    assert receipt_path.is_file()


def test_branch_context_inherit_parent_receipt_is_optional_write(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    branch = root / "ION/04_packages/kernel/demo_inherit"
    branch.mkdir(parents=True)

    dry_run = action_branch_invoke(
        root,
        branch_id="branch_context",
        route_id="inherit_parent_context",
        args={"path": "ION/04_packages/kernel/demo_inherit"},
        expected_route_schema_version="v0",
    )

    assert dry_run["ok"] is True
    assert dry_run["mutates_active_state"] is False
    assert dry_run["delegated_result"]["materialization_receipt"]["wrote"] is False


def test_browser_codex_agent_routes_archive_attach_and_previews(monkeypatch, tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    codex_home = tmp_path / "codex_home"
    sessions_dir = codex_home / "sessions/2026/06/02"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    session_id = "019e88c9-73f3-7a33-b2a1-84ea4bddb5f9"
    session_path = sessions_dir / f"session-{session_id}.jsonl"
    session_path.write_text(
        "\n".join(
            json.dumps(row)
            for row in [
                {"type": "session_meta", "timestamp": "2026-06-02T20:52:00Z", "payload": {"id": session_id, "cwd": str(root)}},
                {"type": "event_msg", "timestamp": "2026-06-02T20:52:10Z", "payload": {"type": "user_message", "message": "Build Browser GPT Codex chat attachment support"}},
                {"type": "response_item", "timestamp": "2026-06-02T20:52:20Z", "payload": {"role": "assistant", "content": [{"text": "Added Attach Codex chats and redacted archive packet support."}]}},
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (codex_home / "history.jsonl").write_text(
        json.dumps({"session_id": session_id, "ts": "2026-06-02T20:52:10Z", "text": "Build Browser GPT Codex chat attachment support"}) + "\n",
        encoding="utf-8",
    )
    (codex_home / "session_index.jsonl").write_text(
        json.dumps({"id": session_id, "thread_name": "Browser GPT Codex archive attach", "updated_at": "2026-06-02T20:52:30Z"}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    described = action_branch_describe(root, branch_id="browser_codex_agent", depth="full")
    status = action_branch_invoke(
        root,
        branch_id="browser_codex_agent",
        route_id="browser_codex_agent_status",
        args={"session_limit": 5},
        expected_route_schema_version="v0",
    )
    search = action_branch_invoke(
        root,
        branch_id="browser_codex_agent",
        route_id="codex_archive_search_preview",
        args={"query": "attachment", "session_limit": 5},
        expected_route_schema_version="v0",
    )
    preview = action_branch_invoke(
        root,
        branch_id="browser_codex_agent",
        route_id="codex_archive_attach_preview",
        args={"session_id": session_id},
        expected_route_schema_version="v0",
    )
    no_idempotency = action_branch_invoke(
        root,
        branch_id="browser_codex_agent",
        route_id="codex_archive_attach",
        args={"session_id": session_id, "confirmation": "ION_BOUNDED_WRITE_CONFIRMED"},
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    attached = action_branch_invoke(
        root,
        branch_id="browser_codex_agent",
        route_id="codex_archive_attach",
        args={"session_id": session_id, "confirmation": "ION_BOUNDED_WRITE_CONFIRMED", "idempotency_key": "browser-codex-archive-attach-smoke"},
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key="browser-codex-archive-attach-smoke",
        expected_route_schema_version="v0",
    )
    playwright = action_branch_invoke(
        root,
        branch_id="browser_codex_agent",
        route_id="playwright_work_preview",
        args={"objective": "Smoke Browser GPT Codex archive attach", "target_url": "http://127.0.0.1:8765"},
        expected_route_schema_version="v0",
    )
    contact = action_branch_invoke(
        root,
        branch_id="browser_codex_agent",
        route_id="browser_agent_contact",
        args={},
        expected_route_schema_version="v0",
    )
    invoke_preview = action_branch_invoke(
        root,
        branch_id="browser_codex_agent",
        route_id="browser_agent_invoke_preview",
        args={"objective": "Inspect archive attach smoke", "target_url": "http://127.0.0.1:8765", "queue": False},
        expected_route_schema_version="v0",
    )
    invoke_no_idempotency = action_branch_invoke(
        root,
        branch_id="browser_codex_agent",
        route_id="browser_agent_invoke",
        args={"objective": "Inspect archive attach smoke", "target_url": "http://127.0.0.1:8765", "queue": False, "confirmation": "ION_BOUNDED_WRITE_CONFIRMED"},
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    invoked = action_branch_invoke(
        root,
        branch_id="browser_codex_agent",
        route_id="browser_agent_invoke",
        args={"objective": "Inspect archive attach smoke", "target_url": "http://127.0.0.1:8765", "queue": False, "confirmation": "ION_BOUNDED_WRITE_CONFIRMED", "idempotency_key": "browser-agent-invoke-smoke"},
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key="browser-agent-invoke-smoke",
        expected_route_schema_version="v0",
    )

    assert described["ok"] is True
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert routes["browser_codex_agent_status"]["mutates_state"] is False
    assert routes["codex_archive_search_preview"]["mutates_state"] is False
    assert routes["codex_archive_attach_preview"]["mutates_state"] is False
    assert routes["codex_archive_attach"]["mutates_state"] is True
    assert routes["playwright_work_preview"]["mutates_state"] is False
    assert status["ok"] is True
    assert status["delegated_result"]["session_count_returned"] >= 1
    assert status["delegated_result"]["raw_transcript_exported"] is False
    assert search["ok"] is True
    assert search["delegated_result"]["sessions"][0]["session_id"] == session_id
    assert search["delegated_result"]["raw_transcript_exported"] is False
    assert preview["ok"] is True
    assert preview["delegated_result"]["found"] is True
    assert preview["delegated_result"]["would_write_attachment_packet"] is True
    assert preview["delegated_result"]["mutates_active_state"] is False
    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert attached["ok"] is True
    assert attached["mutates_active_state"] is True
    attach_result = attached["delegated_result"]["attach_result"]
    assert attach_result["ok"] is True
    packet_path = attach_result["attachment"]["packet_path"]
    packet = json.loads((root / packet_path).read_text(encoding="utf-8"))
    assert packet["session_id"] == session_id
    assert packet["raw_transcript_exported"] is False
    assert packet["hidden_reasoning_exposed"] is False
    assert (root / attached["delegated_result"]["receipt_path"]).is_file()
    assert playwright["ok"] is True
    playwright_result = playwright["delegated_result"]
    assert playwright_result["would_launch_browser"] is False
    assert playwright_result["would_call_playwright"] is False
    assert any(call["branch_id"] == "codex_queue" and call["route_id"] == "spark_scout_packet_preview" for call in playwright_result["recommended_branch_calls"])
    assert contact["ok"] is True
    contact_result = contact["delegated_result"]
    assert contact_result["mutates_active_state"] is False
    assert contact_result["silent_send"] is False
    assert "browser_gpt_pair" in json.dumps(contact_result["contact"])
    assert invoke_preview["ok"] is True
    invoke_preview_result = invoke_preview["delegated_result"]
    assert invoke_preview_result["would_invoke"] is False
    assert invoke_preview_result["would_queue"] is False
    assert invoke_preview_result["silent_send"] is False
    assert invoke_preview_result["packet_preview"]["agent_role"] == "role.browser_dom_cartographer"
    assert invoke_no_idempotency["ok"] is False
    assert invoke_no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert invoked["ok"] is True
    assert invoked["mutates_active_state"] is True
    invoked_result = invoked["delegated_result"]
    assert invoked_result["silent_send"] is False
    assert invoked_result["accepted_state_claim"] is False
    assert (root / invoked_result["receipt_path"]).is_file()
    invoke_receipt = json.loads((root / invoked_result["receipt_path"]).read_text(encoding="utf-8"))
    assert invoke_receipt["payload"]["status"] == "PREPARED_NOT_QUEUED"
    assert invoke_receipt["payload"]["agent_role"] == "role.browser_dom_cartographer"
    assert invoke_receipt["payload"]["agent_tag"] == "@codex_cli_carrier.browser_gpt_pair"
    assert invoke_receipt["payload"]["invocation_path"]
    assert invoke_receipt["payload"]["codex_work_request_path"]
    assert invoke_receipt["payload"]["silent_send"] is False
    invoke_result = invoked_result["invoke_result"]
    assert invoke_result["ok"] is True
    assert invoke_result.get("production_authority") is False
    assert invoke_result.get("live_execution_authority") is False


def _write_large_artifact_fixtures(root: Path) -> dict[str, str]:
    fixture_root = root / "ION/tests/fixtures/large_artifacts"
    fixture_root.mkdir(parents=True, exist_ok=True)
    md_path = fixture_root / "large_notes.md"
    md_lines = ["# Overview\n", "This section proves bounded section reads.\n", "## Deep Section\n"]
    md_lines.extend(
        f"line {index:05d} carries ANCHOR_NEEDLE and bounded stream payload for deterministic chunking.\n"
        for index in range(4200)
    )
    md_path.write_text("".join(md_lines), encoding="utf-8")

    py_path = fixture_root / "symbols.py"
    py_path.write_text(
        "import json\n\n"
        "TOP_LEVEL_CONSTANT = 'visible-name-only'\n\n"
        "class ArtifactWorker:\n"
        "    def run(self):\n"
        "        return json.dumps({'ok': True})\n\n"
        "def chunk_source(value):\n"
        "    return value\n",
        encoding="utf-8",
    )

    json_path = fixture_root / "large_data.json"
    json_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.large_artifact_fixture.v0",
                "summary": {"name": "large fixture", "anchor": "ANCHOR_NEEDLE"},
                "agents": [{"id": f"agent-{index}", "role": "fixture"} for index in range(8000)],
            }
        ),
        encoding="utf-8",
    )

    secret_path = fixture_root / ".env"
    secret_path.write_text("TOKEN=not-returned\n", encoding="utf-8")
    return {
        "md": md_path.relative_to(root).as_posix(),
        "py": py_path.relative_to(root).as_posix(),
        "json": json_path.relative_to(root).as_posix(),
        "secret": secret_path.relative_to(root).as_posix(),
        "fixture_root": fixture_root.relative_to(root).as_posix(),
    }


def test_large_artifact_intelligence_branch_streams_and_indexes_oversized_files(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    paths = _write_large_artifact_fixtures(root)

    described = action_branch_describe(root, branch_id="large_artifact_intelligence", depth="full")
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    profile = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_profile",
        args={"path": paths["md"]},
        expected_route_schema_version="v0",
    )
    manifest = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_chunk_manifest",
        args={"path": paths["md"], "chunk_size_bytes": 16384},
        expected_route_schema_version="v0",
    )
    stream_start = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_stream_start",
        args={"path": paths["md"], "chunk_size_bytes": 16384},
        expected_route_schema_version="v0",
    )
    first_chunk = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_stream_next",
        args={"cursor": stream_start["delegated_result"]["cursor"]},
        expected_route_schema_version="v0",
    )
    second_chunk = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_stream_next",
        args={"cursor": first_chunk["delegated_result"]["next_cursor"]},
        expected_route_schema_version="v0",
    )
    range_by_artifact = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_stream_range",
        args={"artifact_id": stream_start["delegated_result"]["artifact_id"], "chunk_start": 0, "chunk_count": 2, "chunk_size_bytes": 16384},
        expected_route_schema_version="v0",
    )
    slice_read = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_slice_read",
        args={"path": paths["md"], "start_line": 3, "line_count": 3},
        expected_route_schema_version="v0",
    )
    search = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_anchor_search",
        args={"path": paths["md"], "query": "ANCHOR_NEEDLE", "max_hits": 3},
        expected_route_schema_version="v0",
    )
    symbols = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_symbol_index",
        args={"path": paths["py"]},
        expected_route_schema_version="v0",
    )
    json_subtree = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_json_path_read",
        args={"path": paths["json"], "json_path": "agents[0:3]"},
        expected_route_schema_version="v0",
    )
    section = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_section_read",
        args={"path": paths["md"], "heading": "Deep Section", "include_children": True, "max_bytes": 4000},
        expected_route_schema_version="v0",
    )
    claim = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_artifact_claim_check",
        args={"claim": "ANCHOR_NEEDLE appears in the large notes", "evidence_refs": [{"path": paths["md"], "start_line": 3, "line_count": 5}]},
        expected_route_schema_version="v0",
    )
    blocked = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_profile",
        args={"path": paths["secret"]},
        expected_route_schema_version="v0",
    )

    assert described["ok"] is True
    assert all(route["mutates_state"] is False for route in routes.values())
    assert profile["delegated_result"]["oversize"] is True
    assert profile["delegated_result"]["size_bytes"] > 262_144
    assert profile["delegated_result"]["line_count"] > 4000
    assert profile["delegated_result"]["content_returned"] == "metadata_only"
    assert manifest["delegated_result"]["chunk_count"] > 1
    assert len(manifest["delegated_result"]["chunks"]) > 1
    assert stream_start["delegated_result"]["chunk_count"] > 1
    assert first_chunk["delegated_result"]["chunk_index"] == 0
    assert first_chunk["delegated_result"]["next_cursor"]
    assert second_chunk["delegated_result"]["chunk_index"] == 1
    assert len(range_by_artifact["delegated_result"]["chunks"]) == 2
    assert range_by_artifact["delegated_result"]["chunks"][0]["chunk_index"] == 0
    assert slice_read["delegated_result"]["source_range"]["start_line"] == 3
    assert "ANCHOR_NEEDLE" in slice_read["delegated_result"]["content"]
    assert search["delegated_result"]["hit_count"] >= 1
    assert search["delegated_result"]["hits"][0]["recommended_slice_args"]["path"] == paths["md"]
    assert symbols["delegated_result"]["exec_indexed_code"] is False
    assert any(item["name"] == "ArtifactWorker" for item in symbols["delegated_result"]["classes"])
    assert any(item["name"] == "chunk_source" for item in symbols["delegated_result"]["functions"])
    assert len(json_subtree["delegated_result"]["subtree"]) == 3
    assert section["delegated_result"]["line_range"]["start_line"] == 3
    assert claim["delegated_result"]["candidate_support_status"] == "supported"
    assert blocked["ok"] is False
    assert blocked["refusal_class"] == "PATH_NOT_ALLOWED"


def test_branch_gateway_exposes_oversize_recovery_metadata(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)

    branches = action_branch_list(root, limit=100)
    large = action_branch_describe(root, branch_id="large_artifact_intelligence", depth="full")
    codex = action_branch_describe(root, branch_id="codex_queue", depth="full")
    domain = action_branch_describe(root, branch_id="domain_weaver_agents", depth="full")

    branch_rows = {row["branch_id"]: row for row in branches["branches"]}
    assert branch_rows["large_artifact_intelligence"]["oversize_recovery"]["role"] == (
        "primary_action_gateway_oversize_recovery_branch"
    )
    assert branch_rows["codex_queue"]["compact_response_guidance"]["preferred_load_pattern"] == (
        "queue_summary_then_artifact_slice"
    )
    assert large["branch"]["oversize_recovery"]["sequential_load_handoff"] == [
        "large_file_profile",
        "large_file_chunk_manifest",
        "large_file_anchor_search",
        "large_file_slice_read",
    ]
    codex_routes = {route["route_id"]: route for route in codex["branch"]["routes"]}
    assert codex_routes["process_once"]["compact_response_guidance"]["content_returned"] == "compact_run_envelope"
    assert codex_routes["worker_trace"]["compact_response_guidance"]["content_returned"] == (
        "artifact_index_and_bounded_previews"
    )
    domain_routes = {route["route_id"]: route for route in domain["branch"]["routes"]}
    assert domain["branch"]["oversize_recovery"]["fallback_metadata"]["large_projection_path"] == (
        "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    )
    assert domain_routes["comms_overview"]["compact_response_guidance"]["content_returned"] == (
        "comms_summary_threads_and_path_refs"
    )


def test_artifact_transfer_branch_previews_and_materializes_safe_zip(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    paths = _write_large_artifact_fixtures(root)

    described = action_branch_describe(root, branch_id="artifact_transfer", depth="full")
    preview = action_branch_invoke(
        root,
        branch_id="artifact_transfer",
        route_id="zip_request_preview",
        args={"paths": [paths["fixture_root"]], "package_label": "large-artifact-smoke", "max_bytes": 1000000},
        expected_route_schema_version="v0",
    )
    no_gate = action_branch_invoke(
        root,
        branch_id="artifact_transfer",
        route_id="zip_materialize_request",
        args={"paths": [paths["fixture_root"]], "package_label": "large-artifact-smoke", "confirmation": "ION_BOUNDED_WRITE_CONFIRMED", "max_bytes": 1000000},
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    materialized = action_branch_invoke(
        root,
        branch_id="artifact_transfer",
        route_id="zip_materialize_request",
        args={
            "paths": [paths["fixture_root"]],
            "package_label": "large-artifact-smoke",
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": "artifact-transfer-smoke",
            "max_bytes": 1000000,
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key="artifact-transfer-smoke",
        expected_route_schema_version="v0",
    )
    manifest = action_branch_invoke(
        root,
        branch_id="artifact_transfer",
        route_id="zip_manifest_read",
        args={"package_id": materialized["delegated_result"]["package_id"]},
        expected_route_schema_version="v0",
    )
    instruction = action_branch_invoke(
        root,
        branch_id="artifact_transfer",
        route_id="sandbox_upload_instruction",
        args={"package_id": materialized["delegated_result"]["package_id"]},
        expected_route_schema_version="v0",
    )

    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert described["ok"] is True
    assert routes["zip_request_preview"]["mutates_state"] is False
    assert routes["zip_materialize_request"]["mutates_state"] is True
    assert preview["delegated_result"]["would_create_zip"] is False
    assert preview["delegated_result"]["estimated_file_count"] >= 2
    assert any(item["path"].endswith(".env") for item in preview["delegated_result"]["excluded_paths"])
    assert no_gate["ok"] is False
    assert no_gate["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert materialized["ok"] is True
    assert materialized["mutates_active_state"] is True
    zip_path = root / materialized["delegated_result"]["zip_path"]
    manifest_path = root / materialized["delegated_result"]["manifest_path"]
    receipt_path = root / materialized["delegated_result"]["receipt_path"]
    assert zip_path.is_file()
    assert manifest_path.is_file()
    assert receipt_path.is_file()
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert paths["md"] in names
    assert paths["secret"] not in names
    manifest_data = manifest["delegated_result"]["manifest"]
    assert manifest_data["package_sha256"] == materialized["delegated_result"]["package_sha256"]
    assert all("sha256" in item for item in manifest_data["files"])
    assert instruction["delegated_result"]["upload_performed"] is False
    assert instruction["delegated_result"]["instruction"] == "Upload this zip to the current ChatGPT thread."


def test_large_artifact_inference_preview_routes_are_no_model_call(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    paths = _write_large_artifact_fixtures(root)

    described = action_branch_describe(root, branch_id="large_artifact_inference_preview", depth="full")
    status = action_branch_invoke(
        root,
        branch_id="large_artifact_inference_preview",
        route_id="inference_provider_status",
        args={},
        expected_route_schema_version="v0",
    )
    plan = action_branch_invoke(
        root,
        branch_id="large_artifact_inference_preview",
        route_id="inference_plan_preview",
        args={"path": paths["md"], "provider": "codex_spark_preview", "task": "summarize"},
        expected_route_schema_version="v0",
    )
    index_preview = action_branch_invoke(
        root,
        branch_id="large_artifact_inference_preview",
        route_id="large_artifact_inference_index_preview",
        args={"path": paths["md"], "provider": "codex_spark_preview"},
        expected_route_schema_version="v0",
    )
    question_preview = action_branch_invoke(
        root,
        branch_id="large_artifact_inference_preview",
        route_id="large_artifact_inference_question_preview",
        args={"path": paths["md"], "question": "Where is ANCHOR_NEEDLE?"},
        expected_route_schema_version="v0",
    )

    assert described["ok"] is True
    assert all(route["mutates_state"] is False for route in described["branch"]["routes"])
    assert status["delegated_result"]["secrets_exposed"] is False
    assert status["delegated_result"]["network_used"] is False
    assert all(provider["would_call_model"] is False for provider in status["delegated_result"]["providers"].values())
    assert plan["delegated_result"]["would_call_model"] is False
    assert plan["delegated_result"]["would_send_full_text"] is False
    assert plan["delegated_result"]["accepted_state_claim"] is False
    assert index_preview["delegated_result"]["would_call_model"] is False
    assert index_preview["delegated_result"]["would_write_index"] is False
    assert question_preview["delegated_result"]["would_call_model"] is False
    assert question_preview["delegated_result"]["would_send_full_text"] is False


def test_codex_queue_model_routing_surfaces_spark_preview_without_enqueue(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)

    described = action_branch_describe(root, branch_id="codex_queue", depth="full")
    status = action_branch_invoke(
        root,
        branch_id="codex_queue",
        route_id="codex_model_capability_status",
        args={},
        expected_route_schema_version="v0",
    )
    low_risk = action_branch_invoke(
        root,
        branch_id="codex_queue",
        route_id="codex_model_route_preview",
        args={"route_family": "scout", "requested_model": "codex-5.3-spark", "requested_reasoning_effort": "low"},
        expected_route_schema_version="v0",
    )
    high_stakes = action_branch_invoke(
        root,
        branch_id="codex_queue",
        route_id="codex_model_route_preview",
        args={"route_family": "settlement", "requested_model": "codex-5.3-spark", "requested_reasoning_effort": "low"},
        expected_route_schema_version="v0",
    )
    packet = action_branch_invoke(
        root,
        branch_id="codex_queue",
        route_id="spark_scout_packet_preview",
        args={"objective": "Scout a large file", "route_family": "large_artifact_index"},
        expected_route_schema_version="v0",
    )
    validated = action_branch_invoke(
        root,
        branch_id="codex_queue",
        route_id="spark_scout_args_validate",
        args={"objective": "Scout a large file", "route_family": "large_artifact_index"},
        expected_route_schema_version="v0",
    )

    assert described["ok"] is True
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert routes["codex_model_capability_status"]["mutates_state"] is False
    assert routes["codex_model_route_preview"]["mutates_state"] is False
    assert routes["spark_scout_packet_preview"]["mutates_state"] is False
    assert status["ok"] is True
    status_result = status["delegated_result"]
    assert status_result["spark_request_supported_by_packet_schema"] is True
    assert "codex-5.3-spark" in status_result["spark_aliases"]
    assert status_result["spark_actual_cli_call_verified"] is False
    assert status_result["secrets_exposed"] is False
    assert low_risk["ok"] is True
    low_result = low_risk["delegated_result"]
    assert low_result["selected_model"] == "codex-5.3-spark"
    assert low_result["selected_reasoning_effort"] == "low"
    assert low_result["spark_allowed"] is True
    assert low_result["frontier_required"] is False
    high_result = high_stakes["delegated_result"]
    assert high_result["selected_model"] == "gpt-5.5"
    assert high_result["selected_reasoning_effort"] == "xhigh"
    assert high_result["spark_allowed"] is False
    assert high_result["frontier_required"] is True
    assert packet["ok"] is True
    packet_result = packet["delegated_result"]
    assert packet_result["would_enqueue"] is False
    assert validated["ok"] is True
    validated_result = validated["delegated_result"]
    assert validated_result["valid"] is True
    assert validated_result["findings"] == []
    assert validated_result["generated_model_args"] == {"model": "codex-5.3-spark", "reasoning_effort": "low"}
    assert validated_result["forbidden_generated_keys_absent"]["service_tier"] is True
    assert validated_result["would_enqueue"] is False
    assert validated_result["would_call_codex"] is False
    preview = packet_result["packet_preview"]
    assert preview["requested_model"] == "codex-5.3-spark"
    assert preview["requires_confirmation_to_enqueue"] is True
    call = preview["suggested_branch_call"]
    assert call["branch_id"] == "codex_queue"
    assert call["route_id"] == "request_work_packet"
    assert call["args"]["confirmation"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert call["args"]["idempotency_key"] == "spark-scout-<stable-id>"


def test_domain_weaver_agents_branch_views_comms_and_spawn_preview(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    projection_path = root / "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    comms_dir = root / "ION/05_context/current/agent_comms"
    projection_path.parent.mkdir(parents=True, exist_ok=True)
    comms_dir.mkdir(parents=True, exist_ok=True)
    projection_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.projection.v1",
                "weave_status": "ready",
                "summary": {"usable_domain_count": 1, "gap_count": 0, "edge_count": 1},
                "domains": [
                    {"domain_id": "domain.test", "title": "Test Domain"},
                    {"domain_id": "ion_vnext_front_door", "title": "vNext Front Door Alias"},
                ],
                "agents": [{"role_id": "role.test_steward", "domain_id": "domain.test", "title": "Test Steward"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    manifest_path = (
        root
        / "ION/05_context/current/codex_agent_mounts/role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json"
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"schema_id": "ion.codex_agent_mount.v0_1", "domain_id": "ion_vnext_front_door"}, indent=2),
        encoding="utf-8",
    )
    (comms_dir / "COMMUNICATION_DIRECTORY.json").write_text(
        json.dumps({"schema_id": "ion.agent_comms.communication_directory.v1", "available_agent_count": 1}),
        encoding="utf-8",
    )

    described = action_branch_describe(root, branch_id="domain_weaver_agents", depth="full")
    status = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="domain_weaver_status",
        args={},
        expected_route_schema_version="v0",
    )
    projection = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="projection_summary",
        args={},
        expected_route_schema_version="v0",
    )
    projection_refresh_plan = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="projection_accepted_refresh_plan",
        args={},
        expected_route_schema_version="v0",
    )
    projection_replacement_body = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="projection_replacement_body_candidate",
        args={},
        expected_route_schema_version="v0",
    )
    semantic_alias_preflight = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="semantic_alias_supervised_apply_preflight",
        args={
            "agent_id": "codex_cli:test-semantic-alias",
            "lease_id": "lease-semantic-alias-both",
            "idempotency_prefix": "test-semantic-alias",
        },
        expected_route_schema_version="v0",
    )
    comms = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_overview",
        args={},
        expected_route_schema_version="v0",
    )
    spawn = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="spawn_plan_preview",
        args={"objective": "Spawn a test steward", "domain_id": "domain.test", "role_id": "role.test_steward"},
        expected_route_schema_version="v0",
    )
    start_plan = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="spawn_dispatch_start_plan",
        args={"max_lanes": 3},
        expected_route_schema_version="v0",
    )
    quarantine = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="spawn_dispatch_legacy_receipt_quarantine",
        args={},
        expected_route_schema_version="v0",
    )
    pressure_plan = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="pressure_wave_plan",
        args={"native_slot_cap": 6, "active_native_agent_count": 3, "exact_queue_start_cap": 2},
        expected_route_schema_version="v0",
    )
    backlog_hygiene = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="worker_start_backlog_hygiene",
        args={"example_limit": 2},
        expected_route_schema_version="v0",
    )
    active_context_preflight = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="active_context_reissue_preflight",
        args={"max_age_seconds": 60},
        expected_route_schema_version="v0",
    )
    active_context_refresh_plan = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="active_context_gated_refresh_plan",
        args={"max_age_seconds": 60},
        expected_route_schema_version="v0",
    )

    assert described["ok"] is True
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert routes["domain_weaver_status"]["mutates_state"] is False
    assert routes["worker_start_readiness_summary"]["mutates_state"] is False
    assert routes["worker_start_backlog_hygiene"]["mutates_state"] is False
    assert routes["active_context_reissue_preflight"]["mutates_state"] is False
    assert routes["active_context_gated_refresh_plan"]["mutates_state"] is False
    assert routes["active_context_gated_refresh_apply"]["mutates_state"] is True
    assert routes["active_context_gated_refresh_apply"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert routes["active_context_gated_refresh_apply"]["edit_lease_required"] is True
    assert routes["active_context_gated_refresh_apply"]["lease_gate_public"]["handler_dynamic_target_gate_deferred"] is True
    assert routes["active_context_gated_refresh_apply"]["required_mutation_fields"] == [
        "preflight_path",
        "execute_write",
        "idempotency_key",
        "confirmation",
        "agent_id",
        "lease_id",
    ]
    assert routes["spawn_dispatch_start_plan"]["mutates_state"] is False
    assert routes["spawn_dispatch_legacy_receipt_quarantine"]["mutates_state"] is False
    assert routes["pressure_wave_plan"]["mutates_state"] is False
    assert routes["pressure_wave_spawn_request_seed"]["mutates_state"] is True
    assert routes["pressure_wave_spawn_request_seed"]["idempotency_required"] is True
    assert routes["pressure_wave_spawn_request_seed"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert routes["pressure_wave_spawn_request_seed"]["write_intent_required_target_roots"] == [
        "ION/05_context/current/domain_weaver/workers",
    ]
    assert routes["pressure_wave_spawn_request_seed"]["required_mutation_fields"] == [
        "execute_write",
        "idempotency_key",
        "confirmation",
        "agent_id",
        "write_intent_lease_id",
    ]
    assert routes["projection_summary"]["mutates_state"] is False
    assert routes["projection_accepted_refresh_plan"]["mutates_state"] is False
    assert routes["projection_replacement_body_candidate"]["mutates_state"] is False
    assert routes["semantic_alias_supervised_apply_preflight"]["mutates_state"] is False
    assert routes["projection_accepted_refresh_apply"]["mutates_state"] is True
    assert routes["projection_accepted_refresh_apply"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert routes["projection_accepted_refresh_apply"]["edit_lease_required"] is True
    assert routes["projection_accepted_refresh_apply"]["lease_id_required"] is True
    assert routes["projection_accepted_refresh_apply"]["lease_gate_public"]["target_derivation"] == "static"
    assert routes["projection_accepted_refresh_apply"]["lease_gate"]["target_path"] == (
        "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    )
    assert routes["projection_accepted_refresh_apply"]["required_mutation_fields"] == [
        "execute_write",
        "before_sha256",
        "replacement_body_sha256",
        "accepted_state_write_confirmation",
        "idempotency_key",
        "confirmation",
        "agent_id",
        "lease_id",
    ]
    assert routes["semantic_alias_projection_apply"]["mutates_state"] is True
    assert routes["semantic_alias_projection_apply"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert routes["semantic_alias_projection_apply"]["edit_lease_required"] is True
    assert routes["semantic_alias_projection_apply"]["lease_id_required"] is True
    assert routes["semantic_alias_projection_apply"]["lease_gate_public"]["target_derivation"] == "static"
    assert routes["semantic_alias_projection_apply"]["lease_gate"]["target_path"] == (
        "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    )
    assert routes["semantic_alias_projection_apply"]["required_mutation_fields"] == [
        "execute_write",
        "before_sha256",
        "replacement_body_sha256",
        "semantic_alias_write_confirmation",
        "idempotency_key",
        "confirmation",
        "agent_id",
        "lease_id",
    ]
    assert routes["semantic_alias_mount_manifest_apply"]["mutates_state"] is True
    assert routes["semantic_alias_mount_manifest_apply"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert routes["semantic_alias_mount_manifest_apply"]["edit_lease_required"] is True
    assert routes["semantic_alias_mount_manifest_apply"]["lease_id_required"] is True
    assert routes["semantic_alias_mount_manifest_apply"]["lease_gate_public"]["target_derivation"] == "static"
    assert routes["semantic_alias_mount_manifest_apply"]["lease_gate"]["target_path"] == (
        "ION/05_context/current/codex_agent_mounts/"
        "role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json"
    )
    assert routes["semantic_alias_mount_manifest_apply"]["required_mutation_fields"] == [
        "execute_write",
        "before_sha256",
        "replacement_body_sha256",
        "manifest_write_confirmation",
        "idempotency_key",
        "confirmation",
        "agent_id",
        "lease_id",
    ]
    assert semantic_alias_preflight["ok"] is True
    semantic_alias_preflight_result = semantic_alias_preflight["delegated_result"]
    assert semantic_alias_preflight_result["operation"] == "domainWeaverSemanticAliasSupervisedApplyPreflight"
    assert semantic_alias_preflight_result["ok"] is True
    assert semantic_alias_preflight_result["mutates_active_state"] is False
    assert semantic_alias_preflight_result["active_root_apply_invoked"] is False
    assert [step["route_id"] for step in semantic_alias_preflight_result["write_sequence"]] == [
        "semantic_alias_projection_apply",
        "semantic_alias_mount_manifest_apply",
    ]
    assert routes["comms_overview"]["mutates_state"] is False
    assert routes["spawn_plan_preview"]["mutates_state"] is False
    assert routes["comms_pickup_preview"]["mutates_state"] is False
    assert routes["comms_pickup"]["mutates_state"] is True
    assert routes["comms_pickup"]["idempotency_required"] is True
    assert routes["comms_pickup"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert routes["comms_send"]["write_intent_required_target_roots"] == [
        "ION/05_context/current/agent_comms",
        "ION/05_context/current/runtime_services/receipts",
    ]
    assert routes["comms_pickup"]["write_intent_required_target_roots"] == [
        "ION/05_context/current/agent_comms",
        "ION/05_context/current/runtime_services/receipts",
    ]
    assert routes["comms_autoreaction_proof"]["mutates_state"] is False
    assert routes["comms_dispatch_preview"]["mutates_state"] is False
    assert routes["comms_dispatch_enqueue"]["mutates_state"] is True
    assert routes["comms_dispatch_enqueue"]["idempotency_required"] is True
    assert routes["comms_dispatch_enqueue"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert routes["comms_dispatch_enqueue"]["write_intent_required_target_roots"] == [
        "ION/05_context/current/agent_comms",
        "ION/05_context/current/chatgpt_connector",
        "ION/05_context/current/runtime_services/receipts",
    ]
    assert status["ok"] is True
    status_result = status["delegated_result"]
    assert status_result["projection_exists"] is True
    assert status_result["projection_summary"]["domain_count"] == 2
    assert status_result["projection_summary"]["agent_count"] == 1
    assert status_result["agent_comms_directory_exists"] is True
    assert status_result["safe_spawn_authority"] == "preview_only"
    assert status_result["mutates_active_state"] is False
    assert projection["delegated_result"]["projection_summary"]["weave_status"] == "ready"
    assert projection["delegated_result"]["promotion_review_exists"] is False
    assert projection_refresh_plan["ok"] is True
    projection_refresh_plan_result = projection_refresh_plan["delegated_result"]
    assert projection_refresh_plan_result["content_returned"] == "accepted_projection_target_hashes_gate_blockers"
    assert projection_refresh_plan_result["plan_ok"] is False
    assert projection_refresh_plan_result["mutates_active_state"] is False
    assert projection_refresh_plan_result["target"]["path"] == "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    assert projection_refresh_plan_result["target"]["before_sha256"]
    assert projection_refresh_plan_result["target"]["after_sha256"]
    assert projection_refresh_plan_result["target"]["after_sha256_status"] == "candidate_replacement_body_available_not_applied"
    assert projection_refresh_plan_result["replacement_body_candidate"]["body_omitted_from_plan"] is True
    assert projection_replacement_body["ok"] is True
    projection_replacement_body_result = projection_replacement_body["delegated_result"]
    assert projection_replacement_body_result["schema_id"] == "ion.domain_weaver.projection_replacement_body_candidate.v0_1_candidate"
    assert projection_replacement_body_result["content_returned"] == "candidate_projection_body_hashes_invariants_summary"
    assert projection_replacement_body_result["candidate_body_omitted"] is True
    assert "candidate_body" not in projection_replacement_body_result
    assert projection_replacement_body_result["ok"] is True
    assert projection_replacement_body_result["mutates_active_state"] is False
    assert projection_replacement_body_result["accepted_state_claim"] is False
    assert projection_replacement_body_result["target"]["candidate_body_sha256"]
    assert projection_replacement_body_result["invariants"]["ok"] is True
    assert comms["ok"] is True
    comms_result = comms["delegated_result"]
    assert comms_result["agent_comms_directory_exists"] is True
    assert "agent_comms.start_run" in comms_result["write_routes_not_invoked"]
    assert comms_result["mutates_active_state"] is False
    assert spawn["ok"] is True
    spawn_result = spawn["delegated_result"]
    assert spawn_result["domain_id"] == "domain.test"
    assert spawn_result["role_id"] == "role.test_steward"
    assert spawn_result["plan"]["spawn_authority"] == "preview_only"
    assert any(call["branch_id"] == "domain_weaver_agents" and call["route_id"] == "domain_weaver_status" for call in spawn_result["plan"]["recommended_branch_calls"])
    assert any(call["branch_id"] == "agent_swarm" and call["route_id"] == "spawn_plan" for call in spawn_result["plan"]["recommended_branch_calls"])
    assert spawn_result["mutates_active_state"] is False
    assert spawn_result["accepted_state_claim"] is False
    assert start_plan["ok"] is True
    start_plan_result = start_plan["delegated_result"]
    assert start_plan_result["schema_id"] == "ion.domain_weaver.spawn_dispatch_start_plan.v0_1_candidate"
    assert start_plan_result["queueable_spawn_dispatch_request_count"] == 0
    assert start_plan_result["planned_start_count"] == 0
    assert start_plan_result["blocked_start_count"] == 0
    assert start_plan_result["codex_queue_run_started"] is False
    assert start_plan_result["general_queue_processing_allowed"] is False
    assert start_plan_result["mutates_active_state"] is False
    assert start_plan_result["accepted_state_claim"] is False
    assert quarantine["ok"] is True
    quarantine_result = quarantine["delegated_result"]
    assert quarantine_result["schema_id"] == "ion.domain_weaver.spawn_dispatch_legacy_receipt_quarantine.v0_1_candidate"
    assert quarantine_result["content_returned"] == "legacy_false_enqueue_quarantine_counts_paths_nonclaims"
    assert quarantine_result["mutates_active_state"] is False
    assert quarantine_result["accepted_state_claim"] is False
    assert quarantine_result["actual_spawn_performed"] is False
    assert quarantine_result["codex_queue_run_started"] is False
    assert quarantine_result["worker_start_allowed"] is False
    assert pressure_plan["ok"] is True
    pressure_plan_result = pressure_plan["delegated_result"]
    assert pressure_plan_result["schema_id"] == "ion.domain_weaver.pressure_wave_plan.v0_1_candidate"
    assert pressure_plan_result["content_returned"] == "pressure_wave_caps_batches_spawn_templates_nonclaims"
    assert pressure_plan_result["caps"]["native_slot_cap"] == 6
    assert pressure_plan_result["caps"]["active_native_agent_count"] == 3
    assert pressure_plan_result["lane_count"] == 12
    assert pressure_plan_result["lane_counts"]["foreground_native_batch_count"] == 3
    assert pressure_plan_result["actual_spawn_performed"] is False
    assert pressure_plan_result["recursive_child_spawn_allowed"] is False
    assert pressure_plan_result["codex_queue_run_started"] is False
    assert pressure_plan_result["accepted_state_claim"] is False
    assert backlog_hygiene["ok"] is True
    backlog_hygiene_result = backlog_hygiene["delegated_result"]
    assert backlog_hygiene_result["content_returned"] == "compact_worker_start_backlog_hygiene"
    assert backlog_hygiene_result["mutates_active_state"] is False
    assert backlog_hygiene_result["general_queue_processing_allowed"] is False
    assert backlog_hygiene_result["codex_queue_run_started"] is False
    assert active_context_preflight["ok"] is True
    active_context_preflight_result = active_context_preflight["delegated_result"]
    assert active_context_preflight_result["schema_id"] == "ion.domain_weaver.active_context_reissue_preflight.v0_1_candidate"
    assert active_context_preflight_result["refresh_run"] is False
    assert active_context_preflight_result["mutates_active_state"] is False
    assert active_context_refresh_plan["ok"] is False
    assert active_context_refresh_plan["refusal_class"] == "DELEGATED_ROUTE_BLOCKED"
    active_context_refresh_plan_result = active_context_refresh_plan["delegated_result"]
    assert active_context_refresh_plan_result["schema_id"] == "ion.domain_weaver.active_context.gated_refresh.v0_1_candidate"
    assert active_context_refresh_plan_result["refresh_run"] is False
    assert active_context_refresh_plan_result["mutates_active_state"] is False
    assert active_context_refresh_plan_result["write_authority_granted"] is False
    assert "active_context_refresh_confirmation_required" in active_context_refresh_plan_result["blockers"]

    send_args = {
        "from_role": "operator",
        "to_roles": ["role.comms_cartographer"],
        "channel_id": "team",
        "subject": "Domain Weaver comms action smoke",
        "body": "Please inspect the Domain Weaver JOC comms action smoke.",
        "message_kind": "thread_note",
        "source_refs": ["ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"],
    }
    agent_id = "codex_cli:domain-weaver-comms-gate-smoke"
    send_idempotency = "domain-weaver-agent-comms-send-smoke"
    send_lease_id = "lease-domain-weaver-comms-send"
    send_target_paths = [
        "ION/05_context/current/agent_comms",
        "ION/05_context/current/runtime_services/receipts",
    ]
    _seed_codex_queue_write_intent_lease(
        root,
        agent_id=agent_id,
        lease_id=send_lease_id,
        target_paths=send_target_paths,
        route_id="comms_send",
        mutation_context="domain_weaver_agents",
        idempotency_key=send_idempotency,
    )
    preview = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_send_preview",
        args=send_args,
        expected_route_schema_version="v0",
    )
    no_idempotency = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_send",
        args={**send_args, "confirmation": "ION_BOUNDED_WRITE_CONFIRMED"},
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    sent = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_send",
        args={
            **send_args,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": send_idempotency,
            "agent_id": agent_id,
            "write_intent_lease_id": send_lease_id,
            "write_intent": {"target_paths": send_target_paths},
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key=send_idempotency,
        expected_route_schema_version="v0",
    )

    assert preview["ok"] is True
    preview_result = preview["delegated_result"]
    assert preview_result["would_send"] is True
    assert preview_result["mutates_active_state"] is False
    assert preview_result["send_route"] == "domain_weaver_agents.comms_send"
    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert sent["ok"] is True
    assert sent["mutates_active_state"] is True
    sent_result = sent["delegated_result"]
    assert sent_result["ok"] is True
    assert sent_result["mutates_active_state"] is True
    send_result = sent_result["send_result"]
    assert send_result["ok"] is True
    assert send_result["message_id"]
    assert send_result["thread_id"]
    assert (root / send_result["message_path"]).is_file()
    assert (root / send_result["thread_path"]).is_file()
    assert (root / sent_result["receipt_path"]).is_file()
    assert send_result["production_authority"] is False
    assert send_result["live_execution_authority"] is False
    assert sent_result["accepted_state_claim"] is False

    pickup_args = {
        "role_id": "role.comms_cartographer",
        "message_id": send_result["message_id"],
        "thread_id": send_result["thread_id"],
        "carrier_id": "CODEX_CLI_CARRIER",
        "context_package_id": "test_context_package",
        "pickup_reason": "domain_weaver_agent_comms_pickup_smoke",
    }
    pickup_idempotency = "domain-weaver-agent-comms-pickup-smoke"
    pickup_lease_id = "lease-domain-weaver-comms-pickup"
    pickup_target_paths = [
        "ION/05_context/current/agent_comms",
        "ION/05_context/current/runtime_services/receipts",
    ]
    _seed_codex_queue_write_intent_lease(
        root,
        agent_id=agent_id,
        lease_id=pickup_lease_id,
        target_paths=pickup_target_paths,
        route_id="comms_pickup",
        mutation_context="domain_weaver_agents",
        idempotency_key=pickup_idempotency,
    )
    pickup_preview = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_pickup_preview",
        args=pickup_args,
        expected_route_schema_version="v0",
    )
    pickup_no_idempotency = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_pickup",
        args={**pickup_args, "confirmation": "ION_BOUNDED_WRITE_CONFIRMED"},
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    pickup_no_confirmation = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_pickup",
        args={**pickup_args, "idempotency_key": "domain-weaver-agent-comms-pickup-smoke"},
        idempotency_key="domain-weaver-agent-comms-pickup-smoke",
        expected_route_schema_version="v0",
    )
    picked_up = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_pickup",
        args={
            **pickup_args,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": pickup_idempotency,
            "agent_id": agent_id,
            "write_intent_lease_id": pickup_lease_id,
            "write_intent": {"target_paths": pickup_target_paths},
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key=pickup_idempotency,
        expected_route_schema_version="v0",
    )
    replayed_pickup = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_pickup",
        args={
            **pickup_args,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": pickup_idempotency,
            "agent_id": agent_id,
            "write_intent_lease_id": pickup_lease_id,
            "write_intent": {"target_paths": pickup_target_paths},
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key=pickup_idempotency,
        expected_route_schema_version="v0",
    )
    duplicate_pickup_idempotency = "domain-weaver-agent-comms-pickup-smoke-duplicate"
    duplicate_pickup_lease_id = "lease-domain-weaver-comms-pickup-duplicate"
    _seed_codex_queue_write_intent_lease(
        root,
        agent_id=agent_id,
        lease_id=duplicate_pickup_lease_id,
        target_paths=pickup_target_paths,
        route_id="comms_pickup",
        mutation_context="domain_weaver_agents",
        idempotency_key=duplicate_pickup_idempotency,
    )
    duplicate_pickup = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_pickup",
        args={
            **pickup_args,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": duplicate_pickup_idempotency,
            "agent_id": agent_id,
            "write_intent_lease_id": duplicate_pickup_lease_id,
            "write_intent": {"target_paths": pickup_target_paths},
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key=duplicate_pickup_idempotency,
        expected_route_schema_version="v0",
    )

    assert pickup_preview["ok"] is True
    pickup_preview_result = pickup_preview["delegated_result"]["pickup_preview"]
    assert pickup_preview_result["ok"] is True
    assert pickup_preview_result["would_mark_inbox_ref_picked_up"] is True
    assert pickup_preview_result["mutates_active_state"] is False
    assert pickup_no_idempotency["ok"] is False
    assert pickup_no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert pickup_no_confirmation["ok"] is False
    assert pickup_no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"
    assert picked_up["ok"] is True
    assert picked_up["mutates_active_state"] is True
    picked_up_result = picked_up["delegated_result"]
    assert picked_up_result["ok"] is True
    assert picked_up_result["mutates_active_state"] is True
    pickup_result = picked_up_result["pickup_result"]
    assert pickup_result["ok"] is True
    assert pickup_result["ref_status"] == "picked_up"
    assert pickup_result["claim_boundary"] == "proves_role_inbox_pickup_only_not_worker_execution_or_accepted_state"
    assert (root / pickup_result["pickup_receipt_path"]).is_file()
    assert (root / picked_up_result["receipt_path"]).is_file()
    inbox_ref = json.loads((root / pickup_result["inbox_ref_path"]).read_text(encoding="utf-8"))
    assert inbox_ref["status"] == "picked_up"
    assert inbox_ref["pickup_context_package_id"] == "test_context_package"
    assert replayed_pickup["ok"] is True
    replayed_result = replayed_pickup["delegated_result"]
    assert replayed_result["mutates_active_state"] is False
    assert replayed_result["pickup_result"]["idempotent_replay"] is True
    assert replayed_result["pickup_result"]["mutates_active_state"] is False
    assert duplicate_pickup["ok"] is False
    assert duplicate_pickup["refusal_class"] == "AGENT_COMMS_PICKUP_FAILED"
    assert duplicate_pickup["pickup_result"]["finding"] == "inbox_ref_not_unread"

    (root / "ION/03_registry/agent_roster_registry.yaml").write_text(
        "\n".join(
            [
                "agents:",
                "  - entity_id: role.comms_cartographer",
                "    display_name: Comms Cartographer",
                "    registry_primary_domain: domain.agent_communication_systems",
                "    source_refs:",
                "      - README.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    dispatch_args = {
        "role_id": "role.comms_cartographer",
        "agent_role": "role.comms_cartographer",
        "domain_id": "domain.agent_communication_systems",
        "message_id": send_result["message_id"],
        "thread_id": send_result["thread_id"],
        "pickup_receipt_path": pickup_result["pickup_receipt_path"],
        "objective": "Inspect the Domain Weaver comms pickup bridge and report blockers only.",
        "proof_correlation_id": "test-proof-correlation",
    }
    dispatch_idempotency = "domain-weaver-agent-comms-dispatch-smoke"
    dispatch_lease_id = "lease-domain-weaver-comms-dispatch"
    dispatch_target_paths = [
        "ION/05_context/current/agent_comms",
        "ION/05_context/current/chatgpt_connector",
        "ION/05_context/current/runtime_services/receipts",
    ]
    _seed_codex_queue_write_intent_lease(
        root,
        agent_id=agent_id,
        lease_id=dispatch_lease_id,
        target_paths=dispatch_target_paths,
        route_id="comms_dispatch_enqueue",
        mutation_context="domain_weaver_agents",
        idempotency_key=dispatch_idempotency,
    )
    dispatch_preview = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_dispatch_preview",
        args=dispatch_args,
        expected_route_schema_version="v0",
    )
    dispatch_no_idempotency = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_dispatch_enqueue",
        args={**dispatch_args, "confirmation": "ION_BOUNDED_WRITE_CONFIRMED"},
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    dispatch_no_confirmation = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_dispatch_enqueue",
        args={**dispatch_args, "idempotency_key": "domain-weaver-agent-comms-dispatch-smoke"},
        idempotency_key="domain-weaver-agent-comms-dispatch-smoke",
        expected_route_schema_version="v0",
    )
    dispatched = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_dispatch_enqueue",
        args={
            **dispatch_args,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": dispatch_idempotency,
            "agent_id": agent_id,
            "write_intent_lease_id": dispatch_lease_id,
            "write_intent": {"target_paths": dispatch_target_paths},
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        idempotency_key=dispatch_idempotency,
        expected_route_schema_version="v0",
    )

    assert dispatch_preview["ok"] is True
    dispatch_preview_result = dispatch_preview["delegated_result"]["dispatch_preview"]
    assert dispatch_preview_result["ok"] is True
    assert dispatch_preview_result["domain_id"] == "domain.agent_communication_systems"
    assert dispatch_preview_result["model_route"]["requested_model"] == "gpt-5.5"
    assert dispatch_preview_result["model_route"]["requested_reasoning_effort"] == "xhigh"
    assert dispatch_preview_result["model_route"]["codex_model_override"] == {
        "selected_model": "gpt-5.5",
        "selected_reasoning_effort": "xhigh",
        "reason": "domain_weaver_agent_comms_dispatch_high_stakes_route",
    }
    assert dispatch_preview_result["would_enqueue_codex_work_request"] is True
    assert dispatch_preview_result["would_start_worker"] is False
    assert dispatch_no_idempotency["ok"] is False
    assert dispatch_no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert dispatch_no_confirmation["ok"] is False
    assert dispatch_no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"
    assert dispatched["ok"] is True
    assert dispatched["mutates_active_state"] is True
    dispatched_result = dispatched["delegated_result"]
    assert dispatched_result["dispatch_status"] == "queued_not_started"
    assert dispatched_result["accepted_state_claim"] is False
    dispatch_result = dispatched_result["dispatch_result"]
    assert dispatch_result["ok"] is True
    assert dispatch_result["status"] == "QUEUED"
    assert (root / dispatch_result["invocation_path"]).is_file()
    assert (root / dispatch_result["codex_work_request_path"]).is_file()
    invocation_packet = json.loads((root / dispatch_result["invocation_path"]).read_text(encoding="utf-8"))
    work_request = json.loads((root / dispatch_result["codex_work_request_path"]).read_text(encoding="utf-8"))
    assert invocation_packet["domain_id"] == "domain.agent_communication_systems"
    assert work_request["domain_id"] == "domain.agent_communication_systems"
    assert invocation_packet["risk_level"] == "critical"
    assert work_request["risk_level"] == "critical"
    assert invocation_packet["requested_model"] == "gpt-5.5"
    assert invocation_packet["requested_reasoning_effort"] == "xhigh"
    assert invocation_packet["model_override_reason"] == "domain_weaver_agent_comms_dispatch_high_stakes_route"
    assert invocation_packet["codex_model_override"] == {
        "selected_model": "gpt-5.5",
        "selected_reasoning_effort": "xhigh",
        "reason": "domain_weaver_agent_comms_dispatch_high_stakes_route",
    }
    assert work_request["requested_model"] == "gpt-5.5"
    assert work_request["requested_reasoning_effort"] == "xhigh"
    assert work_request["model_override_reason"] == "domain_weaver_agent_comms_dispatch_high_stakes_route"
    assert work_request["codex_model_override"] == invocation_packet["codex_model_override"]
    assert invocation_packet["domain_weaver_agent_comms_dispatch"]["proof_correlation_id"] == "test-proof-correlation"
    assert work_request["proof_correlation_id"] == "test-proof-correlation"
    assert work_request["source_agent_comms_message_id"] == send_result["message_id"]
    assert work_request["pickup_receipt_path"] == pickup_result["pickup_receipt_path"]
    assert work_request["status"] == "QUEUED_FOR_CODEX_CARRIER"
    assert work_request["live_execution_authority"] is False

    autoreaction = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_autoreaction_proof",
        args={
            "role_id": "role.comms_cartographer",
            "message_id": send_result["message_id"],
            "thread_id": send_result["thread_id"],
            "pickup_receipt_path": pickup_result["pickup_receipt_path"],
            "codex_work_request_path": dispatch_result["codex_work_request_path"],
        },
        expected_route_schema_version="v0",
    )

    assert autoreaction["ok"] is True
    proof = autoreaction["delegated_result"]
    assert proof["mutates_active_state"] is False
    assert proof["automatic_agent_reaction_proven"] is False
    assert proof["proof_state"] == "durable_delivery_and_pickup_only"
    assert "task_return_path" in proof["missing_links"]
    assert proof["accepted_state_claim"] is False

    message_only_autoreaction = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_autoreaction_proof",
        args={
            "message_id": send_result["message_id"],
        },
        expected_route_schema_version="v0",
    )

    assert message_only_autoreaction["ok"] is True
    message_only_proof = message_only_autoreaction["delegated_result"]
    assert message_only_proof["automatic_agent_reaction_proven"] is False
    assert message_only_proof["proof_state"] == "durable_delivery_and_pickup_only"
    assert "message_path" not in message_only_proof["missing_links"]
    assert "thread_path" not in message_only_proof["missing_links"]
    assert "inbox_ref" not in message_only_proof["missing_links"]
    assert "pickup_receipt" not in message_only_proof["missing_links"]
    assert "task_return_path" in message_only_proof["missing_links"]

    task_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/alternate_return.json"
    task_return_path = root / task_return_rel
    task_return_path.parent.mkdir(parents=True, exist_ok=True)
    task_return_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
                "accepted_for_carrier_intake": True,
                "carrier_intake_only": True,
                "product_state_accepted": False,
                "return_lane": "alternate_worker_return",
                "alternate_worker_return": True,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    run_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/alternate_recovery_run/run.json"
    run_path = root / run_rel
    run_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner.run_packet.v1",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": task_return_rel,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    reply_path = root / f"ION/05_context/current/agent_comms/threads/{send_result['thread_id']}/messages/20260604T0000000000_msg_alternate_recovery.json"
    reply_path.parent.mkdir(parents=True, exist_ok=True)
    reply_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.agent_comms.message.v1",
                "message_id": "msg_alternate_recovery",
                "message_kind": "synced_reply",
                "thread_id": send_result["thread_id"],
                "source_refs": [send_result["message_id"]],
                "artifact_refs": [task_return_rel],
                "receipt_refs": [],
                "body": f"alternate recovery return for {send_result['message_id']} via {task_return_rel}",
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    alternate_recovery = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_autoreaction_proof",
        args={
            "message_id": send_result["message_id"],
            "thread_id": send_result["thread_id"],
            "pickup_receipt_path": pickup_result["pickup_receipt_path"],
            "codex_work_request_path": dispatch_result["codex_work_request_path"],
            "worker_run_packet_path": run_rel,
            "task_return_path": task_return_rel,
            "synced_reply_message_path": reply_path.relative_to(root).as_posix(),
        },
        expected_route_schema_version="v0",
    )

    assert alternate_recovery["ok"] is True
    alternate_proof = alternate_recovery["delegated_result"]
    assert alternate_proof["proof_ok"] is True
    assert alternate_proof["proof_state"] == "alternate_worker_return_recovery_chain_proven"
    assert alternate_proof["automatic_agent_reaction_proven"] is False
    assert alternate_proof["alternate_worker_return_recovery_proven"] is True
    assert alternate_proof["task_return_lane"] == "alternate_worker_return"
    assert alternate_proof["alternate_worker_return"] is True
    assert alternate_proof["missing_links"] == []

    work_request_path = root / dispatch_result["codex_work_request_path"]
    work_request_packet = json.loads(work_request_path.read_text(encoding="utf-8"))
    work_request_packet["latest_return_packet_path"] = task_return_rel
    work_request_path.write_text(json.dumps(work_request_packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    original_failed_run_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/original_failed_run/run.json"
    original_failed_run_path = root / original_failed_run_rel
    original_failed_run_path.parent.mkdir(parents=True, exist_ok=True)
    original_failed_run_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner.run_packet.v1",
                "status": "CODEX_CLI_TRANSIENT_USAGE_LIMIT_BUG_RETRY_EXHAUSTED",
                "failure_classification": "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BUG",
                "latest_return_packet_path": None,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    original_failed_run_projection = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="comms_autoreaction_proof",
        args={
            "message_id": send_result["message_id"],
            "thread_id": send_result["thread_id"],
            "pickup_receipt_path": pickup_result["pickup_receipt_path"],
            "codex_work_request_path": dispatch_result["codex_work_request_path"],
            "worker_run_packet_path": original_failed_run_rel,
        },
        expected_route_schema_version="v0",
    )

    assert original_failed_run_projection["ok"] is True
    original_failed_run_proof = original_failed_run_projection["delegated_result"]
    assert original_failed_run_proof["proof_ok"] is False
    assert original_failed_run_proof["automatic_agent_reaction_proven"] is False
    assert original_failed_run_proof["alternate_worker_return_recovery_proven"] is False
    assert original_failed_run_proof["first_missing_link"] == "task_return_path"
    assert original_failed_run_proof["task_return_lane"] is None
    assert "task_return_path" in original_failed_run_proof["missing_links"]


def test_domain_weaver_pressure_wave_seed_route_requires_write_intent_and_writes_only_spawn_rows(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    agent_id = "codex_cli:pressure-wave-seed"
    lease_id = "lease-pressure-wave-seed"
    idempotency_key = "domain-weaver-pressure-wave-seed"
    target_paths = ["ION/05_context/current/domain_weaver/workers"]

    no_idempotency = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="pressure_wave_spawn_request_seed",
        args={
            "execute_write": True,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "agent_id": agent_id,
            "write_intent_lease_id": lease_id,
            "write_intent": {"target_paths": target_paths},
        },
        expected_route_schema_version="v0",
    )
    no_lease = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="pressure_wave_spawn_request_seed",
        args={
            "execute_write": True,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": idempotency_key,
            "agent_id": agent_id,
            "write_intent_lease_id": lease_id,
            "write_intent": {"target_paths": target_paths},
        },
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    _seed_codex_queue_write_intent_lease(
        root,
        agent_id=agent_id,
        lease_id=lease_id,
        target_paths=target_paths,
        route_id="pressure_wave_spawn_request_seed",
        mutation_context="domain_weaver_agents",
        idempotency_key=idempotency_key,
    )
    seeded = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="pressure_wave_spawn_request_seed",
        args={
            "execute_write": True,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": idempotency_key,
            "agent_id": agent_id,
            "write_intent_lease_id": lease_id,
            "write_intent": {"target_paths": target_paths},
            "limit": 2,
        },
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_lease["ok"] is False
    assert no_lease["refusal_class"] == "LEASE_REQUIRED"
    assert seeded["ok"] is True
    seeded_result = seeded["delegated_result"]
    assert seeded_result["schema_id"] == "ion.domain_weaver.pressure_wave_spawn_request_seed.v0_1"
    assert seeded_result["status"] == "pressure_wave_spawn_requests_seeded"
    assert seeded_result["spawn_request_count"] == 2
    assert seeded_result["mutates_active_state"] is True
    assert seeded_result["actual_spawn_performed"] is False
    assert seeded_result["codex_queue_run_started"] is False
    assert seeded_result["worker_start_allowed"] is False
    assert seeded_result["accepted_state_claimed"] is False
    assert seeded_result["production_or_live_authority"] is False
    for rel_path in seeded_result["spawn_request_paths"]:
        assert rel_path.startswith("ION/05_context/current/domain_weaver/workers/")
        payload = json.loads((root / rel_path).read_text(encoding="utf-8"))
        assert payload["status"] == "requested"
        assert payload["spawn_execution"]["direct_nested_subagent_spawn_allowed"] is False
        assert payload["spawn_execution"]["actual_spawn_performed"] is False
        assert payload["paths"]["codex_solo_touched"] is False
    assert not list((root / "ION/05_context/current/chatgpt_connector/codex_work_requests").glob("*.json"))


def test_domain_weaver_active_context_refresh_plan_uses_live_exclusive_lease_gate(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    agent_id = "codex_cli:domain-weaver-active-context-refresh"
    lease_id = "lease-domain-weaver-active-context-refresh"
    target_path = (
        "ION/05_context/current/codex_agent_mounts/"
        "role_context_cartographer__domain_context_active_resolver/.ion/ACTIVE_CONTEXT_PACKAGE.md"
    )
    active_context_path = root / target_path
    active_context_path.parent.mkdir(parents=True, exist_ok=True)
    active_context_path.write_text("old active context package\n", encoding="utf-8")
    preflight_rel = "ION/05_context/current/domain_weaver/active_context_refresh/test_preflight.json"
    preflight_path = root / preflight_rel
    preflight_path.parent.mkdir(parents=True, exist_ok=True)
    preflight_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.active_context_reissue_preflight.v0_1_candidate",
                "preflight_completed": True,
                "refresh_run": False,
                "mutates_active_state": False,
                "active_root": str(root),
                "target_mount_count": 1,
                "target_mounts": [
                    {
                        "mount_id": "role_context_cartographer__domain_context_active_resolver",
                        "role_id": "role.context_cartographer",
                        "domain_id": "domain.context_active_resolver",
                    }
                ],
                "mount_package_refs_requiring_reissue": [
                    {
                        "path": target_path,
                        "mount_id": "role_context_cartographer__domain_context_active_resolver",
                        "reason": "active_context_package_stale",
                    }
                ],
                "blockers": ["active_context_targets_require_reissue"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    _seed_exclusive_active_context_refresh_lease(
        root,
        agent_id=agent_id,
        lease_id=lease_id,
        target_paths=[target_path],
    )

    result = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="active_context_gated_refresh_plan",
        args={
            "preflight_path": preflight_rel,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": "domain-weaver-active-context-refresh-smoke",
            "agent_id": agent_id,
            "lease_id": lease_id,
            "lease_type": "exclusive_write",
            "preview_only": False,
            "allow_write": True,
        },
        expected_route_schema_version="v0",
    )

    assert result["ok"] is False
    assert result["refusal_class"] == "DELEGATED_ROUTE_BLOCKED"
    assert result["mutates_active_state"] is False
    delegated = result["delegated_result"]
    assert delegated["schema_id"] == "ion.domain_weaver.active_context.gated_refresh.v0_1_candidate"
    assert delegated["ok"] is False
    assert delegated["write_gate_passed"] is True
    assert delegated["write_authority_granted"] is False
    assert delegated["live_worker_shift_gate_checked"] is True
    assert delegated["non_preview_refresh_allowed"] is False
    assert delegated["refresh_run"] is False
    assert delegated["mutates_active_state"] is False
    assert delegated["lease_gate"]["worker_shift_live_lease_gate"]["ok"] is True
    assert delegated["lease_gate"]["worker_shift_live_lease_gate"]["worker_shift_gate"]["ok"] is True
    assert delegated["target_coverage"]["target_coverage_ok"] is True
    assert "active_context_refresh_write_path_not_implemented" in delegated["blockers"]
    assert active_context_path.read_text(encoding="utf-8") == "old active context package\n"


def test_domain_weaver_active_context_refresh_plan_rejects_unsafe_preflight_path(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)

    result = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="active_context_gated_refresh_plan",
        args={"preflight_path": "../outside.json"},
        expected_route_schema_version="v0",
    )

    assert result["ok"] is False
    assert result["refusal_class"] == "PATH_INVALID"
    delegated = result["delegated_result"]
    assert delegated["ok"] is False
    assert delegated["refusal_class"] == "PATH_INVALID"
    assert delegated["mutates_active_state"] is False
    assert delegated["accepted_state_claim"] is False


def test_domain_weaver_active_context_refresh_apply_is_confirmed_and_handler_gated(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    agent_id = "codex_cli:domain-weaver-active-context-refresh"
    lease_id = "lease-domain-weaver-active-context-refresh-apply"
    target_path = (
        "ION/05_context/current/codex_agent_mounts/"
        "role_context_cartographer__domain_context_active_resolver/.ion/ACTIVE_CONTEXT_PACKAGE.md"
    )
    active_context_path = root / target_path
    active_context_path.parent.mkdir(parents=True, exist_ok=True)
    active_context_path.write_text("old active context package\n", encoding="utf-8")
    preflight_rel = "ION/05_context/current/domain_weaver/active_context_refresh/test_apply_preflight.json"
    preflight_path = root / preflight_rel
    preflight_path.parent.mkdir(parents=True, exist_ok=True)
    preflight_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.active_context_reissue_preflight.v0_1_candidate",
                "preflight_completed": True,
                "refresh_run": False,
                "mutates_active_state": False,
                "active_root": str(root),
                "target_mount_count": 1,
                "target_mounts": [
                    {
                        "mount_id": "role_context_cartographer__domain_context_active_resolver",
                        "role_id": "role.context_cartographer",
                        "domain_id": "domain.context_active_resolver",
                        "lane_ids": ["active_context_apply_smoke"],
                    }
                ],
                "mount_package_refs_requiring_reissue": [
                    {
                        "path": target_path,
                        "mount_id": "role_context_cartographer__domain_context_active_resolver",
                        "reason": "active_context_package_stale",
                    }
                ],
                "blockers": ["active_context_targets_require_reissue"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    _seed_exclusive_active_context_refresh_lease(
        root,
        agent_id=agent_id,
        lease_id=lease_id,
        target_paths=[target_path],
    )
    apply_args = {
        "preflight_path": preflight_rel,
        "execute_write": True,
        "idempotency_key": "domain-weaver-active-context-refresh-apply-smoke",
        "agent_id": agent_id,
        "lease_id": lease_id,
    }

    no_confirmation = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="active_context_gated_refresh_apply",
        args=apply_args,
        expected_route_schema_version="v0",
    )
    no_execute = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="active_context_gated_refresh_apply",
        args={
            **apply_args,
            "execute_write": False,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": "domain-weaver-active-context-refresh-apply-no-execute",
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    applied = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="active_context_gated_refresh_apply",
        args={**apply_args, "confirmation": "ION_BOUNDED_WRITE_CONFIRMED"},
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"
    assert no_execute["ok"] is False
    assert no_execute["refusal_class"] == "DELEGATED_ROUTE_BLOCKED"
    assert "active_context_refresh_execute_write_required" in no_execute["delegated_result"]["blockers"]
    assert applied["ok"] is True
    assert applied["mutates_active_state"] is True
    assert applied["handler_dynamic_target_gate_deferred"]["deferred"] is True
    delegated = applied["delegated_result"]
    assert delegated["schema_id"] == "ion.domain_weaver.active_context.gated_refresh_apply.v0_1_candidate"
    assert delegated["ok"] is True
    assert delegated["refresh_run"] is True
    assert delegated["accepted_state_claim"] is False
    assert delegated["target_count"] == 1
    assert delegated["receipt_path"].startswith("ION/05_context/current/domain_weaver/active_context_refresh/apply_receipts/")
    assert "gated_active_context_refresh" in active_context_path.read_text(encoding="utf-8")


def test_domain_weaver_worker_start_readiness_summary_reports_blockers(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    request_dir = root / "ION/05_context/current/chatgpt_connector/codex_work_requests"
    request_dir.mkdir(parents=True, exist_ok=True)
    (request_dir / "queued_missing_domain.json").write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_missing_domain",
                "status": "QUEUED_FOR_CODEX_CARRIER",
                "lane_id": "architecture_lane",
                "role_id": "role.exact_active_binding_specialist",
                "work_class": "exact_active_binding_audit",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    full = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="worker_start_readiness",
        args={},
        expected_route_schema_version="v0",
    )
    summary = action_branch_invoke(
        root,
        branch_id="domain_weaver_agents",
        route_id="worker_start_readiness_summary",
        args={},
        expected_route_schema_version="v0",
    )

    assert full["ok"] is False
    assert full["finding"] == "worker_start_readiness_blocked"
    assert full["delegated_result"]["finding"] == "worker_start_readiness_blocked"
    assert summary["ok"] is False
    assert summary["finding"] == "worker_start_readiness_blocked"
    delegated = summary["delegated_result"]
    assert delegated["finding"] == "worker_start_readiness_blocked"
    assert delegated["mutates_active_state"] is False
    assert delegated["content_returned"] == "compact_worker_start_readiness_summary_only"
    assert "queueable_requests_missing_domain_id" in delegated["blockers"]
    assert delegated["summary"]["queueable_request_count"] == 1
    assert delegated["lane_summaries"][0]["lane_id"] == "architecture_lane"


def test_local_intelligence_branch_indexes_symbols_without_execution(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    module_path = root / "ION/04_packages/kernel/demo_local_intelligence.py"
    test_path = root / "ION/tests/test_demo_local_intelligence.py"
    module_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text(
        "import json\n\n"
        "class DemoThing:\n"
        "    \"\"\"Demo class.\"\"\"\n"
        "    pass\n\n"
        "def useful_function():\n"
        "    \"\"\"Useful docstring.\"\"\"\n"
        "    return 1\n",
        encoding="utf-8",
    )
    test_path.write_text("from kernel import demo_local_intelligence\n", encoding="utf-8")

    described = action_branch_describe(root, branch_id="local_intelligence", depth="full")
    manifest = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="tool_manifest_deep",
        args={"root_path": "ION/04_packages/kernel", "limit": 10},
        expected_route_schema_version="v0",
    )
    symbols = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="code_symbol_index",
        args={"path": "ION/04_packages/kernel/demo_local_intelligence.py"},
        expected_route_schema_version="v0",
    )
    blocked = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="code_symbol_index",
        args={"path": "README.md"},
        expected_route_schema_version="v0",
    )

    assert described["ok"] is True
    assert described["branch"]["branch_id"] == "local_intelligence"
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert routes["tool_manifest_deep"]["mutates_state"] is False
    assert routes["code_symbol_index"]["mutates_state"] is False
    assert manifest["ok"] is True
    assert manifest["mutates_active_state"] is False
    manifest_result = manifest["delegated_result"]
    assert manifest_result["ok"] is True
    assert manifest_result["arbitrary_shell_authority"] is False
    assert manifest_result["exec_indexed_code"] is False
    demo_module = next(item for item in manifest_result["modules"] if item["path"].endswith("demo_local_intelligence.py"))
    assert demo_module["class_count"] == 1
    assert demo_module["function_count"] == 1
    assert demo_module["test_reference_count"] == 1
    assert symbols["ok"] is True
    symbol_result = symbols["delegated_result"]
    names = {item["name"] for item in symbol_result["files"][0]["symbols"]}
    assert {"DemoThing", "useful_function"} <= names
    assert symbol_result["exec_indexed_code"] is False
    assert blocked["ok"] is False
    assert blocked["delegated_result"]["refusal_class"] == "PATH_NOT_ALLOWED"


def test_local_intelligence_dag_extracts_route_and_validation_graphs(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    monkeypatch.setattr(runtime_services.subprocess, "run", _fake_runtime_services_run)

    validation = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="dag_extract",
        args={"dag_type": "validation_suite_dag", "suite_id": "local_intelligence_manifest_smoke"},
        expected_route_schema_version="v0",
    )
    routes = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="dag_extract",
        args={"dag_type": "action_route_dag", "branch_id": "local_intelligence"},
        expected_route_schema_version="v0",
    )
    blocked = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="dag_extract",
        args={"dag_type": "embedding_vector_dag"},
        expected_route_schema_version="v0",
    )

    assert validation["ok"] is True
    assert validation["mutates_active_state"] is False
    validation_result = validation["delegated_result"]
    assert validation_result["ok"] is True
    assert validation_result["dag_type"] == "validation_suite_dag"
    assert validation_result["arbitrary_shell_authority"] is False
    assert validation_result["exec_indexed_code"] is False
    assert any(node["id"] == "suite:local_intelligence_manifest_smoke" for node in validation_result["nodes"])
    assert any(edge["kind"] == "includes_test" for edge in validation_result["edges"])
    assert routes["ok"] is True
    route_result = routes["delegated_result"]
    assert route_result["dag_type"] == "action_route_dag"
    assert any(node["id"] == "branch:local_intelligence" for node in route_result["nodes"])
    assert any(node["id"] == "route:local_intelligence.dag_extract" for node in route_result["nodes"])
    assert any(edge["from"] == "route:local_intelligence.dag_extract" and edge["to"] == "local_handler:runtime_services" for edge in route_result["edges"])
    assert blocked["ok"] is False
    assert blocked["delegated_result"]["refusal_class"] == "DAG_TYPE_NOT_ALLOWED"


def test_local_intelligence_data_profile_profiles_common_formats(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    data_dir = root / "ION/05_context/current/action_surface_cartography"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "profile.json").write_text(
        json.dumps({"schema_id": "ion.test.profile", "items": [{"name": "a"}, {"name": "b"}]}),
        encoding="utf-8",
    )
    (data_dir / "profile.yaml").write_text("schema_id: ion.test.yaml\nname: demo\nname: second\n", encoding="utf-8")
    (data_dir / "profile.csv").write_text("name,status\na,ok\nb,\n", encoding="utf-8")
    (data_dir / "profile.md").write_text(
        "# Heading\n\nschema_id: ion.test.md\nSee ION/04_packages/kernel/ion_runtime_service_control.py\n",
        encoding="utf-8",
    )

    json_profile = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="data_profile",
        args={"path": "ION/05_context/current/action_surface_cartography/profile.json"},
        expected_route_schema_version="v0",
    )
    yaml_profile = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="data_profile",
        args={"path": "ION/05_context/current/action_surface_cartography/profile.yaml"},
        expected_route_schema_version="v0",
    )
    csv_profile = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="data_profile",
        args={"path": "ION/05_context/current/action_surface_cartography/profile.csv"},
        expected_route_schema_version="v0",
    )
    md_profile = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="data_profile",
        args={"path": "ION/05_context/current/action_surface_cartography/profile.md"},
        expected_route_schema_version="v0",
    )
    blocked = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="data_profile",
        args={"path": "README.md"},
        expected_route_schema_version="v0",
    )

    assert json_profile["ok"] is True
    json_result = json_profile["delegated_result"]
    assert json_result["file_type"] == "json"
    assert json_result["content_returned"] == "summary_only"
    assert json_result["profile"]["schema_ids"] == ["ion.test.profile"]
    assert yaml_profile["delegated_result"]["file_type"] == "yaml"
    assert yaml_profile["delegated_result"]["profile"]["schema_ids"] == ["ion.test.yaml"]
    assert csv_profile["delegated_result"]["file_type"] == "csv"
    assert csv_profile["delegated_result"]["profile"]["row_count"] == 2
    assert csv_profile["delegated_result"]["profile"]["non_empty_counts"]["status"] == 1
    assert md_profile["delegated_result"]["file_type"] == "markdown"
    assert md_profile["delegated_result"]["profile"]["heading_count"] == 1
    assert "ion.test.md" in md_profile["delegated_result"]["profile"]["schema_ids"]
    assert "ION/04_packages/kernel/ion_runtime_service_control.py" in md_profile["delegated_result"]["profile"]["path_refs"]
    assert md_profile["delegated_result"]["arbitrary_shell_authority"] is False
    assert md_profile["delegated_result"]["exec_indexed_code"] is False
    assert md_profile["delegated_result"]["network_authority"] is False
    assert blocked["ok"] is False
    assert blocked["delegated_result"]["refusal_class"] == "PATH_NOT_ALLOWED"


def test_local_intelligence_receipt_graph_links_receipts_and_proof_refs(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    receipt_dir = root / "ION/05_context/current/runtime_services/test_run_receipts"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt = receipt_dir / "20260602T000000Z_focused_test_run_demo.json"
    receipt.write_text(
        json.dumps(
            {
                "schema_id": "ion.runtime_focused_test_run_receipt.v0_1",
                "created_at": "2026-06-02T00:00:00+00:00",
                "suite_id": "demo_suite",
                "idempotency_key": "demo-key",
                "payload": {
                    "ok": True,
                    "finding": "tests_passed",
                    "returncode": 0,
                    "test_ids": ["ION/tests/test_demo.py::test_demo"],
                    "stdout_tail": "ION/04_packages/kernel/demo.py referenced",
                },
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_claim": False,
                "secrets_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    graph = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="receipt_graph",
        args={"receipt_dir": "ION/05_context/current/runtime_services/test_run_receipts", "limit": 5},
        expected_route_schema_version="v0",
    )
    blocked = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="receipt_graph",
        args={"receipt_dir": "README.md"},
        expected_route_schema_version="v0",
    )

    assert graph["ok"] is True
    assert graph["mutates_active_state"] is False
    result = graph["delegated_result"]
    assert result["ok"] is True
    assert result["processed_receipts"] == 1
    assert result["content_returned"] == "summary_only"
    assert result["arbitrary_shell_authority"] is False
    assert result["exec_indexed_code"] is False
    assert result["network_authority"] is False
    node_ids = {node["id"] for node in result["nodes"]}
    assert "suite:demo_suite" in node_ids
    assert "intent:demo-key" in node_ids
    assert f"receipt:{receipt.relative_to(root).as_posix()}" in node_ids
    assert "test:ION/tests/test_demo.py::test_demo" in node_ids
    assert "file:ION/04_packages/kernel/demo.py" in node_ids
    assert any(edge["from"] == "suite:demo_suite" and edge["kind"] == "has_receipt" for edge in result["edges"])
    assert any(edge["from"] == "intent:demo-key" and edge["kind"] == "produced_receipt" for edge in result["edges"])
    assert any(edge["kind"] == "covers_test" for edge in result["edges"])
    assert any(edge["kind"] == "references_path" for edge in result["edges"])
    assert blocked["ok"] is False
    assert blocked["delegated_result"]["refusal_class"] == "PATH_NOT_ALLOWED"


def test_local_intelligence_local_search_plus_finds_symbols_schema_and_paths(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    kernel_dir = root / "ION/04_packages/kernel"
    cartography_dir = root / "ION/05_context/current/action_surface_cartography"
    kernel_dir.mkdir(parents=True, exist_ok=True)
    cartography_dir.mkdir(parents=True, exist_ok=True)
    (kernel_dir / "search_plus_demo.py").write_text(
        "def search_plus_target_symbol():\n"
        "    return 'ION/05_context/current/action_surface_cartography/search_plus_profile.md'\n",
        encoding="utf-8",
    )
    (cartography_dir / "search_plus_profile.md").write_text(
        "---\nschema_id: ion.search.plus.demo\n---\n# Search Plus Demo\nSee ION/04_packages/kernel/search_plus_demo.py\n",
        encoding="utf-8",
    )

    symbol_search = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="local_search_plus",
        args={"root_path": "ION/04_packages/kernel", "query": "search_plus_target", "max_files": 20},
        expected_route_schema_version="v0",
    )
    schema_search = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="local_search_plus",
        args={"root_path": "ION/05_context/current/action_surface_cartography", "query": "ion.search.plus.demo", "max_files": 20},
        expected_route_schema_version="v0",
    )
    blocked_query = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="local_search_plus",
        args={"root_path": "ION/04_packages/kernel", "query": ""},
        expected_route_schema_version="v0",
    )
    blocked_path = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="local_search_plus",
        args={"root_path": "README.md", "query": "anything"},
        expected_route_schema_version="v0",
    )

    assert symbol_search["ok"] is True
    symbol_result = symbol_search["delegated_result"]
    assert symbol_result["ok"] is True
    assert symbol_result["content_returned"] == "snippets_only"
    assert symbol_result["arbitrary_shell_authority"] is False
    assert symbol_result["exec_indexed_code"] is False
    assert symbol_result["network_authority"] is False
    symbol_hit_file = next(item for item in symbol_result["results"] if item["path"].endswith("search_plus_demo.py"))
    assert symbol_hit_file["symbol_hits"][0]["symbol"] == "search_plus_target_symbol"
    assert symbol_hit_file["line_hit_count"] >= 1
    assert schema_search["ok"] is True
    schema_result = schema_search["delegated_result"]
    schema_hit_file = next(item for item in schema_result["results"] if item["path"].endswith("search_plus_profile.md"))
    assert "ion.search.plus.demo" in schema_hit_file["schema_ids"]
    assert "ION/04_packages/kernel/search_plus_demo.py" in schema_hit_file["path_refs"]
    assert blocked_query["ok"] is False
    assert blocked_query["delegated_result"]["refusal_class"] == "SCHEMA_INVALID"
    assert blocked_path["ok"] is False
    assert blocked_path["delegated_result"]["refusal_class"] == "PATH_NOT_ALLOWED"


def test_local_and_large_intelligence_share_domain_weaver_read_root_without_secret_access(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    swarm_dir = root / "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns"
    archaeology_dir = root / "ION/05_context/current/domain_weaver/temporal_scheduler_master_index_archaeology"
    sensitive_dir = root / "ION/05_context/current/domain_weaver/.codex"
    secret_dir = root / "ION/05_context/current/domain_weaver/secrets"
    swarm_dir.mkdir(parents=True, exist_ok=True)
    archaeology_dir.mkdir(parents=True, exist_ok=True)
    sensitive_dir.mkdir(parents=True, exist_ok=True)
    secret_dir.mkdir(parents=True, exist_ok=True)
    swarm_artifact = swarm_dir / "swarm_control_plane_steward.return.candidate.md"
    archaeology_artifact = archaeology_dir / "DOMAIN_WEAVER_TEMPORAL_SCHEDULER_MASTER_INDEX_ARCHAEOLOGY_CONSOLIDATION.latest.md"
    swarm_artifact.write_text(
        "# Swarm Return\n\nschema_id: ion.domain_weaver.wave0\n\nWAVE0_BATCH_A_RETURN_NEEDLE\n",
        encoding="utf-8",
    )
    archaeology_artifact.write_text(
        "# Archaeology\n\nschema_id: ion.domain_weaver.archaeology\n\nARCHAEOLOGY_INDEX_NEEDLE\n",
        encoding="utf-8",
    )
    (sensitive_dir / "config.toml").write_text("token = 'not-returned'\n", encoding="utf-8")
    (secret_dir / "token.txt").write_text("TOKEN=not-returned\n", encoding="utf-8")

    swarm_search = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="local_search_plus",
        args={
            "root_path": "ION/05_context/current/domain_weaver/swarm_expansion",
            "query": "WAVE0_BATCH_A_RETURN_NEEDLE",
            "max_files": 20,
        },
        expected_route_schema_version="v0",
    )
    archaeology_search = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="local_search_plus",
        args={
            "root_path": "ION/05_context/current/domain_weaver/temporal_scheduler_master_index_archaeology",
            "query": "ARCHAEOLOGY_INDEX_NEEDLE",
            "max_files": 20,
        },
        expected_route_schema_version="v0",
    )
    large_profile = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_profile",
        args={"path": "ION/05_context/current/domain_weaver/temporal_scheduler_master_index_archaeology/DOMAIN_WEAVER_TEMPORAL_SCHEDULER_MASTER_INDEX_ARCHAEOLOGY_CONSOLIDATION.latest.md"},
        expected_route_schema_version="v0",
    )
    large_slice = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_slice_read",
        args={
            "path": "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns/swarm_control_plane_steward.return.candidate.md",
            "start_line": 1,
            "line_count": 5,
        },
        expected_route_schema_version="v0",
    )
    blocked_local_sensitive = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="local_search_plus",
        args={
            "root_path": "ION/05_context/current/domain_weaver/.codex/config.toml",
            "query": "token",
        },
        expected_route_schema_version="v0",
    )
    blocked_large_sensitive = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_profile",
        args={"path": "ION/05_context/current/domain_weaver/.codex/config.toml"},
        expected_route_schema_version="v0",
    )
    blocked_large_secret = action_branch_invoke(
        root,
        branch_id="large_artifact_intelligence",
        route_id="large_file_profile",
        args={"path": "ION/05_context/current/domain_weaver/secrets/token.txt"},
        expected_route_schema_version="v0",
    )

    assert swarm_search["ok"] is True
    swarm_result = swarm_search["delegated_result"]
    assert swarm_result["ok"] is True
    assert swarm_result["root_path"] == "ION/05_context/current/domain_weaver/swarm_expansion"
    assert swarm_result["content_returned"] == "snippets_only"
    assert swarm_result["arbitrary_shell_authority"] is False
    assert swarm_result["exec_indexed_code"] is False
    assert swarm_result["network_authority"] is False
    assert any(item["path"].endswith("swarm_control_plane_steward.return.candidate.md") for item in swarm_result["results"])
    assert archaeology_search["ok"] is True
    assert archaeology_search["delegated_result"]["result_count"] == 1
    assert large_profile["ok"] is True
    assert large_profile["delegated_result"]["path"].endswith("DOMAIN_WEAVER_TEMPORAL_SCHEDULER_MASTER_INDEX_ARCHAEOLOGY_CONSOLIDATION.latest.md")
    assert large_profile["delegated_result"]["mutates_active_state"] is False
    assert large_profile["delegated_result"]["accepted_state_claim"] is False
    assert large_profile["delegated_result"]["secrets_authority"] is False
    assert large_slice["ok"] is True
    assert "WAVE0_BATCH_A_RETURN_NEEDLE" in large_slice["delegated_result"]["content"]
    assert large_slice["delegated_result"]["mutates_active_state"] is False
    assert large_slice["delegated_result"]["accepted_state_claim"] is False
    assert large_slice["delegated_result"]["secrets_authority"] is False
    assert blocked_local_sensitive["ok"] is False
    assert blocked_local_sensitive["delegated_result"]["refusal_class"] == "PATH_NOT_ALLOWED"
    assert blocked_large_sensitive["ok"] is False
    assert blocked_large_sensitive["delegated_result"]["refusal_class"] == "PATH_NOT_ALLOWED"
    assert blocked_large_secret["ok"] is False
    assert blocked_large_secret["delegated_result"]["refusal_class"] == "PATH_NOT_ALLOWED"


def test_local_intelligence_domain_weaver_swarm_expansion_index_is_monitor_friendly(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    base = root / "ION/05_context/current/domain_weaver/swarm_expansion"
    wave0 = base / "wave0_batch_a"
    plan_dir = wave0 / "relaunch_plan"
    work_packet_dir = wave0 / "work_packets"
    returns_dir = wave0 / "returns"
    launch_receipts_dir = wave0 / "launch_receipts"
    fanin_dir = wave0 / "fanin"
    ladder_dir = base / "durable_carrier_ladder"
    hidden_dir = base / ".codex"
    git_dir = base / ".git"
    secret_dir = base / "secrets"
    for path in (plan_dir, work_packet_dir, returns_dir, launch_receipts_dir, fanin_dir, ladder_dir, hidden_dir, git_dir, secret_dir):
        path.mkdir(parents=True, exist_ok=True)

    expected = [
        "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns/swarm_control_plane_steward.return.candidate.md",
        "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns/worker_shift_lease_marshal.return.candidate.md",
        "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns/browser_gpt_action_gateway_steward.return.candidate.md",
    ]
    (plan_dir / "DOMAIN_WEAVER_WAVE0A_RELAUNCH_PLAN.candidate.md").write_text(
        "# Relaunch Plan\n\n"
        "Expected returns:\n"
        f"- {expected[0]}\n"
        f"- {expected[1]}\n"
        f"- {expected[2]}\n",
        encoding="utf-8",
    )
    (work_packet_dir / "PCKT-DOMAIN-WEAVER-WAVE0A-DURABLE-SWARM-CONTROL-PLANE-STEWARD-V0_1.json").write_text(
        json.dumps({"schema_id": "ion.domain_weaver.work_packet.v0_1", "role": "swarm_control_plane_steward"}),
        encoding="utf-8",
    )
    (returns_dir / "swarm_control_plane_steward.return.candidate.md").write_text(
        "# Return\n\nschema_id: ion.domain_weaver.return\nrole: swarm_control_plane_steward\n",
        encoding="utf-8",
    )
    (returns_dir / "worker_shift_lease_marshal.return.candidate.md").write_text(
        "# Return\n\nschema_id: ion.domain_weaver.return\nrole: worker_shift_lease_marshal\n",
        encoding="utf-8",
    )
    (returns_dir / "unexpected_extra.return.candidate.md").write_text(
        "# Return\n\nschema_id: ion.domain_weaver.return\nrole: unexpected_extra\n",
        encoding="utf-8",
    )
    (launch_receipts_dir / "20260605T000000Z_launch_receipt.json").write_text(
        json.dumps({"schema_id": "ion.domain_weaver.launch_receipt.v0_1", "role": "swarm_control_plane_steward"}),
        encoding="utf-8",
    )
    (fanin_dir / "DOMAIN_WEAVER_WAVE0A_FIRST_THREE_FANIN_SYNTHESIS.candidate.md").write_text(
        "# Fanin\n\nschema_id: ion.domain_weaver.fanin\n",
        encoding="utf-8",
    )
    (ladder_dir / "DURABLE_CARRIER_LADDER.candidate.md").write_text(
        "# Durable Carrier Ladder\n\nschema_id: ion.domain_weaver.durable_carrier_ladder\n",
        encoding="utf-8",
    )
    (hidden_dir / "config.toml").write_text("DONT_READ_SECRET_NEEDLE=hidden\n", encoding="utf-8")
    (git_dir / "config").write_text("DONT_READ_SECRET_NEEDLE=git\n", encoding="utf-8")
    (secret_dir / "token.txt").write_text("DONT_READ_SECRET_NEEDLE=secret\n", encoding="utf-8")
    (base / ".env").write_text("DONT_READ_SECRET_NEEDLE=env\n", encoding="utf-8")

    described = action_branch_describe(root, branch_id="local_intelligence", depth="full")
    indexed = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="domain_weaver_swarm_expansion_index",
        args={"max_files": 50},
        expected_route_schema_version="v0",
    )
    direct_runtime_index = runtime_services.invoke_runtime_service_route(
        root,
        route_id="domain_weaver_swarm_expansion_index",
        args={"root_path": "ION/05_context/current/domain_weaver/swarm_expansion", "max_files": 50},
    )
    child_index = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="domain_weaver_swarm_expansion_index",
        args={"root_path": "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a", "max_files": 50},
        expected_route_schema_version="v0",
    )
    blocked_outside = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="domain_weaver_swarm_expansion_index",
        args={"root_path": "ION/05_context/current/domain_weaver"},
        expected_route_schema_version="v0",
    )
    blocked_hidden_root = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="domain_weaver_swarm_expansion_index",
        args={"root_path": "ION/05_context/current/domain_weaver/swarm_expansion/.codex"},
        expected_route_schema_version="v0",
    )

    assert described["ok"] is True
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert routes["domain_weaver_swarm_expansion_index"]["mutates_state"] is False
    assert routes["domain_weaver_swarm_expansion_index"]["owner_tool"] == "ion_branch_leader_gateway"

    assert indexed["ok"] is True
    assert indexed["mutates_active_state"] is False
    result = indexed["delegated_result"]
    assert direct_runtime_index["ok"] is True
    assert direct_runtime_index["route_id_used"] == "domain_weaver_swarm_expansion_index"
    assert direct_runtime_index["stored_index_written"] is False
    assert direct_runtime_index["mutates_active_state"] is False
    assert direct_runtime_index["accepted_state_claim"] is False
    assert direct_runtime_index["materialization_claim"] is False
    assert result["ok"] is True
    assert result["route_id_used"] == "domain_weaver_swarm_expansion_index"
    assert result["index_route_version"] == "ion.local_intelligence.domain_weaver_swarm_expansion_index.v0_1"
    assert result["root_path"] == "ION/05_context/current/domain_weaver/swarm_expansion"
    assert result["stored_index_written"] is False
    assert result["mutates_active_state"] is False
    assert result["accepted_state_claim"] is False
    assert result["materialization_claim"] is False
    assert result["secrets_authority"] is False
    assert result["secret_content_read"] is False
    assert len(result["manifest_sha256"]) == 64

    entries = {entry["path"]: entry for entry in result["entries"]}
    kinds = {entry["kind"] for entry in result["entries"]}
    assert {"relaunch_plan", "work_packet", "return", "launch_receipt", "fanin", "durable_carrier_ladder"} <= kinds
    return_entry = entries[expected[0]]
    assert return_entry["role"] == "swarm_control_plane_steward"
    assert return_entry["size_bytes"] > 0
    assert len(return_entry["sha256"]) == 64
    assert isinstance(return_entry["mtime_ns"], int)
    assert return_entry["line_count"] >= 1
    assert "ion.domain_weaver.return" in return_entry["schema_ids"]
    assert return_entry["secret_scan_status"] == "not_scanned_by_index_route"
    packet_entry = next(entry for entry in result["entries"] if entry["kind"] == "work_packet")
    assert packet_entry["role"] == "swarm_control_plane_steward"

    wave_summary = result["wave0_batch_a"]
    assert wave_summary["expected_first_three_returns"] == expected
    assert wave_summary["present_expected_returns"] == expected[:2]
    assert wave_summary["missing_expected_returns"] == expected[2:]
    assert wave_summary["unexpected_returns"] == [
        "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns/unexpected_extra.return.candidate.md"
    ]
    assert wave_summary["work_packet_count"] == 1
    assert wave_summary["launch_receipt_count"] == 1
    assert wave_summary["fanin_artifact_count"] == 1
    hidden_paths = {item["path"] for item in wave_summary["hidden_scaffolding_detected"]}
    assert "ION/05_context/current/domain_weaver/swarm_expansion/.codex" in hidden_paths
    assert "ION/05_context/current/domain_weaver/swarm_expansion/.git" in hidden_paths
    assert "ION/05_context/current/domain_weaver/swarm_expansion/secrets" in hidden_paths
    assert "ION/05_context/current/domain_weaver/swarm_expansion/.env" in hidden_paths
    assert "DONT_READ_SECRET_NEEDLE" not in json.dumps(result)

    assert child_index["ok"] is True
    assert child_index["delegated_result"]["root_path"] == "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a"
    assert blocked_outside["ok"] is False
    assert blocked_outside["delegated_result"]["refusal_class"] == "PATH_NOT_ALLOWED"
    assert blocked_hidden_root["ok"] is False
    assert blocked_hidden_root["delegated_result"]["refusal_class"] == "PATH_NOT_ALLOWED"


def test_local_intelligence_context_pack_compile_plus_rehydrates_operation_context(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    context_dir = root / "ION/05_context/current/chatgpt_connector/context_packages"
    receipt_dir = root / "ION/05_context/current/runtime_services/test_run_receipts"
    cartography_dir = root / "ION/05_context/current/action_surface_cartography"
    context_dir.mkdir(parents=True, exist_ok=True)
    receipt_dir.mkdir(parents=True, exist_ok=True)
    cartography_dir.mkdir(parents=True, exist_ok=True)
    (cartography_dir / "context_pack_lexical.md").write_text(
        "---\nschema_id: ion.context.pack.lexical.fixture\n---\n# Context Pack Lexical\n"
        "Context pack lexical digest fixture.\n",
        encoding="utf-8",
    )
    capsule_path = context_dir / "ACTION_EVOLUTION_OPERATION_CONTEXT_CAPSULE_20260602.candidate.yaml"
    state_card_path = context_dir / "ACTION_EVOLUTION_ACTIVE_STATE_CARD.md"
    capsule_path.write_text(
        "schema_id: ion.action_evolution_operation_context_capsule.v0_1_candidate\n"
        "mission_name: ChatGPT-native Action evolution and validation hardening\n"
        "next_recommended_slices:\n"
        "  - id: NEXT-local-intelligence\n",
        encoding="utf-8",
    )
    state_card_path.write_text(
        "# Action Evolution Active State Card\n\n"
        "## Current validation suites\n\n"
        "- local_intelligence_manifest_smoke — 5 passed.\n",
        encoding="utf-8",
    )
    (receipt_dir / "20260602T000000Z_focused_test_run_local_intelligence_manifest_smoke_context-pack-test.json").write_text(
        json.dumps(
            {
                "schema_id": "ion.runtime_focused_test_run_receipt.v0_1",
                "created_at": "2026-06-02T00:00:00+00:00",
                "suite_id": "local_intelligence_manifest_smoke",
                "idempotency_key": "context-pack-test",
                "payload": {
                    "ok": True,
                    "finding": "tests_passed",
                    "returncode": 0,
                    "test_ids": ["ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_local_intelligence_context_pack_compile_plus_rehydrates_operation_context"],
                },
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_claim": False,
                "secrets_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    pack = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="context_pack_compile_plus",
        args={"receipt_limit": 1, "include_route_dag": True, "include_receipt_graph": True, "include_lexical_manifest": True},
        expected_route_schema_version="v0",
    )
    blocked = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="context_pack_compile_plus",
        args={"capsule_path": "README.md"},
        expected_route_schema_version="v0",
    )

    assert pack["ok"] is True
    assert pack["mutates_active_state"] is False
    result = pack["delegated_result"]
    assert result["ok"] is True
    assert result["content_returned"] == "compact_context_pack"
    assert result["capsule"]["ok"] is True
    assert "ChatGPT-native Action evolution" in result["capsule"]["excerpt"]
    assert result["state_card"]["ok"] is True
    assert "local_intelligence_manifest_smoke" in result["state_card"]["excerpt"]
    latest = result["latest_status_by_suite"]["local_intelligence_manifest_smoke"]
    assert latest["ok"] is True
    assert latest["finding"] == "tests_passed"
    assert result["route_dag_summary"]["node_count"] >= 1
    assert result["receipt_graph_summary"]["processed_receipts"] >= 1
    lexical_summary = result["lexical_index_manifest_summary"]
    assert lexical_summary["file_count"] >= 1
    assert len(lexical_summary["manifest_sha256"]) == 64
    assert lexical_summary["content_returned"] == "manifest_only"
    assert lexical_summary["stored_index_written"] is False
    assert lexical_summary["files"]
    assert result["local_intelligence_self_search"]["ok"] is True
    assert result["arbitrary_shell_authority"] is False
    assert result["exec_indexed_code"] is False
    assert result["network_authority"] is False
    assert blocked["ok"] is False
    assert blocked["delegated_result"]["refusal_class"] == "PATH_NOT_ALLOWED"


def test_local_intelligence_lexical_index_manifest_is_read_only_and_deterministic(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    cartography_dir = root / "ION/05_context/current/action_surface_cartography"
    cartography_dir.mkdir(parents=True, exist_ok=True)
    (cartography_dir / "lexical_manifest_demo.md").write_text(
        "---\nschema_id: ion.lexical.demo\n---\n# Lexical Demo\n"
        "Lexical lexical route graph proof. See ION/04_packages/kernel/ion_runtime_service_control.py\n",
        encoding="utf-8",
    )
    (cartography_dir / "lexical_manifest_data.json").write_text(
        json.dumps({"schema_id": "ion.lexical.json", "keywords": ["lexical", "manifest"]}),
        encoding="utf-8",
    )

    manifest = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="lexical_index_manifest",
        args={"root_path": "ION/05_context/current/action_surface_cartography", "max_files": 10, "term_limit": 10},
        expected_route_schema_version="v0",
    )
    blocked = action_branch_invoke(
        root,
        branch_id="local_intelligence",
        route_id="lexical_index_manifest",
        args={"root_path": "README.md"},
        expected_route_schema_version="v0",
    )

    assert manifest["ok"] is True
    assert manifest["mutates_active_state"] is False
    result = manifest["delegated_result"]
    assert result["ok"] is True
    assert result["content_returned"] == "manifest_only"
    assert result["stored_index_written"] is False
    assert result["arbitrary_shell_authority"] is False
    assert result["exec_indexed_code"] is False
    assert result["network_authority"] is False
    assert len(result["manifest_sha256"]) == 64
    paths = {item["path"]: item for item in result["files"]}
    md = paths["ION/05_context/current/action_surface_cartography/lexical_manifest_demo.md"]
    js = paths["ION/05_context/current/action_surface_cartography/lexical_manifest_data.json"]
    assert md["sha256"]
    assert "ion.lexical.demo" in md["schema_ids"]
    assert "Lexical Demo" in md["heading_titles"]
    assert "ION/04_packages/kernel/ion_runtime_service_control.py" in md["path_refs"]
    assert "ion.lexical.json" in js["schema_ids"]
    assert any(item["term"] == "lexical" for item in result["aggregate_top_terms"])
    assert blocked["ok"] is False
    assert blocked["delegated_result"]["refusal_class"] == "PATH_NOT_ALLOWED"


def test_repo_ingest_apply_create_and_readback_are_confirmation_gated(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    target = "ION/05_context/current/action_surface_cartography/REPO_INGEST_BRANCH_SMOKE.candidate.md"
    lease_args = _seed_repo_ingest_edit_lease(
        root,
        path=target,
        mode="artifact",
        agent_id="agent-repo-ingest-create",
        lease_id="lease-repo-ingest-create",
    )

    no_idempotency = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="apply_create",
        args={
            "target_path": target,
            "text": "# Repo Ingest Branch Smoke\n",
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease_args,
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="apply_create",
        args={"target_path": target, "text": "# Repo Ingest Branch Smoke\n", **lease_args},
        idempotency_key="repo-ingest-create-smoke",
        expected_route_schema_version="v0",
    )
    created = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="apply_create",
        args={
            "target_path": target,
            "text": "# Repo Ingest Branch Smoke\n",
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease_args,
        },
        idempotency_key="repo-ingest-create-smoke",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    readback = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="readback",
        args={"path": target, "max_bytes": 2000},
        expected_route_schema_version="v0",
    )

    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"
    assert created["ok"] is True
    assert created["mutates_active_state"] is True
    assert (root / target).is_file()
    assert readback["ok"] is True
    assert readback["mutates_active_state"] is False
    assert readback["delegated_result"]["data"]["text"] == "# Repo Ingest Branch Smoke\n"
    assert readback["delegated_result"]["data"]["path"] == target


def test_repo_ingest_artifact_upload_branch_routes_require_idempotency(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    target = "ION/05_context/current/chatgpt_connector/artifacts/branch-upload.bin"
    data = b"branch-upload-payload"
    expected = hashlib.sha256(data).hexdigest()
    lease_args = _seed_repo_ingest_edit_lease(
        root,
        path=target,
        mode="artifact",
        agent_id="agent-repo-ingest-upload",
        lease_id="lease-repo-ingest-upload",
    )

    init_args = {
        "artifact_name": "branch-upload.bin",
        "target_path": target,
        "expected_sha256": expected,
        "total_bytes": len(data),
        "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
        **lease_args,
    }
    no_init_idempotency = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="artifact_upload_init",
        args=init_args,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    init = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="artifact_upload_init",
        args=init_args,
        idempotency_key="repo-ingest-upload-init",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    upload_id = init["delegated_result"]["data"]["upload_id"]

    chunk_args = {
        "upload_id": upload_id,
        "chunk_index": 0,
        "data_base64": base64.b64encode(data).decode("ascii"),
        "chunk_sha256": expected,
        "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
        **lease_args,
    }
    no_chunk_idempotency = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="artifact_upload_chunk",
        args=chunk_args,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    chunk = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="artifact_upload_chunk",
        args=chunk_args,
        idempotency_key="repo-ingest-upload-chunk-0",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    commit_args = {
        "upload_id": upload_id,
        "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
        **lease_args,
    }
    no_commit_idempotency = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="artifact_upload_commit",
        args=commit_args,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    commit = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="artifact_upload_commit",
        args=commit_args,
        idempotency_key="repo-ingest-upload-commit",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert no_init_idempotency["ok"] is False
    assert no_init_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert init["ok"] is True
    assert no_chunk_idempotency["ok"] is False
    assert no_chunk_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert chunk["ok"] is True
    assert no_commit_idempotency["ok"] is False
    assert no_commit_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert commit["ok"] is True
    assert commit["delegated_result"]["data"]["sha256"] == expected
    assert (root / target).read_bytes() == data


def test_repo_ingest_patch_preview_apply_and_readback_smoke(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    target = "ION/05_context/current/action_surface_cartography/REPO_INGEST_PATCH_TARGET.txt"
    target_path = root / target
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text("alpha\n", encoding="utf-8")
    lease_args = _seed_repo_ingest_edit_lease(
        root,
        path=target,
        mode="exclusive_write",
        agent_id="agent-repo-ingest-patch",
        lease_id="lease-repo-ingest-patch",
    )

    preview = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="preview_patch",
        args={"path": target, "old_text": "alpha\n", "new_text": "beta\n"},
        expected_route_schema_version="v0",
    )
    no_idempotency = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="apply_patch",
        args={
            "path": target,
            "old_text": "alpha\n",
            "new_text": "beta\n",
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease_args,
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="apply_patch",
        args={"path": target, "old_text": "alpha\n", "new_text": "beta\n", **lease_args},
        idempotency_key="repo-ingest-patch-smoke",
        expected_route_schema_version="v0",
    )
    applied = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="apply_patch",
        args={
            "path": target,
            "old_text": "alpha\n",
            "new_text": "beta\n",
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease_args,
        },
        idempotency_key="repo-ingest-patch-smoke",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    readback = action_branch_invoke(
        root,
        branch_id="repo_ingest",
        route_id="readback",
        args={"path": target, "max_bytes": 2000},
        expected_route_schema_version="v0",
    )

    assert preview["ok"] is True
    assert preview["mutates_active_state"] is False
    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"
    assert applied["ok"] is True
    assert applied["mutates_active_state"] is True
    assert target_path.read_text(encoding="utf-8") == "beta\n"
    assert readback["ok"] is True
    assert readback["mutates_active_state"] is False
    assert readback["delegated_result"]["data"]["text"] == "beta\n"


def test_connector_exposes_branch_leader_tools_and_read_only_invoke():
    manifest = call_chatgpt_connector_tool(Path.cwd(), "ion_tool_manifest", {})
    branch_list = call_chatgpt_connector_tool(Path.cwd(), "ion_action_branch_list", {})
    invoke = call_chatgpt_connector_tool(
        Path.cwd(),
        "ion_action_branch_invoke",
        {
            "branch_id": "gateway_core",
            "route_id": "health",
            "expected_route_schema_version": "v0",
        },
    )

    assert {"ion_action_branch_list", "ion_action_branch_describe", "ion_action_branch_receipts"} <= STATUS_READ_TOOLS
    assert "ion_action_branch_invoke" in BOUNDED_QUEUE_RECEIPT_TOOLS
    assert "ion_action_branch_list" in manifest["data"]["allowed_tools"]
    assert branch_list["ok"] is True
    assert branch_list["data"]["ok"] is True
    assert invoke["ok"] is True
    assert invoke["mutates_active_state"] is False
    assert invoke["data"]["delegated_result"]["ok"] is True


def test_http_mcp_branch_invoke_read_only_does_not_require_confirmation():
    response = handle_mcp_jsonrpc(
        Path.cwd(),
        {
            "jsonrpc": "2.0",
            "id": "branch-read",
            "method": "tools/call",
            "params": {
                "name": "ion_action_branch_invoke",
                "arguments": {
                    "branch_id": "gateway_core",
                    "route_id": "health",
                    "expected_route_schema_version": "v0",
                },
            },
        },
    )

    assert response is not None
    structured = response["result"]["structuredContent"]
    assert structured["ok"] is True
    assert structured["mutates_active_state"] is False


def test_branch_invoke_project_file_slice_forwards_line_args(monkeypatch, tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    cosmos = tmp_path / "cosmos"
    (cosmos / "src").mkdir(parents=True)
    (cosmos / "src/Lines.txt").write_text("alpha\nbeta\ngamma\ndelta\n", encoding="utf-8")
    monkeypatch.setenv("ION_COSMOS_PROJECT_ROOT", cosmos.as_posix())
    lease_args = _seed_project_workbench_edit_lease(
        root,
        path="src/Lines.txt",
        lease_id="lease-cosmos-lines",
    )

    result = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="file_slice_read",
        args={"project_id": "cosmos", "path": "src/Lines.txt", "start_line": 2, "line_count": 2},
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["owner_tool"] == "ion_project_file_slice_read"
    delegated = result["delegated_result"]
    assert delegated["ok"] is True
    assert delegated["data"]["mode"] == "line"
    assert delegated["data"]["text"] == "beta\ngamma\n"


def test_project_workbench_file_slice_missing_path_is_classified(monkeypatch, tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    cosmos = tmp_path / "cosmos"
    (cosmos / "src").mkdir(parents=True)
    monkeypatch.setenv("ION_COSMOS_PROJECT_ROOT", cosmos.as_posix())

    result = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="file_slice_read",
        args={"project_id": "cosmos", "path": "src/Missing.txt", "start_line": 1, "line_count": 2},
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["owner_tool"] == "ion_project_file_slice_read"
    assert result["mutates_active_state"] is False
    delegated = result["delegated_result"]
    assert delegated["ok"] is False
    assert delegated["finding"] == "project_path_missing"
    assert delegated["data"]["path"] == "src/Missing.txt"
    assert delegated["mutates_active_state"] is False
    assert delegated["production_authority"] is False
    assert delegated["live_execution_authority"] is False


def _seed_project_workbench_edit_lease(
    root: Path,
    *,
    project_id: str = "cosmos",
    path: str = "src/App.tsx",
    agent_id: str = "agent-cosmos",
    lease_id: str = "lease-cosmos-app",
) -> dict[str, str]:
    import json
    from datetime import datetime, timezone

    board_path = root / "ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json"
    board_path.parent.mkdir(parents=True, exist_ok=True)
    lease_path = f"project_workbench/{project_id}/{path}"
    board_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.worker_shift_board.v0_1",
                "active_shifts": [],
                "active_leases": [
                    {
                        "lease_id": lease_id,
                        "worker_id": agent_id,
                        "identity_binding_status": "bound",
                        "mode": "exclusive_write",
                        "lease_type": "exclusive_write",
                        "paths": [lease_path],
                        "raw_paths": [lease_path],
                        "claimed_at": datetime.now(timezone.utc).isoformat(),
                        "status": "ACTIVE",
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"agent_id": agent_id, "lease_id": lease_id}


def _seed_repo_ingest_edit_lease(
    root: Path,
    *,
    path: str,
    mode: str,
    agent_id: str,
    lease_id: str,
) -> dict[str, str]:
    import json
    from datetime import datetime, timezone

    board_path = root / "ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json"
    board_path.parent.mkdir(parents=True, exist_ok=True)
    board_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.worker_shift_board.v0_1",
                "active_shifts": [],
                "active_leases": [
                    {
                        "lease_id": lease_id,
                        "worker_id": agent_id,
                        "identity_binding_status": "bound",
                        "mode": mode,
                        "lease_type": mode,
                        "paths": [path],
                        "raw_paths": [path],
                        "claimed_at": datetime.now(timezone.utc).isoformat(),
                        "status": "ACTIVE",
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"agent_id": agent_id, "lease_id": lease_id}


def test_project_workbench_patch_preview_apply_and_replay_branch_smoke(monkeypatch, tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    cosmos = tmp_path / "cosmos"
    (cosmos / "src").mkdir(parents=True)
    target = cosmos / "src/App.tsx"
    target.write_text("export const VALUE = 1;\n", encoding="utf-8")
    monkeypatch.setenv("ION_COSMOS_PROJECT_ROOT", cosmos.as_posix())
    lease_args = _seed_project_workbench_edit_lease(root)
    operations = [
        {
            "path": "src/App.tsx",
            "old_text": "export const VALUE = 1;\n",
            "new_text": "export const VALUE = 2;\n",
        }
    ]

    preview = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="patch_preview",
        args={"project_id": "cosmos", "operations": operations},
        expected_route_schema_version="v0",
    )
    no_idempotency = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="patch_apply",
        args={
            "project_id": "cosmos",
            "operations": operations,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease_args,
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="patch_apply",
        args={"project_id": "cosmos", "operations": operations, **lease_args},
        idempotency_key="project-workbench-patch-smoke",
        expected_route_schema_version="v0",
    )
    applied = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="patch_apply",
        args={
            "project_id": "cosmos",
            "operations": operations,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease_args,
        },
        idempotency_key="project-workbench-patch-smoke",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    replay = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="patch_apply",
        args={
            "project_id": "cosmos",
            "operations": operations,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease_args,
        },
        idempotency_key="project-workbench-patch-smoke",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert preview["ok"] is True
    assert preview["mutates_active_state"] is False
    assert preview["owner_tool"] == "ion_project_patch_preview"
    assert "-export const VALUE = 1;" in preview["delegated_result"]["data"]["previews"][0]["diff"]
    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"
    assert applied["ok"] is True
    assert applied["mutates_active_state"] is True
    assert applied["owner_tool"] == "ion_project_patch_apply"
    assert target.read_text(encoding="utf-8") == "export const VALUE = 2;\n"
    assert replay["ok"] is True
    assert replay["delegated_result"]["data"]["idempotent_replay"] is True


def test_project_workbench_branch_file_read_slice_patch_preview_and_gates(monkeypatch, tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    cosmos = tmp_path / "cosmos"
    (cosmos / "src").mkdir(parents=True)
    (cosmos / "src/App.tsx").write_text("export const VALUE = 1;\n", encoding="utf-8")
    (cosmos / "src/Lines.txt").write_text("alpha\nbeta\ngamma\ndelta\n", encoding="utf-8")
    (cosmos / "package.json").write_text('{"scripts":{"build":"vite build"}}\n', encoding="utf-8")
    monkeypatch.setenv("ION_COSMOS_PROJECT_ROOT", cosmos.as_posix())
    lease_args = _seed_project_workbench_edit_lease(root)
    operations = [
        {
            "path": "src/App.tsx",
            "old_text": "export const VALUE = 1;\n",
            "new_text": "export const VALUE = 2;\n",
        }
    ]

    read = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="file_read",
        args={"project_id": "cosmos", "path": "src/App.tsx"},
        expected_route_schema_version="v0",
    )
    sliced = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="file_slice_read",
        args={"project_id": "cosmos", "path": "src/Lines.txt", "start_line": 2, "line_count": 2},
        expected_route_schema_version="v0",
    )
    blocked_path = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="file_read",
        args={"project_id": "cosmos", "path": ".env"},
        expected_route_schema_version="v0",
    )
    preview = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="patch_preview",
        args={"project_id": "cosmos", "operations": operations},
        expected_route_schema_version="v0",
    )
    no_idempotency = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="patch_apply",
        args={
            "project_id": "cosmos",
            "operations": operations,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease_args,
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="patch_apply",
        args={"project_id": "cosmos", "operations": operations, **lease_args},
        idempotency_key="project-workbench-branch-smoke",
        expected_route_schema_version="v0",
    )

    assert read["ok"] is True
    assert read["mutates_active_state"] is False
    assert read["owner_tool"] == "ion_project_file_read"
    assert "VALUE = 1" in read["delegated_result"]["data"]["text"]
    assert sliced["ok"] is True
    assert sliced["mutates_active_state"] is False
    assert sliced["delegated_result"]["data"]["mode"] == "line"
    assert sliced["delegated_result"]["data"]["text"] == "beta\ngamma\n"
    assert blocked_path["ok"] is True
    assert blocked_path["delegated_result"]["ok"] is False
    assert blocked_path["delegated_result"]["finding"] == "project_path_contains_forbidden_part"
    assert preview["ok"] is True
    assert preview["mutates_active_state"] is False
    assert preview["owner_tool"] == "ion_project_patch_preview"
    assert "-export const VALUE = 1;" in preview["delegated_result"]["data"]["previews"][0]["diff"]
    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"
    assert (cosmos / "src/App.tsx").read_text(encoding="utf-8") == "export const VALUE = 1;\n"


def test_project_workbench_slice_preview_and_patch_gates(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    cosmos = tmp_path / "cosmos"
    (cosmos / "src").mkdir(parents=True)
    (cosmos / "src/Lines.txt").write_text("alpha\nbeta\ngamma\ndelta\n", encoding="utf-8")
    monkeypatch.setenv("ION_COSMOS_PROJECT_ROOT", cosmos.as_posix())
    lease_args = _seed_project_workbench_edit_lease(
        root,
        path="src/Lines.txt",
        lease_id="lease-cosmos-lines-patch",
    )

    read = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="file_read",
        args={"project_id": "cosmos", "path": "src/Lines.txt", "max_bytes": 100},
        expected_route_schema_version="v0",
    )
    slice_read = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="file_slice_read",
        args={"project_id": "cosmos", "path": "src/Lines.txt", "start_line": 2, "line_count": 2},
        expected_route_schema_version="v0",
    )
    preview = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="patch_preview",
        args={
            "project_id": "cosmos",
            "operations": [{"path": "src/Lines.txt", "old_text": "beta\n", "new_text": "BETA\n"}],
        },
        expected_route_schema_version="v0",
    )
    no_idempotency = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="patch_apply",
        args={
            "project_id": "cosmos",
            "operations": [{"path": "src/Lines.txt", "old_text": "beta\n", "new_text": "BETA\n"}],
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease_args,
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="patch_apply",
        args={
            "project_id": "cosmos",
            "operations": [{"path": "src/Lines.txt", "old_text": "beta\n", "new_text": "BETA\n"}],
            **lease_args,
        },
        idempotency_key="project-workbench-smoke",
        expected_route_schema_version="v0",
    )
    blocked_path = action_branch_invoke(
        root,
        branch_id="project_workbench",
        route_id="file_read",
        args={"project_id": "cosmos", "path": "../outside.txt"},
        expected_route_schema_version="v0",
    )

    assert read["ok"] is True
    assert read["mutates_active_state"] is False
    assert read["owner_tool"] == "ion_project_file_read"
    assert read["delegated_result"]["data"]["text"] == "alpha\nbeta\ngamma\ndelta\n"
    assert slice_read["ok"] is True
    assert slice_read["mutates_active_state"] is False
    assert slice_read["delegated_result"]["data"]["mode"] == "line"
    assert slice_read["delegated_result"]["data"]["text"] == "beta\ngamma\n"
    assert preview["ok"] is True
    assert preview["mutates_active_state"] is False
    assert preview["owner_tool"] == "ion_project_patch_preview"
    assert preview["delegated_result"]["data"]["schema_id"] == "ion.project_patch_preview.v1"
    assert preview["delegated_result"]["data"]["operation_count"] == 1
    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"
    assert blocked_path["ok"] is True
    assert blocked_path["delegated_result"]["ok"] is False
    assert blocked_path["delegated_result"]["finding"] == "project_path_must_be_relative"


def test_native_ide_status_defaults_to_dist_status(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    runner = root / "ION/05_context/current/chatgpt_connector/scripts/native_ide_control_lane_v7.py"
    runner.parent.mkdir(parents=True)
    runner.write_text(
        "import json, sys\n"
        "print(json.dumps({'argv': sys.argv[1:]}))\n",
        encoding="utf-8",
    )

    result = action_branch_invoke(
        root,
        branch_id="chatgpt_browser_carrier_context",
        route_id="native_ide_status",
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["mutates_active_state"] is False
    delegated = result["delegated_result"]
    assert delegated["ok"] is True
    assert delegated["argv_shape"][-1] == "dist-status"
    assert delegated["stdout_json"]["argv"] == ["dist-status"]
    assert delegated["mutates_state"] is False


def test_native_ide_overlay_routes_target_v4_dist_commands(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    runner = root / "ION/05_context/current/chatgpt_connector/scripts/native_ide_control_lane_v7.py"
    runner.parent.mkdir(parents=True)
    runner.write_text(
        "import json, sys\n"
        "print(json.dumps({'argv': sys.argv[1:]}))\n",
        encoding="utf-8",
    )

    expectations = {
        "native_ide_patch_dry_run": "patch-dist-overlay-dry-run",
        "native_ide_patch_apply": "patch-dist-overlay-apply",
        "native_ide_smoke_source": "smoke-dist-overlay",
        "native_ide_extension_smoke": "smoke-dist-overlay",
    }
    native_apply_target = "browser_extension/ion_chatops_bridge/src/content.ts"

    for route_id, expected_command in expectations.items():
        route_args = {"confirmation": "ION_BOUNDED_WRITE_CONFIRMED"}
        if route_id == "native_ide_patch_apply":
            route_args.update(
                _seed_repo_ingest_edit_lease(
                    root,
                    path=native_apply_target,
                    mode="exclusive_write",
                    agent_id="agent-native-ide",
                    lease_id="lease-native-ide",
                )
            )
            route_args["target_paths"] = [native_apply_target]
        result = action_branch_invoke(
            root,
            branch_id="chatgpt_browser_carrier_context",
            route_id=route_id,
            args=route_args,
            idempotency_key=f"native-ide-v4-alias-{route_id}",
            confirmation="ION_BOUNDED_WRITE_CONFIRMED",
            expected_route_schema_version="v0",
        )

        assert result["ok"] is True
        assert result["mutates_active_state"] is True
        delegated = result["delegated_result"]
        assert delegated["ok"] is True
        assert delegated["argv_shape"][-1] == expected_command
        assert delegated["stdout_json"]["argv"] == [expected_command]
        assert delegated["production_authority"] is False
        assert delegated["live_execution_authority"] is False
        assert delegated["secrets_authority"] is False


def test_native_ide_patch_apply_requires_actor_target_and_edit_lease(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    target = "browser_extension/ion_chatops_bridge/src/content.ts"

    no_actor = action_branch_invoke(
        root,
        branch_id="chatgpt_browser_carrier_context",
        route_id="native_ide_patch_apply",
        args={
            "lease_id": "lease-native-ide",
            "target_paths": [target],
        },
        idempotency_key="native-ide-apply-gate",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    no_target = action_branch_invoke(
        root,
        branch_id="chatgpt_browser_carrier_context",
        route_id="native_ide_patch_apply",
        args={
            "agent_id": "agent-native-ide",
            "lease_id": "lease-native-ide",
        },
        idempotency_key="native-ide-apply-gate",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    no_active_lease = action_branch_invoke(
        root,
        branch_id="chatgpt_browser_carrier_context",
        route_id="native_ide_patch_apply",
        args={
            "agent_id": "agent-native-ide",
            "lease_id": "lease-native-ide",
            "target_paths": [target],
        },
        idempotency_key="native-ide-apply-gate",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert no_actor["ok"] is False
    assert no_actor["refusal_class"] == "ACTOR_PROOF_REQUIRED"
    assert no_target["ok"] is False
    assert no_target["refusal_class"] == "MUTATION_PROOF_REQUIRED"
    assert no_target["required_fields"] == ["target_paths"]
    assert no_active_lease["ok"] is False
    assert no_active_lease["refusal_class"] == "LEASE_REQUIRED"


def test_branch_receipts_delegates_to_receipt_search():
    receipts = action_branch_receipts(Path.cwd(), branch_id="receipts", route_id="search", limit=3)

    assert receipts["ok"] is True
    assert receipts["delegated_result"]["ok"] is True
    assert receipts["delegated_result"]["data"]["limit"] == 3


def test_branch_registry_yaml_has_no_dynamic_function_targets():
    registry = yaml.safe_load(Path(REGISTRY_RELATIVE_PATH).read_text(encoding="utf-8"))
    for branch in registry["branches"]:
        for route in branch.get("routes", []):
            assert "python_function" not in route
            assert "shell" not in route


def _branch_gateway_root(tmp_path: Path) -> Path:
    root = tmp_path / "ion-root"
    (root / "ION/03_registry").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    (root / "README.md").write_text("# Root\n\nRead `ION_CONTEXT_CAPSULE.yaml`.\n", encoding="utf-8")
    (root / "ION_CONTEXT_CAPSULE.yaml").write_text(
        "schema_id: ion.branch_context_node.v0_1\nmaturity_level: B2_capsule_node\n",
        encoding="utf-8",
    )
    registry = Path(REGISTRY_RELATIVE_PATH).read_text(encoding="utf-8")
    (root / REGISTRY_RELATIVE_PATH).write_text(registry, encoding="utf-8")
    return root


def _seed_multi_root_workspace_registry(root: Path, tmp_path: Path) -> dict[str, Path]:
    workspace_parent = tmp_path / "workspace parent"
    codex_store = tmp_path / "codex_home/sessions"
    sandbox_root = tmp_path / "codex_peer_worker_sandboxes"
    workspace_parent.mkdir(parents=True, exist_ok=True)
    codex_store.mkdir(parents=True, exist_ok=True)
    sandbox_root.mkdir(parents=True, exist_ok=True)
    (workspace_parent / "parent_notes.md").write_text(
        "# Parent Root\n\nMULTI_ROOT_NEEDLE lives here.\n",
        encoding="utf-8",
    )
    (codex_store / "session.jsonl").write_text(
        json.dumps({"type": "message", "text": "saved session"}) + "\n",
        encoding="utf-8",
    )
    (sandbox_root / "sandbox_notes.txt").write_text("sandbox write/test lane\n", encoding="utf-8")
    registry = {
        "schema_id": "ion.workspace_root_registry.v1_candidate",
        "status": "test_candidate",
        "default_root_id": "active_ion_control",
        "roots": [
            {
                "root_id": "active_ion_control",
                "label": "Active ION control root",
                "absolute_path": root.as_posix(),
                "root_class": "active_ion_control_root",
                "allowed_operations": ["read", "search", "profile", "spawn_agent", "write_candidate", "run_tests"],
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
                "path_exclusions": [".git", ".env", "__pycache__"],
                "proof_requirements": ["root_id", "cwd", "authority_flags", "non_claims"],
            },
            {
                "root_id": "ion_workspace_parent",
                "label": "Workspace parent",
                "absolute_path": workspace_parent.as_posix(),
                "root_class": "workspace_parent_root",
                "allowed_operations": ["read", "search", "profile", "spawn_agent"],
                "forbidden_operations": ["write_candidate", "run_tests", "run_shell", "git_push", "deletion", "secrets", "accepted_state", "production"],
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
                "path_exclusions": [".git", ".env", "__pycache__"],
                "proof_requirements": ["root_id", "cwd", "authority_flags", "non_claims"],
            },
            {
                "root_id": "codex_session_store",
                "label": "Codex session store",
                "absolute_path": codex_store.as_posix(),
                "root_class": "codex_session_store_root",
                "allowed_operations": ["read", "search", "profile"],
                "forbidden_operations": ["spawn_agent", "write_candidate", "run_tests", "run_shell", "git_push", "deletion", "secrets", "accepted_state", "production"],
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
                "path_exclusions": ["auth.json", "config.toml", ".env"],
                "proof_requirements": ["root_id", "bounded_read", "redaction", "non_claims"],
            },
            {
                "root_id": "codex_peer_worker_sandbox_root",
                "label": "Codex peer worker sandbox",
                "absolute_path": sandbox_root.as_posix(),
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
                "path_exclusions": [".git", ".env", "__pycache__"],
                "proof_requirements": ["root_id", "cwd", "sandbox_path", "authority_flags", "non_claims"],
            },
        ],
    }
    (root / "ION/03_registry/ion_workspace_root_registry.yaml").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return {"workspace_parent": workspace_parent, "codex_store": codex_store, "sandbox_root": sandbox_root}


def _multi_root_safe_idempotency_key(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"{value[:80]}_{digest}"


def _signon_multi_root_worker(root: Path) -> str:
    signon = write_signon_receipt(
        root=root,
        identity={
            "worker_id": "codex_cli:multi-root-workspace-test:20260604:001",
            "display_callsign": "Codex / MultiRootGate / Domain-Weaver",
        },
        carrier_type="codex_cli",
        role_hint="MultiRootGate",
        domain_hint="Domain-Weaver",
        current_objective="multi-root workspace mutation gate proof",
        likely_touched_paths=["ION/04_packages/kernel/ion_multi_root_workspace.py"],
    )
    return signon["receipt"]["worker_id"]


def _claim_multi_root_lease(root: Path, *, worker_id: str, lease_id: str, lease_type: str, paths: list[str]) -> None:
    claim_work_lease(
        root=root,
        worker_id=worker_id,
        lease_id=lease_id,
        lease_type=lease_type,
        paths=paths,
        objective="multi-root workspace mutation gate proof",
        branch_id="multi_root_workspace",
    )


def test_multi_root_workspace_registered_roots_load_and_routes_visible(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    _seed_multi_root_workspace_registry(root, tmp_path)

    described = action_branch_describe(root, branch_id="multi_root_workspace", depth="full")
    result = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_registry",
        expected_route_schema_version="v0",
    )

    assert described["ok"] is True
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert {
        "root_registry",
        "root_status",
        "root_register_preview",
        "root_register",
        "root_discovery_preview",
        "root_file_profile",
        "root_file_slice",
        "root_search",
        "root_agent_spawn_preview",
        "root_agent_spawn",
        "root_command_preview",
        "root_command_run",
        "root_receipts",
    } <= set(routes)
    assert routes["root_agent_spawn"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert routes["root_agent_spawn"]["idempotency_required"] is True
    assert "exclusive_write_lease_over_spawn_run" in routes["root_agent_spawn"]["proof_requirements"]
    assert "exclusive_write_lease_over_command_cwd" in routes["root_command_run"]["proof_requirements"]
    assert routes["root_register"]["edit_lease_required"] is True
    assert routes["root_register"]["agent_id_required"] is True
    assert routes["root_register"]["lease_id_required"] is True
    assert routes["root_register"]["lease_gate"]["required_lease_type"] == "exclusive_write"
    assert routes["root_register"]["lease_gate"]["target_path"] == "ION/03_registry/ion_workspace_root_registry.yaml"
    assert routes["root_register"]["lease_gate_public"]["central_active_lease_validation"] is True
    assert routes["root_register"]["lease_gate_public"]["handler_dynamic_target_gate_deferred"] is False
    assert routes["root_agent_spawn"]["edit_lease_required"] is True
    assert routes["root_agent_spawn"]["agent_id_required"] is True
    assert routes["root_agent_spawn"]["lease_id_required"] is True
    assert routes["root_agent_spawn"]["lease_gate"]["required_lease_type"] == "exclusive_write"
    assert routes["root_agent_spawn"]["lease_gate"]["target_path_template"].endswith(
        "spawn_runs/{root_id}/{safe_idempotency_key}"
    )
    assert routes["root_agent_spawn"]["required_mutation_fields"] == [
        "idempotency_key",
        "confirmation",
        "agent_id",
        "lease_id",
    ]
    assert routes["root_agent_spawn"]["lease_gate_public"]["central_active_lease_validation"] is True
    assert routes["root_agent_spawn"]["lease_gate_public"]["handler_dynamic_target_gate_deferred"] is False
    assert routes["root_command_run"]["edit_lease_required"] is True
    assert routes["root_command_run"]["agent_id_required"] is True
    assert routes["root_command_run"]["lease_id_required"] is True
    assert routes["root_command_run"]["lease_gate"]["target_argument"] == "cwd"
    assert routes["root_command_run"]["lease_gate"]["target_derivation"] == "handler_dynamic"
    assert routes["root_command_run"]["lease_gate_public"]["target_derivation"] == "handler_dynamic"
    assert routes["root_command_run"]["lease_gate_public"]["central_active_lease_validation"] is False
    assert routes["root_command_run"]["lease_gate_public"]["handler_dynamic_target_gate_deferred"] is True
    assert (
        routes["root_command_run"]["lease_gate_public"]["central_enforcement"]
        == "actor_and_lease_proof_required_target_validation_deferred_to_handler"
    )
    assert result["ok"] is True
    delegated = result["delegated_result"]
    root_ids = {item["root_id"] for item in delegated["roots"]}
    assert {"active_ion_control", "ion_workspace_parent", "codex_session_store", "codex_peer_worker_sandbox_root"} <= root_ids
    assert all(item["accepted_state_claim"] is False for item in delegated["roots"])


def test_multi_root_workspace_rejects_path_traversal_and_unregistered_root(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    _seed_multi_root_workspace_registry(root, tmp_path)

    traversal = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_file_profile",
        args={"root_id": "ion_workspace_parent", "path": "../outside.txt"},
        expected_route_schema_version="v0",
    )
    missing = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_status",
        args={"root_id": "missing_root"},
        expected_route_schema_version="v0",
    )

    assert traversal["ok"] is False
    assert traversal["delegated_result"]["refusal_class"] == "PATH_NOT_ALLOWED"
    assert missing["ok"] is False
    assert missing["delegated_result"]["refusal_class"] == "ROOT_NOT_REGISTERED"


def test_multi_root_workspace_read_and_search_are_bounded_by_root_id(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    _seed_multi_root_workspace_registry(root, tmp_path)

    profile = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_file_profile",
        args={"root_id": "ion_workspace_parent", "path": "parent_notes.md", "max_bytes": 2000},
        expected_route_schema_version="v0",
    )
    search = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_search",
        args={"root_id": "ion_workspace_parent", "query": "MULTI_ROOT_NEEDLE", "max_files": 5, "max_matches": 5},
        expected_route_schema_version="v0",
    )
    slice_result = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_file_slice",
        args={"root_id": "ion_workspace_parent", "path": "parent_notes.md", "line_count": 2, "max_bytes": 2000},
        expected_route_schema_version="v0",
    )

    assert profile["ok"] is True
    assert profile["delegated_result"]["root_id"] == "ion_workspace_parent"
    assert profile["delegated_result"]["path"] == "parent_notes.md"
    assert search["ok"] is True
    assert search["delegated_result"]["match_count"] == 1
    assert search["delegated_result"]["matches"][0]["path"] == "parent_notes.md"
    assert slice_result["ok"] is True
    assert slice_result["delegated_result"]["returned_line_count"] == 2


def test_multi_root_workspace_read_only_and_sandbox_operation_boundaries(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    paths = _seed_multi_root_workspace_registry(root, tmp_path)

    codex_blocked = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_command_preview",
        args={"root_id": "codex_session_store", "command_argv": ["python3", "-c", "print('no')"]},
        expected_route_schema_version="v0",
    )
    parent_blocked = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_command_preview",
        args={"root_id": "ion_workspace_parent", "command_argv": ["python3", "-c", "print('no')"]},
        expected_route_schema_version="v0",
    )
    sandbox_preview = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_command_preview",
        args={"root_id": "codex_peer_worker_sandbox_root", "cwd": paths["sandbox_root"].as_posix(), "command_argv": ["python3", "-c", "print('ok')"]},
        expected_route_schema_version="v0",
    )
    sandbox_outside = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_command_preview",
        args={"root_id": "codex_peer_worker_sandbox_root", "cwd": paths["workspace_parent"].as_posix(), "command_argv": ["python3", "-c", "print('bad')"]},
        expected_route_schema_version="v0",
    )

    assert codex_blocked["ok"] is False
    assert codex_blocked["delegated_result"]["finding"] == "operation_not_allowed_for_root"
    assert parent_blocked["ok"] is False
    assert parent_blocked["delegated_result"]["finding"] == "operation_not_allowed_for_root"
    assert sandbox_preview["ok"] is True
    assert sandbox_preview["delegated_result"]["would_run"] is True
    assert sandbox_outside["ok"] is False
    assert sandbox_outside["delegated_result"]["refusal_class"] == "PATH_NOT_ALLOWED"


def test_multi_root_workspace_agent_spawn_preview_is_read_only(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    paths = _seed_multi_root_workspace_registry(root, tmp_path)

    preview = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_agent_spawn_preview",
        args={
            "root_id": "ion_workspace_parent",
            "cwd": paths["workspace_parent"].as_posix(),
            "objective": "Inspect sibling workspace without writing.",
            "agent_role": "workspace_scout",
            "model": "gpt-5.5",
            "effort": "high",
            "max_runtime": 300,
        },
        expected_route_schema_version="v0",
    )

    assert preview["ok"] is True
    assert preview["mutates_active_state"] is False
    assert preview["delegated_result"]["would_start_process"] is False
    assert preview["delegated_result"]["spawn_packet_preview"]["root_id"] == "ion_workspace_parent"
    assert not (root / "ION/05_context/current/workspace_roots").exists()


def test_multi_root_workspace_agent_spawn_requires_confirmation_and_idempotency(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    paths = _seed_multi_root_workspace_registry(root, tmp_path)
    args = {
        "root_id": "ion_workspace_parent",
        "cwd": paths["workspace_parent"].as_posix(),
        "objective": "Prepare root-scoped scout packet.",
        "agent_role": "workspace_scout",
    }

    no_idempotency = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_agent_spawn",
        args={**args, "confirmation": "ION_BOUNDED_WRITE_CONFIRMED"},
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_agent_spawn",
        args={**args, "idempotency_key": "multi-root-spawn-missing-confirmation"},
        idempotency_key="multi-root-spawn-missing-confirmation",
        expected_route_schema_version="v0",
    )

    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"


def test_multi_root_workspace_agent_spawn_receipt_contains_root_authority_and_non_claims(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    paths = _seed_multi_root_workspace_registry(root, tmp_path)
    idempotency_key = "multi-root-spawn-receipt-test"
    worker_id = _signon_multi_root_worker(root)
    lease_id = "multi-root-spawn-exclusive-write-lease"
    spawn_target = f"ION/05_context/current/workspace_roots/spawn_runs/ion_workspace_parent/{_multi_root_safe_idempotency_key(idempotency_key)}"
    _claim_multi_root_lease(
        root,
        worker_id=worker_id,
        lease_id=lease_id,
        lease_type="exclusive_write",
        paths=[spawn_target],
    )

    spawned = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_agent_spawn",
        args={
            "root_id": "ion_workspace_parent",
            "cwd": paths["workspace_parent"].as_posix(),
            "objective": "Prepare root-scoped scout packet.",
            "agent_role": "workspace_scout",
            "idempotency_key": idempotency_key,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "agent_id": worker_id,
            "actor_root_id": "active_ion_control",
            "lease_id": lease_id,
        },
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    replay = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_agent_spawn",
        args={
            "root_id": "ion_workspace_parent",
            "cwd": paths["workspace_parent"].as_posix(),
            "objective": "Prepare root-scoped scout packet.",
            "agent_role": "workspace_scout",
            "idempotency_key": idempotency_key,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "agent_id": worker_id,
            "actor_root_id": "active_ion_control",
            "lease_id": lease_id,
        },
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert spawned["ok"] is True
    delegated = spawned["delegated_result"]
    receipt_path = root / delegated["receipt_path"]
    packet_path = root / delegated["spawn_packet_path"]
    task_return_path = root / delegated["task_return_path"]
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    assert receipt["root_id"] == "ion_workspace_parent"
    assert receipt["mutation_proof"]["actor_proof"]["agent_id"] == worker_id
    assert receipt["mutation_proof"]["actor_proof"]["actor_root_id"] == "active_ion_control"
    assert receipt["mutation_proof"]["target_proof"]["target_root_id"] == "ion_workspace_parent"
    assert receipt["mutation_proof"]["lease_proof"]["lease_id"] == lease_id
    assert packet["mutation_proof"]["lease_proof"]["required_lease_type"] == "exclusive_write"
    assert receipt["cwd"] == paths["workspace_parent"].as_posix()
    assert receipt["actual_process_started"] is False
    assert receipt["accepted_state_claim"] is False
    assert receipt["production_authority"] is False
    assert receipt["secrets_authority"] is False
    assert receipt["git_push_authority"] is False
    assert receipt["deletion_authority"] is False
    assert receipt["non_claims"]
    assert packet_path.is_file()
    assert task_return_path.is_file()
    assert replay["ok"] is True
    assert replay["delegated_result"]["idempotent_replay"] is True


def test_multi_root_workspace_agent_spawn_requires_actor_root_and_artifact_lease(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    paths = _seed_multi_root_workspace_registry(root, tmp_path)
    idempotency_key = "multi-root-spawn-proof-required"
    base_args = {
        "root_id": "ion_workspace_parent",
        "cwd": paths["workspace_parent"].as_posix(),
        "objective": "Prepare root-scoped scout packet.",
        "agent_role": "workspace_scout",
        "idempotency_key": idempotency_key,
        "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
    }

    missing_actor = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_agent_spawn",
        args=base_args,
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    worker_id = _signon_multi_root_worker(root)
    spawn_target = f"ION/05_context/current/workspace_roots/spawn_runs/ion_workspace_parent/{_multi_root_safe_idempotency_key(idempotency_key)}"
    missing_lease = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_agent_spawn",
        args={
            **base_args,
            "agent_id": worker_id,
            "actor_root_id": "active_ion_control",
            "lease_id": "missing-artifact-lease",
        },
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert missing_actor["ok"] is False
    assert missing_actor["refusal_class"] == "ACTOR_PROOF_REQUIRED"
    assert "delegated_result" not in missing_actor
    assert missing_lease["ok"] is False
    assert missing_lease["refusal_class"] == "LEASE_REQUIRED"
    assert missing_lease["required_lease_type"] == "exclusive_write"
    assert missing_lease["target_files"][0]["target_path"] == spawn_target
    assert "delegated_result" not in missing_lease


def test_multi_root_workspace_root_register_requires_exclusive_write_lease(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    _seed_multi_root_workspace_registry(root, tmp_path)
    new_root = tmp_path / "new candidate root"
    new_root.mkdir(parents=True)
    worker_id = _signon_multi_root_worker(root)
    idempotency_key = "multi-root-register-proof-required"
    lease_id = "multi-root-register-exclusive-lease"
    base_args = {
        "root_id": "new_candidate_root",
        "label": "New candidate root",
        "absolute_path": new_root.as_posix(),
        "root_class": "external_project_root",
        "allowed_operations": ["read", "search", "profile"],
        "idempotency_key": idempotency_key,
        "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
        "agent_id": worker_id,
        "actor_root_id": "active_ion_control",
        "lease_id": lease_id,
    }

    missing_lease = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_register",
        args=base_args,
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    _claim_multi_root_lease(
        root,
        worker_id=worker_id,
        lease_id=lease_id,
        lease_type="exclusive_write",
        paths=["ION/03_registry/ion_workspace_root_registry.yaml"],
    )
    registered = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_register",
        args=base_args,
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert missing_lease["ok"] is False
    assert missing_lease["refusal_class"] == "LEASE_REQUIRED"
    assert missing_lease["required_lease_type"] == "exclusive_write"
    assert missing_lease["target_files"][0]["target_path"] == "ION/03_registry/ion_workspace_root_registry.yaml"
    assert "delegated_result" not in missing_lease
    assert registered["ok"] is True
    assert registered["delegated_result"]["registered_root"]["root_id"] == "new_candidate_root"
    assert registered["delegated_result"]["mutation_proof"]["target_proof"]["lease_target_paths"] == [
        "ION/03_registry/ion_workspace_root_registry.yaml"
    ]


def test_multi_root_workspace_command_run_requires_exclusive_write_lease(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    paths = _seed_multi_root_workspace_registry(root, tmp_path)
    worker_id = _signon_multi_root_worker(root)
    idempotency_key = "multi-root-command-run-proof-required"

    missing_lease_id = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_command_run",
        args={
            "root_id": "codex_peer_worker_sandbox_root",
            "cwd": paths["sandbox_root"].as_posix(),
            "command_argv": ["python3", "-c", "print('ok')"],
            "idempotency_key": idempotency_key,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "agent_id": worker_id,
            "actor_root_id": "active_ion_control",
        },
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    blocked = action_branch_invoke(
        root,
        branch_id="multi_root_workspace",
        route_id="root_command_run",
        args={
            "root_id": "codex_peer_worker_sandbox_root",
            "cwd": paths["sandbox_root"].as_posix(),
            "command_argv": ["python3", "-c", "print('ok')"],
            "idempotency_key": idempotency_key,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "agent_id": worker_id,
            "actor_root_id": "active_ion_control",
            "lease_id": "missing-command-run-exclusive-lease",
        },
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert missing_lease_id["ok"] is False
    assert missing_lease_id["refusal_class"] == "LEASE_REQUIRED"
    assert missing_lease_id["lease_gate_public"]["handler_dynamic_target_gate_deferred"] is True
    assert "delegated_result" not in missing_lease_id
    assert blocked["ok"] is False
    assert blocked["refusal_class"] == "LEASE_REQUIRED"
    assert blocked["handler_dynamic_target_gate_deferred"]["deferred"] is True
    assert blocked["handler_dynamic_target_gate_deferred"]["central_active_lease_validation"] is False
    assert blocked["handler_dynamic_target_gate_deferred"]["handler_fail_closed_required"] is True
    assert blocked["required_lease_type"] == "exclusive_write"
    assert "delegated_result" in blocked
    assert blocked["delegated_result"]["ok"] is False


def _seed_worker_shift_state(root: Path) -> None:
    write_signon_receipt(
        root=root,
        carrier_type="codex_cli",
        role_hint="WorkerA",
        now="2026-05-15T19:00:00+00:00",
    )
    write_signon_receipt(
        root=root,
        carrier_type="chatgpt_browser",
        role_hint="WorkerB",
        now="2026-05-15T19:01:00+00:00",
    )
    claim_work_lease(
        root=root,
        worker_id="codex_cli:ion-root:20260515:001",
        lease_type="exclusive_write",
        paths=["ION/04_packages/kernel"],
        now="2026-05-15T19:02:00+00:00",
    )
    claim_work_lease(
        root=root,
        worker_id="chatgpt_browser:ion-root:20260515:001",
        lease_type="write_intent",
        paths=["ION/04_packages/kernel/ion_action_mcp_branch_leaders.py"],
        now="2026-05-15T19:03:00+00:00",
    )
    queue_path = root / "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(
        "{\n"
        "  \"schema_id\": \"ion.chatgpt_connector_codex_work_queue.v0\",\n"
        "  \"request_count\": 3,\n"
        "  \"duplicate_group_count\": 1,\n"
        "  \"requests\": [\n"
        "    {\"request_id\": \"r1\", \"status\": \"QUEUED_FOR_CODEX_CARRIER\"},\n"
        "    {\"request_id\": \"r2\", \"status\": \"CLAIMED_BY_CODEX_QUEUE_RUNNER\"},\n"
        "    {\"request_id\": \"r3\", \"status\": \"QUEUED_FOR_CODEX_CARRIER\"}\n"
        "  ]\n"
        "}\n",
        encoding="utf-8",
    )


class _FakeCompleted:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _fake_runtime_services_run(args, check=False, capture_output=True, text=True, timeout=8):  # noqa: ANN001
    unit = ""
    for value in args:
        if isinstance(value, str) and value.startswith("ion-") and value.endswith(".service"):
            unit = value
            break
    if "pytest" in args:
        return _FakeCompleted(0, "focused tests passed", "")
    if "show" in args:
        stdout = (
            f"Id={unit}\n"
            "MainPID=0\n"
            "LoadState=loaded\n"
            "ActiveState=active\n"
            "SubState=running\n"
            f"FragmentPath=/home/sev/.config/systemd/user/{unit}\n"
            "ExecMainStartTimestamp=Fri 2026-05-15 20:00:00 UTC\n"
        )
        return _FakeCompleted(0, stdout, "")
    if "restart" in args:
        return _FakeCompleted(0, "", "")
    return _FakeCompleted(1, "", "unexpected command")


class _FakeHTTPResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:  # noqa: ANN001
        return None

    def read(self, _size: int = -1) -> bytes:
        return b'{"ok": true}'


def _fake_runtime_services_urlopen(request, timeout=1.5):  # noqa: ANN001
    return _FakeHTTPResponse()


CODEX_LIVE_SESSION_TEST_ID = "019e8b2b-c770-71d3-b2d8-e4c1c14eba0b"


def _codex_live_session_args(session_id: str = CODEX_LIVE_SESSION_TEST_ID) -> dict:
    return {
        "session_id": session_id,
        "role_id": "lead_codex_domain_weaver_build_manager",
        "display_name": "Lead Codex Domain Weaver Build Manager",
        "domain_id": "domain.domain_weaver",
        "objective": "Manage Domain Weaver exact-active binding work as candidate state.",
        "current_packet_id": "unknown_current_packet",
        "context_refs": [
            "ION/05_context/current/domain_weaver/stewarded_autonomy/DOMAIN_WEAVER_STEWARDED_AUTONOMY_TRIAL_SETTLEMENT_20260603.md"
        ],
        "evidence_refs": [
            "ION/05_context/current/domain_weaver/live_carrier_binding/ACTIVE_INVOKABLE_BINDING_PROOF_ROWS.candidate.json"
        ],
        "registered_by": "pytest",
        "status": "active",
    }


def _register_codex_live_session(root: Path, session_id: str = CODEX_LIVE_SESSION_TEST_ID):
    return action_branch_invoke(
        root,
        branch_id="codex_live_session_bridge",
        route_id="session_register",
        args=_codex_live_session_args(session_id),
        idempotency_key=f"register-{session_id}",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )


def _codex_live_session_dir(root: Path, session_id: str = CODEX_LIVE_SESSION_TEST_ID) -> Path:
    return root / "ION/05_context/current/chatgpt_connector/codex_live_sessions" / session_id


def test_codex_live_session_register_preview_is_read_only_and_authority_false(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)

    result = action_branch_invoke(
        root,
        branch_id="codex_live_session_bridge",
        route_id="session_register_preview",
        args=_codex_live_session_args(),
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["mutates_active_state"] is False
    delegated = result["delegated_result"]
    assert delegated["would_write"] is False
    assert delegated["accepted_state_claim"] is False
    assert delegated["production_authority"] is False
    assert delegated["live_execution_authority"] is False
    assert delegated["secrets_authority"] is False
    assert not _codex_live_session_dir(root).exists()


def test_codex_live_session_register_writes_session_index_and_receipt(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)

    result = _register_codex_live_session(root)

    assert result["ok"] is True
    assert result["mutates_active_state"] is True
    delegated = result["delegated_result"]
    session_dir = _codex_live_session_dir(root)
    assert (session_dir / "session.json").is_file()
    assert (session_dir / "latest_status.json").is_file()
    assert (session_dir / "receipts/session_register_receipt.json").is_file()
    assert (root / "ION/05_context/current/chatgpt_connector/codex_live_sessions/INDEX.json").is_file()
    session = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))
    index = json.loads((root / "ION/05_context/current/chatgpt_connector/codex_live_sessions/INDEX.json").read_text(encoding="utf-8"))
    assert session["session_id"] == CODEX_LIVE_SESSION_TEST_ID
    assert session["accepted_state_claim"] is False
    assert CODEX_LIVE_SESSION_TEST_ID in index["sessions"]
    assert (root / delegated["receipt_path"]).is_file()


def test_codex_live_session_relay_preview_is_read_only(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    _register_codex_live_session(root)

    result = action_branch_invoke(
        root,
        branch_id="codex_live_session_bridge",
        route_id="relay_enqueue_preview",
        args={
            "session_id": CODEX_LIVE_SESSION_TEST_ID,
            "objective": "Preview relay",
            "message": "Preview only.",
        },
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["mutates_active_state"] is False
    delegated = result["delegated_result"]
    assert delegated["would_append"] is False
    assert delegated["message_payload"]["accepted_state_claim"] is False
    assert not (_codex_live_session_dir(root) / "inbox.jsonl").exists()


def test_codex_live_session_relay_enqueue_appends_once_and_is_idempotent(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    _register_codex_live_session(root)
    args = {
        "session_id": CODEX_LIVE_SESSION_TEST_ID,
        "objective": "Relay smoke",
        "message": "Write durable status only.",
        "expected_response_contract": {"reply_route": "outbox_record"},
        "stop_settlement_condition": "Stop after outbox reply.",
    }

    first = action_branch_invoke(
        root,
        branch_id="codex_live_session_bridge",
        route_id="relay_enqueue",
        args=args,
        idempotency_key="relay-smoke-once",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    second = action_branch_invoke(
        root,
        branch_id="codex_live_session_bridge",
        route_id="relay_enqueue",
        args=args,
        idempotency_key="relay-smoke-once",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    inbox_path = _codex_live_session_dir(root) / "inbox.jsonl"
    assert first["ok"] is True
    assert first["mutates_active_state"] is True
    assert second["ok"] is True
    assert second["mutates_active_state"] is False
    assert second["delegated_result"]["idempotent_replay"] is True
    assert len([line for line in inbox_path.read_text(encoding="utf-8").splitlines() if line.strip()]) == 1
    assert (root / first["delegated_result"]["receipt_path"]).is_file()


def test_codex_live_session_outbox_and_harvest_record_write_receipts(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    _register_codex_live_session(root)

    outbox = action_branch_invoke(
        root,
        branch_id="codex_live_session_bridge",
        route_id="outbox_record",
        args={
            "session_id": CODEX_LIVE_SESSION_TEST_ID,
            "message": "Current status path is ION/05_context/current/example.json.",
            "summary": "Candidate progress only.",
            "evidence_paths": ["ION/05_context/current/example.json"],
        },
        idempotency_key="outbox-smoke",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    harvest = action_branch_invoke(
        root,
        branch_id="codex_live_session_bridge",
        route_id="harvest_record",
        args={
            "session_id": CODEX_LIVE_SESSION_TEST_ID,
            "transcript_excerpt": "Codex reported candidate status only.",
            "summary": "Harvested candidate transcript excerpt.",
            "evidence_paths": ["ION/05_context/current/example.json"],
        },
        idempotency_key="harvest-smoke",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    session_dir = _codex_live_session_dir(root)
    assert outbox["ok"] is True
    assert harvest["ok"] is True
    assert (session_dir / "outbox.jsonl").is_file()
    assert (root / outbox["delegated_result"]["receipt_path"]).is_file()
    assert (root / harvest["delegated_result"]["harvest_path"]).is_file()
    assert (root / harvest["delegated_result"]["receipt_path"]).is_file()


def test_codex_live_session_rejects_unsafe_session_id(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)

    result = action_branch_invoke(
        root,
        branch_id="codex_live_session_bridge",
        route_id="session_register_preview",
        args=_codex_live_session_args("../bad"),
        expected_route_schema_version="v0",
    )

    assert result["ok"] is False
    assert result["refusal_class"] == "SCHEMA_INVALID"
    assert result["finding"] == "unsafe_session_id"


def test_codex_live_session_secret_looking_content_is_redacted_in_receipts(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)
    _register_codex_live_session(root)
    secret = "sk-testsecret1234567890"

    result = action_branch_invoke(
        root,
        branch_id="codex_live_session_bridge",
        route_id="relay_enqueue",
        args={
            "session_id": CODEX_LIVE_SESSION_TEST_ID,
            "objective": "Redaction smoke",
            "message": f"Do not print SECRET_TOKEN={secret} in receipts.",
        },
        idempotency_key="relay-secret-redaction",
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    receipt_text = (root / result["delegated_result"]["receipt_path"]).read_text(encoding="utf-8")
    assert secret not in receipt_text
    assert "***REDACTED***" in receipt_text


def test_codex_live_session_routes_visible_through_action_branch_describe(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)

    described = action_branch_describe(root, branch_id="codex_live_session_bridge", depth="full")

    assert described["ok"] is True
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert {
        "session_register_preview",
        "session_register",
        "session_status",
        "relay_enqueue_preview",
        "relay_enqueue",
        "outbox_record",
        "harvest_record",
        "session_receipts",
    } <= set(routes)
    assert routes["session_register_preview"]["mutates_state"] is False
    assert routes["relay_enqueue_preview"]["mutates_state"] is False
    assert routes["session_register"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert routes["relay_enqueue"]["idempotency_required"] is True


def test_codex_live_session_mutating_routes_require_confirmation_and_idempotency(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)

    no_idempotency = action_branch_invoke(
        root,
        branch_id="codex_live_session_bridge",
        route_id="session_register",
        args=_codex_live_session_args(),
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        root,
        branch_id="codex_live_session_bridge",
        route_id="session_register",
        args=_codex_live_session_args(),
        idempotency_key="register-missing-confirmation",
        expected_route_schema_version="v0",
    )

    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"


CODEX_SESSION_STORE_TEST_ID = "019e8b2b-c770-71d3-b2d8-e4c1c14eba0b"


def _seed_codex_session_store_fixture(tmp_path: Path, monkeypatch, session_id: str = CODEX_SESSION_STORE_TEST_ID) -> Path:
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    store = home / ".codex/sessions/2026/06/02"
    store.mkdir(parents=True, exist_ok=True)
    path = store / f"rollout-2026-06-02T21-49-22-{session_id}.jsonl"
    rows = [
        {
            "timestamp": "2026-06-03T01:50:12.366Z",
            "type": "session_meta",
            "payload": {
                "id": session_id,
                "timestamp": "2026-06-03T01:49:22.691Z",
                "cwd": "/home/sev/ION - Production",
                "originator": "codex-tui",
                "cli_version": "0.136.0",
                "source": "cli",
                "thread_source": "user",
                "model_provider": "openai",
                "base_instructions": {"text": "large prompt omitted by bridge"},
            },
        },
        {
            "timestamp": "2026-06-03T01:51:00.000Z",
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Inspect Domain Weaver status."}],
            },
        },
        {
            "timestamp": "2026-06-03T01:52:00.000Z",
            "type": "event_msg",
            "payload": {
                "type": "agent_message",
                "message": "Candidate only. SECRET_TOKEN=sk-testsecret1234567890 should be redacted.",
            },
        },
        {
            "timestamp": "2026-06-03T01:53:00.000Z",
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Latest status remains candidate-only."}],
            },
        },
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    (home / ".codex/history.jsonl").write_text(json.dumps({"session_id": session_id, "text": "Inspect Domain Weaver status."}) + "\n", encoding="utf-8")
    (home / ".codex/session_index.jsonl").write_text(json.dumps({"id": session_id, "thread_name": "Domain Weaver"}) + "\n", encoding="utf-8")
    return path


def test_codex_session_store_rejects_unsafe_session_ids_and_path_traversal(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    _seed_codex_session_store_fixture(tmp_path, monkeypatch)

    unsafe = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_metadata",
        args={"session_id": "../bad"},
        expected_route_schema_version="v0",
    )
    traversal = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_transcript_slice",
        args={"session_id": "../../.codex/auth.json", "line_count": 1},
        expected_route_schema_version="v0",
    )

    assert unsafe["ok"] is False
    assert unsafe["refusal_class"] == "SCHEMA_INVALID"
    assert unsafe["finding"] == "unsafe_session_id"
    assert traversal["ok"] is False
    assert traversal["finding"] == "unsafe_session_id"


def test_codex_session_store_discovery_is_read_only(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    _seed_codex_session_store_fixture(tmp_path, monkeypatch)

    result = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_store_discovery",
        args={"session_id": CODEX_SESSION_STORE_TEST_ID},
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["mutates_active_state"] is False
    assert result["delegated_result"]["session_found"] is True
    assert result["delegated_result"]["searched_auth_json"] is False
    assert not (root / "ION/05_context/current/chatgpt_connector/codex_session_store_harvests").exists()


def test_codex_session_store_fixture_session_can_be_read_and_bounded(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    fixture = _seed_codex_session_store_fixture(tmp_path, monkeypatch)

    metadata = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_metadata",
        args={"session_id": CODEX_SESSION_STORE_TEST_ID},
        expected_route_schema_version="v0",
    )
    profile = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_transcript_profile",
        args={"session_id": CODEX_SESSION_STORE_TEST_ID},
        expected_route_schema_version="v0",
    )
    bounded = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_transcript_slice",
        args={"session_id": CODEX_SESSION_STORE_TEST_ID, "start_line": 2, "line_count": 1, "max_bytes": 2000},
        expected_route_schema_version="v0",
    )

    assert metadata["ok"] is True
    assert metadata["delegated_result"]["storage_path"] == str(fixture)
    assert metadata["delegated_result"]["session_meta"]["cwd"] == "/home/sev/ION - Production"
    assert profile["delegated_result"]["file_format"] == "codex_rollout_jsonl"
    assert profile["delegated_result"]["message_count"] >= 3
    assert bounded["delegated_result"]["bounded"] is True
    assert bounded["delegated_result"]["returned_record_count"] == 1


def test_codex_session_store_redacts_secret_looking_content(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    _seed_codex_session_store_fixture(tmp_path, monkeypatch)
    secret = "sk-testsecret1234567890"

    result = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_find",
        args={"session_id": CODEX_SESSION_STORE_TEST_ID, "query": "SECRET_TOKEN", "max_matches": 5},
        expected_route_schema_version="v0",
    )

    text = json.dumps(result, sort_keys=True)
    assert result["ok"] is True
    assert result["delegated_result"]["match_count"] == 1
    assert secret not in text
    assert "***REDACTED***" in text


def test_codex_session_store_missing_session_returns_clean_not_found(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    _seed_codex_session_store_fixture(tmp_path, monkeypatch)

    result = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_metadata",
        args={"session_id": "019e0000-0000-7000-8000-000000000000"},
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["delegated_result"]["found"] is False
    assert result["delegated_result"]["finding"] == "session_not_found"


def test_codex_session_store_routes_visible_through_action_branch_describe(tmp_path: Path):
    root = _branch_gateway_root(tmp_path)

    described = action_branch_describe(root, branch_id="codex_session_store", depth="full")

    assert described["ok"] is True
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert {
        "session_store_discovery",
        "session_list",
        "session_metadata",
        "session_transcript_profile",
        "session_transcript_slice",
        "session_find",
        "session_summary",
        "session_resume_command_preview",
        "session_resume_send_preview",
        "session_resume_send",
        "session_resume_status",
        "session_resume_harvest",
        "session_harvest_to_ion",
    } <= set(routes)
    assert routes["session_transcript_slice"]["mutates_state"] is False
    command_props = routes["session_resume_command_preview"]["args_schema"]["properties"]
    assert "sandbox_mode" not in command_props
    assert routes["session_resume_send_preview"]["mutates_state"] is False
    preview_props = routes["session_resume_send_preview"]["args_schema"]["properties"]
    send_props = routes["session_resume_send"]["args_schema"]["properties"]
    assert preview_props["sandbox_mode"]["enum"] == ["read-only", "workspace-write"]
    assert preview_props["driver_mode"]["enum"] == ["exec", "tui_inline"]
    assert send_props["sandbox_mode"]["enum"] == ["read-only", "workspace-write"]
    assert send_props["sandbox"]["enum"] == ["read-only", "workspace-write"]
    assert send_props["driver_mode"]["enum"] == ["exec", "tui_inline"]
    assert routes["session_resume_send"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert routes["session_resume_send"]["idempotency_required"] is True
    assert routes["session_resume_status"]["mutates_state"] is False
    assert routes["session_resume_harvest"]["mutates_state"] is False
    assert routes["session_harvest_to_ion"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert routes["session_harvest_to_ion"]["idempotency_required"] is True


def test_codex_session_resume_send_requires_confirmation_and_idempotency(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    _seed_codex_session_store_fixture(tmp_path, monkeypatch)

    no_idempotency = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_resume_send",
        args={
            "session_id": CODEX_SESSION_STORE_TEST_ID,
            "prompt": "Reply with SESSION_RESUME_BRIDGE_SMOKE_OK and do not mutate files.",
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
        },
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_resume_send",
        args={
            "session_id": CODEX_SESSION_STORE_TEST_ID,
            "prompt": "Reply with SESSION_RESUME_BRIDGE_SMOKE_OK and do not mutate files.",
            "idempotency_key": "resume-send-missing-confirmation",
        },
        idempotency_key="resume-send-missing-confirmation",
        expected_route_schema_version="v0",
    )

    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"


def test_codex_session_resume_send_records_receipt_delta_and_idempotency(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    fixture = _seed_codex_session_store_fixture(tmp_path, monkeypatch)
    prompt = "Reply with SESSION_RESUME_BRIDGE_SMOKE_OK and do not mutate files."
    idempotency_key = "resume-send-smoke-test"

    class FakeCompleted:
        returncode = 0
        stdout = "SESSION_RESUME_BRIDGE_SMOKE_OK\n"
        stderr = ""

    def fake_run(argv, cwd, text, capture_output, timeout, env):
        assert argv[-2] == CODEX_SESSION_STORE_TEST_ID
        assert argv[-1] == prompt
        assert "resume" in argv
        assert cwd
        assert text is True
        assert capture_output is True
        assert timeout == 10
        assert env["TERM"] == "xterm-256color"
        with fixture.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "timestamp": "2026-06-03T15:10:00.000Z",
                        "type": "response_item",
                        "payload": {
                            "role": "assistant",
                            "content": [{"type": "output_text", "text": "SESSION_RESUME_BRIDGE_SMOKE_OK"}],
                        },
                    }
                )
                + "\n"
            )
        return FakeCompleted()

    monkeypatch.setattr(codex_session_store_bridge.subprocess, "run", fake_run)

    preview = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_resume_send_preview",
        args={"session_id": CODEX_SESSION_STORE_TEST_ID, "prompt": prompt, "timeout_seconds": 10},
        expected_route_schema_version="v0",
    )
    run_root = root / "ION/05_context/current/chatgpt_connector/codex_session_store_runs"

    assert preview["ok"] is True
    assert preview["mutates_active_state"] is False
    assert preview["delegated_result"]["resume_command_not_executed"] is True
    assert preview["delegated_result"]["prompt"] == prompt
    assert not run_root.exists()

    sent = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_resume_send",
        args={
            "session_id": CODEX_SESSION_STORE_TEST_ID,
            "prompt": prompt,
            "timeout_seconds": 10,
            "idempotency_key": idempotency_key,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
        },
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )

    assert sent["ok"] is True
    assert sent["mutates_active_state"] is True
    delegated = sent["delegated_result"]
    assert delegated["ok"] is True
    assert delegated["executed"] is True
    assert delegated["line_count_delta"] == 1
    assert delegated["message_count_delta"] == 1
    assert delegated["session_reply_found"] is True
    assert (root / delegated["receipt_path"]).is_file()
    assert (root / delegated["stdout_path"]).read_text(encoding="utf-8") == "SESSION_RESUME_BRIDGE_SMOKE_OK\n"

    replay = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_resume_send",
        args={
            "session_id": CODEX_SESSION_STORE_TEST_ID,
            "prompt": prompt,
            "timeout_seconds": 10,
            "idempotency_key": idempotency_key,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
        },
        idempotency_key=idempotency_key,
        confirmation="ION_BOUNDED_WRITE_CONFIRMED",
        expected_route_schema_version="v0",
    )
    status = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_resume_status",
        args={"session_id": CODEX_SESSION_STORE_TEST_ID},
        expected_route_schema_version="v0",
    )
    harvest = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_resume_harvest",
        args={"session_id": CODEX_SESSION_STORE_TEST_ID, "message_count": 5},
        expected_route_schema_version="v0",
    )

    assert replay["ok"] is True
    assert replay["delegated_result"]["idempotent_replay"] is True
    assert status["ok"] is True
    assert status["delegated_result"]["run_count"] == 1
    assert status["delegated_result"]["latest_run"]["session_reply_found"] is True
    assert harvest["ok"] is True
    assert harvest["delegated_result"]["latest_run"]["session_reply_found"] is True
    assert "SESSION_RESUME_BRIDGE_SMOKE_OK" in json.dumps(harvest["delegated_result"], sort_keys=True)


def test_codex_session_store_harvest_requires_confirmation_and_idempotency(tmp_path: Path, monkeypatch):
    root = _branch_gateway_root(tmp_path)
    _seed_codex_session_store_fixture(tmp_path, monkeypatch)

    no_idempotency = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_harvest_to_ion",
        args={"session_id": CODEX_SESSION_STORE_TEST_ID},
        expected_route_schema_version="v0",
    )
    no_confirmation = action_branch_invoke(
        root,
        branch_id="codex_session_store",
        route_id="session_harvest_to_ion",
        args={"session_id": CODEX_SESSION_STORE_TEST_ID},
        idempotency_key="harvest-missing-confirmation",
        expected_route_schema_version="v0",
    )

    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"


def test_agent_observatory_branch_describe_routes_are_visible():
    described = action_branch_describe(Path.cwd(), branch_id="agent_observatory", depth="full")

    assert described["ok"] is True
    routes = {route["route_id"] for route in described["branch"]["routes"]}
    assert "agent_observatory_overview" in routes
    assert "agent_observatory_agent_detail" in routes
    assert "agent_observatory_domain_weaver_status" in routes
    assert "agent_observatory_cockpit_status" in routes
