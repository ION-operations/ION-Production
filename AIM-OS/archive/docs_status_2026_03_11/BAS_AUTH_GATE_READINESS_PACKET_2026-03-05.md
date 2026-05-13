# BAS Auth Gate Readiness Packet (2026-03-05)

## Purpose

Provide one operator-safe packet that separates:

1. baseline no-auth operational gates
2. authenticated ChatGPT response/extraction gates

This packet prevents false success claims when provider login is missing.

## Canon Inputs

- `context/00_operational_definition.md`
- `PROJECT_TRUTH/05_operational_definition.md`
- `docs/BAS_AUTH_GATES_7_8_PROOF_RUNBOOK_2026-03-04.md`
- `docs/OPUS1_BROWSER_SYSTEM_VALIDATION_REPORT_V1.md`

## Gate Split

### Track A: Baseline No-Auth Gates

Required pass set:

- MCP health and execute path (`:5001`)
- BAS health and browser lifecycle (`:5002`)
- JOC build
- BAS build + tests
- MCP parity check

Interpretation:

- If all pass, baseline operational spine is healthy.
- This does not prove authenticated provider interaction.

### Track B: Authenticated ChatGPT Gates

Required pass set:

- Gate 7 send-prompt with `waitForResponse=true`
- Gate 8 extract-response with non-empty provider content

Required condition:

- Operator must confirm active ChatGPT login in the same BAS browser session.

## Status Rules

1. `PASS_BASELINE`: Track A complete.
2. `PASS_AUTH`: Track B complete with evidence.
3. `PENDING_AUTH`: login missing/expired, or auth gates not executed yet.
4. `FAIL_AUTH`: auth gates executed and failed with classified cause.

Guardrail:

- Never upgrade `PASS_BASELINE` to `PASS_AUTH` without explicit Track B evidence.

## Auth Execution Lock

- Gate 7/8 execution is blocked unless operator issues explicit token: **`AUTH_READY`**.
- Without `AUTH_READY`, only baseline/no-auth checks are allowed.
- Any run attempted without `AUTH_READY` must be recorded as `PENDING_AUTH`.

## Evidence Template

| Field | Required |
|---|---|
| Timestamp (ET) | Yes |
| Operator | Yes |
| Browser ID | Yes |
| Login confirmed before Gate 7 | Yes |
| Gate 7 request payload | Yes |
| Gate 7 response payload | Yes |
| Gate 8 request payload | Yes |
| Gate 8 response payload | Yes |
| Final status (`PASS_AUTH` / `PENDING_AUTH` / `FAIL_AUTH`) | Yes |
| Failure category (if any) | Conditional |

## Failure Categories

1. `AUTH_REQUIRED`
2. `SELECTOR_MISMATCH`
3. `TIMEOUT_RESPONSE`
4. `EXTRACTION_EMPTY`
5. `TRANSPORT_ERROR`

## Execution Hand-off

1. Codex/Composer maintain packet integrity and packaging.
2. Opus coordinates live run sequence.
3. Operator performs login-dependent action in browser session.
4. Composer posts evidence bundle path and status in roundtable thread.
