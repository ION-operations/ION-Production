# Task 4 Capsule Completion — COMPLETE

**Agent:** FORGE
**Date:** 2026-03-23T22:28:00-04:00
**Phase/Task:** V5 Task 4 — Capsule Completion (PRE/POST flow)
**Confidence:** 0.90

## Reasoning

- Existing `capsule.py` (52 lines) was a basic session serializer — `save_session`/`load_session` with JSON in markdown
- V5 genome Task 4 calls for full PRE/POST capsule flow: PRE snapshots context before operation, POST records results/metrics/decisions after
- `overseer.py` already writes POST capsules inline (lines 256-270) — the capsule module should be the canonical path
- `create_capsule_ion()` factory at `model.py:795` correctly produces `IonType.CAPSULE` + `A5_INFRA` + `CapsulePhase`
- **Decision:** Kept legacy `ContextCapsule` class as thin wrapper over new `CapsuleManager` for backward compat
- **Decision:** POST capsule bonds to PRE capsule via `depends_on` — creates traceable operation lifecycle

## Work Done

### CapsuleManager (new)
- `create_pre_capsule()` — snapshots context state (active ions, manifest state, custom context)
- `create_post_capsule()` — records results, metrics, decisions, errors with optional bond to PRE
- `parse_capsule_body()` — static method for extracting JSON state from capsule markdown body
- All capsules use `create_capsule_ion()` factory from model.py

### ContextCapsule (legacy wrapper)
- `save_session()` → delegates to `CapsuleManager.create_post_capsule()`
- `load_session()` → uses `CapsuleManager.parse_capsule_body()` with format migration

### model.py deprecation
- Legacy aliases (A1_LOCAL, A3_CORE, A4_SYSTEM) marked DEPRECATED with guidance to use canonical names

## Files Changed

| File | Action | Lines |
|------|--------|------:|
| `victus/ion/capsule.py` | REWRITTEN | 52 → 202 |
| `victus/ion/model.py` | MODIFIED | 1 line (comment) |

## Open Questions

1. **Overseer migration:** `overseer.py` (lines 256-270) creates POST capsules inline — should be migrated to use `CapsuleManager` but that's outside FORGE scope (NEXUS/SENTINEL territory)
2. **No tests:** `victus/ion/tests/` directory doesn't exist — SENTINEL should create verification tests
3. **SeedOS capsules:** `seedos_runtime.py` has its own capsule system (35 sessions) — left untouched per V5 §2 C3
