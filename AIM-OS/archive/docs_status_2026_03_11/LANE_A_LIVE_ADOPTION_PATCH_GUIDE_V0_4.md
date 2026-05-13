# Lane A Live Adoption Patch Guide v0.4

Status: Historical reference (Lane A has executed constrained slice)  
Date: 2026-03-02

---

## Purpose

Translate the validated Lane B reference hook (in `context_mapper_lab`) into the real Lane A seam:

- `src-tauri/src/context_mapper/api.rs`
- `src-tauri/src/context_mapper/mod.rs`
- new `src-tauri/src/context_mapper/shadow_hook.rs`

This guide is implementation-oriented and was used for constrained-slice translation planning.  
Live implementation state is now recorded in `docs/LANE_A_CHECKPOINT_D_PASSIVE_HOOK_EXECUTION_REPORT_V1.md`.

---

## Scope (Do only this)

Implement:

- post-resolution, pre-envelope passive hook call
- env flag `AIMOS_SHADOW_BCI_PASSIVE_EMIT` (default off)
- fail-open behavior for all shadow failures
- minimal logging (`shadow_emit_attempt`, `shadow_emit_success`, `shadow_emit_failure`)

Do not implement:

- hard/soft sync gates
- routing overrides
- contradiction/drift enforcement
- daemon-plane governance coupling

---

## Source Reference (already validated)

Use these files as the proven reference:

- `context_capsule_wire_and_mapper_v1/context_mapper_lab/src/shadow_hook.rs`
- `context_capsule_wire_and_mapper_v1/context_mapper_lab/src/main.rs`
- `context_capsule_wire_and_mapper_v1/context_mapper_lab/src/lib.rs`

Validation already passed:

- `cargo test` in `context_mapper_lab`: `4/4` hook tests
- runtime checks: disabled path, enabled success, forced emitter failure (fail-open)

---

## Lane A Patch Steps

1) Add module:

- create `src-tauri/src/context_mapper/shadow_hook.rs`
- port logic from lab `shadow_hook.rs`
- keep env names unchanged:
  - `AIMOS_SHADOW_BCI_PASSIVE_EMIT`
  - optional: `AIMOS_SHADOW_BCI_ROOT`, `AIMOS_SHADOW_BCI_OUT_DIR`, `AIMOS_SHADOW_BCI_PYTHON`, `AIMOS_SHADOW_BCI_EMITTER`, `AIMOS_SHADOW_BCI_SCHEMA`

2) Export module in `src-tauri/src/context_mapper/mod.rs`:

- add `mod shadow_hook;`
- re-export hook API if needed by `api.rs`

3) Wire call in `src-tauri/src/context_mapper/api.rs`:

- insert call after dependency resolution is finalized
- place before `SystemEnvelope::new(...)` (or equivalent envelope assembly)
- do not alter envelope return shape
- do not propagate hook errors

4) Dependencies:

- if live crate does not already include them, add:
  - `serde` with `derive`
  - `serde_json`

---

## Validation Checklist (mandatory)

1. Flag unset:

- passive hook must be skipped
- envelope output must match pre-hook behavior

2. Flag enabled + healthy emitter path:

- passive hook should emit records
- envelope output must remain unchanged

3. Flag enabled + forced emitter failure:

- warning logged
- envelope output still succeeds unchanged

4. Report all three runs with:

- command
- pass/fail
- key evidence lines

---

## Rollback

Immediate rollback:

- unset or set `AIMOS_SHADOW_BCI_PASSIVE_EMIT=false`

Code rollback:

- remove `shadow_hook.rs`
- remove single callsite in `api.rs`
- remove module export in `mod.rs`

---

## Merge Classification

- **Safe now**
  - this guide
  - reference implementation already in lab
- **Safe later**
  - live seam patch after explicit authorization
- **Not safe yet**
  - any behavior-affecting governance logic
