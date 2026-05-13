# AIM-OS Hardening Backlog (Execution-Ready)

- Owner: Lead Dev (Codex) + Human Principal
- Date: 2026-02-19
- Source: findings register + audit evidence

## Sprint 1: Contract and Trust Reset

### HB-001 MCP parity gate (Critical)
- Status: Completed on 2026-02-19.
- Goal: `tools/list` exactly equals callable tool set.
- Tasks:
  1. extract registry into canonical source,
  2. remove duplicated/manual tool declarations,
  3. add CI parity test.
- Done when:
  - hidden callable tools = 0,
  - listed-only phantom tools = 0.

### HB-002 Source-of-truth generator hardening (Critical)
- Status: Completed on 2026-02-19 (schema validation task deferred to Sprint 1.1).
- Goal: deterministic, parse-safe metrics in `SOURCE_OF_TRUTH.yaml`.
- Tasks:
  1. replace fragile header/category parsing,
  2. add schema validation for generated YAML,
  3. add regression tests for metric stability.
- Done when:
  - no malformed YAML keys,
  - generated counts match detector scripts in CI.

### HB-003 Stale reference cleanup (High)
- Status: Completed on 2026-02-19.
- Goal: remove broken imports in scripts/tests.
- Tasks:
  1. repair `scripts/verify_mcp_tools.py` dependency path,
  2. repair/replace cross-model test harness references,
  3. dedupe `Makefile` test targets.
- Done when:
  - no ModuleNotFound collection errors for targeted suites.

## Sprint 2: Integration Stability

### HB-004 APOE import/schema stabilization (High)
- Status: Completed on 2026-02-19.
- Goal: fix `ExecutionPlan` contract and enhanced executor imports.
- Tasks:
  1. align `apoe.models` exports,
  2. align model schemas with executor expectations,
  3. pass targeted APOE collection + suite subset.

### HB-005 HHNI embedding/Qdrant contract fix (High)
- Status: Completed on 2026-02-19.
- Goal: resolve `PointStruct` mismatch.
- Tasks:
  1. standardize point object handling in embedding path,
  2. update tests/mocks to match runtime contract,
  3. rerun HHNI suite.

### HB-006 SEG/SDF-CVF integration mode normalization (High)
- Status: Completed on 2026-02-19.
- Goal: make dependency availability assumptions explicit.
- Tasks:
  1. define integration mode flags (`strict`, `fallback`, `mocked`),
  2. update tests to mode-specific expectations,
  3. ensure deterministic behavior under CI env.

## Sprint 3: Tooling and Structural Debt

### HB-007 Tagged file policy (High)
- Status: Completed on 2026-02-19 (policy path selected).
- Goal: remove tooling breakage from `*_TAGGED.py` failures.
- Options:
  1. repair all tagged files syntactically, or
  2. exclude tagged mirrors from executable/coverage paths with policy docs.
- Done when:
  - no coverage parse warnings from tagged mirrors.

### HB-008 MCP monolith decomposition plan (High)
- Goal: reduce `lucid_mcp_server.py` risk concentration.
- Tasks:
  1. isolate transport/protocol layer,
  2. extract tool registry,
  3. extract domain handlers,
  4. introduce typed error taxonomy.

## Sprint 4: External Readiness

### HB-009 Claim-to-evidence lock (Critical)
- Status: Completed on 2026-02-19.
- Goal: documentation claims generated from test artifacts.
- Tasks:
  1. machine-generate readiness table,
  2. remove static 100%/production-ready claims,
  3. attach evidence links per claim.

### HB-010 Benchmark package for OpenAI evaluation (Critical)
- Status: In progress (Phase 1 and Phase 2 completed on 2026-02-19).
- Goal: produce reproducible A/B performance evidence.
- Tasks:
  1. define benchmark task suite,
  2. run baseline vs AIM-OS-assisted evaluations,
  3. publish outcome dashboard with logs.
- Phase 1 completed:
  - manifest-driven benchmark profiles (`smoke`, `quick`, `full`),
  - runner/comparator tooling,
  - smoke baseline/candidate run pair + comparison artifacts.
- Phase 2 completed:
  - executed and published `quick` baseline/candidate campaign and comparison artifacts,
  - executed and published `full` baseline/candidate campaign and comparison artifacts.
- Remaining for completion:
  - add multi-run variance/trend reporting for performance metrics,
  - finalize external-facing outcome dashboard package for submission.

### HB-011 Warning/deprecation burn-down for evidence suites (High)
- Status: Completed on 2026-02-19.
- Goal: remove warning noise in package suites used for claim evidence.
- Tasks:
  1. modernize APOE UTC timestamp usage and tests,
  2. remove SEG pytest return-value warnings,
  3. eliminate SDF-CVF blast-radius parser and sqlite datetime adapter warning sources.
- Done when:
  - APOE/SEG/SDF-CVF suites are green with zero warnings in Sprint 4 validation artifacts.

## Reporting Cadence
- Weekly:
  1. failed test count by subsystem,
  2. contract mismatches,
  3. source-of-truth drift,
  4. blocker burn-down.
