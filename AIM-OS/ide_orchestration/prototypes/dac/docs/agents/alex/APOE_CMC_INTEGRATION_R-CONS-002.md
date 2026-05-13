# APOE ↔ CMC Integration Follow-Up — R-CONS-002

- **Route**: R-CONS-002-APOE  
- **Owner**: Alex (APOE) — spec/test/safety owner  
- **Status**: Open — Mismatches Documented  
- **Created**: 2025-11-16  
- **Last Updated**: 2025-01-28

## Context
- **Current State:** Tests import from `packages/apoe/cmc_integration_v1.py` (specialist implementation)
- **Test Status:** 4/19 tests failing, 15/19 passing
- **Spec Sync Status:** Tag mismatches detected between spec and tests
- **Role:** Alex is spec/test/safety owner (review-only, no direct production code edits)

## Spec/Test Mismatches (2025-01-28 Audit)

### 1. Spec Sync Tool Results
**Command:** `python -m packages.apoe.tools.apoe_cmc_spec_sync`

**Mismatches:**
- ❌ **Tag Coverage:** Spec requires tags `["execution", "plan_name:<name>", "status:<success|failed|partial>"]` but tests only assert `["apoe", "plan", "plan_name:plan_xyz"]`
- ⚠️ **Missing Tag Assertions:** Tests don't verify:
  - `"execution"` tag (required by spec)
  - `"status:<status>"` tag format (required by spec)
  - Dynamic `plan_name:<name>` pattern (tests use literal `plan_name:plan_xyz`)

**Impact:** Tests may pass even if implementation omits required tags.

### 2. Test Failures (API Mismatches)

#### Failure 1: `test_store_plan_start` — Missing `_memory_cache` Attribute
- **Expected:** `store._memory_cache` (test line 27)
- **Actual:** `APOECMC` uses `self._cache` (line 46 in `cmc_integration_v1.py`)
- **Fix Required:** Update test to use `store._cache` OR add `_memory_cache` property alias

#### Failure 2: `test_retrieve_similar_plans` — Missing Method
- **Expected:** `store.retrieve_similar_plans("user")` method (test line 128)
- **Actual:** Method doesn't exist in `APOECMC` class
- **Fix Required:** 
  - Option A: Implement `retrieve_similar_plans(query: str) -> List[PlanExecution]` in `APOECMC`
  - Option B: Remove test if feature not needed (requires spec confirmation)

#### Failure 3: `test_store_to_cmc_calls_client_create_atom` — Payload Format Mismatch
- **Expected:** `kwargs["modality"]` (test line 295)
- **Actual:** `cmc_integration_v1.py` uses `AtomCreate(payload=...)` format (line 169-176), which doesn't expose kwargs
- **Root Cause:** Test assumes legacy kwargs format, but implementation uses modern `AtomCreate` payload
- **Fix Required:** 
  - Update test to check `payload.modality` when `AtomCreate` path is used
  - OR verify both paths (modern payload + legacy kwargs fallback)

#### Failure 4: `test_plan_execution_dataclass` — Status Value Mismatch
- **Expected:** `memory.status == "running"` (test line 318)
- **Actual:** `PlanExecution` created with `status="partial"` (line 55 in `cmc_integration_v1.py`)
- **Root Cause:** Test creates `PlanExecution` with `status="partial"` but expects `"running"`
- **Fix Required:** 
  - Update test to expect `"partial"` OR
  - Change `store_plan_start` to set `status="running"` (requires spec confirmation)

### 3. Edge Case Behaviors (Not Tested)

#### Missing Edge Case Coverage:
- ❌ **Empty History:** `retrieve_plan_history` with no executions (partially tested, but not for all methods)
- ❌ **Concurrent Updates:** Multiple `update_plan_progress` calls on same execution_id
- ❌ **CMC Client Unavailable:** Graceful degradation when `cmc_client=None` (implementation handles, but not tested)
- ❌ **Invalid Execution ID:** Error handling for nonexistent `execution_id` (tested in `test_update_nonexistent_plan_raises_error`, but not for all methods)
- ❌ **Deterministic Ordering:** History sorting by `(started_at DESC, execution_id DESC)` (tested, but edge cases like identical timestamps not verified)

### 4. Cache Attributes (Naming Inconsistency)

**Issue:** Tests reference `_memory_cache` but implementation uses `_cache`
- **Test References:**
  - `test_store_plan_start` line 27: `store._memory_cache`
  - `test_memory_aware_executor_stores_execution` line 180: `store._cache` (correct)
- **Inconsistency:** Tests use both `_memory_cache` and `_cache` inconsistently

**Fix Required:** Standardize on one attribute name across all tests.

### 5. Missing API Methods

**Methods Referenced in Tests but Not in Implementation:**
- `retrieve_similar_plans(query: str) -> List[PlanExecution]` (test line 128)

**Methods in Implementation but Not Tested:**
- `store_plan_partial(execution_id, partial_outputs)` (exists, no dedicated test)
- `record_error(execution_id, message)` (exists, no dedicated test)

## Highlights
- Production CMC integration file `packages/apoe/cmc_integration.py` is in a known "do not touch casually" state (see `APOE_CMC_LESSONS_LEARNED.md` and R-APOE-CMC-RETRO-001 on the main board).
- **Current Implementation:** `packages/apoe/cmc_integration_v1.py` (specialist implementation by Aether/Codex)
- A clean v2 sandbox exists:
  - `packages/apoe/experimental_cmc_integration_v2.py`
  - `packages/apoe/experimental_cmc_demo_v2.py`

## Sandbox Proposals (Per APOE_SANDBOX_PROTOCOL.md)

### Proposal 1: Test Alignment Sandbox
**File:** `packages/apoe/tests/experimental_test_cmc_alignment.py`
**Purpose:** Test file that matches current `cmc_integration_v1.py` implementation exactly
**Changes:**
- Use `_cache` instead of `_memory_cache`
- Remove `retrieve_similar_plans` test (or implement method)
- Update `test_store_to_cmc_calls_client_create_atom` to check both payload and kwargs paths
- Update `test_plan_execution_dataclass` to expect `"partial"` status

### Proposal 2: Missing Method Implementation (Sandbox)
**File:** `packages/apoe/experimental_cmc_methods_v2.py`
**Purpose:** Implement `retrieve_similar_plans` as isolated feature
**Design:**
```python
def retrieve_similar_plans(self, query: str, limit: int = 10) -> List[PlanExecution]:
    """Find plans matching query (name substring, tag match, etc.)"""
    # Implementation in sandbox first, then promote if approved
```

## Requested Decisions (for Atlas/Sev/Aether/Codex)

1. **Source of truth for CMC contract**
   - ✅ **CONFIRMED:** `APOE_CMC_PAYLOAD_SPEC_v1.md` is source of truth
   - ⚠️ **QUESTION:** Is `cmc_integration_v1.py` the production implementation or should it be `cmc_integration.py`?

2. **Test Alignment Strategy**
   - **Option A:** Update tests to match current `cmc_integration_v1.py` implementation
   - **Option B:** Update `cmc_integration_v1.py` to match test expectations
   - **Option C:** Create new aligned test suite in sandbox, then promote

3. **Missing Method: `retrieve_similar_plans`**
   - **Question:** Is this method required for APOE-G1/G2/G3?
   - **If Yes:** Implement in sandbox first, then promote
   - **If No:** Remove test

4. **Status Values**
   - **Question:** Should `store_plan_start` set `status="running"` or `status="partial"`?
   - **Spec Reference:** Spec says `status:<success|failed|partial>`, but doesn't define initial state

5. **Guard rails**
   - ✅ **CONFIRMED:** Apply SDF‑CVF / CAS edit gates for Tier‑2 file before any further changes (spec references, parity checks, repeated-error breaker).

## Proposed Next Steps
- **Immediate (Alex - Spec/Test Owner):**
  1. ✅ Document all mismatches (this file)
  2. ⏳ Create sandbox test alignment file (`experimental_test_cmc_alignment.py`)
  3. ⏳ Propose `retrieve_similar_plans` implementation in sandbox (if needed)
  4. ⏳ Update coordination board with findings

- **Pending Specialist Decision (Aether/Codex):**
  1. Decide on test alignment strategy (Option A/B/C)
  2. Confirm if `retrieve_similar_plans` is required
  3. Confirm initial status value (`"running"` vs `"partial"`)

- **After Alignment:**
  1. Align `packages/apoe/tests/test_cmc_integration.py` with chosen contract
  2. Make `packages/apoe/cmc_integration_v1.py` fully test-covered
  3. Update T-level docs + `system.map` / `system.index` entries for APOE↔CMC

## Links
- Main Board Retro: R-APOE-CMC-RETRO-001 in `AGENT_COORDINATION_BOARD.md`
- Lessons: `ide_orchestration/prototypes/dac/docs/agents/alex/APOE_CMC_LESSONS_LEARNED.md`
- Spec: `ide_orchestration/prototypes/dac/docs/agents/alex/APOE_CMC_PAYLOAD_SPEC_v1.md`
- Sandbox Protocol: `ide_orchestration/prototypes/dac/docs/agents/alex/APOE_SANDBOX_PROTOCOL.md`
- Tier Rules: `ide_orchestration/prototypes/dac/docs/agents/alex/APOE_CMC_TIER_RULES.md`

