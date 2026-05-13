# AIMOS Stale Canon Collision Register - 2026-03-13

Status: evidence-only collision register for `CONSOLIDATION-WORK-PACKAGE-02`

Purpose:
- record direct doc-to-disk or report-to-disk collisions
- make stale-looking authoritative claims explicit
- avoid resolving any collision in this pass

| ID | Source artifact | Source claim | Direct current evidence | Collision type | Current note |
|---|---|---|---|---|---|
| SCC-001 | `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | `68` package directories, `44` importable, `24` non-importable | live package scan used in Work Package 01 found `71` directories total under `packages/`, `70` excluding `__pycache__`, `43` with `__init__.py`, and `27` without | report-to-disk count collision | the count drift is real; this is not just wording drift |
| SCC-002 | `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` importable package list | `shared` is grouped with importable infrastructure | direct filesystem check in this pass found `packages/shared/` exists and `packages/shared/__init__.py` does not | report-to-disk importability collision | earlier material is stale or using a different counting rule |
| SCC-003 | `.agent/AIMOS_MASTER_SYSTEM_INDEX.md` and older authoritative-looking package descriptions | `timeline_context_system` is presented as a package-level core system | direct filesystem check in this pass found `packages/timeline_context_system/` exists and `packages/timeline_context_system/__init__.py` does not | doc-to-disk importability collision | current simple importability test says the surface is non-importable in this checkout |
| SCC-004 | `.agent/AIMOS_MASTER_SYSTEM_INDEX.md` | Echo Forge Loop path is `apps/echo-forge-loop/` | direct disk evidence shows `echo-forge-loop/` at repo root, and Work Package 01 verification slice recorded no `apps/echo-forge-loop/` path in the current checkout | doc-to-disk path collision | path claim and visible tree do not match |
| SCC-005 | `echo-forge-loop/docs/ECHO_FORGE_LOOP_APP_DOCUMENTATION.md` | local instructions and structural references still point to `apps/echo-forge-loop/` | direct disk evidence shows the surface lives at `echo-forge-loop/` in the current checkout | local-doc-to-disk path collision | the path mismatch is repeated inside local Echo Forge docs, not only in the master index |

## Collision Notes

- `SCC-001` through `SCC-003` are all tied to the same pattern: authoritative-looking package classification text does not fully match the current filesystem state.
- `SCC-004` and `SCC-005` are a second pattern: Echo Forge documentation lineage is pointing at a path that is not the visible path in this checkout.
- this register does not decide which source should win. It records the collisions so later review can evaluate lineage, recency, and scope.
