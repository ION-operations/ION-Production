```yaml
packet_id: PCKT-G1-IDENTICAL-UNIFY-NAMESPACE-MERGE-SCAFFOLD-20260617
produced_by: Composer carrier (role.mason)
produced_at: 2026-06-17T04:28:57Z
write_posture: candidate_only
read_only: true
nemesis_posture: dry_run_evidence_only_no_source_edits
temp_workspace: /tmp/g1a2_namespace_scaffold_UIk1Oe
shell_root: /home/sev/ION - Production/ION_Developement
```

# G1-A2 — Namespace Scaffold Candidate Diff + Temp-Dir Dry Run

## Executive summary (VERIFIED dry run)

**Import-resolution mechanism works:** with `pkgutil.extend_path` patched into monolith `kernel/__init__.py` and `PYTHONPATH=$TMP/mono:$TMP/core` (monolith first), all 9 shared controls resolve to monolith; all sampled `ion_vnext_*` harnesses resolve to `ion_core`; monolith-only modules remain on monolith.

**176-suite gate: FAIL.** Under the scaffold, `ion_core/tests/control` yields **78 passed, 89 failed, 1 collection error** (167 collected + 9 uncollected from `test_kernel_ion_path_authority.py` = 176 baseline). **NOT green.**

**Verdict:** The namespace scaffold is **not safe to land as-is** for the stated G1-A exit gate (“176 control tests green”). It is **coupled to G1-B** (diverged reconcile), at minimum porting `discover_workspace_manifest()` into monolith `ion_path_authority` and aligning default manifest resolution so harnesses that call `load_workspace_authority()` without an explicit manifest can find `ION_WORKSPACE_MANIFEST.yaml`.

---

## 1. Proposed unified diffs (NOT applied)

### 1.1 `ION/04_packages/kernel/__init__.py`

Insert immediately after the module docstring, before existing imports:

```diff
--- a/ION/04_packages/kernel/__init__.py
+++ b/ION/04_packages/kernel/__init__.py
@@ -4,6 +4,10 @@
 also be invoked as entrypoints.
 """
 
+from pkgutil import extend_path
+
+__path__ = extend_path(__path__, __name__)
+
 from importlib import import_module
 from typing import Any
```

**Exact lines added (2 functional lines):**

```python
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
```

### 1.2 Unified PYTHONPATH (monolith first)

**Proposed runtime value (relative to shell root):**

```text
PYTHONPATH="ION/04_packages:ION_VNEXT/02_kernel/ion_core/src"
```

**Absolute (this machine):**

```text
PYTHONPATH="/home/sev/ION - Production/ION_Developement/ION/04_packages:/home/sev/ION - Production/ION_Developement/ION_VNEXT/02_kernel/ion_core/src"
```

### 1.3 Root `pyproject.toml` — `[tool.pytest.ini_options]`

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -16,4 +16,4 @@
 
 [tool.pytest.ini_options]
 testpaths = ["ION/tests"]
-pythonpath = ["ION/04_packages"]
+pythonpath = ["ION/04_packages", "ION_VNEXT/02_kernel/ion_core/src"]
```

### 1.4 `ION_VNEXT/02_kernel/ion_core/pyproject.toml` — control-test pythonpath

```diff
--- a/ION_VNEXT/02_kernel/ion_core/pyproject.toml
+++ b/ION_VNEXT/02_kernel/ion_core/pyproject.toml
@@ -16,4 +16,4 @@
 
 [tool.pytest.ini_options]
 testpaths = ["tests/control"]
-pythonpath = ["src"]
+pythonpath = ["../../ION/04_packages", "src"]
 addopts = "-q"
```

(Path `../../ION/04_packages` is relative to `ion_core/` directory.)

### 1.5 Codex mount `PYTHONPATH` (representative; all mounts today use monolith-only)

Example: `ION/05_context/current/codex_agent_mounts/role_mason__domain_construction_routing_integration/.codex/config.toml`

```diff
--- a/.codex/config.toml
+++ b/.codex/config.toml
@@ -40,4 +40,4 @@
 startup_timeout_sec = 10
 tool_timeout_sec = 60
 enabled_tools = ["ion.status", "ion.boot_packet", "ion.horizon.current", "ion.receipts.list", "ion.tools.list"]
-env = { PYTHONPATH = "/home/sev/ION - Production/ION_Developement/ION/04_packages", PYTHONDONTWRITEBYTECODE = "1" }
+env = { PYTHONPATH = "/home/sev/ION - Production/ION_Developement/ION/04_packages:/home/sev/ION - Production/ION_Developement/ION_VNEXT/02_kernel/ion_core/src", PYTHONDONTWRITEBYTECODE = "1" }
```

**INFERENCE:** Per reconciliation plan §1, default Codex mounts may stay monolith-only until a cutover packet requires live `kernel.ion_vnext_*` CLI invocation. The diff above documents the unified path when harness access is needed.

---

## 2. Temp-dir dry run — commands (verbatim)

```bash
SHELL_ROOT="/home/sev/ION - Production/ION_Developement"
export TMP=$(mktemp -d /tmp/g1a2_namespace_scaffold_XXXXXX)
echo "TMP=$TMP"
mkdir -p "$TMP/mono" "$TMP/core"
cp -a "$SHELL_ROOT/ION/04_packages/kernel" "$TMP/mono/"
cp -a "$SHELL_ROOT/ION_VNEXT/02_kernel/ion_core/src/kernel" "$TMP/core/"
cp -a "$SHELL_ROOT/ION_VNEXT/02_kernel/ion_core/tests" "$TMP/core_tests/"

# Patch ONLY temp monolith __init__.py (extend_path after docstring)
python3 <<PY
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

export PYTHONPATH="$TMP/mono:$TMP/core"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export PYTHONDONTWRITEBYTECODE=1

# Import-resolution probe
python3 <<'PY'
import importlib, sys
def probe(name):
    if name in sys.modules:
        del sys.modules[name]
    mod = importlib.import_module(name)
    path = mod.__file__ or ''
    src = 'mono' if '/mono/' in path.replace('\\','/') else ('core' if '/core/' in path.replace('\\','/') else 'other')
    print(f"{name}\t{path}\t{src}")
shared = [
    'kernel.ion_ai_movement_gate','kernel.ion_codex_work_request_target_binding',
    'kernel.ion_template_action_gate','kernel.ion_path_authority',
    'kernel.ion_context_proof_gate','kernel.ion_agent_cwd_boundary',
    'kernel.ion_workspace_root_registry','kernel.ion_operator_artifact_hygiene_check',
    'kernel.ion_carrier_mount_receipt',
]
for m in shared: probe(m)
for m in ['kernel.ion_vnext_readiness_lock','kernel.ion_vnext_boot_dogfood_smoke',
          'kernel.ion_vnext_cutover_gap_closure_plan','kernel.ion_vnext_release_rollback_dryrun']:
    probe(m)
for m in ['kernel.ion_codex_queue_runner','kernel.sequential_kernel','kernel.operator_cli']:
    probe(m)
import kernel
print('kernel.__path__', list(kernel.__path__))
PY

# Control test suite (continue past collection errors)
cd "$TMP"
python3 -m pytest -p no:cacheprovider core_tests/control --continue-on-collection-errors -v --tb=line
```

**Temp workspace used:** `/tmp/g1a2_namespace_scaffold_UIk1Oe`

**Negative control (VERIFIED):** Without `extend_path`, `import kernel.ion_vnext_readiness_lock` raises `ModuleNotFoundError`; shared controls still import from monolith-only `PYTHONPATH`.

---

## 3. Import-resolution table (VERIFIED)

| module | resolved path | source |
|--------|---------------|--------|
| `kernel.ion_ai_movement_gate` | `.../mono/kernel/ion_ai_movement_gate.py` | **mono** |
| `kernel.ion_codex_work_request_target_binding` | `.../mono/kernel/ion_codex_work_request_target_binding.py` | **mono** |
| `kernel.ion_template_action_gate` | `.../mono/kernel/ion_template_action_gate.py` | **mono** |
| `kernel.ion_path_authority` | `.../mono/kernel/ion_path_authority.py` | **mono** |
| `kernel.ion_context_proof_gate` | `.../mono/kernel/ion_context_proof_gate.py` | **mono** |
| `kernel.ion_agent_cwd_boundary` | `.../mono/kernel/ion_agent_cwd_boundary.py` | **mono** |
| `kernel.ion_workspace_root_registry` | `.../mono/kernel/ion_workspace_root_registry.py` | **mono** |
| `kernel.ion_operator_artifact_hygiene_check` | `.../mono/kernel/ion_operator_artifact_hygiene_check.py` | **mono** |
| `kernel.ion_carrier_mount_receipt` | `.../mono/kernel/ion_carrier_mount_receipt.py` | **mono** |
| `kernel.ion_vnext_readiness_lock` | `.../core/kernel/ion_vnext_readiness_lock.py` | **core** |
| `kernel.ion_vnext_boot_dogfood_smoke` | `.../core/kernel/ion_vnext_boot_dogfood_smoke.py` | **core** |
| `kernel.ion_vnext_cutover_gap_closure_plan` | `.../core/kernel/ion_vnext_cutover_gap_closure_plan.py` | **core** |
| `kernel.ion_vnext_release_rollback_dryrun` | `.../core/kernel/ion_vnext_release_rollback_dryrun.py` | **core** |
| `kernel.ion_codex_queue_runner` | `.../mono/kernel/ion_codex_queue_runner.py` | **mono** |
| `kernel.sequential_kernel` | `.../mono/kernel/sequential_kernel.py` | **mono** |
| `kernel.operator_cli` | `.../mono/kernel/operator_cli.py` | **mono** |

`kernel.__path__` (VERIFIED): `['.../mono/kernel', '.../core/kernel']`

---

## 4. Test results (VERIFIED)

### 4.1 Baseline (ion_core-only PYTHONPATH, pre-scaffold)

```text
176 tests collected in 0.06s
```

(Run from `ION_VNEXT/02_kernel/ion_core` with `PYTHONPATH=src`.)

### 4.2 Under namespace scaffold (temp workspace)

```text
collected 167 items / 1 error
==================== 89 failed, 78 passed, 1 error in 0.26s ====================
exit code: 1
```

| bucket | count |
|--------|-------|
| passed | **78** |
| failed | **89** |
| collection errors | **1** (entire `test_kernel_ion_path_authority.py`; **9 tests** not collected) |
| **effective total** | **176** (78 + 89 + 9) |

### 4.3 Collection error (verbatim)

```text
ERROR collecting core_tests/control/test_kernel_ion_path_authority.py
ImportError while importing test module '.../core_tests/control/test_kernel_ion_path_authority.py'.
from kernel.ion_path_authority import (
E   ImportError: cannot import name 'discover_workspace_manifest' from 'kernel.ion_path_authority'
    (.../mono/kernel/ion_path_authority.py)
```

**Cause:** Monolith `ion_path_authority` has no `discover_workspace_manifest` export; ion_core test module imports it at collection time.

### 4.4 Diverged-control test files — per-file summary

| diverged control | tests | scaffold result |
|------------------|-------|-----------------|
| `ion_path_authority` | 9 | **COLLECTION ERROR** (missing API) |
| `ion_workspace_root_registry` | 6 | **5 passed, 1 failed** |
| `ion_agent_cwd_boundary` | 4 | **4 passed** |
| `ion_context_proof_gate` | 4 | **4 passed** |
| `ion_operator_artifact_hygiene_check` | 5 | **5 passed** |
| `ion_carrier_mount_receipt` | 11 | **11 passed** |

**Identical controls (3):** all unit tests **passed** (10 + 7 + 3 = 20 tests).

**vNext-only primitives (4):** all unit tests **passed** (receipt, context_package, source_pool, promotion_plan cores).

### 4.5 Primary failure mode for 89 runtime failures (VERIFIED)

Representative traceback (readiness lock harness):

```text
evaluate_vnext_readiness_lock → load_workspace_authority()
→ mono/kernel/ion_path_authority.py DEFAULT_WORKSPACE_MANIFEST
→ NotADirectoryError: '.../mono/kernel/ion_path_authority.py/ION_WORKSPACE_MANIFEST.yaml'
```

Monolith default: `resolve_repo_root(Path(__file__)) / "ION_WORKSPACE_MANIFEST.yaml"`.  
ion_core default: `discover_workspace_manifest()` (env + upward walk).

Harnesses and `test_current_workspace_manifest_*` tests expect ion_core manifest discovery semantics; monolith-first routing breaks them.

### 4.6 All 89 failed test names (verbatim)

```
core_tests/control/test_kernel_ion_vnext_boot_dogfood_smoke.py::test_current_repo_vnext_boot_dogfood_smoke_accepts_front_door_route
core_tests/control/test_kernel_ion_vnext_boot_dogfood_smoke.py::test_boot_smoke_path_gate_rejects_private_and_escape_probes
core_tests/control/test_kernel_ion_vnext_boot_dogfood_smoke.py::test_smoke_blocks_when_required_front_door_file_is_missing
core_tests/control/test_kernel_ion_vnext_cutover_execution_rehearsal_dryrun.py::test_current_repo_m100_creates_clean_operator_surface
core_tests/control/test_kernel_ion_vnext_cutover_execution_rehearsal_dryrun.py::test_m100_closes_only_rehearsal_gate_and_keeps_authority_false
core_tests/control/test_kernel_ion_vnext_cutover_execution_rehearsal_dryrun.py::test_m100_step_trace_and_hash_manifest_are_paired
core_tests/control/test_kernel_ion_vnext_cutover_execution_rehearsal_dryrun.py::test_m100_operator_text_preserves_dryrun_boundary
core_tests/control/test_kernel_ion_vnext_cutover_execution_rehearsal_dryrun.py::test_m100_blocks_when_m99_is_not_ready_or_claims_authority
core_tests/control/test_kernel_ion_vnext_cutover_execution_rehearsal_dryrun.py::test_m100_rejects_relative_parent_escape
core_tests/control/test_kernel_ion_vnext_cutover_gap_closure_plan.py::test_current_repo_gap_closure_plan_maps_all_m88_blockers_without_closing_them
core_tests/control/test_kernel_ion_vnext_cutover_gap_closure_plan.py::test_gap_closure_plan_keeps_live_smokes_optional_and_approval_gated
core_tests/control/test_kernel_ion_vnext_cutover_gap_closure_plan.py::test_gap_closure_plan_receipt_core_keeps_authority_false
core_tests/control/test_kernel_ion_vnext_cutover_gap_closure_plan.py::test_gap_closure_plan_blocks_if_m88_result_is_not_ready
core_tests/control/test_kernel_ion_vnext_cutover_remaining_gates_review.py::test_current_repo_m94_creates_clean_operator_surface
core_tests/control/test_kernel_ion_vnext_cutover_remaining_gates_review.py::test_m94_keeps_review_only_and_all_authority_false
core_tests/control/test_kernel_ion_vnext_cutover_remaining_gates_review.py::test_m94_preserves_remaining_gate_ledger_and_dependency_order
core_tests/control/test_kernel_ion_vnext_cutover_remaining_gates_review.py::test_m94_operator_text_is_review_only_and_selects_m95
core_tests/control/test_kernel_ion_vnext_cutover_remaining_gates_review.py::test_m94_blocks_when_m93_is_not_ready_or_claims_authority
core_tests/control/test_kernel_ion_vnext_cutover_remaining_gates_review.py::test_m94_rejects_relative_parent_escape
core_tests/control/test_kernel_ion_vnext_executable_cutover_packet_review.py::test_current_repo_m98_creates_clean_operator_surface
core_tests/control/test_kernel_ion_vnext_executable_cutover_packet_review.py::test_m98_keeps_execution_authority_false_and_closes_only_cutover_packet_gate
core_tests/control/test_kernel_ion_vnext_executable_cutover_packet_review.py::test_m98_cutover_candidate_and_hash_manifest_are_paired
core_tests/control/test_kernel_ion_vnext_executable_cutover_packet_review.py::test_m98_operator_text_uses_standing_mandate_without_execution_claim
core_tests/control/test_kernel_ion_vnext_executable_cutover_packet_review.py::test_m98_blocks_when_m96_or_m97b_is_not_ready
core_tests/control/test_kernel_ion_vnext_executable_cutover_packet_review.py::test_m98_rejects_relative_parent_escape
core_tests/control/test_kernel_ion_vnext_operator_production_approval_review.py::test_current_repo_m97_creates_clean_operator_surface
core_tests/control/test_kernel_ion_vnext_operator_production_approval_review.py::test_m97_requires_explicit_decision_without_recording_approval
core_tests/control/test_kernel_ion_vnext_operator_production_approval_review.py::test_m97_operator_text_rejects_proceed_as_approval
core_tests/control/test_kernel_ion_vnext_operator_production_approval_review.py::test_m97_blocks_when_m96_is_not_ready_or_claims_authority
core_tests/control/test_kernel_ion_vnext_operator_production_approval_review.py::test_m97_blocks_when_m96_remaining_gates_drift
core_tests/control/test_kernel_ion_vnext_operator_production_approval_review.py::test_m97_rejects_relative_parent_escape
core_tests/control/test_kernel_ion_vnext_operator_readiness_review_packet.py::test_current_repo_operator_readiness_review_creates_clean_operator_surface
core_tests/control/test_kernel_ion_vnext_operator_readiness_review_packet.py::test_operator_readiness_review_requires_explicit_decision_without_recording_approval
core_tests/control/test_kernel_ion_vnext_operator_readiness_review_packet.py::test_operator_readiness_review_text_limits_approval_to_m92_draft_only
core_tests/control/test_kernel_ion_vnext_operator_readiness_review_packet.py::test_operator_readiness_review_receipt_keeps_authority_false
core_tests/control/test_kernel_ion_vnext_operator_readiness_review_packet.py::test_operator_readiness_review_blocks_when_m90_not_ready
core_tests/control/test_kernel_ion_vnext_operator_readiness_review_packet.py::test_operator_readiness_review_rejects_relative_parent_escape
core_tests/control/test_kernel_ion_vnext_optional_live_mcp_supabase_smoke_proof.py::test_current_repo_m93_with_fake_mcp_probe_creates_clean_operator_surface
core_tests/control/test_kernel_ion_vnext_optional_live_mcp_supabase_smoke_proof.py::test_m93_closes_only_mcp_live_smoke_and_keeps_supabase_deferred
core_tests/control/test_kernel_ion_vnext_optional_live_mcp_supabase_smoke_proof.py::test_m93_operator_text_does_not_claim_supabase_observed
core_tests/control/test_kernel_ion_vnext_optional_live_mcp_supabase_smoke_proof.py::test_m93_blocks_when_mcp_probe_exposes_arbitrary_shell
core_tests/control/test_kernel_ion_vnext_optional_live_mcp_supabase_smoke_proof.py::test_m93_blocks_when_m92_not_ready
core_tests/control/test_kernel_ion_vnext_optional_live_mcp_supabase_smoke_proof.py::test_m93_rejects_relative_parent_escape
core_tests/control/test_kernel_ion_vnext_production_authority_decision_packet_draft.py::test_current_repo_m102_creates_clean_operator_surface
core_tests/control/test_kernel_ion_vnext_production_authority_decision_packet_draft.py::test_m102_keeps_remaining_gates_open_and_authority_false
core_tests/control/test_kernel_ion_vnext_production_authority_decision_packet_draft.py::test_m102_matrix_and_hash_manifest_are_paired
core_tests/control/test_kernel_ion_vnext_production_authority_decision_packet_draft.py::test_m102_operator_text_preserves_draft_boundary
core_tests/control/test_kernel_ion_vnext_production_authority_decision_packet_draft.py::test_m102_blocks_when_m101_is_not_ready_or_claims_authority
core_tests/control/test_kernel_ion_vnext_production_authority_decision_packet_draft.py::test_m102_rejects_relative_parent_escape
core_tests/control/test_kernel_ion_vnext_production_authority_transition_precheck.py::test_current_repo_m101_creates_clean_operator_surface
core_tests/control/test_kernel_ion_vnext_production_authority_transition_precheck.py::test_m101_keeps_remaining_gates_open_and_authority_false
core_tests/control/test_kernel_ion_vnext_production_authority_transition_precheck.py::test_m101_matrix_and_hash_manifest_are_paired
core_tests/control/test_kernel_ion_vnext_production_authority_transition_precheck.py::test_m101_operator_text_preserves_precheck_boundary
core_tests/control/test_kernel_ion_vnext_production_authority_transition_precheck.py::test_m101_blocks_when_m100_is_not_ready_or_claims_authority
core_tests/control/test_kernel_ion_vnext_production_authority_transition_precheck.py::test_m101_rejects_relative_parent_escape
core_tests/control/test_kernel_ion_vnext_production_cutover_packet_draft.py::test_current_repo_production_cutover_packet_draft_creates_clean_operator_surface
core_tests/control/test_kernel_ion_vnext_production_cutover_packet_draft.py::test_production_cutover_packet_draft_keeps_execution_and_authority_false
core_tests/control/test_kernel_ion_vnext_production_cutover_packet_draft.py::test_production_cutover_packet_draft_text_is_non_executable
core_tests/control/test_kernel_ion_vnext_production_cutover_packet_draft.py::test_production_cutover_packet_draft_blocks_when_m91_not_ready
core_tests/control/test_kernel_ion_vnext_production_cutover_packet_draft.py::test_production_cutover_packet_draft_blocks_if_m91_claims_authority
core_tests/control/test_kernel_ion_vnext_production_cutover_packet_draft.py::test_production_cutover_packet_draft_rejects_relative_parent_escape
core_tests/control/test_kernel_ion_vnext_production_execution_authority_review.py::test_current_repo_m99_creates_clean_operator_surface
core_tests/control/test_kernel_ion_vnext_production_execution_authority_review.py::test_m99_keeps_execution_authority_false_and_routes_rehearsal
core_tests/control/test_kernel_ion_vnext_production_execution_authority_review.py::test_m99_decision_matrix_and_hash_manifest_are_paired
core_tests/control/test_kernel_ion_vnext_production_execution_authority_review.py::test_m99_operator_text_skips_supabase_branch_and_preserves_non_claims
core_tests/control/test_kernel_ion_vnext_production_execution_authority_review.py::test_m99_blocks_when_m98_is_not_ready_or_claims_authority
core_tests/control/test_kernel_ion_vnext_production_execution_authority_review.py::test_m99_rejects_relative_parent_escape
core_tests/control/test_kernel_ion_vnext_readiness_lock.py::test_current_repo_readiness_lock_is_ready_for_review_not_cutover
core_tests/control/test_kernel_ion_vnext_readiness_lock.py::test_readiness_lock_requires_m87_smoke_to_remain_accepted
core_tests/control/test_kernel_ion_vnext_readiness_lock.py::test_readiness_lock_receipt_core_keeps_authority_false
core_tests/control/test_kernel_ion_vnext_readiness_lock.py::test_readiness_lock_does_not_count_m90_dryrun_as_validated_release
core_tests/control/test_kernel_ion_vnext_release_rollback_dryrun.py::test_current_repo_release_rollback_dryrun_creates_clean_operator_surface
core_tests/control/test_kernel_ion_vnext_release_rollback_dryrun.py::test_release_rollback_dryrun_keeps_authority_and_blockers_false
core_tests/control/test_kernel_ion_vnext_release_rollback_dryrun.py::test_release_and_rollback_manifests_are_paired_by_hash
core_tests/control/test_kernel_ion_vnext_release_rollback_dryrun.py::test_release_rollback_dryrun_blocks_when_m89_gate_not_ready
core_tests/control/test_kernel_ion_vnext_release_rollback_dryrun.py::test_release_rollback_dryrun_rejects_relative_parent_escape
core_tests/control/test_kernel_ion_vnext_rollback_package_candidate.py::test_current_repo_m96_creates_clean_operator_surface
core_tests/control/test_kernel_ion_vnext_rollback_package_candidate.py::test_m96_keeps_execution_authority_false_and_closes_only_rollback_gate
core_tests/control/test_kernel_ion_vnext_rollback_package_candidate.py::test_m96_rollback_manifest_and_hash_manifest_are_paired
core_tests/control/test_kernel_ion_vnext_rollback_package_candidate.py::test_m96_operator_text_routes_m97_without_execution_claim
core_tests/control/test_kernel_ion_vnext_rollback_package_candidate.py::test_m96_blocks_when_m95_is_not_ready_or_claims_authority
core_tests/control/test_kernel_ion_vnext_rollback_package_candidate.py::test_m96_rejects_relative_parent_escape
core_tests/control/test_kernel_ion_vnext_validated_release_bundle_candidate.py::test_current_repo_m95_creates_clean_operator_surface
core_tests/control/test_kernel_ion_vnext_validated_release_bundle_candidate.py::test_m95_keeps_non_release_authority_false_and_closes_only_bundle_gate
core_tests/control/test_kernel_ion_vnext_validated_release_bundle_candidate.py::test_m95_release_bundle_and_hash_manifests_are_paired
core_tests/control/test_kernel_ion_vnext_validated_release_bundle_candidate.py::test_m95_operator_text_routes_m96_without_cutover_claim
core_tests/control/test_kernel_ion_vnext_validated_release_bundle_candidate.py::test_m95_blocks_when_m94_is_not_ready_or_claims_authority
core_tests/control/test_kernel_ion_vnext_validated_release_bundle_candidate.py::test_m95_rejects_relative_parent_escape
core_tests/control/test_kernel_ion_workspace_root_registry.py::test_current_workspace_manifest_projects_quarentine_without_quarantine_conflict
```

---

## 5. Open empirical question — answer

**Question (from G1A identity proof):** With monolith-first resolution, do ion_core’s tests for the 6 diverged controls (and the 176-suite overall) stay green?

**Answer (VERIFIED): NO.**

- The suite is **not** green: 78/176 pass under scaffold; 98/176 fail or cannot collect.
- **Not all 6 diverged controls break isolated unit tests:** `agent_cwd_boundary`, `context_proof_gate`, `operator_artifact_hygiene_check`, and `carrier_mount_receipt` unit tests pass against monolith copies.
- **`path_authority` breaks at import** (missing `discover_workspace_manifest`).
- **`workspace_root_registry`** loses 1 integration-style test tied to current-repo manifest discovery.
- **89 vNext harness tests** fail primarily because harness code paths call `load_workspace_authority()` which hits monolith `path_authority` manifest defaults — a **G1-B coupling**, not an extend_path mechanics bug.

**INFERENCE:** Re-running the same dry run against the real repo tree (not temp copies) would likely reduce some `NotADirectoryError` paths if `resolve_repo_root(__file__)` finds a real repo root, but would **not** fix the missing `discover_workspace_manifest` import or ion_core-specific manifest semantics; real-repo re-run was **not** executed in this packet.

---

## 6. VERDICT

| question | answer |
|----------|--------|
| Is extend_path + unified PYTHONPATH mechanically correct? | **YES (VERIFIED)** — merged `__path__`, correct mono/core routing |
| Is scaffold safe to land **as-is** for G1-A “176 green” gate? | **NO (VERIFIED)** |
| Must it pair with G1-B diverged reconcile? | **YES** — at minimum `path_authority` / manifest discovery alignment before G1-A3 duplicate collapse |

**Recommended sequencing (confirms G1A identity proof correction):**

1. **G1-A2 scaffold** (this diff) — namespace mechanism only  
2. **G1-B** — promote diverged monolith modules + port `discover_workspace_manifest`  
3. **G1-A3** — collapse 3 identical ion_core duplicates (behavior-neutral after 1+2)

---

## 7. Risks

| risk | severity | dry-run evidence |
|------|----------|------------------|
| Monolith-first shadows ion_core diverged copies | HIGH | All 9 shared true-names → mono |
| Missing API (`discover_workspace_manifest`) | CRITICAL | Collection error; 89 harness failures cascade |
| extend_path absent → vNext harnesses invisible | HIGH | Negative control: `ModuleNotFoundError` without patch |
| Premature identical-unify (G1-A3) before scaffold | HIGH | INFERENCE from G1A proof — would break harness imports |
| Codex mount PYTHONPATH widening | MEDIUM | Exposes vNext-only modules to live carriers before cutover review |

---

## 8. Explicit non-claims

- **No** real-repo source edits (only this candidate artifact written).
- **No** production / live-execution / accepted-state authority.
- **No** claim that landing scaffold alone restores 176/176 — dry run proves otherwise.
- **No** `pip install`, venv, worker/queue start, or git writes.
- **No** real-repo unified-PYTHONPATH pytest re-run (temp-dir only for scaffold proof).
- Synthesis is not settlement; nemesis audit required before any source edit.
