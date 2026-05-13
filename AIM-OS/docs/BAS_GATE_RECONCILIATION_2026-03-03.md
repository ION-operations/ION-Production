# BAS Gate Reconciliation (2026-03-03)

## Purpose

Resolve numbering drift between:

- Earlier acceptance note in team messaging (`aimos_roundtable_plan_consolidation_2026-03-03`)
- Current executable smoke script `packages/joc/scripts/bas-e2e-smoke.mjs`

## Confirmed Runtime Gate Map (Current Source of Truth)

From `packages/joc/scripts/bas-e2e-smoke.mjs`:

1. `BAS Health` -> `GET /health`
2. `Browser Launch` -> `POST /api/browser/launch`
3. `Navigation` -> `POST /api/browser/navigate` (chatgpt.com)
4. `Screenshot Capture` -> `GET /api/browser/screenshot`
5. `Browser Status` -> `GET /api/browser/status`
6. `Provider Discovery` -> `GET /api/bridge/providers`
7. `Prompt Injection` -> `POST /api/bridge/send-prompt` (manual login required)
8. `Response Extraction` -> `POST /api/bridge/extract-response` (manual login required)

## Drift Summary

- Prior message text described gates 5-6 as inject/extract.
- Script currently executes status/providers as gates 5-6 and treats inject/extract as gates 7-8.
- This is now treated as contract clarification, not a runtime defect.

## Operational Rule

Use script gate numbering as canonical for execution and reporting until superseded:

- `node packages/joc/scripts/bas-e2e-smoke.mjs`

## Evidence Snapshot (2026-03-03)

Smoke run (no-auth gates):

- Gate 1: PASS
- Gate 2: PASS
- Gate 3: PASS
- Gate 4: PASS
- Gate 5: PASS
- Gate 6: PASS

Auth-required gates 7-8 remain manual by design.
