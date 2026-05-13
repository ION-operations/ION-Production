from pathlib import Path

import yaml

from kernel.ion_custom_gpt_action_gateway import (
    OPENAPI_RELATIVE_PATH,
    POLICY_RELATIVE_PATH,
    REFUSAL_CLASSES,
)


def test_action_gateway_policy_file_declares_draft_non_production():
    text = Path(POLICY_RELATIVE_PATH).read_text(encoding="utf-8")

    assert "schema_id: ion.custom_gpt_action_gateway_policy.v1" in text
    assert "status: draft_non_production" in text
    assert "production_authority: false" in text
    assert "live_execution_authority: false" in text
    assert "listen_port: 8777" in text
    assert "  - /openapi.yaml" in text


def test_action_gateway_policy_names_supported_and_hard_gated_intents():
    text = Path(POLICY_RELATIVE_PATH).read_text(encoding="utf-8")

    for intent in [
        "register_artifact",
        "write_file_draft",
        "create_codex_work_packet",
        "create_github_issue_draft",
    ]:
        assert f"  - {intent}" in text
    for intent in [
        "delete_file",
        "overwrite_protected_file",
        "push_main",
        "access_credential",
        "production_deploy",
        "broad_shell",
    ]:
        assert f"  - {intent}" in text


def test_action_gateway_policy_names_required_refusal_classes():
    text = Path(POLICY_RELATIVE_PATH).read_text(encoding="utf-8")

    for refusal_class in REFUSAL_CLASSES:
        assert f"  - {refusal_class}" in text


def test_action_gateway_openapi_exposes_only_mvp_paths():
    text = Path(OPENAPI_RELATIVE_PATH).read_text(encoding="utf-8")

    for path in [
        "/health:",
        "/policy:",
        "/context-pack:",
        "/codex/queue:",
        "/agent/status:",
        "/projects/daimon/visibility:",
        "/receipts/recent:",
        "/actions/validate:",
        "/actions/submit:",
        "/supabase/cockpit/overview:",
        "/supabase/events/recent:",
        "/supabase/service-health/latest:",
        "/supabase/carrier-mounts/current:",
        "/supabase/events/record:",
        "/supabase/service-health/record:",
        "/supabase/carrier-mounts/record:",
    ]:
        assert path in text
    for forbidden_path_fragment in [
        "/shell",
        "/files/delete",
        "/git/push",
        "/deploy",
        "/credentials",
    ]:
        assert forbidden_path_fragment not in text


def test_action_gateway_openapi_has_explicit_object_properties_for_gpt_actions():
    doc = yaml.safe_load(Path(OPENAPI_RELATIVE_PATH).read_text(encoding="utf-8"))
    schemas = doc.get("components", {}).get("schemas", {})

    def assert_schema(schema, location):
        if not isinstance(schema, dict):
            return
        if schema.get("type") == "object":
            assert "properties" in schema, f"object schema missing properties at {location}"
        for key, value in schema.items():
            if key == "$ref":
                continue
            if isinstance(value, dict):
                assert_schema(value, f"{location}.{key}")
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    assert_schema(item, f"{location}.{key}[{index}]")

    for schema_name, schema in schemas.items():
        assert_schema(schema, f"components.schemas.{schema_name}")

    for path_name, path_item in doc["paths"].items():
        for method_name, operation in path_item.items():
            for status_code, response in operation.get("responses", {}).items():
                media = response.get("content", {}).get("application/json", {})
                schema = media.get("schema", {})
        assert schema.get("$ref"), f"response schema should use explicit component ref at {path_name} {method_name} {status_code}"


def test_action_gateway_openapi_preserves_old_ops_and_adds_supabase_ops_without_secrets():
    text = Path(OPENAPI_RELATIVE_PATH).read_text(encoding="utf-8")
    openapi = yaml.safe_load(text)
    operation_ids = [
        operation.get("operationId")
        for path_item in openapi.get("paths", {}).values()
        for operation in path_item.values()
        if isinstance(operation, dict)
    ]

    old_required = {
        "ionGatewayHealth",
        "ionGatewayPolicy",
        "ionGatewayContextPack",
        "ionGatewayCodexQueue",
        "ionGatewayAgentStatus",
        "ionGatewayDaimonVisibility",
        "ionGatewayReceiptsRecent",
        "ionBrowserQueueStatus",
        "ionBrowserQueueReceiptsRecent",
        "ionBrowserQueueEnqueue",
        "ionGatewayValidateAction",
        "ionGatewaySubmitAction",
        "ionGatewayAgentInvoke",
        "ionGatewayAgentRelayPending",
        "ionGatewayAgentRelayRespond",
        "ionGatewayAgentControl",
        "ionGatewayAgentReceiptsRecent",
        "ionGatewayAgentSettle",
    }
    supabase_required = {
        "ionSupabaseCockpitOverview",
        "ionSupabaseRecentEvents",
        "ionSupabaseLatestServiceHealth",
        "ionSupabaseCurrentCarrierMounts",
        "ionSupabaseRecordAutomationEvent",
        "ionSupabaseRecordServiceHealth",
        "ionSupabaseRecordCarrierMount",
    }

    assert old_required.issubset(set(operation_ids))
    assert supabase_required.issubset(set(operation_ids))
    assert len(operation_ids) == len(set(operation_ids))
    assert openapi["servers"][0]["url"] == "https://ion-actions.helixion.net"
    lowered = text.lower()
    assert "supabase_secret_key" not in lowered
    assert "supabase_service_role_key" not in lowered
    assert "service_role_key" not in lowered


def test_policy_and_openapi_include_bounded_agent_surfaces():
    policy = yaml.safe_load(Path(POLICY_RELATIVE_PATH).read_text(encoding="utf-8"))
    openapi = yaml.safe_load(Path(OPENAPI_RELATIVE_PATH).read_text(encoding="utf-8"))

    for path in ["/agent/relay/pending", "/agent/receipts/recent"]:
        assert path in policy.get("allowed_get_paths", [])
        assert path in openapi.get("paths", {})
    for path in ["/agent/invoke", "/agent/relay/respond", "/agent/control", "/agent/settle"]:
        assert path in policy.get("allowed_post_paths", [])
        assert path in openapi.get("paths", {})
