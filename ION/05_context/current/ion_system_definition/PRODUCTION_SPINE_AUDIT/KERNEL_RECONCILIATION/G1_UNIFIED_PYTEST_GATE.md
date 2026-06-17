# G1 — Unified Kernel Pytest Gate (documented exit test)

```
schema_id:  ion.production_spine.g1_unified_pytest_gate.v0_1_candidate
packet:     PCKT-G1-IDENTICAL-UNIFY-NAMESPACE-MERGE-SCAFFOLD-20260617 (+ path_authority additive port)
status:     foundation APPLIED to working tree (uncommitted); verified 176/176 in the real repo
posture:    candidate_only
```

## What this gate proves

That the two `kernel` trees are reconciled into one coherent namespace: every shared control resolves to the **monolith** (authoritative), the 16 `ion_vnext_*` harnesses resolve to `ion_core` via `pkgutil.extend_path`, and `ion_core`'s full control suite passes against that merged namespace.

## The command (run from the active repo root)

```bash
cd "/home/sev/ION - Production/ION_Developement"
PYTHONPATH="ION/04_packages:ION_VNEXT/02_kernel/ion_core/src" \
  python -m pytest ION_VNEXT/02_kernel/ion_core/tests/control -q
```

**Expected:** `176 passed` (29 control modules). Monolith dir is first on `PYTHONPATH`, so shared true-names resolve to the monolith; `extend_path` in `kernel/__init__.py` adds `ion_core`'s dir so `kernel.ion_vnext_*` resolves to `ion_core`.

## What was applied (working tree; additive; +28 / -0)

- `ION/04_packages/kernel/__init__.py` (+4): `from pkgutil import extend_path` / `__path__ = extend_path(__path__, __name__)`.
- `ION/04_packages/kernel/ion_path_authority.py` (+24): `import os`, `WORKSPACE_MANIFEST_NAME`, and the additive `discover_workspace_manifest()` function. No existing functions changed.

## Zero live-runtime impact (verified)

With only the monolith on the path (the live runtime today), `kernel.__path__` stays monolith-only — `extend_path` is a no-op until `ion_core/src` is added to the runtime path. `discover_workspace_manifest` is opt-in (the live default still uses `DEFAULT_WORKSPACE_MANIFEST`).

## Deferred (separate gates)

- **Runtime binding:** add `ion_core/src` to the live Codex-mount `PYTHONPATH` (and/or the root pytest `pythonpath`) to make the merged namespace real in the runtime — the actual cutover; security-review the exposure of the 16 harnesses.
- **G1-A3 collapse:** remove the 3 byte-identical duplicate modules from `ion_core` (behavior-neutral by sha256 proof).
- **Commit:** the working-tree changes are uncommitted, pending operator go.
