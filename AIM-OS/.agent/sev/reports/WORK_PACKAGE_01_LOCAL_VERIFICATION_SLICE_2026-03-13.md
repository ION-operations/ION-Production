# Work Package 01 Local Verification Slice - 2026-03-13

## Purpose

This note captures direct local verification of the top stale-canon and overlap
signals exposed by `AIMOS_CONSOLIDATION_GAP_REGISTER_2026-03-13.md`.

## Verified Findings

### VF-001 - Package inventory drift is real

Direct evidence:

- `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` states:
  - `68` package directories
  - `44` importable
  - `24` not importable
- live package scan used by Work Package 01 states:
  - `71` directories total under `packages/`
  - `70` excluding `__pycache__`
  - `43` with `__init__.py`
  - `27` without

Conclusion:

- the count drift is real
- this is not just a wording mismatch

### VF-002 - `shared` and `timeline_context_system` are currently non-importable

Direct evidence:

- `packages/shared/` exists with no `__init__.py`
- `packages/timeline_context_system/` exists with no `__init__.py`

Conclusion:

- both surfaces are currently non-importable by the simple package test used in this pass
- earlier authoritative-looking material that implies otherwise is stale or using a different counting rule

### VF-003 - Echo Forge path mismatch is real

Direct evidence:

- `.agent/AIMOS_MASTER_SYSTEM_INDEX.md` points Echo Forge Loop to `apps/echo-forge-loop/`
- current local repo contains `echo-forge-loop/` at repo root
- current local repo does not show `apps/echo-forge-loop/`
- local Echo Forge docs still reference `apps/echo-forge-loop/`

Conclusion:

- a real canon-to-disk mismatch exists
- the mismatch appears in both master index and local Echo Forge docs

### VF-004 - JOC/operator-facing UI surface fragmentation is real

Direct evidence:

- `packages/joc/`
- `packages/joc-tournament/`
- `packages/ide_chat_app/`
- `IDE/`

Conclusion:

- multiple adjacent operator-facing UI / habitat surfaces coexist locally
- overlap is not hypothetical; it is directly visible on disk

## Constraint

These findings verify mismatches and overlap only.
They do not decide which surface is canonical.
