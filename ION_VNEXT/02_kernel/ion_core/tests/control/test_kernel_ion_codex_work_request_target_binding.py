from __future__ import annotations

from kernel.ion_codex_work_request_target_binding import (
    apply_codex_work_request_target_binding,
    build_codex_work_request_target_binding,
    compact_codex_work_request_target_binding_projection,
    normalize_target_root_id,
)


def test_normalizes_aliases_and_family_names():
    assert normalize_target_root_id("ion_development") == "active_ion_control"
    assert normalize_target_root_id("ION_GPT") == "ion_gpt"
    assert normalize_target_root_id("dAimon") == "daimon"
    assert normalize_target_root_id("quarantine") == "quarentine"


def test_builds_explicit_browser_extension_binding():
    binding = build_codex_work_request_target_binding(
        {
            "target_root_id": "browser_extension",
            "target_project_subpath": "ion_chatops_bridge",
            "planned_writes": ["src/content.ts"],
        },
        source="unit_test",
    )

    assert binding["schema_id"] == "ion.codex_work_request_target_binding.v1"
    assert binding["target_root_id"] == "browser_extension"
    assert binding["movement_class"] == "BROWSER_EXTENSION_MOVEMENT"
    assert binding["target_family"] == "browser_extension"
    assert binding["root_relation"] == "sibling_project_root"
    assert binding["binding_source"] == "request.target_root_id"
    assert binding["target_project_subpath"] == "ion_chatops_bridge"
    assert binding["planned_writes"] == ["src/content.ts"]
    assert binding["required_for_queue_preflight"] is True
    assert binding["runner_legacy_default_allowed"] is False
    assert binding["production_authority"] is False
    assert binding["live_execution_authority"] is False
    assert binding["accepted_state_claim"] is False


def test_infers_target_from_planned_write_path():
    binding = build_codex_work_request_target_binding(
        {"planned_writes": ["ION_GPT/01_GPT_BUILDER_INPUTS/README.md"]},
        source="unit_test",
    )

    assert binding["target_root_id"] == "ion_gpt"
    assert binding["movement_class"] == "CUSTOM_GPT_RELEASE_MOVEMENT"
    assert binding["binding_source"] == "request.planned_writes"


def test_apply_preserves_payload_and_adds_template():
    payload: dict[str, object] = {}
    binding = apply_codex_work_request_target_binding(
        payload,
        {
            "target_root_id": "mcp",
            "target_project_subpath": "ion_local_bridge",
            "planned_artifacts": ["mcp/receipt.json"],
        },
        source="unit_test",
    )

    assert binding["target_root_id"] == "mcp"
    assert payload["target_root_id"] == "mcp"
    assert payload["movement_class"] == "MCP_BRIDGE_MOVEMENT"
    assert payload["target_project_subpath"] == "ion_local_bridge"
    assert payload["planned_artifacts"] == ["mcp/receipt.json"]
    assert payload["ai_movement_request_template"] == binding


def test_compact_projection_accepts_matching_template_and_runner_evidence():
    request = {
        "target_root_id": "browser_extension",
        "movement_class": "BROWSER_EXTENSION_MOVEMENT",
    }
    binding = build_codex_work_request_target_binding(request, source="unit_test")
    request["ai_movement_request_template"] = binding

    projection = compact_codex_work_request_target_binding_projection(request)

    assert projection["accepted"] is True
    assert projection["status"] == "TARGET_BINDING_OK"
    assert projection["warning_level"] == "ok"
    assert projection["target_root_id"] == "browser_extension"
    assert projection["blocker_count"] == 0


def test_compact_projection_blocks_missing_target_evidence():
    projection = compact_codex_work_request_target_binding_projection({})

    assert projection["accepted"] is False
    assert projection["warning_level"] == "blocked"
    assert projection["status"] == "TARGET_BINDING_MISSING"
    assert projection["blocker_codes"] == ["TARGET_BINDING_MISSING"]


def test_compact_projection_blocks_template_target_conflict():
    binding = build_codex_work_request_target_binding(
        {"target_root_id": "browser_extension"},
        source="unit_test",
    )
    projection = compact_codex_work_request_target_binding_projection(
        {
            "target_root_id": "active_ion_control",
            "movement_class": "BROWSER_EXTENSION_MOVEMENT",
            "ai_movement_request_template": binding,
        }
    )

    assert projection["accepted"] is False
    assert projection["warning_level"] == "blocked"
    assert "TARGET_BINDING_TARGET_CONFLICT" in projection["blocker_codes"]
