# OpenAI Eval Pack Comparison

- Generated UTC: 2026-02-19T06:23:51.400116+00:00
- Baseline run: `20260219T054002Z_baseline_full`
- Candidate run: `20260219T060125Z_aimos_assisted_full`
- Profile: `full`
- Verdict: `pass`

## Aggregate

| Metric | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| commands_failed | 0 | 0 | 0 |
| pytest_passed | 760 | 760 | 0 |
| pytest_failed | 0 | 0 | 0 |
| pytest_warnings | 0 | 0 | 0 |
| duration_seconds_total | 1275.167 | 1338.396 | 63.229 |

## Performance Deltas

| Metric | Baseline | Candidate | Delta | Improved |
|---|---:|---:|---:|---|
| cmc_write_error_rate | 0.000000 | 0.000000 | +0.000000 | False |
| cmc_write_p99_ms | 40.989800 | 67.541100 | +26.551300 | False |
| hhni_retrieval_mean_relevance | 0.649286 | 0.649286 | +0.000000 | False |
| hhni_retrieval_p95_ms | 33457.766400 | 28901.877100 | -4555.889300 | True |
| hhni_retrieval_p99_ms | 34905.545600 | 31666.176600 | -3239.369000 | True |
| hhni_write_error_rate | 0.000000 | 0.000000 | +0.000000 | False |
| hhni_write_p99_ms | 9753.133100 | 12699.498700 | +2946.365600 | False |

## Checks

| Check | Type | Passed | Details |
|---|---|---|---|
| candidate has zero command failures | hard_gate | True | commands_failed=0 |
| candidate pytest failures <= baseline | hard_gate | True | baseline=0 candidate=0 |
| candidate pytest warnings <= baseline | hard_gate | True | baseline=0 candidate=0 |
| performance metric improved: cmc_write_error_rate | advisory | False | baseline=0.000000 candidate=0.000000 delta=+0.000000 |
| performance metric improved: cmc_write_p99_ms | advisory | False | baseline=40.989800 candidate=67.541100 delta=+26.551300 |
| performance metric improved: hhni_retrieval_mean_relevance | advisory | False | baseline=0.649286 candidate=0.649286 delta=+0.000000 |
| performance metric improved: hhni_retrieval_p95_ms | advisory | True | baseline=33457.766400 candidate=28901.877100 delta=-4555.889300 |
| performance metric improved: hhni_retrieval_p99_ms | advisory | True | baseline=34905.545600 candidate=31666.176600 delta=-3239.369000 |
| performance metric improved: hhni_write_error_rate | advisory | False | baseline=0.000000 candidate=0.000000 delta=+0.000000 |
| performance metric improved: hhni_write_p99_ms | advisory | False | baseline=9753.133100 candidate=12699.498700 delta=+2946.365600 |
