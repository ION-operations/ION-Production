"""ION Custom GPT Action release domain helper.

This module treats GPT Builder Action schemas as release artifacts, not normal
implementation snippets. It classifies schema surfaces, validates the canonical
OpenAPI contract, and writes a release bundle with rollback and auth handoff
material.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml

from .ion_workspace_paths import display_path, resolve_ion_path, resolve_repo_root

DOMAIN_ID = "CUSTOM_GPT_ACTION_RELEASE"
DEFAULT_SERVER_URL = "https://ion-actions.helixion.net"
DEFAULT_TOKEN_SOURCE = "/home/sev/.config/ion/action-gateway.env"
CANONICAL_SCHEMA_RELATIVE_PATH = Path("ION_GPT/03_ACTIONS/ion-actions.helixion.net/SCHEMA_TO_PASTE.yaml")
LEGACY_CANONICAL_SCHEMA_RELATIVE_PATH = Path("ION/09_integrations/custom_gpt_action_gateway/openapi.yaml")
SOURCE_CURRENT_SCHEMA_RELATIVE_PATH = Path("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_action_gateway/openapi.yaml")
DEFAULT_RELEASE_ROOT = Path("ION/05_context/current/action_release_recovery")
MAX_GPT_ACTION_OPERATIONS = 30

CORE_OPERATION_IDS = (
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
)

SUPABASE_OPERATION_IDS = (
    "ionSupabaseCockpitOverview",
    "ionSupabaseRecentEvents",
    "ionSupabaseLatestServiceHealth",
    "ionSupabaseCurrentCarrierMounts",
    "ionSupabaseRecordAutomationEvent",
    "ionSupabaseRecordServiceHealth",
    "ionSupabaseRecordCarrierMount",
)

BRANCH_LEADER_OPERATION_IDS = (
    "ionActionBranchList",
    "ionActionBranchDescribe",
    "ionActionBranchInvoke",
    "ionActionBranchReceipts",
)

FORBIDDEN_FRAGMENT_PATHS = (
    "ION/07_templates/actions/ION_SUPABASE_ACTIONS_OPENAPI_V0_1.yaml",
)

SECRET_TEXT_PATTERNS = (
    re.compile(r"SUPABASE_(?:SERVICE_ROLE_KEY|SECRET_KEY|DB_PASSWORD)\\s*[:=]", re.I),
    re.compile(r"ION_ACTION_GATEWAY_TOKEN\\s*[:=]\\s*[A-Za-z0-9_\\-]{12,}", re.I),
    re.compile(r"eyJ[A-Za-z0-9_\\-]{20,}\\.[A-Za-z0-9_\\-]{20,}\\.", re.I),
    re.compile(r"sb_secret_[A-Za-z0-9_\\-]{12,}", re.I),
    re.compile(r"service[_ -]?role[_ -]?key\\s*[:=]", re.I),
)

AUTH_INVALID_STOP_RULE = (
    "If a protected GPT Action returns AUTH_INVALID, gateway_token_invalid, "
    "or unexpected AUTH_MISSING, stop all protected Action calls immediately."
)


class ActionSchemaReleaseError(ValueError):
    """Raised when an Action release artifact fails validation."""


@dataclass(frozen=True)
class Operation:
    path: str
    method: str
    operation_id: str


def _resolve_repo_root(start: str | Path | None = None) -> Path:
    return resolve_repo_root(start)


def _load_yaml_text(text: str) -> dict[str, Any]:
    loaded = yaml.safe_load(text)
    if not isinstance(loaded, dict):
        raise ActionSchemaReleaseError("OpenAPI document must parse to an object")
    return loaded


def _read_schema(schema_path: Path) -> tuple[str, dict[str, Any]]:
    text = schema_path.read_text(encoding="utf-8")
    return text, _load_yaml_text(text)


def _schema_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def inspect_action_gateway_routes(openapi: Mapping[str, Any]) -> list[Operation]:
    """Return route/method/operationId triples from an OpenAPI document."""

    routes: list[Operation] = []
    paths = openapi.get("paths", {})
    if not isinstance(paths, Mapping):
        raise ActionSchemaReleaseError("OpenAPI paths must be an object")
    for path, path_item in paths.items():
        if not isinstance(path_item, Mapping):
            continue
        for method, operation in path_item.items():
            if not isinstance(operation, Mapping):
                continue
            operation_id = operation.get("operationId")
            if isinstance(operation_id, str):
                routes.append(Operation(path=str(path), method=str(method).lower(), operation_id=operation_id))
    return routes


def _operation_ids(openapi: Mapping[str, Any]) -> list[str]:
    return [route.operation_id for route in inspect_action_gateway_routes(openapi)]


def classify_schema_surface(
    *,
    openapi: Mapping[str, Any],
    source_path: str | Path | None = None,
) -> dict[str, Any]:
    """Classify whether a schema is canonical, a fragment, or unsafe."""

    operation_ids = _operation_ids(openapi)
    operation_set = set(operation_ids)
    core_set = set(CORE_OPERATION_IDS)
    supabase_set = set(SUPABASE_OPERATION_IDS)
    branch_set = set(BRANCH_LEADER_OPERATION_IDS)
    missing_core = sorted(core_set - operation_set)
    missing_supabase = sorted(supabase_set - operation_set)
    missing_branch_leader = sorted(branch_set - operation_set)
    duplicates = sorted({item for item in operation_ids if operation_ids.count(item) > 1})
    over_operation_limit = len(operation_ids) > MAX_GPT_ACTION_OPERATIONS
    source = str(source_path or "")
    forbidden_path = source.replace("\\", "/") in FORBIDDEN_FRAGMENT_PATHS

    if not missing_core and not missing_supabase and not missing_branch_leader and not duplicates and not over_operation_limit:
        classification = "canonical_full_schema"
        install_target = True
    elif operation_set and operation_set.issubset(supabase_set) and not operation_set.intersection(core_set):
        classification = "fragment_template_not_install_target"
        install_target = False
    elif over_operation_limit:
        classification = "schema_operation_limit_exceeded"
        install_target = False
    else:
        classification = "incomplete_or_unknown_schema"
        install_target = False

    if forbidden_path:
        classification = "forbidden_fragment_path"
        install_target = False

    return {
        "classification": classification,
        "install_target": install_target,
        "operation_count": len(operation_ids),
        "max_gpt_action_operations": MAX_GPT_ACTION_OPERATIONS,
        "operation_limit_exceeded": over_operation_limit,
        "operation_ids": operation_ids,
        "missing_core_operations": missing_core,
        "missing_supabase_operations": missing_supabase,
        "missing_branch_leader_operations": missing_branch_leader,
        "branch_leader_operations_present": sorted(branch_set & operation_set),
        "duplicate_operation_ids": duplicates,
        "source_path": source,
    }


def validate_operation_manifest(openapi: Mapping[str, Any]) -> dict[str, Any]:
    operation_ids = _operation_ids(openapi)
    duplicates = sorted({item for item in operation_ids if operation_ids.count(item) > 1})
    missing_core = sorted(set(CORE_OPERATION_IDS) - set(operation_ids))
    missing_supabase = sorted(set(SUPABASE_OPERATION_IDS) - set(operation_ids))
    branch_present = sorted(set(BRANCH_LEADER_OPERATION_IDS) & set(operation_ids))
    missing_branch = sorted(set(BRANCH_LEADER_OPERATION_IDS) - set(operation_ids))
    over_operation_limit = len(operation_ids) > MAX_GPT_ACTION_OPERATIONS
    servers = openapi.get("servers", [])
    server_url = None
    if isinstance(servers, list) and servers and isinstance(servers[0], Mapping):
        server_url = servers[0].get("url")

    errors: list[str] = []
    if duplicates:
        errors.append("duplicate_operation_ids")
    if missing_core:
        errors.append("missing_core_operations")
    if missing_supabase:
        errors.append("missing_supabase_operations")
    if missing_branch:
        errors.append("missing_branch_leader_operations")
    if over_operation_limit:
        errors.append("operation_limit_exceeded")
    if server_url != DEFAULT_SERVER_URL:
        errors.append("server_url_mismatch")

    if errors:
        raise ActionSchemaReleaseError(
            json.dumps(
                {
                    "errors": errors,
                    "duplicate_operation_ids": duplicates,
                    "missing_core_operations": missing_core,
                    "missing_supabase_operations": missing_supabase,
                    "missing_branch_leader_operations": missing_branch,
                    "operation_count": len(operation_ids),
                    "max_gpt_action_operations": MAX_GPT_ACTION_OPERATIONS,
                    "server_url": server_url,
                },
                sort_keys=True,
            )
        )

    return {
        "operation_count": len(operation_ids),
        "max_gpt_action_operations": MAX_GPT_ACTION_OPERATIONS,
        "operation_limit_exceeded": False,
        "operation_ids": operation_ids,
        "core_operations": list(CORE_OPERATION_IDS),
        "supabase_operations": list(SUPABASE_OPERATION_IDS),
        "branch_leader_operations": list(BRANCH_LEADER_OPERATION_IDS),
        "branch_leader_operations_present": branch_present,
        "missing_branch_leader_operations": missing_branch,
        "duplicate_operation_ids": [],
        "server_url": server_url,
    }


def validate_no_secret_strings(text: str) -> list[str]:
    findings = [pattern.pattern for pattern in SECRET_TEXT_PATTERNS if pattern.search(text)]
    if findings:
        raise ActionSchemaReleaseError(f"secret_like_text_detected: {findings}")
    return findings


def validate_fragment_not_install_target(classification: Mapping[str, Any]) -> None:
    if classification.get("classification") != "canonical_full_schema" and classification.get("install_target"):
        raise ActionSchemaReleaseError("non-canonical schema cannot be install target")
    if classification.get("classification") in {"fragment_template_not_install_target", "forbidden_fragment_path"}:
        if classification.get("install_target"):
            raise ActionSchemaReleaseError("fragment classified as install target")


def build_canonical_openapi(
    *,
    repo_root: str | Path | None = None,
    schema_path: str | Path | None = None,
) -> dict[str, Any]:
    """Load and validate the canonical full OpenAPI schema."""

    root = _resolve_repo_root(repo_root)
    requested_path = Path(schema_path) if schema_path else CANONICAL_SCHEMA_RELATIVE_PATH
    path = resolve_ion_path(root, requested_path)
    if not path.exists() and schema_path is None:
        path = resolve_ion_path(root, LEGACY_CANONICAL_SCHEMA_RELATIVE_PATH)
    if not path.exists() and schema_path is None:
        path = resolve_ion_path(root, SOURCE_CURRENT_SCHEMA_RELATIVE_PATH)
    text, openapi = _read_schema(path)
    classification = classify_schema_surface(openapi=openapi, source_path=display_path(path, root))
    if classification["classification"] != "canonical_full_schema":
        raise ActionSchemaReleaseError(f"canonical schema classification failed: {classification}")
    manifest = validate_operation_manifest(openapi)
    validate_no_secret_strings(text)
    return {
        "path": path,
        "text": text,
        "openapi": openapi,
        "sha256": _schema_sha256(text),
        "classification": classification,
        "manifest": manifest,
    }


def _markdown_list(values: list[str] | tuple[str, ...]) -> str:
    return "\n".join(f"- `{value}`" for value in values)


def build_release_report(canonical: Mapping[str, Any]) -> str:
    manifest = canonical["manifest"]
    return f"""# Action Schema Release Report

Domain: `{DOMAIN_ID}`
Status: candidate release report.

## Canonical schema

```text
{CANONICAL_SCHEMA_RELATIVE_PATH.as_posix()}
```

Schema SHA256:

```text
{canonical["sha256"]}
```

Operation count:

```text
{manifest["operation_count"]}
```

GPT Builder operation budget:

```text
max_operations: {manifest["max_gpt_action_operations"]}
within_limit: {not manifest["operation_limit_exceeded"]}
```

Server:

```text
{manifest["server_url"]}
```

Token source:

```text
{DEFAULT_TOKEN_SOURCE}
```

## Core operations preserved

{_markdown_list(list(CORE_OPERATION_IDS))}

## Supabase operations included

{_markdown_list(list(SUPABASE_OPERATION_IDS))}

## Required companion sheets

- `GPT_BUILDER_INSTALL_SHEET.md`
- `GPT_BUILDER_ROLLBACK_SHEET.md`
- `AUTH_TOKEN_HANDOFF_CHECKLIST.md`
- `POST_INSTALL_SMOKE_PLAN.md`

## Stop rule

{AUTH_INVALID_STOP_RULE}
"""


def build_builder_install_sheet(canonical: Mapping[str, Any]) -> str:
    return f"""# GPT Builder Install Sheet

Status: candidate release sheet. Use only after release review approval.

## Install only this schema

```text
{CANONICAL_SCHEMA_RELATIVE_PATH.as_posix()}
```

Do not install fragments or Supabase-only schemas.

## Proof values

```text
operation_count: {canonical["manifest"]["operation_count"]}
max_operations: {canonical["manifest"]["max_gpt_action_operations"]}
schema_sha256: {canonical["sha256"]}
server: {DEFAULT_SERVER_URL}
```

## Auth source

Use the ION Action Gateway bearer token from:

```text
{DEFAULT_TOKEN_SOURCE}
```

Never use a Supabase key in GPT Builder.

## Fresh session rule

After saving GPT Builder changes, start a fresh GPT session. Existing sessions
may keep stale Action definitions.

## Stop rule

{AUTH_INVALID_STOP_RULE}
"""


def build_rollback_sheet(canonical: Mapping[str, Any]) -> str:
    return f"""# GPT Builder Rollback Sheet

Status: candidate rollback sheet.

## Freeze triggers

- GPT Builder rejects the canonical schema.
- Old/core operations are missing after install.
- Any Supabase-only schema appears as the install surface.
- A protected Action returns `AUTH_INVALID`, `gateway_token_invalid`, or unexpected `AUTH_MISSING`.

## Rollback target

Freeze Actions and return to the last verified full schema release. The current
candidate full schema is:

```text
{CANONICAL_SCHEMA_RELATIVE_PATH.as_posix()}
```

SHA256:

```text
{canonical["sha256"]}
```
"""


def build_auth_token_handoff_checklist() -> str:
    return f"""# Auth Token Handoff Checklist

Status: candidate checklist.

## Token source

```text
{DEFAULT_TOKEN_SOURCE}
```

Expected variable:

```text
ION_ACTION_GATEWAY_TOKEN
```

Do not print the token in chat, logs, reports, or committed files.

## Forbidden credentials

Do not put Supabase URL, Supabase service/secret keys, database passwords, JWT
secrets, or Cloudflare tokens in GPT Builder.

## Stop rule

{AUTH_INVALID_STOP_RULE}
"""


def build_post_install_smoke_plan() -> str:
    return f"""# Post-Install Smoke Plan

Status: candidate smoke plan.

Run only after the release bundle passes and GPT Builder has been saved.

1. Start a fresh GPT session.
2. Run `ionGatewayHealth`.
3. Run one protected read route only.
4. If the read route succeeds, run `ionSupabaseCockpitOverview`.
5. Do not run writes until read-only checks pass.

Stop immediately on `AUTH_INVALID`, `gateway_token_invalid`, or unexpected
`AUTH_MISSING`.
"""


def build_route_source_inventory(canonical: Mapping[str, Any]) -> str:
    routes = inspect_action_gateway_routes(canonical["openapi"])
    lines = "\n".join(f"- `{route.method.upper()} {route.path}` -> `{route.operation_id}`" for route in routes)
    return f"""# Route Source Inventory

Status: generated from canonical OpenAPI.

## Routes

{lines}
"""


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def package_release(
    *,
    repo_root: str | Path | None = None,
    packet_id: str = "PCKT-ION-GPT001-ACTION-SCHEMA-RECOVERY-001",
) -> dict[str, Any]:
    root = _resolve_repo_root(repo_root)
    canonical = build_canonical_openapi(repo_root=root)
    package_dir = root / DEFAULT_RELEASE_ROOT / packet_id
    package_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "packet_id": packet_id,
        "domain_id": DOMAIN_ID,
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "canonical_schema_path": CANONICAL_SCHEMA_RELATIVE_PATH.as_posix(),
        "schema_sha256": canonical["sha256"],
        "operation_count": canonical["manifest"]["operation_count"],
        "max_gpt_action_operations": canonical["manifest"]["max_gpt_action_operations"],
        "operation_limit_exceeded": canonical["manifest"]["operation_limit_exceeded"],
        "operation_ids": canonical["manifest"]["operation_ids"],
        "core_operations": list(CORE_OPERATION_IDS),
        "supabase_operations": list(SUPABASE_OPERATION_IDS),
        "duplicate_operation_ids": [],
        "server_url": DEFAULT_SERVER_URL,
        "token_source": DEFAULT_TOKEN_SOURCE,
        "auth_invalid_stop_rule": AUTH_INVALID_STOP_RULE,
        "accepted_state_authority": False,
        "settlement_required": True,
    }

    _write_text(package_dir / "COMBINED_OPENAPI_SCHEMA.yaml", canonical["text"])
    _write_text(package_dir / "ACTION_SCHEMA_RELEASE_REPORT.md", build_release_report(canonical))
    _write_text(package_dir / "ROUTE_SOURCE_INVENTORY.md", build_route_source_inventory(canonical))
    _write_text(package_dir / "GPT_BUILDER_INSTALL_SHEET.md", build_builder_install_sheet(canonical))
    _write_text(package_dir / "GPT_BUILDER_ROLLBACK_SHEET.md", build_rollback_sheet(canonical))
    _write_text(package_dir / "AUTH_TOKEN_HANDOFF_CHECKLIST.md", build_auth_token_handoff_checklist())
    _write_text(package_dir / "POST_INSTALL_SMOKE_PLAN.md", build_post_install_smoke_plan())
    _write_text(package_dir / "OPERATION_ID_MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True))

    return {"ok": True, "package_dir": str(package_dir), **manifest}


def _cmd_inspect(args: argparse.Namespace) -> dict[str, Any]:
    canonical = build_canonical_openapi(repo_root=args.ion_root)
    return {
        "ok": True,
        "classification": canonical["classification"],
        "manifest": canonical["manifest"],
        "sha256": canonical["sha256"],
    }


def _cmd_build(args: argparse.Namespace) -> dict[str, Any]:
    canonical = build_canonical_openapi(repo_root=args.ion_root)
    return {
        "ok": True,
        "canonical_schema_path": str(canonical["path"]),
        "sha256": canonical["sha256"],
        "operation_count": canonical["manifest"]["operation_count"],
        "max_gpt_action_operations": canonical["manifest"]["max_gpt_action_operations"],
        "operation_limit_exceeded": canonical["manifest"]["operation_limit_exceeded"],
    }


def _cmd_validate(args: argparse.Namespace) -> dict[str, Any]:
    canonical = build_canonical_openapi(repo_root=args.ion_root)
    validate_fragment_not_install_target(canonical["classification"])
    return {
        "ok": True,
        "schema_sha256": canonical["sha256"],
        "operation_count": canonical["manifest"]["operation_count"],
        "max_gpt_action_operations": canonical["manifest"]["max_gpt_action_operations"],
        "operation_limit_exceeded": canonical["manifest"]["operation_limit_exceeded"],
        "auth_invalid_stop_rule": AUTH_INVALID_STOP_RULE,
    }


def _cmd_package(args: argparse.Namespace) -> dict[str, Any]:
    return package_release(repo_root=args.ion_root, packet_id=args.packet_id)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ION Custom GPT Action release helper")
    parser.add_argument("command", choices=("inspect", "build", "validate", "package"))
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--packet-id", default="PCKT-ION-GPT001-ACTION-SCHEMA-RECOVERY-001")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    handlers = {
        "inspect": _cmd_inspect,
        "build": _cmd_build,
        "validate": _cmd_validate,
        "package": _cmd_package,
    }
    result = handlers[args.command](args)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
