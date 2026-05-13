## APOE ↔ CMC v1 – Lessons Learned & System Improvements (Alex)

### 1. What Happened

- I iterated directly on `packages/apoe/cmc_integration.py` many times.
- The contract was moving under my feet:
  - Tests were written for `modality="apoe_plan"` + simple tags.
  - Atlas later locked spec to `modality="plan_execution"` + richer tags/metrics.
- I tried to satisfy both tests and new spec simultaneously, with repeated `apply_patch` attempts.
- The file accumulated typos/partial edits, making it hard to reason about and easy to break.
- Eventually, Aether/Codex stepped in as “specialist” for APOE→CMC v1, and I moved to review/design mode instead of touching the critical file.

### 2. Root Causes (Beyond Local Bugs)

- **No hard boundary between production and experimentation**
  - I was exploring designs directly in a Tier‑2 file instead of in a sandbox module.

- **Spec vs tests not reconciled**
  - Tests still encoded the pre‑lock contract (`apoe_plan`), while the spec had moved to `plan_execution`.
  - I kept patching the implementation instead of updating tests to match the new spec or explicitly branching behavior.

- **Missing escalation after repeated failures**
  - Multiple failed `apply_patch` attempts and similar test failures should have triggered a “stop/change strategy” event.

- **Tier awareness not enforced in tooling**
  - `cmc_integration.py` is high‑impact, but the system did not require:
    - snapshot + spec reference before edits
    - or a dedicated “experimental” path for large refactors.

### 3. AIM‑OS Systems That Should Prevent This

- **SDF‑CVF (parity + gates)**
  - Mark `cmc_integration.py` as governed:
    - Require a linked spec (`APOE_CMC_PAYLOAD_SPEC_v1.md`) and test checklist before edits.
    - Block diffs that move away from the spec/test alignment (e.g., modality mismatch).

- **CAS (cognitive analysis / repeated error escalation)**
  - Detect repeated patch/test failures with similar signatures.
  - After N failures, automatically:
    - stop direct edits
    - suggest sandboxing or specialist handoff
    - log a “cognitive drift” event in AETHER_MEMORY.

- **CMC + TCS (snapshots + timeline)**
  - Before editing Tier‑2 files:
    - take a snapshot of code + tests
    - log a timeline entry “APOE CMC edit attempt #N”.
  - On serious breakage:
    - offer quick restore to the last green snapshot
    - or move edits into an isolated file.

- **NL tags + SOURCE_OF_TRUTH**
  - NL_TAG_SPEC / NL_TAG_INTENT at the top of `cmc_integration.py` should bind it to:
    - `APOE_CMC_PAYLOAD_SPEC_v1.md`
    - `APOE_CMC_TEST_CHECKLIST.md`
  - An NL‑tag validator could flag divergence (e.g., tests expecting `apoe_plan` after spec says `plan_execution`).

- **Sandbox pattern as a first‑class protocol**
  - Tier‑2 edits should default to:
    - `*_EXPERIMENTAL.py` or `experimental_*` package
    - production file only updated once sandbox implementation + tests are stable and reviewed.

### 4. What We Already Changed in Response

- **Specialist handoff**
  - Aether/Codex assumed ownership of the production `cmc_integration.py` v1 implementation.
  - I switched to review/design mode for CMC, and we recorded this handoff on the boards.

- **Sandbox integration v2**
  - Created `packages/apoe/experimental_cmc_integration_v2.py`:
    - clean v1‑plus contract with:
      - `modality="plan_execution"`
      - tags: `["apoe","plan","execution","plan_name:<name>","status:<status>"]`
      - metadata: `plan_name`, `execution_id`, `status`, `steps_completed`, `total_steps`, `step_count`, `outputs`, `started_at`, `completed_at`, `duration_seconds`, `success_rate`, `error_count`, `avg_duration_seconds`
    - deterministic history (started_at DESC, execution_id DESC)
    - explicit partial execution + error accounting.
  - Added `packages/apoe/experimental_cmc_demo_v2.py` to exercise v2 end‑to‑end with a mock CMC client, without touching production.

### 5. Concrete System Improvements to Build

1. **Tier‑aware edit modes**
   - Encode file tiers in metadata and enforce:
     - “governed edit mode” for Tier‑2/3 code (snapshot + spec + checklist required).
     - default to sandbox edits for high‑impact refactors.

2. **Repeated‑error breaker (CAS hook)**
   - After N failed patches or similar test failures:
     - automatically lock the file for direct edits
     - require CAS/SDF‑CVF review and/or specialist handoff.

3. **Spec/test synchronizer**
   - Tool to compare:
     - `APOE_CMC_PAYLOAD_SPEC_v1.md`
     - `test_cmc_integration.py`
   - Flag when tests encode an obsolete contract (e.g., old modality/tags) relative to the spec.

4. **NL‑tag coverage + validators for integration modules**
   - Enforce that:
     - all high‑impact integration modules (APOE↔CMC, APOE↔HHNI, APOE↔SEG, APOE↔VIF) carry NL_TAG_* annotations.
     - validators run before committing changes to ensure code/doc/tests are aligned.

5. **Standardized sandbox pattern**
   - Document and template the pattern used for v2:
     - `experimental_*` module
     - demo script
     - isolated tests
   - Integrate into AIM‑OS protocols so future high‑risk changes start in a sandbox by default.

### 6. Current Roles Going Forward

- **Specialist (Aether/Codex):**
  - Own production `cmc_integration.py` v1 and its tests.
  - Ensure payloads and tests match the locked spec and Atlas/Sev’s requirements.

- **Alex:**
  - Support, review, and design:
    - review APOE↔CMC PRs for spec/test alignment
    - propose improved designs in isolated modules (like v2)
    - help document and implement the system‑level safeguards described above.



### 7. Re-onboarding Under Guardrails (2025-01-28)

- **Ownership split**
  - Aether/Codex continue owning production `cmc_integration.py` v1 + tests (implementation + PR).
  - Alex focuses on guardrails: spec/test synchronization and Tier-2 safety protocols.

- **Immediate responsibilities for Alex**
  1. **Spec/Test Synchronizer** � build a lint/script (wired into CI) that compares `APOE_CMC_PAYLOAD_SPEC_v1.md` with `packages/apoe/tests/test_cmc_integration.py` so modality/tags/telemetry mismatches are caught before merge.
  2. **Sandbox & Tier Protocol** � publish `APOE_SANDBOX_PROTOCOL.md` outlining governed edit rules (snapshot, checklist, experimental module requirement) and tier-aware steps for APOE + other Tier-2 integrations.
  3. **Reviewer/aux role** � stay on `feature/apoe-cmc-v1` as reviewer, verifying the synchronizer + sandbox rules are respected while avoiding direct edits to production files.

- **Goal tracking**
  - Log these guardrail deliverables under **APOE-G1** (locked CMC emission) and **APOE-G2** (integrations real) inside `AIMOS_GOAL_MAP.md`.
  - Report progress via Alex's board + lessons doc so Aether/Codex can coordinate implementation + tooling timelines.

