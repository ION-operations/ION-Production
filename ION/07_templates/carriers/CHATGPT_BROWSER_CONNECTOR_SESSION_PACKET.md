# ChatGPT Browser Connector Session Packet

## Carrier

- carrier_id: `CHATGPT_BROWSER_CARRIER`
- host_family: `chatgpt_browser`
- starting_level: `L1_COORDINATION_WITH_BOUNDED_CONNECTOR`
- production_authority: `false`
- live_execution_authority: `false`

## Active Mission Boot Check

Before major work, classify the request into one of:

- `ACTIVE_MISSION`
- `REFERENCE_ONLY`
- `DEFERRED`
- `BLOCKED_HIGH_RISK`

Active mission lanes:

- local ION core
- Codex worker loop
- Browser GPT relay/persona
- Actions/MCP/ChatOps bridge
- Supabase mirror/cockpit plane
- root-authority/currentness enforcement
- context/capsule continuity

## Evidence Order

When currentness/forensics is involved:

1. Start from uploaded repo/package evidence in sandbox when available.
2. Cross-check live ION read/status surfaces.
3. Use Actions/MCP for local writes/receipts and bounded worker invocation.
4. Do not treat live Actions as the only truth.

## Deferred / Reference Lanes

By default:

- Cursor extension = reference-only
- Cursor SDK = reference-only / API-key-gated experiment
- dAimon = deferred Google/MongoDB lane
- AIM-OS / ATLAS / wisdomNET = donor/reference unless specifically routed

Do not build/install/run these lanes unless fresh proof reactivates them.

## Shell Root Proof

- shell_root:
- `pyproject.toml` present:
- `ION/REPO_AUTHORITY.md` present:

## Root authority and Repo Root Proof

Repo root must be supplied by ION runtime or discovered by markers:

- `pyproject.toml`
- `ION/REPO_AUTHORITY.md`

Forbidden as repo-root authority:

- fixed parent-depth root inference
- hard-coded local root literals
- stale `ION/09_integrations` active paths

Related enforcement:

- `ION/04_packages/kernel/ion_workspace_paths.py`
- `ION/tests/test_root_authority_no_unsafe_parent_depth.py`

## Correct Onboarding Sources

- current_operating_packet:
- carrier_profile:
- mount_contract:
- active_carrier_onboarding_packet:
- active_work_packet:
- active_carrier_turn_packet:
- active_role_spawn_plan:
- active_task_return_ledger:

## Allowed Connector Operations

- read bounded ION state
- read current operating packet
- read active packets by allowlist
- request Codex work packets only through `ion_request_codex_work_packet`
- queue operator messages with bounded write confirmation
- record ChatGPT decisions as receipts
- submit task returns only with context proof and template-action proof

## Route Map

- Uploaded forensics -> sandbox/Python first
- Architecture/currentness -> GPT-5.5 high
- Draft packets/digests -> Actions/ChatOps
- Live proof/status -> MCP/Actions read-only
- Source patch/tests -> Codex bounded packet
- Supabase -> read-only mirror by default; typed write only after exact packet
- Secrets/deploy/service/git/destructive -> blocked/high-risk packet

## Braden Interaction Rule

Do not ask Braden to solve ordinary engineering decisions.
Ask Braden only for product intent, UX direction, veto of risky/destructive
work, secrets/auth/deploy/public release/main push/service mutation, or
product-future choices.

## Plain-Language Self-Gate

For mutation-capable steps, use:

```text
action:
owners:
evidence:
duplicate risk:
allowed output:
forbidden output:
new_system:false
verdict:
```

Allowed verdicts:

- `SELF_GATE_PASS_EXECUTE`
- `SELF_GATE_FAIL_SAFE_PACKET`
- `BLOCKED_BY_SECRET_AUTH_DEPLOY_DELETE_MAIN_PUSH`
- `NEEDS_BRADEN_PRODUCT_INTENT`

## High-Stakes Codex Request Shape

For `red_alert`, `action_native_mount`, `authority_security`, `gpt_builder`,
`settlement`, `branch_gateway_mount_equivalence`, or
`operator_release_packaging` work, the connector must send structured fields.
Prose instructions are not enough.

```yaml
confirmation: ION_BOUNDED_WRITE_CONFIRMED
idempotency_key: pckt-<stable-packet-id>
work_class: red_alert
risk_level: red_alert
route_family: red_alert
codex_model_override:
  selected_model: gpt-5.5
  selected_reasoning_effort: high
  reason: <why this work requires the frontier route>
requested_model: gpt-5.5
requested_reasoning_effort: high
model_override_reason: <same fallback reason>
objective: <bounded packet objective>
```

GPT Builder or operator release packaging packets must also include the
operator artifact hygiene gate in their return: one `OPERATOR_FINAL/` outcome
or one final upload kit, with internal logs/fallbacks separated.

## Forbidden Connector Operations

- arbitrary shell
- arbitrary file write
- direct delete
- git push
- credential access
- provider API calls
- browser/computer control
- unbounded local filesystem access
- accepting unproofed worker output as current truth

## Required Return

```text
### CONTEXT PROOF
- root confirmed:
- current operating packet read:
- carrier profile read:
- mount contract read:
- active packets/context surfaces used:
- assumptions:

### TEMPLATE ACTION PROOF
- requested change:
- files changed:
- tests run:
- receipts/view models emitted:
- boundaries not crossed:

### RESULT
- implementation result:
- validation result:
- remaining blockers:
- next lawful move:

### NON-CLAIMS
- no accepted production/live-state claim:
- no Supabase mutation unless explicitly packeted:
- no deploy/restart/git push:
- no secrets access:
```
