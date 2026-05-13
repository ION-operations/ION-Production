# Thread Packet: Codex-BAS Hardening (2026-03-03)

Thread ID: `aimos_task_codex_bas_hardening_2026-03-03`  
Owner: Codex-BAS  
Coordinator: Codex Agent  
Primary consumer: Claude Opus 4.6 (JOC lane)

---

## Mission Objective

Harden BAS contracts and runtime behavior so Opus can safely build and validate JOC browser workflows without interface drift.

---

## In Scope

- `packages/browser-automation-service/` API contract stability
- BAS to JOC compatibility for:
  - screenshot
  - browser status
  - providers
  - extract-response metadata
- E2E reliability for ChatGPT-first flow

## Out of Scope

- Non-browser kernel/context sovereignty changes
- Broad JOC visual redesign not tied to BAS behavior

---

## 24h Deliverables

1. Contract freeze note
   - Confirm current response shapes and version date.
   - Publish explicit field-level contract for JOC consumers.

2. E2E smoke verification
   - Run and document:
     - service health
     - launch/navigate/screenshot/status
     - prompt inject/extract

3. Metadata parity patch plan
   - Decide whether to:
     - extend JOC types to include BAS metadata fields
     - or add adapter fields in BAS responses
   - Keep backward compatibility during transition.

---

## 72h Deliverables

1. Session durability checks
   - save-session
   - verify-session
   - load-session
   - cookie update path

2. Failure-mode hardening
   - invalid browser id
   - stale session
   - selector mismatch

3. Runtime ops note
   - restart behavior
   - expected recovery semantics
   - known limitations

---

## Acceptance Gates

1. Build/test gate
   - `npm run build` passes in `packages/browser-automation-service`
   - `npm test` passes in `packages/browser-automation-service`

2. Contract gate
   - JOC client calls complete without shape errors on frozen endpoints.

3. E2E gate
   - One documented ChatGPT-first proof path from launch to extract.

4. Evidence gate
   - Update posted in thread with required COO report structure.

---

## Validation Commands (minimum)

- `npm run build` (BAS)
- `npm test` (BAS)
- API smoke calls against `:5002` routes listed in `docs/OPUS1_BROWSER_SYSTEM_CONTRACT_AUDIT_V1.md`

---

## Rollback

- Keep additive changes for response shape expansions.
- Do not remove existing fields until JOC adapter is merged.
- Preserve previous endpoint behavior behind compatibility guards where possible.

