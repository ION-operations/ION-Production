import json
import os
from datetime import datetime, timezone
from pathlib import Path

from kernel import ion_codex_queue_runner as runner
from kernel import ion_codex_session_store_bridge as session_bridge
from kernel.ion_codex_queue_runner import (
    DEFAULT_CONTEXT_READS,
    bridge_codex_transient_usage_limit_request,
    build_codex_parallel_plan_preview,
    build_codex_queue_runner_status,
    prepare_codex_queue_run,
    preview_codex_transient_usage_limit_bridge,
    process_codex_queue_once,
    requeue_codex_transient_usage_limit_request,
    reconcile_codex_queue_runner_state,
    run_codex_queue_worker,
)
from kernel.ion_agent_comms import send_agent_message
from kernel.ion_worker_shift_presence import claim_work_lease, load_shift_board, summarize_shift_board


def test_classifies_visual_proof_work_as_browser_lane():
    by_work_class = runner.classify_codex_work_request_lane(
        {
            "request_id": "codex_req_visual_proof",
            "work_class": "visual_proof_and_review",
            "objective": "Domain Weaver visual proof and stewardship review.",
        }
    )
    by_role = runner.classify_codex_work_request_lane(
        {
            "request_id": "codex_req_visual_role",
            "agent_role": "VISUAL_PROOF_AUDITOR",
            "objective": "Capture browser screenshots and geometry proof.",
        }
    )
    explicit = runner.classify_codex_work_request_lane(
        {
            "request_id": "codex_req_browser_probe",
            "lane_id": "browser_lane",
            "work_class": "browser_probe",
            "objective": "Run browser proof.",
        }
    )

    assert by_work_class["lane_id"] == "browser_lane"
    assert by_work_class["source"] == "work_class"
    assert by_role["lane_id"] == "browser_lane"
    assert by_role["source"] == "agent_field"
    assert explicit["lane_id"] == "browser_lane"
    assert explicit["source"] == "explicit_lane_id"


def test_validation_lane_aliases_to_audit_lane():
    explicit = runner.classify_codex_work_request_lane(
        {
            "request_id": "codex_req_validation_lane",
            "lane_id": "validation_lane",
            "objective": "Run focused validation proof.",
        }
    )
    shorthand = runner.classify_codex_work_request_lane(
        {
            "request_id": "codex_req_validation_short",
            "lane_id": "validation",
            "objective": "Run focused validation proof.",
        }
    )

    assert runner.normalize_codex_work_lane_id("validation_lane") == "audit_lane"
    assert runner.normalize_codex_work_lane_id("validation") == "audit_lane"
    assert explicit["lane_id"] == "audit_lane"
    assert explicit["source"] == "explicit_lane_id"
    assert explicit["valid_lane"] is True
    assert "validation_lane_alias_to_audit_lane" in explicit["reasons"]
    assert shorthand["lane_id"] == "audit_lane"
    assert shorthand["source"] == "explicit_lane_id"
    assert shorthand["valid_lane"] is True
    assert "validation_lane_alias_to_audit_lane" in shorthand["reasons"]


def _seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    (root / ".codex").mkdir(parents=True, exist_ok=True)
    (root / ".codex/config.toml").write_text("sandbox_mode = \"workspace-write\"\n", encoding="utf-8")
    (root / "ION_WORKSPACE_MANIFEST.yaml").write_text(
        f"""schema_id: ion.workspace_manifest.v1
status: TEST

workspace_root: "{root.parent}"
active_repo_root: "{root}"
ion_content_root: "{root}/ION"
export_root: "{root.parent}/ION_EXPORTS_LOCAL"
vault_root: "{root.parent}/ION_VAULT_LOCAL"

allowed_sibling_roots:
  - "{root.parent}/ION_EXPORTS_LOCAL"
  - "{root.parent}/ION_VAULT_LOCAL"
  - "{root.parent}/Needs_Routed"
  - "{root.parent}/quarentine"

forbidden_roots:
  - "{root.parent.parent}/ION_EXPORTS_LOCAL"
  - "{root.parent.parent}/.ssh"

path_policy:
  forbid_parent_segments_for_write: true
  canonicalize_all_leases: true
  require_workspace_containment_for_artifacts: true
  require_artifacts_outside_active_repo: true

families:
  ION_Developement:
    role: active ION kernel/context repo
    git_status: nested_repo_current
  ION_GPT:
    role: Custom GPT surfaces
    git_status: workspace_folder_candidate
  browser_extension:
    role: browser carrier extension
    git_status: workspace_folder_candidate
  mcp:
    role: MCP and ChatGPT browser connector surfaces
    git_status: workspace_folder_candidate
  local_daemon:
    role: local bridge daemons
    git_status: workspace_folder_candidate
  systemd:
    role: local user service templates
    git_status: workspace_folder_candidate
  product_packager:
    role: packaging/export builders
    git_status: workspace_folder_candidate
  dAimon:
    role: dAimon app/agent project
    git_status: nested_repo_current
  Needs_Routed:
    role: operator staging/inbox
    git_status: workspace_folder_candidate
  quarentine:
    role: archive witness and quarantine
    git_status: workspace_folder_candidate
    active_source: false
""",
        encoding="utf-8",
    )
    for rel in (
        "ION_GPT/01_GPT_BUILDER_INPUTS",
        "browser_extension/ion_chatops_bridge/src",
        "mcp",
        "local_daemon",
        "systemd",
        "product_packager",
        "dAimon",
        "Needs_Routed",
        "quarentine",
        "ION_EXPORTS_LOCAL",
        "ION_VAULT_LOCAL",
    ):
        (root.parent / rel).mkdir(parents=True, exist_ok=True)
    for rel in DEFAULT_CONTEXT_READS:
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"seeded test context for {rel}\n", encoding="utf-8")
    codex_solo = root / "ION/05_context/current/codex_solo"
    codex_solo.mkdir(parents=True, exist_ok=True)
    for name in ("CAPSULE.md", "MINI.md", "HOT_CONTEXT.md"):
        (codex_solo / name).write_text(f"# seeded {name}\n", encoding="utf-8")
    for name in ("LONG_HORIZON.json", "ROUTE.json", "STATUS.json"):
        (codex_solo / name).write_text("{}\n", encoding="utf-8")
    generated_at = datetime.now(timezone.utc).isoformat()
    (codex_solo / "CONTEXT_PACKAGES.json").write_text(
        json.dumps(
            {
                "schema_id": "ion.test.codex_solo_context_packages.v1",
                "generated_at": generated_at,
                "package_count": 1,
                "selected_by_default": ["test_codex_solo"],
                "packages": [
                    {
                        "package_id": "test_codex_solo",
                        "context_type": "test",
                        "load_policy": "default",
                        "path_refs": [
                            "ION/05_context/current/codex_solo/CAPSULE.md",
                            "ION/05_context/current/codex_solo/MINI.md",
                            "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
                        ],
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _seed_request(
    root: Path,
    *,
    objective: str = "Runner test objective",
    ai_movement_root_envelope: dict[str, object] | None = None,
    target_root_id: str | None = "active_ion_control",
    target_project_subpath: str | None = None,
    movement_class: str | None = None,
    planned_writes: list[str] | None = None,
    planned_artifacts: list[str] | None = None,
    codex_model_override: dict[str, object] | None = None,
    requested_model: str | None = None,
    requested_reasoning_effort: str | None = None,
    requested_service_tier: str | None = None,
    model_override_reason: str | None = None,
    work_class: str | None = None,
    risk_level: str | None = None,
    route_family: str | None = None,
    idempotency_key: str | None = None,
    agent_role_id: str | None = None,
    domain_id: str | None = None,
    role_tier: str | None = None,
    callsign: str | None = None,
    include_codex_model_move: bool = True,
) -> str:
    rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/2026-05-04T000000Z0000_runner_test.json"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
        "request_id": "codex_req_runner_test",
        "objective": objective,
        "requested_by": "chatgpt_browser_connector",
        "status": "QUEUED_FOR_CODEX_CARRIER",
        "created_at": "2026-05-04T00:00:00+00:00",
        "updated_at": "2026-05-04T00:00:00+00:00",
        "return_packet_paths": [],
        "latest_return_packet_path": None,
        "request_kind": "codex_chat_response",
        "ion_skill_activation": {
            "skill_id": "codex-chat-answer",
            "display_name": "Codex Chat Answer",
            "activates_templates": ["ION/07_templates/context/ION_CONTEXT_LOAD_PROOF.md"],
        },
        "ion_chat_engine_turn": {
            "response_mode": "answer",
            "carrier_strategy": {"mode": "gpt_5_5_codex_chat_response_contract"},
            "native_lenses": [{"display_name": "Persona", "purpose": "User-facing clarity."}],
        },
        "production_authority": False,
        "live_execution_authority": False,
    }
    if include_codex_model_move:
        payload["codex_model_move"] = {
            "selected_model": "gpt-5.5",
            "selected_reasoning_effort": "medium",
            "work_class": "cheap_classification",
            "ion_stage_id": "relay_ingress",
            "usage_pool_id": "frontier_main_observed",
            "usage_pool_authority": "operator_observed_pending_verification",
        }
    if ai_movement_root_envelope is not None:
        payload["ai_movement_root_envelope"] = ai_movement_root_envelope
    if target_root_id is not None:
        payload["target_root_id"] = target_root_id
    if target_project_subpath is not None:
        payload["target_project_subpath"] = target_project_subpath
    if movement_class is not None:
        payload["movement_class"] = movement_class
    if planned_writes is not None:
        payload["planned_writes"] = planned_writes
    if planned_artifacts is not None:
        payload["planned_artifacts"] = planned_artifacts
    if codex_model_override is not None:
        payload["codex_model_override"] = codex_model_override
    if requested_model is not None:
        payload["requested_model"] = requested_model
    if requested_reasoning_effort is not None:
        payload["requested_reasoning_effort"] = requested_reasoning_effort
    if requested_service_tier is not None:
        payload["requested_service_tier"] = requested_service_tier
    if model_override_reason is not None:
        payload["model_override_reason"] = model_override_reason
    if work_class is not None:
        payload["work_class"] = work_class
    if risk_level is not None:
        payload["risk_level"] = risk_level
    if route_family is not None:
        payload["route_family"] = route_family
    if idempotency_key is not None:
        payload["idempotency_key"] = idempotency_key
    if agent_role_id is not None:
        payload["agent_role_id"] = agent_role_id
    if domain_id is not None:
        payload["domain_id"] = domain_id
    if role_tier is not None:
        payload["role_tier"] = role_tier
    if callsign is not None:
        payload["callsign"] = callsign
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return rel


def _seed_codex_agent_mount(
    root: Path,
    mount_id: str,
    *,
    portable_context: bool = True,
    lane_ids: list[str] | None = None,
) -> Path:
    mount = root / "ION/05_context/current/codex_agent_mounts" / mount_id
    mount.mkdir(parents=True, exist_ok=True)
    role_part, _, domain_part = mount_id.partition("__")
    role_id = role_part.replace("_", ".", 1) if role_part.startswith("role_") else role_part.replace("_", ".")
    domain_id = domain_part.replace("_", ".", 1) if domain_part.startswith("domain_") else domain_part.replace("_", ".")
    (mount / "ION_AGENT_MOUNT_MANIFEST.json").write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_agent_mount.v0_1",
                "mount_id": mount_id,
                "agent_role_id": role_id,
                "domain_id": domain_id,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (mount / "AGENTS.md").write_text("# test agent mount\n", encoding="utf-8")
    (mount / ".codex").mkdir(parents=True, exist_ok=True)
    (mount / ".codex/config.toml").write_text("sandbox_mode = \"workspace-write\"\n", encoding="utf-8")
    if portable_context:
        portable = mount / ".ion"
        portable.mkdir(parents=True, exist_ok=True)
        (portable / "ION_CONTEXT_CAPSULE.yaml").write_text("schema_id: test.context\n", encoding="utf-8")
        (portable / "CAPSULE.md").write_text("# test capsule\n", encoding="utf-8")
        (portable / "ACTIVE_CONTEXT_PACKAGE.md").write_text("# test active package\n", encoding="utf-8")
        if lane_ids is not None:
            (portable / "ACTIVE_CONTEXT_PACKAGE.json").write_text(
                json.dumps(
                    {
                        "schema_id": "ion.test.active_context_package.v1",
                        "lane_ids": lane_ids,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
    return mount


def _seed_lane_request(
    root: Path,
    *,
    filename: str,
    request_id: str,
    work_class: str,
    objective: str,
    agent_role_id: str | None = None,
    domain_id: str | None = None,
) -> str:
    rel = f"ION/05_context/current/chatgpt_connector/codex_work_requests/{filename}"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
        "request_id": request_id,
        "objective": objective,
        "requested_by": "chatgpt_browser_connector",
        "status": "QUEUED_FOR_CODEX_CARRIER",
        "created_at": "2026-05-04T00:00:00+00:00",
        "updated_at": "2026-05-04T00:00:00+00:00",
        "return_packet_paths": [],
        "latest_return_packet_path": None,
        "work_class": work_class,
        "target_root_id": "active_ion_control",
        "movement_class": "ION_KERNEL_CONTROL_MOVEMENT",
        "production_authority": False,
        "live_execution_authority": False,
    }
    if agent_role_id is not None:
        payload["agent_role_id"] = agent_role_id
    if domain_id is not None:
        payload["domain_id"] = domain_id
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return rel


def _seed_agent_cartography_request(root: Path) -> str:
    rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/2026-05-04T000100Z0000_runner_agent_cartography_test.json"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
        "request_id": "codex_req_runner_agent_cartography_test",
        "objective": "Agent cartography proof run",
        "requested_by": "ion_agent_invocation_broker",
        "status": "QUEUED_FOR_CODEX_CARRIER",
        "created_at": "2026-05-04T00:01:00+00:00",
        "updated_at": "2026-05-04T00:01:00+00:00",
        "return_packet_paths": [],
        "latest_return_packet_path": None,
        "request_kind": "runtime_cartography",
        "target_root_id": "active_ion_control",
        "production_authority": False,
        "live_execution_authority": False,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return rel


def _valid_task_return(required_paths: list[str]) -> str:
    proof_lines = ["### CONTEXT PROOF"]
    proof_lines.extend(f"path: {path}\nsha256: testhash\nexcerpt: \"line evidence\"" for path in required_paths)
    return "\n".join([
        *proof_lines,
        "",
        "### TEMPLATE ACTION PROOF",
        "template_id: ion.template.autonomous_loop.local_worker.v1",
        "action_id: codex_queue_runner_test",
        "result: validated queue runner task return",
        "touched_paths:",
        "  - ION/04_packages/kernel/ion_codex_queue_runner.py",
        "",
        "### VALIDATION",
        "commands_run:",
        "  - focused queue runner unit test",
        "tests_passed: queue runner proof gate smoke",
        "tests_failed: none",
        "",
        "### RESULT",
        "implementation_result: queue runner smoke accepted",
        "remaining_blockers: none for unit test",
        "next_lawful_moves: continue",
        "",
        "### WORKLOAD DIFF",
        "- ION/04_packages/kernel/ion_codex_queue_runner.py",
        "",
        "### BLOCKERS",
        "- none",
        "",
        "### RECOMMENDED NEXT PACKET",
        "NEXT_PACKET_EXAMPLE",
        "",
    ])


def test_return_contract_sections_include_operational_posture_for_red_alert_requests():
    sections = runner._return_contract_sections_for_request(
        {
            "work_class": "red_alert",
            "objective": "repair Codex carrier mount",
        }
    )

    assert "### ION OPERATIONAL POSTURE" in sections


def test_codex_queue_runner_status_reports_pending_request(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)

    status = build_codex_queue_runner_status(tmp_path)

    assert status["schema_id"] == "ion.codex_queue_runner.v1"
    assert status["queued_request_count"] == 1
    assert status["next_request_path"] == request_rel
    assert status["manual_proceed_relay_required"] is False


def test_live_status_reports_idle_when_no_active_or_latest_run(tmp_path):
    _seed_root(tmp_path)

    status = build_codex_queue_runner_status(tmp_path, reconcile=False)

    live = status["live_worker_telemetry"]
    assert live["phase_status"] == "idle"
    assert live["active_worker_pid"] is None
    assert live["run_packet_path"] is None
    assert live["artifacts"]["run_packet"]["exists"] is False


def test_live_status_reports_active_run_with_log_sizes(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])
    run["status"] = "CODEX_CLI_RUNNING"
    run["pid"] = os.getpid()
    run["started_at"] = "2026-05-04T00:00:00+00:00"
    run_path = tmp_path / run["run_packet_path"]
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    (tmp_path / run["stdout_path"]).write_text("stdout-bytes\n", encoding="utf-8")
    (tmp_path / run["stderr_path"]).write_text("stderr-bytes\n", encoding="utf-8")
    (tmp_path / run["last_message_path"]).write_text("last-return\n", encoding="utf-8")
    run_dir = tmp_path / run["run_dir"]
    (run_dir / "worker_stdout.log").write_text("worker-stdout\n", encoding="utf-8")
    (run_dir / "worker_stderr.log").write_text("worker-stderr\n", encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": run["run_id"],
                    "pid": os.getpid(),
                    "run_packet_path": run["run_packet_path"],
                    "request_path": request_rel,
                    "started_at": "2026-05-04T00:00:00+00:00",
                },
                "latest_run": run["run_packet_path"],
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    status = build_codex_queue_runner_status(tmp_path, reconcile=False)

    live = status["live_worker_telemetry"]
    assert live["phase_status"] == "active"
    assert live["active_worker_pid"] == os.getpid()
    assert live["request_path"] == request_rel
    assert live["worker_lifecycle_events"] == []
    assert live["latest_worker_lifecycle_event"] is None
    assert live["artifacts"]["stdout"]["exists"] is True
    assert live["artifacts"]["stderr"]["exists"] is True
    assert live["artifacts"]["latest_return"]["exists"] is True
    assert live["artifacts"]["worker_stdout"]["exists"] is True
    assert live["artifacts"]["worker_stderr"]["exists"] is True
    assert live["artifacts"]["worker_stdout"]["bytes"] == len("worker-stdout\n".encode("utf-8"))
    assert live["preferred_preview"]["target"] == "latest_return"
    assert live["observability_trace"]["schema_id"] == "ion.codex_worker_observability_trace.v0"
    assert live["observability_trace"]["artifacts"]["metadata"]["latest_return"]["exists"] is True
    assert live["terminal_intake_result"]["state"] == "not-completed"
    assert isinstance(live["elapsed_seconds"], int)


def test_codex_queue_runner_status_reports_lane_locks_for_parallel_workers(tmp_path):
    _seed_root(tmp_path)
    implementation_rel = _seed_lane_request(
        tmp_path,
        filename="2026-05-04T000001Z0000_impl.json",
        request_id="codex_req_impl",
        work_class="implementation",
        objective="Implementation lane worker",
    )
    audit_rel = _seed_lane_request(
        tmp_path,
        filename="2026-05-04T000002Z0000_audit.json",
        request_id="codex_req_audit",
        work_class="audit",
        objective="Audit lane worker",
    )
    implementation = prepare_codex_queue_run(tmp_path, request_path=implementation_rel, claim=True)["run"]
    audit = prepare_codex_queue_run(tmp_path, request_path=audit_rel, claim=True)["run"]
    for run in (implementation, audit):
        run["status"] = "CODEX_CLI_RUNNING"
        run["pid"] = os.getpid()
        run["started_at"] = "2026-05-04T00:00:00+00:00"
        (tmp_path / run["run_packet_path"]).write_text(json.dumps(run, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": audit["run_id"],
                    "pid": os.getpid(),
                    "run_packet_path": audit["run_packet_path"],
                    "request_path": audit_rel,
                    "lane_id": "audit_lane",
                    "started_at": "2026-05-04T00:00:00+00:00",
                },
                "active_runs": {
                    implementation["run_id"]: {
                        "run_id": implementation["run_id"],
                        "pid": os.getpid(),
                        "run_packet_path": implementation["run_packet_path"],
                        "request_path": implementation_rel,
                        "lane_id": "implementation_lane",
                        "started_at": "2026-05-04T00:00:00+00:00",
                    },
                    audit["run_id"]: {
                        "run_id": audit["run_id"],
                        "pid": os.getpid(),
                        "run_packet_path": audit["run_packet_path"],
                        "request_path": audit_rel,
                        "lane_id": "audit_lane",
                        "started_at": "2026-05-04T00:00:00+00:00",
                    },
                },
                "latest_run": audit["run_packet_path"],
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    status = build_codex_queue_runner_status(tmp_path, reconcile=False)

    assert status["active_run_count"] == 2
    assert status["concurrency"]["mode"] == "bounded_per_lane_workers"
    assert status["concurrency"]["global_active_lock"] is False
    assert status["active_lane_locks"]["locks"]["implementation_lane"]["locked"] is True
    assert status["active_lane_locks"]["locks"]["audit_lane"]["locked"] is True


def test_pid_running_treats_zombie_process_as_not_running(monkeypatch):
    class FakeProcStatPath:
        def __init__(self, value: str) -> None:
            self.value = value

        def read_text(self, *, encoding: str = "utf-8", errors: str = "replace") -> str:
            return "1587510 (python3) Z 944633 1587510 1587510 0 -1 4228108"

    monkeypatch.setattr(runner.os, "kill", lambda pid, sig: None)
    monkeypatch.setattr(runner, "Path", FakeProcStatPath)

    assert runner._pid_running(1587510) is False


def test_live_status_prefers_latest_return_when_worker_stdout_empty(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])
    run["status"] = "CODEX_CLI_RUNNING"
    run["pid"] = os.getpid()
    run_path = tmp_path / run["run_packet_path"]
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    run_dir = tmp_path / run["run_dir"]
    (run_dir / "latest_return.md").write_text(
        "\n".join(
            [
                "### RESULT",
                "implemented worker trace",
                "",
                "### TEMPLATE ACTION PROOF",
                "touched_paths:",
                "  - ION/04_packages/kernel/ion_codex_queue_runner.py",
                "",
                "### VALIDATION",
                "- 3 passed",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "stdout.log").write_text("stdout fallback\n", encoding="utf-8")
    (run_dir / "stderr.log").write_text("x" * 4096 + "tail-error-line\n", encoding="utf-8")
    (run_dir / "worker_stdout.log").write_text("", encoding="utf-8")
    (run_dir / "worker_stderr.log").write_text("ModuleNotFoundError: No module named yaml\n", encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": run["run_id"],
                    "pid": os.getpid(),
                    "run_packet_path": run["run_packet_path"],
                    "request_path": request_rel,
                    "started_at": "2026-05-04T00:00:00+00:00",
                },
                "latest_run": run["run_packet_path"],
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    status = build_codex_queue_runner_status(tmp_path, reconcile=False, include_preview=True, preview_max_bytes=128)

    live = status["live_worker_telemetry"]
    trace = live["observability_trace"]
    assert live["preview"]["target"] == "latest_return"
    assert "ion_codex_queue_runner.py" in live["preview"]["text"]
    assert trace["artifacts"]["preferred_preview"]["target"] == "latest_return"
    assert trace["operational_summary"]["touched_paths"] == ["ION/04_packages/kernel/ion_codex_queue_runner.py"]
    assert trace["operational_summary"]["test_summaries"] == ["3 passed"]
    assert "ModuleNotFoundError" in trace["operational_summary"]["error_summaries"][-1]
    assert trace["artifacts"]["previews"]["stderr"]["shown_bytes"] <= 128
    assert trace["chain_of_thought_policy"]["hidden_model_chain_of_thought_exposed"] is False


def test_live_status_classifies_terminal_accepted_and_blocked(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])
    run["started_at"] = "2026-05-04T00:00:00+00:00"
    run["completed_at"] = "2026-05-04T00:05:00+00:00"
    run_path = tmp_path / run["run_packet_path"]
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": None,
                "latest_run": run["run_packet_path"],
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    run["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    run["submit_result"] = {
        "accepted_for_carrier_intake": True,
        "context_proof_accepted": True,
        "template_action_proof_accepted": True,
    }
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    accepted_status = build_codex_queue_runner_status(tmp_path, reconcile=False)
    accepted_live = accepted_status["live_worker_telemetry"]
    assert accepted_live["phase_status"] == "terminal-accepted"
    assert accepted_live["terminal_intake_result"]["state"] == "accepted"
    assert accepted_live["terminal_intake_result"]["accepted_for_carrier_intake"] is True

    run["status"] = "RETURN_RECORDED_PROOF_BLOCKED"
    run["submit_result"] = {
        "accepted_for_carrier_intake": False,
        "context_proof_accepted": False,
        "template_action_proof_accepted": True,
    }
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    blocked_status = build_codex_queue_runner_status(tmp_path, reconcile=False)
    blocked_live = blocked_status["live_worker_telemetry"]
    assert blocked_live["phase_status"] == "terminal-blocked"
    assert blocked_live["terminal_intake_result"]["state"] == "blocked"
    assert blocked_live["terminal_intake_result"]["accepted_for_carrier_intake"] is False


def test_prepare_codex_queue_run_writes_prompt_and_receipt_without_claiming(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)

    prepared = prepare_codex_queue_run(tmp_path)

    assert prepared["ok"] is True
    assert prepared["prepared_only"] is True
    run = prepared["run"]
    assert (tmp_path / run["prompt_path"]).exists()
    assert (tmp_path / run["context_receipt_path"]).exists()
    prompt = (tmp_path / run["prompt_path"]).read_text(encoding="utf-8")
    assert request_rel in prompt
    assert 'request_kind: "codex_chat_response"' in prompt
    assert "ion_chat_engine:" in prompt
    assert 'selected_skill: "Codex Chat Answer"' in prompt
    assert "Persona: User-facing clarity." in prompt
    assert "codex_model_move:" in prompt
    assert 'selected_model: "gpt-5.5"' in prompt
    assert "worker_spawn_contract:" in prompt
    assert "agent_cwd_boundary:" in prompt
    assert "ion_runtime_budget:" in prompt
    assert "return_template: |" in prompt
    assert "result: <one-line result>" in prompt
    assert "touched_paths as a non-empty YAML list" in prompt
    assert run["codex_model_move"]["selected_model"] == "gpt-5.5"
    assert run["codex_command"][:8] == [
        "codex",
        "exec",
        "-C",
        str(tmp_path),
        "-m",
        "gpt-5.5",
        "-c",
        "model_reasoning_effort=medium",
    ]
    assert run["codex_cli_launch_profile"]["codex_cd_arg_present"] is True
    assert run["codex_cli_launch_profile"]["codex_cd_arg"] == str(tmp_path)
    assert run["codex_cli_launch_profile"]["subprocess_cwd"] == str(tmp_path)
    output_arg = run["codex_command"].index("--output-last-message") + 1
    assert Path(run["codex_command"][output_arg]).is_absolute()
    request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert request["status"] == "QUEUED_FOR_CODEX_CARRIER"


def test_prepare_codex_queue_run_records_ai_movement_gate_preflight(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    run = prepared["run"]
    preflight = run["ai_movement_preflight"]
    assert preflight["schema_id"] == "ion.codex_queue_runner_ai_movement_preflight.v1"
    assert preflight["accepted"] is True
    assert preflight["gate_decision"]["schema_id"] == "ion.ai_movement_gate_decision.v1"
    assert preflight["gate_decision"]["target_root_id"] == "active_ion_control"
    assert preflight["runner_start_allowed"] is True
    assert run["ai_movement_preflight_receipt_path"] == preflight["receipt_path"]
    assert preflight["root_envelope"]["agent_cwd_boundary"]["accepted"] is True
    assert run["worker_launch_cwd"] == str(tmp_path)
    assert run["target_command_cwd"] == str(tmp_path)
    assert (tmp_path / preflight["receipt_path"]).exists()
    assert run["worker_spawn_contract"]["ai_movement_gate_preflight"]["verdict"] == "ACCEPTED"
    prompt = (tmp_path / run["prompt_path"]).read_text(encoding="utf-8")
    assert "ai_movement_gate_preflight:" in prompt
    assert "agent_cwd_boundary:" in prompt
    assert 'verdict: "ACCEPTED"' in prompt
    status = build_codex_queue_runner_status(tmp_path, reconcile=False)
    warning_map = status["ai_movement_preflight_warning_map"]
    assert warning_map["schema_id"] == "ion.codex_queue_runner_ai_movement_preflight_warning_map.v1"
    assert warning_map["accepted_count"] == 1
    assert warning_map["blocked_count"] == 0
    assert warning_map["latest_preflight"]["target_root_id"] == "active_ion_control"
    assert warning_map["latest_preflight"]["agent_cwd_boundary_projection"]["warning_level"] == "ok"
    assert warning_map["latest_preflight"]["worker_launch_cwd"] == str(tmp_path)
    assert warning_map["agent_cwd_boundary_blocked_count"] == 0
    assert warning_map["agent_cwd_boundary_missing_count"] == 0
    assert status["live_worker_telemetry"]["ai_movement_gate_preflight"]["warning_level"] == "ok"


def test_prepare_codex_queue_run_launches_agent_work_from_portable_mount(tmp_path):
    _seed_root(tmp_path)
    mount = _seed_codex_agent_mount(tmp_path, "role_mason__domain_construction_routing_integration")
    request_rel = _seed_request(
        tmp_path,
        agent_role_id="role.mason",
        domain_id="domain.construction_routing_integration",
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    run = prepared["run"]
    envelope = run["ai_movement_preflight"]["root_envelope"]
    resolution = envelope["codex_agent_mount_resolution"]
    assert resolution["accepted"] is True
    assert resolution["mount_id"] == "role_mason__domain_construction_routing_integration"
    assert run["worker_launch_cwd"] == str(mount)
    assert run["target_command_cwd"] == str(mount)
    assert run["codex_project_cwd"] == str(tmp_path)
    assert run["codex_command"][:4] == ["codex", "exec", "-C", str(tmp_path)]
    launch_profile = run["codex_cli_launch_profile"]
    assert launch_profile["launch_policy"] == "active_root_codex_config_with_generated_mount_context"
    assert launch_profile["subprocess_cwd"] == str(tmp_path)
    assert launch_profile["codex_cd_arg"] == str(tmp_path)
    assert launch_profile["codex_config_path"] == str(tmp_path / ".codex/config.toml")
    assert launch_profile["codex_config_exists"] is True
    assert launch_profile["context_mount_cwd"] == str(mount)
    assert launch_profile["context_mount_config_path"] == str(mount / ".codex/config.toml")
    assert launch_profile["context_mount_config_exists"] is True
    assert run["domain_context_package"] == "ION/05_context/current/codex_agent_mounts/role_mason__domain_construction_routing_integration"
    assert run["agent_cwd_boundary"]["active_root_subdir_worker_launch_allowed"] is True
    assert "ION/05_context/current/codex_agent_mounts/role_mason__domain_construction_routing_integration/.ion/CAPSULE.md" in envelope["planned_reads"]
    prompt = (tmp_path / run["prompt_path"]).read_text(encoding="utf-8")
    assert "codex_launch_boundary:" in prompt
    assert f'codex_project_cwd: "{tmp_path}"' in prompt
    assert f'context_mount_cwd: "{mount}"' in prompt


def test_prepare_codex_queue_run_preserves_explicit_agent_mount_id(tmp_path):
    _seed_root(tmp_path)
    mount = _seed_codex_agent_mount(tmp_path, "role_atlas__domain_kernel_cartography")
    request_rel = _seed_request(
        tmp_path,
        ai_movement_root_envelope={"codex_agent_mount_id": mount.name},
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    run = prepared["run"]
    resolution = run["ai_movement_preflight"]["root_envelope"]["codex_agent_mount_resolution"]
    assert resolution["accepted"] is True
    assert resolution["source"] == "declared_codex_agent_mount"
    assert resolution["mount_id"] == mount.name
    assert resolution["mount_abspath"] == str(mount)
    assert run["codex_agent_mount_id"] == mount.name
    assert run["worker_launch_cwd"] == str(mount)
    assert run["target_command_cwd"] == str(mount)
    assert run["codex_project_cwd"] == str(tmp_path)


def test_prepare_codex_queue_run_blocks_stale_agent_mount_without_portable_context(tmp_path):
    _seed_root(tmp_path)
    mount = _seed_codex_agent_mount(
        tmp_path,
        "role_atlas__ion_vnext_front_door",
        portable_context=False,
    )
    request_rel = _seed_request(
        tmp_path,
        agent_role_id="role.atlas",
        domain_id="ion_vnext_front_door",
        ai_movement_root_envelope={
            "worker_launch_cwd": str(mount),
            "target_command_cwd": str(mount),
            "codex_agent_mount_manifest": str(mount / "ION_AGENT_MOUNT_MANIFEST.json"),
        },
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)

    assert prepared["ok"] is False
    assert prepared["result"] == "AI_MOVEMENT_GATE_REJECTED"
    preflight = prepared["ai_movement_preflight"]
    resolution = preflight["root_envelope"]["codex_agent_mount_resolution"]
    assert resolution["accepted"] is False
    assert resolution["status"] == "CODEX_AGENT_MOUNT_CONTEXT_MISSING"
    blocker_codes = {item["code"] for item in preflight["gate_decision"]["blockers"]}
    assert "CODEX_AGENT_MOUNT_CONTEXT_MISSING" in blocker_codes
    assert preflight["root_envelope"]["agent_cwd_boundary"]["accepted"] is False
    assert not (tmp_path / "ION/05_context/current/chatgpt_connector/codex_queue_runs").exists()


def test_prepare_codex_queue_run_rejects_legacy_request_without_target_policy(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path, target_root_id=None)

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)

    assert prepared["ok"] is False
    assert prepared["result"] == "AI_MOVEMENT_GATE_REJECTED"
    preflight = prepared["ai_movement_preflight"]
    assert preflight["accepted"] is False
    assert preflight["verdict"] == "BLOCKED"
    assert preflight["root_envelope"]["legacy_target_policy"]["status"] == "BLOCKED"
    assert preflight["root_envelope"]["legacy_target_policy"]["source"] == "legacy_default_active_ion_control"
    blocker_codes = {item["code"] for item in preflight["gate_decision"]["blockers"]}
    assert "LEGACY_QUEUE_REQUEST_TARGET_ROOT_MISSING" in blocker_codes
    run_dir = tmp_path / "ION/05_context/current/chatgpt_connector/codex_queue_runs"
    assert not run_dir.exists()
    request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert request["status"] == "CODEX_QUEUE_RUNNER_FAILED"
    assert request["failure_classification"] == "CARRIER_ADAPTER_FAILURE"


def test_prepare_codex_queue_run_accepts_path_inferred_target_policy(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        target_root_id=None,
        planned_writes=["ION_GPT/01_GPT_BUILDER_INPUTS/README.md"],
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    envelope = prepared["run"]["ai_movement_preflight"]["root_envelope"]
    assert envelope["target_root_id"] == "ion_gpt"
    assert envelope["legacy_target_policy"]["accepted"] is True
    assert envelope["legacy_target_policy"]["source"] == "request.planned_writes"
    assert envelope["planned_writes"] == ["ION_GPT/01_GPT_BUILDER_INPUTS/README.md"]


def test_prepare_codex_queue_run_rejects_blocked_ai_movement_gate_preflight(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        ai_movement_root_envelope={
            "actual_cwd": str(tmp_path.parent),
            "actual_realpath": str(tmp_path.parent),
        },
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)

    assert prepared["ok"] is False
    assert prepared["result"] == "AI_MOVEMENT_GATE_REJECTED"
    preflight = prepared["ai_movement_preflight"]
    assert preflight["accepted"] is False
    assert preflight["verdict"] == "BLOCKED"
    assert (tmp_path / prepared["ai_movement_preflight_receipt_path"]).exists()
    blocker_codes = {item["code"] for item in preflight["gate_decision"]["blockers"]}
    assert "WRONG_ROOT_CWD" in blocker_codes
    assert "EXPECTED_REALPATH_MISMATCH" in blocker_codes
    request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert request["status"] == "CODEX_QUEUE_RUNNER_FAILED"
    assert request["failure_classification"] == "CARRIER_ADAPTER_FAILURE"
    run_dir = tmp_path / "ION/05_context/current/chatgpt_connector/codex_queue_runs"
    assert not run_dir.exists()
    status = build_codex_queue_runner_status(tmp_path, reconcile=False)
    warning_map = status["ai_movement_preflight_warning_map"]
    assert warning_map["blocked_count"] == 1
    assert warning_map["operator_warning_count"] >= 1
    assert warning_map["latest_preflight"]["warning_level"] == "blocked"
    assert "AI_MOVEMENT_GATE_BLOCKED" in {row["code"] for row in warning_map["warning_rows"]}


def test_prepare_codex_queue_run_compiles_browser_extension_movement_envelope(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        target_root_id="browser_extension",
        target_project_subpath="ion_chatops_bridge",
        planned_writes=["src/content.ts"],
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    preflight = prepared["run"]["ai_movement_preflight"]
    envelope = preflight["root_envelope"]
    assert preflight["accepted"] is True
    assert envelope["target_root_id"] == "browser_extension"
    assert envelope["movement_class"] == "BROWSER_EXTENSION_MOVEMENT"
    assert envelope["target_project_root"].endswith("/browser_extension/ion_chatops_bridge")
    assert envelope["agent_cwd_boundary"]["worker_launch_cwd"].endswith("/browser_extension/ion_chatops_bridge")
    assert envelope["agent_cwd_boundary"]["target_command_cwd"].endswith("/browser_extension/ion_chatops_bridge")
    assert prepared["run"]["worker_launch_cwd"].endswith("/browser_extension/ion_chatops_bridge")
    assert envelope["planned_writes"] == ["browser_extension/ion_chatops_bridge/src/content.ts"]
    assert envelope["control_plane_receipt_writes"]
    assert all(not path.startswith("ION/05_context/current/chatgpt_connector/codex_queue_runs") for path in envelope["planned_writes"])
    assert preflight["gate_decision"]["target_root_id"] == "browser_extension"


def test_prepare_codex_queue_run_compiles_ion_gpt_movement_envelope(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        target_root_id="ion_gpt",
        planned_writes=["01_GPT_BUILDER_INPUTS/README.md"],
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    envelope = prepared["run"]["ai_movement_preflight"]["root_envelope"]
    assert envelope["target_root_id"] == "ion_gpt"
    assert envelope["movement_class"] == "CUSTOM_GPT_RELEASE_MOVEMENT"
    assert envelope["agent_cwd_boundary"]["worker_launch_cwd"].endswith("/ION_GPT")
    assert envelope["planned_writes"] == ["ION_GPT/01_GPT_BUILDER_INPUTS/README.md"]
    assert prepared["run"]["ai_movement_preflight"]["gate_decision"]["target_root_id"] == "ion_gpt"


def test_prepare_codex_queue_run_compiles_daimon_movement_envelope(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        target_root_id="dAimon",
        planned_writes=["src/agent.py"],
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    envelope = prepared["run"]["ai_movement_preflight"]["root_envelope"]
    assert envelope["target_root_id"] == "daimon"
    assert envelope["movement_class"] == "DAIMON_PROJECT_MOVEMENT"
    assert envelope["target_project_root"].endswith("/dAimon")
    assert envelope["agent_cwd_boundary"]["worker_launch_cwd"].endswith("/dAimon")
    assert envelope["planned_writes"] == ["dAimon/src/agent.py"]
    assert prepared["run"]["ai_movement_preflight"]["gate_decision"]["target_root_id"] == "daimon"


def test_prepare_codex_queue_run_compiles_export_artifact_envelope(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        target_root_id="ion_exports_local",
        planned_artifacts=["package.zip"],
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    envelope = prepared["run"]["ai_movement_preflight"]["root_envelope"]
    assert envelope["target_root_id"] == "ion_exports_local"
    assert envelope["movement_class"] == "EXPORT_PACKAGE_MOVEMENT"
    assert envelope["agent_cwd_boundary"]["worker_launch_cwd"] == str(tmp_path)
    assert envelope["planned_artifacts"] == ["ION_EXPORTS_LOCAL/package.zip"]
    assert prepared["run"]["ai_movement_preflight"]["gate_decision"]["target_root_id"] == "ion_exports_local"


def test_prepare_codex_queue_run_rejects_sibling_movement_write_mismatch(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        target_root_id="browser_extension",
        planned_writes=["ION_GPT/01_GPT_BUILDER_INPUTS/README.md"],
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is False
    assert prepared["result"] == "AI_MOVEMENT_GATE_REJECTED"
    preflight = prepared["ai_movement_preflight"]
    assert preflight["root_envelope"]["movement_class"] == "BROWSER_EXTENSION_MOVEMENT"
    blocker_codes = {item["code"] for item in preflight["gate_decision"]["blockers"]}
    assert "SIBLING_ROOT_IMPLICIT_EDIT" in blocker_codes


def test_prepare_codex_queue_run_writes_machine_generated_worker_context_awareness_receipt(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    run = prepared["run"]
    receipt_path = tmp_path / run["worker_context_awareness_receipt_path"]
    assert receipt_path.exists()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["schema_id"] == "ion.worker_context_awareness_receipt.v1"
    assert receipt["generated_by"] == "runner_or_control_plane"
    assert receipt["worker_authored"] is False
    assert receipt["status"] == "WORKER_CONTEXT_ACKNOWLEDGED"
    assert receipt["prompt_path"] == run["prompt_path"]
    assert receipt["run_packet_path"] == run["run_packet_path"]
    assert receipt["context_receipt_path"] == run["context_receipt_path"]
    assert isinstance(receipt["prompt_sha256"], str) and len(receipt["prompt_sha256"]) == 64
    assert isinstance(receipt["run_packet_sha256"], str) and len(receipt["run_packet_sha256"]) == 64
    assert isinstance(receipt["context_receipt_sha256"], str) and len(receipt["context_receipt_sha256"]) == 64
    assert receipt["agent_cwd_boundary"]["accepted"] is True
    assert receipt["worker_launch_cwd"] == run["worker_launch_cwd"]
    assert receipt["target_command_cwd"] == run["target_command_cwd"]
    assert isinstance(receipt["machine_attestation_sha256"], str) and len(receipt["machine_attestation_sha256"]) == 64
    assert receipt["required_context_reads"]
    assert all(row["status"] == "READY" for row in receipt["required_context_reads"])


def test_prepare_codex_queue_run_applies_requested_codex_model_override(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        codex_model_override={
            "selected_model": "gpt-5.5",
            "selected_reasoning_effort": "medium",
            "reason": "proof repair requires explicit model route",
        },
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    run = prepared["run"]
    assert run["codex_model_move"]["selected_model"] == "gpt-5.5"
    assert run["codex_model_move"]["selected_reasoning_effort"] == "medium"
    assert run["codex_command"][:8] == [
        "codex",
        "exec",
        "-C",
        str(tmp_path),
        "-m",
        "gpt-5.5",
        "-c",
        "model_reasoning_effort=medium",
    ]
    override_receipt = run["codex_model_override_receipt"]
    assert override_receipt["requested"] is True
    assert override_receipt["applied"] is True
    assert override_receipt["source"] == "request.codex_model_override"
    assert override_receipt["reason"] == "proof repair requires explicit model route"
    assert run["codex_model_move"]["model_override"]["source"] == "request.codex_model_override"


def test_prepare_codex_queue_run_applies_requested_service_tier_fast(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        codex_model_override={
            "selected_model": "gpt-5.5",
            "selected_reasoning_effort": "xhigh",
            "reason": "dynamic swarm lane uses fast service tier",
        },
        requested_service_tier="fast",
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    run = prepared["run"]
    assert run["codex_service_tier"] == "fast"
    assert "-c" in run["codex_command"]
    assert "service_tier=fast" in run["codex_command"]


def test_prepare_codex_queue_run_rejects_requested_account_rejected_spark_model(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        requested_model="gpt-5.3-codex-spark",
        requested_reasoning_effort="medium",
        model_override_reason="bounded fast lane test",
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is False
    assert prepared["result"] == "MODEL_OVERRIDE_INVALID"
    assert prepared["finding"] == "chatgpt_account_rejected_codex_model"
    override_receipt = prepared["model_override_receipt"]
    assert override_receipt["requested"] is True
    assert override_receipt["applied"] is False
    assert override_receipt["source"] == "request.requested_model_fields"
    assert override_receipt["reason"] == "bounded fast lane test"
    assert override_receipt["replacement_model"] == "gpt-5.5"


def test_prepare_codex_queue_run_threads_work_class_and_risk_into_model_move(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        objective="Nemesis adversarial review of queue model routing.",
        work_class="adversarial_review",
        risk_level="high",
        include_codex_model_move=False,
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    run = prepared["run"]
    assert run["codex_model_move"]["work_class"] == "adversarial_review"
    assert run["codex_model_move"]["risk_level"] == "high"
    assert run["codex_model_move"]["selected_model"] == "gpt-5.5"
    assert run["codex_model_move"]["selected_reasoning_effort"] == "high"


def test_prepare_codex_queue_run_rejects_unknown_requested_model_override(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        codex_model_override={
            "selected_model": "gpt-not-real",
            "selected_reasoning_effort": "medium",
            "reason": "negative test",
        },
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is False
    assert prepared["result"] == "MODEL_OVERRIDE_INVALID"
    assert prepared["finding"] == "unknown_requested_model"
    receipt = prepared["model_override_receipt"]
    assert receipt["requested"] is True
    assert receipt["applied"] is False
    assert receipt["validation"]["finding"] == "unknown_requested_model"


def test_prepare_codex_queue_run_rejects_unknown_requested_reasoning_effort(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        codex_model_override={
            "selected_model": "gpt-5.5",
            "selected_reasoning_effort": "turbo",
            "reason": "negative test",
        },
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is False
    assert prepared["result"] == "MODEL_OVERRIDE_INVALID"
    assert prepared["finding"] == "unknown_requested_reasoning_effort"
    receipt = prepared["model_override_receipt"]
    assert receipt["requested"] is True
    assert receipt["applied"] is False
    assert receipt["validation"]["finding"] == "unknown_requested_reasoning_effort"


def test_prepare_codex_queue_run_rejects_red_alert_prose_without_structured_route(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        objective="RED ALERT: authority route repair without structured metadata",
        idempotency_key="red-alert-prose-only",
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is False
    assert prepared["result"] == "ROUTE_ENFORCEMENT_REJECTED"
    assert prepared["finding"] == "structured_route_metadata_required_for_high_stakes_objective"
    assert prepared["route_enforcement_receipt"]["prose_guardrail_triggered"] is True


def test_prepare_codex_queue_run_rejects_high_stakes_without_structured_model_override(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        work_class="authority_security",
        risk_level="critical",
        route_family="authority_security",
        idempotency_key="authority-security-missing-model",
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is False
    assert prepared["result"] == "ROUTE_ENFORCEMENT_REJECTED"
    assert prepared["route_enforcement_receipt"]["high_stakes"] is True
    assert "high_stakes_codex_model_override_selected_model_must_be_gpt_5_5" in prepared["route_enforcement_receipt"]["findings"]


def test_prepare_codex_queue_run_records_route_enforcement_receipt_for_red_alert(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        objective="Structured red-alert route",
        work_class="red_alert",
        risk_level="red_alert",
        route_family="red_alert",
        idempotency_key="red-alert-run-positive",
        codex_model_override={
            "selected_model": "gpt-5.5",
            "selected_reasoning_effort": "high",
            "reason": "red-alert queue runner route",
        },
        requested_model="gpt-5.5",
        requested_reasoning_effort="high",
        model_override_reason="red-alert queue runner route",
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    run = prepared["run"]
    assert run["route_enforcement_receipt"]["high_stakes"] is True
    assert run["route_enforcement_receipt"]["model_override_receipt_required"] is True
    assert run["codex_model_override_receipt"]["requested"] is True
    assert run["codex_model_move"]["selected_model"] == "gpt-5.5"
    assert run["codex_model_move"]["selected_reasoning_effort"] == "high"


def test_prepare_codex_queue_run_includes_workload_diff_for_agent_cartography_contract(tmp_path):
    _seed_root(tmp_path)
    _seed_request(tmp_path)
    request_rel = _seed_agent_cartography_request(tmp_path)

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    prompt = (tmp_path / prepared["run"]["prompt_path"]).read_text(encoding="utf-8")
    assert "### WORKLOAD DIFF" in prompt


def test_prepare_codex_queue_run_carries_worker_identity_root_proof_and_return_status(tmp_path):
    _seed_root(tmp_path)
    _seed_codex_agent_mount(tmp_path, "role_turing__domain_parallel_execution")
    request_rel = _seed_request(
        tmp_path,
        work_class="implementation",
        agent_role_id="role.turing",
        domain_id="domain.parallel_execution",
        role_tier="R6_RUNTIME_IMPLEMENTER",
        callsign="Turing",
    )

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel)

    assert prepared["ok"] is True
    run = prepared["run"]
    assert run["active_root_proof"]["proof_ok"] is True
    assert run["worker_identity"]["lane_id"] == "implementation_lane"
    assert run["worker_identity"]["domain_id"] == "domain.parallel_execution"
    assert run["worker_identity"]["role_id"] == "role.turing"
    assert run["worker_identity"]["role_tier"] == "R6_RUNTIME_IMPLEMENTER"
    assert run["worker_identity"]["callsign"] == "Turing"
    assert run["domain_alignment"]["target_request_domain_id"] == "domain.parallel_execution"
    assert run["domain_alignment"]["prestart_domain_checked"] == "domain.parallel_execution"
    assert run["worker_return_status"]["run_status"] == "PREPARED_NOT_STARTED"
    assert run["worker_return_status"]["carrier_intake_only"] is True
    assert run["worker_return_status"]["product_state"] is False
    assert prepared["context_receipt"]["active_root_proof"]["proof_ok"] is True
    assert prepared["context_receipt"]["worker_identity"]["callsign"] == "Turing"
    assert run["worker_spawn_contract"]["worker_identity"]["role_tier"] == "R6_RUNTIME_IMPLEMENTER"


def test_process_once_context_gate_block_preserves_identity_domain_and_blockers(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        work_class="implementation",
        agent_role_id="role.turing",
        domain_id="domain.parallel_execution",
        role_tier="R6_RUNTIME_IMPLEMENTER",
        callsign="Turing",
    )

    result = process_codex_queue_once(
        tmp_path,
        request_path=request_rel,
        start=True,
        background=False,
        task_output_override=_valid_task_return(DEFAULT_CONTEXT_READS),
    )

    assert result["ok"] is False
    assert result["result"] == "WORKER_START_CONTEXT_GATE_BLOCKED"
    assert result["active_root_proof"]["proof_ok"] is True
    assert result["worker_identity"]["role_id"] == "role.turing"
    assert result["worker_identity"]["role_tier"] == "R6_RUNTIME_IMPLEMENTER"
    assert result["worker_identity"]["callsign"] == "Turing"
    assert result["domain_alignment"]["target_request_domain_id"] == "domain.parallel_execution"
    assert result["worker_return_status"]["carrier_intake_only"] is True
    assert result["worker_return_status"]["product_state"] is False
    assert "worker_start_context_active_resolver_blocked" in result["worker_return_status"]["blockers"]
    assert "no_matching_active_context_mount_for_lane" in result["worker_return_status"]["blockers"]


def test_process_once_retries_transient_codex_usage_limit_bug_once(tmp_path, monkeypatch):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        idempotency_key="transient-usage-limit-retry",
    )
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    required_paths = [item["path"] for item in prepared["context_receipt"]["required_context_reads"]]
    calls = []

    class Completed:
        def __init__(self, returncode, stdout, stderr):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def fake_run(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        if len(calls) == 1:
            return Completed(
                1,
                "",
                "ERROR: You've hit your usage limit. Upgrade to Pro, visit codex/settings/usage to purchase more credits or try again at Jun 4th, 2026 1:33 AM.",
            )
        return Completed(0, _valid_task_return(required_paths), "")

    monkeypatch.setattr("kernel.ion_codex_queue_runner.subprocess.run", fake_run)

    result = run_codex_queue_worker(tmp_path, prepared["run"]["run_packet_path"])

    assert result["ok"] is True
    assert len(calls) == 2
    run = result["run"]
    assert run["status"] == "RETURN_RECORDED_PROOF_ACCEPTED"
    assert run["codex_transient_usage_limit_retries"][0]["finding"] == "codex_cli_reported_usage_limit_but_operator_identified_transient_bug"
    assert any(event["event"] == "codex_cli_transient_usage_limit_retry" for event in run["worker_lifecycle_events"])
    assert run["worker_return_status"]["product_state"] is False


def test_process_once_uses_active_root_subprocess_cwd_for_generated_agent_mount(tmp_path, monkeypatch):
    _seed_root(tmp_path)
    mount = _seed_codex_agent_mount(tmp_path, "role_context_cartographer__domain_agent_communication_systems")
    request_rel = _seed_request(
        tmp_path,
        idempotency_key="generated-mount-active-root-codex-project-cwd",
        agent_role_id="role.context_cartographer",
        domain_id="domain.agent_communication_systems",
    )
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    required_paths = [item["path"] for item in prepared["context_receipt"]["required_context_reads"]]
    calls = []

    class Completed:
        returncode = 0
        stderr = ""

        def __init__(self, stdout):
            self.stdout = stdout

    def fake_run(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return Completed(_valid_task_return(required_paths))

    monkeypatch.setattr("kernel.ion_codex_queue_runner.subprocess.run", fake_run)

    result = run_codex_queue_worker(tmp_path, prepared["run"]["run_packet_path"])

    assert result["ok"] is True
    assert calls
    assert calls[0]["kwargs"]["cwd"] == tmp_path
    command = list(calls[0]["args"][0])
    assert command[:4] == ["codex", "exec", "-C", str(tmp_path)]
    run = result["run"]
    assert run["worker_launch_cwd"] == str(mount)
    assert run["codex_project_cwd"] == str(tmp_path)
    assert run["codex_cli_launch_profile"]["launch_policy"] == "active_root_codex_config_with_generated_mount_context"


def test_process_once_prompts_through_transient_usage_limit_with_saved_session(
    tmp_path,
    monkeypatch,
):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        idempotency_key="transient-usage-limit-prompt-through",
    )
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    required_paths = [item["path"] for item in prepared["context_receipt"]["required_context_reads"]]
    run_path = tmp_path / prepared["run"]["run_packet_path"]
    run_packet = json.loads(run_path.read_text(encoding="utf-8"))
    run_packet["codex_resume_session_id"] = "019eabcd-1111-2222-3333-555555555555"
    run_path.write_text(json.dumps(run_packet, indent=2), encoding="utf-8")
    calls = []
    resume_calls = []

    class Completed:
        returncode = 1
        stdout = ""
        stderr = "ERROR: You've hit your usage limit. Upgrade to Pro, visit codex/settings/usage to purchase more credits or try again at Jun 4th, 2026 1:33 AM."

    def fake_run(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return Completed()

    def fake_resume_route(root, *, route_id, args):
        resume_calls.append({"root": root, "route_id": route_id, "args": dict(args)})
        stdout_rel = (
            "ION/05_context/current/chatgpt_connector/codex_session_store_runs/"
            "019eabcd-1111-2222-3333-555555555555/runs/prompt-through/stdout.txt"
        )
        stdout_path = tmp_path / stdout_rel
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text(_valid_task_return(required_paths), encoding="utf-8")
        return {
            "ok": True,
            "returncode": 0,
            "timed_out": False,
            "receipt_path": stdout_rel.replace("stdout.txt", "run_receipt.json"),
            "stdout_path": stdout_rel,
            "stderr_path": stdout_rel.replace("stdout.txt", "stderr.txt"),
            "line_count_delta": 4,
            "message_count_delta": 1,
            "driver_mode": "tui_inline",
            "driver_label": "codex_resume_tui_inline_no_alt_screen",
        }

    monkeypatch.setattr("kernel.ion_codex_queue_runner.subprocess.run", fake_run)
    monkeypatch.setattr(session_bridge, "invoke_codex_session_store_route", fake_resume_route)

    result = run_codex_queue_worker(tmp_path, prepared["run"]["run_packet_path"])

    assert result["ok"] is True
    assert len(calls) == 1
    assert len(resume_calls) == 1
    resume_args = resume_calls[0]["args"]
    assert resume_calls[0]["route_id"] == "session_resume_send"
    assert resume_args["prompt"] == "continue"
    assert resume_args["driver_mode"] == "tui_inline"
    assert resume_args["sandbox_mode"] == "workspace-write"
    assert resume_args["session_id"] == "019eabcd-1111-2222-3333-555555555555"
    run = result["run"]
    assert run["status"] == "RETURN_RECORDED_PROOF_ACCEPTED"
    prompt_through = run["codex_transient_usage_limit_prompt_through"][0]
    assert prompt_through["attempted"] is True
    assert prompt_through["ok"] is True
    assert prompt_through["session_resolution"]["source"] == "run_packet_explicit_session_id"
    assert any(
        event["event"] == "codex_cli_transient_usage_limit_prompt_through"
        for event in run["worker_lifecycle_events"]
    )
    assert run["worker_return_status"]["product_state"] is False


def test_process_once_repeats_prompt_through_when_continue_advances_without_output(
    tmp_path,
    monkeypatch,
):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        idempotency_key="transient-usage-limit-prompt-through-repeat",
    )
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    required_paths = [item["path"] for item in prepared["context_receipt"]["required_context_reads"]]
    run_path = tmp_path / prepared["run"]["run_packet_path"]
    run_packet = json.loads(run_path.read_text(encoding="utf-8"))
    run_packet["codex_resume_session_id"] = "019eabcd-1111-2222-3333-666666666666"
    run_path.write_text(json.dumps(run_packet, indent=2), encoding="utf-8")
    calls = []
    resume_calls = []

    class Completed:
        returncode = 1
        stdout = ""
        stderr = "ERROR: You've hit your usage limit. Upgrade to Pro, visit codex/settings/usage to purchase more credits or try again at Jun 4th, 2026 1:33 AM."

    def fake_run(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return Completed()

    def fake_resume_route(root, *, route_id, args):
        resume_calls.append({"root": root, "route_id": route_id, "args": dict(args)})
        assert args["timeout_seconds"] == runner.CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_TIMEOUT_SECONDS
        if len(resume_calls) == 1:
            return {
                "ok": False,
                "finding": "codex_resume_send_failed_or_timed_out",
                "returncode": -9,
                "timed_out": True,
                "receipt_path": "ION/05_context/current/chatgpt_connector/codex_session_store_runs/repeat/first.json",
                "line_count_delta": 7,
                "message_count_delta": 3,
                "driver_mode": "tui_inline",
                "driver_label": "codex_resume_tui_inline_no_alt_screen",
            }
        stdout_rel = (
            "ION/05_context/current/chatgpt_connector/codex_session_store_runs/"
            "019eabcd-1111-2222-3333-666666666666/runs/prompt-through-2/stdout.txt"
        )
        stdout_path = tmp_path / stdout_rel
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text(_valid_task_return(required_paths), encoding="utf-8")
        return {
            "ok": True,
            "returncode": 0,
            "timed_out": False,
            "receipt_path": stdout_rel.replace("stdout.txt", "run_receipt.json"),
            "stdout_path": stdout_rel,
            "stderr_path": stdout_rel.replace("stdout.txt", "stderr.txt"),
            "line_count_delta": 4,
            "message_count_delta": 1,
            "driver_mode": "tui_inline",
            "driver_label": "codex_resume_tui_inline_no_alt_screen",
        }

    monkeypatch.setattr("kernel.ion_codex_queue_runner.subprocess.run", fake_run)
    monkeypatch.setattr(session_bridge, "invoke_codex_session_store_route", fake_resume_route)

    result = run_codex_queue_worker(tmp_path, prepared["run"]["run_packet_path"])

    assert result["ok"] is True
    assert len(calls) == 1
    assert len(resume_calls) == 2
    assert resume_calls[0]["args"]["idempotency_key"].endswith("usage-limit-prompt-through-1")
    assert resume_calls[1]["args"]["idempotency_key"].endswith("usage-limit-prompt-through-2")
    run = result["run"]
    assert run["status"] == "RETURN_RECORDED_PROOF_ACCEPTED"
    assert run["codex_transient_usage_limit_prompt_through"][0]["ok"] is False
    assert run["codex_transient_usage_limit_prompt_through"][1]["ok"] is True


def test_process_once_stops_prompt_through_when_continue_hits_usage_limit_again(
    tmp_path,
    monkeypatch,
):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        idempotency_key="transient-usage-limit-prompt-through-recurrent-usage",
    )
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run_path = tmp_path / prepared["run"]["run_packet_path"]
    run_packet = json.loads(run_path.read_text(encoding="utf-8"))
    run_packet["codex_resume_session_id"] = "019eabcd-1111-2222-3333-777777777777"
    run_path.write_text(json.dumps(run_packet, indent=2), encoding="utf-8")
    calls = []
    resume_calls = []

    class Completed:
        returncode = 1
        stdout = ""
        stderr = "ERROR: You've hit your usage limit. Upgrade to Pro, visit codex/settings/usage to purchase more credits or try again at Jun 4th, 2026 1:33 AM."

    def fake_run(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return Completed()

    def fake_resume_route(root, *, route_id, args):
        resume_calls.append({"root": root, "route_id": route_id, "args": dict(args)})
        stdout_rel = (
            "ION/05_context/current/chatgpt_connector/codex_session_store_runs/"
            "019eabcd-1111-2222-3333-777777777777/runs/prompt-through-usage/stdout.txt"
        )
        stdout_path = tmp_path / stdout_rel
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text(
            "› continue\n■ You've hit your usage limit. Upgrade to Pro, visit "
            "https://chatgpt.com/codex/settings/usage to purchase more credits "
            "or try again at 6:00 PM.\n",
            encoding="utf-8",
        )
        return {
            "ok": False,
            "finding": "codex_resume_send_failed_or_timed_out",
            "returncode": 0,
            "timed_out": True,
            "receipt_path": stdout_rel.replace("stdout.txt", "run_receipt.json"),
            "stdout_path": stdout_rel,
            "stderr_path": stdout_rel.replace("stdout.txt", "stderr.txt"),
            "line_count_delta": 7,
            "message_count_delta": 3,
            "driver_mode": "tui_inline",
            "driver_label": "codex_resume_tui_inline_no_alt_screen",
        }

    monkeypatch.setattr("kernel.ion_codex_queue_runner.subprocess.run", fake_run)
    monkeypatch.setattr(session_bridge, "invoke_codex_session_store_route", fake_resume_route)

    result = run_codex_queue_worker(tmp_path, prepared["run"]["run_packet_path"])

    assert result["ok"] is False
    assert len(calls) == 1
    assert len(resume_calls) == 1
    run = result["run"]
    assert run["status"] == runner.CODEX_TRANSIENT_USAGE_LIMIT_BUG_STATUS
    assert run["failure_classification"] == runner.CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS
    prompt_through = run["codex_transient_usage_limit_prompt_through"][0]
    assert prompt_through["ok"] is False
    assert prompt_through["route_output_usage_limit_recurred"] is True
    assert run.get("codex_transient_usage_limit_retries") is None


def test_accepted_domain_weaver_comms_task_return_syncs_reply(tmp_path):
    _seed_root(tmp_path)
    source = send_agent_message(
        tmp_path,
        {
            "from_role": "role.chatgpt_browser",
            "to_roles": ["role.context_cartographer"],
            "channel_id": "team",
            "subject": "Domain Weaver source comms",
            "body": "Please inspect this source message.",
            "message_kind": "thread_note",
            "emit_signal": True,
        },
    )
    request_rel = _seed_request(
        tmp_path,
        idempotency_key="domain-weaver-comms-accepted-sync",
        agent_role_id="role.context_cartographer",
        domain_id="domain.agent_communication_systems",
    )
    request_path = tmp_path / request_rel
    request = json.loads(request_path.read_text(encoding="utf-8"))
    request["domain_weaver_agent_comms_dispatch"] = {
        "source_agent_comms_message_id": source["message_id"],
        "source_agent_comms_message_path": source["message_path"],
        "source_agent_comms_thread_id": source["thread_id"],
        "source_agent_comms_thread_path": source["thread_path"],
        "pickup_receipt_path": "ION/05_context/current/agent_comms/receipts/pickups/test_pickup.json",
    }
    request["source_agent_comms_message_id"] = source["message_id"]
    request["source_agent_comms_thread_id"] = source["thread_id"]
    request_path.write_text(json.dumps(request, indent=2), encoding="utf-8")

    _seed_codex_agent_mount(tmp_path, "role_context_cartographer__domain_agent_communication_systems")
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    required_paths = [item["path"] for item in prepared["context_receipt"]["required_context_reads"]]

    result = run_codex_queue_worker(
        tmp_path,
        prepared["run"]["run_packet_path"],
        task_output_override=_valid_task_return(required_paths),
    )

    assert result["ok"] is True
    run = result["run"]
    sync = run["domain_weaver_agent_comms_synced_reply"]
    assert sync["ok"] is True
    assert sync["source_message_id"] == source["message_id"]
    assert sync["sync_kind"] == "synced_reply"
    assert sync["task_return_packet_path"] == run["latest_return_packet_path"]
    assert (tmp_path / sync["synced_reply_message_path"]).is_file()
    reply = json.loads((tmp_path / sync["synced_reply_message_path"]).read_text(encoding="utf-8"))
    assert reply["message_kind"] == "answer"
    assert run["latest_return_packet_path"] in reply["source_refs"]
    assert run["worker_return_status"]["product_state"] is False


def test_process_once_classifies_transient_codex_usage_limit_retry_exhausted(tmp_path, monkeypatch):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        idempotency_key="transient-usage-limit-exhausted",
    )
    calls = []

    class Completed:
        returncode = 1
        stdout = ""
        stderr = "ERROR: You've hit your usage limit. Upgrade to Pro, visit codex/settings/usage to purchase more credits or try again at Jun 4th, 2026 1:33 AM."

    def fake_run(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return Completed()

    monkeypatch.setattr("kernel.ion_codex_queue_runner.subprocess.run", fake_run)

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    result = run_codex_queue_worker(tmp_path, prepared["run"]["run_packet_path"])

    assert result["ok"] is False
    assert result["result"] == "CODEX_CLI_TRANSIENT_USAGE_LIMIT_BUG_RETRY_EXHAUSTED"
    assert len(calls) == 2
    run = result["run"]
    assert run["status"] == "CODEX_CLI_TRANSIENT_USAGE_LIMIT_BUG_RETRY_EXHAUSTED"
    assert run["failure_classification"] == "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BUG"
    assert run["codex_transient_usage_limit_bug"]["operator_reported_actual_usage_exhausted"] is False
    assert run["worker_return_status"]["failure_classification"] == "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BUG"
    request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert request["status"] == "CODEX_QUEUE_RUNNER_FAILED"
    assert request["failure_classification"] == "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BUG"


def test_requeue_transient_codex_usage_limit_request_preserves_source_run(tmp_path, monkeypatch):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        idempotency_key="transient-usage-limit-recovery",
    )

    class Completed:
        returncode = 1
        stdout = ""
        stderr = "ERROR: You've hit your usage limit. Upgrade to Pro, visit codex/settings/usage to purchase more credits or try again at Jun 4th, 2026 1:33 AM."

    monkeypatch.setattr("kernel.ion_codex_queue_runner.subprocess.run", lambda *args, **kwargs: Completed())

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    failed = run_codex_queue_worker(tmp_path, prepared["run"]["run_packet_path"])
    source_run_rel = failed["run"]["run_packet_path"]

    result = requeue_codex_transient_usage_limit_request(
        tmp_path,
        run_packet_path=source_run_rel,
        confirmation=runner.CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_CONFIRMATION,
    )

    assert result["ok"] is True
    assert result["result"] == "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_RECOVERY_REQUEUED"
    assert result["carrier_session_recovery"]["source_run_packet_path"] == source_run_rel
    assert result["carrier_session_recovery"]["request_path"] == request_rel
    assert result["carrier_session_recovery"]["accepted_state_claim"] is False
    assert (tmp_path / result["receipt_path"]).exists()
    request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert request["status"] == "QUEUED_FOR_CODEX_CARRIER"
    assert "failure_classification" not in request
    assert request["last_failure_classification"] == "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BUG"
    assert request["carrier_session_recovery_history"][0]["source_run_packet_path"] == source_run_rel
    source_run = json.loads((tmp_path / source_run_rel).read_text(encoding="utf-8"))
    assert source_run["status"] == "CODEX_CLI_TRANSIENT_USAGE_LIMIT_BUG_RETRY_EXHAUSTED"
    assert source_run["failure_classification"] == "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BUG"
    assert source_run["worker_return_status"]["product_state"] is False
    trace = runner.build_codex_worker_observability_trace(tmp_path, run=source_run, run_rel=source_run_rel)
    assert trace["carrier_session_recovery"]["eligible"] is True
    assert "fresh_worker_shift_lease_on_next_start" in trace["carrier_session_recovery"]["proof_requirements"]

    repeated = requeue_codex_transient_usage_limit_request(
        tmp_path,
        run_packet_path=source_run_rel,
        confirmation=runner.CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_CONFIRMATION,
    )

    assert repeated["ok"] is True
    assert repeated["result"] == "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_RECOVERY_ALREADY_REQUEUED"

    request["status"] = "CODEX_QUEUE_RUNNER_FAILED"
    request["failure_classification"] = "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BUG"
    (tmp_path / request_rel).write_text(json.dumps(request, indent=2), encoding="utf-8")
    exhausted = requeue_codex_transient_usage_limit_request(
        tmp_path,
        run_packet_path=source_run_rel,
        confirmation=runner.CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_CONFIRMATION,
    )

    assert exhausted["ok"] is False
    assert exhausted["result"] == "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_RECOVERY_EXHAUSTED"
    assert exhausted["recovery_count"] == runner.MAX_CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_REQUEUES
    exhausted_trace = runner.build_codex_worker_observability_trace(tmp_path, run=source_run, run_rel=source_run_rel)
    assert exhausted_trace["carrier_session_recovery"]["eligible"] is False
    assert exhausted_trace["carrier_session_recovery"]["recovery_exhausted"] is True
    assert exhausted_trace["next_recommended_action"].startswith("Do not requeue this request again")


def test_requeue_transient_usage_limit_blocks_when_same_request_active(tmp_path, monkeypatch):
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        idempotency_key="transient-usage-limit-recovery-active",
    )

    class Completed:
        returncode = 1
        stdout = ""
        stderr = "ERROR: You've hit your usage limit. Upgrade to Pro, visit codex/settings/usage to purchase more credits or try again at Jun 4th, 2026 1:33 AM."

    monkeypatch.setattr("kernel.ion_codex_queue_runner.subprocess.run", lambda *args, **kwargs: Completed())

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    failed = run_codex_queue_worker(tmp_path, prepared["run"]["run_packet_path"])
    source_run_rel = failed["run"]["run_packet_path"]
    state_path = tmp_path / runner.RUNNER_STATE_PATH
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_runs": [
                    {
                        "request_path": request_rel,
                        "run_packet_path": source_run_rel,
                        "lane_id": failed["run"]["lane_id"],
                        "pid": 999999,
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = requeue_codex_transient_usage_limit_request(
        tmp_path,
        run_packet_path=source_run_rel,
        confirmation=runner.CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_CONFIRMATION,
    )

    assert result["ok"] is False
    assert result["result"] == "ACTIVE_SAME_REQUEST_WORKER_PRESENT"
    request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert request["status"] == "CODEX_QUEUE_RUNNER_FAILED"
    assert request["failure_classification"] == "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BUG"


def _seed_exhausted_transient_usage_limit_request(tmp_path, monkeypatch, *, idempotency_key: str) -> tuple[str, str]:
    _seed_root(tmp_path)
    request_rel = _seed_request(
        tmp_path,
        idempotency_key=idempotency_key,
    )

    class Completed:
        returncode = 1
        stdout = ""
        stderr = "ERROR: You've hit your usage limit. Upgrade to Pro, visit codex/settings/usage to purchase more credits or try again at Jun 4th, 2026 1:33 AM."

    monkeypatch.setattr("kernel.ion_codex_queue_runner.subprocess.run", lambda *args, **kwargs: Completed())

    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    failed = run_codex_queue_worker(tmp_path, prepared["run"]["run_packet_path"])
    source_run_rel = failed["run"]["run_packet_path"]
    recovered = requeue_codex_transient_usage_limit_request(
        tmp_path,
        run_packet_path=source_run_rel,
        confirmation=runner.CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_CONFIRMATION,
    )
    assert recovered["ok"] is True
    request_path = tmp_path / request_rel
    request = json.loads(request_path.read_text(encoding="utf-8"))
    request["status"] = "CODEX_QUEUE_RUNNER_FAILED"
    request["failure_classification"] = "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BUG"
    request_path.write_text(json.dumps(request, indent=2), encoding="utf-8")
    return request_rel, source_run_rel


def test_bridge_transient_usage_limit_request_creates_packet_without_requeue_or_task_return(tmp_path, monkeypatch):
    request_rel, source_run_rel = _seed_exhausted_transient_usage_limit_request(
        tmp_path,
        monkeypatch,
        idempotency_key="transient-usage-limit-bridge",
    )

    result = bridge_codex_transient_usage_limit_request(
        tmp_path,
        run_packet_path=source_run_rel,
        confirmation=runner.CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_CONFIRMATION,
        idempotency_key="bridge-create",
    )

    assert result["ok"] is True
    assert result["result"] == "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BRIDGE_CREATED"
    assert result["task_return_created"] is False
    assert result["accepted_for_carrier_intake"] is False
    assert result["automatic_agent_reaction_proven"] is False
    assert (tmp_path / result["receipt_path"]).is_file()
    assert (tmp_path / result["relay_request_path"]).is_file()
    bridge = json.loads((tmp_path / result["receipt_path"]).read_text(encoding="utf-8"))
    assert bridge["same_request_requeue_allowed"] is False
    assert bridge["worker_start_allowed"] is False
    assert bridge["task_return_created"] is False
    assert bridge["accepted_for_carrier_intake"] is False
    relay = json.loads((tmp_path / result["relay_request_path"]).read_text(encoding="utf-8"))
    assert relay["requested_action"] == "parent_session_review_and_reissue"
    assert "synthesize_task_return_from_failed_log" in relay["forbidden_actions"]
    request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert request["status"] == "CODEX_QUEUE_RUNNER_FAILED"
    assert request["failure_classification"] == "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BUG"
    assert request["latest_return_packet_path"] is None
    assert request["carrier_session_bridge_history"][0]["task_return_created"] is False
    assert request["carrier_session_bridge_history"][0]["accepted_for_carrier_intake"] is False


def test_bridge_preview_uses_request_history_for_vanished_recovered_usage_limit_run(
    tmp_path,
    monkeypatch,
):
    request_rel, source_run_rel = _seed_exhausted_transient_usage_limit_request(
        tmp_path,
        monkeypatch,
        idempotency_key="transient-usage-limit-vanished-bridge",
    )
    run_path = tmp_path / source_run_rel
    run = json.loads(run_path.read_text(encoding="utf-8"))
    run["status"] = "CODEX_CLI_VANISHED_NO_OUTPUT"
    run["failure_classification"] = "CODEX_CLI_FAILURE"
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    request_path = tmp_path / request_rel
    request = json.loads(request_path.read_text(encoding="utf-8"))
    request["failure_classification"] = "CODEX_CLI_FAILURE"
    request["last_failure_classification"] = runner.CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS
    request_path.write_text(json.dumps(request, indent=2), encoding="utf-8")

    preview = preview_codex_transient_usage_limit_bridge(
        tmp_path,
        run_packet_path=source_run_rel,
        idempotency_key="bridge-after-vanished-no-output",
    )

    bridge = preview["carrier_session_bridge"]
    assert preview["would_create_bridge"] is True
    assert bridge["eligible"] is True
    assert bridge["failure_classification"] == runner.CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS
    assert bridge["source_run_failure_classification"] == "CODEX_CLI_FAILURE"
    assert bridge["lineage_failure_classification_basis"][
        "preserved_from_prior_transient_usage_limit"
    ] is True


def test_bridge_transient_usage_limit_request_is_idempotent(tmp_path, monkeypatch):
    request_rel, source_run_rel = _seed_exhausted_transient_usage_limit_request(
        tmp_path,
        monkeypatch,
        idempotency_key="transient-usage-limit-bridge-idempotent",
    )

    first = bridge_codex_transient_usage_limit_request(
        tmp_path,
        run_packet_path=source_run_rel,
        confirmation=runner.CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_CONFIRMATION,
        idempotency_key="bridge-idempotent",
    )
    second = bridge_codex_transient_usage_limit_request(
        tmp_path,
        run_packet_path=source_run_rel,
        confirmation=runner.CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_CONFIRMATION,
        idempotency_key="bridge-idempotent",
    )

    assert first["ok"] is True
    assert second["ok"] is True
    assert second["result"] == "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BRIDGE_ALREADY_CREATED"
    assert second["receipt_path"] == first["receipt_path"]
    request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert len(request["carrier_session_bridge_history"]) == 1


def test_bridge_transient_usage_limit_blocks_when_same_request_active(tmp_path, monkeypatch):
    request_rel, source_run_rel = _seed_exhausted_transient_usage_limit_request(
        tmp_path,
        monkeypatch,
        idempotency_key="transient-usage-limit-bridge-active",
    )
    source_run = json.loads((tmp_path / source_run_rel).read_text(encoding="utf-8"))
    state_path = tmp_path / runner.RUNNER_STATE_PATH
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_runs": [
                    {
                        "request_path": request_rel,
                        "run_packet_path": source_run_rel,
                        "lane_id": source_run["lane_id"],
                        "pid": 999999,
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = bridge_codex_transient_usage_limit_request(
        tmp_path,
        run_packet_path=source_run_rel,
        confirmation=runner.CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_CONFIRMATION,
        idempotency_key="bridge-active",
    )

    assert result["ok"] is False
    assert result["result"] == "ACTIVE_SAME_REQUEST_WORKER_PRESENT"
    assert result["carrier_session_bridge"]["active_same_request_worker_count"] == 1
    request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert "carrier_session_bridge_history" not in request
    assert request["status"] == "CODEX_QUEUE_RUNNER_FAILED"


def test_worker_observability_trace_recommends_bridge_after_recovery_exhausted(tmp_path, monkeypatch):
    request_rel, source_run_rel = _seed_exhausted_transient_usage_limit_request(
        tmp_path,
        monkeypatch,
        idempotency_key="transient-usage-limit-bridge-trace",
    )
    source_run = json.loads((tmp_path / source_run_rel).read_text(encoding="utf-8"))

    trace = runner.build_codex_worker_observability_trace(tmp_path, run=source_run, run_rel=source_run_rel)

    assert trace["carrier_session_recovery"]["recovery_exhausted"] is True
    assert trace["carrier_session_recovery"]["bridge_required"] is True
    assert trace["carrier_session_bridge"]["eligible"] is True
    assert trace["carrier_session_bridge"]["request_path"] == request_rel
    assert trace["carrier_session_bridge"]["same_request_requeue_allowed"] is False
    assert trace["carrier_session_bridge"]["creates_task_return"] is False
    assert "Route a session bridge" in trace["next_recommended_action"]


def test_live_status_reports_start_requested_claim_without_worker_receipt(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)

    status = build_codex_queue_runner_status(tmp_path, reconcile=False)

    live = status["live_worker_telemetry"]
    assert prepared["ok"] is True
    assert live["phase_status"] == "start_requested"
    assert live["run_status"] == "CLAIMED_BY_CODEX_QUEUE_RUNNER"
    assert live["request_path"] == request_rel
    assert live["active_process_running"] is False
    assert live["run_packet_path"] == prepared["run"]["run_packet_path"]


def test_reconcile_marks_start_no_receipt_after_simulated_connector_timeout(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])
    run_path = tmp_path / run["run_packet_path"]
    run["created_at"] = "2026-05-04T00:00:00+00:00"
    run["updated_at"] = "2026-05-04T00:00:00+00:00"
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")

    status = build_codex_queue_runner_status(tmp_path, reconcile=True)

    live = status["live_worker_telemetry"]
    assert status["reconciliation"]["action"] == "mark_start_no_receipt"
    assert status["reconciliation"]["start_no_receipt_updated"] is True
    assert live["phase_status"] == "start_no_receipt"
    assert live["run_status"] == "CODEX_QUEUE_START_NO_RECEIPT"
    updated_run = json.loads(run_path.read_text(encoding="utf-8"))
    assert updated_run["status"] == "CODEX_QUEUE_START_NO_RECEIPT"
    assert updated_run["failure_classification"] == "CARRIER_ADAPTER_FAILURE"
    assert updated_run["start_no_receipt_diagnostic"]["reason"] == "start_requested_but_no_worker_receipt_or_active_process_after_grace"


def test_process_once_blocks_explicit_request_when_same_lane_is_active(tmp_path):
    _seed_root(tmp_path)
    active_rel = _seed_lane_request(
        tmp_path,
        filename="2026-05-04T000001Z0000_impl_active.json",
        request_id="codex_req_impl_active",
        work_class="implementation",
        objective="Active implementation worker",
    )
    next_rel = _seed_lane_request(
        tmp_path,
        filename="2026-05-04T000002Z0000_impl_next.json",
        request_id="codex_req_impl_next",
        work_class="implementation",
        objective="Next implementation worker",
    )
    active_run = prepare_codex_queue_run(tmp_path, request_path=active_rel, claim=True)["run"]
    active_run["status"] = "CODEX_CLI_RUNNING"
    active_run["pid"] = os.getpid()
    active_run["started_at"] = "2026-05-04T00:00:00+00:00"
    (tmp_path / active_run["run_packet_path"]).write_text(json.dumps(active_run, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": active_run["run_id"],
                    "pid": os.getpid(),
                    "run_packet_path": active_run["run_packet_path"],
                    "request_path": active_rel,
                    "lane_id": "implementation_lane",
                    "started_at": "2026-05-04T00:00:00+00:00",
                },
                "active_runs": {
                    active_run["run_id"]: {
                        "run_id": active_run["run_id"],
                        "pid": os.getpid(),
                        "run_packet_path": active_run["run_packet_path"],
                        "request_path": active_rel,
                        "lane_id": "implementation_lane",
                        "started_at": "2026-05-04T00:00:00+00:00",
                    }
                },
                "latest_run": active_run["run_packet_path"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = process_codex_queue_once(tmp_path, request_path=next_rel, start=True, background=False)

    assert result["ok"] is False
    assert result["finding"] == "codex_queue_lane_already_active"
    assert result["lane_id"] == "implementation_lane"
    assert result["active_runs"][0]["request_path"] == active_rel


def test_parallel_plan_preview_projects_conflicts_without_mutating_queue_state(tmp_path):
    _seed_root(tmp_path)
    active_rel = _seed_lane_request(
        tmp_path,
        filename="2026-05-04T000001Z0000_impl_active.json",
        request_id="codex_req_impl_active",
        work_class="implementation",
        objective="Active implementation worker",
    )
    active_path = tmp_path / active_rel
    active_payload = json.loads(active_path.read_text(encoding="utf-8"))
    active_payload["dedupe_key"] = "idempotency_key:pckt-preview"
    active_payload["write_set"] = ["ION/04_packages/kernel/ion_codex_queue_runner.py"]
    active_path.write_text(json.dumps(active_payload, indent=2), encoding="utf-8")
    active_run = prepare_codex_queue_run(tmp_path, request_path=active_rel, claim=True)["run"]
    active_run["status"] = "CODEX_CLI_RUNNING"
    active_run["pid"] = os.getpid()
    active_run["started_at"] = "2026-05-04T00:00:00+00:00"
    (tmp_path / active_run["run_packet_path"]).write_text(json.dumps(active_run, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": active_run["run_id"],
                    "pid": os.getpid(),
                    "run_packet_path": active_run["run_packet_path"],
                    "request_path": active_rel,
                    "lane_id": "implementation_lane",
                    "started_at": "2026-05-04T00:00:00+00:00",
                },
                "active_runs": {
                    active_run["run_id"]: {
                        "run_id": active_run["run_id"],
                        "pid": os.getpid(),
                        "run_packet_path": active_run["run_packet_path"],
                        "request_path": active_rel,
                        "lane_id": "implementation_lane",
                        "started_at": "2026-05-04T00:00:00+00:00",
                    }
                },
                "latest_run": active_run["run_packet_path"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    queue_path = tmp_path / "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json"
    queue_sha_before = json.dumps(json.loads(queue_path.read_text(encoding="utf-8")), sort_keys=True)
    state_sha_before = json.dumps(json.loads(state_path.read_text(encoding="utf-8")), sort_keys=True)
    run_count_before = len(list((tmp_path / "ION/05_context/current/chatgpt_connector/codex_queue_runs").rglob("run.json")))

    preview = build_codex_parallel_plan_preview(
        tmp_path,
        {
            "proposed_request": {
                "request_id": "codex_req_preview_candidate",
                "objective": "Preview implementation change",
                "lane_request": "implementation_lane",
                "idempotency_key": "pckt-preview",
                "read_set": ["ION/04_packages/kernel/ion_codex_queue_runner.py"],
                "write_set": ["ION/04_packages/kernel/ion_codex_queue_runner.py"],
                "authority_class": "candidate_write",
            }
        },
    )

    assert preview["schema_id"] == "ion.codex_queue_parallel_plan_preview.v0_1"
    assert preview["lane_request"] == "implementation_lane"
    assert preview["lane_resolved"] == "implementation_lane"
    assert preview["lane_remap_reason"] is None
    assert preview["dedupe_signature"]["dedupe_key"] == "idempotency_key:pckt-preview"
    assert preview["conflict_projection"]["active_codex_run_count"] == 1
    assert preview["conflict_projection"]["duplicate_active_or_terminal_count"] == 1
    assert preview["conflict_projection"]["write_conflict_count"] >= 1
    assert preview["lease_decision"]["would_enqueue"] is False
    assert preview["lease_decision"]["worker_process_started"] is False
    assert preview["mutates_active_state"] is False
    assert preview["production_authority"] is False
    assert preview["live_execution_authority"] is False
    assert preview["accepted_state_claim"] is False
    assert json.dumps(json.loads(queue_path.read_text(encoding="utf-8")), sort_keys=True) == queue_sha_before
    assert json.dumps(json.loads(state_path.read_text(encoding="utf-8")), sort_keys=True) == state_sha_before
    assert len(list((tmp_path / "ION/05_context/current/chatgpt_connector/codex_queue_runs").rglob("run.json"))) == run_count_before


def test_process_once_allows_explicit_request_when_other_lane_is_active(tmp_path, monkeypatch):
    _seed_root(tmp_path)
    _seed_codex_agent_mount(
        tmp_path,
        "role_mason__domain_construction_routing_integration",
        lane_ids=["implementation_lane"],
    )
    active_rel = _seed_lane_request(
        tmp_path,
        filename="2026-05-04T000001Z0000_audit_active.json",
        request_id="codex_req_audit_active",
        work_class="audit",
        objective="Active audit worker",
    )
    next_rel = _seed_lane_request(
        tmp_path,
        filename="2026-05-04T000002Z0000_impl_next.json",
        request_id="codex_req_impl_next",
        work_class="implementation",
        objective="Next implementation worker",
        agent_role_id="role.mason",
        domain_id="domain.construction_routing_integration",
    )
    active_run = prepare_codex_queue_run(tmp_path, request_path=active_rel, claim=True)["run"]
    active_run["status"] = "CODEX_CLI_RUNNING"
    active_run["pid"] = os.getpid()
    active_run["started_at"] = "2026-05-04T00:00:00+00:00"
    (tmp_path / active_run["run_packet_path"]).write_text(json.dumps(active_run, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": active_run["run_id"],
                    "pid": os.getpid(),
                    "run_packet_path": active_run["run_packet_path"],
                    "request_path": active_rel,
                    "lane_id": "audit_lane",
                    "started_at": "2026-05-04T00:00:00+00:00",
                },
                "active_runs": {
                    active_run["run_id"]: {
                        "run_id": active_run["run_id"],
                        "pid": os.getpid(),
                        "run_packet_path": active_run["run_packet_path"],
                        "request_path": active_rel,
                        "lane_id": "audit_lane",
                        "started_at": "2026-05-04T00:00:00+00:00",
                    }
                },
                "latest_run": active_run["run_packet_path"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    def fake_worker(_root, run_packet, **_kwargs):
        run = json.loads((tmp_path / run_packet).read_text(encoding="utf-8"))
        return {"schema_id": runner.SCHEMA_ID, "ok": True, "result": "RETURN_RECORDED_PROOF_ACCEPTED", "run": run}

    monkeypatch.setattr(runner, "run_codex_queue_worker", fake_worker)

    result = process_codex_queue_once(tmp_path, request_path=next_rel, start=True, background=False)

    assert result["ok"] is True
    assert result["result"] == "RETURN_RECORDED_PROOF_ACCEPTED"
    assert result["run"]["lane_id"] == "implementation_lane"


def test_process_once_inline_records_proof_gated_task_return(tmp_path):
    _seed_root(tmp_path)
    _seed_codex_agent_mount(
        tmp_path,
        "role_mason__domain_construction_routing_integration",
        lane_ids=["implementation_lane"],
    )
    request_rel = _seed_request(
        tmp_path,
        agent_role_id="role.mason",
        domain_id="domain.construction_routing_integration",
    )
    prepared = prepare_codex_queue_run(tmp_path)
    required_paths = [item["path"] for item in prepared["context_receipt"]["required_context_reads"]]
    task_output = _valid_task_return(required_paths)

    result = process_codex_queue_once(
        tmp_path,
        request_path=request_rel,
        start=True,
        background=False,
        task_output_override=task_output,
    )

    assert result["ok"] is True
    assert result["result"] == "RETURN_RECORDED_PROOF_ACCEPTED"
    assert result["run"]["pid"] > 0
    event_names = [event["event"] for event in result["run"]["worker_lifecycle_events"]]
    assert "worker_sign_in_context_awareness" in event_names
    assert event_names[-2:] == ["worker_boot", "worker_terminal"]
    assert result["run"]["worker_lifecycle_events"][-1]["terminal_state"] == "accepted"
    assert result["run"]["worker_lifecycle_events"][-1]["context_proof_accepted"] is True
    assert result["run"]["worker_lifecycle_events"][-1]["template_action_proof_accepted"] is True
    status = build_codex_queue_runner_status(tmp_path, reconcile=False)
    live = status["live_worker_telemetry"]
    assert live["latest_worker_lifecycle_event"]["event"] == "worker_terminal"
    assert live["latest_worker_lifecycle_event"]["terminal_state"] == "accepted"
    request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert request["status"] == "RETURN_RECORDED_PROOF_ACCEPTED"
    assert request["latest_context_proof_accepted"] is True
    assert request["latest_template_action_proof_accepted"] is True
    assert (tmp_path / request["latest_return_packet_path"]).exists()


def test_process_once_inline_claims_and_releases_worker_shift_lease(tmp_path):
    _seed_root(tmp_path)
    _seed_codex_agent_mount(
        tmp_path,
        "role_mason__domain_construction_routing_integration",
        lane_ids=["implementation_lane"],
    )
    request_rel = _seed_request(
        tmp_path,
        work_class="implementation",
        planned_writes=["ION/04_packages/kernel/ion_codex_queue_runner.py"],
        agent_role_id="role.mason",
        domain_id="domain.construction_routing_integration",
    )
    prepared = prepare_codex_queue_run(tmp_path)
    required_paths = [item["path"] for item in prepared["context_receipt"]["required_context_reads"]]
    task_output = _valid_task_return(required_paths)

    result = process_codex_queue_once(
        tmp_path,
        request_path=request_rel,
        start=True,
        background=False,
        task_output_override=task_output,
    )

    assert result["ok"] is True
    lease = result["run"]["worker_shift_lease"]
    release = result["run"]["worker_shift_lease_release"]
    assert lease["ok"] is True
    assert lease["claim_status"] == "ACTIVE"
    assert lease["mode"] == "write"
    assert "ION/04_packages/kernel/ion_codex_queue_runner.py" in lease["paths"]
    assert runner.CODEX_WORK_QUEUE_INDEX.as_posix() not in lease["paths"]
    assert runner.RUNNER_STATE_PATH.as_posix() not in lease["paths"]
    assert lease["shared_coordination_paths_excluded_from_worker_shift_lease"] == [
        runner.CODEX_WORK_QUEUE_INDEX.as_posix(),
        runner.RUNNER_STATE_PATH.as_posix(),
    ]
    assert (tmp_path / lease["receipt_path"]).is_file()
    assert release["ok"] is True
    assert release["release_result"] == "RELEASED"
    assert release["released_count"] == 1
    assert (tmp_path / release["receipt_path"]).is_file()
    board = load_shift_board(tmp_path)
    assert all(item.get("lease_id") != lease["lease_id"] for item in board["active_leases"])


def test_codex_queue_run_worker_shift_leases_allow_distinct_parallel_lanes(tmp_path):
    _seed_root(tmp_path)
    implementation_rel = _seed_lane_request(
        tmp_path,
        filename="2026-05-04T000001Z0000_impl.json",
        request_id="codex_req_impl",
        work_class="implementation",
        objective="Implementation lane worker",
    )
    audit_rel = _seed_lane_request(
        tmp_path,
        filename="2026-05-04T000002Z0000_audit.json",
        request_id="codex_req_audit",
        work_class="audit",
        objective="Audit lane worker",
    )
    implementation_run = prepare_codex_queue_run(tmp_path, request_path=implementation_rel, claim=True)["run"]
    audit_run = prepare_codex_queue_run(tmp_path, request_path=audit_rel, claim=True)["run"]

    implementation_lease = runner._claim_codex_queue_run_lease(tmp_path, implementation_run)
    audit_lease = runner._claim_codex_queue_run_lease(tmp_path, audit_run)

    assert implementation_lease["ok"] is True
    assert audit_lease["ok"] is True
    assert implementation_lease["claim_status"] == "ACTIVE"
    assert audit_lease["claim_status"] == "ACTIVE"
    assert runner.CODEX_WORK_QUEUE_INDEX.as_posix() not in implementation_lease["paths"]
    assert runner.CODEX_WORK_QUEUE_INDEX.as_posix() not in audit_lease["paths"]
    assert runner.RUNNER_STATE_PATH.as_posix() not in implementation_lease["paths"]
    assert runner.RUNNER_STATE_PATH.as_posix() not in audit_lease["paths"]


def test_codex_queue_worker_shift_ids_remain_unique_for_same_prefix_run_ids():
    first = {
        "run_id": "codex_run_2026-06-04T191455Z0000_codex_req_metadata_identity_reissue_20260604t184840z_37e599b4f10e"
    }
    second = {
        "run_id": "codex_run_2026-06-04T191455Z0000_codex_req_metadata_identity_reissue_20260604t184840z_fc16779d845e"
    }

    assert runner._safe_slug(first["run_id"]) == runner._safe_slug(second["run_id"])
    assert runner._codex_queue_worker_id_for_run(first) != runner._codex_queue_worker_id_for_run(second)
    assert runner._codex_queue_lease_id_for_run(first) != runner._codex_queue_lease_id_for_run(second)


def test_reconcile_release_keeps_unrelated_orphan_exclusive_write_lease_classified(tmp_path):
    _seed_root(tmp_path)
    orphan_lease_id = "codex_action_gateway_oversize_recovery_20260603"
    orphan = claim_work_lease(
        root=tmp_path,
        worker_id="codex_cli:action_gateway_oversize_recovery",
        lease_id=orphan_lease_id,
        paths=[
            "ION/04_packages/kernel/ion_custom_gpt_action_gateway.py",
            "ION/tests/test_kernel_ion_custom_gpt_action_gateway.py",
        ],
        mode="exclusive_write",
        objective="Bounded Action Gateway oversized-response recovery",
        allow_worker_id_mismatch=True,
        now="2026-06-03T23:19:04+00:00",
    )
    assert orphan["receipt"]["result"] == "ACTIVE"
    terminal_rel = _seed_lane_request(
        tmp_path,
        filename="2026-05-04T000002Z0000_impl_terminal_orphan.json",
        request_id="codex_req_impl_terminal_orphan",
        work_class="implementation",
        objective="Terminal implementation lane with unrelated orphan lease",
    )
    terminal = prepare_codex_queue_run(tmp_path, request_path=terminal_rel, claim=True)["run"]
    lease_claim = claim_work_lease(
        root=tmp_path,
        worker_id="codex_queue_runner:test_terminal_orphan",
        lease_id="codex_queue_lease:test_terminal_orphan",
        paths=["ION/04_packages/kernel/ion_codex_queue_runner.py"],
        mode="write",
        allow_worker_id_mismatch=True,
    )
    terminal["worker_shift_lease"] = {
        "schema_id": "ion.codex_queue_runner_worker_shift_lease.v0_1",
        "ok": True,
        "worker_id": "codex_queue_runner:test_terminal_orphan",
        "lease_id": "codex_queue_lease:test_terminal_orphan",
        "mode": "write",
        "paths": ["ION/04_packages/kernel/ion_codex_queue_runner.py"],
        "receipt_path": lease_claim["receipt_path"],
        "claim_status": "ACTIVE",
    }
    terminal["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    terminal["pid"] = 999999999
    terminal["completed_at"] = "2026-05-04T00:05:00+00:00"
    run_path = tmp_path / terminal["run_packet_path"]
    run_path.write_text(json.dumps(terminal, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": terminal["run_id"],
                    "pid": 999999999,
                    "run_packet_path": terminal["run_packet_path"],
                    "request_path": terminal_rel,
                    "lane_id": "implementation_lane",
                    "started_at": "2026-05-04T00:00:00+00:00",
                    "worker_shift_lease_id": "codex_queue_lease:test_terminal_orphan",
                },
                "latest_run": terminal["run_packet_path"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = reconcile_codex_queue_runner_state(tmp_path, write=True)

    assert result["ok"] is True
    assert result["worker_shift_lease_release"]["release_result"] == "RELEASED"
    assert result["worker_shift_lease_release"]["released_count"] == 1
    updated_run = json.loads(run_path.read_text(encoding="utf-8"))
    queue_lease = updated_run["worker_shift_lease"]
    board = load_shift_board(tmp_path)
    active_lease_ids = [item.get("lease_id") for item in board["active_leases"]]
    assert queue_lease["lease_id"] not in active_lease_ids
    assert orphan_lease_id in active_lease_ids
    summary = summarize_shift_board(root=tmp_path, now="2026-06-03T23:55:00+00:00")
    assert summary["orphan_active_exclusive_write_count"] == 1
    assert summary["orphan_exclusive_write_leases"][0]["lease_id"] == orphan_lease_id
    assert summary["orphan_exclusive_write_leases"][0]["classification"] == "ORPHAN_ACTIVE_EXCLUSIVE_WRITE_BLOCKED"
    assert summary["orphan_exclusive_write_leases"][0]["auto_release_allowed"] is False


def test_worker_prefers_task_return_body_path_for_submit_when_last_message_is_wrapper(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])
    run_path = tmp_path / run["run_packet_path"]
    required_paths = [item["path"] for item in prepared["context_receipt"]["required_context_reads"]]
    body_text = _valid_task_return(required_paths)
    (tmp_path / run["task_return_body_path"]).write_text(body_text, encoding="utf-8")

    result = run_codex_queue_worker(
        tmp_path,
        run["run_packet_path"],
        task_output_override="Created a corrected task-return packet and validated it.\n",
    )

    assert result["ok"] is True
    assert result["result"] == "RETURN_RECORDED_PROOF_ACCEPTED"
    assert result["run"]["task_output_submission_source"] == "task_return_body_path"
    assert result["run"]["submit_result"]["return_template_valid"] is True
    assert result["run"]["submit_result"]["context_proof_accepted"] is True
    assert result["run"]["submit_result"]["template_action_proof_accepted"] is True


def test_process_once_blocks_worker_when_required_context_read_missing(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    missing_rel = "ION/04_packages/kernel/ion_carrier_continue.py"
    (tmp_path / missing_rel).unlink()

    result = process_codex_queue_once(
        tmp_path,
        request_path=request_rel,
        start=True,
        background=False,
    )

    assert result["ok"] is False
    assert result["result"] == "WORKER_START_CONTEXT_GATE_BLOCKED"
    assert result["finding"] == "queue_worker_start_domain_id_required_for_context_gate"
    assert result["worker_return_status"]["carrier_intake_only"] is True
    assert result["worker_return_status"]["product_state"] is False
    request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert request["status"] == "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE"
    assert request["failure_classification"] == "CONTEXT_ACTIVE_RESOLVER_BLOCKED"
    assert request["context_gate"]["finding"] == "queue_worker_start_domain_id_required_for_context_gate"


def test_process_once_inline_reports_proof_blocked_return_as_backend_failure(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])

    result = run_codex_queue_worker(
        tmp_path,
        run["run_packet_path"],
        task_output_override="### RESULT\nmissing required proof sections\n",
    )

    assert result["ok"] is False
    assert result["result"] == "RETURN_TEMPLATE_INVALID"
    assert result["run"]["failure_classification"] == "BACKEND_CODEX_FAILURE"
    assert result["run"]["worker_lifecycle_events"][-1]["event"] == "worker_terminal"
    assert result["run"]["worker_lifecycle_events"][-1]["terminal_state"] == "template_invalid"
    request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert request["status"] == "RETURN_TEMPLATE_INVALID"
    assert request["failure_classification"] == "BACKEND_CODEX_FAILURE"
    assert request["latest_context_proof_accepted"] is False
    assert request["latest_template_action_proof_accepted"] is False


def test_process_once_separates_context_proof_failure_from_template_invalid(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    task_output = "\n".join(
        [
            "### CONTEXT PROOF",
            "Context proof intentionally omits required paths and machine evidence.",
            "",
            "### TEMPLATE ACTION PROOF",
            "template_id: ion.template.autonomous_loop.local_worker.v1",
            "action_id: codex_queue_runner_test",
            "result: designed",
            "touched_paths:",
            "  - ION/04_packages/kernel/ion_codex_queue_runner.py",
            "",
            "### VALIDATION",
            "- not run",
            "",
            "### RESULT",
            "Useful return content exists, but context proof is missing.",
            "",
            "### WORKLOAD DIFF",
            "- ION/04_packages/kernel/ion_codex_queue_runner.py",
            "",
            "### BLOCKERS",
            "- context proof omitted for regression coverage",
            "",
            "### RECOMMENDED NEXT PACKET",
            "Repair context proof only.",
            "",
        ]
    )
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])

    result = run_codex_queue_worker(
        tmp_path,
        run["run_packet_path"],
        task_output_override=task_output,
    )

    assert result["ok"] is False
    assert result["result"] == "RETURN_RECORDED_PROOF_BLOCKED"
    assert result["run"]["status"] == "RETURN_RECORDED_PROOF_BLOCKED"
    assert result["run"]["submit_result"]["return_template_valid"] is True
    assert result["run"]["submit_result"]["context_proof_accepted"] is False
    assert result["run"]["submit_result"]["template_action_proof_accepted"] is True
    assert result["run"]["submit_result"]["carrier_intake_state"] == "template_action_proof_ok_context_failed"
    assert result["run"]["worker_return_status"]["carrier_intake_state"] == "template_action_proof_ok_context_failed"
    assert result["run"]["worker_return_status"]["product_state_accepted"] is False
    request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert request["status"] == "RETURN_RECORDED_PROOF_BLOCKED"
    assert request["latest_task_return_carrier_intake_state"] == "template_action_proof_ok_context_failed"
    assert request["latest_task_return_product_state_accepted"] is False


def test_reconcile_marks_dead_active_worker_failed_and_clears_state(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])
    run_path = tmp_path / run["run_packet_path"]
    run["status"] = "CODEX_CLI_RUNNING"
    run["pid"] = 999999999
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": run["run_id"],
                    "pid": 999999999,
                    "run_packet_path": run["run_packet_path"],
                    "request_path": request_rel,
                    "started_at": "2026-05-04T00:00:00+00:00",
                },
                "latest_run": run["run_packet_path"],
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = reconcile_codex_queue_runner_state(tmp_path, write=True)

    assert result["ok"] is True
    assert result["stale_active_run_detected"] is True
    assert result["action"] == "mark_codex_cli_vanished_no_output_and_clear_active"
    updated_run = json.loads(run_path.read_text(encoding="utf-8"))
    assert updated_run["status"] == "CODEX_CLI_VANISHED_NO_OUTPUT"
    assert updated_run["failure_classification"] == "CODEX_CLI_FAILURE"
    assert updated_run["daemon_reconciliation"]["output_presence"] == {
        "stdout_exists": False,
        "stderr_exists": False,
        "last_message_exists": False,
    }
    assert updated_run["daemon_reconciliation"]["reason"] == "active_pid_not_running_no_terminal_output"
    assert updated_run["worker_lifecycle_events"][-1]["terminal_state"] == "vanished_no_output"
    snapshot_rel = updated_run["worker_trace_snapshot_path"]
    snapshot = json.loads((tmp_path / snapshot_rel).read_text(encoding="utf-8"))
    assert snapshot["schema_id"] == "ion.codex_worker_observability_trace.v0"
    assert snapshot["run"]["run_status"] == "CODEX_CLI_VANISHED_NO_OUTPUT"
    assert snapshot["durable_trace"]["snapshot_write_state"] == "snapshot_written"
    assert snapshot["chain_of_thought_policy"]["hidden_model_chain_of_thought_requested"] is False
    updated_request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert updated_request["status"] == "CODEX_QUEUE_RUNNER_FAILED"
    assert updated_request["failure_classification"] == "CODEX_CLI_FAILURE"
    runner_state = json.loads(state_path.read_text(encoding="utf-8"))
    assert runner_state["active_run"] is None


def test_reconcile_preserves_usage_limit_lineage_when_recovered_run_vanishes(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])
    run_path = tmp_path / run["run_packet_path"]
    run["status"] = "CODEX_CLI_RUNNING"
    run["pid"] = 999999999
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    request_path = tmp_path / request_rel
    request = json.loads(request_path.read_text(encoding="utf-8"))
    request["status"] = "QUEUED_FOR_CODEX_CARRIER"
    request["last_failure_classification"] = runner.CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS
    request["carrier_session_recovery_history"] = [
        {
            "recovery_id": "codex_carrier_recovery_test",
            "recovery_class": runner.CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS,
            "previous_failure_classification": runner.CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS,
        }
    ]
    request_path.write_text(json.dumps(request, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": run["run_id"],
                    "pid": 999999999,
                    "run_packet_path": run["run_packet_path"],
                    "request_path": request_rel,
                    "started_at": "2026-05-04T00:00:00+00:00",
                },
                "latest_run": run["run_packet_path"],
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = reconcile_codex_queue_runner_state(tmp_path, write=True)

    assert result["ok"] is True
    assert result["action"] == "mark_codex_cli_vanished_no_output_and_clear_active"
    updated_run = json.loads(run_path.read_text(encoding="utf-8"))
    assert updated_run["status"] == "CODEX_CLI_VANISHED_NO_OUTPUT"
    assert updated_run["failure_classification"] == runner.CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS
    assert updated_run["daemon_reconciliation"]["failure_classification_basis"][
        "preserved_from_prior_transient_usage_limit"
    ] is True
    updated_request = json.loads(request_path.read_text(encoding="utf-8"))
    assert updated_request["status"] == "CODEX_QUEUE_RUNNER_FAILED"
    assert updated_request["failure_classification"] == runner.CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS

    bridge_preview = preview_codex_transient_usage_limit_bridge(
        tmp_path,
        run_packet_path=run["run_packet_path"],
        idempotency_key="usage-limit-bridge-after-vanish",
    )

    assert bridge_preview["would_create_bridge"] is True
    assert bridge_preview["carrier_session_bridge"]["eligible"] is True
    assert bridge_preview["carrier_session_bridge"]["blockers"] == []
    bridge = bridge_codex_transient_usage_limit_request(
        tmp_path,
        run_packet_path=run["run_packet_path"],
        confirmation=runner.CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_CONFIRMATION,
        idempotency_key="usage-limit-bridge-after-vanish",
    )

    assert bridge["ok"] is True
    receipt = json.loads((tmp_path / bridge["receipt_path"]).read_text(encoding="utf-8"))
    assert receipt["failure_classification"] == runner.CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS
    assert receipt["source_run_failure_classification"] == runner.CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS
    assert receipt["lineage_failure_classification_basis"][
        "preserved_from_prior_transient_usage_limit"
    ] is True
    updated_request = json.loads(request_path.read_text(encoding="utf-8"))
    assert updated_request["failure_classification"] == runner.CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS
    assert (
        updated_request["worker_return_status"]["failure_classification"]
        == runner.CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS
    )


def test_reconcile_adopts_terminal_request_status_before_vanished_no_output(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])
    run_path = tmp_path / run["run_packet_path"]
    run["status"] = "CODEX_CLI_RUNNING"
    run["pid"] = 999999999
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    request_path = tmp_path / request_rel
    request = json.loads(request_path.read_text(encoding="utf-8"))
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = "ION/05_context/current/chatgpt_connector/task_returns/accepted.json"
    request["return_packet_paths"] = ["ION/05_context/current/chatgpt_connector/task_returns/accepted.json"]
    request["latest_task_return_machine_receipt_path"] = "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/accepted_receipt.json"
    request_path.write_text(json.dumps(request, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": run["run_id"],
                    "pid": 999999999,
                    "run_packet_path": run["run_packet_path"],
                    "request_path": request_rel,
                    "started_at": "2026-05-04T00:00:00+00:00",
                },
                "latest_run": run["run_packet_path"],
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = reconcile_codex_queue_runner_state(tmp_path, write=True)

    assert result["ok"] is True
    assert result["action"] == "adopt_terminal_request_status_and_clear_active"
    updated_run = json.loads(run_path.read_text(encoding="utf-8"))
    assert updated_run["status"] == "RETURN_RECORDED_PROOF_ACCEPTED"
    assert updated_run["failure_classification"] is None
    assert updated_run["latest_return_packet_path"].endswith("accepted.json")
    assert updated_run["return_packet_paths"] == ["ION/05_context/current/chatgpt_connector/task_returns/accepted.json"]
    assert updated_run["latest_task_return_machine_receipt_path"].endswith("accepted_receipt.json")
    assert updated_run["submit_result"]["return_packet_paths"] == ["ION/05_context/current/chatgpt_connector/task_returns/accepted.json"]
    assert updated_run["submit_result"]["machine_receipt_path"].endswith("accepted_receipt.json")
    assert updated_run["daemon_reconciliation"]["reason"] == "active_reference_stale_but_request_already_terminal"
    assert updated_run["daemon_reconciliation"]["return_packet_paths"] == ["ION/05_context/current/chatgpt_connector/task_returns/accepted.json"]
    assert updated_run["daemon_reconciliation"]["latest_task_return_machine_receipt_path"].endswith("accepted_receipt.json")
    assert updated_run["worker_lifecycle_events"][-1]["terminal_state"] == "request_terminal_status_adopted"
    updated_request = json.loads(request_path.read_text(encoding="utf-8"))
    assert updated_request["status"] == "RETURN_RECORDED_PROOF_ACCEPTED"
    runner_state = json.loads(state_path.read_text(encoding="utf-8"))
    assert runner_state["active_run"] is None


def test_reconcile_marks_latest_running_without_active_state_as_vanished_no_output(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])
    run_path = tmp_path / run["run_packet_path"]
    run["status"] = "CODEX_CLI_RUNNING"
    run["pid"] = 999999999
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": None,
                "latest_run": run["run_packet_path"],
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = reconcile_codex_queue_runner_state(tmp_path, write=True)

    assert result["ok"] is True
    assert result["stale_active_run_detected"] is True
    assert result["action"] == "mark_codex_cli_vanished_no_output"
    updated_run = json.loads(run_path.read_text(encoding="utf-8"))
    assert updated_run["status"] == "CODEX_CLI_VANISHED_NO_OUTPUT"
    assert updated_run["failure_classification"] == "CODEX_CLI_FAILURE"
    assert updated_run["daemon_reconciliation"]["reason"] == "latest_run_pid_not_running_no_terminal_output"
    updated_request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert updated_request["status"] == "CODEX_QUEUE_RUNNER_FAILED"
    assert updated_request["failure_classification"] == "CODEX_CLI_FAILURE"
    runner_state = json.loads(state_path.read_text(encoding="utf-8"))
    assert runner_state["active_run"] is None


def test_reconcile_repairs_failed_latest_run_from_accepted_request(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])
    run_path = tmp_path / run["run_packet_path"]
    run["status"] = "CODEX_CLI_VANISHED_NO_OUTPUT"
    run["failure_classification"] = "CODEX_CLI_FAILURE"
    run["pid"] = 999999999
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    request_path = tmp_path / request_rel
    request = json.loads(request_path.read_text(encoding="utf-8"))
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = "ION/05_context/current/chatgpt_connector/task_returns/accepted.json"
    request_path.write_text(json.dumps(request, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": None,
                "latest_run": run["run_packet_path"],
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = reconcile_codex_queue_runner_state(tmp_path, write=True)

    assert result["ok"] is True
    assert result["latest_run_terminal_request_status_mismatch"] is True
    updated_run = json.loads(run_path.read_text(encoding="utf-8"))
    assert updated_run["status"] == "RETURN_RECORDED_PROOF_ACCEPTED"
    assert updated_run["failure_classification"] is None
    assert updated_run["daemon_reconciliation"]["reason"] == "terminal_request_status_supersedes_failed_latest_run_status"


def test_status_classifies_latest_proof_blocked_run_without_accepting(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])
    run_path = tmp_path / run["run_packet_path"]
    run["status"] = "RETURN_RECORDED_PROOF_BLOCKED"
    run["failure_classification"] = None
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": None,
                "latest_run": run["run_packet_path"],
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    status = build_codex_queue_runner_status(tmp_path)

    assert status["reconciliation"]["latest_run_failure_classification_updated"] is True
    updated_run = json.loads(run_path.read_text(encoding="utf-8"))
    assert updated_run["status"] == "RETURN_RECORDED_PROOF_BLOCKED"
    assert updated_run["failure_classification"] == "BACKEND_CODEX_FAILURE"
    updated_request = json.loads((tmp_path / request_rel).read_text(encoding="utf-8"))
    assert updated_request["status"] == "RETURN_RECORDED_PROOF_BLOCKED"
    assert updated_request["failure_classification"] == "BACKEND_CODEX_FAILURE"


def test_reconcile_terminal_failed_run_clears_active_without_starting_new_work(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])
    run_path = tmp_path / run["run_packet_path"]
    run["status"] = "CODEX_CLI_EXIT_NONZERO"
    run["failure_classification"] = "CODEX_CLI_FAILURE"
    run["pid"] = 999999999
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    request_path = tmp_path / request_rel
    request = json.loads(request_path.read_text(encoding="utf-8"))
    request["status"] = "CODEX_QUEUE_RUNNER_FAILED"
    request["failure_classification"] = "CODEX_CLI_FAILURE"
    request_path.write_text(json.dumps(request, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": run["run_id"],
                    "pid": 999999999,
                    "run_packet_path": run["run_packet_path"],
                    "request_path": request_rel,
                    "started_at": "2026-05-04T00:00:00+00:00",
                },
                "latest_run": run["run_packet_path"],
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    run_count_before = len(list((tmp_path / "ION/05_context/current/chatgpt_connector/codex_queue_runs").rglob("run.json")))

    result = reconcile_codex_queue_runner_state(tmp_path, write=True)

    run_count_after = len(list((tmp_path / "ION/05_context/current/chatgpt_connector/codex_queue_runs").rglob("run.json")))
    assert result["ok"] is True
    assert result["action"] == "clear_terminal_active_reference"
    assert result["stale_active_run_detected"] is False
    assert run_count_after == run_count_before
    updated_run = json.loads(run_path.read_text(encoding="utf-8"))
    assert updated_run["status"] == "CODEX_CLI_EXIT_NONZERO"
    updated_request = json.loads(request_path.read_text(encoding="utf-8"))
    assert updated_request["status"] == "CODEX_QUEUE_RUNNER_FAILED"
    runner_state = json.loads(state_path.read_text(encoding="utf-8"))
    assert runner_state["active_run"] is None


def test_reconcile_multi_lane_clears_terminal_without_dropping_running_lane(tmp_path):
    _seed_root(tmp_path)
    running_rel = _seed_lane_request(
        tmp_path,
        filename="2026-05-04T000001Z0000_impl_running.json",
        request_id="codex_req_impl_running",
        work_class="implementation",
        objective="Running implementation lane",
    )
    terminal_rel = _seed_lane_request(
        tmp_path,
        filename="2026-05-04T000002Z0000_audit_terminal.json",
        request_id="codex_req_audit_terminal",
        work_class="audit",
        objective="Terminal audit lane",
    )
    running = prepare_codex_queue_run(tmp_path, request_path=running_rel, claim=True)["run"]
    terminal = prepare_codex_queue_run(tmp_path, request_path=terminal_rel, claim=True)["run"]
    running["status"] = "CODEX_CLI_RUNNING"
    running["pid"] = os.getpid()
    running["started_at"] = "2026-05-04T00:00:00+00:00"
    terminal["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    terminal["pid"] = 999999999
    terminal["completed_at"] = "2026-05-04T00:05:00+00:00"
    (tmp_path / running["run_packet_path"]).write_text(json.dumps(running, indent=2), encoding="utf-8")
    (tmp_path / terminal["run_packet_path"]).write_text(json.dumps(terminal, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": terminal["run_id"],
                    "pid": 999999999,
                    "run_packet_path": terminal["run_packet_path"],
                    "request_path": terminal_rel,
                    "lane_id": "audit_lane",
                    "started_at": "2026-05-04T00:00:00+00:00",
                },
                "active_runs": {
                    running["run_id"]: {
                        "run_id": running["run_id"],
                        "pid": os.getpid(),
                        "run_packet_path": running["run_packet_path"],
                        "request_path": running_rel,
                        "lane_id": "implementation_lane",
                        "started_at": "2026-05-04T00:00:00+00:00",
                    },
                    terminal["run_id"]: {
                        "run_id": terminal["run_id"],
                        "pid": 999999999,
                        "run_packet_path": terminal["run_packet_path"],
                        "request_path": terminal_rel,
                        "lane_id": "audit_lane",
                        "started_at": "2026-05-04T00:00:00+00:00",
                    },
                },
                "latest_run": terminal["run_packet_path"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = reconcile_codex_queue_runner_state(tmp_path, write=True)

    assert result["ok"] is True
    assert result["action"] == "reconciled_multi_lane_active_runs_remaining"
    assert result["terminal_active_run_detected"] is True
    assert result["active_process_running"] is True
    runner_state = json.loads(state_path.read_text(encoding="utf-8"))
    assert list(runner_state["active_runs"]) == [running["run_id"]]
    assert runner_state["active_run"]["run_id"] == running["run_id"]
    assert runner_state["active_lane_locks"]["locks"]["implementation_lane"]["locked"] is True
    assert runner_state["active_lane_locks"]["locks"]["audit_lane"]["locked"] is False


def test_reconcile_releases_terminal_worker_shift_lease(tmp_path):
    _seed_root(tmp_path)
    terminal_rel = _seed_lane_request(
        tmp_path,
        filename="2026-05-04T000002Z0000_impl_terminal.json",
        request_id="codex_req_impl_terminal",
        work_class="implementation",
        objective="Terminal implementation lane",
    )
    terminal = prepare_codex_queue_run(tmp_path, request_path=terminal_rel, claim=True)["run"]
    lease_claim = claim_work_lease(
        root=tmp_path,
        worker_id="codex_queue_runner:test_terminal",
        lease_id="codex_queue_lease:test_terminal",
        paths=["ION/04_packages/kernel/ion_codex_queue_runner.py"],
        mode="write",
        allow_worker_id_mismatch=True,
    )
    terminal["worker_shift_lease"] = {
        "schema_id": "ion.codex_queue_runner_worker_shift_lease.v0_1",
        "ok": True,
        "worker_id": "codex_queue_runner:test_terminal",
        "lease_id": "codex_queue_lease:test_terminal",
        "mode": "write",
        "paths": ["ION/04_packages/kernel/ion_codex_queue_runner.py"],
        "receipt_path": lease_claim["receipt_path"],
        "claim_status": "ACTIVE",
    }
    terminal["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    terminal["pid"] = 999999999
    terminal["completed_at"] = "2026-05-04T00:05:00+00:00"
    run_path = tmp_path / terminal["run_packet_path"]
    run_path.write_text(json.dumps(terminal, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": terminal["run_id"],
                    "pid": 999999999,
                    "run_packet_path": terminal["run_packet_path"],
                    "request_path": terminal_rel,
                    "lane_id": "implementation_lane",
                    "started_at": "2026-05-04T00:00:00+00:00",
                    "worker_shift_lease_id": "codex_queue_lease:test_terminal",
                },
                "latest_run": terminal["run_packet_path"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = reconcile_codex_queue_runner_state(tmp_path, write=True)

    assert result["ok"] is True
    assert result["worker_shift_lease_release"]["release_result"] == "RELEASED"
    updated_run = json.loads(run_path.read_text(encoding="utf-8"))
    assert updated_run["worker_shift_lease_release"]["released_count"] == 1
    board = load_shift_board(tmp_path)
    assert all(item.get("lease_id") != "codex_queue_lease:test_terminal" for item in board["active_leases"])


def test_reconcile_non_terminal_running_process_is_not_marked_complete(tmp_path):
    _seed_root(tmp_path)
    request_rel = _seed_request(tmp_path)
    prepared = prepare_codex_queue_run(tmp_path, request_path=request_rel, claim=True)
    run = dict(prepared["run"])
    run_path = tmp_path / run["run_packet_path"]
    run["status"] = "CODEX_CLI_RUNNING"
    run["pid"] = os.getpid()
    run_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": run["run_id"],
                    "pid": os.getpid(),
                    "run_packet_path": run["run_packet_path"],
                    "request_path": request_rel,
                    "started_at": "2026-05-04T00:00:00+00:00",
                },
                "latest_run": run["run_packet_path"],
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = reconcile_codex_queue_runner_state(tmp_path, write=True)

    runner_state = json.loads(state_path.read_text(encoding="utf-8"))
    updated_run = json.loads(run_path.read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["action"] == "active_run_still_running"
    assert result["active_process_running"] is True
    assert result["stale_active_run_detected"] is False
    assert updated_run["status"] == "CODEX_CLI_RUNNING"
    assert runner_state["active_run"] is not None
