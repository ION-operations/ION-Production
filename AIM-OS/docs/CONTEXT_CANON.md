# Context Canon — Single Entry Point

**Purpose:** One place to find context-system truth.  
**Source:** DEC-007 (2026-03-05)

---

## Canonical Registry

**Full registry:** `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`

| Tier | Role | Path |
|------|------|------|
| **A** | Live seam | `IDE/src-tauri/src/context_mapper/*`, `context_service.rs` |
| **B** | Staging/prototype | `context_capsule_wire_and_mapper_v1/*` |
| **S** | Support layer | `packages/context_bootloader/*` |
| **D** | Deferred | `packages/timeline_context_system/*` — do not promote until dedupe |
| **E** | Evidence only | `docs/phase2b_context_packet/*` |

---

## Rules

1. No new context stack without DEC + tier assignment.
2. `*_TAGGED*` files are non-canonical until explicitly promoted.
3. Tier D/E work = audit/refactor only, not runtime promotion.

---

## Promotion Criteria (before Tier D → canon)

1. Envelope contract explicit and shared.
2. Duplicate cleanup complete (`*_TAGGED*` in timeline_context_system).
3. JOC integration proof exists.
4. Rollback plan documented.
