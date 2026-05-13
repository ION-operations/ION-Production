# OpenAI Eval Pack Comparison

- Generated UTC: 2026-02-19T05:39:34.484977+00:00
- Baseline run: `20260219T052525Z_baseline_quick`
- Candidate run: `20260219T053301Z_aimos_assisted_quick`
- Profile: `quick`
- Verdict: `pass`

## Aggregate

| Metric | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| commands_failed | 0 | 0 | 0 |
| pytest_passed | 641 | 641 | 0 |
| pytest_failed | 0 | 0 | 0 |
| pytest_warnings | 0 | 0 | 0 |
| duration_seconds_total | 449.232 | 384.936 | -64.296 |

## Performance Deltas

No overlapping performance metrics were found between runs.

## Checks

| Check | Type | Passed | Details |
|---|---|---|---|
| candidate has zero command failures | hard_gate | True | commands_failed=0 |
| candidate pytest failures <= baseline | hard_gate | True | baseline=0 candidate=0 |
| candidate pytest warnings <= baseline | hard_gate | True | baseline=0 candidate=0 |
