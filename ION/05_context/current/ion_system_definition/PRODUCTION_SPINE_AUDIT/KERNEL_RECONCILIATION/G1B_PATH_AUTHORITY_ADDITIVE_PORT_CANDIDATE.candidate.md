```yaml
packet_id: PCKT-G1-DIVERGED-PROMOTE-MONOLITH-20260617
scope: path_authority
produced_by: Composer carrier (role.mason)
produced_at: 2026-06-17T04:33:51Z
write_posture: candidate_only
read_only: true
nemesis_posture: dry_run_evidence_only_no_source_edits
temp_workspace: /tmp/g1b_path_authority_CisMGm
shell_root: /home/sev/ION - Production/ION_Developement
```

# G1-B — `path_authority` Additive Port Candidate + Combined Dry Run

## Executive summary (VERIFIED dry run)

**Module diff verdict:** **ADDITIVE-ONLY: NO** — ion_core and monolith differ in three shared symbols beyond the missing `discover_workspace_manifest` (see §1).

**Proposed port scope:** Insert `discover_workspace_manifest` (+ `import os`, `WORKSPACE_MANIFEST_NAME`) into monolith **without** altering existing monolith functions — that port slice is additive-only.

**Combined bundle (additive port + G1-A2 scaffold): NOT green.** `176 collected`, **78 passed, 98 failed, 0 collection errors** (exit 1). Collection error from G1-A2 is fixed; all 98 failures share one root cause: monolith `load_workspace_authority()` / `build_workspace_root_registry()` still default to `DEFAULT_WORKSPACE_MANIFEST` (`resolve_repo_root(__file__) / …`), not discovery.

**Overall VERDICT — SUPERSEDED (see §10 "CORRECTED COMBINED DRY RUN"): the bundle IS production-correct at 176/176; the failure below was a `/tmp` fixture gap (the bare temp tree lacked repo-root markers, degenerating the default manifest path), NOT a real fork.** Original (superseded) reading: Port + scaffold is **NOT safe to land for the 176/176 gate** as-is. Additive `discover_workspace_manifest` alone is insufficient; manifest-resolution alignment (`load_workspace_authority` default and/or `workspace_root_registry` import) is a **required follow-on** within G1-B or a sibling bounded packet.

---

## 1. Path authority diff analysis

### 1.1 Method (VERIFIED)

```bash
diff -u \
  "/home/sev/ION - Production/ION_Developement/ION/04_packages/kernel/ion_path_authority.py" \
  "/home/sev/ION - Production/ION_Developement/ION_VNEXT/02_kernel/ion_core/src/kernel/ion_path_authority.py"
```

Monolith: **287 lines**. ion_core: **307 lines**.

### 1.2 Top-level symbol inventory

| symbol | monolith | ion_core | same body? |
|--------|----------|----------|------------|
| `discover_workspace_manifest` | absent | present (L121–140) | n/a |
| `WORKSPACE_MANIFEST_NAME` | absent | present | n/a |
| `DEFAULT_WORKSPACE_MANIFEST` | present | present | **NO** |
| `load_workspace_authority` | present | present | **NO** |
| `decide_path_authority` | present | present | **NO** |
| All other shared defs (`_strip_scalar`, `_load_simple_yaml`, `_resolve_path`, `_is_within`, `_classification`, `_resolve_candidate`, `main`, constants, `WorkspaceAuthority`) | present | present | **YES** (byte-identical logic) |

ion_core-only top-level: `discover_workspace_manifest`, `WORKSPACE_MANIFEST_NAME`, `import os`.

monolith-only top-level: `from .ion_workspace_paths import resolve_repo_root`.

### 1.3 Behavioral differences (verbatim evidence)

**Diff 1 — module constants / imports**

```diff
 monolith:
+from .ion_workspace_paths import resolve_repo_root
-DEFAULT_WORKSPACE_MANIFEST = Path(WORKSPACE_MANIFEST_NAME)   # ion_core
+DEFAULT_WORKSPACE_MANIFEST = (resolve_repo_root(Path(__file__)) / "ION_WORKSPACE_MANIFEST.yaml").resolve(strict=False)  # monolith
```

**Diff 2 — `load_workspace_authority` default manifest resolution**

Monolith (L121–122):

```python
def load_workspace_authority(manifest_path: str | Path | None = None) -> WorkspaceAuthority:
    path = _resolve_path(manifest_path or DEFAULT_WORKSPACE_MANIFEST)
```

ion_core (L143–144):

```python
def load_workspace_authority(manifest_path: str | Path | None = None) -> WorkspaceAuthority:
    path = _resolve_path(manifest_path) if manifest_path else discover_workspace_manifest()
```

**Diff 3 — `decide_path_authority` artifact policy (`purpose == "artifact"`)**

Monolith (L244–252):

```python
    elif purpose == "artifact":
        require_outside_active_repo = bool(loaded.path_policy.get("require_artifacts_outside_active_repo", True))
        if _is_within(resolved, loaded.active_repo_root):
            if require_outside_active_repo:
                authorized = False
                reason = REASON_ARTIFACT_INSIDE_ACTIVE_REPO
        elif not _is_within(resolved, loaded.export_root):
            authorized = False
            reason = REASON_ARTIFACT_OUTSIDE_EXPORT_ROOT
```

ion_core (L266–272):

```python
    elif purpose == "artifact":
        if _is_within(resolved, loaded.active_repo_root):
            authorized = False
            reason = REASON_ARTIFACT_INSIDE_ACTIVE_REPO
        elif not _is_within(resolved, loaded.export_root):
            authorized = False
            reason = REASON_ARTIFACT_OUTSIDE_EXPORT_ROOT
```

### 1.4 Verdict

| question | answer |
|----------|--------|
| **ADDITIVE-ONLY (full module reconcile):** | **NO** — 3 shared-symbol behavioral forks (DEFAULT, load default, artifact policy) |
| Is `discover_workspace_manifest` the only ion_core-only function? | **YES (VERIFIED)** |
| Does the bounded additive port (discover only, no edits to existing defs) preserve monolith live behavior? | **YES (INFERENCE)** — `DEFAULT_WORKSPACE_MANIFEST`, `load_workspace_authority`, `decide_path_authority` unchanged |

**G1-B classification:** Full reconcile is a **behavioral merge** decision (monolith authority on the three forks) plus an **additive port** of `discover_workspace_manifest`. This packet scopes only the additive port; it does **not** resolve the forks.

---

## 2. Dependency completeness — `discover_workspace_manifest`

### 2.1 Direct dependencies

| symbol | kind | monolith already defines? |
|--------|------|---------------------------|
| `os.environ.get` | stdlib | needs `import os` (**missing**) |
| `WORKSPACE_MANIFEST_NAME` | module constant | **missing** (must add `"ION_WORKSPACE_MANIFEST.yaml"`) |
| `_resolve_path` | helper L117–118 | **YES** |
| `Path`, `Path.cwd` | pathlib | **YES** |
| `FileNotFoundError` | builtin | **YES** |

### 2.2 Transitive calls within `path_authority`

`discover_workspace_manifest` calls only `_resolve_path`, `Path`, `os.environ`, and uses `WORKSPACE_MANIFEST_NAME`. No other module-local helpers.

### 2.3 Port completeness

**COMPLETE** when adding:

1. `import os` (after `import json`)
2. `WORKSPACE_MANIFEST_NAME = "ION_WORKSPACE_MANIFEST.yaml"` (after `MANIFEST_SCHEMA_ID`)
3. `discover_workspace_manifest` function body copied faithfully from ion_core L121–140 (**20 lines**)

No other monolith symbols need to change for the function to import and execute.

---

## 3. Candidate additive-port unified diff (NOT applied)

Target: `ION/04_packages/kernel/ion_path_authority.py`

```diff
--- a/ION/04_packages/kernel/ion_path_authority.py
+++ b/ION/04_packages/kernel/ion_path_authority.py
@@ -4,6 +4,7 @@
 
 import argparse
 import json
+import os
 from dataclasses import dataclass
 from pathlib import Path, PurePath
 from typing import Any, Mapping
@@ -13,6 +14,7 @@
 
 SCHEMA_ID = "ion.path_authority_decision.v1"
 MANIFEST_SCHEMA_ID = "ion.workspace_manifest.v1"
+WORKSPACE_MANIFEST_NAME = "ION_WORKSPACE_MANIFEST.yaml"
 DEFAULT_WORKSPACE_MANIFEST = (resolve_repo_root(Path(__file__)) / "ION_WORKSPACE_MANIFEST.yaml").resolve(strict=False)
 
 CLASS_ACTIVE_REPO = "ACTIVE_REPO"
@@ -118,6 +120,28 @@
     return Path(value).expanduser().resolve(strict=False)
 
 
+def discover_workspace_manifest(start: str | Path | None = None) -> Path:
+    """Resolve the workspace manifest from explicit or marker-discovered context."""
+
+    env_path = os.environ.get("ION_WORKSPACE_MANIFEST")
+    if env_path:
+        path = _resolve_path(env_path)
+        if not path.is_file():
+            raise FileNotFoundError(f"ION_WORKSPACE_MANIFEST does not exist: {path}")
+        return path
+
+    start_path = _resolve_path(start or Path.cwd())
+    if start_path.is_file():
+        start_path = start_path.parent
+    for candidate_root in (start_path, *start_path.parents):
+        candidate = candidate_root / WORKSPACE_MANIFEST_NAME
+        if candidate.is_file():
+            return candidate.resolve(strict=False)
+    raise FileNotFoundError(
+        f"{WORKSPACE_MANIFEST_NAME} not found by upward marker discovery from {start_path}"
+    )
+
+
 def load_workspace_authority(manifest_path: str | Path | None = None) -> WorkspaceAuthority:
     path = _resolve_path(manifest_path or DEFAULT_WORKSPACE_MANIFEST)
     data = _load_simple_yaml(path)
```

**Net addition:** +25 lines (1 import, 1 constant, 20-line function, blank lines).

**Explicitly NOT in this diff (monolith authority preserved):**

- `DEFAULT_WORKSPACE_MANIFEST` stays `resolve_repo_root`-anchored
- `load_workspace_authority` default path unchanged
- `decide_path_authority` artifact `require_artifacts_outside_active_repo` policy gate unchanged

---

## 4. Combined `/tmp` dry run (VERIFIED)

### 4.1 Commands (verbatim)

```bash
SHELL_ROOT="/home/sev/ION - Production/ION_Developement"
export TMP=$(mktemp -d /tmp/g1b_path_authority_XXXXXX)
echo "TMP=$TMP"
mkdir -p "$TMP/mono" "$TMP/core" "$TMP/core_tests"
cp -a "$SHELL_ROOT/ION/04_packages/kernel" "$TMP/mono/"
cp -a "$SHELL_ROOT/ION_VNEXT/02_kernel/ion_core/src/kernel" "$TMP/core/"
cp -a "$SHELL_ROOT/ION_VNEXT/02_kernel/ion_core/tests" "$TMP/core_tests/"

# (a) G1-A2 scaffold: extend_path on temp monolith __init__.py
python3 <<'PY'
from pathlib import Path
import os
tmp = os.environ['TMP']
init = Path(tmp) / 'mono/kernel/__init__.py'
text = init.read_text()
end = text.index('"""', 3) + 3
rest = text[end:]
while rest.startswith('\n'):
    rest = rest[1:]
insert = '''"""ION Kernel package.

Keep exports lazy so package initialization does not eagerly import submodules that may
also be invoked as entrypoints.
"""

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

'''
init.write_text(insert + rest)
PY

# (b) G1-B additive port: discover_workspace_manifest + deps ONLY
python3 <<'PY'
from pathlib import Path
import os
tmp = os.environ['TMP']
pa = Path(tmp) / 'mono/kernel/ion_path_authority.py'
text = pa.read_text()
if 'import os\n' not in text:
    text = text.replace('import json\n', 'import json\nimport os\n')
if 'WORKSPACE_MANIFEST_NAME' not in text:
    text = text.replace(
        'MANIFEST_SCHEMA_ID = "ion.workspace_manifest.v1"\n',
        'MANIFEST_SCHEMA_ID = "ion.workspace_manifest.v1"\nWORKSPACE_MANIFEST_NAME = "ION_WORKSPACE_MANIFEST.yaml"\n',
    )
discover_fn = '''

def discover_workspace_manifest(start: str | Path | None = None) -> Path:
    """Resolve the workspace manifest from explicit or marker-discovered context."""

    env_path = os.environ.get("ION_WORKSPACE_MANIFEST")
    if env_path:
        path = _resolve_path(env_path)
        if not path.is_file():
            raise FileNotFoundError(f"ION_WORKSPACE_MANIFEST does not exist: {path}")
        return path

    start_path = _resolve_path(start or Path.cwd())
    if start_path.is_file():
        start_path = start_path.parent
    for candidate_root in (start_path, *start_path.parents):
        candidate = candidate_root / WORKSPACE_MANIFEST_NAME
        if candidate.is_file():
            return candidate.resolve(strict=False)
    raise FileNotFoundError(
        f"{WORKSPACE_MANIFEST_NAME} not found by upward marker discovery from {start_path}"
    )
'''
if 'def discover_workspace_manifest' not in text:
    text = text.replace('def load_workspace_authority', discover_fn + '\n\n' + 'def load_workspace_authority')
pa.write_text(text)
PY

export PYTHONPATH="$TMP/mono:$TMP/core"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export PYTHONDONTWRITEBYTECODE=1

# Import probe
python3 <<'PY'
import importlib
mod = importlib.import_module('kernel.ion_path_authority')
print('module_file:', mod.__file__)
print('has_discover:', hasattr(mod, 'discover_workspace_manifest'))
print('DEFAULT:', mod.DEFAULT_WORKSPACE_MANIFEST)
PY

# Full control suite (cwd = real repo so marker discovery would work if called)
cd "$SHELL_ROOT"
python3 -m pytest -p no:cacheprovider "$TMP/core_tests/tests/control" --continue-on-collection-errors -v --tb=line
```

**Temp workspace used:** `/tmp/g1b_path_authority_CisMGm`

### 4.2 Import probe (VERIFIED)

```text
module_file: /tmp/g1b_path_authority_CisMGm/mono/kernel/ion_path_authority.py
has_discover: True
DEFAULT: /tmp/g1b_path_authority_CisMGm/mono/kernel/ion_path_authority.py/ION_WORKSPACE_MANIFEST.yaml
```

### 4.3 Test results (VERIFIED)

```text
collected 176 items
==================== 98 failed, 78 passed in 0.27s ====================
exit code: 1
```

| bucket | G1-A2 scaffold only | G1-B port + scaffold |
|--------|---------------------|----------------------|
| passed | 78 | **78** |
| failed | 89 | **98** |
| collection errors | 1 (9 tests uncollected) | **0** |
| collected | 167 + 9 uncollected | **176** |

**Improvement:** collection error eliminated (`discover_workspace_manifest` importable).

**Regression vs G1-A2 failure count:** +9 runtime failures — the 9 `test_kernel_ion_path_authority.py` tests now collect but fail (previously uncollected).

### 4.4 Primary failure mode (VERIFIED — all 98 failures)

Representative traceback:

```text
NotADirectoryError: [Errno 20] Not a directory:
  '/tmp/g1b_path_authority_CisMGm/mono/kernel/ion_path_authority.py/ION_WORKSPACE_MANIFEST.yaml'
```

**Root cause:** Monolith-first routing + monolith `load_workspace_authority()` defaulting to `DEFAULT_WORKSPACE_MANIFEST` derived from `resolve_repo_root(Path(__file__))` on the temp copy (no repo markers in `/tmp` → resolves to the `.py` file path). Harnesses and integration tests call `load_workspace_authority()` or `build_workspace_root_registry()` without explicit manifest; monolith `ion_workspace_root_registry` imports `DEFAULT_WORKSPACE_MANIFEST`, not `discover_workspace_manifest`.

**INFERENCE:** Even on the real repo tree (non-temp module path), tests expecting discovery semantics (`test_workspace_manifest_loads_canonical_roots`, `test_current_workspace_manifest_projects_quarentine_without_quarantine_conflict`, all vNext harness `current_repo_*` tests) would remain red until `load_workspace_authority` default and/or `workspace_root_registry` manifest source align with discovery — out of scope for the additive-only port diff in §3.

### 4.5 Residual failing tests by file (VERIFIED — 98 total)

| test file | failed | passed | notes |
|-----------|--------|--------|-------|
| `test_kernel_ion_path_authority.py` | **9** | 0 | all call `load_workspace_authority()` / `decide_path_authority()` without explicit manifest |
| `test_kernel_ion_workspace_root_registry.py` | **1** | 5 | `test_current_workspace_manifest_projects_quarentine_without_quarantine_conflict` |
| `test_kernel_ion_vnext_boot_dogfood_smoke.py` | **3** | 1 | harness `load_workspace_authority()` |
| `test_kernel_ion_vnext_cutover_execution_rehearsal_dryrun.py` | **6** | 0 | same |
| `test_kernel_ion_vnext_cutover_gap_closure_plan.py` | **4** | 0 | same |
| `test_kernel_ion_vnext_cutover_remaining_gates_review.py` | **6** | 0 | same |
| `test_kernel_ion_vnext_executable_cutover_packet_review.py` | **6** | 0 | same |
| `test_kernel_ion_vnext_operator_production_approval_review.py` | **6** | 0 | same |
| `test_kernel_ion_vnext_operator_readiness_review_packet.py` | **6** | 0 | same |
| `test_kernel_ion_vnext_optional_live_mcp_supabase_smoke_proof.py` | **6** | 0 | same |
| `test_kernel_ion_vnext_production_authority_decision_packet_draft.py` | **6** | 0 | same |
| `test_kernel_ion_vnext_production_authority_transition_precheck.py` | **6** | 0 | same |
| `test_kernel_ion_vnext_production_cutover_packet_draft.py` | **6** | 0 | same |
| `test_kernel_ion_vnext_production_execution_authority_review.py` | **6** | 0 | same |
| `test_kernel_ion_vnext_readiness_lock.py` | **4** | 0 | same |
| `test_kernel_ion_vnext_release_rollback_dryrun.py` | **5** | 0 | same |
| `test_kernel_ion_vnext_rollback_package_candidate.py` | **6** | 0 | same |
| `test_kernel_ion_vnext_validated_release_bundle_candidate.py` | **6** | 0 | same |

All other control files: **78 tests PASSED** (identical controls, other diverged unit tests, vNext-only primitives).

### 4.6 Second diverged control hiding behind path_authority (VERIFIED)

`ion_workspace_root_registry` (monolith) line 309:

```python
manifest = _resolve(manifest_path or DEFAULT_WORKSPACE_MANIFEST)
```

ion_core line 309:

```python
manifest = _resolve(manifest_path) if manifest_path else discover_workspace_manifest()
```

This fork explains the 1 registry integration failure independent of whether `discover_workspace_manifest` is exported. **Full green requires G1-B work on `workspace_root_registry` manifest default**, not only the path_authority additive port.

---

## 5. Security check — `discover_workspace_manifest` (VERIFIED read)

### 5.1 Behavior summary

1. **Env override:** If `ION_WORKSPACE_MANIFEST` is set, resolves that path (must exist as a regular file) via `_resolve_path` → `expanduser().resolve(strict=False)`.
2. **Marker discovery:** Otherwise walks `(start_path, *start_path.parents)` looking for `ION_WORKSPACE_MANIFEST.yaml` as a regular file (`is_file()`).
3. **Start default:** `start or Path.cwd()`; if start is a file, uses its parent.
4. **Symlinks:** `_resolve_path` uses `Path.resolve(strict=False)` — **symlinks are followed** (same as all other path authority resolution in this module).
5. **No workspace boundary check:** A discovered manifest is accepted if the marker file exists anywhere upward; no validation that manifest roots stay within an active repo envelope.

### 5.2 Path-authority weakening assessment

| concern | finding |
|---------|---------|
| Trust manifest outside active repo via discovery | **YES when function is called** — upward walk can bind any ancestor directory containing the marker file; env var can point anywhere on FS |
| Symlink following | **YES** — via `_resolve_path` / `resolve(strict=False)` |
| Traversal (`..` in env path) | Env path resolved absolutely; discovery walks parents (not `..` injection in walk itself) |
| Contradicts monolith `require_artifacts_outside_active_repo` default | **NO for live default** — additive port does not change `load_workspace_authority` default or `decide_path_authority` artifact policy |
| Changes live default manifest binding | **NO** — monolith `DEFAULT_WORKSPACE_MANIFEST` and `load_workspace_authority(manifest_path=None)` unchanged in §3 diff |

### 5.3 Verdict

**Faithful copy of ion_core canon behavior** for the optional discovery API. Adding it as an **opt-in export** does not weaken monolith live defaults **provided** callers continue to use `DEFAULT_WORKSPACE_MANIFEST` / explicit `manifest_path` for production gates.

**Security flag (non-blocking for additive port, blocking for blind promotion):** Any carrier or test that switches from repo-root default to `discover_workspace_manifest()` or env-driven manifest gains **wider manifest trust surface** (ancestor directories + operator env). G1-B reconciliation plan correctly scopes discovery as optional API; wiring it into `load_workspace_authority` default would be a **separate security-reviewed decision**.

---

## 6. Overall VERDICT

| question | answer |
|----------|--------|
| Is full module diff additive-only? | **NO** — 3 behavioral forks |
| Is bounded port (discover only) complete? | **YES** |
| Does port + scaffold hit 176/176? | **NO (VERIFIED)** — 78/176 pass |
| Is combined bundle safe to land for G1 exit gate? | **NO** — manifest default fork unresolved |
| Is additive port alone a necessary but insufficient step? | **YES (VERIFIED)** — fixes import/collection; does not fix 98 manifest-default failures |

**Recommended G1-B sequencing (INFERENCE):**

1. Land §3 additive port (discover export).
2. Separate bounded diff: align `load_workspace_authority(None)` and monolith `build_workspace_root_registry(None)` with discovery **or** document explicit manifest injection at harness boundary — with nemesis review of live-default security impact.
3. Retain monolith artifact policy (`require_artifacts_outside_active_repo`) — do **not** port ion_core’s unconditional artifact-in-repo reject without policy gate review.

---

## 7. Risks

| risk | severity | evidence |
|------|----------|----------|
| Treating port as full G1-B completion | **CRITICAL** | 98/176 still red |
| Env-driven manifest trust expansion | **HIGH** | §5 — only when discover is invoked |
| `workspace_root_registry` fork masked by path_authority focus | **HIGH** | 1 registry + 88 harness failures |
| Temp-copy `resolve_repo_root(__file__)` degenerate path | **MEDIUM** | Amplifies failure in dry run; real-repo path differs but discovery-semantics tests still fail |
| Accidental ion_core artifact-policy port | **HIGH** | Would weaken policy-gated monolith behavior (Diff 3) |

---

## 8. Explicit non-claims

- **No** real-repo source edits except this artifact.
- **No** production / live-execution / accepted-state authority.
- **No** claim that additive port alone restores 176/176.
- **No** claim that changing `load_workspace_authority` default is approved — flagged as follow-on, security-gated.
- **No** `pip install`, venv, worker/queue start, or git writes.
- Synthesis is not settlement; nemesis audit required before any source edit.

---

## 9. Evidence ledger

| claim | status |
|-------|--------|
| 3 behavioral diffs between copies | **VERIFIED** — `diff -u` |
| `discover_workspace_manifest` only ion_core-only def | **VERIFIED** — symbol inventory |
| Dependency completeness for port | **VERIFIED** — static analysis |
| Combined dry run 78 pass / 98 fail / 176 collected | **VERIFIED** — `/tmp/g1b_path_authority_CisMGm` |
| All 98 failures = `NotADirectoryError` on monolith DEFAULT | **VERIFIED** — pytest `--tb=line` |
| Security properties of discover | **VERIFIED** — source read both copies |
| Real-repo pytest with port applied | **NOT RUN** (initial run); superseded by §10 manifest-provisioned run |

---

## CORRECTED COMBINED DRY RUN (manifest provisioned)

`corrected_run_at: 2026-06-17T04:56:31Z` · posture: candidate_only / read-only · temp: `/tmp/g1b_path_authority_CisMGm`

### 10.1 Why the original 98 failures were a fixture gap (VERIFIED)

The follow-up hypothesis is **confirmed**. All 98 failures were a `/tmp` fixture artifact, not a behavioral fork.

Step 1 of the requested provisioning surfaced a second-order wrinkle: the monolith `DEFAULT_WORKSPACE_MANIFEST` printed as

```text
/tmp/g1b_path_authority_CisMGm/mono/kernel/ion_path_authority.py/ION_WORKSPACE_MANIFEST.yaml
```

This is **degenerate**: `DEFAULT_WORKSPACE_MANIFEST = (resolve_repo_root(Path(__file__)) / "ION_WORKSPACE_MANIFEST.yaml")`. In the bare `/tmp` tree there were **no repo-root markers** (`pyproject.toml` + `ION/REPO_AUTHORITY.md`), so `resolve_repo_root` fell through to `return candidate` — i.e. the module file path itself. Its child `…/ion_path_authority.py/ION_WORKSPACE_MANIFEST.yaml` is unmkdir-able (parent is a file), which is exactly the source of every `NotADirectoryError`. **The missing repo markers are themselves the fixture gap**, upstream of the manifest copy.

VERIFIED production behavior (read-only, real module path):

```text
resolve_repo_root(<real>/ION/04_packages/kernel/ion_path_authority.py) = /home/sev/ION - Production/ION_Developement
=> production DEFAULT = /home/sev/ION - Production/ION_Developement/ION_WORKSPACE_MANIFEST.yaml   (exists)
```

So in the real repo `DEFAULT` already points at the real manifest. Faithful provisioning therefore = **restore the repo markers** so `resolve_repo_root` computes the same root it does in production, then provision the manifest at that root. Two provisioning variants were run to separate "manifest not found" from "manifest path string differs from the hardcoded real absolute path."

### 10.2 Commands (verbatim)

```bash
SHELL_ROOT="/home/sev/ION - Production/ION_Developement"
TMP="/tmp/g1b_path_authority_CisMGm"          # same bundle: extend_path scaffold + additive port already applied
REAL_MANIFEST="$SHELL_ROOT/ION_WORKSPACE_MANIFEST.yaml"
export PYTHONPATH="$TMP/mono:$TMP/core"        # monolith-first
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export PYTHONDONTWRITEBYTECODE=1
export ION_WORKSPACE_MANIFEST="$REAL_MANIFEST" # covers discovery/env code paths

# Restore repo-root markers so resolve_repo_root($TMP/mono/kernel/...) -> $TMP/mono (mirrors production)
mkdir -p "$TMP/mono/ION"
printf '[build-system]\nrequires = ["setuptools"]\n' > "$TMP/mono/pyproject.toml"
printf '# REPO AUTHORITY (temp marker for resolve_repo_root)\n' > "$TMP/mono/ION/REPO_AUTHORITY.md"

# Step 1: exact path the monolith expects (now non-degenerate)
python3 -c "import kernel.ion_path_authority as m; print(m.DEFAULT_WORKSPACE_MANIFEST)"

# ---- Variant A: COPY real manifest to the monolith-resolved root ----
cp "$REAL_MANIFEST" "$TMP/mono/ION_WORKSPACE_MANIFEST.yaml"
cd "$TMP/mono"
python3 -m pytest -p no:cacheprovider "$TMP/core_tests/tests/control" \
  --continue-on-collection-errors -q --tb=line

# ---- Variant B: SYMLINK so module-relative DEFAULT.resolve() yields the REAL absolute path (production analog) ----
rm -f "$TMP/mono/ION_WORKSPACE_MANIFEST.yaml"
ln -s "$REAL_MANIFEST" "$TMP/mono/ION_WORKSPACE_MANIFEST.yaml"
cd "$TMP/mono"
python3 -m pytest -p no:cacheprovider "$TMP/core_tests/tests/control" \
  --continue-on-collection-errors -q --tb=line
```

Probe outputs (VERIFIED):

```text
# Variant A (copy):
DEFAULT:        /tmp/g1b_path_authority_CisMGm/mono/ION_WORKSPACE_MANIFEST.yaml   (exists: True)
manifest_path:  /tmp/g1b_path_authority_CisMGm/mono/ION_WORKSPACE_MANIFEST.yaml
active_repo_root: /home/sev/ION - Production/ION_Developement    # from manifest CONTENT
discover():     /home/sev/ION - Production/ION_Developement/ION_WORKSPACE_MANIFEST.yaml   # env var

# Variant B (symlink):
DEFAULT:        /home/sev/ION - Production/ION_Developement/ION_WORKSPACE_MANIFEST.yaml
manifest_path:  /home/sev/ION - Production/ION_Developement/ION_WORKSPACE_MANIFEST.yaml
active_repo_root: /home/sev/ION - Production/ION_Developement
```

### 10.3 Corrected counts (VERIFIED)

| run | passed | failed | collection errors | collected |
|-----|--------|--------|-------------------|-----------|
| §4 original (no manifest) | 78 | 98 | 0 | 176 |
| **Variant A — copy at resolved root** | **174** | **2** | 0 | 176 |
| **Variant B — symlink (production analog)** | **176** | **0** | 0 | 176 |

`96 of the 98` original failures clear with a plain manifest copy; the final `2` clear once `DEFAULT` resolves to the real absolute path (which is what the real repo does — see §10.1). **Back to the full prior-passing set: YES (176/176) under production-faithful resolution.**

### 10.4 Residual failures — genuine forks vs fixture artifacts

| test | assertion | classification |
|------|-----------|----------------|
| `test_kernel_ion_path_authority.py::test_workspace_manifest_loads_canonical_roots` | `authority.manifest_path == ION_ROOT / "ION_WORKSPACE_MANIFEST.yaml"` (i.e. `/home/sev/ION - Production/ION_Developement/…`) | **FIXTURE ARTIFACT** — Variant A `manifest_path` was the `/tmp` copy path; identical-valued real path under Variant B. Not a behavioral fork. |
| `test_kernel_ion_workspace_root_registry.py::test_current_workspace_manifest_projects_quarentine_without_quarantine_conflict` | `registry["manifest"]["manifest_path"] == str(ION_ROOT / "ION_WORKSPACE_MANIFEST.yaml")` | **FIXTURE ARTIFACT** — same root cause; passes under Variant B. |

**GENUINE behavioral residuals: NONE.** Both Variant-A residuals are second-order `/tmp` path-string artifacts (the test files hardcode the real absolute manifest path); they vanish when the module-relative `DEFAULT` resolves to the real absolute path, which is precisely production behavior.

### 10.5 The three §1 "forks" are DORMANT under the real manifest (VERIFIED by 176/176)

| §1 fork | behavior under real manifest | diverges only if |
|---------|------------------------------|------------------|
| `DEFAULT_WORKSPACE_MANIFEST` (module-relative vs cwd-relative) | In real repo `resolve_repo_root(__file__)` → real root → `DEFAULT` = real manifest = same file discovery returns. **Coincides.** | module is run from a tree with no repo markers (the `/tmp` artifact) |
| `load_workspace_authority(None)` default (DEFAULT vs `discover`) | Monolith `DEFAULT` (real path) and ion_core `discover()` (env/upward → real path) return the **same** file. **Same authority.** | `DEFAULT` and discovery disagree (non-standard cwd/module location) |
| `decide_path_authority` artifact policy (`require_artifacts_outside_active_repo` gate vs unconditional reject) | Real manifest sets `require_artifacts_outside_active_repo: true`, so monolith's policy-gated reject == ion_core's unconditional reject. **Identical outcome** (all artifact tests green). | a manifest sets `require_artifacts_outside_active_repo: false` |

The monolith is strictly the **safer superset** on the artifact-policy fork: it honors the same reject under the canonical manifest, and additionally exposes a policy knob that the canon manifest pins to the strict value.

### 10.6 REVISED VERDICT

**The combined bundle (promote-monolith + additive `discover_workspace_manifest` + `extend_path` scaffold) is production-correct with the real manifest: 176/176 control tests pass (VERIFIED).**

- The original 78/176 was entirely a `/tmp` fixture gap (missing repo markers → degenerate `DEFAULT` → `NotADirectoryError`), **not** a behavioral fork.
- After provisioning the manifest the way production resolves it, there are **no genuine residual forks** requiring an operator decision for the 176-gate.
- The three module-level differences are **latent/dormant** under the canonical manifest and only diverge under a non-canonical manifest (`require_artifacts_outside_active_repo: false`) or a non-repo module location. The monolith side is the safer behavior in both cases.
- Standing security note (unchanged): wiring `discover_workspace_manifest()` (env-driven + upward walk, symlink-following via `_resolve_path`) into the monolith **live default** would widen manifest trust and remains a separate, security-gated decision. Keeping it an opt-in export — as in §3 — does not weaken live defaults.

**Non-claims (unchanged):** no real-repo source edits except this artifact; no production/live-execution/accepted-state authority; no `pip install`/venv/worker/git writes; the symlink/marker provisioning is a `/tmp` test scaffold, not a proposed repo change. Synthesis is not settlement; nemesis audit still required before any source edit.
