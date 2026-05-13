## APOE CMC Integration – Tier‑Aware Edit Rules (Alex)

**File(s):**
- `packages/apoe/cmc_integration.py` (production v1)
- `packages/apoe/tests/test_cmc_integration.py`

**Tier:** 2 (critical cross‑system integration: APOE ↔ CMC ↔ HHNI/SEG/VIF/TCS)

---

### 1. Core Principle

`cmc_integration.py` is **governed**:

- No ad‑hoc edits.
- All changes must flow through **spec → tests → implementation**, not the other way around.
- Experimental work must happen in sandbox modules first.

---

### 2. Allowed Edit Modes

**Mode A – Spec/Test Alignment (Preferred)**

Allowed when:
- Updating `APOE_CMC_PAYLOAD_SPEC_v1.md` and/or `APOE_CMC_TEST_CHECKLIST.md`.

Requirements:
- Run `python -m packages.apoe.tools.apoe_cmc_spec_sync` and ensure:
  - modality in tests matches spec (`plan_execution`).
  - tags list in tests covers required tags (`apoe`, `plan`, `execution`, `plan_name:<name>`, `status:<…>`).
- Only after spec/tests are aligned, small, mechanical changes to `cmc_integration.py` are permitted to match the spec (e.g., field rename, tag tweak).

**Mode B – Sandbox Promotion**

Allowed when:
- A sandbox module (e.g., `experimental_cmc_integration_v2.py`) has been implemented and reviewed.

Requirements:
- Promotion plan documented (what behavior is being adopted and why).
- Tests updated first (or in the same change) to reflect new behavior.
- Code ported from sandbox into production in small, focused diffs.

**Mode C – Emergency Fix (Discouraged)**

Only in:
- Production‑blocking bugs where sandbox/normal flow would cause unacceptable delay.

Requirements:
- Snapshot + branch first.
- Document the emergency fix in `APOE_CMC_LESSONS_LEARNED.md`.
- Follow‑up task to refactor via sandbox and clean up any technical debt.

---

### 3. Gates Before Editing `cmc_integration.py`

Before any non‑trivial change:

1. **Spec Gate**
   - Confirm `APOE_CMC_PAYLOAD_SPEC_v1.md` describes the desired behavior.
   - If not, update the spec first.

2. **Test Gate**
   - Confirm `test_cmc_integration.py` is aligned with the spec, or adjust tests to match the spec change.
   - Use `apoe_cmc_spec_sync.py` to sanity‑check modality/tags/metrics alignment.

3. **Tier Gate (SDF‑CVF/CAS)**
   - If more than N failed attempts on this file have occurred recently, require:
     - CAS review (explain motivation, risks, alternatives).
     - SDF‑CVF parity check (code/tests/docs/NL tags).

4. **Sandbox Gate (for larger changes)**
   - For substantial behavior changes (new metrics, new status flows, different tagging), implement and validate in an experimental module first, following `APOE_SANDBOX_PROTOCOL.md`.

---

### 4. Disallowed Actions

- Editing `cmc_integration.py` to “try things” without:
  - referencing the spec
  - updating tests
  - or using a sandbox.
- Changing payload modality or tags directly in code when they conflict with `APOE_CMC_PAYLOAD_SPEC_v1.md`.
- Repeatedly patching `cmc_integration.py` after multiple failures without escalating to CAS/SDF‑CVF and/or handing off to a specialist.

---

### 5. Role Separation

- **Aether/Codex (Specialist)**
  - Own production implementation of `cmc_integration.py` and its tests.
  - Approve or reject proposals for behavior changes at the spec/implementation level.

- **Alex**
  - Owns spec/test/safety‑rail side:
    - maintains `APOE_CMC_PAYLOAD_SPEC_v1.md` and checklists
    - maintains sandbox designs/demos
    - runs `apoe_cmc_spec_sync.py` and raises mismatches via specs/tests
  - Does *not* directly edit `cmc_integration.py` unless explicitly requested and all gates above are passed.


