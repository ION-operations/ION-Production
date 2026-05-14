from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def load_yaml(rel: str):
    return yaml.safe_load(read(rel))


def load_json(rel: str):
    return json.loads(read(rel))


def test_ion_wide_protocol_is_not_custom_gpt_only():
    text = read("ION/02_architecture/ARCHITECTURE_SIGNAL_CAPTURE_AND_ORDERED_CONTEXT_FANOUT_PROTOCOL.md")

    assert "ION-wide candidate architecture law" in text
    assert "not limited to the Custom GPT" in text
    assert "ARCHITECTURE_SIGNAL_CAPTURE_LAW" in text
    assert "Ordered Context Fan-Out / Sequential Baton" in text
    assert "Agent B receives Agent A's dense baton before analyzing section B" in text
    assert "Agent C receives the Agent A plus Agent B baton set before analyzing section C" in text
    assert "The carrier must not rely on chat memory alone" in text
    assert "recovered dirty-tree audit is candidate operational evidence" in text
    assert "No accepted ION state is claimed" in text

    for projection in [
        "Custom GPT",
        "Codex CLI",
        "ChatGPT Browser",
        "MCP Actions",
        "local project workbench",
    ]:
        assert projection in text

    for alias in [
        "relay packet",
        "context baton",
        "handoff capsule",
        "forward alert",
        "downstream alert",
        "upstream reopen alert",
        "branch return metadata",
        "fan-in settlement input",
    ]:
        assert alias in text


def test_ion_architecture_signal_schema_hardens_capture_contract():
    schema = load_json("ION/03_registry/ion_architecture_signal.schema.json")
    required = schema["required"]

    for field in [
        "signal_id",
        "captured_at_utc",
        "source",
        "raw_summary",
        "normalized_requirement",
        "aliases",
        "related_existing_protocols",
        "product_version_target",
        "status",
        "continuity_export_required",
        "tests_required",
        "accepted_state_claim",
        "route",
        "continuity_export_refs",
        "ordered_context_fanout",
    ]:
        assert field in required

    assert schema["properties"]["schema_id"]["const"] == "ion.architecture_signal.v0_1"
    assert schema["properties"]["source"]["enum"] == [
        "operator_chat",
        "mounted_doc",
        "codex_return",
        "artifact",
    ]
    assert "candidate_unimplemented" in schema["properties"]["status"]["enum"]
    assert "rejected_with_reason" in schema["properties"]["status"]["enum"]
    assert schema["properties"]["continuity_export_required"]["const"] is True
    assert schema["properties"]["tests_required"]["const"] is True
    assert schema["properties"]["accepted_state_claim"]["const"] is False
    assert schema["properties"]["route"]["properties"]["target_protocol"]["const"] == "ION_ORDERED_CONTEXT_FANOUT_V4_4"
    assert schema["properties"]["ordered_context_fanout"]["properties"]["scope"]["enum"][0] == "ion_wide"


def test_template_routes_operator_remark_to_ion_wide_ordered_fanout():
    data = load_yaml("ION/07_templates/context/ARCHITECTURE_SIGNAL_CAPTURE.template.yaml")
    schema = load_json("ION/03_registry/ion_architecture_signal.schema.json")

    assert set(data).issubset(set(schema["properties"]))
    for field in schema["required"]:
        assert field in data

    assert data["raw_summary"] == "Agent B needs Agent A's findings before reading section B."
    assert "ION-wide ordered fan-out" in data["normalized_requirement"]
    assert data["product_version_target"] == "v4.4a_v4.4b"
    assert data["status"] == "candidate_unimplemented"
    assert data["continuity_export_required"] is True
    assert data["tests_required"] is True
    assert data["accepted_state_claim"] is False
    assert data["route"]["target_protocol"] == "ION_ORDERED_CONTEXT_FANOUT_V4_4"
    assert data["route"]["ordered_baton_required"] is True

    fanout = data["ordered_context_fanout"]
    assert fanout["protocol_id"] == "ION_ORDERED_CONTEXT_FANOUT_V4_4"
    assert fanout["scope"] == "ion_wide"
    assert fanout["section_order"][1]["agent"] == "Agent B"
    assert fanout["section_order"][1]["input_batons"] == ["Agent A dense baton"]
    assert fanout["section_order"][2]["input_batons"] == [
        "Agent A dense baton",
        "Agent B dense baton",
    ]
    assert fanout["upstream_reopen_alert_required"] is True
    assert fanout["fan_in_settlement_input_required"] is True


def test_custom_gpt_projection_points_back_to_ion_wide_law():
    text = read("../ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL_CAPTURE.md")
    assert "Custom GPT" in text
    assert "ION-wide" in text
    assert "ARCHITECTURE_SIGNAL_CAPTURE_AND_ORDERED_CONTEXT_FANOUT_PROTOCOL.md" in text
