from kernel.ion_codex_model_moves import (
    build_codex_model_move_plan,
    codex_exec_args_from_model_move,
    infer_codex_work_class,
    list_codex_model_profiles,
)


def test_model_profiles_mark_usage_limits_as_advisory():
    profiles = list_codex_model_profiles()

    assert profiles["verdict"] == "ION_CODEX_CLI_MODEL_MOVES_READY"
    assert profiles["usage_limits_authoritative"] is False
    assert profiles["profiles"]["gpt-5.3-codex-spark"]["usage_pool_authority"] == "operator_observed_pending_verification"
    assert profiles["profiles"]["gpt-5.5"]["reasoning_efforts_supported"] == ["low", "medium", "high", "xhigh"]


def test_conserve_main_bank_routes_low_risk_status_to_spark():
    move = build_codex_model_move_plan(
        lane_id="codex_general",
        objective="Read-only smoke status check.",
    )

    assert move["selected_model"] == "gpt-5.5"
    assert move["selected_reasoning_effort"] == "medium"
    assert move["usage_limits_authoritative"] is False
    assert codex_exec_args_from_model_move(move) == [
        "-m",
        "gpt-5.5",
        "-c",
        "model_reasoning_effort=medium",
    ]
    assert not any("service_tier=" in arg for arg in codex_exec_args_from_model_move(move))
    assert "chatgpt_account_codex_cli_rejects_legacy_fast_pool_use_supported_frontier_route" in move["selection_reason"]


def test_model_move_escalates_authority_and_architecture_to_gpt55():
    steward = build_codex_model_move_plan(
        lane_id="ion_system",
        stage_id="steward_route",
        objective="Classify public URL and privacy policy authority.",
    )
    architecture = build_codex_model_move_plan(
        lane_id="codex_general",
        objective="Plan architecture and schema changes for the router.",
    )

    assert steward["selected_model"] == "gpt-5.5"
    assert steward["selected_reasoning_effort"] == "high"
    assert architecture["work_class"] == "architecture_design"
    assert architecture["selected_model"] == "gpt-5.5"


def test_low_risk_codex_implementation_uses_spark_pool():
    move = build_codex_model_move_plan(
        lane_id="codex_general",
        objective="Implement a focused parser fix.",
    )

    assert infer_codex_work_class(lane_id="codex_general", objective="Implement a focused parser fix.") == "code_patch"
    assert move["selected_model"] == "gpt-5.5"
    assert move["selected_reasoning_effort"] == "medium"
    assert "chatgpt_account_codex_cli_rejects_legacy_spark_pool_use_supported_frontier_route" in move["selection_reason"]
