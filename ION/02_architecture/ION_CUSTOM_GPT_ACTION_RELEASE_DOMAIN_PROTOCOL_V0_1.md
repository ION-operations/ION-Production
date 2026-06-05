# ION Custom GPT Action Release Domain Protocol V0.1

Status: candidate protocol.
Domain ID: `CUSTOM_GPT_ACTION_RELEASE`.
Risk class: high-trust operator control surface.

## Purpose

Custom GPT Actions are not ordinary implementation files. They are a human-admin
control surface that determines what a GPT can call, which gateway it can reach,
which auth boundary it uses, and what operator-visible capabilities appear in
GPT Builder.

This domain governs every GPT Builder Action schema, auth, release, rollback,
and post-install smoke workflow.

## Incident class addressed

This protocol exists because a Supabase-only OpenAPI fragment was handed to the
operator as if it were the full GPT Builder Action schema. That replaced or
obscured the prior working Action surface and damaged operator trust.

The failure class is:

```text
candidate fragment/template
treated as
operator-installable control surface
```

## Domain model

```yaml
DOMAIN_ID: CUSTOM_GPT_ACTION_RELEASE
DOMAIN_TYPE: human_admin_control_surface
OWNER_ROLE: action_release_steward
PRIMARY_CARRIER: codex_cli
HUMAN_SURFACE: GPT Builder
RISK_CLASS: high_trust_operator_surface
DEFAULT_AUTHORITY: candidate_release_only
ACCEPTED_STATE_AUTHORITY: false
SETTLEMENT_REQUIRED: true
```

## Controlled surfaces

- OpenAPI schema generation.
- `operationId` manifest.
- Schema fragment versus canonical schema classification.
- Action Gateway auth token source.
- GPT Builder install sheet.
- GPT Builder rollback sheet.
- Fresh-session requirement.
- `AUTH_INVALID` containment.
- Post-install smoke order.
- Operator handoff.

## Required agents / phases

### action_schema_cartographer

Inspects live route sources, canonical OpenAPI, fragments/templates, and existing
operationIds.

Outputs:

```text
ROUTE_SOURCE_INVENTORY.md
OPERATION_ID_MANIFEST.json
```

### action_schema_builder

Builds or refreshes the full canonical OpenAPI schema. It must not produce a
fragment as an install target.

Output:

```text
../ION_GPT/03_ACTIONS/ion-actions.helixion.net/SCHEMA_TO_PASTE.yaml
../ION_GPT/03_ACTIONS/ion.helixion.net_mcp/SCHEMA_TO_PASTE.yaml
```

### action_release_nemesis

Attempts to disprove the release by checking preservation, duplicate IDs,
server URL, auth scheme, and secret text.

### action_auth_custodian

Verifies token-source posture without printing the token.

### operator_release_scribe

Creates human release sheets only after validation passes.

## Required release bundle

GPT Builder must not be touched unless a release bundle exists with:

- `ACTION_SCHEMA_RELEASE_REPORT.md`
- `COMBINED_OPENAPI_SCHEMA.yaml`
- `OPERATION_ID_MANIFEST.json`
- `ROUTE_SOURCE_INVENTORY.md`
- `GPT_BUILDER_INSTALL_SHEET.md`
- `GPT_BUILDER_ROLLBACK_SHEET.md`
- `AUTH_TOKEN_HANDOFF_CHECKLIST.md`
- `POST_INSTALL_SMOKE_PLAN.md`

## Canonical install target

The installable GPT Builder schema sources are the current Action Gateway schemas:

```text
../ION_GPT/03_ACTIONS/ion-actions.helixion.net/SCHEMA_TO_PASTE.yaml
../ION_GPT/03_ACTIONS/ion.helixion.net_mcp/SCHEMA_TO_PASTE.yaml
```

Fragments and templates are never GPT Builder install targets.

## Stop rule

If a protected GPT Action returns `AUTH_INVALID`, `gateway_token_invalid`, or an
unexpected `AUTH_MISSING`, stop all protected Action calls immediately.

Do not try another protected route.
Do not attempt write actions.
Do not run smoke tests.
Report that GPT Builder Action auth is wrong or stale.

## Non-claims

This domain does not grant production authority, deployment authority, accepted
state authority, Supabase secret exposure, or unrestricted Action use.
