# AIM-OS OpenAI Evaluation Benchmark Pack

## Purpose

This package provides a reproducible benchmark workflow for external technical evaluation.
It is designed to compare two variants under the same task suite:

1. `baseline` (without AIM-OS assist layer enabled)
2. `aimos_assisted` (with AIM-OS assist layer enabled/configured)

The output is evidence artifacts, not narrative claims.

## Components

- `benchmarks/openai_eval/benchmark_manifest.json`
  - Defines benchmark profiles (`smoke`, `quick`, `full`) and task commands.
- `scripts/run_openai_benchmark_pack.py`
  - `run` subcommand: executes a profile and writes run artifacts.
  - `compare` subcommand: compares two run artifacts and writes delta reports.

## Artifact Contract

Each `run` writes:

- `run.json` (machine-readable summary)
- `logs/*.log` (raw command output by task)
- `artifacts/*.json` (task-specific benchmark outputs when configured)

Each `compare` writes:

- `comparison.json`
- `comparison.md`

## Execution

### 1) Baseline run

```powershell
python scripts/run_openai_benchmark_pack.py run `
  --profile smoke `
  --variant baseline
```

### 2) AIM-OS-assisted run

Apply your variant-specific configuration (environment variables, flags, or launch mode), then run:

```powershell
python scripts/run_openai_benchmark_pack.py run `
  --profile smoke `
  --variant aimos_assisted `
  --set-env AIMOS_ASSISTED=1
```

### 3) Compare runs

```powershell
python scripts/run_openai_benchmark_pack.py compare `
  --baseline benchmarks/openai_eval/results/<baseline_run_id>/run.json `
  --candidate benchmarks/openai_eval/results/<candidate_run_id>/run.json
```

## Profile Guidance

- `smoke`: fast contract check and mini benchmarks (for iteration and CI smoke).
- `quick`: full APOE/SEG/SDF-CVF package suites plus parity/source-of-truth checks.
- `full`: quick profile + HHNI suite + full HHNI performance/retrieval benchmarks.

## Notes

- Run profiles should be executed on the same machine class for fair comparisons.
- Keep benchmark input sizes consistent between variants.
- Treat `comparison.md` as the external-facing evidence summary and `run.json` as source data.
