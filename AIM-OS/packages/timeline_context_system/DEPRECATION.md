# Timeline Context System — Tier D (Deferred)

**Status:** Non-canonical until promotion criteria pass.  
**Registry:** `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`  
**Decision:** DEC-007 (2026-03-05)

---

## Why Deferred

- **Duplicate noise:** 33+ `*_TAGGED*` and `*_TAGGED_TAGGED*` files in this package.
- **Unclear promotion state:** No single envelope contract; no JOC integration proof.
- **Rule:** Do not treat as canonical context mapper. Use for audit/refactor only.

---

## Before Promotion

1. Dedupe: remove or consolidate `*_TAGGED*` variants.
2. Define envelope contract shared with Tier A/B.
3. Prove JOC integration against promoted path.
4. Document rollback plan.

---

## Canonical Context Paths (Use These)

- **Live seam:** `IDE/src-tauri/src/context_mapper/*`
- **Staging:** `context_capsule_wire_and_mapper_v1/*`
- **Support:** `packages/context_bootloader/*`
