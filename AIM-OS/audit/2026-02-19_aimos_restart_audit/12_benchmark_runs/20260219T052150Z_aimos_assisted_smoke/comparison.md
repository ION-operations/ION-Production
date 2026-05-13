# OpenAI Eval Pack Comparison

- Generated UTC: 2026-02-19T05:23:02.182788+00:00
- Baseline run: `20260219T052150Z_baseline_smoke`
- Candidate run: `20260219T052150Z_aimos_assisted_smoke`
- Profile: `smoke`
- Verdict: `pass`

## Aggregate

| Metric | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| commands_failed | 0 | 0 | 0 |
| pytest_passed | 48 | 48 | 0 |
| pytest_failed | 0 | 0 | 0 |
| pytest_warnings | 0 | 0 | 0 |
| duration_seconds_total | 65.758 | 65.981 | 0.223 |

## Performance Deltas

| Metric | Baseline | Candidate | Delta | Improved |
|---|---:|---:|---:|---|
| cmc_write_error_rate | 0.000000 | 0.000000 | +0.000000 | False |
| cmc_write_p99_ms | 174.920600 | 160.342600 | -14.578000 | True |
| hhni_retrieval_mean_relevance | 0.766667 | 0.766667 | +0.000000 | False |
| hhni_retrieval_p95_ms | 238.463500 | 266.003400 | +27.539900 | False |
| hhni_retrieval_p99_ms | 238.463500 | 266.003400 | +27.539900 | False |
| hhni_write_error_rate | 0.000000 | 0.000000 | +0.000000 | False |
| hhni_write_p99_ms | 11303.838500 | 11336.800800 | +32.962300 | False |

## Checks

| Check | Type | Passed | Details |
|---|---|---|---|
| candidate has zero command failures | hard_gate | True | commands_failed=0 |
| candidate pytest failures <= baseline | hard_gate | True | baseline=0 candidate=0 |
| candidate pytest warnings <= baseline | hard_gate | True | baseline=0 candidate=0 |
| performance metric improved: cmc_write_error_rate | advisory | False | baseline=0.000000 candidate=0.000000 delta=+0.000000 |
| performance metric improved: cmc_write_p99_ms | advisory | True | baseline=174.920600 candidate=160.342600 delta=-14.578000 |
| performance metric improved: hhni_retrieval_mean_relevance | advisory | False | baseline=0.766667 candidate=0.766667 delta=+0.000000 |
| performance metric improved: hhni_retrieval_p95_ms | advisory | False | baseline=238.463500 candidate=266.003400 delta=+27.539900 |
| performance metric improved: hhni_retrieval_p99_ms | advisory | False | baseline=238.463500 candidate=266.003400 delta=+27.539900 |
| performance metric improved: hhni_write_error_rate | advisory | False | baseline=0.000000 candidate=0.000000 delta=+0.000000 |
| performance metric improved: hhni_write_p99_ms | advisory | False | baseline=11303.838500 candidate=11336.800800 delta=+32.962300 |
