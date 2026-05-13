# Sprint 5 Progress Report

- Date: 2026-02-19
- Scope: HB-010 benchmark package for external evaluation
- Status: Phase 1 and Phase 2 completed (framework + smoke/quick/full A/B campaigns)

## Objective

Stand up a reproducible benchmark package that can be used for baseline vs AIM-OS-assisted A/B evaluation with machine-readable outputs.

## Implemented

1. Benchmark pack manifest
- Added: `benchmarks/openai_eval/benchmark_manifest.json`
- Profiles:
  - `smoke` (fast contract/perf sanity checks)
  - `quick` (parity + source-of-truth + APOE/SEG/SDF-CVF package suites)
  - `full` (quick + HHNI suite + full HHNI perf/retrieval benchmarks)

2. Benchmark pack runner/comparator
- Added: `scripts/run_openai_benchmark_pack.py`
- Supports:
  - `run` subcommand:
    - manifest-driven execution,
    - per-task raw logs,
    - pytest summary parsing,
    - benchmark metric extraction.
  - `compare` subcommand:
    - aggregate delta reports,
    - hard-gate checks:
      - command failures,
      - pytest failures,
      - pytest warnings,
    - advisory performance delta checks.

3. Benchmark protocol docs
- Added: `benchmarks/openai_eval/README.md`

4. HHNI retrieval benchmark modernization
- Reworked: `benchmarks/hhni_retrieval_benchmark.py`
  - aligned to current HHNI APIs (`HierarchicalIndex`, `TwoStageRetriever`),
  - fixed stale import/API assumptions,
  - added runtime knobs:
    - `--provider`
    - `--coarse-k`
    - `--dvns-iterations`
    - `--token-budget`

## Validation Evidence

1. Smoke A/B campaign (tuned)
- Baseline:
  - `audit/2026-02-19_aimos_restart_audit/12_benchmark_runs/20260219T052150Z_baseline_smoke/run.json`
- Candidate:
  - `audit/2026-02-19_aimos_restart_audit/12_benchmark_runs/20260219T052150Z_aimos_assisted_smoke/run.json`
- Comparison:
  - `audit/2026-02-19_aimos_restart_audit/12_benchmark_runs/20260219T052150Z_aimos_assisted_smoke/comparison.md`
- Result:
  - hard-gate verdict `pass`
  - both variants: `commands_failed=0`, `pytest_failed=0`, `pytest_warnings=0`

2. Quick A/B campaign
- Baseline:
  - `audit/2026-02-19_aimos_restart_audit/12_benchmark_runs/20260219T052525Z_baseline_quick/run.json`
- Candidate:
  - `audit/2026-02-19_aimos_restart_audit/12_benchmark_runs/20260219T053301Z_aimos_assisted_quick/run.json`
- Comparison:
  - `audit/2026-02-19_aimos_restart_audit/12_benchmark_runs/20260219T053301Z_aimos_assisted_quick/comparison.md`
- Result:
  - hard-gate verdict `pass`
  - both variants: `commands_failed=0`, `pytest_failed=0`, `pytest_warnings=0`
  - aggregate parity: `pytest_passed=641`, `pytest_failed=0`, `pytest_warnings=0`

3. Full A/B campaign
- Baseline:
  - `audit/2026-02-19_aimos_restart_audit/12_benchmark_runs/20260219T054002Z_baseline_full/run.json`
- Candidate:
  - `audit/2026-02-19_aimos_restart_audit/12_benchmark_runs/20260219T060125Z_aimos_assisted_full/run.json`
- Comparison:
  - `audit/2026-02-19_aimos_restart_audit/12_benchmark_runs/20260219T060125Z_aimos_assisted_full/comparison.md`
- Result:
  - hard-gate verdict `pass`
  - both variants: `commands_failed=0`, `pytest_failed=0`, `pytest_warnings=0`
  - aggregate parity: `pytest_passed=760`, `pytest_failed=0`, `pytest_warnings=0`

## Performance Snapshot (Latest Full Campaign)

- `cmc_write_p99_ms`: baseline `40.99`, candidate `67.54` (candidate worse)
- `hhni_write_p99_ms`: baseline `9753.13`, candidate `12699.50` (candidate worse)
- `hhni_retrieval_p95_ms`: baseline `33457.77`, candidate `28901.88` (candidate improved)
- `hhni_retrieval_p99_ms`: baseline `34905.55`, candidate `31666.18` (candidate improved)
- `hhni_retrieval_mean_relevance`: baseline `0.6493`, candidate `0.6493` (no change)

## Interpretation

- Benchmark package is operational end-to-end for smoke, quick, and full profiles.
- A/B contract quality is stable across campaigns (zero hard-gate failures in completed pairs).
- Performance deltas remain mixed and should be treated as optimization backlog inputs, not readiness claims.

## Remaining for HB-010 Completion

- Add multi-run trend and variance reporting (N-run medians/p95 distributions) before external submission.
