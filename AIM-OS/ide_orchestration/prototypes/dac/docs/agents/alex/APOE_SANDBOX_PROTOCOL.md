## APOE Sandbox Protocol (Alex)

**Scope:** APOE Tier‑2 integrations (APOE↔CMC, APOE↔HHNI, APOE↔SEG, APOE↔VIF, APOE↔SDF‑CVF, APOE↔TCS, APOE↔CAS).

**Goal:** Ensure high‑impact changes are developed and validated in an *isolated sandbox* before touching production modules.

---

### 1. When to Use the Sandbox

Use this protocol whenever:

- Changing a Tier‑2 integration contract (payload shape, tags, metrics, statuses).
- Refactoring integration modules in ways that affect cross‑system behavior.
- Exploring new behaviors/metrics that are not yet reflected in the spec.

**Do NOT** apply experimental changes directly to:

- `packages/apoe/cmc_integration.py`
- other canonical APOE integration modules

without going through the sandbox steps below.

---

### 2. Sandbox Flow (High‑Level)

1. **Snapshot + Spec Check**
   - Take a snapshot (via CMC/TCS tools or simple git branch).
   - Confirm the current spec and tests are up to date:
     - `APOE_CMC_PAYLOAD_SPEC_v1.md`
     - `APOE_CMC_TEST_CHECKLIST.md`

2. **Create Sandbox Module**
   - Add an *isolated* module, e.g.:
     - `packages/apoe/experimental_cmc_integration_v2.py`
   - Do **not** import it from production `__init__` or wire it into APOE’s main code paths.

3. **Add Demo + Local Tests**
   - Add a small demo script under `packages/apoe/` (e.g. `experimental_cmc_demo_v2.py`) that:
     - constructs a mock CMC client
     - runs several plans through the sandbox
     - prints payloads + aggregated stats.
   - Add isolated tests under a clearly marked experimental path or with markers so they don’t block production CI.

4. **Validate Against Spec & Checklists**
   - Use the spec/test synchronizer (`apoe_cmc_spec_sync.py`) to compare:
     - spec (`APOE_CMC_PAYLOAD_SPEC_v1.md`)
     - tests (`test_cmc_integration.py`)
   - Manually compare sandbox payloads with:
     - expected modality
     - tag list (plan_name, status)
     - metadata fields/metrics.

5. **Review & Promotion**
   - Present sandbox design + demo + diff to Aether/Codex (or other specialists).
   - Only after review:
     - port *minimal, clean* changes into production modules
     - update tests + spec together.

---

### 3. Sandbox DOs and DON’Ts

**DO:**

- Keep sandbox modules small, focused, and well‑documented.
- Use clear names: `experimental_*` or `*_EXPERIMENTAL.py`.
- Include inline comments tying behavior back to spec sections.
- Treat sandbox as a design reference for future changes.

**DON’T:**

- Import sandbox modules into core APOE paths without an explicit design decision.
- Let experimental code accumulate untested behaviors; always include at least a demo and a few targeted tests.
- Use sandbox as a permanent fork; reconcile with production or retire it once decisions are made.

---

### 4. Example: APOE↔CMC v2 Sandbox (Existing)

Already implemented as a model for this protocol:

- `packages/apoe/experimental_cmc_integration_v2.py`
  - clean v1+ contract, deterministic history, partial/error handling, metrics.
- `packages/apoe/experimental_cmc_demo_v2.py`
  - demo script exercising sandbox end‑to‑end with a mock CMC client.

These serve as the reference pattern for future APOE sandboxes.


