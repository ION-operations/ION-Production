# OpenAI Eval Pack Comparison

- Generated UTC: 2026-02-19T05:15:26.434693+00:00
- Baseline run: `20260219T050458Z_baseline_smoke`
- Candidate run: `20260219T050958Z_aimos_assisted_smoke`
- Profile: `smoke`
- Verdict: `pass`

## Aggregate

| Metric | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| commands_failed | 0 | 0 | 0 |
| pytest_passed | 48 | 48 | 0 |
| pytest_failed | 0 | 0 | 0 |
| pytest_warnings | 0 | 0 | 0 |
| duration_seconds_total | 293.658 | 321.773 | 28.115 |

## Performance Deltas

| Metric | Baseline | Candidate | Delta | Improved |
|---|---:|---:|---:|---|
| cmc_write_error_rate | 0.000000 | 0.000000 | +0.000000 | False |
| cmc_write_p99_ms | 83.997500 | 36.623100 | -47.374400 | True |
| hhni_retrieval_mean_relevance | 0.617022 | 0.617022 | +0.000000 | False |
| hhni_retrieval_p95_ms | 66618.480900 | 71202.408100 | +4583.927200 | False |
| hhni_retrieval_p99_ms | 66618.480900 | 71202.408100 | +4583.927200 | False |
| hhni_write_error_rate | 0.000000 | 0.000000 | +0.000000 | False |
| hhni_write_p99_ms | 9183.415500 | 10104.326800 | +920.911300 | False |

## Checks

| Check | Type | Passed | Details |
|---|---|---|---|
| candidate has zero command failures | hard_gate | True | commands_failed=0 |
| candidate pytest failures <= baseline | hard_gate | True | baseline=0 candidate=0 |
| candidate pytest warnings <= baseline | hard_gate | True | baseline=0 candidate=0 |
| performance metric improved: cmc_write_error_rate | advisory | False | baseline=0.000000 candidate=0.000000 delta=+0.000000 |
| performance metric improved: cmc_write_p99_ms | advisory | True | baseline=83.997500 candidate=36.623100 delta=-47.374400 |
| performance metric improved: hhni_retrieval_mean_relevance | advisory | False | baseline=0.617022 candidate=0.617022 delta=+0.000000 |
| performance metric improved: hhni_retrieval_p95_ms | advisory | False | baseline=66618.480900 candidate=71202.408100 delta=+4583.927200 |
| performance metric improved: hhni_retrieval_p99_ms | advisory | False | baseline=66618.480900 candidate=71202.408100 delta=+4583.927200 |
| performance metric improved: hhni_write_error_rate | advisory | False | baseline=0.000000 candidate=0.000000 delta=+0.000000 |
| performance metric improved: hhni_write_p99_ms | advisory | False | baseline=9183.415500 candidate=10104.326800 delta=+920.911300 |
