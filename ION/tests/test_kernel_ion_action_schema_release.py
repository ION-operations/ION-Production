from pathlib import Path

import pytest
import yaml

from kernel.ion_action_schema_release import (
    AUTH_INVALID_STOP_RULE,
    BRANCH_LEADER_OPERATION_IDS,
    CANONICAL_SCHEMA_RELATIVE_PATH,
    CORE_OPERATION_IDS,
    DEFAULT_SERVER_URL,
    MAX_GPT_ACTION_OPERATIONS,
    SUPABASE_OPERATION_IDS,
    ActionSchemaReleaseError,
    build_builder_install_sheet,
    build_canonical_openapi,
    build_release_report,
    build_rollback_sheet,
    classify_schema_surface,
    validate_no_secret_strings,
    validate_operation_manifest,
)
from kernel.ion_workspace_paths import resolve_repo_root


def _supabase_fragment_doc():
    return {
        "openapi": "3.1.0",
        "servers": [{"url": DEFAULT_SERVER_URL}],
        "paths": {
            f"/fragment/{operation_id}": {"get": {"operationId": operation_id}}
            for operation_id in SUPABASE_OPERATION_IDS
        },
    }


def test_action_schema_preserves_core_operations():
    canonical = build_canonical_openapi()
    operation_ids = set(canonical["manifest"]["operation_ids"])

    assert set(CORE_OPERATION_IDS).issubset(operation_ids)


def test_action_schema_adds_supabase_operations():
    canonical = build_canonical_openapi()
    operation_ids = set(canonical["manifest"]["operation_ids"])

    assert set(SUPABASE_OPERATION_IDS).issubset(operation_ids)


def test_action_schema_manifest_requires_branch_leader_group():
    branch_doc = {
        "openapi": "3.1.0",
        "servers": [{"url": DEFAULT_SERVER_URL}],
        "paths": {
            f"/branches/{operation_id}": {"post": {"operationId": operation_id}}
            for operation_id in BRANCH_LEADER_OPERATION_IDS
        }
        | {
            f"/core/{operation_id}": {"get": {"operationId": operation_id}}
            for operation_id in CORE_OPERATION_IDS
        }
        | {
            f"/supabase/{operation_id}": {"get": {"operationId": operation_id}}
            for operation_id in SUPABASE_OPERATION_IDS
        },
    }

    manifest = validate_operation_manifest(branch_doc)

    assert set(BRANCH_LEADER_OPERATION_IDS).issubset(set(manifest["branch_leader_operations_present"]))
    assert manifest["missing_branch_leader_operations"] == []


def test_action_schema_enforces_openai_gpt_builder_operation_limit():
    canonical = build_canonical_openapi()

    assert canonical["manifest"]["operation_count"] <= MAX_GPT_ACTION_OPERATIONS
    assert canonical["manifest"]["operation_limit_exceeded"] is False
    assert canonical["classification"]["install_target"] is True

    over_limit_doc = {
        "openapi": "3.1.0",
        "servers": [{"url": DEFAULT_SERVER_URL}],
        "paths": {
            **{
                f"/core/{operation_id}": {"get": {"operationId": operation_id}}
                for operation_id in CORE_OPERATION_IDS
            },
            **{
                f"/supabase/{operation_id}": {"get": {"operationId": operation_id}}
                for operation_id in SUPABASE_OPERATION_IDS
            },
            **{
                f"/branches/{operation_id}": {"post": {"operationId": operation_id}}
                for operation_id in BRANCH_LEADER_OPERATION_IDS
            },
            "/extra/one": {"get": {"operationId": "ionExtraOne"}},
            "/extra/two": {"get": {"operationId": "ionExtraTwo"}},
        },
    }
    classification = classify_schema_surface(openapi=over_limit_doc, source_path="over-limit.yaml")

    assert classification["classification"] == "schema_operation_limit_exceeded"
    assert classification["install_target"] is False
    assert classification["operation_count"] == MAX_GPT_ACTION_OPERATIONS + 1
    with pytest.raises(ActionSchemaReleaseError, match="operation_limit_exceeded"):
        validate_operation_manifest(over_limit_doc)


def test_action_schema_rejects_missing_branch_leader_operations():
    branchless_doc = {
        "openapi": "3.1.0",
        "servers": [{"url": DEFAULT_SERVER_URL}],
        "paths": {
            f"/core/{operation_id}": {"get": {"operationId": operation_id}}
            for operation_id in CORE_OPERATION_IDS
        }
        | {
            f"/supabase/{operation_id}": {"get": {"operationId": operation_id}}
            for operation_id in SUPABASE_OPERATION_IDS
        },
    }

    classification = classify_schema_surface(openapi=branchless_doc, source_path="branchless.yaml")
    assert classification["classification"] == "incomplete_or_unknown_schema"
    assert classification["install_target"] is False
    with pytest.raises(ActionSchemaReleaseError):
        validate_operation_manifest(branchless_doc)


def test_action_schema_rejects_fragment_install_target():
    classification = classify_schema_surface(
        openapi=_supabase_fragment_doc(),
        source_path="ION/07_templates/actions/ION_SUPABASE_ACTIONS_OPENAPI_V0_1.yaml",
    )

    assert classification["classification"] == "forbidden_fragment_path"
    assert classification["install_target"] is False


def test_action_schema_no_duplicate_operation_ids():
    duplicate_doc = {
        "openapi": "3.1.0",
        "servers": [{"url": DEFAULT_SERVER_URL}],
        "paths": {
            "/a": {"get": {"operationId": "ionGatewayHealth"}},
            "/b": {"get": {"operationId": "ionGatewayHealth"}},
        },
    }

    with pytest.raises(ActionSchemaReleaseError):
        validate_operation_manifest(duplicate_doc)


def test_action_schema_no_secret_strings():
    validate_no_secret_strings("description: uses ION Action Gateway bearer auth")

    with pytest.raises(ActionSchemaReleaseError):
        validate_no_secret_strings("SUPABASE_SECRET_KEY=sb_secret_example_value")


def test_action_schema_server_correct():
    canonical = build_canonical_openapi()

    assert canonical["manifest"]["server_url"] == DEFAULT_SERVER_URL


def test_action_release_report_includes_operation_count_schema_hash_token_source_and_rollback():
    canonical = build_canonical_openapi()
    report = build_release_report(canonical)

    assert "Operation count" in report
    assert str(canonical["manifest"]["operation_count"]) in report
    assert f"max_operations: {MAX_GPT_ACTION_OPERATIONS}" in report
    assert canonical["sha256"] in report
    assert "/home/sev/.config/ion/action-gateway.env" in report
    assert "GPT_BUILDER_ROLLBACK_SHEET.md" in report


def test_install_sheet_requires_fresh_gpt_session():
    canonical = build_canonical_openapi()
    install_sheet = build_builder_install_sheet(canonical)

    assert "fresh GPT session" in install_sheet
    assert str(CANONICAL_SCHEMA_RELATIVE_PATH) in install_sheet


def test_auth_invalid_circuit_breaker_documented():
    canonical = build_canonical_openapi()
    install_sheet = build_builder_install_sheet(canonical)
    rollback_sheet = build_rollback_sheet(canonical)

    assert AUTH_INVALID_STOP_RULE in install_sheet
    assert "AUTH_INVALID" in rollback_sheet


def test_action_release_registry_yaml_parses():
    registry = resolve_repo_root(Path.cwd()) / "ION/03_registry/ion_custom_gpt_action_release_registry.yaml"
    parsed = yaml.safe_load(registry.read_text(encoding="utf-8"))

    assert parsed["domain_id"] == "CUSTOM_GPT_ACTION_RELEASE"
    assert parsed["canonical_schema_path"] == str(CANONICAL_SCHEMA_RELATIVE_PATH)
