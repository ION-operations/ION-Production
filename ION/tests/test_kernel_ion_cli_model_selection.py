from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import yaml
import pytest

from kernel import ion_carrier_quota_health as quota_health
from kernel import ion_claude_cli_runner as claude_runner
from kernel import ion_cli_model_selection as selection
from kernel import ion_cursor_queue_runner as cursor_runner
from kernel import ion_prompt_spawn_carrier_routing as routing


def _minimal_shell_root(tmp_path: Path, *, active_blackout_window: bool = True) -> Path:
    (tmp_path / "ION" / "05_context" / "current" / "domain_weaver").mkdir(parents=True, exist_ok=True)
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    (tmp_path / "ION" / "REPO_AUTHORITY.md").write_text("", encoding="utf-8")
    repo_root = Path(__file__).resolve().parents[2]
    yaml_text = (repo_root / selection.ROUTING_RELATIVE_PATH).read_text(encoding="utf-8")
    json_text = (repo_root / selection.ROUTING_JSON_RELATIVE_PATH).read_text(encoding="utf-8")
    if active_blackout_window:
        yaml_text = yaml_text.replace(
            "expires_at: '2026-07-24T22:00:00-04:00'",
            "expires_at: '2099-12-31T23:59:59+00:00'",
        )
        json_text = json_text.replace(
            "2026-07-24T22:00:00-04:00",
            "2099-12-31T23:59:59+00:00",
        )
    routing_yaml = tmp_path / selection.ROUTING_RELATIVE_PATH
    routing_yaml.parent.mkdir(parents=True, exist_ok=True)
    routing_yaml.write_text(yaml_text, encoding="utf-8")
    routing_json = tmp_path / selection.ROUTING_JSON_RELATIVE_PATH
    routing_json.parent.mkdir(parents=True, exist_ok=True)
    routing_json.write_text(json_text, encoding="utf-8")
    return tmp_path


def test_domain_leader_selects_exact_opus_4_8_claude(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.context_systems",
        carrier="auto",
    )
    assert sel["carrier_id"] == "claude_cli"
    assert sel["is_domain_leader"] is True
    assert sel["default_model"] == "claude-opus-4-8"


def test_prompt_spawn_surface_picks_approved_claude_model(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    resolved = routing.resolve_carrier_for_domain(
        root,
        domain_id="domain.context_systems",
        carrier="auto",
        work_class="status_summary",
    )
    assert resolved["carrier_id"] == "claude_cli"
    assert resolved["model"] == "claude-opus-4-8"


def test_fallback_chain_includes_model_downgrade(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.cli_carrier_selection_and_usage_fallback",
        work_class="schema_law",
        execution_surface="prompt_spawn",
    )
    chain = sel.get("fallback_chain") or []
    models = [row.get("model") for row in chain if row.get("carrier_id") == "cursor_cli"]
    assert "composer-2.5-fast" in models
    assert "composer-2.5" in models
    downgrade_models = {"composer-2.5", "composer-2.5-fast"}
    assert downgrade_models.issubset(set(models))
    assert "claude-opus-4-8-thinking-high" not in models


def test_resolve_next_fallback_steps_down_ladder(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.lateral_reasoning_and_template_evolution",
        execution_surface="prompt_spawn",
    )
    current = dict(sel)
    current["carrier_id"] = "cursor_cli"
    current["model"] = "composer-2.5-fast"
    nxt = selection.resolve_next_fallback(current, usage_signal="usage_limit")
    assert nxt is not None
    assert nxt.get("carrier_id") == "cursor_cli"
    assert nxt.get("model") == "composer-2.5"


def test_resolve_next_fallback_requires_a_failure_signal(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.lateral_reasoning_and_template_evolution",
        execution_surface="prompt_spawn",
    )
    assert selection.resolve_next_fallback(sel) is None


def test_exact_operator_carrier_models_are_encoded(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    data = selection.load_unified_routing(root)
    assert "claude_cli" not in data.get("disabled_carriers", {})
    assert data["default_carrier"] == "cursor_cli"
    assert data["model_downgrade_ladders"]["cursor_cli"] == [
        "composer-2.5-fast",
        "composer-2.5",
    ]
    assert data["model_downgrade_ladders"]["codex_cli"] == ["gpt-5.6-sol"]


def test_all_fallback_models_are_operator_approved(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(root, domain_id="domain.context_systems")
    for row in sel["fallback_chain"]:
        carrier_id = row["carrier_id"]
        model = row["model"]
        approved = (
            model in selection.OPERATOR_APPROVED_MODELS.get(carrier_id, frozenset())
            or selection.is_leader_tier_model(carrier_id, model)
        )
        assert approved, f"{carrier_id}:{model}"


def test_execution_boundary_allowlists_are_exact() -> None:
    assert selection.approved_models_for_carrier("claude_cli") == (
        "claude-opus-4-8",
        "claude-sonnet-5",
    )
    assert selection.approved_models_for_carrier("cursor_cli") == (
        "composer-2.5-fast",
        "composer-2.5",
    )
    assert selection.approved_models_for_carrier("codex_cli") == (
        "gpt-5.6-sol",
    )
    assert not selection.is_operator_approved_model("claude_cli", "claude-opus-4-1")
    assert not selection.is_operator_approved_model("cursor_cli", "sonnet-4")
    assert not selection.is_operator_approved_model("codex_cli", "gpt-5.5")
    assert not selection.is_operator_approved_model("cursor_cli", "auto")


def test_cursor_experimental_models_are_explicit_execution_only() -> None:
    experimental = (
        "gemini-3.1-pro",
        "cursor-grok-4.5-high",
    )
    leader_tier = (
        "claude-opus-4-8-thinking-high",
        "claude-sonnet-5-thinking-high",
        "gpt-5.6-sol-high",
    )
    assert selection.experimental_models_for_carrier("cursor_cli") == experimental
    assert selection.execution_models_for_carrier("cursor_cli") == (
        "composer-2.5-fast",
        "composer-2.5",
        *leader_tier,
        *experimental,
    )
    assert all(
        selection.is_operator_approved_model("cursor_cli", model)
        for model in (*leader_tier, *experimental)
    )
    assert all(selection.is_leader_tier_model("cursor_cli", model) for model in leader_tier)
    assert not selection.is_experimental_model("cursor_cli", leader_tier[0])
    assert not selection.is_operator_approved_model(
        "cursor_cli", "claude-fable-5-thinking-high"
    )


def test_cursor_experimental_model_requires_explicit_work_class(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    blocked = selection.resolve_execution_selection(
        root,
        domain_id="domain.lateral_reasoning_and_template_evolution",
        carrier="cursor_cli",
        requested_model="gemini-3.1-pro",
        execution_surface="prompt_spawn",
    )
    assert blocked["policy_blocked"] is True
    assert blocked["finding"] == "experimental_model_requires_explicit_work_class"
    assert blocked["fallback_chain"] == []


def test_cursor_experimental_primary_never_enrolls_peer_experiments_as_fallbacks(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    selected = selection.resolve_execution_selection(
        root,
        domain_id="domain.lateral_reasoning_and_template_evolution",
        carrier="cursor_cli",
        requested_model="gemini-3.1-pro",
        work_class="model_evaluation",
        execution_surface="prompt_spawn",
    )
    assert selected["policy_blocked"] is False
    assert selected["model"] == "gemini-3.1-pro"
    assert selected["experimental_model"] is True
    cursor_models = [
        row["model"]
        for row in selected["fallback_chain"]
        if row["carrier_id"] == "cursor_cli"
    ]
    assert cursor_models == [
        "gemini-3.1-pro",
        "composer-2.5-fast",
        "composer-2.5",
    ]
    assert set(cursor_models[1:]).isdisjoint(
        set(selection.experimental_models_for_carrier("cursor_cli"))
    )


def test_cursor_experiment_code_roster_matches_candidate_routing_source() -> None:
    root = Path(__file__).resolve().parents[2]
    routing = yaml.safe_load(
        (root / selection.ROUTING_RELATIVE_PATH).read_text(encoding="utf-8")
    )
    configured = routing["experimental_exact_models"]
    cursor = configured["cursor_cli"]
    assert tuple(cursor["models"]) == selection.experimental_models_for_carrier(
        "cursor_cli"
    )
    assert cursor["explicit_only"] is True
    assert cursor["explicit_work_class_required"] is True
    assert cursor["default_routing"] is False
    assert cursor["fallback_eligible"] is False
    assert cursor["concurrency_limit"] == 1
    assert cursor["read_only"] is True
    assert cursor["cursor_mode"] == "ask"
    assert set(configured["privacy_restricted"]["models"]) == set(
        selection.PRIVACY_RESTRICTED_MODELS
    )


def test_claude_auth_status_does_not_claim_token_freshness(monkeypatch) -> None:
    completed = subprocess.CompletedProcess(
        ["claude", "auth", "status"],
        0,
        stdout=json.dumps({"loggedIn": True, "authMethod": "claude.ai"}),
        stderr="",
    )
    monkeypatch.setattr(claude_runner.subprocess, "run", lambda *_args, **_kwargs: completed)

    status = claude_runner._auth_status("claude")

    assert status["ok"] is True
    assert status["session_record_present"] is True
    assert status["token_freshness_verified"] is False
    assert status["finding"] == "claude_auth_session_present_token_freshness_unverified"


def test_leader_tier_fallback_chain_blocks_cursor_claude_during_availability_window(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.context_systems",
        work_class="status_summary",
        execution_surface="prompt_spawn",
    )
    chain = sel.get("fallback_chain") or []
    cursor_models = [
        (row.get("reason"), row.get("model"))
        for row in chain
        if row.get("carrier_id") == "cursor_cli"
    ]
    assert ("cross_carrier_tier_equivalent", "claude-opus-4-8-thinking-high") not in cursor_models
    composer_rows = [
        model for _, model in cursor_models if str(model).startswith("composer")
    ]
    assert "composer-2.5-fast" in composer_rows


def test_claude_unavailable_leader_domain_selects_composer_during_blackout_window(
    monkeypatch, tmp_path: Path
) -> None:
    root = _minimal_shell_root(tmp_path)

    def fake_probe(_root, carrier_id, **_kwargs):
        return (carrier_id != "claude_cli", f"probe:{carrier_id}")

    monkeypatch.setattr(selection, "probe_carrier_available", fake_probe)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.context_systems",
        work_class="status_summary",
        execution_surface="prompt_spawn",
    )
    assert sel["carrier_id"] == "cursor_cli"
    assert str(sel["model"]).startswith("composer")
    assert sel.get("availability_window_id") is None


def test_non_leader_domain_still_selects_composer_during_blackout_window(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.cli_carrier_selection_and_usage_fallback",
        work_class="schema_law",
        execution_surface="prompt_spawn",
    )
    assert sel["carrier_id"] == "cursor_cli"
    assert sel["model"] == "composer-2.5-fast"
    assert sel.get("availability_window_id") is None


def test_consequential_leader_work_prefers_codex_during_blackout_window(
    monkeypatch, tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)

    def fake_probe(_root, carrier_id, **_kwargs):
        return (carrier_id != "claude_cli", f"probe:{carrier_id}")

    monkeypatch.setattr(selection, "probe_carrier_available", fake_probe)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.context_systems",
        work_class="model_routing",
        execution_surface="prompt_spawn",
    )
    assert sel["carrier_id"] == "codex_cli"
    assert sel["model"] == "gpt-5.6-sol"
    assert sel["reasoning_effort"] == "max"
    assert sel["availability_window_id"] == (
        "PCKT-CURSOR-CLAUDE-BLACKOUT-CODEX-SOL-WINDOW-20260722"
    )
    cursor_claude = [
        row
        for row in sel.get("fallback_chain") or []
        if row.get("carrier_id") == "cursor_cli"
        and str(row.get("model") or "").startswith("claude-")
    ]
    assert cursor_claude == []


def test_consequential_model_routing_domain_selects_sol_max(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        work_class="production_readiness_validation",
        execution_surface="prompt_spawn",
    )
    assert sel["carrier_id"] == "codex_cli"
    assert sel["model"] == "gpt-5.6-sol"
    assert sel["reasoning_effort"] == "max"
    assert sel["model_tier"] == "codex_sol_max"
    assert {row["carrier_id"] for row in sel["fallback_chain"]} <= {
        "codex_cli",
        "claude_cli",
        "cursor_cli",
    }


def test_routine_work_in_critical_domain_routes_to_composer_during_blackout(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        work_class="status_summary",
        execution_surface="prompt_spawn",
    )
    assert sel["carrier_id"] == "cursor_cli"
    assert sel["model"] == "composer-2.5-fast"
    assert sel.get("availability_window_id") is None


def test_explicit_approved_model_is_bound_into_canonical_decision(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    fast = selection.resolve_execution_selection(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        carrier="cursor_cli",
        requested_model="composer-2.5-fast",
        work_class="design_report",
        execution_surface="prompt_spawn",
    )
    composer = selection.resolve_execution_selection(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        carrier="cursor_cli",
        requested_model="composer-2.5",
        work_class="design_report",
        execution_surface="prompt_spawn",
    )

    assert fast["carrier_id"] == "cursor_cli"
    assert fast["model"] == "composer-2.5-fast"
    assert composer["carrier_id"] == "cursor_cli"
    assert composer["model"] == "composer-2.5"
    assert composer["requested_model"] == "composer-2.5"
    assert fast["routing_decision_sha256"] != composer["routing_decision_sha256"]


def test_prompt_spawn_resolution_binds_explicit_opus_instead_of_default_sonnet(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    resolved = routing.resolve_carrier_for_domain(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        carrier="claude_cli",
        requested_model="claude-opus-4-8",
        work_class="architecture_design",
    )

    assert resolved["model"] == "claude-opus-4-8"
    assert resolved["requested_model"] == "claude-opus-4-8"
    assert resolved["unified_selection"]["model"] == "claude-opus-4-8"


def test_consequential_tier_allows_cursor_cross_carrier_equivalent(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        carrier="cursor_cli",
        work_class="production_readiness_validation",
        execution_surface="prompt_spawn",
    )
    assert sel["policy_blocked"] is False
    assert sel["carrier_id"] == "cursor_cli"
    assert sel["model"] == "gpt-5.6-sol-high"
    assert sel["source_model_tier"] == "codex_sol_max"


def test_consequential_tier_cursor_only_constraint_selects_sol_high(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        work_class="production_readiness_validation",
        allowed_carriers=["cursor_cli"],
        execution_surface="prompt_spawn",
    )
    assert sel["policy_blocked"] is False
    assert sel["carrier_id"] == "cursor_cli"
    assert sel["model"] == "gpt-5.6-sol-high"
    assert sel["effective_allowed_carriers"] == ["cursor_cli"]


@pytest.mark.parametrize(
    ("domain_id", "expected_tier", "expected_model"),
    [
        (
            "domain.agent_communication_and_settlement",
            "leader_sonnet",
            "claude-sonnet-5",
        ),
        (
            "domain.context_systems",
            "orchestration_opus",
            "claude-opus-4-8",
        ),
    ],
)
def test_claude_leader_tiers_publish_effective_carrier_allowlist(
    tmp_path: Path,
    domain_id: str,
    expected_tier: str,
    expected_model: str,
) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id=domain_id,
        carrier="claude_cli",
        requested_model=expected_model,
        work_class="status_summary",
        execution_surface="prompt_spawn",
    )

    assert sel["policy_blocked"] is False
    assert sel["source_model_tier"] == expected_tier
    assert sel["model"] == expected_model
    assert sel["tier_allowed_carriers"] == ["claude_cli", "cursor_cli"]
    assert sel["effective_allowed_carriers"] == ["claude_cli", "cursor_cli"]
    assert {row["carrier_id"] for row in sel["fallback_chain"]} == {
        "claude_cli",
        "cursor_cli",
    }


def test_general_tier_cannot_be_widened_to_codex_by_caller(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        work_class="status_summary",
        allowed_carriers=["codex_cli"],
        execution_surface="prompt_spawn",
    )
    assert sel["policy_blocked"] is True
    assert sel["finding"] == "carrier_constraints_empty_intersection"
    assert sel["fallback_chain"] == []


@pytest.mark.parametrize("work_class", [None, "", "unknown", "unspecified"])
def test_leader_prompt_spawn_requires_explicit_work_class(
    tmp_path: Path, work_class: str | None
) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        work_class=work_class,
        execution_surface="prompt_spawn",
    )
    assert sel["policy_blocked"] is True
    assert sel["finding"] == "work_class_required_for_leader_execution"


def test_every_leader_domain_routes_consequential_work_to_sol_max(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    for domain_id in selection.DEFAULT_LEADER_DOMAINS:
        sel = selection.resolve_execution_selection(
            root,
            domain_id=domain_id,
            work_class="production_readiness_validation",
            execution_surface="prompt_spawn",
        )
        assert sel["carrier_id"] == "codex_cli", domain_id
        assert sel["model"] == "gpt-5.6-sol", domain_id
        assert sel["reasoning_effort"] == "max", domain_id
        assert sel["model_tier"] == "codex_sol_max", domain_id


def test_sol_unavailable_fallback_uses_cursor_tier_equivalent_before_claude(
    monkeypatch, tmp_path: Path
) -> None:
    root = _minimal_shell_root(tmp_path)

    def fake_probe(_root, carrier_id, **_kwargs):
        return (carrier_id != "codex_cli", f"probe:{carrier_id}")

    monkeypatch.setattr(selection, "probe_carrier_available", fake_probe)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        work_class="production_readiness_validation",
        execution_surface="prompt_spawn",
    )
    assert sel["carrier_id"] == "cursor_cli"
    assert sel["model"] == "gpt-5.6-sol-high"
    assert sel["model_env"] == "ION_CURSOR_MODEL"
    assert sel["reasoning_effort"] is None
    assert sel["model_tier"] is None
    assert sel["source_model_tier"] == "codex_sol_max"


def test_consequential_runtime_fallback_rebinds_claude_metadata(
    monkeypatch, tmp_path: Path
) -> None:
    root = _minimal_shell_root(tmp_path)
    monkeypatch.setattr(
        selection,
        "probe_carrier_available",
        lambda *_args, **_kwargs: (True, "probe:ready"),
    )
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        work_class="production_readiness_validation",
        execution_surface="prompt_spawn",
    )
    fallback = selection.resolve_next_fallback(
        sel,
        usage_signal="carrier_not_ready",
    )
    assert fallback is not None
    assert fallback["carrier_id"] == "cursor_cli"
    assert fallback["model"] == "gpt-5.6-sol-high"
    assert fallback["model_env"] == "ION_CURSOR_MODEL"
    assert fallback["reasoning_effort"] is None
    assert fallback["model_tier"] is None
    assert fallback["source_model_tier"] == "codex_sol_max"
    assert fallback["selection_reason"] in {
        "usage_limit_fallback",
        "usage_limit_fallback_cross_carrier",
    }
    assert fallback["parent_routing_decision_id"] == sel["routing_decision_id"]
    assert fallback["fallback_decision_id"].startswith("fallback_")


def test_general_domain_selects_composer_fast_speed_lane(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.lateral_reasoning_and_template_evolution",
        execution_surface="prompt_spawn",
    )
    assert sel["carrier_id"] == "cursor_cli"
    assert sel["model"] == "composer-2.5-fast"


def test_json_and_yaml_routing_sources_have_runtime_parity() -> None:
    shell_root = Path(__file__).resolve().parents[2]
    yaml_route = yaml.safe_load((shell_root / selection.ROUTING_RELATIVE_PATH).read_text(encoding="utf-8"))
    json_route = json.loads(
        (shell_root / selection.ROUTING_JSON_RELATIVE_PATH).read_text(encoding="utf-8")
    )
    assert yaml_route == json_route


def test_missing_routing_uses_current_schema_but_blocks_material_execution(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    (root / selection.ROUTING_RELATIVE_PATH).unlink()
    (root / selection.ROUTING_JSON_RELATIVE_PATH).unlink()

    loaded = selection.load_unified_routing(root)
    resolved = selection.resolve_execution_selection(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        work_class="design_report",
        execution_surface="prompt_spawn",
    )

    assert loaded["schema_id"] == "ion.domain_leader_carrier_routing.v0_4_candidate"
    assert loaded["_routing_source_missing"] is True
    assert resolved["policy_blocked"] is True
    assert resolved["finding"] == "routing_source_required_for_execution"
    assert resolved["fallback_chain"] == []


def test_unknown_carrier_has_no_auto_model_ladder() -> None:
    assert selection._model_ladder({}, "unknown_cli") == []


@pytest.mark.parametrize("json_body", ["{}", "{broken-json"])
def test_routing_source_divergence_blocks_execution(
    tmp_path: Path, json_body: str
) -> None:
    root = _minimal_shell_root(tmp_path)
    json_path = root / selection.ROUTING_JSON_RELATIVE_PATH
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json_body, encoding="utf-8")
    resolved = selection.resolve_execution_selection(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        work_class="production_readiness_validation",
        execution_surface="prompt_spawn",
    )
    assert resolved["policy_blocked"] is True
    assert resolved["finding"] == "routing_source_parity_mismatch"
    assert resolved["fallback_chain"] == []


def test_unknown_carrier_request_fails_closed(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    resolved = selection.resolve_execution_selection(
        root,
        domain_id="domain.context_systems",
        carrier="gemini_cli",
        work_class="status_summary",
        execution_surface="prompt_spawn",
    )
    assert resolved["policy_blocked"] is True
    assert resolved["finding"] == "unsupported_carrier_request"
    assert all(row["carrier_id"] != "gemini_cli" for row in resolved["fallback_chain"])


def test_claude_runner_defaults_to_sonnet_5_without_permission_bypass() -> None:
    command = claude_runner.build_claude_command(
        claude_binary="claude",
        model=claude_runner.DEFAULT_MODEL,
    )
    assert claude_runner.DEFAULT_MODEL == "claude-sonnet-5"
    assert "--dangerously-skip-permissions" not in command
    assert command[command.index("--output-format") + 1] == "json"
    assert command[command.index("--permission-mode") + 1] == "dontAsk"
    assert command[command.index("--tools") + 1] == "Read,Glob,Grep"
    assert "--no-session-persistence" in command


def test_command_builders_refuse_unapproved_models_and_permission_bypass() -> None:
    with pytest.raises(ValueError, match="unapproved_claude_model"):
        claude_runner.build_claude_command(claude_binary="claude", model="claude-opus-4-1")
    with pytest.raises(ValueError, match="claude_permission_bypass_forbidden"):
        claude_runner.build_claude_command(
            claude_binary="claude",
            model="claude-sonnet-5",
            skip_permissions=True,
        )
    with pytest.raises(ValueError, match="unapproved_cursor_model"):
        cursor_runner._build_cursor_command(
            cursor_binary="cursor-agent",
            model="sonnet-4",
            mode="",
            force=True,
        )


def test_is_usage_limit_failure_detects_signal() -> None:
    assert selection.is_usage_limit_failure("Error: usage limit reached for model")
    assert not selection.is_usage_limit_failure("completed successfully")
    assert selection.is_usage_limit_failure(
        "You've hit your weekly limit · resets Jul 24, 10pm (America/Toronto)"
    )


def test_is_carrier_whole_quota_exhaustion_detects_weekly_limit() -> None:
    weekly = (
        "You've hit your weekly limit · resets Jul 24, 10pm (America/Toronto)"
    )
    assert selection.is_carrier_whole_quota_exhaustion(output_text=weekly)
    assert not selection.is_carrier_whole_quota_exhaustion(
        output_text="Error: usage limit reached for model"
    )


def test_claude_whole_quota_crosses_to_codex_during_blackout_window(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.context_systems",
        work_class="status_summary",
        execution_surface="prompt_spawn",
    )
    current = dict(sel)
    current["carrier_id"] = "claude_cli"
    current["model"] = "claude-opus-4-8"
    weekly = (
        "You've hit your weekly limit · resets Jul 24, 10pm (America/Toronto)"
    )
    nxt = selection.resolve_next_fallback(current, output_text=weekly)
    assert nxt is not None
    assert nxt["carrier_id"] == "cursor_cli"
    assert str(nxt["model"]).startswith("composer")
    assert nxt["selection_reason"] == "usage_limit_fallback_cross_carrier"
    assert nxt["whole_cli_quota_exhaustion"] is True
    assert "claude_cli" in (nxt.get("exhausted_carriers") or [])


def test_same_model_cross_carrier_preferred_over_same_carrier_downgrade(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.context_systems",
        work_class="status_summary",
        execution_surface="prompt_spawn",
    )
    current = dict(sel)
    current["carrier_id"] = "claude_cli"
    current["model"] = "claude-opus-4-8"
    per_model = "Error: usage limit reached for model claude-opus-4-8"
    nxt = selection.resolve_next_fallback(current, output_text=per_model)
    assert nxt is not None
    assert nxt["carrier_id"] == "claude_cli"
    assert nxt["model"] == "claude-sonnet-5"
    assert nxt["selection_reason"] == "usage_limit_fallback"


def test_exhausted_carrier_not_retried_after_whole_quota_crossover(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.context_systems",
        work_class="status_summary",
        execution_surface="prompt_spawn",
    )
    current = dict(sel)
    current["carrier_id"] = "claude_cli"
    current["model"] = "claude-opus-4-8"
    weekly = (
        "You've hit your weekly limit · resets Jul 24, 10pm (America/Toronto)"
    )
    first = selection.resolve_next_fallback(current, output_text=weekly)
    assert first is not None
    assert first["carrier_id"] == "cursor_cli"
    assert str(first["model"]).startswith("composer")
    assert "claude_cli" in (first.get("exhausted_carriers") or [])
    second = selection.resolve_next_fallback(
        dict(first),
        output_text="Error: usage limit reached for model composer-2.5-fast",
    )
    assert second is not None
    assert second["carrier_id"] == "cursor_cli"
    assert second["model"] == "composer-2.5"
    assert "claude_cli" in (first.get("exhausted_carriers") or [])


def test_model_routing_mitosis_candidate_closure_is_proof_bound() -> None:
    shell_root = Path(__file__).resolve().parents[2]
    domain_root = (
        shell_root
        / "ION/05_context/current/domain_weaver/candidate_founding_domains/"
        "domain.model_routing_and_reasoning_economics"
    )
    receipt_path = domain_root / "receipts/MODEL_ROUTING_MITOSIS_CLOSURE.candidate.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt_sha = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    ledger = yaml.safe_load(
        (domain_root / "BLOCKER_LEDGER.candidate.yaml").read_text(encoding="utf-8")
    )
    relay = yaml.safe_load(
        (domain_root / "CROSS_DOMAIN_RELAY.candidate.yaml").read_text(encoding="utf-8")
    )
    sol_receipt = json.loads(
        (domain_root / "receipts/MODEL_ROUTING_SOL_MAX_EXECUTION.candidate.json").read_text(
            encoding="utf-8"
        )
    )
    final_push = json.loads(
        (domain_root / "receipts/FINAL_PUSH_DOMAIN_CLOSURE.candidate.json").read_text(
            encoding="utf-8"
        )
    )
    substantive = json.loads(
        (
            shell_root
            / "ION/05_context/current/domain_weaver/receipts/"
            "SUBSTANTIVE_BLOCKER_CLOSURE.candidate.json"
        ).read_text(encoding="utf-8")
    )

    blockers = {row["id"]: row for row in ledger["blockers"]}
    closure = blockers["BLK-RC-MITOSIS-001"]
    assert receipt["closure_scope"] == ["BLK-RC-MITOSIS-001"]
    assert receipt["steward_candidate_intake"]["status"] == "ACCEPTED"
    assert receipt["blocker_translation_intake"]["status"] == "ACCEPTED"
    assert receipt["accepted_state_authority"] is False
    assert receipt["production_authority"] is False
    assert receipt["live_execution_authority"] is False
    assert closure["status"] == "CLOSED"
    assert closure["closure_posture"] == "candidate_only_no_accepted_state"
    assert closure["closure_receipt_sha256"] == receipt_sha
    assert not [
        row for row in ledger["blockers"] if row.get("status") in {"OPEN", "REOPENED"}
    ]
    assert sol_receipt["closure_scope"] == [
        "BLK-MRA03",
        "BLK-MRA-SOL-EXECUTION-001",
    ]
    for stale in (substantive, final_push):
        assert stale["superseded_by"]["sha256"] == receipt_sha
        assert stale["original_fields_preserved"] is True
    assert relay["supersession_status"] == "PARTIALLY_SUPERSEDED"
    assert relay["superseded_by"]["sha256"] == receipt_sha
    assert {row["assertion"] for row in relay["superseded_assertions"]} == {
        "no_kernel_domain_or_model_selection_binding",
        "no_sub_charter_for_cli_model_execution_law",
        "context_proof_return_gate_unexercised",
    }


def test_infrastructure_fit_bonus_favors_cursor_universal_access_lane() -> None:
    shell_root = Path(__file__).resolve().parents[2]
    routing = selection.load_unified_routing(shell_root)
    cursor_bonus = selection._infrastructure_fit_bonus(routing, "cursor_cli")
    claude_bonus = selection._infrastructure_fit_bonus(routing, "claude_cli")
    assert cursor_bonus > claude_bonus
    assert cursor_bonus >= 11.0


def test_exhausted_claude_health_record_routes_leader_to_composer_during_blackout(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    weekly = (
        "You've hit your weekly limit · resets Jul 24, 10pm (America/Toronto)"
    )
    quota_health.record_whole_cli_quota_exhaustion(
        root,
        carrier_id="claude_cli",
        output_text=weekly,
        evidence_run_id="test_run_exhausted_claude",
    )
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.context_systems",
        work_class="status_summary",
        execution_surface="prompt_spawn",
    )
    assert sel["carrier_id"] == "cursor_cli"
    assert str(sel["model"]).startswith("composer")
    claude_rows = [
        row for row in sel["fallback_chain"] if row.get("carrier_id") == "claude_cli"
    ]
    assert claude_rows
    assert claude_rows[0]["available"] is False
    assert str(claude_rows[0]["probe_detail"]).startswith("carrier_quota_exhausted:")


def test_exhausted_carrier_health_reset_expiry_restores_claude_eligibility(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    past_reset = "2020-01-01T00:00:00+00:00"
    quota_health.record_carrier_exhaustion(
        root,
        carrier_id="claude_cli",
        signal_class=quota_health.SIGNAL_WHOLE_CLI_QUOTA_EXHAUSTION,
        reset_hint="Jan 1, 12am (UTC)",
        reset_at_iso=past_reset,
        evidence_run_id="test_run_expired_reset",
    )
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.context_systems",
        work_class="status_summary",
        execution_surface="prompt_spawn",
    )
    assert sel["carrier_id"] == "claude_cli"
    assert sel["model"] == "claude-opus-4-8"
    health = quota_health.load_carrier_exhaustion_health(root)
    assert "claude_cli" not in (health.get("records") or {})


def test_absent_health_file_leaves_leader_claude_selection_unchanged(
    tmp_path: Path,
) -> None:
    root = _minimal_shell_root(tmp_path)
    health_path = root / quota_health.CARRIER_EXHAUSTION_HEALTH_RELATIVE_PATH
    assert not health_path.is_file()
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.context_systems",
        work_class="status_summary",
        execution_surface="prompt_spawn",
    )
    assert sel["carrier_id"] == "claude_cli"
    assert sel["model"] == "claude-opus-4-8"


def test_plan_codex_to_cursor_fallback_shape(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    plan = selection.plan_codex_to_cursor_fallback(
        root,
        domain_id="domain.context_systems",
        work_class="operator_message_relay",
    )
    assert plan["schema_id"].startswith("ion.cli_model_selection")
    assert plan.get("carrier_id") == "cursor_cli"
    assert str(plan.get("model") or "").startswith("composer")

# ION R3 focused explicit Claude model tests

def test_r3_explicit_claude_ids_are_approved_only_by_explicit_roster() -> None:
    from kernel import ion_cli_model_selection as _selection

    approved = _selection.approved_models_for_carrier("claude_cli")
    for model_id in ("claude-fable-5",):
        assert model_id not in approved
        assert not _selection.is_operator_approved_model("claude_cli", model_id)
        assert _selection.is_explicit_only_claude_model(model_id)
    assert _selection.is_operator_approved_model("claude_cli", "claude-sonnet-5")
    assert "claude-opus-5" not in approved


def test_r3_existing_claude_models_remain_approved() -> None:
    from kernel import ion_cli_model_selection as _selection

    approved = _selection.approved_models_for_carrier("claude_cli")
    assert "claude-sonnet-5" in approved
    assert "claude-opus-4-8" in approved


def test_r4_claude_alias_request_fails_before_default_fallback(
    tmp_path: Path,
) -> None:
    import pytest
    from kernel import ion_cli_model_selection as _selection

    root = _minimal_shell_root(tmp_path)
    with pytest.raises(
        ValueError,
        match="alias_forbidden_requires_explicit_model_id",
    ):
        _selection.resolve_execution_selection(
            root,
            carrier="claude_cli",
            requested_model="opus",
            execution_surface="prompt_spawn",
        )


def test_r4_explicit_high_end_models_are_not_automatic_defaults(
    tmp_path: Path,
) -> None:
    from kernel import ion_cli_model_selection as _selection

    root = _minimal_shell_root(tmp_path)
    resolved = _selection.resolve_execution_selection(
        root,
        carrier="claude_cli",
        execution_surface="prompt_spawn",
    )
    assert resolved["model"] not in _selection.EXPLICIT_ONLY_CLAUDE_EXECUTION_MODELS


def test_r5_explicit_high_end_model_is_honored_only_when_requested(
    tmp_path: Path,
) -> None:
    import pytest
    from kernel import ion_cli_model_selection as _selection

    root = _minimal_shell_root(tmp_path)
    resolved = _selection.resolve_execution_selection(
        root,
        carrier="claude_cli",
        requested_model="claude-fable-5",
        execution_surface="prompt_spawn",
    )
    assert resolved["model"] == "claude-fable-5"
    with pytest.raises(ValueError, match="sovereign_banned_spawn_model"):
        _selection.resolve_execution_selection(
            root,
            carrier="claude_cli",
            requested_model="claude-opus-5",
            execution_surface="prompt_spawn",
        )


def test_derive_execution_tier_tags_composer_reduced(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    assert selection.derive_execution_tier("cursor_cli", "composer-2.5", shell_root=root) == "reduced"
    assert (
        selection.derive_execution_tier("cursor_cli", "composer-2.5-fast", shell_root=root)
        == "reduced"
    )
    assert (
        selection.derive_execution_tier(
            "cursor_cli",
            "claude-sonnet-5-thinking-high",
            shell_root=root,
        )
        == "full"
    )
    assert selection.derive_execution_tier("claude_cli", "claude-sonnet-5", shell_root=root) == "full"
    assert selection.derive_execution_tier("claude_cli", "claude-fable-5", shell_root=root) == "reduced"


def test_resolve_execution_selection_emits_execution_tier(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    sel = selection.resolve_execution_selection(
        root,
        domain_id="domain.model_routing_and_reasoning_economics",
        carrier="cursor_cli",
        requested_model="composer-2.5",
        work_class="code_implementation",
        execution_surface="prompt_spawn",
    )
    assert sel.get("execution_tier") == "reduced"
    assert sel.get("operation_mode") == "full"


def test_enumerate_carrier_models_matches_execution_boundary() -> None:
    snapshot = selection.enumerate_carrier_models_from_code()
    assert "composer-2.5" in snapshot["cursor_cli"]
    assert "claude-opus-4-8" in snapshot["claude_cli"]
    assert snapshot["codex_cli"] == ("gpt-5.6-sol",)
