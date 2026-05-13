# Sprint 3 Progress Report

- Date: 2026-02-19
- Scope: HB-007, HB-009
- Status: Completed

## Completed

1. HB-007 Tagged file policy
- Implemented coverage exclusion for tagged mirror files:
  - `pyproject.toml` -> `[tool.coverage.run].omit` now includes `*_TAGGED*.py`.
- Added policy checker:
  - `scripts/check_tagged_coverage_policy.py`
  - Confirms tagged omit is present and reports tagged parse health inventory.
- Validation:
  - `python scripts/check_tagged_coverage_policy.py` -> `policy_ok=true`, `tagged_file_count=115`, `parse_failure_count=18`.
  - `pytest packages/seg/tests/test_models.py -q` (default coverage) no longer emits `CoverageWarning: couldnt-parse` for tagged files.

2. HB-009 Claim-to-evidence lock
- Implemented machine-generated evidence bundle:
  - `scripts/generate_claim_evidence_lock.py`
  - outputs:
    - `09_CLAIM_EVIDENCE_LOCK.json`
    - `09_CLAIM_EVIDENCE_LOCK.md`
- Full execution evidence generated on 2026-02-19:
  - MCP parity: `103/103`, parity true
  - APOE: `381 passed`, `10 skipped`
  - HHNI: `119 passed`, `1 skipped`
  - SEG: `104 passed`
  - SDF-CVF: `154 passed`
  - MCP parity pytest guardrail: `2 passed`
3. README claim normalization (completed)
- Replaced high-risk static readiness blocks in `README.md` with evidence-linked wording.
- Added explicit links to `09_CLAIM_EVIDENCE_LOCK.*` in status/testing sections.
- Updated key stale MCP tool count references from `81` to detector-backed `103`.
- Removed/reframed explicit `100% complete`, `100% pass rate`, and `production ready` claim strings in README.

4. CI claim-evidence automation (completed)
- Added workflow:
  - `.github/workflows/claim-evidence-lock.yml`
- Added README claim-language guard script:
  - `scripts/check_readme_claim_language.py`
- Added cross-platform path handling fix in:
  - `scripts/generate_claim_evidence_lock.py`
- CI now enforces:
  - claim-language policy on README,
  - quick claim-evidence lock generation for PR/push,
  - full claim-evidence lock generation on schedule/manual.

## Notes

- Warning debt remains significant in package runs (deprecations and third-party syntax warnings in scanned paths).
- Sprint 3 shifted trust posture from static narrative claims toward command-backed evidence artifacts.
- Historical note: warning debt called out above was addressed in Sprint 4 (`11_SPRINT4_PROGRESS.md`).
