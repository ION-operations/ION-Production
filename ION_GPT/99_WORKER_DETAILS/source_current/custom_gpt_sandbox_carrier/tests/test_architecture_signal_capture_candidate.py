#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[5]
PACKAGE = "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def load_yaml(rel: str):
    return yaml.safe_load(read(rel))


def load_json(rel: str):
    return json.loads(read(rel))


def test_instruction_preserves_architecture_signal_capture_law():
    text = read(f"{PACKAGE}/instructions/ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL_CAPTURE.md")
    assert "ARCHITECTURE_SIGNAL_CAPTURE_LAW" in text
    assert "v4.4a: Ordered Context Fan-Out / Sequential Baton" in text
    assert "v4.4b: Architecture Signal Capture / No-Loss Rule" in text
    assert "The carrier must not rely on chat memory alone" in text
    assert "Agent B receives Agent A's dense baton before analyzing section B" in text
    assert "Agent C receives the Agent A plus Agent B baton set before analyzing section C" in text
    assert "No accepted ION state is claimed" in text

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

    for rel in [
        f"{PACKAGE}/instructions/ION_CUSTOM_GPT_MAIN_INSTRUCTIONS_8000.md",
        "ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md",
    ]:
        runtime_text = read(rel)
        assert "ARCHITECTURE_SIGNAL_CAPTURE_LAW" in runtime_text
        assert "durable candidate signals with route/version, continuity export, and tests" in runtime_text


def test_architecture_signal_schema_hardens_required_fields_and_non_claims():
    schema = load_json(f"{PACKAGE}/schemas/ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL.schema.json")
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
    ]:
        assert field in required

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
    assert schema["properties"]["route"]["properties"]["target_protocol"]["const"] == "ION_CUSTOM_GPT_ORDERED_CONTEXT_FANOUT_V4_4"
    assert schema["properties"]["route"]["properties"]["ordered_baton_required"]["const"] is True
    assert "ordered_context_fanout" in required
    assert schema["properties"]["ordered_context_fanout"]["properties"]["protocol_id"]["const"] == "ION_CUSTOM_GPT_ORDERED_CONTEXT_FANOUT_V4_4"
    assert schema["properties"]["ordered_context_fanout"]["properties"]["upstream_reopen_alert_required"]["const"] is True
    assert schema["properties"]["ordered_context_fanout"]["properties"]["fan_in_settlement_input_required"]["const"] is True


def test_template_routes_operator_remark_into_ordered_context_fanout():
    data = load_yaml(f"{PACKAGE}/templates/ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL_CAPTURE.template.yaml")
    schema = load_json(f"{PACKAGE}/schemas/ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL.schema.json")
    assert set(data).issubset(set(schema["properties"]))
    for field in schema["required"]:
        assert field in data

    assert data["raw_summary"] == "Agent B needs Agent A's findings before reading section B."
    assert "Agent B inherits Agent A before section B" in data["normalized_requirement"]
    assert data["product_version_target"] == "v4.4a_v4.4b"
    assert data["status"] == "candidate_unimplemented"
    assert data["continuity_export_required"] is True
    assert data["tests_required"] is True
    assert data["accepted_state_claim"] is False
    assert data["route"]["target_protocol"] == "ION_CUSTOM_GPT_ORDERED_CONTEXT_FANOUT_V4_4"
    assert data["route"]["ordered_baton_required"] is True

    fanout = data["ordered_context_fanout"]
    assert fanout["protocol_id"] == "ION_CUSTOM_GPT_ORDERED_CONTEXT_FANOUT_V4_4"
    assert fanout["section_order"][1]["agent"] == "Agent B"
    assert fanout["section_order"][1]["input_batons"] == ["Agent A dense baton"]
    assert fanout["section_order"][2]["input_batons"] == [
        "Agent A dense baton",
        "Agent B dense baton",
    ]
    assert fanout["upstream_reopen_alert_required"] is True
    assert fanout["fan_in_settlement_input_required"] is True


def test_continuity_package_and_indexes_export_architecture_signal():
    context = load_yaml(f"{PACKAGE}/context/ION_CUSTOM_GPT_SANDBOX_CARRIER_CONTEXT_PACKAGE.yaml")
    knowledge = load_yaml(f"{PACKAGE}/indexes/ION_CUSTOM_GPT_KNOWLEDGE_INDEX.yaml")
    routes = load_yaml(f"{PACKAGE}/indexes/ION_CUSTOM_GPT_ROUTE_INDEX.yaml")

    root_nodes = "\n".join(context["root_nodes"])
    assert "ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL_CAPTURE.md" in root_nodes
    assert "ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL.schema.json" in root_nodes
    assert "ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL_CAPTURE.template.yaml" in root_nodes
    assert context["architecture_signal_capture"]["continuity_export_required"] is True
    assert context["architecture_signal_capture"]["accepted_state_claim"] is False

    start_paths = "\n".join(item["path"] for item in knowledge["primary_start_files"])
    assert "ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL_CAPTURE.md" in start_paths
    assert "ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL.schema.json" in start_paths
    assert "ION_CUSTOM_GPT_ARCHITECTURE_SIGNAL_CAPTURE.template.yaml" in start_paths

    route = routes["route_families"]["architecture_signal_capture"]
    assert "STEWARD" in route["roles"]
    assert "SCRIBE" in route["roles"]
    assert route["target_protocol"] == "ION_CUSTOM_GPT_ORDERED_CONTEXT_FANOUT_V4_4"
    assert route["continuity_export_required"] is True


if __name__ == "__main__":
    test_instruction_preserves_architecture_signal_capture_law()
    test_architecture_signal_schema_hardens_required_fields_and_non_claims()
    test_template_routes_operator_remark_into_ordered_context_fanout()
    test_continuity_package_and_indexes_export_architecture_signal()
    print("architecture signal capture candidate regression: PASS")
