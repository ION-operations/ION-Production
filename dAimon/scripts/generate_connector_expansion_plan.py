#!/usr/bin/env python3
"""Validate and summarize dAimon connector expansion readiness.

This script does not call partner APIs and does not read secret values. It
turns the connector registry into a small evidence artifact for the dashboard
and Custom GPT visibility surfaces.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "orchestration" / "connector_expansion_registry.json"
OUTPUT_PATH = ROOT / "sample_outputs" / "connector_expansion_plan.json"

REQUIRED_CONNECTORS = {
    "custom_gpt_actions",
    "gitlab",
    "arize_phoenix",
    "elastic",
    "fivetran",
}
REQUIRED_FIELDS = {
    "connector_id",
    "name",
    "category",
    "status",
    "priority",
    "connection_surface",
    "required_env",
    "secret_handling",
    "read_capabilities",
    "write_capabilities",
    "authority_boundary",
    "proof_gates",
    "current_evidence",
    "next_gate",
    "non_claims",
}


class ConnectorRegistryError(Exception):
    """Raised when the connector registry is incomplete."""


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def require_non_empty(connector: Mapping[str, Any], field: str) -> None:
    if field not in connector:
        raise ConnectorRegistryError(f"{connector.get('connector_id', '<unknown>')} missing {field}")
    if connector[field] in ("", None, [], {}):
        raise ConnectorRegistryError(f"{connector.get('connector_id', '<unknown>')} has empty {field}")


def validate_registry(registry: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    connectors = registry.get("connector_targets")
    if not isinstance(connectors, list):
        raise ConnectorRegistryError("connector_targets must be a list")
    connector_ids = {connector.get("connector_id") for connector in connectors if isinstance(connector, Mapping)}
    missing = REQUIRED_CONNECTORS - connector_ids
    if missing:
        raise ConnectorRegistryError(f"missing connector targets: {sorted(missing)}")
    for connector in connectors:
        if not isinstance(connector, Mapping):
            raise ConnectorRegistryError("connector target must be an object")
        for field in REQUIRED_FIELDS:
            require_non_empty(connector, field)
    return connectors


def summarize_connector(connector: Mapping[str, Any]) -> dict[str, Any]:
    evidence = []
    for path in connector.get("current_evidence", []):
        if not isinstance(path, str):
            continue
        evidence.append({
            "path": path,
            "exists": (ROOT / path).exists() if not path.startswith("ION/") else None,
        })
    return {
        "connector_id": connector.get("connector_id"),
        "name": connector.get("name"),
        "status": connector.get("status"),
        "priority": connector.get("priority"),
        "required_env_names": connector.get("required_env", []),
        "proof_gate_count": len(connector.get("proof_gates", [])),
        "next_gate": connector.get("next_gate"),
        "evidence": evidence,
        "live_integration_claimed": str(connector.get("status")) in {
        "primary_live_proof_substrate",
        "local_gateway_live_schema_ready",
        "custom_gpt_visibility_action_proven_read_only",
    },
    }


def main() -> int:
    try:
        registry = load_registry()
        connectors = validate_registry(registry)
        result = {
            "schema": "daimon.connector_expansion_plan.v0_1",
            "ok": True,
            "connector_count": len(connectors),
            "connector_ids": [connector["connector_id"] for connector in connectors],
            "connectors": [summarize_connector(connector) for connector in connectors],
            "next_priority_connector": sorted(connectors, key=lambda item: int(item["priority"]))[0]["connector_id"],
            "state_boundary": registry.get("state_boundary"),
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
        }
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0
    except (ConnectorRegistryError, json.JSONDecodeError, OSError) as exc:
        result = {
            "schema": "daimon.connector_expansion_plan.v0_1",
            "ok": False,
            "error": str(exc),
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
        }
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
