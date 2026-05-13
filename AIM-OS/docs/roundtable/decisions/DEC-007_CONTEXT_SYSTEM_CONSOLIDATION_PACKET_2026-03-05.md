# DEC-007 Context-System Consolidation Packet (2026-03-05)

## Scope

Determine whether AIM-OS context systems should be consolidated into one stack now, federated by lane, or deferred.

## Candidate Comparison (from PROJECT_TRUTH evidence)

| Candidate | Path | Status | Strength | Risk |
|---|---|---|---|---|
| Live Rust mapper seam | `IDE/src-tauri/src/context_mapper/*`, `IDE/src-tauri/src/context_service.rs` | part-built | Closest to live machine seam; deterministic runtime intent | Not yet singular canonical contract for all lanes |
| Context capsule wire stack | `context_capsule_wire_and_mapper_v1/*` | part-built | Strong shadow-sync and packaging experiments | Prototype cluster; not cleanly promoted |
| Context bootloader | `packages/context_bootloader/*` | support layer | Useful loader boundary | Not a full mapper canon by itself |
| Timeline context system | `packages/timeline_context_system/*` | part-built | Broad functionality surface | Heavy duplicate noise (`*_TAGGED*`) and unclear promotion state |
| Phase2b packet snapshots | `docs/phase2b_context_packet/*` | evidence-only | Good historical reference | Not runtime source of truth |

## Decision

### Chosen option: Federate by lane now, consolidate by promotion gate later

Do not force a single merged mapper immediately.  
Use a lane-federated model:

1. **Lane A (live seam):** `IDE/src-tauri/src/context_mapper/*` is primary.
2. **Lane B (shadow/prototype):** `context_capsule_wire_and_mapper_v1/*` continues as staging lane.
3. **Support lane:** `packages/context_bootloader/*` remains shared loader/support component.
4. **Noisy lane containment:** `packages/timeline_context_system/*` stays non-canonical until dedupe and promotion check pass.

## Rationale

1. Current evidence shows multiple viable but competing sources; forced merge now would increase regression risk.
2. Federating lanes preserves momentum while preventing rebuild drift.
3. Promotion-gate consolidation keeps a clear path to one canon without pretending uncertainty is solved.

## Promotion Criteria (required before full consolidation)

1. Single contract doc for context input/output envelope shape.
2. Duplicate cleanup pass on timeline context system (`*_TAGGED*` variants).
3. Integration proof that JOC/Dispatch/Session consume one promoted context path without fallback ambiguity.
4. Runtime evidence pack with pass/fail gates and failure rollback steps.

## Immediate Actions

1. Maintain this lane map as current canon in planning/capsule docs.
2. Block greenfield context rewrites until promotion criteria are met.
3. Prepare next bounded task: context registry + deprecation markers for non-canonical variants.

## Uncertainty Log

1. Whether timeline context system can be promoted after dedupe without contract break.
2. Whether Rust mapper and capsule wire stack can share one envelope contract without adapters.
3. Exact owner boundaries for context-system promotion sign-off under current governance pressure.

