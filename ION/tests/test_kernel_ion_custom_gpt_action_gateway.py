import json
from pathlib import Path

from kernel.ion_chatops_bridge import ACTION_SCHEMA, APPROVAL_TOKEN
from kernel.ion_custom_gpt_action_gateway import (
    READY_VERDICT,
    build_daimon_project_visibility,
    build_gateway_health,
    build_gateway_policy_surface,
    build_recent_gateway_receipts,
    normalize_gateway_response_for_action_transport,
    submit_gateway_action_packet,
    validate_gateway_action_packet,
    validate_gateway_auth,
)


def _seed_root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-gateway-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    for rel in [
        "ION/02_architecture/ION_BROWSER_CARRIER_RUNTIME_PROTOCOL.md",
        "ION/02_architecture/ION_BROWSER_FILE_ATTACHMENT_AUTOMATION_PROTOCOL.md",
        "ION/02_architecture/ION_CHATOPS_YAML_ACTION_PROTOCOL.md",
        "ION/02_architecture/ION_CHATGPT_SANDBOX_RETURN_INTAKE_PROTOCOL.md",
        "ION/02_architecture/ION_CUSTOM_GPT_ACTION_GATEWAY_PROTOCOL.md",
        "ION/03_registry/ion_chatops_action.schema.yaml",
        "ION/03_registry/ion_chatops_extension_policy.yaml",
        "ION/03_registry/ion_chatops_local_daemon_policy.yaml",
        "ION/03_registry/ion_custom_gpt_action_gateway_policy.yaml",
        "ION/03_registry/ion_github_data_plane_registry.yaml",
        "ION/03_registry/ion_chatgpt_sandbox_return.schema.json",
        "ION/03_registry/chatgpt_browser_carrier_profile.yaml",
        "ION/docs/setup/ION_CURRENT_OPERATING_PACKET_V119.md",
        "ION/04_packages/kernel/ion_chatops_bridge.py",
        "ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py",
        "ION/04_packages/kernel/ion_chatgpt_sandbox_return_intake.py",
        "ION/04_packages/kernel/ion_codex_queue_runner.py",
        "ION/04_packages/kernel/ion_agent_invocation_broker.py",
        "ION/04_packages/kernel/ion_lifecycle_packager.py",
        "ION/04_packages/kernel/ion_safe_full_project_packager.py",
    ]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{rel}\n", encoding="utf-8")
    openapi_path = root.parent / "ION_GPT/custom_gpt_action_gateway/openapi.yaml"
    openapi_path.parent.mkdir(parents=True, exist_ok=True)
    openapi_path.write_text("../ION_GPT/custom_gpt_action_gateway/openapi.yaml\n", encoding="utf-8")
    policy = root / "ION/03_registry/ion_custom_gpt_action_gateway_policy.yaml"
    policy.write_text(
        "\n".join(
            [
                "schema_id: ion.custom_gpt_action_gateway_policy.v1",
                "status: draft_non_production",
                "production_authority: false",
                "live_execution_authority: false",
                "listen_host: 127.0.0.1",
                "listen_port: 8777",
                "public_transport: cloudflare_tunnel",
                "auth:",
                "  required: true",
                "  scheme: bearer",
                "  token_env_var: ION_ACTION_GATEWAY_TOKEN",
                "  token_sha256_env_var: ION_ACTION_GATEWAY_TOKEN_SHA256",
                "limits:",
                "  max_body_bytes: 262144",
                "  max_response_bytes: 131072",
                "  require_idempotency_key_for_mutation: true",
                "allowed_get_paths:",
                "  - /health",
                "  - /policy",
                "allowed_post_paths:",
                "  - /actions/validate",
                "  - /actions/submit",
                "supported_mvp_intents:",
                "  - register_artifact",
                "  - write_file_draft",
                "  - create_codex_work_packet",
                "  - create_github_issue_draft",
                "hard_gated_intents:",
                "  - delete_file",
                "  - overwrite_protected_file",
                "  - push_main",
                "  - access_credential",
                "  - production_deploy",
                "  - broad_shell",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / "ION/05_context/current/ACTIVE_WORK_PACKET.json").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/05_context/current/ACTIVE_WORK_PACKET.json").write_text(
        json.dumps({"objective": "Gateway test active work packet."}) + "\n",
        encoding="utf-8",
    )


def _seed_assistant_work_routes(root: Path) -> None:
    registry = root / "ION/05_context/current/ai_assistant_work/registries/AI_ASSISTANT_WORK_ROUTE_REGISTRY_CANDIDATE_V0_1.yaml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        "\n".join(
            [
                "schema: ion.ai_assistant_work.route_registry.v0_1",
                "status: candidate_current_state_not_accepted_canon",
                "routes:",
                "- route_id: route.ui_specialist_work",
                "  trigger_patterns:",
                "  - frontend component",
                "  - accessibility",
                "  required_domains:",
                "  - ui_ux_domain",
                "  primary_agents:",
                "  - UI_ARCHITECT",
                "  output_contract:",
                "    include:",
                "    - screen states",
                "    forbid:",
                "    - visual polish without state/a11y proof",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    compiler_dir = root / "ION/05_context/current/ai_assistant_work/route_compiler"
    compiler_dir.mkdir(parents=True, exist_ok=True)
    (compiler_dir / "AI_ASSISTANT_WORK_ROUTE_COMPILER_CANDIDATE_MAP_20260508T182500Z.json").write_text(
        json.dumps(
            {
                "route_mappings": [
                    {
                        "route_id": "route.ui_specialist_work",
                        "active_skill_candidates": ["codex-solo-work"],
                        "active_lens_candidates": ["vizier", "mason_codex", "nemesis"],
                        "template_spec_candidates": ["screen_state_matrix_packet"],
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )


def _seed_assistant_work_fission(root: Path) -> None:
    fission = root / "ION/05_context/current/ai_assistant_work/fission/AI_ASSISTANT_WORK_DOMAIN_FISSION_CANDIDATES_V0_1.yaml"
    fission.parent.mkdir(parents=True, exist_ok=True)
    fission.write_text(
        "\n".join(
            [
                "schema: ion.ai_assistant_work.domain_fission_candidates.v0_1",
                "status: candidate_current_state_not_accepted_canon",
                "candidate_count: 1",
                "candidates:",
                "- candidate_domain_id: pr_agent_work_domain",
                "  title: PR Agent Work Domain",
                "  parent_domains:",
                "  - review_security_domain",
                "  - testing_quality_domain",
                "  rationale: PR-agent work combines diff review, CI evidence, lockfile analysis, review comments, and merge settlement.",
                "  pressure_signals:",
                "  - CI and lockfile evidence need specialized proof",
                "  proposed_primary_agents:",
                "  - PR_REVIEW_STEWARD",
                "  - CI_EVIDENCE_TRIAGER",
                "  - LOCKFILE_AUDITOR",
                "  proposed_template_packets:",
                "  - pr_review_packet",
                "  - ci_evidence_triage_packet",
                "  proposed_protocols:",
                "  - merge_requires_settlement_receipt",
                "  critical_state_surfaces:",
                "  - diff_state",
                "  - ci_state",
                "  - lockfile_state",
                "  settlement_route: review_return_to_settlement_steward",
                "  status: fission_candidate_not_accepted_domain",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _seed_daimon_repo(parent: Path) -> Path:
    root = parent / "dAimon"
    outputs = root / "sample_outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text("# dAimon\n", encoding="utf-8")
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "docs/google_user_access_readiness.md").write_text("# Google User Access\n", encoding="utf-8")
    (root / "agent_builder").mkdir(parents=True, exist_ok=True)
    (root / "agent_builder/openapi_tools_contract.json").write_text("{}\n", encoding="utf-8")
    (root / "agent_builder/system_prompt.md").write_text("# System prompt\n", encoding="utf-8")
    (outputs / "demo_evidence_package.json").write_text(
        json.dumps(
            {
                "headline_status": "live_vertical_slice_proven_agent_builder_mcp_proven",
                "metrics": {"cloud_run_live_proven": True, "google_user_access_proven": False},
                "claim_matrix": [
                    {
                        "claim_id": "cloud_run_kernel_live_endpoint",
                        "status": "proven_live_cloud_run",
                        "evidence": ["sample_outputs/cloud_run_live_health.json"],
                        "non_claim": False,
                    },
                    {
                        "claim_id": "google_user_tester_access",
                        "status": "pending_google_user_access",
                        "evidence": ["sample_outputs/google_user_access_readiness.json"],
                        "blockers": ["gcloud reauthentication required"],
                        "non_claim": True,
                    },
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (outputs / "cloud_run_live_health.json").write_text(
        json.dumps(
            {
                "ok": True,
                "cloud_run_url": "https://daimon.example.run.app",
                "auth_mode": "gcloud_identity_token",
                "evidence": {"mongodb": {"database": "ion_continuity_bridge"}},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (outputs / "cloud_run_deploy_summary.json").write_text(
        json.dumps({"ok": True, "project": "example-project", "region": "us-central1", "cloud_run_url": "https://daimon.example.run.app"}) + "\n",
        encoding="utf-8",
    )
    (outputs / "agent_builder_mcp_trace_validation.json").write_text(
        json.dumps({"ok": True, "proof_status": "proven_live_agent_builder_mcp", "live_mcp_execution_proven": True}) + "\n",
        encoding="utf-8",
    )
    (outputs / "agent_engine_deploy_summary.json").write_text(
        json.dumps(
            {
                "remote_agent_name": "projects/123/locations/us-central1/reasoningEngines/456",
                "service_account": "123-compute@developer.gserviceaccount.com",
                "location": "us-central1",
                "cloud_run_url": "https://daimon.example.run.app",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (outputs / "google_user_access_readiness.json").write_text(
        json.dumps(
            {
                "ok": False,
                "proof_status": "google_user_access_blocked_or_incomplete",
                "target_principals": [],
                "runtime_identity": {
                    "agent_engine_resource": "projects/123/locations/us-central1/reasoningEngines/456",
                    "agent_service_account": "123-compute@developer.gserviceaccount.com",
                },
                "blockers": [
                    "No target users configured; pass --target-user.",
                    "ERROR: (gcloud.services.list) Please run: gcloud auth login",
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (outputs / "live_vertical_slice_summary.json").write_text(
        json.dumps({"mongo_database": "ion_continuity_bridge", "mongo_collection": "daimon_continuity_objects"}) + "\n",
        encoding="utf-8",
    )
    for name in [
        "dashboard_evidence_trace.json",
        "demo_video_claims.json",
        "agent_builder_mcp_trace.json",
        "orchestration_validation.json",
    ]:
        (outputs / name).write_text("{}\n", encoding="utf-8")
    return root


def _action(action_id: str, intent: str = "register_artifact") -> dict:
    return {
        "ion_action": {
            "schema": ACTION_SCHEMA,
            "action_id": action_id,
            "intent": intent,
            "actor": {"callsign": "Sev", "carrier": "chatgpt_browser"},
            "authority": {
                "human_sovereign": "Braden",
                "requires_approval": True,
                "production_authority": False,
                "live_execution_authority": False,
            },
            "artifact_refs": [{"provider": "local_ion", "path": "ION/05_context/current/demo.md"}],
            "context_refs": [],
            "receipts": {"requested": ["action_receipt"]},
        }
    }


def _approved(packet: dict, *, idempotency_key: str = "gateway-test-key") -> dict:
    return {
        **packet,
        "idempotency_key": idempotency_key,
        "operator_approval_evidence": {
            "approved": True,
            "approved_by": "Braden",
            "approval_token": APPROVAL_TOKEN,
        },
    }


def _approved_without_token(packet: dict, *, idempotency_key: str = "gateway-test-key") -> dict:
    return {
        **packet,
        "idempotency_key": idempotency_key,
        "operator_approval_evidence": {
            "approved": True,
            "approved_by": "Braden",
        },
    }


def test_gateway_health_returns_non_production_status(tmp_path):
    _seed_root(tmp_path)

    result = build_gateway_health(tmp_path)

    assert result["ok"] is True
    assert result["verdict"] == READY_VERDICT
    assert result["production_authority"] is False
    assert result["live_execution_authority"] is False


def test_gateway_policy_surface_imports_chatops_hard_gates(tmp_path):
    _seed_root(tmp_path)

    result = build_gateway_policy_surface(tmp_path)

    assert result["verdict"] == READY_VERDICT
    assert "delete_file" in result["hard_gated_intents"]
    assert "delete_file" in result["imported_chatops_hard_gated_intents"]
    assert result["auth"]["required"] is True
    assert result["limits"]["max_response_bytes"] == 131072
    assert "secret-token" not in json.dumps(result)


def test_gateway_normalizes_oversized_response_to_recovery_handoff(tmp_path):
    _seed_root(tmp_path)
    payload = {
        "schema_id": "ion.test.oversized.gateway.response.v1",
        "ok": True,
        "action_id": "large-action",
        "gateway_receipt_path": "ION/05_context/current/action_gateway/receipts/large-action.json",
        "owner_result": {
            "schema_id": "ion.owner.large.v1",
            "ok": True,
            "receipt_path": "ION/05_context/current/chatgpt_connector/task_returns/large-return.json",
            "result": "X" * 12000,
            "rows": [{"path": "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"}] * 20,
        },
    }

    normalized = normalize_gateway_response_for_action_transport(payload, max_response_bytes=6000)
    body = json.dumps(normalized, indent=2, sort_keys=True)

    assert normalized["schema_id"] == "ion.custom_gpt_action_gateway_oversized_response_recovery.v1"
    assert normalized["response_normalized"] is True
    assert normalized["original_schema_id"] == payload["schema_id"]
    assert normalized["original_response_bytes"] > 6000
    assert normalized["gateway_receipt_path"] == "ION/05_context/current/action_gateway/receipts/large-action.json"
    assert "large_artifact_intelligence" in {
        route["branch_id"] for route in normalized["oversize_recovery"]["fallback_routes"]
    }
    assert normalized["sequential_load_handoff"]["order"][0] == "read compact_summary and path_refs"
    assert "X" * 100 not in body
    assert len(body.encode("utf-8")) <= 6000


def test_daimon_project_visibility_reads_curated_receipts_without_secrets(tmp_path):
    ion_root = tmp_path / "ION_Developement"
    _seed_root(ion_root)
    daimon_root = _seed_daimon_repo(tmp_path)

    result = build_daimon_project_visibility(ion_root)
    text = json.dumps(result)

    assert result["ok"] is True
    assert result["project"]["repo_path"] == daimon_root.as_posix()
    assert result["live_surfaces"]["cloud_run_url"] == "https://daimon.example.run.app"
    assert result["live_surfaces"]["mongodb_database"] == "ion_continuity_bridge"
    assert result["claim_state"]["headline_status"] == "live_vertical_slice_proven_agent_builder_mcp_proven"
    assert result["claim_state"]["google_user_access"]["proof_status"] == "google_user_access_blocked_or_incomplete"
    assert "gcloud reauthentication required before IAM/user-access queries can complete" in result["current_blockers"]
    assert "MONGODB_URI" not in text
    assert "mongodb+srv://" not in text
    assert "password=" not in text.lower()
    assert "token_value" not in text
    assert result["production_authority"] is False
    assert result["live_execution_authority"] is False


def test_gateway_auth_rejects_missing_and_accepts_valid_token(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    policy = build_gateway_policy_surface(tmp_path)
    monkeypatch.setenv("ION_ACTION_GATEWAY_TOKEN", "secret-token")

    missing = validate_gateway_auth({}, policy)
    valid = validate_gateway_auth({"Authorization": "Bearer secret-token"}, policy)
    invalid = validate_gateway_auth({"Authorization": "Bearer wrong"}, policy)

    assert missing["ok"] is False
    assert missing["refusal_class"] == "AUTH_MISSING"
    assert valid["ok"] is True
    assert "secret-token" not in json.dumps(valid)
    assert invalid["ok"] is False
    assert invalid["refusal_class"] == "AUTH_INVALID"


def test_gateway_validate_does_not_write_receipts(tmp_path):
    _seed_root(tmp_path)

    result = validate_gateway_action_packet(tmp_path, _action("gateway-validate-only"))

    assert result["ok"] is True
    assert result["assistant_work_route"]["candidate_only"] is True
    assert result["approval_checked"] is True
    assert result["approval_mode"] == "submit_equivalent_evidence_check"
    assert result["approval_source"] == "none"
    assert "operator_approval_evidence_required" in result["approval_findings"]
    assert not (tmp_path / "ION/05_context/current/action_gateway/receipts").exists()


def test_gateway_validate_attaches_candidate_assistant_work_route(tmp_path):
    _seed_root(tmp_path)
    _seed_assistant_work_routes(tmp_path)
    packet = _action("gateway-ui-route", intent="create_codex_work_packet")
    packet["ion_action"]["objective"] = "Draft a frontend component with accessibility and screen states."

    result = validate_gateway_action_packet(tmp_path, packet)

    route = result["assistant_work_route"]
    assert result["ok"] is True
    assert route["ok"] is True
    assert route["gateway_validation_only"] is True
    assert route["gateway_packet_validated"] is True
    assert route["route_id"] == "route.ui_specialist_work"
    assert route["candidate_only"] is True
    assert route["authority_boundary"]["mutates_ION_03_registry"] is False
    assert route["authority_boundary"]["mutates_product_front_door"] is False


def test_gateway_validate_surfaces_dynamic_domain_agent_proposal(tmp_path):
    _seed_root(tmp_path)
    _seed_assistant_work_routes(tmp_path)
    _seed_assistant_work_fission(tmp_path)
    packet = _action("gateway-pr-dynamic-route", intent="create_codex_work_packet")
    packet["ion_action"]["objective"] = "Review PR branch, classify CI failure evidence, inspect lockfile diff risk, and prepare merge settlement."

    result = validate_gateway_action_packet(tmp_path, packet)

    route = result["assistant_work_route"]
    proposal = route["dynamic_domain_agent_proposal"]
    assert result["ok"] is True
    assert route["gateway_validation_only"] is True
    assert proposal["needed"] is True
    assert proposal["trigger"] == "fission_candidate_match"
    assert proposal["recommended_local_hub_report"] is True
    assert proposal["candidate_domains"][0]["domain_id"] == "pr_agent_work_domain"
    assert "CI_EVIDENCE_TRIAGER" in [agent["agent_id"] for agent in proposal["candidate_agents"]]
    assert proposal["authority_boundary"]["requires_explicit_acceptance_to_land"] is True


def test_gateway_validate_reports_approval_source_and_no_findings_when_evidence_present(tmp_path):
    _seed_root(tmp_path)
    packet = _approved(_action("gateway-validate-approval-source"), idempotency_key="validate-approval-source")

    result = validate_gateway_action_packet(tmp_path, packet)

    assert result["ok"] is True
    assert result["approval_checked"] is True
    assert result["approval_mode"] == "submit_equivalent_evidence_check"
    assert result["approval_source"] == "approval"
    assert result["approval_findings"] == []


def test_gateway_validate_accepts_operator_evidence_without_token_by_default(tmp_path):
    _seed_root(tmp_path)
    packet = _approved_without_token(_action("gateway-validate-no-token"), idempotency_key="validate-no-token")

    result = validate_gateway_action_packet(tmp_path, packet)

    assert result["ok"] is True
    assert result["approval_findings"] == []


def test_gateway_submit_bridges_operator_evidence_without_token_to_chatops_owner(tmp_path):
    _seed_root(tmp_path)
    packet = _approved_without_token(_action("gateway-submit-no-token"), idempotency_key="submit-no-token")

    result = submit_gateway_action_packet(tmp_path, packet)

    assert result["ok"] is True
    assert result["owner"] == "ION/04_packages/kernel/ion_chatops_bridge.py"
    assert result["owner_result"]["ok"] is True


def test_gateway_submit_requires_token_when_packet_explicitly_requires_token(tmp_path):
    _seed_root(tmp_path)
    packet = _approved_without_token(_action("gateway-submit-token-required"), idempotency_key="submit-token-required")
    packet["operator_approval_evidence"]["approval_token_required"] = True

    result = submit_gateway_action_packet(tmp_path, packet)

    assert result["ok"] is False
    assert result["refusal_class"] == "APPROVAL_EVIDENCE_INVALID"
    assert "approval_token_invalid" in result["approval"]["findings"]


def test_gateway_submit_requires_idempotency_key(tmp_path):
    _seed_root(tmp_path)

    result = submit_gateway_action_packet(tmp_path, _action("gateway-no-idempotency"))

    assert result["ok"] is False
    assert result["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert (tmp_path / result["gateway_receipt_path"]).exists()


def test_gateway_submit_requires_operator_approval_evidence(tmp_path):
    _seed_root(tmp_path)
    packet = {**_action("gateway-no-approval"), "idempotency_key": "missing-approval"}

    result = submit_gateway_action_packet(tmp_path, packet)

    assert result["ok"] is False
    assert result["refusal_class"] == "OPERATOR_APPROVAL_REQUIRED"
    assert (tmp_path / result["gateway_receipt_path"]).exists()


def test_gateway_rejects_production_and_live_authority(tmp_path):
    _seed_root(tmp_path)
    packet = _approved(_action("gateway-authority-refusal"))
    packet["ion_action"]["authority"]["production_authority"] = True
    packet["ion_action"]["authority"]["live_execution_authority"] = True

    result = submit_gateway_action_packet(tmp_path, packet)

    assert result["ok"] is False
    assert result["refusal_class"] == "PRODUCTION_AUTHORITY_REFUSED"


def test_gateway_hard_gated_intent_rejected_before_owner_submit(tmp_path):
    _seed_root(tmp_path)
    packet = _approved(_action("gateway-hard-gated", intent="delete_file"))

    result = submit_gateway_action_packet(tmp_path, packet)

    assert result["ok"] is False
    assert result["refusal_class"] == "INTENT_HARD_GATED"
    receipts = build_recent_gateway_receipts(tmp_path)
    assert receipts["gateway_receipts"]


def test_gateway_submit_routes_to_chatops_owner_and_blocks_replay(tmp_path):
    _seed_root(tmp_path)
    packet = _approved(_action("gateway-register-artifact"), idempotency_key="replay-key")

    first = submit_gateway_action_packet(tmp_path, packet)
    second = submit_gateway_action_packet(tmp_path, packet)

    assert first["ok"] is True
    assert first["owner"] == "ION/04_packages/kernel/ion_chatops_bridge.py"
    assert (tmp_path / first["gateway_receipt_path"]).exists()
    assert (tmp_path / first["owner_result"]["receipt_path"]).exists()
    assert second["ok"] is False
    assert second["refusal_class"] == "IDEMPOTENCY_REPLAY_BLOCKED"


def test_gateway_submit_create_codex_work_packet_persists_model_override_fields(tmp_path):
    _seed_root(tmp_path)
    packet = _action("gateway-codex-work-override", intent="create_codex_work_packet")
    action = packet["ion_action"]
    action["objective"] = "Gateway should preserve codex override fields into work request JSON."
    action["codex_model_override"] = {
        "selected_model": "gpt-5.5",
        "selected_reasoning_effort": "medium",
        "reason": "gateway front door proof",
        "unsafe_extra": "drop_me",
    }
    action["requested_model"] = "gpt-5.5"
    action["requested_reasoning_effort"] = "medium"
    action["model_override_reason"] = "gateway fallback fields"
    action["project_hash"] = "proj_hash_gateway_20260514"
    action["unexpected_unallowlisted_field"] = "must_not_forward"

    result = submit_gateway_action_packet(tmp_path, _approved(packet, idempotency_key="gateway-codex-override-1"))

    assert result["ok"] is True
    owner_result = result["owner_result"]
    request_path = tmp_path / owner_result["execution"]["packet_path"]
    request_packet = json.loads(request_path.read_text(encoding="utf-8"))
    assert request_packet["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert request_packet["codex_model_override"]["selected_reasoning_effort"] == "medium"
    assert request_packet["codex_model_override"]["reason"] == "gateway front door proof"
    assert "unsafe_extra" not in request_packet["codex_model_override"]
    assert request_packet["requested_model"] == "gpt-5.5"
    assert request_packet["requested_reasoning_effort"] == "medium"
    assert request_packet["model_override_reason"] == "gateway fallback fields"
    assert request_packet["project_hash"] == "proj_hash_gateway_20260514"
    assert "unexpected_unallowlisted_field" not in request_packet


def test_gateway_agent_invocation_status_and_relay_wrappers(tmp_path):
    from kernel.ion_custom_gpt_action_gateway import (
        build_gateway_agent_pending_relays,
        build_gateway_agent_status,
        submit_gateway_agent_invocation,
        submit_gateway_agent_relay_response,
        submit_gateway_agent_settlement,
    )
    from kernel.ion_agent_invocation_broker import create_agent_relay_message

    _seed_root(tmp_path)
    packet = {
        "schema_id": "ion.agent_invocation_packet.v1",
        "idempotency_key": "gateway-agent-key-001",
        "agent_role": "role.context_cartographer",
        "objective": "Return a bounded proof report.",
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "local_write_authority": "none",
            "allowed_paths": ["ION/"],
        },
        "capsule_context": {"inline_summary": "Gateway wrapper test."},
    }
    invoked = submit_gateway_agent_invocation(tmp_path, packet)
    assert invoked["ok"] is True

    status = build_gateway_agent_status(tmp_path, invocation_id=invoked["invocation_id"])
    assert status["ok"] is True
    assert status["invocation"]["invocation_id"] == invoked["invocation_id"]

    relay = create_agent_relay_message(
        tmp_path,
        {
            "invocation_id": invoked["invocation_id"],
            "from_agent": "role.context_cartographer",
            "to": "chatgpt_browser",
            "question_type": "route",
            "question": "Continue?",
        },
    )
    pending = build_gateway_agent_pending_relays(tmp_path, invocation_id=invoked["invocation_id"])
    assert pending["count"] == 1
    response = submit_gateway_agent_relay_response(
        tmp_path,
        {
            "schema_id": "ion.agent_relay_response.v1",
            "relay_id": relay["relay_id"],
            "invocation_id": invoked["invocation_id"],
            "answered_by": "chatgpt_browser",
            "response": "Continue within the same authority ceiling.",
            "continue": True,
        },
    )
    assert response["ok"] is True
    settled = submit_gateway_agent_settlement(
        tmp_path,
        {
            "schema_id": "ion.agent_invocation_settlement.v1",
            "invocation_id": invoked["invocation_id"],
            "terminal_state": "blocked",
            "settled_by": "chatgpt_browser",
            "summary": "Wrapper settlement smoke.",
            "evidence_refs": [invoked["capsule_context_path"]],
        },
    )
    assert settled["ok"] is True


def test_gateway_browser_agent_contact_and_invoke_wrapper(tmp_path):
    from kernel.ion_custom_gpt_action_gateway import (
        build_codex_browser_agent_action_contact,
        submit_codex_browser_agent_action_invocation,
    )

    _seed_root(tmp_path)

    contact = build_codex_browser_agent_action_contact(tmp_path)
    assert contact["ok"] is True
    assert contact["agent_name"] == "codex_cli_carrier.browser_gpt_pair"
    assert contact["agent_tag"] == "@codex_cli_carrier.browser_gpt_pair"
    assert contact["authority"]["production_authority"] is False
    assert contact["authority"]["live_execution_authority"] is False
    assert "ION/04_packages/kernel/ion_codex_browser_agent.py" in contact["context_refs"]

    result = submit_codex_browser_agent_action_invocation(
        tmp_path,
        {
            "client_request_id": "browser-agent-wrapper-001",
            "mode": "plan",
            "objective": "Plan the bounded Browser GPT Playwright inspection lane.",
            "context_refs": ["ION/05_context/current/browser_gpt_dom_profiles/latest_probe_snapshot.json"],
            "queue": False,
        },
    )
    assert result["ok"] is True
    assert result["agent_tag"] == "@codex_cli_carrier.browser_gpt_pair"
    assert result["agent_role"] == "role.browser_dom_cartographer"
    invocation = result["invocation"]
    assert invocation["status"] == "PREPARED_NOT_QUEUED"
    packet = json.loads((tmp_path / invocation["invocation_path"]).read_text(encoding="utf-8"))
    assert packet["agent_role"] == "role.browser_dom_cartographer"
    assert packet["authority"]["production_authority"] is False
    assert packet["authority"]["live_execution_authority"] is False
    assert packet["authority"]["silent_send"] is False
    assert "ION/04_packages/kernel/ion_codex_browser_agent.py" in packet["capsule_context"]["context_refs"]
