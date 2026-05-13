# ION GPT Setup Audit - 2026-05-13

Status: candidate audit / operator setup checkpoint.

## Operator-facing folder shape

`ION_GPT/` now presents a non-coder setup path:

```text
01_GPT_BUILDER_INPUTS/
02_PACKAGES_TO_UPLOAD/
03_ACTIONS/
04_CURRENT_SANDBOX_CARRIER/
90_HISTORICAL_ZIPS/
99_WORKER_DETAILS/
README.md
```

## Current instructions

Use:

```text
ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md
```

Current instruction posture:

```text
version: v0.3 local reproduction
size: 4044 chars
boot output: compact operator telemetry
BOOT-SEED: suppressed from public output
role_sequence: suppressed unless role phases actually ran and matter
non-claims: compressed into AUTHORITY line
```

Public boot contract:

```text
BOOT :: mounted | blocked
POSTURE :: CLEAN | CONSERVATIVE | DEGRADED | BLOCKED
SOURCES :: <one-line source summary>
OBJECTIVE :: <current objective or none found>
BLOCKER :: <only if actionable>
NEXT :: <one next route>
AUTHORITY :: read-only | sandbox-candidate-write | approved-bounded-write | live-authorized
```

## Upload packages

Use this folder directly:

```text
ION_GPT/02_PACKAGES_TO_UPLOAD/UPLOAD_THESE_ZIPS/
```

It contains real zip files, not symlinks/pointers.

Current upload count:

```text
10 zip files
```

Current sandbox package shown there:

```text
ION_CUSTOM_GPT_SANDBOX_CARRIER_PACKAGE_20260513T155539Z.zip
```

The upload zip files are ignored by git so they are available locally without bloating the repo.

## Actions

There are two GPT Builder Action schemas.

### 1. ION Action Gateway

Use:

```text
ION_GPT/03_ACTIONS/ion-actions.helixion.net/SCHEMA_TO_PASTE.yaml
```

Schema:

```text
version: 0.4.0
operation_count: 25
sha256: 9ee5e43885e85607ae51a0efccd72d780ba57635074bc6b01a2f81dff8ae72ba
```

### 2. ION MCP Action

Use:

```text
ION_GPT/03_ACTIONS/ion.helixion.net_mcp/SCHEMA_TO_PASTE.yaml
```

Schema:

```text
version: 0.1.1
operation_count: 3
sha256: 32933c593667b014e477dadf4638d7133c831267c9bfd50f95b4a69656360214
```

## Local service repair

The old broken service paths pointing at `ION_CODEX FULL` were corrected.

Current local service roots:

```text
ion-action-gateway.service -> /home/sev/ION - Production/ION_Developement
ion-mcp-preview.service -> /home/sev/ION - Production/ION_Developement
```

Current service state from audit:

```text
ion-action-gateway.service: active
ion-mcp-preview.service: active
ion-action-tunnel.service: active
ion-mcp-tunnel.service: active
```

## Auth token

The Action Gateway bearer token is local-only here:

```text
/home/sev/.config/ion/action-gateway.env
```

Use the value after:

```text
ION_ACTION_GATEWAY_TOKEN=
```

Do not upload or paste this token into repo/docs/chat.

## Live GPT signal

The Custom GPT reported:

```text
POSTURE :: CLEAN
MOUNT :: Actions reachable
Gateway verdict: ION_CUSTOM_GPT_ACTION_GATEWAY_READY
MCP preview verdict: ION_CHATGPT_BROWSER_HTTP_MCP_PREVIEW_READY
BLOCKER :: none for read-only probes
AUTHORITY :: read-only
```

Interpretation: the live GPT Action path is reachable for read-only probes.

## Remaining cautions

- Do not change schemas again unless a release packet requires it.
- Test read-only first: gateway health, MCP tools/list, ion_status, active packet, receipts, queue visibility.
- Do not run write/mutation smoke until read-only probes remain clean.
- If `AUTH_INVALID`, `gateway_token_invalid`, or unexpected `AUTH_MISSING` appears, stop protected Action calls and repair auth.
- If public tunnel access fails from non-browser clients but GPT works, trust the GPT Action result for GPT Builder usability and treat CLI public checks as secondary diagnostics.

## Git posture

This work is not committed yet. It includes intended folder moves, new builder scripts, regenerated local upload folders, and service/runbook corrections. Review before commit.

## Non-claims

- no production deployment
- no accepted-state claim
- no GPT Builder change made by Codex
- no live write/mutation action run
- no secrets printed
