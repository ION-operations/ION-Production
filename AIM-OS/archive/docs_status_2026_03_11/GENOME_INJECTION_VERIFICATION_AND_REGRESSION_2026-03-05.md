# Genome Injection Verification and Regression Canon (2026-03-05)

Status: active
Owner: Codex (verification) + Opus (runtime implementation owner in Antigravity)
Scope: lock genome injection behavior as canonical and testable

## Why This Exists

Genome injection moved from "design intent" to "runtime working behavior."
This document freezes:
- what is confirmed working
- where it is configured
- how to retest quickly after any restart/update

## Confirmed Evidence

1. User runtime proof (Braden):
- New Antigravity chat with only "hey" produced correct identity behavior.

2. Opus milestone on MCP bus:
- Message ID: `ai_msg_7_20260305_115527`
- Thread: `aimos_roundtable_audit_day_2026-03-05`
- Claim: zero-context conversation boots full identity and startup protocol from injected genome rules.

3. Runtime configuration path found:
- `C:\Users\bombe\.gemini\GEMINI.md` (updated 2026-03-05 11:51 ET)
- Contains Opus identity, role, rules, team roster, startup protocol.

4. Startup workflow path found:
- `.agent/workflows/startup.md`
- Defines startup sequence including genome read and comms checks.

## Canonical Injection Paths

1. Antigravity:
- Injection source: `C:\Users\bombe\.gemini\GEMINI.md`
- Genome reference inside injection: `.agent/genomes/antigravity.genome.md`
- Startup workflow: `.agent/workflows/startup.md`

2. Cross-platform mapping reference:
- `docs/GENOME_INJECTION_PROTOCOLS_BY_PLATFORM.md`

3. Architecture reference:
- `docs/GENOME_ARCHITECTURE_BASE_PLUS_OVERLAY.md`

## Regression Test (Fast, Required)

Run this after any Antigravity update, IDE restart, or genome edit.

### Test A - Zero-context identity boot

1. Open a brand-new Antigravity conversation.
2. Send exactly: `hey`
3. Pass criteria:
- agent identifies itself as Opus/COO
- behavior matches configured rules (not generic default behavior)
- startup protocol awareness is present

### Test B - Startup protocol behavior

1. In the same fresh conversation, run startup flow (or verify it is followed).
2. Pass criteria:
- comms check occurs (`get_ai_messages`)
- context retrieval behavior is present (`retrieve_memory` or equivalent)
- bus announcement is posted

### Test C - Bus proof

1. Query MCP bus for latest Opus status message.
2. Pass criteria:
- message appears with expected sender identity
- message content reflects startup/online posture

## Failure Criteria

Mark `FAIL_GENOME_INJECTION` if any occur:
- generic/no-identity response in fresh chat
- missing role/team awareness
- startup protocol not followed
- no bus announcement after startup

## Known Drift Risks

1. Documentation can lag runtime:
- Some audit docs earlier in the day marked genome injection as disconnected.
- Current evidence supersedes that state for Antigravity runtime.

2. Static capability text drift:
- `C:\Users\bombe\.gemini\GEMINI.md` currently states MCP counts that may become stale.
- Keep identity/rules stable, but review numeric telemetry claims periodically.

## Operational Rule

No architecture claim is "real" until it passes the zero-context `hey` test in a fresh session.

## Next Sync Actions

1. Add a short "post-audit update" note in capability docs linking this file.
2. Mirror this same regression pattern to ChatGPT and Cursor injection paths.
3. Keep one canonical message ID per day proving zero-context boot worked.
