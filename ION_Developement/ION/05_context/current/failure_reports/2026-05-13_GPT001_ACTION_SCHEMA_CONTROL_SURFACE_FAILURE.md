# Failure Report: GPT-001 Action Schema Control Surface Failure

Status: candidate failure report.
Date: 2026-05-13.
Reporter: operator.
Carrier responsible: Codex / ChatGPT-assisted local implementation lane.

## Incident title

GPT-001 Action schema was replaced with an incomplete Supabase-only schema
fragment, breaking trust and likely removing prior Action Gateway operations
from the GPT Builder configuration.

## Operator impact

The operator followed the carrier's instructions and was made to repeatedly
modify GPT Builder Action settings with broken or incomplete YAML.

The operator reported that three consecutive errors fully shut down their
ability to continue work. The practical impact was not only technical breakage;
it was loss of trust, interruption of working state, and forced manual recovery
labor inside GPT Builder.

## Failed instruction chain

The carrier built and presented a Supabase-specific OpenAPI schema as if it were
the correct install target for GPT-001 Actions.

The problematic artifact was:

```text
ION/07_templates/actions/ION_SUPABASE_ACTIONS_OPENAPI_V0_1.yaml
```

That file contained only the Supabase cockpit operations. It did not contain the
older ION Action Gateway operations. It has now been removed from the live
template path because even retaining it as a `.yaml` reference was an operator
hazard.

The operator-facing guide also incorrectly said:

```text
Use:
ION/07_templates/actions/ION_SUPABASE_ACTIONS_OPENAPI_V0_1.yaml
```

That instruction was wrong. The canonical GPT Builder schema target is:

```text
ION/09_integrations/custom_gpt_action_gateway/openapi.yaml
```

## Evidence observed

Commit adding the incomplete Supabase schema surface:

```text
0b5fc50 PCKT: expose Supabase ion_ops cockpit actions
```

Files added or changed by that commit included:

```text
ION/07_templates/actions/ION_SUPABASE_ACTIONS_OPENAPI_V0_1.yaml
ION/docs/setup/ION_ACTION_GATEWAY_SUPABASE_ACTIONS.md
ION/04_packages/kernel/ion_custom_gpt_action_gateway.py
ION/tests/test_kernel_ion_custom_gpt_action_gateway_supabase.py
```

The later recovery commit created a combined schema:

```text
9929253 PCKT: recover combined GPT Action Gateway schema
```

That recovery commit touched:

```text
ION/09_integrations/custom_gpt_action_gateway/openapi.yaml
ION/tests/test_kernel_ion_custom_gpt_action_gateway_policy.py
```

The combined schema currently contains:

```text
18 prior ION Action Gateway operations
7 Supabase cockpit operations
25 total operations
```

## What was true

The Supabase cockpit operations were real local Action Gateway routes.

The local Supabase event mirror and readmodel work had progressed enough to add
Action Gateway endpoints.

A Supabase action schema fragment was useful as a reference artifact.

## What the carrier incorrectly assumed

The carrier treated the Supabase fragment as a GPT Builder replacement schema.

The carrier failed to treat GPT Builder as a live external control surface that
needed rollback, operation inventory, and canonical merge validation before any
manual operator action.

The carrier also failed to stop after the first `AUTH_INVALID` result and let
the GPT Action path attempt additional calls while the lane was already blocked.

## Root cause

The root cause was control-surface confusion:

```text
template / fragment schema
was treated as
canonical live GPT Action schema
```

The engineering failure was not just YAML syntax. The failure was allowing a
candidate partial surface to be installed over a live composed Action surface.

The ION-law failure was:

```text
candidate output was treated as operator-executable state
before merge, proof, rollback, and install-target validation
```

## Missing gates

The following gates should have been mandatory before asking the operator to
touch GPT Builder:

- Export or screenshot current GPT Builder Action configuration.
- Inventory old operationIds.
- Mark Supabase OpenAPI as a fragment, not the install target.
- Merge Supabase paths into the canonical schema.
- Verify all old operationIds remain present.
- Verify no duplicate operationIds.
- Verify server and auth are unchanged.
- Verify the canonical schema is served by the live gateway.
- Provide a rollback path before replacement.
- Stop all Action calls after first `AUTH_INVALID`.

## Containment decision

Do not ask the operator to paste or replace any more GPT Builder YAML until the
canonical schema recovery is treated as the only install path.

Do not run more GPT Action calls from GPT-001 while the Builder auth/schema state
is uncertain.

Do not treat the Supabase-only OpenAPI file as an installable schema.

## Correct install target

Only this file should be used as the Custom GPT Action schema:

```text
ION/09_integrations/custom_gpt_action_gateway/openapi.yaml
```

The Supabase-specific file must not exist as an installable template:

```text
ION/07_templates/actions/ION_SUPABASE_ACTIONS_OPENAPI_V0_1.yaml
```

## Recovery prerequisites

Before recovery continues:

1. The combined canonical schema must be the only GPT Builder install target.
2. The operator must not be asked to install a fragment schema.
3. The GPT Builder bearer token must be aligned to the current Action Gateway
   token without printing it in chat.
4. A fresh GPT session must be started after Builder changes are saved.
5. The GPT instructions or schema descriptions must tell the carrier to stop all
   Action calls after `AUTH_INVALID`.

## Non-claims

This report does not claim accepted ION state.

This report does not claim production deployment.

This report does not claim GPT Builder has already been repaired.

This report does not claim the operator caused the failure.

This report assigns the failure to the carrier instruction chain.
