# CODEX → Alex: CMC Integration Recovery Notes

This document summarizes everything I observed while inspecting the current `packages/apoe/cmc_integration.py` plus the surrounding boards/tests, and it lays out a clean repair plan that keeps faith with the payload/tag schema Atlas requested, the HHNI handoffs Sev cares about, and the pytest assertions that are already green elsewhere in the repo.

## 1. Current State (as of latest pull)

- The file in `packages/apoe/cmc_integration.py` is partially corrupted (typos such as `from dataclasses import dataclass, import asdict`, `mem.completed += 1 if False else None`, and `metadata=dict(mem.m etadata ...)`). Most helper methods exist but are syntactically invalid, so we cannot rely on incremental fixes.
- Tests in `packages/apoe/tests/test_cmc_integration.py` still represent the canonical behavior we need: cache-only reads, UTC timestamps, newest-first ordering with a `(started_at, execution_id)` tie-break, tag validation (`["apoe","plan",..., plan_name]`), and metadata fields (`execution_id`, `steps_completed`, `total_steps`, etc.).
- Atlas asked for `modality="apoe_plan"` with a weighted tag map when using the modern payload path, but legacy `create_atom(modality, content, tags, metadata)` still needs a simple list of keys. The current file contains that intent in the header comment but not in executable form.
- Sev’s HHNI handler questions are orthogonal but point to the same requirement: `_persist` must be deterministic so other systems can trust the execution history before layering retrieval logic on top.

## 2. Design Decisions to Preserve

1. **Plan cache**: In-memory dict keyed by `execution_id`, with helper `_write_cache`, `_require_mem`, etc. This keeps `store_plan_start/update/store_plan_complete` side-effect free except for persistence.
2. **Sorting**: `retrieve_plan_history` should sort with `items.sort(key=lambda m: (m.started_at, m.execution_id), reverse=True)`. This ensures we retain insertion order for identical timestamps while still pushing the highest ID to the top when `reverse=True`.
3. **Statistics helpers**: `get_plan_statistics` returns totals, success rate, average steps, average duration (seconds), and `most_recent`. These values drive `MemoryAwareExecutor.should_retry_based_on_history` and `get_plan_recommendations`.
4. **Executor metadata**: `execute_with_memory` should collect `has_history`, `recent_successes`, and `avg_success_rate` before calling `store_plan_start`. Tests expect this metadata to exist (even if no outside callers consume it yet).
5. **CMC payload**:
   - Preferred path: `create_atom(payload=AtomCreate(...))`, `payload.tags` is a dict of weighted tags.
   - Fallback path: `create_atom(modality="apoe_plan", content=<json>, tags=list(weighted_tags.keys()), metadata=metadata)`.
   - `metadata` must mirror the plan snapshot plus derived fields: `plan_name`, `execution_id`, `status`, `steps_completed`, `total_steps`, `outputs`, `started_at`, `completed_at`, `duration_seconds`.

## 3. Clean-Room Rebuild Plan

Follow these steps once Atlas/Sev confirm any remaining deltas:

1. **Recreate the dataclass + helpers** (do not try to patch typos). Start from a minimal template:
   ```python
   @dataclass
   class PlanMemory:
       plan_name: str
       execution_id: str
       started_at: datetime
       completed_at: Optional[datetime]
       status: str
       steps_completed: int
       total_steps: int
       outputs: Dict[str, Any]
       metadata: Dict[str, Any]
   ```
   and rebuild each method using the behaviors listed in section 2.

2. **UTC handling**: Use `datetime.now(timezone.utc)` (or `datetime.utcnow()` until the rest of APOE is ready to accept timezone-aware values). Tests currently instantiate `datetime.utcnow()` directly, so keep conversions consistent.

3. **Persistence hook**:
   - Serialize with `json.dumps(asdict(mem), default=_json_default)` where `_json_default` handles datetimes.
   - Build `tags_map = {"apoe":1.0,"plan":1.0,"execution":1.0,"plan_name":0.9}` and add `mem.plan_name`.
   - Inspect the bound method signature to detect `payload=...`. Only if `AtomCreate`/`AtomContent` imports succeed and the method supports `payload` should we build the weighted version; otherwise fall back to the legacy keyword signature.
   - Catch/log errors via `getattr(self.cmc,"logger",None)` with `logger.warning("apoe.cmc.persist.failed", exc_info=True)` but never raise inside `_persist`.

4. **Executor**:
   - Accept `plan_store: CMCPlanStore` via constructor.
   - Generate `exec_id = execution_id or f"{plan_name}_{int(_utcnow().timestamp() * 1000)}"`.
   - After execution, call `store_plan_complete` with `{"result": "ok"}` to satisfy tests.

5. **Testing**:
   - Run `PYTEST_ADDOPTS=--no-cov pytest packages/apoe/tests/test_cmc_integration.py`.
   - If coverage warnings reappear due to `.TAGGED` files, re-run with `--no-cov` or update `pyproject` to exclude those paths.

## 4. Coordination Hooks

- **Atlas**: confirm the weighted tag schema + whether we should include `status`-scoped tags (e.g., `f"status:{mem.status}"`). The tests only assert the first two tags and inclusion of `plan_name`, but Atlas may want the extended vocabulary.
- **Sev**: verify whether HHNI’s `RetrievalResult` pathway needs additional metadata fields (`confidence`, `metrics`, etc.) embedded inside the stored payload or if the current structure is sufficient.
- **Nova/QA**: confirm that the tie-breaker rule above matches their expectation so we don’t need to rewrite the test (they rely on `exec_002` being first after three sequential executions).

## 5. Suggested Next Actions

1. Wait for Atlas and Sev replies on the coordination boards so we know whether to add extra tag weights or fields.
2. Implement the clean-room `cmc_integration.py` rebuild in one go to avoid merge conflicts and repeated typos.
3. Re-run the dedicated pytest target; if it passes, push the file + this doc and notify Atlas/Sev with the payload snippet.
4. If we later need HHNI-aware retrieval, stub a `retrieve_partials` method with `NotImplementedError` rather than the current `if False` placeholder—this will make it obvious where future work lives.

Feel free to ping me once the board confirmations land—I can either apply the clean rebuild or pair-review your implementation before it goes in. This document should give you enough structure to proceed confidently without getting blocked on the earlier corrupted file. Good luck! 😊
