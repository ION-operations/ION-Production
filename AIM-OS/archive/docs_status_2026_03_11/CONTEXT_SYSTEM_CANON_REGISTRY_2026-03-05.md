# Context System Canon Registry (2026-03-05)

Status: active registry  
Source decision: `docs/roundtable/decisions/DEC-007_CONTEXT_SYSTEM_CONSOLIDATION_PACKET_2026-03-05.md`

## Purpose

Prevent context-system drift by labeling which paths are canonical now, staging now, support-only, or deferred.

## Canon Registry

| Canon Tier | Role | Path | Rule |
|---|---|---|---|
| Tier A | Live seam canonical | `IDE/src-tauri/src/context_mapper/*`, `IDE/src-tauri/src/context_service.rs` | Use for live machine context-mapper integration decisions |
| Tier B | Staging/prototype canonical | `context_capsule_wire_and_mapper_v1/*` | Use for shadow sync experiments and packetized staging only |
| Tier S | Shared support layer | `packages/context_bootloader/*` | Reuse as support/loader component, not as standalone canonical mapper |
| Tier D | Deferred non-canonical | `packages/timeline_context_system/*` | Do not promote to canon until duplicate cleanup + promotion criteria pass |
| Tier E | Evidence snapshot only | `docs/phase2b_context_packet/*` | Reference for audit/history only; never treat as runtime source |

## Deprecation Markers

1. Any context implementation outside Tier A/B/S must be treated as non-canonical by default.
2. `*_TAGGED*` duplicate variants in context packages are non-canonical until explicitly promoted.
3. No new context stack may be introduced without a DEC entry and canon-tier assignment.

## Promotion Criteria (must all pass)

1. Envelope contract is explicit and shared across candidate paths.
2. Duplicate cleanup is complete for candidate path.
3. JOC integration proof exists against promoted path.
4. Rollback plan is documented if promotion regresses runtime behavior.

## Enforcement Rule for Agent Work

When assigning context work packets:

1. Name canon tier (`A`, `B`, `S`, `D`, or `E`) in task header.
2. If tier is `D` or `E`, scope must be audit/refactor only, not runtime promotion.
3. If promotion is requested, include DEC reference and proof criteria up front.

