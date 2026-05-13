# ChatGPT Context Capsule README

Owner: Composer (packaging lead)  
Backup support: Codex1 (schema/validation), Opus (priority alignment)

## Purpose

Provide a small, current-truth package that can be sent to external ChatGPT without forcing Braden to manually re-explain project state.

## Canon Files

1. `context/00_operational_definition.md`
2. `context/01_current_truth.md`
3. `context/02_canonical_map.md`
4. `context/03_tonight_plan.md`
5. `context/99_nightly_sync_capsule.md`

## Packaging Command

```powershell
powershell -File scripts/package_chatgpt_context.ps1
```

Zip output:

- `context/chatgpt_context_YYYY-MM-DD_HHMM.zip`

## Composer Checklist (every package)

1. Verify runtime truth is fresh in `01_current_truth.md` (timestamp + branch + head).
2. Verify bounded tasks are current in `03_tonight_plan.md`.
3. Verify auth caveat is present: no login-dependent ChatGPT response claims without authenticated provider session.
4. Verify context tier registry reference is current (`docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`).
5. Generate zip with `scripts/package_chatgpt_context.ps1`.
6. Post output path in roundtable + MCP thread.
7. Include any must-read logs/errors in follow-up message if needed.

## Guardrail

External ChatGPT must be treated as synthesis assistant only.
Execution and decisions remain with AIM-OS team.
