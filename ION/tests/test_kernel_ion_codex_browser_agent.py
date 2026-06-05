import json
from pathlib import Path

import kernel.ion_codex_browser_agent as agent_module
from kernel.ion_action_mcp_branch_leaders import action_branch_describe
from kernel.ion_browser_gpt_dom_calibration import (
    INDEX_PATH,
    LATEST_PROFILE_PATH,
    build_selector_profile,
    write_profile_artifacts,
    write_seed_candidate_profile,
)
from kernel.ion_cockpit_view_model import build_cockpit_view_model
from kernel.ion_codex_browser_agent import (
    CAPSULE_SCHEMA_ID,
    COMPARISON_SCHEMA_ID,
    LATEST_CAPSULE_PATH,
    LATEST_REPORT_PATH,
    LATEST_SANDBOX_BENCHMARK_PATH,
    REQUIREMENTS_SCHEMA_ID,
    build_context_capsule,
    build_dom_requirement_matrix,
    compare_selector_profiles,
    latest_codex_browser_agent_summary,
    run_codex_browser_agent,
    run_sandbox_skill_benchmark,
)


def write_json(root: Path, rel: str, payload: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")


def seed_minimal_cockpit_runtime(root: Path) -> None:
    seed_root(root)
    current = "ION/05_context/current"
    write_json(root, f"{current}/ACTIVE_CURSOR_HOOK_STATE.json", {"status": "ready"})
    write_json(root, f"{current}/ACTIVE_WORK_PACKET.json", {"carrier": "codex_cli", "objective": "browser agent"})
    write_json(root, f"{current}/ACTIVE_ROLE_SPAWN_PLAN.json", {"role_spawn_plan": []})
    write_json(root, f"{current}/ACTIVE_CARRIER_TURN_PACKET.json", {"carrier": "codex_cli", "objective": "browser agent"})
    write_json(root, f"{current}/ACTIVE_CARRIER_TASK_RETURN_LEDGER.json", {"records": []})
    write_json(root, f"{current}/ACTIVE_STEWARD_INTEGRATION_QUEUE.json", {"items": []})
    write_json(root, f"{current}/ACTIVE_OPERATOR_MESSAGE_QUEUE.json", {"items": []})
    write_json(root, f"{current}/ACTIVE_CARRIER_MESSAGE_QUEUE.json", {"items": []})
    write_json(root, f"{current}/ACTIVE_HUMAN_GATE_QUEUE.json", {"gates": []})
    write_json(root, f"{current}/ACTIVE_FRONT_DOOR_PROOF_TRACE.json", {})
    write_json(root, f"{current}/ACTIVE_LANE_TIMELINE_VIEW_MODEL.json", {})
    write_json(root, f"{current}/ACTIVE_RECEIPT_HYDRATION_VIEW_MODEL.json", {})
    write_json(root, f"{current}/ACTIVE_RUNTIME_DEBUG_OVERLAY.json", {})
    write_json(root, f"{current}/SAFE_FULL_PROJECT_PACKAGE_RESULT_V110.json", {})
    write_json(root, f"{current}/V108_V72_MCP_DONOR_RECONCILIATION_AUDIT.json", {})


def live_candidate(selector: str, *, score: int = 92, role: str = "button") -> dict:
    return {
        "selector": selector,
        "score": score,
        "tag": "button" if role != "textbox" else "textarea",
        "role": role,
        "label": role,
        "rect": {"width": 100, "height": 30},
        "unique": True,
        "validated_by": ["unit"],
    }


def required_ready_candidates() -> dict[str, list[dict]]:
    return {
        "composer": [live_candidate("#prompt-textarea", role="textbox")],
        "send_button": [live_candidate("[data-testid='send-button']")],
        "message_list": [live_candidate("main [data-testid^='conversation-turn']", role="list")],
    }


def test_dom_requirement_matrix_flags_required_and_phase_surfaces():
    matrix = build_dom_requirement_matrix(
        {
            "surfaces": [
                {
                    "surface_id": "composer",
                    "selector": "#prompt-textarea",
                    "confidence": 0.92,
                    "validated_by": ["unit"],
                }
            ],
            "chatgpt_dom_twin": {"controls": []},
        }
    )

    assert matrix["schema_id"] == REQUIREMENTS_SCHEMA_ID
    assert matrix["critical_gap_count"] >= 2
    rows = {row["surface_id"]: row for row in matrix["surfaces"]}
    assert rows["composer"]["status"] == "ready"
    assert rows["send_button"]["status"] == "missing_required"
    assert rows["file_upload_menu_option"]["status"] == "needs_phase_capture"
    assert rows["send_button"]["requirement"].startswith("Prove the draft-visible send button")


def test_context_capsule_includes_plan_capabilities_and_authority(tmp_path: Path):
    seed_root(tmp_path)
    write_seed_candidate_profile(tmp_path, "chatgpt_web_test")

    capsule = build_context_capsule(tmp_path, objective="unit browser agent", profile_id="chatgpt_web_test")

    assert capsule["schema_id"] == CAPSULE_SCHEMA_ID
    assert capsule["objective"] == "unit browser agent"
    assert capsule["agent_plan"]["no_send_click"] is True
    assert "inspect_headless" in capsule["agent_plan"]["commands"]
    loop = capsule["gpt_dialogue_action_loop"]
    assert loop["schema_id"] == "ion.codex_browser_agent.gpt_dialogue_action_loop.v1"
    assert "approved_gpt_turn" in {phase["phase"] for phase in loop["phases"]}
    assert "semantic_dom_verification" in {phase["phase"] for phase in loop["phases"]}
    assert loop["authority"]["operator_approved_send_required"] is True
    assert loop["authority"]["silent_send_authority"] is False
    assert loop["authority"]["action_execution_from_chat_text"] is False
    assert loop["authority"]["browser_game_client_control_authority"] is False
    assert loop["authority"]["third_party_terms_bypass_authority"] is False
    assert loop["advanced_skill_benchmark"]["status"] == "sandbox_only_design"
    assert "live MMORPG botting" in loop["advanced_skill_benchmark"]["forbidden_examples"]
    cdp_witness = capsule["cdp_accessibility_witness"]
    assert cdp_witness["schema_id"] == "ion.codex_browser_agent.cdp_accessibility_witness.v1"
    assert "CDP Accessibility.getFullAXTree" in cdp_witness["read_only_methods"]
    assert "native_action_cards" in cdp_witness["target_surfaces"]
    assert "dialog" in cdp_witness["target_roles"]
    assert cdp_witness["authority"]["read_only_probe"] is True
    assert cdp_witness["authority"]["playwright_send_click_authority"] is False
    assert cdp_witness["authority"]["cookie_read_authority"] is False
    sandbox_benchmark = capsule["sandbox_skill_benchmark"]
    assert sandbox_benchmark["schema_id"] == "ion.codex_browser_agent.sandbox_skill_benchmark.v1"
    assert sandbox_benchmark["case_count"] == 3
    assert "synthetic_phase_reaction_grid" in {case["case_id"] for case in sandbox_benchmark["benchmark_cases"]}
    assert sandbox_benchmark["authority"]["sandbox_only"] is True
    assert sandbox_benchmark["authority"]["third_party_game_client_control_authority"] is False
    assert "third_party_game_client" in sandbox_benchmark["forbidden_surfaces"]
    self_loop = capsule["self_evolution_loop"]
    assert self_loop["schema_id"] == "ion.codex_browser_agent.self_evolution_loop.v1"
    self_phases = {phase["phase"] for phase in self_loop["cycle_phases"]}
    assert {
        "observe_current_capability_state",
        "ask_gpt_for_candidate_improvements",
        "extract_candidate_actions",
        "rank_candidates",
        "prove_candidate_in_sandbox",
        "prepare_bounded_patch_or_packet",
        "operator_or_policy_gate",
        "write_receipt_and_next_capsule",
    } <= self_phases
    candidate_classes = {row["candidate_class"] for row in self_loop["candidate_classes"]}
    assert {
        "dom_selector_repair",
        "action_detail_extraction",
        "ui_compaction_and_state",
        "pending_message_ux",
        "cdp_accessibility_witness",
        "sandbox_skill_benchmark",
        "test_hardening",
    } <= candidate_classes
    assert self_loop["score_weights"]["operator_value"] > self_loop["score_weights"]["implementation_cost"]
    assert self_loop["top_candidate_id"] == "all_current_candidates_validated"
    assert self_loop["implemented_candidate_count"] == 7
    assert self_loop["ranked_candidate_count"] >= 7
    assert self_loop["ranked_candidate_queue"][0]["status"] == "implemented_validated"
    assert self_loop["ranked_candidate_queue"][1]["status"] == "implemented_validated"
    assert self_loop["ranked_candidate_queue"][2]["status"] == "implemented_validated"
    assert self_loop["ranked_candidate_queue"][3]["status"] == "implemented_validated"
    assert self_loop["ranked_candidate_queue"][4]["status"] == "implemented_validated"
    assert self_loop["ranked_candidate_queue"][5]["status"] == "implemented_validated"
    assert self_loop["ranked_candidate_queue"][6]["status"] == "implemented_validated"
    assert "extension_parser_smoke" in self_loop["ranked_candidate_queue"][5]["proof_plan"]
    assert "sandbox_benchmark_cli" in self_loop["ranked_candidate_queue"][6]["proof_plan"]
    assert self_loop["ranked_candidate_queue"][0]["candidate_class"] == "action_detail_extraction"
    assert "extension_parser_smoke" in self_loop["ranked_candidate_queue"][0]["proof_plan"]
    assert "third_party_game_client_or_terms_evasion_requested" in self_loop["stop_conditions"]
    assert self_loop["authority"]["patch_apply_from_gpt_text_authority"] is False
    assert self_loop["authority"]["native_action_auto_approval_authority"] is False
    assert self_loop["authority"]["accepted_state_authority"] is False
    assert self_loop["authority"]["browser_game_client_control_authority"] is False
    assert capsule["authority"]["playwright_send_click_authority"] is False
    assert capsule["production_authority"] is False
    assert {row["capability_id"] for row in capsule["capabilities"]} >= {
        "python_playwright",
        "dom_probe_extension",
        "chatops_bridge_extension",
    }


def test_plan_run_writes_capsule_report_requirements_and_receipt(tmp_path: Path):
    seed_root(tmp_path)
    write_seed_candidate_profile(tmp_path, "chatgpt_web_test")

    result = run_codex_browser_agent(tmp_path, inspect=False, profile_id="chatgpt_web_test")

    assert result["ok"] is True
    assert result["mode"] == "plan_only"
    assert result["no_send_click_performed"] is True
    assert result["receipt_path"].endswith(".receipt.json")
    assert (tmp_path / LATEST_CAPSULE_PATH).exists()
    assert (tmp_path / LATEST_REPORT_PATH).exists()
    report = json.loads((tmp_path / LATEST_REPORT_PATH).read_text(encoding="utf-8"))
    assert report["authority"]["playwright_send_click_authority"] is False
    assert report["artifacts"]["latest_capsule_path"] == result["capsule_path"]

    summary = latest_codex_browser_agent_summary(tmp_path)
    assert summary["status"] == "planned"
    assert summary["no_send_click_performed"] is True
    assert summary["artifacts"]["receipt_path"] == result["receipt_path"]
    assert summary["gpt_dialogue_action_loop"]["authority"]["operator_approved_send_required"] is True
    assert summary["gpt_dialogue_action_loop"]["authority"]["browser_game_client_control_authority"] is False
    assert summary["cdp_accessibility_witness"]["schema_id"] == "ion.codex_browser_agent.cdp_accessibility_witness.v1"
    assert summary["cdp_accessibility_witness"]["authority"]["native_action_approval_authority"] is False
    assert summary["sandbox_skill_benchmark"]["schema_id"] == "ion.codex_browser_agent.sandbox_skill_benchmark.v1"
    assert summary["sandbox_skill_benchmark"]["authority"]["third_party_game_client_control_authority"] is False
    assert summary["self_evolution_loop"]["schema_id"] == "ion.codex_browser_agent.self_evolution_loop.v1"
    assert summary["self_evolution_loop"]["authority"]["patch_apply_from_gpt_text_authority"] is False


def test_cockpit_view_model_projects_codex_browser_agent(tmp_path: Path):
    seed_minimal_cockpit_runtime(tmp_path)
    write_seed_candidate_profile(tmp_path, "chatgpt_web_test")
    run_codex_browser_agent(tmp_path, inspect=False, profile_id="chatgpt_web_test")

    model = build_cockpit_view_model(tmp_path)

    agent = model["extension_micro_shell"]["codex_browser_agent"]
    assert agent["schema_id"] == "ion.codex_browser_agent.v1"
    assert agent["status"] == "planned"
    assert agent["no_send_click_performed"] is True
    assistant_map = model["extension_micro_shell"]["computer_assistant_capability_map"]
    assert assistant_map["schema_id"] == "ion.browser_gpt_computer_assistant_capability_map.v1"
    assert assistant_map["production_authority"] is False
    assert assistant_map["live_execution_authority"] is False
    assert assistant_map["authority"]["computer_control_authority"] is False
    lane_ids = {row["lane_id"] for row in assistant_map["architecture_lanes"]}
    assert {
        "in_page_dom_bridge",
        "semantic_playwright_verifier",
        "cdp_accessibility_tree",
        "screen_computer_use_harness",
        "action_gateway_bridge",
        "gpt_dialogue_action_loop",
        "sandbox_skill_benchmark",
        "self_evolution_loop",
        "context_capsule_memory",
    } <= lane_ids
    dialogue_lane = next(row for row in assistant_map["architecture_lanes"] if row["lane_id"] == "gpt_dialogue_action_loop")
    assert dialogue_lane["operator_approved_send_required"] is True
    assert dialogue_lane["native_action_approval_required"] is True
    sandbox_lane = next(row for row in assistant_map["architecture_lanes"] if row["lane_id"] == "sandbox_skill_benchmark")
    assert sandbox_lane["authority"] == "sandbox_only_no_third_party_game_botting"
    assert sandbox_lane["case_count"] == 3
    assert sandbox_lane["third_party_game_client_control_authority"] is False
    cdp_lane = next(row for row in assistant_map["architecture_lanes"] if row["lane_id"] == "cdp_accessibility_tree")
    assert cdp_lane["target_surface_count"] >= 6
    assert cdp_lane["target_role_count"] >= 8
    self_evolution_lane = next(row for row in assistant_map["architecture_lanes"] if row["lane_id"] == "self_evolution_loop")
    assert self_evolution_lane["authority"] == "candidate_self_evolution_only_no_autonomous_mutation"
    assert self_evolution_lane["patch_apply_from_gpt_text_authority"] is False
    assert self_evolution_lane["native_action_auto_approval_authority"] is False
    assert self_evolution_lane["candidate_class_count"] >= 7
    assert self_evolution_lane["ranked_candidate_count"] >= 7
    assert self_evolution_lane["implemented_candidate_count"] == 7
    assert self_evolution_lane["top_candidate_id"] == "all_current_candidates_validated"


def test_sandbox_skill_benchmark_writes_local_result(tmp_path: Path):
    seed_root(tmp_path)
    write_seed_candidate_profile(tmp_path, "chatgpt_web_test")

    result = run_sandbox_skill_benchmark(tmp_path)

    assert result["ok"] is True
    assert result["schema_id"] == "ion.codex_browser_agent.sandbox_skill_benchmark_result.v1"
    assert result["status"] == "passed"
    assert result["case_count"] == 3
    assert result["scripted_step_count"] >= 10
    assert result["measured_score"] >= result["minimum_pass_score"]
    assert result["authority"]["third_party_game_client_control_authority"] is False
    assert result["forbidden_surface_check"]["terms_bypass_authority"] is False
    assert (tmp_path / LATEST_SANDBOX_BENCHMARK_PATH).exists()


def test_chatgpt_browser_branch_exposes_codex_agent_read_routes():
    description = action_branch_describe(".", branch_id="chatgpt_browser_carrier_context")

    routes = description["branch"]["routes"]
    route_ids = {route["route_id"] for route in routes}
    assert {
        "browser_gpt_codex_agent_report",
        "browser_gpt_codex_agent_capsule",
        "browser_gpt_codex_agent_requirements",
    } <= route_ids
    report_route = next(route for route in routes if route["route_id"] == "browser_gpt_codex_agent_report")
    assert report_route["mutates_state"] is False


def test_profile_artifacts_can_write_comparison_candidate_without_promoting_latest(tmp_path: Path):
    seed_root(tmp_path)
    baseline = build_selector_profile(
        "chatgpt_web_test",
        surface_candidates=required_ready_candidates(),
        calibration_source="unit_baseline",
    )
    write_profile_artifacts(tmp_path, profile=baseline, promote_latest=True)
    latest_before = (tmp_path / LATEST_PROFILE_PATH).read_text(encoding="utf-8")

    candidate = build_selector_profile(
        "chatgpt_web_test_candidate",
        surface_candidates={"composer": [live_candidate("#prompt-textarea", role="textbox")]},
        calibration_source="unit_candidate",
    )
    result = write_profile_artifacts(tmp_path, profile=candidate, promote_latest=False)

    assert result["promoted_latest"] is False
    assert (tmp_path / result["profile_path"]).exists()
    assert (tmp_path / LATEST_PROFILE_PATH).read_text(encoding="utf-8") == latest_before
    index = json.loads((tmp_path / INDEX_PATH).read_text(encoding="utf-8"))
    assert index["latest_profile_id"] == "chatgpt_web_test"
    assert index["profiles"][0]["profile_id"] == "chatgpt_web_test_candidate"
    assert index["profiles"][0]["promoted_latest"] is False


def test_selector_profile_comparison_detects_required_regression(tmp_path: Path):
    seed_root(tmp_path)
    baseline = build_selector_profile(
        "chatgpt_web_test",
        surface_candidates=required_ready_candidates(),
        calibration_source="unit_baseline",
    )
    candidate = build_selector_profile(
        "chatgpt_web_test_candidate",
        surface_candidates={"composer": [live_candidate("#prompt-textarea", role="textbox")]},
        calibration_source="unit_candidate",
    )
    write_profile_artifacts(tmp_path, profile=baseline, promote_latest=True)
    candidate_result = write_profile_artifacts(tmp_path, profile=candidate, promote_latest=False)

    comparison = compare_selector_profiles(
        tmp_path,
        candidate_profile_path=candidate_result["profile_path"],
        baseline_profile_path=LATEST_PROFILE_PATH,
        run_id="unit-comparison",
    )

    assert comparison["schema_id"] == COMPARISON_SCHEMA_ID
    assert comparison["status"] == "regression_detected"
    assert comparison["regression_count"] >= 1
    assert comparison["candidate_profile_id"] == "chatgpt_web_test_candidate"
    assert (tmp_path / comparison["comparison_path"]).exists()


def test_agent_comparison_inspection_preserves_canonical_latest(tmp_path: Path, monkeypatch):
    seed_root(tmp_path)
    baseline = build_selector_profile(
        "chatgpt_web_test",
        surface_candidates=required_ready_candidates(),
        calibration_source="unit_baseline",
    )
    write_profile_artifacts(tmp_path, profile=baseline, promote_latest=True)
    latest_before = (tmp_path / LATEST_PROFILE_PATH).read_text(encoding="utf-8")

    def fake_calibrate(root: Path, *, profile_id: str, promote_latest: bool = True, **kwargs):
        candidate = build_selector_profile(
            profile_id,
            surface_candidates={"composer": [live_candidate("#prompt-textarea", role="textbox")]},
            calibration_source="unit_fake_playwright",
        )
        return write_profile_artifacts(root, profile=candidate, promote_latest=promote_latest)

    monkeypatch.setattr(agent_module, "calibrate_with_playwright", fake_calibrate)

    result = run_codex_browser_agent(
        tmp_path,
        inspect=True,
        profile_id="chatgpt_web_test",
        comparison_profile=True,
    )

    assert result["comparison_profile"] is True
    assert result["canonical_profile_preserved"] is True
    assert result["inspection_result"]["promoted_latest"] is False
    assert result["comparison_report"]["regression_count"] >= 1
    assert result["status"] == "degraded"
    assert (tmp_path / result["comparison_report"]["comparison_path"]).exists()
    assert (tmp_path / LATEST_PROFILE_PATH).read_text(encoding="utf-8") == latest_before
    summary = latest_codex_browser_agent_summary(tmp_path)
    assert summary["comparison_profile"] is True
    assert summary["canonical_profile_preserved"] is True
    assert summary["comparison_regression_count"] >= 1
